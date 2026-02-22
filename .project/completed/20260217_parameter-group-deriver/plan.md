# Component: ParameterGroupDeriver (C13)

**Status**: DONE
**Created**: 2026-02-17
**Last updated**: 2026-02-17
**Updated by**: Build agent — C13 conformance complete

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — C13
- **Design intent**: [17-parameter-group-deriver.md](../../concepts/refactor-design-intent/17-parameter-group-deriver.md)
- **Requirements**: REQ-PGD-01 through REQ-PGD-07
- **Depends on**: C03 (extraction — provides CalcUsageData, CalculationDefinitionData), C08 (output registry — for backtracker in filtering test), C11a (backtracker — for real BacktrackingResult in filtering test). All complete.

---

## 1. Assessment

### What This Component Does

`ParameterGroupDeriver` organizes pipeline entry points (user-supplied runtime parameters) into JSON input file groups that mirror the SysML source file structure. It builds 4 internal indexes (attr, binding, unbound, literal) with strict precedence to ensure each parameter is claimed by exactly one index, then derives `DerivedParameterGroup` objects grouped by source file stem. Downstream, `graph_builder.py` consumes `derive_groups_filtered()` (Step 5) and `classify()` (Steps 6.5-6.7 for FORMULA/aggregation entry points).

### Current State

- **Exists?** Yes — `src/sysml_codegen/analysis/parameter_groups.py` (739 lines)
- **Needs extraction/refactoring?** No structural changes needed for conformance. The class, its methods, and data models are stable. Phase 7.1 will eventually extract orchestration helpers, but C13 tests the deriver in isolation.
- **Current test coverage**: `tests/unit/test_parameter_groups.py` — 3 test classes using live SysIDE extraction (chain_spike_model). No conformance tests exist. No snapshot-based tests.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **Snapshot design_attributes key type mismatch.** The snapshot loader (`tests/helpers/snapshot_loader.py`) returns `design_attributes` as `dict[str, list[DesignAttributeData]]` (string keys — absolute file paths). But `ParameterGroupDeriver.__init__` expects `dict[Path, list[DesignAttributeData]]` and accesses `.stem` and `.name` on keys. **Resolution**: Test helper converts keys via `{Path(k): v for k, v in snap["design_attributes"].items()}`. This is a test infrastructure concern, not a design issue.

2. **`classify()` returns `None` for synthetically-constructed qnames.** FORMULA and aggregation modules create entry points with qnames like `"{part_eqn}__{input_name}"` that may not appear in any of the deriver's 4 indexes. The graph_builder handles this with an "orphan → system_design" fallback (lines 214-248 of graph_builder.py). This is by design — the deriver's REQ-PGD-01 guarantees unique assignment among its own indexes, not total coverage of all possible qnames. **No action needed.**

3. **`derive_groups_filtered()` accesses `backtracking_result.entry_points` as a set.** The design doc says it filters to "only true entry points." For testing, we need a real `BacktrackingResult` (Pydantic model). Constructing one with `entry_points` populated from known snapshot data is straightforward — all other fields have defaults or can be empty.

4. **`_literal_index` only captures Type B literals (inline numeric `source_path`).** Type A literals (`source_path=None`, `literal_value` set via FeatureReferenceExpression) are skipped by the `if not param_name or not binding.source_path: continue` guard. This is correct behavior — Type A literals don't have a parseable numeric `source_path`. Verified in solar_battery snapshot data.

### Risks & Unknowns

None significant. The component is stable, well-documented, and has rich fixture data in solar_battery (9 design + 90 library attrs, 15 usages with all 4 index types populated) and catf_mfe (530 attrs across 17 files). No spike needed.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: The ParameterGroupDeriver exists, is stable, has clear interfaces matching the design doc, and all 4 indexes are exercised by existing fixture data. The snapshot data provides all needed inputs. The only test infrastructure need (dict key conversion) is trivial. No unknowns warrant a spike.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_parameter_group_deriver.py`
**Fixture data**: `solar_battery_model` (primary — richest data), `chain_spike_model` (secondary — smallest/simplest), `catf_mfe_model` (cross-model — largest)

### Test Infrastructure Needed

**Helper function** (test-local):
```python
def build_deriver_from_snapshot(snap: dict) -> ParameterGroupDeriver:
    """Build ParameterGroupDeriver from extraction snapshot data.
    Converts design_attributes dict keys from str to Path (snapshot loader
    returns string keys; deriver expects Path keys for .stem/.name access).
    """
    design_attrs = {Path(k): v for k, v in snap["design_attributes"].items()}
    return ParameterGroupDeriver(design_attrs, snap["calc_usages"], snap["calc_defs"])
