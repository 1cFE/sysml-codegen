# Component: CalcUsage Module Factory (C14)

**Status**: DONE
**Created**: 2026-02-17
**Last updated**: 2026-02-17
**Updated by**: Build session

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` -- C14
- **Design intent**: [05-module-factory.md](../../concepts/refactor-design-intent/05-module-factory.md) (Section 2)
- **Requirements**: REQ-MF-01, REQ-MF-02, REQ-MF-05, REQ-MF-08
- **Depends on**: C11a/b (BacktrackingResult with typed dispatch -- done), C08 (OutputRegistry -- done)

---

## 1. Assessment

### What This Component Does

`_build_pipeline_module()` transforms a `CalcUsageData` + its `CalculationDefinitionData` + pre-computed `binding_resolutions` into a `PipelineModule`. It is a pure data lookup -- no resolution logic, no shared state mutation. Each calc def input attribute is wired to either an upstream module's output channel (MODULE_OUTPUT) or a user-provided entry point (ENTRY_POINT), determined entirely by the binding_resolutions dict pre-computed by the backtracker.

### Current State

- **Exists?** Yes -- `src/sysml_codegen/resolution/graph_builder.py` lines 1297-1409
- **Needs extraction/refactoring?** No structural changes needed for C14. The function is already cleanly separated within graph_builder.py. Extraction to a standalone module is deferred to Phase 7.
- **Current test coverage**: Existing unit tests in `tests/unit/test_graph_builder.py` use mocks and constructed data. No conformance tests exist that exercise the factory with real extraction data and real binding_resolutions.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc(s)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **Checklist output type mismatch (cosmetic)**: The COMPONENT_CHECKLIST says C14 output is `(PipelineModule, dict[str, EntryPoint])` -- the tuple signature from the design doc's unified factory interface (Section 5). The current implementation returns just `PipelineModule` and reads entry_points by reference rather than creating new ones. This is correct per the design intent: "CalcUsage factories are truly pure data transformers -- lookup only, no resolution logic" (doc 05 Section 5). CalcUsage entry points are pre-created by `_classify_entry_points()` before the factory loop. The checklist describes the target interface; the current implementation achieves the same goal differently. **Resolution**: Test current behavior. Note for Phase 7 if a unified return signature is desired.

2. **Multi-output calc defs may not exist in fixture models**: REQ-MF-08 requires testing both single-output (field_name="root") and multi-output (field_name=attr.name) paths. Need to verify which fixture models have multi-output calc defs during build. If none exist, construct minimal data using real qualified names from snapshots (same pattern as C09 CHAIN override tests). **Resolution**: Test single-output with real data; test multi-output path with constructed data using real qualified names if no natural fixture exercises it.

3. **`entry_points` parameter is read-only in CalcUsage factory**: The function reads `entry_points.get(resolution.qualified_name)` for ENTRY_POINT bindings but never writes to it. This confirms the "pure data transformer" requirement (REQ-MF-01) -- the factory has no side effects. The entry_points dict is populated upstream. **Resolution**: Include a test that copies entry_points before/after and verifies no mutation.

### Risks & Unknowns

- **Low risk**: The function is simple (110 lines), well-understood, and already passes existing unit tests. No resolution logic, no registry lookups, no complex dispatch.
- **Unknown**: Whether any fixture model has multi-output calc defs. Likely not (TEAx convention is single-output per module). Will resolve during build with a parametrized check.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: The CalcUsage factory is the simplest of the three factory types -- pure lookup with no resolution logic, no registry access, no strategy chains. The current implementation at graph_builder.py:1297-1409 is well-understood from reading the code. All inputs are available from existing infrastructure (build_backtracker_from_snapshot helper from C11). The only unknown (multi-output fixtures) is trivially resolved during the build phase. No spike needed.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_factory_calc_usage.py`
**Fixture data**: solar_battery_model, catf_mfe_model, chain_spike_model (via build_backtracker_from_snapshot helper)

### Test Infrastructure Needed

**Helper**: Reuse `build_backtracker_from_snapshot()` from `tests/conformance/test_backtracker.py`. This builds OutputRegistry + BacktrackingResult from extraction snapshots. The factory also needs `_classify_entry_points()` and `calc_def_map` -- these are built in `build_computation_graph()` Steps 1 and 4.

**New helper**: `build_factory_inputs_from_snapshot(model_name)` -- wraps `build_backtracker_from_snapshot()` and adds the `calc_def_map` and `entry_points` dict needed to call `_build_pipeline_module()`. Returns `(BacktrackingResult, entry_points, calc_def_map, snap)`.

The helper replicates Steps 1 + 4 of `build_computation_graph()`:
1. Build `calc_def_map = {cd.name: cd for cd in snap["calc_defs"]}`
2. Build `entry_points` via `_classify_entry_points()` with the BacktrackingResult
3. Return all components needed to call `_build_pipeline_module()` for any usage in `result.required_usages`

