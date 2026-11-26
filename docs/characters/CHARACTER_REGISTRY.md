# AETHERFALL character and weapon registry

Machine-readable asset locations and truthful source status live in `art/asset_registry.json`.

- **Existing AETHERFALL:** `CHR_Vellaris_Bloodshield`, `CHR_ThornDell`, `WPN_Vellaris_Bloodshield` (IDs preserved; artwork not yet checked into the repository).
- **Legacy candidates:** `CHR_Korvex`, `CHR_Dreadhull`, `CHR_Morrigan`, `CHR_Pixi`, `CHR_Noxis`, `CHR_Orion`, `CHR_Temporis`, `CHR_Symbion` (empty folders; no models).
- **Historic alias:** Thorndell corresponds to existing `CHR_ThornDell`; never rename the existing ID silently.

The ten character concepts reflect older owner roster selections, but the eight new entries need AETHERFALL-specific design approval before production. Every asset remains `reserved_no_source`; nothing is an imported rig, model or playable character. See `LEGACY_ROSTER.md` and `../legacy/README.md`.

## Art evidence from 26 November 2026

The approved ThornDell concept and Vellaris/Korvex sheets were categorised in [tank visual references](TANK_VISUAL_REFERENCES_2026-11-26.md) and the [media intake manifest](../art/MEDIA_INTAKE_2026-11-26.json). Files are staged in a conversation attachment and still await binary repository check-in; `status=reserved_no_source` remains appropriate for all records because no actual `.blend` or `.glb` models were supplied in this intake. Offline model-preview GIF/video files do not change source-validation status.
