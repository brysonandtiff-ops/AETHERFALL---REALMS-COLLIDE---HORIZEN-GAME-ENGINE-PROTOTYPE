# AETHERFALL — Canonical Android Game Storage Law
**ID:** AF-LOCAL-STORAGE-001
**Owner decision:** 26 November 2026 (Australia/Perth)
**Project:** AETHERFALL: REALMS COLLIDE
**Status:** Owner-authorised governance rule; Android write verification still pending.

## Rule
Every AETHERFALL game artifact intended for the owner's Android phone—characters, weapons, art, concepts, builds, scripts, audio, scenes, VFX, testing, captures, logs, and versioned delivery packages—must be filed **under the one AETHERFALL folder already present in Internal storage**, shown in the owner's 26 November screenshots as `AETHERFALL – REALMS COLIDE`.

Keep the **existing directory entry and spelling**, including any one-L spelling of COLIDE. Inspect the real device directory before copying. **Never create a duplicate nearby folder with a corrected project name.** Preserve the `korvex_blockout_v01/` folder already shown there, as well as every other pre-existing file. Never delete, rename, overwrite, or move legacy items without a separate owner-approved migration and verified backups.

## Source-control relationship
The connected AETHERFALL GitHub repository remains the canonical *version-controlled source* for code, configuration, work orders and tracked editable assets, following `AGENTS.md` and `docs/art/ASSET_PIPELINE.md`. The phone root is the mandatory local owner-facing *delivery/workspace mirror*. Neither GitHub, ChatGPT sandbox nor Library uploads prove that Android storage has been updated.

## New-file layout inside the existing phone root
```text
<existing AETHERFALL Android folder>/
  korvex_blockout_v01/           # existing: preserve, do not touch
  00_GOVERNANCE/
  01_CHARACTERS/
    TANKS/
    DAMAGE/RAZOR/v0.1.0/{models,source,reference,evidence,docs}/
    DAMAGE/RAVEN/v0.1.0/{models,source,reference,evidence,docs}/
    SUPPORTS/
  02_GAME_AND_ENGINE/
  03_WORLD_AND_ART/
  04_SOUND_AND_VFX/
  05_TESTS_AND_PROOF/
  90_INCOMING_UNVERIFIED/
  99_BACKUPS_AND_ARCHIVES/
```

## Enforcement
1. For every new game deliverable, assign an asset ID, provenance and version; save it within the above project root, NOT as an uncategorised permanent Download.
2. Include owner-approved art/reference IDs; exported filenames, sha256 checksums, source generator/revision, valid stage label, test results and proof locations. Do not call generated art gameplay proof or a raw GLB an approved game-ready character.
3. If Android access is absent or tool usage is exhausted, produce a **transfer-ready ZIP whose entries are relative to the existing phone root**; label status `TRANSFER_REQUIRED / NOT_ON_PHONE`, keep the file accessible and explicitly disclose that the phone copy is unverified.
4. On connection, inspect the actual local directory first, copy without replacing owner files, then **read back size and SHA-256**. Set `SAVED_ON_PHONE=true` only after an authorised device check or owner confirmation.
5. Preserve source history, existing art locks, project IDs, Godot UIDs and backups. The rule does not authorise merging/deploying, destructive changes or creating substitute agents.

## This work order
`AETHERFALL-DAMAGE-RAZOR-RAVEN-001`: Build separated real 3D **blockout** GLBs for four-legged Razor and hooded Raven, plus detachable harpoon/Omen Loom and corvid prop, genuine offline GLB views, generators and integrity manifest. Blender, animation, finished sculpt, native Godot playtests and Android copy are later gates.

## Acceptance
- A reproducible, versioned package exists with manifest, real model screenshots, source and checksums.
- Phone transfer is explicitly `PENDING` until a connected executor checks the actual existing folder.
- No unrelated repository paths, game files or the existing Korvex folder are modified.

**Governance scope:** This is an AETHERFALL project routing law, not an unverified installation of a new global S.I.R.E. master law.