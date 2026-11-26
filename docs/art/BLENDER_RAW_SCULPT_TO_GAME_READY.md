# AF-ART-BLENDER-001 — Raw AI sculpt → game-ready character

**Project:** AETHERFALL: REALMS COLLIDE (1P + 3P hero shooter)  
**Owner instruction date:** 2026-11-26  
**Authorised executors:** Existing owner-approved Blender art team and S.I.R.E. / HORIZON / GENESIS workflow with actual asset and tool access. This document does **not** create a new agent or grant access.  
**Status:** Production standard / checklist; **not evidence** that any sculpt has been retopologized, exported, or verified in Godot.  
**Work order:** AF-ART-BLENDER-001 — build, validate and hand off source-matched character models, keeping original artwork intact.

This is the mandatory detailed procedure beneath `docs/art/ASSET_PIPELINE.md` and `docs/characters/CHARACTER_WORKFLOW.md`. Follow FIND → PLAN → BUILD → TEST → REPAIR → RETEST → SHOW → HARDEN → PROVE → FINISH. No shortcut or AI render establishes "game-ready" without the real deliverables and tests below.

## 0. PRE-FLIGHT — art and source lock (blocking)

1. Read `AGENTS.md`, `docs/characters/VISUAL_CANON_LOCK.md` and `docs/characters/CANON_LOCKS.json`. Check the exact registered asset ID in `art/asset_registry.json` and its character plan.
2. Inspect the **actual owner-approved master reference**, its SHA-256 and relevant four-angle silhouette/weapon/kit sheet. If the real canonical reference is missing, stop claiming canonical fidelity. Do not invent missing images from memory. New variants are `PROPOSAL_PENDING_OWNER_REVIEW`.
3. Confirm raw sculpt origin, rights/licence, filename, format, byte size and SHA-256. Preserve the untouched input. Separately record the source image versus AI-generated geometry; one is not proof of the other.
4. Agree character-specific height, posture, weapon handling, target Godot build/renderer, 1P/3P poly/texture budgets and essential camera distances. The ranges below are **starting budgets**, not universal pass thresholds.
5. Start a handoff from `docs/art/templates/BLENDER_HANDOFF_TEMPLATE.json`. Record work order, source hash, author/tool versions, real test results and blockers. Do not mark `PASS` until tested.

**STOP** if canonical visual identity, hero variant, asset ownership or model provenance is unresolved. Preserve original character identities; do not silently choose between conflicting Korvex/Corvex or Razor/Raven references. ThornDell is intentionally asymmetric: never blindly mirror its unique antlers or Root Bulwark.

## 1. IMPORT, SCALE & REMOVE PEDESTAL

- Save a **versioned copy** of the raw file as the working `.blend` under `art/blender/characters/<CHR_ID>/` before destructive edits. Keep the untouched source in `RawSource` and a working duplicate in `Working`. Suggested collection layout: `Reference`, `RawSource`, `HighPoly`, `GameMesh_3P`, `ViewModel_1P`, `Rig`, `Weapons`, `LOD` and `Evidence`.
- Blender: **File → Import** `glTF 2.0 (.glb/.gltf)`, `FBX` or `Wavefront (.obj)` as appropriate. An OBJ does **not** contain a usable animation/rig handoff by itself.
- Set **Scene Properties → Units → Metric**, Unit Scale `1.0` (1 Blender unit = 1 metre). Align the feet/ground-contact reference to Z=0; confirm +Z up and the agreed engine-facing orientation (existing repo baseline: -Y forward in Blender). For ordinary humanoids, ~1.8–2.2 m is a provisional range; preserve intended giant, quadruped, flying or crouched proportions.
- Select the display base only if it is a **separate connected component**: Edit Mode (`Tab`), hover over base, `L` (Select Linked), `X → Faces`. Inspect selection before deletion; if joined to feet/boots, separate safely with manual topology work instead. Never delete canonical props as "pedestal".
- Split distinct weapons/gear with `L` then `P → Selection` in Edit Mode, preserving original pivots, rig attachments and material assignments. Keep gameplay weapons as separately exported `WPN_...` assets where required.
- Return from Edit Mode with `Tab`. In **Object Mode**, apply Rotation & Scale (`Ctrl+A → Rotation & Scale`) on suitable **unrigged** working objects after checking negative scales, modifiers and parent relations. Do **not** apply Location to every individual sub-object: this can move origins/pivots; only zero the intended root deliberately. Never indiscriminately apply transforms after animation/constraint setup.
- **Gate 1:** Save native viewport evidence of scale/grounding, clean hierarchy and preserved props. Confirm untouched raw/source hash is unchanged.

## 2. MESH REPAIR & SAFE SYMMETRY

