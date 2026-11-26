# Work order queue

Work orders are **reviewable JSON requests**, not executable commands or running agents.

Each order must include: ID, project, repository, goal, authorised executor, requirements, current status, completion criteria, evidence status and rollback. Keep execution_status = NOT_CONNECTED unless a real source-pinned authenticated handoff runs.

CLI:
```sh
python3 tools/aetherfall.py work list
python3 tools/aetherfall.py work show AETHERFALL-DEVOPS-001
python3 tools/aetherfall.py handoff AETHERFALL-DEVOPS-001
```

`handoff` prints a proposal; it never calls an LLM, MCP server, S.I.R.E. worker or network. A separate authorised executor must review and accept it. NEVER assert that writing a work-order is dispatch success.

Create the next bounded, **local** work order without overwriting an old one:

```sh
python3 tools/aetherfall.py work new AETHERFALL-ART-002 \
  --team character_art \
  --goal "Import approved Vellaris model while preserving its source" \
  --criterion "Actual Godot 4.7.2 import succeeds"
```

The command writes only `.sire/work-orders/AETHERFALL-ART-002.json`, with `PLANNED` status and all evidence `NOT_RUN`. Review/commit it in a new development branch; it will **not** dispatch itself. Existing IDs are never overwritten. `python3 tools/aetherfall.py calls --json` lists existing upstream suggested commands and reports their live connections as unverified.
