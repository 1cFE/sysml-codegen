# Phase 1 stop report — stop rule tripped, halted to owner

**Date:** 2026-08-17 (revised same day with post-report orchestrator evidence)
**Status:** Phase 1 NOT executed. No commits on either implementation branch. Both worktrees clean
at their pinned SHAs; `occurrence.py` byte-identical to `C_base`. Original user checkouts retain
their entry digests.

The Phase 1 implement agent (session `9a72162c`, $2.90) verified the base, ran the retained
harness (37 passed) and the D1-D4 matrix (105 passed, licensed tests confirmed live), then tripped
the Global Execution Contract's lock rule and stopped without writing anything.

Two protection mechanisms fired, and both worked: the plan's pre-flight (recompute every locked
hash before Phase 1) caught a starting tree that contradicts its own evidence lock, and the
proof-point rule ("a different failure is not the proof point") caught that the design's
description of the defect does not match what the code does. Neither finding touches the approved
architecture (D5-D9, closed variants, inventory-before-consumer, D1-D4); both invalidate specific
factual claims the design makes about the starting state.

Provenance of evidence below: **[verified]** = reproduced by the orchestrator's own commands in the
clean worktree at `C_base`; **[agent]** = the implement agent's run, scratch models retained under
`/tmp/stop-parser-rev2/scratch/`.

## Finding 1 — the lock caught a silent post-production recapture [verified]

Timeline: the lock `43edf9bd` (`probe-fixture-lock.json`, 118 files) was committed 2026-08-17
00:26. The failed candidate kept developing past it on the same line: `09fdae1` "Adopt semantic
evidence boundary" → `da4aa78` (the failed candidate's `C_prod`) → `46694e2` → `78a9beb` = this
plan's `C_base`.

Orchestrator recomputed all 118 locked hashes against `C_base` by hand: exactly 2 mismatch.

| Locked path | Locked (43edf9bd) | At `C_base` | Changed by |
|---|---|---|---|
| `tests/fixtures/v6_recapture_batch/batch.json` | `bd7bf245…` | `7f926978…` | `09fdae1`, `da4aa78` |
| `verification/capture_baseline.py` | `6aef97af…` | `c8a7de07…` | `da4aa78`, `46694e2` |

`batch.json` is a baseline recapture after production code changed — the pattern design.md forbids
("No baseline is recaptured after production code changes and then called 'before'"). Content
shift [verified]: `deep_cross_scope_probe` moved captured → refused; counts 15 graph / 22 refused
→ 14 / 23; every graph snapshot sha rewritten. `C_base` is internally self-contradictory: its own
`verification/fixture-manifest.json` still pins `canonical_batch.sha256 = bd7bf245…` (the
pre-recapture bytes), and design.md's "Closed fixture inventory" pins the same.

**Why nothing caught it:** the committed `test_evidence_artifact_topology.py` asserts only the
lock's key *set* (`set(lock["files"]) == {…}`); no committed test recomputes hashes. The rev-6
design asserted the hashes recompute at `C_base` without anyone having run the recompute; the
Phase-1 pre-flight was the first execution of that check.

## Finding 2 — the old `deep_cross_scope` capture was itself the forbidden defect [verified]

The fixture's Pattern B authors a 6-segment reference,
`in data_point = measurement_system::station::array::sensor::core::metric_value;`, aimed at the one
concrete produced output; the fixture comment says exact projection should wire it there.

How the pre-recapture baseline graph (still present at `C_base` as a stale
`baseline_outputs/deep_cross_scope_probe/computation_graph.json`) actually wired it:

| Consumer | Authored source | Old graph wired it to |
|---|---|---|
| `derived_calc` | (chain to) `core.metric_value` | concrete producer channel `…core__metric_value` — correct |
| `ref_analysis` | `…::core::metric_value` (same concrete output) | `DeepCrossScopeProducer__Core_Metric__metric_value` — a definition-scoped name surfaced as a **caller-supplied entry-point parameter** |

Same authored referent, two different sources; one consumer receives whatever the caller passes.
That is the item's forbidden class verbatim ("never … changed into another expression through a …
caller-supplied substitute"). The old baseline was not a working capture that the evidence boundary
broke; it was a mis-wire of the defect class this item exists to kill.

At `C_base` the same fixture refuses [verified]:
`SI_OCCURRENCE_MISSING: reference='measurement_system::station::array::sensor::core::metric_value':
exact output … has no producer in the consumer domain` — named, fail-closed, authored reference
preserved. Under the spec obligation (honor exactly, or refuse by name), refusal is correct until
exact projection can wire this shape; the fixture comment marks exact wiring as the eventual goal
(a capability follow-up, not a correctness defect). What remains wrong is process, not content:
the recapture was silent, leaving manifest, lock, and design contradicting the tree.

