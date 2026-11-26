#!/usr/bin/env python3
"""AETHERFALL owner-canon source and metadata lock. NOT image similarity or native proof.

Fail closed if exact approved references, metadata or hero identities drift. A
generated alternative never gets canonical approval through a sidecar alone.
"""
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

PROJECT = "AETHERFALL: REALMS COLLIDE"
HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
LOCK_FILE = "docs/characters/CANON_LOCKS.json"
STYLE_FILE = "docs/art/AETHERFALL_STYLE_CANON.json"
STYLE_DOC = "docs/art/AETHERFALL_STYLE_CANON.md"
STYLE_ID = "AF-STYLE-39403-V1"
STYLE_SHA = "4d100d50cf0769da47cbe1b782deeb842d15a11c1c46a08f8bd5bd090fa34939"
STYLE_BRAND = "AETHERFALL – REALMS COLIDE"
STYLE_BANNED_BRANDS = ["MIDNIGHT", "SHADOWSPIRE", "NEXUSFALL"]

# Intentionally anchored twice (here AND in the committed JSON): a casual JSON
# edit cannot promote a new canonical character source without code-owner review.
PINNED = {
    "CHR_Vellaris_Bloodshield": {
        "path": "art/concepts/characters/CHR_Vellaris_Bloodshield/Vellaris_Bloodshield_concept_v1.webp",
        "sha256": "4d100d50cf0769da47cbe1b782deeb842d15a11c1c46a08f8bd5bd090fa34939",
        "format": "WEBP", "width": 1536, "height": 1152, "bytes": 340668,
        "name": "Vellaris", "title": "The Bloodshield", "role": "tank",
        "focus": "bloodshield",
        "actives": ["Blood Barrier", "Crimson Riposte", "Sanguine Pact", "Hemorrhage Veil"],
        "passive": "Royal Ichor",
        "traits": ("vampiric", "hair", "red eyes", "pauldrons", "cape", "gold", "bloodshield"),
    },
    "CHR_ThornDell": {
        "path": "art/concepts/characters/CHR_ThornDell/ThornDell_Venomroot_APPROVED_v1.png",
        "sha256": "34056a337ebfa67f413375a757f837a247938a3897aabf5e06b0683b48ba89d5",
        "format": "PNG", "width": 1536, "height": 1024, "bytes": 3219162,
        "name": "ThornDell", "title": "The Venomroot", "role": "tank",
        "focus": "Root Bulwark",
        "actives": [], "passive": None,
        "traits": ("antlers", "bark", "basalt", "venom", "root bulwark", "fungi"),
    },
}
EXTRA_KNOWN = {
    "art/concepts/characters/CHR_ThornDell/ThornDell_Venomroot_chat_copy.webp": {
        "format": "WEBP", "width": 1536, "height": 1024, "bytes": 375978,
        "sha256": "3ca49cb4b1aa4f13ae79e38250eff5fc7dce6a0f22afea1f3b57984495badfaf",
    },
}
LAYOUT = [
    "brand_and_character_title_header", "large_hero_portrait_left",
    "four_view_turnaround_top_centre", "silhouette_explorations_top_right",
    "expressions_middle_centre", "palette_and_material_detail_middle_right",
    "hero_role_identity_lower_left", "unique_weapon_or_focus_lower_centre",
    "gameplay_role_lower_right", "ability_icons_and_descriptions_bottom",
    "concept_art_disclaimer_footer",
]
IMAGE_EXTS = {".webp", ".png", ".jpg", ".jpeg", ".gif"}
DIGEST = re.compile(r"^[a-f0-9]{64}$")


def _safe(root, path):
    if not isinstance(path, str) or not path or "\\" in path or "\x00" in path:
        return None
    if path.startswith("/") or any(x in ("", ".", "..") or ":" in x for x in path.split("/")):
        return None
    candidate = root.joinpath(*path.split("/"))
    if not candidate.resolve().is_relative_to(root.resolve()):
        return None
    return candidate


def _json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return None


