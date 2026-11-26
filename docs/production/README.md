# AETHERFALL production command centre

**Start here:** [../../BUILD_HERE.md](../../BUILD_HERE.md).  
**Authoritative task queue:** `WORK_QUEUE.json` (IDs, dependencies, status, acceptance and evidence).  
**Human build order:** [MASTER_BUILD_ROADMAP.md](MASTER_BUILD_ROADMAP.md).

Read [the source and review hardening guide](../security/REPO_HARDENING.md), [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md), [TEST_MATRIX.md](TEST_MATRIX.md), [DECISIONS_AND_RISKS.md](DECISIONS_AND_RISKS.md), [HANDOFF_AND_RECOVERY.md](HANDOFF_AND_RECOVERY.md) and [RELEASE_AND_OPERATIONS.md](RELEASE_AND_OPERATIONS.md) to understand every gate.

```sh
python3 tools/production_queue.py --next
python3 tools/production_queue.py --summary
python3 tools/production_queue.py --validate
```

This is an ordered plan and safe handoff mechanism, **not** an autonomous worker. All tasks start `planned`; no unverified work is silently marked complete.
