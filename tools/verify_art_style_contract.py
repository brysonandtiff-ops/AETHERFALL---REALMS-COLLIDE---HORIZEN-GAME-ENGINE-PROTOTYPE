#!/usr/bin/env python3
"""AETHERFALL fail-closed art *submission* style gate.

This verifies reference identity, declared presentation structure, media size and
proposal-sidecar integrity. It cannot certify aesthetic similarity or native
engine evidence. Actual original-vs-candidate comparison requires owner review.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = "docs/art/ART_STYLE_LOCK.json"
CANON_PATH = "docs/characters/CANON_LOCKS.json"
LOCK_ID = "AF-ART-STYLE-20261126-V1"
PROJECT = "AETHERFALL: REALMS COLLIDE"
PANELS = [
    "brand_and_character_title_header",
    "large_hero_portrait_left",
    "four_view_turnaround_top_centre",
    "silhouette_explorations_top_right",
    "expressions_middle_centre",
    "palette_and_material_detail_middle_right",
    "hero_role_identity_lower_left",
    "unique_weapon_or_focus_lower_centre",
    "gameplay_role_lower_right",
    "ability_icons_and_descriptions_bottom",
    "concept_art_disclaimer_footer",
]
REFERENCE_PINS = {
    "vellaris_infographic": ("39403.png", "image/webp", 1536, 1152, 340668,
        "4d100d50cf0769da47cbe1b782deeb842d15a11c1c46a08f8bd5bd090fa34939",
        "PRIMARY_FULL_CHARACTER_INFOGRAPHIC_AND_EXISTING_VELLARIS_CANON"),
    "korvex_infographic": ("39412.png", "image/webp", 1536, 1152, 364990,
        "ff352a079685864ced7bbc255a81f73060847156ac24f74edbc2883dd348621b",
        "PRIMARY_FULL_CHARACTER_INFOGRAPHIC_LAYOUT_AND_MATERIAL_QUALITY_REFERENCE_ONLY"),
    "legacy_roster_capture": ("39401.jpg", "image/webp", 1384, 1536, 289520,
        "7df96bfb7a968f0b51d1423b75e99f76f06f2f04c6b8df32f512dadc91ca2aab",
        "ROSTER_COMPOSITION_AND_ROLE_CODING_REFERENCE_ONLY_NOT_BRANDING_OR_ROSTER_APPROVAL"),
}
ALLOWED_MODES = {
    "FULL_CHARACTER_INFOGRAPHIC",
    "BLACK_BACKGROUND_HERO_KEY_ART",
    "3D_BLOCKOUT_EVIDENCE",
}
IMAGE_EXTS = {".webp", ".png", ".jpg", ".jpeg"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return None


def _real_image_dimensions(path):
    """Read basic dimensions with stdlib; NOT a pixel-level style validator."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24 and data[12:16] == b"IHDR":
        return struct.unpack(">II", data[16:24])
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP" and len(data) >= 30:
        tag = data[12:16]
        if tag == b"VP8X":
            return (int.from_bytes(data[24:27], "little") + 1,
                    int.from_bytes(data[27:30], "little") + 1)
        if tag == b"VP8L" and data[20:21] == b"\x2f" and len(data) >= 25:
            fields = int.from_bytes(data[21:25], "little")
            return ((fields & 0x3fff) + 1, ((fields >> 14) & 0x3fff) + 1)
        if tag == b"VP8 " and len(data) >= 30 and data[23:26] == b"\x9d\x01\x2a":
            w, h = struct.unpack("<HH", data[26:30])
            return (w & 0x3fff, h & 0x3fff)
    if data.startswith(b"\xff\xd8"):
        at = 2
        while at < len(data) - 9:
            if data[at] != 0xff:
                return None
            marker = data[at + 1]
            if marker in (0xd8, 0xd9):
                at += 2
                continue
            if marker == 0xda:
                return None
            if at + 4 > len(data):
                return None
            size = int.from_bytes(data[at + 2:at + 4], "big")
            if size < 2 or at + 2 + size > len(data):
                return None
            if marker in (0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf):
                return (int.from_bytes(data[at + 7:at + 9], "big"),
                        int.from_bytes(data[at + 5:at + 7], "big"))
            at += 2 + size
    return None


