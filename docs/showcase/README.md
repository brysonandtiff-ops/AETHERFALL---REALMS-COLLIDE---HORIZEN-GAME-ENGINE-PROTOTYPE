# AETHERFALL — Installable live media showcase

**Owner request:** One clickable, install-to-home web app that automatically reflects progress as AETHERFALL develops.

**Hosted URL:** https://aetherfall-live-showcase.brysonandtiff.workers.dev/

## What actually updates automatically

The Cloudflare Worker source is `docs/showcase/aetherfall-live-worker.js`. The PWA:
- reads the **public** repository `main` tree through GitHub's read-only API and `art/asset_registry.json`;
- discovers committed `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.avif`, `.mp4`, `.webm`, `.mov`, `.m4v` files anywhere in the repository;
- shows character and model names based on verified file paths rather than fabricated model status;
- checks for changes at initial load, upon returning to the app and every two minutes while visible; the GitHub tree/registry fetches use approximately 60-second edge caching;
- serves media by GitHub raw main path with video range headers where upstream supports them;
- provides HTTPS app manifest, 192px/512px PNG icons, service worker for offline shell, and Android Install prompt / fallback instructions.

**Not automatic:** Files left in chat, Library, on a phone, in Downloads or on an uncommitted local disk are **not uploaded** to GitHub or Cloudflare. The Cloudflare Worker bundle is deployed independently from the GitHub feature branch; future gallery content changes need only commits to main, but *website source-code* changes require their own reviewed redeployment. There is no claim of automatic game build, gameplay, rig, Blender or Godot verification.

At initial inspection the GitHub main repository had **zero images and videos**. The prior offline collection of 28 images and 11 MP4s was **not** pushed to this public repo because original art permission, canonical provenance and file-review requirements still apply.

## Owner installation (Android)

1. Open the hosted HTTPS URL in Chrome.
2. Tap **Install to Home** when a browser install prompt is available.
3. If no prompt appears, tap the Chrome menu (three dots), then **Install app** or **Add to Home screen**.
4. Launch AETHERFALL from its icon. Reopening or tapping **Check updates** fetches current repo content.

On iPhone, open in Safari and use Share → Add to Home Screen.

## To publish artwork and videos

Use canonical source paths documented in `docs/art/ASSET_PIPELINE.md`: `art/concepts/characters/CHR_Korvex/<file>.png` for approved concept files, `game/assets/` for exported game-ready assets, and `evidence/godot/` for unedited runtime captures with proofs. Do not mislabel concept videos as real engine captures. Respect `docs/characters/VISUAL_CANON_LOCK.md` and the protected main-branch review process.

Do not bulk-import the offline archive automatically. Record owner approval, source, stage, file hash and license/rights for each public media file. Keep unapproved explorations distinct from approved art. This deployment is a **source-linked gallery**, not a playable game.

## Verification and boundaries

- Worker created under the connected Cloudflare account as `aetherfall-live-showcase`; subdomain enabled, deployment acknowledged by the Cloudflare API.
- JS source syntax checks and actual 192/512 PNG dimensions were verified in an isolated JS harness.
- Manual browser installation, Cloudflare public HTTP playback on an actual phone, native device install and service-worker offline acceptance were **not** performed in this audit.
- GitHub main is protected: source changes are proposed on this feature branch by PR, not forced to main.


## 26 November phone screenshot fix — local gallery importer

The owner confirmed the installed site loaded and displayed the truthful **0 images / 0 videos** from GitHub. To show the previously audited artwork without violating repo art-lock and provenance gates, the PWA now has a **Load existing gallery ZIP** button.

- Download `AETHERFALL_PHONE_GALLERY_STARTER.zip` from the ChatGPT conversation (approximately 10.85 MB). It includes **28 display-optimised WebP images** and **11 original MP4 previews**, plus an import manifest.
- In Android Chrome / the installed AETHERFALL app, tap **Load existing gallery ZIP** and select the downloaded file.
- Browser JavaScript reads the ZIP locally, validates ZIP structure, blocks encryption/path traversal/oversize entries, decompresses via native `DecompressionStream('deflate-raw')`, and stores the results in **IndexedDB on that device**.
- The gallery merges imported device assets with new media committed to GitHub `main`. Media cards label their source as **Device archive** or **GitHub**. Exploratory files containing `UNAPPROVED` are clearly labelled.
- **No upload endpoint was added.** Imported files are not transferred to Cloudflare storage or GitHub, do not alter canonical game art and are not production proof.
- If the user clears website data, changes device/browser or hits a browser storage quota, the local library may need re-importing. The source ZIP remains the recoverable handoff.
- The installed app uses a network-first shell cache v2. Online GitHub polling continues after import.
- 10 mock Worker route tests passed previously; a synthetic ZIP central-directory parser test and actual ZIP CRC readback passed. Actual Android Chrome import and device persistence have **not been observed** and remain an acceptance gate.

This is a deliberate two-source showcase: **private existing media, live public GitHub changes**. Do not call local imported preview art canonical or claim the public GitHub repo contains those images.
