# Definition of done — no false verification

A task becomes **VERIFIED** in `WORK_QUEUE.json` only after review finds **every** acceptance condition true in real code/assets and exact source identity and evidence have been captured. Updating task status is itself a reviewed source change.

## Required evidence for every work item

1. **Source:** recorded Git commit SHA, changed paths, the applicable work-order ID and preserved existing canon.
2. **Tests:** exact commands, environment/tool versions, pass/fail output and failures fixed and rerun. Unit/structure tests do not substitute for engine tests.
3. **Runtime:** real Godot startup/gameplay proof for scene/features; real Blender captures for meshes/rigs; real server/client traces for multiplayer; physical device capture for device claims.
4. **Security:** reject invalid input, verify authority/auth where needed, no secrets/PII in repository, licensing and rights cleared for committed art.
5. **UX:** controls, actionable errors/recovery, readability, accessibility and measurable performance for changed user-facing functionality.
6. **Review:** owner/authorised reviewer confirms approval, test evidence, remaining limits and rollback. Never auto-approve locked visual changes or release spend.

## Evidence categories (do not conflate)

| Claim | Minimum genuine proof |
| --- | --- |
| STRUCTURE_ONLY | Source tree inspection + static Python tests with exact SHA. |
| NATIVE_BOOT_ONLY | Official engine version/import/start output tied to SHA; headless passes **do not** verify visuals. |
| ART_SOURCE_VERIFIED | Editable `.blend`, approved source/art lock, Blender native views, rig/UV/topology and hashes. |
| GODOT_ASSET_VERIFIED | Fresh native Godot import and in-engine screenshots/animation; licensing and dependencies verified. |
| GAMEPLAY_VERIFIED | Live end-to-end gameplay video and reproducible behavior tests, including start-to-win/loss. |
| MULTIPLAYER_VERIFIED | Real independent clients + server logging authority, latency, disconnect/reconnect and abuse tests. |
| DEVICE_VERIFIED | Actual target device OS/build ID, input/capture, frame-time and memory results. |
| RELEASE_VERIFIED | Approved, signed, reproducible build, user-tested release and rehearsed recovery; explicit go/no-go. |

## Before status promotion

- `status=verified`: all `depends_on` tasks must already be VERIFIED. Record `assigned_executor`, explicit `reviewed_by`, `verified_commit_sha` (full 40-character Git SHA), and real `evidence_refs`. These are claims requiring independent review, not proof by themselves.
- The task queue checker enforces *shape*, dependency order and prior-commit transition rules, **not authenticity**. Reviewer must check each link/hash, content rights, real runtime and recorded reviewer identity. Existing task identity/acceptance/dependencies are append-only contracts by default; approved revisions require deliberate, separately reviewed migration of the guardrails, never silent rewrites.
- `status=review`: attach candidate `evidence_refs` and actual `assigned_executor`. CI history audits reject planned→verified jumps; a previous reviewed task and separate review decision are required for VERIFIED.
- `status=blocked`: give `blocked_reason`, preserve attempted work; other independent tasks may continue.
- If evidence is later found incorrect or functionality regresses, reopen as PLANNED or BLOCKED and file a repair work order. Nothing inherits stale proof.

## How to check locally

```sh
python3 tools/validate_structure.py
python3 tools/production_queue.py --validate
python3 -m unittest discover -s tests -v
python3 tools/production_queue.py --next
```

Then run the native Godot, Blender, network and device checks required by the changed feature. CI performs headless native Godot smoke; no graphical/physical proof without actual capture.

## Asset file statuses are distinct from gameplay acceptance

`concept_recorded`, `blender_source_recorded` and `runtime_export_recorded` mean that approved/reviewable source records point at actual files with checked SHA256—not that a native engine or a player has verified them. `native_import_reviewed` additionally requires original Godot import log and screenshot/video with an actual reviewer record; the validator can confirm recorded bytes, not the truth of their content. Every next stage requires one reviewed PR and retains canonical asset IDs and original source history. Gameplay still requires separate, genuine engine tests and videos under the production queue.
