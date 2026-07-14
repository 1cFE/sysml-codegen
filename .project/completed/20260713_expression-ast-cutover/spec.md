# Spec: Calc-Seam Cutover — Retire ExpressionAST

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-13
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic

---

## Problem

`sysml-codegen` carries two semantic expression trees. `ExpressionIR` (agentic-mbse, landed
Item 2) is the neutral, serializable tree the constraint predicates already compile from
(Item 7). `ExpressionAST` (`extraction/expression_compiler.py:56`) is the older calc-side
tree: arithmetic-only, references pre-classified as input/intermediate at construction,
n-ary left-folded at build, never serialized. S2 proved (probe 4) that a ~40-line codegen
compat renderer over `ExpressionIR` reproduces today's `ExpressionAST` compiler output
**byte-identically** for every calc expression in the corpus. Keeping both trees is the
"silent second semantic representation" the concept forbids: two code paths that must be
kept in lock-step by hand, one of them redundant.

This item executes S2's extract-and-migrate decision on the calc side: move the calc
consumers onto `ExpressionIR` + the compat renderer, then delete `ExpressionAST`. It is a
representation migration under byte-identity gates — no expression semantics change.

The migration is last-of-the-codegen-track by design: predicates ship first (Item 7), so the
staged-decision ordering S2 set is already satisfied when this item runs.

## Success Criteria

- [x] The calc-compiler seam produces its Python expression strings through the
      `ExpressionIR` + compat-renderer path; `build_expression_ast` + `compile_expression`
      are no longer called to compile calc outputs. *(Audit: static-verified — seam + computed-attr
      both flipped; old functions deleted.)*
- [x] Every corpus calc expression renders **byte-identically** through the IR path before
      each consumer flips (the S2 proof kept as a test until `ExpressionAST` is deleted).
      *(Audit: static-verified — live parity ran Phases 0–3, frozen to D4 golden; live pass = Probe P1/P4.)*
- [ ] Generated packages are byte-identical after **each** staged step (not only at the end),
      timestamps excepted, against the post-Item-8 corpus baseline.
- [x] `ExpressionAST`, `build_expression_ast`, and `compile_expression` are deleted; a grep
      gate proves those three symbols no longer appear in `sysml-codegen/src`.
      *(Audit: static-verified — independent whole-family grep of src clean; grep gate present.)*
- [ ] The serialized calc-compilation section round-trips byte-identically after the seam
      flips, and `generate --from-snapshot` packages stay byte-identical; baselines
      re-captured only if the capture shape changes, as a reviewed diff.
- [ ] Full suite green; `mypy src/` and `ruff check src/` clean.

## Known Requirements

The three consumers below are the ones that actually depend on `ExpressionAST`. Each migrates
as its own gated step, and each step's parity gate compares against the **exact function it
replaces**, not a downstream proxy (the F4-cutover comparand lesson — see
`memory: f4-cutover-fallback-divergence`).

- **[INHERITED]** (epic Item 13 §1) **Seam cutover.** A codegen-side compat renderer over
  `ExpressionIR` — classifying references as input vs intermediate **at render time from the
  supplied name sets**, not pre-classified into the tree — replaces `build_expression_ast` +
  `compile_expression` at the calc-compiler seam (`compile_calc_def`,
  `orchestration/pipeline_builder.py:920`). Comparand: the exact string `compile_expression`
  produces today. Gate: byte-identical calc output for the entire corpus. Keep S2's
  byte-identity proof as a test until `ExpressionAST` is deleted.
- **[INHERITED]** (epic Item 13 §2) **Computed attributes.** `computed_attribute_extractor.py`
  (lines ~300–306) calls `build_expression_ast` + `compile_expression` directly. Migrate it
  onto the same renderer as its own gated step. Comparand: the exact compiled string that
  path produces today.
- **[INHERITED]** (epic Item 13 §2) **Snapshot `compilation_results` replay.** This consumes
  the *result* of compilation, not the tree: `snapshot/loader.py` and `serializer.py` carry
  `CalcDefCompilationResult` / `CompilationResult` (compiled Python strings + refs).
  Requirement: after the seam flips, the serialized calc-compilation section round-trips
  byte-identically, `--from-snapshot` packages stay byte-identical, and re-capture happens
  only if the capture shape changes, as a reviewed diff.
- **[INFERRED]** The `CompilationResult` / `CalcDefCompilationResult` data model does **not**
  change in this item. Output shape is held constant; this is representation migration on the
  producing side, so the serialized section and every downstream `CompilationResult` consumer
  (`graph_builder.py`, `resolution/models.py`) see the same shape they see today. (Confirmed
  with the orchestrator.)
- **[INHERITED]** (epic Item 13 §4) **Delete-and-gate.** When the last calc consumer moves,
  delete `ExpressionAST` and its two functions. A grep gate asserts no silent replacement
  remains — scoped to the symbols `ExpressionAST`, `build_expression_ast`,
  `compile_expression` in `sysml-codegen/src`.
