# AETHERFALL: REALMS COLLIDE — 1P + 3P character-to-combat production standard

**Work order:** AF-PIPELINE-3D-COMBAT-001 · **Version:** 0.1.0 · **Created:** 2026-11-26 (Australia/Perth)
**Project:** `brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE`
**Goal:** Turn authorised concept and dense AI/Meshy sculpts into inspectable, animatable hero assets and fair, readable 1P/3P combat integrations, without altering visual canon.
**Authorised executor:** Existing S.I.R.E. / AXIOM G.A.I.S. governance, HORIZON game execution and approved Blender / Gameplay engineering workers. This document does **not** create new agents, credentials or background workers.
**Current status:** SPECIFICATION_AND_OFFLINE_CHECKER_ONLY. No new hero has passed native Blender/engine/gameplay gates by this work order.
**Finish criterion:** exact-owner-source-verified model + native 4-view renders + retopo/UV/PBR + skin/animation/IK + exported GLB + independently parsed GLB + actual Godot 4.7.2 character import + 1P/3P combat/AI and device runs + signed stage receipts + separate owner/platform release gates.

## Authority and no-drift precedence

Read `AGENTS.md`, `docs/characters/VISUAL_CANON_LOCK.md`, `docs/characters/CANON_LOCKS.json`, `docs/characters/CHARACTER_WORKFLOW.md`, `docs/art/ASSET_PIPELINE.md`, `art/asset_registry.json` **before asset work**. Unavailable exact owner artwork = STOP claiming canon-fidelity, even if a prompt or screenshot looks similar. A dense AI source mesh is an **input proposal**, never an approved output or an engine-ready character. Preserve its unmodified bytes, provenance, licence and SHA-256. Generated retopology/variants require an original-to-candidate comparison and explicit owner sign-off.

In particular `CHR_ThornDell` is the current registry ID (not silently `CHR_Thorndell`), `CHR_Korvex` and `CHR_Corvex` have an unresolved collision hold, and Razor/Raven concepts/weapon variants have outstanding intake conflicts; **none are silently resolved here**. Two source images are pinned in current canonical locks but not yet committed to GitHub. Do not treat previously produced offline GLBs/VTK renders as native Blender or Godot proof.

## Two coordinated specialist work orders, one evidence ledger

| Team | Owns | Must hand off to | Gate that blocks promotion |
|---|---|---|---|
| Blender Art | Approved concept → separated neutral source → retopo/UV/PBR → deform rig → 1P viewmodel → GLB | Gameplay engineer: fixed asset IDs, measured dimensions, bone/clip/socket/material names, real evidence | Missing exact approved source, failed normal/UV/weights/rig/4-view checks, unsafe export |
| Game AI & Gameplay | Controller/camera → locomotion/AI → abilities → server authority → projectile/hurtboxes → 1P/3P render and effects | Art: missing animations, telegraphs, socket positioning and clipping reports | Code cannot compile, authoritative rules differ per camera, failed hit/LOS/lag/accessibility tests |
| S.I.R.E. sovereign verifier | Source identity, provenance, staged SHA-256 manifest, independently signed receipts, no-promotion decision | Owner + downstream platform holder | Missing native proof, independent signature, source identity or owner/mobile acceptance |

**Shared iteration:** art and gameplay can iterate in parallel on placeholders; placeholders never replace locked masters. All gameplay changes are committed/reviewed against one source SHA. A changed source or approved art invalidates affected downstream receipts.

## Mandatory phase progression (S.I.R.E. LAW-108)

1. Concept art: exact master ID and rights/source sign-off.
2. Level blueprint: camera sightlines, spawn/nav/collision and objectives documented.
3. S.I.R.E. kernel/rules: engine pinned, performance/security/authority/LOD targets agreed.
4. 3D modelling: editable mesh + real native **0°/90°/180°/270°** screenshot set, source hash and true topology report for **every** 3D model, including weapons.
5. UV & PBR: distinct UV0 unwrap, bake/material maps and genuine material/texture inspection.
6. Rig & GLB seal: weights/poses/clips/1P viewmodel, reproducible export hash + independent GLB parser; real Blender and import/animation evidence.
7. Greybox: actual match space, collision shapes, camera volumes, navigation data and objective rules.
8. Mechanics/GDScript: actual compiled state machines, input map, abilities, bots and test interactions.
9. Asset integration: clean Godot import, skeleton, clips, VFX/audio, sockets, 1P/3P switches and interaction.
10. Lighting/VFX: real game-window captures, frame-time evidence, colour/readability and graceful fallbacks.
11. HUD/telemetry: accessible UI, controller and real-owner-phone input/indicators.
12. Gold candidate: source-exact end-to-end playthrough, multiplayer, security, save/reconnect/recovery, hashes, independently signed review. **This does not grant platform distribution approval.**

