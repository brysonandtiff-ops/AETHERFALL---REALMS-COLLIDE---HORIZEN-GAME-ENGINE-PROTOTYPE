# AETHERFALL — PROFESSIONAL AAA STUDIO REPOSITORY ARCHITECTURE

**Status:** A reviewable Godot 4.x studio structure, not a claim to match Blizzard's private source repositories or to have Unreal runtime code.  
**Approved engine boundary:** native `game/project.godot` remains the executable project; `Blender` is the source-art DCC.  
**Machine contract:** `studio/layout_manifest.json` + `config/toolchain.json` + `tools/validate_studio_layout.py`.

## Research-backed comparison

Official Unreal documentation distinguishes `Config/`, `Content/`, `Source/`, `Plugins/`, `Build/` and generated `Intermediate/`, `DerivedDataCache/`, `Saved/` and `Binaries/`. Epic also describes modular feature ownership and binary asset locking/workflows for larger teams. Godot has a different resource model, and its official guidance favours scene-centred ownership, stable names and avoiding imported cache in version control.

**We adopt the production *separation of concerns*, not Unreal-specific .uproject, UObjects, .uassets, .umaps, C++ build scripts, or proprietary Blizzard/Marvel assets.** An actual Unreal port must be approved as a separate project change.

| Unreal/studio idea | Where AETHERFALL implements that responsibility | Truth |
| --- | --- | --- |
| `Source/` gameplay modules | `game/scripts/`, split core/characters/combat/abilities/match/teams/network/AI/input/save/UI | Paths only; no finished gameplay |
| `Content/` runtime packages | `game/scenes/`, `game/data/`, `game/assets/`, `game/audio/`, `game/shaders/` | Real Godot root maintained |
| `Plugins/` and modular features | `game/addons/` for vetted Godot plugins; module boundaries in `studio/layout_manifest.json` | No add-ons installed |
| `Config/` project defaults | `game/project.godot` (native) + `config/toolchain.json` (studio toolchain) | Not a second engine config |
| `Build/` scripts, content packaging | Executables in `tools/`; stage contracts under `pipeline/`; CI in `.github/workflows/` | Headless smoke and source tests exist; full exporters don't |
| `Intermediate/`, `Saved/`, `DerivedDataCache/`, `Binaries/` | Godot `.godot/` and local generated files, ignored `build/` and `dist/`; player saves in `user://` | Never commit transient state |
| Perforce/Git LFS binary asset tracking | Original Blender in `art/`; git + binary attributes; LFS/Perforce only by approved migration | Neither LFS nor Perforce configured |

## Canonical repository tree

```text
AETHERFALL/
├── .github/                  # CI, PR templates, code ownership; GitHub rules remain separate
├── BUILD_HERE.md             # Single first-stop instructions
├── AGENTS.md                 # Existing S.I.R.E. task governance
├── config/                   # Nonsecret version/toolchain definitions
│   └── toolchain.json
├── studio/                   # Machine-enforced domain ownership and layout
│   └── layout_manifest.json
├── game/                     # GODOT NATIVE PROJECT (unchanged project.godot)
│   ├── project.godot
│   ├── addons/               # Reviewed Godot add-ons only; none installed
│   ├── autoload/             # Explicitly approved singletons only
│   ├── data/                 # Typed future heroes/abilities/modes/balance definitions
│   ├── scripts/              # Systems: core, input, combat, heroes, AI, net, save, UI
│   ├── scenes/               # Boot, hero scenes, real match modes, arenas, UI, cinematics
│   ├── assets/               # Only engine-ready approved exports (GLB, textures, VFX)
│   ├── audio/                # Engine-ready runtime tracks
│   ├── localization/         # Future vetted in-game translations
│   └── shaders/              # Godot-compatible shader sources
├── art/                      # OWNER-APPROVED EDITABLE MASTER ART
│   ├── asset_registry.json   # Authoritative stable CHR_ / WPN_ IDs
│   ├── concepts/             # Canonical sheets / diagrams / character and world references
│   ├── blender/              # Original models, rigs, environment sources and versions
│   ├── textures/source/      # Original texture masters
│   ├── audio/source/         # Original audio masters
│   ├── storyboards/          # Future cinematics story sources
│   ├── ui/                   # Future editable interface design sources
│   └── vfx/                  # Future editable effects sources
├── pipeline/                 # Documented asset ingest, build, QA, release lanes
├── docs/                     # Game, world, architecture, source-rights and production canon
├── tools/                    # Real Python validators; future deterministic build tooling
├── tests/                    # Source, engine, gameplay, network, acceptance
└── evidence/                 # GENUINE capture/log/checksum, with exact source SHA
```

