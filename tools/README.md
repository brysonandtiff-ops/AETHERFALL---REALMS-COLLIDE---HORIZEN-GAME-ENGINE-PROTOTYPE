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
