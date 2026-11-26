# Security policy — AETHERFALL

Never put live tokens, signing keys, private user/player data, credentials, copyrighted artwork without rights, or private photographs in public Git history, issues, CI logs or screenshots.

Report possible vulnerabilities to the repository owner **privately**, using GitHub private vulnerability reporting if enabled or an existing trusted private channel. A leaked secret must be revoked/rotated even after the commit is reverted. Do not paste secret values into public tickets.

The new `tools/git_preflight.py` catches only **obvious added patterns**, conflict debris and source hazards. It is not an independent security audit or full secrets scanner. Existing S.I.R.E. Git Stop and permission policies remain authoritative.

The main GitHub ruleset is now **active**, but it requires **zero independent reviewer approvals** and does not yet enforce the new preflight check ([Issue #11](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/issues/11)). Green CI alone is not permission to merge or deploy.
