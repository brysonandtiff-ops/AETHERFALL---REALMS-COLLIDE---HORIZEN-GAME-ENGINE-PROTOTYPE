#!/usr/bin/env python3
"""AETHERFALL local command centre: fail-closed, offline and dependency-free.

This command does not launch S.I.R.E. workers, install plugins, call MCP,
merge PRs or send network requests. External execution requires an
independently authorised S.I.R.E. runner and a real source-pinned receipt.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".sire/integration.json"
SHORTCUTS = ROOT / ".sire/commands.json"
ORDERS = ROOT / ".sire/work-orders"
EXPECTED_PROJECT = "AETHERFALL: REALMS COLLIDE"
EXPECTED_REPO = "brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE"
EXPECTED_ENGINE = "4.7.2.stable"
ORDER_ID = re.compile(r"^AETHERFALL-[A-Z0-9-]{2,64}$")
ROUTE_IDS = {"gameplay", "character_art", "runtime_qa", "git", "security", "integrations"}
ACTIONS = {"doctor", "status", "routes", "skills", "calls", "check", "work list", "work new", "handoff"}
ALLOWED_ORDER_STATES = {"PLANNED", "STAGED_FOR_REVIEW", "IN_REVIEW", "BLOCKED"}


def read_json(path: Path) -> dict:
    """Load only explicitly selected local JSON files."""
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path.name}")
    return value


def relative_safe(raw: object, prefix: str, root: Path = ROOT) -> Path | None:
    if not isinstance(raw, str) or not raw.startswith(prefix):
        return None
    parts = raw.split("/")
    if any(part in {"", ".", ".."} or ":" in part or "\\" in part for part in parts):
        return None
    candidate = root.joinpath(*parts)
    if not candidate.resolve().is_relative_to(root.resolve()) or candidate.is_symlink():
        return None
    return candidate


def config_issues(config: dict, shortcuts: dict, root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    if config.get("schema_version") != 1 or config.get("project") != EXPECTED_PROJECT:
        issues.append("Integration manifest project/schema mismatch")
    if config.get("repository") != EXPECTED_REPO or config.get("game_path") != "game/project.godot":
        issues.append("Integration repository/project path mismatch")
    if config.get("expected_engine") != EXPECTED_ENGINE:
        issues.append("Unapproved Godot version change")
    upstream = config.get("upstream")
    if not isinstance(upstream, dict) or upstream.get("repository") != "brysonandtiff-ops/SIRE" or upstream.get("interface") != "S.I.R.E AI":
        issues.append("Missing existing S.I.R.E master identity")
    elif upstream.get("connection_status") != "NOT_CONNECTED" or upstream.get("verified_live_executor") is not False:
        issues.append("Unverified upstream connection claim")
    policy = config.get("release_policy")
    if not isinstance(policy, dict) or any(policy.get(name) is not False for name in (
        "auto_merge", "auto_deploy", "paid_apis", "destructive_actions"
    )):
        issues.append("Unapproved automatic release/spend/destructive permissions")
    routes = config.get("routes")
    if not isinstance(routes, dict) or set(routes) != ROUTE_IDS:
        issues.append("Routes must match the six approved responsibilities")
        routes = routes if isinstance(routes, dict) else {}
    for name, route in routes.items():
        if not isinstance(route, dict):
            issues.append("Malformed route: " + name)
            continue
        path = relative_safe(route.get("skill"), ".sire/skills/", root)
        if path is None or path.suffix != ".md" or not path.is_file():
            issues.append("Missing/unsafe skill: " + name)
        if route.get("upstream_cli", "").startswith("python -m sire") is False:
            issues.append("Unsafe upstream call suggestion: " + name)
        if not isinstance(route.get("specialist"), str) or not route["specialist"].strip():
            issues.append("Missing specialist label: " + name)
    connections = config.get("connection_boundaries")
    if not isinstance(connections, dict) or connections.get("remote_runner", {}).get("status") != "NOT_CONNECTED":
        issues.append("Unverified remote runner promoted")
    if not isinstance(shortcuts, dict) or shortcuts.get("schema_version") != 1:
        issues.append("Shortcut schema invalid")
        keys = {}
    else:
        keys = shortcuts.get("shortcuts")
        if not isinstance(keys, dict):
            issues.append("Shortcut definitions missing")
            keys = {}
    for key, item in keys.items():
        if not re.fullmatch(r"[A-Z][A-Z0-9]{0,11}", key):
            issues.append("Invalid shortcut key")
        if not isinstance(item, dict):
            issues.append("Malformed shortcut: " + key)
            continue
        if item.get("route") not in ROUTE_IDS or item.get("action") not in ACTIONS:
            issues.append("Unsafe shortcut action/route: " + key)
    return issues


def order_issues(order: dict, routes: set[str] = ROUTE_IDS) -> list[str]:
    errors: list[str] = []
    if order.get("schema_version") != 1 or order.get("project") != EXPECTED_PROJECT:
        errors.append("Work order project/schema mismatch")
    if order.get("repository") != EXPECTED_REPO:
        errors.append("Work order repository mismatch")
    if not isinstance(order.get("id"), str) or not ORDER_ID.fullmatch(order["id"]):
        errors.append("Invalid work order ID")
    if not isinstance(order.get("goal"), str) or len(order["goal"].strip()) < 12:
        errors.append("Missing meaningful goal")
    executor = order.get("authorised_executor")
    if not isinstance(executor, dict) or executor.get("master") != "S.I.R.E AI":
        errors.append("Work order must reuse sole S.I.R.E master")
    else:
        if executor.get("team") not in routes:
            errors.append("Unrecognised work-order team")
        if executor.get("execution_status") != "NOT_CONNECTED":
            errors.append("Executor connection cannot be claimed by JSON")
    if order.get("status") not in ALLOWED_ORDER_STATES:
        errors.append("Work order claims an unverified completion")
    for key in ("requirements", "completion_criteria"):
        if not isinstance(order.get(key), list) or not order[key] or not all(
            isinstance(x, str) and x.strip() for x in order[key]
        ):
            errors.append("Missing " + key)
    evidence = order.get("evidence")
    if not isinstance(evidence, dict) or any(
        not isinstance(value, str) or not value.startswith(("NOT_RUN", "BLOCKED"))
        for value in evidence.values()
    ):
        errors.append("Unproved work-order evidence claim")
    if not isinstance(order.get("rollback"), str) or not order["rollback"].strip():
        errors.append("Missing rollback instructions")
    return errors


def all_issues(root: Path = ROOT) -> list[str]:
    try:
        config = read_json(root / ".sire/integration.json")
        keys = read_json(root / ".sire/commands.json")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return ["Missing/malformed integration manifest: " + str(exc)]
    problems = config_issues(config, keys, root)
    path = root / ".sire/work-orders"
    ids: set[str] = set()
    if not path.is_dir():
        return problems + ["Missing work-order directory"]
    for filename in sorted(path.glob("*.json")):
        try:
            order = read_json(filename)
            if filename.stem != order.get("id"):
                problems.append("Work order filename mismatch: " + filename.name)
            if filename.stem in ids:
                problems.append("Duplicate work-order name")
            ids.add(filename.stem)
            problems.extend(f"{filename.name}: {x}" for x in order_issues(order))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            problems.append(f"Malformed work order {filename.name}: {exc}")
    if not ids:
        problems.append("No work orders found")
    return problems


def git_observation() -> dict:
    git = shutil.which("git")
    if not git:
        return {"status": "NOT_CONNECTED", "sha": None, "clean": False, "branch": None}
    def call(*args):
        try:
            p = subprocess.run([git, "-C", str(ROOT), *args], capture_output=True,
                               text=True, timeout=8, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return None
        return p.stdout.strip() if p.returncode == 0 else None
    sha = call("rev-parse", "--verify", "HEAD")
    porcelain = call("status", "--porcelain", "--untracked-files=normal")
    branch = call("branch", "--show-current")
    valid_sha = bool(sha and re.fullmatch(r"[0-9a-f]{40}", sha))
    return {"status": "OBSERVED" if valid_sha else "NOT_CONNECTED",
            "sha": sha if valid_sha else None,
            "clean": porcelain == "" if porcelain is not None else False,
            "branch": branch or "(detached)"}


def doctor_report(root: Path = ROOT) -> dict:
    problems = all_issues(root)
    validator = root / "tools/validate_structure.py"
    if not validator.is_file():
        problems.append("Missing static repository validator")
        static_result = "FAIL"
    else:
        p = subprocess.run([sys.executable, str(validator)], cwd=root,
                           capture_output=True, text=True, timeout=30, check=False)
        static_result = "PASS" if p.returncode == 0 else "FAIL"
        if p.returncode:
            problems.append("Static validator failed: " + (p.stderr.strip() or p.stdout.strip()))
    return {
        "project": EXPECTED_PROJECT,
        "integration_contract": "PASS" if not problems else "FAIL",
        "static_repository": static_result,
        "issues": problems,
        "git": git_observation(),
        "sire_runner": "NOT_CONNECTED",
        "sire_mcp": "NOT_CONNECTED",
        "sire_plugins": "DEFINED_NOT_CONNECTED",
        "godot_binary": "PRESENT_VERSION_UNVERIFIED" if shutil.which("godot") else "NOT_INSTALLED_IN_THIS_ENVIRONMENT",
        "native_gameplay": "NOT_RUN",
        "graphical_proof": "NOT_RUN",
        "note": "A local manifest/CLI cannot authenticate S.I.R.E. or certify a native game."
    }


def render(value: object, json_output: bool) -> None:
    if json_output:
        print(json.dumps(value, indent=2, sort_keys=True))
    elif isinstance(value, dict):
        for key, item in value.items():
            if key == "issues" and item == []:
                print("issues: none")
            else:
                print(f"{key}: {item}")
    elif isinstance(value, list):
        for item in value:
            print(item)
    else:
        print(value)


def commands_report() -> dict:
    return read_json(SHORTCUTS)["shortcuts"]


def list_orders() -> list[dict]:
    return [
        {"id": item["id"], "status": item["status"],
         "team": item["authorised_executor"]["team"], "goal": item["goal"]}
        for file in sorted(ORDERS.glob("*.json"))
        for item in [read_json(file)]
    ]


def show_order(order_id: str) -> dict:
    if not ORDER_ID.fullmatch(order_id):
        raise ValueError("Invalid work-order identifier")
    path = ORDERS / (order_id + ".json")
    order = read_json(path)
    problems = order_issues(order)
    if problems or order.get("id") != order_id:
        raise ValueError("Invalid work order: " + "; ".join(problems))
    return order



def available_calls() -> dict:
    """Display upstream *suggestions*, never run commands or authenticate apps."""
    config = read_json(MANIFEST)
    return {
        route_id: {
            "owner": "S.I.R.E AI",
            "specialist": data["specialist"],
            "suggested_upstream_command": data["upstream_cli"],
            "connection": "DEFINED_NOT_CONNECTED",
            "invoked": False,
            "needs_authenticated_runner": True,
        }
        for route_id, data in config["routes"].items()
    }


def create_order(order_id: str, team: str, goal: str, criteria: list[str], root: Path = ROOT) -> dict:
    """Create one bounded local work-order atomically. Never dispatch it."""
    if not ORDER_ID.fullmatch(order_id):
        raise ValueError("Invalid AETHERFALL work-order ID")
    if not isinstance(goal, str) or len(goal.strip()) < 12:
        raise ValueError("Goal must contain at least 12 characters")
    if not criteria or any(not isinstance(item, str) or len(item.strip()) < 5 for item in criteria):
        raise ValueError("Supply at least one meaningful --criterion")
    config = read_json(root / ".sire/integration.json")
    shortcuts = read_json(root / ".sire/commands.json")
    issues = config_issues(config, shortcuts, root)
    if issues:
        raise ValueError("Invalid integration contract: " + "; ".join(issues))
    if team not in config["routes"]:
        raise ValueError("Unapproved team: " + team)
    path = root / ".sire/work-orders" / (order_id + ".json")
    if not path.parent.is_dir():
        raise ValueError("Missing work order directory")
    order = {
        "schema_version": 1,
        "id": order_id,
        "project": EXPECTED_PROJECT,
        "repository": EXPECTED_REPO,
        "goal": goal.strip(),
        "authorised_executor": {
            "master": "S.I.R.E AI",
            "specialist": config["routes"][team]["specialist"],
            "team": team,
            "execution_status": "NOT_CONNECTED",
        },
        "requirements": [
            "Preserve existing approved artwork, original source and saved drafts",
            "Follow FIND → PLAN → BUILD → TEST → REPAIR → RETEST → SHOW → HARDEN → PROVE → FINISH",
            "No new paid APIs, unapproved remote calls, merges, deploys or destructive changes",
            "Use exact source SHA and separately verify real native/graphical/device proof",
        ],
        "status": "PLANNED",
        "completion_criteria": [criterion.strip() for criterion in criteria],
        "evidence": {"source_tests": "NOT_RUN", "native_godot": "NOT_RUN",
                     "graphical_proof": "NOT_RUN", "device": "NOT_RUN"},
        "rollback": "Stop this work order, leave the current approved source unchanged and preserve existing media.",
    }
    errors = order_issues(order)
    if errors:
        raise ValueError("; ".join(errors))
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump(order, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    return {
        "id": order_id,
        "status": "PLANNED",
        "saved_path": path.relative_to(root).as_posix(),
        "dispatched": False,
        "source_modified": True,
    }


def handoff(order_id: str) -> dict:
    """Output a source-pinned *proposal*. No network, process dispatch or file write."""
    order = show_order(order_id)
    problems = all_issues()
    if problems:
        raise ValueError("Integration invalid: " + "; ".join(problems))
    git = git_observation()
    if git["status"] != "OBSERVED" or not git["clean"]:
        raise ValueError("Git source must be available and clean to hand off")
    return {
        "schema_version": 1,
        "kind": "SIRE_WORK_ORDER_PROPOSAL",
        "dispatched": False,
        "execution_status": "NOT_CONNECTED",
        "project": EXPECTED_PROJECT,
        "repository": EXPECTED_REPO,
        "source_commit_sha": git["sha"],
        "source_branch": git["branch"],
        "master": "S.I.R.E AI",
        "specialist": order["authorised_executor"]["specialist"],
        "team": order["authorised_executor"]["team"],
        "work_order_id": order["id"],
        "goal": order["goal"],
        "requirements": order["requirements"],
        "completion_criteria": order["completion_criteria"],
        "approval_gates": {"network_call": False, "new_cost": False,
                           "merge": False, "deployment": False,
                           "proof_required": True},
        "instruction": "Review in the existing authorised S.I.R.E. master; authenticate executor, verify exact source, run real tests and return independent evidence before changing status."
    }


def run_checks() -> int:
    commands = [
        [sys.executable, str(ROOT / "tools/validate_structure.py")],
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
    ]
    if all_issues():
        print("FAIL: integration/work-order configuration invalid", file=sys.stderr)
        for line in all_issues():
            print(" - " + line, file=sys.stderr)
        return 1
    for cmd in commands:
        result = subprocess.run(cmd, cwd=ROOT, check=False)
        if result.returncode:
            print(f"FAIL: {cmd[1]} returned {result.returncode}", file=sys.stderr)
            return 1
    print("PASS: AETHERFALL offline checks. Native engine/visual/device proof is separate.")
    return 0


def native_smoke(executable: str | None) -> int:
    """Explicit local headless run only; never download/launch a background service."""
    candidate = executable or shutil.which("godot")
    if not candidate:
        print("BLOCKED: native Godot not installed; use CI/headless or approved runner", file=sys.stderr)
        return 2
    try:
        version = subprocess.run([candidate, "--version"], capture_output=True, text=True,
                                 timeout=15, check=False)
        if version.returncode or not version.stdout.strip().startswith(EXPECTED_ENGINE):
            print("BLOCKED: only official/version-verified Godot 4.7.2 is approved", file=sys.stderr)
            return 2
        for args in (
            ["--headless", "--path", str(ROOT / "game"), "--editor", "--import", "--quit"],
            ["--headless", "--path", str(ROOT / "game"), "--quit-after", "5"],
        ):
            p = subprocess.run([candidate, *args], capture_output=True, text=True,
                               timeout=120, check=False)
            combined = p.stdout + p.stderr
            if p.returncode or re.search(r"(?mi)(?:^|\s)(?:ERROR|FATAL):", combined):
                print("FAIL: real Godot headless test\n" + combined[-3500:], file=sys.stderr)
                return 1
    except (OSError, subprocess.TimeoutExpired) as exc:
        print("BLOCKED: native Godot could not be run: " + str(exc), file=sys.stderr)
        return 2
    print("PASS: real native headless Godot import + five-frame startup. NOT visual or gameplay proof.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AETHERFALL / S.I.R.E. offline developer command centre")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("doctor", "status", "routes", "skills", "calls", "check", "native-smoke"):
        option = sub.add_parser(name)
        if name not in ("check", "native-smoke"):
            option.add_argument("--json", action="store_true")
        if name == "native-smoke":
            option.add_argument("--godot", help="Path to already installed Godot 4.7.2 binary")
    work = sub.add_parser("work")
    work_sub = work.add_subparsers(dest="work_command", required=True)
    work_list = work_sub.add_parser("list")
    work_list.add_argument("--json", action="store_true")
    work_show = work_sub.add_parser("show")
    work_show.add_argument("work_id")
    work_show.add_argument("--json", action="store_true")
    work_new = work_sub.add_parser("new")
    work_new.add_argument("work_id")
    work_new.add_argument("--team", choices=sorted(ROUTE_IDS), required=True)
    work_new.add_argument("--goal", required=True)
    work_new.add_argument("--criterion", action="append", required=True)
    work_new.add_argument("--json", action="store_true")
    hand = sub.add_parser("handoff")
    hand.add_argument("work_id")
    hand.add_argument("--json", action="store_true")
    shortcut = sub.add_parser("cmd")
    shortcut.add_argument("key", nargs="?", help="Examples: G, T, E, N, GENESIS, HGE")
    shortcut.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.command in ("doctor", "status"):
            report = doctor_report()
            if args.command == "status":
                report = {k: report[k] for k in (
                    "project", "integration_contract", "git", "sire_runner",
                    "sire_mcp", "sire_plugins", "godot_binary", "native_gameplay", "graphical_proof"
                )}
            render(report, args.json)
            return 0 if report["integration_contract"] == "PASS" else 1
        if args.command in ("routes", "skills", "calls"):
            config = read_json(MANIFEST)
            routes = config["routes"]
            if args.command == "skills":
                routes = {key: value["skill"] for key, value in routes.items()}
            if args.command == "calls":
                routes = available_calls()
            render(routes, args.json)
            return 0 if not all_issues() else 1
        if args.command == "cmd":
            keys = commands_report()
            if not args.key:
                render(keys, args.json)
                return 0
            key = args.key.upper()
            if key not in keys:
                raise ValueError("Unknown shortcut: " + key)
            render({"key": key, **keys[key],
                    "invocation": "python3 tools/aetherfall.py " + keys[key]["action"],
                    "automatically_dispatched": False}, args.json)
            return 0
        if args.command == "work":
            if args.work_command == "list":
                render(list_orders(), args.json)
            elif args.work_command == "new":
                render(create_order(args.work_id, args.team, args.goal, args.criterion), args.json)
            else:
                render(show_order(args.work_id), args.json)
            return 0
        if args.command == "handoff":
            render(handoff(args.work_id), args.json)
            return 0
        if args.command == "check":
            return run_checks()
        if args.command == "native-smoke":
            return native_smoke(args.godot)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
