#!/usr/bin/env python3
"""Fail-closed static evidence gates for AETHERFALL's Blender-to-Godot handoffs.

Only verifies manifest consistency, registered identity, source hashes and file headers.
It CANNOT attest Blender/Godot execution, visual similarity or owner identity.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path

PROJECT = "AETHERFALL: REALMS COLLIDE"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")
ASSET_ID = re.compile(r"CHR_[A-Za-z][A-Za-z0-9_]*\Z")
STAGE_NAMES = (
    "reference_lock", "import_scale_pedestal", "mesh_repair_symmetry",
    "retopo_3p_1p_lods", "uv_pbr_bakes", "rig_sockets_export",
    "blender_native_review", "godot_native_import",
    "camera_animation_gameplay", "owner_review",
)
STAGE_STATUSES = {"NOT_RUN", "PASS", "FAIL", "BLOCKED"}
PRODUCTION_STATUSES = {"NOT_VERIFIED", "IN_PROGRESS", "BLOCKED", "READY_FOR_OWNER_REVIEW", "GAME_READY"}
STAGE_CAPTURE = {
    "reference_lock": "REFERENCE_REVIEW",
    "import_scale_pedestal": "BLENDER_NATIVE",
    "mesh_repair_symmetry": "BLENDER_NATIVE",
    "retopo_3p_1p_lods": "BLENDER_NATIVE",
    "uv_pbr_bakes": "BLENDER_NATIVE",
    "rig_sockets_export": "BLENDER_NATIVE",
    "blender_native_review": "BLENDER_NATIVE",
    "godot_native_import": "GODOT_NATIVE",
    "camera_animation_gameplay": "GODOT_NATIVE",
    "owner_review": "OWNER_REVIEW",
}
MEDIA_TYPES = {".png", ".jpg", ".jpeg", ".webp", ".mp4"}
MAX_MANIFEST_BYTES = 1024 * 1024
MAX_HASHED_FILE_BYTES = 512 * 1024 * 1024  # Do not load evidence or binaries into memory.
CHARACTER_GATES = (
    "identity_owner_approved", "source_archived", "concept_package_reviewed", "blockout_approved",
    "model_verified", "rig_animation_verified", "godot_import_verified", "gameplay_verified",
)


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _obj(value):
    return value if isinstance(value, dict) else {}


def _json_file(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_MANIFEST_BYTES:
        raise ValueError("JSON file absent, unsafe or oversized")
    return json.loads(path.read_text(encoding="utf-8"))


def _file(root, name, prefix, suffix=None):
    """Require a regular in-repo file and prohibit symlinks in every path component."""
    if not isinstance(name, str) or not name or "\\" in name or "\x00" in name:
        return None
    if not name.startswith(prefix) or (suffix and not name.lower().endswith(suffix)):
        return None
    parts = name.split("/")
    if any(not part or part in (".", "..") or ":" in part for part in parts):
        return None
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink():
            return None
    if not current.resolve().is_relative_to(root.resolve()) or not current.is_file():
        return None
    return current


def _signature_ok(path):
    """Cheap wrong-extension defence, NOT an engine parser or proof of honest capture."""
    size = path.stat().st_size
    with path.open("rb") as stream:
        head = stream.read(32)
    ext = path.suffix.lower()
    if ext == ".glb":
        if size < 20 or head[:4] != b"glTF":
            return False
        version, declared = struct.unpack("<II", head[4:12])
        return version == 2 and declared == size and head[16:20] == b"JSON"
    if ext == ".blend":
        return size >= 12 and head[:7] == b"BLENDER" and head[7:8] in (b"_", b"-") and head[8:9] in (b"v", b"V")
    if ext == ".png":
        return head.startswith(b"\x89PNG\r\n\x1a\n") and head[12:16] == b"IHDR"
    if ext in (".jpg", ".jpeg"):
        return head.startswith(b"\xff\xd8\xff")
    if ext == ".webp":
        return head.startswith(b"RIFF") and head[8:12] == b"WEBP"
    if ext == ".mp4":
        return size >= 12 and head[4:8] == b"ftyp"
    if ext == ".fbx":
        return head.startswith(b"Kaydara FBX Binary  \x00") or head.startswith(b"; FBX")
    if ext == ".obj":
        return size > 0
    if ext in (".json", ".md"):
        return size > 0
    return False


def _hashed(root, file_name, digest, prefix, extensions=None):
    if not isinstance(digest, str) or not SHA256.fullmatch(digest):
        return False
    path = _file(root, file_name, prefix)
    if path is None or (extensions and path.suffix.lower() not in extensions):
        return False
    try:
        if not 0 < path.stat().st_size <= MAX_HASHED_FILE_BYTES or not _signature_ok(path):
            return False
        actual = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                actual.update(block)
        return actual.hexdigest() == digest
    except (OSError, ValueError, struct.error):
        return False


def _registered(root, asset_id):
    try:
        registry = _json_file(root / "art/asset_registry.json")
        plan = _json_file(root / "docs/characters/plans" / f"{asset_id}.json")
    except (OSError, ValueError, UnicodeError):
        return None, None
    if not isinstance(registry, dict) or registry.get("project") != PROJECT or not isinstance(registry.get("assets"), list):
        return None, None
    entry = next((x for x in registry["assets"] if isinstance(x, dict) and x.get("id") == asset_id and x.get("type") == "character"), None)
    if not isinstance(plan, dict) or plan.get("project") != PROJECT or plan.get("character_id") != asset_id:
        return entry, None
    return entry, plan


def _evidence_prefixes(asset_id, stage):
    char = f"evidence/characters/{asset_id}/"
    if STAGE_CAPTURE[stage] == "BLENDER_NATIVE":
        return (char, f"evidence/blender/{asset_id}/")
    if STAGE_CAPTURE[stage] == "GODOT_NATIVE":
        return (char, f"evidence/godot/{asset_id}/")
    return (char,)


def _stage_proof(root, asset_id, stage, item, source_commit):
    raw = item.get("evidence_path")
    kind = STAGE_CAPTURE[stage]
    ext = {".json", ".md"} if kind == "OWNER_REVIEW" else (
        {".json", ".md", ".png", ".jpg", ".jpeg", ".webp"} if kind == "REFERENCE_REVIEW"
        else ({".mp4"} if stage == "camera_animation_gameplay" else MEDIA_TYPES)
    )
    if item.get("capture_source") != kind or not _nonempty(item.get("tool_version")):
        return False
    if not _nonempty(item.get("source_commit")) or not COMMIT.fullmatch(item["source_commit"]):
        return False
    if source_commit is None or item["source_commit"] != source_commit:
        return False
    return any(_hashed(root, raw, item.get("evidence_sha256"), prefix, ext)
               for prefix in _evidence_prefixes(asset_id, stage))


def _check_manifest(root, path):
    failures = []
    asset_id = path.parent.name
    tag = path.relative_to(root).as_posix()
    if not ASSET_ID.fullmatch(asset_id):
        return [f"Blender handoff outside registered CHR_ID folder: {tag}"]
    try:
        doc = _json_file(path)
    except (OSError, ValueError, UnicodeError):
        return [f"Malformed or oversized Blender handoff JSON: {tag}"]
    if not isinstance(doc, dict):
        return [f"Malformed Blender handoff object: {tag}"]
    if type(doc.get("schema_version")) is not int or doc["schema_version"] != 1 or doc.get("project") != PROJECT or doc.get("asset_id") != asset_id:
        failures.append(f"Blender handoff identity mismatch: {tag}")
    entry, plan = _registered(root, asset_id)
    if entry is None or plan is None or entry.get("source_dir") != f"art/blender/characters/{asset_id}" or entry.get("concept_dir") != f"art/concepts/characters/{asset_id}":
        failures.append(f"Blender handoff not linked to registered character/plan: {tag}")
    state = doc.get("production_status")
    if not isinstance(state, str) or state not in PRODUCTION_STATUSES:
        failures.append(f"Unknown Blender handoff production status: {tag}")
        state = "INVALID"
    sha = doc.get("source_commit")
    if sha is not None and (not isinstance(sha, str) or not COMMIT.fullmatch(sha)):
        failures.append(f"Invalid Blender source commit: {tag}")
        sha = None
    stages = doc.get("stages")
    if not isinstance(stages, dict) or set(stages) != set(STAGE_NAMES):
        failures.append(f"Incomplete Blender handoff stages: {tag}")
        stages = {}
    earlier_pass = True
    for stage in STAGE_NAMES:
        item = stages.get(stage)
        if not isinstance(item, dict) or not isinstance(item.get("status"), str) or item["status"] not in STAGE_STATUSES:
            failures.append(f"Missing/invalid Blender stage {stage}: {tag}")
            earlier_pass = False
            continue
        if item["status"] == "PASS":
            if not earlier_pass:
                failures.append(f"Blender handoff stage out of order {stage}: {tag}")
            if not _stage_proof(root, asset_id, stage, item, sha):
                failures.append(f"Unverified Blender stage PASS {stage}: {tag}")
            if stage == "reference_lock":
                prov = _obj(doc.get("provenance"))
                ref = _obj(_obj(plan).get("concept_reference"))
                if (entry is None or entry.get("concept_status") != "aetherfall_approved" or
                    prov.get("source_reference_path") != ref.get("repo_path") or
                    prov.get("source_reference_sha256") != ref.get("sha256") or
                    not _hashed(root, prov.get("source_reference_path"), prov.get("source_reference_sha256"),
                                f"art/concepts/characters/{asset_id}/", {".png", ".jpg", ".jpeg", ".webp"})):
                    failures.append(f"Blender reference-lock PASS missing approved canonical source: {tag}")
        else:
            earlier_pass = False
    if state in ("READY_FOR_OWNER_REVIEW", "GAME_READY"):
        required = STAGE_NAMES[:-1] if state == "READY_FOR_OWNER_REVIEW" else STAGE_NAMES
        if any(not isinstance(stages.get(s), dict) or stages[s].get("status") != "PASS" for s in required):
            failures.append(f"Blender handoff prematurely promoted: {tag}")
        if not isinstance(sha, str) or not COMMIT.fullmatch(sha):
            failures.append(f"Blender handoff source commit missing: {tag}")
        if entry is None or plan is None or not all((
            entry.get("concept_status") == "aetherfall_approved",
            _obj(plan.get("concept_reference")).get("archive_status") == "source_verified",
            isinstance(plan.get("gates"), dict),
        )):
            failures.append(f"Blender handoff lacks approved archived character plan: {tag}")
        elif any(plan["gates"].get(gate) is not True for gate in CHARACTER_GATES):
            failures.append(f"Blender handoff character production gates incomplete: {tag}")
        provenance = doc.get("provenance")
        blender = doc.get("blender")
        mesh = doc.get("mesh")
        textures = doc.get("textures")
        export = doc.get("export")
        if not isinstance(provenance, dict) or provenance.get("rights_cleared") is not True or provenance.get("owner_visual_reference_approved") is not True:
            failures.append(f"Blender handoff source approval missing: {tag}")
            provenance = {}
        raw_prefix = f"art/blender/characters/{asset_id}/raw/"
        if not _hashed(root, provenance.get("raw_sculpt_path"), provenance.get("raw_sculpt_sha256"), raw_prefix, {".glb", ".fbx", ".obj", ".blend"}):
            failures.append(f"Blender handoff raw sculpt missing/unsafe: {tag}")
        ref_prefix = f"art/concepts/characters/{asset_id}/"
        if not _hashed(root, provenance.get("source_reference_path"), provenance.get("source_reference_sha256"), ref_prefix, {".png", ".jpg", ".jpeg", ".webp"}):
            failures.append(f"Blender handoff canonical reference missing: {tag}")
        elif plan is not None and (provenance.get("source_reference_path") != _obj(plan.get("concept_reference")).get("repo_path") or provenance.get("source_reference_sha256") != _obj(plan.get("concept_reference")).get("sha256")):
            failures.append(f"Blender handoff source differs from character plan: {tag}")
        try:
            locks = _json_file(root / "docs/characters/CANON_LOCKS.json")
            locked = _obj(_obj(locks).get("locked_characters")).get(asset_id)
        except (OSError, ValueError, UnicodeError):
            locked = None
            failures.append(f"Blender handoff canonical lock registry unavailable: {tag}")
        if isinstance(locked, dict):
            original = _obj(locked.get("source"))
            if provenance.get("source_reference_path") != original.get("path") or provenance.get("source_reference_sha256") != original.get("sha256"):
                failures.append(f"Blender handoff differs from pinned art lock: {tag}")
        if not isinstance(blender, dict) or not _hashed(root, blender.get("source_blend_path"), blender.get("source_blend_sha256"), f"art/blender/characters/{asset_id}/", {".blend"}):
            failures.append(f"Blender handoff editable source missing: {tag}")
        if not isinstance(mesh, dict) or any(type(mesh.get(key)) is not int or mesh[key] <= 0 for key in ("third_person_triangle_count", "first_person_triangle_count", "lod1_triangle_count", "lod2_triangle_count")) or (isinstance(mesh, dict) and (mesh.get("weight_paint_reviewed") is not True or not _nonempty(mesh.get("armature_name")))) or (isinstance(mesh, dict) and all(type(mesh.get(k)) is int for k in ("third_person_triangle_count", "lod1_triangle_count", "lod2_triangle_count")) and not (mesh["third_person_triangle_count"] > mesh["lod1_triangle_count"] > mesh["lod2_triangle_count"])):
            failures.append(f"Blender handoff 1P/3P mesh audit incomplete: {tag}")
        if not isinstance(textures, dict) or textures.get("uv_nonoverlap_verified") is not True or textures.get("all_maps_saved") is not True:
            failures.append(f"Blender handoff UV/PBR audit incomplete: {tag}")
        expected_runtime = entry.get("runtime_dir") if isinstance(entry, dict) else None
        if not isinstance(export, dict) or not isinstance(expected_runtime, str):
            failures.append(f"Blender handoff engine exports missing: {tag}")
        else:
            prefix = expected_runtime + "/"
            third = export.get("third_person_glb_path")
            first = export.get("first_person_glb_path")
            if not all((
                _hashed(root, third, export.get("third_person_glb_sha256"), prefix, {".glb"}),
                _hashed(root, first, export.get("first_person_glb_sha256"), prefix, {".glb"}),
                third != first,
                export.get("third_person_glb_sha256") != export.get("first_person_glb_sha256"),
                _nonempty(export.get("godot_version")),
                isinstance(export.get("animation_clips"), list) and bool(export["animation_clips"]) and all(_nonempty(c) for c in export["animation_clips"]),
                isinstance(export.get("sockets"), list) and bool(export["sockets"]) and all(_nonempty(s) for s in export["sockets"]),
            )):
                failures.append(f"Blender handoff 1P/3P engine exports missing/unsafe: {tag}")
        if state == "READY_FOR_OWNER_REVIEW":
            if _obj(stages.get("owner_review")).get("status") == "PASS" or _obj(doc.get("owner_signoff")).get("approved") is True:
                failures.append(f"Blender owner review already asserted at READY stage: {tag}")
    if state == "GAME_READY":
        owner = doc.get("owner_signoff")
        owner_stage = _obj(stages.get("owner_review"))
        if not isinstance(owner, dict) or owner.get("approved") is not True or not _nonempty(owner.get("reviewer")) or owner.get("review_evidence_path") != owner_stage.get("evidence_path") or not _hashed(root, owner.get("review_evidence_path"), owner.get("review_evidence_sha256"), f"evidence/characters/{asset_id}/", {".json", ".md"}) or owner.get("review_evidence_sha256") != owner_stage.get("evidence_sha256"):
            failures.append(f"Blender handoff owner signoff missing/unmatched: {tag}")
    return failures


def check(root):
    """Check manifest assertions. Empty handoffs indicate zero promoted models."""
    root = Path(root).resolve()
    folder = root / "art/blender/characters"
    if not folder.is_dir():
        return []
    failures = []
    for path in sorted(folder.glob("*/handoff.json")):
        if path.is_symlink() or path.parent.is_symlink():
            failures.append(f"Unsafe Blender handoff symlink: {path.relative_to(root)}")
        else:
            failures.extend(_check_manifest(root, path))
    return failures


if __name__ == "__main__":
    import sys
    issues = check(Path(__file__).resolve().parents[1])
    for issue in issues:
        print("FAIL: " + issue, file=sys.stderr)
    if not issues:
        print("PASS: Blender handoffs (STATIC identity/header/hash/claim consistency; NOT native art proof)")
    raise SystemExit(bool(issues))