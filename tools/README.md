# Development tools

Run from the repo root:

~~~sh
python3 tools/studio_preflight.py
# individual checks for diagnosing a failure:
python3 tools/validate_structure.py
python3 tools/validate_studio_layout.py
python3 tools/validate_asset_handoffs.py --report
python3 tools/production_queue.py --validate
python3 tools/production_queue.py --next
python3 -m unittest discover -s tests -v
~~~

Both checks use only the Python standard library. They verify paths, static references and asset registry consistency only. They cannot prove a native Godot launch, Blender import, 3D animation or a physical-device build.

Use the existing authorised S.I.R.E. runner for real Godot/Blender checks once connected; do not create an unapproved runner or paid dependency.

## Review-base history guard

On GitHub PRs, CI compares the committed `docs/production/WORK_QUEUE.json` baseline with the proposed queue. Manual local check: `python3 tools/production_queue.py --audit-baseline /path/to/prior-committed-WORK_QUEUE.json`. This rejects deleted/renamed tasks, altered acceptance contracts, forged fresh verification and rewritten proofs. It cannot certify that a cited screenshot, reviewer or commit is authentic; owner-approved review remains mandatory.

The `validate_structure.py` scan also checks high-confidence embedded-credential markers in smaller UTF-8 source files (without echoing secrets), unsafe tracked caches and gitlinks. It does **not** scan private unconnected systems, non-text binaries or the full historical Git object database.

`validate_studio_layout.py` checks the machine-readable studio ownership contract and native Godot/Blender toolchain truth. It is source/layout proof only, **not** a functioning game or release pipeline.

`audit_asset_history.py` is a PR-only guard for existing character IDs/source paths and protected art/evidence deletions relative to the real Git base. It needs a previous registry snapshot (`--baseline`) and optionally the exact Git base revision (`--git-base`). GitHub's CI supplies both.

`studio_preflight.py` runs actual local source validators and Python regression tests; `--quick` omits tests. It prints the next unblocked work orders only after the checks succeed. `validate_asset_handoffs.py` checks real paths, provenance fields, bytes, SHA256 and required native *records*, never model fidelity or gameplay. See `art/handoffs/README.md`.
