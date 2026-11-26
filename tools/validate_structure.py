#!/usr/bin/env python3
"""AETHERFALL offline source safety gates. Not native game or art evidence."""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md", "AGENTS.md", ".gitignore", ".gitattributes",
    "game/project.godot", "game/scenes/bootstrap/main.tscn",
    "art/asset_registry.json", "docs/architecture/REPO_LAYOUT.md",
    "docs/art/ASSET_PIPELINE.md",
    "docs/art/UNIVERSAL_INFOGRAPHIC_STANDARD.md",
    "docs/art/INFOGRAPHIC_POLICY.json",
    "docs/art/INFOGRAPHIC_PLAN_TEMPLATE.json", "docs/characters/CHARACTER_REGISTRY.md",
    "docs/legacy/shadowspire_migration.json", "docs/legacy/README.md",
    "docs/characters/LEGACY_ROSTER.md",
    "docs/characters/CHARACTER_WORKFLOW.md",
    "docs/characters/CANON_LOCKS.json",
    "docs/characters/VISUAL_CANON_LOCK.md",
    "tools/verify_visual_canon.py",
    "docs/characters/DRIFT_REVIEW_TEMPLATE.md",
    "docs/architecture/MAIN_BRANCH_LOCK_SETUP.md",
    "docs/characters/CHARACTER_INTAKE.md",
    "docs/characters/templates/CHARACTER_PLAN_TEMPLATE.json",
    "docs/game-design/SHADOWSPIRE_LEGACY_DESIGN.md", "evidence/README.md",
)
REQUIRED_DIRS = (
    "game/scenes/characters/heroes", "game/scenes/characters/enemies",
    "game/scenes/levels/realms", "game/scripts/core", "game/scripts/combat",
    "game/scripts/abilities", "game/assets/characters/heroes", "game/assets/weapons",
    "game/assets/worlds", "game/audio/music", "game/shaders",
    "art/blender/characters", "art/blender/weapons", "art/concepts/characters",
    "evidence/godot", "evidence/blender", "evidence/device", "tests",
)
IGNORED_DIRS = {".git", ".godot", ".import", ".pytest_cache", "__pycache__", "build", "dist", ".venv"}
PRIVATE_FILENAMES = {"id_rsa", "id_ed25519", "credentials.json", "service-account.json", "service_account.json", ".netrc", ".npmrc", ".pypirc"}
PRIVATE_EXTENSIONS = {".pem", ".key", ".p12", ".pfx", ".jks", ".keystore"}
BINARY_ART_EXTENSIONS = {".blend", ".glb", ".fbx", ".gltf", ".png", ".jpg", ".jpeg", ".wav", ".ogg", ".mp4"}
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
            if item.suffix.lower() in BINARY_ART_EXTENSIONS and item.stat().st_size > MAX_DIRECT_BINARY_BYTES:
                errors.append("Binary exceeds 50 MiB without reviewed LFS/storage plan: " + rel)


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



CHARACTER_SECTIONS = (
    "hero_portrait", "turnaround_front", "turnaround_side", "turnaround_back",
    "turnaround_three_quarter", "silhouette_exploration", "face_expressions",
    "palette_swatches", "materials_callouts", "weapon_or_focus",
    "gameplay_identity", "ability_kit", "vfx_motion", "audio_voice",
    "technical_handoff", "accessibility_readability",
)
CHARACTER_GATES = (
    "identity_owner_approved", "source_archived", "concept_package_reviewed",
    "blockout_approved", "model_verified", "rig_animation_verified",
    "godot_import_verified", "gameplay_verified", "release_verified",
)
SECTION_STATES = {
    "pending", "visible_in_unarchived_reference", "source_verified", "approved_waiver",
}
HASH_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _valid_digest(value):
    return isinstance(value, str) and bool(HASH_SHA256.fullmatch(value))


def _file_matches_sha256(path, digest):
    return hashlib.sha256(path.read_bytes()).hexdigest() == digest


