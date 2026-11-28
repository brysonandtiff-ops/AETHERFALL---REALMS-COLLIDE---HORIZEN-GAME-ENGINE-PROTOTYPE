# Game AI / Gameplay Engineering — 1P + 3P hero shooter contracts

**Engine target:** Godot 4.x (repository pinned smoke target 4.7.2). **Status:** IMPLEMENTATION SPEC; not a running game. **No hero kit is automatically approved by an example.**

## Runtime architecture and ownership (authoritative combat, cosmetic dual-view)

```text
NetworkInput (player/controller/AI) → InputValidator (ability/cooldown/resources)
 → CharacterStateMachine (Movement + Combat + StatusEffects)
 → ServerCombatSimulation (target/LOS/hurtbox/projectile/AoE)
 → CombatEvent (stable id / tick / source / target / result)
 ↘ 3P full-body AnimationTree, world VFX and audio
 ↘ 1P arms/weapon AnimationTree, local feedback and crosshair
 ↘ HUD, replay/killcam, combat telemetry (non-authoritative)
```

- **One** authoritative health, damage, team, projectile and cooldown state regardless of 1P/3P camera. Camera choice is rendering only, never a way to bypass cover or claim hits.
- Server owns ability validation, spawn/tick of projectiles, target-team rules, LoS/hitboxes, damage/heal/status and eliminations. Clients can predict visuals/movement and reconcile; never trust client-provided damage, target or cooldown claims.
- Every event has `{event_id, tick, actor_id, team_id, ability_id, phase, transform, targets, seed, results}`. A replay of the same event ID must be idempotent. Random outcomes use reproducible server seed and a logged per-match ruleset version.
- Distinguish simple non-network local bots from a networked authoritative match; a local single-player test does **not** certify PvP networking.

## Locomotion finite-state machine

| State | Entry/exit contract | Typical requested animations | Notes |
|---|---|---|---|
| Idle | grounded, speed below stop threshold; move command → Walk | Idle, Idle_Turn | body 3P turn-in-place, 1P sway only |
| Walk / Strafe | grounded directional velocity; sprint flag → Sprint | WalkF/B/L/R, Start/Stop | strafe animation directional, camera yaw decoupling bounded |
| Sprint / Dash | stamina/resources and cooldown checked; collision sweep mandatory | Sprint, Dash_Start/Loop/Stop | dash may be short-lived override with telegraph |
| Jump / Airborne | ground test + jump buffer; apex → Fall; landing → grounded | Jump_Start, Air_Loop, Land | fixed gravity/air steering authority, no air jump unless approved |
| Crouch / Slide | grounded + posture clearance; slide timed / friction → Stand | Crouch, Slide_Start/Stop | hurtbox capsule shrinks only after clearance check |
| Disabled | stun/root/knockdown/death; exits only after status timer | Hit, Stunned, Knockdown, Death | death interrupts uncommitted ability, not already spawned projectile |
| Quadruped | use neutral 4-foot gait with turn radius and slope thresholds | Trot, Gallop, Pounce, Claw | four-foot IK; body length in collision sweep |
| Flight / Hover / Burrow | **only if hero approved** with dedicated nav layer/altitude or nav links | Takeoff/Hover/Land, Burrow_Enter/Exit | never path through solid cover or skip fair telegraph |

**Parameter baseline (provisional tuning only):** physics simulation 60 Hz, bot decision tick 5–10 Hz, walk 4.5 m/s, sprint 7 m/s, crouch 2 m/s, standard jump 4 m. Per-hero movement, mass, air control, turn rate, acceleration, stamina and real observed timings require balancing and owner/QA approval. Fixed frame budget/authority timestamp on every transition; scale animation rates separately from combat hit windows.

### Navigation and AI

- Godot candidate nodes: `CharacterBody3D` + `NavigationAgent3D` + `AnimationTree` + `Skeleton3D`, with collision and footIK/camera components. NavigationAgent pathfinding needs navmesh and regular `get_next_path_position()` updates; avoidance is *steering assistance*, not authoritative wall permission.
- Bot planner state priority: `DEAD` > `STUNNED` > `RETREAT_IF_UNSAFE` > `PROTECT_OR_OBJECTIVE` > `ACQUIRE_TARGET` > `APPROACH_OR_KITE` > `EXECUTE_COMBO` > `REPOSITION` > `PATROL`.
- Target score (illustrative): `0.35 * objective_threat + 0.25 * kill_opportunity + 0.20 * ally_protection + 0.10 * proximity + 0.10 * line_of_sight` after filtering invalid allies/dead targets/out-of-nav-reach. Healer target selection weights missing allied health and immediate danger, not damage. Expose weights in versioned config; retune after match telemetry.
- LOS must use world/collision masks and cover; no through-wall targeting by default. Targets can have acquisition hysteresis, forget timeout and visibility memory; do not auto-track stealth/invisible enemies without explicit reveal rules.
- Range bands per ability: `min <= distance <= max`, aim cone, projectile speed, splash radius, elevation delta, nav/cover checks and friendly-fire status. Explicit threat/aggro decay, disengage distance, evade opportunity and obstacle avoidance.
- Bots/companions may request ability use; **the same validator** as players must accept or reject the request. No bot-only hidden damage/cooldown exemptions unless declared intentional PvE tuning.

## Combat ability phase machine (mandatory per action)