def _check_proposal(root, path, style, errors):
    rel = path.relative_to(root).as_posix()
    character_id = path.relative_to(root / "art/concepts/characters").parts[0]
    sidecar = path.with_name(path.name + ".review.json")
    review = _json(sidecar)
    if not isinstance(review, dict):
        errors.append("Art proposal lacks .review.json with style lock fields: " + rel)
        return
    if review.get("character_id") != character_id:
        errors.append("Art proposal has wrong character ID: " + rel)
    if review.get("style_lock_id") != LOCK_ID:
        errors.append("Art proposal lacks pinned style lock ID: " + rel)
    expected = {key: REFERENCE_PINS[key][5] for key in ("vellaris_infographic", "korvex_infographic")}
    if review.get("style_reference_sha256") != expected:
        errors.append("Art proposal references wrong infographic originals: " + rel)
    if review.get("branding") != PROJECT:
        errors.append("Art proposal has wrong AETHERFALL brand: " + rel)
    if review.get("status") not in ("PROPOSAL_PENDING_OWNER_REVIEW", "REJECTED_DRIFT"):
        errors.append("Art proposal attempts unapproved canon promotion: " + rel)
    if review.get("review_state") not in ("PENDING_OWNER_VISUAL_COMPARISON", "REJECTED_DRIFT"):
        errors.append("Art proposal bypasses owner visual review: " + rel)
    for key in ("approval", "is_canonical", "owner_approved", "visual_similarity_passed", "native_engine_verified"):
        if key in review:
            errors.append("Art proposal self-certified or self-promoted: " + rel + "/" + key)
    if review.get("candidate_sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
        errors.append("Art proposal image checksum mismatch: " + rel)
    if not isinstance(review.get("reference_attestation"), str) or not review["reference_attestation"].strip():
        errors.append("Art proposal lacks reference briefing record: " + rel)
    if review.get("render_origin") not in (
        "AI_GENERATED_CONCEPT_ONLY", "HUMAN_DRAWN_CONCEPT", "VTK_MESH_RENDER", "BLENDER_NATIVE_CAPTURE", "GODOT_NATIVE_CAPTURE"
    ):
        errors.append("Art proposal render origin missing or invalid: " + rel)
    if review.get("render_origin") in ("BLENDER_NATIVE_CAPTURE", "GODOT_NATIVE_CAPTURE"):
        errors.append("Native engine proof cannot be declared by art proposal metadata alone: " + rel)
    dims = _real_image_dimensions(path)
    if dims is None or min(dims) <= 0:
        errors.append("Art proposal cannot verify image dimensions/format: " + rel)
        return
    mode = review.get("presentation_mode")
    if mode not in ALLOWED_MODES:
        errors.append("Art proposal has unknown presentation mode: " + rel)
    elif mode == "FULL_CHARACTER_INFOGRAPHIC":
        if dims[0] * 3 != dims[1] * 4 or dims[0] < 1536 or dims[1] < 1152:
            errors.append("Full infographic is not 4:3 at 1536x1152+ minimum: " + rel)
        if review.get("panel_attestation") != PANELS:
            errors.append("Full infographic lacks canonical 11-panel attestation: " + rel)
    elif mode == "BLACK_BACKGROUND_HERO_KEY_ART":
        if review.get("not_a_full_sheet") is not True:
            errors.append("Portrait was not separated from full concept sheet: " + rel)
        if review.get("panel_attestation") not in (None, []):
            errors.append("Key art falsely claims full infographic panels: " + rel)
    else:
        if review.get("render_origin") not in ("VTK_MESH_RENDER", "AI_GENERATED_CONCEPT_ONLY", "HUMAN_DRAWN_CONCEPT"):
            errors.append("3D blockout render origin requires separate native evidence: " + rel)


def check(root=ROOT):
    root = Path(root).resolve()
    errors = []
    path = root / LOCK_PATH
    style = _json(path)
    if not isinstance(style, dict):
        return ["Missing or malformed AETHERFALL art style master lock"]
    if any((style.get("schema_version") != 1,
            style.get("project") != PROJECT,
            style.get("lock_id") != LOCK_ID,
            style.get("policy") != "OWNER_REFERENCES_FIRST_FAIL_CLOSED")):
        errors.append("Art style lock identity/policy changed")
    brand = style.get("brand")
    if not isinstance(brand, dict) or (
        brand.get("project_name") != PROJECT or brand.get("logo_text") != "AETHERFALL"
        or brand.get("subtitle") != "REALMS COLLIDE"
        or brand.get("forbidden_new_branding") != ["NEXUSFALL", "SHADOWSPIRE"]
    ):
        errors.append("Wrong project branding or missing legacy title exclusion")
    refs = style.get("references")
    if not isinstance(refs, dict) or set(refs) != set(REFERENCE_PINS):
        errors.append("Master style reference set changed")
        refs = refs if isinstance(refs, dict) else {}
    for key, pinned in REFERENCE_PINS.items():
        info = refs.get(key)
        if not isinstance(info, dict):
            errors.append("Missing style reference: " + key)
            continue
        expected = dict(zip(("uploaded_filename", "actual_media_type", "width", "height", "bytes", "sha256", "use"), pinned))
        if any(info.get(k) != v for k, v in expected.items()):
            errors.append("Style reference identity/hash drift: " + key)
        if info.get("binary_in_git") is not False:
            errors.append("Unverified repository binary-archive claim: " + key)
    infographic = style.get("full_infographic")
    if not isinstance(infographic, dict) or (
        infographic.get("aspect_ratio") != "4:3"
        or infographic.get("minimum_width") != 1536
        or infographic.get("minimum_height") != 1152
        or infographic.get("panel_order") != PANELS
        or "NOT FINAL IN-GAME MODEL" not in str(infographic.get("banner_disclaimer", ""))
        or "magenta" not in str(infographic.get("visual_treatment", "")).lower()
    ):
        errors.append("Full character infographic hierarchy or presentation drift")
    key_art = style.get("hero_key_art")
    if not isinstance(key_art, dict) or key_art.get("background") != "pure_or_near_black" or key_art.get("cannot_replace_full_sheet") is not True:
        errors.append("Poster substituted for full sheet / black-background rule removed")
    enforcement = style.get("enforcement")
    must_be_true = (
        "image_candidates_are_proposals_until_owner_review",
        "require_exact_reference_hashes_in_review_sidecar",
        "require_declared_presentation_mode",
        "require_full_panel_attestation_for_full_sheets",
        "no_generated_art_is_engine_proof", "no_silent_canon_promotion",
    )
    if not isinstance(enforcement, dict) or any(enforcement.get(x) is not True for x in must_be_true):
        errors.append("Artwork review or truthfulness gate disabled")
    canon = _json(root / CANON_PATH)
    if not isinstance(canon, dict):
        errors.append("Existing character visual canon locks missing")
    else:
        present = canon.get("presentation_standard") or {}
        if (present.get("required_panel_order") != PANELS
                or present.get("master_ratio") != "4:3"
                or present.get("reference_size") != [1536, 1152]):
            errors.append("Existing character canon contradicts art style master")
        vellaris = ((canon.get("locked_characters") or {}).get("CHR_Vellaris_Bloodshield") or {}).get("source") or {}
        if vellaris.get("sha256") != REFERENCE_PINS["vellaris_infographic"][5]:
            errors.append("Existing Vellaris master source hash contradicts style lock")
    art_root = root / "art/concepts/characters"
    if art_root.is_dir():
        for character_dir in sorted(art_root.glob("CHR_*")):
            if not character_dir.is_dir() or character_dir.is_symlink():
                continue
            for img in sorted(character_dir.rglob("*")):
                if not img.is_file() or img.suffix.lower() not in IMAGE_EXTS:
                    continue
                rel = img.relative_to(root).as_posix()
                if img.is_symlink():
                    errors.append("Unsafe art symlink: " + rel)
                    continue
                if "proposals" in img.relative_to(character_dir).parts[:-1]:
                    _check_proposal(root, img, style, errors)
                else:
                    # Existing owner-approved source handling belongs to the
                    # pinned CANON_LOCKS validator. Everything else must be a
                    # proposal; no silent new candidate master at the root.
                    locks = (canon or {}).get("locked_characters") or {}
                    allowed = {entry.get("source", {}).get("path") for entry in locks.values()
                               if isinstance(entry, dict) and isinstance(entry.get("source"), dict)}
                    if rel not in allowed:
                        errors.append("Unreviewed hero image outside proposals: " + rel)
    return errors


if __name__ == "__main__":
    failures = check()
    if failures:
        for failure in failures:
            print("FAIL: " + failure, file=sys.stderr)
        sys.exit(1)
    print("PASS: style lock/reference identity/CI submission metadata (STATIC ONLY; human visual approval required)")