def validate_character_plans(root, errors):
    """Fail closed for all registered heroes; never equate a plan to native engine proof."""
    registry_path = root / "art/asset_registry.json"
    if not registry_path.is_file():
        return
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return  # validate_registry has already reported the malformed registry.
    if not isinstance(data, dict) or not isinstance(data.get("assets"), list):
        return
    characters = {item["id"]: item for item in data["assets"]
                  if isinstance(item, dict) and item.get("type") == "character"
                  and isinstance(item.get("id"), str)
                  and ID_PATTERN.fullmatch(item["id"])}
    plan_dir = root / "docs/characters/plans"
    if not plan_dir.is_dir() or plan_dir.is_symlink():
        errors.append("Missing/unsafe character plan directory")
        return
    actual_plans = {path.stem for path in plan_dir.glob("*.json")}
    for orphan in sorted(actual_plans - set(characters)):
        errors.append("Unregistered character plan: " + orphan)
    one_of_one = {}
    for identifier, asset in sorted(characters.items()):
        path = plan_dir / (identifier + ".json")
        if not path.is_file() or path.is_symlink():
            errors.append("Missing character plan: " + identifier)
            continue
        try:
            plan = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            errors.append("Invalid character plan JSON: " + identifier)
            continue
        if not isinstance(plan, dict):
            errors.append("Invalid character plan object: " + identifier)
            continue
        if (plan.get("schema_version") != 1 or
                plan.get("project") != "AETHERFALL: REALMS COLLIDE" or
                plan.get("standard") != "VELLARIS_V1_PLUS" or
                plan.get("character_id") != identifier or
                plan.get("registry_role") != asset.get("role") or
                plan.get("registry_concept_status") != asset.get("concept_status")):
            errors.append("Character plan identity/registry mismatch: " + identifier)
        if not _nonempty(plan.get("display_name")) or not _nonempty(plan.get("epithet")):
            errors.append("Character name/title missing: " + identifier)

        identity = plan.get("identity")
        if not isinstance(identity, dict):
            errors.append("Character identity missing: " + identifier)
            identity = {}
        role = asset.get("role", "")
        expected_class = "tank" if "tank" in role else "support" if "support" in role else None
        if (identity.get("role_class") not in ("tank", "support", "damage", "enemy", "boss", "npc", "unconfirmed")
                or (expected_class and identity.get("role_class") != expected_class)):
            errors.append("Character role class mismatch: " + identifier)
        for key in ("archetype", "one_of_one_hook", "silhouette_read", "gameplay_promise", "counterplay"):
            if not _nonempty(identity.get(key)):
                errors.append("Missing character identity " + key + ": " + identifier)
        hook = identity.get("one_of_one_hook")
        if _nonempty(hook):
            unique = hook.strip().casefold()
            if unique in one_of_one:
                errors.append("Duplicate character one-of-one identity: " + identifier + " and " + one_of_one[unique])
            one_of_one[unique] = identifier

        design = plan.get("design")
        if not isinstance(design, dict):
            design = {}
            errors.append("Character design package missing: " + identifier)
        approved = asset.get("concept_status") == "aetherfall_approved"
        expected_status = "approved_concept_only" if approved else "legacy_candidate_pending_aetherfall_approval"
        if design.get("owner_status") != expected_status:
            errors.append("Unreviewed character approval promotion: " + identifier)
        for key in ("visual_identity", "signature_prop", "accessibility_notes"):
            if not _nonempty(design.get(key)):
                errors.append("Missing character design " + key + ": " + identifier)
        if not isinstance(design.get("palette"), list) or not isinstance(design.get("materials"), list):
            errors.append("Character palette/material data malformed: " + identifier)
        kit_status = design.get("kit_status")
        if kit_status not in ("pending", "concept_reference_only", "owner_locked"):
            errors.append("Unknown character kit status: " + identifier)
        abilities = design.get("active_abilities")
        passive = design.get("passive")
        if not isinstance(abilities, list):
            errors.append("Character abilities not a list: " + identifier)
            abilities = []
        if kit_status != "pending":
            if not abilities or not isinstance(passive, dict) or not _nonempty(passive.get("name")) or not _nonempty(passive.get("summary")):
                errors.append("Character kit lacks named active/passive: " + identifier)
        names = set()
        for ability in abilities:
            if not isinstance(ability, dict) or not all(_nonempty(ability.get(k)) for k in ("slot", "name", "summary")):
                errors.append("Malformed character ability: " + identifier)
                continue
            name = ability["name"].casefold()
            if name in names:
                errors.append("Duplicate character ability: " + identifier)
            names.add(name)

        source = plan.get("concept_reference")
        if not isinstance(source, dict):
            source = {}
            errors.append("Missing character concept reference: " + identifier)
        raw = source.get("repo_path")
        expected_prefix = asset.get("concept_dir", "") + "/"
        file = safe_path(root, raw)
        if (file is None or not isinstance(raw, str)
                or not raw.startswith(expected_prefix) or
                not raw.lower().endswith((".png", ".jpg", ".jpeg", ".webp")) or
                file.parent != root / asset.get("concept_dir", "")):
            errors.append("Unsafe/mismatched character master path: " + identifier)
            file = None
        archive = source.get("archive_status")
        digest = source.get("sha256")
        if archive not in ("pending_source_upload", "source_verified"):
            errors.append("Invalid character source archive status: " + identifier)
        if digest is not None and not _valid_digest(digest):
            errors.append("Malformed character reference SHA-256: " + identifier)
        if not _nonempty(source.get("origin_note")):
            errors.append("Missing character provenance: " + identifier)
        if file is not None:
            if archive == "source_verified":
                if not file.is_file() or file.is_symlink() or not _valid_digest(digest):
                    errors.append("Character source claimed archived without verified file: " + identifier)
                elif not _file_matches_sha256(file, digest):
                    errors.append("Character master source checksum mismatch: " + identifier)
            elif file.is_file():
                errors.append("Character source present but archive not verified: " + identifier)

        sections = plan.get("sheet_sections")
        if not isinstance(sections, dict) or set(sections) != set(CHARACTER_SECTIONS):
            errors.append("Character sheet sections incomplete: " + identifier)
            sections = {}
        waivers = plan.get("section_waivers")
        if not isinstance(waivers, dict):
            waivers = {}
            errors.append("Character section waivers malformed: " + identifier)
        for section, state in sections.items():
            if state not in SECTION_STATES:
                errors.append("Invalid character sheet section state: " + identifier + "/" + section)
            if state == "source_verified" and archive != "source_verified":
                errors.append("Unarchived character sheet marked source-verified: " + identifier)
            if state == "approved_waiver":
                waiver = waivers.get(section)
                if not isinstance(waiver, dict) or not all(_nonempty(waiver.get(k)) for k in ("owner", "reason", "review_path")):
                    errors.append("Undocumented character section waiver: " + identifier + "/" + section)
                else:
                    review = safe_path(root, waiver["review_path"])
                    if (review is None or not waiver["review_path"].startswith("evidence/characters/" + identifier + "/")
                            or not review.is_file() or review.is_symlink()):
                        errors.append("Missing character waiver review: " + identifier + "/" + section)
        for waived in set(waivers) - {k for k, v in sections.items() if v == "approved_waiver"}:
            errors.append("Unused character waiver: " + identifier + "/" + waived)

        gates = plan.get("gates")
        if not isinstance(gates, dict) or set(gates) != set(CHARACTER_GATES) or any(type(x) is not bool for x in gates.values()):
            errors.append("Character stage gates incomplete/invalid: " + identifier)
            continue
        if gates["identity_owner_approved"] != approved:
            errors.append("Character identity gate mismatch with registry: " + identifier)
        if gates["source_archived"] != (archive == "source_verified"):
            errors.append("Character archived source gate mismatch: " + identifier)
        for previous, current in zip(CHARACTER_GATES, CHARACTER_GATES[1:]):
            if gates[current] and not gates[previous]:
                errors.append("Character production gate skipped: " + identifier + "/" + current)
        if gates["concept_package_reviewed"] and any(state not in ("source_verified", "approved_waiver") for state in sections.values()):
            errors.append("Character concept sheet not fully verified: " + identifier)
        if kit_status == "owner_locked" and not gates["concept_package_reviewed"]:
            errors.append("Character kit locked without approved package: " + identifier)

        stage_evidence = plan.get("stage_evidence")
        if not isinstance(stage_evidence, dict):
            errors.append("Character stage_evidence malformed: " + identifier)
            stage_evidence = {}
        for stage in CHARACTER_GATES[2:]:
            if not gates[stage]:
                continue
            proof = stage_evidence.get(stage)
            if not isinstance(proof, dict):
                errors.append("Missing character stage evidence: " + identifier + "/" + stage)
                continue
            proof_path = proof.get("path")
            proof_file = safe_path(root, proof_path)
            proof_hash = proof.get("sha256")
            if (proof_file is None or not isinstance(proof_path, str)
                    or not proof_path.startswith("evidence/characters/" + identifier + "/")
                    or not proof_file.is_file() or proof_file.is_symlink() or not _valid_digest(proof_hash)):
                errors.append("Unsafe/missing character proof file: " + identifier + "/" + stage)
            elif not _file_matches_sha256(proof_file, proof_hash):
                errors.append("Character proof checksum mismatch: " + identifier + "/" + stage)

    registered = set(characters)
    for base in (
        "art/concepts/characters", "art/blender/characters",
        "game/assets/characters/heroes", "game/assets/characters/enemies",
        "game/assets/characters/npcs", "game/scenes/characters/heroes",
        "game/scenes/characters/enemies", "game/scenes/characters/npcs",
    ):
        folder = root / base
        if folder.is_dir():
            for child in folder.iterdir():
                if child.is_dir() and child.name not in registered:
                    errors.append("Unregistered character folder: " + child.relative_to(root).as_posix())


