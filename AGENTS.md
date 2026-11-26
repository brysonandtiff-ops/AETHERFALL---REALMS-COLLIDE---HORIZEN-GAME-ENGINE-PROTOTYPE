# AETHERFALL — Agent and Contributor Work Order

## CANON HARD STOP — run before ALL character artwork or model tasks

**Do not begin a canonical Vellaris, ThornDell or other approved character render unless the exact owner-approved reference image is supplied to that run and the lock file has been checked.** Read docs/characters/VISUAL_CANON_LOCK.md and CANON_LOCKS.json before generating, describing, converting, modelling or accepting output. New render = PROPOSAL_PENDING_OWNER_REVIEW until original-to-candidate evidence and explicit owner signoff. Never replace approved images, assume missing references, copy Vellaris character details to another hero, or silently resolve Korvex/Corvex or Razor/Raven variants.


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

## Character standard and non-negotiable review

Every future AETHERFALL character (including DPS, support, enemy, boss and NPC) requires a registered asset ID and matching plan under `docs/characters/plans/`. Follow `docs/characters/CHARACTER_WORKFLOW.md` (Vellaris completeness plus proof), preserve owner-locked visual identity and hero-unique kits, and never clone shields across tanks. A concept image is not a model or engine proof. New role/approval or Corvex/Korvex alias changes require owner review. CI and code-owner review must not be bypassed.

## HARD STOP: visual canon and drift protection

Before every approved character generation, illustration, blockout, model, import or update, inspect the exact owner-approved source image and read docs/characters/VISUAL_CANON_LOCK.md plus CANON_LOCKS.json. Never generate an alleged canonical image from memory or a paraphrase. New images are unapproved proposals until owner source-to-output comparison. Preserve original image bytes/hash, approved silhouettes, unique weapon/focus and hero role/kit. Use Vellaris board layout as the presentation style, not as a universal bloodshield or hero template. Never silently resolve Corvex/Korvex or conflicting Razor/Raven weapon variants. Source-level CI tests are not artistic similarity or engine proof.
