# AETHERFALL — daily development, in five steps

**1 — Open the repository.** Godot lives in `game/project.godot`. Original Blender sources belong under `art/`.

**2 — Check readiness.** Run `python3 tools/aetherfall.py doctor`. It distinguishes local source checks from missing S.I.R.E. runtime integration.

**3 — Choose a job.** Run `python3 tools/aetherfall.py work list` and `python3 tools/aetherfall.py routes`. One work order = one bounded outcome.

**4 — Develop and test.** Use a branch + draft PR. Run `python3 tools/aetherfall.py check`; CI repeats source tests and exact-version headless Godot on PRs. Real game visuals need separate engine/device capture.

**5 — Show and finish.** Tie honest evidence to a source SHA, review security and regressions, then merge/deploy only through existing S.I.R.E. permissions and independent approval.

Useful short commands: `python3 tools/aetherfall.py cmd T` explains tests; `cmd G` Git, `cmd E` evidence, `cmd N` next. These are route guides, not background executors.

This project is currently a **source foundation**. Work-order and plugin files do not grant automatic dispatch, agent hosting, MCP access or paid APIs.
