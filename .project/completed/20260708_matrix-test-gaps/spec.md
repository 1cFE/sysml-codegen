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

The three rows, and what is actually true at HEAD (R4 re-verified 2026-07-07 at `f9b7958` — Item
1 landed; Item 2's phases have landed, including the ancestor-scope climb, `91e073f`; Item 4 at
plan stage):

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
  Two complications the test must handle honestly: (1) the row text over-claims — it says "via
  `ResolutionContext.consumer_scope`," but FORMULA does **not** go through that field (its own
  Verified-by column already says "FORMULA: scope via owning part QN"), so the text needs the same
  INV-B reframe DM-08 needs (see the RES-08 finding below); (2) Item 2's ancestor-scope climb has
  **landed** (`91e073f`), adding a second scope leg to the backtracker (CalcUsage) arm (base
  consumer scope + ancestor climb), so the enumeration must include it.

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
- The DM-08 test pins the **enforced surface** (defined canonically below): the wrappers are
  NewType, and the `OutputRegistry` registry dicts + `make_*` constructors carry them.
- REQ-DM-08's **text** is reframed from "name fields SHALL use NewType" to the enforced-surface
  claim (the typed-registry surface uses NewType wrappers), citing `09-data-models.md:104` as the
  pre-existing admission that the model fields are not yet typed.
- The model-field typing is filed as a **named BACKLOG entry** (`[DM08-MODEL-FIELD-TYPING]`) with
  the doc's own pointer, so the deferred work is on the ledger, not silently dropped.

## The Enforced Surface — one canonical definition (used by the row text, the test, and the mutation)

"The enforced surface" appeared in five non-equivalent phrasings in the first draft (registry
keys/values, method params, constructor returns — genuinely different sets). Pinned to **one**
definition, used everywhere below and matching the doc's own words at `09-data-models.md:102`
("OutputRegistry keys/values and the `make_*` constructors"):

> **The enforced surface** is (a) the NewType wrappers in `core/identifier_types.py` — asserted to
> be genuine `NewType`s over their base (`SysMLQN.__supertype__ is str`, etc.); (b) the four
> `OutputRegistry` **registry dict annotations** — `_scoped`, `_sysml_qn`, `_alias`,
> `_scoped_alias` in `core/output_registry.py:48-55` (`dict[ScopedKey, CanonicalChannel]` etc.);
> and (c) the **return annotations** of `make_scoped_key` / `make_canonical_channel`
> (`core/identifier_types.py`).

**Deliberately excluded: the `register_*` method params.** `register_alias` takes
`ScopedKey | str` / `CanonicalChannel | str` for backward compatibility
(`output_registry.py:102-104`), so a naive "every registration param is a NewType" assertion is
**false** and would fail on `register_alias`. The canonical surface is keys/values +
constructors, not method params — this sidesteps the union entirely.

## R4 Finding — REQ-RES-08's row text over-claims; commit the reframe now (INV-B)

**Finding.** REQ-RES-08's row text ends "…via `ResolutionContext.consumer_scope`"
(`03-resolution-overview.md:70`, matrix:467). That clause is universal, and it is **false for the
FORMULA arm**: FORMULA scopes by the consumer's owning-part QN
(`_build_attribute_resolution_map` keys on `ca.owning_part_name`; module_eqn from
`ca.owning_part_qualified_name`, `graph_builder.py:966,978-982`), never touching
`ResolutionContext.consumer_scope`. The row's own Verified-by column already contradicts the text
("FORMULA: scope via owning part QN"). A test that honestly asserts FORMULA's owning-part
mechanism pins other-than the "via consumer_scope" clause — the exact INV-B situation DM-08 has.

**Ruling (committed here, not deferred): reframe the RES-08 row text.** Drop the false universal
clause; state the three per-path mechanisms; state plainly that for a computed attribute the
owning part **is** the consumer, so owning-part scoping is consumer-scope derivation for that arm;
and do not let the text read as an exhaustiveness proof (it is an enumeration of named paths — its
guarantee is the completeness of that list, no more). The reframe target:

> **REQ-RES-08 (reframed):** Each live resolution path SHALL scope references to the consumer's
> scope: the backtracker (CalcUsage) derives a dotted consumer scope (`_consumer_scope_dotted`,
> `segments[1:-1]`) and, for deep CHAIN bindings, climbs to ancestor scopes
> (`_resolve_chain_dispatch`, Item 2); `resolve_input(AGG_STRATEGIES)` (aggregation) carries the
> same dotted scope on `ResolutionContext.consumer_scope`; FORMULA scopes by the consumer's
> owning-part QN (for a computed attribute, owner = consumer). The invariant is per-path scope
> application over the enumerated paths, not an exhaustiveness proof.

This is the same INV-B discipline as DM-08 — a PASS row must not pin more or other than its text.

## Success Criteria

- [x] **REQ-DM-08** flips `UNTESTED → PASS`: a **source/AST-scan** static test pins the enforced
  surface (as canonically defined above); the row's text is reframed to the enforced-surface claim;
  `[DM08-MODEL-FIELD-TYPING]` is filed for the model fields.
