# Studio integration, build and release trains

## Real present vs future

- **Now:** source checks, queued work-order validation, GitHub PR review and real Godot 4.7.2 **headless** import/bootstrap CI exist.
- **Not yet operating:** a running dedicated build farm, automated content exporter, asset LFS/Perforce server, packaging train, gameplay test farm, multiplayer servers and scheduled release service. Folder names do not make these real.

## Proposed lanes — one verified change at a time

| Lane | Entry | Exit / owner | Artifacts |
| --- | --- | --- | --- |
| Feature / art work branch | Verified dependency and protected owner reference; `AF-###` work order | Author + relevant discipline reviewer | Source diff, work-order ID, actual tests and visuals |
| Integration PR | Non-destructive review branch with adequate regression coverage | Required CI + suitable independent review, subject to GitHub rulesets | Exact SHA, test output, art/asset manifest |
| Nightly candidate (future) | Owner-approved runner/pipeline, assembled tested content | Build engineering + QA | Versioned real exports, import logs, crash/performance reports |
| Milestone candidate (future) | Signed-off vertical slice / alpha / beta gate | QA lead and game lead | Full test matrix, native screenshots/video, approved risk register |
| Release candidate (future) | Owner-approved target platform/packaging/signing | Release lead + explicit owner go/no-go | Reproducible checksum, signing, rollout + tested rollback |
| Hotfix (future) | Verified incident, test reproduction and minimal fix | Release lead and QA after actual rollback drill | Incident note, regression, patch proof |

## Parallel teams without hidden overlap

- Game systems: `game/scripts/` and `game/data/`; assets are referenced through stable IDs.
- Art and animation: `art/` masters; handoff to `game/assets/` only after review.
- Maps/level: `game/scenes/levels/`, environment source `art/blender/environments/`.
- UI and accessibility: `art/ui/`, `game/assets/ui/`, `game/scenes/ui/`, `game/scripts/ui/`.
- Tools/build: `tools/`, `pipeline/`, `config/`, workflow CI. QA: `tests/`, `evidence/`.
- No task authorises a new AI agent, repository rewrite, unapproved plugin or paid external service.

**Continuation:** run `python3 tools/production_queue.py --next`, take one valid work item, follow FIND → PLAN → BUILD → TEST → REPAIR → RETEST → SHOW → HARDEN → PROVE → FINISH. If blocked, record why; progress only on independent eligible work.
