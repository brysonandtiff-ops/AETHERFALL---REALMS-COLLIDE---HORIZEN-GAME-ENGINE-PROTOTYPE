## Change

Describe what changed and link the work order.

## Tests performed (exact commands and results)

- [ ] Structure validator run (or explain why not)
- [ ] Native Godot project opened and main scene run (only check if really performed)
- [ ] Native Blender import/export tested (if relevant)
- [ ] Physical device tested (if relevant)

## Art and evidence

- [ ] No approved reference artwork overwritten
- [ ] Original art and exported GLB stored separately
- [ ] Genuine screenshots/video/hashes attached when actual visual/runtime change is claimed
- [ ] Not-run or blocked checks clearly identified

## Risks / rollback

State known limitations and exact revert instructions. No auto-deploy or merge.

## Character-specific signoff if relevant

- [ ] All changed characters have registered unique IDs and matching `docs/characters/plans/<ID>.json`.
- [ ] Owner-approved unique silhouette, ability kit, palette and focus; not a generic shield copy.
- [ ] Original concept binary, hash and provenance committed, **or gate honestly pending**.
- [ ] Genuine Blender/Godot/device evidence for any production status claims, or explicitly not run.
- [ ] No legacy character silently promoted; Corvex/Korvex spelling checked.

## Visual canon drift gate (for character art)

- [ ] Viewed exact source media and locked manifest, not merely a remembered text prompt.
- [ ] Verified actual file signature/extension, SHA-256 and pinned source identity; did not replace original.
- [ ] Provided genuine side-by-side source-to-output comparison: face, hair, shape, silhouette, materials, props, four views, infographic layout and role/kit.
- [ ] Owner approval explicitly recorded; until then saved as proposal, not new canon.
- [ ] Cross-PR conflict (including Razor/Raven weapons) and alias (including Corvex/Korvex) reconciled.
- [ ] Native engine/model/device status reported accurately.

## AETHERFALL art-style hard lock — required for visual content

- [ ] Used **exact Vellaris + Korvex original style references** (SHA-256 in `docs/art/ART_STYLE_LOCK.json`) with the correct hero's separate identity reference.
- [ ] No NEXUSFALL/Shadowspire branding or screenshot UI from the roster composition-only source.
- [ ] For a FULL_CHARACTER_INFOGRAPHIC, checked 4:3, >=1536x1152 and all 11 required panels (front/side/back/three-quarter, portraits, materials, silhouette, focus, kit, disclaimer).
- [ ] For BLACK_BACKGROUND_HERO_KEY_ART, clearly marked **not a full sheet**.
- [ ] Proposal has correct `<image>.review.json` plus style-lock ID, original reference hashes, candidate hash, origin and pending-owner-review state.
- [ ] Showed actual original-versus-output comparisons to owner; no AI/self attestation of final visual match.
- [ ] Ran `python3 tools/verify_art_style_contract.py` and `python3 -m unittest discover -s tests -v`; report exact result and any blockers.
