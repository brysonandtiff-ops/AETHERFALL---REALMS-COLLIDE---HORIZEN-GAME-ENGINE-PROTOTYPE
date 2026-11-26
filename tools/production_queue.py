#!/usr/bin/env python3
"""Read/validate the owner-governed AETHERFALL build queue. Does not execute work."""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "docs/production/WORK_QUEUE.json"
STATUSES = {"planned", "in_progress", "review", "blocked", "verified"}
SHA = re.compile(r"^[0-9a-f]{40}$")
ID = re.compile(r"^AF-[0-9]{3}$")
PHASE_ID = re.compile(r"^M[0-9]+$")


def validate(data):
    """Return structural errors only; never attest to actual external evidence."""
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
    ids_by_phase = set()
    for phase in phases:
        if not isinstance(phase, dict):
            errors.append("Invalid phase object")
            continue
        phase_id = phase.get("id")
        if not isinstance(phase_id, str) or not PHASE_ID.fullmatch(phase_id) or phase_id in ids_by_phase:
            errors.append("Invalid/duplicate phase ID")
        else:
            ids_by_phase.add(phase_id)
        if not isinstance(phase.get("name"), str) or not phase["name"].strip() or not isinstance(phase.get("gate"), str) or not phase["gate"].strip():
            errors.append("Phase name/gate missing")
    ids = {}
    for n, item in enumerate(tasks):
        if not isinstance(item, dict):
            errors.append(f"Task #{n} is not an object")
            continue
        task_id = item.get("id")
        if not isinstance(task_id, str) or not ID.fullmatch(task_id):
            errors.append(f"Invalid task ID #{n}")
            continue
        if task_id in ids:
            errors.append("Duplicate task ID: " + task_id)
        ids[task_id] = item
        if item.get("phase") not in ids_by_phase:
            errors.append("Unknown task phase: " + task_id)
        for key in ("title", "responsible_discipline"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append("Missing " + key + ": " + task_id)
        for key in ("acceptance", "required_evidence"):
            values = item.get(key)
            if not isinstance(values, list) or not values or not all(isinstance(v, str) and v.strip() for v in values):
                errors.append("Missing/invalid " + key + ": " + task_id)
        deps = item.get("depends_on")
        if not isinstance(deps, list) or not all(isinstance(v, str) for v in deps) or len(deps) != len(set(deps)):
            errors.append("Invalid/duplicate dependency: " + task_id)
        state = item.get("status")
        if state not in STATUSES:
            errors.append("Invalid status: " + task_id)
        refs = item.get("evidence_refs")
        if not isinstance(refs, list) or not all(isinstance(ref, str) and
                (ref.startswith("https://github.com/") or ref.startswith("evidence/")) and
                ".." not in ref.split("/") and ref.strip() for ref in refs):
            errors.append("Invalid evidence_refs: " + task_id)
        reason = item.get("blocked_reason")
        if state == "blocked" and (not isinstance(reason, str) or not reason.strip()):
            errors.append("Blocked task without reason: " + task_id)
        if state != "blocked" and reason is not None:
            errors.append("Nonblocked task has blocked_reason: " + task_id)
        executor = item.get("assigned_executor")
        if executor is not None and (not isinstance(executor, str) or not executor.strip()):
            errors.append("Invalid assigned_executor: " + task_id)
        if state in ("in_progress", "review") and executor is None:
            errors.append("Active/review task missing actual executor: " + task_id)
        sha = item.get("verified_commit_sha")
        if state == "verified":
            if not isinstance(sha, str) or not SHA.fullmatch(sha):
                errors.append("Verified task missing real SHA-format identity: " + task_id)
            if not refs:
                errors.append("Verified task missing proof references: " + task_id)
        elif sha is not None:
            errors.append("Unverified task claims verification SHA: " + task_id)
        if state in ("planned", "in_progress") and refs:
            errors.append("Unreviewed task holds proof references: " + task_id)
    for task_id, item in ids.items():
        deps = item.get("depends_on", [])
        if not isinstance(deps, list):
            continue
        for dep in deps:
            if dep not in ids:
                errors.append("Missing task dependency: " + task_id + " -> " + dep)
            if dep == task_id:
                errors.append("Self dependency: " + task_id)
        if item.get("status") == "verified":
            for dep in deps:
                if dep in ids and ids[dep].get("status") != "verified":
                    errors.append("Premature verified task: " + task_id + " needs " + dep)
    colors = {}
    def visit(task_id):
        color = colors.get(task_id, 0)
        if color == 1:
            errors.append("Cyclic task dependency: " + task_id)
            return
        if color == 2:
            return
        colors[task_id] = 1
        deps = ids[task_id].get("depends_on", [])
        if isinstance(deps, list):
            for dep in deps:
                if dep in ids and dep != task_id:
                    visit(dep)
        colors[task_id] = 2
    for task_id in ids:
        visit(task_id)
    return errors


def ready_tasks(data):
    """List unclaimed work whose all upstream tasks have reviewed VERIFIED status."""
    lookup = {item["id"]: item for item in data["work_items"]}
    return [item for item in data["work_items"]
            if item["status"] == "planned" and
            all(lookup[dep]["status"] == "verified" for dep in item["depends_on"])]


def load_plan(path=PLAN_PATH):
    with Path(path).open(encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate/show production tasks; never executes game development.")
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--validate", action="store_true", help="Check queue schema, gates and graph")
    choice.add_argument("--next", action="store_true", help="Show work with all prerequisites verified")
    choice.add_argument("--summary", action="store_true", help="Show per-stage task status counts")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args(argv)
    try:
        data = load_plan()
    except (OSError, ValueError) as exc:
        print("FAIL: cannot read build queue: " + str(exc), file=sys.stderr)
        return 1
    errors = validate(data)
    if errors:
        for err in errors:
            print("FAIL: " + err, file=sys.stderr)
        return 1
    if args.validate:
        print(f"PASS: production plan schema, {len(data['work_items'])} tasks, dependencies and evidence-state safety (PLAN ONLY)")
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