- **[INHERITED]** (S2 result; epic §3) **Comparand discipline.** Each staged parity gate
  compares against the exact function it replaces, captured before the flip — never a
  downstream proxy artifact. A green whole-package diff is necessary but not sufficient; the
  per-function comparand is the primary gate.
- **[INHERITED]** (epic byte-identity discipline; `memory: byte-identity-captured-at-churn`)
  **Baseline is the post-Item-8 corpus.** Item 8 (Snapshot v3) is landing concurrently and
  re-captures the corpus. "Byte-identical" here means against the post-Item-8-certified
  corpus. Run the established timestamp-only churn check (diff → revert timestamp-only
  changes) so only real diffs surface.

## Non-Goals

- **New expression capability.** No new operators, invocation, feature chains, or unit
  conversion. This is representation migration, not a semantics change. `ExpressionIR` already
  carries nodes for constructs `ExpressionAST` blocks; those stay blocked here.
- **Predicate compilation.** Predicates already compile from `ExpressionIR` via Item 7. Not
  re-touched.
- **Aggregation-walking convergence.** Aggregation walking
  (`extraction/hierarchy_resolver.py`) renders through `agentic_mbse.sysml.aggregation`
  (`shared_aggregation`) — a neutral tree **owned by agentic-mbse** from the PUSH-DOWN epic.
  It never imports `ExpressionAST`, so it neither blocks nor belongs to this retirement.
  Out of scope: folding `shared_aggregation` into `ExpressionIR` is real future work, but it
  is agentic-mbse-owned and cross-repo, exceeding this sysml-codegen item's stated repo and
  budget. Recorded as a candidate coordinated-pair item in Related Artifacts below.

## Open Questions / Deferred to design

- **Compat-renderer home.** Whether the codegen-side compat renderer lives in
  `expression_compiler.py` (as `ExpressionAST` retires around it), a new module, or beside
  Item 7's predicate compiler. Mechanism — defer to design.
- **Staging order and commit granularity.** The three consumers can flip in any order that
  keeps each step's gate green; the exact sequence and how many commits carry per-step
  byte-identity evidence is a design/plan call. S2 measured convergence cost at the
  seam only, so treat computed attributes and snapshot replay as independently gated.
- **Undeclared-intermediate + topological-sort handling.** `compile_calc_def` owns dependency
  graphing, undeclared-intermediate discovery, and topological sort around the per-output
  compile. The renderer swap must preserve that orchestration; whether any of it moves is a
  design detail, not a scope change.

---

## Scope Correction (surfaced, not silent)

Epic Item 13 §2 lists **aggregation walking** as an in-scope staged consumer to migrate. A
code trace for this spec shows that path runs on agentic-mbse's owned `shared_aggregation`
neutral tree and **never consumes `ExpressionAST`** — so it neither blocks nor belongs to
retiring `ExpressionAST`. The epic's consumer list carried S2's pre-verification assumption
that aggregation walking sat on the same tree as the calc compiler; the trace corrects that.

**Decision (orchestrator, agent-grade, 2026-07-13):** Item 13 = Option A — retire
`ExpressionAST` only (the three real consumers), scoped to sysml-codegen, grep gate on the
three symbols. The `shared_aggregation` → `ExpressionIR` convergence is deferred as future
work. This is a recorded correction of the epic Item 13 scope text, surfaced here rather than
resolved silently (capture-fidelity Law 4).

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution.md` (Item 13)
- **Required Reading:** concept Architectural Bets (predicate/IR bullet — extract-and-migrate,
  staged); S2 result and carry-forward (1)
  (`.project/active/spike-expression-tree-parity/findings.md`); `memory:
  f4-cutover-fallback-divergence` (comparand discipline).
- **Upstream (certified):** Item 2 — `ExpressionIR` + S2's compat-rendering proof
  (`.project/reference/s2-spike/` probe4/probe5 reproduce today's calc compiler output
  byte-identically). Item 7 — predicates already compile from IR (staged-decision ordering
  satisfied).
- **Concurrent dependency:** Item 8 (Snapshot v3) is landing snapshot-facts to this tree
  concurrently. Item 13's byte-identity baseline is the **post-Item-8** corpus; Item 13's
  implement sequences **after** Item 8 certifies (orchestrator-enforced).
- **Candidate follow-on item (decision record, not an instruction):** Converge
  `shared_aggregation` (agentic-mbse) and its sysml-codegen renderer onto `ExpressionIR`, so
  a single neutral semantic tree remains. Coordinated-pair (agentic-mbse + sysml-codegen),
  out of Item 13's scope. Raised by the aggregation-walking trace above.
- **Design:** `.project/active/expression-ast-cutover/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