def _image_format_dimensions(data):
    """Probe real PNG/WebP headers without optional modules or re-encoding."""
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        w, h = struct.unpack(">II", data[16:24])
        return "PNG", w, h
    if len(data) > 30 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        if int.from_bytes(data[4:8], "little") + 8 != len(data):
            return "BAD_WEBP_LENGTH", None, None
        chunk = data[12:16]
        if chunk == b"VP8X":
            return ("WEBP", 1 + int.from_bytes(data[24:27], "little"),
                    1 + int.from_bytes(data[27:30], "little"))
        if chunk == b"VP8 ":
            idx = data.find(b"\x9d\x01\x2a", 20, 64)
            if idx >= 0 and len(data) >= idx + 7:
                return ("WEBP", int.from_bytes(data[idx+3:idx+5], "little") & 0x3fff,
                        int.from_bytes(data[idx+5:idx+7], "little") & 0x3fff)
        if chunk == b"VP8L" and len(data) >= 25 and data[20] == 0x2f:
            bits = int.from_bytes(data[21:25], "little")
            return "WEBP", (bits & 0x3fff) + 1, ((bits >> 14) & 0x3fff) + 1
    return "UNKNOWN", None, None


def _check_bytes(path, expected, errors, label):
    if not path.is_file() or path.is_symlink():
        errors.append("Missing/unsafe approved image: " + label)
        return
    try:
        data = path.read_bytes()
    except OSError:
        errors.append("Unreadable approved image: " + label)
        return
    expected_ext = {"PNG": ".png", "WEBP": ".webp"}.get(expected.get("format"))
    if path.suffix.lower() != expected_ext:
        errors.append("Approved image MIME/extension mismatch: " + label)
    fmt, w, h = _image_format_dimensions(data)
    if (fmt != expected.get("format") or w != expected.get("width")
            or h != expected.get("height") or len(data) != expected.get("bytes")):
        errors.append("Approved image signature/size drift: " + label)
    if hashlib.sha256(data).hexdigest() != expected.get("sha256"):
        errors.append("Approved image checksum drift: " + label)


def _validate_proposal(root, img, character, source_sha, errors):
    sidecar = img.with_name(img.name + ".review.json")
    rel = img.relative_to(root).as_posix()
    doc = _json(sidecar)
    if not isinstance(doc, dict):
        errors.append("Untracked character art proposal: " + rel)
        return
    expected_id = character
    if (doc.get("character_id") != expected_id
            or doc.get("status") not in ("PROPOSAL_PENDING_OWNER_REVIEW", "REJECTED_DRIFT")
            or doc.get("canonical_source_sha256") != source_sha
            or doc.get("candidate_sha256") != hashlib.sha256(img.read_bytes()).hexdigest()
            or not isinstance(doc.get("source_note"), str)
            or not doc["source_note"].strip()):
        errors.append("Unsafe/mislabelled character art proposal: " + rel)
    if (doc.get("style_lock_id") != STYLE_ID
            or doc.get("style_reference_sha256") != STYLE_SHA
            or doc.get("display_brand") != STYLE_BRAND):
        errors.append("Proposal missing AETHERFALL canonical art style anchor: " + rel)
    if "approval" in doc or "is_canonical" in doc or "owner_approved" in doc:
        errors.append("Proposal cannot self-promote to canonical art: " + rel)


