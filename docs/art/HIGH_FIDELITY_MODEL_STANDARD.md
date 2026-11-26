# AETHERFALL — Premium model fidelity & production acceptance (owner visual quality ceiling)

**Contract:** `AF-HERO-QUALITY-CEILING-001` · **Status:** staged review candidate, not native engine evidence. Applies to hero art, enemy creatures, pets and cosmetics without replacing exact approved canon.

## Purpose

Raw AI/Meshy statue previews can look elaborate while containing fused clothing, inaccessible anatomy, unriggable capes, display stands, floating parts, nonmanifold plates, and millions of triangles. **The goal is better gameplay-ready craft than the screenshot**, not merely a re-render with stronger lighting. Retain the visible hero-specific detail as a visual fidelity *target* while creating lighter, animatable, readable assets.

## Five independent scores (each needs human review + evidence)

| Pillar | Required professional improvement | Acceptance evidence |
|---|---|---|
| Canon identity | Same owner-locked face, ears/eyes, body proportions, silhouette, signature colors, individual armor patterns, weapon/focus, accessories, four-angle consistency. | Exact master and native model four-view source-to-output comparison; signed owner review. |
| Animation integrity | Neutral pose, separate limbs, continuous deformation, adequate shoulder/hip/jaw/face edge loops, no floating body panels, controlled cape/hair/chain/antler intersections, shape keys and facial deformation. | Blender actual animation clips: A-pose/neutral, sprint, strafe, attack, jump/dodge, emote and extreme joint poses; cloth/cape simulation pass. |
| Materials and detail | Intentional material differences with baked normal/AO/roughness/metallic/emissive, silhouette-preserving sculpt layers, calibrated metals/bone/cloth/skin/energy, cleaned UV seams. No apparent detail loss from normal maps. | UV sheet, normal/AO bake map proof, material close-ups, glTF texture readback, representative Godot lighting. |
| Gameplay readability | Separately authored first-person viewmodel, clean sightline/reticle, non-obscuring feathers, shield, muzzle and hands; silhouette recognisable at normal combat distance; team-color VFX; separate combat hitbox. | Native gameplay 1P and 3P footage, viewmodel motion checks, ally/enemy comparison, accessibility and combat collision tests. |
| Performance and source trust | Controlled tri count, material draw calls, LOD screen-space transitions, rig constraints, GPU/CPU simulation costs, origin/height and sockets validated; signed exact-source evidence. | Tri/vertex/material reports from real imported mesh; performance telemetry on target device; SHA-256 for source, GLB, screenshots and recordings; independent gate. |

## Working numeric budgets (planning; test rather than assume)

- Third-person hero LOD0: **~40,000–70,000 triangles**, inclusive of attached always-visible meshes. Special large creatures may use a justified independent budget and measured platform target; not a licence for raw 2.46M-triangle gameplay meshes.
- First-person hands/arms/viewmodel: **~20,000–35,000 triangles** including visible focus. For a quadruped, render safe jaw/forelimb content only if first-person gameplay requires it; omit body occlusion while preserving gameplay identity.
- LOD1/LOD2 candidate reductions: **~50%/~25%** of LOD0 as starting targets, subject to visible gameplay distance and material performance; do not decimate facial loops blindly. Optional LOD3/crowd/impostor for long sightlines where measured.
- PBR: prefer three planned **2K** character texture sets, optimized by material need and actual device memory. A 4K source bake need not ship as a 4K runtime texture. Bake normal/AO/metallic/roughness/emissive; use transparent material sparingly.
- Bone/socket counts must come from actual native rig scan, not fabricated from a concept card. 1P and 3P animation retargeting must be proven per character and weapon/focus.
- Performance and responsiveness: capture frame times, draw calls, triangle counts, peak memory and shader compilation on actual supported device. **No invented FPS budgets marked as passed**.

## Art-specific enhancements worth doing

**Vellaris:** Sculpt expressive, identifiable vampiric-elven face (not generic mask), physically plausible silver-lavender hair clumps, **large four-layer jagged crimson pauldrons with arm-clearance testing**, fitted charcoal plate/antique gold, segmented boots and textured split cape; keep the **separate ornate Bloodshield** despite absence from the newest raw sculpt screenshot. Add visual weight without replacing the approved silhouette.

**Razor:** Keep absolute **quadrupedal skeletal predator**. Rebuild articulated scapula/hips and metatarsals, strong skull/jaw proportions, individually sculpted asymmetrical bone plates, secure segmented spine and long tail, deep red ichor glow inside armour channels, independently skinned chain harpoon and visible paw contact. It must sprint, pounce and bite without limb penetration or stretched bone plates. No decorative base in runtime.

**Raven:** Improve original facial likeness, layered raven-feather cape with readable large/medium/small feather rhythm, articulated hood, silver hair strands, clean arm escape points, independent shoulder corvid and separated omen glyph focus. Make feathers respond to strafe/aim/cast without trapping arms or obscuring first-person sightlines. Confirm the exact approved Omen/Echo weapon version instead of silently choosing a contradictory draft.

**Unassigned A & B:** Preserve the red lantern heroine and untextured spectral figure as *separate unassigned references*; no copying their outfits to named heroes, or merging their files into one character.

## Rig and gameplay stress acceptance matrix

- **Humanoid extreme poses:** arm raise/abduction, aiming over shoulder, crouch, slide, jump landing, forward sprint, reverse strafe, turn-in-place; visible cape/feather/paulettes clipping reviewed from front/side/back.
- **Quadruped:** four-paw ground contact, diagonal trot, canter/gallop, rapid turn, crouch/pounce, jaw bite, chain harpoon fire/pull, tail sweep; spine deformation and foot-IK tested on slopes/steps.
- **VFX:** no opaque screen-obscuring bloom; silhouettes visible through hostile zone effects, high-contrast gameplay telegraphs and color-blind-safe outline alternatives.
- **Network/combat:** server-owned damage/cooldowns; VFX non-colliding; physics props are cosmetic unless explicitly authored as separate hitboxes; camera 1P/3P cannot change targeting advantage.

## Stop/go proof labels

`SCREENSHOT_REFERENCE` → `SOURCE_MESH_VERIFIED` → `CANON_REVIEWED` → `BLENDER_MODEL_VERIFIED` → `RIG_ANIMATION_VERIFIED` → `GLB_SEALED` → `GODOT_IMPORT_VERIFIED` → `GAMEPLAY_TESTED` → `OWNER_APPROVED_FOR_STAGE`. Each gate is **BLOCKED unless genuine evidence exists**. A model can look spectacular in a screenshot and still fail as a game asset.

Existing AETHERFALL character and S.I.R.E. LAW-108 stages are authoritative; this supplemental quality contract does **not** add a duplicate release agent or bypass a prior gate.