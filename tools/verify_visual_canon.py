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
    "CHR_Dreadhull": {
        "path": "art/concepts/characters/CHR_Dreadhull/Dreadhull_Bonebrine_Reaver_CANONICAL_v1.webp",
        "sha256": "6d172d578f0d01e5ea126f755ae7c309a4e5d176b801bf11af7de3990a43273c",
        "format": "WEBP", "width": 1536, "height": 1152, "bytes": 538780,
        "name": "Dreadhull", "title": "Bonebrine Reaver — The Cursed Salvager", "role": "tank",
        "focus": "Ossuary Dredge",
        "actives": ["Dredge Snare","Salvage Recall","Reforge Bulwark","Wreckline Drag","Graveyard Forge"],
        "passive": "Sunken Claim",
        "traits": ("hooded", "bone-brine", "cyan", "crimson", "ossuary dredge", "salvage bulwark", "wreck frame"),
    },
    "CHR_KRAIT": {
        "path": "art/concepts/characters/CHR_KRAIT/KRAIT_The_Sovereign_Guardian_CANONICAL_v1.webp",
        "sha256": "129597d1fc89bbbe35a306295ad8239d6ffc05eb39dcb52264355717329fe944",
        "format": "WEBP", "width": 1536, "height": 1384, "bytes": 191796,
        "name": "K.R.A.I.T", "title": "The Sovereign Guardian", "role": "tank",
        "focus": "Rift Knuckles", "actives": [], "passive": None,
        "traits": ("horn", "cyan", "dragon-shaped", "gauntlets", "reactor", "ascension"),
    },
    "CHR_Korvex": {
        "path": "art/concepts/characters/CHR_Korvex/Korvex_The_Hollow_Titan_CANONICAL_v1.png",
        "sha256": "697796f1da2a4561c19671ee20e44f38e830634e61f803a71206204f5d615ec6",
        "format": "PNG", "width": 1448, "height": 1086, "bytes": 3166920,
        "name": "Korvex", "title": "The Hollow Titan", "role": "tank",
        "focus": "Grave Maul", "actives": ["Grave Maul","Bone Bastion","Decay Field","Titan's Roar"],
        "passive": "Hollow Endurance",
        "traits": ("mausoleum", "horned", "purple", "chains", "lanterns", "grave maul", "funeral cloth"),
    },
}
# Independently pinned owner-selected design contract. Progress gates are not locked here.
DREADHULL_DESIGN_CONTRACT = {
    "identity": {
        "display_name": "Dreadhull",
        "epithet": "Bonebrine Reaver — The Cursed Salvager",
        "role_class": "tank",
        "signature_focus": "Ossuary Dredge",
        "active_ability_names": [
            "Dredge Snare",
            "Salvage Recall",
            "Reforge Bulwark",
            "Wreckline Drag",
            "Graveyard Forge"
        ],
        "passive_ability_name": "Sunken Claim"
    },
    "visual_lock": [
        "Broad asymmetrical heavy bipedal tank; hooded undead face with dark recess, narrow cyan glow and exposed cyan-lit skeletal ribs; no tentacle beard.",
        "Bone-brine plates with ivory curved whale-bone ribs, dark blue-black metal, rusted antique-gold ironwork, chains and bound salvage ropes.",
        "Tattered crimson-magenta sails and cloth drape over shoulder and waist; cyan brine lantern and magical energy glow.",
        "Ossuary Dredge: large arm-carried cylindrical salvage winch, circular ribbed bone-claw aperture and glowing cyan brine chamber; preserve exact weapon shape, not an anchor-scythe.",
        "Opposite arm retains the original strapped jagged timber-and-bone salvage bulwark shown in hero art and turnarounds.",
        "Original wreck frame mounted behind shoulders: open shipwreck timber rigging, rope webbing, mast fragments and hanging lantern; do NOT substitute a full galleon.",
        "Preserve the owner-approved dark navy/cyan/gold 4:3 board, its exact hood, armor, proportions, five turnaround views, material studies, weapon breakdown and six ability panels."
    ],
    "forbidden_drift": [
        "Do not change the hooded face to an octopus or tentacle-bearded pirate, substitute a generic knight or alter body proportions.",
        "No weapon replacement, including anchor-scythe, anchor-harpoon, cutlass or ship bell; no generic shield substitution.",
        "No full pirate galleon back attachment, new costume, recolor, altered original artwork, or earlier #07/other variant as master without explicit owner approval of a separately versioned change.",
        "Do not replace the six named kit abilities/passive or change tank role; the earlier Kraken ideas are not part of this approved source.",
        "Never present concept art as a verified 3D model, animation, gameplay or engine render."
    ],
    "visual_identity": "Broad asymmetrical heavy bipedal tank; hooded undead face with dark recess, narrow cyan glow and exposed cyan-lit skeletal ribs; no tentacle beard. Bone-brine plates with ivory curved whale-bone ribs, dark blue-black metal, rusted antique-gold ironwork, chains and bound salvage ropes. Tattered crimson-magenta sails and cloth drape over shoulder and waist; cyan brine lantern and magical energy glow. Ossuary Dredge: large arm-carried cylindrical salvage winch, circular ribbed bone-claw aperture and glowing cyan brine chamber; preserve exact weapon shape, not an anchor-scythe. Opposite arm retains the original strapped jagged timber-and-bone salvage bulwark shown in hero art and turnarounds. Original wreck frame mounted behind shoulders: open shipwreck timber rigging, rope webbing, mast fragments and hanging lantern; do NOT substitute a full galleon. Preserve the owner-approved dark navy/cyan/gold 4:3 board, its exact hood, armor, proportions, five turnaround views, material studies, weapon breakdown and six ability panels.",
    "palette": [
        "bone ivory",
        "dark navy-black",
        "antique gold",
        "cyan brine energy",
        "crimson-magenta sailcloth"
    ],
    "materials": [
        "Bone-brine plates",
        "Shipwreck timber",
        "Salvage rigging",
        "Rusted ironwork",
        "Whale bone ribs",
        "Tattered sails"
    ],
    "signature_prop": "Ossuary Dredge",
    "active_abilities": [
        {
            "slot": "1",
            "name": "Dredge Snare",
            "summary": "Fires chains and bone-ribs from the Ossuary Dredge to latch onto enemies and wreckage, dragging them toward Dreadhull and displacing their position."
        },
        {
            "slot": "2",
            "name": "Salvage Recall",
            "summary": "Pulls floating or shattered debris back into himself, restoring armor and briefly healing for a portion of the reclaimed wreckage."
        },
        {
            "slot": "3",
            "name": "Reforge Bulwark",
            "summary": "Converts dredged wreckage into a large bonebrine barricade, granting cover and a protective aura that reduces incoming damage for Dreadhull and nearby allies."
        },
        {
            "slot": "4",
            "name": "Wreckline Drag",
            "summary": "Whips a chain line from the dredge, dragging a targeted enemy along with nearby wreckage, briefly slowing them on arrival and disrupting their formation."
        },
        {
            "slot": "5_ultimate",
            "name": "Graveyard Forge",
            "summary": "Dredges a massive field of wreckage from the seafloor, erupting into a fortified salvage zone. The area becomes a graveyard forge that grants cover, empowers allies' defenses, and continuously reclaims debris over time."
        }
    ],
    "passive": {
        "name": "Sunken Claim",
        "summary": "Damage absorbed by his shields stores Salvage Charge. At high charge, his next defensive ability is strengthened (increased shield, duration, and additional effect)."
    },
    "archetype": "Battlefield Reclamation Tank",
    "one_of_one_hook": "Ossuary Dredge reclaims cursed wreckage into temporary cover and protective power using Salvage Charge.",
    "silhouette_read": "Heavy asymmetrical hooded undead biped, giant circular bone-rib dredge, opposing jagged timber bulwark, open wreck rigging and cyan lantern.",
    "gameplay_promise": "Protect, reclaim, reforge, control and empower; reclaim debris into defenses and displace enemies."
}

