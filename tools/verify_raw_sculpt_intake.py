#!/usr/bin/env python3
"""Read-only owner raw-sculpt screenshot seal verification.

A successful result means: reference MANIFEST and (optionally) eight screenshot BYTES
were validated. It does NOT establish 3D mesh, Blender, Godot, gameplay, or release.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REGISTER_REL = "docs/characters/RAW_SCULPT_REFERENCE_REGISTER_2026-11-26.json"
EXPECTED_SHA256 = {
    "40174.jpg": "5f2562e32ad22c4919dacfb613552d500e9c0f4661df250d3e364c1e422bb836",
    "40166.jpg": "4474d206af3a061e2deff701a4d9ff07419c65fb318a8c92c8a6bfcacc63d70e",
    "40168.jpg": "8e3a3b52605b860cc199d9cb9c070812f306613043068d082fa661bbea4c89ea",
    "40170.jpg": "1bf470f77fec4e0f82768336ce35f630962e091dccdd669bc3a1ed0a41d20d0a",
    "40149.jpg": "c84cbdae4e6e7a4ed5485378f4da2a662be88555826792dccd4aab20734b22b2",
    "40151.jpg": "d994a9d116ea09015bd1d40f9c5bd98497af8bfc94bd6c753c257d0ae9b07081",
    "40136.jpg": "b67050e84e4a0868c94d85901dac75810b2d7eaa9bb73d35578b47cec54abf44",
    "40132.jpg": "f33ed03fa9926820bbf06e90da517ae5c8289693bace06d1c6f4dbcab7ce5233",
}
EXPECTED_ROLES = {
    "40174.jpg": "CHR_Raven", "40166.jpg": "CHR_Raven",
    "40168.jpg": None, "40170.jpg": None,
    "40149.jpg": "CHR_Razor", "40151.jpg": "CHR_Razor",
    "40136.jpg": "CHR_Vellaris_Bloodshield", "40132.jpg": "CHR_Vellaris_Bloodshield",
}
EXPECTED_LEN = {
    "40174.jpg": 138076, "40166.jpg": 88972, "40168.jpg": 77104, "40170.jpg": 40212,
    "40149.jpg": 139828, "40151.jpg": 59218, "40136.jpg": 77254, "40132.jpg": 49248,
}
EXPECTED_LIB_PREFIX = "/SIRE Games Concepts/Concept Art and Visuals/AETHERFALL/Raw Sculpt References/2026-11-26/"
ALLOWED_KIND = {
    "sculpt_visual_reference", "viewer_screenshot", "unassigned_candidate",
    "mesh_statistics_screenshot", "untextured_sculpt_reference",
}


def validate_register(record: object) -> list[str]:
    issues = []
    if not isinstance(record, dict):
        return ["register is not an object"]
    if record.get("schema_version") != 1 or record.get("project") != "AETHERFALL: REALMS COLLIDE":
        issues.append("wrong schema/project")
    if record.get("register_id") != "AF-RAW-SCULPT-QUALITY-LOCK-20261126":
        issues.append("wrong immutable seal ID")
    entries = record.get("items")
    if not isinstance(entries, list) or len(entries) != 8 or record.get("screenshot_count") != 8:
        return issues + ["exactly eight screenshots required"]
    seen = set()
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            issues.append(f"item {index} not object")
            continue
        name = item.get("original_upload_name")
        if name not in EXPECTED_SHA256:
            issues.append(f"unknown source alias: {name!r}")
            continue
        if name in seen:
            issues.append(f"duplicate source alias: {name}")
        seen.add(name)
        if item.get("original_bytes_sha256") != EXPECTED_SHA256[name]:
            issues.append(f"source SHA mismatch: {name}")
        if item.get("original_bytes") != EXPECTED_LEN[name]:
            issues.append(f"source size mismatch: {name}")
        if item.get("character_id") != EXPECTED_ROLES[name]:
            issues.append(f"character identity drift: {name}")
        if item.get("reference_class") not in ALLOWED_KIND:
            issues.append(f"unknown reference class: {name}")
        if item.get("detected_media_type") != "image/webp" or item.get("detected_format") != "WEBP":
            issues.append(f"forged media signature claim: {name}")
        if item.get("dimensions_pixels") != [1536, 1384]:
            issues.append(f"unexpected claimed dimensions: {name}")
        out = item.get("archived_filename")
        if not isinstance(out, str) or not out.startswith(name[:-4]+"__") or not out.endswith(".webp") or "/" in out or "\\" in out or ".." in out:
            issues.append(f"unsafe archive filename: {name}")
        path = item.get("library_archive_path")
        if not isinstance(path, str) or not path.startswith(EXPECTED_LIB_PREFIX) or path != EXPECTED_LIB_PREFIX+out:
            issues.append(f"wrong archive reference: {name}")
        if item.get("git_binary_status") != "NOT_COMMITTED_IN_GIT":
            issues.append(f"false Git binary claim: {name}")
        if item.get("approval_scope") != "OWNER_PRESENTED_AS_SCULPT_QUALITY_TARGET_ONLY":
            issues.append(f"invalid approval claim: {name}")
        for assertion in ("canon_replacement", "actual_3d_source_file_verified", "native_blender_or_godot_verified"):
            if item.get(assertion) is not False:
                issues.append(f"unsupported promotion {assertion}: {name}")
        for text_key in ("observed_content", "limitations_and_open_identity_gate"):
            if not isinstance(item.get(text_key), str) or len(item[text_key].strip()) < 18:
                issues.append(f"missing evidence caveat {text_key}: {name}")
    if seen != set(EXPECTED_SHA256):
        issues.append("missing/extraneous screenshot alias")
    stats = record.get("reported_external_mesh_statistics")
    if not isinstance(stats, dict) or (stats.get("screenshot") != "40151.jpg" or
       stats.get("faces_ui") != 2460470 or stats.get("vertices_ui") != 1229959 or
       stats.get("status") != "SCREENSHOT_ONLY_UNVERIFIED_SOURCE_MESH"):
        issues.append("unverified Meshy UI stats altered or promoted")
    g = record.get("production_gate")
    if not isinstance(g, dict):
        issues.append("missing production gate")
    else:
        for k in ("raw_mesh_file_supplied", "blender_native_source_verified", "retopo_and_rig_verified", "godot_runtime_verified", "owner_final_model_approval"):
            if g.get(k) is not False:
                issues.append("unsupported production gate: " + k)
    return issues


def validate_local_screenshot_bytes(register: dict, directory: Path) -> list[str]:
    issues=[]
    for item in register.get("items", []):
        filename=item.get("original_upload_name", "")
        if filename not in EXPECTED_SHA256:
            issues.append(f"unsafe or unexpected source path {filename!r}")
            continue
        p=directory / filename
        if not p.is_file() or p.is_symlink():
            issues.append(f"missing/unreadable source screenshot: {filename}")
            continue
        payload=p.read_bytes()
        if len(payload)!=EXPECTED_LEN[filename]:
            issues.append(f"file size differs: {filename}")
        if hashlib.sha256(payload).hexdigest()!=EXPECTED_SHA256[filename]:
            issues.append(f"file hash differs: {filename}")
        if len(payload)<12 or payload[:4]!=b"RIFF" or payload[8:12]!=b"WEBP":
            issues.append(f"actual bytes not WEBP: {filename}")
    return issues


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description="Read-only AETHERFALL raw sculpt screenshot provenance gate. Not native 3D evidence.")
    parser.add_argument("--manifest",type=Path, default=Path(__file__).resolve().parents[1]/REGISTER_REL)
    parser.add_argument("--source-dir", type=Path, default=None, help="Optional directory containing original filenames 40174.jpg etc. Required to verify actual screenshot bytes.")
    parser.add_argument("--json",action="store_true")
    args=parser.parse_args(argv)
    errors=[]
    try:
        data=json.loads(args.manifest.read_text(encoding="utf-8"))
        errors.extend(validate_register(data))
        if args.source_dir is not None:
            errors.extend(validate_local_screenshot_bytes(data, args.source_dir))
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        errors.append(f"cannot inspect manifest: {type(exc).__name__}: {exc}")
    if errors:
        outcome={"result":"BLOCKED", "proof_type":"SPEC_OR_SCREENSHOT_ONLY", "errors":errors,
                 "native_blender": "NOT_RUN", "native_godot": "NOT_RUN"}
    else:
        outcome={"result":"SCREENSHOT_BYTES_VERIFIED_ONLY" if args.source_dir else "METADATA_VALIDATED_ONLY",
                 "count":8, "source_bytes_checked":bool(args.source_dir),
                 "native_blender":"NOT_RUN", "native_godot":"NOT_RUN", "model_ready":False, "errors":[]}
    if args.json: print(json.dumps(outcome,indent=2))
    else: print(outcome["result"] + (": " + "; ".join(errors) if errors else " — no raw 3D or gameplay proof"))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())