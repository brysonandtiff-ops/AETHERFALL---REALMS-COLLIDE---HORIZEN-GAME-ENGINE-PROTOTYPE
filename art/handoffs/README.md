# Approved-source asset handoff receipts

This directory stores **real, per-asset receipt JSON** for assets that advance beyond `reserved_no_source` in `art/asset_registry.json`. It is currently empty because no original concept/source/runtime files have been verified as present in the repository.

## Allowed status progression

`reserved_no_source` → `concept_recorded` → `blender_source_recorded` → `runtime_export_recorded` → `native_import_reviewed`.

The status describes recorded **source/artifact custody**, not hero gameplay implementation. It can only advance **one step per reviewed PR**. A concept image or owner approval does not prove a 3D model; a GLB export does not prove native Godot import; a headless boot does not prove a hero looks or plays correctly.

## Required receipt path and content

A staged `CHR_ThornDell` would have its receipt at `art/handoffs/CHR_ThornDell.json`. Do **not** create it until real, rights-cleared files are present and signed off for public storage.

Receipt format (field names shown; the following is **documentation**, not real files/proof):

```json
{
  "schema_version": 1,
  "asset_id": "CHR_ThornDell",
  "status": "concept_recorded",
  "provenance": {
    "rights_basis": "owner_original",
    "source_reference": "approved original source record",
    "rights_reviewed_by": "actual authorised reviewer",
    "rights_review_reference": "reviewed decision/PR reference"
  },
  "files": {
    "concept": {
      "path": "art/concepts/characters/CHR_ThornDell/approved_sheet.png",
      "bytes": 123456,
      "sha256": "replace_with_actual_64_hex_sha256_of_file"
    }
  }
}
```

For `blender_source_recorded`, add `files.blender` pointing to a genuine `.blend` under the ID's `source_dir`. For `runtime_export_recorded`, also add `files.runtime` pointing to a real `.glb` under the ID's `runtime_dir`. These stages are permitted only for `concept_status=aetherfall_approved` characters.

For `native_import_reviewed`, additionally provide `native_import` with `engine=Godot`, `engine_version=4.7.2`, actual `reviewed_by` and `review_reference`, plus `log` and `capture` artifact records (`path`, `bytes`, `sha256`) under `evidence/godot/`. The capture must be a *genuine* Godot screenshot/video, not an image-generated replacement. External reviewer checks the recording, engine version and source identity; code verifies **only files and checksums**.

## Commands

```sh
python3 tools/validate_asset_handoffs.py --report
python3 tools/validate_asset_handoffs.py --validate
```

Hash files with `sha256sum <file>` (or equivalent). Keep private owner photos outside this public GitHub repo unless the owner explicitly authorises publication. Submit source additions and receipt/status changes together; never bypass review or fabricate assets. The registry remains the single authoritative ID/approval record.
