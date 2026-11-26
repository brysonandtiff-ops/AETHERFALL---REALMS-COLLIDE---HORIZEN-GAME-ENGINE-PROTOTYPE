# AETHERFALL: REALMS COLLIDE — staged-media audit (26 November 2026)

**Work order:** AF-ASSET-STAGING-AUDIT-20261126  
**Goal:** inventory and organise existing AETHERFALL concepts, GLB blockouts and MP4 previews without losing canonical art.  
**Authorised executor:** ChatGPT staging file auditor (Python/trimesh/Pillow/ffprobe/ffmpeg/zipfile); GitHub tool for this documentation commit.  
**Source scope:** original ChatGPT Library files and previously prepared AETHERFALL asset atlas. **NOT** the user's Android/PC Downloads folder.  
**Status:** Source staging audited and packaged; device Downloads audit blocked by Remote Desktop Commander monthly quota.  
**Acceptance:** verified file inventory, preserved originals, segregated unapproved artwork, no false engine/phone claims; remaining device intake explicitly open.

## Observed external media (not currently imported into this repository)

| Character | Real files found outside repo | Verification status |
| --- | --- | --- |
| Razor | `CHR_Razor_HuntArchon.glb`, `WPN_Razor_ChainHarpoon.glb`, `SCENE_Razor_Preview.glb`; turntable MP4; artwork/references | Real 3D procedural blockout, not rigged or engine-verified |
| Raven | `CHR_Raven_EchoWeaver.glb`, `WPN_Raven_OmenLoom.glb`, `PROP_Raven_CorvidEcho.glb`, `SCENE_Raven_Preview.glb`; turntable MP4; artwork/references | Real 3D procedural blockout, not rigged or engine-verified |
| ThornDell (Thorndell filename) | `CHR_Thorndell_Venomroot.glb`, `WPN_Thorndell_RootBulwark.glb`, `39408.mp4`; offline GLB screenshots | Real 3D blockout, not rigged or engine-verified |
| Korvex | Three distinct PNG concept boards | Concept-only **in accessible staging**; existing phone `korvex_blockout_v01/` still requires direct inspection |
| Vellaris | Approved concept and reserved asset ID documented here | Original media not accessible in audited staging; no valid reason to mark model present |
| Dreadhull, Morrigan, Pixi, Noxis, Orion, Temporis, Symbion | Reserved legacy candidates | No GLBs confirmed in this accessible audit |

**Counts:** 9 GLBs (3 character + 3 weapon + 1 prop + 2 assembled preview scenes); 3 MP4s (3 seconds each); 6 standalone PNG concept boards (3 Korvex, 3 shared Razor/Raven); 13 actual *offline* GLB screenshots. Three untouched Razor/Raven source ZIPs archived. The nine GLBs are **not nine character models**.

## Independently run audits

- SHA-256 comparisons for **43/43** entries in the earlier atlas manifest: **PASS**.
- GLB headers, binary length, JSON metadata and geometry readback: **9/9 PASS**.
- All 9 GLBs have **zero skin and zero animation objects** in their glTF metadata: do not mark as rigged.
- MP4 full video decode: **3/3 PASS**; no footage establishes gameplay.
- Original ZIP CRC/safe-path checks: **3/3 PASS**.
- Razor/Raven `offline_tests.py` rerun in an isolated copy: **31/31 PASS**, exit code 0.
- Found one exact SHA-256 image duplication: the `Razor_Raven_Exploration_UNAPPROVED.png` is byte-identical to `Aetherfall Damage Heroes: Razor and Raven.png`. Both original names preserved; explicitly unapproved artwork segregated, not promoted to canon.
- Native Blender, Godot graphical/runtime, phone Downloads readback and physical-device tests: **NOT PERFORMED**.

## Organised staging handoff

Prepared separately as `AETHERFALL_AUDITED_STAGING_2026-11-26.zip` (not pushed into GitHub because source binaries should follow reviewed import/provenance). Internal structure:

```text
00_GOVERNANCE/
01_CHARACTERS/DAMAGE/{RAZOR,RAVEN}/v0.1.0/{models,evidence,reference,docs}/
01_CHARACTERS/TANKS/THORNDELL/v0.1.0/{models,evidence}/
01_CHARACTERS/TANKS/KORVEX/v0.1.0/concepts/
01_CHARACTERS/TANKS/VELLARIS/STATUS.md
02_GAME_AND_ENGINE/{RAZOR_RAVEN_PROCEDURAL_SOURCE,UNRUN_GODOT_IMPORT_TEST}/
03_WORLD_AND_ART/{SHARED_RAZOR_RAVEN_CONCEPTS,OWNER_REFERENCES}/
04_VISUAL_ATLAS/
05_TESTS_AND_PROOF/{AUDIT_REPORT.md,AUDIT.json,INVENTORY.csv,SHA256SUMS.txt,...}/
90_INCOMING_UNVERIFIED/
99_BACKUPS_AND_ORIGINAL_ARCHIVES/
```

**Do not extract indiscriminately over an existing phone folder**; first inspect its contents/hashes. Existing Android working root spelling is `AETHERFALL – REALMS COLIDE`, including `korvex_blockout_v01/`. The Downloads folder was not opened or modified. The archive is staged for later controlled transfer. This GitHub documentation commit does not import any model or approve any character art, and `art/asset_registry.json` must still distinguish reserved source paths from actual repository assets.

## Next steps / gates

1. Restore authorised device filesystem access when available; inspect actual Downloads and the existing `korvex_blockout_v01/` **read-only** first. List names, sizes, hashes and duplicates before moves. Preserve all prior user edits.
2. Compare version/path collisions against the staged archive. Only move/import after matching approved names and SHA-256. Preserve source ZIPs and original owner art.
3. Validate intended character/canon/IDs; especially preserve canonical `CHR_ThornDell` in this repository rather than silently renaming to `Thorndell`.
4. Import reviewed source and exported files to `art/` and `game/assets/` with manifests; update `art/asset_registry.json` only after an actual import.
5. Build native Blender source, UV/PBR, rig/skeleton, animation and LOD; then run actual Godot 4.x graphical import/interaction and phone performance checks. Capture real runtime screenshots/MP4 with source SHA and test evidence.

**Claim limit:** This report verifies *staged artifact integrity* and the offline blockout test suite, **not** a finished character, playable build, installed phone copy or successful in-engine render.
