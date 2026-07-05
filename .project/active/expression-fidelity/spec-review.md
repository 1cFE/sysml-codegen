# Spec Review: Expression Reconstruction Fidelity (SC-6)

**Spec:** `.project/active/expression-fidelity/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/expression-fidelity/spec-review.md`
**Date:** 2026-07-05

---

## Reality Check

**Sound, with one mis-stated invariant.** The spec is about the right work item, the two root causes are correctly identified (branch ordering + missing parens, per the corrected research), and the fix direction is right. I traced every code-facing claim. The core mechanics hold: the literal branch works if reached; the reorder carries no opposite-bug risk; the two-tier regen matches the capture scripts as they exist now; numbering and doc scoping are correct.

The one substantive problem is that the spec's headline safety invariant — "executable text comes from a separate function (`build_expression_ast`), so reconstructor changes can't touch executable bodies" — is **false for the aggregation path**. It's true for the calc path only. Executable output is still unchanged in practice, but for a different, corpus-scoped reason than the spec states. That, plus stale/contradictory footprint counts and an under-specified baseline-review procedure, is a Revise, not a Rework.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (highest stakes):** The `[HARD]` safety invariant is wrong as stated. The spec says executable expression text is produced *only* by `expression_compiler.build_expression_ast`, and that "this separation is the invariant that guarantees executable bodies stay byte-identical" (spec lines 74–79). That is true for **CalcDef** modules but **false for aggregation** modules. The aggregation executable path routes `reconstruct_expression` output straight into the executable fields:

- `_walk_aggregation_ast` calls `reconstruct_expression(node)` for literal leaves (`hierarchy_resolver.py:433`) and reaches it for chain heads via `extract_feature_chain_name` → `reconstruct_expression` (`expression_utils.py:145`).
- Its return becomes `AggregationExpressionData.transformed_expression` (`hierarchy_resolver.py:485`).
- That becomes `compiled_expression` (`graph_builder.py:1344–1348`) and then `auto_impl_context` (`graph_builder.py:1358–1361`) — the exact two fields the success criteria require to be byte-identical.

So `reconstruct_expression` is **not** cleanly separated from executable output. The reason executable bodies actually stay byte-identical is empirical and corpus-scoped, not structural:
  1. No committed baseline carries `Literal*Evaluation` in any executable field — every occurrence is in `calc_expressions` (verified across all three `computation_graph.json`).
  2. The literal-delegation line (`hierarchy_resolver.py:433`) is currently unreachable for literals anyway — `_walk_aggregation_ast` has the **same** literal-after-invocation ordering (catch-all at `:372`, literal branch at `:431`), so a literal in an aggregation hits the invocation catch-all first, sets `has_unsupported`, and is never compiled (see L3-1).
  3. Aggregation chain heads resolve to bare `FeatureReferenceExpression` names, which neither the literal fix nor the paren fix touches.

Net: for the current corpus the byte-identical guarantee holds, but the *stated mechanism* for it is unsound. This matters because the invariant is load-bearing — it's what tells the reviewer they can trust "executable unchanged" without re-deriving it. **Recommend:** rewrite the invariant to state the real guarantee (reconstructor output reaches executable fields only via the aggregation path; in that path the changed branches are unreachable or resolve to FRE names for this corpus; the byte-identical baseline check on `compiled_expression`/`auto_impl_context` is the actual gate, not a structural separation). Keep the byte-identical check — it's the correct backstop — but stop resting it on a false premise.

**L1-2 · Direct claim:** The footprint counts are stale and internally contradictory.
- Line 92 says "173 `LiteralRationalEvaluation` occurrences across 12 committed fixture files." Actual at HEAD: **~225** occurrences (222 `LiteralRationalEvaluation` + 3 `LiteralIntegerEvaluation`) across **14** files. The 173/12 figure is the research-era count, pre Items 2/3/4 regen.
- Line 102 (`[HARD]`, tier-1) says the fix "Affects the **7** `*/extraction_snapshot.json` files." But the Verified-footprint section (lines 179–182) lists **10** named extraction snapshots, and the actual count is **11**. The "7" contradicts the spec's own footprint and is wrong.

The spec hedges at line 186 ("the exact set is confirmed at plan time… the review rule is what governs, not the count"), which softens the impact — but a `[HARD]` requirement hard-coding "7 files" is a defect the plan agent will trip over. Fix the numbers or replace them with "confirm the set at plan time" rather than a wrong literal.

**L1-3 · Direct claim:** The Verified-footprint list omits `return_styles/extraction_snapshot.json` (3 occurrences), a fixture added by Item 3. It's a tier-1 extraction snapshot carrying `Literal*Evaluation` and will regenerate like the others. This is the concrete instance of L1-2's staleness — the footprint was written against the pre-Item-3 corpus.

### Lens 2 — Problem & Approach

**L2-1 · Rewrite request:** The `[HARD]` "expected change classes" (lines 106–110) name only `expression_text` / `raw_expression_text` (and derived docstring text). But **every** `Literal*Evaluation` occurrence in the three `computation_graph.json` baselines lives in `calc_expressions`, and `calc_expressions` is built from `reconstruct_expression` (`extractor.py:233`). So `calc_expressions` is the field that will visibly churn in the pipeline baselines, and the spec's enumeration doesn't list it. A reviewer applying "expected classes, and nothing else" literally could flag the `calc_expressions` diff as unexpected. Add `calc_expressions` to the expected display-change classes (and confirm the snapshot fields — I verified the string lives in `expression_text` and `calc_expressions`; `expression_ast` is `null`, not affected).

