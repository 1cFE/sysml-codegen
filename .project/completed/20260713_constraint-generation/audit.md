# Audit: Item 7 — Constraint Module, Kleene Compiler, Aggregator, and Catalog Generation

**Verdict:** Certify-with-notes
**Audited:** 2026-07-13
**Branch:** constraint-exec-epic
**Commit:** b14b74b (Item 7 = ac9aed1..ec33c3b)

---

## Audit-session limitation (read first)

**This session could not execute any Python.** Every interpreter invocation — `uv run
pytest`, `.venv/bin/python -c "print(2+2)"`, `/usr/bin/python3` — is refused with "requires
approval," which is unavailable in a non-interactive orchestrated run. Command-substitution
(`$(...)`) is also blocked, so the brief's license incantation cannot run as written either.
`git`, `grep`, `ls`, and file reads work; nothing that runs code does.

Consequence: **none of the eight execution-based verifications in the brief were
independently re-executed.** This audit is a rigorous *static* review — I read every seam,
every test, and the full item diff, and reasoned each mutation probe through the actual
code. Where a result depends on running (suite-green counts, mypy 76, ruff, the 3/3
execution lane), I mark it **author-reported** — taken from `plan.md`/`run-log.md`, not
re-verified here. This is stated plainly rather than papered over; see **Not checked**.

The static review is strong on its own: the mechanisms are readable, and every mutation
probe the brief names is falsifiable-by-construction in the code as written. What I cannot
do is catch a runtime defect that only appears on execution — which is exactly the class of
bug the execution lane found three of.

---

## Summary

The core of Item 7 is delivered and, by static reading, correct. The Kleene compiler
implements three-valued logic faithfully (boundary normalization, polarity, margin-sign),
the exit pin (D1) is load-bearing and falsifiably tested, the same-IR (INV-2) and leaf-name
(B5) guards are structural and name the `constraint_id`, D11 is exactly one condition, and
the three Phase-4 bug fixes are real structural corrections, not string patches. SC-1 (the
S4 slice, both truth values) has a well-formed execution test that asserts INV-3.

Two gaps hold this back from a clean Certify. **(1)** Three named spec success criteria are
deferred, not delivered: the indeterminate/negated-inline cases at execution (SC-2), the
modeled-default override changing the verdict (SC-3), and the Break-the-YAML kept test. The
deferral is honestly surfaced in the plan, but these are first-class success criteria, and
two of them (SC-3, Break-the-YAML) have no test at any level. **(2)** The three Phase-4 bug
fixes have no regression test in any automatically-run lane — only the manual, non-CI
execution lane catches them, so a revert of any fix stays green in CI.

---

## Findings

### Plan completion

All five phases are marked `[x]` and the code backing each is present. One phase-4 checkbox
is honestly left `[ ]` — the deferred five execution cases (plan.md:240). Verified:

- **Phase 1** — `generation/predicate_compiler.py` present; `tests/unit/test_predicate_compiler.py`
  has 11 cells, one per rendered semantic (compiler code read below). ✓ (static)
- **Phase 2** — exit pin present (`pipeline.py:232-304`), falsifiable test present
  (`test_exit_pin.py`). ✓ (static)
- **Phase 3** — six seams filled, catalog + guards present, faildloud suite flipped. ✓ (static)
- **Phase 4** — 3 execution tests present; **5 of the brief's/spec's cases deferred** (finding below).
- **Phase 5** — determinism test present; byte-identity/suite/mypy/ruff **author-reported green**.

### Spec conformance

Criterion-by-criterion. "static" = verified by reading; "author-reported" = from run-log,
not re-executed here.

- **SC-1 (S4 slice under real simkit, both truth values, persisted).** Test present and
  correctly shaped: `test_s4_slice_both_truth_values` asserts area 12.0 / cost 3000.0,
  satisfied +2000 / violated −500, the violated run "must NOT raise" (INV-3) with ordinary
  outputs intact (`test_constraint_execution.py:128,135-136`), and the report persisted to
  `constraint_report.json` (lines 138-146). **Author-reported PASS** (run-log 3/3). ✓ static
  structure, author-reported execution.
