---
date: 2026-07-19 22:10 PDT
author: Claude
topic: "Gate B coverage-scope decision — extension-time V11 is vacuous; delete it"
tags: [decision, gate-b, v11, constraint-extension, lifecycle-item-3]
status: decided
branch: constraint-exec-epic
candidate_base: 3700fee
supersedes: lowering INV-6 (whole-extended-graph V11 recheck)
last_updated: 2026-07-19
---

# Decision: Gate B coverage scope

`[OWNER]` **Pace directive, 2026-07-19:** this decision record replaces the full spec/design pair
for Item 3. The vacuity proof is the design input; there is no design space left to explore once
the branch is selected.

## The question

Can append-only constraint extension introduce a **new** V11 coverage violation — one that
`collect_uncovered_params` does not already report on the input graph?

This matters because `extend_graph_with_constraints` ran a whole-extended-graph V11 check at its
tail. When constraints are present, that check runs at capture, where it rejects pre-existing
coverage gaps that the generation gate already owns and that a downstream consumer legitimately
fills later. The epic's branch was: if extension *can* introduce a violation, reject only the
introduced one by semantic identity; if it *cannot*, delete the check.

## The answer: it cannot `[AGENT]` (constructed evidence, ratified by owner 2026-07-19)

Established by spike, `.project/active/constraint-lifecycle-gate-b/findings.md`, at candidate
`3700fee`. The proof is a closed enumeration of every way an appended module input can satisfy
V11's predicate — not an absence of counterexamples.

V11 flags a module input when all three hold: it is `entry_point`-sourced, its QN is in
`graph.fallback_entry_points`, and that entry point is valueless. So:

1. **Only appended inputs can be new offenders.** Extension deep-copies the base modules and copies
   `fallback_entry_points` verbatim (`constraint_lowering.py:1499`). Baseline offenders are
   preserved exactly; the copy adds none.
2. **Most appended inputs are not entry-point-sourced at all.** Every report-aggregator input and
   every `MODULE_OUTPUT` constraint input is `module_output`, which the predicate never inspects.
3. **MODELED_DEFAULT mints a fresh synthetic key.** It *can* be valueless (a non-literal modeled
   default), and extension did raise when that key was forced into the fallback set. But the key is
   `{constraint_id}__{formal}`, where `constraint_id` ends in a 16-hex SHA-256 segment
   (`constraint_lowering.py:204-223`), while every fallback-set member is `{calc_eqn}__{formal}`
   minted by the single writer at `dependency_backtracker.py:603`. Colliding needs a SHA-256
   preimage.
4. **DESIGN_ATTRIBUTE cannot reach a fallback key.** Its identity is always a key of
   `design_attr_by_qn` (`producer_resolution.py:561`). Across 35 live fixture models — 60 fallback
   QNs, 846 design-attribute QNs — the intersection is empty. Both constructible collision vectors
   are blocked at extraction: two same-named members in one namespace are rejected outright (a
   renamed control isolates the duplicate name as the cause), and a design attribute whose *name*
   embeds `__` has it sanitized to `_`, so it lands in a different string than the `__`-joined
   fallback key.

A second, independent block covers the fresh-mint case: a valueless usage-owned design attribute is
not extracted into the design-attribute index at all, so a constraint actual cannot resolve to one —
strict resolution raises INV-2 instead. This does not cover the reuse case (`mint()` returns early
for an existing QN without updating its default), so the QN-collision block in (4) is the
load-bearing one.

**Consequence for the reports' shapes.** Shape A (pre-existing/unrelated) reproduces exactly as both
Gate B reports describe. Shapes B (newly consumed) and C (mixed) are not constructible from a model —
they exist only when the constraint input is hand-forged at the object layer.

## Selected branch: delete `[OWNER]`

Extension performs no V11 coverage check. Final generation owns coverage, whole-graph and strict.

Deleted at this commit, in `src/sysml_codegen/analysis/constraint_lowering.py`:

- the `collect_uncovered_params(extended)` call and its `raise _generation_error(...)` at the tail
  of `extend_graph_with_constraints`;
- the `collect_uncovered_params` name in that function's local import;
- the docstring sentence claiming the function re-runs the collector.

Deliberately unchanged:

- `collect_uncovered_params` itself — its production caller is the generation gate
  (`cli/__init__.py`, `_reconcile_params_coverage`), which LC-E04 requires whole-graph and strict.
- `_validate_channel_references` on the extended graph (LC-E03).
- Strict constraint-actual resolution (LC-E03 / INV-2). Nothing here synthesizes a constraint
  actual, textual default, or fallback entry point.
- Both `extend_graph_with_constraints` call sites — live capture
  (`orchestration/pipeline_builder.py`) and from-snapshot rebuild (`snapshot/graph_rebuild.py`).
  Changing the function body covers both.

**No replacement wrapper.** There is no differential collector, no scoped variant, no module-name
filter, and no feature flag preserving the old path. The check is gone because it had no reachable
job, and a wrapper would reintroduce the dead surface the epic's success criteria forbid.

### Rejected alternative

