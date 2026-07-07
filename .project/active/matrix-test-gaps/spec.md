# Spec: Matrix Test-Gap Authoring (REQ-DM-08, REQ-RES-05, REQ-RES-08)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-07
**Complexity:** MEDIUM
**Branch:** truth-debt-epic
**Epic:** TRUTH-DEBT, Item 3 (SC-C)

---

## Problem

Three verification-matrix rows are marked `UNTESTED` with an argument, not a test. The
behavior each claims is real, but no honest test pins it, so the matrix is trusting an
argument where it should be trusting a test. This item retires that debt by authoring one
independently-anchored pinning test per row and flipping the three rows `UNTESTED → PASS` in
the same change (R1).

The three rows, and what is actually true at HEAD (R4 re-verified 2026-07-07 — Item 1 landed,
Items 2/4 are at plan stage, not implemented):

- **REQ-DM-08** — "Name fields with semantic format constraints SHALL use NewType wrappers,
  not bare `str`." The wrappers exist and are real NewTypes (`core/identifier_types.py`), and
  they **are** carried on the `OutputRegistry` surface. But the **model fields** the row's text
  points at are still bare `str` — `EntryPoint.qualified_name`, `InputSource.qualified_name` /
  `producer_channel`, `ModuleOutput.channel_name` (`resolution/models.py`). The reference doc
  already admits this in prose (`09-data-models.md:104`: "the model fields listed are still
  annotated `str` … REQ-DM-08 is open"). So a test that faithfully asserts the row's *current*
  text fails at HEAD — the row is UNTESTED precisely because the fields are deliberately not
  typed yet. See the R4 finding and its ruling below.

- **REQ-RES-05** — "The orchestrator SHALL be a linear sequence: classify → build modules →
  rebuild groups → toposort → validate." No test pins `build_computation_graph`'s **internal**
  sequence. The existing `test_orchestrator.py::test_step_ordering_call_sequence` pins the
  **outer** `build_pipeline_context` DAG order (REQ-ORCH-01), a different function.

- **REQ-RES-08** — "Consumer scope derivation SHALL apply to ALL live resolution paths:
  backtracker (CalcUsage), attribute resolution map (FORMULA), and `resolve_input(AGG_STRATEGIES)`
  (aggregation)." Per-path derivation is verified indirectly (aggregation via REQ-IR-07,
  CalcUsage-CHAIN via REQ-DRA-04); no single test pins the cross-cutting "ALL paths" invariant.

## R4 Finding — REQ-DM-08 cannot flip to PASS as originally framed; Route A ruling

**Finding.** The item framed DM-08 as "assert the documented model fields are annotated with
the NewType wrappers." R4 re-verification against HEAD refutes the premise: the documented model
fields (`09-data-models.md:111-126`) are bare `str`, and the doc itself states DM-08 is open.
A test faithful to the row's text **fails**; annotating the fields is a code change this
test-authoring item rules out of scope. So the naive flip is impossible.

**Ruling (orchestrator): Route A.** Pin the **enforced** surface, reframe the row's text to that
enforced reality, and file the still-open model-field typing as its own backlog entry.

**Rationale (recorded per the ruling).** The epic's own honesty discipline settles this. INV-B
forbids a PASS row pinning less than its text, and REQ-text reframes are an explicitly accepted
tool in this epic (Item 5 lands 11 of them). Route A is the only path that satisfies SC-C's flip
honestly without a code change Item 3 rules out. Route C (annotate the model fields) is real code
churn out of a test-authoring item; Route B (test the full table as a documented xfail) abandons
SC-C for the row. Route A it is.

Concretely, Route A means:
- The DM-08 test pins the **enforced** claim: the wrappers are NewType, and the `OutputRegistry`
  registries + `make_*` constructors carry them (`core/identifier_types.py`,
  `core/output_registry.py`).
- REQ-DM-08's **text** is reframed from "name fields SHALL use NewType" to the enforced-surface
  claim (the typed-registry surface uses NewType wrappers), citing `09-data-models.md:104` as the
  pre-existing admission that the model fields are not yet typed.
- The model-field typing is filed as a **named BACKLOG entry** (`[DM08-MODEL-FIELD-TYPING]`) with
  the doc's own pointer, so the deferred work is on the ledger, not silently dropped.

## Success Criteria

- [ ] **REQ-DM-08** flips `UNTESTED → PASS`: a static test pins the enforced NewType surface
  (wrappers are NewType; `OutputRegistry` registries + constructors carry them); the row's text is
  reframed to the enforced-surface claim; `[DM08-MODEL-FIELD-TYPING]` is filed for the model
  fields.
- [ ] **REQ-RES-05** flips `UNTESTED → PASS`: a test pins `build_computation_graph`'s internal
  five-milestone sequence (classify → build modules → rebuild groups → toposort → validate) on
  the **real** function, distinct from the outer `build_pipeline_context` pin.
