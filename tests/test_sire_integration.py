"""Tests for safe S.I.R.E. interface declarations and command dispatch boundaries."""
import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("aetherfall_cli", ROOT / "tools/aetherfall.py")
CLI = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLI)


class DeveloperInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.config = CLI.read_json(CLI.MANIFEST)
        self.shortcuts = CLI.read_json(CLI.SHORTCUTS)
        self.order = CLI.show_order("AETHERFALL-DEVOPS-001")

    def invoke(self, *parts):
        return subprocess.run(
            [sys.executable, str(ROOT / "tools/aetherfall.py"), *parts],
            cwd=ROOT, text=True, capture_output=True, check=False, timeout=30
        )

    def test_manifest_has_no_live_executor_claim(self):
        self.assertEqual(CLI.config_issues(self.config, self.shortcuts), [])

    def test_six_unique_routes_without_duplicate_master(self):
        self.assertEqual(set(self.config["routes"]), CLI.ROUTE_IDS)
        self.assertEqual(self.config["upstream"]["interface"], "S.I.R.E AI")
        self.assertFalse(self.config["upstream"]["verified_live_executor"])

    def test_doctor_is_honest_about_connections(self):
        result = self.invoke("doctor", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["integration_contract"], "PASS")
        self.assertEqual(report["sire_runner"], "NOT_CONNECTED")
        self.assertEqual(report["native_gameplay"], "NOT_RUN")

    def test_shortcut_t_is_non_executing(self):
        result = self.invoke("cmd", "T", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["action"], "check")
        self.assertFalse(data["automatically_dispatched"])

    def test_unknown_shortcut_fails_closed(self):
        self.assertEqual(self.invoke("cmd", "DROP").returncode, 2)

    def test_work_list_contains_exact_order(self):
        result = self.invoke("work", "list", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(any(x["id"] == "AETHERFALL-DEVOPS-001" for x in data))

    def test_work_order_has_governance_contract(self):
        self.assertEqual(CLI.order_issues(self.order), [])
        self.assertEqual(self.order["authorised_executor"]["master"], "S.I.R.E AI")
        self.assertEqual(self.order["status"], "STAGED_FOR_REVIEW")

    def test_handoff_is_read_only_and_source_pinned(self):
        result = self.invoke("handoff", "AETHERFALL-DEVOPS-001", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["kind"], "SIRE_WORK_ORDER_PROPOSAL")
        self.assertRegex(data["source_commit_sha"], r"^[0-9a-f]{40}$")
        self.assertFalse(data["dispatched"])
        self.assertFalse(data["approval_gates"]["network_call"])

    def test_bad_work_order_name_rejected(self):
        self.assertEqual(self.invoke("handoff", "../../secrets").returncode, 2)

    def test_unapproved_master_rejected(self):
        changed = copy.deepcopy(self.config)
        changed["upstream"]["interface"] = "NEW_MASTER"
        self.assertTrue(any("master identity" in x for x in
                            CLI.config_issues(changed, self.shortcuts)))

    def test_unsafe_skill_traversal_rejected(self):
        changed = copy.deepcopy(self.config)
        changed["routes"]["gameplay"]["skill"] = ".sire/skills/../../AGENTS.md"
        self.assertTrue(any("Missing/unsafe skill" in x for x in
                            CLI.config_issues(changed, self.shortcuts)))

    def test_fake_runner_connection_rejected(self):
        changed = copy.deepcopy(self.config)
        changed["connection_boundaries"]["remote_runner"]["status"] = "CONNECTED"
        self.assertTrue(any("runner" in x for x in CLI.config_issues(changed, self.shortcuts)))

    def test_auto_merge_risk_rejected(self):
        changed = copy.deepcopy(self.config)
        changed["release_policy"]["auto_merge"] = True
        self.assertTrue(any("automatic release" in x for x in
                            CLI.config_issues(changed, self.shortcuts)))

    def test_proof_fabrication_rejected(self):
        changed = copy.deepcopy(self.order)
        changed["evidence"]["native_godot"] = "PASS"
        self.assertIn("Unproved work-order evidence claim", CLI.order_issues(changed))

    def test_work_order_cannot_claim_completed(self):
        changed = copy.deepcopy(self.order)
        changed["status"] = "COMPLETE"
        self.assertIn("Work order claims an unverified completion", CLI.order_issues(changed))

    def test_source_branch_never_installs_mcp_plugin(self):
        self.assertNotIn("subprocess", self.invoke("handoff", "AETHERFALL-DEVOPS-001").stderr)
        # A handoff is a proposal, not a side effect in an outside app.


if __name__ == "__main__":
    unittest.main()