- On a working duplicate, inspect topology in Edit Mode: **Select → Select All by Trait → Non Manifold**; identify holes, internal faces, doubled vertices, zero-area faces, flipped winding, disconnected material scraps and self-intersections. Some open cloth/shell surfaces are intentional; **do not auto-fill every boundary**.
- Select the relevant geometry (`A`), recalculate normals outside (`Shift+N`), and inspect **Viewport Overlays → Face Orientation** (blue outward / red flipped). Check both sides of open and mirrored shells.
- Remove actual internal debris, fix winding, merge accidental duplicates at a controlled tolerance and verify shading. Retain authored hard edges, cloth thickness, wing membranes and special silhouettes.
- Use **Mesh → Symmetrize** about X=0 **only** on elements confirmed to be bilaterally symmetrical in the approved reference. Keep asymmetric hair, armour, antlers, scars, cape shapes, gear and weapons untouched.
- **Gate 2:** Record actual manifold/non-manifold findings, corrected faults, intentionally open surfaces, symmetry exceptions and before/after screenshots.

## 3. HIGH-POLY BAKE SOURCE & GAME-READY QUAD RETOPO

- Duplicate/preserve the sculpt as `<AssetID>_HighPoly`, hide it inside `HighPoly` and never decimate the sole bake source.
- Build `<AssetID>_GameMesh_3P` with quad-dominant, deformation-friendly topology. Use Face snap / Project Individual Elements and **In Front** overlay if helpful; do not mistake automatic remesh for final joint topology.
- Create controlled loops around shoulders, elbows, wrists, hips, knees, ankles, jaw/face and other moving joints. Follow creature-specific bend axes (e.g. all four Razor legs, tails, wings, tendrils) rather than forcing humanoid geometry. Use appropriate hard-surface edges for armour, weapons and sharp silhouettes.
- **Provisional budgets:** third-person hero **40k–70k triangles total**; first-person arms/viewmodel **20k–35k triangles total**; plan weapons/attachments separately and record whether totals include them. Count **evaluated/exported triangles**, not Blender quad faces. Tighten budgets using real on-device performance measurements, hero size and visibility.
- Create distinct `ViewModel_1P` geometry/visibility as needed for camera-safe hands, sleeves, effects and weapon; do not simply clip the 3P mesh into the camera. Match proportions, costume details, materials and skin weights to the approved 3P identity.
- Create and test LOD1/LOD2 from 3P silhouette priorities. Possible starting targets are around 50–60% / 20–30% of LOD0 triangles, **subject to actual in-game visual review**, and never at the expense of hero readability.
- **Gate 3:** Record triangle counts per object and 1P/3P/LOD, bone-dependent edge-loop review, silhouette comparison and deformation test evidence.

## 4. UVs & PBR TEXTURE BAKING

- Mark seams on protected/natural boundaries (`Ctrl+E → Mark Seam`), unwrap (`U → Unwrap`), check stretching/texel density and pack non-overlapping UVs using **UV Editor → UV → Pack Islands**, with mip-safe padding. Shortcut keys depend on editor focus and Blender version: use the menu when in doubt.
- Set the **Cycles** render engine for baking. On **each low-poly target material**, create/select an **Image Texture** node with a correctly sized, writable image. High-poly source object(s) selected **first**, low-poly target **last and active**. Enable `Selected to Active` and tune cage/extrusion or max ray distance on the actual mesh. Bake in pieces to avoid intersecting-armour projection artifacts.
- Bake and inspect **tangent-space Normal**, **Ambient Occlusion**, **Diffuse Color only** (no baked lighting for albedo), **Roughness**, and **Emit** where relevant. Blender's Cycles bake types do **not** provide a direct one-click **Metallic** pass: route the metallic value into an emission shader and bake `Emit`, or author/pack the metallic map separately. Do similarly for other unsupported channel extraction. Retain alpha/transmission/subsurface only when the engine shader genuinely needs them.
- Save textures to physical files with meaningful names. Set **color** textures to sRGB and **data** maps (normal, roughness, metallic, AO) to Non-Color. Validate green-channel convention and normal strength against the **actual Godot import**, not by assumption. Do not assume Blender-only procedural node graphs will export intact.
- Run seam checks, padding/mip checks, texture-size budget and material comparison under neutral and gameplay lighting.
- **Gate 4:** Archive UV layout, bake settings, map filenames/sizes, native Blender inspection and actual shader comparison screenshots. Any unmapped/missing texture blocks promotion.

## 5. RIG, SOCKETS & ENGINE EXPORT