- [ ] **REQ-RES-08** flips `UNTESTED → PASS`: a test enumerates the live resolution paths and
  asserts consumer-scope derivation on each, with each expectation written **independently** of the
  code under test (R1), over the `plant_values` cross-part fixtures.
- [ ] Each of the three tests **fails under a deliberate production mutation** (spot-check recorded
  in close-out).
- [ ] No expectation is computed from the code under test (R1 anti-pattern ban); every pin is
  independently anchored.
- [ ] The three matrix rows carry their new citations; recount-from-rows holds (UNTESTED drops from
  4 to 1 — only REQ-PGD-06 remains UNTESTED); the summary/index counts reconcile to the rows.
- [ ] Full suite green; baselines byte-identical (no baseline touch expected — this is pure
  test-authoring plus a matrix/text/doc reframe).

## Known Requirements

- **[HARD]** **R1 independent anchoring.** No test computes its expectation from the code under
  test. Every pin's expected value is hand-authored (the documented sequence, a hand-transcribed
  scope, an enumerated NewType set) and asserted against what the code produces. This is the epic's
  standing anti-vacuity rule; RES-08 is the highest-risk case.
- **[HARD]** **Mutation-provable.** Each test fails under a deliberate, realistic production
  mutation of the thing it pins (DM-08: swap a registry annotation to bare `str`; RES-05: reorder
  two milestones; RES-08: hardcode an empty/ wrong consumer scope on one path). The mutation is
  reverted; the red→green transition is recorded, not left in the tree.
- **[HARD]** **INV-B — no PASS pins less than its text.** DM-08's text is reframed so the PASS
  row's text matches what the test pins. This forces the reframe; the flip is not honest without
  it.
- **[HARD]** **Conformance tests use real SysML fixtures, never mocks (R1).** RES-08 uses the
  `plant_values` (and, where a second cross-part shape is needed, `plant_value_shapes`) fixtures as
  substrate — real extraction snapshots, not synthetic stubs.
- **[HARD]** **REQ-RES-05 pins the inner function, not the outer orchestrator.** The pin targets
  `build_computation_graph`, source-order or a call-sequence spy. `build_pipeline_context` is
  already pinned by `test_orchestrator.py::test_step_ordering_call_sequence` (REQ-ORCH-01); the new
  test must not duplicate or re-pin that.
- **[NEED]** **RES-08 asserts per-path scope honestly, not a false uniform mechanism.** The three
  paths do not share one derivation. Backtracker (`_consumer_scope_dotted`, `dependency_backtracker.py:450`)
  and aggregation (`ResolutionContext.consumer_scope`, derived at `graph_builder.py:1383`) share the
  same `segments[1:-1]` rule; FORMULA scopes **differently** — via the owning-part-keyed resolution
  map (`_build_attribute_resolution_map` keys on `ca.owning_part_name`; the module_eqn is built from
  `ca.owning_part_qualified_name`, `graph_builder.py:965-985`), not a dotted `consumer_scope` string.
  The test asserts that each path applies **the consumer's scope** (independently computed per path),
  never that all three call one function. Asserting a shared mechanism would be a false pin.
- **[HARD]** **Row/text/doc/backlog move together (R1).** The matrix rows flip with their
  citations; DM-08's text reframes; `09-data-models.md` (and, if RES-05/08 wording drifts,
  `03-resolution-overview.md`) stays consistent; `[DM08-MODEL-FIELD-TYPING]` is filed — all in the
  one change.
- **[INFERRED]** **RES-08 verifies against post-cutover reality.** Item 1 landed, so the
  aggregation path already runs `resolve_input(AGG_STRATEGIES)` via `_build_agg_input_source`
  (`graph_builder.py:1383`), and the matrix row already names it. The RES-08 enumeration is the
  three post-cutover paths, not the pre-cutover `_resolve_aggregation_input_channel`.

## Non-Goals

- **Behavior / code changes.** This is test-authoring plus a matrix/text/doc reframe. Annotating
  the model fields (DM-08 Route C), changing any resolution path, or touching production logic is
  out of scope. If a test **exposes a real bug**, file/absorb it explicitly with a matrix pointer —
  do not fix it inline.
- **The other UNTESTED row.** REQ-PGD-06 stays UNTESTED (its accessor was deleted as dead by Item
  8); it is not this item's row.
- **Item 5's sweep residue** — the 17-strengthen / 11-reframe / 5-citation batch is Item 5, not
  here. The only reframe this item lands is REQ-DM-08's (forced by INV-B), plus any RES-05/08 text
  the flip requires.
- **The DM-08 model-field typing itself** — filed as `[DM08-MODEL-FIELD-TYPING]`, not done here.

## Open Questions / Deferred to design

