# Spike Brief — Lifecycle Item 3: Gate B Vacuity Probe

**Stage:** spike (de-risk before spec/design — the epic mandates the proof precedes any
implementation choice)
**Epic authority:** Item 3, register row 3, in
`.project/backlog/epic_constraint_execution_lifecycle_remediation.md`.
**Required reading:** both Gate B reports —
`.project/research/20260719-103419_gate-b-independent-assessment.md` and
`../fusion-tea-stellarator-mbse-demo/.project/research/20260719-082509_gate-b-root-cause-constraint-lowering-vs-v11-bridge.md`
— plus ratified invariants 24–26 and LC-E02–LC-E04B in the lifecycle contract/spec.

## The question (answer it with constructed evidence, not argument)

Can append-only constraint extension introduce a NEW V11 violation under current semantics —
at the certified Item 2 candidate (`3700fee`, resolver unified)? Build the exact shapes from
both Gate B reports: pre-existing/unrelated V11, newly consumed, and mixed. Prove or refute.

## Ground truth you inherit (verified, do not re-derive)

- V11 fires only on calculation QNs: `_fallback_entry_points.add` has exactly one writer, in
  the calculation consumer (Item 2's I10, one-writer check reproduced twice). Constraint
  actuals resolve strictly — a constraint miss raises at terminal, it never mints a fallback
  entry point. Weigh what that already implies for extension-time V11 before building shapes.
- Item 2 preserved V11's scope precisely so THIS item can answer the widening question with
  today's semantics as the baseline.
- The Item 2 resolver's strict path refuses ambiguity contextually; check whether any
  extension path can still reach lenient minting.

## Outputs

1. A verdict: vacuous / possible (with the constructed offender), with runnable evidence kept
   under `.project/active/constraint-lifecycle-gate-b/probes/` (throwaway quality is fine;
   provenance and exact commands are not optional).
2. If vacuous: name the exact call/helper that becomes deletable and every caller.
3. If possible: characterize the introduced-violation identity (what "reject only the
   introduced violation by semantic identity" must key on).
4. The V11-widening disposition input: does extension-time behavior change if V11 ever widens
   beyond calculation QNs (Item 2 PC-3 context)?

Do NOT change production code or commit fixtures into tests/ — this is a probe. License env:
`set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`.
