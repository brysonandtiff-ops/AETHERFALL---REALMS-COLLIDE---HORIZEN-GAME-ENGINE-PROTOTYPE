# Test and evidence matrix by build stage

**Always:** `python3 tools/validate_structure.py` + `python3 tools/production_queue.py --validate` + `python3 -m unittest discover -s tests -v` on review branches. Their success proves only source and plan integrity.

| Stage | Functional/integration tests | Security/regression | Genuine runtime evidence / tool |
| --- | --- | --- | --- |
| M0 | Godot 4.7.2 clean import/start, toolchain/setup and backup restore, schema fixture parse | Credential/path/rights checks, malicious registry values, cache isolation | Official Godot headless engine logs (not UI). Blender version output when configured |
| M1 | Movement, collision, hit detection, health, death, ability costs/cooldown and match primitive tests | Invalid targets, no double-damage, missing resources, restart/scene exit | Actual Godot in-game controls and debug HUD, frame-time baseline |
| M2 | Tank/DPS/support ability kit, team heal/damage, hero selection, objective score, complete match | Wrong-team healing, stale ability state, match restart/resume and UI navigation | Genuine full local match video; interaction capture; accessible HUD |
| M3 | Real 2+ independent client sessions, replication, prediction, leave/rejoin, authority | Packet abuse, replay, invalid client damage, rate limits, secret redaction, latency/jitter and loss | Server and client logs, measured packet/latency results, actual multi-client video |
| M4 | Blender rig/UV/animation/LOD/export and native Godot import; scene collision | Source hashes, approved art comparison, rights/attribution, GPU/material budgets | Native Blender four-view renders and rig playback, Godot in-game visual captures |
| M5 | Save/load/migration, controller/input mapping, settings, tutorial, role clarity | Corrupt saves, privacy minimisation, UI accessibility, crash/soak/regression | Target hardware FPS/frame time/memory, usability and accessibility report |
| M6 | Actual export/install/update/reinstall and cross-platform matrix; multi-device soak and load | Signing, auth, privacy/ratings/rights, incident and rollback exercise | Actual device screens/video and install logs for approved release platforms |
| M7 | Signed release candidate and rollback smoke | Go/no-go, sensitive config review, supply-chain and server rollback | Exact build hash, approval log, deployed version proof if approved |
| M8 | Bug reproductions and non-regression on every patch | Exploit mitigations, data safety, incident response and backup restore | Real hotfix evidence, incident reports, post-release metrics |

## Typical failure injection required before shipping

Missing asset, wrong case, corrupt Godot resource, doubled health change, invalid team target, disconnect mid-ultimate, duplicate/late packets, gameplay restart, scene unload, process crash, save corruption, low memory, UI focus loss and accessibility navigation failures. Add them as automated tests where possible; document any manual verification.

**Device truth:** simulated latency/headless tests are not physical-phone/device acceptance. No screenshots or generated animation may be represented as a real engine capture. Only claim the exact tests run and pass at the referenced commit.