**L2-2 · Question to the user:** What is the rule when an **unexpected** change class appears? The procedure defines two outcomes only: expected display classes (accept) and any executable-field diff (defect → stop). It's silent on the middle case — a non-executable field the enumeration didn't anticipate (the `calc_expressions` case in L2-1 is exactly this). Should the rule be: "any diff outside the enumerated display classes AND outside the executable set halts for investigation and, if benign, gets added to the enumeration"? Without that, the procedure either over-rejects benign display churn or silently waves through something it didn't foresee. **Recommend** the spec state the default explicitly.

### Lens 3 — Pipeline Risk

**L3-1 · Question to the user:** Revising REQ-AST-03's canonical ordering has a blast radius the spec doesn't address. REQ-AST-03 asserts *all* dispatch sites follow "FCE, OE, FRE, Invocation, Literal," and the spec revises that to put literals before the invocation catch-all. But `reconstruct_expression` is not the only site with literal-after-invocation ordering — `_walk_aggregation_ast` has the identical structure (invocation catch-all at `hierarchy_resolver.py:372`, literal branch at `:431`). After the doc revision, that site becomes a documented-invariant violator, and it carries the same latent bug: a literal operand in an aggregation is mis-dispatched to the invocation branch and marked unsupported (its `reconstruct_expression` delegation at `:433` is dead code today). The spec scopes the aggregation reconstructor out (Non-Goals), which is a fine call for *this* item — but the doc revision shouldn't silently leave a second site contradicting the newly-canonical ordering. **Decide:** either (a) note `_walk_aggregation_ast` in the doc as a known deviation and file the latent literal-in-aggregation bug as a follow-up, or (b) scope the REQ-AST-03 wording so it doesn't claim conformance the aggregation site no longer has. `build_expression_ast` is unaffected — it has no invocation catch-all (explicit "unknown" fallback), so its literals already reach their branch.

**L3-2 · Direct claim / question:** The literal-detection totality has two small gaps.
- The `[HARD]` requirement says use `is_instance` "consistent with `is_literal_expression`" (line 84) but also lists `NullExpression` among the branches to move (line 81). `is_literal_expression` (`expression_utils.py:168–180`) covers the five `Literal*` types and **not** `NullExpression`. So "consistent with `is_literal_expression`" and "include NullExpression" can't both be taken literally — design must detect `NullExpression` via its own `is_instance` check. Minor, but the requirement is internally inconsistent as written.
- `LiteralInfinity` (KerML `*`) is covered by neither `is_literal_expression` nor the spec's branch list. If it can appear in a value expression it would hit the catch-all and stringify as `LiteralInfinityEvaluation()`. Confirm it can't reach these expressions, or add it to the branch set. Low risk, worth a line.

*(Reassurance, not a finding: the reorder carries no opposite-bug risk. Literal `is_instance` checks are false for `OperatorExpression`/`FRE`/`FCE`, so moving literals ahead of the invocation catch-all cannot capture an operator expression by mistake. The scrutiny item #2 concern does not materialize.)*

### Lens 4 — Hygiene

None material. The spec is well-structured and readable.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request (folds into L1-1):** The safety invariant is the one place the prose actively misleads: it reads as a clean structural guarantee ("separate function → can't touch executable bodies") when the real guarantee is empirical and has an aggregation-path caveat. Because a reviewer will lean on this exact sentence to accept "executable unchanged," it needs to say what's actually true. Handled by the L1-1 rewrite.

---

## Engagement Summary

**Overall take:** The work item is sound and the fix direction is right — the bug, its two causes, and the two-tier regen all check out against HEAD. The blocker for approval is that the spec's headline safety invariant is mis-stated: `reconstruct_expression` *does* feed the executable aggregation path (`compiled_expression`/`auto_impl_context`), so the "separate function" guarantee is false for aggregations. Executable output stays byte-identical anyway, but for a corpus-scoped empirical reason, and the spec should say so rather than rest on a premise a future fixture could break. Secondary: the footprint counts are stale/contradictory and the baseline-review procedure under-specifies which display fields change and what to do with a surprise.

**Here's what I need you to weigh in on:**

1. **[L1-1, L5-1]** The safety invariant is wrong for the aggregation path. Confirm you want it rewritten to the real guarantee (corpus-scoped: reconstructor reaches executable fields only via aggregation, where the changed branches are unreachable/FRE-only today; the byte-identical `compiled_expression`/`auto_impl_context` check is the actual gate). No code gate is needed — it's empirically safe — but the *claim* must be corrected.
2. **[L3-1]** Revising REQ-AST-03 leaves `_walk_aggregation_ast` (same literal-after-invocation ordering) as a documented-invariant violator with a latent twin bug. Decide: note it as a known deviation + file the follow-up, or narrow the doc-revision wording. In-scope-for-this-item stays "no," but the doc mustn't lie.
3. **[L2-1, L2-2]** The expected-change-class list omits `calc_expressions` — the field where all baseline occurrences actually live. Add it, and add a rule for what happens when an unexpected (non-executable) change class shows up, so the review procedure isn't ambiguous.
4. **[L1-2, L1-3]** Fix the stale counts: "173 / 12 files" is now ~225 / 14; "7 extraction snapshots" contradicts the spec's own 10-file list (actual 11); `return_styles` is missing from the footprint. Either correct the numbers or replace the literals with "confirmed at plan time."
5. **[L3-2]** `NullExpression` vs "consistent with `is_literal_expression`" is internally inconsistent (the helper doesn't cover NullExpression), and `LiteralInfinity` is unhandled by anything. Small, but tighten the requirement.

---

## Resolutions

*(To be filled in as the user resolves each finding. This section is what the spec agent reads to incorporate the review.)*

---

**Verdict:** Revise
**Next Steps:** Once resolutions are recorded here, re-run `/_my_spec` (or return to the spec-agent session) and point it at this review to incorporate. The reviewer does not edit the spec.
