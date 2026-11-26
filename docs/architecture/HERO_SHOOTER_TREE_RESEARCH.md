# AETHERFALL — Competitive hero-shooter file-tree research

**Research date:** 2026-11-26  
**Project:** AETHERFALL: REALMS COLLIDE  
**Executor:** authorised repository contributor using the connected GitHub integration  
**Scope:** Publicly observable *installed-game* files and published engine guidance, not proprietary developer source trees. No game files were downloaded or copied.

## External observations — confirmed vs unknown

| Reference | Publicly observed installation/file system | Architectural lesson | Important limit |
| --- | --- | --- | --- |
| **Overwatch 2** | Blizzard's game data uses `data/casc/` archives and associated indices; the public Overwatch support discussion identifies these client folders. | Separate content distribution and versioned data from authored source. Preserve stable hero/content identifiers and validate patchable assets. | Client CASC archives are **not** Blizzard's private development source tree. Their packaging layout is **not** a suitable Godot project template. |
| **Marvel Rivals** | Public Steam manifests expose `MarvelGame/Marvel/Content/Paks/`, alongside binaries and other runtime paths. Packed `.pak`, `.ucas`, `.utoc` files are distributed game output. | Give playable characters, maps, presentation and game systems clearly owned boundaries; maintain a separate import/build pipeline. | The published layout is **cooked Unreal client output**, not the internal authoring hierarchy; no claim about unreleased source files. |
| **Unreal Engine** | Epic documents `Config/`, `Content/`, `Plugins/`, `Source/`, `Intermediate/` and `Saved/` as ordinary Unreal project directories. | Distinguish editable source, plugins, build artifacts, configuration and generated caches. | AETHERFALL is **Godot 4.x**, so cloning Unreal directories would introduce incompatible conventions. |
| **Godot** | Official guidance recommends scene-centered organisation, assets near their owners, `snake_case` names, and `user://` for local persistent data. | Keep one Godot project and design data/scenes around match and hero responsibilities rather than adopting a foreign engine's runtime archives. | Folders alone do not prove any feature is implemented. |

## Decision: retain AETHERFALL's verified source identity

**No engine change. No mass move. No copied proprietary archives.**

- Runtime project remains `game/project.godot` (Godot 4.x).
- Editable original artwork remains in `art/`; exported assets remain in `game/assets/`.
- Existing `CHR_*` and `WPN_*` registry paths, approved visual canon and legacy hold are preserved.
- Existing scene, script, and asset paths remain stable for imports and Git history.
- This work only adds organisational boundaries and static tests. Gameplay, network services, hero selection and HUD have **not** been built.

## Additive AETHERFALL hierarchy

```text
AETHERFALL/
├── game/
│   ├── project.godot                 # Existing Godot root, unchanged
│   ├── assets/                      # Exported engine-ready characters, VFX, UI, weapons
│   ├── data/                        # Reserved definition files; currently empty
│   │   ├── heroes/                  # Future hero configuration / role metadata
│   │   ├── abilities/               # Future ability values and effect definitions
│   │   ├── modes/                   # Future match rules / objectives
│   │   └── balance/                 # Future balance tables / versioning
│   ├── scenes/
│   │   ├── characters/heroes/       # Existing assembled hero scene boundary
│   │   ├── levels/arenas/           # Existing playable arena boundary
│   │   ├── matches/                 # Future match composition
│   │   └── ui/{hero_select,hud}/    # Future player UI scenes
│   ├── scripts/
│   │   ├── abilities/               # Existing ability behavior boundary
│   │   ├── combat/                  # Existing combat behavior boundary
│   │   ├── match/                   # Future lifecycle / win conditions
│   │   ├── teams/                   # Future allegiance, team allocation
│   │   └── network/                 # Future authoritative transport/state validation
│   └── autoload/                    # Existing approved singletons only
├── art/                             # Existing original concept/Blender sources
├── docs/                            # Design, architecture, art and S.I.R.E. handoff
├── tests/
│   ├── gameplay/                    # Reserved executable gameplay/regression tests
│   └── network/                     # Reserved multiplayer/security tests
└── evidence/                        # Genuine native captures / logs by commit
```

## Future content contract (design only)

1. **Hero identity:** Reserve a unique `CHR_*` entry in `art/asset_registry.json`; do not mark an asset as present until genuine source and import evidence are available.
2. **Art:** Owner-approved references go to `art/concepts/characters/CHR_*/`; editable Blender originals go to `art/blender/characters/CHR_*/`; approved exports go to `game/assets/characters/heroes/CHR_*/`.
3. **Playable hero:** Once implemented, assemble a Godot scene under `game/scenes/characters/heroes/` and keep behavior in the relevant `game/scripts/` module. Avoid a second competing copy of character art.
4. **Gameplay definitions:** Prefer Godot-compatible `.tres` Resources in `game/data/` when typed, editor-editable data becomes necessary. Final schema/format must be established with an executable import test; no fake definitions are added here.
5. **Modes and multiplayer:** Keep match rules independent of transport. Any future network implementation must check authority, input validity, lag compensation/rollback strategy as appropriate, disconnect/rejoin behavior and misuse cases before claiming multiplayer.
6. **Naming and canonical art:** Keep existing stable asset ID directories; use lower-case `snake_case` for *new* Godot scene/script/data file names. Changes to locked visual design require owner approval.
7. **Agent/team boundary:** S.I.R.E. / AXIOM G.A.I.S. / HORIZON remain existing external governance/integration workflows. No new agent, plugin, service, credentials or live endpoints are created by this structure.

## Verification, preservation and deferred work

- Require `python3 tools/validate_structure.py` and `python3 -m unittest discover -s tests -v`; pull-request CI also attempts native headless Godot import/boot.
- Do not place Blizzard CASC archives, Marvel Rivals Unreal `.pak`/`.ucas`/`.utoc`, copied game assets, licensed content or fake screenshots in this repository.
- Do not treat reserved folders as engine features, compiled builds, multiplayer services or gameplay proof.
- When real gameplay is implemented, add genuine replayable integration tests, native screenshots/video, exact commit and engine metadata under `evidence/`. Never manufacture runtime evidence.
- Continue keeping installed-game packaging, local saves (`user://`), temporary caches and deployment builds out of the source tree. Obtain review before any destructive rearrangement.

## Public sources

1. Blizzard support, Overwatch CASC game-data directory: https://us.forums.blizzard.com/en/blizzard/t/overwatch-update-failing/15103
2. Blizzard product configuration mirror, `data/casc/` and installation branch: https://www.blizztrack.com/config/pro/pc/3ac04cec5bcdf18c4a37e0bdc3c2a6a3
3. SteamDB, Marvel Rivals public depot/file manifests: https://steamdb.info/depot/2767031/apps/
4. Epic Games, Unreal Engine project directory structure: https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-directory-structure
5. Godot, project organisation: https://docs.godotengine.org/en/stable/tutorials/best_practices/project_organization.html
6. Godot, `res://` and persistent `user://` paths: https://docs.godotengine.org/en/stable/tutorials/io/data_paths.html
