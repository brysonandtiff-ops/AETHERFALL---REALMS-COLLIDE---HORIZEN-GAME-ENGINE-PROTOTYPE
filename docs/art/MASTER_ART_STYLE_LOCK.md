# AETHERFALL — MASTER ART-STYLE LOCK / NO DRIFT

**Lock:** `AF-ART-STYLE-20261126-V1` | **Project:** AETHERFALL: REALMS COLLIDE  
**Order:** exact owner-approved hero identity > owner-supplied style references > evaluated new proposal > AI preference.  
**Status:** Owner directed style correction; actual artwork still requires source-to-output approval. This is not a Blender or Godot evidence claim.

## The exact three supplied references

| Reference | How it is used | Strict restriction |
| --- | --- | --- |
| `39403.png`, Vellaris — The Bloodshield | **Primary** full 4:3 infographic master; locked Vellaris-specific identity | Do not transfer Vellaris's facial features, red armour, bloodshield or abilities to another hero. Source is WebP despite `.png` upload name. |
| `39412.png`, Korvex — The Hollow Titan | **Co-primary** full 4:3 infographic master and materials/ornament quality benchmark | Do not confuse Korvex with the conflicting Corvex draft or automatically approve this candidate as playable/canon. Source is WebP despite `.png` upload name. |
| `39401.jpg`, NEXUSFALL original-lineup screenshot | Secondary roster **composition, role coding and visual consistency** reference | The image contains a **different old brand** and phone UI/black bars; do not copy the NEXUSFALL name, claim a 15-hero approved AETHERFALL roster, or use the screenshot's device framing in game art. Source is WebP despite `.jpg` upload name. |

The original bytes and SHA-256 hashes are pinned in `docs/art/ART_STYLE_LOCK.json`. They are attached to the owner conversation **but are not stored in GitHub**. This repository can protect their recorded identity, not reconstitute the source from a description. Do not change file extension, transcode, resize or overwrite a master. A reference copy can be used in the actual generation session if the original is accessible; otherwise block any claim of source-faithful final art.

## Non-negotiable output formats

**A. Full character infographic — default for final concept development.** Use a **4:3**, minimum **1536×1152** board, `AETHERFALL / REALMS COLLIDE` top left, hero name/title/class, dark violet-black environment, luminous lavender/magenta borders, eclipse/gothic spire background detail, polished premium high-detail materials. The exact eleven panel identifiers and their ordering are in the lock JSON; human-readable version:

1. Brand and hero name/title/class header; large hero portrait on the left.
2. Front, side, back and three-quarter **consistent** turnaround above center; silhouettes at upper right.
3. Facial/expression studies and detailed palette, armour, cloth and materials close-ups.
4. Hero identity/role at lower left; hero-unique weapon/focus in lower center; readable gameplay identity lower right.
5. A full-width ability-kit icon strip at bottom and clear **CONCEPT ART / NOT FINAL IN-GAME MODEL** disclaimer.

**B. Black-background hero key art — for individual promotional portraits only.** Pure or near-black background, same detailed rendering, polished quality and recognizable character identity. May show dramatic VFX and logo/title. **It does not count as, and must never replace, a full infographic or a 3D model.**

**C. 3D blockout / rotating MP4 — technical evidence.** Render genuine mesh geometry with the real source/model identifier and renderer declared; preserve the approved silhouette and signatures. A greybox or GLB turntable is **not** a full-quality concept illustration, and a 2D view-cycle is **not** an actual mesh rotation. Native Blender/Godot labels are allowed only with actual native evidence.

## STOP conditions — reject on sight

- Poster substituted for full-sheet request; missing front/side/back/three-quarter, materials, expression studies, unique weapon/focus, ability strip, or footer.
- Generic character swapped for owner-approved face, proportions, hair, silhouette, signature ornament or role palette. **Do not share Vellaris's face or costume** with Symbion or Temporis.
- Wrong project title or copied NEXUSFALL, Shadowspire, screenshot UI chrome, unrelated lore or unapproved 15-hero roster.
- Reused generic palette and generic shield across all characters; Korvex, ThornDell, Vellaris, Razor, Raven, Temporis and Symbion must preserve individually recognizable proportions, powers and equipment.
- Pretending an image generation, a color-coded checklist, an offline blockout or a 2D MP4 proves Blender/Godot gameplay, rigging or playable art.
- Automated visual-similarity pass claims. The source-level checker **only** checks the metadata, pinned reference hashes and proposal packaging. It **cannot** certify that an image really looks right.

## Mandatory generation brief and human review

Before **every** character render or sheet, include the exact **two pinned infographic reference images** in the artist or generation session. Include the specific character's own approved source sheet when one exists; keep style and character identity as **two different references**. The roster reference is used only for lineup overview, not branded output. Use the same style finish, typography hierarchy, borders, layout, camera discipline and information density, without copying another hero's equipment.

Every new candidate image goes in `art/concepts/characters/<CHR_ID>/proposals/` with its existing `<image>.review.json` and this patch's **style fields**, checked by `tools/verify_art_style_contract.py`. The reviewer must inspect **actual side-by-side imagery** at useful scale and record PASS/FAIL/NOT TESTED for: correct hero identity; consistent silhouette across all views; palette and materials; unique weapon; layout completeness; typography/brand; kit/role; artwork fidelity. The generated asset remains `PROPOSAL_PENDING_OWNER_REVIEW` or `REJECTED_DRIFT` until independently approved; metadata cannot grant canon status.

Use `docs/characters/DRIFT_REVIEW_TEMPLATE.md`, `docs/characters/VISUAL_CANON_LOCK.md` and `docs/characters/CANON_LOCKS.json` alongside this style lock. Save visual comparison reports under `evidence/characters/<CHR_ID>/`. No destructive replacements or silent version upgrades.

## Enforcement and limits

`python3 tools/verify_art_style_contract.py` checks the style lock against a second in-code pinned manifest, reads existing character canon layout to prevent mismatch and rejects noncompliant candidate sidecars. CI runs the script and its adversarial unit tests. Owner **must** inspect actual reference-to-proposal art; CI cannot detect all aesthetic drift.

The separate GitHub **main branch protection** rules (require PR + code-owner approval + status checks; block direct updates, bypass and force pushes) must be activated in repository settings before this becomes a server-enforced merge barrier. A draft PR alone is **not active on main**.