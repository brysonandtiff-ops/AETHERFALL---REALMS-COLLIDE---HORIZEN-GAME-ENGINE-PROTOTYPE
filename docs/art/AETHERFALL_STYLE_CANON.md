# AETHERFALL – REALMS COLIDE | CANONICAL ART STYLE LOCK
**Owner decision:** 26 November 2026 · **Lock:** `AF-STYLE-39403-V1` · **Status:** OWNER LOCKED
**Scope:** ALL future AETHERFALL character concepts, planning sheets and applicable game-world visual design, including tanks, support, damage, enemies, bosses, weapons, factions and scenes. Already-approved art is preserved exactly.

## The one primary visual standard
**The owner's THIRD uploaded picture (`39403.png`) showing Vellaris — The Bloodshield is the canonical art-*style* and presentation reference.** Its actual bytes are WebP (1536 × 1152; 340,668 bytes), SHA-256 `4d100d50cf0769da47cbe1b782deeb842d15a11c1c46a08f8bd5bd090fa34939`. The file belongs at `art/concepts/characters/CHR_Vellaris_Bloodshield/Vellaris_Bloodshield_concept_v1.webp` but **the exact binary is not yet committed**: its hash is verified from the user upload, not from GitHub. Never claim the image is stored in the repo until a binary check-in and hash readback succeeds.

Do **not** substitute the Shadowspire-branded Razor/Raven panels, the historic Nexusfall roster image, a generic clay model, a plain screenshot, the later simplified blockout dashboard or any MIDNIGHT artwork for this sheet. Those materials can be archived as evidence or character-specific inspiration only when their identity and provenance are recorded. No MIDNIGHT logo, glyph, name or art is permitted in AETHERFALL branding.

The owner-facing game title is **AETHERFALL – REALMS COLIDE** (owner-provided display spelling). Existing repository folders and internal `AETHERFALL: REALMS COLLIDE` machine identifiers are legacy technical IDs and are **not renamed** by this art-direction patch; don't mix the display name with other game titles. Do not edit the original Vellaris image to change its historic caption.

## MUST MATCH: visual language
- **Finish and aesthetic:** premium illustrated gothic fantasy, painterly/anime-influenced faces, richly articulated armour and costume, ornate sharp details, cinematic lighting, magical glow, highly readable silhouettes. No flat generic humanoids or style drift into mundane sci-fi/photoreal military or minimal diagrams unless explicitly approved.
- **Sheet frame:** very dark aubergine/black-violet background, luminous violet/lavender-magenta filigree and delineated panels, silver-white legible typography, an AETHERFALL masthead and crisp iconography. Frame colours remain consistent; hero-specific material colours are **not** forced to match Vellaris.
- **Visual composition:** the third image's 4:3 *character-sheet* master layout, not an approximation: striking hero portrait on the left; consistent front/side/back/three-quarter views above; silhouette studies top-right; facial expressions, armour/material close-ups and palette below; hero identity, unique weapon/focus, gameplay identity; final named ability-icon band and concept-only disclaimer footer.
- **Every panel:** labels, real character-specific content and visual hierarchy must be complete and legible. Don't merely copy the words of Vellaris's abilities; use each hero's own kit.
- **Model handoff:** actual 3D blockouts may show real meshes in the evidence frames, but **a low-poly proxy is not permission to change the approved 2D identity**. A concept illustration is not real geometry or a verified runtime capture.

## No cross-character or cross-project contamination
Keep each approved character's exact owner-approved face, hair, horns, anatomy, outfit, proportions, palette, weapon/unique magic and role. For Vellaris, the bloodshield, crimson spiked pauldrons, pointed ears, lavender-white hair and red cloak are identity locks; they are **not** generic tank features. ThornDell's venom/antlers/Root Bulwark also remain distinct.

**Forbidden on newly produced AETHERFALL assets:** `MIDNIGHT`, `SHADOWSPIRE`, `NEXUSFALL` branding. The first two old image examples may have relevant earlier character information but their logos and layout authority are not canonical for this game. Preserve source evidence; do not silently rewrite history.

## Hard STOP before each character/design job
1. Read `AGENTS.md`, `docs/characters/VISUAL_CANON_LOCK.md`, `docs/characters/CANON_LOCKS.json` and this file plus `docs/art/AETHERFALL_STYLE_CANON.json`.
2. Load and visually inspect the **actual third picture** (check source SHA), plus the exact original owner-approved image for the particular character. If either required image is absent, do **not** claim a canon-matching output. Record the blocker; use a pending proposal only.
3. Register the exact `CHR_...`/asset ID and its plan; state the unique visual identity, role and signature focus.
4. Produce a concept sheet following the standard, with clear source identity and no borrowed brand/other hero traits. A cinematic model render/turnaround is a separate proof type.
5. Attach source-to-candidate comparisons (portrait, four views, signature prop, palette, sheet hierarchy) using `docs/characters/DRIFT_REVIEW_TEMPLATE.md`. Record actual source and candidate checksums.
6. Default state: `PROPOSAL_PENDING_OWNER_REVIEW`. Any material drift or missing critical category is a **FAIL**, not an approval. Only explicit owner acceptance can create a versioned canonical successor.
7. For actual 3D/runtime claims, provide genuine Blender/Godot/device capture and source commit; never use illustration, AI mockup, or GIF as engine proof.

## Machine guards and their limits
`docs/art/AETHERFALL_STYLE_CANON.json` is the machine-readable locked brief. `docs/characters/CANON_LOCKS.json` links its identifier and source SHA; `tools/verify_visual_canon.py` rejects source/style/branding-metadata changes and incomplete proposal sidecars; CI unit tests exercise negative cases. This is a source-contract check, **not** a visual-similarity classifier. Genuine art review and source-specific runtime tests remain mandatory.

**No change to existing approved characters or locked artwork was made by this policy.**
