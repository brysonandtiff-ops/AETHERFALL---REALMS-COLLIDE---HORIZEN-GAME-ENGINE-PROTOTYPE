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

## Safe file layout and breaking-change gate

- `config/layout-contract.json` defines paths and base-to-head invariants. Run `python3 tools/structure_guard.py check` and `python3 tools/structure_guard.py diff --base <actual-trusted-ancestor-SHA>` before promoting work. CI does so for PRs.
- New scenes/scripts/assets are additive; do not silently delete/rename originals, move Godot entry scenes, change registered character IDs or weaken the base version of the layout policy.
- Keep original `.blend` art in `art/`, exported `.glb` in `game/assets/`, unchanged genuine media in `evidence/`. The guardian checks Godot literal `res://` references, UIDs and Windows/Linux file portability.
- Breaking changes need a separately reviewed migration work order, original source backup, reference patch plan, native engine regression and exact-SHA proof. CODEOWNERS is only a review signal until repository branch rules enforce it.

## AETHERFALL continual development and S.I.R.E. team routing

- Master is the **existing S.I.R.E AI**; gameplay/art route to **GENESIS AI / HORIZON**, Git to S.I.R.E. Git Team, security/plugins to the existing stewards. No local definition is a new running AI.
- Use `.sire/integration.json` and `.sire/work-orders/` for bounded authorisation, honest connection status, explicit tests and acceptance. `docs/development/SIRE_INTEGRATION.md` documents the source paths and routing.
- Repeatable pipeline: FIND → PLAN → BUILD → TEST → REPAIR → RETEST → SHOW → HARDEN → PROVE → FINISH. One change/PR at a time.
- Local command: `python3 tools/aetherfall.py doctor|status|routes|skills|check|work|handoff|cmd`. None of these automatically contacts S.I.R.E. agents/plugins or grants a runner.
- Keep revisions in a review branch/draft PR. CI is source-contract/native headless verification only; genuine graphical/device/Blender/video evidence must be reported separately.
- No new spending, undisclosed networks, remote control, user credential copying, automatic merge, auto-release or destructive cleanups. Only use verified upstream S.I.R.E. connections and existing permissions.

## Android local documents (owner-controlled)

- The on-phone folder is exactly `Internal storage/AETHERFALL – REALMS COLIDE/` (**COLIDE**, as already present in the owner's screenshots), NOT the GitHub repository spelling. Never rename this Android folder or touch its existing `korvex_blockout_v01` subfolder.
- Downloaded, owner-approved text/PDF/Office documents go under `Docs/Inbox/` within that phone folder, per `config/local-documents.json` and `docs/development/ANDROID_LOCAL_DOCUMENTS.md`.
- `tools/phone_docs.py` offers **preview-only by default**, then explicit `--apply` COPY + SHA256 check, no overwrite or deletion. `--watch` is owner-started foreground only; no installed service or automatic Android system setting.
- GitHub/ChatGPT tools cannot set phone download destinations or claim the target exists after this repository edit. Phone-local use, permission and actual file-copy verification remain owner/device actions.
