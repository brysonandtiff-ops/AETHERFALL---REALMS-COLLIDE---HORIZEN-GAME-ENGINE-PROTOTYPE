# AETHERFALL — Concept-to-game art pipeline

1. **Reference / concept:** Save owner-approved, rights-cleared source sheets under `art/concepts/`; record which version is canonical. Do not substitute or edit approved art without permission.
2. **Blender source:** Save editable models in `art/blender/` using the asset ID; preserve iterations, armatures, UVs, materials, actions and mesh names.
3. **Scale and orientation:** Use metric units, unit scale 1.0, +Z up and -Y forward in Blender. Confirm the final orientation and scale after importing into Godot.
4. **Export:** Export a separate `.glb` into the corresponding `game/assets/` folder. Preserve source `.blend`; do not overwrite it with GLB output. Weapon assets stay separate from characters.
5. **Import:** Fresh import in actual Godot 4.x; check scale, vertex normals, material slots, textures, rig and animation clips, foot placement, and missing dependencies.
6. **Evidence:** Native Blender render/capture of front, side, back and 3/4 views; mesh/topology and animation checks; native Godot screenshots and unedited video of clips/gameplay when applicable. Record exact source commit and hashes.

## Naming

- Characters: `CHR_<Name>`; weapons: `WPN_<Name>`; realms: `LVL_<Name>`; animation clips use stable descriptive names.
- Keep original source and approval/reference notes distinct from exported engine files.
- Per-asset manifests may record mesh triangles, LODs, material maps, skeleton, clips, export settings, Godot version and hashes. Empty folders do NOT count as validated assets.

## Large files

Binary `.blend`, `.glb`, textures and audio remain binary. Git LFS is not enabled here. Before committing large art, agree storage limits and enable an approved approach to prevent expensive repository growth.

## Mandatory hero-sheet intake

Follow `docs/characters/CHARACTER_WORKFLOW.md` and keep `docs/characters/plans/<ID>.json` updated. All characters require Vellaris-grade completeness (turnaround, silhouettes, expressions, palettes/materials, unique weapon/focus, gameplay, kit, technical and accessibility handoff) plus per-stage proof. Her bloodshield design is unique to her; **do not give every tank a shield**. An uploaded chat image does not satisfy the source-archival gate until the exact binary is committed and hashed.

## Reference-locked art pipeline

Honor docs/characters/CANON_LOCKS.json and VISUAL_CANON_LOCK.md. Preserve exact master source bytes/MIME and owner-approved face, silhouette, palette, weapon and kit. Use Vellaris branded infographic layout but not her personal shield/appearance on other heroes. ThornDell must preserve antlers, green venom and Root Bulwark. No character image becomes canon without source-to-output owner review. Never claim a generated reference is native Blender/Godot evidence.

## Master visual style stop gate — effective 2026-11-26

**Before creating ANY new hero image, turntable, concept infographic or variant**, follow `docs/art/MASTER_ART_STYLE_LOCK.md` and its pinned machine-readable `ART_STYLE_LOCK.json`. The Vellaris (`39403.png`) and Korvex (`39412.png`) 4:3 character boards are the owner-designated **presentation style** references; the older NEXUSFALL roster screenshot (`39401.jpg`) is **only** a roster-layout/role-coding inspiration. All three uploads contain WebP bytes regardless of their misleading filename suffixes. Do not import their names or branding as AETHERFALL canon.

Use `python3 tools/verify_art_style_contract.py` as a **hard source metadata gate**, in addition to the preexisting character identity validator. Declare `FULL_CHARACTER_INFOGRAPHIC`, `BLACK_BACKGROUND_HERO_KEY_ART` or `3D_BLOCKOUT_EVIDENCE` explicitly in proposal sidecars. Full sheets require all 11 sections and 4:3 1536×1152+; black-background key art is *not* a substitute. Any visual art acceptance still requires actual image comparisons and the owner's approval; scripts and status checkboxes cannot certify aesthetic fidelity.
