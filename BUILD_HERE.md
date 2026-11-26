# AETHERFALL — START BUILDING HERE

**Project:** AETHERFALL: REALMS COLLIDE  
**Current product truth:** Pre-production source scaffold. `game/project.godot` boots a placeholder scene. **No playable combat, finished heroes, online game, or real-device release is verified.**  
**Source of truth:** [docs/production/WORK_QUEUE.json](docs/production/WORK_QUEUE.json) (task status and dependencies), [docs/production/MASTER_BUILD_ROADMAP.md](docs/production/MASTER_BUILD_ROADMAP.md) (human build order).

## Three actions to take first

1. **Find the next safe work:** `python3 tools/production_queue.py --next`. This prints unblocked tasks whose prerequisites are VERIFIED. Never assume a task is completed because its folder exists.
2. **Take one task as an actual work order:** Check its owner decision, dependencies, files, acceptance and proof; follow [docs/production/HANDOFF_AND_RECOVERY.md](docs/production/HANDOFF_AND_RECOVERY.md) and `AGENTS.md`.
3. **Build, test, repair, retest and prove:** `python3 tools/validate_structure.py && python3 tools/production_queue.py --validate && python3 -m unittest discover -s tests -v`, then real native Godot/Blender/device tests appropriate to the task. Capture exact commit SHA and original evidence. Submit review and update the task status only with real proof.

**See every milestone:** [MASTER BUILD ROADMAP](docs/production/MASTER_BUILD_ROADMAP.md) · [Definition of done](docs/production/DEFINITION_OF_DONE.md) · [Test matrix](docs/production/TEST_MATRIX.md) · [Decision and risk register](docs/production/DECISIONS_AND_RISKS.md) · [Release/operations](docs/production/RELEASE_AND_OPERATIONS.md).

## Current first work, not fake progress

The queue currently exposes **AF-001** (confirm core rules/platforms), **AF-002** (rights and canon protection), **AF-003** (hero roster/naming decisions), and **AF-004** (reproducible local toolchain). These are parallel *pre-production* tasks; the owner decides locked art, team size, camera, engine changes and expenses. Reassess `--next` after a task is genuinely VERIFIED.

The initial architecture is under review in [PR #8](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/pull/8). Nothing in this document represents an automatic merge or ongoing agent execution.

## Continue without losing momentum

- A failed test means **repair/retest**, never skip or mark verified. A blocked task receives a clear reason and a handoff; continue only *independent* unblocked tasks.
- Do not bypass required owner decisions, visual locks, rights/privacy/security gates, paid-service consent, engine/device proof, or deployment approval.
- Keep work small and reviewable; preserve every approved concept, Godot UID, path, original photograph, and canonical reference. Do not move/delete existing content casually.
- CI is an automatic **checker**, not an always-running game builder. Continuous development requires an authorised executor, actual repo/runner access and explicit review/merge workflow.

## Location map

| Looking for | Open |
| --- | --- |
| Ordered entire build | `docs/production/MASTER_BUILD_ROADMAP.md` |
| Next exact task and dependencies | `docs/production/WORK_QUEUE.json`, via `tools/production_queue.py --next` |
| What proves completion | `docs/production/DEFINITION_OF_DONE.md` and `docs/evidence/PROOF_REQUIREMENTS.md` |
| Where files go | `docs/architecture/REPO_LAYOUT.md` |
| How original art becomes a Godot asset | `docs/art/ASSET_PIPELINE.md` |
| What to do after a failure / handoff | `docs/production/HANDOFF_AND_RECOVERY.md` |
| What cannot proceed without owner approval | `docs/production/DECISIONS_AND_RISKS.md` |
| Real code / Godot starter | `game/project.godot` |
