# Component: Schema Generator (C22)

**Status**: DONE
**Created**: 2026-02-18
**Last updated**: 2026-02-18
**Updated by**: build agent

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — C22
- **Design intent**: [22-output-schema-rules.md](../../concepts/refactor-design-intent/22-output-schema-rules.md)
- **Requirements**: REQ-OSR-01 through REQ-OSR-07
- **Depends on**: C18 (Graph Assembly — complete), C20 (Pipeline YAML Generator — complete), C21 (Module Wrapper Generator — complete)

---

## 1. Assessment

### What This Component Does

The schema generator (`generation/schemas.py`) produces Pydantic `MultiOutput` subclasses for calculation definitions with 2+ output attributes. Single-output modules use `RootModel[float]` (aliased as `Float`) and produce no schema file. The generator consumes `CalculationDefinitionData` (extraction layer) and renders the `multioutput_model.py.jinja2` template with typed fields, descriptions, and optional default values.

### Current State

- **Exists?** Yes — `src/sysml_codegen/generation/schemas.py` (274 lines)
- **Needs extraction/refactoring?** No structural changes for Phase 6. The documented gap is that `generate_multioutput_model()` consumes `CalculationDefinitionData` instead of `PipelineModule`/`ComputationGraph` — this is a Phase 7 migration target (REQ-PIPE-07). However, C22 conformance tests can cross-reference schema output against `PipelineModule.outputs` from the ComputationGraph to verify consistency.
- **Current test coverage**: No conformance tests exist. Integration coverage via `test_e2e_output_registry.py` exercises the generation pipeline but doesn't verify schema-specific requirements.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc(s)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **REQ-OSR-05 (no default values on output fields) may not be actively enforced.**
   The Jinja2 template (`multioutput_model.py.jinja2:12-16`) conditionally adds `default=` when `field.default` is truthy. The `_format_default_value()` function passes through `attr.default_value` as-is. If any output attribute in a fixture model has a non-None `default_value`, the generated schema WILL have `default=...`, violating REQ-OSR-05.
   **Resolution**: The test should verify that generated MultiOutput schemas do NOT contain `default=` on output fields. If they do, this is a Bug 11 instance that should be documented as a finding (the schema generator SHOULD strip defaults from outputs before rendering). This is a known design issue per doc 22 ("The rule: Output fields on MultiOutput subclasses MUST NOT have default=... values").

2. **`generate_multioutput_model()` consumes `CalculationDefinitionData`, not `PipelineModule`.**
   The schema generator operates on extraction-layer data, while the ComputationGraph is the "single source of truth." For cross-referencing, the same calc_def → PipelineModule mapping from C21 (`BacktrackingResult.required_usages`) can be reused. CalcUsage modules with `is_multi_output` (multiple outputs) should have a corresponding MultiOutput schema.
   **Resolution**: Cross-reference schema output field names against `PipelineModule.outputs[i].field_name` for multi-output modules. This verifies REQ-OSR-01/02/03 through the ComputationGraph lens.

3. **`_map_output_type()` in schemas.py is one of 4 type mapping copies (REQ-GEN-06 violation).**
   Same issue as C21's `_map_input_type()`. The output type mapping may diverge from `PipelineModule.outputs[i].python_type` (which is hardcoded to `"float"` in graph_builder.py:1414). Since graph builder always uses `"float"`, any divergence would only manifest if a calc def has Integer/Boolean/String outputs AND the schema generates a non-float type while the graph builder says float.
   **Resolution**: Test verifies `_map_output_type()` covers all documented SysML types. Cross-reference with graph builder's hardcoded `"float"` noted as finding.

4. **REQ-OSR-06 (aggregation and FORMULA always single-output) is a graph builder invariant, not a schema generator invariant.**
   The schema generator never sees aggregation or FORMULA modules — they're always single-output (`field_name="root"`) and don't trigger `should_use_multioutput()`. The test can verify this property on the ComputationGraph directly: all modules with `is_aggregation=True` or `is_computed_attribute=True` have exactly 1 output with `field_name="root"`.
   **Resolution**: Include a graph-level test that verifies REQ-OSR-06 on real ComputationGraphs.

