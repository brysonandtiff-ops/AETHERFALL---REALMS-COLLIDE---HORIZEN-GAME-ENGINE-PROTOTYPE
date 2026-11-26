# Test scope

`python3 -m unittest discover -s tests -v` runs structural tests using the Python standard library.

Later native Godot tests should cover main-scene parsing, import, gameplay, save/load, navigation, controller/touch and real performance. No native Godot or Blender execution is claimed by these folder checks.

- `test_structure_guard.py`: portable names, UID/link failure handling, additive scene additions, and real isolated Git-commit regression tests against a base SHA. These are source-level fixtures, not native game footage.

- `test_phone_docs.py`: sandboxed document intake checks (preview, copy, checksum, duplicate and collision safety, path validation). Not a real Android device test.
