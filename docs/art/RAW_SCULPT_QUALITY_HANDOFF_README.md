# AETHERFALL — Owner Raw Sculpt Visual Quality Seal v0.1.0

**Work order:** `AF-SCULPT-QUALITY-001` | **Date:** 2026-11-26 | **Status:** reference provenance sealed in Library; GitHub documentation review candidate; model execution not performed.

This package contains text-only GitHub staging sources and exact screenshot backups for an **owner-reviewed premium model quality target**, not evidence of a finished 3D character. It extends the existing `docs/characters/CHARACTER_WORKFLOW.md`, `docs/characters/CANON_LOCKS.json`, `docs/characters/VISUAL_CANON_LOCK.md`, S.I.R.E. LAW-108 and the proposed 1P/3P PR #22, without modifying approved master art.

## Docs to start with

1. `docs/characters/RAW_SCULPT_REFERENCE_SEAL_2026-11-26.md` — user-intended design/quality lock, identity handling, screenshot-vs-model truth and source hierarchy.
2. `docs/characters/RAW_SCULPT_REFERENCE_REGISTER_2026-11-26.json` — exact aliases, byte hashes, Library reference locations and current stage blockers for all eight screenshots.
3. `docs/art/HIGH_FIDELITY_MODEL_STANDARD.md` — upgraded AAA-quality visual/animation/1P+3P acceptance targets and measurable gates.
4. `docs/art/RAW_SCULPT_TO_PRODUCTION_WORK_ORDERS.md` — one-character-at-a-time work orders for Razor, Raven and Vellaris, and two unassigned sculpt holds.
5. `tools/verify_raw_sculpt_intake.py` and `tests/test_raw_sculpt_intake.py` — read-only fail-closed reference manifest audit; cannot assert Blender or Godot execution.

## Tests

- Source-level suite: `python -m unittest discover -s tests -v`
- Validate versioned hashed reference register: `python tools/verify_raw_sculpt_intake.py --json`
- Validate **actual original screenshot bytes** (only where all eight files exist under their uploaded `.jpg` aliases): `python tools/verify_raw_sculpt_intake.py --source-dir <folder> --json`
- A result of `SCREENSHOT_BYTES_VERIFIED_ONLY` is **not** model proof.

## Archive and phone boundary

All eight exact original screenshots (detected as WebP even though uploaded with `.jpg` suffix) are archived in Library at:

`/SIRE Games Concepts/Concept Art and Visuals/AETHERFALL/Raw Sculpt References/2026-11-26/`

The package's `reference_screenshots/` files are byte-identical copies with accurate `.webp` suffix and original aliases in their names. GitHub receives only the text-based SHA/identity register by this handoff; do not claim the screenshot binary or raw Meshy GLB has been committed. The owner's phone target folder `Internal storage/AETHERFALL – REALMS COLIDE` is NOT connected or modified by this work order.

**Native Blender model reconstruction, retopo, rig, Godot import, gameplay, device acceptance, and final release remain BLOCKED until exact source assets and authorised runner exist.**