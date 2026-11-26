"""Adversarial tests for the roadmap dependency and evidence gate, not gameplay proof."""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("aetherfall_queue", ROOT / "tools/production_queue.py")
queue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(queue)


class ProductionPlanTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "docs/production/WORK_QUEUE.json").read_text(encoding="utf-8"))

    def task(self, ident):
        return next(x for x in self.data["work_items"] if x["id"] == ident)

    def assert_bad(self, fragment):
        errors = queue.validate(self.data)
        self.assertTrue(any(fragment in issue for issue in errors), errors)

    def test_initial_queue_valid(self):
        self.assertEqual(queue.validate(self.data), [])
        self.assertTrue(all(x["status"] == "planned" for x in self.data["work_items"]))

    def test_next_tasks_respect_prerequisites(self):
        self.assertEqual([x["id"] for x in queue.ready_tasks(self.data)],
                         ["AF-001", "AF-002", "AF-003", "AF-004"])
        self.task("AF-001")["status"] = "verified"
        self.task("AF-001")["verified_commit_sha"] = "a" * 40
        self.task("AF-001")["evidence_refs"] = ["https://github.com/example/repo/pull/123"]
        self.assertNotIn("AF-010", [x["id"] for x in queue.ready_tasks(self.data)])
        self.assertNotIn("AF-006", [x["id"] for x in queue.ready_tasks(self.data)])

    def test_missing_dependency_fails(self):
        self.task("AF-010")["depends_on"] = ["AF-999"]
        self.assert_bad("Missing task dependency")

    def test_cycle_fails(self):
        self.task("AF-001")["depends_on"] = ["AF-010"]
        self.assert_bad("Cyclic task dependency")

    def test_duplicate_id_fails(self):
        self.task("AF-002")["id"] = "AF-001"
        self.assert_bad("Duplicate task ID")

    def test_false_verified_without_proof_fails(self):
        self.task("AF-001")["status"] = "verified"
        self.assert_bad("Verified task missing real SHA-format identity")
        self.assert_bad("Verified task missing proof references")

    def test_verification_before_dependency_fails(self):
        self.task("AF-010")["status"] = "verified"
        self.task("AF-010")["verified_commit_sha"] = "b" * 40
        self.task("AF-010")["evidence_refs"] = ["https://github.com/example/repo/actions/runs/1"]
        self.assert_bad("Premature verified task")

    def test_blocked_must_have_reason(self):
        self.task("AF-001")["status"] = "blocked"
        self.assert_bad("Blocked task without reason")

    def test_active_must_have_real_executor(self):
        self.task("AF-001")["status"] = "in_progress"
        self.assert_bad("Active/review task missing actual executor")

    def test_unreviewed_proof_claim_fails(self):
        self.task("AF-001")["evidence_refs"] = ["evidence/godot/anything.png"]
        self.assert_bad("Unreviewed task holds proof references")

    def test_cli_reports_initial_next(self):
        result = subprocess.run([sys.executable, str(ROOT / "tools/production_queue.py"), "--next"],
                                cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("AF-001", result.stdout)
        self.assertIn("AF-004", result.stdout)
        self.assertNotIn("AF-010", result.stdout)


if __name__ == "__main__":
    unittest.main()
