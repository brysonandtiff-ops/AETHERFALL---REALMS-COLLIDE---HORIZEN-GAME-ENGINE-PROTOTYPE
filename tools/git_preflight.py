#!/usr/bin/env python3
"""Read-only AETHERFALL Git preflight; S.I.R.E. Git Stop remains authority."""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = "brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE"
SHA = re.compile(r"^[0-9a-f]{40}$")
PROTECTED = {
    "AGENTS.md", "game/project.godot", "art/asset_registry.json",
    "docs/characters/CANON_LOCKS.json", ".github/CODEOWNERS",
    ".github/workflows/foundation-check.yml", "tools/validate_structure.py",
}
NO_REMOVE_ROOTS = ("game/", "art/", "evidence/", "docs/characters/", ".sire/")
REVIEW_ROOTS = ("game/", "art/", "evidence/", "docs/characters/", ".github/", "tools/")
GIT_OPERATIONS = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-apply", "rebase-merge")
TOKEN_PATTERNS = (
    re.compile(r"-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"(?<![A-Z0-9])AKIA[A-Z0-9]{16}(?![A-Z0-9])"),
)
CONFLICT = re.compile(r"^\+\s*(?:<{7}|={7}|>{7})(?:\s|$)")


class GitUnavailable(RuntimeError):
    pass


def run_git(root: Path, *args: str, allow_failure: bool = False) -> tuple[int, bytes]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=False, timeout=25,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GitUnavailable("Git inspection unavailable or timed out") from exc
    if result.returncode and not allow_failure:
        raise GitUnavailable("Git read failed: " + " ".join(args[:2]))
    return result.returncode, result.stdout


def git_text(root: Path, *args: str, allow_failure: bool = False) -> str:
    return run_git(root, *args, allow_failure=allow_failure)[1].decode("utf-8", "replace").strip()


def valid_remote(remote: str) -> bool:
    for prefix in ("https://github.com/", "git@github.com:", "ssh://git@github.com/"):
        if remote.startswith(prefix):
            return remote[len(prefix):].removesuffix(".git").rstrip("/") == CANONICAL
    return False


def pending_operation(root: Path) -> bool:
    for marker in GIT_OPERATIONS:
        path = Path(git_text(root, "rev-parse", "--git-path", marker))
        if not path.is_absolute():
            path = root / path
        if path.exists():
            return True
    return False


def diff_changes(root: Path, base: str) -> list[tuple[str, str]]:
    raw = run_git(root, "diff", "--name-status", "-z", "--no-renames", base, "HEAD", "--")[1]
    parts = [x.decode("utf-8", "replace") for x in raw.split(b"\x00")]
    if parts and not parts[-1]:
        parts.pop()
    if len(parts) % 2:
        raise GitUnavailable("Malformed Git change listing")
    return list(zip(parts[::2], parts[1::2]))


def diff_issues(root: Path, base: str) -> list[str]:
    raw = run_git(root, "diff", "--no-ext-diff", "--no-color", "--unified=0", base, "HEAD", "--")[1]
    problems = []
    for line in raw.decode("utf-8", "replace").splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        if CONFLICT.match(line):
            problems.append("Merge-conflict marker added in commit range")
        if any(rule.search(line) for rule in TOKEN_PATTERNS):
            problems.append("Credential-like addition detected (content withheld)")
    return sorted(set(problems))


def assess(root: Path, expected_head: str | None = None,
           base_sha: str | None = None, strict: bool = False) -> dict:
    """No network operations or writes; fields do not represent reviewer approval."""
    root = root.resolve()
    actual = git_text(root, "rev-parse", "--verify", "HEAD")
    if not SHA.fullmatch(actual):
        raise GitUnavailable("Git HEAD is unavailable or invalid")
    branch = git_text(root, "symbolic-ref", "-q", "--short", "HEAD", allow_failure=True) or "(detached)"
    remote_ok = valid_remote(git_text(root, "remote", "get-url", "origin", allow_failure=True))
    clean = not run_git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")[1]
    unmerged = bool(run_git(root, "ls-files", "--unmerged", "-z")[1])
    pending = pending_operation(root)
    problems = []
    review = []
    if not remote_ok:
        problems.append("Git origin does not identify the canonical AETHERFALL repository")
    if unmerged:
        problems.append("Unresolved Git index conflicts")
    if pending:
        problems.append("Git merge/rebase/cherry-pick/revert in progress")
    if strict and not clean:
        problems.append("Working tree has uncommitted or untracked changes")
    if strict and expected_head is None:
        problems.append("Expected HEAD is required in strict mode")
    if expected_head is not None:
        if not isinstance(expected_head, str) or not SHA.fullmatch(expected_head):
            problems.append("Expected HEAD SHA is invalid")
        elif actual != expected_head:
            problems.append("Git HEAD does not match requested candidate SHA")
    comparison = "NOT_CHECKED"
    changed = []
    if base_sha is not None:
        if not isinstance(base_sha, str) or not SHA.fullmatch(base_sha):
            comparison = "INVALID"
            problems.append("Trusted base SHA must be exactly 40 hex characters")
        elif run_git(root, "cat-file", "-e", base_sha + "^{commit}", allow_failure=True)[0]:
            comparison = "MISSING"
            problems.append("Trusted base commit missing from local history")
        elif run_git(root, "merge-base", "--is-ancestor", base_sha, "HEAD", allow_failure=True)[0]:
            comparison = "DIVERGED"
            problems.append("PR base is not ancestor of HEAD; reconcile before integration")
        else:
            comparison = "ANCESTOR"
            changed = diff_changes(root, base_sha)
            if run_git(root, "diff", "--check", base_sha, "HEAD", "--", allow_failure=True)[0]:
                problems.append("Committed diff has whitespace problems")
            problems.extend(diff_issues(root, base_sha))
            for status, path in changed:
                if not path:
                    problems.append("Git returned empty changed path")
                    continue
                if path in PROTECTED or path.startswith(REVIEW_ROOTS):
                    review.append(path)
                if status in ("D", "T") and (
                    path in PROTECTED or (
                        path.startswith(NO_REMOVE_ROOTS) and not path.endswith("/.gitkeep")
                    )
                ):
                    problems.append("Existing protected source removed/replaced: " + path)
    return {
        "project": "AETHERFALL: REALMS COLLIDE", "source_commit_sha": actual,
        "branch": branch, "origin": "MATCH" if remote_ok else "UNKNOWN_OR_WRONG",
        "clean_worktree": clean, "unmerged": unmerged,
        "operation_in_progress": pending, "base_comparison": comparison,
        "changed_paths_count": len(changed), "review_required_paths": sorted(set(review)),
        "issues": sorted(set(problems)),
        "result": "PASS_SOURCE_PREFLIGHT" if not problems else "BLOCKED",
        "server_side_branch_protection": "NOT_VERIFIED",
        "sire_git_stop": "SEPARATE_AUTHORITY_NOT_RUN",
        "runtime_or_device_proof": "NOT_RUN",
        "mutation_performed": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="AETHERFALL Git preflight (read-only)")
    sub = parser.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor")
    doctor.add_argument("--json", action="store_true")
    check = sub.add_parser("check")
    check.add_argument("--expected-head", required=True)
    check.add_argument("--base")
    check.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = assess(ROOT, expected_head=getattr(args, "expected_head", None),
                        base_sha=getattr(args, "base", None), strict=args.command == "check")
    except GitUnavailable as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, sort_keys=True, indent=2))
    else:
        for key in ("source_commit_sha", "branch", "origin", "clean_worktree",
                    "base_comparison", "changed_paths_count", "result"):
            print(key + ": " + str(report[key]))
        for problem in report["issues"]:
            print("BLOCKED: " + problem, file=sys.stderr)
        print("Review, S.I.R.E. Git Stop and native game/device proof are separate.")
    return 0 if not report["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
