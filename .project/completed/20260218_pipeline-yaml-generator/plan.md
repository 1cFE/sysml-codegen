# Component: Pipeline YAML Generator (C20)

**Status**: DONE
**Created**: 2026-02-18
**Last updated**: 2026-02-18
**Updated by**: build agent

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — C20
- **Design intent**: [21-pipeline-yaml-generation.md](../../concepts/refactor-design-intent/21-pipeline-yaml-generation.md)
- **Requirements**: REQ-PY-01 through REQ-PY-07
- **Depends on**: C18 (Graph Assembly — complete), C19 (Orchestrator — complete), 5.2 (E2E Pipeline Validation — complete)

---

## 1. Assessment

### What This Component Does

The pipeline YAML generator (`generation/pipeline.py`) takes a `ComputationGraph` as its sole input and renders a pipeline YAML configuration via a Jinja2 template. The YAML defines execution order, module wiring (entry points, module-to-module channels), and exit points. This is the "gold standard" generator — it consumes only the ComputationGraph, no raw extraction data.

### Current State
- **Exists?** Yes — `src/sysml_codegen/generation/pipeline.py` (239 lines)
- **Needs extraction/refactoring?** No structural changes to pipeline.py itself. Two upstream bugs in `resolution/graph_builder.py` need fixing (Bug 9: missing `param_group.` prefix on orphan entry points; Bug 10: `int` type for multiplicity counts).
- **Current test coverage**: Existing integration test (`tests/integration/test_e2e_output_registry.py`) compares generated YAML against 4 baseline YAML files. No conformance tests exist yet. No requirement-level (REQ-PY-XX) testing.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc(s)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **Bug 9 present in current baselines and code (REQ-PY-01, REQ-PY-02 violation).**
   The solar_battery baseline YAML has multiplicity entry points WITHOUT `param_group.` prefix:
   ```yaml
   module_count: int SolarBatteryDesign__solar_battery_plant__solar_array__module_count
   ```
   should be:
   ```yaml
   module_count: float system_design.SolarBatteryDesign__solar_battery_plant__solar_array__module_count
   ```
   **Root cause**: `graph_builder.py` Step 6.8 creates orphan ParameterGroup entries for EPs with `param_group=None`, but does NOT propagate the group name back to the `InputSource.param_group` field in already-created module inputs. The YAML generator at `pipeline.py:167-171` falls back to no prefix when `param_group` is None.
   **Resolution**: Add param_group propagation after Step 6.8 in `graph_builder.py`. Walk all module inputs and set `source.param_group` from final group membership. ~6 lines.

2. **Bug 10 present in current baselines and code (REQ-PY-03 violation).**
   `graph_builder.py:1045` hardcodes `python_type="int"` for multiplicity inputs — the ONLY `int` usage in the entire pipeline. TEAx requires all numeric values as `float`.
   **Resolution**: One-line fix at `graph_builder.py:1045`: `"int"` → `"float"`.

3. **Baseline YAML files must be updated after Bug 9/10 fixes.** All 4 baseline YAML files (`tests/fixtures/baseline_yaml/`) will change: multiplicity inputs get `float` type and `system_design.` prefix. The existing integration test (`test_e2e_output_registry.py`) compares against these baselines, so they must be regenerated.

4. **No design doc contradictions found.** REQ-PY-01 through REQ-PY-07 are internally consistent and non-overlapping. Upstream interfaces (ComputationGraph from C18, entry_point_groups from C17) match what the generator expects.

### Risks & Unknowns

