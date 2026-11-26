# AETHERFALL — MASTER BUILD ROADMAP

**Project:** AETHERFALL: REALMS COLLIDE  
**Plan status:** Production path documented; gameplay and multiplayer are not yet implemented.  
**Owner:** Project owner; only authorised S.I.R.E. / HORIZON / GENESIS workflows and connected contributors may execute.  
**Execution system:** `docs/production/WORK_QUEUE.json` defines all named work packages and dependency status. Query with `python3 tools/production_queue.py --next`. This document explains *why* and *how*.

## Non-negotiable operating cycle

**FIND → PLAN → BUILD → TEST → REPAIR → RETEST → SHOW → HARDEN → PROVE → FINISH.**

For **every** work package: inspect current main/branch, actual project and canon; write the smallest approved implementable change; add real functionality; run automated and native tests; fix root causes; capture genuine runtime media where visual; verify security/accessibility/performance as relevant; link commit + test logs + proof; submit review; move the work item to VERIFIED only after evidence is checked. Then query the queue again.

No stage is complete merely because documentation, a folder, a generated concept, a smoke screen or a CI job exists. **Do not execute an infinite autonomous agent loop:** the repo is a manual/connected-tool work queue with machine-enforced checks, not a running service.

## Nine-stage development highway

| Stage | What is built | Blocking exit gate | Work packages |
| --- | --- | --- | --- |
| **M0 — Decisions and safety** | Owner-approved vision, canonical roster, rights ledger, reproducible Godot/Blender toolchain, versioned data schemas, CI. | Gameplay/camera/team/device scope is recorded; no copyrighted/unlicensed content imported; real toolchain verified. | AF-001 to AF-006 |
| **M1 — Functional prototype** | Real player input/camera/movement, health/damage/shooting, ability runtime, greybox arena, debug HUD, regression scenes. | Actual native Godot prototype works; scripted cases fail on broken combat. | AF-010 to AF-018 |
| **M2 — First true playable match** | One unique approved **tank**, **DPS**, **support**, selection HUD, team rules, first match mode, bots, onboarding. | One complete local match demonstrable in genuine Godot footage, with automated scores/abilities. | AF-020 to AF-028 |
| **M3 — Proven multiplayer** | Server authority, replication, latency policy, reconnect, abuse resistance, host/cost decisions. | Two independent clients complete a real match; invalid actions rejected; real network/quit/rejoin evidence. | AF-030 to AF-036 |
| **M4 — Art and expanded content** | Approved Blender hero blockouts/models, skeletons, animations, materials, VFX/audio, Godot exports, polished realm/arena and balanced roster. | Native Blender and Godot compare to locked art; exported rigs/clips and performance are verified. | AF-040 to AF-048 |
| **M5 — Alpha stability** | Save/settings persistence if applicable, accessibility, controller support, performance, regression/soak tests, safe telemetry. | Quality, device and security evidence meets recorded targets; no unresolved blocker. | AF-050 to AF-056 |
| **M6 — Beta qualification** | Reproducible builds, signed packaging, actual device/network load tests, upgrades, legal and content/IP review. | Candidate meets all approved platforms and has recovery/rollback proof. | AF-060 to AF-064 |
| **M7 — Controlled launch** | Rollback drills, correct store/support material, explicitly approved release. | Owner go/no-go, real build + signing logs, safe rollout and restore plan. | AF-070 to AF-072 |
| **M8 — Live operations** | Incident triage, safe hotfixes, new approved content and scheduled maintenance. | Each patch passes the same safety and evidence gates; keep an owner-governed release cycle. | AF-080 to AF-082 |

**Critical path:** AF-001 + AF-003 + AF-004 → AF-006/010 → AF-012/014/015 → AF-020/021/022 → AF-024/025/028 → AF-030/031/035 → AF-047/048 → AF-056 → AF-064 → AF-072. Other scoped work may progress in parallel when all its own dependencies have passed.

## Technical blueprint — who owns what