A before/after multiset differential (both Gate B reports' preferred repair) is not implemented.
Recorded as a decision, not an instruction: the differential's whole purpose is to distinguish
introduced offenders from baseline ones, and the enumeration above shows the introduced set is
always empty. It would be dead code with a maintenance cost and a misleading invariant.

## The V11-widening dividing line

The vacuity result is conditional, and this is the exact condition.

**The dividing line is not "V11 fires only on calculation QNs."** It is whether
`fallback_entry_points` and the design-attribute index can ever share a key.

- **Safe widening — more lenient consumers as writers.** If the aggregation consumer (or any other
  lenient consumer) also records into `fallback_entry_points`, extension-time behavior does not
  change. Those keys come from `entry_point_qualified_name` in the same `{consumer_eqn}__{key}`
  family (`producer_resolution.py:462-474`), so they remain disjoint from design-attribute QNs by
  the same argument, and remain unreachable from a constraint actual. Vacuity holds; this deletion
  stands.
- **Breaking widening — design-attribute QNs entering the fallback set.** If a design attribute can
  itself land in `fallback_entry_points`, vacuity ends immediately. The forged shape from the spike
  becomes reachable from a real model, and extension-time V11 acquires a real job for the first
  time.

**Re-open trigger.** Any change that puts a design-attribute QN into `fallback_entry_points` — or
that otherwise lets the fallback set and `design_attr_by_qn` share a key — must re-open this
decision before landing. At that point the introduced-violation identity is
`(module name, input param_name, entry-point QN)`, not the QN alone: the spike's mixed shape shows
one QN appearing as both a baseline and a new offender on different modules, which a QN-keyed
multiset difference would cancel to zero.

### Safety note: name sanitization is now load-bearing under that widening `[AGENT]`

The `__` → `_` collapse in entry-point naming is what closes the second collision vector: an
attribute named `scaler__gain` becomes QN `..._scaler_gain`, never `...__scaler__gain`. Today it is
an entry-point-naming convenience with no coverage responsibility, and nothing in this commit
depends on it — the deletion removes the only consumer that could have cared.

If the breaking widening above ever happens, that changes. The sanitization becomes the sole
structural barrier between the two QN namespaces, and it must then be stated as a V11 precondition
where it is implemented, not left as an incidental naming rule.

## Contract effect

- **LC-E02** — settled to its second branch: extension performs no V11 coverage check; final
  generation owns coverage. Recorded in
  `.project/active/constraint-execution-lifecycle-contract/spec.md`.
- **LC-E03, LC-E04** — unchanged and explicitly preserved.
- **Old lowering INV-6** (`.project/completed/20260713_constraint-lowering/design.md:294-295`) is
  superseded. Its literal first sentence required the extended graph to have zero V11 uncovered
  params; that requirement is withdrawn. Its surviving intent — that constraints do not introduce
  uncovered inputs — is now a proven property of the code rather than a runtime check.

## Kept evidence

Committed with this change:

- `tests/unit/test_constraint_graph_extension.py` — an unrelated pre-existing V11 offender does not
  block extension (the spike's Shape A), and extension mints no fallback keys of its own.
- `tests/conformance/test_gate_b_generation_gate.py` — the generation gate still fails on a
  whole-graph V11 offender that extension now lets through, and passes once it is covered.

The spike's throwaway probes stay under `probes/` as reproduction, not as tests.

## Surfaced and resolved: `shared_producer`'s stale header, not an evidence contradiction

Found while running the Gate B corpus sweep; resolved by the orchestrator (Item 2's evidence
owner) by re-deriving against Item 2's recorded reasoning, per the rule this section originally
invoked.

The in-model header of `tests/fixtures/shared_producer/model.sysml` predated Item 2's SR-A02
ruling and asserted convergence intent ("one modeled default, one group assignment") with
neither consumer reaching a terminal miss. That header was stale, and only the header: the
fixture's `PROVENANCE.md` and Item 2's `evidence.md` (SR-R23 row, PC-4) both record the
committed state as **recorded known-incomplete — two entry points, convergence NOT MET,
referred to Item 4's written-reference carry**. Item 2 never certified convergence for this
shape; there is no contradiction with its certified evidence.

Live behavior at this commit disagrees, on the calculation side only:

```
fallback: ['SharedProducer__the_rig__scaler__gain']
  EP SharedProducer__the_rig__gain           DESIGN_ATTRIBUTE  default=40.0
  EP SharedProducer__the_rig__scaler__gain   USAGE_LITERAL     default=40.0
CALCULATION ...__scaler       gain <- entry_point SharedProducer__the_rig__scaler__gain
CONSTRAINT  ...__floor_check  gain <- entry_point SharedProducer__the_rig__gain
```

The constraint resolves positively through the design-attribute tier, as documented. The calc does
not — it takes a lenient terminal miss and mints a per-consumer fallback. So the two consumers land
on **two** entry points for one design attribute, which is the outcome invariant 21 forbids and the
shape this fixture was built to prove absent.

What is and is not affected:

- **Nothing in Gate B changes.** Both entry points carry `40.0`, so V11 is clean either way
  (`collect_uncovered_params` and `collect_unwired_fallthrough` both return empty here), and the
  QNs differ, which is consistent with — not a counterexample to — the vacuity enumeration above.
- **Item 2's evidence is not in question.** The observed two-entry-point behavior is exactly the
  state `PROVENANCE.md` pins (constraint positive at the source QN; calc per-consumer lenient
  mint — the self-named binding structurally cannot feed the exact key form because extraction
  discards the written reference).

Action taken: the stale in-model header was corrected to state observed behavior and point at
this section, line count preserved so `extraction_snapshot.json` source lines do not move.
`[AGENT, orchestrator-resolved 2026-07-20]` Reconciled against Item 2's recorded reasoning:
records agree; convergence completes with Item 4's written-reference carry as already booked in
the epic.

## Source documents

- Spike findings and reproduction: `.project/active/constraint-lifecycle-gate-b/findings.md`
- Independent assessment: `.project/research/20260719-103419_gate-b-independent-assessment.md`
- Fusion root cause: `../fusion-tea-stellarator-mbse-demo/.project/research/20260719-082509_gate-b-root-cause-constraint-lowering-vs-v11-bridge.md`
- Upstream filing of fusion finding #8: `.project/active/constraint-lifecycle-gate-b/upstream-filing.md`
- Epic Item 3: `.project/backlog/epic_constraint_execution_lifecycle_remediation.md`
