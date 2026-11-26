#!/usr/bin/env python3
"""AETHERFALL additive file-structure guard (source-level, no gameplay claims).

Check the working tree for Windows/Linux portability, Godot resource and UID
integrity, and critical layout paths. On PRs, compare against the *base commit*
to reject accidental removal/renaming or changes to pre-existing asset IDs.
No network, source rewrite, auto-approval, merge, or deletion is performed.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_FILE = "config/layout-contract.json"
HEAD_SHA = re.compile(r"^[0-9a-f]{40}$")
UID_RE = re.compile(r"^uid://[a-z0-9]+$")
SCENE_UID = re.compile(r'(?m)^\[gd_(?:scene|resource)\b[^\n]*\buid="(uid://[^"]+)"')
STATIC_RESOURCE = re.compile(r'''(["'])res://([^"'\n]*)\1''')
MAIN_SCENE = re.compile(r'(?m)^\s*run/main_scene\s*=\s*"([^"]+)"')
RESERVED_WIN = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{index}" for prefix in ("COM", "LPT") for index in range(1, 10)
}
WINDOWS_CHARS = set('<>:"\\|?*')
SOURCES = {".tscn", ".tres", ".gd", ".gdshader", ".shader", ".godot"}
DELETE_OK = ("/.gitkeep",)
ASSET_CHANGE_KEYS = ("type", "concept_dir", "source_dir", "runtime_dir",
                     "concept_status", "legacy_alias")


def _portable_errors(path: str, max_path: int, max_component: int) -> list[str]:
    errors = []
    if not path or path.startswith("/") or len(path) > max_path:
        errors.append("Non-portable relative path length/form: " + path)
    for part in path.split("/"):
        if not part or part in (".", "..") or len(part) > max_component:
            errors.append("Invalid component/length: " + path)
        if any(char in WINDOWS_CHARS or ord(char) < 32 for char in part):
            errors.append("Windows-unsafe character: " + path)
        if part.endswith((" ", ".")) or part.split(".", 1)[0].upper() in RESERVED_WIN:
            errors.append("Windows-reserved name/ending: " + path)
        if part != unicodedata.normalize("NFC", part):
            errors.append("Non-normalised Unicode path: " + path)
    return errors


def _load_contract(root: Path) -> tuple[dict | None, list[str]]:
    try:
        data = json.loads((root / CONTRACT_FILE).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        return None, ["Missing or malformed layout contract: " + str(exc)]
    if not isinstance(data, dict) or data.get("schema_version") != 1 or data.get("project") != "AETHERFALL: REALMS COLLIDE":
        return None, ["Invalid layout contract version/project"]
    problems = []
    if data.get("godot_project") != "game/project.godot" or data.get("asset_registry") != "art/asset_registry.json":
        problems.append("Canonical project/registry paths changed")
    for key in ("protected_paths", "preserved_roots", "identity_fields", "ignore_generated_dirs", "immutable_binary_roots", "immutable_binary_extensions"):
        values = data.get(key)
        if not isinstance(values, list) or not values or any(not isinstance(item, str) or not item for item in values):
            problems.append("Invalid contract array: " + key)
        elif len(values) != len(set(values)):
            problems.append("Duplicate contract entries: " + key)
    if not all(isinstance(data.get(key), int) and 32 <= data[key] <= 255
               for key in ("max_component", "max_relative_path")):
        problems.append("Invalid path-length limits")
    if problems:
        return None, problems
    paths = data["protected_paths"]
    roots = data["preserved_roots"]
    for value in paths:
        if ".." in value.split("/") or value.startswith("/") or value.endswith("/"):
            problems.append("Unsafe protected path declaration: " + value)
    for value in roots + data["immutable_binary_roots"]:
        if ".." in value.split("/") or not value.endswith("/") or value.startswith("/"):
            problems.append("Unsafe preserved/immutable root declaration: " + value)
    for value in data["immutable_binary_extensions"]:
        if not re.fullmatch(r"\.[a-z0-9]{2,6}", value):
            problems.append("Invalid immutable binary extension")
    if CONTRACT_FILE not in paths or "game/project.godot" not in paths or "art/asset_registry.json" not in paths:
        problems.append("Contract does not protect itself and canonical game files")
    if set(ASSET_CHANGE_KEYS) - set(data["identity_fields"]):
        problems.append("Contract omits historical identity fields")
    return (data if not problems else None), problems


def _safe_resource_path(game: Path, value: str) -> bool:
    if not value or value.startswith("/") or "\\" in value or "\x00" in value:
        return False
    if any(part in ("", ".", "..") or ":" in part for part in value.split("/")):
        return False
    target = game.joinpath(*value.split("/"))
    return target.resolve().is_relative_to(game.resolve()) and target.is_file() and not target.is_symlink()


def workspace_issues(root: Path = ROOT) -> list[str]:
    root = Path(root).resolve()
    policy, errors = _load_contract(root)
    if policy is None:
        return errors
    game = root / "game"
    for rel in policy["protected_paths"]:
        p = root / rel
        if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(root):
            errors.append("Missing/moved protected file: " + rel)
    for rel in policy["preserved_roots"]:
        p = root / rel.rstrip("/")
        if not p.is_dir() or p.is_symlink() or not p.resolve().is_relative_to(root):
            errors.append("Missing/moved protected directory: " + rel)
    seen: dict[str, str] = {}
    tracked = _git(root, "ls-files", "-z")
    if tracked is not None:
        for rel in [x for x in tracked.split("\0") if x]:
            components = rel.split("/")
            if set(components) & set(policy["ignore_generated_dirs"]):
                errors.append("Generated/cache directory tracked by Git: " + rel)
            if rel.endswith((".blend1", ".blend2", ".tmp", ".apk", ".aab")):
                errors.append("Generated/export package tracked by Git: " + rel)
    for current, folders, files in os.walk(root, followlinks=False):
        folders[:] = sorted(v for v in folders if v not in policy["ignore_generated_dirs"])
        for name in folders + sorted(files):
            path = Path(current) / name
            rel = path.relative_to(root).as_posix()
            errors.extend(_portable_errors(rel, policy["max_relative_path"], policy["max_component"]))
            folded = rel.casefold()
            previous = seen.setdefault(folded, rel)
            if previous != rel:
                errors.append(f"Case collision between {previous} and {rel}")
            if path.is_symlink():
                errors.append("Symlink not allowed in game source: " + rel)
    if not game.is_dir():
        errors.append("Missing game/ project directory")
        return errors
    if len(list(game.rglob("project.godot"))) != 1:
        errors.append("Multiple or missing nested Godot project files under game/")
    uid_to_source: dict[str, str] = {}
    for current, folders, files in os.walk(game, followlinks=False):
        folders[:] = [name for name in folders if name not in policy["ignore_generated_dirs"]]
        for name in files:
            resource = Path(current) / name
            rel = resource.relative_to(root).as_posix()
            if resource.is_symlink():
                continue
            if name.endswith(".gd.uid"):
                uid = resource.read_text(encoding="utf-8").strip()
                if not UID_RE.fullmatch(uid):
                    errors.append("Invalid Godot .gd.uid sidecar: " + rel)
                    continue
                existing = uid_to_source.setdefault(uid, rel)
                if existing != rel:
                    errors.append(f"Duplicate Godot UID {uid}: {existing} / {rel}")
                if not resource.with_suffix("").is_file():
                    errors.append("Orphan Godot script UID sidecar: " + rel)
                continue
            if resource.suffix not in SOURCES and name != "project.godot":
                continue
            try:
                text = resource.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                errors.append("Unreadable Godot text resource " + rel + ": " + str(exc))
                continue
            if resource.suffix in (".tscn", ".tres"):
                found = SCENE_UID.search(text)
                if found:
                    uid = found.group(1)
                    if not UID_RE.fullmatch(uid):
                        errors.append("Invalid scene/resource UID: " + rel)
                    else:
                        existing = uid_to_source.setdefault(uid, rel)
                        if existing != rel:
                            errors.append(f"Duplicate Godot UID {uid}: {existing} / {rel}")
            for line_no, line in enumerate(text.splitlines(), start=1):
                if line.lstrip().startswith(("#", ";")):
                    continue
                for m in STATIC_RESOURCE.finditer(line):
                    target = m.group(2)
                    if not target or target.endswith("/") or any(marker in target for marker in ("%s", "{", "}")):
                        continue  # dynamic/dir reference; must be proved in a real Godot run
                    if not _safe_resource_path(game, target):
                        errors.append(f"Broken static res:// link: {rel}:{line_no} -> {target}")
    return errors


def _git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(root), *args],
                                capture_output=True, check=False, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.decode("utf-8", errors="replace") if result.returncode == 0 else None


def _git_success(root: Path, *args: str) -> bool:
    try:
        result = subprocess.run(["git", "-C", str(root), *args],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                check=False, timeout=15)
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _git_show(root: Path, base: str, file_path: str) -> str | None:
    return _git(root, "show", base + ":" + file_path)


def _declared_uid(rel: str, content: str) -> str | None:
    if rel.endswith(".gd.uid"):
        uid = content.strip()
        return uid if UID_RE.fullmatch(uid) else None
    if rel.endswith((".tscn", ".tres")):
        found = SCENE_UID.search(content)
        return found.group(1) if found else None
    return None


def compare_issues(root: Path, base: str) -> list[str]:
    """Compare against a verified ancestor SHA. Never use an untrusted branch name."""
    root = Path(root).resolve()
    errors = []
    if not HEAD_SHA.fullmatch(base):
        return ["Base must be an exact 40-digit commit SHA"]
    if not _git_success(root, "cat-file", "-e", base + "^{commit}"):
        return ["Base Git commit is inaccessible"]
    if not _git_success(root, "merge-base", "--is-ancestor", base, "HEAD"):
        return ["Base is not an ancestor of current HEAD; refusing ambiguous comparison"]
    policy, issues = _load_contract(root)
    errors.extend(issues)
    if policy is None:
        return errors
    old_policy_text = _git_show(root, base, CONTRACT_FILE)
    if old_policy_text:
        try:
            old_policy = json.loads(old_policy_text)
            for key in ("protected_paths", "preserved_roots", "identity_fields",
                        "immutable_binary_roots", "immutable_binary_extensions", "ignore_generated_dirs"):
                if set(old_policy[key]) - set(policy[key]):
                    errors.append("Attempted weakening of base layout contract: " + key)
            for key in ("max_component", "max_relative_path"):
                if policy[key] > old_policy[key]:
                    errors.append("Attempted loosening of portability limit: " + key)
        except (ValueError, KeyError, TypeError):
            errors.append("Unable to verify base layout contract")
    old_assets = _git_show(root, base, policy["asset_registry"])
    try:
        previous = json.loads(old_assets) if old_assets else None
        current = json.loads((root / policy["asset_registry"]).read_text(encoding="utf-8"))
        if previous:
            old_by_id = {a["id"]: a for a in previous["assets"]}
            new_by_id = {a["id"]: a for a in current["assets"]}
            for asset_id, old in old_by_id.items():
                if asset_id not in new_by_id:
                    errors.append("Existing asset ID removed: " + asset_id)
                    continue
                for key in policy["identity_fields"]:
                    if old.get(key) != new_by_id[asset_id].get(key):
                        errors.append(f"Existing asset identity/path changed: {asset_id}.{key}")
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        errors.append("Cannot compare asset identities against base")
    old_project = _git_show(root, base, policy["godot_project"])
    if old_project is None:
        errors.append("Base Godot project missing")
    else:
        try:
            current_project = (root / policy["godot_project"]).read_text(encoding="utf-8")
            old_main = MAIN_SCENE.search(old_project)
            new_main = MAIN_SCENE.search(current_project)
            if not old_main or not new_main or old_main.group(1) != new_main.group(1):
                errors.append("Main scene path changed without a reviewed migration")
        except (OSError, UnicodeError):
            errors.append("Current Godot project is missing or unreadable")
    raw = _git(root, "diff", "--name-status", "-z", "--no-renames", base, "HEAD", "--")
    if raw is None:
        errors.append("Git delta cannot be read")
        return errors
    pieces = raw.split("\0")
    if pieces and not pieces[-1]:
        pieces.pop()
    if len(pieces) % 2:
        errors.append("Malformed Git change listing")
        return errors
    for status, rel in zip(pieces[::2], pieces[1::2]):
        if not rel:
            errors.append("Empty changed path")
            continue
        if status in ("D", "T"):
            if rel in policy["protected_paths"]:
                errors.append("Protected file deleted/replaced: " + rel)
            elif any(rel.startswith(prefix) for prefix in policy["preserved_roots"]) and not rel.endswith(DELETE_OK):
                errors.append("Existing source/art/evidence file removed without review: " + rel)
        if status in ("M", "T"):
            if any(rel.startswith(prefix) for prefix in policy["immutable_binary_roots"]) and (
                Path(rel).suffix.casefold() in policy["immutable_binary_extensions"]
            ):
                errors.append("Original binary changed in place; version the asset instead: " + rel)
            if rel.endswith((".tscn", ".tres", ".gd.uid")):
                original = _git_show(root, base, rel)
                candidate = root / rel
                if original is not None and candidate.is_file():
                    try:
                        current_text = candidate.read_text(encoding="utf-8")
                    except (OSError, UnicodeError):
                        errors.append("Godot UID source unreadable: " + rel)
                    else:
                        old_uid = _declared_uid(rel, original)
                        if old_uid is not None and _declared_uid(rel, current_text) != old_uid:
                            errors.append("Existing Godot UID changed: " + rel)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AETHERFALL structural contracts (no mutation)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="Check repository layout and literal resource links")
    diff = sub.add_parser("diff", help="Check protected paths against an ancestor SHA")
    diff.add_argument("--base", required=True, help="Exact trusted Git base commit SHA")
    args = parser.parse_args(argv)
    issues = workspace_issues(ROOT)
    if args.command == "diff":
        issues.extend(compare_issues(ROOT, args.base))
    if issues:
        for issue in issues:
            print("FAIL: " + issue, file=sys.stderr)
        return 1
    print("PASS: portable file layout, protected paths, Godot static resources and "
          + ("ancestor structural invariants" if args.command == "diff" else "workspace structure")
          + " (SOURCE ONLY)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
