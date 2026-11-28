# Recover Git without losing game work

Keep the original art, Godot UIDs, saves, history, source receipts and work orders intact. **Avoid force push, `git reset --hard`, `git clean -fdx` and hook bypass as generic repair shortcuts.**

**If a merge is conflicted:** inspect `git status -sb`, `git diff`, and the existing S.I.R.E. Git Stop (if connected). Secure unrelated work, resolve individual source conflicts against actual owner-approved artwork and then rerun source/native tests. Only if abandoning an **in-progress merge you initiated**, after safeguarding local changes, consider `git merge --abort`.

**If CI fails:** open the exact SHA's run, capture real first failure and reproduce it. Repair the root cause, add a regression test, and rerun; earlier receipts cannot certify the new commit.

**If something is missing:** inspect `git log -- <path>`, `git show <sha>:<path>` and `git reflog` before restoration. Restore via a reviewable commit from a trusted copy; do not overwrite original binary art.

**If a branch diverged:** inspect `git branch -avv` and `git log --graph --oneline --decorate --all` before any merge/rebase. Use a deliberate PR and new tests, not a history rewrite. On a shared branch, a reviewed `git revert <sha>` is usually safer than force-push.

**If runner/phone/owner art source is unavailable:** mark it BLOCKED/NOT_RUN; never fabricate gameplay, original screenshots or connectivity evidence.

Complete recovery requires a verified source SHA, actual test results, risk/rollback record and independent reviewer.
