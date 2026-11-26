# CHR_Temporis — Chronowarden support concept plan

**Stage:** AETHERFALL adaptation proposal / pending owner approval  
**Reserved ID:** `CHR_Temporis` | **Role:** time-control rescue + positional support  
**Source:** owner's 2026-11-26 Shadowspire support-expansion concept sheet (see `SUPPORT_PAIR_PHASE_01.md`)  
**Evidence status:** concept planning only; NO Blender model, rig, Godot import or gameplay verified

## Character promise

**“She doesn't just heal damage; she gives an ally one moment back.”**

Temporis is the high-skill **clutch rescue** support. Players track threats, preserve an anchor for the right ally and use a limited rewind to turn a lost fight without reverting the objective or the entire match. She is strongest with good timing and awareness, weakest when rescue abilities are on cooldown.

## Six ability slots — source-faithful names, provisional gameplay rules

| Slot on source sheet | Ability | Intended player-facing behavior | Prototype safeguards |
| --- | --- | --- | --- |
| LMB | **Chrono Beam** | A visible beam heals one ally and provides a small amount of recent-damage recovery. | Requires valid target and line of sight; cannot heal beyond maximum HP or restore unlimited prior damage. |
| RMB | **Time Anchor** | Marks one ally with a visible temporal anchor. One lethal hit in its valid window triggers a survival rescue and limited return toward a recorded safe location. | Only one active anchor per caster; consumption is atomic; rescue is interruptible/counterplay-readable. |
| E | **Phase Rewind** | Rewinds a living ally's eligible state by **3 seconds**: restores bounded lost HP, may cleanse designated harmful effects, attempts safe relocation. | No resurrection, score rewind, objective rollback, cooldown refund or unsafe teleport. |
| Q | **Time Dilation Field** | Place a bounded clock-dome: enemies inside are slowed, allies gain a modest movement advantage, ally healing is slightly enhanced. | Finite size/duration, non-stacking limits, clear enemy warning and exit path. |
| Passive | **Temporal Echo** | Effective ally healing leaves a short healing echo (source sheet: **2-second echo**). | Each valid heal produces at most one bounded echo; cannot spawn infinite echo chains. |
| Ultimate | **Reset Protocol** | Cast a large temporal field and restore eligible allies toward their **5-second** recorded state (health, safe position and permitted debuffs). | Resolve snapshots server-side if PvP; limited restore budget; no rewinding kills, inventory or objective capture by default. |

**Note:** Timing is from legacy concept art, not an approved balance contract. Ranges, costs, cooldowns, heal values and full death interactions need design/playtest signoff.

## Core interaction loop

1. Observe the fight and mark the endangered frontliner or objective holder with **Time Anchor**.
2. Use **Chrono Beam** to sustain between heavy hits; prioritize threat detection over raw healing volume.
3. Deploy **Time Dilation Field** for a retreat, contested objective or controlled team push.
4. Spend **Phase Rewind** on a single well-timed save; reserve **Reset Protocol** for a team collapse rather than routine healing.
5. Opponents can pressure Temporis during cooldowns, split the team, bait an anchor and disengage from the dome.

## Silhouette + art blockout (owner review, not an art lock)

**Reference anchors to preserve for review:** pale silver-lilac hair, metallic violet-and-gold temporal armour, floating clockwork / zodiac dial behind upper body, an ornate luminous hourglass as chest focus, purple time trails and layered asymmetric robes. The design should read as a **chronomancer**, not a shield tank.

**Greybox decomposition:** head + swept hair mass; high collar; controlled width shoulder plates; slim central torso; hourglass housing; two detached clock rings; layered skirt panels; hands with casting poses; identifiable rear profile. The rings must not cover target indicators or obscure a third-person camera. Establish front/side/back/3/4 proportion sheets before sculpting details.

**Animation signatures:** rewind gesture pulling an invisible thread backward; Time Anchor placing a hovering clock glyph over an ally; one-hand beam pose; two-handed ultimate clock rift. Use distinct silhouette poses for each state.

**Accessibility / readability:** time effects need shape, sound and countdown in addition to violet/gold; allies and enemies must distinguish anchor-active, rewind-armed and expired states.

## Proposed technical contract for an eventual Godot prototype

- Track a rolling, timestamped **bounded ally-only history** for eligible fields; specify memory and sample rate after team size is set.
- Use stable ally IDs, valid snapshots, safe-transform checks and explicit combat event IDs to prohibit double refunds of the same damage.
- Evaluate rescue/rewind atomically against the authoritative combat state; make overlapping anchor and rewind resolution deterministic.
- Rewind failure must degrade gracefully: never put a character in geometry or erase progression. Log an explicit result reason.
- Structure input through action names rather than hardcoding the original LMB/RMB/E/Q labels.

## Acceptance test checklist (not run)

- Chrono Beam healing respects LOS, max HP and damage-rewind caps.
- Anchor triggers **once**, only for its owner target and within its valid window; never creates an endless death loop.
- Three-second rewind handles stale snapshots, out-of-bounds positions, collisions, debuff whitelist and disconnects.
- Dilation field respects radius, expiry, team membership and overlapping modifiers.
- Echo cannot self-trigger; predictable healing amount under packet duplication.
- Five-second ultimate resolves two simultaneous target rewinds deterministically; objective score never rewinds.
- Controller input, effect visibility, adverse network states, FPS/VFX budget and native Godot import pass when a runner exists.

## Unresolved decisions

Confirm rewind-to-position versus HP-only fallback, allowable debuffs, interactions with downed allies, whether Time Anchor is dispellable, and the exact visual model relative to approved AETHERFALL heroes. Do not promote this proposal to `aetherfall_approved` or `implemented` without owner acceptance and separate actual evidence.
