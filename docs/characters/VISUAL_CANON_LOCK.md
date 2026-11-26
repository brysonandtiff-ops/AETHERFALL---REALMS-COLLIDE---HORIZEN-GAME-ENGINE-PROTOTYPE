# AETHERFALL — VISUAL CANON LOCK: NO SILENT DRIFT

**Status:** owner-directed repository hardening, 2026-11-26. **Authority:** exact owner-approved original image > approved character identity > verified model > new concept proposal > legacy concept > AI guess.

## HARD STOP before generation or modelling

1. For ANY owner-approved character, obtain and inspect its exact original approved source image. If the actual image cannot be supplied to the artist or generation run, STOP claiming canon-faithful output. Never attempt to reconstruct an approved face, hair, outfit, armor or weapon from memory alone.
2. Never re-encode, crop, overwrite or rename approved master art. File extensions must match actual signatures. Preserve all originals and hash against the pinned SHA-256. Changes must create a NEW version and must obtain explicit owner signoff.
3. Reuse the Vellaris **infographic layout and branding**, not her actual bloodshield character design. The board uses 4:3 master grid, AETHERFALL top bar, gothic violet-black background with luminous magenta/lavender frames, large portrait left, front/side/back/three-quarter views top middle, silhouettes top right, faces and materials middle, role/unique weapon/gameplay below, icon-labelled ability strip at bottom, and clear CONCEPT ART / NOT FINAL IN-GAME MODEL footer. Improved companion panels require owner approval; never drop key information.
4. Character models must retain face, costume, silhouette, colours, props and identity across all four views. A blockout can simplify topology but MUST retain all signature proportions, shapes and focus. No generic shield on every tank: Vellaris uses her bloodshield; ThornDell uniquely uses the Root Bulwark.
5. Generated output is PROPOSAL_PENDING_OWNER_REVIEW, not automatically approved art. Save variants separately; never replace a locked master or call a procedural GLB render a Blender/Godot screenshot.
6. Identify conflicts between other branches before choosing a design. ThornDell ID does not rename to Thorndell; Corvex versus Korvex is unresolved; Razor/Raven weapons in PR #4 conflict with later asset-audit descriptions. Do not silently select one version.

## Pinned original sources

**Vellaris — The Bloodshield:** uploaded name 39403.png, actually 1536x1152 WebP, 340668 bytes. SHA-256 4d100d50cf0769da47cbe1b782deeb842d15a11c1c46a08f8bd5bd090fa34939. Intended GitHub source path: art/concepts/characters/CHR_Vellaris_Bloodshield/Vellaris_Bloodshield_concept_v1.webp. Preserve exact regal vampiric-elven female face, lavender-white hair, red eyes, pointed ears, jagged crimson pauldrons, fitted black-violet/gold plate, flowing deep red split cape, bloodshield and crimson magical crescent. Concept kit: Blood Barrier; Crimson Riposte; Sanguine Pact; Hemorrhage Veil; passive Royal Ichor.

**ThornDell — The Venomroot:** owner-approved 1536x1024 real PNG, 3219162 bytes. SHA-256 34056a337ebfa67f413375a757f837a247938a3897aabf5e06b0683b48ba89d5. Intended source path: art/concepts/characters/CHR_ThornDell/ThornDell_Venomroot_APPROVED_v1.png. Preserve giant asymmetrical antlered forest titan, bark/basalt armour, bronze, fungi, roots, lime poison pathways and thorn-wrapped Root Bulwark. Proposed gameplay kit is not native-tested.

**Important:** neither original master image is yet archived in GitHub. The exact SHA pins preserve source identity but cannot by themselves validate a new generated illustration's visual similarity.

## Mandatory source-to-output comparison

Use actual side-by-side original versus generated output at matching scale/orientation and gameplay view. Mark each category PASS / FAIL / NOT TESTED: (a) face/hair/eyes; (b) silhouette/shape/proportions; (c) colours/material/ornaments; (d) correct unique weapon/prop; (e) all four angles show the same design; (f) infographic panel layout/title/footer and all sections; (g) hero role/kit; (h) source hashes and genuine model/runtime capture if production claimed.

Any FAIL or missing/not-tested critical identity/prop/kit evidence blocks canonical promotion. Only owner-reviewed approvals can change the canon specification. Write a comparison report under evidence/characters/<ID>/, linking both image hashes and exact source revision. An AI assertion of likeness cannot replace a genuine side-by-side review.

## Code and repository boundaries

- Machine-readable source identity: docs/characters/CANON_LOCKS.json. Its references use **actual** MIME/formats, not misleading uploaded filename extensions.
- Approved master images live under art/concepts/characters/<ID>/, proposals under art/concepts/characters/<ID>/proposals/. Source Blender .blend lives under art/blender/, exported Godot GLB under game/assets/.
- Only master reference or explicitly SHA-listed alternate may be in approved character concept roots. Any other image requires a tracked proposal or owner-approved manifest update; no silent promotion.
- tools/verify_visual_canon.py, called from tools/validate_structure.py, checks immutable exact approved paths/hash/layout/identity and rejects path/format/source-gate mistakes. Automated checks do NOT evaluate face or model visual fidelity.
- Main-branch hard protection requires server-side branch rules: required GitHub Actions static-source-security status, code owner review, no admin bypass, disallow force push. CODEOWNERS text alone does not enforce it. Do not claim this server rule exists until inspected.

## Evidence state

Concept references approved; original binaries remain external to GitHub. No native Blender character render, in-game Godot visual or real device verification has been established. Plans and CI cannot turn an unverified candidate into a completed model.

## Supplement: AF-ART-STYLE-20261126-V1 — exact presentation references

In addition to **character-specific canonical likeness**, every new AETHERFALL hero image must follow the independent **presentation style** lock in `docs/art/MASTER_ART_STYLE_LOCK.md` and `docs/art/ART_STYLE_LOCK.json`. The exact primary owner-supplied style reference hashes are Vellaris (`39403.png`) `4d100d50cf0769da47cbe1b782deeb842d15a11c1c46a08f8bd5bd090fa34939` and Korvex (`39412.png`) `ff352a079685864ced7bbc255a81f73060847156ac24f74edbc2883dd348621b`. Both are actual WebP sources. The `39401.jpg` NEXUSFALL screenshot is a composition-only roster reference, never the AETHERFALL name or a source of automatic approvals. A black-background key-art portrait must not be labelled a complete infographic; a full character sheet must preserve the locked 11-panel Vellaris/Korvex layout, and each hero must retain its own distinctive anatomy, costume and weapon. Proposals require style and identity review separately. The art-style static validator checks only file/source integrity and declared metadata; owner visual review is required to judge any artistic match.
