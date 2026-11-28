#!/usr/bin/env python3
"""Read-only S.I.R.E. dependency bridge; never downloads or dispatches jobs."""
import argparse
import ast
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PIN = "061943f2dd67c1d5cfd943f1739348346b433636"
REPO = "brysonandtiff-ops/SIRE"
REGISTRY = "sire/capability_registry.py"
REGISTRY_BLOB = "d6b85514057adc6ef706552149f6d69197bca18a"
STUDIO = "sire/sire/professional_game_build_capabilities.py"
STUDIO_BLOB = "034e4d46f285d13cd6cfa1005fca088c53097d5c"
ORIGINS = {"https://github.com/" + REPO, "https://github.com/" + REPO + ".git",
           "git@github.com:" + REPO + ".git", "ssh://git@github.com/" + REPO + ".git"}
FALSE_FLAGS = ("auto_fetch", "auto_dispatch", "auto_spend", "auto_merge", "auto_deploy")


def lock_errors(data):
    expected = {"schema_version": 1, "project": "AETHERFALL: REALMS COLLIDE",
                "repository": REPO, "commit": PIN, "visibility": "private",
                "distribution": "external_authorised_checkout_only",
                "registry_path": REGISTRY, "registry_blob": REGISTRY_BLOB,
                "studio_path": STUDIO, "studio_blob": STUDIO_BLOB,
                "runtime_status": "NOT_VERIFIED"}
    if not isinstance(data, dict):
        return ["Invalid source lock"]
    errors = [key + " mismatch" for key, value in expected.items()
              if type(data.get(key)) is not type(value) or data.get(key) != value]
    errors += [key + " must be false" for key in FALSE_FLAGS if data.get(key) is not False]
    return errors


def load_lock(root=ROOT):
    path = root / ".sire/source-lock.json"
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Unsafe lock path")
    return json.loads(path.read_text(encoding="utf-8"))


def safe_env():
    env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "WINDIR",
           "TEMP", "TMP", "LANG", "LC_ALL") if key in os.environ}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1",
               GIT_TERMINAL_PROMPT="0")
    return env


def git(root, *args):
    p = subprocess.run(["git", "-c", "core.fsmonitor=false", "-C", str(root), *args],
                       env=safe_env(), capture_output=True, text=True,
                       timeout=30, check=False)
    if p.returncode:
        raise ValueError("Git source check failed: " + args[0])
    return p.stdout


def source_report(source, project=ROOT):
    """Verify a separate clean private checkout, not a connected runner."""
    base = {"source": "BLOCKED", "runtime": "NOT_VERIFIED",
            "runner": "NOT_VERIFIED", "dispatch": False}
    if source is None:
        return dict(base, reason="No authorised private checkout supplied")
    try:
        root = Path(source).resolve(strict=True)
        project = project.resolve()
        if root == project or root.is_relative_to(project) or project.is_relative_to(root):
            raise ValueError("Use a separate checkout outside the public game repository")
        if Path(git(root, "rev-parse", "--show-toplevel").strip()).resolve() != root:
            raise ValueError("Not the private repository root")
        if git(root, "remote", "get-url", "origin").strip() not in ORIGINS:
            raise ValueError("Unexpected source origin")
        if git(root, "rev-parse", "--verify", "HEAD").strip() != PIN:
            raise ValueError("Upstream commit differs from the reviewed lock")
        if git(root, "status", "--porcelain=v1", "--untracked-files=all",
               "--ignored=matching", "--ignore-submodules=none").strip():
            raise ValueError("Checkout must be clean, including ignored files")
        for path, expected in ((REGISTRY, REGISTRY_BLOB), (STUDIO, STUDIO_BLOB)):
            file = root / path
            if file.is_symlink() or not file.is_file() or not file.resolve().is_relative_to(root):
                raise ValueError("Missing or unsafe upstream entrypoint")
            if git(root, "rev-parse", PIN + ":" + path).strip() != expected:
                raise ValueError("Pinned entrypoint differs from reviewed blob")
            if git(root, "hash-object", "--no-filters", str(file)).strip() != expected:
                # Windows CRLF conversion is intentionally not accepted.
                raise ValueError("Working entrypoint bytes differ from pinned blob")
        return dict(base, source="PINNED_SOURCE_VERIFIED", commit=PIN,
                    tracked_paths=len(git(root, "ls-tree", "-r", "--name-only", PIN).splitlines()))
    except (OSError, ValueError, subprocess.TimeoutExpired):
        # Do not expose private local paths, remote credentials or subprocess logs.
        return dict(base, reason="Private checkout missing, dirty, wrong origin/version, or unreadable")


