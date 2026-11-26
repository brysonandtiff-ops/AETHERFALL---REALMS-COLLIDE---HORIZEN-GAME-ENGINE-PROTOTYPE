"""S.I.R.E.-aligned source integrity checks using isolated real local Git commits.

These tests deliberately use synthetic fixtures. They prove that fail-closed
source protection behaves as specified; they do NOT certify the game release.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("aetherfall_integrity", ROOT / "tools/sire_seal.py")
seal = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(seal)


class SireSourceSealTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aetherfall-source-seal-")
        self.path = Path(self.temp.name)
        self.root = self.path / "candidate"
        shutil.copytree(
            ROOT, self.root,
            ignore=shutil.ignore_patterns(
                ".git", ".godot", ".import", "__pycache__", ".pytest_cache",
                ".mypy_cache", ".venv", "build", "dist",
            ),
        )
        self.git("init", "-q")
        self.git("config", "user.name", "AETHERFALL Test Fixture")
        self.git("config", "user.email", "aetherfall-fixture@example.invalid")
        self.commit("fixture source")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.root), *args],
                                capture_output=True, text=True, timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD").stdout.strip()

    def receipt(self):
        head = self.git("rev-parse", "HEAD").stdout.strip()
        return seal.source_receipt(self.root, self.base, head)

    def test_real_git_bytes_sha256_sha3_and_merkle(self):
        result = self.receipt()
        self.assertEqual(result["source_commit_sha"], self.base)
        self.assertGreater(len(result["source_inventory"]), 70)
        self.assertRegex(result["merkle_root_sha256"], r"^[0-9a-f]{64}$")
        rows = {entry["path"]: entry for entry in result["source_inventory"]}
        original = (self.root / "game/project.godot").read_bytes()
        self.assertEqual(rows["game/project.godot"]["sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(rows["game/project.godot"]["sha3_256"], hashlib.sha3_256(original).hexdigest())
        self.assertEqual(result["release_status"], "BLOCKED")
        self.assertEqual(result["law106_release_badge"], "NOT_MINTED")
        self.assertEqual(result["artifact_status"], "UNANCHORED_INTEGRITY_ONLY")

    def test_deterministic_root_and_no_mutation(self):
        before = self.git("status", "--porcelain").stdout
        one = self.receipt()
        two = self.receipt()
        self.assertEqual(one, two)
        self.assertEqual(before, self.git("status", "--porcelain").stdout)

    def test_stale_sha_is_blocked(self):
        with self.assertRaisesRegex(seal.IntegrityBlocked, "Source SHA mismatch"):
            seal.source_receipt(self.root, self.base, "0" * 40)

    def test_non_ancestor_is_blocked(self):
        with self.assertRaises(seal.IntegrityBlocked):
            seal.source_receipt(self.root, "0" * 40, self.base)

    def test_dirty_worktree_is_blocked(self):
        (self.root / "README.md").write_text("corrupted source", encoding="utf-8")
        with self.assertRaisesRegex(seal.IntegrityBlocked, "dirty"):
            self.receipt()

    def test_untracked_file_is_blocked(self):
        (self.root / "UNTRACKED.txt").write_text("unreviewed", encoding="utf-8")
        with self.assertRaisesRegex(seal.IntegrityBlocked, "dirty"):
            self.receipt()

    def test_deleted_protected_file_is_blocked(self):
        (self.root / "config/local-documents.json").unlink()
        self.commit("delete phone policy")
        with self.assertRaisesRegex(seal.IntegrityBlocked, "structural gate"):
            self.receipt()

    def test_fake_release_approval_is_blocked(self):
        path = self.root / seal.POLICY_PATH
        data = json.loads(path.read_text(encoding="utf-8"))
        data["approval_state"] = "CERTIFIED"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.commit("fake SIRE Gold seal")
        with self.assertRaisesRegex(seal.IntegrityBlocked, "policy deviation"):
            self.receipt()


    def test_unverified_branch_protection_cannot_be_claimed_enabled(self):
        path = self.root / seal.POLICY_PATH
        data = json.loads(path.read_text(encoding="utf-8"))
        data["required_server_controls"]["mandatory_status_checks"] = "ENABLED"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.commit("falsely report GitHub branch enforcement")
        with self.assertRaisesRegex(seal.IntegrityBlocked, "server-side approval rules"):
            self.receipt()

    def test_fake_phone_access_is_not_inferred(self):
        result = self.receipt()
        self.assertEqual(result["phone_downloads_access"], "NOT_VERIFIED")
        self.assertEqual(result["sire_agent_mcp_runtime"], "NOT_CONNECTED")

    def test_new_scene_addition_is_allowed_with_new_root(self):
        old_root = self.receipt()["merkle_root_sha256"]
        path = self.root / "game/scenes/levels/realms/qa_new_scene.tscn"
        path.write_text('[gd_scene format=3]\n[node name="New" type="Node3D"]\n')
        next_sha = self.commit("add legal new scene")
        changed = seal.source_receipt(self.root, self.base, next_sha)
        self.assertNotEqual(changed["merkle_root_sha256"], old_root)
        self.assertEqual(changed["source_commit_sha"], next_sha)

    def test_lfs_pointer_is_not_verified(self):
        path = self.root / "game/assets/characters/heroes/placeholder.glb"
        path.write_text(
            "version https://git-lfs.github.com/spec/v1\n"
            "oid sha256:" + "a" * 64 + "\nsize 555\n",
            encoding="utf-8",
        )
        self.commit("unresolved LFS pointer")
        with self.assertRaisesRegex(seal.IntegrityBlocked, "LFS pointer"):
            self.receipt()

    def test_receipt_roundtrip_is_not_release_certification(self):
        data = self.receipt()
        path = self.path / "source.json"
        seal._write_outside_repo(path, seal.canonical_json(data), self.root)
        verified = seal.check_saved_receipt(self.root, path, self.base, None)
        self.assertTrue(verified["inventory_matches"])
        self.assertEqual(verified["result"], "UNANCHORED_INTEGRITY_ONLY")
        self.assertEqual(verified["release_status"], "BLOCKED")
        trusted_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        # Fixture digest simulates an externally supplied pin, NOT real independent approval.
        stronger = seal.check_saved_receipt(self.root, path, self.base, trusted_digest)
        self.assertEqual(stronger["result"], "ANCHORED_INTEGRITY_ONLY")
        self.assertEqual(stronger["release_status"], "BLOCKED")

    def test_mismatched_digest_anchor_is_blocked(self):
        path = self.path / "source.json"
        path.write_bytes(seal.canonical_json(self.receipt()))
        with self.assertRaisesRegex(seal.IntegrityBlocked, "independently supplied digest"):
            seal.check_saved_receipt(self.root, path, self.base, "0" * 64)

    def test_tampered_receipt_rejected(self):
        original = self.receipt()
        modified = copy.deepcopy(original)
        modified["source_inventory"][0]["sha256"] = "0" * 64
        path = self.path / "tampered.json"
        path.write_bytes(seal.canonical_json(modified))
        with self.assertRaisesRegex(seal.IntegrityBlocked, "does not match"):
            seal.check_saved_receipt(self.root, path, self.base, None)

    def test_receipt_cannot_claim_release(self):
        result = self.receipt()
        result["release_status"] = "CERTIFIED"
        path = self.path / "fake.json"
        path.write_bytes(seal.canonical_json(result))
        with self.assertRaisesRegex(seal.IntegrityBlocked, "unsupported release claim"):
            seal.check_saved_receipt(self.root, path, self.base, None)

    def test_receipt_cannot_write_inside_repository(self):
        with self.assertRaisesRegex(seal.IntegrityBlocked, "outside tracked source"):
            seal._write_outside_repo(self.root / "receipt.json", b"{}",
                                     self.root)
        self.assertFalse((self.root / "receipt.json").exists())

    def test_receipt_never_overwrites_existing_record(self):
        path = self.path / "saved.json"
        path.write_bytes(b"original receipt")
        with self.assertRaisesRegex(seal.IntegrityBlocked, "Refusing to overwrite"):
            seal._write_outside_repo(path, b"new contents", self.root)
        self.assertEqual(path.read_bytes(), b"original receipt")


    def test_previous_source_path_lock_cannot_be_removed(self):
        path = self.root / seal.POLICY_PATH
        data = json.loads(path.read_text(encoding="utf-8"))
        data["required_paths"].remove("docs/development/SIRE_SOURCE_SEAL.md")
        path.write_text(json.dumps(data), encoding="utf-8")
        self.commit("weaken earlier source file lock")
        with self.assertRaisesRegex(seal.IntegrityBlocked, "Attempted weakening"):
            self.receipt()

    def test_previous_proof_gate_cannot_be_renamed_or_removed(self):
        path = self.root / seal.POLICY_PATH
        data = json.loads(path.read_text(encoding="utf-8"))
        del data["evidence_gates"]["native_godot_headless"]
        path.write_text(json.dumps(data), encoding="utf-8")
        self.commit("remove native test requirement")
        with self.assertRaisesRegex(seal.IntegrityBlocked, "inherited proof gate"):
            self.receipt()

    def test_oversize_receipt_file_fails_before_full_read(self):
        path = self.path / "oversized-receipt.json"
        with path.open("wb") as output:
            output.seek(50 * 1024 * 1024)
            output.write(b"X")
        with self.assertRaisesRegex(seal.IntegrityBlocked, "oversize receipt"):
            seal.check_saved_receipt(self.root, path, self.base, None)

    def test_prior_commit_receipt_is_stale_after_new_commit(self):
        before = self.receipt()
        receipt = self.path / "older-source.json"
        receipt.write_bytes(seal.canonical_json(before))
        with (self.root / "README.md").open("a", encoding="utf-8") as output:
            output.write("\nExtra documented scope\n")
        new_sha = self.commit("new source commit invalidates old integrity proof")
        with self.assertRaisesRegex(seal.IntegrityBlocked, "another Git commit"):
            seal.check_saved_receipt(self.root, receipt, new_sha, None)

    def test_duplicate_json_key_is_blocked(self):
        with self.assertRaisesRegex(seal.IntegrityBlocked, "Repeated JSON key"):
            seal.strict_json('{"release_status":"BLOCKED","release_status":"CERTIFIED"}')


if __name__ == "__main__":
    unittest.main()
