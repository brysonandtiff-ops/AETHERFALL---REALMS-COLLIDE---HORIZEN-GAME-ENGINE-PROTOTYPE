# Studio content handoff — concept → master → engine → QA → acceptance

A professional content pipeline is a **verified handoff**, not just a folder. Each character, weapon, world, effect and UI asset has one canonical asset ID, an owner-approved reference and an explicit chain of custody.

## Asset work order (required fields)

| Step | Owning discipline | Deliverable | Gate |
| --- | --- | --- | --- |
| 1. Creative brief / owner art lock | Art direction + owner | Original brief, approved concept, rights/provenance, role/silhouette, source filename/hash | Distinguish concepts from model/runtime evidence |
| 2. Technical spec | Tech art + gameplay | Asset ID, mesh count/LOD budgets, scale/orientation, collision, animations, palette, memory budget | Approved spec before modelling |
| 3. Author original source | Blender artist | Non-destructive original .blend model/rig and source textures/audio, versions and exports | Protect originals from flattening/overwrite |
| 4. Review rig and animation | Animation / character lead | Four views, topology/UV screenshots, weights, clips, actual Blender animation playback | Correct anatomy/identity and clean transitions |
| 5. Export deterministically | Technical art | GLB with stable naming/version, source hash, material/armature mapping and export settings | Reproducible, size-checked and licensed |
| 6. Native Godot import | Engine integrator | Runtime asset in matching `game/assets/` path, scene references, animations, materials and collision | Actual Godot 4 import, no missing dependencies |
| 7. Functional gameplay integration | Gameplay/QA | Real hero or world in a real Godot scene, ability and collision tests, readable UI | Test actual interaction, not just render |
| 8. Accept and archive proof | QA + authorised reviewer | Source commit, artifact checksums, actual editor + engine screenshots/video, test exit codes | Evidence in `evidence/`; never fake runtime |

## Single source of truth by discipline

- Hero `CHR_ThornDell`: concept `art/concepts/characters/CHR_ThornDell/`; source `art/blender/characters/CHR_ThornDell/`; export `game/assets/characters/heroes/CHR_ThornDell/`. Keep the approved ID and visual details unchanged.
- Weapon `WPN_Vellaris_Bloodshield`: concept, Blender and runtime paths follow the existing `art/asset_registry.json` exactly.
- Planned Razor/Raven designs or unregistered support concepts must receive an approved ID and reference before producing new canonical content; avoid inventing approved assets.
- UI sources: `art/ui/`; runtime `game/assets/ui/` + `game/scenes/ui/`.
- VFX sources: `art/vfx/`; runtime `game/assets/vfx/` + `game/scenes/vfx/`.
- Cinematic storyboards: `art/storyboards/`; actual scene files under `game/scenes/cinematics/` once authorised.

## Collision and rollback policy

Binary .blend and image files cannot always merge. Use branch ownership, explicit asset reservations, immutable handoff hashes, source version history, reviewed locks or an **approved** LFS/Perforce workflow once enabled. If two artists edit one master, stop the conflicting change and resolve against the canonical original—never automatically overwrite.

Never move/bulk-rename Godot resource paths, invent original artwork or call generated concepts native model evidence. Protect private original photographs before putting any material in this public repository.

## Non-destructive source history gate

During a GitHub PR, `tools/audit_asset_history.py --baseline <base-registry> --git-base <base-commit>` refuses removal/renaming of tracked original art, evidence or canonical character definitions. New approved IDs can be appended without deleting previous history. A necessary destructive migration must be separately proposed, rights-checked, backed up, documented, tested and approved; never disable the guard silently.

## Record real files instead of claiming finished characters from directories

Use `python3 tools/validate_asset_handoffs.py --report` to view the registered source-art status of every character and weapon. Only genuine, rights-cleared files in the registry's exact concept/Blender/runtime directories may be referenced by `art/handoffs/<asset-id>.json` receipts containing SHA256, byte count and provenance review fields. Source-status promotions move forward just **one adjacent stage** per reviewed PR, guarded by `tools/audit_asset_history.py`. The current registry remains unchanged until actual source and approval are available. Native import review additionally needs real Godot log and screenshot/video capture evidence; no shape/CRC/hash-only test can establish visual authenticity.

Run `python3 tools/studio_preflight.py` before handoff and attach actual Blender/Godot evidence separately. This source flow does not change locked canonical character identities, licensing requirements, or the owner-only approval of legacy candidates.