def studio_ids(source):
    """Read the studio capability IDs from the reviewed source without executing it."""
    tree = ast.parse(git(source, "show", PIN + ":" + STUDIO))
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "CAPABILITIES":
            if not isinstance(node.value, ast.Tuple):
                break
            ids = []
            for item in node.value.elts:
                if not (isinstance(item, ast.Call) and isinstance(item.func, ast.Name)
                        and item.func.id == "StudioCapability" and item.args
                        and isinstance(item.args[0], ast.Constant) and isinstance(item.args[0].value, str)):
                    raise ValueError("Unsupported studio capability declaration")
                ids.append(item.args[0].value)
            if not ids or len(set(ids)) != len(ids):
                raise ValueError("Invalid studio registry")
            return ids
    raise ValueError("Studio registry not found")


def catalog(source):
    source = Path(source).resolve(strict=True)
    report = source_report(source)
    if report["source"] != "PINNED_SOURCE_VERIFIED":
        return report
    # Execute only the actual pinned, reviewed registry blob; no arbitrary commands.
    code = git(source, "show", PIN + ":" + REGISTRY)
    p = subprocess.run([sys.executable, "-I", "-B", "-c", code, str(source)],
                       cwd=source, env=safe_env(), capture_output=True,
                       text=True, timeout=30, check=False)
    if p.returncode:
        raise ValueError("Upstream registry execution failed")
    data = json.loads(p.stdout)
    if not isinstance(data, dict) or data.get("success") is not True:
        raise ValueError("Upstream registry returned an invalid report")
    for name in ("agents", "skills", "plugins", "abilities", "execution"):
        rows = data.get(name)
        count = data.get("counts", {}).get(name)
        if not isinstance(rows, list) or type(count) is not int or count != len(rows):
            raise ValueError("Invalid catalogue counts")
    ids = studio_ids(source)
    if source_report(source)["source"] != "PINNED_SOURCE_VERIFIED":
        raise ValueError("Private checkout changed during cataloguing")
    return dict(report, catalogue="EXECUTED_SOURCE_REGISTRY",
                studio_capability_ids=ids, studio_required_count=len(ids),
                studio_verified_count=0, registry=data,
                note="Private local catalogue; not authority, runner or gameplay evidence.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("contract", "doctor", "catalog"))
    parser.add_argument("--sire-root", type=Path)
    args = parser.parse_args(argv)
    try:
        errors = lock_errors(load_lock())
        if errors:
            print(json.dumps({"contract": "FAIL", "issues": errors}))
            return 1
        if args.command == "contract":
            print(json.dumps({"contract": "PASS", "private_source": "NOT_CHECKED",
                              "runtime": "NOT_VERIFIED"}))
            return 0
        result = source_report(args.sire_root)
        if args.command == "catalog" and result["source"] == "PINNED_SOURCE_VERIFIED":
            result = catalog(args.sire_root)
        print(json.dumps(result, indent=2))
        return 0 if result["source"] == "PINNED_SOURCE_VERIFIED" else 2
    except (OSError, ValueError, subprocess.TimeoutExpired, TypeError):
        print(json.dumps({"status": "FAIL", "runtime": "NOT_VERIFIED",
                          "reason": "Source lock or catalogue could not be verified"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
