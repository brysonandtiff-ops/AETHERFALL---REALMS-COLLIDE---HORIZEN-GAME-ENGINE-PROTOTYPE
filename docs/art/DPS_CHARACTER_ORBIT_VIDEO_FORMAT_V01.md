# AETHERFALL — DPS character orbit presentation format V01

**Reference authority:** Owner-supplied `40051.mp4` (Temporis) and `40052.mp4` (Symbion), 26 November 2026.  
**Scope:** Character review and presentation videos only. This is **not** gameplay evidence, engine screenshots, an art-lock approval, or a claim that meshes are checked into the repository.

## Frame contract

- Output each character as its **own MP4**: **1280×720, 24 fps, 4.000 seconds, 96 frames**, H.264/yuv420p.
- Use the visual structure from the owner's MP4 references: gothic-black/plum canvas, thin bright magenta/purple framing, AETHERFALL/REALMS COLLIDE masthead, left **real 360° mesh orbit** on a neon plinth, right named information panel, live CAMERA ANGLE 000° → 356°, four MODEL ELEMENTS and source disclosure footer.
- Wording: `PHASE 01 | DPS BLOCKOUT`, `GENUINE 3D MESH ORBIT`, and `SOURCE GEOMETRY • NOT GAMEPLAY OR ENGINE PROOF`. No false gameplay evidence.
- Generate four actual render stills for 000°, 090°, 180° and 270° to inspect silhouette continuity.
- Preserve each hero's already defined design distinctions and standalone weapon IDs. Do not reuse another hero's locked model or silhouette.
- Camera and lights are presentation aids. Art-direction colours do **not** justify changing any approved canonical assets.

## Character-specific V01 look

| Asset ID | Role and subtitle | Highlights in review presentation | Weapon |
| --- | --- | --- | --- |
| `CHR_Razor` | Melee DPS / THE RIFT REAVER | Crimson & ember, dual talons, asymmetric spined shoulder, red visor | `WPN_Razor_RiftTalons` |
| `CHR_Raven` | Ranged DPS / THE ECLIPSE MARKSMAN | Violet & cyan, hood and beak mask, feather mantle, cyan optic | `WPN_Raven_Nightpiercer` |

## Real V01 artifact evidence (outside this branch)

Video names and SHA-256, reproduced from **the actual exported GLB geometry** using trimesh reimport → VTK 9.6 offline rendering → Pillow info panels → FFmpeg H.264:

| Character | Actual video filename | SHA-256 |
| --- | --- | --- |
| Razor | `Razor_DPS_GLB_mesh_orbit_1280x720.mp4` | `fa9de02d219e8757ce939beb985ae760c2c9da539d1894c0ab12d10f4e` |
| Raven | `Raven_DPS_GLB_mesh_orbit_1280x720.mp4` | `d8f77bedf9bffea437872f386e0f88f7c51380015100f2a870c8a568880975b4` |

- Source character GLBs have SHA-256 `a6d2424ccecb2b805721d080e2a36f52c3bb21c519e42bec81a37987127e2a45` (Razor), `6f69434fa18d00bef7e3c9f039d811bbeb626108741b695ecdef15fe9d6d197e` (Raven).
- The owner-facing downloadable ZIP includes these four original model/weapon GLBs, two MP4s, eight angle stills, renderer script, side-by-side PNG and a checksum manifest.
- Both MP4 files validated with FFprobe as **96 frames, 24/1 fps, 1280×720 and 4.000s duration**; different 000°/180° images visually confirm actual rotation.
- Existing three local blockout integrity tests passed; **no Blender or Godot character import was performed**.

## What still requires acceptance

- Owner approval of actual character appearances (V01 blockouts are not locked character canon).
- Transfer handoff binaries into approved repo folders with matching hashes and reviewed art-storage solution.
- Native Blender source/rig/UV work, real Godot character import, character animations, real gameplay/ability tests, captures and physical-device evidence.

Never call source art a Blender or Godot runtime screenshot. The rendered video is a genuine offline mesh orbit only.
