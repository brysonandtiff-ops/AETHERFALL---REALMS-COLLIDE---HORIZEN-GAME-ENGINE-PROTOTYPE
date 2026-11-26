#!/usr/bin/env python3
"""Validate an owner-reviewed work queue; never execute tasks or attest external proof."""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "docs/production/WORK_QUEUE.json"
MAX_PLAN_BYTES = 2 * 1024 * 1024
STATUSES = frozenset({"planned", "in_progress", "review", "blocked", "verified"})
SHA = re.compile(r"^[0-9a-f]{40}$")
ID = re.compile(r"^AF-[0-9]{3}$")
PHASE_ID = re.compile(r"^M[0-9]+$")
IMMUTABLE_TASK_KEYS = ("id", "title", "phase", "depends_on", "responsible_discipline",
                       "acceptance", "required_evidence")
TRANSITIONS = {
    "planned": {"planned", "in_progress", "review", "blocked"},
    "in_progress": {"in_progress", "review", "planned", "blocked"},
    "review": {"review", "verified", "in_progress", "blocked"},
    "blocked": {"blocked", "planned", "in_progress", "review"},
    "verified": {"verified", "blocked", "planned"},
}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def valid_evidence_ref(raw):
    """Only structurally allow local evidence/ or true HTTPS github.com references."""
    if not nonempty(raw) or "\\" in raw or any(ord(c) < 32 for c in raw):
        return False
    if raw.startswith("evidence/"):
        parts = raw.split("/")
        return len(parts) >= 3 and all(part not in ("", ".", "..") and ":" not in part
                                        and "%" not in part and "?" not in part
                                        and "#" not in part for part in parts)
    try:
        url = urlsplit(raw)
    except ValueError:
        return False
    parts = url.path.split("/")
    return (url.scheme == "https" and url.netloc == "github.com" and
            not url.username and not url.password and not url.query and not url.fragment and
            len(parts) >= 3 and all(part and part not in (".", "..") and "%" not in part
                                    for part in parts[1:]))


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field: " + key)
        result[key] = value
    return result


def load_plan(path=PLAN_PATH):
    path = Path(path)
    if path.stat().st_size > MAX_PLAN_BYTES:
        raise ValueError("Build plan larger than 2 MiB; review scope before accepting")
    with path.open(encoding="utf-8") as stream:
        return json.load(stream, object_pairs_hook=reject_duplicate_keys)


