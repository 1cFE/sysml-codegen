# Design Review: Calc-Seam Cutover — Retire ExpressionAST

**Design:** `.project/active/expression-ast-cutover/design.md`
**Spec:** `.project/active/expression-ast-cutover/spec.md`
**Review File:** `.project/active/expression-ast-cutover/design-review.md`
**Date:** 2026-07-13
**Reviewer note:** Orchestrated CONSTRAINT-EXEC run, non-interactive. Verified against code in
`sysml-codegen`. The landed agentic-mbse `extract_expression_ir` (commit 3ad890e) could **not**
be read from this sandbox (agentic-mbse is outside the allowed working dir) — findings that turn
on the landed extractor's node kinds / literal typing are flagged as *Stage-0-verified, not
reviewer-verified* where that matters.

---

## Fundamental Assessment

**Sound.** The approach is the right one and is well-justified against the codebase:

- One thin renderer over the shared `ExpressionIR`, sibling-in-role to Item 7's
  `predicate_compiler.py` (D1), is the correct shape. The design's rejection of a shared
  dual-mode `ir_python.py` is verified: `compile_expression` renders `str(value)` + `inputs.`/bare,
  `predicate_compiler._compile_numeric` renders `repr(value)` + bare — a merged module would fork
  through every branch and cross the extraction/generation layer boundary. Two renderers over one
  tree is correct.
- Reuse-the-extractor (D2) over a codegen-side re-derivation is the right call — a second
  syside→IR path is exactly the drift this epic removes.
- The staged, per-function byte-identity gate with the F4 comparand lesson baked in (INV-1) is the
  right risk posture for a "no semantics change" migration.

