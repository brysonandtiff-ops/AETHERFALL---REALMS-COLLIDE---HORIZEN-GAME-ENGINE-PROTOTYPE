# HORIZEN model and combat production law — AETHERFALL

Status: **work-order template; no game models or combat execution verified by this file.** The approved `docs/characters/VISUAL_CANON_LOCK.md` and `docs/characters/CANON_LOCKS.json` in the AETHERFALL repository outrank any generated illustration. The exact original reference image must be present for character production; SHA-only records cannot establish likeness.

## 1. Board requirements (every character)

A 4:3 master board uses the established AETHERFALL dark gothic-cosmic obsidian/amethyst frame with hero-specific energy trim and hexagonal role/sub-role badges. Preserve a three-quarter splash portrait, title, lore, playstyle and identity anchors. Provide front, side, back and three-quarter-back turnarounds, multiple silhouettes, 4–5 expressions or species gestures, palette/material swatches and part callouts. Include the 3P idle, walk (contact/down/passing/push-off), sprint, strafe, dodge, jump and crouch/slide strip with realistic weight and trailing cloth/hair/chain/tendril motion. For every LMB/RMB/E/Q/Passive/Ultimate show unique gameplay purpose, first-person and third-person readability, wind-up, active hit, follow-through, and resource/cooldown constraints; the ultimate gets a three-beat activation/peak/aftermath breakdown. Ally and enemy VFX must be directionally distinct and must not obscure the center 1P sightline.

**No canonical promotion** from generated boards, a mesh screenshot, staging receipt or a source-level unit test. Never substitute another hero's face, colours, silhouette, weapon, shield or kit. In particular, do not transfer Vellaris's personal bloodshield to other tanks. Keep owner-approved master bytes unchanged, version all proposals, and require actual source-to-output comparison and owner approval.

## 2. Blender source → Godot export

1. Import `.glb`, `.fbx` or `.obj`, set metres and unit scale 1, ground the feet/creature stance, remove only the display pedestal, split weapon and gear into separate objects, apply transforms.
2. Repair non-manifold geometry and outward normals. Symmetrise **only** when the canonical silhouette permits: preserve asymmetrical horns, capes, armour and root structures.
3. Preserve raw high-poly in a protected source collection. Retopologise with anatomical edge loops and crisp hard-surface bevel control; track actual triangles (~40–70k 3P and ~20–35k 1P design targets, not automatic approval). Create measured LODs.
4. Unwrap UVs, pack islands with padding and consistent texel density. Bake normal, AO, base colour, roughness, metallic and emission; verify the real imported PBR appearance, not just map filenames.
5. Rig in an A-pose or appropriate neutral animal stance, clean twist bones and skin weights; create named weapon/shield/muzzle/core sockets. Export clean `.glb` / `.fbx`; check the native Blender four-angle deform tests and exact-version Godot import with source hashes.

## 3. Combat & AI contract

Each ability in **both 1P and 3P** must have these authoritative phases: `WIND_UP_TELEGRAPH → ACTIVE_HITBOX/PROJECTILE/ZONE → RECOVERY/FOLLOW_THROUGH → COOLDOWN/RESOURCE`. Attack collision volumes and gameplay timing are distinct from particles, fog, bloom and visual effects. Implement target priority, navigable obstacle avoidance, dynamic line-of-sight, range bands, movement/turn speeds, foot-IK and jump/dash/cover transitions. Ultimate: activation callout → peak release/zone/mode → aftermath. Multiplayer authority, replicated state and anti-cheat require actual server-run integration tests before any PASS claim.

## 4. Evidence and release gates

Submit exact original/image source SHA, native editable source SHA, export hashes, measured topology, native renders and genuine unedited runtime capture, exact source commit, tested engine and device identifiers, test output and owner signoff. Browser WebGL/Canvas2D can preview uploaded source triangles but **cannot** establish Blender or Godot scene startup, rigging, gameplay, animation, network correctness, frame rate, phone acceptance or external store clearance. S.I.R.E. verifies and stages; distributors hold final publication authority.

## 5. Work order acceptance checklist

- [ ] Exact locked owner reference inspected (not inferred from notes).
- [ ] Hero-unique role, kit, material, silhouette and 1P/3P board approved.
- [ ] Real high-poly, retopo, UV/PBR, rig/socket and export source files exist and are hashed.
- [ ] Native Blender four-angle and deformation evidence captured.
- [ ] Native Godot import, animation, combat and AI tests run with proof.
- [ ] Genuine runtime screenshots and video linked to source commit.
- [ ] Real phone/target-device and release-gate review complete.

Every unchecked item remains **NOT VERIFIED**, never a simulated PASS.
