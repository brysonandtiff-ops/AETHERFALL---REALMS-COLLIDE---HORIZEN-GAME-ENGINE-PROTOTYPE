# AETHERFALL — Concrete Blender/gameplay work orders from the new raw sculpt refs

Work order group `AF-SCULPT-QUALITY-001` · staged for review. The **raw Meshy GLBs have not been supplied here**. Do not treat the screenshots as editable 3D sources. Executor: existing authorised Blender Art Team and Game AI/Gameplay Engineering teams working under S.I.R.E. / AXIOM G.A.I.S. and the current repo's `AGENTS.md`.

## Shared preflight (all tasks)

- [ ] Read `docs/characters/CANON_LOCKS.json` and `VISUAL_CANON_LOCK.md`. Hash and inspect exact approved canonical source **before** working on any approved hero.
- [ ] Verify rights to use raw Meshy model; obtain actual `.glb`/`.fbx`/`.obj` + PBR source textures, platform usage permissions, original screenshots, generator version and raw SHA-256. Preserve unmodified import outside runtime and outside `art/` `.glb` paths; derive Blender source in `art/blender/`.
- [ ] Inspect the raw file in Blender with 4 real views, actual triangle/vertex/material/UV/object counts, nonmanifold and wrong-normal reports; compare screenshot's reported values with mesh readback.
- [ ] Duplicate raw source to working scene. Delete/separate display base **from export only**; maintain raw archive. Split capes/feathers/hair/chain/weapon/glyph/corvid/etc into intentional objects.
- [ ] Put humanoid into A-pose (or approved neutral), creature into quadruped neutral with clear hip/scapula/neck/jaw gaps. Restore symmetry only where canonical; never destroy a deliberate asymmetric silhouette.
- [ ] Retopo deforming anatomy to clear quad edge loops; high-poly bake and low-poly UV/PBR, weighted skeleton/shape keys, 1P viewmodel, 3P mesh and LODs. No direct 2M+ triangle raw asset in standard gameplay.
- [ ] Validate Blender four-angle 0°/90°/180°/270° raw render; real native animation stress clip and independent GLB parser readback; Godot 4.7.2 scene/animation/ability video only when run.

## AF-CHAR-RAZOR-001 — Razor (quadrupedal DPS), highest raw mesh density

**Reference:** `40149.jpg` (colored quadruped), `40151.jpg` (Meshy UI stats); registered `CHR_Razor` only when full character intake/owner identity accepted. **Screenshot-reported:** ~2.46M triangular faces, ~1.23M verts, pending raw mesh verification.

**Art implementation:** Keep bleached skull and layered spinal ribs, dark inner body, red fissures, hooked silhouette and long tapering tail. Build separate `GEO_Head_Jaw`, `GEO_Spine_Plates`, `GEO_Limbs_Front`, `GEO_Limbs_Back`, `GEO_Tail`, `GEO_Claws`, `WPN_Razor_ChainHarpoon` and prop/FX sockets. Rebuild bite jaw hinge; preserve horn plate shapes through low-poly bake. Detach round display disc and non-physical emissive splines. Target ~40–70k 3P LOD0 subject to camera/console/mobile profiling; do not assume from source screenshot.

**Rig/gameplay:** Real four-leg plant and ground IK, spine and tail chain, jaw open, chain throw/pull, sprint, leap, land and recovery. `SOCK_Jaw_Chain`, `SOCK_Claw_L/R`, `SOCK_Spine_VFX`, `SOCK_Head_Camera`. Make chain collision/ability hitbox explicit separate from mesh. Server-authoritative pounce, drag and bite; prevent teleport across blocked cover. First-person local jaw/forelegs and projectile alignment can be a separate reduced viewmodel (do not render massive back spines over reticle).

**Acceptance:** true quad locomotion and grounded feet, four-angle original-to-final comparison, detached chain, no stretched spine on bend, visible kill/drag telegraphs, tested 1P and 3P camera/hit fairness, exported GLB/touch/engine proof.

