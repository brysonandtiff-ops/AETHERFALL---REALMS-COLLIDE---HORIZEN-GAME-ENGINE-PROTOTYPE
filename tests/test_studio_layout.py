"""Adversarial AAA studio layout tests. All passes prove source structure only."""
import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("aetherfall_studio_layout", ROOT / "tools/validate_studio_layout.py")
studio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(studio)


class StudioLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = studio.load_json(ROOT / studio.MANIFEST)
        cls.toolchain = studio.load_json(ROOT / studio.TOOLCHAIN)

    def setUp(self):
        self.manifest_copy = copy.deepcopy(self.manifest)
        self.toolchain_copy = copy.deepcopy(self.toolchain)

    def errors(self):
        return studio.check(ROOT, self.manifest_copy, self.toolchain_copy)

    def assert_bad(self, text):
        issues = self.errors()
        self.assertTrue(any(text in i for i in issues), issues)

    def test_real_studio_root_is_valid(self):
        self.assertEqual(studio.check(ROOT), [])

    def test_engine_cannot_silently_switch_to_unreal(self):
        self.manifest_copy["engine_family"] = "Unreal"
        self.assert_bad("engine identity changed")

    def test_toolchain_cannot_claim_unreviewed_perforce(self):
        self.toolchain_copy["source_control"]["perforce_configured"] = True
        self.assert_bad("Unapproved VCS/LFS/Perforce")

    def test_missing_ownership_zone_fails(self):
        self.manifest_copy["zones"] = [z for z in self.manifest_copy["zones"] if z["id"] != "source_art"]
        self.assert_bad("Required studio ownership zone removed")

    def test_unsafe_path_traversal_fails(self):
        self.manifest_copy["required_directories"].append("../private")
        self.assert_bad("Unsafe studio contract path")

    def test_duplicate_module_owner_paths_fail(self):
        self.manifest_copy["modules"][0]["path"] = self.manifest_copy["modules"][1]["path"]
        self.assert_bad("Runtime module ID/path ownership contract changed")
        self.assert_bad("Runtime module paths reused")

    def test_removed_module_fails(self):
        self.manifest_copy["modules"].pop()
        self.assert_bad("Runtime module ID/path ownership contract changed")

    def test_removed_required_source_dir_fails(self):
        self.manifest_copy["required_directories"].remove("game/scripts/network")
        self.assert_bad("Required studio required_directories omitted")

    def test_cannot_remove_asset_handoff_contract_dir(self):
        self.manifest_copy["required_directories"].remove("art/handoffs")
        self.assert_bad("Required studio required_directories omitted")

    def test_cannot_remove_preflight_from_studio_contract(self):
        self.manifest_copy["required_files"].remove("tools/studio_preflight.py")
        self.assert_bad("Required studio required_files omitted")

    def test_missing_protected_file_fails(self):
        self.manifest_copy["required_files"].remove("art/asset_registry.json")
        self.assert_bad("Required studio required_files omitted")

    def test_second_art_registry_rejected(self):
        self.manifest_copy["authoritative_character_source"] = "art/characters.json"
        self.assert_bad("Second or missing character identity registry")

    def test_all_approval_gates_are_required(self):
        self.manifest_copy["constraints"]["no_public_private_photos_or_secrets"] = False
        self.assert_bad("approval gates missing")

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "studio.json"
            bad.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate JSON field"):
                studio.load_json(bad)

    def test_cli_validates_real_scaffold(self):
        cmd = subprocess.run([sys.executable, str(ROOT / "tools/validate_studio_layout.py")],
                             cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(cmd.returncode, 0, cmd.stdout + cmd.stderr)
        self.assertIn("STRUCTURE ONLY", cmd.stdout)

    def make_temp_root(self):
        temp = tempfile.TemporaryDirectory(prefix="aetherfall-layout-")
        root = Path(temp.name)
        for directory in self.manifest["required_directories"]:
            (root / directory).mkdir(parents=True, exist_ok=True)
        for path in self.manifest["required_files"]:
            dest = root / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            if path in (studio.TOOLCHAIN, studio.MANIFEST):
                shutil.copyfile(ROOT / path, dest)
            else:
                dest.write_text("temporary test fixture", encoding="utf-8")
        return temp, root

    def test_missing_actual_directory_fails(self):
        tmp, root = self.make_temp_root()
        try:
            missing = root / "game/scripts/save"
            missing.rmdir()
            errors = studio.check(root)
            self.assertTrue(any("Missing studio directory: game/scripts/save" in e for e in errors), errors)
        finally:
            tmp.cleanup()

    def test_symlinked_owned_path_is_rejected(self):
        tmp, root = self.make_temp_root()
        try:
            target = root / "game/scripts/ai"
            target.rmdir()
            target.symlink_to(root / "game/scripts/network", target_is_directory=True)
            issues = studio.check(root)
            self.assertTrue(any("Unsafe studio contract path: game/scripts/ai" in e for e in issues), issues)
        finally:
            tmp.cleanup()

    def test_unreal_cooked_content_is_rejected(self):
        tmp, root = self.make_temp_root()
        try:
            forbidden = root / "game/assets/wrong.uasset"
            forbidden.write_bytes(b"unreal fixture")
            issues = studio.check(root)
            self.assertTrue(any("Unreal-only game artifact inside Godot project" in e for e in issues), issues)
        finally:
            tmp.cleanup()

    def test_addon_missing_provenance_is_rejected(self):
        tmp, root = self.make_temp_root()
        try:
            (root / "game/addons/unlicensed").mkdir()
            issues = studio.check(root)
            self.assertTrue(any("Unreviewed Godot add-on missing provenance" in e for e in issues), issues)
        finally:
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
