# Support Phase 01 — actual proxy geometry and Vellaris reference handoff

**Project:** AETHERFALL: REALMS COLLIDE | **Date:** 2026-11-26 | **Status:** Owner review, not canon lock or game build.

Two 3D **procedural prototype meshes** and their real rotating VTK renders were created in the local render environment. A zipped pack containing `.glb`, `.mp4`, views, source Python, original user image references, README and integrity manifest was delivered in the owner conversation as `AETHERFALL_SUPPORT_BLOCKOUTS_PHASE01_ALL_FILES_v01.zip`. **None of those binary artifacts is committed to this repository.**

| Artifact | Verified identity / SHA-256 |
|---|---|
| `CHR_Temporis_Blockout_v01.glb` | 90 named parts / 21,286 triangles; `a92b63d27d1e620852d13226347dbe4316976166fcb50ab4b0683653ac883b58` |
| `CHR_Symbion_Blockout_v01.glb` | 81 named parts / 18,724 triangles; `75ea9e31980f0aaccd61d268b7bfbed79febe29190b9175adc5737d284dfc809` |
| `CHR_Temporis_360_Blockout_v01.mp4` | Real 3D proxy turntable, 1280×720 24fps 96 frames / 4s; `fc814372edc5dad218087d2ffdc37df8bb347a96c5e57afcabe4d46ff6c6cd48` |
| `CHR_Symbion_360_Blockout_v01.mp4` | Real 3D proxy turntable, 1280×720 24fps 96 frames / 4s; `727571e1d928da22bf09e56663fec56c12892a66f7c7de1d34b311243bef0306` |
| `CHR_Vellaris_Bloodshield_Concept_View_Turnaround.mp4` | **Concept-only 2D image-view cycle**, 1280×720 24fps 120 frames / 5s, **not a 3D rotation**; `bf5578b6d8c334ab8a333c831bc4f7d8113feaadc2778246c0a745da7035e62f` |
| `CHR_Temporis_Blockout_Infographic_v01.png` | 4 real mesh view renders; `4838d953d7536992cb2c1cf4649665c53048f3e9ee575a8293ceef47a56de52d` |
| `CHR_Symbion_Blockout_Infographic_v01.png` | 4 real mesh view renders; `2b23b1c59dd0f0f6ff054d77522e6ba91205defddf11f0f4eb03a29af722b5f0` |

**Provenance:** User support source `39397.png` SHA256 `886e712d196f61e7c59faf20a1f94cd314e42f7455d4a74212149b4cca738021`; user *existing Vellaris* sheet `39403.png` SHA256 `4d100d50cf0769da47cbe1b782deeb842d15a11c1c46a08f8bd5bd090fa34939`. Vellaris model `.blend` or `.glb` was not available in connected AETHERFALL source or accessible uploaded files; no substitute Vellaris design was generated.

**Real verification:** exported `.glb` files loaded and triangulations inspected; glTF mesh axes converted to +Y up, −Z forward; all three H.264 MP4s fully decoded without warnings using FFmpeg; VTK 9.6.2 was used to render actual rotating proxy geometry for the two supports.

**Explicitly not verified:** Blender native `.blend` scenes/rigs, Godot 4 native import, actual gameplay, devices, controllers, balance, live footage, visual approval, or release readiness. Existing `reserved_no_source` asset registry states remain unchanged because assets are not yet staged/validated in Git.

**Review/import gates:** (1) owner reviews silhouettes; (2) archive approved art and local delivered GLBs under their existing character paths without overwriting canonical art; (3) review imported Godot model orientation, scale, materials and collision in a real runner; (4) record native screenshots/video and source hash; (5) update registry through separate approved changes. Never present proxy turntables as engine evidence.
