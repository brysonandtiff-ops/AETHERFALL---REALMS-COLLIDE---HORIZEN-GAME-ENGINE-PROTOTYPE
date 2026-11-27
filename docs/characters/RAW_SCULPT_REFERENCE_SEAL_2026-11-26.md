# AETHERFALL — Owner-supplied raw sculpt screenshot reference seal

**Seal ID:** `AF-RAW-SCULPT-QUALITY-LOCK-20261126`
**Date:** 26 November 2026 · **Project:** AETHERFALL: REALMS COLLIDE
**Scope:** This is an **owner-directed visual-quality reference archive**, not a replacement for `CANON_LOCKS.json`, a certified model, or a new universal S.I.R.E. law.
**Source register:** [RAW_SCULPT_REFERENCE_REGISTER_2026-11-26.json](RAW_SCULPT_REFERENCE_REGISTER_2026-11-26.json) (eight entries, exact byte SHA-256).

## Decision and precedence

The owner wants the presented Meshy/raw-AI sculpt appearances **preserved as high-detail visual targets and then improved** during professional Blender → Godot production. We may improve deformation, topology, texture fidelity, performance, 1P/3P readability, facial expression and rig quality **without silently redesigning the character**.

**Visual master precedence remains:** exact previously approved owner master images and `CANON_LOCKS.json` > owner-reviewed future variant > these uploaded raw sculpt *screenshots* > model-generated guesses. These screenshots do **not** amend Vellaris's locked face, shield, palette, name or ability kit, or ThornDell's approved identity. A variant becomes a new master only after an owner-reviewed source-to-output comparison and separately versioned canon change. The owner's reference choice permits improving modeling fidelity, **not relabelling screenshots as approved final GLBs**.

### Reference classification

| Screenshot aliases | Identification from visible content | Preserved target / art direction | Gate |
|---|---|---|---|
| `40174.jpg`, `40166.jpg` | Raven, sculpt screenshots | Hooded gothic oracle, long silver hair, broad layered black-violet feathers, shoulder corvid, violet ritual orb, sculpt pedestal to remove in working mesh | Source GLB and approved canonical identity/weapon variants must be reconciled before promoting sculpt. |
| `40149.jpg`, `40151.jpg` | Razor, sculpt and Meshy stats screenshot | **Four-legged** skeletal hunter, pale bone ribs and skull, red fissures, oversized fang jaw, segmented long tail, claws, hanging chain | No humanoid conversion; pedestal separate; stat values are screenshot-only, not independently measured from mesh. |
| `40136.jpg`, `40132.jpg` | Vellaris, colored + grey screenshots | Tall vampiric armour, sharp layered crimson pauldrons, pale hair, fitted plate, split deep-red cape | Canon source has a **unique Bloodshield** absent from these screenshots; restore it in model stage; no face/palette drift. |
| `40168.jpg` | **Unassigned** colored woman with rose/bronze armour, teal-dark hair, lantern and red cape | Preserve as unassigned candidate concept source; no character identity determined from screen | No assignment to Vellaris, Morrigan, Raven or other hero without explicit owner choice. |
| `40170.jpg` | **Unassigned** monochrome spectral/hair-tendril humanoid | Preserve grey sculpt screenshot as different unassigned candidate | No hero, species, rig or role approval inferred. |

**Original upload format caution:** All eight incoming files had `.jpg` names but the inspected byte signatures and PIL decoding show WebP, resolution **1536×1384** each. We preserve the exact bytes and their SHA-256, and archive them with `.webp` on the Library surface. Do not regenerate, resample, or overwrite this reference archive. The filenames in the register retain the supplied `.jpg` aliases for traceability.

**Verified external preservation:** `/SIRE Games Concepts/Concept Art and Visuals/AETHERFALL/Raw Sculpt References/2026-11-26/` in the owner's ChatGPT Library. This is an external reference archive; GitHub holds the **register/hash/documentation only**. Do not mark `source_archived=true` for a character until its actual master image is committed to the approved source path and hash-verified under the existing character workflow.

### Screenshot-specific truth

`40151.jpg` visibly reports Meshy 7.1: Triangle topology; Faces **2,460,470**; Vertices **1,229,959** for Razor. These are UI-displayed values; the actual raw mesh file was **not provided** in this turn. Counts, topology, object separation, weight painting, UVs, usable texture maps and animation suitability cannot be independently verified from a screenshot. None of the screenshots establishes a native Blender viewport or a Godot gameplay scene.

## Required improvement programme (visual target is the floor, not the output)

1. **Preflight:** Pin exact approved master image and every owner-supplied screenshot SHA; identify all silhouette/face/gear conflicts as review blockers before work begins. Do not change `CANON_LOCKS.json` or `art/asset_registry.json` without a separate approval and validator-aware migration.
2. **Keep raw:** Archive untouched imported original mesh and material pack (when actually supplied). Store `.glb` raw originals in an approved external input vault (not `art/`; the existing AETHERFALL validator forbids `.glb` under `art/`). Record provider, licence, model ID/URL when available, app/engine version, origin hash and asset transfer permission.
3. **Separate and pose:** On a **duplicate working scene**, remove the circular pedestal from the character's export, independently preserve it as optional `PRP_*` when wanted; separate weapons, chains, props, wings/feathers and accessories; neutral A-pose humanoids or clean neutral quadruped stance; apply safe transforms on working meshes only.
4. **Art-quality + animation:** Sculpt/art-direct high-resolution forms against the exact master, manually resolve sculpt fusion/hidden anatomy and dangling parts, retopologize deforming anatomy with proper loops, bake onto 3P 40k–70k/1P 20k–35k *planning budgets* (verify per hero/device, not automatic certification). Add UVs, PBR, facial rig, cloth/hair/chain simulation proxies, and camera-safe separate 1P assets.
5. **Fair gameplay:** Visual feathers/tendrils/spines must not secretly enlarge combat hurtboxes. Same authoritative gameplay collision and damage in 1P vs 3P, with telegraphs readable at distance and flash/contrast accessibility checked.
6. **Proof:** Produce actual Blender front/side/back/3-quarter orthographic captures, posed deformation clips and real exported GLB. Then capture genuine Godot 4.x import, gameplay/ability test, FPS and user-device test. Attribute all captures to source commit/hash and a different independent verifier in the S.I.R.E. release pipeline.

## Promotion gates and owner acceptance

- **Reference:** current screenshot intake preserved by SHA in Library; **PASS_SCREENSHOT_ARCHIVE_ONLY**.
- **Original raw 3D:** source GLB/OBJ/FBX absent; **BLOCKED**.
- **Approved master art in repository:** existing `CANON_LOCKS.json` gate remains unchanged; **BLOCKED where not committed**.
- **Model build:** native Blender readback and quad retopology not done; **NOT_VERIFIED**.
- **Rig/LODs/PBR:** **NOT_VERIFIED**.
- **Godot 1P/3P gameplay:** **NOT_VERIFIED**.
- **Final release:** **BLOCKED**; S.I.R.E. controls internal verification, hashing and staging only, while external distribution platforms control their own release gates.

See [HIGH_FIDELITY_MODEL_STANDARD.md](../art/HIGH_FIDELITY_MODEL_STANDARD.md), [RAW_SCULPT_TO_PRODUCTION_WORK_ORDERS.md](../art/RAW_SCULPT_TO_PRODUCTION_WORK_ORDERS.md), existing [CHARACTER_WORKFLOW.md](CHARACTER_WORKFLOW.md) and [VISUAL_CANON_LOCK.md](VISUAL_CANON_LOCK.md). More polished images are **not** substitutions for actual editable `.blend` or checked `.glb` source.