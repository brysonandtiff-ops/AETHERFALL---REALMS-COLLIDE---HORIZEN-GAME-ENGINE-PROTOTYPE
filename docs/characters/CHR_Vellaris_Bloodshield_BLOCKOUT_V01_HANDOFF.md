# CHR_Vellaris_Bloodshield — 3D proxy blockout V01 handoff

**Project:** AETHERFALL: REALMS COLLIDE  
**Work order:** Produce a genuine 3D rotating Vellaris Bloodshield proxy from the *existing*, owner-approved 2D concept reference; protect the approved visual identity.  
**Executor:** Connected, local Python + trimesh + VTK software renderer and FFmpeg. No external native Godot/Blender execution was performed.  
**Stage:** Actual GLB geometry and authentic orbit media delivered in owner conversation, **PENDING OWNER REVIEW**; not the original model or final art.  
**Date:** 2026-11-26.

## FIND — source-of-truth and preservation

- Approved source: owner-provided `39403.png` / `reference_original_approved_Vellaris_39403.png`, unchanged original SHA-256 `4d100d50cf0769da47cbe1b782deeb842d15a11c1c46a08f8bd5bd090fa34939`.
- User-provided `40055.mp4` is a **2D reference-view sequence**, not the requested genuine rotating mesh.
- Source 3D Vellaris `.blend` or `.glb` was not available in accessible repository files. A **new proxy mesh** was generated from the existing concept. No canonical original was replaced or deleted.

## BUILD — genuine, downloadable proxy deliverables

The following generated artifacts are in the owner conversation download `AETHERFALL_VELLARIS_BLOODSHIELD_3D_BLOCKOUT_V01_ALL_FILES.zip`. These binary assets are **not checked into this branch**; keep asset registry truthful until a subsequent reviewed import.

| Artifact | Verification and SHA-256 |
|---|---|
| `CHR_Vellaris_Bloodshield_Blockout_v01.glb` | Real 238-part / **28,658-triangle** geometry; provisional GLB +Y-up, -Z-forward, **1.9803-meter** height; SHA256 `e2997e3c2ead6503c15c35c9ae07cb91a4c6c3ffaf741c32cf67c12f933be76a` |
| `WPN_Vellaris_Bloodshield_Blockout_v01.glb` | Independent 20-part / **772-triangle** optional proxy shield, ~1.0074 m; SHA256 `f962b6939039edfd3e10f9f14024e5d31d7d388ade4dd11129fd489f02c19231` |
| `CHR_Vellaris_Bloodshield_360_Blockout_v01.mp4` | Genuine VTK 3D orbit, **96 frames / 24 fps / 4 s / 1280 × 720**; SHA256 `a68ac495d8019631ee5f9bdbe7480708b41a5cfb2d048c82e0fbb76adda6f329` |
| `CHR_Vellaris_Bloodshield_Blockout_Infographic_v01.png` | Four actual geometry views, titled and annotated; SHA256 `042f5021da99485d1f5a2afab298367fd4588ef40f73f333d5a02a198b985f79` |
| Complete ZIP | Original source references, two GLBs, MP4, GIF, four rendered views, comparison image, generator source, local verification tests and SHA manifest. SHA256 `1962de45bf027639c1f96538afa1a3a83f188d95905ccf5385373d736bac1c71` |

## TEST / SHOW — scope

The included `verify_bundle.py` passes **10/10 static-media checks**: GLB parse, finite triangles, part counts, provisional height, optional shield, full H.264 decode, exact 96-frame video metadata, actual viewport motion difference between frame 0 and frame 48, four-angle screenshots, and original source image checksum retention.

The MP4 and screenshots are from **actual rendered proxy geometry in VTK**, **not** a simulated Godot or Blender build. Full source generator and verification report are supplied in the separate downloadable ZIP.

## Art boundaries, next gates and acceptance

1. Owner compares the source art to V01 model in `CHR_Vellaris_Bloodshield_Canon_Comparison_v01.png`. First-pass face/hair/cloak/armour proportions are *not* claimed to reproduce every approved detail exactly.
2. Owner accepts the visual adaptation or requests corrections. Do not silently promote this proxy to the existing canonical Vellaris visual master.
3. After review, stage original concept reference under `art/concepts/characters/CHR_Vellaris_Bloodshield/`, independently authored native Blender files under `art/blender/characters/CHR_Vellaris_Bloodshield/` **only when they exist**, and verified runtime GLB under `game/assets/characters/heroes/CHR_Vellaris_Bloodshield/`. Store optional shield separately at `game/assets/weapons/WPN_Vellaris_Bloodshield/`.
4. Actually import/test in Blender and **Godot 4.x**: proportions, shaders/materials, normals, skeleton/animation, collisions, camera, controls, FPS, gamepad and asset performance. Capture genuine Blender/Godot screenshots and unedited footage, with engine/device identifiers and source commit. These checks are **NOT RUN**.
5. Keep `art/asset_registry.json` status as `reserved_no_source` until actual reviewed files are present and properly verified in the repo. No gameplay, native character rig, release, device test or archived repo binaries are claimed.

Follow `AGENTS.md`, `docs/art/ASSET_PIPELINE.md`, `docs/evidence/PROOF_REQUIREMENTS.md` and approved S.I.R.E. production governance. This handoff changes no approved game art.
