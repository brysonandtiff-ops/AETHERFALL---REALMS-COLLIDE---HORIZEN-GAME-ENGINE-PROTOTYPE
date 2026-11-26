"""Adversarial structure compatibility checks using genuine local Git fixtures.

Tests exercise the guard, NOT native Godot graphics or a physical device.
"""
import copy
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("aetherfall_structure_guard", ROOT / "tools/structure_guard.py")
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


class StructureGuardTests(unittest.TestCase):
    def setUp(self):
        self.context = tempfile.TemporaryDirectory(prefix="aetherfall-layout-")
        self.root = Path(self.context.name)
        policy = json.loads((ROOT / guard.CONTRACT_FILE).read_text(encoding="utf-8"))
        for rel in policy["protected_paths"]:
            src = ROOT / rel
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, target)
        for rel in policy["preserved_roots"]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        (self.root / "game/scenes/levels/realms").mkdir(parents=True, exist_ok=True)
        (self.root / "game/scenes/levels/realms/.gitkeep").write_text("reserve", encoding="utf-8")
        (self.root / "game/scenes/levels/realms/old_map.tscn").write_text(
            "[gd_scene format=3]\n[node name=\"Old\" type=\"Node3D\"]\n",
            encoding="utf-8"
        )
        self.git("init", "-q")
        self.git("config", "user.email", "aetherfall-tests@example.invalid")
        self.git("config", "user.name", "AETHERFALL Fixture")
        self.commit("baseline")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()

    def tearDown(self):
        self.context.cleanup()

    def git(self, *args):
        result = subprocess.run(
            ["git", "-C", str(self.root), *args],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding="utf-8", check=False, timeout=15
        )
        self.assertEqual(result.returncode, 0, f"git {args!r}: {result.stderr}")
        return result

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-qm", message)

    def assert_issue(self, issues, phrase):
        self.assertTrue(any(phrase in issue for issue in issues), issues)

    def test_clean_baseline_and_unchanged_comparison(self):
        self.assertEqual(guard.workspace_issues(self.root), [])
        self.assertEqual(guard.compare_issues(self.root, self.base), [])

    def test_new_scene_is_allowed(self):
        (self.root / "game/scenes/levels/realms/new_map.tscn").write_text(
            '[gd_scene format=3]\n[node name="New" type="Node3D"]\n',
            encoding="utf-8"
        )
        self.commit("add new level")
        self.assertEqual(guard.workspace_issues(self.root), [])
        self.assertEqual(guard.compare_issues(self.root, self.base), [])

    def test_replacing_placeholder_gitkeep_is_allowed(self):
        (self.root / "game/scenes/levels/realms/.gitkeep").unlink()
        (self.root / "game/scenes/levels/realms/level.tscn").write_text("[gd_scene format=3]\n")
        self.commit("replace placeholder")
        self.assertEqual(guard.compare_issues(self.root, self.base), [])

    def test_deleting_existing_scene_is_blocked(self):
        (self.root / "game/scenes/levels/realms/old_map.tscn").unlink()
        self.commit("delete source")
        self.assert_issue(guard.compare_issues(self.root, self.base), "source/art/evidence file removed")

    def test_deleting_project_is_rejected_without_crash(self):
        (self.root / "game/project.godot").unlink()
        self.commit("delete project")
        self.assert_issue(guard.compare_issues(self.root, self.base), "Protected file deleted/replaced")

    def test_existing_asset_id_removal_is_blocked(self):
        path = self.root / "art/asset_registry.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["assets"].pop()
        path.write_text(json.dumps(data), encoding="utf-8")
        self.commit("drop asset")
        self.assert_issue(guard.compare_issues(self.root, self.base), "Existing asset ID removed")

    def test_existing_asset_path_change_is_blocked(self):
        path = self.root / "art/asset_registry.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["assets"][0]["runtime_dir"] = "game/assets/characters/heroes/NEW_ID"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.commit("rename character path")
        self.assert_issue(guard.compare_issues(self.root, self.base), "Existing asset identity/path changed")

    def test_main_scene_change_is_blocked(self):
        path = self.root / "game/project.godot"
        data = path.read_text(encoding="utf-8")
        path.write_text(
            data.replace("res://scenes/bootstrap/main.tscn", "res://scenes/levels/realms/old_map.tscn"),
            encoding="utf-8"
        )
        self.commit("change main scene without migration")
        self.assert_issue(guard.compare_issues(self.root, self.base), "Main scene path changed")

    def test_policy_cannot_remove_protected_files(self):
        path = self.root / guard.CONTRACT_FILE
        config = json.loads(path.read_text(encoding="utf-8"))
        config["protected_paths"].remove("game/scenes/bootstrap/main.tscn")
        path.write_text(json.dumps(config), encoding="utf-8")
        self.commit("weaken policy")
        self.assert_issue(guard.compare_issues(self.root, self.base), "Attempted weakening")

    def test_invalid_ancestor_ref_is_rejected(self):
        self.assert_issue(guard.compare_issues(self.root, "../../main"), "Base must be")
        self.assert_issue(guard.compare_issues(self.root, "0" * 40), "Base Git commit is inaccessible")

    def test_broken_scene_resource_is_detected(self):
        path = self.root / "game/scenes/levels/realms/old_map.tscn"
        path.write_text(
            '[gd_scene load_steps=2 format=3]\n[ext_resource type="Texture2D" path="res://assets/missing.png" id="1"]\n',
            encoding="utf-8"
        )
        self.assert_issue(guard.workspace_issues(self.root), "Broken static res:// link")

    def test_broken_gd_script_resource_is_detected(self):
        file = self.root / "game/scripts/unsafe.gd"
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text('var file = preload("res://scenes/absent.tscn")\n', encoding="utf-8")
        self.assert_issue(guard.workspace_issues(self.root), "Broken static res:// link")

    def test_existing_gd_resource_is_valid(self):
        file = self.root / "game/scripts/good.gd"
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text('var file = preload("res://scenes/bootstrap/main.tscn")\n', encoding="utf-8")
        self.assertEqual(guard.workspace_issues(self.root), [])

    def test_duplicate_scene_uid_detected(self):
        for name in ("a.tscn", "b.tscn"):
            (self.root / "game/scenes/levels/realms" / name).write_text(
                '[gd_scene format=3 uid="uid://same123"]\n',
                encoding="utf-8"
            )
        self.assert_issue(guard.workspace_issues(self.root), "Duplicate Godot UID")

    def test_orphan_script_uid_rejected(self):
        file = self.root / "game/scripts/missing.gd.uid"
        file.write_text("uid://abc123\n", encoding="utf-8")
        self.assert_issue(guard.workspace_issues(self.root), "Orphan Godot script UID sidecar")

    def test_second_nested_godot_project_rejected(self):
        file = self.root / "game/scenes/project.godot"
        file.write_text("config_version=5\n", encoding="utf-8")
        self.assert_issue(guard.workspace_issues(self.root), "Multiple or missing nested Godot project")

    def test_windows_reserved_file_is_rejected(self):
        (self.root / "game/scenes/CON.tscn").write_text("[gd_scene format=3]\n", encoding="utf-8")
        self.assert_issue(guard.workspace_issues(self.root), "Windows-reserved")

    def test_windows_trailing_dot_rejected(self):
        (self.root / "game/scenes/bad.").mkdir()
        self.assert_issue(guard.workspace_issues(self.root), "Windows-reserved")

    def test_case_alias_rejected(self):
        (self.root / "game/Scenes").mkdir()
        self.assert_issue(guard.workspace_issues(self.root), "Case collision")

    def test_symlink_rejected(self):
        link = self.root / "game/scenes/original_link"
        try:
            link.symlink_to(self.root / "game/scenes/bootstrap")
        except OSError:
            self.skipTest("Symlinks unsupported on fixture filesystem")
        self.assert_issue(guard.workspace_issues(self.root), "Symlink not allowed")


if __name__ == "__main__":
    unittest.main()
