# AETHERFALL character and weapon registry

Machine-readable asset locations and truthful source status live in `art/asset_registry.json`.

- **Existing AETHERFALL:** `CHR_Vellaris_Bloodshield`, `CHR_ThornDell`, `WPN_Vellaris_Bloodshield` (IDs preserved; artwork not yet checked into the repository).
- **Legacy candidates:** `CHR_Korvex`, `CHR_Dreadhull`, `CHR_Morrigan`, `CHR_Pixi`, `CHR_Noxis`, `CHR_Orion`, `CHR_Temporis`, `CHR_Symbion` (empty folders; no models).
- **Historic alias:** Thorndell corresponds to existing `CHR_ThornDell`; never rename the existing ID silently.

The ten character concepts reflect older owner roster selections, but the eight new entries need AETHERFALL-specific design approval before production. Every asset remains `reserved_no_source`; nothing is an imported rig, model or playable character. See `LEGACY_ROSTER.md` and `../legacy/README.md`.

## New required per-character contract

For every registered character, review `docs/characters/plans/<ID>.json` and `CHARACTER_WORKFLOW.md` before concept, Blender or gameplay work. The Vellaris master PNG is supplied in conversation but not committed; all source/model/engine/gameplay gates remain pending. Additional proposed heroes go through `CHARACTER_INTAKE.md` and an explicit unique ID approval first.
