# Source-controlled toolchain and studio configuration

`toolchain.json` is the factual, checked-in configuration baseline. It identifies the native Godot project, the exact Godot version used by current headless CI, and explicitly unverified Blender/LFS/Perforce/release states.

This directory is for **non-secret source configuration only**: version pins, content budgets, agreed build defaults and validation schemas. Never store credentials, signing certificates, personally identifying player data, private owner media or host tokens.

Do not change Godot's actual project path or engine family by changing this JSON alone. Any approved engine migration requires a separate full source/art migration, native runnable prototype, import tests, CI rewrite and owner-approved rollback.