# SIRE-ART-INFO-001: protect all new visual asset categories, not just characters.
# A metadata gate proves only existence/identity, NEVER artistic similarity or gameplay.
INFOGRAPHIC_REQUIRED_PANELS = {
    "character": ("hero_visual", "four_view_turnaround", "silhouette_studies",
                  "materials_palette", "unique_equipment", "gameplay_identity",
                  "abilities_and_movement"),
    "weapon": ("hero_visual", "multi_angle_views", "materials_palette",
               "construction_and_operation", "gameplay_effects"),
    "object": ("hero_visual", "multi_angle_views", "scale_and_silhouette",
               "materials_palette", "interaction_states"),
    "level": ("key_environment_art", "top_down_map", "elevations_and_vistas",
              "routes_cover_and_sightlines", "spawns_objectives_and_exits"),
    "environment": ("key_environment_art", "layout_and_landmarks",
                    "elevations_and_vistas", "lighting_and_materials"),
    "building": ("architectural_hero", "exterior_views", "interior_and_floor_plan",
                 "scale_and_materials", "traversal_and_interactions"),
    "creature": ("hero_visual", "four_view_turnaround", "silhouette_and_anatomy",
                 "locomotion_and_abilities"),
    "vehicle": ("hero_visual", "multi_angle_views", "parts_and_mechanisms",
                "controls_and_movement"),
    "ui": ("hero_screen", "responsive_layouts", "component_variants",
           "interaction_and_state_flows", "accessibility_and_platform_handoff"),
    "vfx": ("key_visual", "time_based_sequence", "triggers_and_telegraph",
            "accessibility_and_performance"),
}


