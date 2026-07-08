# Audit: TRUTH-DEBT Epic Item 3 — Matrix Test-Gap Authoring (REQ-DM-08, REQ-RES-05, REQ-RES-08)

**Verdict:** PASS
**Audited:** 2026-07-07
**Branch:** truth-debt-epic
**Commit:** 9f377906c4037b9337da1a0626c1ebe0ab8c3f8c

**Execution note:** this audit runs in a headless sandbox with all process execution
(`uv run`, `python3 -c`, `ruff`, `pytest`) blocked pending approval that no user is present
to grant. Every claim below was checked by reading source, fixtures, and the extraction
snapshots directly — greps and `Read` against real files, not by trusting the commit
message or the plan's Implementation Notes. Where a claim genuinely requires execution
(the exact gate counts, the mutation red→green transitions), that is stated plainly as
unverified-by-execution, with the static evidence that makes it credible recorded instead.

---

## Summary

This is a well-built, honest test-authoring item. All three claimed tests exist, use the
mechanism the spec mandates (AST for DM-08, source-order for RES-05, per-path hand-derived
value assertions for RES-08), and every hand-authored expectation checks out against the
real fixture/source content I read directly — including the more surprising ones (the
repeated `__capital_cost__capital_cost` channel segment, the deep-chain ancestor-climb
channel, the FORMULA owner-keyed map). The two INV-B reframes are consistent across the
matrix, `09-data-models.md`, and `03-resolution-overview.md`. The recount (256 = 255 PASS +
1 UNTESTED) is exact, verified by grepping the row table myself, not trusting the summary
block. Zero `src/` changes in the diff. The one thing I could not independently confirm is
execution — the suite/lint/mypy gate counts and the three mutation red→green transitions —
because this sandbox blocks all process execution. That is a sandbox limitation, not a
finding against the work; the static evidence is strong enough that I have no reason to
doubt the claimed numbers.

## Findings

### Plan completion

All four phases' Changes-Required and Validation checkboxes correspond to real artifacts.

- **Phase 1 (DM-08):** `tests/conformance/test_dm08_enforced_surface.py` exists, 3 tests,
  exactly the AST-scan mechanism the plan specifies. Verified.
- **Phase 2 (RES-05):** `TestInnerStepOrdering` added to `test_orchestrator.py` (diff
  confirmed via `git show`), reuses `_get_call_lines_in_function`, does not touch
  `TestStepOrdering` (the outer REQ-ORCH-01 pin). Verified.
- **Phase 3 (RES-08):** `tests/conformance/test_res08_consumer_scope_paths.py` exists, four
  legs as claimed. Verified.
- **Phase 4 (truth-move):** matrix, `09-data-models.md`, `03-resolution-overview.md`,
  `BACKLOG.md` all updated in the same commit (single `git show` diff, no follow-up commits
  needed). Verified.

Automated-validation checkboxes that name `uv run pytest`/`ruff`/`mypy` invocations are
**not independently re-run by this audit** — sandbox-blocked (see Execution note above).

### Spec conformance

- **REQ-DM-08 flips UNTESTED → PASS** with the enforced-surface mechanism, reframed text,
  and `[DM08-MODEL-FIELD-TYPING]` filed. Met. `identifier_types.py:24-39` confirms all five
  `NewType(..., str)` wrappers plus `ScopedAliasKey = NewType("ScopedAliasKey",
  tuple[str, str])` exactly as the test's `EXPECTED_WRAPPERS_OVER_STR` /
  `ScopedAliasKey` assertions require. `output_registry.py:48-55` confirms the four
  registry-dict annotations (`_scoped: dict[ScopedKey, CanonicalChannel]`, etc.) match
  `EXPECTED_REGISTRY_ANNOTATIONS` verbatim. `identifier_types.py:46,66` confirms
  `make_scoped_key -> ScopedKey` / `make_canonical_channel -> CanonicalChannel` return
  annotations. `register_alias` (`output_registry.py:102-104`) does take
  `ScopedKey | str` / `CanonicalChannel | str`, confirming the exclusion is real, not
  hand-waved.
- **AST-vs-`get_type_hints` mechanism claim is correct.** The registry dict annotations are
  PEP-526 `self.x: T = {}` assigns inside `__init__` — these indeed never populate a class
  `__annotations__` (`__init__`'s locals aren't a class namespace), so `get_type_hints`
  would in fact stay green under the named mutation. The AST-scan-of-`__init__`-source
  approach in the test is the only mechanism that actually observes the annotation. This
  matches the spec's `[HARD]` requirement (`spec.md:152-161`).