Stage 4's four views must come from real native 3D source and be distinct, nonblank and source-matched. Stage 6 requires a genuine independent GLB re-import. No fake/synthetic screenshots or test fixtures can meet production proof. The S.I.R.E. SIRE-LAW-108 policy currently describes a proposed/draft adoption; do not assert it is already an enforced production service.

## Asset-to-combat handshake

An asset is **Handoff-ready**, not game-ready, when all these are true:

- Character and all unique props have stable IDs, owner reference hash + character plan, and no pending identity conflict.
- Matching 3P `CHR_*` and 1P `VM_*` identifiers, neutral rig poses, verified armature remap and non-colliding meshes.
- `Skeleton3D`, `AnimationPlayer`/`AnimationTree` conventions, clip list, expected state animations, gameplay frame events and VFX socket local transforms documented.
- Mesh, capsule and hurtbox extents measured (not inferred from beauty concept), projectile muzzle/impact origins separately defined.
- LOD/profile and measured 1P & 3P visual/hitbox consistency report included.
- Clean artifact hashes plus per-step PASS/FAIL/NOT_RUN evidence; all open gates remain BLOCKED for downstream promotion.

## Source tree / device delivery layout

Use existing repo roots, **without moving or renaming anything**:

```text
art/concepts/characters/<CHR_ID>/                # immutable source + variants in proposals/
art/blender/characters/<CHR_ID>/                   # editable high/low/rig .blend revisions
art/blender/weapons/<WPN_ID>/
art/textures/source/characters/<CHR_ID>/          # editable PBR maps, normal/bake masters
game/assets/characters/heroes/<CHR_ID>/          # final exported 3P GLB and LODs
game/assets/characters/viewmodels/<CHR_ID>/      # separate 1P arms/hands GLB
game/assets/weapons/<WPN_ID>/                    # separate weapon/focus GLB
game/scenes/characters/heroes/<CHR_ID>/          # inherited Godot character scene
game/scripts/characters/; game/scripts/combat/; game/scripts/abilities/
docs/characters/plans/<CHR_ID>.json              # existing canonical plan/gates
docs/pipeline/                                    # this new spec and templates
evidence/characters/<CHR_ID>/<source_sha>/         # native screenshots, genuine video, checksums, reports
```

For phone handoff, preserve the **existing** owner-provided `Internal storage/AETHERFALL – REALMS COLIDE/` path (the phone's current spelling) and any current `korvex_blockout_v01/`; deliver a versioned ZIP containing `models/`, `art/`, `docs/`, `evidence/`, `manifest.json`. Staging to ChatGPT/Library/GitHub is **not** proof that bytes are present on the physical phone.

## Baseline work order for the next hero

**Milestone AF-CHR-ART-SLICE-001:** choose one already AETHERFALL-approved hero whose *exact* master image is accessible and hash-verified. Do NOT auto-select or alter an unapproved legacy candidate. Art team: non-destructive mesh prep, neutral pose, 4-view visual, 3P LOD0 + one LOD, rig skeleton, weapon and 1P hands. Gameplay: one locomotion controller, one fully phased attack and one ability, one AI sparring dummy and collision replay. S.I.R.E.: independent proof and owner visual review; no whole-roster expansion before first complete slice passes.

## What is not implemented by this specification

No Blender sculpture was created, no Godot runtime/camera/AI system was launched, and no platform binary was uploaded. The offline Python checks in this handoff inspect specification structure and available staged file integrity only; no 3D visual, AI fairness, engine, phone or multiplayer certification follows from those checks.