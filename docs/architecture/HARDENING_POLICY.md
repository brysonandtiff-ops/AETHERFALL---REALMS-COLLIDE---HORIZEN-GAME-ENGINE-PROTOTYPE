# Source and asset protection

- The authenticated GitHub repository is the sole source for these AETHERFALL source checks; do not infer executable status from concept folders.
- Approved visual identity is protected. Original `.blend` files are editable source in `art/`; `.glb` files are runtime exports in `game/assets/`.
- `status=reserved_no_source` is the only allowed asset register status until a proof-verified importer is built. `concept_status` indicates concept history, not engine proof.
- Reject unsafe asset paths, traversal, symbolic links, case collisions, credential-looking files, malformed registry entries and unreviewed direct binary files over 50 MiB.
- Do not install paid services, store secrets in GitHub, or add/remove agents. A real change in legacy source/deletion status requires a new independent audit, not text changes alone.
- CI source tests prove only static properties. Godot headless tests prove a real native import/start, not rendered gameplay, phone acceptance or model fidelity.
- Native screenshots, full animation footage, real device/controller tests and exact-source hashes are separate required release gates.
- Only an individually identified, owned and fully archived Shadowspire repository could ever be considered for deletion. This upgrade deletes nothing.
