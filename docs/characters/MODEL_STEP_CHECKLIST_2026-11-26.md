# AETHERFALL – REALMS COLIDE | Hero models — exact step checklist
**Evidence snapshot:** 2026-11-26. **This is a production checklist, not completed-model certification.**

Legend: **C** = visual concept recorded; **V** = rendered 3D preview recorded; **B** = separate offline procedural GLB blockout documented; **G** = GLB/.blend committed to AETHERFALL default branch; **E** = native Blender + Godot source-specific verification; **P** = playable, tested character. \`✓\` means evidence recorded at the stated strength; \`—\` means not evidenced. Existing screenshots/turnarounds are not a substitute for the original source mesh.

| Role | Hero | C | V | B | G | E | P | Production truth |
| --- | --- | :---: | :---: | :---: | :---: | :---: | :---: | --- |
| Tank | Vellaris | ✓ | ✓ | — | — | — | — | Concept approved; 3D proxy/turnaround shown, original GLB not verified in main. Draft PR #13 includes no model binary. |
| Tank | Thorndell / ThornDell | ✓ | ✓ | — | — | — | — | Antlered venom tank turnaround exists; GLB not verified. |
| Tank | Korvex | ✓ | ✓ | ✓ | — | — | — | Separate offline reconstruction manifest reports three GLB exports, 25 offline checks; original Korvex GLB not recovered, native Godot/Blender not tested. |
| Tank | Dreadhull | ✓ | — | — | — | — | — | Concept only. |
| Tank | Morrigan | ✓ | — | — | — | — | — | Concept only. |
| Support | Pixi | ✓ | — | — | — | — | — | Concept only. |
| Support | Noxis | ✓ | — | — | — | — | — | Concept only. |
| Support | Orion | ✓ | — | — | — | — | — | Concept only. |
| Support | Temporis | ✓ | — | — | — | — | — | Concept only. |
| Support | Symbion | ✓ | — | — | — | — | — | Support character, not Tank; concept only. |
| Damage | Razor | ✓ | ✓ | ✓ | — | — | — | Quadruped silhouette and 3D preview recorded; offline model handoff reported but not imported to main. |
| Damage | Raven | ✓ | ✓ | ✓ | — | — | — | Hooded omen sniper / wormhole direction; offline model handoff reported but not imported to main. |
| Damage | Voltex | ✓ | — | — | — | — | — | Roster concept only. |
| Damage | Vyra | ✓ | — | — | — | — | — | Roster concept only. |
| Damage | Khaelis | ✓ | — | — | — | — | — | Roster concept only. |

**Summary:** 15 planned heroes; **3** separately documented offline blockouts (Korvex, Razor, Raven) from external project records; **2** additional preview-only heroes (Vellaris, Thorndell); **10** concept-only; **0** native Godot-verified playable heroes; **0** GLB/.blend hero files committed to AETHERFALL \`main\` as of this snapshot. Vellaris's separate proxy artwork does **not** move her to verified GLB without an exact source file and readback.

## For every hero: step checklist
- [x] Identify concept and locked source or explicit candidate status.
- [ ] Archive the **exact original** owner reference bytes/hash in the canonical asset location.
- [ ] Build an editable Blender model without drifting away from each hero's own face, silhouette, gear and palette.
- [ ] Export **actual** versioned GLB and separate weapon/focus GLB, store SHA-256 receipts, re-import offline.
- [ ] Produce genuine four-angle Blender screenshots/video and mesh audit (topology, UV, rig, materials, LOD).
- [ ] Owner-approved source-to-model comparison using the THIRD Vellaris infographic as **art-style standard** (not a clone of Vellaris).
- [ ] Re-import in actual Godot; verify scale, materials, 1P/3P rigs, animations, abilities and collisions.
- [ ] Run gameplay, persistence, accessibility, performance, device and regression tests; link source commit and real media.

The GitHub main repository's \`art/asset_registry.json\` currently reserves **10** character IDs with \`status=reserved_no_source\`. Razor/Raven plus Voltex/Vyra/Khaelis do not all exist in that register yet. Register only under reviewed IDs and don't silently promote a legacy Shadowspire concept to AETHERFALL engine approval.

**No mixed branding:** The game is **AETHERFALL – REALMS COLIDE**, not MIDNIGHT, SHADOWSPIRE or NEXUSFALL. **No silent canon drift.**