## AF-CHAR-RAVEN-001 — Raven (Echo Weaver / owner-confirmed variant pending)

**Reference:** `40174.jpg` and `40166.jpg`; screen is a rich statue-style sculpt, NOT motion proof. Preserve purple feather silhouette, silver hair, hood, shoulder raven and omen spell glyph; do not silently resolve Echo Weaver vs alternate wormhole-sniper weapon/kit without the owner's actual locked brief.

**Art implementation:** `GEO_Head_Face`, `GEO_Hood`, `GEO_Hair`, `GEO_Cape_Feather_Layers`, `GEO_Armor`, `GEO_Gauntlets`, `COMP_Corvid`, `WPN_Raven_OmenFocus` (if confirmed). Keep broad raven feather read; separate feathers by anchor regions or controlled cards/shells, not millions of individually simulated fragments. Split floor display base as optional prop. Build face controls and hands in A-pose without changing approved head and hairline.

**Rig/gameplay:** Feather chain anchors and limited physics; rigid shoulder corvid socket with separate flight rig, low-cost simulation; cloth stop before 1P arms; distinguish visible 3P omen VFX from hitbox. Aim/cast/teleport tests without feather arm intersection; generate 1P hands/focus/reticle-safe cast FX and low-latency projectile alignment.

**Acceptance:** match exact portrait and feather tiers from owner ref across four angles, capture feather side-view motion while sprinting, arm raise and cast; actual Godot render/LOD and 1P/3P UI contrast; no fictitious canonical weapon adoption.

## AF-CHAR-VELLARIS-001 — Vellaris (Bloodshield Tank)

**Reference:** `40136.jpg` colored newer preview; `40132.jpg` grey preview. These are secondary sculpt quality directions. Canon is the existing exact `39403.png` actually WebP, SHA-256 recorded in `CANON_LOCKS.json`. Do not substitute a screenshot model face for original.

**Art implementation:** Keep approved regal face, red eyes, pointed ears, pale lavender flowing hair, **large red enamel multi-layer armour**, polished antique gold trim, split cape and stand-alone `WPN_Vellaris_Bloodshield` even though the screenshot **does not show it**. Detach pedestal from exported character. Model clear shoulder pivots and cloth rest pose; sculpt fingernails, glove plates and shield grip/attachment.

**Rig/gameplay:** Facial blend shapes, hair/cape joints, layered shoulder clearance, blood magic sockets `SOCK_Weapon_Hand_L`, `SOCK_Weapon_Hand_R`, `SOCK_Barrier_Origin`, `SOCK_Aura_Ground`, `SOCK_Chest_Core`. Game damage direction/mitigation must not depend on rendered shield geometry; 1P close-up bloodshield and cast hands remain separate from 3P body.

**Acceptance:** mandatory exact approved screenshot side-by-side, original Bloodshield present, no generic replacement face, no clipping while raising arms or shield, 1P shield occupancy test, grounded boots, genuine Blender/Godot view/animation evidence.

## Unassigned-sculpt holding order

`40168.jpg` and `40170.jpg` are held as **two distinct unnamed model directions**. Archive exactly; do not create `CHR_...` IDs, names, kits, source promotions or infer which hero they belong to. If named later, start the normal character intake and record a new owner-approved canon delta.

## Evidence and finish

Required per hero: raw source SHA, screenshot refs+hashes, designer approval record, low-poly/UV/topology/rig reports, three LODs, first-person and third-person render tests, real Blender orthographic PNGs, an uncut demonstration of every requested animation, independent `.glb` re-import, actual Godot 4.7.2 import/ability test and device performance evidence. Record what failed and repaired; do not call a generated image or software projection an engine render.

**Current status:** completed task specification, not completed native modelling. All production native/runtime fields begin `BLOCKED/NOT_RUN` until verified.