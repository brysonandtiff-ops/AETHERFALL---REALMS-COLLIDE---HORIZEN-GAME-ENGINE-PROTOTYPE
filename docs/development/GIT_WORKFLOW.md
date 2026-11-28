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

The later GitHub verification on 26 November 2026 found an active ruleset protecting `main` from deletion and non-fast-forward pushes. **However, it requires zero approving reviews**, does not require CODEOWNERS review, does not require up-to-date branch checks, and lists only `static-source-security` and `native-godot-4-7-2-smoke` as required status checks. The new `git-preflight` job can be added after PR #14 is reviewed and merged. The owner-admin must enable independent review and confirm it through a blocked failing PR. See [exact observed settings](BRANCH_RULESET_AUDIT.md) and [Issue #11](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/issues/11).
