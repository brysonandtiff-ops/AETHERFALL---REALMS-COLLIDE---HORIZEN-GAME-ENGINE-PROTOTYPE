"""SIRE-ART-INFO-001 metadata gate tests (not image similarity or engine proof)."""
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("infographic_guard", ROOT / "tools/validate_structure.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class InfographicPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aetherfall-infographic-")
        self.root = Path(self.temp.name)
        for rel in (
            "docs/art/INFOGRAPHIC_POLICY.json",
            "docs/art/INFOGRAPHIC_PLAN_TEMPLATE.json",
            "docs/characters/CANON_LOCKS.json",
        ):
            dest = self.root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, dest)

    def tearDown(self):
        self.temp.cleanup()

    def change(self, rel, transform):
        p = self.root / rel
        doc = json.loads(p.read_text(encoding="utf-8"))
        transform(doc)
        p.write_text(json.dumps(doc), encoding="utf-8")

    def findings(self):
        errors = []
        guard.validate_infographic_policy(self.root, errors)
        return errors

    def assert_rejected(self, message):
        self.assertTrue(any(message in issue for issue in self.findings()), self.findings())

    def test_complete_unapproved_policy_is_accepted_as_metadata(self):
        self.assertEqual(self.findings(), [])

    def test_reference_hash_cannot_silently_change(self):
        self.change("docs/art/INFOGRAPHIC_POLICY.json",
                    lambda d: d["master_reference"].update(sha256="0" * 64))
        self.assert_rejected("master reference identity/hash drift")

    def test_all_asset_families_must_be_covered(self):
        self.change("docs/art/INFOGRAPHIC_POLICY.json",
                    lambda d: d["asset_panels"].pop("level"))
        self.assert_rejected("asset type coverage drift")

    def test_weapon_panel_cannot_be_removed(self):
        self.change("docs/art/INFOGRAPHIC_POLICY.json",
                    lambda d: d["asset_panels"]["weapon"].remove("construction_and_operation"))
        self.assert_rejected("required panels missing: weapon")

    def test_generated_concept_cannot_claim_runtime_proof(self):
        self.change("docs/art/INFOGRAPHIC_POLICY.json",
                    lambda d: d.update(generated_art_is_runtime_proof=True))
        self.assert_rejected("owner review/evidence safety drift")

    def test_owner_approval_flag_cannot_be_removed(self):
        self.change("docs/art/INFOGRAPHIC_POLICY.json",
                    lambda d: d.update(owner_approval_required=False))
        self.assert_rejected("owner review/evidence safety drift")

    def test_template_cannot_self_approve(self):
        self.change("docs/art/INFOGRAPHIC_PLAN_TEMPLATE.json",
                    lambda d: d["owner_review"].update(decision="approved"))
        self.assert_rejected("plan template self-approval")

    def test_template_cannot_forge_native_engine_proof(self):
        self.change("docs/art/INFOGRAPHIC_PLAN_TEMPLATE.json",
                    lambda d: d["runtime_evidence"].update(status="GODOT_RUNTIME_VERIFIED"))
        self.assert_rejected("plan template self-approval")

    def test_missing_policy_is_not_a_pass(self):
        (self.root / "docs/art/INFOGRAPHIC_POLICY.json").unlink()
        self.assert_rejected("Missing/invalid infographic policy")


if __name__ == "__main__":
    unittest.main()
