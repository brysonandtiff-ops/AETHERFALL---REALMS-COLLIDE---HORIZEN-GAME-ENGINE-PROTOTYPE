# Repository layout

## Runtime (game/)

- `project.godot`: open this file in the Godot 4 editor.
- `scenes/bootstrap/`: first screen until actual gameplay is ready.
- `scenes/characters/`: assembled character scenes with animation/controllers.
- `scenes/levels/realms/`, `hubs/`, `arenas/`: playable zones when implemented.
- `scenes/ui/`, `props/`, `vfx/`: reusable scene components.
- `scripts/core/`, `characters/`, `combat/`, `abilities/`, `levels/`, `systems/`, `ui/`: GDScript separated by responsibility.
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
- `tests/`: future Godot or asset import tests.
- `tools/validate_structure.py`: self-contained static validator.

## Boundaries

Keep saved-game data in Godot `user://`, not under the repository. Preserve model version history rather than overwriting source .blend files. Do not automatically commit private photographs, secrets, paid/licensed third-party assets or enormous binaries. Set up Git LFS deliberately if the team needs large binary files; this scaffold does not claim LFS is configured.

## File identity and no-break gate

The versioned `config/layout-contract.json` defines protected source paths and preserved roots. `tools/structure_guard.py` checks cross-platform filename hazards, existing Godot `res://` references, resource UIDs, and disallowed deletions/renames against the pull request's base commit. See [FILE_STRUCTURE_SAFETY.md](FILE_STRUCTURE_SAFETY.md). This supports additive scenes while protecting existing originals.
