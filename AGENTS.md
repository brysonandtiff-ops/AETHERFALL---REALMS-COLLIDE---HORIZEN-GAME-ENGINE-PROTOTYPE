# AETHERFALL — Agent and Contributor Work Order

**Project:** AETHERFALL: REALMS COLLIDE
**Goal:** Build the game in this repository without changing approved visual canon or making false completion claims.
**Authorised executor:** The owner and specifically authorised S.I.R.E. / GENESIS AI / HORIZON development tools with verified repository and runner access. This file does not grant a new agent or connection.
**Current status:** Scaffold only. Real Godot 4.7.2 headless import/bootstrap has passed in GitHub CI, but gameplay, authored Blender model/runtime visuals, multiplayer and physical-device acceptance remain NOT VERIFIED.
**Acceptance for this work order:** Versioned folder layout; Godot 4 project and startup scene; accurate asset registry; offline validator; linkable commit. Native-engine/gameplay verification remains a separate gate.

## Working rules

1. Inspect current files, branch, canonical references and dependencies before modifying.
2. Follow FIND → PLAN → BUILD → TEST → REPAIR → RETEST → SHOW → HARDEN → PROVE → FINISH.
3. One source of truth for each asset: editable art in `art/`; exported engine imports in `game/assets/`.
4. Respect art locks, original artwork, ownership and licensing. Never replace approved art with a concept or placeholder.
5. Preserve existing files, drafts, Godot UIDs, saved games and history. Prefer small, reviewable source changes.
6. No invented agents, evidence, gameplay, external service connections, passing tests or deployment results.
7. Do not create new paid dependencies, merges, deploys or releases automatically.
8. Use `python3 tools/validate_structure.py` for structural checks; engine and device verification need a real runner.
9. For 3D assets, record native Blender four-angle renders, topology/UV/rig checks, genuine Godot import and animation tests, hashes and full-length video when applicable.
10. Capture real runtime screenshots/video only from a real engine or device, and tie them to the exact source commit.

## Evidence reporting

Report WHAT HAPPENED → WHY IT MATTERS → WHAT WAS FIXED → WHAT WAS VERIFIED → WHAT REMAINS. Include files/commit, actual tests and exit codes, risks and rollback, and never promote 'placeholder' to 'playable'.

For upstream governance consult the existing S.I.R.E. repository's canonical engineering laws and game-production pipeline; links here are guidance only and do not assert those external controls are connected.

## Source migration, truth and hardening

- Shadowspire is a legacy concept source; no owned standalone Shadowspire repository is currently verified. Do not delete third-party repositories or unreachable local original Unreal/Godot source.
- Vellaris Bloodshield and ThornDell are AETHERFALL-approved concepts. Eight other reserved character IDs represent historical selected *Shadowspire* hero concepts, not playable models or automatic new AETHERFALL approvals.
- Protect original art, model versions, file paths, local saves and reference history. Do not fabricate assets or runtime media to fill missing source.
- `tools/validate_structure.py`, adversarial tests and actual Godot headless CI are mandatory source-level gates. Only genuine graphical/native engine and actual device captures can establish visual acceptance. Never claim a playable game from a headless placeholder.
- No new paid APIs, merges, deployments or destructive repository operations without the relevant independent evidence and owner authorisation.

## Mandatory continuous-build routing

Before starting a work order, read `BUILD_HERE.md`, `docs/production/MASTER_BUILD_ROADMAP.md`, `docs/production/DEFINITION_OF_DONE.md` and the dependency/status source `docs/production/WORK_QUEUE.json`. Query `python3 tools/production_queue.py --next`; do not pick blocked or prerequisite-incomplete work. Each job follows FIND → PLAN → BUILD → TEST → REPAIR → RETEST → SHOW → HARDEN → PROVE → FINISH.

After real work, record exact source commit, test commands/results, original engine/art/device evidence, reviewer decision, and next safe task using `docs/production/HANDOFF_AND_RECOVERY.md`. No task can become VERIFIED without real evidence and all dependencies verified. If a step fails, repair and retest. If owner approval, original art, rights, budget or authorised runner is missing, mark it BLOCKED with an actionable reason and move to **independent** unblocked work only. Never silently bypass a gate.

The task queue is a **plan**, not an active autonomous execution system or permission to create new agents, spend, merge or deploy. Existing owner-authorised S.I.R.E. / AXIOM G.A.I.S. / HORIZON governance remains in force.

## Hardened source history and review gates

- Before promoting an item, check `docs/production/DEFINITION_OF_DONE.md`. A VERIFIED task requires `reviewed_by`, `assigned_executor`, a real commit SHA and authentic evidence references; its dependencies must already be VERIFIED. The checker can validate only their structure; reviewers inspect the actual proof.
- Preserve committed work-order IDs and dependency contracts. CI audits new PR plans against the base branch once the plan is merged; do not delete past work, silently change accepted criteria or rewrite already-verified evidence.
- `.github/CODEOWNERS` documents sensitive ownership, but **does not enforce approvals by itself**. Owner-controlled branch protection/rulesets must enforce required CI and appropriate independent review. See `docs/security/REPO_HARDENING.md`.
- The source scanner checks high-confidence textual secret markers, tracked ignored caches, symlinks and unreviewed git submodules. No automated scanner can certify secret-free binaries, licensed art or connected services; do manual security review.

## AAA studio layout and content change authority

The native Godot project remains `game/project.godot`. Treat `studio/layout_manifest.json` and `config/toolchain.json` as required source-controlled architecture; no fake Unreal project trees or new agents. Before changing folders, review `docs/architecture/AAA_STUDIO_ARCHITECTURE.md`; run `python3 tools/validate_studio_layout.py` and the existing source/queue tests.

Never create a second hero identity register. Follow `docs/production/CONTENT_HANDOFF.md`: canonical concept → editable Blender master → independently versioned engine GLB/export → native Godot scene → test and genuine evidence. Plugin imports must include license/provenance reviews and actual engine tests. Build/QA/release lanes are **reserved organisational boundaries**, not operating automation or permission to provision external servers.

A requested engine migration, source-art renaming, new licensed dependency, LFS/Perforce transition or paid build farm requires a separately scoped owner decision and safe migration tests.

## Operational asset receipt progression

Keep the registry authoritative: `art/asset_registry.json` owns immutable character IDs and canon approval, while `art/handoffs/<id>.json` documents real source files with SHA256. Each status moves only **one adjacent stage** in a reviewed PR: reservation → concept file → Blender file → GLB export → separately reviewed Godot native import. `python3 tools/studio_preflight.py` is the single local source/test gate; `python3 tools/validate_asset_handoffs.py --report` identifies the next honest stage. Never mark an asset native verified from a header, checksum, synthetic unit-test fixture or concept illustration. Legacy candidate canon approval remains a separate owner decision.
