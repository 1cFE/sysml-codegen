# Component: Aggregation Scoping (C10)

**Status**: DONE
**Created**: 2026-02-17
**Last updated**: 2026-02-17
**Updated by**: PROMPT-plan agent — C10 Aggregation Scoping Spike

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — C10
- **Design intent**: [13-aggregation-scoping.md](../../concepts/refactor-design-intent/13-aggregation-scoping.md)
- **Requirements**: REQ-AS-01 through REQ-AS-08
- **Depends on**: C01 (Data Models), C02 (Naming Conventions), C08 (Output Registry) — all complete

---

## 1. Assessment

### What This Component Does

Aggregation scoping bridges the gap between PartDef-level aggregation expressions (type-level:
"any Solar_Array computes capital_cost this way") and concrete design instances
(e.g., `Design__plant__solar_array`). Three functions implement this:

1. `find_instance_paths_for_partdef()` — discovers dotted design instance paths from virtual
   CalcUsage parent QNs using two strategies (direct match, child-walk fallback)
2. `_scope_aggregation_expressions()` — produces one `ScopedAggregationData` per
   (AggregationExpressionData, instance_path) pair (one-to-many expansion)
3. `_build_chain_aliases()` — produces `ChannelAlias` objects for `:>>` CHAIN redefinitions
   scoped to design instance paths

These three functions consume extraction data (`HierarchyExtractionResult`, `CalcUsageData`) and
produce `list[ScopedAggregationData]` + `list[ChannelAlias]`, which feed into Phase 1b/2 of the
OutputRegistry registration protocol and downstream module factory construction.

### Current State

- **Exists?** Yes — `src/sysml_codegen/generation/initialization.py`:
  - `find_instance_paths_for_partdef()`: lines 337-403
  - `_build_chain_aliases()`: lines 406-459
  - `_scope_aggregation_expressions()`: lines 462-505
- **Needs extraction/refactoring?** No structural changes for C10. Functions have clean
  interfaces already. Phase 7.1 will extract to `orchestration/` but C10 validates in-place.
- **One code change needed**: REQ-AS-08 requires `logger.warning()` when zero scoped modules
  are produced for an aggregation expression. Currently line 504 uses `logger.info()` for the
  total count but doesn't log per-expression zero-instance cases at all.
