# Design Review: Constraint Module, Kleene Compiler, Aggregator, and Catalog Generation

**Design:** `.project/active/constraint-generation/design.md`
**Spec:** `.project/active/constraint-generation/spec.md`
**Review File:** `.project/active/constraint-generation/design-review.md`
**Date:** 2026-07-12
**Reviewer note:** Orchestrated CONSTRAINT-EXEC run, Item 7. Fresh session; did not author the design. Verified every load-bearing claim against branch `constraint-exec-epic` code and the S2/S4 spikes — not the design's own word.

---

## Fundamental Assessment

**Sound.** The approach is right and not over-built. Item 5 already lowers assertions to `ConcreteConstraint`/`REPORT_AGGREGATOR` graph nodes and fails loud at five generation seams; Item 7 supplies the missing emission. That is a fill-the-seams job, not a new architecture. The one genuinely new abstraction — the Kleene predicate compiler — earns its place: S2 proved that raw IEEE evaluation returns a confident, diagnostic-free `False` from a `1.0/0.0` operand, so a three-valued compiler is the only thing that keeps a broken value from reading as a confident verdict. Catalog-on-graph reuses the codebase's "generation reads only the graph" invariant rather than threading `ctx`. Compile-once-per-definition (D3) de-duplicates rather than parallels. Decisions D1–D11 each name a rejected alternative with a real reason.

Two things I verified against code that the design got **right**, and which are the usual places a design of this kind goes wrong:

- **D11 is correctly scoped.** The `REPORT_AGGREGATOR` is created in a separate `if eligible:` block (`constraint_lowering.py:761`), distinct from the per-constraint `for c in eligible:` loop (`:716`). Relaxing line 761 alone emits the zero-eligible aggregator **without** letting non-eligible records produce CONSTRAINT modules — the loop stays independently gated. And byte-identity for the constraint-free corpus holds through guards the design doesn't even need D11 to touch: `pipeline_builder.py:976` skips the whole call when `concrete_constraints` is empty, and the flag defaults off. Verified.
- **B3/D2 input format matches.** Item 5 serializes `predicate_ir` via `serialize_expression` from `agentic_mbse.sysml.expression_ir` (`constraint_lowering.py:537`) — the exact serializer the compiler's `parse_expression` round-trips. No spike-vs-production IR mismatch. Verified.

So this is **Approved-with-must-fixes**, not Rework. The must-fixes are concrete gaps in *proof and test construction*, not a mis-framed item. Proceed to the dimensional review.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every spec `[HARD]` maps to a design element. The gaps are in two acceptance criteria the spec (and spec-review) made must-fixes:

- **Falsifiable exit test (spec SC-4, spec-review L3-2).** The design picks the pin mechanism (D1) but leaves the *test* under-specified, and ground truth shows the control leg is not constructible against production as written (see Must-Fix 1).
- **Compile-once / same-IR as a *checked* criterion (spec-review L3-1).** INV-2 states the property, but its wording describes a per-class check the D3 shared-function design cannot perform, and the Validation Approach never turns the Kleene semantics into compiler-level tests (Must-Fix 2, Should-Fix 3).