- [x] **REQ-RES-05** flips `UNTESTED → PASS`: a test pins `build_computation_graph`'s internal
  five-milestone sequence (classify → build modules → rebuild groups → toposort → validate) on
  the **real** function, distinct from the outer `build_pipeline_context` pin.
- [x] **REQ-RES-08** flips `UNTESTED → PASS`: a test enumerates the live resolution paths —
  backtracker (CalcUsage) including the landed ancestor-scope climb leg, aggregation, and FORMULA —
  and asserts consumer-scope derivation on each, with each expectation written **independently** of
  the code under test (R1), over the `plant_values` cross-part fixtures; the row text is reframed
  (drop the false "via `ResolutionContext.consumer_scope`" universal).
- [ ] Each of the three tests **fails under a deliberate production mutation** (spot-check recorded
  in close-out).
- [x] No expectation is computed from the code under test (R1 anti-pattern ban); every pin is
  independently anchored.
- [x] The three matrix rows carry their new citations; recount-from-rows holds (UNTESTED drops from
  4 to 1 — only REQ-PGD-06 remains UNTESTED); the summary/index counts reconcile to the rows.
- [ ] Full suite green; baselines byte-identical (no baseline touch expected — this is pure
  test-authoring plus a matrix/text/doc reframe).

## Known Requirements

- **[HARD]** **R1 independent anchoring.** No test computes its expectation from the code under
  test. Every pin's expected value is hand-authored (the documented sequence, a hand-transcribed
  scope, an enumerated NewType set) and asserted against what the code produces. This is the epic's
  standing anti-vacuity rule; RES-08 is the highest-risk case.
- **[HARD]** **DM-08 mechanism is a source/AST scan — and the mutation must match it.** A
  `typing.get_type_hints` (runtime) mechanism **cannot** pin the enforced surface: the registry
  dict annotations are PEP 526 `self._scoped: …` assignments inside `OutputRegistry.__init__`,
  which never reach any `__annotations__`, so a `get_type_hints` test stays green when `_scoped` is
  re-annotated to `dict[str, str]`. The test therefore uses `inspect.getsource` + `ast` — the exact
  sibling pattern at `test_orchestrator.py:97-117` (`_get_call_lines_in_function`). It (1) asserts
  each wrapper is `NewType` over its base at runtime (`__supertype__`); (2) AST-scans
  `OutputRegistry.__init__` and asserts the four registry dict annotations name their NewTypes; (3)
  AST-scans `make_scoped_key` / `make_canonical_channel` and asserts the return annotations name
  theirs.
- **[HARD]** **Mutation-provable, consistent with the mechanism.** Each test fails under a
  deliberate, realistic production mutation of the thing it pins:
  - DM-08: re-annotate `OutputRegistry._scoped` from `dict[ScopedKey, CanonicalChannel]` to
    `dict[str, str]` — the AST scan finds the annotation no longer names its NewTypes → red. (This
    is why the mechanism is AST, not `get_type_hints`, which would stay green under this exact
    mutation.)
  - RES-05: reorder two milestones in `build_computation_graph`'s source (e.g. move the toposort
    call above the module-build calls) → the source-order pin goes red.
  - RES-08: hardcode an empty or wrong consumer scope on one enumerated path → that path's
    independent expectation fails.

  Each mutation is reverted; the red→green transition is recorded in close-out, not left in the
  tree.