No over-abstraction, no invented pattern, no wrong-problem. The must-fixes below are
**completeness and precision gaps in the plan-facing detail**, not foundational flaws. Proceed to
detailed review.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every spec success-criterion has a design element, and the scope correction (aggregation walking
is out — it runs on agentic-mbse's `shared_aggregation`, never touches `ExpressionAST`) is carried
faithfully with provenance. The `[INFERRED]` "shape does not change" is treated as a held
constraint (INV-3) — legitimate, since the spec records it "Confirmed with the orchestrator."

The gap is the spec's SC **"Full suite green ... at each stage."** The design's deletion scope
(Stage 4 / INV-4) is bounded to `src/` and the *new* parity test. It does not account for the
existing test bodies that directly exercise the deleted symbols (Finding M1). As written, Stage 4
cannot meet its own green-suite gate.

### 2. Pattern Consistency
**Assessment:** Pass

Sibling-to-`predicate_compiler.py` placement, `CompilationError` kept (D3) so existing
`except CompilationError` → `MANUAL_REQUIRED` clauses behave identically, grep gate mirrors prior
retirement gates. `_sanitize_name`'s intentional divergence from the shared sanitizer is preserved
(the renderer must keep calling this one, not the shared version — noted in code comment at
`expression_compiler.py:167`). Consistent with the codebase.

### 3. Abstraction Quality
**Assessment:** Pass

`render_calc_expression(ir, input_names, member_names)` + `collect_calc_refs(...)` is the minimal
surface. Classification-at-render-time from supplied name sets (not baked into the tree) matches
the concept requirement and `probe4.compat_render`. No excess.

### 4. Duplication Avoidance
**Assessment:** Pass

The design explicitly declines to merge with the predicate renderer and justifies it against the
actual divergences (`str`/`repr`, `inputs.`/bare, Kleene-vs-arithmetic top layer). Verified in code.

### 5. Data Structure Clarity
**Assessment:** Concerns

`CompilationResult` / `CalcDefCompilationResult` shapes are held constant (INV-3), correct. But two
field-level details that decide byte-identity are under-specified:

- **Literal type preservation** (Finding M2): `python_expression` is built with `str(value)`; the
  int-vs-float distinction is load-bearing and the design does not pin how the renderer preserves it.
- **`intermediate_refs` composition** (Finding M3): the seam's `member_names` set is unstated;
  the serialized ref lists depend on it.

### 6. Route Safety
**Assessment:** Pass

The error path is routed correctly: renderer raises `CompilationError` (kept symbol) on unresolved
ref / unparseable output, so caller fallbacks are unchanged (D3). No new exception type, no
catch-clause drift. Confirmed the corpus never routes a calc output down the renderer-swapped error
branch (see M-note on `unsupported_reason`), so the error route is effectively dead for the gate —
safe, but state it.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

B1–B3 are genuine reality-claims each with a stated "if false." B1 (re-prove byte-identity with the
*landed* extractor, not the spike's) is honest and correctly refuses to inherit the S2 proof. D1–D4
each name the rejected alternative and why. Good.

**Hidden bet surfaced — B4 (unstated): the landed `extract_expression_ir` preserves the raw
integer-vs-float literal distinction (a `value_type` the renderer can key on).** The old path
renders `str(raw_syside_value)`, so an integer literal `4` → `"4"` and a rational `4.0` → `"4.0"`.
If the landed IR normalizes numerics to Python `float` (a plausible choice for a `Real`-typed IR),
`str(value)` yields `"4.0"` and the int form is **unrecoverable from the IR**. The corpus contains
integer-literal calc outputs (`return_styles`: `out y = a * 2`, `out y = x * 4`), so Stage-0 parity
*will* catch this — but the design rests on B4 without stating it, and if B4 is false the fix is a
cross-repo extractor change, not a renderer tweak. This is the same class as R1/R2 and belongs
next to plan-task-0. (See M2.)

### 8. Reader Comprehension
**Assessment:** Pass

The Core Concept states the model plainly (one neutral tree; calc side is the last holdout; a thin
compat renderer reproduces the old dialect byte-for-byte) before the mechanism. The old-vs-new
divergence table and the ASCII producer diagram give a tired reader the shape at a glance. Terms
are anchored. No comprehension blocker.

---

## Issues by Severity

### Critical
None. The foundation is sound; nothing here warrants Rework.

### Major (must-fix before `/_my_plan` produces the plan)

- **M1 — Stage-4 deletion breaks ~240+ existing test references; unscoped.** Deleting
  `ExpressionAST` / `build_expression_ast` / `compile_expression` (plus `ExpressionNodeType`,
  `PYTHON_OPERATOR_MAP`, `_collect_refs`) breaks seven test files that import or exercise them:
  `tests/unit/test_expression_compiler.py` (**237** references),
  `tests/conformance/test_expression_compiler.py`, `tests/conformance/test_ast_dispatch_invariant.py`,
  `tests/conformance/test_data_models.py`, `tests/unit/test_computed_attribute_extraction.py`,
  `tests/integration/test_hierarchy_e2e.py`, `tests/helpers/impl_execution.py`.
  `test_ast_dispatch_invariant.py` is worse than an import break: it hard-codes `build_expression_ast`
  as an audited FCE-before-OE dispatch site **and asserts "exactly 6 audited dispatch functions"**
  (REQ-AST-04) — deleting the function invalidates the count guardrail and the raw-node dispatch
  invariant moves to agentic-mbse's extractor, so the invariant must be re-derived, not just deleted.
  *Why must-fix:* the spec's "full suite green at each stage" is unmeetable otherwise, and Stage 4
  is more than "delete symbols + grep gate" — it must retire/rewrite these tests and ensure the
  renderer inherits equivalent unit coverage. Add this to the Stage-4 order and the Component
  Overview deletion list.

- **M2 — Renderer literal rule under-specified; this is the actual byte-identity failure mode.**
  The design's only literal note is `str(value)` "(not `repr`)". It must specify: render integer
  literals as `str(int(value))` and reals as `str(float(value))`, **keyed on the IR node's
  `value_type`**, reproducing the raw syside type the old path passed through unmodified. Corpus has
  both (`a * 2`, `x * 4` ints; `p * 2.0`, `1.0e9` floats), so Stage-0 gates it — but the design
  should specify the rule, and elevate B4 (extractor preserves int/float) beside R1 at plan-task-0.
  If the landed IR discards the distinction, byte-identity is unrecoverable renderer-side → cross-repo
  fix. *Why must-fix:* a missed rule here is a mid-implement Stage-0 red with an unclear owner.

- **M3 — Seam `member_names` composition unstated.** `build_expression_ast` classifies
  input→`INPUT_REF`, output→`INTERMEDIATE_REF`, member→`INTERMEDIATE_REF`
  (`expression_compiler.py:388-393`). For byte-identical `intermediate_refs` (serialized, so
  byte-identity matters), the renderer's `member_names` at the `compile_calc_def` seam must be
  **`output_names ∪ all_member_names`**. The design states the empty-set for computed attributes
  (correct) but leaves the seam composition implicit. Stage-1's full-`CalcDefCompilationResult`
  comparand would catch a mistake, but the design is the place to pin it. *Why must-fix:* cheap to
  state, and getting it wrong (e.g. passing only `all_member_names`, trusting it contains declared
  outputs) costs an implement cycle.

### Minor (nice-to-have)

- **N1 — Stage-0 name-set provenance.** State that the `in`/`out`/`mem` fed to both paths in the
  Stage-0 parity assertion must mirror what `compile_calc_def` derives (from
  `input_attributes` / `output_attributes` / `all_member_names`), **not** re-derived probe4-style by
  walking `owned_elements` by direction. Probe4's ad-hoc derivation is fine for a spike; a green
  Stage-0 built on non-production name sets proves less than it looks. Stage-1 backstops this, but
  say it.
- **N2 — `unsupported_reason` premise, state it.** Verified: across every committed snapshot the
  only serialized `unsupported_reason` is `"no expression AST"` (4×) — an **orchestration-level**
  reason from `compile_calc_def` (`:573`), untouched by the renderer swap. No renderer-path reason
  (`"Cannot compile unsupported node…"`, `"unsupported operator"`, `"unresolved reference"`,
  `"feature chain…"`) is serialized anywhere in the corpus, and the computed-attribute path *logs*
  its reason without persisting it (`computed_attribute_extractor.py:308-316`). So the renderer need
  **not** reproduce the old error-string text for the corpus gate. The design should state this
  premise explicitly (it currently implies full-`CalcDefCompilationResult` equality without noting
  the error branch is dead for the corpus), so a reader knows byte-identity does not hinge on
  error-message parity.
- **N3 — Stale comment.** `hierarchy_resolver.py:54` references `PYTHON_OPERATOR_MAP` in a comment;
  it survives deletion (comment, not code, and out of the grep-gate's 3-symbol scope) but should be
  cleaned when the symbol goes.
- **N4 — Rebaseline.** `base_commit 043fdb8` predates Item 8 completion — Item 8 Phase 5
  (`df5ed97`, "corpus re-capture at v3 — item complete") is already committed on this branch. R4's
  "Item 8 lands concurrently" is now "already landed," which de-risks the coupling; rebaseline the
  design/plan onto current HEAD and treat the post-Item-8 corpus as fixed, not moving.
- **N5 — Stage-0 must include an integer-literal *calc-def* output.** `return_styles` provides two
  (`a * 2`, `x * 4`); confirm the Stage-0 iterator includes it so M2's rule is gated at Stage 0, not
  only at Stage 2's computed-attribute golden.

---

## Probe Findings (per brief)

1. **Stage-0 parity harness** — defined at the right level (old vs new over the corpus, both paths
   present) but two precision gaps: name-set provenance (N1) and the fact that probe4 also drove a
   synthetic SCRATCH model for unary/power/n-ary/nested shapes. Those shapes are now covered by
   richer committed fixtures (`-(a + b)`, `a ** b ** c`, 7-ary `p_coils + …`, nested parens), so
   fixture-only iteration is adequate today — but say "fixtures, verified to cover probe4's SCRATCH
   shapes," not just "fixtures."
2. **Dialect completeness** — verified against `expression_compiler.py`: `^`/`**`→`" ** "` (both map
   in `PYTHON_OPERATOR_MAP`; `d38_caret` covers `^`), unary→`(-x)`, `[`-unit strip to operand 0,
   left-fold parens at every step, `inputs.`/bare classification — all reproduced by
   `probe4.compat_render`. Computed-attribute dialect (`:300-306`) is the **same** functions with
   `output_names=∅, all_member_names=None`, so identical dialect with an empty member set — renderer
   with `member_names=∅` matches exactly. The one under-specified rule is literal int-vs-float (M2).
3. **Snapshot replay (Stage 3)** — reasoning stated and **correct**: `compilation_results` carry
   compiled strings; once Stage-1's re-capture confirms the section is byte-identical (timestamp-churn
   reverted), `--from-snapshot` replays identical strings and packages stay byte-identical.
   `test_factory_purity` + the from-snapshot package diff are the proving tests. No new test needed.
   Pass.
4. **Deletion completeness (Stage 4)** — `src/` sweep is clean: `build_expression_ast` /
   `compile_expression` used only in the two consumers; no stray `ExpressionAST` / `_collect_refs`;
   the snapshot serializer nullifies **raw-syside** fields via `_AST_FIELDS`
   (`serializer.py:42-49`) and never references the `ExpressionAST` dataclass, so no serializer
   coupling. **But the test tree is not swept** — that is M1.
5. **Rollback** — clean. Stages 1–2 revert by commit (old path present until Stage 4); Stage 4 is
   the only hard-to-reverse step, acknowledged. The timestamp-churn revert keeps re-captured
   snapshots byte-identical, so no snapshot artifact entangles with Item 8's v3 landing. No false
   coupling. Pass.

---

## Recommendations

1. **M1:** Extend Stage 4 to retire/rewrite the seven test files (esp. the 237-ref
   `test_expression_compiler.py` and the REQ-AST-04 count guardrail in `test_ast_dispatch_invariant.py`)
   and transfer equivalent unit coverage to the renderer. Add to the deletion list and Stage-4 order.
2. **M2:** Specify the literal rule (int vs float, keyed on IR `value_type`) and elevate the
   "extractor preserves int/float" bet (B4) to plan-task-0 beside the entry-point probe.
3. **M3:** State `member_names = output_names ∪ all_member_names` at the `compile_calc_def` seam.
4. Fold in N1–N5 as plan notes.

---

## Resolutions

_Filled during Stage 4 (finalize-with-owner). One entry per resolved issue._

---

**Overall:** Approved-with-must-fixes.
**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent
session) pointed at this review to fold M1–M3 (and N1–N5) into `design.md` before `/_my_plan`. The
reviewer does not edit the design.