- **SC-2 (cases S4 did not exercise).** zero-assertion aggregator ✓ (test present, author-
  reported pass); multi-instance expansion ✓ (present, author-reported pass); **indeterminate
  (non-finite) point — DEFERRED at execution**; **negated + inline assertions — DEFERRED at
  execution.** The *semantics* of indeterminate and negated are proven at the compiler-unit
  level (`test_nonfinite_leaf_is_indeterminate`, `test_negated_polarity_...`,
  `test_negated_inequality_margin_sign_flip`), so only the end-to-end integration is missing
  — but SC-2 as written ("all execute correctly") is **not fully met**.
- **SC-3 (modeled-default formal overridable at runtime, override changes the verdict).**
  **Not met — no test at any level.** The generation-half mechanism exists (the compiler
  turns feature refs into args, never baking a default as a constant — INV-6 by construction;
  bug-fix-3 makes the default flow through the entry point), but there is no test that
  overriding the defaulted formal flips the verdict. `_override_budget` in the S4 test
  overrides *budget* to flip satisfied→violated — that is the two-truth-values path, not a
  defaulted-formal override. SC-3 is unproven.
- **SC-4 (exit-ancestry falsifiable, control drops / mechanism keeps).** **Met (static).**
  `test_pin_keeps_report_under_narrowed_exit` narrows `selected_channels={"area"}` (excludes
  the report), asserts control (`pin=False`) drops it and mechanism (`pin=True`) keeps it.
  Mutation probe (brief #2) confirmed by reasoning: the report channel reaches the mechanism
  leg's output *only* via the pin clause `(pin_report_channels and channel in pinned)`
  (`pipeline.py:286-288`); deleting the pin ⇒ `constraint_report` absent ⇒ the mechanism
  assertion goes RED. The pin is genuinely load-bearing.
- **Break-the-YAML (kept test that surfaces a missing result as an executor failure).**
  **Not met — DEFERRED.** No such test exists (grep across `tests/`/`src/` finds none). The
  *mechanism* is in place — the aggregator has an exact schema, one required field per
  eligible constraint, `extra="forbid"` (INV-4), so a missing/rewired evaluation is a
  `ValidationError` — but the spec explicitly requires a *kept end-to-end test through the
  executor*, and S4 only proved it at constructor level. That obligation is unmet.
- **Suite green; constraint-free corpus byte-identical (INV-7).** Logic is sound (static):
  `ComputationGraph.constraint_catalog` is `Optional` + `exclude=True` (models.py), so a
  constraint-free graph serializes no field; `lower_constraints_enabled` defaults `False` on
  the shared path, so existing corpora never touch the new code. **Author-reported green**
  (Phase-5 baseline suites, 2233 passed).
- **Handoff gate to Item 8 (deterministic `constraint_id`s + catalog ordering, INV-8).**
  Assembly orders by `concrete` (already `constraint_id`-sorted), fingerprint is
  sha256 of canonical JSON (`constraint_catalog.py:99-108`). Determinism test present
  (`test_constraint_catalog_determinism.py`). Correctly framed as an Item-8 handoff, not an
  Item-7 exit gate. ✓ static; author-reported pass.

**Tagged requirements (Known Requirements):** the `[HARD]` Kleene semantics, the compile-once
`[HARD]`, the same-IR `[HARD]`, the `[HARD]` boundary-zero normalization, the `[HARD]`
never-raise-on-verdict (INV-3, asserted in the S4 test), the `[HARD]` exact-schema aggregator,
the `[HARD]` zero-assertion aggregator (D11), and the `[NEED]` polarity/margin rules are all
present in code and unit-tested. The `[NEED]` Break-the-YAML requirement is the one unmet
tagged requirement.

**Non-goals respected:** no production exit-*narrowing* feature (only the test seam); no
snapshot/flag change (Item 8); no new expression capability (equality/feature-chain still
raise `PredicateCompileError`). ✓

### Design conformance

Implementation follows the design closely.

- **D1** exit pin — as designed, production defaults a no-op (`selected_channels is None`
  short-circuits). ✓ One benign deviation: `pinned` iterates *all* aggregator outputs, not
  `outputs[0]` (plan.md:339-343 notes it) — harmless.
- **D2/D3** compiler home + compile-once — `compile_shared_predicates` emits one function
  per `predicate_definition_key` (= `usage_qualified_name`), runtime block once via
  `function_source_only`. INV-1 holds (offline + live tests assert `count("def
  constraint_pred_") == 1`). ✓
- **D5** evidence schema (S4 split: `actual_value: Optional[bool]` + `observed`) — matches
  Appendix B. ✓
- **D6** catalog embedded on graph, fingerprint once, `predicate_ir` added to each concrete
  entry (INV-2 arm b needs it). ✓
- **D8** three render / three skip — offline integration test asserts no handwritten/backlog/
  test entries for constraint kinds. ✓
- **D9** naming from `module_type` placeholder scheme, collisions handled. ✓
- **D11** one-condition relaxation — diff confirms exactly the `if eligible:` removal; the
  block de-indent is mechanical (finding note below on the file's other changes). ✓

INV-2 mutation probe (brief #5) confirmed by reasoning: `assert_same_ir`
(`constraint_catalog.py:111-145`) raises `CodeGenerationError` naming the `constraint_id` on
arm (a) round-trip failure and arm (b) cross-entry divergence; it is called from
`compile_shared_predicates` (modules.py:117) *before* the single compile. Mutating one
entry's `predicate_ir` post-lowering trips arm (a) (a space breaks canonical round-trip) or
arm (b) (divergence from a shared-definition sibling) — either way generation fails naming
the id.

### Code integrity

No slop or failure-honesty problems in the new code. The guards raise loudly rather than
falling back (B5, INV-2, the "needs catalog to render" checks in `generate_teax_module`).
The compiler's `PredicateCompileError` on blocked constructs is correct fail-loud behavior.
Two findings, both about test coverage rather than production code:

**Finding 1 — Three Phase-4 bug fixes have no regression test in any CI/offline lane
(medium).** `analysis/constraint_lowering.py` and `parameter_groups.py`. The bracket-strip
(`_constraint_module_type`, lowering.py:~624), the `sanitize_name(c.constraint_id)`
aggregator field (lowering.py:786), and `design_attribute_default_value`
(parameter_groups.py:504) are each correct and structural. But: the offline integration test
(`test_constraint_generation_integration.py`) hand-builds a bracket-free
`owner_instance_path` and a clean `param_name="C1"`, so it exercises none of them; the
`@requires_license` multi-instance live test counts modules/predicates but never
`ast.parse`s the three generated constraint files (a bracket regression produces a valid
generation and only fails at *import*); wi014 is single-instance and its test doesn't load
JSON (bug-3 bites only at pydantic load). The only lane that catches all three is the
**manual, non-CI execution lane**. **Effect:** revert any of the three fixes and the entire
offline suite stays green. Brief verification #3 explicitly required each fix to "have a
regression test." **What should change:** add an offline (or generation-level `@requires_license`)
test that `ast.parse`s the multi-instance constraint module files (catches bugs 1-2) and one
that validates the generated JSON input template against the schema for a constraint-only
design attribute (catches bug 3) — neither needs simkit.

**Finding 2 — Three spec success criteria deferred without a test (medium).** SC-2
(indeterminate + negated/inline at execution), SC-3 (modeled-default override flips verdict),
and Break-the-YAML are deferred (plan.md:240, 407-411). The deferral is surfaced honestly per
capture-fidelity §4 — not hidden — but SC-3 and Break-the-YAML have **zero** coverage at any
level, and SC-2's execution half is unrun. These are named success criteria, not optional
companions. **What should change:** the owner decides whether these are Item-7-blocking; if
so, each is a same-shaped extension of the now-working execution harness (plan's own
assessment) plus, for Break-the-YAML, a kept test that rewires an evaluation and asserts the
executor raises.

**Note (not a finding):** `constraint_lowering.py` (an Item 5 file) received four changes this
item — D11 plus the three Phase-4 fixes — all four surfaced in run-log.md/plan.md rather than
folded silently. This is correct capture-fidelity practice; brief #6's "D11 = exactly one
condition" refers to the D11 logic change specifically, which holds.

---

## Certification

**Checked (static, this session):**
- Kleene compiler source (`predicate_compiler.py`) — three-valued `_and/_or/_not`, `_cmp`
  non-finite→None, `_norm0` boundary, polarity/margin sign, unit strip, equality/feature-chain
  blocked. Independently traced three brief-named cells (leaf-unknown on NaN via `_fin`;
  false-and-unknown=false via `_and`; `-0.0→0.0` via `_norm0`) against the emitted source.
- Exit pin (`pipeline.py`) + falsifiable test; mutation probe reasoned to RED.
- Same-IR guard (`constraint_catalog.py`) + B5 assertion (`modules.py`); both name the id.
- Full item diff of `constraint_lowering.py` — D11 one-condition + three structural fixes.
- Seam wiring (modules/pipeline/registry render; test-gen/stencil skip) via the offline
  integration test's assertions and the diff.
- Byte-identity mechanism (`exclude=True` + flag default) and determinism/fingerprint logic.
- Execution-lane test structure — INV-3 (violated completes, outputs intact) asserted.

**Author-reported (NOT re-executed — python blocked this session):** full suite 2233 passed /
4 skipped / 3 deselected; mypy 76-error baseline; ruff clean; execution lane 3/3 pass;
byte-identity baseline suites green. All taken from `plan.md` Phase-5 and `run-log.md`, which
are internally consistent and honest about what ran.

**Not checked:**
- **No independent execution of anything** — the eight execution-based brief verifications
  (Kleene suite run, exit mutation *run*, bug-fix regression *runs*, the S4 slice + gap cases
  under real simkit, the INV-2/B5 *runs*, gates) were reasoned statically, not run. A runtime
  defect invisible to reading is outside this pass.
- The teax-state precondition (scalar persistence at teax HEAD `7560d65`) — orchestrator-pinned
  and re-verified in run-log.md from the teax-accessible env; **not re-verified here** (teax is
  outside this sandbox and code execution is blocked).
- Template *text* correctness beyond the offline integration test's `ast.parse` — I read the
  render functions, not every `.jinja2` line-by-line.
- Whether "inline assertion" (SC-2) has any coverage at all — no execution test; not separately
  traced at the unit level.

---

## Recommendation

The mechanism at the heart of Item 7 — a modeled assertion running as an ordinary module with
its verdict as data — is built and, by every static check, correct; SC-1 and SC-4 are
delivered with real tests. **Certify-with-notes**, contingent on the owner accepting the two
gaps as either (a) Item-7-acceptable deferrals to be tracked, or (b) blocking, in which case:
close the three Phase-4 fixes with offline regression tests (Finding 1) and add execution/kept
tests for SC-2's remaining cases, SC-3, and Break-the-YAML (Finding 2). A re-audit that can
actually run the suite should confirm the author-reported gates before any epic-level
certification.

ARTIFACT: .project/active/constraint-generation/audit.md

---

## Addendum: cures verified + gates executed by orchestrator (2026-07-13)

Phase 6 (audit cures) landed all four requirements: SC-2 execution tests (indeterminate,
negated/inline), SC-3 modeled-default override flip, break-the-YAML executor failure, and the
three Phase-4 CI regression pins (session-verified RED on isolated revert). Orchestrator
re-ran the gates with the license env: full suite **2236 passed / 0 failed**, regression pins
3/3, mypy **76 = baseline**, ruff clean.

**Final verdict: Certify** (upgraded from Certify-with-notes; both notes cured and gates
independently executed).
