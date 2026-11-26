# Continuity, work orders and recovery — no abandoned work

## Work-order protocol

Before any code/art change, pick an item from `python3 tools/production_queue.py --next`. Confirm all dependencies are VERIFIED. The active authorised executor may change its status to `in_progress` with `assigned_executor` identifying an actual approved person/tool; do not invent a connected agent. Keep one main integration branch and small review branches; always inspect and avoid overwriting in-flight work.

**Template (copy into a PR or issue):**

```text
Project: AETHERFALL: REALMS COLLIDE
Work item: AF-___ / title:
Executor (authorised and actually connected):
Goal and minimal deliverable:
Input files / current commit / dependencies:
Protected art, data, Godot UIDs, rights and secrets boundaries:
Implementation and exact paths changed:
Commands run and real results (PASS / FAIL / NOT RUN):
Native Blender/Godot/multiplayer/device proof (or NOT RUN):
Commit SHA, logs, screenshots/video, hashes:
Errors or blockers, severity, last reproducible command:
Rollback and recovery plan:
Reviewer identity, explicit approval and status (planned/in_progress/review/blocked/verified):
Next unblocked item from python3 tools/production_queue.py --next:
```

## Repair/retest loop

1. **Identify failure** by running smallest deterministic reproducer; keep original logs and exact SHA.
2. **Triage severity:** destructive data, secret leak, rights violation, broken approved art, false verification or failed safety checks are hard blocks to *affected work*.
3. **Repair root cause**, never mute tests or skip CI to make progress look green. Keep old working scenes/models and make backups before migrations.
4. **Retest** target case, existing unit/integration suite, native Godot import/boot and impacted features; add a regression test.
5. **Record proof** and request review. Only with reviewer acceptance move to VERIFIED, then rerun `--next`.
6. **If environment, permission, original asset or owner decision is missing**, mark BLOCKED with precise reason and safe reproduction/next instruction; work on independent tasks only. Do not promise background execution.

## Concurrency without destructive collisions

- Reserve folders/files by **responsible discipline** only; this is a boundary, not a real assigned agent.
- Hero art producers work in `art/`; Godot gameplay systems in `game/scripts/`; definitions in `game/data/`; CI/test engineers in `tests/` and `tools/`.
- Cross-boundary changes require asset ID/schema review. Avoid parallel writes to the same Godot `.tscn`, `.tres`, registry or source `.blend`.
- PR reviews protect approval gates; CI detects breakage. A queued CI run or passing static test is not authorisation to merge.
- Locked visual identity, paid infrastructure, external integrations, releases and destructive moves need specific owner authorisation; do not bypass to keep momentum.

## Immutable history and review protection

When a production queue exists on the PR base branch, CI runs `python3 tools/production_queue.py --audit-baseline <prior_plan.json>`. It rejects renamed/deleted/reordered old tasks, unreviewed additions marked done, rewritten contracts, erased proof and illegal status jumps. To revise a frozen requirement legitimately, propose a reviewed governance/tool migration with rationale and preserved audit history rather than silently editing existing task records. A blocked item may resume under its documented state-transition rules; verified work that regresses must be reopened explicitly. See [repo hardening](../security/REPO_HARDENING.md).

## Resume after interruption

Fetch latest branch, check open PRs/CI, run `python3 tools/production_queue.py --validate` then `--next`; read any BLOCKED entries and the latest work-order/issue evidence. Confirm original assets and refs before work. Do not re-create specialist agents, reset status or promote stale records simply to restart.