```text
READY → WINDUP → TELEGRAPH → ACTIVE → FOLLOW_THROUGH → RECOVERY → COOLDOWN → READY
                       └─ if valid server action, spawn HITBOX / PROJECTILE / ZONE
INTERRUPTED/DEAD stops new spawns; committed projectile/zone follows explicit lifetime policy.
```

Every Primary/Secondary, mobility skill, defensive ability, Passive and Ultimate needs structured data:

- `ability_id`, readable title, `slot`, targeting policy, team restrictions, damage/heal/mitigation type, range/LOS, resource and cooldown; 1P + 3P matching animation event names.
- Phases in integer simulation ticks: `windup`, `telegraph`, `active`, `follow_through`, `recovery`, `cooldown`. Phase durations may be **0 for genuine instant events** but ACTIVE must have at least one tick; all phases explicitly specified so an action can be reproduced.
- Attack spawn at exact `active_start_tick`; projectiles use server origin + snapshot aim/seed, velocity, lifetime, collision mask, damage falloff and authoritative impact; avoid triggering damage from VFX particles or from both client and server.
- Ultimates have clear enemy warning and interruption/cancellation policy, resource cap, contest readability, no unbounded AoE loops or infinite stacks. Passives specify trigger, cooldown/ICD, stack cap, expiration, suppression and data-driven healing/damage rules.
- Interrupted, stunned, death, weapon swap, camera change, duplicate/replayed requests and expired targets are explicit state transitions with deterministic outcomes.

**Example acceptance fixture (NOT a locked character kit):** a primary with windup 8 ticks, telegraph 4, active 1, follow-through 6, recovery 7, cooldown 30; server rejects simultaneous second commit; event emits once at active tick, both camera presentations show muzzle cue at the same tick; projectile damages an enemy only after server collision, not when the client reticle turns red. Actual tuning to be established in match tests.

## Hitboxes, hurtboxes and visual clarity

- Player capsule/CharacterBody collider for world navigation; separate per-bone hurtboxes (`HURT_Head`, `HURT_Torso`, limbs) and team filters; collision events use a layer matrix documented in `ABILITY_CONTRACT.json`.
- Suggested collision categories (configurable): `WORLD_STATIC`, `WORLD_DYNAMIC`, `PLAYER_BODY`, `PLAYER_HURTBOX`, `PROJECTILE`, `ABILITY_SENSOR`, `BOT_NAV`, `VFX_NON_COLLIDING`. Explicit masks, no auto `1 << N` assumptions in production.
- Visual projectiles, blood/rune effects, spark particles, shields and aim reticles **never** serve as collision authority. An AoE has a server-defined primitive (Sphere/Box/Capsule/Arc) with radius, height, lifetime, team and intersection policy.
- Shield/blocking interaction order versioned: static geometry → barrier/cover → hurtbox, with any exceptions explicitly specified. Penetration/ricochet needs separate rules and readable telegraph.
- 1P arms/world model never have two simultaneously damageable body proxies; spectator 3P and first-person owner must agree on hit origin, impact point, server damage and charge progress.
- Enemy/ally effects distinguishable without colour alone: different shapes, borders, animation rhythms, hit-confirm icon + audio subtitle/caption option; flashing limits and reduced-VFX profile documented. Performance tested under full 5v5 fight/10 active effects as a **test target**, not asserted game mode.

## Hero-specific intent examples — concept-only, not kit approval

- **Vellaris (AETHERFALL-approved concept only):** `Blood Barrier` uses a distinct server barrier collider; `Crimson Riposte` uses a time-bounded, telegraphed counter window; `Sanguine Pact` ally link requires range/LOS and healing cap; `Hemorrhage Veil` is an AoE sensor distinct from fog VFX; `Royal Ichor` has bounded stacks. DO NOT replace named abilities, unique bloodshield or visual identity.
- **ThornDell (AETHERFALL-approved concept only):** rooted venom AoE creates clear floor hazards distinct from bright foliage VFX; Root Bulwark has its own blocking volume; resist/cleanse counterplay. Do not assume the historical ThornDell art proves model/skills or force humanoid movement on any other species.
- **Razor/Raven (legacy candidate until owner intake resolved):** quadruped lunge and four-foot pathing vs. omens/echo projectiles require very different hit/LOS and camera tests; do not resolve variant conflicts by copying a generic template.

## Integration task order and actual test evidence

1. Define input map and simple local greybox arena (never claim PvP from starter screen).
2. Implement authoritative movement with 1P/3P render-only toggle and one collision body; verify movement rates and wall collision at 60Hz.
3. Implement one phased ability with event ID, cooldown/range/resource validator and independent server-side AoE/projectile tests.
4. Add 3P AnimationTree/1P viewmodel clips and identical ability event hooks, dynamic sockets, FOV/readability and no duplicate hit registration.
5. Add bot NavigationAgent3D, cover-aware LOS, threat weighting, unreachable-target recovery, support ally filtering and performance constraints.
6. Test network clients with authoritative server + latency/jitter/loss/reconciliation; exploit attempts: request reuse, cross-team healing, teleport through wall, spoofed aim, collision bypass.
7. Native Godot 4.7.2 tests: input replay, fresh import, cast/interrupt/death, navmesh obstacle, persistence/rejoin, device gamepad/touch, full-match perf and real inline video captured from game window.

**Status required:** `NOT_IMPLEMENTED` until actual imported character gameplay and native per-test receipts exist. A design sketch, AI text or offscreen GLB viewer can never satisfy this gate.