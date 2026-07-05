# Spec: Expression Reconstruction Fidelity (SC-6)

**Status:** Implementation In Progress (Phases 1, 2, 4 complete; Phase 3 regen pending — see plan)
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** MEDIUM
**Branch:** upstream-findings-epic
**Epic:** UPSTREAM-FINDINGS — Item 6

---

## Problem

Generated docstrings and implementation stencils show corrupted math. A calc
whose executable body is correct displays its formula with every literal
replaced by the string `LiteralRationalEvaluation()` and with grouping parens
dropped. The research reproduction shows it plainly: the model expression

```
capacity * rate + capacity * (rate / 2.0) * 3.0
```

renders in the docstring as

```
capacity * rate / LiteralRationalEvaluation() * LiteralRationalEvaluation()
```

— literals gone, `(rate / 2.0)` grouping lost. The executable body next to it is
correct, so this is a display-only defect, but it makes generated code
unreadable and untrustworthy exactly where a human reads the math.

Two independent causes, both in `expression_utils.py`
(`extraction/expression_utils.py`):

1. **Branch ordering.** `reconstruct_expression` checks the invocation
   catch-all (`hasattr(expr_node, "function")`, line 57) *before* the literal
   branches (lines 64-77). Every SysIDE expression node carries a derived KerML
   `.function`, so every literal hits the catch-all first and stringifies to
   `LiteralRationalEvaluation()`. The literal branches are dead code as written.
   The register blamed node-type *naming*; research corrected this — the literal
   branch works if reached (`is_instance(node, "LiteralRational")` is `True` on
   live nodes). Ordering alone is the bug.

2. **No parenthesization.** `reconstruct_operator_expression` emits
   `f"{left}{op_str}{right}"` with no parens, so model-level grouping that
   changes meaning is lost.

Why now: this item must land **before the PUSH-DOWN epic moves
`expression_utils.py` wholesale into agentic-mbse**, so the pushed-down code is
born correct and the mass baseline churn is reviewed once, here.

## Success Criteria

- [ ] The research repro (`capacity * rate + capacity * (rate / 2.0) * 3.0`)
  renders faithfully in docstrings and stencils — every literal as its numeric
  value, grouping that changes meaning preserved — proven by a regression test
  against a **real parsed AST**, not mocks.
- [ ] Zero `LiteralRationalEvaluation` (and any sibling `Literal*Evaluation`)
  strings remain in regenerated extraction snapshots and pipeline baselines.
- [ ] Executable content is byte-identical after regen: `compiled_expression`,
  `compilation_results`, `auto_impl_context`, pipeline YAML wiring, and channel
  names are all unchanged — verified by the explicit byte-identity gate on
  `compiled_expression` / `auto_impl_context` in the regen review (structural for
  CalcDef modules, corpus-scoped-and-checked for aggregation modules; see the
  invariant under Known Requirements).
- [ ] Reference doc (doc 19) and verification-matrix rows updated; new/changed
  behavior carries REQ tags.
- [ ] agentic-mbse impact recorded (expected: the fix travels with the
  PUSH-DOWN move; no teaching/checking-surface change).

## Known Requirements

### The fix

