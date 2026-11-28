# Level 01 — The Unbound Reach

Project: AETHERFALL: REALMS COLLIDE. Goal: test the game in the owner's practice range before building any competitive map. Work is under the existing HORIZON/Godot repository and its checks; no external agent or hero asset is asserted. Status: first training blockout, not final environment art. Owner's design source: the conversation's dark technical plate titled THE UNBOUND REACH / PRACTICE RANGE. Original file SHA-256: `a4d29cb7d569a93604127257cef3b3d1dc98f02d9c3e9518b95818d7b8a50109`. The Split Gate board is not a second level in this work order.

## Try it
Open `game/project.godot` in the project's Godot 4.7.2 stable editor and press F6 on the range scene or F5 to test the complete entry point. At the observation glass you face the valley. Click to capture the mouse, move the mouse to turn around to the three terminals. WASD moves, Shift runs, Space jumps, Escape releases the mouse. E near Practice Mode cycles the portal destination; E at Custom Drills changes drone respawn time; E at Quick Portals enters the selected zone. Click again to fire a test ray. In Rescue, use E once to revive a pod and again to heal it. T resets counters and targets. R returns to the Hub. No gamepad, touchscreen, networking, audio or hero loadouts certified.

## Blockout contract
| Zone | Board dimensions | What must read in play |
|---|---|---|
| Hub | 25 m wide, +28 m | Curved observation glass, spire beyond the central arena, consoles and quick port. Arrival is offset from the deck centre so the floor does not obscure the valley. |
| Arena | 30 m diameter, 0 m | Sandstone ring, four cardinal approaches, radial pillar cover and red drills. |
| Sniper A–D | +8 to +14 m | Violet perches at four corners; climb the ramps, check 45–80 m attack lines. |
| Rescue | 24 m across, +6 m | Emerald pads, four allies, partial cover. |
| Drone tracks | Two 60 m ovals, +10 to +22 m | Six targets on each rail, cyan flight rings. Prototype interprets 60 m as the major span shown in the drawing, not the lap distance. |
| Arch | 12 m span, 0 to +4 m zone | Sheltered western route with return portal. |

Coordinates between labelled features, scenery beyond the valley and the test body are implementation choices, not additional approved canon. Waterfall strips, crystals, architecture, drones and pods are blockout geometry. Native pixels, not this reference, are the evidence. No match rules, capture points, competitive spawn logic, or playable hero models have been added.

## Gate before the first match map
Run the repository validator and adversarial suite; then `GODOT=/path/to/Godot bash tools/unbound_reach_evidence.sh /tmp/new-unbound-evidence` on a Linux graphical test host with Xvfb, Mesa and FFmpeg. Output records both the tested checkout and PR head. Compare the native hub, arena, sniper and rescue captures against the original. Review actual ramp traversal, sightlines, mantle and melee mechanics, kit integration, performance, accessibility, controller/touch and real-device controls separately; an automated zone warp is not proof a player walked the route. No competitive level work or art acceptance until the owner approves these gates. Rollback is not merging the draft or reverting its integration through normal repository review.
