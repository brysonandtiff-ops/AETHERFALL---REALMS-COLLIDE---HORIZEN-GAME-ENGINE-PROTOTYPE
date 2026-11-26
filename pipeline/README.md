# AAA production pipeline — RESERVED, not an operating build farm

**Source-of-truth executables:** `../tools/` contains current actual validators. `pipeline/` reserves distinct studio lanes and explicit handoffs; no pipeline lane currently runs a full art/packaging system.

| Lane | Goal when implemented | Required input and gate |
| --- | --- | --- |
| `asset_ingest/` | Review rights, original master, GLB export, import metadata, hashes | Original owner-approved reference + source model + asset registry ID |
| `build/` | Deterministic native Godot import/export and build manifests | Verified engine version, no credentials in repo, tested content |
| `qa/` | Automated gameplay, integration, network, accessibility and performance suites | Real scenes, replayable tests and genuine logs/captures |
| `release/` | Reproducible candidates, signing, rollback drill and staged distribution | Owner go/no-go, external signing, target-device and security acceptance |

**Never claim operational lanes by creating empty folders.** Keep generated binaries in ignored `build/` and `dist/`, native `.godot/` generated cache untracked, and actual player saves under Godot `user://`. See `../docs/production/BUILD_TRAINS.md`.
