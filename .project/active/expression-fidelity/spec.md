# Spec: Expression Reconstruction Fidelity (SC-6)

**Status:** Draft
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
  names are all unchanged (they were always correct — they come from a different
  code path).
- [ ] Reference doc (doc 19) and verification-matrix rows updated; new/changed
  behavior carries REQ tags.
- [ ] agentic-mbse impact recorded (expected: the fix travels with the
  PUSH-DOWN move; no teaching/checking-surface change).

## Known Requirements

### The fix

- **[HARD]** The change lives **only** in `reconstruct_expression` and
  `reconstruct_operator_expression` (the display path). Executable expression
  text is produced by a separate function, `expression_compiler.build_expression_ast`
  (`compiled_expression` / `compilation_results`), which this item does not
  touch. This separation is the invariant that guarantees executable bodies stay
  byte-identical.
- **[HARD]** Literal branches (`LiteralInteger`, `LiteralReal`, `LiteralRational`,
  `LiteralBoolean`, `LiteralString`, `NullExpression`) SHALL dispatch **before**
  the invocation catch-all, and SHALL use `SysideAdapter.is_instance` rather than
  `type(expr_node).__name__` — consistent with `is_literal_expression`
  (`expression_utils.py:168`). Reason: every node carries a derived `.function`,
  so the catch-all must not precede literals.
- **[NEED]** Operator expressions preserve parenthesization so the displayed math
  is unambiguous — a subexpression whose grouping changes the meaning renders
  with its parens.

### Baseline regeneration & review procedure (R1/R2/R3)

The regen is large (research: 173 `LiteralRationalEvaluation` occurrences across
12 committed fixture files; verified footprint below). The spec defines the
review procedure because a mass regen can mask a real regression.

- **[HARD]** Regeneration goes through the capture scripts only, never
  hand-edited baselines (R3).
- **[HARD]** Two-tier regen, in order:
  1. `scripts/capture_extraction_snapshots.py` re-runs extraction — this is where
     the display fix manifests (the `expression_text` field). **Requires a live
     syside license.** Affects the 7 `*/extraction_snapshot.json` files that carry
     `LiteralRationalEvaluation`.
  2. `scripts/capture_pipeline_baselines.py` rebuilds `computation_graph.json` /
     `registry_init.py` **offline** from the committed snapshots — the corrected
     display text flows through. Affects the 3 `baseline_outputs/*/computation_graph.json`.
- **[HARD]** Expected change classes, and nothing else:
  - `LiteralRationalEvaluation()` (and sibling `Literal*Evaluation()`) → the
    literal's value, in `expression_text` / `raw_expression_text` and any
    docstring text derived from them.
  - Parenthesization text in the same display fields.
- **[HARD]** Executable content is untouched — reviewer confirms
  `compiled_expression`, `compilation_results`, `auto_impl_context`,
  `compilability`, pipeline YAML (`capture_baseline_yaml.py` output), and channel
  names are byte-identical. Any executable-field diff is a defect, not a display
  change — stop and investigate.
- **[HARD]** `captured_at` churn is reverted (Item 3 discipline): re-running
  `capture_extraction_snapshots.py` restamps `captured_at` on every snapshot even
  when content is identical. Commit only snapshots whose `expression_text`
  actually changed; revert the timestamp-only rewrites on the rest (the ~3
  snapshots with no `Literal*Evaluation`).
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

## Non-Goals

- Replacing the reconstructor with the expression compiler's renderer
  (`build_expression_ast`) — rejected in research: the compiler is
  Python-flavored and deliberately narrower (no FCE / chains / booleans), and
  `reconstruct_expression` also serves constraint text and the aggregation
  fallback.
- Any change to executable/compiled expressions, `compilation_results`, or
  pipeline YAML wiring.
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

`Literal*Evaluation` occurrences at HEAD (regen targets):

- Extraction snapshots (live re-capture, tier 1): `attr_expr_probe` (8),
  `catf_mfe_model` (25), `solar_battery_model` (39), `retype_model` (3),
  plus `chain_override_probe`, `alias_agg_probe`, `expression_binding_probe`,
  `issue22_model`, `unresolvable_attr_probe`, `sample_model` (1 each).
- Pipeline baselines (offline rebuild, tier 2):
  `baseline_outputs/{solar_battery (39), catf_mfe (49), attr_expr_probe (7)}/computation_graph.json`.

The exact set is confirmed at plan time; the review rule (expected change classes
only, executable content byte-identical) is what governs, not the count.

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
