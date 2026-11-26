# Razor & Raven — the first AETHERFALL DPS hero blockouts (V0.1)
**Project:** AETHERFALL: REALMS COLLIDE
**Requested:** 26 November 2026.
**Work-order scope:** Two original, readable DPS character models and distinct weapons; do not override Vellaris, ThornDell or Korvex art.
**Executor:** ChatGPT, local offline Python/trimesh and VTK.
**Status:** REVIEW BLOCKOUT — not locked canon, not a native Blender model, not verified in Godot.
**Repository status:** art/razor-raven-dps-review-20261126 — TEXT-ONLY RECORD, no GLB files checked in.

## Core visual rules
- Keep the broader team's gothic fantasy / supernatural armour language, but give each hero a strongly distinctive play silhouette and weapon.
- No shields; no tank-like armour bulk, turret armour or copied Korvex/Vellaris/ThornDell parts.
- Real model scale in metres, Blender +Z up / -Y front. Visor and elemental accents aid role readability, not final texturing.
- Concept choices await owner approval before final materials, rigging, animation or art lock.

## Razor — dual Rift Talons / melee DPS
**ID:** `CHR_Razor`; weapons `WPN_Razor_RiftTalons`.
- Lean, athletic, forward-combat V torso; spined **asymmetrical** shoulders; scarred, pronged visor helm.
- Twin forearm-mounted **hooked rift blades**, reaching down/outward. Red energy slit and sparing aged-brass attachments.
- Palette: graphite / iron / bone-edge / ember crimson. Separate blade objects for rigging later.
- Proposed kit only: Rift Lunge, Chain Carve, Bloodline Mark, Execution Arc. None implemented.
- Clear danger language: razor-edged light armour, not a shield or walking fortress.

## Raven — the Eclipse Marksman / ranged DPS
**ID:** `CHR_Raven`; weapon `WPN_Raven_Nightpiercer`.
- Slender upright hood, **beak half-mask**, cyan slit visor and a wearable **left-side split feather mantle**; right shoulder remains spare.
- Long asymmetric dark precision rifle with spectral cell and blade-like muzzle.
- Palette: charcoal / indigo / pale steel, violet feather accents, cyan optics.
- Proposed kit only: Eclipse Mark, Piercing Shot, Featherstep, Nightfall Round. None implemented.
- Historical Shadowspire "Raven Sharpshooter" was a concept candidate, **not a playable model or pre-existing AETHERFALL canon**.

## V0.1 exports produced outside the GitHub repository
These actual geometry files and their real rendered previews were delivered as a downloadable ZIP in the conversation, not committed to this text-only review branch. Do not claim them as installed into Godot.

| Model | Mesh parts | Triangles | SHA-256 |
| --- | ---: | ---: | --- |
| `CHR_Razor_blockout_v01.glb` | 56 parts | 1,144 | `a6d2424ccecb2b805721d080e2a36f52c3bb21c519e42bec81a37987127e2a45` |
| `WPN_Razor_RiftTalons_pair_blockout_v01.glb` | 12 parts | 172 | `75c1b2555ddbce253e9dd3d88f9f9269e77d46f300b3d077d75e79c5b95aaa62` |
| `CHR_Raven_blockout_v01.glb` | 61 parts | 1,280 | `6f69434fa18d00bef7e3c9f039d811bbeb626108741b695ecdef15fe9d6d197e` |
| `WPN_Raven_Nightpiercer_blockout_v01.glb` | 13 parts | 138 | `e45a731a2c3969dc8110a0cb2fd3a17bf08f8fd3d86fada24edf0b66bda8f08c` |

**Verified offline:** All four GLBs exported and re-imported with exact part/triangle counts, expected bounds, watertight component meshes and original vertex colours; comparison/four-view PNGs and a turntable MP4 rendered using VTK 9.6 from the actual exported GLB objects; local Python integrity tests 3/3 PASS.

**NOT VERIFIED:** Blender startup, a saved native `.blend`, production-ready topology/UVs/armatures/animations, imported characters in Godot 4.x, playable damage or controls, physical devices, true FPS or capture in the game. The VTK preview is not equivalent to native Blender/Godot screenshots or game footage.

## Next owner and production gates
1. Owner reviews the four-angle silhouettes and confirms or revises this provisional art direction.
2. Add unchanged GLB bytes from owner handoff to `game/assets/characters/heroes/CHR_Razor`, `CHR_Raven` and the corresponding `game/assets/weapons` folders; record hashes. Store original generator and later Blender source in `art/blender`, not `game`.
3. Import in **real Blender**, fix topology/UVs, separate weapon meshes, bind skeleton and animation, save a versioned `.blend`.
4. Re-import actual files in Godot and capture four native views, motion/gameplay, collision, timings and regression tests.
5. Only promote registry status after the repo validator / evidence policy explicitly supports it. Never call a conceptual model playable.

No merges, approved-canon overrides or production release from this proposal.
