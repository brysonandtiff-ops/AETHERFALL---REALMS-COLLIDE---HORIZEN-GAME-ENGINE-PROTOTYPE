# AETHERFALL character and weapon registry

Machine-readable asset locations and truthful source status live in `art/asset_registry.json`.

- **Existing AETHERFALL:** `CHR_Vellaris_Bloodshield`, `CHR_ThornDell`, `CHR_Dreadhull`, `CHR_KRAIT`, `CHR_Korvex`, `WPN_Vellaris_Bloodshield` (IDs preserved; artwork not yet checked into the repository).
- **Legacy candidates:** `CHR_Morrigan`, `CHR_Pixi`, `CHR_Noxis`, `CHR_Orion`, `CHR_Temporis`, `CHR_Symbion` (empty folders; no models).
- **Historic alias:** Thorndell corresponds to existing `CHR_ThornDell`; never rename the existing ID silently.

Ten historical character concepts reflect older owner roster selections; the newly registered K.R.A.I.T replaces the previously unregistered Bryskar proposal, but the six remaining legacy candidates need AETHERFALL-specific design approval before production. Every asset remains `reserved_no_source`; nothing is an imported rig, model or playable character. See `LEGACY_ROSTER.md` and `../legacy/README.md`.

## New required per-character contract

For every registered character, review `docs/characters/plans/<ID>.json` and `CHARACTER_WORKFLOW.md` before concept, Blender or gameplay work. The Vellaris, ThornDell, Dreadhull, K.R.A.I.T and Korvex master references are supplied in conversation but not committed; all source/model/engine/gameplay gates remain pending. Additional proposed heroes go through `CHARACTER_INTAKE.md` and an explicit unique ID approval first.

**Owner replacement, 2026-11-27:** `CHR_KRAIT` is K.R.A.I.T — The Sovereign Guardian, the approved successor to the unregistered `CHR_Bryskar` proposal. Do not register Bryskar as a separate active hero. See [K.R.A.I.T canonical lock](KRAIT_CANONICAL_V1.md).
