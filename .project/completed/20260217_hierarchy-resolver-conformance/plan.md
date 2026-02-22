# Component: Hierarchy Resolver Conformance (C06)

**Status**: DONE
**Created**: 2026-02-17
**Last updated**: 2026-02-17
**Updated by**: C06 build session

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — C06
- **Design intent**: [25-hierarchy-resolver.md](../../concepts/refactor-design-intent/25-hierarchy-resolver.md), [13-aggregation-scoping.md](../../concepts/refactor-design-intent/13-aggregation-scoping.md)
- **Requirements**: REQ-HR-01 through REQ-HR-07
- **Depends on**: C01 (Data Models), C02 (Naming Conventions), C03 (Extractor) — all complete

---

## 1. Assessment

### What This Component Does

The hierarchy resolver (`extraction/hierarchy_resolver.py`) is a pure extraction module that walks the SysIDE AST to extract structural patterns from PartDefinitions: `:>>` redefinition classification, multiplicity extraction, and aggregation expression transformation (decomposing `sum()` calls into typed SumTerm/SingletonTerm/LocalTerm terms with parametric multiply). It produces `HierarchyExtractionResult` consumed by downstream orchestration (virtual binding rewrite, aggregation scoping, literal value propagation).

### Current State

- **Exists?** Yes — `src/sysml_codegen/extraction/hierarchy_resolver.py` (573 lines)
- **Needs extraction/refactoring?** No structural changes needed for conformance. The module is already cleanly separated in the extraction layer.
- **Current test coverage**: `tests/unit/test_hierarchy_resolver.py` has mock-based unit tests for data model construction, reconstruct_expression handling, redefinition scanning, and deep-path resolution. No real-data conformance tests exist yet.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc(s)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **Doc reference mismatch in COMPONENT_CHECKLIST**: Checklist says C06 doc refs are `[01-extraction.md]` and `[13-aggregation-scoping.md]`, but `IMPLEMENTATION_PLAN.md` step 1.6 says `[25-hierarchy-resolver.md]` and `[13-aggregation-scoping.md]`. Doc 25 is the detailed design intent doc for hierarchy resolver specifically, and contains REQ-HR-01 through REQ-HR-07. **Resolution**: Use doc 25 as the authoritative requirement source. The checklist should be updated to reference doc 25.

2. **"Template detection (is_template)" AC is ambiguous**: The checklist AC says "Template detection (is_template) correct for all fixture models" but `hierarchy_resolver.py` has no `is_template` concept. The `is_template` field exists on `CalcUsageData` (covered by C03/REQ-EXT-05). **Resolution**: Interpret this AC as verifying that `part_usage_names` correctly maps assembly PartDefs to their child PartUsage names — this is the hierarchy resolver's contribution to template/instance identification. The `part_usage_names` dict enables downstream `find_instance_paths_for_partdef()` (C10) to discover which PartDefs are assembly templates.

3. **REQ-HR-07 alias detection has zero fixture coverage**: All 20 aggregation expressions in solar_battery have empty `aliases` lists. No CHAIN sibling redefinition has `source_path` ending with an aggregation attribute_name in any fixture model. **Resolution**: Document as coverage gap. The code path exists (`hierarchy_resolver.py:550-557`) and is verifiable by checking that: (a) the logic runs without error on real data, (b) the zero-alias result is correct given the SysML model structure. Cannot test the positive case without a fixture model that has CHAIN aliases. Issue22 model also has empty aliases.

4. **Deferred Issue #1 (.() syntax) reassigned to C06 but not reproducible in snapshots**: The `.()` syntax bug was from `reconstruct_expression()` in `expression_utils.py`, called by `_walk_aggregation_ast()`. The bug was fixed in commit `20b720e` before snapshot capture, so all 20 transformed expressions are clean. **Resolution**: Verify via static analysis that FCE-before-OE ordering is maintained (REQ-HR-05, which prevents the root cause). The `.()` symptom is gone; the invariant test prevents regression.