def validate_infographic_policy(root, errors):
    """Lock source-standard, panel coverage and unapproved template state."""
    p = root / "docs/art/INFOGRAPHIC_POLICY.json"
    t = root / "docs/art/INFOGRAPHIC_PLAN_TEMPLATE.json"
    c = root / "docs/characters/CANON_LOCKS.json"
    try:
        policy = json.loads(p.read_text(encoding="utf-8"))
        template = json.loads(t.read_text(encoding="utf-8"))
        canon = json.loads(c.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as exc:
        errors.append("Missing/invalid infographic policy or template: " + str(exc))
        return
    if (not isinstance(policy, dict)
            or policy.get("schema_version") != 1
            or policy.get("law_id") != "SIRE-ART-INFO-001"
            or policy.get("project") != "AETHERFALL: REALMS COLLIDE"
            or policy.get("policy") != "INFOGRAPHIC_FIRST_NO_CANON_DRIFT"
            or policy.get("authority") != "docs/art/UNIVERSAL_INFOGRAPHIC_STANDARD.md"):
        errors.append("Infographic policy authority/identity drift")
        return
    ref = policy.get("master_reference")
    if not isinstance(ref, dict):
        ref = {}
    try:
        approved = canon["locked_characters"]["CHR_Vellaris_Bloodshield"]["source"]
    except (KeyError, TypeError):
        approved = {}
    if (ref.get("character_id") != "CHR_Vellaris_Bloodshield"
            or ref.get("uploaded_name") != "39403.png"
            or ref.get("actual_format") != "WEBP"
            or ref.get("aspect_ratio") != "4:3"
            or ref.get("width") != 1536 or ref.get("height") != 1152
            or ref.get("archive_status") != "pending_binary_checkin"
            or ref.get("sha256") != "4d100d50cf0769da47cbe1b782deeb842d15a11c1c46a08f8bd5bd090fa34939"
            or ref.get("sha256") != approved.get("sha256")):
        errors.append("Infographic master reference identity/hash drift")
    panels = policy.get("asset_panels")
    if not isinstance(panels, dict) or set(panels) != set(INFOGRAPHIC_REQUIRED_PANELS):
        errors.append("Infographic asset type coverage drift")
        panels = {}
    for kind, required in INFOGRAPHIC_REQUIRED_PANELS.items():
        available = panels.get(kind)
        if (not isinstance(available, list) or len(available) != len(set(available))
                or not set(required).issubset(set(available))):
            errors.append("Infographic required panels missing: " + kind)
    frame = policy.get("board_frame")
    if (not isinstance(frame, dict)
            or "hero left" not in str(frame.get("layout", "")).lower()
            or "magenta" not in str(frame.get("palette", "")).lower()
            or "not final in-game model" not in str(frame.get("required_footer", "")).lower()):
        errors.append("Infographic board frame/footer drift")
    if (policy.get("owner_approval_required") is not True
            or policy.get("allow_inapplicable_panels_only_with_owner_waiver") is not True
            or policy.get("generated_art_is_runtime_proof") is not False
            or policy.get("source_integrity_sha256_required_for_archive") is not True
            or not isinstance(policy.get("statuses"), list)
            or policy["statuses"][0] != "PROPOSAL_PENDING_OWNER_REVIEW"):
        errors.append("Infographic owner review/evidence safety drift")
    if (not isinstance(template, dict)
            or template.get("law_id") != "SIRE-ART-INFO-001"
            or template.get("project") != "AETHERFALL: REALMS COLLIDE"
            or template.get("status") != "PROPOSAL_PENDING_OWNER_REVIEW"
            or template.get("owner_review", {}).get("decision") != "pending"
            or template.get("runtime_evidence", {}).get("status") != "NOT_VERIFIED"
            or template.get("infographic", {}).get("archive_status") != "not_archived"):
        errors.append("Infographic plan template self-approval or evidence drift")


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
    validate_registry(root, errors)
    validate_character_plans(root, errors)
    validate_infographic_policy(root, errors)
    import importlib.util
    canon_file = Path(__file__).with_name("verify_visual_canon.py")
    spec = importlib.util.spec_from_file_location("aetherfall_visual_canon", canon_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    errors.extend(module.check(root))
    validate_godot(root, errors)
    validate_legacy_hold(root, errors)
    return errors


def main():
    failures = check()
    if failures:
        for failure in failures:
            print("FAIL: " + failure, file=sys.stderr)
        return 1
    print("PASS: source/asset paths, infographic policy, character source hashes/canon metadata, gate order, Godot references and migration safety (STATIC ONLY; NO VISUAL LIKENESS PROOF)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