- **[HARD]** **INV-B — no PASS pins less than (or other than) its text.** Both DM-08 and RES-08
  need a text reframe so each PASS row's text matches what its test pins — DM-08 to the enforced
  surface, RES-08 to the honest three-mechanism per-path claim (drop the false "via
  `ResolutionContext.consumer_scope`" universal). Neither flip is honest without its reframe.
- **[HARD]** **Conformance tests use real SysML fixtures, never mocks (R1).** RES-08 uses the
  `plant_values` (and, where a second cross-part shape is needed, `plant_value_shapes`) fixtures as
  substrate — real extraction snapshots, not synthetic stubs.
- **[HARD]** **REQ-RES-05 pins the inner function, not the outer orchestrator.** The pin targets
  `build_computation_graph`, source-order or a call-sequence spy. `build_pipeline_context` is
  already pinned by `test_orchestrator.py::test_step_ordering_call_sequence` (REQ-ORCH-01); the new
  test must not duplicate or re-pin that.
- **[NEED]** **RES-08 asserts per-path scope honestly, not a false uniform mechanism.** The paths
  do not share one derivation. Backtracker (`_consumer_scope_dotted`, `dependency_backtracker.py:450`)
  and aggregation (`ResolutionContext.consumer_scope`, derived at `graph_builder.py:1383`) share the
  same `segments[1:-1]` rule; the backtracker also has, since Item 2 landed, an **ancestor-scope
  climb** leg for deep CHAIN bindings (`_resolve_chain_dispatch`, "Step CLIMB",
  `dependency_backtracker.py:652-682`); FORMULA scopes **differently** — via the owning-part-keyed
  resolution map (`_build_attribute_resolution_map` keys on `ca.owning_part_name`; module_eqn from
  `ca.owning_part_qualified_name`, `graph_builder.py:965-985`), not a dotted `consumer_scope` string.
  The test asserts each path applies **the consumer's scope** (independently computed per path),
  never that they call one shared function. Asserting a shared mechanism would be a false pin.
- **[HARD]** **The DM-08 test scopes its target set to exclude `register_alias`.** Whatever the
  test iterates, it must not assert NewType-ness on `register_alias`'s params — they are
  `ScopedKey | str` / `CanonicalChannel | str` by design (`output_registry.py:102-104`). The
  canonical enforced surface (keys/values + constructors) already excludes method params, so this
  is satisfied by construction; it is stated so a plan that broadens to method params knows the
  boundary.
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
  here. This item lands exactly **two** REQ-text reframes, both forced by INV-B: REQ-DM-08 (to the
  enforced surface) and REQ-RES-08 (drop the false "via `ResolutionContext.consumer_scope`"
  universal). RES-05's text is accurate as written; no reframe expected there.
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

- **Item 2 coupling — LANDED; include the climb leg (concrete re-check).** Item 2's ancestor-scope
  climb has **landed** at HEAD (`f9b7958`; the climb itself is phase-3 commit `91e073f`). The
  landed signal an implementer can grep: the **"Step CLIMB"** block in `_resolve_chain_dispatch`
  (`dependency_backtracker.py:652-682`) — the ancestor loop `for i in range(len(scope_segments),
  -1, -1)` (`:675`) with the single-match ambiguity guard `if len(climbed) == 1` (`:681`). So
  RES-08's backtracker arm has **two** scope legs, both to be asserted: (a) the base single
  consumer scope (`_consumer_scope_dotted`, `segments[1:-1]`), and (b) the ancestor climb — for a
  deep CHAIN whose reference lives in an ancestor scope, the hand-authored expectation is the
  channel found at the ancestor scope, and a mutation that disables the climb (or removes the
  ambiguity guard) fails it. **Re-check at implement** is now a confirmation, not a fork: verify
  the "Step CLIMB" block is still present at implement HEAD (it may move line numbers as Item 2
  closes out); if a later Item-2 phase reverts or reshapes it, adjust the climb-leg expectation
  accordingly.

- **RES-05 pin mechanism — source-order vs. call-sequence spy.** Both satisfy the requirement. A
  source-order pin (AST/source scan of `build_computation_graph` for the anchor calls in order) is
  robust to runtime fixture variation but couples to source shape; a call-sequence spy (patch the
  internal helpers, assert call order over a real fixture run) pins runtime behavior but needs a
  fixture that exercises all five milestones. Sibling precedent is the outer test's source-scan
  (`_get_call_lines_in_function`, `test_orchestrator.py:149`). Defer the choice to design/plan.

- **RES-05 milestone → actual call-name mapping (name it in the plan).** The documented sequence
  uses simplified names (`rebuild_groups`, `topological_sort`, `validate_channel_references`,
  `03-resolution-overview.md:203-205`) that do **not** match the code's call names. The anchor set a
  source-order pin greps for is the actual calls: `_classify_entry_points` (`:222`, "classify"),
  the module-build calls (`_build_pipeline_module` / `_build_computed_attr_module` /
  `_build_aggregation_module`, `:247` region, "build modules"), `derive_groups()` + filtering
  (`:326`, "rebuild groups" — note it is `derive_groups`, not a single `rebuild_groups` call),
  `_unified_topological_sort` (`:388`, "toposort"), `_validate_channel_references` (`:392`,
  "validate"). The plan must state the documented-milestone → real-call-name map so the anchor set
  is unambiguous.

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
- **Landed coupling:** Item 2 (multi-hop chains) — ancestor-scope climb **landed** at HEAD
  (`f9b7958`; climb is phase-3 `91e073f`). Signal: the "Step CLIMB" block in `_resolve_chain_dispatch`
  (`dependency_backtracker.py:652-682`). RES-08's backtracker arm includes this climb leg.
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
  - REQ-RES-08: `dependency_backtracker.py:450` (`_consumer_scope_dotted`, base leg) +
    `dependency_backtracker.py:602,652-682` (`_resolve_chain_dispatch` "Step CLIMB", ancestor leg,
    Item 2); `graph_builder.py:1383` (aggregation `consumer_scope` derivation) +
    `input_resolver.py:59,85` (`ResolutionContext.consumer_scope` usage); `graph_builder.py:923-985`
    (`_build_attribute_resolution_map`, FORMULA owning-part scoping);
    `docs/architecture/reference/03-resolution-overview.md:70` (the row text — reframed by this item).
- **Design:** `.project/active/matrix-test-gaps/design.md` (Item 3 has no design stage per the epic
  — deliverables are `{spec,plan}.md`; proceed to `/_my_plan`).

---

**Next Steps:** After approval, proceed to `/_my_plan` (Item 3 skips design — see epic
deliverables). The plan must sequence the RES-08 Item-2-coupling re-check and the three
mutation spot-checks.
