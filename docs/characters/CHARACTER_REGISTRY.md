# AETHERFALL character and weapon registry

Machine-readable asset locations and truthful source status live in `art/asset_registry.json`.

- **Existing AETHERFALL:** `CHR_Vellaris_Bloodshield`, `CHR_ThornDell`, `WPN_Vellaris_Bloodshield` (IDs preserved; artwork not yet checked into the repository).
- **Legacy candidates:** `CHR_Korvex`, `CHR_Dreadhull`, `CHR_Morrigan`, `CHR_Pixi`, `CHR_Noxis`, `CHR_Orion`, `CHR_Temporis`, `CHR_Symbion` (empty folders; no models).
- **Historic alias:** Thorndell corresponds to existing `CHR_ThornDell`; never rename the existing ID silently.

The ten character concepts reflect older owner roster selections, but the eight legacy candidates require AETHERFALL-specific design approval before Blender production. **At the November 26, 2026 baseline** all assets remain `reserved_no_source` with no proven rigs, imports or playable heroes. Future actual status is read from `art/asset_registry.json` and `python3 tools/validate_asset_handoffs.py --report`; only rights-reviewed receipts and real file checksums may promote a stage. See `LEGACY_ROSTER.md` and `../legacy/README.md`.
