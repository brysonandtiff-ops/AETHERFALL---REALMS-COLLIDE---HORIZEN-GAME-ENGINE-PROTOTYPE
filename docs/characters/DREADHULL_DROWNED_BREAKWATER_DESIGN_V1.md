# DREADHULL — THE DROWNED BREAKWATER (SUPERSEDED)

> **SUPERSEDED — NOT CANON — 2026-11-27.** Historical written proposal retained for traceability only. Owner explicitly selected Bonebrine Reaver #07 with the Ossuary Dredge. Do not implement or generate artwork from this Keel Oar / Ballast Heart proposal. The active contract is [CHR_Dreadhull.json](plans/CHR_Dreadhull.json), [CANON_LOCKS.json](CANON_LOCKS.json), and [owner approval](../../evidence/characters/CHR_Dreadhull/OWNER_CANON_APPROVAL_2026-11-27.md). The old kit and numeric hypotheses are not approved.

Work order: AF-DREADHULL-DESIGN-001 | Date: 2026-11-27 (AWST)
Project: AETHERFALL: REALMS COLLIDE | ID: CHR_Dreadhull
Executor: connected GitHub tools under existing S.I.R.E. governance.
Status: DESIGN_SPEC_COMPLETE_FOR_REVIEW / ART_SOURCE_PENDING / NOT_GAMEPLAY_IMPLEMENTED.
Goal: turn the historical denial/disruption tank into an original undead shipmaster whose ocean currents are his defense. Acceptance: owner approves actual new visual and kit, exact source archived, then native pipeline proof. No new agent created.

## Art direction

A dead captain has become the living breakwater of a ship graveyard. A broad low prow-shaped shoulder and ribbed hull plating make him tank-sized, while the opposite side exposes salt-cracked bones and an open pressure cage containing impossible seawater. His human skull has a recessed pale sea-glass eye and a stern jaw, with no tentacle beard, cephalopod head, pirate-film replica or recognizable franchise costume. An off-center stern bell, knotted rigging and torn slate sailcoat establish his seafaring identity. No crown, antlers, oversized cape, claw, handheld shield, or repeated tank armour.

Keel Oar: a weighty, broad blunt ship-steering blade with off-axis shaft and flowing tide channels; one continuous readable prop, not a hammer, anchor or harpoon. Spectral kraken arms belong to a separate summoned creature, never to Dreadhull's face/body. The defense is flowing ocean water, not a portable barrier asset.

Provisional scale: 2.65 m tall, 1.7 m hull shoulder width, 2.25 m oar length; use a substantially smaller stable capsule justified by collision tests. Front: open chest reservoir and prow shoulder. Side: forward-weighted braced stance with clear arm swing. Back: ribbed hull, stern bell and short sailcloth. Three-quarter: same armor, hand, oar and silhouette as all views. Face expressions: still deadpan, gritted command, wide-jaw battle roar, dim exhausted eye. Silhouette studies: reject ordinary armored human, octopus head and shield-bearing variants; selected broad low wreck silhouette remains a proposal.

Palette: abyss navy #101F30; oxidised bronze #426B65; salt bone #D6D1BD; water glass #66CFE3; storm foam #F0F8F4; wet teak #5D4232. Rough wet wood, matte rope, chipped metal and bone contrast with bounded transparent water. No red-blood, green-venom or purple-dominant hero palette. Sheet framing may use shared Vellaris presentation colors, not her body or shield.

## Prototype kit (numbers are hypotheses, not approved balance)

| Slot | Ability | Starting mechanic | Counterplay |
| --- | --- | --- | --- |
| Primary | Keelstroke | 55 damage, 4 m, 0.85 s cycle; broad oar swing | Step outside arc; visible wind-up |
| Secondary | Breakwater | 45% ranged damage reduction for hostile hits crossing frontal current; 20 Ballast upfront + 30/s, max 2.5 s, 5 s cooldown | Melee, flank, wait out Ballast; no invulnerability or reflection |
| Active 1 | Undertow | 7 m marked lane, 0.55 s warning, up to 2 m pull, 30% slow for 1.5 s, 10 s cooldown | Exit lane, use cover, no unsafe forced pit displacement |
| Active 2 | Deadman's Mooring | Plant for up to 4 s; 5 m radius allies gain 60% horizontal knockback resistance; captain slows 25%, cannot attack; 14 s cooldown | Interrupt hard CC, leave zone, pressure stationary captain; no stun immunity |
| Ultimate | Kraken's Wake | Three sequential lanes over 11 m fan, 0.8 s warning per lane, 65 damage, up to 2 m pull, 35% slow for 2 s; 100 ultimate charge | Leave indicated lanes, cover blocks effect, each enemy hit at most once |
| Passive | Ballast Heart | 100 max Ballast; regenerates 15/s after 2 s without expenditure | Resource depletion creates exposure; no heal or damage-based farming |

