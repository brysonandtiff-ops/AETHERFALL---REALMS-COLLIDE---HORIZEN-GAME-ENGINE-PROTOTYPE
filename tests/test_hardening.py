"""Adversarial validator tests; never claim native engine certification."""
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("aetherfall_safety", ROOT / "tools/validate_structure.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class HardenedStructureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aetherfall-harden-")
        self.root = Path(self.temp.name)
        for rel in validator.REQUIRED_DIRS:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        for rel in validator.REQUIRED_FILES:
            target = self.root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, target)
        data = json.loads((self.root / "art/asset_registry.json").read_text())
        for asset in data["assets"]:
            for key in ("concept_dir", "source_dir", "runtime_dir"):
                (self.root / asset[key]).mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.temp.cleanup()

    def assert_rejected(self, fragment):
        errors = validator.check(self.root)
        self.assertTrue(any(fragment in issue for issue in errors), errors)

    def rewrite_registry(self, change):
        path = self.root / "art/asset_registry.json"
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def test_positive_layout_and_legacy_hold(self):
        self.assertEqual(validator.check(self.root), [])

    def test_escape_main_scene_fails(self):
        path = self.root / "game/project.godot"
        path.write_text(path.read_text().replace(
            "res://scenes/bootstrap/main.tscn", "res://../art/asset_registry.json"
        ))
        self.assert_rejected("main scene missing/unsafe")

    def test_missing_external_resource_fails(self):
        path = self.root / "game/scenes/bootstrap/main.tscn"
        path.write_text(path.read_text() + '\n[ext_resource type="Texture2D" path="res://assets/ghost.png" id="1"]\n')
        self.assert_rejected("Missing/unsafe Godot ext_resource")

    def test_duplicate_id_case_insensitive_fails(self):
        def mut(data):
            data["assets"].append({**data["assets"][0], "id": "CHR_vellaris_bloodshield"})
        self.rewrite_registry(mut)
        self.assert_rejected("Duplicate asset ID")

    def test_unverified_status_fails(self):
        self.rewrite_registry(lambda d: d["assets"][0].update(status="engine_verified"))
        self.assert_rejected("Unverified asset status promotion")

    def test_registry_traversal_fails(self):
        self.rewrite_registry(lambda d: d["assets"][0].update(source_dir="../secrets"))
        self.assert_rejected("Missing/unsafe source_dir")

    def test_unverified_source_deletion_claim_fails(self):
        path = self.root / "docs/legacy/shadowspire_migration.json"
        data = json.loads(path.read_text())
        data["deletion_status"] = "DELETED"
        path.write_text(json.dumps(data))
        self.assert_rejected("Unverified deletion status promotion")

    def test_missing_multiplayer_boundary_fails(self):
        (self.root / "game/scripts/network").rmdir()
        self.assert_rejected("Missing/unsafe directory: game/scripts/network")

    def test_secret_env_fails(self):
        (self.root / ".env.production").write_text("TEST_NOT_SECRET=123")
        self.assert_rejected("Private environment file")

    def test_signing_key_fails(self):
        (self.root / "game/production.keystore").write_bytes(b"test")
        self.assert_rejected("Possible key/credential")

    def test_art_source_separation_fails(self):
        path = self.root / "game/assets/copy.blend"
        path.write_bytes(b"fake")
        self.assert_rejected("Editable Blender source inside game/")

    def test_symlink_fails(self):
        (self.root / "art/unsafe-link").symlink_to(self.root / "README.md")
        self.assert_rejected("Symbolic link")

    def test_case_collision_fails(self):
        (self.root / "game/Scenes").mkdir(parents=True)
        self.assert_rejected("Case collision")

    def test_embedded_token_is_rejected_without_leaking_value(self):
        marker = "gh" + "p_" + ("A" * 41)
        (self.root / "game/scripts/core/token_test.gd").write_text("var example = '" + marker + "'")
        errors = validator.check(self.root)
        self.assertTrue(any("Possible embedded credential (GitHub access token)" in e for e in errors), errors)
        self.assertTrue(all(marker not in e for e in errors))

    def test_embedded_private_key_header_is_rejected(self):
        marker = "-----BEGIN " + "PRIVATE KEY-----"
        (self.root / "README.md").write_text("Not a secret: " + marker)
        self.assert_rejected("Possible embedded credential (private key header)")

    def test_build_directory_is_scanned_not_blindly_excluded(self):
        directory = self.root / "build"
        directory.mkdir()
        (directory / "credentials.json").write_text("do not ship")
        self.assert_rejected("Possible key/credential file: build/credentials.json")

    def test_generated_git_cache_is_not_required(self):
        self.assertEqual(validator.check(self.root), [])

    def test_large_binary_without_policy_fails(self):
        path = self.root / "art/blender/unreviewed.blend"
        with path.open("wb") as fh:
            fh.seek(validator.MAX_DIRECT_BINARY_BYTES)
            fh.write(b"\x00")
        self.assert_rejected("Binary exceeds 50 MiB")


if __name__ == "__main__":
    unittest.main()