# K.R.A.I.T visual approval only; do not infer gameplay from the cropped source.
KRAIT_VISUAL_CONTRACT = {
    "visual_lock": [
        "Exact owner-selected primary portrait: tall, heavily built humanoid tank, broad upper torso, large fists and thick articulated leg armor.",
        "Closed angular helmet with two swept upward dark horns and a pointed luminous cyan face visor; preserve the visible helmet contours, no exposed human face.",
        "Silver-blue layered metallic armor; dragon-shaped pauldrons with swept spikes, circular cyan shoulder joints and dark recessed flexible sections.",
        "Bright circular cyan chest reactor and smaller illuminated torso and waist cores; cyan lighting follows the source portrait.",
        "Rift Knuckles: preserve the large armored gauntlets, segmented fingers and pointed forearm fins shown in the approved portrait.",
        "Preserve the visible ascension study: wing-like energy projections on the armor, with cyan/blue and orange-gold states shown. Exact stage names, progression and mechanics are unreadable or incomplete and not approved by inference.",
        "Preserve the supplied screenshot without crop, cleanup, reconstruction or removal of its phone UI overlay. Its darker turnaround/red accents are reference evidence, not permission to replace the primary portrait."
    ],
    "forbidden_drift": [
        "No replacement with Bryskar's earlier character art, another hero's silhouette, a generic knight, an external franchise character, a different helmet or unrelated equipment.",
        "No silent changes to the dragon-shaped pauldrons, horned helmet, cyan visor, chest reactor, gauntlets, armor proportions or visible ascension appearance.",
        "Do not infer an acronym expansion, final transformation mechanics, unreadable ability descriptions, unseen angles or complete palette from the cropped screenshot.",
        "Do not register Bryskar as another active hero or promote the historical Bryskar design file as K.R.A.I.T's visual master.",
        "No model, rig, runtime, full roster uniqueness or completed concept-package claim without corresponding proof."
    ],
    "visual_identity": "Exact owner-selected primary portrait: tall, heavily built humanoid tank, broad upper torso, large fists and thick articulated leg armor. Closed angular helmet with two swept upward dark horns and a pointed luminous cyan face visor; preserve the visible helmet contours, no exposed human face. Silver-blue layered metallic armor; dragon-shaped pauldrons with swept spikes, circular cyan shoulder joints and dark recessed flexible sections. Bright circular cyan chest reactor and smaller illuminated torso and waist cores; cyan lighting follows the source portrait. Rift Knuckles: preserve the large armored gauntlets, segmented fingers and pointed forearm fins shown in the approved portrait. Preserve the visible ascension study: wing-like energy projections on the armor, with cyan/blue and orange-gold states shown. Exact stage names, progression and mechanics are unreadable or incomplete and not approved by inference. Preserve the supplied screenshot without crop, cleanup, reconstruction or removal of its phone UI overlay. Its darker turnaround/red accents are reference evidence, not permission to replace the primary portrait.",
    "signature_prop": "Rift Knuckles",
    "palette": [
        "silver-blue metal (portrait)",
        "dark navy/black recesses",
        "cyan emissive energy",
        "red accents in turnaround studies",
        "orange-gold energy in ascension study"
    ],
    "materials": [
        "Segmented metallic armor",
        "Dark recessed joints",
        "Luminous cyan cores"
    ],
    "approval_scope": "Exact owner-selected visual screenshot and replacement identity only; full gameplay kit/ascension mechanics pending."
}
KRAIT_REPLACEMENT = {
    "previous_name": "Bryskar",
    "previous_proposed_id": "CHR_Bryskar",
    "canonical_id": "CHR_KRAIT",
    "canonical_name": "K.R.A.I.T",
    "status": "superseded_not_active",
    "owner_approval_date": "2026-11-27",
    "historical_kit_path": "docs/characters/BRYSKAR_OWNER_SELECTED_KIT.md",
    "scope": "Owner approved K.R.A.I.T visual design and replacement identity; complete inherited gameplay kit and ascension rules require separate confirmation."
}
# Independent owner-selected Korvex concept contract.
KORVEX_DESIGN_CONTRACT = {
    "identity": {
        "display_name": "Korvex",
        "epithet": "The Hollow Titan",
        "role_class": "tank",
        "signature_focus": "Grave Maul",
        "active_ability_names": [
            "Grave Maul",
            "Bone Bastion",
            "Decay Field",
            "Titan's Roar"
        ],
        "passive_ability_name": "Hollow Endurance"
    },
    "visual_lock": [
        "Massive graveborn humanoid juggernaut, walking mausoleum silhouette, broad shoulders, heavy armored limbs, wide stance.",
        "Closed angular horned helmet with vertical purple glowing visor slits; retain exact face/helmet shapes in the four expression studies.",
        "Layered aged iron and mausoleum stone armor with bronze-gold edging, jagged spikes, bone carving and shoulder skull ornaments.",
        "Purple void-soul energy glows through rib-like chest armor and gothic window-like openings; preserve the pointed-arch illuminated structure on his back.",
        "Heavy chains, suspended purple soul lanterns, tattered purple funeral cloth and front tabard; no pirate rigging or generic cape substitution.",
        "Grave Maul is the signature long-handled gothic mausoleum-shaped hammer with spiked roof, glowing pointed-arch purple windows and hanging lanterns.",
        "Preserve the exact 4:3 AETHERFALL source sheet, front/side/back turnaround and materials/palette, not an earlier alternative or a generated approximation."
    ],
    "forbidden_drift": [
        "No replacement helmet, different silhouette, human face, generic knight or copied hero armor.",
        "No Grave Maul substitution with an axe, shield, sword, anchor or unrelated weapon.",
        "No removal of gothic mausoleum motifs, chains, skulls, lanterns, purple funeral cloth or void-soul energy.",
        "Do not silently rename Korvex to Corvex or resolve the separate unapproved alias/collision record.",
        "No changes to approved source bytes or concept kit without explicit owner review; no final tuning, model or runtime claims."
    ],
    "visual_identity": "Massive graveborn humanoid juggernaut, walking mausoleum silhouette, broad shoulders, heavy armored limbs, wide stance. Closed angular horned helmet with vertical purple glowing visor slits; retain exact face/helmet shapes in the four expression studies. Layered aged iron and mausoleum stone armor with bronze-gold edging, jagged spikes, bone carving and shoulder skull ornaments. Purple void-soul energy glows through rib-like chest armor and gothic window-like openings; preserve the pointed-arch illuminated structure on his back. Heavy chains, suspended purple soul lanterns, tattered purple funeral cloth and front tabard; no pirate rigging or generic cape substitution. Grave Maul is the signature long-handled gothic mausoleum-shaped hammer with spiked roof, glowing pointed-arch purple windows and hanging lanterns. Preserve the exact 4:3 AETHERFALL source sheet, front/side/back turnaround and materials/palette, not an earlier alternative or a generated approximation.",
    "palette": [
        "bone ivory",
        "aged iron gray",
        "violet",
        "deep plum",
        "charcoal",
        "bronze-gold"
    ],
    "materials": [
        "Aged iron",
        "Mausoleum stone",
        "Bone carving",
        "Funeral cloth (tattered)",
        "Void-soul energy"
    ],
    "signature_prop": "Grave Maul",
    "active_abilities": [
        {
            "slot": "primary",
            "name": "Grave Maul",
            "summary": "A devastating, empowered maul strike that crushes enemies, dealing heavy damage (increased against high-durability targets)."
        },
        {
            "slot": "active_1",
            "name": "Bone Bastion",
            "summary": "Raises jagged grave-spires or tombstone barricades from the ground, blocking paths and controlling space."
        },
        {
            "slot": "active_2",
            "name": "Decay Field",
            "summary": "Corrupts the ground in an area, dealing damage over time and weakening enemies' defenses."
        },
        {
            "slot": "active_3",
            "name": "Titan's Roar",
            "summary": "Unleashes a monumental roar that staggers enemies and slows their movement and attack speed."
        }
    ],
    "passive": {
        "name": "Hollow Endurance",
        "summary": "Converts a portion of incoming damage into temporary armor (Endurance), bolstering Korvex's durability."
    },
    "archetype": "Anti-tank / zone denial / frontline juggernaut",
    "one_of_one_hook": "Walking mausoleum with Grave Maul, tombstone barricades, defense-eroding decay and temporary Endurance armor.",
    "silhouette_read": "Broad spiked gothic mausoleum armor, horned visor, purple lantern chains, long-handled mausoleum hammer and tattered funeral cloth.",
    "gameplay_promise": "Pressure high-durability targets, control space with tomb barriers, weaken enemies in corrupted ground and survive extended fights."
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
    locks = manifest.get("locked_characters")
    if not isinstance(locks, dict) or not set(PINNED).issubset(set(locks)):
        errors.append("Pinned owner-approved character canon lock missing")
        locks = {}
    replacements = manifest.get("character_replacements")
    if not isinstance(replacements, dict) or replacements.get("CHR_Bryskar") != KRAIT_REPLACEMENT:
        errors.append("K.R.A.I.T owner replacement decision drift")
    if "CHR_Bryskar" in locks:
        errors.append("Superseded Bryskar cannot be active canon")
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
        cref = plan.get("concept_reference", {})
        if not isinstance(cref, dict) or (cref.get("repo_path") != pinned["path"]
                or cref.get("sha256") != pinned["sha256"]):
            errors.append("Locked source no longer matches character plan: " + identifier)
            cref = {}
        pi = plan.get("identity") or {}
        design = plan.get("design") or {}
        if identifier == "CHR_Korvex":
            actual_contract = {
                "identity": ident,
                "visual_lock": lock.get("visual_lock"),
                "forbidden_drift": lock.get("forbidden_drift"),
                **{key: design.get(key) for key in (
                    "visual_identity", "palette", "materials", "signature_prop",
                    "active_abilities", "passive")},
                **{key: pi.get(key) for key in (
                    "archetype", "one_of_one_hook", "silhouette_read", "gameplay_promise")},
            }
            if actual_contract != KORVEX_DESIGN_CONTRACT:
                errors.append("Korvex approved design contract drift")
            if source.get("media_type") != "image/png" or source.get("uploaded_filename") != "AETHERFALL_Korvex_The_Hollow_Titan_Review.png":
                errors.append("Korvex original source provenance drift")
        if identifier == "CHR_KRAIT":
            actual_visual = {
                "visual_lock": lock.get("visual_lock"),
                "forbidden_drift": lock.get("forbidden_drift"),
                **{key: design.get(key) for key in (
                    "visual_identity", "signature_prop", "palette", "materials")},
                "approval_scope": lock.get("approval_scope"),
            }
            if actual_visual != KRAIT_VISUAL_CONTRACT or ident.get("signature_focus") != pinned["focus"]:
                errors.append("K.R.A.I.T approved visual contract drift")
            if source.get("media_type") != "image/webp" or source.get("uploaded_filename") != "1795779132409.jpeg":
                errors.append("K.R.A.I.T original source provenance drift")
            if plan.get("replaces_proposed_id") != "CHR_Bryskar":
                errors.append("K.R.A.I.T owner replacement plan drift")
            if design.get("kit_status") != "pending" or design.get("active_abilities") != [] or design.get("passive") is not None:
                errors.append("K.R.A.I.T unapproved gameplay kit promotion")
        if identifier == "CHR_Dreadhull":
            # A keyword match alone would allow a renamed weapon or rewritten mechanics.
            actual_contract = {
                "identity": ident,
                "visual_lock": lock.get("visual_lock"),
                "forbidden_drift": lock.get("forbidden_drift"),
                **{key: design.get(key) for key in (
                    "visual_identity", "palette", "materials", "signature_prop",
                    "active_abilities", "passive")},
                **{key: pi.get(key) for key in (
                    "archetype", "one_of_one_hook", "silhouette_read", "gameplay_promise")},
            }
            if actual_contract != DREADHULL_DESIGN_CONTRACT:
                errors.append("Dreadhull approved design contract drift: " + identifier)
            if source.get("media_type") != "image/webp" or source.get("uploaded_filename") != "40768.png":
                errors.append("Dreadhull original source provenance drift: " + identifier)
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
        if any(isinstance(value, str) and value.casefold() == "chr_bryskar" for value in ids):
            errors.append("Superseded Bryskar cannot be registered as an active hero")
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
        for identifier in sorted(set(PINNED) - set(approved)):
            errors.append("Pinned owner-approved character registry status removed: " + identifier)
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