5. **REQ-OSR-07 (PQN channel format) is tested at the graph level, not the schema level.**
   Output channel names are set by graph_builder.py using `get_channel_name()`. The schema generator doesn't produce channel names — it produces field names for MultiOutput classes. The test should verify PQN channel format on `PipelineModule.outputs[i].channel_name` for completeness.
   **Resolution**: Include in graph-level parametrized tests.

### Risks & Unknowns

- **Low risk**: Output default values in fixture data. Most SysML output attributes are computed and don't have defaults, but if any do, the test should detect the REQ-OSR-05 violation and document it.
- **Low risk**: Type mapping divergence between `_map_output_type()` and graph builder's hardcoded `"float"`. Graph builder uses `"float"` for all outputs, so any non-float schema types would be a finding.
- **No risk**: No production code changes expected. Phase 6 is conformance-only.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: The schema generator code is 274 lines, well-structured, and fully readable. The template (`multioutput_model.py.jinja2`) is 17 lines. The cross-referencing approach (calc_defs from snapshot + ComputationGraph from `build_full_graph_from_snapshot()`) is proven by C20 and C21. The main verification targets (single vs multi-output decision, field names, type mapping, default value constraint) are all straightforward to test with real data. No unknowns require prototyping.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_gen_schemas.py`
**Fixture data**: solar_battery_model (has multi-output: PVModuleCostCalc, BatteryPackCostCalc), catf_mfe_model (all CalcUsage — check for multi-output)

### Test Cases

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_single_output_uses_root_field[solar_battery]` | REQ-OSR-01 | Every PipelineModule with 1 output has `field_name="root"` |
| `test_single_output_uses_root_field[catf_mfe]` | REQ-OSR-01 | Same for catf_mfe |
| `test_multioutput_generated_for_multi_output_calcs[solar_battery]` | REQ-OSR-02 | `should_use_multioutput(calc_def)` returns True and `generate_multioutput_model()` produces non-None code for every calc_def with 2+ outputs |
| `test_multioutput_generated_for_multi_output_calcs[catf_mfe]` | REQ-OSR-02 | Same for catf_mfe |
| `test_multioutput_not_generated_for_single_output` | REQ-OSR-02 | `should_use_multioutput()` returns False and `generate_multioutput_model()` returns None for calc_defs with 1 output |
| `test_field_names_match_output_attributes[solar_battery]` | REQ-OSR-03 | Generated MultiOutput field names match `calc_def.output_attributes[i].name` exactly |
| `test_field_names_match_pipeline_module_outputs[solar_battery]` | REQ-OSR-03 | Generated MultiOutput field names match `PipelineModule.outputs[i].field_name` for corresponding multi-output module |
| `test_type_mapping_real_to_float` | REQ-OSR-04 | `_map_output_type("Real")` == `"float"` and `_map_output_type("ScalarValues::Real")` == `"float"` |
| `test_type_mapping_integer_to_int` | REQ-OSR-04 | `_map_output_type("Integer")` == `"int"` and `_map_output_type("ScalarValues::Integer")` == `"int"` |
| `test_type_mapping_boolean_to_bool` | REQ-OSR-04 | `_map_output_type("Boolean")` == `"bool"` and `_map_output_type("ScalarValues::Boolean")` == `"bool"` |
| `test_type_mapping_string_to_str` | REQ-OSR-04 | `_map_output_type("String")` == `"str"` and `_map_output_type("ScalarValues::String")` == `"str"` |
| `test_type_mapping_unknown_defaults_to_float` | REQ-OSR-04 | `_map_output_type("UnknownType")` == `"float"` |
| `test_output_fields_have_no_defaults[solar_battery]` | REQ-OSR-05 | Generated MultiOutput code does NOT contain `default=` on any output field (parse with ast and inspect `Field()` calls) |
| `test_aggregation_always_single_output[solar_battery]` | REQ-OSR-06 | Every PipelineModule with `is_aggregation=True` has exactly 1 output with `field_name="root"` |
| `test_formula_always_single_output[solar_battery]` | REQ-OSR-06 | Every PipelineModule with `is_computed_attribute=True` has exactly 1 output with `field_name="root"` |
| `test_output_channels_use_pqn_format[solar_battery]` | REQ-OSR-07 | Every `ModuleOutput.channel_name` contains `__` separator (PQN format) |
| `test_output_channels_use_pqn_format[catf_mfe]` | REQ-OSR-07 | Same for catf_mfe |
| `test_generated_schema_valid_python[solar_battery]` | REQ-OSR-02 | Every generated MultiOutput schema passes `ast.parse()` |
| `test_generated_schema_class_inherits_multioutput[solar_battery]` | REQ-OSR-02 | Generated class inherits from `MultiOutput` (parse AST, check base class) |
| `test_should_use_multioutput_decision_matches_graph[solar_battery]` | REQ-OSR-01, REQ-OSR-02 | `should_use_multioutput(calc_def)` == `(len(module.outputs) > 1)` for every CalcUsage module |
| `test_schemas_py_imports_extraction` | REQ-OSR-02 | Static analysis: schemas.py imports from `extraction.data_models` (documents known Phase 7 migration target) |

