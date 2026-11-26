# Repository layout

## Runtime (game/)

- `project.godot`: open this file in the Godot 4 editor.
- `scenes/bootstrap/`: first screen until actual gameplay is ready.
- `scenes/characters/`: assembled character scenes with animation/controllers.
- `scenes/levels/realms/`, `hubs/`, `arenas/`: playable zones when implemented.
- `scenes/ui/`, `props/`, `vfx/`: reusable scene components.
- `scenes/ui/hero_select/`, `scenes/ui/hud/`, `scenes/matches/`: reserved hero selection, HUD and match assembly scenes; not implemented.
- `scripts/core/`, `characters/`, `combat/`, `abilities/`, `levels/`, `systems/`, `ui/`: GDScript separated by responsibility.
- `scripts/match/`, `scripts/teams/`, `scripts/network/`: reserved match lifecycle, team rules and multiplayer authority boundaries. No networking is implemented.
- `data/heroes/`, `data/abilities/`, `data/modes/`, `data/balance/`: reserved versioned gameplay definitions, separate from original concept art and Blender assets.
- `autoload/`: approved global managers only; no default singleton invented.
- `assets/`: exported GLBs and textures referenced by Godot scenes.
- `audio/`, `shaders/`: runtime sound and shader code.

## Editable source (art/)

- `concepts/`: approved model sheets, turnarounds, world/weapon references.
- `blender/`: source .blend projects, rigs, environments, weapons and meshes.
- `textures/source/`, `audio/source/`: editable source and high-resolution masters.
- `asset_registry.json`: each reserved asset ID, source path and runtime location.

## Review, proof and tools

- `docs/`: design decisions and workflows.
- `evidence/`: genuine original engine, Blender, device and performance captures, plus hashes and capture notes.
- `tests/`: source validators, plus reserved gameplay/network regression suites; future actual Godot gameplay tests still required.
- `docs/architecture/HERO_SHOOTER_TREE_RESEARCH.md`: public Overwatch 2 / Marvel Rivals installation-tree comparison, Godot-specific adaptation and ownership rules.
- `tools/validate_structure.py`: self-contained static validator.

## Boundaries

Keep saved-game data in Godot `user://`, not under the repository. Preserve model version history rather than overwriting source .blend files. Do not automatically commit private photographs, secrets, paid/licensed third-party assets or enormous binaries. Set up Git LFS deliberately if the team needs large binary files; this scaffold does not claim LFS is configured.

## Hero-shooter module ownership (pre-production)

- `art/` owns original approved concepts and editable `.blend` files; `art/asset_registry.json` is the current identity/status register.
- `game/assets/characters/heroes/CHR_*` owns eventual imported runtime visual assets. Keep stable `CHR_*` IDs, but use `snake_case` for new Godot file names and do not rename existing paths casually.
- `game/scenes/characters/heroes/` owns eventual assembled hero scenes; `game/scripts/abilities/` and `game/data/abilities/` keep behavior and tuning definitions separate.
- `game/scripts/network/` is the future boundary for authoritative multiplayer code; never store tokens, matchmaking credentials or real player records in Git.
- All new folders are **reserved paths only**, not claims of hero implementations, networking, UI, builds or runtime test passes. Use PR review and the required native tests before linking features.

## AAA studio organisation — additive architecture only

See [AAA_STUDIO_ARCHITECTURE.md](AAA_STUDIO_ARCHITECTURE.md) and the machine-owned `../../studio/layout_manifest.json`. Native Godot `game/` remains the **only** runtime project; `game/scripts/` replaces Unreal's conceptual Source responsibility, `game/scenes/`+`data/`+`assets/` replace Content, `game/addons/` corresponds to approved Plugins, and `config/`+`pipeline/`+`tools/` cover nonsecret configuration and build/QA/release automation. None of those folders implies Unreal was installed.

`art/` holds canonical editable masters and references; `game/assets/` holds tested exports only. New `art/ui/`, `art/vfx/`, `art/storyboards/`, `game/localization/`, `game/scripts/ai/`, `input/`, `save/`, `telemetry/`, and `game/scenes/cinematics/` are reserved domains, not completed features.

Generated caches (`game/.godot/`, `game/.import/`, `build/`, `dist/`, `pipeline/.cache/`) are never a source-of-truth. Team asset handoffs follow `../production/CONTENT_HANDOFF.md` and real PR/build lanes follow `../production/BUILD_TRAINS.md`. All existing `CHR_*`, Godot UIDs, canonical original art and existing game paths remain unchanged.
