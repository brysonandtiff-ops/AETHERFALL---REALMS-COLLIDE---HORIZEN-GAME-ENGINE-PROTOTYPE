"""Raw AI sculpt GLB archival is narrow, registered and never a runtime-export shortcut."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import validate_structure as structure


class RawSculptArchivePathTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = Path(self.t.name)
        registry = {"assets": [{"id": "CHR_TestHero", "type": "character"}]}
        self.file("art/asset_registry.json", json.dumps(registry).encode("utf-8"))

    def file(self, path, content=b"glTF sculpt input stub"):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def issues(self):
        errors = []
        structure.scan_source_tree(self.root, errors)
        return errors

    def test_registered_raw_glb_is_allowed(self):
        self.file("art/blender/characters/CHR_TestHero/raw/sculpt_v01.glb")
        self.assertEqual(self.issues(), [])

    def test_wrong_folder_glb_is_rejected(self):
        self.file("art/blender/characters/CHR_TestHero/exports/game_mesh.glb")
        self.assertTrue(any("GLB outside" in x for x in self.issues()))

    def test_unregistered_hero_raw_glb_is_rejected(self):
        self.file("art/blender/characters/CHR_OtherHero/raw/sculpt_v01.glb")
        self.assertTrue(any("GLB outside" in x for x in self.issues()))

    def test_noncharacter_raw_glb_is_rejected(self):
        self.file("art/blender/weapons/WPN_Test/raw/sculpt_v01.glb")
        self.assertTrue(any("GLB outside" in x for x in self.issues()))

    def test_art_root_glb_is_rejected(self):
        self.file("art/sculpt.glb")
        self.assertTrue(any("GLB outside" in x for x in self.issues()))

    def test_case_changed_extension_is_rejected(self):
        self.file("art/blender/characters/CHR_TestHero/raw/sculpt_v01.GLB")
        self.assertTrue(any("GLB outside" in x for x in self.issues()))

    def test_missing_registry_does_not_allow_raw(self):
        self.file("art/asset_registry.json", b"{broken")
        self.file("art/blender/characters/CHR_TestHero/raw/sculpt.glb")
        self.assertTrue(any("GLB outside" in x for x in self.issues()))

    def test_symlinked_raw_source_rejected(self):
        original = self.file("elsewhere/sculpt.glb")
        link = self.root / "art/blender/characters/CHR_TestHero/raw/sculpt.glb"
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(original)
        self.assertTrue(any("Symbolic link" in x for x in self.issues()))


if __name__ == "__main__":
    unittest.main()
