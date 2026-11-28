# S.I.R.E. integration map — exact, fail-closed boundaries

**Parent authority:** [S.I.R.E. repository](https://github.com/brysonandtiff-ops/SIRE). **Project:** AETHERFALL, [this repository](https://github.com/brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE).

We reuse existing upstream components **rather than copy agents or register another master plugin**. The source-based links below exist in S.I.R.E. but do not guarantee a live authentication session.

| Responsibility | Existing source | AETHERFALL contract | Runtime state |
| --- | --- | --- | --- |
| Master / governance | S.I.R.E AI / `AGENTS.md` | `.sire/integration.json` | NOT_CONNECTED |
| Coding supervisor | `sire/agent/` | work orders + handoff envelope | DEFINED_NOT_CONNECTED |
| GENESIS AI / HORIZON | `sire/studio/`, `sire/genesis/` | gameplay and art skill routing | DEFINED_NOT_CONNECTED |
| Git / PR safety | `sire/gitstop/`, `.claude/agents/git-steward.md` | draft PR and review gates | DEFINED_NOT_CONNECTED |
| Plugins and secrets | `sire/plugins/permission_matrix.py` | manifest only, no plugin copies | DEFINED_NOT_CONNECTED |
| MCP | `sire/mcp/server.py` | no live HTTP/stdio link added | DEFINED_NOT_CONNECTED |
| Native test | GitHub Actions + Godot 4.7.2 | existing headless CI | RECHECK ON PR |
| Device/graphical evidence | independent captured media | `evidence/` | NOT_RUN |

**Command map:** `.sire/commands.json`; `python3 tools/aetherfall.py cmd <KEY>`.

**Skills:** `.sire/skills/*.md` hold per-domain handoff instructions. These are project docs and are not automatically installed ChatGPT plugins.

**Work orders:** `.sire/work-orders/*.json` — locally and in Git. `handoff` emits a JSON proposal including exact git SHA; *sending*, executing and accepting it are separate actions by an authorised executor.

**To reach a real live integration:** an owner-authorised runner must confirm repository/branch permissions, authenticate to existing S.I.R.E. agent/MCP, validate the SHA and policy, independently run the work and return signed/testable source-linked evidence. No OAuth or bridge is bypassed.

**Guardrails:** no background daemon created; no new service cost; no unapproved API calls; no secrets in source; no auto-merge/deploy; no claim a proposed team is already working.