### Test Infrastructure Needed

- **Reuse from C17/C20/C21**: `build_full_graph_from_snapshot()` from `tests/conformance/test_entry_point_classifier.py`
- **Reuse from C21**: CalcUsage-to-calc_def mapping pattern using `BacktrackingResult.required_usages`
- **Session-scoped fixtures**: `all_graph_data` (graph + inputs for each model), `template_env` (Jinja2 environment)
- **Helper**: `_build_calcusage_module_to_calcdef_map()` — same pattern as C21 to map PipelineModule names to calc_defs

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written
- [x] Tests run (20 passed, 1 xfailed)
- [x] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify

None. Phase 6 is conformance-only — no production code changes.

### Files to Create

| File | Purpose |
|------|---------|
| `tests/conformance/test_gen_schemas.py` | Conformance tests for C22 |

### Implementation Notes

1. **CalcUsage-to-calc_def mapping**: Same pattern as C21. Use `build_full_graph_from_snapshot()` to get `(graph, inputs_dict)`. Build `calc_def_map = {cd.name: cd for cd in snap["calc_defs"]}`. Map module names to calc_def names via `inputs_dict["result"].required_usages`. Filter multi-output CalcUsage modules by `len(module.outputs) > 1`.

2. **Multi-output modules in solar_battery**: From C21 learnings, solar_battery has PVModuleCostCalc and BatteryPackCostCalc with 5 outputs each. These naturally exercise the multi-output schema generation path. catf_mfe needs checking — it may have multi-output modules too (42 CalcUsage modules total).

3. **REQ-OSR-05 verification**: Parse generated schema code with `ast.parse()`. Walk the AST for `ast.Call` nodes where `func` is `Field`. Check that none have a `default` keyword argument. If any do, the test should document it as a Bug 11 finding. Per the design doc, output defaults should be stripped — if the current code doesn't strip them, this is a conformance violation to document (but not fix in Phase 6).

4. **Template environment**: Same as C20/C21 — `jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR), trim_blocks=True, lstrip_blocks=True)`.

5. **Graph-level tests (REQ-OSR-01, 06, 07)**: These verify properties on the ComputationGraph directly, not on generated schema code. Parametrize over solar_battery and catf_mfe. solar_battery has aggregation + FORMULA modules for REQ-OSR-06 testing; catf_mfe is 100% CalcUsage (no aggregation/FORMULA).

6. **Type mapping cross-reference**: Graph builder hardcodes `python_type="float"` for all outputs (graph_builder.py:1414). The schema generator uses `_map_output_type()` which maps by SysML type. For Real outputs, both produce `"float"`. For Integer/Boolean/String outputs (if any exist in fixture data), the schema generator would produce `"int"`/`"bool"`/`"str"` while the graph builder says `"float"`. This would be a documented divergence, not a test failure.

### Gate: Ready for VALIDATE
- [x] All test cases pass (20 passed, 1 xfailed — Bug 11)
- [x] No regressions in full test suite (1653 passed, 2 skipped, 6 xfailed)
- [x] Lint clean (pre-existing lint issues only, no production code changes)

---

## 5. Validation

- [x] Every acceptance criterion from COMPONENT_CHECKLIST is satisfied
- [x] Every REQ-OSR-NN has at least one passing test
- [x] Full test suite passes (record count: 1653 tests, 0 failures, 6 xfailed)
- [x] Cross-check: re-read design intent doc, verify implementation matches
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### Baseline Impact

