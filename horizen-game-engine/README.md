# S.I.R.E. // HORIZEN GAME ENGINE

A self-contained, offline-capable **local PWA shell**, distinct from the unverified Godot game-engine binary. Official app title: **HORIZEN GAME ENGINE**. Featured game: **AETHERFALL: REALMS COLLIDE**.

## What actually works

- **World Library:** search/filter four seed catalog entries; register custom local worlds; stage/archive; verify same-origin HTTP HTML entry before launching a browser build. The HTML check is **not gameplay certification**. Catalog and asset metadata persist in localStorage.
- **System Status:** 10 honest evidence gates and seven subsystem cards. Native engine, release, phone, connected fleet, and owner art approval remain **HOLD / NOT VERIFIED**.
- **Model Forge:** register genuine local `.glb`, self-contained `.gltf`, `.obj`, `.stl` or `.fbx` files (64 MiB limit), hash with Web Crypto SHA-256, inspect supported glTF 2.0 embedded triangles, OBJ polygons, or binary/ASCII STL geometry and preview actual local triangles with WebGL2 or Canvas2D. External glTF `.bin` buffers are not fetched. FBX is **hash only**. Optional **explicit** IndexedDB retention saves chosen original model bytes on this browser; restored files are SHA-256 checked before preview. Users can erase the stored original. Eight production-stage receipts remain pending independent review. No Blender/Godot material, animation, print or gameplay certification is implied.
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
2. Run `termux-setup-storage` if the PWA is in Android shared storage. At the `(y/n)` prompt, type `y` and wait for that command to finish **before entering another command**. Install Python using `pkg install python`.
3. The launcher at `horizen-game-engine/start-horizen-engine.sh` follows Termux's symlinked `~/storage/shared` location and non-destructively copies an extracted `horizen-game-engine/` directory from shared Android storage on its first run. If the files are still inside a ZIP, run `unzip -n /path/to/downloaded.zip -d "$HOME"` **after** the storage setup `(y/n)` prompt finishes. Start it with `bash /path/to/start-horizen-engine.sh`; if already in Termux HOME use `bash ~/start-horizen-engine.sh`. Without the launcher, recover by copying the Android shared source folder to `~/horizen-game-engine/` and running `cd ~/horizen-game-engine && python3 serve.py --port 8081`.
4. Open the **exact local URL the launcher prints** in Chrome on the same phone (usually `http://127.0.0.1:8080`, or `:8081` when port 8080 is occupied). Remove stale legacy shortcuts if necessary, then use **Add to Home screen → Install**.
5. Load the shell once with the server running before testing offline. Browsing outside the cached shell (including registered game builds) is not guaranteed offline.

The localhost web server binds to `127.0.0.1` and does **not** expose itself on a Wi-Fi or remote interface. The app itself has no remote executor. The launcher never kills existing processes. It tries port 8080 and then up to five alternate loopback ports; a PWA installation is tied to its origin (including the port), so re-install if the origin changes. A successful Linux smoke test does not replace actual Android phone acceptance.

## Explicit non-completion boundaries

No generated art or fake frame is included. No model is promoted to canonical art. No game is claimed to be playable, no Godot/Blender/Android validation is implied, and no GitHub commit is a release certificate. S.I.R.E. stages; external platforms govern final publishing.

Original assets should remain in the approved **AETHERFALL** source folders. Refer to `../AGENTS.md`, `../docs/characters/VISUAL_CANON_LOCK.md`, and `../docs/art/ASSET_PIPELINE.md` when this folder lives inside the AETHERFALL repository.


## Video 40292 — Blender and HORIZEN model pipeline intake

Owner upload `40292.mp4` is a 22-second screen recording of *proposed code in a chat*, SHA-256 `9539f1ab23bd250d1d91b008a13144666d8b0967a7eee537df55c67b3aae0782`. It is **not** a working Blender/Three.js demonstration. The full original 19 MB video has not been committed to Git; the evidence identity and media facts are in `../evidence/intake/40292_CODE_REFERENCE_2026-11-26.json`.

### Export from an actual saved Blender file
Set Blender scene units to **Metric**, unit scale **1.0**, and select **exactly one mesh**. In a real Blender environment run:

```sh
blender /path/to/canonical-character.blend --background \
  --python tools/horizen_blender_export.py -- \
  --asset-id CHR_Example --output-dir /path/to/versioned-exports
```

The exporter writes a **new versioned directory** containing one selected-mesh GLB, a **metres-to-millimetres** binary STL and `export_receipt.json` with source object name, Blender version, mesh-edge audit, file lengths and SHA-256s. It does not re-scale or thicken your canonical Blender mesh. **STL wall thickness, manifold quality and printer/slicer acceptance are NOT proved**; perform explicit native repair and slicer validation before printing. It never copies to a phone or publishes anything.

Run the dependency-free tests first: `python3 -m unittest tests/test_horizen_mesh_io.py -v`. A real Blender execution/test and real Godot import must still be completed by an authorised native runner.

### Local model vault

On the HORIZEN Model Forge asset form, choose a real GLB/embedded glTF/OBJ/STL file. Tick **Save the original file in this browser** only if you want optional on-device retention. On a later reload, selecting the asset can restore the original from IndexedDB after verifying the same SHA-256. The **Forget saved original** action removes the stored file. If IndexedDB is missing, full or cleared, choose the source again; **a JSON receipt by itself does not restore geometry**. No automatic device scan or remote upload is implemented. Real Android offline/reload/device acceptance remains pending.

Full production state: `../docs/characters/MODEL_STEP_CHECKLIST_2026-11-26.md`. AETHERFALL game name and art-source locks apply; HORIZEN is the tool/app name, not the game.
