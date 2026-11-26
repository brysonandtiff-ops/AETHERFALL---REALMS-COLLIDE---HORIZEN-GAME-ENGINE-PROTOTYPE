# AETHERFALL: REALMS COLLIDE

**START HERE: [BUILD_HERE.md](BUILD_HERE.md)** — one clear entry point for the 58-task, nine-stage build path. Run `python3 tools/production_queue.py --next` to see the next safe work packages; follow [master roadmap](docs/production/MASTER_BUILD_ROADMAP.md) and [definition of done](docs/production/DEFINITION_OF_DONE.md). **Planned tasks are not implemented features.**

**Status:** Repository foundation / pre-production. This is not yet a playable game.

AETHERFALL is a 3D game project intended for **Godot 4.x**, with editable character and world source art created in **Blender**. It follows the existing S.I.R.E. / HORIZON GAME ENGINE / GENESIS AI workflow; those systems are external integrations, not additional agents inside this repository.

## Professional AAA-style studio organisation

The current **native Godot** game is separated from editable original art, source-controlled toolchain configuration, module ownership, asset/build/QA/release lanes and real test evidence. See [the AAA studio architecture](docs/architecture/AAA_STUDIO_ARCHITECTURE.md), [machine-readable layout](studio/layout_manifest.json) and [content handoff policy](docs/production/CONTENT_HANDOFF.md). This is **not** a move to Unreal or a claim to have proprietary Blizzard source code.

## Open the game project

1. Clone this repository.
2. In Godot 4.x, choose **Import** and select `game/project.godot`.
3. Run the project (F5) to see the **placeholder bootstrap screen**. It confirms only that the starter scene loads; it is **not gameplay evidence**.
4. Run `python3 tools/validate_structure.py && python3 tools/validate_studio_layout.py && python3 tools/production_queue.py --validate && python3 -m unittest discover -s tests -v` from the repository root.
5. Run `python3 tools/production_queue.py --next` and select an unblocked work order from the actual queue.

Engine target for the wider S.I.R.E. workflow: **Godot 4.7.2**. An actual GitHub Actions job confirmed headless Godot 4.7.2 import/start for the scaffold on [PR #8](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/pull/8). That is **native headless smoke only**, not rendered gameplay, Blender model, physical-device or multiplayer verification. The latest change still requires its own CI validation.

## Repository map

| Path | Purpose |
| --- | --- |
| `game/` | Native Godot project, modular scripts, authored scenes, licensed runtime exports, audio and shaders. |
| `config/` + `studio/` | Nonsecret pinned toolchain, studio ownership and validated source/art boundaries. |
| `pipeline/` | Explicit asset ingest, build, QA and release stages (reserved; not a running build service). |
| `art/` | Editable original Blender files, concepts, high-resolution texture/audio sources. |
| `docs/` | Game design, worldbuilding, character register, **master roadmap, work queue**, technical and asset handoff guides. |
| `tools/` | Offline validation and future deterministic art/build utilities. |
| `tests/` | Test plans and future executable tests. |
| `evidence/` | Genuine engine, Blender, device, and performance capture records. |

## Character and weapon naming

Reserve asset IDs before importing finished models. Planned starter entries are **CHR_Vellaris_Bloodshield**, **CHR_ThornDell**, and **WPN_Vellaris_Bloodshield**. Existing reference imagery and approved artwork must be added from their real sources; folders are not proof that an asset exists.

Blender source belongs in `art/blender/`. Exported `.glb` assets and supporting textures belong in `game/assets/`. Do not overwrite source art or use generated images as game-engine evidence. See `docs/art/ASSET_PIPELINE.md`.

## Completion truth

- **Repository structure:** populated and checkable.
- **Main Godot scene:** starter scene exists; real Godot 4.7.2 headless import/boot was previously verified in GitHub CI. No rendered gameplay proof.
- **Real characters, combat, levels, saves and multiplayer:** not implemented by this scaffold.
- **Blender/Godot screenshots and gameplay video:** not captured.
- **Real Android/iPhone/device acceptance:** not run.

No builds, deployments, merges, subscriptions or paid API calls are needed to use this foundation. Read `AGENTS.md` before modifying gameplay or locked art.

## Protected reviews and safe continuation

Read [the repository security and branch-review guide](docs/security/REPO_HARDENING.md) before changing gameplay contracts, task status, original art or CI. The new queue-history audit and credential-pattern checks are automated, but **CODEOWNERS does not enforce review on its own**. Actual main-branch ruleset/protection requires owner-controlled GitHub configuration; it has not been independently confirmed enabled. The review PR remains unmerged pending approval.

## Shadowspire design transfer and hardening

Historical Shadowspire design notes and 10 owner-selected concept characters are documented at `docs/legacy/README.md` and `docs/characters/LEGACY_ROSTER.md`. The original Godot/Unreal source is **not connected or migrated**, and no Shadowspire repository has been deleted. Two AETHERFALL-approved character IDs are preserved; eight further characters are reserved as *legacy candidates*, not models.

Run `python3 tools/validate_structure.py`, `python3 tools/production_queue.py --validate` and `python3 -m unittest discover -s tests -v` for fail-closed structure/plan protection and adversarial tests. GitHub's hardened workflow also verifies official, SHA-256-pinned Godot **4.7.2** and launches the starter scene **headlessly**. Only a successful actual workflow run provides that native-engine evidence, and it does **not** prove visuals, character models, actual combat or physical devices.
