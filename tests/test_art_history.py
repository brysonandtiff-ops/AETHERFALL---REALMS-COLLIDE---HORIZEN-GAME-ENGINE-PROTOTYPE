"""Fail-closed tests for canonical original art/character identity changes."""
import copy
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("aetherfall_art_audit", ROOT / "tools/audit_asset_history.py")
art = importlib.util.module_from_spec(spec)
spec.loader.exec_module(art)


class ProtectedArtHistoryTests(unittest.TestCase):
    def setUp(self):
        self.before = art.load_registry(ROOT / "art/asset_registry.json")
        self.after = copy.deepcopy(self.before)

    def assert_bad(self, message):
        errors = art.audit_registry(self.before, self.after)
        self.assertTrue(any(message in error for error in errors), errors)

    def test_same_registry_is_safe(self):
        self.assertEqual(art.audit_registry(self.before, self.after), [])

    def test_deleted_canonical_asset_is_rejected(self):
        self.after["assets"].pop()
        self.assert_bad("Canonical art IDs removed, renamed or reordered")

    def test_reordered_existing_ids_is_rejected(self):
        self.after["assets"][0], self.after["assets"][1] = self.after["assets"][1], self.after["assets"][0]
        self.assert_bad("Canonical art IDs removed, renamed or reordered")

    def test_controlled_first_asset_stage_is_allowed_by_history(self):
        self.after["assets"][0]["status"] = "concept_recorded"
        # This audit checks only the status transition. Receipt/files are independently verified.
        self.assertEqual(art.audit_registry(self.before, self.after), [])

    def test_skipped_asset_stage_is_rejected(self):
        self.after["assets"][0]["status"] = "runtime_export_recorded"
        self.assert_bad("Unsafe asset lifecycle transition")

    def test_unknown_asset_stage_is_rejected(self):
        self.after["assets"][0]["status"] = "magic_verified"
        self.assert_bad("Invalid asset lifecycle state")

    def test_reverted_asset_stage_is_rejected(self):
        self.before["assets"][0]["status"] = "blender_source_recorded"
        self.after["assets"][0]["status"] = "concept_recorded"
        self.assert_bad("Unsafe asset lifecycle transition")

    def test_source_dir_change_is_rejected(self):
        self.after["assets"][0]["source_dir"] = "art/blender/characters/CHR_Other"
        self.assert_bad("Approved art identity/source contract rewritten")

    def test_model_concept_status_fake_approval_is_rejected(self):
        self.after["assets"][0]["concept_status"] = "aetherfall_approved_final_model"
        self.assert_bad("Approved art identity/source contract rewritten")

    def test_new_proposed_asset_can_be_appended(self):
        obj = copy.deepcopy(self.after["assets"][0])
        obj.update(id="CHR_Future", status="reserved_no_source")
        self.after["assets"].append(obj)
        self.assertEqual(art.audit_registry(self.before, self.after), [])

    def test_new_asset_cannot_fake_completed_model(self):
        obj = copy.deepcopy(self.after["assets"][0])
        obj.update(id="CHR_Future", status="engine_verified")
        self.after["assets"].append(obj)
        self.assert_bad("New asset falsely claims produced source")

    def test_duplicate_asset_id_rejected(self):
        self.after["assets"].append(copy.deepcopy(self.after["assets"][0]))
        self.assert_bad("Duplicate canonical asset ID")

    def test_duplicate_json_fields_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "registry.json"
            path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate canonical art JSON field"):
                art.load_registry(path)

    def test_removed_art_in_real_git_repository_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
            (root / "art/concepts").mkdir(parents=True)
            (root / "evidence").mkdir()
            (root / "art/concepts/owner-sheet.txt").write_text("master source", encoding="utf-8")
            (root / "evidence/capture.txt").write_text("original log", encoding="utf-8")
            subprocess.run(["git", "add", "art", "evidence"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "-c", "user.name=StudioTest", "-c",
                            "user.email=test@example.invalid", "commit", "-qm", "fixture"],
                           cwd=root, check=True, capture_output=True)
            base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                                  capture_output=True, text=True).stdout.strip()
            self.assertEqual(art.audit_removed_source_files(root, base), [])
            (root / "art/concepts/owner-sheet.txt").unlink()
            (root / "evidence/capture.txt").unlink()
            subprocess.run(["git", "add", "-u"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "-c", "user.name=StudioTest", "-c",
                            "user.email=test@example.invalid", "commit", "-qm", "remove"],
                           cwd=root, check=True, capture_output=True)
            failures = art.audit_removed_source_files(root, base)
            self.assertEqual(sum("Protected original" in x for x in failures), 2, failures)


if __name__ == "__main__":
    unittest.main()
