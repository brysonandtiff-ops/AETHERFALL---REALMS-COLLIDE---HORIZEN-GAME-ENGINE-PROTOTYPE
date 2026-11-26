# Source and asset protection

- The authenticated GitHub repository is the sole source for these AETHERFALL source checks; do not infer executable status from concept folders.
- Approved visual identity is protected. Original `.blend` files are editable source in `art/`; `.glb` files are runtime exports in `game/assets/`.
- Asset statuses advance **one stage per reviewed PR** beyond `reserved_no_source` only when actual files, SHA256 and rights-reviewed receipts under `art/handoffs/<id>.json` exist. `concept_status` is separate canon approval, not proof of native models, gameplay or real-device acceptance.
- Reject unsafe asset paths, traversal, symbolic links, case collisions, credential-looking files, malformed registry entries and unreviewed direct binary files over 50 MiB.
- Do not install paid services, store secrets in GitHub, or add/remove agents. A real change in legacy source/deletion status requires a new independent audit, not text changes alone.
- CI source tests prove only static properties. Godot headless tests prove a real native import/start, not rendered gameplay, phone acceptance or model fidelity.
- Native screenshots, full animation footage, real device/controller tests and exact-source hashes are separate required release gates.
- Only an individually identified, owned and fully archived Shadowspire repository could ever be considered for deletion. This upgrade deletes nothing.

- Studio domain layout is additionally validated by `tools/validate_studio_layout.py` against `studio/layout_manifest.json`. It rejects missing source ownership, false toolchain/LFS/Perforce claims, unsafe add-ons and Unreal-only assets placed into native Godot.
- `config/toolchain.json` holds nonsecret build truth; real Blender version remains unapproved/unverified, and asset/build/release directories are reserved only.
- GitHub admin branch protection/rulesets, native art QA and actual graphical/runtime tests remain separate non-simulatable approval gates.
