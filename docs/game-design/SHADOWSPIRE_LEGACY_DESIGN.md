# Design concepts safely carried from Shadowspire

**Status: candidates for AETHERFALL, not a playable port.** Source: owner's 18 October 2026 Shadowspire concept brief and historical S.I.R.E. records.

## First playable mission candidate

1. Enter an eclipse-lit gothic courtyard as the historical **Witch Rogue** concept; teach camera, movement and objective display.
2. Fight a **Wraith** using ranged **Witch Bolt**; verify actual enemy HP and attack feedback.
3. Clear the encounter and interact with a crystal/obsidian **anchor**.
4. **Extract a relic**, display rewards and weapon experience, finish the run.
5. Reopen saved progress after exit and verify objectives, items and XP persist.

Historical reports describe an early working local prototype. That source is unavailable, so **no stage above is implemented or verified in the AETHERFALL repository**.

## Worlds and style

- Compact gothic courtyard, spires, eclipse sky, violet lighting, luminous crystals and readable anime-inspired combat silhouettes.
- Possible future realms: Floating Gothic City, Crystal Forest, Shadow Ruins.
- Never override Vellaris Bloodshield or the newly approved ThornDell/Venomroot art. Their current AETHERFALL visual identity takes priority.

## Progression and companions

- **Living weapons** concept: gain XP and evolve through Base, Growth, Elemental, Shadow, Crystal and Fusion forms. Rarity tiers, stats and balance remain unapproved for AETHERFALL.
- **Companions:** Shadow Bat as historic Witch Rogue concept; Moon Ghost, Ember Fox, Star Moth, Stone Gargoyle and Black Cat are unapproved candidates.
- Pet behaviour (scouting/protection), co-op, mods and extended hero roster remain long-term proposals.

## Acceptance before claiming a real port

Source code and assets must be verifiably imported, then tested in native Godot 4.7.2: open → move → Witch Bolt → Wraith defeat → anchor → relic extraction → restart and saved recovery. Record true engine screenshots/video, controls, FPS and source SHA. Headless checks are not visual gameplay proof.

See `../legacy/README.md` for the source and deletion hold.