Capture-fidelity: the modeled-default-as-entry-point `[INHERITED]` (spec L1-1's resolved hole) is carried faithfully — INV-6 plus the Implementation Note keep the default entry-point-sourced, never baked. One soft spot: the spec's resolution of "response metadata" (L1-2) says it is **derived at generation** and **optional**; the design's catalog section (D6) never restates that, so the plan could carry it as a stored/required field. Fold the "derived, optional" force into the catalog description.

### 2. Pattern Consistency
**Assessment:** Pass

Reuses the entry-point deriver, the pipeline-yaml/registry templates, the `MultiOutput` single-field-channel idiom, and `_resolve_class_name_collisions`. New patterns (shared predicates module, `tests/execution/` lane) are forced by `[HARD]` requirements, not invented. D7's "new templates for constraint bodies, reuse for structural" is the right cut — a constraint body shares almost nothing with a calc wrapper.

### 3. Abstraction Quality
**Assessment:** Pass

The Kleene compiler is the only new machinery and it is justified. Catalog-on-graph is the correct level. No speculative generality.

### 4. Duplication Avoidance
**Assessment:** Pass

D3 exists specifically to stop the compiled predicate from multiplying with instances. One caveat for the plan: the design should relate INV-2 to the same-IR guard Item 5 **already** enforces at lowering (`constraint_lowering.py:524–536`, object-identity or serialization-equality between the profile-walked and lowered predicate). Item 7's generation-time arm is a different arm, but the plan should not re-implement or contradict the lowering-time one.

### 5. Data Structure Clarity
**Assessment:** Concerns

The evidence schemas (Appendix B) are explicit and pinned. Two clarity gaps: INV-2's wording contradicts the D3 reality (Should-Fix 3), and the design assumes catalog concrete entries carry `predicate_ir` — S4's concrete entries do **not** (`s4_lib.py:883–898` puts it only on source records). The design must state that Item 7's catalog adds it to concrete entries, or point the same-IR check at the source record.

### 6. Route Safety
**Assessment:** Concerns

The five seams flip from explicit membership guards to explicit render/skip — safe and traceable. The pin (D1) is additive (unions into exits, never removes), so it cannot mask an error. The one under-specified route is the falsifiable test's narrowing seam (Must-Fix 1): the design references "the kept test's seam" but never defines it, and no production narrowing surface exists to hang it on.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

B1–B4 are genuine reality-claims, each with a stated "if false → what fails" — not mechanism choices dressed as bets. B3 verified true against code. Decisions each name and reject an alternative. Two issues:

- **Hidden bet, unstated:** `run()` wires resolved actuals into the compiled predicate **by name**, which requires `_leaf_ref_names(predicate_ir)` ⊆ the module's `ModuleInput` `param_name`s. Item 5 sets those names from `actual.name` and `sanitize_name(formal_qn local)` (`constraint_lowering.py:548–566, 738`); the predicate's leaf names come from the same IR. They *probably* coincide, but nothing proves it, and it is the single most likely integration break. Surface it as a bet and a de-risk item (Should-Fix 4).
- **B4 needs a fact check.** B4 asserts teax scalar-persistence is "merged on the epic branch," citing memory `[[teax-scalar-persistence-fixed]]`. The S4 findings instead describe it as **uncommitted teax working-tree changes** absent from HEAD `c9e1e85`. The memory says it is fixed at teax HEAD and the fusion-tea docs citing the old finding are stale — so B4 likely holds — but the two sources disagree on the surface, and the execution lane's persistence assertion rides on it. Verify at plan time which teax state the lane runs against (Nice-to-have 5).

### 8. Reader Comprehension
**Assessment:** Pass

The Core Concept leads with the model — "a modeled assertion becomes an ordinary graph module whose verdict is data, never an exception" — before the mechanism. The compile-once/N-classes bridge is explained in plain terms. INV-2's imprecision is the one comprehension snag, folded into Should-Fix 3.

---

## Issues by Severity

### Critical (Must-fix before implementation)

- **M1 — The falsifiable exit test's control leg is not constructible against production, and the "test seam" is undefined.** [D1, spec SC-4]
- **M2 — The Kleene compiler has no committed compiler-level tests, and the `[HARD]` `-0.0` boundary normalization is new code S2 never tested at all.** [D2, spec Kleene HARDs]

### Major (Should-fix)

- **S3 — INV-2 is mis-stated for the D3 shared-function design and references a catalog field that doesn't exist.**
- **S4 — Surface the predicate-leaf-name / module-input-name reconciliation as an explicit bet and de-risk item.**

### Minor (Nice-to-have)

- **N5 — Reconcile B4's "merged" vs the S4 findings' "uncommitted"; verify the teax state the execution lane runs against.**
- **N6 — D10's execution acceptance is manual and outside CI; record each manual-run result durably so a regression isn't silently missed.**
- **N7 — D2's "port `s2_ir.compile_predicate`" understates that it is a re-author against the `expression_ir` node algebra (different node kinds/fields than the spike's pydantic `IRNode`); budget the plan for a rewrite, not a copy.**
- **N8 — D11: keep `agg_inputs` sourced from `eligible` (not `concrete`); a zero-eligible model must yield an empty-input aggregator, not a validation failure on a non-eligible record's `evaluation_channel=None`.**
- **N9 — Restore the "derived at generation, optional" force on catalog response metadata (spec L1-2 resolution).**

---

## Must-Fix Detail

### M1 — The falsifiable exit test's control leg is not constructible against production code as designed

**Why it matters.** Spec SC-4 and spec-review L3-2 both demand a *falsifying* test: a control leg where, with the ancestry mechanism off and the exit narrowed, the report channel is **absent** — proving the pin is load-bearing and not riding capture-everything incidentally. The spec-review explicitly warned against "a green-but-empty test." The design adopts the pin (good, and it rejects the generation-time ancestry assertion for the right reason) but describes the test only as "the narrowed-exit test toggles" the pin, and Non-Goals says "narrowing is exercised only by the kept test's seam" — without ever defining that seam.

