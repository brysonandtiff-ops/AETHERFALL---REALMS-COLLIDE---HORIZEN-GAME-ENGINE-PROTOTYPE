# AETHERFALL — Concept-to-game art pipeline

**MANDATORY DESIGN-FIRST GATE — SIRE-ART-INFO-001:** Before a newly planned visual asset can be approved for production, prepare an appropriate infographic development board and an accompanying text/JSON plan. Follow [the universal AETHERFALL infographic standard](UNIVERSAL_INFOGRAPHIC_STANDARD.md), the [machine-readable category policy](INFOGRAPHIC_POLICY.json) and the [per-asset plan template](INFOGRAPHIC_PLAN_TEMPLATE.json). All characters, weapons, levels, props, buildings, creatures, vehicles, environments and UI are covered. Use the Vellaris example's presentation grid, not its character design. Archive exact original sources and require owner review; no generated board counts as native engine proof. Historic assets do not become unfinished solely because they lack a new board; index them separately before further production changes.

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
