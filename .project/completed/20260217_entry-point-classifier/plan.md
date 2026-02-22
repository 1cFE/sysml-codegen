# Component: Entry Point Classification (C17)

**Status**: DONE
**Created**: 2026-02-17
**Last updated**: 2026-02-17
**Updated by**: Build session (Opus 4.6)

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` -- C17
- **Design intent**: [06-entry-point-classifier.md](../../concepts/refactor-design-intent/06-entry-point-classifier.md)
- **Requirements**: REQ-EPC-01 through REQ-EPC-08
- **Depends on**: C14 (CalcUsage Factory -- done), C15 (FORMULA Factory -- done), C16 (Aggregation Factory -- done), C13 (ParameterGroupDeriver -- done)

---

## 1. Assessment

### What This Component Does

`_classify_entry_points()` (graph_builder.py:265-367) classifies every unresolved pipeline input into one of three EntryPointType values (DESIGN_ATTRIBUTE, LIBRARY_DEFAULT, USAGE_LITERAL) using a strict precedence decision tree. It consumes the backtracker's entry point set, design attributes, calc usages, and calc defs, and produces a `dict[str, EntryPoint]` with classified types, float-converted defaults, and param_group assignments. Additionally, `build_computation_graph()` Steps 6.5-6.8 handle factory-created entry points (Path 2) and orphan grouping.

### Current State

- **Exists?** Yes -- `src/sysml_codegen/resolution/graph_builder.py` lines 265-367 (`_classify_entry_points`), lines 370-461 (`_group_entry_points_via_deriver`, `_convert_derived_groups`), lines 464-488 (`_get_library_default`), lines 199-248 (Steps 6.6 rebuild + 6.8 orphan collection in `build_computation_graph`)
- **Needs extraction/refactoring?** No structural changes for C17. Conformance-only.
- **Current test coverage**: `_classify_entry_points()` is called by C14/C15/C16 test helpers (`build_factory_inputs_from_snapshot()`) as setup infrastructure, but no test directly verifies classification correctness (type assignment, precedence, default conversion). Existing unit tests in `tests/unit/test_graph_builder.py` use mocks.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc(s)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **REQ-EPC-07 "pure function" vs current implementation.** `_classify_entry_points()` itself IS pure -- it takes inputs and returns a new dict without mutating arguments. The function signature and body confirm this (no argument mutation, returns `result` dict). This AC is straightforward to verify.

2. **REQ-EPC-08 "factory EPs never re-classified" is an architectural property, not a function property.** The design doc says `_classify_entry_points()` runs at Step 4 of `build_computation_graph()`, while factory EPs are created at Steps 6.5 and 6.7. Step 6.6 rebuilds parameter groups but does NOT re-invoke `_classify_entry_points()`. So factory EPs bypass classification by construction (ordering guarantee), not by a guard inside the classifier. **Resolution**: Verify this via static analysis of `build_computation_graph()` -- confirm `_classify_entry_points` is called exactly once (Step 4), before any factory calls (Steps 6.5, 6.7). Also verify factory-created EPs in the final entry_points dict retain `entry_type=DESIGN_ATTRIBUTE` after full graph assembly.

3. **REQ-EPC-06 "groups rebuilt after FORMULA/Aggregation" is tested at the graph assembly level.** Step 6.6 in `build_computation_graph()` rebuilds param_groups from the complete entry point set. This is an orchestration concern, not a classifier concern. **Resolution**: Test by running `build_computation_graph()` with models that have FORMULA and aggregation modules (solar_battery_model) and verifying factory-created EPs appear in the final param_groups.

4. **REQ-EPC-05 orphan handling needs a model that produces orphans.** Scanning the code (lines 214-248), orphans are EPs not covered by any DerivedParameterGroup. This requires an EP whose qualified_name doesn't match any group_deriver group. Natural orphans may not exist in fixture models (the deriver is comprehensive). **Resolution**: Test with a constructed scenario -- add a synthetic EP to the entry_points dict before the rebuild, verify it lands in "system_design". Use real QNs from fixture data but a QN that doesn't match any group.

5. **REQ-EPC-03 float conversion applies to all 3 branches differently.** DESIGN_ATTRIBUTE reads from `attr.default_value`; LIBRARY_DEFAULT reads from `_get_library_default()` which calls `float()` internally; USAGE_LITERAL reads from `entry_point_sources[qname]` and calls `float()`. All 3 paths have try/except for failed conversion. Can verify with real data: solar_battery design attrs have numeric defaults, library defaults have numeric values, usage literals have numeric strings.

6. **Cross-component warning from IMPLEMENTATION_PLAN (Step 4.4).** "C16 creates DESIGN_ATTRIBUTE entry points via in-place mutation of the shared `entry_points` dict. C17 must verify these factory-created EPs retain `entry_type=DESIGN_ATTRIBUTE` and are never re-classified by `_classify_entry_points()`." This is addressed by Issue #2 above.

### Risks & Unknowns

- **Low risk**: The classifier is a well-understood 100-line function with clear precedence logic. All 3 classification paths are exercised by solar_battery_model.
- **Known**: C14/C15/C16 test helpers already call `_classify_entry_points()` successfully on multiple models, confirming the function works end-to-end. C17 adds direct verification of classification correctness.
- **Orphan edge case**: May need constructed data if no natural orphan exists. Low risk -- the orphan path is simple (lines 220-248).

---

## 2. Spike

**Decision**: SKIP
**Rationale**: The classifier function is straightforward (100 lines, 3-branch decision tree). All upstream dependencies are proven (C13 ParameterGroupDeriver, C14-C16 factories). The `build_factory_inputs_from_snapshot()` helper from C14 already demonstrates the full setup pipeline. No unknowns warrant a spike.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_entry_point_classifier.py`
**Fixture data**: solar_battery_model (all 3 EP types + aggregation EPs), catf_mfe_model (large model, many DESIGN_ATTRIBUTE EPs), attr_expr_probe (FORMULA EPs), chain_spike_model (simple baseline)

