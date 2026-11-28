# AETHERFALL — SAFE GIT START

**This is the Git entry point; for game building use the approved Godot workflow.**

1. Identify your source: `git status -sb` and `git rev-parse HEAD`.
2. Run `python3 tools/git_preflight.py doctor`. It inspects the local checkout **without changing it**.
3. Review [open PRs](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/pulls) and the [dependency map](docs/development/PR_INTEGRATION_MAP.md).
4. One authorised work order → one branch → one small PR. Follow `AGENTS.md` and owner-locked artwork.
5. Run `python3 tools/validate_structure.py` and `python3 -m unittest discover -s tests -v`. For clean committed work, check an exact SHA and trusted parent with `tools/git_preflight.py check`.
6. Link the actual source SHA, CI run, genuine evidence and rollback. Obtain independent review before merge.

**Remaining blocker:** main now has an active GitHub ruleset, but it requires **zero approving reviews** and does not yet require CODEOWNERS approval or the new Git preflight check. [Issue #11](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/issues/11) tracks those missing enforcement steps.

This preflight supplements S.I.R.E. Git Stop; it does not fetch, push, merge, install an agent, charge an API or certify gameplay.