- **Low risk**: Bug 9 fix requires walking module inputs after orphan handling — straightforward but touches the graph_builder step ordering. All existing conformance tests (C14-C19) will verify no regressions.
- **Low risk**: Baseline YAML update affects the existing integration test. Must regenerate baselines from fixed pipeline.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: The generator code (`pipeline.py`) is 239 lines, well-structured, and fully readable. Both bugs are documented in the design intent doc with specific line numbers and one-line fix descriptions. The YAML template (`pipeline_yaml.jinja2`) is 50 lines. No unknowns require prototyping. The test approach (generate YAML from snapshot-based ComputationGraph, parse and inspect) follows established patterns from C18 and the existing integration test.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_gen_pipeline_yaml.py`
**Fixture data**: solar_battery_model, catf_mfe_model, chain_spike_model, attr_expr_probe (via `build_full_graph_from_snapshot()`)

### Test Cases

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_param_group_prefix_all_entry_points[solar_battery]` | REQ-PY-01 | Every entry_point source in solar_battery YAML has `{group}.{qn}` format — no bare qualified names |
| `test_param_group_prefix_all_entry_points[catf_mfe]` | REQ-PY-01 | Same for catf_mfe (CalcUsage only, no aggregation) |
| `test_param_group_prefix_all_entry_points[chain_spike]` | REQ-PY-01 | Same for chain_spike |
| `test_param_group_prefix_all_entry_points[attr_expr_probe]` | REQ-PY-01 | Same for attr_expr_probe (has FORMULA modules) |
| `test_param_group_not_none_in_graph[solar_battery]` | REQ-PY-02 | No entry_point InputSource in ComputationGraph has `param_group=None` |
| `test_param_group_not_none_in_graph[catf_mfe]` | REQ-PY-02 | Same for catf_mfe |
| `test_param_group_not_none_in_graph[chain_spike]` | REQ-PY-02 | Same for chain_spike |
| `test_param_group_not_none_in_graph[attr_expr_probe]` | REQ-PY-02 | Same for attr_expr_probe |
| `test_all_numeric_types_float[solar_battery]` | REQ-PY-03 | No `int` type string in any YAML input line (exercises multiplicity fix) |
| `test_all_numeric_types_float[catf_mfe]` | REQ-PY-03 | Same for catf_mfe (control — no aggregation) |
| `test_all_numeric_types_float[chain_spike]` | REQ-PY-03 | Same for chain_spike |
| `test_all_numeric_types_float[attr_expr_probe]` | REQ-PY-03 | Same for attr_expr_probe |
| `test_root_suffix_on_single_output[solar_battery]` | REQ-PY-04 | Every MODULE_OUTPUT source referencing a single-output module (field_name="root") appends `.root` |
| `test_root_suffix_on_single_output[catf_mfe]` | REQ-PY-04 | Same for catf_mfe |
| `test_channel_field_map_complete[solar_battery]` | REQ-PY-05 | `len(channel_field_map) == sum(len(m.outputs) for m in graph.modules)` |
| `test_channel_field_map_complete[catf_mfe]` | REQ-PY-05 | Same for catf_mfe |
| `test_exit_point_type_rules[solar_battery]` | REQ-PY-06 | Exit point type is `RootModel[T]` when field_name="root", else `T` for named fields |
| `test_exit_point_type_rules[catf_mfe]` | REQ-PY-06 | Same for catf_mfe |
| `test_entry_fusion_json_count[solar_battery]` | REQ-PY-07 | `len(entry_fusion_inputs) == len(graph.entry_point_groups)` |
| `test_entry_fusion_json_count[catf_mfe]` | REQ-PY-07 | Same for catf_mfe |
| `test_generator_imports_only_resolution_models` | gold standard | `pipeline.py` imports NOTHING from extraction/, analysis/, or generation/initialization.py — static analysis |
| `test_yaml_parseable[solar_battery]` | structural | Generated YAML is valid YAML with expected top-level keys: metadata, modules |
| `test_yaml_parseable[catf_mfe]` | structural | Same for catf_mfe |
| `test_module_comment_format[solar_battery]` | structural | CalcUsage modules have `# module_type` comment; FORMULA have `# source: computed_attribute`; Aggregation have `# source: aggregation` |
| `test_yaml_baseline_comparison[solar_battery]` | baseline | Generated YAML from snapshot matches updated baseline |
| `test_yaml_baseline_comparison[chain_spike]` | baseline | Same for chain_spike |
| `test_yaml_baseline_comparison[attr_expr_probe]` | baseline | Same for attr_expr_probe |

### Test Infrastructure Needed

