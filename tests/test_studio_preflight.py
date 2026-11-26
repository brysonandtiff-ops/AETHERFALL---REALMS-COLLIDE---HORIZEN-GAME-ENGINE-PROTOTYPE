"""Preflight CLI must remain executable, read-only and honest about native evidence."""
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("aetherfall_preflight", ROOT / "tools/studio_preflight.py")
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


class PreflightTests(unittest.TestCase):
    def test_checklist_contains_real_validators(self):
        paths = [args[0] for _, args in preflight.CHECKS]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertIn("tools/validate_structure.py", paths)
        self.assertIn("tools/validate_studio_layout.py", paths)
        self.assertIn("tools/validate_asset_handoffs.py", paths)
        self.assertIn("tools/production_queue.py", paths)

    def test_quick_runs_real_local_source_checks(self):
        process = subprocess.run(
            [sys.executable, str(ROOT / "tools/studio_preflight.py"), "--quick"],
            cwd=ROOT, capture_output=True, text=True, check=False, timeout=100,
        )
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertIn("PREFLIGHT PASS:", process.stdout)
        self.assertIn("4 unblocked planned task(s)", process.stdout)
        self.assertIn("are NOT certified", process.stdout)
        self.assertNotIn("Adversarial/regression tests", process.stdout)

    def test_help_does_not_execute_work(self):
        process = subprocess.run(
            [sys.executable, str(ROOT / "tools/studio_preflight.py"), "--help"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(process.returncode, 0)
        self.assertIn("--quick", process.stdout)
        self.assertNotIn("PREFLIGHT PASS:", process.stdout)


if __name__ == "__main__":
    unittest.main()
