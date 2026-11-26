"""Real isolated Git fixture tests; no actual repository mutation."""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("aetherfall_git_preflight", ROOT / "tools/git_preflight.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class GitPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aetherfall-git-test-")
        self.repo = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Git Preflight Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("remote", "add", "origin", "https://github.com/" + guard.CANONICAL + ".git")
        for p, data in (
            ("AGENTS.md", "source rules\n"),
            ("game/project.godot", "config_version=5\n"),
            ("art/asset_registry.json", '{"assets":[]}\n'),
            ("docs/characters/CANON_LOCKS.json", '{"approved":[]}\n'),
        ):
            f = self.repo / p
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(data)
        self.base = self.commit("base")
        self.git("checkout", "-qb", "feature/one-task")
        (self.repo / "game/scripts").mkdir(parents=True)
        (self.repo / "game/scripts/new.gd").write_text("extends Node\n")
        self.head = self.commit("safe addition")

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.repo), *args],
                                capture_output=True, text=True, timeout=15, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD").stdout.strip()

    def verify(self):
        return guard.assess(self.repo, expected_head=self.head, base_sha=self.base, strict=True)

    def test_clean_new_script_passes(self):
        r = self.verify()
        self.assertEqual(r["result"], "PASS_SOURCE_PREFLIGHT")
        self.assertEqual(r["base_comparison"], "ANCESTOR")
        self.assertFalse(r["mutation_performed"])

    def test_bad_origin_fails(self):
        self.git("remote", "set-url", "origin", "https://github.com/unrelated/private.git")
        self.assertEqual(self.verify()["origin"], "UNKNOWN_OR_WRONG")
        self.assertEqual(self.verify()["result"], "BLOCKED")

    def test_ssh_remote_accepted(self):
        self.git("remote", "set-url", "origin", "git@github.com:" + guard.CANONICAL + ".git")
        self.assertEqual(self.verify()["origin"], "MATCH")

    def test_dirty_tree_fails(self):
        (self.repo / "AGENTS.md").write_text("modified and uncommitted\n")
        self.assertIn("Working tree has uncommitted or untracked changes", self.verify()["issues"])

    def test_untracked_file_fails(self):
        (self.repo / "untracked.txt").write_text("untracked\n")
        self.assertIn("Working tree has uncommitted or untracked changes", self.verify()["issues"])

    def test_sha_mismatch_fails(self):
        r = guard.assess(self.repo, expected_head="0" * 40, base_sha=self.base, strict=True)
        self.assertTrue(any("does not match" in p for p in r["issues"]))

    def test_invalid_base_fails(self):
        r = guard.assess(self.repo, expected_head=self.head, base_sha="../main", strict=True)
        self.assertEqual(r["base_comparison"], "INVALID")

    def test_missing_base_fails(self):
        r = guard.assess(self.repo, expected_head=self.head, base_sha="0" * 40, strict=True)
        self.assertEqual(r["base_comparison"], "MISSING")

    def test_protected_scene_delete_fails(self):
        (self.repo / "game/project.godot").unlink()
        self.head = self.commit("bad deletion")
        self.assertTrue(any("Existing protected source removed" in p for p in self.verify()["issues"]))

    def test_original_art_delete_fails(self):
        master = self.repo / "art/concepts/characters/CHR_Korvex/master.webp"
        master.parent.mkdir(parents=True)
        master.write_bytes(b"original-source")
        self.base = self.commit("add original art")
        master.unlink()
        self.head = self.commit("delete original")
        self.assertTrue(any("Existing protected source removed" in p for p in self.verify()["issues"]))

    def test_gitkeep_removal_allows_new_model(self):
        old = self.repo / "game/assets/.gitkeep"
        old.parent.mkdir(parents=True)
        old.write_text("reserved")
        self.base = self.commit("reserve")
        old.unlink()
        (self.repo / "game/assets/model_v002.glb").write_bytes(b"new export")
        self.head = self.commit("real asset")
        self.assertEqual(self.verify()["result"], "PASS_SOURCE_PREFLIGHT")

    def test_canon_change_requires_review(self):
        p = self.repo / "docs/characters/CANON_LOCKS.json"
        p.write_text('{"approved":["new candidate"]}\n')
        self.head = self.commit("change canon")
        report = self.verify()
        self.assertIn("docs/characters/CANON_LOCKS.json", report["review_required_paths"])
        self.assertEqual(report["server_side_branch_protection"], "NOT_VERIFIED")

    def test_conflict_markers_fail(self):
        p = self.repo / "game/scripts/conflicted.gd"
        p.write_text(("<" * 7) + " HEAD\nextends Node\n")
        self.head = self.commit("bad merge marker")
        self.assertIn("Merge-conflict marker added in commit range", self.verify()["issues"])

    def test_token_pattern_fails_without_leaking_token(self):
        token = "gh" + "p_" + "A" * 40
        (self.repo / "unsafe.txt").write_text("TOKEN=" + token + "\n")
        self.head = self.commit("potential token leak")
        r = self.verify()
        self.assertTrue(any("Credential-like addition" in p for p in r["issues"]))
        self.assertNotIn(token, repr(r))

    def test_trailing_whitespace_fails(self):
        (self.repo / "unsafe.txt").write_text("bad trailing spaces    \n")
        self.head = self.commit("bad whitespace")
        self.assertIn("Committed diff has whitespace problems", self.verify()["issues"])

    def test_ci_detached_head_is_ok(self):
        self.git("checkout", "--detach", "HEAD")
        self.assertEqual(self.verify()["branch"], "(detached)")
        self.assertEqual(self.verify()["result"], "PASS_SOURCE_PREFLIGHT")

    def test_incomplete_merge_blocks(self):
        path = Path(self.git("rev-parse", "--git-path", "MERGE_HEAD").stdout.strip())
        if not path.is_absolute():
            path = self.repo / path
        path.write_text(self.base + "\n")
        self.assertIn("Git merge/rebase/cherry-pick/revert in progress", self.verify()["issues"])

    def test_doctor_does_not_invent_approval(self):
        r = guard.assess(self.repo)
        self.assertEqual(r["sire_git_stop"], "SEPARATE_AUTHORITY_NOT_RUN")
        self.assertEqual(r["runtime_or_device_proof"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
