"""Adversarial tests for the static Blender handoff honesty gate."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import validate_blender_handoff as gate


class BlenderHandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.id = "CHR_TestHero"
        self.folder = self.root / "art" / "blender" / "characters" / self.id
        self.folder.mkdir(parents=True)
        self.doc = {
            "schema_version": 1, "project": gate.PROJECT, "asset_id": self.id,
            "production_status": "NOT_VERIFIED", "stages": {
                stage: {"status": "NOT_RUN", "evidence_path": None, "evidence_sha256": None}
                for stage in gate.STAGE_NAMES
            },
        }

    def save(self):
        (self.folder / "handoff.json").write_text(json.dumps(self.doc), encoding="utf-8")

    def test_no_manifests_does_not_assert_a_model(self):
        self.assertEqual(gate.check(self.root), [])

    def test_unverified_manifest_allowed(self):
        self.save()
        self.assertEqual(gate.check(self.root), [])

    def test_fraudulent_game_ready_rejected(self):
        self.doc["production_status"] = "GAME_READY"
        self.save()
        issues = gate.check(self.root)
        self.assertTrue(any("prematurely promoted" in issue for issue in issues))
        self.assertTrue(any("source approval missing" in issue for issue in issues))
        self.assertTrue(any("engine exports missing" in issue for issue in issues))

    def test_pass_without_real_evidence_rejected(self):
        self.doc["stages"]["uv_pbr_bakes"]["status"] = "PASS"
        self.save()
        self.assertTrue(any("Unverified Blender stage PASS uv_pbr_bakes" in x for x in gate.check(self.root)))

    def test_pass_with_hashed_file_allowed_as_static_claim(self):
        folder = self.root / "evidence" / "characters" / self.id
        folder.mkdir(parents=True)
        evidence = folder / "real-capture-note.txt"
        evidence.write_text("Example fixture content; not a native engine capture", encoding="utf-8")
        stage = self.doc["stages"]["uv_pbr_bakes"]
        stage["status"] = "PASS"
        stage["evidence_path"] = evidence.relative_to(self.root).as_posix()
        stage["evidence_sha256"] = hashlib.sha256(evidence.read_bytes()).hexdigest()
        self.save()
        self.assertEqual(gate.check(self.root), [])

    def test_escape_path_rejected(self):
        stage = self.doc["stages"]["godot_native_import"]
        stage.update(status="PASS", evidence_path="evidence/../../etc/passwd", evidence_sha256="0" * 64)
        self.save()
        self.assertTrue(gate.check(self.root))

    def test_unhashable_stage_status_fails_closed(self):
        self.doc["stages"]["rig_sockets_export"]["status"] = ["PASS"]
        self.save()
        self.assertTrue(any("Missing/invalid Blender stage" in x for x in gate.check(self.root)))

    def test_unhashable_production_status_fails_closed(self):
        self.doc["production_status"] = {"status": "GAME_READY"}
        self.save()
        self.assertTrue(any("Unknown Blender handoff production status" in x for x in gate.check(self.root)))

    def test_wrong_identity_rejected(self):
        self.doc["asset_id"] = "CHR_OtherHero"
        self.save()
        self.assertTrue(any("identity mismatch" in x for x in gate.check(self.root)))


if __name__ == "__main__":
    unittest.main()
