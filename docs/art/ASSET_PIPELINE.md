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

## Incoming media category policy (2026-11-26)

Composite **character concept/infographic sheets** belong to the character's existing `art/concepts/characters/CHR_*` directory, not `evidence/godot/`. Offline VTK/blockout screenshots, GIFs and MP4s go to `evidence/prototype-previews/` with the exact source tool and verification limits. Owner-photographed role/approval notes go to `docs/characters/owner-notes/` (confirm public-release permissions first). The source upload's extension must match the actual file signature; do not recode or crop without logging a derivative. Track checksum, size, approval scope and `pending_binary_checkin` versus `checked_in` separately. See [intake catalogue](INTAKE_2026-11-26.md).
