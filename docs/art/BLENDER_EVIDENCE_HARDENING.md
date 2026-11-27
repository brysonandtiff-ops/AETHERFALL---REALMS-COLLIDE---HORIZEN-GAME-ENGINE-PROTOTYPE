# AF-ART-BLENDER-001 — hardening contract for character source and evidence

**Project:** AETHERFALL: REALMS COLLIDE · **Applies to:** 1P and 3P Blender hero models, rigging, source handoff and Godot 4 imports. This adds to the canon lock and production SOP, never replaces them. **Status:** static evidence contract, not character-model certification.

## Controlled raw source and export locations

- Copy the unchanged raw imported sculpt (`.glb`, `.fbx`, `.obj` or `.blend`) to `art/blender/characters/<CHR_ID>/raw/<original-versioned-name>` and hash it before modifying anything. The scoped `raw/` folder is the **only approved exception** for imported GLB files under `art/`. The existing source scanner rejects unregistered characters and all other GLBs in `art/`. Never treat raw sculpt files as runtime exports.
- Save the editable, retopologized, rigged `.blend` under `art/blender/characters/<CHR_ID>/` with a new versioned name. Preserve canonical original concepts unmodified under `art/concepts/characters/<CHR_ID>/`.
- Export **distinct** 1P and 3P `.glb` files to the registry-declared `game/assets/characters/.../<CHR_ID>/`. Record their separate SHA-256 digests, measured triangle counts, LODs, PBR status, armature, animation clips and sockets.
- Treat character names, aliases and `CANON_LOCKS.json` as protected; no silent renames or approved-reference substitutions. Original-to-model side-by-side human review remains mandatory.

## Required fields when any stage is marked PASS

Copy `docs/art/templates/BLENDER_HANDOFF_TEMPLATE.json` to `art/blender/characters/<CHR_ID>/handoff.json` after actual registered production begins. Do not copy the template into a character folder merely to assert that a model exists.

Every passing stage **must** record `status: PASS`, `source_commit` (the **same full 40-digit Git SHA** as the handoff), `capture_source`, `tool_version`, an existing `evidence_path` and the real `evidence_sha256`. Evidence paths must stay within the matching character's evidence folders, not borrow another hero's files, escape the repository, or follow symlinks. Prior stages must have passed. Missing or untested stages remain `NOT_RUN` / `BLOCKED` / `FAIL`.

| Stage | `capture_source` | Evidence required |
| --- | --- | --- |
| `reference_lock` | `REFERENCE_REVIEW` | Approved original master binary and dated comparison file (image, JSON or Markdown) under `evidence/characters/<CHR_ID>/`. |
| Import, repair, retopo, UV/PBR, rig, Blender native review | `BLENDER_NATIVE` | Genuine Blender screenshot or video under `evidence/blender/<CHR_ID>/` or `evidence/characters/<CHR_ID>/`. |
| `godot_native_import` | `GODOT_NATIVE` | Genuine Godot screenshot or video under `evidence/godot/<CHR_ID>/` or `evidence/characters/<CHR_ID>/`. |
| `camera_animation_gameplay` | `GODOT_NATIVE` | Real **unedited `.mp4` gameplay/animation interaction capture** with 1P and 3P view checks. |
| `owner_review` | `OWNER_REVIEW` | Owner's reviewed `.md` or `.json` decision in `evidence/characters/<CHR_ID>/`, recorded in both stage evidence and `owner_signoff` with the **same SHA-256**. |

`tool_version` should identify the real application or review process used. Report the actual Blender/Godot versions, exact source revision, scene and capture environment inside the evidence notes. An AI-generated concept, glTF viewer still, fabricated capture or Godot bootstrap smoke is **never** native model proof.

## Promotion is strictly separate from a file hash

`READY_FOR_OWNER_REVIEW` and `GAME_READY` require more than ten ticked boxes: the registered character must be approved for AETHERFALL, its original source must be archived with matching hashes, and the independent `docs/characters/plans/<CHR_ID>.json` production gates (through gameplay) must be legitimately complete. Evidence must tie to the registered character directory, its approved master and any pinned immutable source hash in `CANON_LOCKS.json`.

`GAME_READY` additionally requires distinct 1P/3P exports, real editable Blender source and untouched raw sculpt, recorded mesh/LOD/UV/rig/animation/socket checks, all ten evidence stages, and the separate actual owner's reviewed approval record. Do **not** set approval based on an automated validator's green status.

### Static safety tests

Run all three from the repository root:

```bash
python3 tools/validate_blender_handoff.py
python3 tools/validate_structure.py
python3 -m unittest discover -s tests -v
```

These scripts reject dangerous paths, symlinks, wrong/borrowed character data, wrong SHA-256 digests, missing raw-source archive, suspect GLB/Blender/image/video headers, impossible production-state transitions and disconnected approvals. They **do not** parse or certify full Blender geometry, real game camera behaviour, file licensing, visual fidelity or the authenticity of a screenshot. Real engine import, real native screenshots and video, physical-device profiling, and owner signoff remain non-automatable production gates.

**Rollback:** The change is review-only until a qualified reviewer merges the draft PR. No character master artwork, scene, model or build is replaced by this policy. Never force-push or bypass branch protection to make a false status pass.
