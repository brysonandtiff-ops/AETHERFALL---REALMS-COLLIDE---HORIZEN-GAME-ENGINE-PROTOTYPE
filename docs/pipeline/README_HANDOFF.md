# AETHERFALL — S.I.R.E. 1P/3P Hero Asset + Gameplay Pipeline v0.1.0

**Status: SPEC_VALIDATED_ONLY · NO NATIVE MODEL/GAMEPLAY CERTIFICATION**  
**Date:** 26 November 2026 · **Work order:** `AF-PIPELINE-3D-COMBAT-001`  
**Repository:** `brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE`  
**Reviewed repository base commit (read-only):** `c11443f01213aaea1b6e86e4f9bed303051135dd` (recheck before branch promotion).

## Deliverables

- `docs/pipeline/PRODUCTION_STANDARD.md` — cross-team handoff, exact source/identity, 1P/3P split, twelve S.I.R.E. stage gates, asset folder/naming.
- `docs/pipeline/BLENDER_ART_TEAM.md` — Meshy cleanup → neutral pose → manual retopo/LODs → PBR → 3P rig / 1P viewmodel → native Blender/Godot handoff.
- `docs/pipeline/GAMEPLAY_AI_ENGINEERING.md` — game server authority, movement and AI state machines, ability phases, target priority, collision/hurtbox, UI and network QA.
- `docs/pipeline/SOVEREIGN_STAGING_AND_PROOF.md` — S.I.R.E. evidence, deterministic packages, signed gates vs external platform release sovereignty.
- `docs/pipeline/contracts/*.json` — strict hero handoff and ability request exemplars. The ability document is deliberately an **unapproved fixture**, not a Vellaris ability addition.
- `docs/pipeline/examples/CHR_Vellaris_Bloodshield_SPEC_ONLY.json` — accepted contract example that honestly marks source unarchived and native evidence NOT_RUN.
- `tools/verify_production_contract.py` — stdlib read-only spec/hash checks with fail-closed fake-proof prevention.
- `tests/test_production_contract.py` — 23 positive/adversarial tests. `evidence/offline_tests_2026-11-26.log` logs their execution.
- `package_manifest.json` — SHA-256 and bytes for this pack (the manifest itself is deliberately excluded from its own entries).

## Verify locally

```sh
python3 -m unittest discover -s tests -v
python3 tools/verify_production_contract.py \
  --hero docs/pipeline/examples/CHR_Vellaris_Bloodshield_SPEC_ONLY.json \
  --ability docs/pipeline/contracts/ABILITY_CONTRACT_EXAMPLE.json
python3 tools/verify_production_contract.py --files-manifest package_manifest.json --root .
```

`PASS_SPEC_OR_BYTE_INTEGRITY_ONLY` and exit 0 mean **only** that local contract/byte checks passed. `--demand-native` intentionally **returns 2 BLOCKED**: native Blender + Godot + independent signed S.I.R.E. LAW-108 proof and physical-owner-device evidence must be collected elsewhere.

## Insert into the existing repository

Treat this as an **additive review candidate**, not a replacement for the existing `docs/characters/CHARACTER_WORKFLOW.md`, `docs/characters/VISUAL_CANON_LOCK.md`, `docs/characters/CANON_LOCKS.json`, original concepts, currently reserved IDs, or the existing `tools/validate_structure.py`. Create a reviewed branch; place the new `docs/pipeline/`, `tools/verify_production_contract.py` and `tests/test_production_contract.py` at the same repo-relative paths. Re-run the repository's own `python3 tools/validate_structure.py`, all unit tests and pinned Godot smoke on that **exact source commit**, then obtain owner/CI review. The new checker is supplemental; existing S.I.R.E. validators remain authoritative.

**Platform boundary:** AETHERFALL/S.I.R.E. may prepare and attest a build candidate but the Xbox/console/store providers remain sole authorities for their certification, platform signatures, publication and distribution.

## Physical phone / rollback

Owner's existing phone folder is shown as `Internal storage/AETHERFALL – REALMS COLIDE/` (one L in COLIDE); preserve that exact existing path and its `korvex_blockout_v01/`. An export archive can be extracted to a **new versioned subfolder** after owner-controlled transfer; this sandbox/archive is not proof of transfer. Source branch rollback: close the draft PR without merge, or revert the additive commit if merged. Do not delete or rename previous game source/art/model folders.

## Explicit blockers

Exact pinned Vellaris and ThornDell source images are still reported unarchived by the current repository; no new Blender model, verified 1P viewmodel, 3P animation, in-game Godot/PvP AI, native performance, owner phone or distribution certificate was produced. `CHR_Corvex` vs `CHR_Korvex` and some Razor/Raven variants have unresolved canon conflicts; this handoff does not resolve them.