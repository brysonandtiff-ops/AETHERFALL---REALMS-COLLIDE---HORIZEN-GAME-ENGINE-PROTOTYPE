#!/usr/bin/env python3
"""Compare the canonical art registry to its committed base (STRUCTURE ONLY).

Existing character/weapon IDs and source directories are immutable by default.
Appending approved planned IDs requires review and the normal source validator.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "art/asset_registry.json"
MAX_BYTES = 1024 * 1024
ASSET_ID = re.compile(r"^(?:CHR|WPN)_[A-Za-z][A-Za-z0-9_]*$")
LOCKED_KEYS = (
    "id", "type", "role", "status", "concept_status",
    "legacy_alias", "concept_dir", "source_dir", "runtime_dir",
)


def reject_dupes(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("Duplicate canonical art JSON field: " + key)
        obj[key] = value
    return obj


def load_registry(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Missing/oversized canonical art registry")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_dupes)


def audit_registry(baseline, current):
    errors = []
    if not isinstance(baseline, dict) or not isinstance(current, dict):
        return ["Canonical art baseline/schema invalid"]
    if (baseline.get("schema_version"), baseline.get("project")) != (1, "AETHERFALL: REALMS COLLIDE"):
        errors.append("Art baseline identity invalid")
    if (current.get("schema_version"), current.get("project")) != (1, "AETHERFALL: REALMS COLLIDE"):
        errors.append("Art current identity invalid")
    old = baseline.get("assets")
    new = current.get("assets")
    if not isinstance(old, list) or not isinstance(new, list) or not old or not new:
        return errors + ["Canonical art assets must remain nonempty lists"]
    if any(not isinstance(x, dict) or not isinstance(x.get("id"), str) for x in old + new):
        return errors + ["Malformed canonical asset objects"]
    old_ids = [x["id"] for x in old]
    new_ids = [x["id"] for x in new]
    if old_ids != new_ids[:len(old_ids)]:
        errors.append("Canonical art IDs removed, renamed or reordered")
        return errors
    if len({x.casefold() for x in new_ids}) != len(new_ids):
        errors.append("Duplicate canonical asset ID")
    for older, newer in zip(old, new):
        for key in LOCKED_KEYS:
            if older.get(key) != newer.get(key):
                errors.append("Approved art identity/source contract rewritten: " + older["id"] + " / " + key)
    for entry in new[len(old):]:
        if not ASSET_ID.fullmatch(entry["id"]):
            errors.append("Invalid new canonical art asset ID")
        if entry.get("status") != "reserved_no_source":
            errors.append("New asset falsely claims produced source: " + entry["id"])
        if entry.get("concept_status") not in (
                "aetherfall_approved", "aetherfall_design_brief",
                "legacy_owner_approved_candidate_for_aetherfall"):
            errors.append("New asset has invalid approval state: " + entry["id"])
    return errors


def audit_removed_source_files(root, git_base):
    """Reject deletion or rename of art/evidence in PRs; doesn't modify Git history."""
    if not isinstance(git_base, str) or not re.fullmatch(r"[0-9a-f]{40}", git_base):
        return ["Invalid Git baseline revision"]
    try:
        check = subprocess.run(
            ["git", "diff", "--diff-filter=D", "--no-renames", "--name-only", "-z",
             git_base, "HEAD", "--", "art/", "evidence/"],
            cwd=root, check=True, capture_output=True, timeout=20,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return ["Cannot compare protected original art/evidence with Git baseline"]
    errors = []
    for item in check.stdout.split(b"\x00"):
        if item:
            name = item.decode("utf-8", errors="replace")
            errors.append("Protected original art/evidence deleted or renamed: " + name)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description="Guard canonical art identity and evidence history.")
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--git-base", help="Optional exact 40-char Git base commit for source deletion check")
    args = parser.parse_args(argv)
    try:
        errors = audit_registry(load_registry(args.baseline), load_registry(REGISTRY))
    except (OSError, ValueError, UnicodeError) as exc:
        print("FAIL: art history validation could not read input: " + str(exc), file=sys.stderr)
        return 1
    if args.git_base:
        errors += audit_removed_source_files(ROOT, args.git_base)
    if errors:
        for error in sorted(set(errors)):
            print("FAIL: " + error, file=sys.stderr)
        return 1
    print("PASS: art IDs, approved source paths, history and protected evidence not silently rewritten (SOURCE ONLY)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