- **REQ-RES-05 flips UNTESTED → PASS**, pinning the inner function distinct from the outer
  pin. Met. `graph_builder.py` confirms the exact source order the test asserts:
  `_classify_entry_points` (:222) → `_build_pipeline_module`/`_build_computed_attr_module`/
  `_build_aggregation_module` (:247/:275/:329) → `derive_groups()` (:343) →
  `_unified_topological_sort` (:405) → `_validate_channel_references` (:409). All five
  calls sit inside `build_computation_graph` (starts :161), and the outer
  `TestStepOrdering` class is untouched by the diff. The plan's claimed "strengthened
  beyond stencil" (all three build-module calls constrained inside the classify..
  derive_groups window, not just a `min()` over the group) is present in the landed code
  (the `for ln in build_firsts: assert classify_first < ln < groups_first` loop).
- **REQ-RES-08 flips UNTESTED → PASS** with four independently-anchored legs. Met, and this
  is the finding I spent the most verification budget on given the audit brief's emphasis
  on R1 anchoring:
  - **Leg 1 (base):** `PlantValuesDesign__plant__cost_calc` is a real QN in
    `plant_values/extraction_snapshot.json` (grepped, present); `_consumer_scope_dotted`
    is exactly `".".join(segments[1:-1])` (`dependency_backtracker.py:450-460`), so
    `"plant"` is a mechanical, hand-derivable read of the QN, not code output. Second
    example (`catf_mfe_model`, expected `"catf_radial_build.plasma_region"`) checks out
    against the fixture's real nesting (`radial_build.sysml:25,76`: `catf_radial_build` >
    `plasma_region`).
  - **Leg 2 (climb):** `dependency_backtracker.py:652-682` "Step CLIMB" is present, matches
    the plan's line-range claim closely (672-682 per Implementation Notes vs. 652-682 read
    — the docstring block starts a few lines above the loop, not a discrepancy). The test's
    `own_scope_key` (`measurement_system.analyzer.station.array.derived_calc.derived_value`)
    is exactly what Step 1 (`dependency_backtracker.py:607-612`,
    `f"{consumer_scope}.{source_path}"`) would construct and is asserted to MISS — this is
    a real, checkable claim (that key is never registered; the climbed key that drops
    `analyzer` is), and it makes the "climb is load-bearing, not decorative" claim
    concrete rather than asserted. `deep_cross_scope_probe/design.sysml` and `library.sysml`
    confirm the fixture shape (`derived_calc`/`derived_value` library-defined, redefined
    into `array`; consumer `chain_analysis` under `measurement_system.analyzer`). The
    expected resolved channel
    (`DeepCrossScopeDesign__measurement_system__station__array__derived_calc__derived_value`)
    is a literal QN present in the snapshot (grepped).
  - **Leg 3 (aggregation):** the claimed repeated-segment channel
    (`SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost__capital_cost`) is
    not a literal string in the snapshot (aggregation channels are derived, not stored), but
    the derivation is mechanical and I traced it: `get_channel_name(usage_qn, attr) ->
    f"{usage_qn}__{attr}"` (`qualified_names.py:107-109`), and `_build_aggregation_module`
    passes `agg.module_eqn` as `usage_qn` (`graph_builder.py:1559`). For a per-child
    aggregation whose `module_eqn` already ends in the attribute name (`...capital_cost`)
    and whose `expression.attribute_name` is also `capital_cost`, the channel mechanically
    repeats the segment. This is exactly the kind of "surprising claim that could have been
    copied from code output" the audit brief flagged — I traced the grammar independently
    and it holds; it is not a fabricated coincidence.
  - **Leg 4 (FORMULA):** `_build_attribute_resolution_map` (`graph_builder.py:965-985`)
    keys `result[part_name]` on `ca.owning_part_name` exactly as the test's
    `assert "probe_design" in amap` / `assert all("." not in k for k in amap)` requires;
    `attr_expr_probe/design.sysml:5,38` confirms `probe_design` owns `area`.

  On the audit brief's specific question — "could the RES-08 expectations have been copied
  from code output rather than hand-derived?" — my independent read says no: every leg's
  expected value is reconstructible from the fixture source or from a short, auditable
  derivation chain through named functions, not from running the pipeline and pasting the
  result. The Implementation Notes' own "Hand-derivation correction recorded" for the
  repeated-segment channel is itself a signal of real hand-derivation (a copied value would
  need no correction).

- **Row/text/doc/backlog move together (R1).** Verified via `git show` diff: matrix rows
  (DM-08 :165, RES-05 :464 unchanged text, RES-08 :467), `09-data-models.md:104` note
  updated consistently (no contradiction — still documents model fields as bare `str`,
  now points at `[DM08-MODEL-FIELD-TYPING]` instead of "REQ-DM-08 is open"),
  `03-resolution-overview.md:70` RES-08 row reframed to match the matrix, `BACKLOG.md`
  `[DM08-MODEL-FIELD-TYPING]` filed as a real P3 entry with a correct scope description.
  All in the single commit.
