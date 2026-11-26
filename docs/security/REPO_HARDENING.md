# AETHERFALL — source, queue, security and review hardening

**Scope:** Repo source and build-plan integrity for a public Godot/Blender game project. **Status:** Source-level controls on the feature/review branch. No playable hero, validated graphics or production servers are implied.

## Threat model and protected canon

The repo may receive contributor PRs, imported 3D art, text configuration, external links and automated build submissions. Risks include accidental deletion of original artwork, changing character identity or existing tasks, leaked credentials, unsafe submodules, stale proof, CI bypass, source-to-runtime confusion and unauthorized release.

Preserve approved visual canon, real owner photographs, original Blender files, stable `CHR_*` and Godot resource IDs, Shadowspire migration history, `game/project.godot`, the real `art/asset_registry.json`, and evidence provenance. Do not fetch or copy proprietary Overwatch 2/Marvel Rivals client assets. Store personal originals and files without public publishing permission outside this **public repository** unless the owner explicitly approves a safe location and rights.

## Automated local/CI controls

1. `python3 tools/validate_structure.py` checks expected files/dirs, safe registry paths, Godot references, case collisions, links, private key filenames, common high-confidence embedded credential patterns, large directly stored binary assets, committed ignored caches and git submodules.
2. `python3 tools/production_queue.py --validate` rejects malformed/duplicate fields, cycles, later-phase dependencies, unproven statuses, spoofed evidence-host URLs, missing executors/reviewer identities and accidental task completion with no evidence references.
3. On PRs after the plan lands on the target branch, `python3 tools/production_queue.py --audit-baseline <prior_queue.json>` rejects removed/renamed/reordered old tasks, silent contract rewrites, illegal status jumps and rewritten already-verified proof. Only new tasks may be appended as PLANNED. Initial adoption skips base-history comparison because no queue exists on main yet.
4. `python3 -m unittest discover -s tests -v` runs source, task and adversarial tests. PR CI also imports and launches real SHA256-pinned Godot 4.7.2 headlessly. These do not test rendered gameplay, Blender models or real devices.
5. `.github/CODEOWNERS` marks affected paths for `@brysonandtiff-ops`. **CODEOWNERS by itself does not block direct pushes or force an approval.** Reviewer approval must be configured using GitHub administration rulesets/branch protection.

The secret detector only catches known obvious text signatures; it does not guarantee no secrets in binary images, encoded files, a live Git history, cloud accounts or outputs on an external machine. A compromised or malicious change to the workflow/scanner in its own PR also needs independent GitHub enforcement.

## Required owner-side GitHub settings (cannot claim active)

At the audit on 2026-11-26, the connected GitHub API returned **no repository rulesets** and did not grant read access to the `main` branch protection endpoint (HTTP 403). Therefore enforcement of protection on `main` is **not verified**. Do not report that the branch is protected.

With authorised GitHub administrator access, review settings for `main` before merging:

- Require PRs instead of direct pushes; block force-pushes and accidental branch deletion.
- Require the exact successful source-plan/CI and native Godot smoke checks. Require fresh checks for the latest commit; invalidate stale review approvals when new commits arrive.
- Require at least one authorised **independent** reviewer of changes to CI, original artwork, queue, governance, release configuration and other sensitive paths. GitHub will not count the author's own review as independent; if only one account exists, establish an approved external reviewer or use an owner-governed alternative rather than enabling an impossible gate.
- Limit bypass permissions and review administrator/bot token privileges; keep GitHub Action tokens read-only by default. Only enable deliberate signed/release credentials with explicit approval.
- Consider private asset storage and a licensed Git LFS/storage and backup policy before pushing binary original/owner photos.

**No merge, release, codeowner enforcement, paid hosting or administrator change is performed by these instructions.**

## Recovery and risk boundaries

- A changed task can move `planned → review → verified` only with appropriate candidate evidence, a reviewer and real observed results. In-progress/blocked repair flows are allowed; verified claims need true Git identity and evidence.
- To *change* a previously frozen task specification, open a separate owner-reviewed governance migration that explicitly preserves the historical decision and updates the corresponding tests. Do not silently delete a task or disable CI to get green.
- On failed tests stop promotion, keep the red result, repair the root cause, rerun affected and full source tests and link resulting logs. Independent unblocked tasks can continue.
- If a credential might have been committed, restrict exposure immediately, rotate/revoke it at the actual provider and consider the entire Git history exposed; deleting a single working-tree file is not sufficient.
- For protected art/IP issues, pause affected upload, verify provenance and owner approval and preserve originals. No fabricated game-engine screenshots or counterfeit art.
- A passing CI run is a source-level check; native graphical Blender/Godot/device/security performance gates still need separately recorded results. Use `docs/evidence/PROOF_REQUIREMENTS.md`.

## Recorded verification

Review this branch's latest GitHub Actions run for actual exit codes, test count and native headless import/boot. Link the exact commit SHA in the PR after checks finish; never stamp unrun tests as passed.

## Files to inspect for continuity

`BUILD_HERE.md`, `AGENTS.md`, `docs/production/WORK_QUEUE.json`, `docs/production/DEFINITION_OF_DONE.md`, `docs/production/HANDOFF_AND_RECOVERY.md`, `docs/architecture/HARDENING_POLICY.md`, `.github/workflows/foundation-check.yml`, `.github/CODEOWNERS` and `tests/`.

## AAA layout, plugin and toolchain isolation

`studio/layout_manifest.json` defines ten ownership zones and thirteen runtime module boundaries. The new `tools/validate_studio_layout.py` detects removals, misrouted future modules, dangerous paths, contradictory Godot/Blender/Perforce claims, dropped art-root protections and suspicious Unreal-only cooked assets inside the Godot source tree. CI executes this validator as a separate step.

The hierarchy is **not** proof of a running commercial build farm or a Blender/render pipeline. All future plugins under `game/addons/` must have local `AETHERFALL_PROVENANCE.md` evidence of source, licence, hash, Godot compatibility and owner review. External secrets, expensive infrastructure, LFS/Perforce changes and public release require separate approval.