### Test Cases

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_pure_data_transformer_no_mutation[model]` | REQ-MF-01 | Call factory, verify entry_points dict and binding_resolutions dict are unchanged (deep copy comparison). Parametrized over 3 models. |
| `test_returns_pipeline_module[model]` | REQ-MF-01 | Return type is PipelineModule. Module has non-empty name, module_type, outputs. Parametrized over 3 models. |
| `test_fail_fast_missing_binding_resolution` | REQ-MF-02 | Call with binding_resolutions missing a required key. Verify ValueError with "ADR-003 VIOLATION" message. Uses real CalcUsageData from solar_battery. |
| `test_fail_fast_missing_entry_point` | REQ-MF-02 | Call with entry_points missing a required ENTRY_POINT resolution target. Verify ValueError with "ADR-003 VIOLATION" message. Uses real CalcUsageData with ENTRY_POINT binding. |
| `test_every_input_has_exactly_one_source[model]` | REQ-MF-05 | For every module built from every required_usage in 3 models: every ModuleInput.source.source_type in {"module_output", "entry_point"}. |
| `test_module_output_wiring[model]` | REQ-MF-05 | For MODULE_OUTPUT bindings: source.source_type=="module_output", source.producer_channel matches binding_resolutions[key].qualified_name. Parametrized. |
| `test_entry_point_wiring[model]` | REQ-MF-05 | For ENTRY_POINT bindings: source.source_type=="entry_point", source.qualified_name matches binding_resolutions[key].qualified_name, source.param_group matches entry_points[qn].param_group. |
| `test_single_output_field_name_root[model]` | REQ-MF-08 | For calc defs with exactly 1 output_attribute: module.outputs[0].field_name == "root". Verified across all modules from 3 models. |
| `test_multi_output_field_names_match_attrs` | REQ-MF-08 | For a calc def with >1 output_attribute: each output.field_name == corresponding attr.name. Constructed from real QNs if no natural fixture exercises this. |
| `test_channel_name_is_pqn[model]` | REQ-MF-08 | Every output channel_name == get_channel_name(usage.qualified_name, output_attr.name). Verified across all modules. |
| `test_module_name_matches_eqn[model]` | REQ-MF-01 | module.name == get_module_name(usage.qualified_name) for every module built. |
| `test_module_type_derives_from_calc_def[model]` | REQ-MF-01 | module.module_type == derive_module_type(calc_def.qualified_name) for every module built. |
| `test_input_count_matches_calc_def[model]` | REQ-MF-05 | len(module.inputs) == len(calc_def.input_attributes) for every module. |
| `test_output_count_matches_calc_def[model]` | REQ-MF-08 | len(module.outputs) == len(calc_def.output_attributes) for every module. |
| `test_wiring_covers_all_bindings[model]` | REQ-MF-02 | Every input_attribute in the calc_def has a corresponding ModuleInput. No input_attribute is missed. |
| `test_execution_order_assigned` | REQ-MF-01 | execution_order parameter is passed through to module.execution_order. |
| `test_default_flags` | REQ-MF-01 | is_computed_attribute==False, is_aggregation==False, compilability==UNKNOWN for CalcUsage modules (flags set externally by caller). |

**Model parametrization**: `["solar_battery_model", "catf_mfe_model", "chain_spike_model"]`
- solar_battery: 15 calc defs, mix of MODULE_OUTPUT and ENTRY_POINT bindings
- catf_mfe: 21 calc defs, cross-package resolution, deepest binding chains
- chain_spike: 3 calc defs, simple but exercises core path

### Gate: Ready for BUILD

- [x] Test file exists with all test cases written
- [x] Tests run (expected: all PASS -- conformance-only, no code changes)
- [x] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify

None -- C14 is conformance-only. No production code changes.

### Files to Create

| File | Purpose |
|------|---------|
| `tests/conformance/test_factory_calc_usage.py` | C14 conformance tests (16+ test cases) |

### Implementation Notes

1. **Helper pattern**: Follow the `build_backtracker_from_snapshot()` pattern from test_backtracker.py. Add `build_factory_inputs_from_snapshot()` that also runs `_classify_entry_points()` to produce the entry_points dict. This helper lives at the top of the test file (like test_backtracker.py's helper).

2. **Import `_build_pipeline_module` directly**: The function is in `__all__` of graph_builder.py (line 1412), so it's a supported import even though it has a leading underscore.

3. **Also import `_classify_entry_points`**: Needed to build the entry_points dict. Also in `__all__` (not listed but used by `build_computation_graph`). If not in `__all__`, import from the module directly -- it's a conformance test, not production code.

   Actually checking graph_builder.py `__all__` -- `_classify_entry_points` is NOT in `__all__`. Import it directly: `from sysml_codegen.resolution.graph_builder import _classify_entry_points`. This is acceptable for test code.

4. **ParameterGroupDeriver needed for entry point classification**: `_classify_entry_points()` takes a `group_deriver` parameter. Build it from snapshot data using the same pattern as `build_pipeline_context()` in initialization.py.

5. **Session-scoped fixtures**: The build_backtracker_from_snapshot and factory_inputs helpers are expensive. Use `@pytest.fixture(scope="session")` for each model.

6. **Multi-output test**: Check across all 3 models for calc defs with `len(output_attributes) > 1`. If none found, construct a minimal test using:
   - Real CalcUsageData from a solar_battery usage (modify in-place for test only)
   - A calc_def with 2 output_attributes (constructed from real AttributeInfo objects)
   - Appropriate binding_resolutions
   This follows the C09 pattern (constructed CHAIN override data using real QNs).

7. **Deep copy for purity test**: Use `copy.deepcopy()` on entry_points and binding_resolutions before the call, compare after. For binding_resolutions (Pydantic BaseModel values), compare via `.model_dump()`.

### Gate: Ready for VALIDATE

- [x] All test cases pass (48 passed)
- [x] No regressions in full test suite (1397 passed, 5 xfailed)
- [x] Lint clean (all lint errors are pre-existing in untouched production code)

---

## 5. Validation

- [x] Every acceptance criterion from COMPONENT_CHECKLIST is satisfied
- [x] Every REQ-MF-01, REQ-MF-02, REQ-MF-05, REQ-MF-08 has at least one passing test
- [x] Full test suite passes (record count: 1397 tests, 0 failures, 5 xfailed)
- [x] Cross-check: re-read design intent doc, verify implementation matches
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### Baseline Impact

None. C14 is conformance-only -- no production code changes, no output changes.

---

## 6. Learnings

### Findings
1. **No natural multi-output calc defs in any fixture model.** All 39 calc defs across 3 models have exactly 1 output_attribute. Multi-output path tested with constructed data using `dataclasses.replace()` on a real calc_def. Same pattern as C09 (constructed CHAIN override data).
2. **build_factory_inputs_from_snapshot() is a clean superset of build_backtracker_from_snapshot().** Adds calc_def_map, ParameterGroupDeriver, and _classify_entry_points() on top. Reusable for C15-C18.
3. **48 tests vs 16 planned test cases.** The plan listed 16 logical test cases; parametrization across 3 models expanded to 48 collected tests. The 2 fail-fast tests and multi-output test are model-specific (not parametrized).

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| None | — | No design doc issues discovered |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| C15 (FORMULA Factory) | Same helper pattern applies | Reuse build_factory_inputs_from_snapshot helper |
| C16 (Aggregation Factory) | Same helper pattern applies | Extend helper with aggregation data |
| C17 (Entry Point Classification) | Depends on C14 test outputs | C17 can verify classification using same fixtures |

### Deviations from Plan
1. **Spike skipped as planned.** No unknowns emerged during build.
2. **Test structure uses pytest classes instead of flat functions.** Grouped by requirement for clarity: TestPureDataTransformer (REQ-MF-01), TestFailFast (REQ-MF-02), TestInputWiring (REQ-MF-05), TestOutputNaming (REQ-MF-08).
3. **Two purity tests instead of one.** Split into `test_no_mutation_of_entry_points` and `test_no_mutation_of_binding_resolutions` for clearer failure messages.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (continuing existing branch)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [ ] `git add` only the files listed in Build Plan + test file, plus IMPLEMENTATION_PLAN and COMPONENT_CHECKLIST (no unrelated changes)
- [ ] Commit message format:
  ```
  refactor(C14): CalcUsage Module Factory conformance tests

  - Tests: N new conformance tests in tests/conformance/test_factory_calc_usage.py
  - Refs: REQ-MF-01, REQ-MF-02, REQ-MF-05, REQ-MF-08
  - Design intent: 05-module-factory.md
  ```
- [ ] Committed successfully

---

## Progress Log

### Session: 2026-02-17 -- Planning
**Phase**: PLANNING
**Work done**:
- Read all context: IMPLEMENTATION_PLAN (step 4.1), COMPONENT_CHECKLIST (C14), design doc 05, graph_builder.py source, data models, Phase 3 audit
- Completed design consistency review -- 3 issues found, all resolved
- Designed 16 test cases covering all 4 requirements
- Made SKIP decision for spike (simple lookup function, no unknowns)
**Stopped at**: Plan complete, ready for build
**Next step**: Build phase -- create test file, run tests, validate
**Blockers**: None

### Session: 2026-02-17 -- Build + Validate
**Phase**: DONE
**Work done**:
- Created `tests/conformance/test_factory_calc_usage.py` (48 tests, 4 test classes)
- Built `build_factory_inputs_from_snapshot()` helper: wraps backtracker + adds calc_def_map, ParameterGroupDeriver, _classify_entry_points
- All 48 tests pass on first run (conformance-only, no production code changes)
- Full suite: 1397 passed, 5 xfailed, 0 failures
- No mocks (grep verified)
- Updated COMPONENT_CHECKLIST (5 ACs checked), IMPLEMENTATION_PLAN (step 4.1 marked complete, test count tracking updated)
- Validated all 4 requirements have passing tests: REQ-MF-01 (7 tests), REQ-MF-02 (3 tests), REQ-MF-05 (4 tests), REQ-MF-08 (4 tests)
- Cross-checked design doc 05 Section 2 — implementation matches
**Stopped at**: DONE — ready for commit
**Next step**: Commit, then proceed to C15 (FORMULA Module Factory)
**Blockers**: None
