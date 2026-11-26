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
        for plan_file in (ROOT / "docs/characters/plans").glob("*.json"):
            target = self.root / plan_file.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(plan_file, target)
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

    def test_large_binary_without_policy_fails(self):
        path = self.root / "art/blender/unreviewed.blend"
        with path.open("wb") as fh:
            fh.seek(validator.MAX_DIRECT_BINARY_BYTES)
            fh.write(b"\x00")
        self.assert_rejected("Binary exceeds 50 MiB")



    def rewrite_plan(self, identifier, change):
        path = self.root / "docs/characters/plans" / (identifier + ".json")
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def test_missing_character_plan_fails(self):
        (self.root / "docs/characters/plans/CHR_Vellaris_Bloodshield.json").unlink()
        self.assert_rejected("Missing character plan")

    def test_unregistered_character_folder_fails(self):
        (self.root / "art/concepts/characters/CHR_Unregistered").mkdir()
        self.assert_rejected("Unregistered character folder")

    def test_character_role_forgery_fails(self):
        self.rewrite_plan("CHR_Vellaris_Bloodshield", lambda d: d["identity"].update(role_class="support"))
        self.assert_rejected("Character role class mismatch")

    def test_candidate_concept_approval_forgery_fails(self):
        self.rewrite_plan("CHR_Korvex", lambda d: d["gates"].update(identity_owner_approved=True))
        self.assert_rejected("Character identity gate mismatch")

    def test_duplicate_unique_hook_fails(self):
        approved = json.loads((self.root / "docs/characters/plans/CHR_Vellaris_Bloodshield.json").read_text())
        self.rewrite_plan("CHR_ThornDell", lambda d: d["identity"].update(
            one_of_one_hook=approved["identity"]["one_of_one_hook"]))
        self.assert_rejected("Duplicate character one-of-one identity")

    def test_corrupted_master_source_hash_fails(self):
        path = self.root / "art/concepts/characters/CHR_Vellaris_Bloodshield/Vellaris_Master_Concept_2026-11-26.png"
        path.write_bytes(b"not the owner-approved image")
        def mutate(d):
            d["concept_reference"]["archive_status"] = "source_verified"
            d["gates"]["source_archived"] = True
        self.rewrite_plan("CHR_Vellaris_Bloodshield", mutate)
        self.assert_rejected("Character master source checksum mismatch")

    def test_unarchived_reference_cannot_fake_section_verification(self):
        self.rewrite_plan("CHR_Vellaris_Bloodshield", lambda d: d["sheet_sections"].update(hero_portrait="source_verified"))
        self.assert_rejected("Unarchived character sheet marked source-verified")

    def test_skipped_godot_gate_fails(self):
        self.rewrite_plan("CHR_Vellaris_Bloodshield", lambda d: d["gates"].update(godot_import_verified=True))
        self.assert_rejected("Character production gate skipped")

    def test_undocumented_waiver_fails(self):
        self.rewrite_plan("CHR_Vellaris_Bloodshield", lambda d: d["sheet_sections"].update(audio_voice="approved_waiver"))
        self.assert_rejected("Undocumented character section waiver")

    def test_master_image_cannot_arrive_unreviewed(self):
        path = self.root / "art/concepts/characters/CHR_Vellaris_Bloodshield/Vellaris_Master_Concept_2026-11-26.png"
        path.write_bytes(b"source added without updating dossier")
        self.assert_rejected("Character source present but archive not verified")


if __name__ == "__main__":
    unittest.main()