## Boundaries and dependency rules

**The game engine does not depend on studio/production files at runtime.** `game/` is the single loadable Godot project, not a duplicate codebase. `pipeline/` calls `tools/` but doesn't become a separate master AI system. `config/` is versioned and non-secret; encrypted signing, secrets, paid backend and player data are never committed.

- **Gameplay:** `core` supplies primitives; `input`/characters/combat/abilities use well-defined interfaces; `match` + `teams` own win/rules; `network` owns validation/replication, never game balance. Future real code requires tests for authority, input and rollback.
- **Art:** `art/` is editable master/approved concept, `game/assets/` is exported engine-ready product. The asset registry is canonical for identities. Do not move current `CHR_* / WPN_*` folders or rename Godot resources without migration and regression tests.
- **World/UI:** `game/scenes/levels/` owns assembled arenas, `game/scenes/ui/` owns screens; runtime art reused from `game/assets/`. Future scene-centred packages may group dependent assets near their owner after deliberate migration tests.
- **DCC/engine:** Native Blender outputs, GLB export, Godot import, rig/animation, device capture and checksum must be individually verified. Source-art folders, future support characters and empty scenes are not finished features.
- **Code review:** Game systems, IDs, CI, plugins, source art and build config have declared CODEOWNERS. Real branch protection and independent review are **not** activated simply by this file.
- **Scale:** For concurrent heavy binary art, approve LFS or Perforce (including file-locking), backups, review costs and migration plan first. Git alone without LFS is *not* equivalent to a staffed AAA depot.

## Deterministic validation and team interfaces

```sh
python3 tools/validate_structure.py
python3 tools/validate_studio_layout.py
python3 tools/production_queue.py --validate
python3 -m unittest discover -s tests -v
```

- `studio/layout_manifest.json` enumerates exactly who owns runtime and source boundaries. The contract validator rejects missing zones/modules, unsafe paths and engine identity mismatches.
- Source/secret scanners, protected-art rules and queue-history audits remain active. External rights/privacy and real runtime acceptance still require people and native tools.
- See [content handoff](../production/CONTENT_HANDOFF.md), [build trains](../production/BUILD_TRAINS.md), [source art pipeline](../art/ASSET_PIPELINE.md) and [release/operations](../production/RELEASE_AND_OPERATIONS.md).

## Primary public references

1. Unreal Directory Structure (Epic Games): https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-directory-structure
2. Game Features / Modular Gameplay (Epic Games): https://dev.epicgames.com/documentation/unreal-engine/game-features-and-modular-gameplay-in-unreal-engine
3. Unreal Perforce Source Control (Epic Games): https://dev.epicgames.com/documentation/en-us/unreal-engine/using-perforce-as-source-control-for-unreal-engine
4. Godot Project Organization (Godot): https://docs.godotengine.org/en/stable/tutorials/best_practices/project_organization.html
5. Godot Version Control (Godot): https://docs.godotengine.org/en/stable/tutorials/best_practices/version_control_systems.html

## Canonical source and review history

The art registry is **append-only** by default across review branches: `tools/audit_asset_history.py` compares to target-branch truth and blocks deleted/relabelled character identities and deleted original `art/` or `evidence/` files. A future approved edit that truly needs to move source art requires a documented full migration and separately reviewed policy change; static structure is not authority to delete originals.

## Refinement: operational asset custody, not a decorative structure

Original concept → Blender source → Godot GLB export → Godot import review is now represented by structured, file-hashed receipts under `art/handoffs/`, and validated using `tools/validate_asset_handoffs.py`. Existing registered IDs and source paths remain immutable. `tools/studio_preflight.py` gives all disciplines a single real local validation entry point. The receipt and preflight are **source-level workflows**, not a full-scale Perforce depot, automatic asset exporter, rendered demo or proof that any character is playable.
