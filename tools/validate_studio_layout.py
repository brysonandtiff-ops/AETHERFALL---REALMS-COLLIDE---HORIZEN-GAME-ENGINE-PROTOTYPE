#!/usr/bin/env python3
"""AETHERFALL AAA-style Godot studio layout contract (static only, no gameplay proof).

Fails closed for accidental engine mixing, deleted ownership zones, misrouted
asset sources, malformed manifests, missing module boundaries and unsafe add-ons.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "studio/layout_manifest.json"
TOOLCHAIN = "config/toolchain.json"
MAX_JSON_BYTES = 1024 * 1024

ZONE_PATHS = {
    "engine_project": "game",
    "source_art": "art",
    "toolchain": "config",
    "pipeline": "pipeline",
    "studio_contracts": "studio",
    "documentation": "docs",
    "scripts": "tools",
    "testing": "tests",
    "proof": "evidence",
    "source_controls": ".github",
}
MODULE_PATHS = {
    "core": "game/scripts/core",
    "player_input": "game/scripts/input",
    "characters": "game/scripts/characters",
    "combat": "game/scripts/combat",
    "abilities": "game/scripts/abilities",
    "teams": "game/scripts/teams",
    "match": "game/scripts/match",
    "network": "game/scripts/network",
    "ai": "game/scripts/ai",
    "save": "game/scripts/save",
    "telemetry": "game/scripts/telemetry",
    "worlds": "game/scripts/levels",
    "ui": "game/scripts/ui",
}
MINIMUM_DIRS = frozenset({
    "game/addons", "game/localization", "game/scripts/input",
    "game/scripts/ai", "game/scripts/save", "game/scripts/telemetry",
    "game/scenes/cinematics", "art/storyboards", "art/ui", "art/vfx",
    "pipeline/asset_ingest", "pipeline/build", "pipeline/qa",
    "pipeline/release", "studio", "config",
})
MINIMUM_FILES = frozenset({
    "game/project.godot", "art/asset_registry.json",
    "studio/layout_manifest.json", "config/toolchain.json",
    "docs/architecture/AAA_STUDIO_ARCHITECTURE.md",
    "docs/production/CONTENT_HANDOFF.md", "docs/production/BUILD_TRAINS.md",
    "pipeline/README.md", "game/addons/README.md",
    "tools/validate_studio_layout.py", "tests/test_studio_layout.py",
})
EXPECTED_FLOW = {
    "character_concept": "art/concepts/characters",
    "blender_master": "art/blender/characters",
    "godot_runtime": "game/assets/characters/heroes",
    "hero_scenes": "game/scenes/characters/heroes",
    "hero_definitions": "game/data/heroes",
}
GENERATED_PATHS = frozenset({"game/.godot", "game/.import", "build", "dist", "pipeline/.cache"})
UNREAL_BINARY_SUFFIXES = {".uasset", ".umap", ".uproject", ".uplugin"}
ID = re.compile(r"^[a-z][a-z0-9_]*$")


def _object_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field: " + key)
        result[key] = value
    return result


def load_json(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError("Missing or oversized studio JSON file: " + path.name)
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_object_no_duplicates)


def safe_repo_path(root, raw):
    """Return a safe path, never allowing path traversal/symlink redirection."""
    if not isinstance(raw, str) or not raw or raw.startswith("/") or "\\" in raw:
        return None
    if any(ord(char) < 32 for char in raw) or len(raw) > 240:
        return None
    parts = raw.split("/")
    if any(part in ("", ".", "..") or ":" in part or not re.fullmatch(r"[A-Za-z0-9_.-]+", part)
           for part in parts):
        return None
    target = root.joinpath(*parts)
    resolved_root = root.resolve()
    if not target.resolve().is_relative_to(resolved_root):
        return None
    cur = target
    while cur != root:
        if cur.is_symlink():
            return None
        cur = cur.parent
    return target


def _path_list(root, obj, key, minimum, expected_kind, errors):
    values = obj.get(key)
    if not isinstance(values, list) or not values or not all(isinstance(x, str) for x in values):
        errors.append("Invalid required " + key)
        return set()
    seen = set()
    paths = set()
    for value in values:
        normal = value.casefold()
        if normal in seen:
            errors.append("Duplicate studio contract path: " + value)
            continue
        seen.add(normal)
        candidate = safe_repo_path(root, value)
        if candidate is None:
            errors.append("Unsafe studio contract path: " + value)
            continue
        paths.add(value)
        if expected_kind == "dir" and not candidate.is_dir():
            errors.append("Missing studio directory: " + value)
        if expected_kind == "file" and not candidate.is_file():
            errors.append("Missing studio file: " + value)
    for value in sorted(minimum - paths):
        errors.append("Required studio " + key + " omitted: " + value)
    return paths


def check(root=ROOT, manifest=None, toolchain=None):
    """Pure validation; no system changes and no external proof claims."""
    root = Path(root).resolve()
    errors = []
    try:
        contract = load_json(root / MANIFEST) if manifest is None else manifest
        tool = load_json(root / TOOLCHAIN) if toolchain is None else toolchain
    except (OSError, ValueError, UnicodeError) as exc:
        return ["Studio JSON read failed: " + str(exc)]
    if not isinstance(contract, dict) or contract.get("schema_version") != 1 or contract.get("project") != "AETHERFALL: REALMS COLLIDE":
        return ["Studio layout identity/schema invalid"]
    if (contract.get("architecture") != "modular-godot-aaa-studio-monorepo" or
            contract.get("engine_family") != "Godot" or
            contract.get("project_file") != "game/project.godot" or
            contract.get("status") != "structure_and_conventions_only"):
        errors.append("Studio project/engine identity changed without migration")
    if contract.get("protected_art_registry") != "art/asset_registry.json":
        errors.append("Canonical art registry location changed")
    if contract.get("authoritative_character_source") != "art/asset_registry.json":
        errors.append("Second or missing character identity registry")
    if not isinstance(tool, dict) or tool.get("schema_version") != 1 or tool.get("project") != "AETHERFALL: REALMS COLLIDE":
        errors.append("Toolchain schema/project invalid")
    else:
        engine = tool.get("game_engine")
        dcc = tool.get("source_art_dcc")
        control = tool.get("source_control")
        policy = tool.get("policy")
        if not isinstance(engine, dict) or (engine.get("name"), engine.get("ci_version"), engine.get("project_file"),
                                             engine.get("native_headless_smoke_only")) != ("Godot", "4.7.2", "game/project.godot", True):
            errors.append("Toolchain engine claim missing/unsafe")
        if not isinstance(dcc, dict) or dcc.get("name") != "Blender" or dcc.get("native_verification") is not False or dcc.get("approved_version") is not None:
            errors.append("Unverified DCC toolchain promoted to approved")
        if not isinstance(control, dict) or control.get("backend") != "Git" or control.get("git_lfs_configured") is not False or control.get("perforce_configured") is not False:
            errors.append("Unapproved VCS/LFS/Perforce configuration claim")
        if not isinstance(policy, dict) or any(policy.get(k) is not True for k in (
                "credentials_must_stay_out_of_git", "third_party_plugins_require_license_and_owner_approval",
                "locked_art_requires_owner_approval")):
            errors.append("Studio safety policy disabled")
    zones = contract.get("zones")
    zone_paths = set()
    if not isinstance(zones, list):
        errors.append("Studio ownership zones missing")
    else:
        ids = {}
        for z in zones:
            if not isinstance(z, dict) or not isinstance(z.get("id"), str) or not isinstance(z.get("path"), str):
                errors.append("Invalid studio ownership zone")
                continue
            key = z["id"]
            if key in ids:
                errors.append("Duplicate studio zone ID: " + key)
            ids[key] = z
            zone_paths.add(z["path"])
            if not isinstance(z.get("owner"), str) or not z["owner"].strip() or not isinstance(z.get("responsibility"), str) or not z["responsibility"].strip():
                errors.append("Studio zone missing real discipline: " + key)
            candidate = safe_repo_path(root, z["path"])
            if candidate is None or not candidate.is_dir():
                errors.append("Missing/unsafe studio ownership zone: " + z["path"])
        if {key: value.get("path") for key, value in ids.items()} != ZONE_PATHS:
            errors.append("Required studio ownership zone removed/moved/duplicated")
    required_dirs = _path_list(root, contract, "required_directories", MINIMUM_DIRS.union(MODULE_PATHS.values()),
                               "dir", errors)
    required_files = _path_list(root, contract, "required_files", MINIMUM_FILES, "file", errors)
    for path in required_dirs | required_files:
        if path.split("/")[0] not in zone_paths:
            errors.append("Studio path outside owner zone: " + path)
    mods = contract.get("modules")
    if not isinstance(mods, list):
        errors.append("Runtime module map missing")
    else:
        seen = {}
        for module in mods:
            if not isinstance(module, dict):
                errors.append("Invalid runtime module")
                continue
            name, path = module.get("id"), module.get("path")
            if not isinstance(name, str) or not ID.fullmatch(name) or not isinstance(path, str):
                errors.append("Invalid runtime module identity")
                continue
            if name in seen:
                errors.append("Duplicate runtime module: " + name)
            seen[name] = path
            if path not in required_dirs or not path.startswith("game/scripts/"):
                errors.append("Runtime module outside owned source boundary: " + name)
            if not isinstance(module.get("owner"), str) or not module["owner"].strip() or module.get("status") != "reserved_or_scaffold_only":
                errors.append("Runtime module ownership/completion claim invalid: " + name)
        if seen != MODULE_PATHS:
            errors.append("Runtime module ID/path ownership contract changed")
        if len(set(seen.values())) != len(seen):
            errors.append("Runtime module paths reused")
    if contract.get("asset_flow") != EXPECTED_FLOW:
        errors.append("Art-to-engine source/export boundary changed")
    if contract.get("generated_paths") is None or not isinstance(contract["generated_paths"], list) or set(contract["generated_paths"]) != GENERATED_PATHS or len(contract["generated_paths"]) != len(GENERATED_PATHS):
        errors.append("Generated outputs/cache policy changed")
    constraints = contract.get("constraints")
    if not isinstance(constraints, dict) or any(value is not True for value in constraints.values()) or set(constraints) != {
        "no_copy_of_commercial_game_files", "no_unapproved_godot_to_unreal_conversion",
        "no_live_agents_created", "no_gameplay_claim_from_directories", "no_public_private_photos_or_secrets",
    }:
        errors.append("Studio protected-content and approval gates missing")
    # A true Unreal port requires a separate, approved migration. No fake .uasset metadata in Godot.
    game = root / "game"
    if game.is_dir():
        for candidate in game.rglob("*"):
            if candidate.is_file() and candidate.suffix.lower() in UNREAL_BINARY_SUFFIXES:
                errors.append("Unreal-only game artifact inside Godot project: " +
                              candidate.relative_to(root).as_posix())
    addons = root / "game/addons"
    if addons.is_dir():
        for child in addons.iterdir():
            if child.is_dir() and not (child / "AETHERFALL_PROVENANCE.md").is_file():
                errors.append("Unreviewed Godot add-on missing provenance: " + child.name)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check actual AAA-style studio layout (static only).")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    failures = check(args.root)
    if failures:
        for error in sorted(set(failures)):
            print("FAIL: " + error, file=sys.stderr)
        return 1
    print("PASS: Godot-native studio ownership, 13 module boundaries, toolchain truth and source/export layout (STRUCTURE ONLY)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