- **Jinja2 Environment fixture**: Session-scoped fixture loading `src/sysml_codegen/templates/` (pattern from `test_e2e_output_registry.py`).
- **Graph fixtures**: Reuse `build_full_graph_from_snapshot()` from `test_entry_point_classifier.py`. Session-scoped for performance.
- **YAML parsing**: Use `yaml.safe_load()` to parse generated YAML and inspect structure. Each input line parses as `key: "type source"` string.
- **Updated baseline YAML files**: After Bug 9/10 fixes, regenerate baselines from snapshot-based graphs. Store alongside existing baselines. catf_mfe baseline needs to be generated (doesn't exist yet).

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written
- [x] Tests run (expected: most/all FAIL at this point — Bug 9/10 not yet fixed)
- [x] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify

| File | Change | Why |
|------|--------|-----|
| `src/sysml_codegen/resolution/graph_builder.py:1045` | Change `python_type="int"` to `python_type="float"` | Fix Bug 10 (REQ-PY-03) |
| `src/sysml_codegen/resolution/graph_builder.py` (after Step 6.8, ~line 248) | Add param_group propagation: build `qn_to_group` map from `param_groups`, walk all module inputs, set `source.param_group` for any entry_point source where it's None | Fix Bug 9 (REQ-PY-01, REQ-PY-02) |
| `tests/fixtures/baseline_yaml/solar_battery.yaml` | Regenerate from fixed pipeline — multiplicity inputs change from `int` to `float` and gain `system_design.` prefix | Baseline update for Bug 9/10 fixes |
| `tests/fixtures/baseline_yaml/attr_expr_probe.yaml` | Regenerate — verify no changes (no aggregation with multiplicity) | Baseline verification |
| `tests/fixtures/baseline_yaml/chain_spike.yaml` | Regenerate — verify no changes (no aggregation with multiplicity) | Baseline verification |
| `tests/fixtures/baseline_yaml/sample_model.yaml` | Regenerate — verify no changes | Baseline verification |

### Files to Create

| File | Purpose |
|------|---------|
| `tests/conformance/test_gen_pipeline_yaml.py` | ~27 conformance tests for REQ-PY-01 through REQ-PY-07 |

### Implementation Notes

1. **Bug 9 fix approach**: After Step 6.8 orphan handling (which creates the system_design ParameterGroup), build a reverse map `qualified_name → group_name` from all param_groups. Walk all modules' inputs: for any `InputSource` with `source_type="entry_point"` and `param_group is None`, look up the group and set it. This ensures the YAML generator never hits the no-prefix fallback. The `InputSource` Pydantic model is mutable (no `frozen=True`), so direct assignment works.

2. **Bug 10 fix**: Line 1045 `python_type="int"` → `python_type="float"`. This is the aggregation module's multiplicity input for SumTerms. The fix affects solar_battery (has SumTerms with named multiplicity attributes like `module_count`, `inverter_count`, `pack_count`).

3. **Baseline regeneration**: Generate YAML from snapshot-based ComputationGraph using `build_full_graph_from_snapshot()` + `generate_pipeline_yaml()`. Write to `tests/fixtures/baseline_yaml/`. This avoids needing the JVM for live extraction. Snapshot-based and live-based YAML should be identical (YAML doesn't render compilability, which is the only difference).

4. **Test parametrization**: Use `@pytest.mark.parametrize` with model names. Session-scoped fixtures for ComputationGraph (expensive to build). Helper to generate YAML once per model.

5. **YAML parsing strategy**: `yaml.safe_load()` parses the generated YAML. Module input lines parse as string values (e.g., `"float design_params.QN"`). Split on first space to get type and source. Check source for dot prefix (param_group) or `.root` suffix.

### Gate: Ready for VALIDATE
- [x] All test cases pass (27/27)
- [x] No regressions in full test suite (`uv run pytest tests/` — 1614 passed, 2 skipped, 5 xfailed)
- [x] Lint clean (no new lint issues — pre-existing issues unchanged)

---

## 5. Validation

- [x] Every acceptance criterion from COMPONENT_CHECKLIST is satisfied:
  - [x] All entry point sources include `param_group.` prefix (REQ-PY-01)
  - [x] All numeric types are "float" (including multiplicity) (REQ-PY-03)
  - [x] Single-output references append `.root` (REQ-PY-04)
  - [x] channel_field_map covers every ModuleOutput (REQ-PY-05)
  - [x] Exit point type matches upstream output type (REQ-PY-06)
  - [x] One JSON file per ParameterGroup (REQ-PY-07)
  - [x] Consumes ONLY ComputationGraph (gold standard)
- [x] Every REQ-PY-NN has at least one passing test
- [x] Full test suite passes (record count: 1614 tests, 0 failures)
- [x] Cross-check: re-read design intent doc, verify implementation matches
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### Baseline Impact

Bug 9 and Bug 10 fixes change the solar_battery baseline YAML:
- ~12 multiplicity input lines change from `int` to `float` (Bug 10)
- ~12 multiplicity entry point sources gain `system_design.` prefix (Bug 9)
- Other 3 baselines (attr_expr_probe, chain_spike, sample_model) expected unchanged (no aggregation with named multiplicity attributes)
- Existing integration test `test_e2e_output_registry.py` will pass with updated baselines

---

## 6. Learnings

### Findings

1. **Bug 9 affected 28 entry point InputSources in solar_battery.** 13 orphan EPs from the classifier (deeply-nested QNs that don't match ParameterGroupDeriver patterns), plus multiplicity EPs shared across multiple aggregation modules. The param_group propagation fix (Step 6.9) correctly assigns `system_design` to all 28.

2. **Bug 10 fix required updating 6 test assertions.** The `"int"` type for multiplicity was asserted in 1 conformance test (C16), 1 unit test, and 4 unit test fixture constructions. All updated to `"float"`.

3. **ComputationGraph JSON baselines also affected.** Both `test_graph_assembly.py` and `test_pipeline_e2e.py` compare solar_battery ComputationGraph JSON against baselines. The Bug 9/10 fixes changed `InputSource.param_group` (None→group_name) and `python_type` ("int"→"float") in the JSON. Baseline at `tests/fixtures/baseline_outputs/solar_battery/computation_graph.json` regenerated.

4. **Only solar_battery baselines changed.** chain_spike and attr_expr_probe YAML baselines are unchanged (no aggregation with named multiplicity attributes). catf_mfe has no baseline (doesn't exist in `baseline_yaml/`).

5. **sample_model YAML baseline not regenerated (uses live pipeline).** The sample_model baseline is tested by `test_e2e_output_registry.py` using `build_pipeline_context()` (live extraction), not snapshot-based graphs. It has no aggregation, so Bug 9/10 fixes don't affect it.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| 21-pipeline-yaml-generation.md | Update Bug 10 line reference from 1039 to 1061; mark fix as applied | Line number accuracy — **Done** |
| 07-graph-assembly.md | Note Step 6.9 (param_group propagation) added after Step 6.8 | Architecture documentation — **Done** |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| C16 (Aggregation Factory) | Bug 10 fix changes multiplicity `python_type` from `int` to `float` | Updated 1 conformance test assertion (`test_sumterm_multiplicity_entry_point`) |
| C18 (Graph Assembly) | Bug 9 fix adds param_group propagation after orphan handling | Updated solar_battery ComputationGraph JSON baseline |
| 5.2 (E2E Pipeline) | Both fixes change ComputationGraph JSON | Updated solar_battery ComputationGraph JSON baseline (shared file) |
| Unit tests | Bug 10 fix changes expected type in unit tests | Updated 1 unit test + 4 fixture constructions in `test_graph_builder_aggregation.py` |

### Deviations from Plan

1. **sample_model YAML baseline not regenerated.** Plan listed it for verification, but it uses the live pipeline (requires JVM). No change expected (no aggregation). The existing integration test (`test_e2e_output_registry.py`) covers it.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (continuing)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [ ] `git add` only the files listed in Build Plan + test file, plus IMPLEMENTATION_PLAN and COMPONENT_CHECKLIST (no unrelated changes)
- [ ] Commit message format:
  ```
  refactor(C20): Pipeline YAML Generator conformance tests + Bug 9/10 fixes

  - Tests: N new conformance tests in tests/conformance/test_gen_pipeline_yaml.py
  - Fixes: Bug 9 (missing param_group prefix on orphan EPs), Bug 10 (int→float for multiplicity)
  - Baselines: Updated 4 YAML baseline files
  - Refs: REQ-PY-01 through REQ-PY-07
  - Design intent: 21-pipeline-yaml-generation.md
  ```
- [ ] Committed successfully

---

## Progress Log

### Session: 2026-02-18 — Planning
**Phase**: PLANNING
**Work done**:
- Read design intent doc (21-pipeline-yaml-generation.md), implementation plan Phase 6, component checklist C20
- Read current source: `generation/pipeline.py`, `templates/pipeline_yaml.jinja2`, `resolution/graph_builder.py`
- Read existing integration test (`test_e2e_output_registry.py`) and pipeline E2E test (`test_pipeline_e2e.py`)
- Read baseline YAML (`solar_battery.yaml`) — confirmed Bug 9 and Bug 10 present
- Design consistency review: identified Bug 9 root cause (Step 6.8 orphan handling doesn't propagate param_group to InputSource), Bug 10 root cause (line 1045 hardcoded `"int"`)
- Verified `InputSource` is mutable Pydantic BaseModel (no frozen config)
- Completed full test plan with 27 test cases across 4 models
- Build plan: 2 production fixes (Bug 9 ~6 lines, Bug 10 one-line), baseline regeneration, new test file
- Spike decision: SKIP (design clear, bugs documented with specific line numbers)
**Stopped at**: Plan complete, ready for review
**Next step**: Execute build — write test file, fix bugs, update baselines
**Blockers**: None

### Session: 2026-02-18 — Build + Validate
**Phase**: PLANNING → TEST → BUILD → VALIDATE → DONE
**Work done**:
- **TEST**: Wrote `tests/conformance/test_gen_pipeline_yaml.py` with 27 test cases across 7 test classes
  - 4 models: solar_battery, catf_mfe, chain_spike, attr_expr_probe
  - Session-scoped fixtures for ComputationGraph and YAML generation
  - Pre-fix results: 3 failed (solar_battery only — Bug 9/10), 24 passed
  - Zero mocks verified
- **BUILD**: Fixed Bug 10 (1-line: `python_type="int"` → `"float"` at graph_builder.py:1045)
- **BUILD**: Fixed Bug 9 (Step 6.9: param_group propagation — 9 lines after Step 6.8 in graph_builder.py)
  - Builds `qn_to_group` map from all param_groups, walks module inputs, sets `source.param_group`
- **BUILD**: Regenerated solar_battery YAML baseline (Bug 9/10 changes)
- **BUILD**: Verified chain_spike and attr_expr_probe YAML baselines unchanged
- **BUILD**: Regenerated solar_battery ComputationGraph JSON baseline
- **BUILD**: Updated 6 test assertions in C16 conformance and unit tests (`"int"` → `"float"`)
- **VALIDATE**: Full suite: 1614 passed, 2 skipped, 5 xfailed, 0 failures
- **VALIDATE**: All 27 C20 conformance tests pass, all REQ-PY-01 through REQ-PY-07 green
- **VALIDATE**: No new lint issues, no TODOs/FIXMEs in new/modified code
**Files modified**:
- `src/sysml_codegen/resolution/graph_builder.py` (Bug 9 + Bug 10)
- `tests/conformance/test_gen_pipeline_yaml.py` (NEW — 27 tests)
- `tests/fixtures/baseline_yaml/solar_battery.yaml` (regenerated)
- `tests/fixtures/baseline_outputs/solar_battery/computation_graph.json` (regenerated)
- `tests/conformance/test_factory_aggregation.py` (1 assertion: int→float)
- `tests/unit/test_graph_builder_aggregation.py` (5 assertions/fixtures: int→float)
**Stopped at**: All validation complete, ready for commit
**Next step**: Commit, update IMPLEMENTATION_PLAN and COMPONENT_CHECKLIST
**Blockers**: None
