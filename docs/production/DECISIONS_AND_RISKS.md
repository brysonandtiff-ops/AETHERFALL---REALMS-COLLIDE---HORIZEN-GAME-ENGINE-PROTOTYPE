# Owner decisions, risks and constraints

These are **unresolved decision gates** and engineering risks, not assumptions. The queue isolates work so unrelated tasks remain actionable.

## Decisions to record before dependent implementation

| Decision | Needed for | Owner decision / current truth |
| --- | --- | --- |
| Game core (hero-shooter match vs other mode) and win condition | AF-001, M1/M2 | Character roles are discussed; final ruleset not signed off in repository. |
| First-person vs third-person camera, PC/mobile/controller and target FPS | AF-001, AF-010, testing | Godot placeholder uses 1280×720; not proof of production target or platform. |
| Team size, role limit, combat rules and initial arena | AF-001, AF-024/025 | Not approved here; do not copy OW2/Marvel Rivals rules wholesale. |
| Canonical hero IDs and approvals | AF-003, AF-020/021/022, AF-040 | `CHR_ThornDell` and `CHR_Vellaris_Bloodshield` in registry; historical `CHR_Korvex` vs requested "Corvex" needs explicit identity decision; Razor/Raven require formal registration when approved. |
| Art usage, original owner photos, third-party licensing and credits | AF-002/040 | Protect approval locks and provenance; do not clone commercial hero designs. |
| Network topology, hosting, geographic region and data retention | AF-030/036 | No servers or credentials are provisioned by a folder. Owner must approve cost and privacy. |
| Supported platforms, distribution, accounts and age-safety requirements | AF-001, M5–M7 | Not fixed in the repository; defer packaging and release claims. |
| Git LFS / asset storage budget and backup retention | AF-004 | `.gitattributes` currently does not establish approved LFS binary policy; no automatic large-binary commits. |
| Final release, paid integrations, signing and spending | M7 | Always explicit owner authorisation. |

## Prioritised risk register

| Risk | Likelihood/impact | Mitigation and stop condition |
| --- | --- | --- |
| Scope expands to full live-service roster before the first working match | High / High | Gate M2 first; use one tank + DPS + support; backlog other characters. |
| Unavailable or wrong original art | High / High | Never substitute generated art as runtime proof; mark task BLOCKED until authentic approved source is received. |
| Frame-time collapse from unbudgeted hero VFX or map complexity | Medium / High | Establish baseline M1 and profile each integrated asset/arena before expansion. |
| Multiplayer cheats/desync/disconnect corruption | High / High | Server authority + protocol abuse/failure tests are M3 release gates; no client-authoritative damage. |
| Unlicensed art/audio or private owner photos committed publicly | Medium / Critical | Rights ledger, canonical visual protection, explicit approval; block file until cleared. |
| CI passes but gameplay or device fails | High / High | Layer true native functional, graphical and device proof; don't promote smoke to playable. |
| Breaking scene paths, registry IDs or model source files during cleanup | Medium / High | Preserve existing IDs and Godot resource paths; require migration/rollback tests. |
| Incomplete release/patch recovery | Medium / High | Rollback rehearsals, build hashes and backup restore before release. |
| Unauthorized cost, automation, data collection or deployment | Medium / Critical | Explicit owner decisions; no silent agent creation, service provisioning or spending. |

## Decision log format

For each owner-approved change add a dated entry in a PR/issue: **ID → choices considered → decision → owner/authorised approver → impacted work items → exact reference/canon approval → rollback → source commit**. Do not record a decision as approved merely because it appears as an idea in chat.
