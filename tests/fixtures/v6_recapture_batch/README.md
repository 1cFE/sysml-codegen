# ACCEPTED v6 recapture batch — owner ruling 2026-08-11

**This batch is authority.** The owner accepted it at the 2026-08-11 REVISE disposition
(`.project/active/cutover-recovery/owner-disposition-20260811.md`, step 1). The plan's
Gate 4C rule keeps the 37 committed v5 snapshots "until their accepted v6 replacements are
ready in the same candidate" — this is that accepted replacement set, and the retirement
executes against it.

Everything in this batch is reversible by Git. If the owner revises the batch, the
retirement commits that follow it revert with it.

## What is in it

37 corpus fixtures, each with exactly one record, and which one is not the batch's choice —
it is whatever the shipped public capture does with that fixture.

| | Count | Where it lives |
|---|---:|---|
| v6 snapshots | **15** | `tests/fixtures/<name>/instance_graph_snapshot.json` |
| typed refusal records | **22** | `batch.json`, `records.<name>` |

A refusal is a real outcome, not a gap. The exact route declines these fixtures, and the
record carries the error class and the exact code multiset rather than a summary, so a
refusal that changes shape is a diff and not a shrug.

## How it was produced, and what was checked

```bash
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
python scripts/capture_v6_batch.py --verify
```

- **Shipped public capture only.** `capture_instance_graph_snapshot`, the same entry point
  the CLI uses. The batch cannot drift from the product because it has no capture code of
  its own.
- **Live equals replay, per fixture.** For all 15: the in-place and relocated reads agree on
  the instance fingerprint and on the projected computation graph, and the projected graph
  equals the live route's modulo the one module `source_file` divergence Slice 3B pinned and
  3E carried. This is the 3A/3B route-test bar, applied fixture by fixture.
- **Every outcome matched the amended Phase 2 corpus ledger**: 15 graph outcomes and 22
  refusals, both error classes with their exact multisets, **0 deviations**. A deviation
  would have been a rule-10 stop, not a new baseline.
- **`fusion_tea`'s already-committed v6 snapshot was reproduced byte-identically** by this
  run. Capture is deterministic, independently confirmed.
- **No absolute paths** in any snapshot or in the manifest, so the batch is portable across
  checkout roots.

## Keeping it honest

`tests/conformance/test_v6_recapture_batch.py` re-derives all of this from the committed
files: every fixture is claimed exactly once, every captured snapshot loads and projects to
the outcome recorded for it, every refusal record is typed, and the whole set still agrees
with the corpus ledger. `python scripts/capture_v6_batch.py --check` does the ledger
comparison alone, without a license.
