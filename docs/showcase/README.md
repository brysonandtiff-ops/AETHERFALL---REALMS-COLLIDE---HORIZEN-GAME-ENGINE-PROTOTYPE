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