- **[HARD]** The change lives **only** in `reconstruct_expression` and
  `reconstruct_operator_expression` (the display path). Its effect on executable
  fields is guaranteed by **two different mechanisms**, and the review must not
  conflate them:
  - **CalcDef modules — structural.** Their executable text comes from a separate
    function, `expression_compiler.build_expression_ast` (→ `compiled_expression`
    / `compilation_results`), which this item does not touch. Reconstructor
    changes cannot reach it.
  - **Aggregation modules — corpus-scoped, NOT structural.** `reconstruct_expression`
    output *does* reach executable fields on the aggregation path:
    `_walk_aggregation_ast` (`hierarchy_resolver.py:433`) delegates literal leaves
    to `reconstruct_expression`, its return becomes
    `AggregationExpressionData.transformed_expression` (`hierarchy_resolver.py:485`),
    which becomes `compiled_expression` and then `auto_impl_context`
    (`graph_builder.py:1344-1361`). Executable output stays byte-identical only
    because, for the current corpus: (1) no committed baseline carries
    `Literal*Evaluation` in any executable field — every occurrence is in
    `calc_expressions`; (2) the literal-delegation line is unreachable anyway —
    `_walk_aggregation_ast` has the *same* literal-after-invocation ordering
    (catch-all `hierarchy_resolver.py:372`, literal branch `:431`), so an
    aggregation literal hits the invocation catch-all first and is never compiled;
    (3) aggregation chain heads resolve to bare `FeatureReferenceExpression` names,
    which neither the literal fix nor the paren fix touches. A future
    literal-bearing aggregation fixture could break this — so the guarantee is a
    **checked gate**, not a structural fact.
- **[HARD]** The baseline-regen review is that gate: it SHALL explicitly diff the
  `compiled_expression` and `auto_impl_context` fields and require **byte-identity**.
  Any change to either is a **hard stop** — no commit, investigate, report.
- **[HARD]** All literal-and-null branches SHALL dispatch **before** the
  invocation catch-all, and SHALL use `SysideAdapter.is_instance` rather than
  `type(expr_node).__name__`. Reason: every node carries a derived `.function`, so
  the catch-all must not precede literals. The full branch set to detect via
  `is_instance`:
  - The five KerML literals: `LiteralInteger`, `LiteralRational`, `LiteralReal`,
    `LiteralBoolean`, `LiteralString`.
  - `LiteralInfinity` (KerML `*`).
  - `NullExpression`.
- **[HARD]** `is_literal_expression` (`expression_utils.py:168`) currently covers
  only the five `Literal*` types — **not** `NullExpression` and **not**
  `LiteralInfinity`. So "consistent with `is_literal_expression`" cannot be taken
  literally for those two: the dispatch detects them via their own `is_instance`
  checks. To keep the two functions consistent, this change also aligns
  `is_literal_expression` to include `LiteralInfinity` (and, per design's call,
  `NullExpression`) — one line each. Design picks the exact rendered text for
  `NullExpression` (`"null"`) and `LiteralInfinity` (`"*"` or `"inf"`).
- **[NEED]** Operator expressions preserve parenthesization so the displayed math
  is unambiguous — a subexpression whose grouping changes the meaning renders
  with its parens.

### Baseline regeneration & review procedure (R1/R2/R3)

