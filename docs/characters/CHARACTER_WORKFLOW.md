# AETHERFALL — Mandatory Character Blueprint: VELLARIS_V1_PLUS

**Policy date:** 2026-11-26. **Owner-authorised standard:** All future playable characters, tanks, DPS, supports, enemies, bosses and important NPCs must use this workflow or a documented owner-approved improvement. This adds to (does not replace) `docs/art/ASSET_PIPELINE.md` and the existing S.I.R.E. production law.

The owner-provided **Vellaris — The Bloodshield** master sheet is the **minimum completeness reference**, *not* a verified final game model. Match the sheet's depth and clarity, **not** her shield, colors, abilities, silhouette or species. Every tank must be meaningfully 1-of-1: avoid giving all tanks a shield. Do not change locked art or canonical IDs without owner approval.

## One character = one registered, searchable plan

1. Inspect `art/asset_registry.json` and `docs/characters/CHARACTER_INTAKE.md`. Reserve a unique `CHR_<Name>` ID and honest `concept_status`; check aliases before renaming anyone (especially Corvex/Korvex).
2. Copy `docs/characters/templates/CHARACTER_PLAN_TEMPLATE.json` to `docs/characters/plans/<ID>.json`. Use exact registry ID, role, concept approval and real blockers. The validator rejects unregistered character folders and missing/mismatched plans.
3. Put rights-cleared *unaltered* concept source under `art/concepts/characters/<ID>/`, with SHA-256 and source credit in `concept_reference`. Source `.blend` goes under `art/blender/characters/<ID>/`; exported `.glb` goes under `game/assets/characters/.../<ID>/`. The original uploaded chat file is **not** a GitHub archive.
4. Set `archive_status=source_verified` and `gates.source_archived=true` only after GitHub holds the exact hashed file. A visible chat reference uses `visible_in_unarchived_reference`; it cannot pass the production gate.
5. Require owner review and truthful native evidence for each further gate. Log task ID, authorised executor, tests, versions, exact source commit, hashes and blockers.

## Required full concept-sheet areas

| Section | Deliverable |
| --- | --- |
| Hero portrait | Beauty image, face, hair, accessories, identity, unique title and role. |
| Turnaround front/side/back/3-quarter | Consistent full-body views, scale, silhouettes and gear visibility. |
| Silhouette exploration | Multiple distinct shapes; selected one clear from gameplay camera. |
| Facial expressions | Neutral, commanding, action/battle, alternative emotion. |
| Palette and materials | Named color swatches, metallic/cloth/organic/PBR/emissive close-ups. |
| Weapon or focus | Unique hero weapon, spell focus, construct or companion; shield only when character-specific. |
| Gameplay identity | Distinctive role, positioning, counterplay, team synergies, movement and signature mechanic. |
| Active and passive kit | Named abilities with summary, timing, anticipation, counterplay and readable VFX/audio cues. Vellaris shows four actives plus passive; other kit layouts must be intentionally justified, not cloned. |
| VFX/motion and audio/voice | Animation beats, skill readability, sound design, voice, localization and performance limits. |
| Technical handoff | Height, scale, armature/rig, animation clips, texture/LOD/triangle targets, exports, engine versions, naming. |
| Accessibility/readability | Ally/enemy silhouette, low-contrast colors, flashes, sound alternatives and real-game camera checks. |

All 16 machine-readable `sheet_sections` are mandatory and start `pending`; mark `visible_in_unarchived_reference` only if actually shown in an external source, and `source_verified` only when the exact source file is archived and hashed. An `approved_waiver` must identify an owner-signed reason in `section_waivers`, never silent omission.

## Locked stage sequence

`identity_owner_approved` → `source_archived` → `concept_package_reviewed` → `blockout_approved` → `model_verified` → `rig_animation_verified` → `godot_import_verified` → `gameplay_verified` → `release_verified`.

- **Identity:** AETHERFALL design/kit identity approved by owner. Historical Shadowspire selection is only a candidate.
- **Source:** Rights-cleared original committed, SHA-256 matches, changes versioned without replacing existing canon.
- **Concept package:** Every required panel verified/explicitly waived; owner review note under `evidence/characters/<ID>/`.
- **Blockout:** Real Blender 4-view preview, proportions, hands/feet, props and silhouette approved.
- **Model:** Real editable sculpt/retopo, UV/PBR/material, weights, texture budgets and LOD checks.
- **Rig and animation:** Real armature, clips, locomotion, action, equipment and rig tests.
- **Godot import:** Genuine engine import and character-scene tests; no missing resources/material/rig errors.
- **Gameplay:** Actual abilities, targeting, hitboxes, team reads, accessibility, performance and regression tests.
- **Release:** Real device/controller, saves, audio, accessibility and build/proof review. Headless boot ≠ visual/gameplay proof.

Any true downstream gate requires all earlier gates, evidence-file path + SHA-256 in `stage_evidence`, and actual owner review. CI checks the *structure*, hashes, and non-skippable order only; a reviewer must assess whether native video/screenshot evidence is genuine.

## One build path for the whole team

FIND → PLAN → BUILD → TEST → REPAIR → RETEST → SHOW → HARDEN → PROVE → FINISH. In the PR/work order state project, ID, goal, owner-approved executor, source path, tests, gate status, genuine proof and remaining blockers. Run `python3 tools/validate_structure.py` and `python3 -m unittest discover -s tests -v`. Existing GitHub Actions runs these and the Godot bootstrap smoke. Enable required CI + CODEOWNERS review on `main` in repo branch settings to make the approved standard a hard merge lock.

**Unarchived Vellaris reference:** original owner upload is a 1536×1152 WebP (uploaded as 39403.png), SHA-256 `4d100d50cf0769da47cbe1b782deeb842d15a11c1c46a08f8bd5bd090fa34939`. Destination: `art/concepts/characters/CHR_Vellaris_Bloodshield/Vellaris_Bloodshield_concept_v1.webp`. It is visible in conversation, **not yet in GitHub**. Treat it as a character development concept sheet, never as native proof.

## Absolute visual-drift gate

First read VISUAL_CANON_LOCK.md and CANON_LOCKS.json. Use the exact source image as reference, never memory alone. Any new output is provisional until actual image comparison and owner signoff; protect both source-image hash and character-specific traits. Continue to use the AETHERFALL sheet hierarchy without copying Vellaris's character details to others. CI proves source integrity, not visual likeness.

## Raw AI sculpt visual-quality appendix — 26 November 2026

Owner-supplied Meshy/raw-sculpt screenshots for Razor, Raven and Vellaris, plus two unassigned candidate designs, are documented in [the screenshot reference seal](RAW_SCULPT_REFERENCE_SEAL_2026-11-26.md) and [SHA-256 register](RAW_SCULPT_REFERENCE_REGISTER_2026-11-26.json). Their intended modelling improvements and 1P/3P performance/animation evidence are specified in [the premium fidelity gate](../art/HIGH_FIDELITY_MODEL_STANDARD.md) and [per-hero work orders](../art/RAW_SCULPT_TO_PRODUCTION_WORK_ORDERS.md). This appendix **does not override CANON_LOCKS.json, alter approved appearance, grant source-archived status, or certify Blender/Godot runtime**; screenshot bytes are stored externally in the documented Library archive until original model/master sources are verified and separately approved.
