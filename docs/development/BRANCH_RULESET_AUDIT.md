# Main branch rule audit — 26 November 2026

**Read-only GitHub observation, not an admin change.** The GitHub API reports `main` protected by the **active** ruleset named **AETHERFALL Final Lock**, ID **28139464**, targeting the default branch.

| Rule | Observed setting |
| --- | --- |
| Ruleset | Active; default branch |
| Deletion/non-fast-forward blocking | Enforced |
| Require pull request | Yes |
| Required approving reviews | **0** |
| Require CODEOWNERS approval | **No** |
| Dismiss stale approvals on push | **No** |
| Require last-push approval | **No** |
| Required conversation resolution | Yes |
| Required status checks | `static-source-security`, `native-godot-4-7-2-smoke` |
| Strict up-to-date status check policy | **No** |
| Listed bypass actors | None |

GitHub's separate branch-protection details endpoints returned `403` to this integration. This audit relies on the readable ruleset detail and main branch metadata.

## Owner-admin changes remaining

1. Require **at least one independent qualified reviewer**, code-owner reviews where supported, and stale-review dismissal on changed commits.
2. Prefer latest-commit approval and an up-to-date required-check policy.
3. **After the Git hygiene PR #14 is independently approved and merged**, add `git-preflight` as a required status check to the two existing checks.
4. Open a deliberately failing review PR and confirm GitHub blocks merge; verify no bypass.
5. Reconcile the overlapping AAA studio PR #8 and the stacked S.I.R.E. PR #1→#2→#6→#10 through a separate reviewed integration candidate ([Issue #15](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/issues/15)).

An active rule requiring **zero reviews** is not a verified independent-review seal. Source-test success is not game/runtime/device release proof. The owner task remains [Issue #11](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/issues/11).
