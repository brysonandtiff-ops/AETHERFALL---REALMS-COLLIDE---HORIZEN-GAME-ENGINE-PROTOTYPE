## One bounded work order
Work order ID (e.g. `AETHERFALL-DEVOPS-001`):
Executor/specialist (existing S.I.R.E. systems only):
Exact project scope and acceptance:

## What changed (FIND → PLAN → BUILD → TEST → REPAIR → RETEST → SHOW → HARDEN → PROVE → FINISH)
Describe source files changed, canonical art locks, dependencies and how to roll back.

## Verified test evidence
- [ ] `python3 tools/aetherfall.py doctor --json` (source contracts, not S.I.R.E. runtime)
- [ ] `python3 tools/aetherfall.py check` (validator + unit tests)
- [ ] GitHub CI headless Godot 4.7.2 run for the exact candidate commit
- [ ] Real Godot graphic gameplay captured, if claiming a playable/visual change
- [ ] Blender original geometry/rig/animation proof, if changing 3D assets
- [ ] Physical-device evidence, if claiming device readiness

List exact exit codes, CI run links, tested commit SHA, screenshot/video originals and evidence limits. Unrun tests are NOT_RUN; no simulated passes.

## Security / integrations
- [ ] No secrets/tokens, unsafe untrusted commands, new paid APIs or unnecessary plugin installs
- [ ] No second master agent or unverified connected runner claims
- [ ] Existing S.I.R.E. Git/permissions/security stewards respected
- [ ] Original art, game files and drafts preserved; no auto-merge or deploy

## Risks, recovery and next
Known limitations, rollback instructions, next bounded step and release hold:

## S.I.R.E. source integrity receipt (if available)
- [ ] Exact candidate `git rev-parse HEAD` matches the CI-reported PR head
- [ ] SHA-256/SHA3-256 manifest and Merkle root attached outside Git
- [ ] Only `UNANCHORED_INTEGRITY_ONLY` or independently anchored integrity is claimed
- [ ] Original graphics, animations, native engine and phone evidence separately verified if the change needs them
- [ ] No self-issued release or owner-signature claim
