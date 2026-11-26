"""Adversarial receipt tests with synthetic *fixtures*, NEVER native art proof."""
import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("aetherfall_asset_intake", ROOT / "tools/validate_asset_handoffs.py")
intake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intake)

PNG_FIXTURE = b"\x89PNG\r\n\x1a\n" + b"\x00" * 24
BLEND_HEADER_FIXTURE = b"BLENDER-v280" + b"\x00" * 24
GLB_HEADER_FIXTURE = b"glTF" + b"\x00" * 28


class AssetReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aetherfall-intake-")
        self.root = Path(self.temp.name)
        self.asset = {
            "id": "CHR_ThornDell",
            "type": "character",
            "concept_status": "aetherfall_approved",
            "status": "reserved_no_source",
            "concept_dir": "art/concepts/characters/CHR_ThornDell",
            "source_dir": "art/blender/characters/CHR_ThornDell",
            "runtime_dir": "game/assets/characters/heroes/CHR_ThornDell",
        }
        self.data = {"schema_version": 1, "project": "AETHERFALL: REALMS COLLIDE", "assets": [self.asset]}
        for key in ("concept_dir", "source_dir", "runtime_dir"):
            (self.root / self.asset[key]).mkdir(parents=True)
        (self.root / "art/handoffs").mkdir(parents=True)
        (self.root / "evidence/godot").mkdir(parents=True)
        self.receipt = {
            "schema_version": 1,
            "asset_id": self.asset["id"],
            "status": "concept_recorded",
            "provenance": {
                "rights_basis": "owner_original",
                "source_reference": "actual source decision needed; synthetic test only",
                "rights_reviewed_by": "test-only-actor",
                "rights_review_reference": "test-only-review",
            },
            "files": {}
        }

    def tearDown(self):
        self.temp.cleanup()

    def write_artifact(self, kind, folder, name, binary):
        path = self.root / folder / name
        path.write_bytes(binary)
        return {
            "path": path.relative_to(self.root).as_posix(),
            "bytes": len(binary),
            "sha256": hashlib.sha256(binary).hexdigest(),
        }

    def concept(self):
        self.asset["status"] = "concept_recorded"
        self.receipt["status"] = "concept_recorded"
        self.receipt["files"]["concept"] = self.write_artifact(
            "concept", self.asset["concept_dir"], "fixture.png", PNG_FIXTURE
        )
        self.save_receipt()

    def blender(self):
        self.concept()
        self.asset["status"] = "blender_source_recorded"
        self.receipt["status"] = "blender_source_recorded"
        self.receipt["files"]["blender"] = self.write_artifact(
            "blender", self.asset["source_dir"], "fixture.blend", BLEND_HEADER_FIXTURE
        )
        self.save_receipt()

    def runtime(self):
        self.blender()
        self.asset["status"] = "runtime_export_recorded"
        self.receipt["status"] = "runtime_export_recorded"
        self.receipt["files"]["runtime"] = self.write_artifact(
            "runtime", self.asset["runtime_dir"], "fixture.glb", GLB_HEADER_FIXTURE
        )
        self.save_receipt()

    def save_receipt(self):
        path = self.root / "art/handoffs/CHR_ThornDell.json"
        path.write_text(json.dumps(self.receipt), encoding="utf-8")

    def assert_issue(self, contains):
        errors = intake.check(self.root, self.data)
        self.assertTrue(any(contains in item for item in errors), errors)

    def test_current_repo_has_no_premature_production_claim(self):
        self.assertEqual(intake.check(ROOT), [])

    def test_reservation_without_source_is_valid(self):
        self.assertEqual(intake.check(self.root, self.data), [])

    def test_premature_receipt_fails(self):
        self.save_receipt()
        self.assert_issue("premature handoff receipt")

    def test_promoted_without_receipt_fails(self):
        self.asset["status"] = "concept_recorded"
        self.assert_issue("Missing handoff receipt")

    def test_synthetic_concept_checksum_flow(self):
        self.concept()
        self.assertEqual(intake.check(self.root, self.data), [])

    def test_blender_receipt_file_flow_synthetic_only(self):
        self.blender()
        self.assertEqual(intake.check(self.root, self.data), [])

    def test_runtime_receipt_file_flow_synthetic_only(self):
        self.runtime()
        self.assertEqual(intake.check(self.root, self.data), [])

    def test_fake_checksum_rejected(self):
        self.concept()
        self.receipt["files"]["concept"]["sha256"] = "0" * 64
        self.save_receipt()
        self.assert_issue("Asset checksum mismatch")

    def test_wrong_asset_path_rejected(self):
        self.concept()
        self.receipt["files"]["concept"]["path"] = "art/concepts/characters/CHR_Else/fixture.png"
        self.save_receipt()
        self.assert_issue("Unsafe/missing concept artifact")

    def test_path_traversal_rejected(self):
        self.concept()
        self.receipt["files"]["concept"]["path"] = "../fixture.png"
        self.save_receipt()
        self.assert_issue("Unsafe/missing concept artifact")

    def test_invalid_provenance_rejected(self):
        self.concept()
        self.receipt["provenance"]["rights_basis"] = "unlicensed_download"
        self.save_receipt()
        self.assert_issue("Missing provenance rights basis")

    def test_candidate_cannot_enter_blender_production(self):
        self.blender()
        self.asset["concept_status"] = "legacy_owner_approved_candidate_for_aetherfall"
        self.assert_issue("lacks AETHERFALL canon approval")

    def test_corrupt_blend_header_rejected(self):
        self.blender()
        item = self.receipt["files"]["blender"]
        path = self.root / item["path"]
        data = b"NOT_REAL" + b"\x00" * 24
        path.write_bytes(data)
        item["sha256"] = hashlib.sha256(data).hexdigest()
        item["bytes"] = len(data)
        self.save_receipt()
        self.assert_issue("Unrecognised blender artifact header")

    def test_native_stage_without_actual_review_fields_rejected(self):
        self.runtime()
        self.asset["status"] = "native_import_reviewed"
        self.receipt["status"] = "native_import_reviewed"
        self.save_receipt()
        self.assert_issue("Missing genuine native import record")

    def test_native_stage_requires_actual_capture_and_log(self):
        self.runtime()
        self.asset["status"] = "native_import_reviewed"
        self.receipt["status"] = "native_import_reviewed"
        self.receipt["native_import"] = {
            "engine": "Godot", "engine_version": "4.7.2",
            "reviewed_by": "test-only-reviewer",
            "review_reference": "synthetic-fixture",
            "log": {"path": "evidence/godot/nonexistent.log", "bytes": 32, "sha256": "0"*64},
            "capture": {"path": "evidence/godot/nonexistent.png", "bytes": 32, "sha256": "0"*64}
        }
        self.save_receipt()
        self.assert_issue("Unsafe/missing log artifact")
        self.assert_issue("Unsafe/missing capture artifact")

    def test_orphan_manifest_rejected(self):
        (self.root / "art/handoffs/CHR_Foreign.json").write_text("{}", encoding="utf-8")
        self.assert_issue("Handoff receipt has no registered asset")

    def test_duplicate_receipt_fields_rejected(self):
        self.asset["status"] = "concept_recorded"
        (self.root / "art/handoffs/CHR_ThornDell.json").write_text(
            '{"schema_version":1,"schema_version":1}', encoding="utf-8"
        )
        self.assert_issue("Invalid handoff receipt")


if __name__ == "__main__":
    unittest.main()
