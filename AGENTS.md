# AETHERFALL — Agent and Contributor Work Order

**Project:** AETHERFALL: REALMS COLLIDE
**Goal:** Build the game in this repository without changing approved visual canon or making false completion claims.
**Authorised executor:** The owner and specifically authorised S.I.R.E. / GENESIS AI / HORIZON development tools with verified repository and runner access. This file does not grant a new agent or connection.
**Current status:** Scaffold only. Gameplay, assets, native Godot/Blender execution and device evidence are NOT VERIFIED.
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
