# Phase 1 stop report — stop rule tripped, halted to owner

**Date:** 2026-08-17 (revision 3: base diagnosis corrected after external review; every review
claim independently re-verified by the orchestrator)
**Status:** Phase 1 NOT executed. No commits on either implementation branch. Both worktrees clean
at their pinned SHAs; `occurrence.py` byte-identical to `C_base`. Original user checkouts retain
their entry digests.

The Phase 1 implement agent verified the base, ran the retained harness (37 passed) and the D1-D4
matrix (105 passed, licensed tests confirmed live), then tripped the Global Execution Contract's
lock rule ("every locked probe/fixture hash must recompute before Phase 1") and stopped without
writing anything. The stop was correct behavior under the plan as written. The diagnosis has
changed twice as evidence deepened; this revision is the corrected record.

Provenance: **[verified]** = reproduced by the orchestrator's own commands in the clean worktree
at `C_base`. Nothing below rests on an agent's or reviewer's unchecked claim.

## Finding 1 (corrected) — the lock is intact; Revision 6's prose mis-describes its own base

**The lock itself is coherent.** All 118 hashes in `verification/probe-fixture-lock.json`
recompute exactly against the lock commit's own tree (`43edf9bd`): 0 mismatches [verified].
Against the current `C_base` tree, 2 differ — `tests/fixtures/v6_recapture_batch/batch.json` and
`verification/capture_baseline.py` — and both differences are deliberate, ledger-owned
transitions, not corruption.

**`C_base`'s implemented evidence contract handles this explicitly** [verified, from
`verification/capture_baseline.py` and `verification/expected-transitions.md` at `C_base`]:

- The frozen inventory is reconstructed **from Git at the named `P_seed` commit** (`52a03cd`, a
  child of the lock) and checked against `FROZEN_BATCH_SHA256 = bd7bf245…`
  (`capture_baseline.py:76`). The manifest's `canonical_batch` pin refers to those frozen bytes by
  construction, not to the working-tree file.
- The current batch is validated **separately** at its own pinned hash `7f926978…`
  (`validate_current_batch`, line 166).
- The transition ledger states the semantics outright: "The Phase 1 probe lock is authoritative
  only at P_seed" and the current batch "must not be presented as a current member of the frozen
  P_seed byte inventory."
- Committed tests exercise these validators (`tests/conformance/test_public_route_baselines.py`,
  `test_stop_parser_documentation_contract.py`) and passed in the agent's run.

**Chronology of the two file changes** [verified from git]:
lock `43edf9bd` → `P_seed` `52a03cd` → 4A `09fdae1` (metadata recapture: 23 snapshots rewritten,
**mechanically proven metadata-only** — `_snapshot_semantics` strips two version fields plus
`integrity.digest` and requires byte-identical structures otherwise) → `3b97c0d` "Replace
occurrence fallback elections" (the semantic change) → `38045fd` → `c22c269` (proving tests) →
`da4aa78` (batch reconciliation: exactly two record moves, `deep_cross_scope_probe` and
`plant_value_shapes`, with captured→refused validated as "the exact A2 move") → … → `C_base`.
An earlier revision of this report said "every snapshot sha was rewritten" without the
metadata-only qualification, and attributed the flip loosely to `09fdae1`; both are corrected
above.

**What is actually wrong** is design.md Revision 6's prose, which the plan inherited:

- Its "Closed fixture inventory" pins `bd7bf245…` as "that file's **current** SHA-256" with
  counts 15 graph / 22 refusals — false at the `C_base` it names as its implementation base
  (current file is `7f926978…`, 14/23).
- Its "Probe/fixture commit lock" section demands "Any changed byte invalidates the verdicts and
  returns the item to design" — a byte-identity-in-current-tree rule that its own base's
  implemented contract deliberately does not satisfy, because historical evidence, generated
  output expectations, and an evolving validator are versioned states, not immutable current
  bytes.
- The plan's recompute clause operationalized that wrong rule, and the Phase-1 pre-flight was the
  first time anyone executed it.

An earlier revision of this report called `C_base` "internally self-contradictory." That was
wrong: the contradiction is between Revision 6's prose and the tree, not inside the tree. A
residual gap does remain: no committed check verifies the `43edf9bd` lock against its *historical*
tree — the orchestrator did it by hand; the amendment should name that check.

**Consequence for the remedy: do not re-derive the lock.** Re-locking against `C_base` would
erase the provenance the lock exists to preserve. The correct rule, matching the implemented
contract: verify the lock against its own historical tree; verify current outputs through the
transition-ledger machinery.

## Finding 2 — the old `deep_cross_scope` capture was itself the forbidden defect [verified]

The fixture's Pattern B authors
`in data_point = measurement_system::station::array::sensor::core::metric_value;`, aimed at the
one concrete produced output. The pre-transition baseline graph wired that consumer not to the
concrete producer channel (which a sibling consumer, `derived_calc`, correctly received) but to
`DeepCrossScopeProducer__Core_Metric__metric_value` — a definition-scoped name surfaced as a
**caller-supplied entry-point parameter with `default_value: null`** [verified]. That is the
item's forbidden class verbatim ("never … changed into another expression through a …
caller-supplied substitute"). At `C_base` the fixture refuses with the named, fail-closed
`SI_OCCURRENCE_MISSING` diagnostic, authored reference preserved [verified].