Six slots include primary, secondary defense, two situational actives, ultimate and passive because the directional resource-defense loop must be available independently of lane control. Distinct from Bryskar's dive/rescue, Vellaris's sustain and ThornDell's venom. Initial health hypothesis 650, walk 4.5 m/s; no dash, self-heal, unbounded pull or permanent shield. Tune against actual team combat, not a final stat lock.

## Implementation contract

Server validates alive state, cooldown, resource, team, range and line of sight; server computes damage and displacement once per event. Breakwater has one current plane per tank; for multiple currents use strongest eligible mitigation, never multiply/stack. No self-reflection, projectile teleport or damage to allies. Apply mitigation only to eligible ranged hits crossing the plane while active. Breakwater ends on release, depletion, stun, death or mooring activation; starts cooldown on ending. Ballast clamped to 0..100, deterministic cost per tick; cancel immediately when remaining cost cannot be paid. No regeneration while channeling or during 2 s delay. Mooring starts cooldown on cast, ends on interruption/cancel/death; allies can leave freely. Undertow and Kraken evaluate capsule sweep, safe walkable landing and world collision; cap pull distance, reject hazardous edge displacement; no pull through cover. Slow effects use strongest active value; crowd-control immunity/resistance and hit history enforced by server. Kraken hit set scoped to cast ID, not arm; clear after cast. Ultimate is not a separate playable summon, AI pet or solid wall. One shared combat authority for 1P/3P; renderer only presents effects.

## Presentation and handoff

1P: hands/oar with unobstructed center aim; pressure gauge clearly visible in HUD. 3P: identical oar, hull shoulder, open chest and readable directional current. Full-body rig, left/right grip IK, shoulder clearance, independent bell and sailcloth; idle/walk/run/backpedal/turn, sweep, current start/hold/end, undertow cast, plant/hold/unplant, ultimate, hit and death clips. Suggested 3P LOD0 40-70k triangles; 1P 20-35k, then measured LODs, PBR material maps and actual device budgeting. Not measured or built. Blender +Z up/-Y forward, metres; validate Godot orientation, mesh scale, sockets and animations. Current uses moving foam lines rather than opaque water; kraken lanes use striped contours, timed ripples and short low bell sounds. Distinct friendly/enemy shape patterns plus color and accessible reduced effects. No rapid full-screen flashes or forced camera motion. Voice direction: dry low captain, original lines: "Hold the tide", "Moor here", "The deep answers"; no imitation of another character or actor.

## Originality review and art gate

Documentary comparison, not a completed visual review: Vellaris's crimson shield and blood sustain, ThornDell's antlers/root shield and venom, Korvex's attrition role, Morrigan's area control, Bryskar's mobility/rescue, and Razor's quadruped silhouette are distinct written identities. Exact Dreadhull historical image and complete roster references were unavailable to this run; side-by-side visual tests are NOT_RUN. Do not copy any franchise-specific undead pirate. Final artwork needs actual owner-reviewed 4:3 Vellaris-layout board, 16 required sections, exact archived source and comparison at portrait, four-view, and gameplay silhouette scales. Written plan does not pass these art gates.

## Acceptance tests (NOT_RUN)

- With full Ballast, 2.5 s Breakwater spends 95; no negative or extra free tick; verify regeneration delay, release, depletion and cancellation.
- Frontal eligible 100-damage hit becomes 55; identical flank/melee hit remains 100; overlapping currents do not stack. Test team relation, blockers, latency and server reconciliation.
- Undertow warns before resolving; no more than 2 m displacement; reject through-wall and unsafe ledge landing; verify slow expiry, immunity and cooldown.
- Mooring reduces eligible 10-unit knockback to 4; no stun immunity, no attack while planted; interrupt, leave radius and death cleanup.
- Kraken has three independently visible lane warnings but each enemy receives at most one 65-damage hit per cast; no ally effects, wall pulls, edge kills or obstruction of escape.
- Compare authoritative results in 1P/3P and networked clients, controller/keyboard/touch where supported; profile VFX cost on actual target devices; test contrast, readability, reduced effects, and audio alternative cues.
- Require real Blender native four-view/rig evidence, Godot import/combat video, owner approval and independent S.I.R.E. gates before promotion.

No model, rig, scene, combat script, gameplay video or platform release is claimed. Original historical art and locked hero sources are unchanged.
