# Development tools

Run from the repo root:

~~~sh
python3 tools/validate_structure.py
python3 -m unittest discover -s tests -v
~~~

Both checks use only the Python standard library. They verify paths, static references and asset registry consistency only. They cannot prove a native Godot launch, Blender import, 3D animation or a physical-device build.

Use the existing authorised S.I.R.E. runner for real Godot/Blender checks once connected; do not create an unapproved runner or paid dependency.

## Project command interface (review branch)

```sh
python3 tools/aetherfall.py doctor --json
python3 tools/aetherfall.py status --json
python3 tools/aetherfall.py routes
python3 tools/aetherfall.py skills
python3 tools/aetherfall.py work list
python3 tools/aetherfall.py handoff AETHERFALL-DEVOPS-001 --json
python3 tools/aetherfall.py cmd G
python3 tools/aetherfall.py check
```

Each command is offline. A handoff is printed to the operator only; it does not call an external agent. `native-smoke` optionally runs already-installed Godot 4.7.2 headlessly; if no correct engine is installed it exits BLOCKED with code 2. Graphical/device proof is separate.

## Structural protection (new game work)

```sh
python3 tools/structure_guard.py check
python3 tools/structure_guard.py diff --base <actual-ancestor-40-digit-commit>
```

The first checks project layout, portable names, literal Godot `res://` resources, and UIDs. The second runs read-only Git comparison against a verified ancestor and rejects deletion/renaming of protected existing source and registry identity changes. Pull-request CI obtains the base SHA from GitHub. New additive game files are allowed. See `docs/architecture/FILE_STRUCTURE_SAFETY.md`.

## Optional owner-run Android document intake

```sh
python3 tools/phone_docs.py --status
python3 tools/phone_docs.py --file AETHERFALL_Concept_Brief.pdf
python3 tools/phone_docs.py --file AETHERFALL_Concept_Brief.pdf --apply
python3 tools/phone_docs.py --scan --apply
```

The destination is the existing Android `AETHERFALL – REALMS COLIDE/Docs/Inbox` (not a second differently spelled folder). The script is offline, restricted to the top level of Download, preview-only by default, copies with checksum, leaves originals in Download, never installs an Android system service, and is not yet running on the phone.

## S.I.R.E. source integrity only

```sh
python3 tools/aetherfall.py seal --base TRUSTED_40_HEX_ANCESTOR --expected-head ACTUAL_40_HEX_HEAD
python3 tools/sire_seal.py source --base TRUSTED_40_HEX_ANCESTOR --expected-head ACTUAL_40_HEX_HEAD
```

Refuses dirty Git trees, wrong candidate SHAs, missing original files, unapproved paths and unresolved LFS pointers. CI produces a hash inventory outside source; no signature or Gold Seal is minted. See `docs/development/SIRE_SOURCE_SEAL.md`.
