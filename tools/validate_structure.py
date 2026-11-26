#!/usr/bin/env python3
"""Offline source-layout checks; not a Godot or Blender runtime test."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md",
    "AGENTS.md",
    ".gitignore",
    ".gitattributes",
    "game/project.godot",
    "game/scenes/bootstrap/main.tscn",
    "art/asset_registry.json",
    "docs/architecture/REPO_LAYOUT.md",
    "docs/art/ASSET_PIPELINE.md",
    "evidence/README.md",
)
REQUIRED_DIRS = (
    "game/scenes/characters/heroes",
    "game/scenes/characters/enemies",
    "game/scenes/levels/realms",
    "game/scripts/core",
    "game/scripts/combat",
    "game/scripts/abilities",
    "game/assets/characters/heroes",
    "game/assets/weapons",
    "game/assets/worlds",
    "game/audio/music",
    "game/shaders",
    "art/blender/characters",
    "art/blender/weapons",
    "art/concepts/characters",
    "evidence/godot",
    "evidence/blender",
    "evidence/device",
    "tests",
)


def check():
    errors = []
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            errors.append("Missing file: " + rel)
    for rel in REQUIRED_DIRS:
        if not (ROOT / rel).is_dir():
            errors.append("Missing directory: " + rel)
    project = ROOT / "game/project.godot"
    if project.is_file():
        content = project.read_text(encoding="utf-8")
        match = re.search(r'^run/main_scene\s*=\s*"res://([^"]+)"', content, re.M)
        if match is None:
            errors.append("Godot main scene not declared")
        else:
            scene = ROOT / "game" / match.group(1)
            if not scene.is_file() or not scene.resolve().is_relative_to((ROOT / "game").resolve()):
                errors.append("Godot main scene does not resolve inside game/: " + match.group(1))
            elif "[gd_scene" not in scene.read_text(encoding="utf-8"):
                errors.append("Godot main scene is not a textual .tscn")
        if "config_version=5" not in content:
            errors.append("Missing Godot 4 project config version")
    registry_file = ROOT / "art/asset_registry.json"
    if registry_file.is_file():
        try:
            registry = json.loads(registry_file.read_text(encoding="utf-8"))
            if registry.get("schema_version") != 1:
                errors.append("Unexpected asset registry schema")
            ids = set()
            for asset in registry["assets"]:
                asset_id = asset["id"]
                if asset_id in ids:
                    errors.append("Duplicate asset id: " + asset_id)
                ids.add(asset_id)
                if asset["status"] != "reserved_no_source":
                    errors.append("Non-placeholder status without supporting proof: " + asset_id)
                for key in ("concept_dir", "source_dir", "runtime_dir"):
                    rel = Path(asset[key])
                    if rel.is_absolute() or ".." in rel.parts or not (ROOT / rel).is_dir():
                        errors.append("Missing or unsafe " + key + " for " + asset_id)
        except (ValueError, KeyError, TypeError) as exc:
            errors.append("Invalid asset registry: " + str(exc))
    return errors


def main():
    failures = check()
    if failures:
        for failure in failures:
            print("FAIL: " + failure, file=sys.stderr)
        return 1
    print("PASS: layout, Godot scene reference and reserved asset paths (static checks only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
