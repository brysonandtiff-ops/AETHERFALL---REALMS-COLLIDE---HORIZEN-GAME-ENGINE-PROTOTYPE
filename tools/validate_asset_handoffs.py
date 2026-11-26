#!/usr/bin/env python3
"""Evidence-aware AETHERFALL asset intake (source checks only, never art approval).

The registry is authoritative for IDs/approval. A per-asset receipt establishes
only verifiable files, paths and checksums. Native Blender/Godot proof remains
a separate human-reviewed gate. No binary processing, payments or agent calls.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "art/asset_registry.json"
RECEIPTS = "art/handoffs"
STAGES = (
    "reserved_no_source",
    "concept_recorded",
    "blender_source_recorded",
    "runtime_export_recorded",
    "native_import_reviewed",
)
FILE_KINDS = ("concept", "blender", "runtime")
ALLOWED_EXTENSIONS = {
    "concept": {".png", ".jpg", ".jpeg", ".webp", ".pdf"},
    "blender": {".blend"},
    "runtime": {".glb"},
    "log": {".txt", ".log"},
    "capture": {".png", ".mp4"},
}
MAX_MANIFEST_BYTES = 512 * 1024
HASH = re.compile(r"^[0-9a-f]{64}$")
ASSET_ID = re.compile(r"^(?:CHR|WPN)_[A-Za-z][A-Za-z0-9_]*$")


def no_duplicate_keys(pairs):
    obj = {}
    for name, value in pairs:
        if name in obj:
            raise ValueError("Duplicate intake JSON field: " + name)
        obj[name] = value
    return obj


def load_json(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_MANIFEST_BYTES:
        raise ValueError("Missing or oversized asset intake JSON")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys)


def safe_relative(root, raw):
    if (not isinstance(raw, str) or not raw or raw.startswith("/") or
            "\\" in raw or "\x00" in raw or len(raw) > 255):
        return None
    parts = raw.split("/")
    if any(part in ("", ".", "..") or ":" in part or any(ord(ch) < 32 for ch in part) for part in parts):
        return None
    target = root.joinpath(*parts)
    if not target.resolve().is_relative_to(root.resolve()):
        return None
    current = target
    while current != root:
        if current.is_symlink():
            return None
        current = current.parent
    return target


def reference(value):
    """A provenance/approval locator, not evidence of independent approval."""
    return isinstance(value, str) and 3 <= len(value.strip()) <= 400 and not any(ord(c) < 32 for c in value)


def artifact(root, spec, kind, base_dir, errors, asset_id):
    """Check exact supplied path, bytes, magic header and SHA256, never claim authenticity."""
    if not isinstance(spec, dict):
        errors.append("Missing " + kind + " artifact receipt: " + asset_id)
        return
    raw = spec.get("path")
    candidate = safe_relative(root, raw)
    prefix = base_dir.rstrip("/") + "/"
    if (candidate is None or not raw.startswith(prefix) or
            candidate.suffix.lower() not in ALLOWED_EXTENSIONS[kind] or
            not candidate.is_file()):
        errors.append("Unsafe/missing " + kind + " artifact: " + asset_id)
        return
    declared_size, declared_sha = spec.get("bytes"), spec.get("sha256")
    if type(declared_size) is not int or declared_size < 12 or not isinstance(declared_sha, str) or not HASH.fullmatch(declared_sha):
        errors.append("Malformed " + kind + " file checksum/size: " + asset_id)
        return
    if candidate.stat().st_size != declared_size:
        errors.append("Asset file size mismatch (" + kind + "): " + asset_id)
        return
    with candidate.open("rb") as stream:
        header = stream.read(16)
        stream.seek(0)
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != declared_sha:
        errors.append("Asset checksum mismatch (" + kind + "): " + asset_id)
    suffix = candidate.suffix.lower()
    magic_valid = (
        (suffix == ".blend" and header.startswith(b"BLENDER")) or
        (suffix == ".glb" and header.startswith(b"glTF")) or
        (suffix == ".png" and header.startswith(b"\x89PNG\r\n\x1a\n")) or
        (suffix in (".jpg", ".jpeg") and header.startswith(b"\xff\xd8")) or
        (suffix == ".pdf" and header.startswith(b"%PDF")) or
        (suffix == ".webp" and header.startswith(b"RIFF") and header[8:12] == b"WEBP") or
        (suffix == ".mp4" and header[4:8] == b"ftyp") or
        (suffix in (".log", ".txt") and b"\x00" not in header)
    )
    if not magic_valid:
        errors.append("Unrecognised " + kind + " artifact header: " + asset_id)


def check(root=ROOT, registry=None):
    root = Path(root).resolve()
    errors = []
    try:
        data = load_json(root / REGISTRY) if registry is None else registry
    except (OSError, ValueError, UnicodeError) as exc:
        return ["Cannot parse asset registry for intake: " + str(exc)]
    if not isinstance(data, dict) or data.get("project") != "AETHERFALL: REALMS COLLIDE":
        return ["Invalid asset registry for intake"]
    assets = data.get("assets")
    if not isinstance(assets, list):
        return ["Asset intake registry must contain a list"]
    registered = set()
    for entry in assets:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not ASSET_ID.fullmatch(entry["id"]):
            errors.append("Invalid asset intake ID")
            continue
        asset_id = entry["id"]
        registered.add(asset_id)
        stage = entry.get("status")
        if stage not in STAGES:
            errors.append("Unverified asset status promotion: " + asset_id)
            continue
        receipt_path = root / RECEIPTS / (asset_id + ".json")
        if stage == STAGES[0]:
            if receipt_path.exists() or receipt_path.is_symlink():
                errors.append("Reserved asset has premature handoff receipt: " + asset_id)
            # No promoted state is claimed. Do not inspect placeholders as native art.
            continue
        if not receipt_path.is_file() or receipt_path.is_symlink():
            errors.append("Missing handoff receipt for promoted asset: " + asset_id)
            continue
        try:
            receipt = load_json(receipt_path)
        except (OSError, ValueError, UnicodeError) as exc:
            errors.append("Invalid handoff receipt for " + asset_id + ": " + str(exc))
            continue
        if not isinstance(receipt, dict) or (receipt.get("schema_version"), receipt.get("asset_id"), receipt.get("status")) != (1, asset_id, stage):
            errors.append("Handoff identity/status mismatch: " + asset_id)
            continue
        provenance = receipt.get("provenance")
        if not isinstance(provenance, dict) or provenance.get("rights_basis") not in ("owner_original", "cleared_license"):
            errors.append("Missing provenance rights basis: " + asset_id)
        elif not all(reference(provenance.get(k)) for k in ("source_reference", "rights_review_reference", "rights_reviewed_by")):
            errors.append("Missing provenance review fields: " + asset_id)
        files = receipt.get("files")
        if not isinstance(files, dict):
            errors.append("Handoff asset files are not an object: " + asset_id)
            continue
        phase = STAGES.index(stage)
        for n, kind in enumerate(FILE_KINDS, 1):
            if n > phase:
                continue
            base_dir = entry.get({"concept": "concept_dir", "blender": "source_dir", "runtime": "runtime_dir"}[kind])
            if not isinstance(base_dir, str):
                errors.append("Missing asset base directory: " + asset_id)
                continue
            artifact(root, files.get(kind), kind, base_dir, errors, asset_id)
        if phase >= 2 and entry.get("concept_status") != "aetherfall_approved":
            errors.append("Asset Blender production lacks AETHERFALL canon approval: " + asset_id)
        if phase == 4:
            native = receipt.get("native_import")
            if not isinstance(native, dict):
                errors.append("Missing genuine native import record: " + asset_id)
            else:
                if (native.get("engine") != "Godot" or native.get("engine_version") != "4.7.2" or
                        not reference(native.get("reviewed_by")) or not reference(native.get("review_reference"))):
                    errors.append("Invalid native import review identity/version: " + asset_id)
                artifact(root, native.get("log"), "log", "evidence/godot", errors, asset_id)
                artifact(root, native.get("capture"), "capture", "evidence/godot", errors, asset_id)
    receipts_path = root / RECEIPTS
    if receipts_path.exists():
        for receipt in receipts_path.glob("*.json"):
            if receipt.stem not in registered:
                errors.append("Handoff receipt has no registered asset: " + receipt.name)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit real asset handoff files (source only, no invented approval).")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate", action="store_true")
    group.add_argument("--report", action="store_true")
    args = parser.parse_args(argv)
    failures = check()
    if failures:
        for issue in sorted(set(failures)):
            print("FAIL: " + issue, file=sys.stderr)
        return 1
    if args.report:
        data = load_json(ROOT / REGISTRY)
        for entry in data["assets"]:
            stage = entry["status"]
            next_stage = STAGES[STAGES.index(stage) + 1] if stage != STAGES[-1] else "external gameplay/release gates"
            print(entry["id"] + ": " + stage + " | NEXT: " + next_stage)
        print("All statuses describe recorded files only; no gameplay or model fidelity is claimed.")
    else:
        print("PASS: source checks for asset receipts, bytes, SHA256 and stage claims (NOT NATIVE ART PROOF)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
