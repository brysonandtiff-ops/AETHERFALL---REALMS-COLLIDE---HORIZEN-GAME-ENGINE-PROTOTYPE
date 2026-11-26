# Test scope

`python3 -m unittest discover -s tests -v` runs structural tests using the Python standard library.

Later native Godot tests should cover main-scene parsing, import, gameplay, save/load, navigation, controller/touch and real performance. No native Godot or Blender execution is claimed by these folder checks.

`test_studio_layout.py` runs adversarial missing-zone, engine-mixing, add-on provenance and unsafe path checks; `test_production_queue.py` tests task-state guardrails. Tests are required alongside actual Godot headless CI. Neither source validator establishes real gameplay, device, graphic or multiplayer acceptance.

`test_asset_handoffs.py` uses explicitly **synthetic file-header fixtures** to test checksums, traversal, rights and stage recording; they are not genuine Blender/GLB/Godot assets. `test_studio_preflight.py` tests the real --quick CLI without recursive full-test execution. These are source regressions only, not native gameplay proof.
