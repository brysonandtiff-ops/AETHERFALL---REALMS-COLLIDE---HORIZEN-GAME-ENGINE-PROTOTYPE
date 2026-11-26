# KORVEX — THE HOLLOW TITAN | AETHERFALL visual canon V01

**Owner approval:** 26 November 2026, AETHERFALL: REALMS COLLIDE.  
**Status:** VISUAL CONCEPT LOCKED. A procedural V01 mesh blockout has been produced outside this repository; it is **not** a finished or native-engine-tested character.  
**Original canonical concept image:** `korvex_the_hollow_titan_concept_sheet.png`  
**Concept SHA-256:** `697796f1da2a4561c19671ee20e44f38e830634e61f803a71206204f5d615ec6`

## Preserve this identity

- **ID:** `CHR_Korvex`; role: tank / anti-tank / zone denial / attrition.
- **Body:** exceptionally broad, heavy, monumental gothic walking-mausoleum armour.
- **Head:** helmet with distinctive **vertical violet visor slots** and horned crown.
- **Core:** exposed violet void-soul heart suspended in a **hollow, rib-framed chest**.
- **Silhouette:** layered cathedral-buttress shoulders, stone and blackened iron, bone-shaped spikes, engraved Gothic arches, hanging chains/lanterns, ragged funeral banner.
- **Palette:** blackened iron, grey mausoleum stone, aged bronze/bone, deep violet supernatural light.
- **Signature weapon:** separate `WPN_Korvex_GraveMaul`, an immense two-handed grave maul with cathedral-window construction. **No handheld shield.**
- **Abilities:** Grave Maul, Bone Bastion (rising grave-spires; not a shield prop), Decay Field, Titan's Roar, Hollow Endurance.
- **Group style:** art direction and layout must match owner-approved Vellaris Bloodshield and ThornDell Venomroot sheets while Korvex remains visually 1-of-1.

**DO NOT** substitute the earlier generated Hollow Bastion shield concept, a generic knight, flat silhouette, or other tank's weapon. Any material silhouette changes require owner approval.

## Blockout V01 generated for owner review (external handoff)

| Artifact | File | Export facts |
|---|---|---|
| Editable procedural generator | `build_korvex_blockout.py` | Local Python source; needs NumPy and trimesh |
| Character | `CHR_Korvex_blockout_v01.glb` | 122 object parts; 5,244 triangles; 3.572 m tall; SHA256 `bf0bcc776603b44ca31f7d01ed6ce0abe126a194e6fef7d4e040e94eecc38dfd` |
| Separate weapon | `WPN_Korvex_GraveMaul_blockout_v01.glb` | 38 object parts; 1,348 triangles; SHA256 `45a37bca380f0f8f9362eb215192a2be3299c39a100dd76a29de48ee749108ea` |

The geometry was roundtrip-tested locally with trimesh and captured in a VTK 9.6 preview using the **actual exported GLB data**. These are software 3D mesh previews only, **NOT** Blender screenshots, Godot import/gameplay, rigging, animation, or device acceptance.

Binary GLB and evidence images are in the owner-facing handoff, **not** committed to this branch via the text-only GitHub connector. The asset registry must therefore retain `reserved_no_source` until the corresponding binary is checked in and verified.

## Next gates

1. Transfer the separate .glb exports and the approved concept image under their reserved asset directories, with unchanged hashes.
2. Run Python generator regression; check geometry bounds and triangle counts after independent export.
3. Open the procedural source/GLB in actual Blender, improve detailed shape and topology, save versioned `.blend`.
4. Verify Godot 4.7.2 GLB import, orientation (+Z up, -Y front), rig, materials, collisions, animation and real native capture.
5. Add gameplay/ability implementations only after silhouette and engine import are accepted.

No merge or release without the normal review gates.