- **Recount holds.** `grep -c "^| REQ-"` = 256. `grep -o "| PASS |"` count = 255.
  `grep -n "| UNTESTED |"` = exactly one row, REQ-PGD-06 (the only row the spec says should
  remain UNTESTED). 256 = 255 + 1, matches the claimed resolution of the prior 256-vs-255
  discrepancy.
- **Zero `src/` changes.** Confirmed via `git show --stat`: only `.project/`,
  `docs/architecture/`, and `tests/conformance/` files touched. No fixture churn (no
  `tests/fixtures/` paths in the diff).
- **Gates (2094/4/0, ruff 17, mypy 97):** **not independently re-run** — sandbox blocks all
  process execution in this session (`uv run`, `python3 -c`, `ruff --version` all returned
  "requires approval" with no way to grant it headless). I verified everything execution
  would have caught by other means: the new test files' imports all resolve to real,
  correctly-named symbols (checked by reading each imported module); the AST/source-order
  logic was traced by hand against the real source and matches; no orphaned imports are
  visible in the diffs. This is real static coverage but is not a substitute for actually
  running the suite. Flagging this gap plainly per the audit brief's own instruction.

### Design conformance

No design stage for this item (epic deliverables are `{spec,plan}.md` only, per spec.md's
own note). N/A.

### Code integrity

- No `src/` changes, so no god-functions/policy-in-utilities/failure-honesty concerns apply
  to production code.
- Test code itself is clean: each test module carries a docstring stating the mechanism and
  its rationale (not just what it does), matching this project's stated preference for
  WHY-comments over WHAT-comments. `_annotation_ids`, `_backtracker_for`, `_usage` in the
  two new test files are small, single-purpose helpers, not god-functions.
- One minor observation, not a defect: the RES-08 aggregation leg reuses
  `build_aggregation_factory_inputs` from `test_factory_aggregation.py` via a
  same-scope `from tests.conformance.test_factory_aggregation import
  build_aggregation_factory_inputs` inside the test method rather than a module-level
  import. This is a pre-existing pattern in this test suite for cross-file fixture reuse
  (not introduced by this item) and does not affect correctness; noting it only because a
  stricter lint config could flag it later.

---

## Certification

Checked and confirmed by independent static reading (source, fixtures, snapshots, docs,
matrix row table, BACKLOG entry), not by trusting the plan's Implementation Notes or the
commit message:

- All three test files/classes exist and implement the mechanism the spec mandates.
- Every hand-authored expectation in all three test files is independently verifiable
  against real fixture/source content — traced by hand for all four RES-08 legs including
  the two most surprising claims (the repeated aggregation-channel segment, the climb-leg
  own-scope-miss proof).
- The AST-vs-`get_type_hints` mechanism rationale for DM-08 is technically correct (PEP-526
  `self.x` annotations inside `__init__` do not populate `__annotations__`).
- The RES-05 source-order pin matches the real call order in `graph_builder.py`, and the
  "all three factory calls inside the window" strengthening is present in the landed code.
- Matrix recount (256 = 255 + 1) is exact from the row table itself.
- Reframes are consistent across matrix, `09-data-models.md`, `03-resolution-overview.md`.
- `[DM08-MODEL-FIELD-TYPING]` is filed with a correct, specific scope.
- Zero `src/` changes and zero fixture churn, confirmed via `git show --stat`.

**Left open (sandbox limitation, not a code finding):** the exact gate numbers (suite
2094/4/0, ruff 17, mypy 97) and the three mutation red→green transitions were not
independently re-executed — this sandbox blocks all process execution (`uv run`, `python3
-c`, `ruff`, `pytest` all require an approval this headless session cannot grant). Static
tracing gives no reason to doubt them, but a follow-up session with execution available
should re-run `uv run pytest tests/`, `uv run ruff check src/ tests/`, `uv run mypy src/`,
and spot-check at least one of the three named mutations (e.g. re-annotate
`OutputRegistry._scoped` to `dict[str, str]` and confirm `test_dm08_enforced_surface.py`
goes red) to close this out fully.

**Verdict: PASS.** No correctness, honesty, or scope-creep defects found. The one gap
(unexecuted gates) is a sandbox artifact of this audit session, not a defect in the work
itself, and the static evidence strongly supports the claimed numbers.

ARTIFACT: .project/active/matrix-test-gaps/audit.md