Prior auto-memory already recorded `deep_cross_scope` as a stale-baseline class needing an owner.

## Finding 3 — the design's stated escape shape does not reproduce; the real escape is sharper

Behavior matrix at `C_base` (licensed runs):

| Authored shape | Result | Evidence |
|---|---|---|
| `picked = cells#(2).mass`, `cells : Cell[3]` (design's stencil shape) | REFUSED — `SI_OCCURRENCE_AMBIGUOUS` ("3 concrete occurrences") + `SI_OCCURRENCE_MISSING` cascade | [verified] |
| `picked = cells#(2).mass * 1.0` (any operator) | REFUSED — `SI_INDEXED_SOURCE_UNSUPPORTED` (correct code) | [agent] |
| `picked = cells#(1).mass`, `Cell[1]` | zero-diagnostic graph, silently `cells[0].mass` | [agent] |
| `picked = cells#(2).mass`, `Cell[1]` — index out of range | **zero-diagnostic graph, silently `cells[0].mass`** | [verified — `diagnostics: []`] |

**Mechanism** (inference, strongly supported by the diagnostics themselves): a bare feature-chain
initializer is not treated as an expression — the refusal text calls `picked` a "typed alias". An
alias skips the expression preflight (where the indexed-source check lives) and resolves through
containment-address instantiation, which drops the index segment. Three occurrences → "ambiguous"
refusal under the wrong name; exactly one occurrence → binds occurrence 0 regardless of the
authored index, including out of range. Operator-wrapped forms become real expressions, hit the
preflight, and refuse correctly.

Consequences:

1. The plan's Phase 1 stencil (`Cell[3]` shape) goes red for the wrong reason — an ambiguity
   refusal, which the plan itself rejects as the proof point. The recorded red must be the
   bare-chain / singular-slot shape, sharpest as the out-of-range case.
2. Plural indexed shapes are refused *incidentally* by the occurrence layer as
   `SI_OCCURRENCE_AMBIGUOUS`, not deliberately as `SI_INDEXED_SOURCE_UNSUPPORTED`. Once the
   pre-graph inventory lands (Phases 2-3), those shapes should refuse as indexed-unsupported
   *before* occurrence resolution — a diagnostic transition the design must state explicitly
   (inventory-vs-occurrence ordering, plus a row in `verification/expected-transitions.md`) or
   Phase 4's reconciliation gate will flag it as an unlisted difference.

## What survives, what needs amendment

Unaffected: the approved mechanism — closed `ExactReferenceUse | IndexedReferenceUse` variants,
one inspection operation, inventory-before-consumer, D8 diagnostic ownership, the artifact chain,
all of D1-D4. The out-of-range collapse strengthens the case for it.

Needs amendment (docs only, no code):

1. design.md "Current code facts" — the escape trigger description.
2. Plan Phase 1 stencil — fixture shape and recorded-red definition.
3. Base authority — lock/manifest re-derived against `C_base` with the recapture recorded as an
   owner-ruled transition, or a re-root at `43edf9bd`.
4. Inventory-vs-occurrence ordering and the `AMBIGUOUS → INDEXED_SOURCE_UNSUPPORTED` transition.
5. Closed fixture inventory counts (14 graph / 23 refused; `deep_cross_scope_probe` as refusal).

## Disposition

Per the plan's rollback rule ("any changed locked input … returns the item to design") and the
owner-reserved gate ("stop-rule trips halt to owner"), the run is halted pending owner rulings:

1. **Base authority:** return to design / re-root at `43edf9bd` / keep `C_base` with an explicitly
   recorded transition and re-derived lock. [AGENT recommendation: keep `C_base` with the explicit
   transition — contingent on ruling 2 — rather than discard the evidence-boundary work to
   reinstate a baseline now shown mis-wired.]
2. **`deep_cross_scope` flip:** intended tightening or regression. [AGENT recommendation: intended
   tightening, on the caller-supplied-substitute evidence above; exact wiring of the shape becomes
   a separately-owned capability follow-up.]
3. **Correction scope:** targeted rev-7 design amendment covering the five items above + targeted
   design review + plan patch + relaunch Phase 1, vs. broader design revisit. [AGENT
   recommendation: targeted amendment; nothing found touches the approved mechanism.]

No ruling is recorded yet. Probe evidence: `/tmp/stop-parser-rev2/scratch/`. Stage log:
`/tmp/stop-parser-rev2/logs/`.