- Rig the intended **rest pose**: a clean humanoid A-pose may use ~30–45° arm drop with relaxed elbows and spread fingers. Use appropriate quadruped, floating or non-human bind poses for those characters; never distort the approved silhouette to force a human preset.
- Add deforming skeleton, sensible twist bones and any control rig (keep export deform-bone hierarchy clean). Name and test attachments: `Hand_R_Weapon`, `Hand_L_Shield` (only for heroes with shields), `Chest_Core_VFX` and `Muzzle_Origin`, adding character-specific equivalents as necessary. Verify socket axis/origin in Godot; Blender empties are **not** guaranteed to become gameplay sockets without tested engine mapping.
- Bind with `Ctrl+P → With Automatic Weights` and then **manually** remove weight bleed into belts, hard armour, cloth, hair and weapon parts. Test shoulder, elbow, finger, hip, knee, foot, jaw, jump/land and gameplay-specific extreme poses. Weight-test against both first-person animations and third-person animation retargeting, not a static A-pose alone.
- Apply safe geometric transforms **before** skinning; do not apply arbitrary transforms to the finished animated armature. Preserve `.blend` source with armatures, Actions, NLA state, UVs, cage/bake source and non-destructive versions.
- Export **glTF 2.0 binary (.glb)** into the correct `game/assets/characters/...` location; export separate `WPN_...` assets as appropriate. FBX is an exception for an explicitly verified downstream requirement, not the default Godot 4 handoff.
- Record export-selected meshes, skin influence policy, animation clips, material paths, axis/scale and Blender/exporter versions. Re-import the **actual export** in a **real Godot 4.x editor** (not just into a generic web GLB preview).
- Verify skeleton/bind pose, skinning, named animation clips, sockets/weapon attachment, lighting/materials, visibility, 1P camera, 3P camera, feet/grounding, LOD behavior, hero silhouette, hitbox alignment, VFX origins and errors. Run animations and gameplay actions with genuine input; static screenshots alone are insufficient.
- **Gate 5:** Preserve exact source and export SHA-256, real Blender four-angle captures, UV/topology/rig evidence, genuine Godot editor/runtime capture and short **unedited** interaction video where feasible.

## Required handoff files / routing

| Output | Location / identity | Truth boundary |
| --- | --- | --- |
| Approved source image + owner approval | `art/concepts/characters/<CHR_ID>/` and canonical source lock | Cannot be substituted by AI guess |
| Untouched sculpt and editable versioned .blend | `art/blender/characters/<CHR_ID>/` | Real source, not a screenshot |
| Textures, bake cages, UVs, normal/PBR maps | Versioned art source and exported engine texture locations | Must load on fresh import |
| 3P and 1P .glb / approved LODs | `game/assets/characters/.../<CHR_ID>/` (repo's matching role path) | GLB exists ≠ model visually verified |
| Weapon/gear GLB where separate | `game/assets/weapons/` | Socket/animation must pass actual runtime tests |
| Handoff checklist (copy template) | Next to versioned source .blend; keep source commit/hash | Checklist ≠ engine evidence |
| Blender/Godot capture, test report, hashes | `evidence/blender/`, `evidence/godot/`, and `evidence/characters/<CHR_ID>/` | Only genuine native captures count |
| Owner-facing Android transfer | Exact existing `AETHERFALL – REALMS COLIDE` phone folder (name as actually present) | Repository or sandbox upload ≠ phone save |

Use versioned filenames; preserve existing `korvex_blockout_v01` and all canonical originals. Do not overwrite old approved work, re-label procedural reconstructions as originals, or copy into guessed phone paths.

## Definition of DONE — all are independently required

- [ ] Exact approved reference, hero ID, permissions and hash verified.
- [ ] Raw sculpt preserved; pedestal/scale/mesh/normal/symmetry audits recorded.
- [ ] Real clean 3P and 1P meshes, usable joints, UVs, LODs and measured budgets.
- [ ] Real normal/AO/albedo/roughness/metallic/emission textures as needed and no missing maps.
- [ ] Skinned clean export skeleton, functional animation clips and tested sockets.
- [ ] Both views/LOD and hero-specific weapons actually inspected in Blender **and Godot 4.x**.
- [ ] Engine/runtime screenshot/video, test results, source revision, SHA-256 and owner visual review recorded.
- [ ] QA failures repaired and retested, no open blocking visual/accessibility/performance defects.

**Failure policy:** A missing source, unusable mesh, failed UV/bake, missing rig, invalid GLB, failed import, visual drift, absent native capture or absent signoff means `NOT_VERIFIED` / `BLOCKED`, never `GAME_READY`. Static documentation validation can verify requirements **only**, not Blender startup, visual fidelity or playable character state.

## Primary technical references

- Blender: [Applying object transforms](https://docs.blender.org/manual/en/latest/scene_layout/object/editing/apply.html), [UV island packing](https://docs.blender.org/manual/en/latest/modeling/meshes/uv/editing.html), [Cycles Selected-to-Active bake](https://docs.blender.org/manual/en/latest/render/cycles/baking.html).
- Godot: [Supported 3D formats](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html), [3D import configuration](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html).

**Current production truth at authoring:** no raw sculpt was attached to this work order; no native Blender, Godot, export or device test was performed. Documenting this standard does not mark any model completed.