def validate(data):
    """Validate schema, task status, dependencies and proof *shape*, not proof authenticity."""
    errors = []
    if not isinstance(data, dict) or data.get("schema_version") != 1 or data.get("project") != "AETHERFALL: REALMS COLLIDE":
        return ["Build plan schema/project identity invalid"]
    phases = data.get("phases")
    tasks = data.get("work_items")
    if not isinstance(phases, list) or not phases:
        errors.append("Nonempty phases required")
        phases = []
    if not isinstance(tasks, list) or not tasks:
        return errors + ["Nonempty work_items required"]
    phase_index = {}
    for p, phase in enumerate(phases):
        if not isinstance(phase, dict):
            errors.append("Invalid phase object")
            continue
        ident = phase.get("id")
        if not isinstance(ident, str) or not PHASE_ID.fullmatch(ident) or ident in phase_index:
            errors.append("Invalid/duplicate phase ID")
            continue
        phase_index[ident] = p
        if not nonempty(phase.get("name")) or not nonempty(phase.get("gate")):
            errors.append("Phase name/gate missing: " + ident)
    ids = {}
    for n, item in enumerate(tasks):
        if not isinstance(item, dict):
            errors.append("Task #" + str(n) + " is not an object")
            continue
        task_id = item.get("id")
        if not isinstance(task_id, str) or not ID.fullmatch(task_id):
            errors.append("Invalid task ID #" + str(n))
            continue
        if task_id in ids:
            errors.append("Duplicate task ID: " + task_id)
            continue
        ids[task_id] = item
        phase = item.get("phase")
        if not isinstance(phase, str) or phase not in phase_index:
            errors.append("Unknown task phase: " + task_id)
        for key in ("title", "responsible_discipline"):
            if not nonempty(item.get(key)):
                errors.append("Missing " + key + ": " + task_id)
        for key in ("acceptance", "required_evidence"):
            values = item.get(key)
            if not isinstance(values, list) or not values or not all(nonempty(v) for v in values):
                errors.append("Missing/invalid " + key + ": " + task_id)
        deps = item.get("depends_on")
        if not isinstance(deps, list) or not all(isinstance(v, str) for v in deps):
            errors.append("Invalid/duplicate dependency: " + task_id)
        elif len(deps) != len(set(deps)):
            errors.append("Invalid/duplicate dependency: " + task_id)
        state = item.get("status")
        if not isinstance(state, str) or state not in STATUSES:
            errors.append("Invalid status: " + task_id)
        refs = item.get("evidence_refs")
        if not isinstance(refs, list) or not all(valid_evidence_ref(ref) for ref in refs):
            errors.append("Invalid evidence_refs: " + task_id)
            refs = []
        reason = item.get("blocked_reason")
        if state == "blocked" and not nonempty(reason):
            errors.append("Blocked task without reason: " + task_id)
        if state != "blocked" and reason is not None:
            errors.append("Nonblocked task has blocked_reason: " + task_id)
        executor = item.get("assigned_executor")
        if executor is not None and not nonempty(executor):
            errors.append("Invalid assigned_executor: " + task_id)
        if state in ("in_progress", "review", "verified") and not nonempty(executor):
            errors.append("Active/review/verified task missing actual executor: " + task_id)
        if state == "planned" and executor is not None:
            errors.append("Planned task claims active executor: " + task_id)
        reviewed_by = item.get("reviewed_by")
        if state == "verified" and not nonempty(reviewed_by):
            errors.append("Verified task missing authorised reviewer: " + task_id)
        elif state != "verified" and reviewed_by is not None:
            errors.append("Unverified task claims reviewer approval: " + task_id)
        sha = item.get("verified_commit_sha")
        if state == "verified":
            if not isinstance(sha, str) or not SHA.fullmatch(sha):
                errors.append("Verified task missing real SHA-format identity: " + task_id)
            if not refs:
                errors.append("Verified task missing proof references: " + task_id)
        elif sha is not None:
            errors.append("Unverified task claims verification SHA: " + task_id)
        if state == "review" and not refs:
            errors.append("Review task missing candidate evidence: " + task_id)
        if state in ("planned", "in_progress") and refs:
            errors.append("Unreviewed task holds proof references: " + task_id)
    for task_id, item in ids.items():
        deps = item.get("depends_on")
        if not isinstance(deps, list) or not all(isinstance(dep, str) for dep in deps):
            continue
        for dep in deps:
            if dep not in ids:
                errors.append("Missing task dependency: " + task_id + " -> " + dep)
                continue
            if dep == task_id:
                errors.append("Self dependency: " + task_id)
            if (isinstance(item.get("phase"), str) and
                    isinstance(ids[dep].get("phase"), str) and
                    item["phase"] in phase_index and ids[dep]["phase"] in phase_index and
                    phase_index[ids[dep]["phase"]] > phase_index[item["phase"]]):
                errors.append("Task depends on later phase: " + task_id + " -> " + dep)
            if item.get("status") in ("in_progress", "review", "verified") and ids[dep].get("status") != "verified":
                errors.append("Premature active/verified task: " + task_id + " needs " + dep)
                if item.get("status") == "verified":
                    errors.append("Premature verified task: " + task_id + " needs " + dep)
    # Iterative depth-first traversal avoids unbounded recursion on malicious plans.
    colors = {}
    for origin in ids:
        if colors.get(origin) == 2:
            continue
        stack = [(origin, False)]
        while stack:
            task_id, leaving = stack.pop()
            if leaving:
                colors[task_id] = 2
                continue
            if colors.get(task_id) == 2:
                continue
            if colors.get(task_id) == 1:
                errors.append("Cyclic task dependency: " + task_id)
                continue
            colors[task_id] = 1
            stack.append((task_id, True))
            deps = ids[task_id].get("depends_on")
            if isinstance(deps, list):
                for dep in reversed(deps):
                    if isinstance(dep, str) and dep in ids and dep != task_id:
                        if colors.get(dep) == 1:
                            errors.append("Cyclic task dependency: " + task_id + " -> " + dep)
                        elif colors.get(dep) != 2:
                            stack.append((dep, False))
    return errors


