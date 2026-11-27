# AETHERFALL – REALMS COLIDE | Exact Git work-order readout
**Snapshot:** 26 November 2026, ~21:40 Australia/Perth. **Authorised owner request:** add content from 40292.mp4, inspect actual connected Git state and provide prioritized repository steps. **Executor:** current connected GitHub integration for reviewed source branches, local Python for offline helper checks. **Source-of-truth distinction:** these are REMOTE GitHub observations, **not** a claim to have run `git status` on the owner's phone or a live game project.

## Remote Git HEAD and protection
| Repo | Main SHA at snapshot | Observed GitHub protection | What is actually there |
| --- | --- | --- | --- |
| `brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE` | `c11443f01213aaea1b6e86e4f9bed303051135dd` | `protected: true`; active ruleset `AETHERFALL Final Lock`. Detailed branch rules cannot be read by connector (403). | Godot bootstrap/source framework, 10 reserved character IDs, plans and concept references; **zero committed hero .glb/.blend exports, zero source-verified playable heroes**. |
| `brysonandtiff-ops/SIRE` | `061943f2dd67c1d5cfd943f1739348346b433636` | `protected: false` at snapshot; ruleset endpoint inaccessible for private plan. | Existing S.I.R.E. services and web shell. New HORIZEN PWA and 3D studio are in unmerged PR branches. |

## Actual relevant PRs and dependencies
| Repository | PR | State on snapshot | Action |
| --- | --- | --- | --- |
| AETHERFALL | #19 canonical Vellaris THIRD-image art style lock | open, source CI green, unmerged | Owner review first; safeguard 39403.png actual WebP and AETHERFALL – REALMS COLIDE title. |
| AETHERFALL | #20 infographic-first standard | draft, CI green, unmerged | Reconcile with #19. Preserve improvements; avoid two contradictory style masters. |
| AETHERFALL | #24 HORIZEN local-first PWA | open, three CI workflows green, unmerged | Review install / Model Forge quality, exact source, safe local storage; canonical app decision with S.I.R.E. |
| AETHERFALL | #26 **video 40292** exporter/model vault | open, base **#24 feature branch**; 3 workflows green, unmerged | Review and merge only after parent #24 is integrated or the chain is safely rebased. |
| AETHERFALL | #25 raw sculpt quality seal | draft, CI green, unmerged | Incorporate canon-safe sculpt quality SOP after art-lock review; no fabricated 3D acceptance. |
| AETHERFALL | #22/#23 1P/3P pipeline and Blender SOP | drafts, unmerged | Consolidate the pipeline without overlapping master laws or artist files. |
| AETHERFALL | #4 Razor/Raven and #13 Vellaris proxy | drafts, unmerged | Import only genuine source models with owner side-by-side approval. No GLB model binaries in those PR diffs. |
| S.I.R.E. | #885 3D Asset Studio | draft, no completed workflow run evidenced for HEAD | Review/test source GLB viewer, topology and locked reference handling before merge. |
| S.I.R.E. | #886 installable HORIZEN PWA | draft, **based on #885**, HORIZEN source/build gate green | Merge only after #885 + art/mobile checks, no duplicate independent PWA shells. |
| S.I.R.E. | #887 native Godot workbench | draft, based on main, no workflow run evidenced for HEAD | Verify actual native executor, Godot project open/run, real screenshots and Android permissions. |

## The uploaded video
`40292.mp4`: **19,328,053 bytes; SHA-256 9539f1ab23bd250d1d91b008a13144666d8b0967a7eee537df55c67b3aae0782**, H264 1200×1080, about 22s. It's a screen recording of Python and JavaScript *proposed code* in a chat, **NOT proof that Blender, Three.js, IndexedDB or Godot ran**. A factual evidence manifest is in `evidence/intake/40292_CODE_REFERENCE_2026-11-26.json`. Its **original MP4 bytes remain a conversation attachment, not a Git object**. Long-term media archival and readback remain open.

