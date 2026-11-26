# Release, recovery and live operations

**Current status:** Planning only. No production servers, release builds, live players, matchmaking or app store submissions exist as verified functionality in this repository.

## Build and release controls

- Decide approved release platforms, packaging, signing, account/auth policy and data collection before creating any actual external resources.
- Keep signing keys, tokens, player records and deployment credentials OUT of Git; use owner-approved secure secret management and least-privilege.
- Pin dependencies and source commit; record build checksum, export/tool versions, scene import checks and reproducible packaging commands.
- Gate releases on functional/regression/security/accessibility/performance acceptance (see `TEST_MATRIX.md`); physically test selected devices.
- Stage and monitor before broader rollout; define crash/performance thresholds and abort conditions with an owner-approved rollback path.
- Require **explicit owner release decision**; the queue and CI can show candidates, but they cannot authorise deployments or payments.

## Incident playbook (for when an online service actually exists)

1. Verify incident, classify severity, contain risk to player data/security and preserve relevant *redacted* logs.
2. Identify affected release SHA, environment, devices and reproduction; isolate failed change, roll back safely when needed.
3. Repair on a short-lived branch, add regression, run CI plus relevant real engine/network/device tests.
4. Have an authorised reviewer confirm the patch and release gate; deploy only via approved process.
5. Confirm recovery, communicate accurate status to users, record lessons and update work queue/tests.

## Operations checklist for approved releases

Monitor availability, error/crash rates, auth/network abuse, latency, match completion, memory/frame-time, accessibility reports, privacy retention, licence obligations, moderation/player safety needs where applicable and capacity/cost. Document backups/restores, server version compatibility, secrets rotation, incidents and support triage. Maintain gameplay-independent rollback paths and actual verification after each patch.

M7/M8 tasks in `WORK_QUEUE.json` are **future work**, not an operational service.