```

**BacktrackingResult construction** (for REQ-PGD-04 filtering tests):
Construct a real `BacktrackingResult` Pydantic model with `entry_points` populated from known snapshot qualified names. All other fields use defaults/empty values. `PhantomDetectionReport()` has all-default fields.

### Test Cases

> Every requirement (REQ-PGD-NN) must have at least one test case.
> Every test uses real data — no mocks. Stubs only at SysIDE adapter boundary.

| # | Test | Requirement | What it verifies |
|---|------|-------------|------------------|
| 1 | `test_req_pgd_01_unique_assignment_solar_battery` | REQ-PGD-01 | Build deriver from solar_battery snapshot. Collect all qnames across all 4 indexes. Verify no qname appears in more than one index. |
| 2 | `test_req_pgd_01_unique_assignment_catf_mfe` | REQ-PGD-01 | Same check for catf_mfe (530 attrs, 17 files). |
| 3 | `test_req_pgd_01_every_group_param_unique` | REQ-PGD-01 | `derive_groups()` → collect all `param.name` across all groups → assert no duplicates. |
| 4 | `test_req_pgd_02_four_indexes_populated` | REQ-PGD-02 | Build deriver from solar_battery. Assert all 4 indexes are non-empty: `_attr_index` (9 design attrs), `_binding_index` (>0 binding-traced), `_unbound_index` (>0 unbound), `_literal_index` (>0 literal-bound). |
| 5 | `test_req_pgd_02_attr_index_has_design_attrs` | REQ-PGD-02 | Verify `_attr_index` keys match expected solar_battery design attribute qualified names (e.g., `SolarBatteryDesign__solar_battery_plant__p_net_mw`). |
| 6 | `test_req_pgd_02_binding_excludes_attr_names` | REQ-PGD-02 | Verify intersection of `_binding_index.keys()` and `_attr_index.keys()` is empty. |
| 7 | `test_req_pgd_02_unbound_excludes_higher_precedence` | REQ-PGD-02 | Verify `_unbound_index` keys do not appear in `_attr_index` or `_binding_index`. |
| 8 | `test_req_pgd_02_literal_excludes_all_higher` | REQ-PGD-02 | Verify `_literal_index` keys do not appear in any higher-precedence index. |
| 9 | `test_req_pgd_03_group_count_solar_battery` | REQ-PGD-03 | solar_battery has 2 source files → at least 2 groups with unique names. |
| 10 | `test_req_pgd_03_group_count_chain_spike` | REQ-PGD-03 | chain_spike has 1 source file → at least 1 group with unique names. |
| 11 | `test_req_pgd_03_source_identifier_is_sysml_filename` | REQ-PGD-03 | Every group's `source_identifier` ends with `.sysml`. |
| 12 | `test_req_pgd_03_catf_mfe_many_groups` | REQ-PGD-03 | catf_mfe has 17 source files. Verify group count >= 10 (some files may not produce params). |
| 13 | `test_req_pgd_04_filtered_retains_only_entry_points` | REQ-PGD-04 | Build deriver. Construct a BacktrackingResult with `entry_points` = subset of known deriver index names. Call `derive_groups_filtered()`. Verify every surviving param.name is in entry_points set. |
| 14 | `test_req_pgd_04_filtered_drops_empty_groups` | REQ-PGD-04 | Use entry_points from only one source file. Verify groups from other files are absent. |
| 15 | `test_req_pgd_04_filtered_preserves_group_structure` | REQ-PGD-04 | Verify surviving groups still have correct `name`, `class_name`, `source_type`, `source_identifier`. |
| 16 | `test_req_pgd_05_classify_returns_group_for_attr_index` | REQ-PGD-05 | Pick a known qname from `_attr_index`. `classify(qname)` returns a non-None group name matching expected file stem. |
| 17 | `test_req_pgd_05_classify_returns_group_for_binding_index` | REQ-PGD-05 | Same for a known `_binding_index` qname. |
| 18 | `test_req_pgd_05_classify_returns_group_for_unbound_index` | REQ-PGD-05 | Same for a known `_unbound_index` qname. |
| 19 | `test_req_pgd_05_classify_returns_group_for_literal_index` | REQ-PGD-05 | Same for a known `_literal_index` qname. |
| 20 | `test_req_pgd_05_classify_unknown_returns_none` | REQ-PGD-05 | `classify("nonexistent__param__name")` returns `None`. |
| 21 | `test_req_pgd_05_classify_precedence_matches_index` | REQ-PGD-05 | For each index, verify `classify()` result group name is the `_generate_group_names(file.stem)` of the file stored in that index entry. This confirms classify follows the same precedence as the index builder. |
| 22 | `test_req_pgd_06_default_value_direct_attr` | REQ-PGD-06 | `get_default_value()` for a known design attr qname (e.g., `...p_net_mw`) returns `0.008`. |
| 23 | `test_req_pgd_06_default_value_binding_resolution` | REQ-PGD-06 | `get_default_value()` for a binding-traced qname resolves through `_attr_index` and returns the source attribute's parsed float default. |
| 24 | `test_req_pgd_06_default_value_literal` | REQ-PGD-06 | `get_default_value()` for a literal-indexed qname returns the literal float value. |
| 25 | `test_req_pgd_06_default_value_unbound_returns_none` | REQ-PGD-06 | `get_default_value()` for an unbound-indexed qname returns `None`. |
| 26 | `test_req_pgd_06_default_value_unknown_returns_none` | REQ-PGD-06 | `get_default_value("nonexistent")` returns `None`. |
| 27 | `test_req_pgd_07_snake_case_params_suffix` | REQ-PGD-07 | `_generate_group_names("SolarBatteryDesign")` → `("solar_battery_design_params", "SolarBatteryDesignParams")`. |
| 28 | `test_req_pgd_07_already_suffixed_input` | REQ-PGD-07 | `_generate_group_names("design_params")` → `("design_params", "DesignParams")` (no double `_params`). |
| 29 | `test_req_pgd_07_real_group_names_from_fixture` | REQ-PGD-07 | `derive_groups()` on solar_battery → every group.name ends with `_params`, every group.class_name ends with `Params` and is PascalCase. |
| 30 | `test_req_pgd_07_class_name_matches_group_name` | REQ-PGD-07 | For each group, verify `class_name` is the PascalCase equivalent of `name` (strip `_params`, PascalCase, re-append `Params`). |

**Actual test count**: 30 tests

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written
- [x] Tests run (expected: most/all PASS — deriver already works)
- [x] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify
| File | Change | Why |
|------|--------|-----|
| (none) | No production code changes | C13 is conformance-only; the deriver works correctly |

### Files to Create
| File | Purpose |
|------|---------|
| `tests/conformance/test_parameter_group_deriver.py` | 30 conformance tests covering REQ-PGD-01 through REQ-PGD-07 |

### Implementation Notes

1. **Fixture setup pattern**: Session-scoped fixtures (`solar_battery_deriver`, `catf_mfe_deriver`, `chain_spike_deriver`) call `load_extraction_snapshot()` + `build_deriver_from_snapshot()`. Returns `(deriver, snap)` tuple.

2. **BacktrackingResult for filtering tests**: Construct a real `BacktrackingResult` Pydantic model with:
   - `entry_points`: set of known qnames extracted from the deriver's own indexes (real qualified names from snapshot data)
   - `required_usages`: `[]`
   - `dependency_graph`: `{}`
   - `entry_point_sources`: `{}`
   - `phantom_report`: `PhantomDetectionReport()` (all defaults)
   - Other fields: defaults

   This requires importing `BacktrackingResult` and `PhantomDetectionReport`. Must call `_ensure_backtracking_result_rebuilt()` before constructing (lazy model rebuild for forward reference).

3. **Index access pattern**: Tests access `deriver._attr_index`, `deriver._binding_index`, `deriver._unbound_index`, `deriver._literal_index` directly. These are implementation details but are documented in the design intent doc's "Constructor: The Four Indexes" section and are essential for verifying REQ-PGD-02 (precedence). This is the same pattern used in other conformance tests (C08 accesses `registry._scoped`, C11a accesses `_resolve_binding_via_registry`).

4. **Known solar_battery design attribute qnames** (from snapshot):
   - `SolarBatteryDesign__solar_battery_plant__p_net_mw` (default: "0.008" -> 0.008)
   - `SolarBatteryDesign__solar_battery_plant__discount_rate` (default: "0.05" -> 0.05)
   - `SolarBatteryDesign__solar_battery_plant__plant_lifetime` (default: "25.0" -> 25.0)
   - Plus 6 more design.sysml attrs and 90 library.sysml attrs

5. **Test organization**: Group tests by requirement in PascalCase classes:
   - `TestReqPgd01UniqueAssignment`
   - `TestReqPgd02FourIndexPrecedence`
   - `TestReqPgd03FileBasedGrouping`
   - `TestReqPgd04FilteredGroups`
   - `TestReqPgd05Classify`
   - `TestReqPgd06DefaultValueResolution`
   - `TestReqPgd07GroupNamingConvention`

6. **Markers**: All tests marked with `@pytest.mark.req("REQ-PGD-XX")` for collection via `pytest -m "req"`.

### Gate: Ready for VALIDATE
- [x] All test cases pass
- [x] No regressions in full test suite (`uv run pytest tests/`)
- [x] Lint clean (`uv run ruff check tests/conformance/test_parameter_group_deriver.py`)

---

## 5. Validation

- [x] Every acceptance criterion from COMPONENT_CHECKLIST is satisfied
- [x] Every REQ-PGD-NN has at least one passing test
- [x] Full test suite passes (record count: 1334 tests, 1329 passed, 5 xfailed, 0 failures)
- [x] Cross-check: re-read design intent doc, verify implementation matches
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### Baseline Impact
No baseline changes. C13 is conformance-only; no production code changes.

---

## 6. Learnings

### Findings

1. **chain_spike has 1 source file, not 2.** The plan assumed chain_spike had 2 source files (design.sysml and library.sysml) based on solar_battery's structure, but chain_spike only has `design.sysml`. All design attributes, bindings, and usages come from a single file. Test case #10 was updated from "2 groups" to "1 group".

2. **`derive_groups_filtered()` mutates the group objects in-place.** The method modifies `group.parameters` lists on the objects returned by `derive_groups()`. Since session-scoped fixtures share the deriver, calling `derive_groups_filtered()` with a restrictive `entry_points` set permanently alters the groups. Tests using `derive_groups()` after `derive_groups_filtered()` may see reduced parameter counts. This was not an issue because `derive_groups()` builds fresh groups each call, but it's worth noting for downstream consumers that call both methods on the same deriver instance.

3. **PascalCase class names required by ruff N801.** The plan specified `TestREQ_PGD_01_UniqueAssignment` style, but ruff enforces PascalCase for class names. Updated to `TestReqPgd01UniqueAssignment` to match codebase convention. Other conformance tests (C01-C12) don't use nested classes, so this was first encounter.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| (none) | No updates needed | Implementation matches design intent exactly |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| (none) | No impact | C13 is conformance-only |

### Deviations from Plan

1. Test #9/#10: Changed from parametrized `test_req_pgd_03_group_count_matches_source_files[solar_battery/chain_spike]` to separate `test_req_pgd_03_group_count_solar_battery` and `test_req_pgd_03_group_count_chain_spike` with adjusted assertions (chain_spike has 1 file, not 2).

2. Class names: Changed from `TestREQ_PGD_*` to `TestReqPgd*` for ruff N801 compliance.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (current branch)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [x] `git add` only the test file + IMPLEMENTATION_PLAN and COMPONENT_CHECKLIST
- [x] Commit message format: see commit
- [x] Committed successfully

---

## Progress Log

### Session: 2026-02-17 — Initial planning
**Phase**: PLANNING
**Work done**:
- Read design intent doc (17-parameter-group-deriver.md) and all 7 requirements
- Read current source (analysis/parameter_groups.py, 739 lines)
- Analyzed snapshot data for solar_battery (9+90 attrs, 15 usages), catf_mfe (530 attrs, 17 files), chain_spike (6 attrs)
- Reviewed graph_builder.py consumption patterns (derive_groups_filtered, classify, _convert_derived_groups)
- Design consistency review: 4 issues found and resolved (snapshot key type, classify None semantics, BacktrackingResult construction, Type A/B literal handling)
- Spike decision: SKIP (deriver exists and works; all interfaces clear)
- 30 test cases designed covering all 7 requirements
**Stopped at**: Plan complete, ready for BUILD
**Next step**: Build prompt should create `tests/conformance/test_parameter_group_deriver.py` with all 30 test cases
**Blockers**: None

### Session: 2026-02-17 — TEST + BUILD + VALIDATE
**Phase**: DONE
**Work done**:
- Created `tests/conformance/test_parameter_group_deriver.py` with 30 tests across 7 requirement classes
- Helper: `build_deriver_from_snapshot()` converts str keys to Path keys
- Helper: `_collect_all_index_keys()` for cross-index uniqueness verification
- Session-scoped fixtures for solar_battery, catf_mfe, chain_spike
- BacktrackingResult construction for REQ-PGD-04 filtering tests using `_ensure_backtracking_result_rebuilt()` + `PhantomDetectionReport()`
- Fixed test #10: chain_spike has 1 source file (not 2 as plan assumed)
- Fixed class names: `TestREQ_PGD_*` -> `TestReqPgd*` for ruff N801
- All 30 tests pass, lint clean, full suite 1334 tests (1329 passed, 5 xfailed, 0 failures)
- Validated all 7 ACs from COMPONENT_CHECKLIST against test results
- Cross-checked design intent doc: all 7 REQ-PGD requirements covered
**Stopped at**: DONE — all validation checks green
**Next step**: Update IMPLEMENTATION_PLAN.md test count tracking
**Blockers**: None