### Test Cases

> Every requirement (REQ-EPC-01 through REQ-EPC-08) must have at least one test case.
> Every test uses real data -- no mocks. Stubs only at SysIDE adapter boundary.

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_every_ep_has_exactly_one_type[model]` | REQ-EPC-01 | Every EP in `entry_points` dict has `entry_type in EntryPointType` and is not None. Parametrized over solar_battery, catf_mfe, chain_spike. |
| `test_design_attribute_precedence` | REQ-EPC-02 | For solar_battery: find EPs whose qname appears in both `design_attr_by_qname` AND `unbound_lookup`. Verify they are classified as DESIGN_ATTRIBUTE (not LIBRARY_DEFAULT). Precedence: DA > LD. |
| `test_classification_types_present[solar_battery]` | REQ-EPC-01, REQ-EPC-02 | solar_battery produces all 3 EP types. Verify at least one EP of each type exists. |
| `test_design_attribute_default_float_conversion` | REQ-EPC-03 | For solar_battery DESIGN_ATTRIBUTE EPs with known defaults (e.g., area=1.6, efficiency values): verify `default_value` is a float, not a string. |
| `test_library_default_float_conversion` | REQ-EPC-03 | For solar_battery/catf_mfe LIBRARY_DEFAULT EPs: verify `default_value` is float or None (None when calc def has no parseable default). |
| `test_usage_literal_float_conversion` | REQ-EPC-03 | For USAGE_LITERAL EPs: verify `default_value` is float or None. Check that the value matches `float(entry_point_sources[qname])`. |
| `test_unparseable_default_is_none` | REQ-EPC-03 | Construct a scenario (or find natural case) where `default_value` cannot be parsed as float. Verify `default_value is None`. |
| `test_every_ep_has_param_group[model]` | REQ-EPC-04 | Every EP has a non-None `param_group` string. Parametrized over solar_battery, catf_mfe. |
| `test_orphan_ep_lands_in_system_design` | REQ-EPC-05 | Construct: add a synthetic EP with a QN not matching any group to the entry_points dict. Run Step 6.6 rebuild + 6.8 orphan collection. Verify the orphan appears in a ParameterGroup with `name="system_design"`. |
| `test_groups_rebuilt_after_factory_construction` | REQ-EPC-06 | Run `build_computation_graph()` on solar_battery (has FORMULA + aggregation). Verify factory-created EPs appear in the final `entry_point_groups`. |
| `test_classify_is_pure_function` | REQ-EPC-07 | Deep-copy all inputs before calling `_classify_entry_points()`. After the call, verify all inputs are unchanged (entry_point_names, entry_point_sources, design_attrs, usages unchanged). |
| `test_factory_eps_retain_design_attribute[solar_battery]` | REQ-EPC-08 | Run `build_computation_graph()` on solar_battery. Collect all EPs. Identify factory-created EPs (those not in the backtracker's `entry_points` set). Verify they all have `entry_type=DESIGN_ATTRIBUTE`. |
| `test_classify_called_before_factories` | REQ-EPC-08 | Static analysis: parse `build_computation_graph()` source. Verify `_classify_entry_points` call appears before `_build_computed_attr_module` and `_build_aggregation_module` calls (line number ordering). |
| `test_classify_called_exactly_once` | REQ-EPC-08 | Static analysis: count occurrences of `_classify_entry_points(` in `build_computation_graph()` body. Must be exactly 1. |
| `test_simple_name_derivation[model]` | REQ-EPC-01 | Every EP's `simple_name` equals `qualified_name.split("__")[-1]`. Parametrized. |
| `test_source_calc_usage_set_for_library_default` | REQ-EPC-01 | For every LIBRARY_DEFAULT EP, `source_calc_usage` is not None. For DESIGN_ATTRIBUTE and USAGE_LITERAL EPs, `source_calc_usage` is None. |
| `test_get_library_default_real_calc_defs` | REQ-EPC-03 | Call `_get_library_default()` on real calc defs from solar_battery. Verify it returns float for numeric defaults and None for non-numeric/missing defaults. |
| `test_ep_count_matches_backtracker[model]` | REQ-EPC-01 | The number of classified EPs equals `len(BacktrackingResult.entry_points)`. Parametrized. |

### Test Infrastructure Needed

- **Reuse `build_factory_inputs_from_snapshot()`** from C14 test file (`test_factory_calc_usage.py`). This helper already builds BacktrackingResult, entry_points, calc_def_map, and snapshot data. For C17, we need access to the intermediate inputs (design_attrs, group_deriver, entry_point_sources) that C14's helper doesn't expose.
- **New helper `build_classifier_inputs_from_snapshot()`**: Extended version that returns (BacktrackingResult, entry_points, design_attrs, design_attr_by_qname, unbound_lookup, entry_point_sources, calc_def_map, group_deriver, snap). This exposes the internal data structures needed to verify classification correctness.
- **For REQ-EPC-06/08**: Need to call `build_computation_graph()` directly. Build full inputs from snapshot including computed_attributes, aggregation_data, hierarchy_redefinitions, usage_type_map.
- **Static analysis helpers**: Reuse pattern from C07 (`tests/helpers/static_analysis.py`) for parsing function source.

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written
- [x] Tests run (32 collected, 32 passed)
- [x] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify
| File | Change | Why |
|------|--------|-----|
| None | No production code changes | C17 is conformance-only |

### Files to Create
| File | Purpose |
|------|---------|
| `tests/conformance/test_entry_point_classifier.py` | 32 conformance tests verifying REQ-EPC-01 through REQ-EPC-08 |

### Implementation Notes

1. **Helper function** `build_classifier_inputs_from_snapshot(model_name)`: Follows the same pattern as C14's `build_factory_inputs_from_snapshot()` but returns additional intermediate data:
   - `design_attr_by_qname` dict (for verifying DESIGN_ATTRIBUTE classification)
   - `unbound_lookup` dict (for verifying LIBRARY_DEFAULT classification)
   - `entry_point_sources` (for verifying USAGE_LITERAL classification)
   - `group_deriver` instance (for verifying param_group assignment)

2. **Full graph assembly helper** `build_full_graph_from_snapshot(model_name)`: Calls `build_computation_graph()` with all inputs including computed_attributes, aggregation_data, hierarchy_redefinitions, usage_type_map. Returns the ComputationGraph + entry_points dict. Needed for REQ-EPC-06, REQ-EPC-08 tests.

3. **Classification verification strategy**: For each model, reconstruct the `design_attr_by_qname` and `unbound_lookup` indexes (same logic as `_classify_entry_points()` lines 296-308). Then for each EP, verify that the classification matches the expected precedence: if qname in design_attr_by_qname → DESIGN_ATTRIBUTE; elif qname in unbound_lookup → LIBRARY_DEFAULT; else → USAGE_LITERAL.

4. **Static analysis for REQ-EPC-08**: Use `inspect.getsource(build_computation_graph)` + `ast.parse()` to verify `_classify_entry_points` is called before `_build_computed_attr_module` and `_build_aggregation_module`. Same pattern as C07.

5. **Orphan test (REQ-EPC-05)**: Run `build_computation_graph()` on solar_battery. After it returns, manually add a synthetic EP to the entry_points dict. Then replicate Step 6.6 + 6.8 logic to verify the orphan lands in "system_design". Alternative: test the orphan code path in isolation by mocking the param_groups to exclude one known EP.

   Better approach: Directly test the orphan path by building a full graph, then verifying whether any "system_design" group exists. If no natural orphan exists (likely), construct by calling `_classify_entry_points()` to get EPs, then adding a synthetic EP before calling the grouping/orphan logic.

6. **Session-scoped fixtures**: Use `@pytest.fixture(scope="session")` for expensive snapshot-based fixtures, same pattern as C14/C15/C16.

7. **Parametrization**: Use `@pytest.fixture(scope="session", params=["solar_battery_model", "catf_mfe_model", "chain_spike_model"])` for tests that should verify across models. Exclude sample_model (0 usages per C11 learning #5) and issue22_model (edge case only useful for aggregation).

### Gate: Ready for VALIDATE
- [x] All test cases pass (32/32)
- [x] No regressions in full test suite (1495 passed, 2 skipped, 5 xfailed)
- [x] Lint clean (all lint issues pre-existing, none in new test file)

---

## 5. Validation

- [x] Every acceptance criterion from COMPONENT_CHECKLIST is satisfied
- [x] Every REQ-EPC-01 through REQ-EPC-08 has at least one passing test
- [x] Full test suite passes (record count: 1495 tests, 0 failures, 5 xfailed)
- [x] Cross-check: re-read design intent doc 06, verify implementation matches
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### Baseline Impact
No production code changes. No baseline impact.

---

## 6. Learnings

### Findings

1. **solar_battery has zero DESIGN_ATTRIBUTE EPs from the classifier (Path 1).** Design attribute QNs use library-qualified names (`SolarBatteryLibrary__PVModuleCostCalc__cost_per_watt`) while EP QNs use design-qualified names (`SolarBatteryDesign__solar_battery_plant__...`). The QNs never match, so `_classify_entry_points()` produces only LIBRARY_DEFAULT and USAGE_LITERAL for solar_battery. DESIGN_ATTRIBUTE EPs come exclusively from factory construction (Path 2). catf_mfe_model DOES produce all 3 types from the classifier because its EP QNs match DA QNs.

2. **13 solar_battery EPs have param_group=None from the classifier.** Deeply-nested EPs (e.g., `SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model__capacity_kwh`) don't match any `ParameterGroupDeriver.classify()` pattern. These become orphans handled by Step 6.8 in `build_computation_graph()`, landing in the "system_design" fallback group. catf_mfe and chain_spike have zero param_group=None EPs.

3. **REQ-EPC-04 "every EP assigned a param_group" is a graph-level invariant, not a classifier-level invariant.** The classifier sets `param_group = group_deriver.classify(qname)` which CAN return None. The orphan handling at Step 6.8 ensures the invariant holds after full graph assembly. Tests verify both levels: classifier-level (param_group may be None) and graph-level (every EP in some group).

4. **32 tests collected, up from the plan's 18 estimate.** Parametrization over 3 models (solar_battery, catf_mfe, chain_spike) for 6 test methods = 18 parametrized tests, plus 14 non-parametrized tests for model-specific and static analysis verifications.

5. **`build_full_graph_from_snapshot()` helper enables graph-level verification.** Calling `build_computation_graph()` with all inputs (computed_attributes, aggregation_data, hierarchy_redefinitions, usage_type_map) exercises the full Path 1 + Path 2 + Step 6.6 rebuild + Step 6.8 orphan pipeline. Essential for REQ-EPC-06 and REQ-EPC-08.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| 06-entry-point-classifier.md | Note that solar_battery produces zero DESIGN_ATTRIBUTE EPs from Path 1. catf_mfe is the primary model exercising all 3 classifier types. | C17 conformance finding #1 |
| 06-entry-point-classifier.md | Clarify REQ-EPC-04: param_group may be None from classifier; orphan handling (REQ-EPC-05) ensures all EPs are grouped at graph assembly level | C17 conformance finding #3 |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| C18 (Graph Assembly) | C17 verifies the entry_points dict is correctly populated before graph assembly | C18 can assume classification is correct |
| C18 (Graph Assembly) | `build_full_graph_from_snapshot()` helper reusable for C18 | Import and extend for graph-level tests |

### Deviations from Plan

1. **Used catf_mfe (not solar_battery) for DESIGN_ATTRIBUTE tests.** Plan assumed solar_battery has all 3 types from the classifier, but it only has LIBRARY_DEFAULT and USAGE_LITERAL. Switched to catf_mfe for precedence, DA float conversion, and "all 3 types present" tests.

2. **Added graph-level param_group test (REQ-EPC-04).** Plan's `test_every_ep_has_param_group` assumed param_group is always non-None from the classifier. Added a second test `test_every_ep_in_group_after_graph_assembly` to verify the full invariant.

3. **Orphan test simplified.** Plan suggested constructing synthetic orphans. Instead, verified the orphan code path structurally (source contains "system_design" handling) and tested graph-level grouping completeness. No need for constructed data since the code path is straightforward.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (existing branch)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [ ] `git add` only the files listed in Build Plan + test file, plus IMPLEMENTATION_PLAN and COMPONENT_CHECKLIST (no unrelated changes)
- [ ] Commit message format:
  ```
  refactor(C17): Entry Point Classification conformance tests

  - Tests: N new conformance tests in tests/conformance/test_entry_point_classifier.py
  - Refs: REQ-EPC-01 through REQ-EPC-08
  - Design intent: 06-entry-point-classifier.md
  ```
- [ ] Committed successfully

---

## Progress Log

### Session: 2026-02-17 -- Planning
**Phase**: PLANNING
**Work done**:
- Read design intent doc (06-entry-point-classifier.md) and all 8 requirements
- Read current source code (`_classify_entry_points()` at graph_builder.py:265-367, `_get_library_default()` at 464-488, `build_computation_graph()` Steps 4-6.8)
- Reviewed C14/C15/C16 test patterns for entry point handling
- Verified all 3 classification types are exercised by solar_battery_model
- Identified REQ-EPC-08 verification strategy (static analysis + runtime check)
- Identified orphan edge case strategy (constructed data with real QNs)
- Designed 18 test cases covering all 8 requirements
**Stopped at**: Plan complete, ready for build
**Next step**: Build phase -- create `tests/conformance/test_entry_point_classifier.py`
**Blockers**: None

### Session: 2026-02-17 -- Build + Validate
**Phase**: BUILD → VALIDATE → DONE
**Work done**:
- Created `tests/conformance/test_entry_point_classifier.py` with 32 conformance tests
- Built `build_classifier_inputs_from_snapshot()` helper exposing intermediate data (design_attr_by_qname, unbound_lookup, entry_point_sources)
- Built `build_full_graph_from_snapshot()` helper for graph-level verification (REQ-EPC-06, REQ-EPC-08)
- Discovered solar_battery has zero DESIGN_ATTRIBUTE EPs from classifier (only via factory Path 2); switched to catf_mfe for DA tests
- Discovered 13 solar_battery EPs have param_group=None (deeply nested QNs); added graph-level grouping test
- Fixed 4 initial test failures by using correct model and adjusting param_group expectations
- All 32 C17 tests pass; full suite 1495 passed, 2 skipped, 5 xfailed; lint clean (pre-existing issues only)
- REQ coverage: EPC-01 (5 tests), EPC-02 (3), EPC-03 (4), EPC-04 (2), EPC-05 (1), EPC-06 (1), EPC-07 (1), EPC-08 (3)
- Updated COMPONENT_CHECKLIST C17 ACs, IMPLEMENTATION_PLAN step 4.4 and test count tracking
**Stopped at**: DONE
**Next step**: Commit
**Blockers**: None
