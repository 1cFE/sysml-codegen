# Phase 1 stop report — stop rule tripped, halted to owner

**Date:** 2026-08-17
**Status:** Phase 1 NOT executed. No commits on either implementation branch. Both worktrees clean
at their pinned SHAs; `occurrence.py` byte-identical to `C_base`. Original user checkouts retain
their entry digests.

The Phase 1 implement agent (session `9a72162c`, $2.90) verified the base, ran the retained
harness (37 passed) and D1-D4 matrix (105 passed, licensed tests genuinely live), then tripped the
Global Execution Contract's lock rule and stopped without writing anything. The orchestrator
independently re-verified every load-bearing claim below by hand; all reproduced exactly.

## Finding 1 — two locked inputs changed between the lock and `C_base` [CONFIRMED]

116 of 118 locked hashes recompute. Two do not:

| Locked path | Locked (43edf9bd) | At `C_base` | Changed by |
|---|---|---|---|
| `tests/fixtures/v6_recapture_batch/batch.json` | `bd7bf245…` | `7f926978…` | `09fdae1`, `da4aa78` |
| `verification/capture_baseline.py` | `6aef97af…` | `c8a7de07…` | `da4aa78`, `46694e2` |

The `batch.json` change is a baseline recapture after production code changed — exactly what
design.md forbids ("No baseline is recaptured after production code changes and then called
'before.'"). Confirmed content shift: `deep_cross_scope_probe` moved captured → refused; counts
15 graph / 22 refused → 14 / 23; every graph snapshot sha rewritten. `C_base` is self-contradictory:
its own `verification/fixture-manifest.json` still pins `canonical_batch.sha256 = bd7bf245…` (the
pre-recapture bytes) and design.md's Closed fixture inventory pins the same. Nothing caught it
because `test_evidence_artifact_topology.py` asserts only the lock's key set, never recomputes
hashes.

## Finding 2 — `deep_cross_scope_probe` flip, root cause identified [CONFIRMED]

At `C_base` the probe refuses with
`SI_OCCURRENCE_MISSING: reference='measurement_system::station::array::sensor::core::metric_value':
exact output … has no producer in the consumer domain` — a named, fail-closed refusal with the
authored reference preserved. The flip came from `09fdae1` "Adopt semantic evidence boundary".
Prior memory records `deep_cross_scope` as a pre-existing stale-baseline class still needing an
owner. Whether this flip is the intended tightening or a regression is an owner/design ruling, not
an implementation detail.

## Finding 3 — the design's stated escape shape does not reproduce [CONFIRMED]

Orchestrator re-ran the probes independently at `C_base`, licensed:

| Shape | Result |
|---|---|
| `attribute picked : Real = cells#(2).mass;`, `cells : Cell[3]` (design's shape) | REFUSED — `SI_OCCURRENCE_AMBIGUOUS` (+ `SI_OCCURRENCE_MISSING` cascade), reference preserved |
| same but wrapped in an operator | REFUSED — `SI_INDEXED_SOURCE_UNSUPPORTED` (correct code) |
| `cells#(2).mass` bare, `cells : Cell[1]` (index out of range) | **zero-diagnostic graph** — silently collapses to `cells[0].mass` |

The real escape is a bare indexed feature chain into a singular slot — including an out-of-range
authored index silently rewritten. The design's "Current code facts" trigger description and the
Phase 1 stencil (`Cell[3]` shape) are factually wrong: that stencil goes red for the wrong reason
(ambiguity refusal), which the plan itself rejects as the proof point. The plural shape is already
being refused incidentally by the occurrence layer under the wrong diagnostic name — part of the
intended A5 coverage is currently answered by `SI_OCCURRENCE_AMBIGUOUS` instead of
`SI_INDEXED_SOURCE_UNSUPPORTED`.

## Disposition

Per the plan's rollback rule ("any changed locked input … returns the item to design") and the
owner-reserved gate ("stop-rule trips halt to owner"), the run is halted pending owner decisions:

1. Base authority: return to design / re-root at `43edf9bd` / accept `C_base` with an explicitly
   recorded transition and re-derived lock.
2. Ruling on the `deep_cross_scope` captured→refused flip: intended tightening or regression.
3. Correction scope for the escape-trigger facts and Phase 1 stencil (targeted design amendment vs
   broader revisit, given the wrong-name ambiguity coverage).

Probe evidence: `/tmp/stop-parser-rev2/scratch/`. Stage log: `/tmp/stop-parser-rev2/logs/`.