def audit_baseline(baseline, current):
    """Reject deletion/rewrite of committed tasks and unsafe state transitions."""
    errors = ["Baseline: " + e for e in validate(baseline)] + validate(current)
    if errors:
        return errors
    if (baseline.get("schema_version"), baseline.get("project")) != (
            current.get("schema_version"), current.get("project")):
        errors.append("Build plan identity changed")
    old_phases, new_phases = baseline["phases"], current["phases"]
    if new_phases[:len(old_phases)] != old_phases:
        errors.append("Existing production phases removed or rewritten")
    old_tasks, new_tasks = baseline["work_items"], current["work_items"]
    old_ids = [t["id"] for t in old_tasks]
    new_ids = [t["id"] for t in new_tasks]
    if new_ids[:len(old_ids)] != old_ids:
        errors.append("Existing tasks removed, renamed or reordered")
        return errors
    for old, new in zip(old_tasks, new_tasks):
        task_id = old["id"]
        for key in IMMUTABLE_TASK_KEYS:
            if old.get(key) != new.get(key):
                errors.append("Existing task contract rewritten: " + task_id + " / " + key)
        if new["status"] not in TRANSITIONS[old["status"]]:
            errors.append("Illegal task status transition: " + task_id + " " +
                          old["status"] + " -> " + new["status"])
        if old["status"] == new["status"] == "verified":
            for key in ("verified_commit_sha", "evidence_refs", "reviewed_by", "assigned_executor"):
                if old.get(key) != new.get(key):
                    errors.append("Already-verified proof rewritten: " + task_id)
    for item in new_tasks[len(old_tasks):]:
        if item["status"] != "planned":
            errors.append("New task starts as unreviewed completed work: " + item["id"])
    return errors


def ready_tasks(data):
    """Only unclaimed work with all required verified predecessors."""
    lookup = {item["id"]: item for item in data["work_items"]}
    return [item for item in data["work_items"]
            if item["status"] == "planned" and
            all(lookup[dep]["status"] == "verified" for dep in item["depends_on"])]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate/read production tasks; never execute work.")
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--validate", action="store_true", help="Check schema, state and dependency graph")
    choice.add_argument("--next", action="store_true", help="Show unblocked planned tasks")
    choice.add_argument("--summary", action="store_true", help="Show per-stage status counts")
    choice.add_argument("--audit-baseline", metavar="FILE", help="Reject unsafe changes vs prior committed plan")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args(argv)
    try:
        data = load_plan()
        failures = validate(data)
        if args.audit_baseline:
            failures += audit_baseline(load_plan(args.audit_baseline), data)
    except (OSError, ValueError, UnicodeError) as exc:
        print("FAIL: cannot parse build queue: " + str(exc), file=sys.stderr)
        return 1
    if failures:
        for failure in sorted(set(failures)):
            print("FAIL: " + failure, file=sys.stderr)
        return 1
    if args.audit_baseline:
        print("PASS: previous tasks retained, states transitioned safely, no existing proof rewritten (STRUCTURE ONLY)")
        return 0
    if args.validate:
        print(f"PASS: production plan schema, {len(data['work_items'])} tasks, dependencies and proof-state safety (PLAN ONLY)")
        return 0
    if args.summary:
        for phase in data["phases"]:
            tasks = [t for t in data["work_items"] if t["phase"] == phase["id"]]
            states = ", ".join(f"{k}={sum(t['status']==k for t in tasks)}" for k in sorted(STATUSES) if any(t["status"]==k for t in tasks))
            print(f"{phase['id']} {phase['name']}: {len(tasks)} tasks [{states}]")
        return 0
    if args.limit < 1:
        print("FAIL: --limit must be positive", file=sys.stderr)
        return 1
    todo = ready_tasks(data)
    for item in todo[:args.limit]:
        print(f"{item['id']} [{item['phase']}] {item['title']} — {item['responsible_discipline']}")
        print("  Accept: " + item["acceptance"][0])
        print("  Proof:  " + item["required_evidence"][0])
    print(f"NEXT: {len(todo)} unblocked planned task(s); no automatic executor was started")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
