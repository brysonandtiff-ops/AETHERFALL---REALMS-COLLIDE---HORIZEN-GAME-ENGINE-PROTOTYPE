# Development tools

Run from the repo root:

~~~sh
python3 tools/validate_structure.py
python3 -m unittest discover -s tests -v
~~~

Both checks use only the Python standard library. They verify paths, static references and asset registry consistency only. They cannot prove a native Godot launch, Blender import, 3D animation or a physical-device build.

Use the existing authorised S.I.R.E. runner for real Godot/Blender checks once connected; do not create an unapproved runner or paid dependency.
