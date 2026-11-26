# S.I.R.E. // HORIZEN GAME ENGINE

A self-contained, offline-capable **local PWA shell**, distinct from the unverified Godot game-engine binary. Official app title: **HORIZEN GAME ENGINE**. Featured game: **AETHERFALL: REALMS COLLIDE**.

## What actually works

- **World Library:** search/filter four seed catalog entries; register custom local worlds; stage/archive; verify same-origin HTTP HTML entry before launching a browser build. The HTML check is **not gameplay certification**. Catalog and asset metadata persist in localStorage.
- **System Status:** 10 honest evidence gates and seven subsystem cards. Native engine, release, phone, connected fleet, and owner art approval remain **HOLD / NOT VERIFIED**.
- **Model Forge:** register genuine local `.glb`, `.obj` or `.fbx` files (64 MiB browser limit), hash with Web Crypto SHA-256, inspect glTF 2.0 embedded geometry or OBJ polygons, render actual local triangles through WebGL2 (Canvas2D source-triangle fallback where WebGL2 is unavailable), and submit hash-backed supporting evidence at each of eight production stages. FBX is **hash only**; uploaded files are not persisted. Browser previews are **not** Blender/Godot renders, canonical acceptance, animation or material verification.
- **GAISLINK Doctor:** browser prerequisites and an optional *same-origin* health endpoint check. Even a matching health response does not authenticate GAISLINK authority or certify a connection.
- **Staging receipts:** JSON export/import, with schema validation and independent-review state. Imported receipts contain metadata, **not original source bytes**.
- **Offline PWA:** service worker caches only application shell resources after first successful online load. Server responses use no-store; updates are network-first, offline fallback from service worker cache.

## Run on a computer

```sh
cd horizen-game-engine
python3 serve.py --port 8080
# open http://127.0.0.1:8080 in a Chromium browser
```

For tests: `node --test tests/*.test.mjs` (Node 20+). For an optional real browser smoke test in an environment with Playwright and Chromium: `python3 tests/browser_smoke.py` (does **not** prove Android native installation).

## Run locally on a phone (Termux + Chrome)

1. Put **these actual PWA files**, including `icons/`, into `~/horizen-game-engine/` in Termux. Do not confuse the GitHub repository path or archive name with a completed phone transfer.
2. Install Python (`pkg install python`) and, optionally, `psmisc` (`pkg install psmisc`) to clear the reserved local port.
3. Copy `start-horizen-engine.sh` to `~/start-horizen-engine.sh` and run `chmod +x ~/start-horizen-engine.sh`.
4. Run `~/start-horizen-engine.sh`, then open `http://127.0.0.1:8080` in **Chrome on the same phone**. If an old *Horizen / Horizen Studios* shortcut remains, remove it. Use **Add to Home screen → Install**.
5. Load the shell once with the server running before testing offline. Browsing outside the cached shell (including registered game builds) is not guaranteed offline.

The localhost web server binds to `127.0.0.1` and does **not** expose itself on a Wi-Fi or remote interface. The app itself has no remote executor. The launcher clears port 8080 when `fuser`/`lsof` is available; it should not be run while an unrelated app is using that port.

## Explicit non-completion boundaries

No generated art or fake frame is included. No model is promoted to canonical art. No game is claimed to be playable, no Godot/Blender/Android validation is implied, and no GitHub commit is a release certificate. S.I.R.E. stages; external platforms govern final publishing.

Original assets should remain in the approved **AETHERFALL** source folders. Refer to `../AGENTS.md`, `../docs/characters/VISUAL_CANON_LOCK.md`, and `../docs/art/ASSET_PIPELINE.md` when this folder lives inside the AETHERFALL repository.
