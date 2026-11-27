"""Offline tests for HORIZEN STL export helpers. No Blender or engine assumed."""
import importlib.util
import struct
import tempfile
import unittest
import sys
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("horizen_mesh_io", ROOT / "tools/horizen_mesh_io.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class MeshIOTests(unittest.TestCase):
    def setUp(self):
        self.vertices = [(0., 0., 0.), (1., 0., 0.), (0., 1., 0.)]
        self.faces = [(0, 1, 2)]

    def test_real_binary_stl_size_and_scaled_coordinates(self):
        data = mod.binary_stl(self.vertices, self.faces)
        self.assertEqual(len(data), 134)
        self.assertEqual(struct.unpack_from("<I", data, 80)[0], 1)
        first = struct.unpack_from("<12fH", data, 84)
        self.assertEqual(first[3:12], (0, 0, 0, 1000, 0, 0, 0, 1000, 0))
        self.assertEqual(first[12], 0)

    def test_reject_bad_ids(self):
        for value in ("../../danger", "CHR_../", "", "CHR 1", "NOT-a-name", "CHR_.bad"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                mod.safe_asset_id(value)
        self.assertEqual(mod.safe_asset_id("CHR_Vellaris"), "CHR_Vellaris")

    def test_open_mesh_is_not_called_watertight(self):
        audit = mod.audit_triangles(self.vertices, self.faces)
        self.assertEqual(audit["boundary_edges"], 3)
        self.assertFalse(audit["watertight_candidate"])

    def test_closed_tetrahedron_is_only_candidate(self):
        vertices = [(0., 0., 0.), (1., 0., 0.), (0., 1., 0.), (0., 0., 1.)]
        faces = [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)]
        audit = mod.audit_triangles(vertices, faces)
        self.assertTrue(audit["watertight_candidate"])
        self.assertIn("NOT TESTED", audit["assessment"])

    def test_nonfinite_or_out_of_range_fails(self):
        with self.assertRaises(ValueError):
            mod.audit_triangles([(float("nan"), 0, 0)] + self.vertices, self.faces)
        with self.assertRaises(ValueError):
            mod.binary_stl(self.vertices, [(0, 1, 5)])
        with self.assertRaises(ValueError):
            mod.binary_stl(self.vertices, self.faces, millimetres_per_metre=0)

    def test_receipt_hash_is_exact(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.stl"
            path.write_bytes(mod.binary_stl(self.vertices, self.faces))
            self.assertEqual(mod.sha256_file(path), __import__("hashlib").sha256(path.read_bytes()).hexdigest())


    def test_binary_stl_limit_matches_64_mib_browser_intake(self):
        self.assertLessEqual(84 + mod.MAX_BINARY_STL_TRIANGLES * 50, 64 * 1024 * 1024)
        self.assertGreater(84 + (mod.MAX_BINARY_STL_TRIANGLES + 1) * 50, 64 * 1024 * 1024)
        class TooManyFaces:
            def __len__(self):
                return mod.MAX_BINARY_STL_TRIANGLES + 1
        with self.assertRaisesRegex(ValueError, "64 MiB"):
            mod.binary_stl(self.vertices, TooManyFaces())

    def test_export_rejects_unsaved_scene_changes_before_hash_or_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "saved.blend"
            source.write_bytes(b"offline fixture; not an actual Blender scene")
            fake_bpy = SimpleNamespace(data=SimpleNamespace(filepath=str(source), is_dirty=True))
            exporter_spec = importlib.util.spec_from_file_location("horizen_export_test", ROOT / "tools/horizen_blender_export.py")
            exporter = importlib.util.module_from_spec(exporter_spec)
            with patch.dict(sys.modules, {"bpy": fake_bpy, "horizen_mesh_io": mod}):
                exporter_spec.loader.exec_module(exporter)
                with patch.object(exporter, "sha256_file", side_effect=AssertionError("Must reject before hashing")):
                    with self.assertRaisesRegex(ValueError, "Save all current"):
                        exporter.blender_export(["--asset-id", "CHR_Test", "--output-dir", str(Path(tmp) / "exports")])
            self.assertFalse((Path(tmp) / "exports").exists())


if __name__ == "__main__":
    unittest.main()
