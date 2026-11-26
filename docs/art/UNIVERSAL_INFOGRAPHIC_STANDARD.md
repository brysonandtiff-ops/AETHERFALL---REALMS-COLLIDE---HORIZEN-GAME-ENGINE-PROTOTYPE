# AETHERFALL: REALMS COLLIDE — Universal Infographic Design Standard

**Work order:** AF-ART-INFO-001 · **Issue date:** 2026-11-26 · **Review state:** proposed branch; owner approval of new assets still required.
**Parent authority:** S.I.R.E. universal visual planning law SIRE-ART-INFO-001. **Existing authority remains:** docs/characters/VISUAL_CANON_LOCK.md, docs/characters/CANON_LOCKS.json and docs/characters/CHARACTER_WORKFLOW.md.

## The reference is the presentation standard — not a character template

Use the exact owner-provided **Vellaris — The Bloodshield** sheet (uploaded as 39403.png; actual format WEBP, 1536×1152, ratio 4:3, SHA-256 `4d100d50cf0769da47cbe1b782deeb842d15a11c1c46a08f8bd5bd090fa34939`) as the **layout, finish and information-density reference** for every newly planned AETHERFALL visual asset.

- Framing: deep gothic violet-black with magenta and lavender energy borders, readable bright text, ornate separators, upper logo bar and atmosphere compatible with the project. Individual object/character material palettes are NOT required to be purple or red.
- Architecture: dominant hero visual on the left; top centre main views; top right silhouettes or composition studies; centre faces/parts/materials; lower identity/function/weapon/gameplay panels; a labelled strip of abilities, mechanics or interaction steps at bottom; explicit evidence/status disclaimer in the footer.
- Default art board: 1536×1152 (4:3). Do not confuse image dimensions/format with the filename supplied by chat. Preserve exact sources and artwork, including Vellaris's and ThornDell's approved silhouettes and weapons.
- Visual quality: high-end illustrated/3D development renders, consistently lit, clear original detailing, legible headings, disciplined iconography, no unrelated stock heroes or generic duplicated shields.
- Truth: label new generated boards **PROPOSAL_PENDING_OWNER_REVIEW**; concept illustration is not a native model, Blender file, GLB export, Godot screenshot, real gameplay or real device capture.

The original reference remains an external owner upload; its byte hash is pinned in character canon metadata but its actual binary is **not yet verified as committed to GitHub**. The existing locks take priority. No design is promoted by typography printed inside a generated image.

## Mandatory panel mapping: use the same style, show the right information

| Asset family | Standard panels and callouts |
| --- | --- |
| **Characters, heroes, tanks, DPS, supports, bosses, enemies, NPCs** | Hero portrait, front/side/back/3-quarter, eight or fewer clear silhouette variations, face/helmet expressions when applicable, armour/material swatches, unique weapon/focus, identity, movement/gameplay and full abilities/passive. |
| **Weapons, armour, relics and equipment** | Hero view, front/side/rear or 3/4, scale reference, mechanism or construction cutaway, attachments, material samples, attack/use stages, VFX, limitations. |
| **Objects, props and interactables** | Hero view, four views as relevant, dimensions/scale, close-ups, materials and wear, states, interactivity, placement and collision handoff. |
| **Maps, levels, arenas and realms** | Key environment illustration, top-down map, side elevations/camera views, entry/spawn/exits, sightlines and cover, combat routes, objectives, vertical traversal, zones, lighting, material palette and performance constraints. |
| **Buildings and architecture** | Key view, exterior/front/side/back, floor plan, interior, facade/materials, player-scale reference, traversable zones, interactions and destruction states if applicable. |
| **Creatures, wildlife and vehicles** | Hero render, turnarounds/silhouettes, anatomy or components, locomotion/animation, attack/utility sequences, physics/scale and interaction. |
| **UI, HUD, menus and visible systems** | Key interface screen, responsive layouts and states, typography/colours/components, interaction maps, loading/empty/error states, accessibility and target platform. |
| **VFX, abilities and audio-reactive visuals** | Key frame, timed sequence/storyboard, palette/material, trigger and telegraph, gameplay visibility, performance, audio cues and fallback. |

Every board includes the project header, stable proposed asset ID, role/type, version, status, explanatory labels and a clear footer. If any section does not apply, an owner-approved waiver must explain it; never remove it silently. Supplement the visual board with a searchable text/JSON plan to prevent image-rendered text mistakes becoming 'canon'.

## Design-first gate and status

1. **FIND:** Read canonical references and registered asset IDs. Check existing files to avoid duplicate or renamed heroes.
2. **PLAN:** Build a complete illustrated infographic and machine-readable brief; mark owner decision **pending**.
3. **REVIEW:** Check panel completeness, consistency of all views, scale, unique silhouette, materials, kit/function, accessibility and text accuracy against the real source.
4. **APPROVE:** Owner explicitly approves the particular revision. Archive its unaltered original image bytes, correct format and SHA-256; update its recorded concept/approval status without deleting history.
5. **BUILD:** Create source Blender or game scene only from approved specifications; new renders stay separate from source images.
6. **TEST/PROVE:** Use real Blender/Godot renders and input-tested gameplay to certify runtime. Maintain exact source commit/asset hashes and full animation clips per S.I.R.E. LAW-105.
7. **FINISH:** A complete design is a documented *concept*, not a playable feature. Do not claim anything beyond available evidence.

**Exception:** Technical-only changes with no new visual design do not require a decorative infographic. Historical approved assets can be indexed as pending infographics without breaking working builds or overwriting art.

## Naming, storage and future automation

- Machine-readable standard: `docs/art/INFOGRAPHIC_POLICY.json` (includes asset-type panel rules and source integrity).
- Reusable manifest: `docs/art/INFOGRAPHIC_PLAN_TEMPLATE.json` (copy and fill for each planned asset; statuses begin pending).
- Archive original concept sheets under the correct `art/concepts/<family>/<asset-id>/` after source integrity verification; keep variants in a clearly named `proposals/` folder and preserve originals.
- Game assets/models belong separately in `art/blender/` and `game/assets/`; never insert a 2D concept board as proof of a finished 3D asset.
- Source-level checks can validate policy identity and field completeness. Only genuine side-by-side owner review, real engine testing and device media can establish art fidelity or gameplay.
- Existing registry character IDs and previous approvals are preserved. Any new Bryce/Bryskar proposal remains unapproved until explicitly accepted.

## Acceptance checklist

- [ ] Exact source image and SHA-256 obtained and preserved
- [ ] Proposed asset ID, role, status and version documented
- [ ] Complete asset-specific 4:3 infographic with readable panel titles
- [ ] Multi-view continuity plus visual and functional identity reviewed
- [ ] Materials, mechanics, accessibility, technical constraints captured
- [ ] Generated text corrected in companion spec if necessary
- [ ] Owner comparison and sign-off recorded for this exact revision
- [ ] Appropriate genuine native engine/runtime evidence attached **only when claimed**

This document expands the sheet standard to **ALL visual asset families**. It does not silently change existing Vellaris, ThornDell, Razor, Raven, Korvex or other character canon.
