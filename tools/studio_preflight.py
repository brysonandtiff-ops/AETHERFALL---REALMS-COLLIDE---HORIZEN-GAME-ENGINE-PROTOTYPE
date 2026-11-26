#!/usr/bin/env python3
"""One local studio preflight; executes real source tests, NOT native visual proof."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = (
    ("Repository and source safety", ("tools/validate_structure.py",)),
    ("Godot studio layout", ("tools/validate_studio_layout.py",)),
    ("Original asset receipts", ("tools/validate_asset_handoffs.py", "--validate")),
    ("Production task dependencies", ("tools/production_queue.py", "--validate")),
)
TESTS = ("-m", "unittest", "discover", "-s", "tests", "-v")
NEXT = ("tools/production_queue.py", "--next")


def run_checked(label, args, timeout=120):
    print("\n== " + label + " ==", flush=True)
    try:
        result = subprocess.run([sys.executable, *args], cwd=ROOT,
                                timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print("FAIL: " + label + " could not finish: " + type(exc).__name__, file=sys.stderr)
        return False
    if result.returncode:
        print("FAIL: " + label + " exit=" + str(result.returncode), file=sys.stderr)
        return False
    print("PASS: " + label + " (source-level only)", flush=True)
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run actual local validators and Python tests, not a fake gameplay build."
    )
    parser.add_argument("--quick", action="store_true", help="Skip the Python unit tests; validate sources only.")
    args = parser.parse_args(argv)
    passed = []
    for name, command in CHECKS:
        passed.append(run_checked(name, command))
    if not args.quick:
        passed.append(run_checked("Adversarial/regression tests", TESTS))
    if all(passed):
        print("\n== Next eligible work orders ==", flush=True)
        passed.append(run_checked("Task queue", NEXT))
    if not all(passed):
        print("\nPREFLIGHT FAILED: repair errors before promoting this change.", file=sys.stderr)
        return 1
    print("\nPREFLIGHT PASS: local source/plan checks only; graphics, Blender, "
          "multiplayer and physical devices are NOT certified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