- **RES-08 test shape given the FORMULA mechanism-divergence.** The requirement is a per-path
  consumer-scope assertion with independent expectations; the exact assertion form is a design
  choice. Two families: (a) a **call-sequence / value spy** that observes the scope string or
  scoped-key each path constructs and compares to a hand-authored expectation; (b) an
  **outcome-level** assertion that the wired channel for a cross-part reference resolves to the
  correct producer under the consumer's scope (and would mis-resolve under a wrong scope). The
  honest handling of FORMULA — which has no `consumer_scope` string — is the crux: design decides
  whether to assert its owning-part scoping as a distinct third arm or to unify at the outcome
  level. Defer the mechanism; the requirement (per-path, independent, real fixtures) is fixed.

- **Item 2 coupling — re-check at implement.** Item 2 (multi-hop chains) adds an **ancestor-scope
  climb** to the backtracker's chain dispatch (per its landed design: scoped-lookup with an
  ancestor-scope climb, 3+-segment gated — `c7aecd6`). It is **not landed** at spec time (plan
  stage only). If it lands before this item implements, the backtracker path's scope handling gains
  an ancestor-climb variant, and RES-08's backtracker arm should extend to cover it (the base
  consumer-scope derivation is still the first rung). **Re-check Item 2's landed phases at implement
  time** and extend the RES-08 enumeration if the climb has landed. Authored against current HEAD
  (single `consumer_scope`, no climb) otherwise.

- **RES-05 pin mechanism — source-order vs. call-sequence spy.** Both satisfy the requirement. A
  source-order pin (AST/source scan of `build_computation_graph` for the anchor calls in order) is
  robust to runtime fixture variation but couples to source shape; a call-sequence spy (patch the
  internal helpers, assert call order over a real fixture run) pins runtime behavior but needs a
  fixture that exercises all five milestones. Sibling precedent is the outer test's source-scan
  (`_get_call_lines_in_function`, `test_orchestrator.py:149`). Defer the choice to design/plan.

- **Which fixture(s) for RES-08.** `plant_values` is the named substrate. Whether a second cross-part
  shape (`plant_value_shapes`) is needed to exercise all three paths in one test, or whether the
  three arms use different minimal fixtures, is a design call. The `[HARD]` constraint is real
  fixtures with a genuine consumer-vs-producer scope gap.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_truth_debt.md` (Item 3; R1–R4; SC-C)
- **Required Reading:**
  - BACKLOG `[ITEM7-MATRIX-TEST-GAPS]` (`.project/backlog/BACKLOG.md:255`) — the original filing.
  - `.project/active/matrix-truth/design.md` — the UNTESTED-12 disposition (why these three were
    left UNTESTED rather than cross-cited).
  - Memory `verification-matrix-drift-modes` — recount-from-rows discipline; the drift modes
    (index counts, missing families, PASS-pins-narrower).
  - `docs/architecture/reference/07-graph-assembly.md` (the graph-builder reference; note: the epic
    cited this as `07-graph-builder.md`, which does not exist — the file is `07-graph-assembly.md`).
- **Landed dependency:** `.project/active/f4-cutover/design.md` — Item 1's post-cutover end-state
  (aggregation runs `resolve_input(AGG_STRATEGIES)` via `_build_agg_input_source`), the substrate
  for RES-08's aggregation arm.
- **Parallel coupling:** Item 2 (multi-hop chains) design `c7aecd6` — the ancestor-scope climb that
  RES-08's backtracker arm may need to account for; re-check landed phases at implement.
- **Key source anchors:**
  - REQ-DM-08: `src/sysml_codegen/core/identifier_types.py` (wrappers),
    `src/sysml_codegen/core/output_registry.py` (enforced surface),
    `src/sysml_codegen/resolution/models.py` (bare-str model fields),
    `docs/architecture/reference/09-data-models.md:101-127` (the documented table + the open-status
    admission at :104).
  - REQ-RES-05: `src/sysml_codegen/resolution/graph_builder.py:161` (`build_computation_graph`,
    Steps 4 / 6–6.7 / 6.6 / 7 / 8); `docs/architecture/reference/03-resolution-overview.md:185`
    (the documented orchestrator sequence); the outer pin at
    `tests/conformance/test_orchestrator.py:124`.
  - REQ-RES-08: `dependency_backtracker.py:450` (`_consumer_scope_dotted`);
    `graph_builder.py:1383` (aggregation `consumer_scope` derivation) + `input_resolver.py:59,85`
    (`ResolutionContext.consumer_scope` usage); `graph_builder.py:923-985`
    (`_build_attribute_resolution_map`, FORMULA owning-part scoping);
    `docs/architecture/reference/03-resolution-overview.md:70` (the row text).
- **Design:** `.project/active/matrix-test-gaps/design.md` (Item 3 has no design stage per the epic
  — deliverables are `{spec,plan}.md`; proceed to `/_my_plan`).

---

**Next Steps:** After approval, proceed to `/_my_plan` (Item 3 skips design — see epic
deliverables). The plan must sequence the RES-08 Item-2-coupling re-check and the three
mutation spot-checks.
