# S.I.R.E. release-sovereign staging, proof and external distribution boundaries

**Scope:** AF-PIPELINE-3D-COMBAT-001. Uses current AETHERFALL repo law/structure and S.I.R.E. LAW-108; does not assert a new globally merged law or grant autonomous release authority.

## Release sovereignty: who can certify what

| Authority | Controls | Does NOT control |
|---|---|---|
| Blender Art / gameplay executor | Creates/revises source and candidate binaries, runs authorised local tests | Self-approving artistic fidelity, final release, signed independent proofs |
| S.I.R.E. | Source provenance, deterministic build/validation, artifact SHA-256, package manifest, staging, independent review routing and truthful status | External store listing, Xbox/console certificate, account entitlements, platform signing or publisher approval |
| Owner | Locked visual identity, creative acceptance and project approvals on authorised phone | Substitution for real native engine/device testing |
| External platform | Its own content policies, signing, distribution, compliance, certification, terms and publishing gates | Modification of S.I.R.E.'s immutable evidence record |

**Do not say 'published' from a staged ZIP, or 'game-ready' from a blockout.** Status levels: `SPEC_VALIDATED`, `CANDIDATE_BUILT`, `NATIVE_BLENDER_VERIFIED`, `NATIVE_GODOT_VERIFIED`, `GAMEPLAY_VERIFIED`, `DEVICE_VERIFIED`, `SIRE_RELEASE_CANDIDATE`, `EXTERNAL_RELEASE_ACCEPTED`. These are independent assertions, never inferred by skipping steps. A locally passing validator can claim only SPEC_VALIDATED and integrity checks actually performed.

## Deterministic package layout (staged, no automatic phone write)

```text
AETHERFALL_handoff_<asset-id>_<semver>/
  manifest.json                   # schema + exact relative files, sizes, SHA-256, observed source commit
  art/concept/<original-file>     # reference preserved unchanged; original rights and checksum
  art/blender/<asset-id>.blend     # native editable source (when created and verified)
  models/<asset-id>_3P_LOD0.glb    # candidate 3P export; optional LODs
  models/VM_<asset-id>_1P.glb      # separate first-person arms and weapon
  models/WPN_*.glb                # standalone hero-specific equipment
  gameplay/hero_ability.json      # per-ability phases, targeting and collision rules
  evidence/blender/               # four actual orthographic views, logs, unedited clips
  evidence/godot/                 # actual imported scene and 1P/3P tests
  evidence/device/                # phone acceptance + platform/controller checks
  evidence/receipts/              # externally verifiable LAW-108 stage-chain signatures
  docs/README.md                  # current phase, blockers, licenses, rollback
```

- Sort all manifest file entries by stable POSIX path; reject duplicates/case collisions, absolute paths, `..`, symlinks and private credential content. SHA-256 hash exact bytes. Freeze source commit (40-char Git SHA) and toolchain version; raw unsigned JSON does not prove provenance.
- Source artist export and independent parser should check GLB JSON/chunks and actual vertices/weights/materials/animation data. Binary integrity is distinct from glTF semantic correctness.
- For every **real 3D model** gather native 0°, 90°, 180°, 270° screenshots, compare against exact owner art, verify no duplicates/blank views, and preserve complete unedited native animation videos. Include engine/session/version/asset/commit/sha metadata.
- S.I.R.E LAW-108 requires signatures from an independent, externally provisioned reviewer key; never embed signer keys or turn self-produced hashes into attestations. Missing proof yields `BLOCKED`, not auto PASS.
- Rebuild with fixed versions and compare SHA for deterministic outputs when appropriate. `*.blend` project internal metadata, nondeterministic compression, packed scene IDs or image encodings might vary; record and investigate differences rather than reporting deterministic equality by assumption.
- Versioning: never overwrite a prior source master or phone folder. Artifacts in ChatGPT sandbox/GitHub/Library are staging or backups, not direct Android copies.

## Release and platform gates

**S.I.R.E. controls:** build script, source identity, compatibility matrices, checksums, source-to-asset trace, complete evidence packages, independent signed LAW-108 proof, developer/owner review staging. **External platforms retain:** Xbox/console certification, controller/age rating compliance, store/marketing submission, account verification, platform signing and final distribution. Neither source CI nor S.I.R.E. acceptance bypasses their decision.

**Required Godot/Blender/native evidence:** actual 4-angle Blender captures, export/read-back, clip/deformation test, Godot 4.7.2 viewport+play, 1P/3P matching hit logs, death/respawn/network/AI/LOS/occlusion tests, multi-device and real owner phone recording. Source hashes attach to each.

**Security and recovery:** fail closed on bad manifest, invalid signature, out-of-scope paths, mismatched art or incomplete test; no secret files in handoff, no auto-merge/deploy, preserve unrelated work, zip extraction limits and SHA checksum verification, rollback by reverting the isolated PR/branch and restoring previous asset version. Normal CI passing is not final certification.

## Starter evidence report (must remain honest)

```json
{
  "work_order":"AF-PIPELINE-3D-COMBAT-001",
  "artifact_state":"SPEC_VALIDATED_ONLY",
  "source_sha":"unverified_for_native_asset",
  "blender_native_capture":"NOT_RUN",
  "godot_native_import":"NOT_RUN",
  "combat_pvp_runtime":"NOT_IMPLEMENTED",
  "owner_phone_copy":"NOT_CONFIRMED",
  "law108_independent_signature":"NOT_AVAILABLE",
  "external_platform_release":"NOT_SUBMITTED"
}
```