- **Current test coverage**: No dedicated tests. Functions are exercised indirectly through
  `build_pipeline_context()` integration and pipeline baseline tests (Phase 0.2), but no
  conformance test isolates and verifies each function's behavior against individual REQs.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc(s)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **Snapshot data includes post-scoped aggregation (same pattern as C09).**
   The extraction snapshots capture `aggregation_expressions: list[ScopedAggregationData]`
   (post-scoped output) AND `hierarchy_data.aggregation_expressions: list[AggregationExpressionData]`
   (pre-scoped raw data) AND `channel_aliases: list[ChannelAlias]` (post-built aliases).

   **Resolution**: Unlike C09, this is NOT a blocker — we can directly test by passing raw
   `hierarchy_data` + `calc_usages` from the snapshot to the scoping functions and comparing
   output against the snapshot's `aggregation_expressions` and `channel_aliases`. The raw inputs
   are unmodified by scoping (scoping creates new objects, doesn't mutate inputs). C09's
   Learning #1 confirmed this pattern works.

2. **IMPLEMENTATION_PLAN step 2.3 says REQ-AS-01 through REQ-AS-07 but COMPONENT_CHECKLIST
   lists REQ-AS-01 through REQ-AS-08.**
   The IMPLEMENTATION_PLAN acceptance criteria omits REQ-AS-08 (zero-instance WARNING).

   **Resolution**: Include REQ-AS-08 in the test plan. This is the only requirement that
   needs a production code change (add `logger.warning()` for zero-instance case). The
   IMPLEMENTATION_PLAN should be updated to say REQ-AS-01 through REQ-AS-08 during the
   LEARN phase.

3. **REQ-AS-05 and REQ-AS-06 reference OutputRegistry operations, not scoping.**
   These requirements describe Phase 1b registration and Phase 2 alias resolution, which
   happen in `build_output_registry()`, not in the scoping functions themselves. However,
   the C10 AC in the COMPONENT_CHECKLIST includes "Phase 1b registration" and "Phase 2
   resolution" items.

   **Resolution**: C10 tests should verify the scoping output *structure* that enables
   correct registry operations (e.g., `module_eqn` format, `instance_path` format,
   `ChannelAlias` field values). The actual registration is already tested by C08 (Output
   Registry). C10 tests should NOT re-test the registry itself, but SHOULD verify that
   calling `build_output_registry()` with C10 outputs works (integration check).

4. **REQ-AS-04 filter condition in doc says `"." not in source_path`.**
   The actual code at line 436 has `if not redef.source_path or "." not in redef.source_path`.
   The `not redef.source_path` guard is an additional safety check not mentioned in the
   requirement text but is logically necessary.

   **Resolution**: Not a contradiction — the code is strictly more defensive. Test both the
   dot-filter and the null-source_path guard.

5. **`_scope_aggregation_expressions` instance_path format uses `__` separator with design
   prefix included, but `find_instance_paths_for_partdef` returns dotted, prefix-stripped
   paths.** The scoping function reconstructs the `__`-separated path by prepending the
   design prefix. This is the intended behavior per REQ-AS-03 ("paths SHALL be converted from
   `__`-separated to dotted format with design prefix stripped") — but note that REQ-AS-03
   describes `find_instance_paths_for_partdef`'s output, not `ScopedAggregationData.instance_path`.
   The `instance_path` field keeps the full `__`-separated path WITH design prefix.

   **Resolution**: This is consistent — `find_instance_paths_for_partdef` strips for dotted
   human-readable paths; `_scope_aggregation_expressions` reconstructs full `__` paths for
   `module_eqn` computation. Test both formats.

6. **C06 Learning: REQ-HR-07 alias detection has zero positive-case fixture coverage.**
   `aliases` field on `AggregationExpressionData` is empty for all expressions in all fixtures.
   The `_build_chain_aliases` function filters on `hierarchy_data.redefinitions`, not on
   `aggregation_expressions.aliases`. These are different: `aliases` on the expression data
   refers to BF-7 alias names registered in Phase 1b (handled in `build_output_registry`),
   while `_build_chain_aliases` produces Phase 2 `ChannelAlias` objects from CHAIN
   redefinitions on the PartDef.

   **Resolution**: Check if solar_battery has any CHAIN redefinitions that qualify for
   `_build_chain_aliases`. The three filters are: `redefinition_type == CHAIN`,
   `not is_deep_path`, `"." in source_path`. Based on C06 data (78 redefinitions), some
   may qualify. If none do, test with constructed data using real names (same pattern as C09).

### Risks & Unknowns

1. **Zero qualifying CHAIN redefinitions for alias testing.** If no solar_battery redefinitions
   pass all three filters, `_build_chain_aliases` returns empty and REQ-AS-04 needs constructed
   test data. This is manageable (C09 proved the constructed-data pattern works) but needs a
   spike to confirm.

2. **issue22_model coverage.** The issue22 model has 1 aggregation expression with null
   multiplicity. This is a useful edge case for REQ-AS-01 (one-to-many with exactly one
   instance) and for the `SumTerm` with null count.

3. **Design prefix derivation depends on CalcUsage ordering.** The `_scope_aggregation_expressions`
   function takes the design prefix from the FIRST virtual CalcUsage. If no virtual CalcUsages
   exist, `design_prefix` is None and instance_paths lack the prefix. Edge case to test.

---

## 2. Spike

**Decision**: SPIKE
**Rationale**: Two unknowns must be resolved before writing the test plan:
(1) Whether any solar_battery CHAIN redefinitions qualify for `_build_chain_aliases` (determines
whether we need constructed test data for REQ-AS-04).
(2) Whether `_scope_aggregation_expressions` output matches snapshot `aggregation_expressions`
exactly when given the same inputs (validates the test comparison strategy).

### Spike Questions

1. **Do any solar_battery CHAIN redefinitions pass all three filters in `_build_chain_aliases`?**
   Specifically: `redefinition_type == CHAIN`, `not is_deep_path`, and `"." in source_path`.
   If yes, how many, and what are their attribute_name and source_path values?

2. **Does calling `_scope_aggregation_expressions(hierarchy_data, calc_usages)` with snapshot
   inputs produce output that matches the snapshot's `aggregation_expressions`?** Specifically,
   do the `instance_path` values and expression references match?

3. **What `channel_aliases` with `source="redefinition"` exist in the solar_battery snapshot?**
   These are the output of `_build_chain_aliases`. If non-empty, they validate the function
   produces real output.

4. **Does `find_instance_paths_for_partdef` use Strategy 1 or Strategy 2 for each PartDef in
   solar_battery?** Understanding which strategy fires helps design targeted tests.

### Spike Approach

1. Load solar_battery snapshot. Inspect `hierarchy_data.redefinitions` — filter for CHAIN type,
   not deep_path, source_path contains ".". Count qualifying entries.
2. Call `_scope_aggregation_expressions(hierarchy_data, calc_usages)` on snapshot data. Compare
   output against snapshot `aggregation_expressions` by checking `instance_path` and
   `expression.attribute_name` for each entry.
3. Filter snapshot `channel_aliases` for `source="redefinition"`.
4. For each of the 4 unique `owning_part_qn` values in solar_battery aggregation expressions,
   call `find_instance_paths_for_partdef()` and observe which strategy produces results.

### Spike Findings

1. **Q1: 41 qualifying CHAIN redefinitions in solar_battery.** Across 9 PartDefs (PV_Module,
   String_Inverter, Array_BOS, Battery_Pack, Hybrid_Inverter, Battery_BOS, Racking_Mounting,
   Electrical_Panel, Permitting_Interconnect). Each has 5 aliases (capital_cost, raw_material_cost,
   fabrication_cost, installation_cost, idiot_index) except Permitting_Interconnect which has 1
   (capital_cost only). The `cas_category` CHAIN redefs are filtered out because `source_path`
   has no dot (e.g., `"CAS220101"`). Solar_Array, Battery_System, Site_Infrastructure, and
   Solar_Battery_Plant have no qualifying CHAIN redefs (they have `cas_category` only or none).
   **No constructed test data needed for REQ-AS-04** — real data provides full coverage.

2. **Q2: `_scope_aggregation_expressions` output matches snapshot exactly.** 20 computed
   `ScopedAggregationData` match 20 snapshot entries on `(instance_path, attribute_name)` pairs.
   Test comparison strategy is validated.

3. **Q3: 41 redefinition aliases in snapshot.** All 41 match the 41 computed by
   `_build_chain_aliases`. `alias_name` and `canonical_name` pairs are identical.
   **Snapshot comparison works for alias testing.**

4. **Q4: Strategy selection by PartDef:**
   - `SolarBatteryLibrary__Solar_Array` → Strategy 1 (direct match) → `["solar_battery_plant.solar_array"]`
   - `SolarBatteryLibrary__Battery_System` → Strategy 2 (child-walk) → `["solar_battery_plant.battery_system"]`
   - `SolarBatteryLibrary__Site_Infrastructure` → Strategy 2 (child-walk) → `["solar_battery_plant.site_infra"]`
   - `SolarBatteryLibrary__Solar_Battery_Plant` → Strategy 2 (child-walk) → `["solar_battery_plant"]`

   Only 1 of 4 PartDefs uses Strategy 1. The other 3 use Strategy 2 (child-walk fallback),
   providing good coverage for both strategies with real data.

5. **issue22 model: 1 scoped aggregation.** `instance_path="Issue22Design__plant__assembly"`,
   `attribute_name="total_cost"`, `module_eqn="Issue22Design__plant__assembly__total_cost"`.
   Matches snapshot.

### Spike Impact on Plan

1. **No constructed test data needed.** All spike concerns resolved positively — real fixture
   data covers CHAIN aliases (41 entries), both strategies (1 direct, 3 child-walk), and
   snapshot comparison validates cleanly. This simplifies the test plan significantly.

2. **Test plan updates:**
   - `test_req_as_04_chain_alias_filters`: Use real solar_battery data (41 qualifying, 12
     filtered by no-dot source_path). No constructed data needed.
   - `test_req_as_02_strategy_ordering` and `test_req_as_02_strategy_2_child_walk_fallback`:
     Use real PartDefs — Solar_Array for Strategy 1, Battery_System/Site_Infrastructure/
     Solar_Battery_Plant for Strategy 2.
   - `test_req_as_04_alias_matches_snapshot`: Snapshot has 41 redefinition aliases — full
     comparison possible.

3. **No plan changes needed.** All test cases as designed are feasible with real data.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_aggregation_scoping.py`
**Fixture data**: solar_battery_model (primary — 20 aggregation expressions, 4 PartDefs),
issue22_model (edge case — 1 expression, null multiplicity). Supplemented with constructed
data for CHAIN alias coverage if needed.

### Test Cases

> Every requirement (REQ-AS-NN) must have at least one test case.
> Every test uses real data — no mocks. Stubs only at SysIDE adapter boundary.

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_req_as_01_one_to_many_expansion[solar_battery]` | REQ-AS-01 | solar_battery has 4 PartDefs with 5 aggregation expressions each = 20 raw expressions. Each PartDef maps to exactly 1 design instance. Scoping produces exactly 20 `ScopedAggregationData`, one per expression. |
| `test_req_as_01_expansion_matches_snapshot[solar_battery]` | REQ-AS-01 | Call `_scope_aggregation_expressions(hierarchy_data, calc_usages)` on snapshot data; verify output count matches snapshot `aggregation_expressions` count (20); verify each `instance_path` and `expression.attribute_name` pair matches |
| `test_req_as_01_issue22_single_instance` | REQ-AS-01 | issue22_model has 1 aggregation expression. Scoping produces exactly 1 `ScopedAggregationData`. Verify `instance_path` contains the design instance path. |
| `test_req_as_02_strategy_1_direct_match[solar_battery]` | REQ-AS-02 | For `SolarBatteryLibrary__Solar_Array`, virtual CalcUsages with matching `owning_part_def_qn` exist (e.g., `allocation_model`). Strategy 1 finds instance path directly. Verify `find_instance_paths_for_partdef()` returns non-empty for this PartDef. |
| `test_req_as_02_strategy_ordering` | REQ-AS-02 | Verify Strategy 1 is tried first: call `find_instance_paths_for_partdef()` with a PartDef that has direct matches. Verify Strategy 2 child-walk is NOT needed (Strategy 1 produces results). Then call with a PartDef that has NO direct matches but has `part_usage_names` — verify child-walk fallback produces results. |
| `test_req_as_02_strategy_2_child_walk_fallback` | REQ-AS-02 | Construct a scenario where Strategy 1 fails: use a PartDef QN that has no virtual CalcUsages with matching `owning_part_def_qn`, but whose child PartUsage names appear in other CalcUsage QN segments. Verify `find_instance_paths_for_partdef()` with `part_usage_names` returns correct instance paths. |
| `test_req_as_03_dotted_prefix_stripped[solar_battery]` | REQ-AS-03 | For `SolarBatteryLibrary__Solar_Array`, `find_instance_paths_for_partdef()` returns dotted paths like `"solar_battery_plant.solar_array"` (design prefix `"SolarBatteryDesign"` stripped, `__` → `.`). Verify no `__` in output. Verify no `SolarBatteryDesign` prefix. |
| `test_req_as_03_all_partdefs_stripped[solar_battery]` | REQ-AS-03 | Parametrize over all 4 solar_battery PartDef QNs. Verify every returned path is dotted and prefix-stripped. |
| `test_req_as_04_chain_alias_filters` | REQ-AS-04 | Verify `_build_chain_aliases()` applies all three filters: (1) skips non-CHAIN redefinitions, (2) skips deep-path redefinitions, (3) skips redefinitions where source_path has no dot. Use real solar_battery redefinitions if qualifying ones exist; otherwise construct test data with real names. |
| `test_req_as_04_chain_alias_output_format` | REQ-AS-04 | For qualifying CHAIN redefinitions, verify `ChannelAlias` output: `alias_name = "{dotted_path}.{attribute_name}"`, `canonical_name = "{dotted_path}.{source_path}"`, `source = "redefinition"`. |
| `test_req_as_04_alias_matches_snapshot[solar_battery]` | REQ-AS-04 | Filter snapshot `channel_aliases` for `source="redefinition"`. If non-empty, verify `_build_chain_aliases()` output matches. If empty, verify function returns empty list (confirms no qualifying redefinitions in fixture). |
| `test_req_as_05_phase_1b_registration[solar_battery]` | REQ-AS-05 | Build scoped agg data from snapshot, then call `build_output_registry()` with it. Verify each `ScopedAggregationData` has a corresponding canonical channel registered. Verify `scoped_lookup(key_e_stripped)` returns the canonical channel. |
| `test_req_as_06_phase_2_alias_resolution[solar_battery]` | REQ-AS-06 | If chain aliases exist, verify `build_output_registry()` resolves `canonical_name` before registering alias. Verify `alias_lookup()` on the alias key returns the resolved canonical channel. If no chain aliases, verify Phase 2 produces 0 registrations from redefinition aliases. |
| `test_req_as_07_module_eqn_format[solar_battery]` | REQ-AS-07 | For each `ScopedAggregationData` in the snapshot, verify `module_eqn == f"{instance_path}__{attribute_name}"`. Parametrize over all 20 entries. |
| `test_req_as_07_module_eqn_issue22` | REQ-AS-07 | Verify issue22 `ScopedAggregationData.module_eqn` follows the same format. |
| `test_req_as_08_zero_instance_warning` | REQ-AS-08 | Construct an `AggregationExpressionData` with an `owning_part_qn` that matches no virtual CalcUsages (e.g., `"NonExistent__PartDef"`). Call `_scope_aggregation_expressions()`. Verify it logs a WARNING (not info) containing the PartDef QN and attribute name. Verify zero `ScopedAggregationData` produced for that expression. |
| `test_find_instance_paths_empty_calc_usages` | REQ-AS-02 | Call `find_instance_paths_for_partdef()` with empty `calc_usages`. Verify returns empty list. |
| `test_find_instance_paths_no_virtual_usages` | REQ-AS-02 | Call with calc_usages that are all templates or have no `owning_part_def_qn`. Verify returns empty. |
| `test_scope_agg_no_hierarchy_data` | REQ-AS-01 | Call `_scope_aggregation_expressions(None, calc_usages)`. Verify returns empty list. |
| `test_scope_agg_empty_expressions` | REQ-AS-01 | Call with `hierarchy_data` that has empty `aggregation_expressions`. Verify returns empty list. |
| `test_instance_path_has_design_prefix[solar_battery]` | REQ-AS-01, REQ-AS-03 | Each `ScopedAggregationData.instance_path` starts with the design prefix (e.g., `"SolarBatteryDesign__"`). Verify `__` separator used. Verify `module_eqn` derived from this path. |

### Test Infrastructure Needed

- Existing conftest.py fixtures: `solar_battery_snapshot`, `issue22_snapshot` (session-scoped)
- Import `_scope_aggregation_expressions`, `_build_chain_aliases`, `find_instance_paths_for_partdef`
  from `sysml_codegen.generation.initialization`
- Import `build_output_registry` for REQ-AS-05/06 integration checks
- `caplog` pytest fixture for REQ-AS-08 WARNING verification
- `copy.deepcopy` for any mutation-sensitive tests (scoping creates new objects so likely not needed)

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written
- [x] Tests run (46 passed, 1 failed — REQ-AS-08 only, as expected)
- [x] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify
| File | Change | Why |
|------|--------|-----|
| `src/sysml_codegen/generation/initialization.py` | Add per-expression `logger.warning()` when `find_instance_paths_for_partdef()` returns empty in `_scope_aggregation_expressions()` (around line 492-493). Warning message must include `agg_expr.owning_part_qn` and `agg_expr.attribute_name`. | REQ-AS-08 |

### Files to Create
| File | Purpose |
|------|---------|
| `tests/conformance/test_aggregation_scoping.py` | Conformance tests for REQ-AS-01 through REQ-AS-08 |

### Implementation Notes

1. **REQ-AS-08 code change is minimal**: Add a conditional check after the
   `find_instance_paths_for_partdef()` call at line 487-491. If `dotted_paths` is empty,
   log `logger.warning("Aggregation expression '%s' on PartDef '%s' produced zero scoped "
   "modules — PartDef may not be instantiated in the design", agg_expr.attribute_name,
   agg_expr.owning_part_qn)`. Then `continue` (no ScopedAggregationData emitted, same as now).

2. **Test comparison strategy**: The snapshot contains both raw inputs and expected outputs.
   Call scoping functions with raw inputs from the snapshot, compare outputs against snapshot
   post-scoped data. No reconstruction of pre-state needed (unlike C09).

3. **Phase 1b/2 integration tests (REQ-AS-05/06)**: Build a real `OutputRegistry` from
   snapshot data using `build_output_registry()`, then verify typed lookups return channels
   for aggregation keys. This reuses the C08 build infrastructure without re-testing registry
   internals.

4. **CHAIN alias testing**: Spike must determine if any solar_battery CHAIN redefinitions
   qualify. If none do, construct `RedefinitionData` with real names from the fixture (same
   pattern as C09's CHAIN override tests). The `ChannelAlias` output format is well-defined:
   `alias_name=f"{dotted_path}.{attr_name}"`, `canonical_name=f"{dotted_path}.{source_path}"`.

5. **Strategy 2 (child-walk) testing**: Need a PartDef QN that has NO direct virtual CalcUsage
   matches but has children in `part_usage_names`. May need to construct this case if all
   solar_battery PartDefs use Strategy 1. Alternatively, could modify the input to remove
   the direct-match CalcUsages and verify Strategy 2 finds paths via children.

### Gate: Ready for VALIDATE
- [x] All test cases pass (47 passed)
- [x] No regressions in full test suite (`uv run pytest tests/` — 1165 passed)
- [x] Lint clean (`uv run ruff check src/` — all checks passed)

---

## 5. Validation

- [x] One ScopedAggregationData per design instance (one-to-many expansion) — REQ-AS-01
- [x] Direct CalcUsage match strategy before child-walk fallback — REQ-AS-02
- [x] Instance paths: `__`-separated converted to dotted, design prefix stripped — REQ-AS-03
- [x] CHAIN aliases only for non-deep-path with `.` in source_path — REQ-AS-04
- [x] Phase 1b registration of canonical channels per ScopedAggregationData — REQ-AS-05
- [x] Phase 2 resolution of ChannelAlias before registering — REQ-AS-06
- [x] module_eqn = `"{instance_path}__{attribute_name}"` — REQ-AS-07
- [x] Test: solar_battery model produces expected scoped modules — REQ-AS-01 (snapshot comparison)
- [x] Zero-instance case logs WARNING with PartDef QN and attribute name — REQ-AS-08
- [x] Every REQ-AS-NN has at least one passing test
- [x] Full test suite passes (record count: 1165 tests, 0 failures)
- [x] Cross-check: re-read design intent doc 13, verify implementation matches
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### Baseline Impact

Minimal — REQ-AS-08 adds a `logger.warning()` call for zero-instance edge cases. No change
to scoping outputs or downstream behavior. Existing baselines should be unaffected since all
fixture models produce non-zero scoped modules.

---

## 6. Learnings

### Findings

1. **All three scoping functions work correctly with real fixture data — no constructed test
   data needed.** Unlike C09 (which needed constructed CHAIN override data), C10 has full
   coverage from real solar_battery data: 41 qualifying CHAIN redefinitions, both Strategy 1
   and Strategy 2 exercised naturally, and 20 aggregation expressions with snapshot-verifiable
   output. This made testing significantly simpler.

2. **Strategy 2 (child-walk) is the dominant strategy.** 3 of 4 PartDefs with aggregation
   expressions use Strategy 2. Only Solar_Array uses Strategy 1 (direct match). This is
   because aggregation PartDefs like Battery_System, Site_Infrastructure, and Solar_Battery_Plant
   don't have their own virtual CalcUsages — they aggregate child PartUsage calc outputs.

3. **cas_category CHAIN redefinitions correctly filtered.** The `"." not in source_path`
   filter correctly excludes CAS code references (e.g., `CAS220101`, `CAS24`) which are
   entry-point identifiers, not channel chains. 12 such redefinitions are filtered out across
   the fixture data.

4. **REQ-AS-08 implementation was trivial.** Added 6 lines: an `if not dotted_paths` check
   with `logger.warning()` and `continue`. No behavior change for existing paths — the warning
   only fires for the zero-instance edge case.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| IMPLEMENTATION_PLAN.md | Change "REQ-AS-01 through REQ-AS-07" to "REQ-AS-01 through REQ-AS-08" in step 2.3 | REQ-AS-08 omitted from acceptance criteria |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| C11 — Backtracker | Consumes OutputRegistry with aggregation channels. No C10 changes affect C11 interface. | None |
| C16 — Aggregation Module Factory | Consumes `ScopedAggregationData` directly. No field changes. | None |

### Deviations from Plan

1. **Test count: 47 vs 21 planned.** Parametrized tests (`test_module_eqn_format_solar_battery`
   parametrized over 20 entries, `test_all_partdefs_stripped` over 4 PartDefs) expanded the
   count. Several additional edge-case tests were added (empty input guards, type assertions).
   The plan's test case table listed 21 logical tests; the actual parametrized expansion
   produced 47 test items.

2. **No separate test for `test_scope_agg_no_hierarchy_data` null multiplicity.** The plan
   mentioned issue22's null multiplicity as an edge case, but this is a SumTerm property tested
   by C06 (Hierarchy Resolver), not a scoping concern. Scoping only cares about instance_path
   and attribute_name — multiplicity is consumed by the aggregation module factory (C16).

3. **REQ-AS-05/06 tests use `build_output_registry()` directly** rather than constructing a
   minimal registry. This is simpler and tests the actual integration path.  The plan anticipated
   this approach in Implementation Note #3.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (current branch)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [x] Committed as part of Phase 2 batch commit (C08 + C09 + C10 + TRR + audit)
- [x] Committed successfully *(2026-02-17)*

---

## Progress Log

### Session: 2026-02-17 — Plan creation
**Phase**: PLANNING
**Work done**:
- Loaded design intent doc (13-aggregation-scoping.md), COMPONENT_CHECKLIST, IMPLEMENTATION_PLAN
- Read current source: `initialization.py` lines 337-505 (all three functions)
- Read data models: `data_models.py` lines 274-368 (SumTerm, SingletonTerm, LocalTerm, AggregationExpressionData, ScopedAggregationData)
- Verified snapshot structure: raw inputs (hierarchy_data.aggregation_expressions) and post-scoped outputs (aggregation_expressions, channel_aliases) both available
- Explored fixture data: solar_battery has 20 agg expressions across 4 PartDefs, issue22 has 1
- Reviewed C08 and C09 learnings for reusable patterns
- Completed design consistency review: found 6 issues, all resolved
- Wrote complete test plan with 21 test cases covering REQ-AS-01 through REQ-AS-08
- Identified one production code change needed: REQ-AS-08 WARNING logging
**Stopped at**: Plan complete, ready for spike
**Next step**: Run spike to answer 4 questions (CHAIN redef qualification, output comparison, channel alias content, strategy selection). Then proceed to TEST phase.
**Blockers**: None — spike questions are answerable with existing snapshot data

### Session: 2026-02-17 — Spike + TEST + BUILD
**Phase**: SPIKE → TEST → BUILD
**Work done**:
- Ran all 4 spike questions against real solar_battery and issue22 data
- Findings: 41 qualifying CHAIN redefs, output matches snapshot exactly, both strategies exercised
- No constructed test data needed — all real data covers all requirements
- Advanced status to TEST
**Work done (continued)**:
- Wrote 47 conformance tests in `tests/conformance/test_aggregation_scoping.py`
- All tests pass except REQ-AS-08 (expected — code change needed)
- Verified no mocks in test file
- Advanced to BUILD phase
- Implemented REQ-AS-08: added `logger.warning()` in `_scope_aggregation_expressions()` (6 lines)
- All 47 tests pass, full suite 1165 pass, lint clean
- Advanced to VALIDATE, verified all checkboxes
- Updated COMPONENT_CHECKLIST.md: C10 AC all checked
- Updated IMPLEMENTATION_PLAN.md: step 2.3 complete, learnings added, test count updated
- Advanced to DONE
**Stopped at**: Component complete
**Next step**: Commit (section 7)
