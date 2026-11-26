# AETHERFALL — S.I.R.E. Source Integrity Seal

**State: source inventory capability only. Release certification: BLOCKED.**

The canonical S.I.R.E. master remains in [the existing S.I.R.E. repository](https://github.com/brysonandtiff-ops/SIRE). This folder does **not** introduce another agent, new paid verifier or self-issued release authority.

## Why this is separate from a game release seal

S.I.R.E. **LAW-104** requires exact content identity, tests, reproducible builds, security/recovery, **independent cryptographic provenance**, visual/runtime evidence, evidence integrity, and owner authorisation. **LAW-105** demands real engine/phone graphics and complete continuous animation videos. **LAW-106** requires a clean tree and independently verified stage state. The **LAW-108** twelve-stage signed game pipeline is still a separate gate. **LAW-115** remains a draft.

We can establish an unsigned **SOURCE_INTEGRITY_ONLY** report for an exact Git commit, but we must not call it a Gold Seal or playable game certification. **Hash matches alone are not independent provenance.**

## What the source seal does

- Validates the real clean Git HEAD against an independently supplied candidate SHA.
- Requires a trusted ancestor SHA and uses the existing `tools/structure_guard.py` to protect original artwork, character IDs, Godot paths, UID references and Android document location.
- Computes **SHA-256 and SHA3-256** of actual tracked Git blobs (not names or Git SHA-1 alone), rejects unresolved LFS pointers/symlinks and malformed source paths.
- Builds a deterministic domain-separated SHA-256 Merkle root from the sorted per-file inventory.
- Generates a receipt **outside the checkout** to avoid changing the files it hashes. The output is *unsigned* and `UNANCHORED_INTEGRITY_ONLY`.
- Can re-verify a saved receipt and, if supplied independently, its SHA-256 anchor. That raises provenance to **ANCHORED_INTEGRITY_ONLY**, still not runtime/release certification.

## Commands

Use a local authorised clone of this repository, checking the actual branch/commit first:

```sh
git rev-parse HEAD
git status --porcelain
python3 tools/structure_guard.py check
python3 tools/sire_seal.py source --base TRUSTED_40_HEX_ANCESTOR --expected-head ACTUAL_40_HEX_HEAD
```

Optional receipt (must be outside the repository and not already exist):

```sh
python3 tools/sire_seal.py source \
  --base TRUSTED_40_HEX_ANCESTOR \
  --expected-head ACTUAL_40_HEX_HEAD \
  --output /tmp/aetherfall-source-integrity.json
```

Re-check the saved record:

```sh
python3 tools/sire_seal.py verify \
  --receipt /tmp/aetherfall-source-integrity.json \
  --expected-head ACTUAL_40_HEX_HEAD
```

The optional `--expected-receipt-sha256` must come from an *independently controlled anchor*; a hash pasted from the same untrusted receipt is not independent evidence.

## CI delivery

On pull requests, GitHub Actions checks out the **PR's actual head commit** instead of relying on a synthetic merge SHA. It runs the existing source/security/structure tests, then produces a source-only integrity record and archives it for inspection (short retention). Another job runs the real SHA-pinned Godot **4.7.2** binary headlessly and preserves its **original logs**, separately. Neither produces real graphical/screenshots/character animation/device/phone-download proof.

Original phone folder remains **`Internal storage/AETHERFALL – REALMS COLIDE/Docs/Inbox`**; no remote tool has read or modified those phone files. The repository seal records only Git-tracked source, never private Android storage.

## Promotion gate

A subsequent S.I.R.E.-authorised reviewer would need source-pinned real Blender geometry/four views, original full animation videos, graphical Godot gameplay, physical device checks, recovery, security, externally held keys/independent signatures, and explicit owner release approval. Until then **RELEASE BLOCKED**.

**Rollback:** Close this stacked draft PR. The previous S.I.R.E. integration, file layout and phone document code remain unchanged. No deleted or overwritten source was necessary.

## Continuity and previous-seal hardening

Once the source-seal policy exists on a trusted ancestor, future PRs cannot silently remove earlier required paths, loosen the maximum verified blob size or drop/change existing proof gates. A saved receipt is first size/symlink checked before digest validation, so untrusted oversized bytes fail closed. An earlier exact-SHA receipt cannot be replayed against a newer source commit.

These are additional **integrity safeguards**, not independent signing or game-release certification.