def check(root=ROOT):
    root = Path(root).resolve()
    errors = []
    lock_path = root / LOCK_FILE
    manifest = _json(lock_path)
    if not isinstance(manifest, dict):
        return ["Missing/invalid visual canon locks JSON"]
    if (manifest.get("schema_version") != 1 or manifest.get("project") != PROJECT
            or manifest.get("lock_id") != "AF-VISUAL-CANON-V1"
            or manifest.get("policy") != "OWNER_REFERENCE_FIRST_FAIL_CLOSED"):
        errors.append("Visual canon manifest identity/policy drift")
    present = manifest.get("presentation_standard")
    if not isinstance(present, dict) or present.get("required_panel_order") != LAYOUT:
        errors.append("Vellaris infographic panel hierarchy drift")
        present = {}
    if (present.get("reference_character") != "CHR_Vellaris_Bloodshield"
            or present.get("master_ratio") != "4:3"
            or present.get("reference_size") != [1536, 1152]
            or not isinstance(present.get("frame_style"), str)
            or "magenta" not in present.get("frame_style", "").lower()
            or "purple" not in present.get("frame_style", "").lower()):
        errors.append("Character infographic presentation identity drift")
    # Third owner image is the global presentation reference. This proves
    # identifier/metadata consistency, NOT actual visual resemblance.
    style = _json(root / STYLE_FILE)
    if not isinstance(style, dict):
        errors.append("Missing canonical AETHERFALL style lock")
        style = {}
    if (style.get("schema_version") != 1
            or style.get("style_lock_id") != STYLE_ID
            or style.get("state") != "OWNER_LOCKED_PRESENTATION_STYLE"
            or style.get("owner_display_title") != STYLE_BRAND
            or style.get("internal_project_id") != PROJECT
            or style.get("excluded_external_branding") != STYLE_BANNED_BRANDS
            or style.get("candidate_review_status") != "PROPOSAL_PENDING_OWNER_REVIEW"):
        errors.append("AETHERFALL canonical style lock/branding drift")
    source = style.get("source_reference")
    source = source if isinstance(source, dict) else {}
    for key, expected in (
            ("sha256", STYLE_SHA),
            ("source_upload_name", "39403.png"),
            ("actual_format", "WEBP"),
            ("width", 1536), ("height", 1152), ("bytes", 340668),
            ("repository_target", PINNED["CHR_Vellaris_Bloodshield"]["path"]),
            ("archive_state", "pending_binary_checkin"),
    ):
        if source.get(key) != expected:
            errors.append("Third-image style reference changed: " + key)
    if (style.get("sheet_panel_order") != LAYOUT
            or not isinstance(style.get("frame_style"), dict)
            or style["frame_style"].get("master_ratio") != "4:3"
            or "gothic" not in style["frame_style"].get("tone", "").lower()):
        errors.append("AETHERFALL third-image art style hierarchy drift")
    master_doc_path = _safe(root, STYLE_DOC)
    try:
        master_doc = master_doc_path.read_text(encoding="utf-8") if master_doc_path else ""
    except OSError:
        master_doc = ""
    if STYLE_SHA not in master_doc or STYLE_BRAND not in master_doc or STYLE_ID not in master_doc:
        errors.append("AETHERFALL canonical art style instructions missing or drifted")
    if (present.get("style_lock_id") != STYLE_ID
            or present.get("style_reference_sha256") != STYLE_SHA
            or present.get("style_manifest_path") != STYLE_FILE
            or present.get("display_brand") != STYLE_BRAND):
        errors.append("Character presentation not bound to owner's third image")

    locks = manifest.get("locked_characters")
    if not isinstance(locks, dict) or not set(PINNED).issubset(set(locks)):
        errors.append("Pinned owner-approved character canon lock missing")
        locks = {}
    allowlisted = set(EXTRA_KNOWN)
    for identifier, pinned in PINNED.items():
        lock = locks.get(identifier)
        if not isinstance(lock, dict):
            errors.append("Missing approved character canon lock: " + identifier)
            continue
        source = lock.get("source")
        if not isinstance(source, dict):
            source = {}
        for key in ("path", "sha256", "format", "width", "height", "bytes"):
            if source.get(key) != pinned[key]:
                errors.append("Approved reference identity/hash drift: " + identifier + "/" + key)
        if lock.get("approval") != "owner_approved_aetherfall_concept" or lock.get("evidence_class") != "CONCEPT_ONLY":
            errors.append("Unverified character visual status promotion: " + identifier)
        ident = lock.get("identity")
        if not isinstance(ident, dict):
            ident = {}
        if (ident.get("display_name") != pinned["name"] or ident.get("epithet") != pinned["title"]
                or ident.get("role_class") != pinned["role"]
                or pinned["focus"].casefold() not in str(ident.get("signature_focus", "")).casefold()
                or ident.get("active_ability_names") != pinned["actives"]
                or ident.get("passive_ability_name") != pinned["passive"]):
            errors.append("Approved character role/weapon/kit lock drift: " + identifier)
        traits = lock.get("visual_lock", [])
        if not isinstance(traits, list) or not all(isinstance(x, str) for x in traits):
            errors.append("Approved character visual trait list invalid: " + identifier)
            traits = []
        merged = " ".join(traits).casefold()
        for token in pinned["traits"]:
            if token not in merged:
                errors.append("Approved character missing visual anchor: " + identifier + "/" + token)
        if not isinstance(lock.get("forbidden_drift"), list) or len(lock["forbidden_drift"]) < 3:
            errors.append("Approved character drift restrictions removed: " + identifier)
        path = _safe(root, pinned["path"])
        if path is None:
            errors.append("Unsafe locked source path: " + identifier)
            continue
        plan = _json(root / "docs/characters/plans" / (identifier + ".json"))
        if not isinstance(plan, dict):
            errors.append("Missing plan for locked character: " + identifier)
            continue
        if (plan.get("presentation_style_lock_id") != STYLE_ID
                or plan.get("presentation_style_source_sha256") != STYLE_SHA):
            errors.append("Approved character plan missing third-image art style: " + identifier)
        cref = plan.get("concept_reference", {})
        if not isinstance(cref, dict) or (cref.get("repo_path") != pinned["path"]
                or cref.get("sha256") != pinned["sha256"]):
            errors.append("Locked source no longer matches character plan: " + identifier)
            cref = {}
        pi = plan.get("identity") or {}
        design = plan.get("design") or {}
        if (plan.get("display_name") != pinned["name"] or plan.get("epithet") != pinned["title"]
                or pi.get("role_class") != pinned["role"]
                or pinned["focus"].casefold() not in str(design.get("signature_prop", "")).casefold()):
            errors.append("Approved character design/prop changed in plan: " + identifier)
        if pinned["actives"] and [a.get("name") for a in design.get("active_abilities", []) if isinstance(a, dict)] != pinned["actives"]:
            errors.append("Approved character active kit drift: " + identifier)
        if pinned["passive"] is not None and (not isinstance(design.get("passive"), dict)
                                              or design["passive"].get("name") != pinned["passive"]):
            errors.append("Approved character passive drift: " + identifier)
        state = source.get("state")
        archived = path.is_file() and not path.is_symlink()
        if state not in ("pending_binary_checkin", "source_verified"):
            errors.append("Unknown approved art source state: " + identifier)
        if archived:
            _check_bytes(path, pinned, errors, identifier)
            if state != "source_verified" or cref.get("archive_status") != "source_verified" or not plan.get("gates", {}).get("source_archived"):
                errors.append("Character source exists but archival review incomplete: " + identifier)
        else:
            if state != "pending_binary_checkin" or cref.get("archive_status") != "pending_source_upload" or plan.get("gates", {}).get("source_archived"):
                errors.append("Character source promoted without original image bytes: " + identifier)
        allowlisted.add(pinned["path"])
    alternates = manifest.get("alternate_references")
    if not isinstance(alternates, dict) or set(alternates) != set(EXTRA_KNOWN):
        errors.append("Approved alternate art allowlist changed")
        alternates = {}
    for relative, expected in EXTRA_KNOWN.items():
        data = alternates.get(relative, {})
        if not isinstance(data, dict) or any(data.get(k) != v for k, v in expected.items()) or data.get("owner_lock") is not False:
            errors.append("Alternate reference changed or promoted: " + relative)
        path = _safe(root, relative)
        if path is not None and path.exists():
            _check_bytes(path, expected, errors, relative)
    collision = manifest.get("collision_hold")
    if not isinstance(collision, dict) or collision.get("new_id") != "CHR_Corvex" or collision.get("existing_id") != "CHR_Korvex" or collision.get("state") != "requires_explicit_owner_identity_resolution":
        errors.append("Corvex/Korvex collision protection changed")
    registry = _json(root / "art/asset_registry.json")
    if isinstance(registry, dict) and isinstance(registry.get("assets"), list):
        ids = {entry.get("id") for entry in registry["assets"] if isinstance(entry, dict)}
        if "CHR_Corvex" in ids and "CHR_Korvex" in ids:
            errors.append("Unresolved Corvex/Korvex alias collision")

        # Every newly approved hero MUST also have a source-backed canon lock.
        # Legacy concepts and provisional designs cannot get an approved lock
        # merely by adding a JSON record. Human owner review is separate.
        approved = {
            entry["id"]: entry for entry in registry["assets"]
            if isinstance(entry, dict) and entry.get("type") == "character"
            and entry.get("concept_status") == "aetherfall_approved"
            and isinstance(entry.get("id"), str)
        }
        for identifier in sorted(set(approved) - set(locks)):
            errors.append("Approved character missing visual lock: " + identifier)
        for identifier in sorted(set(locks) - set(PINNED)):
            if identifier not in approved:
                errors.append("Unregistered/unapproved extra visual lock: " + identifier)
                continue
            entry = approved[identifier]
            extra = locks[identifier]
            if not isinstance(extra, dict):
                errors.append("Malformed approved character extra visual lock: " + identifier)
                continue
            media = extra.get("source")
            ident = extra.get("identity")
            plan = _json(root / "docs/characters/plans" / (identifier + ".json"))
            if not isinstance(media, dict) or not isinstance(ident, dict) or not isinstance(plan, dict):
                errors.append("Approved character extra lock missing source/plan: " + identifier)
                continue
            prefix = entry.get("concept_dir", "") + "/"
            raw = media.get("path")
            img = _safe(root, raw)
            expected_ext = {"PNG": ".png", "WEBP": ".webp"}.get(media.get("format"))
            if (img is None or not isinstance(raw, str) or not raw.startswith(prefix)
                    or img.parent != root / entry.get("concept_dir", "")
                    or img.suffix.lower() != expected_ext
                    or not isinstance(media.get("width"), int) or media["width"] < 1
                    or not isinstance(media.get("height"), int) or media["height"] < 1
                    or not isinstance(media.get("bytes"), int) or media["bytes"] < 1
                    or not isinstance(media.get("sha256"), str)
                    or not DIGEST.fullmatch(media["sha256"])):
                errors.append("Approved character extra lock malformed master source: " + identifier)
                continue
            allowlisted.add(raw)
            if (extra.get("approval") != "owner_approved_aetherfall_concept"
                    or extra.get("evidence_class") != "CONCEPT_ONLY"
                    or ident.get("display_name") != plan.get("display_name")
                    or ident.get("epithet") != plan.get("epithet")
                    or ident.get("role_class") != (plan.get("identity") or {}).get("role_class")
                    or ident.get("signature_focus") != (plan.get("design") or {}).get("signature_prop")
                    or ident.get("active_ability_names") != [
                        a.get("name") for a in (plan.get("design") or {}).get("active_abilities", [])
                        if isinstance(a, dict)
                    ]
                    or ident.get("passive_ability_name") != (
                        (plan.get("design") or {}).get("passive") or {}
                    ).get("name")
                    or not isinstance(extra.get("visual_lock"), list)
                    or len(extra["visual_lock"]) < 6
                    or not isinstance(extra.get("forbidden_drift"), list)
                    or len(extra["forbidden_drift"]) < 3):
                errors.append("Approved character extra lock identity/review incomplete: " + identifier)
            if (plan.get("presentation_style_lock_id") != STYLE_ID
                    or plan.get("presentation_style_source_sha256") != STYLE_SHA):
                errors.append("New approved character plan missing third-image art style: " + identifier)
            cref = plan.get("concept_reference") or {}
            if cref.get("repo_path") != raw or cref.get("sha256") != media["sha256"]:
                errors.append("Approved character extra lock not linked to plan: " + identifier)
            archived = img.is_file() and not img.is_symlink()
            if archived:
                _check_bytes(img, media, errors, identifier)
                if (media.get("state") != "source_verified"
                        or cref.get("archive_status") != "source_verified"
                        or not (plan.get("gates") or {}).get("source_archived")):
                    errors.append("New approved character source arrived without verification: " + identifier)
            else:
                if (media.get("state") != "pending_binary_checkin"
                        or cref.get("archive_status") != "pending_source_upload"
                        or (plan.get("gates") or {}).get("source_archived")):
                    errors.append("New approved character falsely promoted without image: " + identifier)
    base = root / "art/concepts/characters"
    if base.is_dir():
        for character_folder in base.iterdir():
            if not character_folder.is_dir() or character_folder.name not in locks:
                continue
            for img in character_folder.rglob("*"):
                if not img.is_file() or img.suffix.lower() not in IMAGE_EXTS:
                    continue
                rel = img.relative_to(root).as_posix()
                if rel in allowlisted:
                    continue
                subpath = img.relative_to(character_folder)
                if subpath.parts[0] == "proposals" and len(subpath.parts) >= 2:
                    _validate_proposal(root, img, character_folder.name, locks[character_folder.name]["source"]["sha256"], errors)
                else:
                    errors.append("Unregistered art in approved character master folder: " + rel)
    return errors


if __name__ == "__main__":
    failures = check()
    if failures:
        for failure in failures:
            print("FAIL: " + failure, file=sys.stderr)
        sys.exit(1)
    print("PASS: pinned canonical source integrity and hero locks (STATIC ONLY; no visual likeness proof)")