**What the code shows.** `_build_exit_points` (`generation/pipeline.py:228–272`) is unconditional capture-everything: it appends every output of every module with no membership filter, no `targets` parameter, no allowlist. There is no `selected_exits` concept anywhere in `src/`. The design's `exits = selected_exits ∪ pinned_exits` invents `selected_exits`; production has no narrowing at the exit layer. The one real narrowing surface — `find_required_modules(targets, include_all=False)` (`analysis/dependency_backtracker.py:228`) — prunes *whole modules*, is never invoked by any CLI or snapshot path (both hardcode `include_all=True`), and, decisively, runs **before** `extend_graph_with_constraints` adds the aggregator (`pipeline_builder.py:976`). So it cannot exclude the report channel — the aggregator doesn't exist yet when it runs.

Consequence: with the pin off, the report is **always** captured, because capture-everything captures it. The control leg cannot drop the report using any production surface. As written, the plan has nothing concrete to build, and the risk is exactly the vacuous test the spec-review flagged.

**What to add.** Pin down the test construction: make the pin a set computed separately and unioned into `_build_exit_points`, and give the exit builder a base "selected" set the test can inject narrow (e.g. parametrize the capture-everything set, or monkeypatch it). The control leg then feeds a narrowed base that excludes the report with the pin disabled → report drops; the mechanism leg feeds the same narrowed base with the pin on → report present. State plainly that this narrowing is test-only (there is no production narrowing feature — the pin guarantees membership structurally), and show the control leg genuinely drops the report. Without that, "toggles" is not implementable.

### M2 — The Kleene compiler needs committed compiler-level tests; `-0.0` normalization is new, untested code

**Why it matters.** The Kleene compiler is the safety-critical core: a wrong truth-table cell or an un-normalized `-0.0` reads as a *confident wrong verdict*, which is the exact failure the whole feature exists to prevent. End-to-end execution tests (the bulk of the Validation Approach) exercise happy paths and won't catch a wrong propagation cell.

**What the code shows.** S2's semantic "proofs" are throwaway probe scripts (`probe3_nonfinite_kleene.py`), not a committed pytest suite. Probe3 does cover — at the compiler level — three-valued leaf, and/or/not propagation, compound propagation, negated status, and margin sign. But **boundary `-0.0 → 0.0` is not compiler-tested anywhere**: `s2_ir.py` performs no such normalization, and probe3 only *masks* signed zero with `math.isclose`. The design correctly adds the normalization (Implementation Note, `[HARD]` S2 carry-forward 3) — which means Item 7 is writing normalization code with **zero** existing test behind it, plus porting propagation logic whose only proof is an uncommitted script.

**What to add.** Commit compiler-level unit tests (assert on `compile_predicate`'s emitted-function output directly, probe3-style) for each rendered semantic: non-finite leaf → `unknown`/`indeterminate`/`margin=None`; and/or/not propagation cells; negated-polarity status; negated-inequality margin-sign flip; **boundary-zero normalization**; non-finite margin → `None`. These belong in the default offline suite (they need no simkit), so they are CI-enforceable even though the end-to-end execution lane is not.

---

## Recommendations

1. **M1:** Define the pin/narrowing test seam concretely and show the control leg drops the report; keep the "no production narrowing" honesty in Non-Goals.
2. **M2:** Add committed compiler-level Kleene unit tests, boundary-zero included, in the offline lane.
3. **S3:** Rewrite INV-2 to the data-level check the Implementation Note already describes (round-trip stability per entry + byte-agreement across a `definition_qn` before compiling once), and state that concrete entries carry `predicate_ir`. Relate it to Item 5's lowering-time same-IR guard.
4. **S4:** Add the leaf-name/input-name reconciliation to the de-risk-first list beside the two-instance case; state it as a bet.
5. Fold in the minors (N5–N9) at plan time.

---

## Resolutions

_(To be filled in as the owner/design-agent resolves each finding. Keyed by ID.)_

---

**Overall:** Approved-with-must-fixes — M1 (falsifiable exit test) and M2 (compiler-level Kleene tests) are the must-fix set; S3/S4 should-fix; N5–N9 nice-to-have. The approach, D11 scoping, and the D7/D8 skip decisions are verified sound against code.

**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent session) pointed at this review to incorporate. The reviewer does not edit the design.
