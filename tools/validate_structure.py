#!/usr/bin/env python3
"""AETHERFALL offline source safety gates. Not native game or art evidence."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md", "BUILD_HERE.md", "AGENTS.md", ".gitignore", ".gitattributes",
    ".github/CODEOWNERS", "docs/security/REPO_HARDENING.md",
    "studio/layout_manifest.json", "config/toolchain.json",
    "docs/architecture/AAA_STUDIO_ARCHITECTURE.md",
    "docs/production/CONTENT_HANDOFF.md", "docs/production/BUILD_TRAINS.md",
    "pipeline/README.md", "game/addons/README.md",
    "tools/validate_studio_layout.py", "tests/test_studio_layout.py",
    "tools/production_queue.py", "docs/production/WORK_QUEUE.json",
    "docs/production/README.md", "docs/production/MASTER_BUILD_ROADMAP.md",
    "docs/production/DEFINITION_OF_DONE.md",
    "docs/production/HANDOFF_AND_RECOVERY.md",
    "docs/production/TEST_MATRIX.md",
    "docs/production/DECISIONS_AND_RISKS.md",
    "docs/production/RELEASE_AND_OPERATIONS.md",
    "game/project.godot", "game/scenes/bootstrap/main.tscn",
    "art/asset_registry.json", "docs/architecture/REPO_LAYOUT.md",
    "docs/architecture/HERO_SHOOTER_TREE_RESEARCH.md",
    "docs/art/ASSET_PIPELINE.md", "docs/characters/CHARACTER_REGISTRY.md",
    "docs/legacy/shadowspire_migration.json", "docs/legacy/README.md",
    "docs/characters/LEGACY_ROSTER.md",
    "docs/game-design/SHADOWSPIRE_LEGACY_DESIGN.md", "evidence/README.md",
)
REQUIRED_DIRS = (
    "game/scenes/characters/heroes", "game/scenes/characters/enemies",
    "game/scenes/levels/realms", "game/scripts/core", "game/scripts/combat",
    "game/scripts/abilities", "game/assets/characters/heroes", "game/assets/weapons",
    "game/assets/worlds", "game/audio/music", "game/shaders",
    "art/blender/characters", "art/blender/weapons", "art/concepts/characters",
    "game/data/heroes", "game/data/abilities", "game/data/modes",
    "game/data/balance", "game/scenes/matches", "game/scenes/ui/hero_select",
    "game/scenes/ui/hud", "game/scripts/match", "game/scripts/teams",
    "game/scripts/network", "tests/gameplay", "tests/network",
    "studio", "config", "pipeline/asset_ingest", "pipeline/build",
    "pipeline/qa", "pipeline/release", "game/addons", "game/localization",
    "game/scripts/ai", "game/scripts/input", "game/scripts/save",
    "game/scripts/telemetry", "game/scenes/cinematics",
    "art/storyboards", "art/ui", "art/vfx",
    "evidence/godot", "evidence/blender", "evidence/device", "tests",
)
IGNORED_DIRS = {".git", ".godot", ".import", ".pytest_cache", "__pycache__", ".venv"}
# build/ and dist/ are deliberately SCANNED if present, even if ignored by Git.
PRIVATE_FILENAMES = {"id_rsa", "id_ed25519", "credentials.json", "service-account.json", "service_account.json", ".netrc", ".npmrc", ".pypirc"}
PRIVATE_EXTENSIONS = {".pem", ".key", ".p12", ".pfx", ".jks", ".keystore"}
BINARY_ART_EXTENSIONS = {".blend", ".glb", ".fbx", ".gltf", ".png", ".jpg", ".jpeg", ".webp", ".wav", ".ogg", ".mp3", ".mp4", ".mov", ".psd", ".exr"}
TEXT_SCAN_EXTENSIONS = {".py", ".gd", ".gdshader", ".godot", ".tscn", ".tres", ".json", ".md", ".yml", ".yaml", ".sh", ".toml", ".cfg", ".ini", ".txt"}
MAX_TEXT_SCAN_BYTES = 2 * 1024 * 1024
# Only high-confidence credential signatures. Never print the matched token.
SECRET_SIGNATURES = (
    ("private key header", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("GitHub access token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{36,}|github_pat_[A-Za-z0-9_]{40,})\b")),
    ("OpenAI project key", re.compile(r"\bsk-proj-[A-Za-z0-9_-]{30,}\b")),
    ("production payment key", re.compile(r"\bsk_live_[A-Za-z0-9]{20,}\b")),
)

MAX_DIRECT_BINARY_BYTES = 50 * 1024 * 1024
ID_PATTERN = re.compile(r"^(CHR|WPN)_[A-Za-z][A-Za-z0-9_]*$")
MAIN_SCENE = re.compile(r'(?m)^\s*run/main_scene\s*=\s*"res://([^"]+)"')
EXTERNAL_RESOURCE = re.compile(r'(?m)^\[ext_resource\s+[^\n]*\bpath="res://([^"]+)"')


def safe_path(root, raw):
    """Only accept stable relative POSIX paths staying within the repository."""
    if not isinstance(raw, str) or not raw or "\\" in raw or "\x00" in raw:
        return None
    parts = raw.split("/")
    if raw.startswith("/") or any(part in ("", ".", "..") or ":" in part for part in parts):
        return None
    candidate = root.joinpath(*parts)
    if not candidate.resolve().is_relative_to(root.resolve()):
        return None
    return candidate


def scan_source_tree(root, errors):
    """Reject obvious private key files, symlinks, oversized art and case collisions."""
    seen = {}
    for current, dirs, filenames in os.walk(root, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name not in IGNORED_DIRS)
        for name in dirs + sorted(filenames):
            item = Path(current) / name
            rel = item.relative_to(root).as_posix()
            lower_rel = rel.casefold()
            previous = seen.setdefault(lower_rel, rel)
            if previous != rel:
                errors.append("Case collision: " + previous + " / " + rel)
            if item.is_symlink():
                errors.append("Symbolic link is not approved: " + rel)
                continue
            if not item.is_file():
                continue
            lower = name.casefold()
            if lower == ".env" or lower.startswith(".env.") and lower != ".env.example":
                errors.append("Private environment file: " + rel)
            if lower in PRIVATE_FILENAMES or item.suffix.lower() in PRIVATE_EXTENSIONS:
                errors.append("Possible key/credential file: " + rel)
            if rel.startswith("game/") and item.suffix.casefold() == ".blend":
                errors.append("Editable Blender source inside game/: " + rel)
            if rel.startswith("art/") and item.suffix.casefold() == ".glb":
                errors.append("Runtime GLB export inside art/: " + rel)
            size = item.stat().st_size
            if item.suffix.lower() in BINARY_ART_EXTENSIONS and size > MAX_DIRECT_BINARY_BYTES:
                errors.append("Binary exceeds 50 MiB without reviewed LFS/storage plan: " + rel)
            if item.suffix.lower() in TEXT_SCAN_EXTENSIONS:
                if size > MAX_TEXT_SCAN_BYTES:
                    errors.append("Text file too large for secret inspection: " + rel)
                    continue
                try:
                    content = item.read_text(encoding="utf-8")
                except (UnicodeError, OSError):
                    errors.append("Unreadable UTF-8 source text: " + rel)
                    continue
                for secret_type, signature in SECRET_SIGNATURES:
                    if signature.search(content):
                        errors.append("Possible embedded credential (" + secret_type + "): " + rel)


def validate_git_index(root, errors):
    """Catch tracked ignored caches and gitlinks that ordinary tree walks skip."""
    if not (root / ".git").exists():
        return
    try:
        result = subprocess.run(
            ["git", "ls-files", "--stage", "-z"],
            cwd=root, capture_output=True, check=True, timeout=15,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        errors.append("Cannot inspect tracked Git source index")
        return
    for record in result.stdout.split(b"\x00"):
        if not record:
            continue
        try:
            meta, path = record.split(b"\t", 1)
            mode = meta.split(b" ", 1)[0]
            rel = path.decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            errors.append("Unreadable Git index record")
            continue
        if mode == b"160000":
            errors.append("Unreviewed git submodule: " + rel)
        if mode == b"120000":
            errors.append("Tracked symbolic link: " + rel)
        if any(part in IGNORED_DIRS for part in rel.split("/")):
            errors.append("Generated/cache directory committed to Git: " + rel)


def validate_registry(root, errors):
    path = root / "art/asset_registry.json"
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError, OSError) as exc:
        errors.append("Invalid asset JSON: " + str(exc))
        return
    if not isinstance(data, dict) or data.get("schema_version") != 1 or data.get("project") != "AETHERFALL: REALMS COLLIDE":
        errors.append("Asset registry identity/schema invalid")
        return
    assets = data.get("assets")
    if not isinstance(assets, list) or not assets:
        errors.append("Asset registry needs a nonempty assets list")
        return
    ids = set()
    destinations = set()
    for index, asset in enumerate(assets, start=1):
        if not isinstance(asset, dict):
            errors.append("Invalid asset object #" + str(index))
            continue
        identifier = asset.get("id")
        match = ID_PATTERN.fullmatch(identifier) if isinstance(identifier, str) else None
        if match is None:
            errors.append("Invalid asset ID #" + str(index))
            continue
        normalized = identifier.casefold()
        if normalized in ids:
            errors.append("Duplicate asset ID: " + identifier)
        ids.add(normalized)
        expected_type = "character" if match.group(1) == "CHR" else "weapon"
        if asset.get("type") != expected_type:
            errors.append("Asset ID/type mismatch: " + identifier)
        if not isinstance(asset.get("role"), str) or not asset["role"].strip():
            errors.append("Asset role missing: " + identifier)
        if asset.get("status") != "reserved_no_source":
            errors.append("Unverified asset status promotion: " + identifier)
        if asset.get("concept_status") not in (
            "aetherfall_approved", "aetherfall_design_brief",
            "legacy_owner_approved_candidate_for_aetherfall",
        ):
            errors.append("Unknown concept approval state: " + identifier)
        for key, prefix in (
            ("concept_dir", "art/concepts/"),
            ("source_dir", "art/blender/"),
            ("runtime_dir", "game/assets/"),
        ):
            raw = asset.get(key)
            candidate = safe_path(root, raw)
            if candidate is None or not raw.startswith(prefix) or candidate.name != identifier or not candidate.is_dir() or candidate.is_symlink():
                errors.append("Missing/unsafe " + key + ": " + identifier)
                continue
            unique = (key, candidate.resolve())
            if unique in destinations:
                errors.append("Reused asset path: " + identifier)
            destinations.add(unique)


def validate_godot(root, errors):
    project = root / "game/project.godot"
    if not project.is_file():
        return
    source = project.read_text(encoding="utf-8")
    if not re.search(r"(?m)^\s*config_version\s*=\s*5\s*$", source):
        errors.append("Godot 4 project config_version missing")
    matches = MAIN_SCENE.findall(source)
    if len(matches) != 1:
        errors.append("Godot main scene must be declared exactly once")
    else:
        main = safe_path(root, "game/" + matches[0])
        if main is None or not main.is_file() or main.suffix != ".tscn":
            errors.append("Godot main scene missing/unsafe: " + matches[0])
        elif not re.search(r"^\s*\[gd_scene\b", main.read_text(encoding="utf-8")):
            errors.append("Missing textual Godot scene header")
    game = root / "game"
    for extension in ("*.tscn", "*.tres"):
        for resource in game.rglob(extension):
            if ".godot" in resource.parts or resource.is_symlink():
                continue
            text = resource.read_text(encoding="utf-8")
            for raw in EXTERNAL_RESOURCE.findall(text):
                dep = safe_path(root, "game/" + raw)
                if dep is None or not dep.is_file():
                    errors.append("Missing/unsafe Godot ext_resource: " + raw)


def validate_legacy_hold(root, errors):
    path = root / "docs/legacy/shadowspire_migration.json"
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError, OSError) as exc:
        errors.append("Malformed legacy migration JSON: " + str(exc))
        return
    if not isinstance(data, dict) or data.get("schema_version") != 1 or data.get("project") != "AETHERFALL: REALMS COLLIDE":
        errors.append("Legacy migration identity/schema invalid")
        return
    if data.get("source_repository") is not None or data.get("source_code_available") is not False:
        errors.append("Legacy source unexpectedly promoted from NOT_FOUND")
    if data.get("original_godot_source_migrated") is not False or data.get("original_unreal_source_migrated") is not False:
        errors.append("Unproved legacy source transfer claim")
    if data.get("deletion_status") != "BLOCKED_NO_VERIFIED_OWNED_REPOSITORY_OR_TRANSFER":
        errors.append("Unverified deletion status promotion")


def check(root=ROOT):
    root = Path(root).resolve()
    errors = []
    for rel in REQUIRED_FILES:
        candidate = safe_path(root, rel)
        if candidate is None or not candidate.is_file() or candidate.is_symlink():
            errors.append("Missing/unsafe file: " + rel)
    for rel in REQUIRED_DIRS:
        candidate = safe_path(root, rel)
        if candidate is None or not candidate.is_dir() or candidate.is_symlink():
            errors.append("Missing/unsafe directory: " + rel)
    scan_source_tree(root, errors)
    validate_git_index(root, errors)
    validate_registry(root, errors)
    validate_godot(root, errors)
    validate_legacy_hold(root, errors)
    return errors


def main():
    failures = check()
    if failures:
        for failure in failures:
            print("FAIL: " + failure, file=sys.stderr)
        return 1
    print("PASS: source/asset path safety, Godot reference checks and migration status (STATIC ONLY)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