- **Godot 4.x gameplay:** `game/project.godot`; `game/scripts/core/` and `characters/` own movement and state, `combat/` damage/hits, `abilities/` effect execution, `match/` mode lifecycle, `teams/` team rules, `network/` transport/authority. `game/data/heroes|abilities|modes|balance/` holds future typed definitions. No scene root rewrites without migration tests.
- **Heroes:** reserve stable `CHR_*` asset ID in `art/asset_registry.json`; approved concepts under `art/concepts/characters/`, editable models `art/blender/characters/`, engine-ready exports `game/assets/characters/heroes/`, scenes `game/scenes/characters/heroes/`. Each unique kit requires distinct behavior, hitboxes, rig, animations, counters and real tests.
- **Levels:** reference under `art/concepts/worlds/`, Blender environment under `art/blender/environments/`, exported worlds under `game/assets/worlds/realms/`, Godot gameplay layout under `game/scenes/levels/`; preserve spawn/collision/visibility and performance.
- **UI/audio/VFX:** UI scenes `game/scenes/ui/`, logic `game/scripts/ui/`, assets `game/assets/ui/`, original sounds `art/audio/source/`, runtime tracks `game/audio/`, VFX under `game/assets/vfx/` and `game/scenes/vfx/`.
- **State and security:** only real player settings/saves in Godot `user://`, no Git secrets or stored private player records; server validates authoritative gameplay; deliberate asset licensing and permissions.
- **Verification:** `tests/` + GitHub Actions do source/headless tests; original screenshots/video, Blender captures, device captures and frame-time traces under `evidence/` with exact commit metadata.

## Planned first release vertical slice (not yet design-locked)

**One arena + one ruleset + three distinct roles (tank/DPS/support) + basic HUD + complete local match + measured 2-client multiplayer.** A commercial-scale roster is **not** the first acceptance gate. Names, camera, roster selection, team size, platforms, network hosting and cosmetics remain owner decisions (AF-001/003/030/036). Character references such as ThornDell, Vellaris, Razor and Raven are not playable models or silently approved roster changes.

**First slice MUST work before content explosion.** Prefer modular reusable abilities, data, collision, effects, character controllers and one faithful art pipeline. Scope additional worlds, cosmetics, matchmaking, monetisation, live voice and storefront integrations only after appropriate decisions/approvals.

## S.I.R.E. integration and team handoff

AXIOM G.A.I.S. is the *existing* master command interface per owner governance; HORIZON coordinates approved game-engine work. These names do not imply live agent sessions or additional repo access. Any authorised team/agent reads `AGENTS.md` → `BUILD_HERE.md` → queue `--next` → task dependencies and acceptance → real project files → `DEFINITION_OF_DONE.md`.

Each work order records: project; goal/ID; authorised executor; requirement/inputs; affected paths and protected art; exact commit; status; test outcomes; genuine captures; blockers; next safe task. Handoffs follow `HANDOFF_AND_RECOVERY.md`.

## Hard-failure policy — no silent stopping, no bypassing

**Failed check:** stop promotion, repair same task, retest and log cause.  
**Blocked by approval/asset/tool:** mark BLOCKED with specific reason, preserve state, pick independent next task; do not fabricate substitute art.  
**Security/rights/payment/engine/locked-canon issue:** halt the affected change and request the actual owner decision.  
**Review not merged:** production/main does not receive it; continue safe branch/test work with its limitations clearly stated.  
**Release gate missing:** no deployment or public gameplay claims.

## Current truth

The repository currently contains a Godot starter scene, source checks, art registry and placeholders for future features. Prior GitHub workflow proof confirms **Godot 4.7.2 headless import/start only**, not rendered gameplay, finished characters or device tests. Plan tasks start as PLANNED and are never marked VERIFIED from this document alone.

See [tests](TEST_MATRIX.md), [definition of done](DEFINITION_OF_DONE.md), [decisions/risks](DECISIONS_AND_RISKS.md), [recovery](HANDOFF_AND_RECOVERY.md), [release](RELEASE_AND_OPERATIONS.md) and [architecture](../architecture/REPO_LAYOUT.md).