5. **AST fields null in snapshots**: `expression_ast` on both `RedefinitionData` and `AggregationExpressionData` is `None` in snapshots (serialization boundary, Phase 0 Learning #2). Cannot re-execute `build_aggregation_expression()` or `_walk_aggregation_ast()` from snapshot data. **Resolution**: Test the output properties of the extraction result (redefinition types, multiplicity values, term classifications, transformed expressions) rather than re-running the extraction functions. Static analysis for dispatch ordering.

6. **Checklist has no explicit REQ-HR-XX references**: Unlike other checklist entries, C06 doesn't list REQ IDs. **Resolution**: The implementation plan step 1.6 specifies REQ-HR-01 through REQ-HR-07 as acceptance criteria. These come from doc 25.

### Risks & Unknowns

- **Low risk**: All snapshot data is captured and stable. No JVM dependency for conformance tests.
- **Coverage gap**: REQ-HR-07 (alias detection) positive case untestable with current fixtures. The code path has zero real-data exercise.
- **issue22_model edge case**: Has a SumTerm with `multiplicity_attr=None` and `multiplicity_count=None` — a no-multiplicity sum edge case worth validating as a negative test for REQ-HR-06.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: The hierarchy resolver is a stable, already-working extraction module with 573 lines of well-documented code. The snapshot data provides rich real-data coverage (78 redefinitions, 13 design overrides, 3 multiplicities, 20 aggregation expressions in solar_battery). All requirements are clear and testable via snapshot output verification + static source analysis. No unknowns that could invalidate the build plan.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_hierarchy_resolver.py`
**Fixture data**: solar_battery_model (primary — rich hierarchy data), issue22_model (edge cases), all 6 models for cross-model checks

### Test Cases

> Every requirement (REQ-HR-NN) must have at least one test case.
> All tests use real snapshot data — no mocks. Static analysis uses Python ast module on real source.

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_req_hr_01_every_redef_has_valid_type` | REQ-HR-01 | Every RedefinitionData.redefinition_type in {LITERAL, CHAIN, EXPRESSION} across all models |
| `test_req_hr_01_all_three_types_present_solar_battery` | REQ-HR-01 | solar_battery has all 3 RedefinitionType values: 54 CHAIN, 4 LITERAL, 20 EXPRESSION |
| `test_req_hr_01_redef_type_exclusive` | REQ-HR-01 | Each redefinition has exactly one type (not None, is valid enum member) |
| `test_req_hr_02_chain_includes_both_dotted_and_bare` | REQ-HR-02 | CHAIN redefs in solar_battery include both dotted-path (FCE pattern: `x.y`) and bare-name (FRE pattern: no `.`) source_paths |
| `test_req_hr_02_fce_and_fre_both_produce_chain` | REQ-HR-02 | No CHAIN redef has redefinition_type other than CHAIN; both source_path patterns map to same type |
| `test_req_hr_03_design_overrides_deep_path` | REQ-HR-03 | All 13 solar_battery design_overrides have `is_deep_path=True` |
| `test_req_hr_03_deep_path_target_populated` | REQ-HR-03 | All deep-path overrides have non-empty `target_path` with >= 2 segments |
| `test_req_hr_03_shallow_redefs_not_deep` | REQ-HR-03 | Non-deep-path redefinitions have `is_deep_path=False` and empty `target_path` |
| `test_req_hr_04_multiplicity_counts_correct` | REQ-HR-04 | solar_battery: pv_module=20, inverter=4, battery_pack=8 |
| `test_req_hr_04_multiplicity_integer_type` | REQ-HR-04 | All multiplicity `count` values are `int` (not float, not off-by-one) |
| `test_req_hr_04_count_attribute_name_populated` | REQ-HR-04 | All multiplicities with non-None count have non-None `count_attribute_name` |
| `test_req_hr_05_fce_before_oe_in_walk_aggregation_ast` | REQ-HR-05 | Static analysis: in `_walk_aggregation_ast()`, `is_instance(node, "FeatureChainExpression")` appears at a lower line number than `is_instance(node, "OperatorExpression")` |
| `test_req_hr_05_fce_before_oe_comment_present` | REQ-HR-05 | The FCE check in `_walk_aggregation_ast()` has the invariant comment "MUST be before OperatorExpression" |
| `test_req_hr_06_sum_terms_have_multiplicity` | REQ-HR-06 | All SumTerms in solar_battery have non-None `multiplicity_attr` and `multiplicity_count` |
| `test_req_hr_06_transformed_expression_has_parametric_multiply` | REQ-HR-06 | Transformed expressions with sum_terms contain `(mult_attr * child.attr)` pattern |
| `test_req_hr_06_entry_points_contain_multiplicity_attrs` | REQ-HR-06 | For expressions with sum_terms, entry_points includes the multiplicity_attr names |
| `test_req_hr_06_no_multiplicity_edge_case_issue22` | REQ-HR-06 | issue22 SumTerm has `multiplicity_attr=None` (no named count attribute) — verify the edge case is handled |
| `test_req_hr_07_alias_detection_zero_result_correct` | REQ-HR-07 | All 20 solar_battery aggregation expressions have empty aliases — correct because no CHAIN sibling source_path ends with an aggregation attribute_name |
| `test_req_hr_07_alias_field_exists_and_is_list` | REQ-HR-07 | Every AggregationExpressionData has `aliases` field of type `list` |

**Additional tests (checklist AC coverage):**

| Test | AC | What it verifies |
|------|-----|------------------|
| `test_part_usage_names_populated` | Template detection | solar_battery part_usage_names has entries for assembly PartDefs (Solar_Array, Battery_System, etc.) |
| `test_part_usage_names_child_names_correct` | Template detection | Solar_Array's children include {"pv_module", "inverter", "array_bos"} |
| `test_part_usage_names_all_models` | Template detection | part_usage_names populated correctly across all models with hierarchy data |
| `test_usage_type_map_populated` | Parent/child hierarchy | solar_battery usage_type_map maps (parent_qn, child_name) → type PartDef QN |
| `test_usage_type_map_tuple_keys` | Parent/child hierarchy | All usage_type_map keys are `tuple[str, str]` (deserialized correctly) |
| `test_term_type_all_three_present` | Aggregation term classification | solar_battery aggregation expressions collectively have all 3 term types |
| `test_singleton_terms_have_dotted_source_path` | FCE→SingletonTerm | Every SingletonTerm.source_path contains `.` (dotted FCE pattern, not bare name) |
| `test_local_terms_have_bare_name` | FRE→LocalTerm | Every LocalTerm.attribute_name does NOT contain `.` (bare name FRE pattern) |
| `test_sum_terms_have_child_dot_attr` | SumTerm structure | Every SumTerm has non-empty part_usage_name and attribute_name |
| `test_transformed_expression_valid_python` | Expression validity | All 20 transformed expressions pass `ast.parse()` as valid Python (no `.()` syntax) |
| `test_cross_model_issue22_hierarchy` | Cross-model | issue22 has 2 redefinitions, 1 multiplicity, 1 aggregation expression |
| `test_cross_model_no_hierarchy_models` | Cross-model | sample_model and chain_spike_model have empty hierarchy data |
| `test_hierarchy_data_structure_complete` | Data integrity | HierarchyExtractionResult has all 7 expected fields |
| `test_aggregation_expression_count` | Data integrity | solar_battery has exactly 20 aggregation expressions, one per EXPRESSION-type redef |

**Estimated test count**: ~33 tests

### Test Infrastructure Needed

- Existing fixtures from conftest.py are sufficient (extraction_snapshots, solar_battery_snapshot, issue22_snapshot)
- Static analysis tests use Python `ast` module on source file (same pattern as C04)
- No new fixtures or helpers needed

### Gate: Ready for BUILD

- [x] Test file exists with all test cases written
- [x] Tests run (expected: most/all PASS since testing snapshot output properties)
- [x] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify

| File | Change | Why |
|------|--------|-----|
| None | No production code changes expected | C06 is a conformance-only component — verifying existing extraction output |

### Files to Create

| File | Purpose |
|------|---------|
| `tests/conformance/test_hierarchy_resolver.py` | Conformance tests for REQ-HR-01 through REQ-HR-07 plus checklist ACs |

### Implementation Notes

1. **All tests verify snapshot output, not re-execution**: Since AST fields are null in snapshots, tests verify the properties of the already-extracted data (redefinition types, multiplicity values, term classifications, transformed expressions). This is the correct approach — the snapshot represents the ground truth output of `extract_hierarchy_data()`.

2. **Static analysis for REQ-HR-05**: Use Python `ast` module to parse `hierarchy_resolver.py` source and verify FCE `is_instance` check appears before OE check in `_walk_aggregation_ast()`. Same pattern as C04's REQ-AST-01 tests.

3. **solar_battery is the primary test model**: 78 redefs, 13 design overrides, 3 multiplicities, 20 aggregation expressions. issue22 provides edge cases (no multiplicity attribute on SumTerm). catf_mfe has part_usage_names/usage_type_map but zero hierarchy extraction items.

4. **Expected test counts from snapshots (regression anchors)**:
   - solar_battery redefinitions: 54 CHAIN + 4 LITERAL + 20 EXPRESSION = 78
   - solar_battery design_overrides: 13 (all LITERAL, all deep-path)
   - solar_battery multiplicities: 3 (pv_module=20, inverter=4, battery_pack=8)
   - solar_battery aggregation_expressions: 20 (4 owning parts x 5 attributes each)
   - issue22 aggregation_expressions: 1 (total_cost with null multiplicity)

5. **REQ-HR-07 coverage gap**: Document that alias detection positive case has zero fixture coverage. The empty aliases result in solar_battery is correct (no matching siblings), not a bug.

6. **Follow C05 test patterns**: Use `@pytest.mark.req("REQ-HR-XX")` class grouping, parametrize where useful, use snapshot convenience fixtures.

### Gate: Ready for VALIDATE

- [x] All test cases pass (36 tests, 0 failures)
- [x] No regressions in full test suite (1022 passed, 2 pre-existing spike failures)
- [x] Lint clean (`uv run ruff check tests/conformance/test_hierarchy_resolver.py`)

---

## 5. Validation

- [x] Every acceptance criterion from COMPONENT_CHECKLIST is satisfied
- [x] Every REQ-HR-NN has at least one passing test (21 req-marked tests across 7 requirements)
- [x] Full test suite passes (record count: 1022 tests, 0 failures; 2 pre-existing spike failures excluded)
- [x] Cross-check: re-read design intent doc, verify implementation matches
- [x] No unresolved TODOs or FIXMEs in new/modified code

### Baseline Impact

No baseline impact expected — C06 is conformance-only (no production code changes).

---

## 6. Commit

**Branch**: `cost-pattern-refactor` (current branch)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [x] `git add` only the files listed in Build Plan + test file (no unrelated changes)
- [ ] Commit message format:
  ```
  refactor(C06): Hierarchy Resolver conformance tests

  - Tests: 36 new conformance tests in tests/conformance/test_hierarchy_resolver.py
  - Refs: REQ-HR-01 through REQ-HR-07
  - Design intent: 25-hierarchy-resolver.md, 13-aggregation-scoping.md
  ```
- [ ] Committed successfully

---

## 7. Learnings

### Findings

1. **36 tests, not 33**: Plan estimated ~33 tests. Actual count is 36 due to parametrize expanding multiplicity tests (3 params) and cross-model no-hierarchy tests (2 params) into individual test items. The logical test case count matches the plan.
2. **All tests pass on first run**: Unlike TEST→BUILD components, C06 conformance tests verify snapshot output properties, so all tests passed immediately. No production code changes needed.
3. **issue22 edge case confirmed**: The `multiplicity_attr=None, multiplicity_count=None` edge case on issue22's SumTerm is correct — the widget PartUsage has multiplicity `[3]` but `count_attribute_name` is None (no named count attribute in the model), so the parametric multiply transformation is skipped.
4. **Static analysis helper reuse**: Copied `_find_is_instance_calls_in_function` and `_is_syside_is_instance_call` from C04 rather than importing. These are test utilities specific to static analysis verification; sharing via import would create coupling between conformance test files.

### Design Doc Updates Needed

| Doc | What to update | Why |
|-----|---------------|-----|
| COMPONENT_CHECKLIST.md | C06 doc reference: change `01-extraction.md` to `25-hierarchy-resolver.md` | Checklist references wrong design doc; doc 25 has the actual REQ-HR-XX requirements |
| COMPONENT_CHECKLIST.md | C06: add explicit REQ-HR-01 through REQ-HR-07 references | Missing from checklist (other entries have explicit REQ refs) |
| COMPONENT_CHECKLIST.md | C06: clarify "Template detection (is_template)" AC — should say "part_usage_names correctly maps assembly PartDefs to child names" | is_template doesn't exist in hierarchy_resolver.py; ambiguous AC |
| 25-hierarchy-resolver.md | Note REQ-HR-07 alias detection has zero fixture coverage | No fixture model exercises CHAIN sibling alias detection |

### Cross-Component Impact

| Component | Impact | Action needed |
|-----------|--------|---------------|
| C07 (AST Dispatch Invariant) | REQ-HR-05 overlaps with REQ-AST-05. C06 tests FCE-before-OE in `_walk_aggregation_ast()` only; C07 covers all 8+ dispatch sites | C07 can skip `_walk_aggregation_ast()` or include it for completeness |
| C10 (Aggregation Scoping) | part_usage_names verified here feeds `find_instance_paths_for_partdef()` in C10 | C10 can trust part_usage_names correctness |

### Deviations from Plan

None. All test cases from the plan were implemented. No production code changes were needed.

---

## Progress Log

### Session: 2026-02-17 — C06 Planning
**Phase**: PLANNING
**Work done**:
- Read design intent docs (25-hierarchy-resolver.md, 13-aggregation-scoping.md, 19-ast-dispatch-invariant.md)
- Read current source (hierarchy_resolver.py, 573 lines)
- Analyzed snapshot data: solar_battery has rich hierarchy data (78 redefs, 13 overrides, 3 mults, 20 aggs); catf_mfe has zero; issue22 has minimal
- Verified Deferred Issue #1 (.() syntax) not present in snapshot data
- Identified 6 design consistency issues (all resolved)
- Mapped all 7 REQ-HR requirements to concrete test cases
- Produced complete plan with ~33 test cases
**Stopped at**: Plan complete, ready for BUILD
**Next step**: Build the conformance test file following this plan
**Blockers**: None

### Session: 2026-02-17 — C06 Build
**Phase**: BUILD → VALIDATE → DONE
**Work done**:
- Verified snapshot data counts against plan expectations (all matched)
- Created `tests/conformance/test_hierarchy_resolver.py` with 36 test cases
- All 36 tests pass on first run (0.21s)
- Full test suite: 1022 passed, 0 failures (2 pre-existing spike test failures excluded)
- Lint clean after auto-fix of import sorting
- No mocks used (verified by grep)
- No TODOs or FIXMEs
- All validation checks green
- REQ coverage: 21 req-marked tests cover REQ-HR-01 through REQ-HR-07
- 15 additional AC tests cover checklist criteria
**Stopped at**: DONE — ready for commit
**Next step**: Commit
**Blockers**: None
