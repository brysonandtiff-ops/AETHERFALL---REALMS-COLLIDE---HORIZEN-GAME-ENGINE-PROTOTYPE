# GitHub main-branch protection — operator checklist

**Current observed state (2026-11-26):** main protected=false. The connected GitHub tool can edit repository content but DOES NOT offer a branch-protection/ruleset WRITE action. CODEOWNERS by itself is informational, not mandatory. This setup requires the repository administrator to enable rules in GitHub; no claim is made that the server-side lock is active.

Repository: brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE
Settings: https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/settings/rules

## Required main ruleset

1. Create an **Active** branch ruleset targeting the exact default branch main (or equivalent branch-protection rule).
2. Require a pull request before merging; require at least one owner approval and mandatory CODEOWNERS review; dismiss stale reviews after pushed changes.
3. Require successful status checks from the AETHERFALL workflow: **static-source-security** and **native-godot-4-7-2-smoke** (exact job names shown on real completed PR). Set them to require up-to-date merge branch checks if available.
4. Block force pushes and branch deletion; restrict direct updates and admin bypass wherever your GitHub plan and permissions support it. Require conversation resolution.
5. Require changes to approved source art/manifest/validator/AGENTS.md to be owner-reviewed. Existing CODEOWNERS already covers important areas; add /AGENTS.md and /docs/characters/CANON_LOCKS.json if missing from coverage.
6. Verify by opening Settings → Rules → Rulesets (or Settings → Branches) and checking that main displays protection enabled. Open a harmless failing PR to confirm it cannot merge while static-source-security fails; do not deliberately push unverified art to main.

## Important limitations

CI checks static hashes, paths, mandatory planning, and source-approved identity metadata. It cannot judge generated faces, armor or model resemblance; source-to-output visual review and actual screenshots still required. The Vellaris and ThornDell source files are external and must be imported as correct, verified binaries before declaring source-archived. PR #9 remains reviewable and should only be merged after its checks and owner review. No existing game code/artwork is deleted by this rule.
