# AF-PLATFORM-MOBILE-001 — First-class smartphone and tablet gameplay

**Project:** AETHERFALL: REALMS COLLIDE  
**Owner requirement:** Fully playable on compatible smartphones and tablets, not a companion app, streaming-only UI, or reduced demo.  
**Authorised executor (this work order):** GitHub-connected ChatGPT, documentation-only proposal under the existing S.I.R.E. / HORIZON review process; no new agent authorised.  
**Source baseline:** `main` at `b99d862070926d73d7c698399445e9c2baf273e5` (2026-11-27).  
**Status:** `SPEC_ONLY / NOT_IMPLEMENTED / NOT_DEVICE_TESTED`. This document does not change playable runtime code.  
**Visual canon:** Existing approved hero and environment references, art locks, sources, and workflows remain binding.

## Mandatory platform scope

- Native **Android phones and Android tablets**, **iPhones and iPads** are target platforms. PC/controller work may be shared, but neither PC nor console verification substitutes for physical mobile acceptance.
- A supported mobile device must be able to install/launch the real game, enter the complete 3D game loop, select a hero, explore the practice range, move, aim, shoot, use every ability/ultimate, interact with targets, pause/resume, navigate menus, save applicable settings/progression, and exit/relaunch **without an external keyboard or controller**.
- Supported phones/tablets receive the **same core maps, heroes, ability rules, game modes, progression and multiplayer features** as the game release on other platforms (subject only to publicly documented, justified platform restrictions). Adaptive graphics and UI layouts are allowed; gameplay content must not be silently cut to make a device pass.
- Define a **tested compatibility matrix** by actual OS version, device model, chipset/GPU, RAM, screen dimensions, renderer, build and control method. Do not promise every smartphone or tablet is supported; publish a supported-device tier only after real tests.

## Input requirements — touchscreen and controllers

- Mobile landscape play: two-thumb default touch layout (virtual movement joystick + aim/camera swipe), on-screen fire, aim-down-sights, reload, jump, crouch/slide, interact, ability 1/2/3 and ultimate, hero/team/menu controls as relevant to the actual hero kit.
- Simultaneous multitouch must allow moving, aiming and firing/using an ability together. Verify reliable gestures when crossing controls, interruptions, and accidental touches.
- Remappable controls; move/resize/opacity controls; left-handed layout; aim sensitivity and inversion; optional gyro aim/haptics if supported. Persist per-user control preferences across sessions.
- Bluetooth Xbox and other supported gamepads: detect attach/detach, map complete gameplay and menu navigation, allow remapping and trigger/analog calibration, and fall back seamlessly to touch if disconnected.
- Input parity: touch, mouse/keyboard, and gamepad drive the same authoritative game actions, cooldowns, hit validation and movement constraints. Avoid controller-only or desktop-only mechanics.

## Responsive HUD and accessibility

- No critical HUD element obscured by notches, rounded edges, system gesture/navigation areas, or tablet aspect ratios. Use safe areas, scalable anchors and tested font/target sizes.
- Context-specific touch UI must show health/shield, ammunition, ability states/cooldowns, ultimate progress, objective markers, pause/settings, and readable hit feedback.
- Maintain legibility and touch-target usability on compact phones and tablets, with contrast and color-independent indicators. Provide text size/HUD scale options and a control tutorial.

## Rendering, performance and lifecycle

- Keep the existing **Godot 4** project and approved art pipeline. Treat `gl_compatibility` currently in `game/project.godot` as a starting configuration, **not** proof of a working Android/iOS build.
- Engineer separate measured quality/LOD/shadow/particle/texture/resolution tiers without changing locked visual identity. Preserve ability telegraphs and important gameplay information on the low tier.
- **Performance targets, not measured achievements:** stable 30 FPS entry tier on explicitly supported lower-powered devices; 60 FPS option/target on capable devices, with recorded frame times, thermals, loading, memory and power impact. Establish limits and actual supported devices through profiling.
- Test install/update, permission behavior, background/suspend/resume, incoming calls/notifications, audio interruption, lost focus, rotation restrictions, low-memory recovery, network interruption/reconnect, and saved-data integrity.
- Mobile multiplayer (when implemented) must maintain secure network validation, fair input/aim-assist policy, bounded bandwidth and graceful disconnect/reconnect behavior. Cross-play remains a separate decision; never imply it works before testing.

## Release gates and authentic evidence

1. **Source gate:** exact commit, dependency inventory, clean code-review record, automated GDScript/structure/integration tests, mobile export settings, signing/deployment process documented (without credentials).
2. **Android gate:** build actual Android package, install on at least one physical supported phone **and** one tablet, run complete touch and Bluetooth gamepad test cases. Record engine/OS/hardware/build IDs.
3. **iOS/iPadOS gate:** export and sign with an authorised Apple/macOS toolchain, install on at least one physical supported iPhone **and** one iPad, run the same complete tests. Simulator-only tests are insufficient.
4. **Vertical-slice gate:** practice range + one real playable approved hero + complete HUD/inputs; measure start, 10-minute active combat, pause/resume, settings persistence, relaunch, performance and crash-free operation.
5. **Full-game gate:** repeat the matrix for all approved launch heroes, maps, combat interactions, objective modes and multiplayer/progression when each exists; regression and accessibility checks on every supported OS tier.
6. **Evidence gate:** genuine screenshots and an unedited on-device gameplay recording for each claimed platform/form factor; capture device model, OS, source SHA, build identity, FPS/frame-time and test logs under `evidence/device/` and `evidence/performance/`. If capture is unavailable, record `NOT_RUN`, never `PASS`.

**Release blocker:** No claim of “mobile/tablet playable”, “mobile parity”, or “ready for stores” until the relevant physical-device gates pass with attributable evidence. A Godot headless check or desktop demo is not mobile proof.

## Delivery sequence

1. Implement a single shared game action layer + touch input adapters and device-responsive HUD on the existing Godot project.
2. Build The Unbound Reach practice-range vertical slice with one real approved hero, all core inputs and an actual on-device prototype.
3. Harden rendering and stability on low/mid/high device tiers, then add the rest of the approved gameplay.
4. Verify all supported phone/tablet form factors and release artifacts before any owner-approved deployment.

## Relation to existing rules

Follow `AGENTS.md`, `GIT_HERE.md`, `docs/characters/VISUAL_CANON_LOCK.md`, `docs/evidence/PROOF_REQUIREMENTS.md` and `docs/development/PR_INTEGRATION_MAP.md`. This contract adds an owner-specified platform acceptance requirement without overwriting art, touching gameplay sources, bypassing review, or claiming a verified release.