The captured→refused change was an intended correctness tightening. Restoring the old graph would
restore the substitution defect. Exact support for the deep qualified shape can remain a
separately owned capability — and the fixture's stale comment ("Exact projection wires this input
to the one concrete core output") plus backlog ownership must be updated to say so, rather than
leaving a comment that contradicts the recorded refusal.

## Finding 3 — the real escape shape, mechanism now a verified code fact

Behavior matrix at `C_base` (licensed runs; first and fourth rows orchestrator-verified, second
and third the agent's retained probes):

| Authored shape | Result |
|---|---|
| `picked = cells#(2).mass`, `cells : Cell[3]` (design's stencil shape) | REFUSED — `SI_OCCURRENCE_AMBIGUOUS` (wrong name; incidental) |
| `picked = cells#(2).mass * 1.0` (any operator) | REFUSED — `SI_INDEXED_SOURCE_UNSUPPORTED` (correct code) |
| `picked = cells#(1).mass`, `Cell[1]` | zero-diagnostic graph, silently `cells[0].mass` |
| `picked = cells#(2).mass`, `Cell[1]` — index out of range | **zero-diagnostic graph, silently `cells[0].mass`** |

**Mechanism** [verified in source at `C_base`]: the preflight screens only calc-usage
in-direction bindings — `screen_source_readiness` iterates `usage.bindings`
(`extraction/source_evidence.py:173`), and the elaborator's binding classification serves
consumer ports the same way. A bare computed-attribute initializer never enters that population:
it becomes a typed alias (the refusal text names it as such), and alias resolution carries the
indexed fact into semantic resolution where the index has no representable role. One occurrence →
silently binds occurrence zero, any authored index, in range or not. Three occurrences → refuses
incidentally as ambiguous. Operator-wrapped forms are real expressions, enter the screen, refuse
correctly.

Consequences:

1. The plan's Phase 1 stencil (`Cell[3]`) goes red for the wrong reason. **Both** indexed cases
   belong in the red set: `Cell[1]` out-of-range proves silent rewriting; `Cell[3]` proves
   inventory refusal must precede occurrence-ambiguity — pinning the
   `SI_OCCURRENCE_AMBIGUOUS → SI_INDEXED_SOURCE_UNSUPPORTED` transition, which the ledger's A5 row
   already anticipates ("an element index is ignored → pre-graph SI_INDEXED_SOURCE_UNSUPPORTED").
2. That diagnostic transition and the inventory-vs-occurrence ordering must be stated in the
   design and ledger explicitly, or Phase 4's reconciliation gate will flag it as unlisted.

## Amendments required (docs only, no code)

1. design.md lock/inventory sections: replace the byte-identity-in-current-tree rule with the
   implemented semantics — lock verified against its historical tree (add the missing committed
   check), current outputs validated through the transition ledger; state frozen (15/22 at
   `P_seed`) vs current (14/23) counts explicitly.
2. design.md "Current code facts": correct the escape trigger to the verified
   bare-chain/typed-alias mechanism.
3. Plan Phase 1 stencil and Global Execution Contract: both indexed red cases; lock-verification
   clause rewritten per (1).
4. `deep_cross_scope`: record the owner ruling (intended tightening; never restore the old
   graph); fix the contradictory fixture comment; file exact deep qualified-output wiring as a
   separately owned capability.
5. Ledger/design: state the `AMBIGUOUS → INDEXED_SOURCE_UNSUPPORTED` transition and
   inventory-before-occurrence ordering.

## Disposition

Halted under the owner-reserved stop-rule gate. Proposed rulings (external review, orchestrator
concurs after independent verification of every claim):

1. Keep `C_base`; do not re-root.
2. Preserve the `43edf9bd` lock unchanged.
3. Verify the lock against its historical tree; verify current output through the transition
   ledger.
4. Accept `deep_cross_scope` graph→refusal as intended tightening; never restore the old graph.
5. Record exact deep qualified-output wiring as an owned capability; fix the fixture comment.
6. Use both indexed regression cases (`Cell[1]` silent-rewrite proof; `Cell[3]`
   inventory-precedes-ambiguity proof).
7. Targeted Revision 7 design amendment → targeted design review → Plan Revision 3 → relaunch
   Phase 1.

**[OWNER, 2026-08-17] Rulings 1-7 ratified: "ok ratified. Proceed. but pause AFTER Phase 1."**
Origin of the rulings remains agent-grade (external review + orchestrator verification), ratified
by owner; challenge them by re-deriving against the recorded evidence above. The run resumes with
the targeted Revision 7 amendment and pauses after Phase 1 completes.

Probe evidence: `/tmp/stop-parser-rev2/scratch/`. Stage log: `/tmp/stop-parser-rev2/logs/`.