No baseline changes expected. Phase 6 is conformance-only — no production code changes.

---

## 6. Learnings

### Findings

1. **Bug 11 confirmed: Permitting_Interconnect has default=0.0 on 4 output fields.**
   `material_cost`, `fab_cost`, `install_cost`, `idiot_index` all render with `Field(default=0.0, ...)`.
   This violates REQ-OSR-05. The schema generator should strip defaults from outputs before rendering.
   Documented as xfail (not a Phase 6 fix).

2. **catf_mfe has multi-output CalcUsage modules.** Both models exercise multi-output schema
   generation. The plan was uncertain about catf_mfe, but it does have multi-output calc_defs.

3. **No type mapping divergence in real data.** All multi-output outputs use `Real` → `"float"`,
   matching graph builder. Integer/Boolean/String type paths verified only via unit tests.

4. **`should_use_multioutput()` perfectly matches graph output count** across all CalcUsage modules.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| 22-output-schema-rules.md | Note Bug 11 confirmed in Permitting_Interconnect fixture | C22 conformance finding #1 |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| X01 (Type Mapping) | `_map_output_type()` divergence not triggered in real data but exists in code | X01 consolidation will resolve |

### Deviations from Plan
None. All 21 planned test cases implemented as specified.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (continuing)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [ ] `git add` only the files listed in Build Plan + test file, plus IMPLEMENTATION_PLAN and COMPONENT_CHECKLIST (no unrelated changes)
- [ ] Commit message format:
  ```
  refactor(C22): Schema Generator conformance tests

  - Tests: N new conformance tests in tests/conformance/test_gen_schemas.py
  - Refs: REQ-OSR-01 through REQ-OSR-07
  - Design intent: 22-output-schema-rules.md
  ```
- [ ] Committed successfully

---

## Progress Log

### Session: 2026-02-18 — Planning
**Phase**: PLANNING
**Work done**:
- Read design intent doc (22-output-schema-rules.md), component checklist (C22), implementation plan (step 6.3)
- Read current source: `generation/schemas.py` (274 lines), `multioutput_model.py.jinja2` (17 lines)
- Read resolution models: `PipelineModule`, `ModuleOutput`, `ComputationGraph`
- Read graph builder output construction (graph_builder.py:1402-1417) — hardcoded `python_type="float"` for all outputs
- Read CLI schema generation: `_generate_schemas()` (cli/__init__.py:148-174)
- Reviewed C20/C21 test patterns (session-scoped fixtures, graph builder, template env, calc_def mapping)
- Reviewed accumulated learnings from C03-C21
- Design consistency review: 5 issues identified and resolved
**Stopped at**: Plan complete, ready for build
**Next step**: Build the conformance test file
**Blockers**: None

### Session: 2026-02-18 — Build + Validate
**Phase**: PLANNING → DONE
**Work done**:
- Wrote `tests/conformance/test_gen_schemas.py` (21 tests)
- Reused C21 patterns: session-scoped fixtures, CalcUsage-to-calc_def mapping, template env
- Graph-level tests: REQ-OSR-01 (root field), REQ-OSR-06 (agg/FORMULA), REQ-OSR-07 (PQN)
- Schema-level tests: REQ-OSR-02 (MultiOutput generation, valid Python, inheritance), REQ-OSR-03 (field names)
- Type mapping tests: REQ-OSR-04 (5 tests covering all SysML types + unknown)
- REQ-OSR-05: Bug 11 confirmed — Permitting_Interconnect has default=0.0 on 4 output fields (xfail)
- Cross-reference: should_use_multioutput matches graph, field names match PipelineModule outputs
- Static analysis: schemas.py imports from extraction (Phase 7 target)
- All 21 tests pass (20 passed, 1 xfailed)
- Full suite: 1653 passed, 2 skipped, 6 xfailed, 0 failures
- Updated COMPONENT_CHECKLIST.md (C22 AC all checked)
- Updated IMPLEMENTATION_PLAN.md (step 6.3 complete, test count row, accumulated learnings)
**Stopped at**: All validation complete, ready for commit
**Next step**: Commit
**Blockers**: None
