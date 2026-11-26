# Support pair — Phase 01: Temporis + Symbion

**Project:** AETHERFALL: REALMS COLLIDE  
**Stage:** DESIGN PROPOSAL / OWNER REVIEW — not locked AETHERFALL canon, gameplay, or a playable build  
**Date:** 2026-11-26  
**Authorised executor:** Connected GitHub documentation workflow; future Blender/Godot work requires approved executors and real runner access  
**Identifiers:** `CHR_Temporis`, `CHR_Symbion` (already reserved; do not rename)

## FIND — verified source and current state

- Owner-supplied Shadowspire reference sheet, **“Support Expansion — 2 New Unique Concepts”**, filename `39397.png`, 1536 x 864 pixels, SHA-256 `886e712d196f61e7c59faf20a1f94cd314e42f7455d4a74212149b4cca738021`. The original image is attached in the conversation; its bytes are **not** committed or claimed as archived in this repository.
- `docs/characters/LEGACY_ROSTER.md` preserves both names as historical Shadowspire support selections. `art/asset_registry.json` marks both `reserved_no_source` and as legacy candidates, **not** AETHERFALL-approved finished characters.
- `art/concepts/characters/CHR_Temporis/`, `art/concepts/characters/CHR_Symbion/`, their `art/blender/characters/` and `game/assets/characters/heroes/` counterparts are reserved locations, **not** proof of art/model exports.
- Repository is a Godot 4.x / Blender scaffold. Active gameplay, network model, final camera, team size and match rules are not implemented or verified.

## PLAN — two supports with fundamentally different value

| Design axis | Temporis — The Chronowarden | Symbion — The Living Bond |
| --- | --- | --- |
| Combat promise | **Prevent a bad moment**: rescue, reposition, timed area control | **Make an ally stronger over time**: sustained links, adaptations, organic protection |
| Tempo | Reactive / clutch / precision windows | Proactive / momentum / maintained connection |
| Defining mechanic | Bounded 3–5-second **ally-state rewind**, not global world rollback | **Living bond** with capped shared vitality and match adaptation |
| Healing shape | Short tactical bursts, echoes | Continuous regeneration and buffs |
| Counterplay | Anticipate anchor, bait rewind, separate allies, pressure between cooldowns | Break link by distance/line of sight, force tough target choices, deny buildup |
| Visual read | Ivory-lilac / violet-gold, mechanical clocks and hourglass | Ebony / dark-crimson / bio-magenta, living tendrils and luminous spore flower |
| Gameplay weakness | Limited sustained recovery while major saves are down | Vulnerable when separated from linked allies; no personal time reset |

### Reference kit retained for concept testing

**Temporis:** Chrono Beam, Time Anchor, Phase Rewind, Time Dilation Field, Temporal Echo (passive), Reset Protocol (ultimate).

**Symbion:** Symbiotic Lash, Shared Vitality, Adaptive Spore, Bio-Forge, Evolution Bond (passive), Ascendant Fusion (ultimate).

The original sheet uses LMB/RMB/E/Q controls. These labels are **reference slots**, not approved PC/gamepad bindings. Define action names and controller bindings only after input and combat-loop decisions.

## Design safeguards / first prototype contract

1. **No generic support clones:** Temporis excels at timed recovery but is not a continuous-link healer; Symbion grows team power but cannot undo a kill.
2. **No immortality stacking:** One active Time Anchor per Temporis, bounded rescue windows; protect against duplicate recovery of the same damage event. Shared Vitality has a finite transfer budget and cannot generate unlimited shields.
3. **No global undo:** Rewind only explicitly approved ally state fields (HP, position, eligible debuffs). It never reverses match score, objective progress, ammo economy, server events, deaths or another hero's cooldowns by default.
4. **Safe positions:** Every rewind relocation requires world/navmesh/collision validation. If the snapshot is blocked or off-map, preserve current valid position and apply only permitted restorative effects.
5. **Readable PvP:** Anchor icons, link ownership, countdowns, ability interrupt/expiry, field boundaries and empowered-state VFX must be clear to teammates and opponents; include non-colour cues.
6. **Network-safe by design:** If multiplayer is selected, the authoritative simulation decides saves, targets, line of sight, positional snapshots and ultimate resolution. Never accept client-supplied HP/history.
7. **No unapproved lore lock:** Adapt silhouettes and materials to approved AETHERFALL art direction only after an explicit owner review. Shadowspire is reference inspiration, not a replacement for existing canon.

## Production sequence and acceptance

| Gate | Work | Proof needed before moving on |
| --- | --- | --- |
| P0 — review | Owner selects/revises kits, visual distinctions, camera, match rules and core counterplay | Approved design revision + decision log |
| P1 — greybox | Reusable ability contracts, target/link model, bounded ally history, dummy support interactions | Actual executable logic tests, deterministic scenarios |
| P2 — art blockouts | Separate original Blender greybox silhouettes and turnarounds for each hero | Genuine Blender front/side/back/3/4 captures and editable source |
| P3 — playable slice | Godot imports, character controllers, four abilities/passive/ultimate and a small team objective encounter | Genuine native Godot import, combat/interaction evidence |
| P4 — harden | Break/edge-case, balance, accessibility, controller, persistence/network if applicable, performance tests | Real tests and unedited screenshots/video, source SHA, engine/device IDs |
| P5 — acceptance | Owner reviews measured playtest behavior and visual comparisons | Recorded approval; then update concept status via reviewed change |

### Cross-character checks

- Temporis rewinding a Symbion-linked ally **must not** replay previously paid link healing/damage transfer.
- Symbion link must detach/reconnect according to explicit range and alive rules when its target is rewound.
- Time Anchor cannot recursively re-trigger from Symbion's shared-damage effects.
- Reset Protocol cannot reset Evolution Bond stacks unless that rule is deliberately chosen and tested.
- If Symbion boosts an ally inside Time Dilation Field, stacking effects have explicit caps and UI.
- Objective state persists through rewinds even when a hero returns to a prior location.

## Open decisions — owner / combat-design review

1. Is combat real-time, turn-based, or a hybrid? The historical sheet assumes real-time seconds. A turn-based version would translate these to bounded turns and explicit activation ordering.
2. Team size, respawn/downed state, objective cadence, camera and match duration.
3. Whether Reset Protocol can rescue a *downed* ally; true resurrection is **not** silently included.
4. Exact duration/range/cooldown/resource values, evolved bond tiers and a fair anti-stall rule.
5. Final controller/UI mappings, VFX limits, performance targets and AETHERFALL-canonical final art direction.

**Not completed:** No art binaries imported, no gameplay authored, no native runner tests, no real screenshots/video. The separate character proposals are `CHR_Temporis_SUPPORT_PLAN.md` and `CHR_Symbion_SUPPORT_PLAN.md`. Follow `AGENTS.md`, `docs/art/ASSET_PIPELINE.md` and `docs/evidence/PROOF_REQUIREMENTS.md`.