The regen is large — **~225 `Literal*Evaluation` occurrences across 14 committed
fixture files** at current HEAD (222 `LiteralRationalEvaluation` + 3
`LiteralIntegerEvaluation`; verified footprint below). (The research-era "173
across 12" predates the Items 2/3/4 regens.) The spec defines the review
procedure because a mass regen can mask a real regression.

- **[HARD]** Regeneration goes through the capture scripts only, never
  hand-edited baselines (R3).
- **[HARD]** Two-tier regen, in order:
  1. `scripts/capture_extraction_snapshots.py` re-runs extraction — this is where
     the display fix manifests (the `expression_text` / `calc_expressions` fields).
     **Requires a live syside license.** Affects the **11**
     `*/extraction_snapshot.json` files that carry `Literal*Evaluation` (enumerated
     in the footprint below).
  2. `scripts/capture_pipeline_baselines.py` rebuilds `computation_graph.json` /
     `registry_init.py` **offline** from the committed snapshots — the corrected
     display text flows through. Affects the 3 `baseline_outputs/*/computation_graph.json`.
- **[HARD]** Expected change classes — display fields only:
  - `LiteralRationalEvaluation()` (and sibling `Literal*Evaluation()`) → the
    literal's value.
  - Parenthesization text.

  These appear in `expression_text`, `raw_expression_text`, **`calc_expressions`**,
  and any docstring text derived from them. `calc_expressions` is the field where
  **every** `Literal*Evaluation` occurrence in the three `computation_graph.json`
  baselines actually lives (it is built from `reconstruct_expression`,
  `extractor.py:233`), so it is the field that visibly churns in the pipeline
  baselines — it must be on this list or the reviewer will wrongly flag its diff.
  (Confirmed: the string lives in `expression_text` and `calc_expressions`;
  `expression_ast` is `null`, unaffected.)
- **[HARD]** Executable content is untouched — reviewer confirms
  `compiled_expression`, `compilation_results`, `auto_impl_context`,
  `compilability`, pipeline YAML (`capture_baseline_yaml.py` output), and channel
  names are byte-identical. Any executable-field diff is a defect, not a display
  change — **hard stop**, investigate, report.
- **[HARD]** Unexpected change class rule: any diff that is **neither** an
  enumerated display class **nor** in the executable set above is a **hard stop** —
  no commit, investigate. If found benign, add it to the enumerated display
  classes (and note why) before committing; do not silently wave it through.
- **[HARD]** `captured_at` churn is reverted (Item 3 discipline): re-running
  `capture_extraction_snapshots.py` restamps `captured_at` on every snapshot even
  when content is identical. Commit only snapshots whose `expression_text`
  actually changed; revert the timestamp-only rewrites on the rest (of the 12
  committed extraction snapshots, 11 carry `Literal*Evaluation` and change; the
  1 that does not is a timestamp-only churn to revert).
- **[HARD]** One item's regen at a time (R3) — Item 6 regens in isolation; do not
  fold in another item's baseline changes.

### Testing & docs

- **[HARD]** The regression test parses a **real** fixture AST (no mocks). Mock
  nodes lack the derived `.function` that caused the bug, which is exactly why
  1,500+ conformance tests missed it.
- **[INFERRED]** Requirements land in the **REQ-AST family** in doc 19
  (`19-ast-dispatch-invariant.md`), which already owns dispatch ordering and
  reconstruction (REQ-AST-03, REQ-AST-07). The fix **revises REQ-AST-03** —
  its stated canonical ordering "FCE, OE, FRE, Literal" is itself part of the
  defect, since it places literals after the invocation catch-all. New REQ-AST
  IDs (≥ 08) cover literal-before-invocation dispatch and parenthesization.
  Verification-matrix rows added for each.
- **[HARD]** Revising REQ-AST-03 makes `_walk_aggregation_ast`
  (`hierarchy_resolver.py:365-435`) a **documented known-violator**: it has the
  same literal-after-invocation ordering (catch-all `:372`, literal branch `:431`)
  and the same latent bug — an aggregation literal is mis-dispatched to the
  invocation branch and marked unsupported, so its `reconstruct_expression`
  delegation at `:433` is dead. This item does **not** fix that site (it touches an
  executable aggregation path — see Non-Goals), but the doc must not claim
  conformance the site lacks. Doc 19 SHALL note `_walk_aggregation_ast` as a known
  deviation from REQ-AST-03, and the latent literal-in-aggregation bug SHALL be
  filed as a `BACKLOG.md` follow-up. (`build_expression_ast` is unaffected — it has
  an explicit "unknown" fallback, no invocation catch-all, so its literals already
  reach their branch.)

## Non-Goals

- Replacing the reconstructor with the expression compiler's renderer
  (`build_expression_ast`) — rejected in research: the compiler is
  Python-flavored and deliberately narrower (no FCE / chains / booleans), and
  `reconstruct_expression` also serves constraint text and the aggregation
  fallback.
- Any change to executable/compiled expressions, `compilation_results`, or
  pipeline YAML wiring.
- Fixing `_walk_aggregation_ast`'s twin literal-after-invocation ordering bug
  (`hierarchy_resolver.py`) — it touches an executable aggregation path and is out
  of this display-only item. Documented as a known REQ-AST-03 deviation and filed
  as a backlog follow-up (see Known Requirements).
- FCE reconstruction — already correct (REQ-AST-07); not in scope.
- Moving `expression_utils.py` into agentic-mbse — that is the PUSH-DOWN epic.
  This item only guarantees it lands first so the moved code is already correct.
- Constraint execution (separate deferred epic).

## Open Questions / Deferred to design

- **Parenthesization algorithm.** Precedence-aware (emit parens only where
  grouping changes meaning) vs. always-paren. The epic recommends precedence-aware
  to minimize baseline text churn — always-paren would rewrite every operator
  `expression_text`. Confirm at design, and pin the precedence/associativity
  table (the `OPERATOR_MAP` operator set: `and`, `or`, comparisons, `+ - * /`,
  `**`, `^`, `implies`, unary `-`/`not`). **[INFERRED]** default: precedence-aware.
- **Real-AST fixture choice.** Whether the regression test parses a new
  purpose-built fixture or reuses an existing expression-bearing fixture (e.g.
  `expression_binding_probe`, `attr_expr_probe`) parsed live. Must at minimum
  exercise the repro shape (nested operators + literals + a meaning-changing
  grouping). Design decides; note the test needs a live license to parse unless
  driven from a committed snapshot that already carries the corrected text.
- **REQ-AST-03 revision vs. new ID.** Whether to edit REQ-AST-03's ordering
  in place or supersede it with a new ID. Design/doc-owner call.
- **License-window fallback.** The zero-`LiteralRationalEvaluation` criterion and
  the docstring-render criterion both depend on live re-capture of extraction
  snapshots (license expires 2026-08-06). If no live license is available in the
  implement window, the code fix + real-AST regression test can still land, but
  snapshot/baseline regen blocks — the item is not "done" until regen runs.
  Design/plan should state how far the item proceeds offline and flag the license
  dependency to the orchestrator rather than hand-editing snapshots.

## Verified baseline footprint

`Literal*Evaluation` at HEAD: ~225 occurrences across 14 files (verified by grep).
Regen targets, by tier:

- **Tier 1 — extraction snapshots (live re-capture), 11 files:** `attr_expr_probe`,
  `catf_mfe_model`, `solar_battery_model`, `retype_model`, `return_styles`
  (added by Item 3), `chain_override_probe`, `alias_agg_probe`,
  `expression_binding_probe`, `issue22_model`, `unresolvable_attr_probe`,
  `sample_model` — each `.../extraction_snapshot.json`.
- **Tier 2 — pipeline baselines (offline rebuild), 3 files:**
  `baseline_outputs/{solar_battery, catf_mfe, attr_expr_probe}/computation_graph.json`.

Exact per-file occurrence counts are confirmed at plan time (they shift with any
prior item's regen). The review rule — expected change classes only, executable
fields byte-identical — governs, not the count.

---

## agentic-mbse impact

- **PUSH-DOWN handoff (primary):** `expression_utils.py` moves wholesale to
  agentic-mbse in the P1 PUSH-DOWN backlog item (design ready, not implemented).
  Record in that design that this fix travels with the move — landing Item 6
  first means the pushed-down `reconstruct_expression` is already correct and the
  baseline churn is reviewed once, here.
- **Teaching/checking surfaces:** expected **none**. This is an internal display
  fix; it does not change what models should look like, so no MODELING_GUIDE /
  sysml-conventions stencil change and no new validator check. Record "none" for
  Item 12's accumulated impact list (R2).

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 6; R1/R2/R3)
- **Required Reading / Research:** `.project/research/20260705_upstream-findings-deep-research.md`
  (SC-6, authoritative on the corrected root cause — branch ordering, not naming)
- **Findings register:** `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md`
- **Contract:** `docs/architecture/modeling-assumptions.md`
- **Reference doc (owner):** `docs/architecture/reference/19-ast-dispatch-invariant.md`
  (REQ-AST family)
- **Code:** `src/sysml_codegen/extraction/expression_utils.py`
  (`reconstruct_expression`, `reconstruct_operator_expression`,
  `is_literal_expression`)
- **Design:** `.project/active/expression-fidelity/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
