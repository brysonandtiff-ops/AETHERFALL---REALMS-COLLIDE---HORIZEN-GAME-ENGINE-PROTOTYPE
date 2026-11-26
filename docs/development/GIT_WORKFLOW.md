# AETHERFALL Git workflow

**FIND → PLAN → BUILD → TEST → REPAIR → RETEST → SHOW → HARDEN → PROVE → FINISH.** Existing S.I.R.E. Git Team remains the authority.

## Each working session

```sh
git status -sb
git rev-parse HEAD
python3 tools/git_preflight.py doctor
python3 tools/validate_structure.py
python3 -m unittest discover -s tests -v
```

The doctor makes **no Git writes or network calls**. Use an approved branch and one scoped work order. The AAA-studio PR #8 proposes `studio_preflight.py` and a task queue, but those commands are **not on main** until its code is independently reviewed/merged.

## Before handing off a committed PR

```sh
python3 tools/git_preflight.py check --expected-head ACTUAL_40_HEX_SHA --base TRUSTED_BASE_40_HEX_SHA
```

Supply the actual HEAD and parent SHA independently. This checks clean Git, correct repository identity, ancestral base, added merge-conflict debris, whitespace problems, obvious added credential shapes and destructive removal of original files. It flags reviewed art/security paths but **does not independently approve** them.

Stacked PRs require parent-before-child integration, SHA refresh, and new CI after resolving each parent. Never treat yesterday's successful tests as certification for today's rewritten source. [Map](PR_INTEGRATION_MAP.md).

## Owner-required server rule

At audit `main` was unprotected with no active rulesets. CODEOWNERS and the new CI do not stop direct pushes until an owner enables active branch rules requiring pull requests, an independent reviewer, passing `static-source-security`, `native-godot-4-7-2-smoke` and `git-preflight` jobs, no force pushes/deletions, and restricted bypass. Follow [Issue #11](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/issues/11); verify actual GitHub settings before claiming it is active.
