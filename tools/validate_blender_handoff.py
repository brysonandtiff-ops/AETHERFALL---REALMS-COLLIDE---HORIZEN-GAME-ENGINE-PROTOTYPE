#!/usr/bin/env python3
"""Static AETHERFALL Blender handoff honesty gate (NOT native model validation)."""

import hashlib
import json
import re
from pathlib import Path

PROJECT = "AETHERFALL: REALMS COLLIDE"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
ASSET_ID = re.compile(r"CHR_[A-Za-z][A-Za-z0-9_]*\Z")
STAGE_NAMES = (
    "reference_lock", "import_scale_pedestal", "mesh_repair_symmetry",
    "retopo_3p_1p_lods", "uv_pbr_bakes", "rig_sockets_export",
    "blender_native_review", "godot_native_import",
    "camera_animation_gameplay", "owner_review",
)
STAGE_STATUSES = {"NOT_RUN", "PASS", "FAIL", "BLOCKED"}
PRODUCTION_STATUSES = {
    "NOT_VERIFIED", "IN_PROGRESS", "BLOCKED", "READY_FOR_OWNER_REVIEW", "GAME_READY"
}


def _file(root, name, prefix, suffix=None):
    """Resolve an existing in-repo file without traversal, symlinks or guessed absolutes."""
    if not isinstance(name, str) or not name or "\\" in name or "\x00" in name:
        return None
    parts = name.split("/")
    if any(not part or part in (".", "..") or ":" in part for part in parts):
        return None
    if not name.startswith(prefix):
        return None
    if suffix and not name.endswith(suffix):
        return None
    target = root.joinpath(*parts)
    if not target.resolve().is_relative_to(root.resolve()) or not target.is_file() or target.is_symlink():
        return None
    return target


def _hashed(root, file_name, digest, prefix, suffix=None):
    file = _file(root, file_name, prefix, suffix)
    return bool(file is not None and isinstance(digest, str) and
                SHA256.fullmatch(digest) and
                hashlib.sha256(file.read_bytes()).hexdigest() == digest)


def _check_manifest(root, file):
    failures = []
    asset_id = file.parent.name
    tag = file.relative_to(root).as_posix()
    if not ASSET_ID.fullmatch(asset_id):
        return [f"Blender handoff outside registered CHR_ID folder: {tag}"]
    try:
        doc = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return [f"Malformed Blender handoff JSON: {tag}"]
    if not isinstance(doc, dict):
        return [f"Malformed Blender handoff object: {tag}"]
    if doc.get("schema_version") != 1 or doc.get("project") != PROJECT or doc.get("asset_id") != asset_id:
        failures.append(f"Blender handoff identity mismatch: {tag}")
    state = doc.get("production_status")
    if state not in PRODUCTION_STATUSES:
        failures.append(f"Unknown Blender handoff production status: {tag}")
    stages = doc.get("stages")
    if not isinstance(stages, dict) or set(stages) != set(STAGE_NAMES):
        failures.append(f"Incomplete Blender handoff stages: {tag}")
        stages = {}
    for stage in STAGE_NAMES:
        item = stages.get(stage)
        if not isinstance(item, dict) or item.get("status") not in STAGE_STATUSES:
            failures.append(f"Missing/invalid Blender stage {stage}: {tag}")
            continue
        if item["status"] == "PASS":
            if not _hashed(root, item.get("evidence_path"), item.get("evidence_sha256"), "evidence/"):
                failures.append(f"Unverified Blender stage PASS {stage}: {tag}")
    if state in ("READY_FOR_OWNER_REVIEW", "GAME_READY"):
        required_stages = STAGE_NAMES[:-1] if state == "READY_FOR_OWNER_REVIEW" else STAGE_NAMES
        if any(not isinstance(stages.get(s), dict) or stages[s].get("status") != "PASS" for s in required_stages):
            failures.append(f"Blender handoff prematurely promoted: {tag}")
    if state == "GAME_READY":
        provenance = doc.get("provenance") or {}
        blender = doc.get("blender") or {}
        export = doc.get("export") or {}
        owner = doc.get("owner_signoff") or {}
        if not isinstance(provenance, dict) or not (
            provenance.get("rights_cleared") is True and
            provenance.get("owner_visual_reference_approved") is True
        ):
            failures.append(f"Blender game-ready source approval missing: {tag}")
        else:
            if not _hashed(root, provenance.get("raw_sculpt_path"), provenance.get("raw_sculpt_sha256"), "art/"):
                failures.append(f"Blender game-ready raw sculpt missing: {tag}")
            if not _hashed(root, provenance.get("source_reference_path"), provenance.get("source_reference_sha256"),
                           f"art/concepts/characters/{asset_id}/"):
                failures.append(f"Blender game-ready canonical reference missing: {tag}")
        if not isinstance(blender, dict) or not _hashed(
            root, blender.get("source_blend_path"), blender.get("source_blend_sha256"),
            f"art/blender/characters/{asset_id}/", ".blend"
        ):
            failures.append(f"Blender game-ready editable .blend missing: {tag}")
        if not isinstance(export, dict) or not all((
            _hashed(root, export.get("third_person_glb_path"), export.get("third_person_glb_sha256"),
                    "game/assets/characters/", ".glb"),
            _hashed(root, export.get("first_person_glb_path"), export.get("first_person_glb_sha256"),
                    "game/assets/characters/", ".glb"),
            isinstance(export.get("godot_version"), str) and bool(export["godot_version"].strip()),
        )):
            failures.append(f"Blender game-ready 1P/3P engine exports missing: {tag}")
        if not isinstance(owner, dict) or owner.get("approved") is not True or not owner.get("reviewer"):
            failures.append(f"Blender game-ready owner signoff missing: {tag}")
        if not isinstance(doc.get("source_commit"), str) or not re.fullmatch(r"[0-9a-f]{40}", doc["source_commit"]):
            failures.append(f"Blender game-ready source commit missing: {tag}")
    return failures


def check(root):
    """Validate any recorded handoffs; no handoffs means no model is certified."""
    root = Path(root).resolve()
    base = root / "art/blender/characters"
    if not base.is_dir():
        return []
    failures = []
    for manifest in sorted(base.glob("*/handoff.json")):
        if manifest.is_symlink():
            failures.append(f"Symlinked Blender handoff forbidden: {manifest.relative_to(root)}")
        else:
            failures.extend(_check_manifest(root, manifest))
    return failures


if __name__ == "__main__":
    import sys
    root = Path(__file__).resolve().parents[1]
    issues = check(root)
    for issue in issues:
        print("FAIL: " + issue, file=sys.stderr)
    if not issues:
        print("PASS: Blender handoff manifests (STATIC CLAIM/EVIDENCE INTEGRITY ONLY; NOT NATIVE ART PROOF)")
    raise SystemExit(bool(issues))
