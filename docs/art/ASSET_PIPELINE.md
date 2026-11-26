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

## Mandatory raw sculpt → 1P/3P game-ready SOP

Follow [AF-ART-BLENDER-001 — Raw AI sculpt to game-ready model](BLENDER_RAW_SCULPT_TO_GAME_READY.md) for every approved hero, gear or character conversion. It prescribes safe raw-input preservation, metres/ground alignment, pedestal removal, topology and canon-safe symmetry, high-poly → retopo, UV/PBR baking, 1P/3P LOD budgets, rigs, sockets, .glb exports and native Godot verification. The per-asset checklist starts at [BLENDER_HANDOFF_TEMPLATE.json](templates/BLENDER_HANDOFF_TEMPLATE.json); copy it next to the real versioned .blend as `handoff.json` only for a registered character. Run `python3 tools/validate_blender_handoff.py`; the offline structural checker also rejects unsupported PASS/GAME_READY claims. **This is static integrity checking only**: no script can substitute for genuine Blender screenshots, Godot runtime, physical-device tests, source comparison and owner signoff.

**Hardening addendum:** [Native capture and source/approval integrity contract](BLENDER_EVIDENCE_HARDENING.md). A registered character may archive an untouched incoming `.glb` only at `art/blender/characters/<CHR_ID>/raw/`; exported Godot `.glb` files never go under `art/`. Native Blender, Godot and owner proof is required independently of hashes and header checks.
