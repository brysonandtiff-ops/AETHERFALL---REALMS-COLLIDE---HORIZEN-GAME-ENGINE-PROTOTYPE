# CHR_Symbion — Living Bond support concept plan

**Stage:** AETHERFALL adaptation proposal / pending owner approval
**Reserved ID:** `CHR_Symbion` | **Role:** symbiotic tether healer + adaptive ally empowerment
**Source:** owner's 2026-11-26 Shadowspire support-expansion concept sheet (see `SUPPORT_PAIR_PHASE_01.md`)
**Evidence status:** concept planning only; NO Blender model, rig, Godot import or gameplay verified

## Character promise

**“The longer the bond survives, the stronger the team becomes.”**

Symbion is a **proactive growth support**, not a time healer or another shield-bearing tank. She picks a partner, survives to protect the connection, and evolves support effects in response to the fight. She is strongest with cohesive teammates and visible coordinated pushes, weakest when range/LOS breaks or enemies force rapid target switches.

## Six ability slots — source-faithful names, provisional gameplay rules

| Slot on source sheet | Ability | Intended player-facing behavior | Prototype safeguards |
| --- | --- | --- | --- |
| LMB | **Symbiotic Lash** | A short-range living tether heals an ally and applies a small regeneration effect; an alternative enemy hit is an explicit design option, not automatic lifesteal. | Clear max range, target ownership and LOS; capped HOT refreshes; no free permanent healing. |
| RMB | **Shared Vitality** | Link to one selected ally; transfer a bounded fraction of their incoming damage into a finite Symbion protection budget and gradually restore both while linked. | One baseline link; transfer has per-window limits, expiry and cannot kill Symbion from redistribution alone; break on distance/LOS/death. |
| E | **Adaptive Spore** | Deploy a living spore to heal, cleanse one eligible debuff, and grant a **player-selected or context-telegraphed** Heal / Armour / Speed adaptation. | Explicitly readable mode, finite coverage/duration and strict non-stacking. Never automatically counter every debuff for free. |
| Q | **Bio-Forge** | Temporarily overgrow a linked ally with organic armour and a modest empowered-attack window. | Bounded bonus shield and attack modifier; obvious start/end silhouettes; no permanent armouring. |
| Passive | **Evolution Bond** | Support activity earns bounded evolution stages during the match; stage perks make links/spores more interesting rather than multiplying raw stats without limit. | Small fixed number of tiers, defined reset/decay rule, visible stage meter and anti-snowball tuning. |
| Ultimate | **Ascendant Fusion** | Briefly fuse with eligible linked allies, granting strong healing, resistance and a distinct role-sensitive enhancement; the legacy sheet proposes **10 seconds**. | Fixed duration, max targets determined by team size, no invulnerability, controlled extra-effect mapping per hero role. |

**Note:** These are testable candidate interpretations of the concept sheet. The original supplies ability names and fantasy, not verified balance, implementation, match rules or approved target caps.

## Core interaction loop

1. Select a forward ally and maintain **Shared Vitality** while managing range and exposure.
2. Use **Symbiotic Lash** and timed **Adaptive Spores** to keep the bond healthy and answer a specific threat.
3. As **Evolution Bond** develops, decide whether to keep a strong current partner or switch to protect an objective holder.
4. Apply **Bio-Forge** at the start of a controlled push; choose **Ascendant Fusion** only when allies can act together for its full window.
5. Opponents can kite the tether, separate the pair, bait the spore mode and punish over-commitment.

## Silhouette + art blockout (owner review, not an art lock)

**Reference anchors to preserve for review:** black / near-ivory biotic armour, dark crimson and vivid magenta luminescence, long living tendril-hair/crown, red-glowing eyes, clawlike organic forearms, an open glowing blossom/spore motif and shifting back appendages. Keep the support silhouette **slender and recognisable**, even when overgrown; avoid confusing it with crimson gothic tank Vellaris.

**Greybox decomposition:** head + tendril crown; narrow asymmetrical torso; armoured claw gauntlets; segmented bio-armour chest; two or four distinct tether appendages; long trailing membranes; bloom/spore focus; alternate light overgrowth rig state. Do not make every appendage independently simulated in the first blockout: start with rig-friendly parent chains.

**Animation signatures:** tendril lash extending then retracting; intimate single-partner link with visible pulse; floating flower spore unfolding; armour plates growing around ally; ultimate silhouette swelling into a controlled crown/lotus form. Preserve head, torso and targeting readability in all poses.

**Accessibility / readability:** tether ownership needs icons, direction, sound, hit/expiry feedback and distinct shapes, not red hues alone. The ally should know whether damage is being redistributed and when it ends.

## Proposed technical contract for an eventual Godot prototype

- Explicit `link_target_id` and a deterministic link state machine: acquiring → active → interrupted → cooldown.
- Bounded damage-transfer accounting with per-hit event IDs; never recursively transfer already-transferred damage or create healing loops.
- Buffs/spores declare modifier category, priority, stacking cap, owner, expiry and cleanup behavior on death/disconnect/rewind.
- Passive evolution progress and reset/decay must use match-authoritative events, not client-supplied damage/heal numbers.
- Fusion sends clear role-specific effect IDs to each eligible linked ally; postpone a bespoke extra ability for every hero until the ability framework supports it.

## Acceptance test checklist (not run)

- Tether breaks and cleans up correctly on distance, LOS, death, disconnect, respawn and target switching.
- Damage splitting conserves damage according to explicit rules, hits shield/HP in defined order and cannot self-recurse.
- Healing/spore refreshes respect caps; each adaptation mode produces the correct visual and timed effect.
- Bio-Forge never grants permanent armour and does not multiply unexpectedly with Time Dilation Field.
- Evolution tiers cap correctly and cannot be farmed from self-inflicted or already-redirected damage.
- Ten-second fusion expires on time, limits targets, recovers on interruption and keeps controller/VFX readable.
- Symbion and Temporis combined cannot form an endless survival loop; native Godot, network and performance checks remain separate gates.

## Unresolved decisions

Confirm whether spore mode is manual or contextual, exact damage-sharing cap, stage decay on death, ult linked-target count, which hero types receive unique bonuses, and how the living visual adapts to AETHERFALL's approved style. Do not promote this proposal to `aetherfall_approved` or `implemented` without owner acceptance and separate actual evidence.
