# AETHERFALL review order — dated 26 November 2026

**Snapshot only.** Check the [live PR list](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/pulls) and current base/HEAD before every merge decision.

## Known dependent chain

```text
main
 └── #1 S.I.R.E. routing and dev CLI [DRAFT]
      └── #2 structure + original-art safety [DRAFT]
           └── #6 Android documents [DRAFT]
                └── #10 source-only integrity seal [DRAFT]
```

**Review parent before child: #1 → #2 → #6 → #10.** Retarget/reconcile and rerun CI at the *new exact SHA* after each parent merge. Do not blindly promote all four.

## Other open requests

| PR | Scope | Status at audit |
| --- | --- | --- |
| [#3](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/pull/3) | Local phone asset directory | Draft / Android runtime unverified |
| [#4](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/pull/4) | Razor/Raven DPS blockouts | Draft / owner art review |
| [#5](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/pull/5) | Temporis/Symbion support designs | Draft / design only |
| [#7](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/pull/7) | Tank concept media audit | Draft / true original source pending |
| [#8](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE/pull/8) | AAA studio build roadmap and file tree | Independent open PR; broad overlap |

**Major integration risk:** PR #8 and PRs #1/#2 all edit `AGENTS.md`, `README.md`, `.github/workflows/foundation-check.yml`, `.github/CODEOWNERS` and architecture/source validation files. Choose the approved studio design first; reconcile with the S.I.R.E. stack as a separate reviewed compatibility task. Do not simply accept both sets of changes automatically.

No PR or game release is approved by this map.
