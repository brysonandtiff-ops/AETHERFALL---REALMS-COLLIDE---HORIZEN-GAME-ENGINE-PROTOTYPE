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

**Dreadhull — Bonebrine Reaver — The Cursed Salvager:** owner-approved 2026-11-27, original upload 40768.png is actually a 1536x1152 WebP, 538780 bytes. SHA-256 `6d172d578f0d01e5ea126f755ae7c309a4e5d176b801bf11af7de3990a43273c`. Intended GitHub source: `art/concepts/characters/CHR_Dreadhull/Dreadhull_Bonebrine_Reaver_CANONICAL_v1.webp`. The exact image with hooded face, bone-brine plates, cyan energy, crimson cloth, original open wreck frame, opposite-arm salvage bulwark and circular Ossuary Dredge is canonical. Locked source kit: Dredge Snare; Salvage Recall; Reforge Bulwark; Wreckline Drag; Graveyard Forge; passive Sunken Claim. Later full-galleon, anchor-scythe and other generated variants are not approved. Do not add or remove visual features without a separately approved version. The exact image is preserved in the original chat and personal Library; repository binary archive is pending.

**K.R.A.I.T — The Sovereign Guardian:** owner-approved 2026-11-27 replacement for unregistered Bryskar. Original uploaded 1795779132409.jpeg is actually WebP, 1536x1384, 191796 bytes. SHA-256 `129597d1fc89bbbe35a306295ad8239d6ffc05eb39dcb52264355717329fe944`. Intended GitHub source: `art/concepts/characters/CHR_KRAIT/KRAIT_The_Sovereign_Guardian_CANONICAL_v1.webp`. Preserve exact supplied screenshot and primary portrait: silver-blue armor, dragon-shaped shoulders, horned helmet, cyan visor/reactor, Rift Knuckles and visible ascension studies. Source is cropped and contains phone overlay; no full kit or unobserved visual detail is inferred. Owner selection is visual/identity approval, not complete package approval. See [K.R.A.I.T canonical reference](KRAIT_CANONICAL_V1.md). Original in chat and Library; GitHub binary pending.

**Important:** original master images are not yet archived in GitHub. The exact SHA pins preserve source identity but cannot by themselves validate a new generated illustration's visual similarity.

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
