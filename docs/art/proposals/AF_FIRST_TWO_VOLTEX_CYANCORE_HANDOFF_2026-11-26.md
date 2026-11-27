# AETHERFALL: REALMS COLLIDE — FIRST TWO SOURCE-IMAGE TO REAL GLB BLOCKOUTS

**Work order:** AF-CHR-BLOCKOUT-40172-40158-001
**Status:** PROCEDURAL SHAPE BLOCKOUT / NOT CANON-APPROVED / NOT GAME-READY
**Executor:** Local procedural mesh construction and independent GLB parser; native S.I.R.E. Blender/Godot team execution not established.

## Original references and identities

- `40172.jpg` (actual WebP; archived byte-for-byte at `reference/40172_owner_reference.webp`) shows the existing AETHERFALL **Voltex / Storm Conductor** concept: silver hair, exposed face, golden-white armour, black undersuit, cyan blue energy core, and long sweeping lower-body armour panels.
- `40158.jpg` (actual WebP; archived byte-for-byte at `reference/40158_owner_reference.webp`) shows a **large blue-core armored robot/knight** with silver steel plating, black understructure, cyan chest/helmet/turbine highlights, very large shoulders and crescent-like dorsal blades. It is **NOT assigned to any existing approved character ID**. Its temporary source asset identifier is `CHR_Unassigned_CyanSentinel_CANDIDATE_BLOCKOUT_v01`, not an approval of a new hero.
- Supplemental `40153.jpg`, `40151.jpg`, `40149.jpg` reference Razor and are **not** the first two requested images. `40470.mp4` is a user-supplied video; not model geometry.

## Source → Blockout deliverables

- `models/CHR_Voltex_StormConductor_BLOCKOUT_v01.glb` — 5,472 tris, modular body/armour/hair/energy structures, oriented +Z up and -Y forward, ground-aligned.
- `models/CHR_Unassigned_CyanSentinel_CANDIDATE_BLOCKOUT_v01.glb` — 6,644 tris, separate silver/cyan armour components, ground-aligned.
- Both exported to valid binary glTF (.glb), then independently re-imported with trimesh and rendered with VTK.
- Original screenshots remain untouched, with source SHA-256 in `evidence/verification.json`.
- Six genuinely rendered VTK images are under `evidence/`, plus `FirstTwo_SOURCE_VS_ACTUAL_GLB.png` and build/render logs.

## CRITICAL: not completed in Blender, Godot, or gameplay

This work is **NOT retopology of the shown Meshy/high-poly sculpt**; the actual original 3D mesh data was not supplied. Generated proxy primitives are not suitable for final animation, performance or visual fidelity approval. These exports do not include native Blender .blend sources, deformation rigs, bones, shape keys, baked PBR maps, animation clips, 1P viewmodel hands, physics, AI or gameplay scenes. Do not call the source screenshot a native screenshot. This asset is a shape test only.

## Required S.I.R.E. Blender next stages

1. Obtain original high-resolution Meshy GLB/FBX/OBJ and textures with clear ownership/approval. Keep exactly hashed source; do not move or overwrite approved art.
2. Strip bases/pedestals only from the **game export** (keep originals and pedestal as optional separate prop), clean A-pose and ensure separated limbs; owner review the visual silhouette.
3. Retopologize with genuine edge-flow, reduce to justified budget (3P LOD0 guideline 40k–70k for detailed hero; 1P separate 20k–35k), create LOD1/2/3, and verify 1P/3P same character identity.
4. UV unwrap and bake normal, AO, metallic/roughness, emissive maps. Use consistent texel density and real PBR lookdev.
5. Rig with human/robot-specific twist and mechanical bones; prove shoulder full arcs, finger articulation, robe/coat clearance and no interpenetration. Add gameplay sockets and a separate 1P arms/weapon setup.
6. Generate 4 independent **real Blender** orthographic views; animations/test clips and a genuine GLB import in Godot 4.7.2 with exact source SHA and recorded video. S.I.R.E. independent stage receipt and physical phone/gameplay acceptance remain mandatory.

## Next work decision

Voltex can proceed to owner reference check against any stricter original concept. The cyan-core sentinel must remain **unassigned** until the owner identifies and approves it. No repo merge or release is implied by this package.
