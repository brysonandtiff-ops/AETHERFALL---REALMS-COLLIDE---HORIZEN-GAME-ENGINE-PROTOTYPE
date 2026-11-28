# AETHERFALL: REALMS COLLIDE

**Status:** Repository foundation / pre-production. This is not yet a playable game.

AETHERFALL is a 3D game project intended for **Godot 4.x**, with editable character and world source art created in **Blender**. It follows the existing S.I.R.E. / HORIZON GAME ENGINE / GENESIS AI workflow; those systems are external integrations, not additional agents inside this repository.

## Open the game project

1. Clone this repository.
2. In Godot 4.x, choose **Import** and select `game/project.godot`.
3. Run the project (F5) to see the **placeholder bootstrap screen**. It confirms only that the starter scene loads; it is **not gameplay evidence**.
4. Run the offline structure check with `python3 tools/validate_structure.py` from the repository root.

Engine target for the wider S.I.R.E. workflow: **Godot 4.7.2**, pending verification in a connected native runner. This scaffold uses basic Godot 4 syntax and has not yet been opened in that engine.

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
- **Main Godot scene:** starter scene exists, native engine launch not yet verified.
- **Real characters, combat, levels, saves and multiplayer:** not implemented by this scaffold.
- **Blender/Godot screenshots and gameplay video:** not captured.
- **Real Android/iPhone/device acceptance:** not run.

No builds, deployments, merges, subscriptions or paid API calls are needed to use this foundation. Read `AGENTS.md` before modifying gameplay or locked art.

## Shadowspire design transfer and hardening

Historical Shadowspire design notes and 10 owner-selected concept characters are documented at `docs/legacy/README.md` and `docs/characters/LEGACY_ROSTER.md`. The original Godot/Unreal source is **not connected or migrated**, and no Shadowspire repository has been deleted. Two AETHERFALL-approved character IDs are preserved; eight further characters are reserved as *legacy candidates*, not models.

Run `python3 tools/validate_structure.py` and `python3 -m unittest discover -s tests -v` for fail-closed static protection and adversarial tests. GitHub's hardened workflow also verifies official, SHA-256-pinned Godot **4.7.2** and launches the starter scene **headlessly**. Only a successful actual workflow run provides that native-engine evidence, and it does **not** prove visuals, character models, actual combat or physical devices.

## Mandatory character production blueprint (proposed policy)

See `docs/characters/CHARACTER_WORKFLOW.md` for the owner-specified Vellaris-plus sheet, `docs/characters/plans/` for every registered character and `docs/characters/CHARACTER_INTAKE.md` for unresolved Razor, Raven, Corvex/Korvex and support briefs. The Vellaris uploaded PNG is **not yet committed in GitHub**, so its source-archive/production gates remain pending. An admin must enable required CI and CODEOWNERS branch protection after review.

## Infographic-first visual planning — all asset types (proposed)

Every new character, weapon, object, level, realm, building, creature, vehicle, environment, HUD or other visual design starts with the owner-approved Vellaris-format **infographic development sheet** as a *presentation template*, adapted to the asset type. See `docs/art/UNIVERSAL_INFOGRAPHIC_STANDARD.md` and `docs/art/INFOGRAPHIC_POLICY.json`. Visuals cannot silently alter locked character art, and generated sheets never count as tested runtime. Adoption requires owner review of the policy branch.

## Approved art: no-silent-drift policy

Read docs/characters/VISUAL_CANON_LOCK.md and CANON_LOCKS.json before character work. The approved Vellaris upload (39403.png) is **actually WebP**, not PNG: archive at art/concepts/characters/CHR_Vellaris_Bloodshield/Vellaris_Bloodshield_concept_v1.webp, with exact source SHA. Do not overwrite master art; all new art remains an owner-review proposal. Automatic gates verify source identity and manifest integrity; only genuine source-to-output review can verify visual fidelity.

## 1P + 3P production standards (candidate for review)

See [S.I.R.E. 1P/3P production standard](docs/pipeline/PRODUCTION_STANDARD.md) for the Blender Art Team and Gameplay AI/Engineering contract: [Blender handoff](docs/pipeline/BLENDER_ART_TEAM.md), [combat/AI states](docs/pipeline/GAMEPLAY_AI_ENGINEERING.md), [proof and platform release gates](docs/pipeline/SOVEREIGN_STAGING_AND_PROOF.md). This is **specification/staging only**; it does not add a game-ready hero, a verified first-person viewmodel, native animation tests or a released game. Existing [visual canon](docs/characters/VISUAL_CANON_LOCK.md) and [character workflow](docs/characters/CHARACTER_WORKFLOW.md) remain binding.

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

For the next safe job, run `python3 tools/aetherfall.py work new AETHERFALL-GAME-002 --team gameplay --goal "Implement one approved playable encounter" --criterion "Real native Godot capture and accepted tests"`. Use `python3 tools/aetherfall.py calls --json` to inspect **suggested upstream S.I.R.E. calls**, which are never executed automatically.

The shared S.I.R.E. software stays in its private canonical repository. See [private source integration](docs/development/SIRE_PRIVATE_SOURCE.md) for the version pin, local catalogue and authenticated-runner boundaries.