### Implemented on the stacked #26 branch
- `tools/horizen_blender_export.py`: selected mesh GLB export + binary STL scaled for mm and a source-hashed, versioned audit receipt. Does not auto-thicken, auto-slice or fake print certification.
- `tools/horizen_mesh_io.py`: offline geometry, manifold-candidate screening, binary STL and SHA-256. Six local unit tests passed.
- `horizen-game-engine/model-extra.js`, `model-inspect.js`: binary/ASCII STL and self-contained embedded glTF triangles, existing GLB/OBJ plus hash-only FBX. No fake external file retrieval.
- `horizen-game-engine/model-vault.js`, `app.js`, `index.html`, `sw.js`: opt-in IndexedDB original-file persistence with SHA readback, retained-file deletion and offline module cache.
- `docs/characters/MODEL_STEP_CHECKLIST_2026-11-26.md`: the 15-character evidence-graded model checklist.
- No approved character reference, rig or game-engine asset was modified.

**CI snapshot on #26:** HORIZEN PWA 18 Node model/contract tests passed + 4 server tests + 4 launcher tests; AETHERFALL 67 Python safety tests passed; Git preflight 18 passed; native **Godot 4.7.2 HEADLESS BOOT** passed (only startup, NOT art/gameplay). The earlier service-worker version test failure was repaired and the re-run passed.

**Unverified:** the actual Blender CLI exporter in native Blender, full graphical browser UI, true IndexedDB reload on a real Chrome page, physical Android installation, Godot imported models, animation, gameplay and 3D print slicer output. A local Chromium browser attempt was blocked by administrator network navigation before page load; **do not call it a browser PASS**.

## Required order — AETHERFALL (game source)
1. **ART LOCK:** Review #19 and the overlapping #18/#20 policies. Pick one source-of-truth style reference: the owner's THIRD Vellaris image `39403.png`, actual 1536×1152 WebP SHA-256 `4d100d50cf0769da47cbe1b782deeb842d15a11c1c46a08f8bd5bd090fa34939`. Archive exact bytes with checksum, don't replace other heroes with Vellaris.
2. **PWA BASE:** Review PR #24, check release authority, offline shell, loopback Termux launcher, original asset handling and the relationship to S.I.R.E. PR #886. Settle which is the supported primary PWA before accepting two shells.
3. **VIDEO INTEGRATION:** Review PR #26 against #24. Run Python/Node CI and source/manifest safety. Merge after parent or rebase with exact diff; never bypass protections. If desired, archive 40292.mp4 as original evidence using approved binary storage, separate from game assets.
4. **VISUAL MODEL INTAKE:** Use the checklist: existing externally documented offline blockouts Korvex/Razor/Raven need source originals imported and hashed; Vellaris/ThornDell previews are not source-certified; 10 others remain concepts. Resolve character IDs/approval without changing locked artwork. Register the missing damage roles in AETHERFALL's asset registry.
5. **NATIVE ART & ENGINE:** In actual Blender test 1P/3P models, topology/UV/rig and the new exporter; create genuine four-view media. In actual Godot import 3D GLBs, test scene, animation, abilities, scale/collision and camera variants; record exact tool versions and source commit.
6. **PHONE / RELEASE:** Independently test installed HORIZEN PWA and actual Android file storage, quota/offline reload, performance, touch controls and sync. Verify physical phone and signed builds; stage releases only after owner review and external platform gates.

## Required order — S.I.R.E. (master HORIZEN engine)
1. Audit source and native test evidence for PR **#885** local 3D Asset Studio; close any fake engine/visual-evidence assumptions.
2. Review **#886** (stacked on #885) for a single canonical HORIZEN GAME ENGINE PWA, app name, service worker offline behavior, source-file import and model viewer.
3. Port/merge only **missing compatible behavior** from AETHERFALL #26 (STL, embedded glTF, retained-file integrity and Blender handoff) through a reviewable S.I.R.E. PR; do not duplicate a second master PWA or break S.I.R.E. plugins.
4. Test **#887** native Godot bridge with a real selected source project, version check, import, edit/run, error recovery and permissions. GUI/device evidence is still missing.
5. Improve S.I.R.E. default-branch protection: GitHub reported `protected:false`. Admin should require owner-approved PRs and relevant CI when supported by the private plan. **Do not assume settings or bypass rights**.
6. Update cross-repo source identity, checksums, build receipts, release blocks and rollback instructions after real tests; no release until actual integrated product proof.

**NEXT ACCEPTANCE RULE:** No one should say "full 3D models completed", "native Blender verified", "works on the phone", "PWA fully integrated", or "game playable" merely from concept sheets, code uploads or headless bootstrap. Real source assets + native import + runtime media + owner-approved art comparison are required.
