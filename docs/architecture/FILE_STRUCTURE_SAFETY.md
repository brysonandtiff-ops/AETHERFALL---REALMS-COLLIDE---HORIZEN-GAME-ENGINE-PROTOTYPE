# AETHERFALL — File Structure Safety Contract

**Policy:** Additive development by default. No destructive migration, silent character-ID rename or overwriting original art.

## Stable boundaries

- `game/` is the one Godot 4.7.2 runtime project; `game/project.godot` stays the import entry. New scene, script, shader and exported game assets go under their existing categories.
- `art/` owns original designs, `.blend` source, high-resolution texture masters, rigs and design history. `game/assets/` owns approved runtime exports (e.g. `.glb`), **not** the only original copy.
- `art/asset_registry.json` owns stable IDs and source/runtime paths. Existing character IDs including `CHR_ThornDell` and `CHR_Vellaris_Bloodshield` must not drift. New approved characters can be added with their own paths.
- `evidence/` stores **genuine** untouched captured proof. Unavailable graphical, Blender or device evidence remains NOT_RUN/BLOCKED.
- `.sire/` stores work orders/skill definitions, not a second running S.I.R.E. master. Commands never grant agents, permissions or subscriptions by text alone.
- `config/layout-contract.json` protects canonical paths and identity fields; `tools/structure_guard.py` checks the working tree and base-to-head changes.

## What the checks reject

1. Missing or moved protected files; missing reserved roots.
2. File names incompatible with Windows/Linux (reserved device names, trailing spaces or periods, case collisions, unnormalised Unicode, control characters, extreme lengths, symbolic links).
3. Broken **literal** `res://` links in Godot scenes, resources, scripts, shaders and project settings; duplicate scene/script UIDs; orphan `.gd.uid` files.
4. A second nested Godot project under `game/`, tracked caches or generated packages.
5. On PRs, deleted tracked art, scene, script, work-order or evidence sources (except unnecessary `.gitkeep`), removed asset IDs, changed stable source/runtime paths or a changed main-scene path.
6. A PR that tries to weaken the *base version* of this contract.

These are source-level checks, not a substitute for real engine import, animation or gameplay testing. Dynamic `res://` paths are intentionally not inferred; genuine Godot execution must cover those.

## Workflow

```sh
python3 tools/aetherfall.py doctor
python3 tools/structure_guard.py check
python3 tools/aetherfall.py check
python3 tools/structure_guard.py diff --base <trusted-40-character-ancestor-SHA>
```

On pull requests, CI fetches the base commit and verifies the file delta; the native Godot CI job separately imports and boots the game with pinned Godot 4.7.2. The contract initially enters on a draft PR, so the first diff uses the new contract for bootstrap. Later changes compare against the existing policy from the base revision.

## If a move or deletion is actually necessary

**Do not bypass the guard, force push, wipe folders or change the old asset ID silently.** Raise a separate approved migration work order with old/new paths, why, all references and importers to update, original-content backup/hashes, exact commit, full test plan, and rollback. The safety guard intentionally blocks breaking changes until a separately reviewed rule/migration is approved; editing its own config in the same PR must not silently weaken earlier protections.

Owner and independent reviewers should check the change. GitHub CODEOWNERS is a review signal; **branch rules must be enabled separately** to enforce review before merge. A green static test does not prove the project will survive runtime gameplay or packaging.

## Owner-facing proof labels

- **SOURCE PASS:** Scripts and static Godot references satisfy available checks.
- **NATIVE HEADLESS PASS:** A real Godot executable imported and started the exact source.
- **VISUAL/DEVICE PASS:** Only after original screenshots/video, source SHA, engine/device ID and independent review.
- **RELEASE:** Separate gate; never inferred from this file structure.
