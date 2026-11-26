# AETHERFALL: REALMS COLLIDE

**Status:** Repository foundation / pre-production. This is not yet a playable game.

AETHERFALL is a 3D game project intended for **Godot 4.x**, with editable character and world source art created in **Blender**. It follows the existing S.I.R.E. / HORIZON GAME ENGINE / GENESIS AI workflow; those systems are external integrations, not additional agents inside this repository.

## Open the game project

1. Clone this repository.
2. In Godot 4.x, choose **Import** and select `game/project.godot`.
3. Run the project (F5) to see the **placeholder bootstrap screen**. It confirms only that the starter scene loads; it is **not gameplay evidence**.
4. Run the offline structure check with `python3 tools/validate_structure.py` from the repository root.

Godot target: **4.7.2**. The repository's prior CI run verified a real native *headless* import and five-frame startup. This does **not** establish a graphical playtest, completed character assets, animations or a physical-device build.

## Repository map

| Path | Purpose |
| --- | --- |
| `game/` | Standalone Godot project, scenes, GDScript, imported runtime assets, audio, shaders. |
| `art/` | Editable original Blender files, concepts, high-resolution texture/audio sources. |
| `docs/` | Game design, worldbuilding, character register, technical and asset handoff guides. |
| `tools/` | Offline validation and future deterministic art/build utilities. |
| `tests/` | Test plans and future executable tests. |
| `evidence/` | Genuine engine, Blender, device, and performance capture records. |

## Character and weapon naming

Reserve asset IDs before importing finished models. Planned starter entries are **CHR_Vellaris_Bloodshield**, **CHR_ThornDell**, and **WPN_Vellaris_Bloodshield**. Existing reference imagery and approved artwork must be added from their real sources; folders are not proof that an asset exists.

Blender source belongs in `art/blender/`. Exported `.glb` assets and supporting textures belong in `game/assets/`. Do not overwrite source art or use generated images as game-engine evidence. See `docs/art/ASSET_PIPELINE.md`.

## Completion truth

- **Repository structure:** populated and checkable.
- **Main Godot scene:** prior CI verified native headless import and five-frame boot; graphical gameplay not yet verified.
- **Real characters, combat, levels, saves and multiplayer:** not implemented by this scaffold.
- **Blender/Godot screenshots and gameplay video:** not captured.
- **Real Android/iPhone/device acceptance:** not run.

No builds, deployments, merges, subscriptions or paid API calls are needed to use this foundation. Read `AGENTS.md` before modifying gameplay or locked art.

## Shadowspire design transfer and hardening

Historical Shadowspire design notes and 10 owner-selected concept characters are documented at `docs/legacy/README.md` and `docs/characters/LEGACY_ROSTER.md`. The original Godot/Unreal source is **not connected or migrated**, and no Shadowspire repository has been deleted. Two AETHERFALL-approved character IDs are preserved; eight further characters are reserved as *legacy candidates*, not models.

Run `python3 tools/validate_structure.py` and `python3 -m unittest discover -s tests -v` for fail-closed static protection and adversarial tests. GitHub's hardened workflow also verifies official, SHA-256-pinned Godot **4.7.2** and launches the starter scene **headlessly**. Only a successful actual workflow run provides that native-engine evidence, and it does **not** prove visuals, character models, actual combat or physical devices.

## Daily development with S.I.R.E. (configuration pending review)

This work lives on a development branch until its tests pass and it is reviewed. Once approved, use:

```sh
python3 tools/aetherfall.py doctor
python3 tools/aetherfall.py routes
python3 tools/aetherfall.py work list
python3 tools/aetherfall.py cmd T
python3 tools/aetherfall.py check
python3 tools/aetherfall.py handoff AETHERFALL-DEVOPS-001 --json
```

`handoff` is **a safe JSON proposal**, never a remote call. The existing S.I.R.E AI master, GENESIS AI/HORIZON, Git/permission stewards and MCP/Plugin services remain external, and are **NOT_CONNECTED** until a real authorised session proves otherwise.

Read [START HERE](docs/development/START_HERE.md) and [S.I.R.E. integration boundaries](docs/development/SIRE_INTEGRATION.md). The CI job on pull requests runs standard-library tests plus a genuine official Godot 4.7.2 **headless** startup. This does not produce native visual/device evidence or automatically merge or deploy anything.
