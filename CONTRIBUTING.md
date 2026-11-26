# Contributing to AETHERFALL

Start at [GIT_HERE.md](GIT_HERE.md), [AGENTS.md](AGENTS.md) and the real [Godot project](game/project.godot). AETHERFALL is still in pre-production.

- Inspect live work and choose the correct base branch before editing. Use scoped `feature/`, `fix/`, `art/`, `docs/`, `design/`, `hardening/`, `chore/` or `architecture/` branches.
- Preserve existing Godot UIDs, character IDs, locked Vellaris/ThornDell artwork and original model sources. New approved source binaries should be versioned, never silently overwritten. Follow [CHARACTER_WORKFLOW.md](docs/characters/CHARACTER_WORKFLOW.md) and [VISUAL_CANON_LOCK.md](docs/characters/VISUAL_CANON_LOCK.md).
- Run actual source tests and relevant native Godot/Blender/device checks. If a check was not run, label it **NOT_RUN** rather than PASS.
- Open a small **draft PR** identifying work order, exact source SHA, parent PR, changed assets, test evidence, risks and rollback. Request a separate qualified reviewer.
- Do not force-push shared branches, bypass S.I.R.E. Git Stop, leak credentials, deploy services, add paid integrations or approve a release automatically.

The repository-local `tools/git_preflight.py` is only a read-only supplement to existing S.I.R.E. Git authority. GitHub branch rules need separate owner setup; see [Issue #11](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/issues/11).
