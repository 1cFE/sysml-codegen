# Component: JSON Template + Parameter Schema Generator (C25)

**Status**: DONE
**Created**: 2026-02-18
**Last updated**: 2026-02-18
**Updated by**: Plan agent (Phase 6, step 6.6)

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — C25
- **Design intent**: [08-generation.md](../../concepts/refactor-design-intent/08-generation.md) (REQ-GEN-05), [21-pipeline-yaml-generation.md](../../concepts/refactor-design-intent/21-pipeline-yaml-generation.md) (REQ-PY-07)
- **Requirements**: REQ-GEN-05, REQ-PY-07
- **Depends on**: C17 (Entry Point Classification), C18 (Graph Assembly), C20 (Pipeline YAML Generator — Bug 9 fix). All complete.

---

## 1. Assessment

### What This Component Does

The JSON template + parameter schema generator consumes `ComputationGraph.entry_point_groups` (a list of `ParameterGroup` objects) and produces two artifacts per group:
1. **JSON template file** (`inputs/{group_name}.json`) — pre-filled with entry point default values
2. **Pydantic schema file** (`schemas/{group_name}.py`) — typed schema class for runtime validation

The two `_from_graph` functions are: `generate_all_derived_schemas_from_graph()` and `generate_all_derived_jsons_from_graph()` in `generation/entry_point.py` (lines 538-631). These are the graph-only code paths (no extraction models).

### Current State

- **Exists?** Yes — `generation/entry_point.py` (645 lines). Contains both legacy (`generate_all_derived_schemas`, `generate_all_derived_jsons`) and graph-based (`generate_all_derived_schemas_from_graph`, `generate_all_derived_jsons_from_graph`) functions. The CLI calls the `_from_graph` variants at `cli/__init__.py:779-796`.
- **Needs extraction/refactoring?** No — conformance tests only.
- **Current test coverage**: Zero. No unit or conformance tests exist for any of the `_from_graph` functions.
- **Template used**: `parameter_group_schema.py.jinja2` (18 lines) — renders a Pydantic BaseModel with Field() entries.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc(s)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **REQ-PY-07 overlap with C20.** REQ-PY-07 ("Entry point module inputs SHALL list one JSON file per ParameterGroup") is about YAML generation, already tested by C20 (`test_gen_pipeline_yaml.py`). C25's scope is the JSON *files* and *schemas* themselves, not the YAML references to them. REQ-GEN-05 is the primary requirement for C25. **Resolution**: C25 tests REQ-GEN-05 directly (file generation). REQ-PY-07 is cross-verified: the count of generated JSON files must match `len(graph.entry_point_groups)`.

2. **JSON excludes entries with `default_value=None`.** The `generate_all_derived_jsons_from_graph()` function (line 616) filters: `if ep.default_value is not None`. This means EPs without defaults are omitted from JSON templates. catf_mfe has one such EP (`magnet_volume` in magnets_params group, `default_value=null`). The Pydantic schema still includes these fields (with `default=None` rendering in the template). This behavior is intentional — JSON templates are pre-filled files, so missing defaults are naturally omitted. **Resolution**: Test verifies this behavior explicitly.

3. **`system_design` group EPs have `param_group=null` at EntryPoint level.** Solar_battery's orphan EPs (collected by Step 6.8/6.9) have `param_group=null` on the EntryPoint objects themselves, even though they are grouped under the `system_design` ParameterGroup. This doesn't affect JSON/schema generation (which uses `ParameterGroup.parameters`, not `EntryPoint.param_group`). **Resolution**: No impact on C25; noted for awareness.

4. **`python_type` is always `"float"` in real fixture data.** All entry points across all 4 models use `python_type="float"`. The `getattr(ep, "python_type", "float")` in the schema generator defensively falls back to `"float"`. No `int`/`bool`/`str` types in real data. **Resolution**: Verify the type path with real data; note coverage limitation.

### Risks & Unknowns

No spiking needed. The functions are straightforward wrappers over `json.dumps()` and Jinja2 template rendering. The graph data is well-understood from C17/C18/C20 baselines. All unknowns are resolved.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: The `_from_graph` functions are simple: iterate `ParameterGroup.parameters`, build dicts, render template or call `json.dumps()`. The data models (`ParameterGroup`, `EntryPoint`) are Pydantic models with clear fields, well-exercised by C17/C18. No unknowns that could invalidate the build plan.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_gen_json_templates.py`
**Fixture data**: solar_battery_model (3 groups: library_params, design_params, system_design), catf_mfe_model (8 groups: heating_params, magnets_params, blanket_params, physics_params, system_params, tritium_params, vacuum_params, radial_build_params). Parametrized over both.

### Test Cases

> Every requirement (REQ-XX-NN) must have at least one test case.
> Every test uses real data — no mocks. Stubs only at SysIDE adapter boundary.

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_req_gen_05_one_json_per_group` | REQ-GEN-05 | `generate_all_derived_jsons_from_graph()` produces exactly `len(graph.entry_point_groups)` JSON files |
| `test_req_gen_05_one_schema_per_group` | REQ-GEN-05 | `generate_all_derived_schemas_from_graph()` produces exactly `len(graph.entry_point_groups)` schema files |
| `test_req_gen_05_json_filenames_match_groups` | REQ-GEN-05 | Each generated JSON filename matches `{group.name}.json` |
| `test_req_gen_05_schema_filenames_match_groups` | REQ-GEN-05 | Each generated schema filename matches `{group.name}.py` |
| `test_req_gen_05_json_values_match_defaults` | REQ-GEN-05 | For each group, JSON keys/values match `{ep.qualified_name: ep.default_value}` for all EPs with non-None defaults |
| `test_req_gen_05_json_excludes_none_defaults` | REQ-GEN-05 | EPs with `default_value=None` are absent from JSON (catf_mfe magnets_params.magnet_volume) |
| `test_req_gen_05_json_keys_sorted` | REQ-GEN-05 | JSON output has keys in sorted order (deterministic output) |
| `test_req_gen_05_schema_class_name_matches` | REQ-GEN-05 | Generated schema contains `class {group.class_name}(BaseModel):` |
| `test_req_gen_05_schema_fields_match_eps` | REQ-GEN-05 | Schema has one field per EP in the group, using `ep.qualified_name` as field name |
| `test_req_gen_05_schema_field_types_float` | REQ-GEN-05 | Schema field types are `float` (matching `ep.python_type` for all real data) |
| `test_req_gen_05_schema_parses_as_valid_python` | REQ-GEN-05 | `ast.parse()` succeeds on every generated schema file |
| `test_req_gen_05_schema_default_matches_ep` | REQ-GEN-05 | Schema fields with defaults render `Field(default={ep.default_value}, ...)` |
| `test_req_py_07_json_file_count_matches_yaml_entry_fusion` | REQ-PY-07 | Number of generated JSON files equals number of ParameterGroups (cross-check with YAML entry_fusion) |
| `test_group_count_solar_battery` | REQ-GEN-05 | solar_battery has exactly 3 parameter groups |
| `test_group_count_catf_mfe` | REQ-GEN-05 | catf_mfe has exactly 8 parameter groups |

### Test Infrastructure Needed

- Reuse `build_full_graph_from_snapshot()` from `tests/conformance/test_entry_point_classifier.py` (already used by C20-C24).
- Reuse `template_env` session-scoped fixture pattern from C22.
- `tmp_path` fixture for file output verification (pytest built-in).
- No new helpers needed.

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written
- [x] Tests run (expected: most/all PASS — conformance-only, no production changes)
- [x] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify
| File | Change | Why |
|------|--------|-----|
| (none) | No production code changes | Conformance-only component |

### Files to Create
| File | Purpose |
|------|---------|
| `tests/conformance/test_gen_json_templates.py` | C25 conformance tests (~15 test cases, parametrized over solar_battery + catf_mfe) |

### Implementation Notes

1. **Session-scoped graph fixture pattern.** Follow the C20-C24 pattern: build `ComputationGraph` once per session via `build_full_graph_from_snapshot()`, parametrize tests over both models.

2. **JSON verification approach.** Call `generate_all_derived_jsons_from_graph()` with `tmp_path`, then:
   - Verify file count and filenames
   - `json.loads()` each file and compare against `ParameterGroup.parameters` list
   - Assert keys are sorted (consecutive keys non-decreasing)

3. **Schema verification approach.** Call `generate_all_derived_schemas_from_graph()` with `tmp_path` and `template_env`, then:
   - Verify file count and filenames
   - `ast.parse()` each generated file
   - String-search for `class {class_name}(BaseModel):`
   - Verify each `ep.qualified_name` appears as a field name in the source

4. **JSON None-default test.** catf_mfe `magnets_params` group has EP `magnet_volume` with `default_value=null`. Verify this key is absent from the generated `magnets_params.json` but present in the schema.

5. **Parametrization.** Use `@pytest.fixture(params=PARAMETRIZED_MODELS)` or `@pytest.mark.parametrize` to run each test against both solar_battery and catf_mfe. Expected ~30 test items total (15 tests x 2 models).

### Gate: Ready for VALIDATE
- [x] All test cases pass
- [x] No regressions in full test suite (`uv run pytest tests/`)
- [x] Lint clean (`uv run ruff check src/`) — no new issues (19 pre-existing)

---

## 5. Validation

- [x] Every acceptance criterion from COMPONENT_CHECKLIST is satisfied
  - [x] Each ParameterGroup produces one JSON template + one Pydantic schema
  - [x] JSON template values match entry point default_value
  - [x] Schema field types match declared SysML types
- [x] Every REQ-XX-NN has at least one passing test (REQ-GEN-05, REQ-PY-07)
- [x] Full test suite passes (record count: 1733 tests, 0 failures, 6 xfailed)
- [x] Cross-check: re-read design intent doc, verify implementation matches
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### Baseline Impact
No baseline changes expected. Conformance-only component — no production code modifications.

---

## 6. Learnings

### Findings
1. **All 28 tests pass on first run.** Straightforward conformance-only component — no production code changes, no surprises. The `_from_graph` functions are thin wrappers as assessed.
2. **catf_mfe magnets_params.magnet_volume confirmed as None-default EP.** The None-default exclusion test correctly finds and verifies this EP is absent from JSON but present in schema.
3. **`python_type` is always `"float"` across all real data.** All entry points in both models use `python_type="float"`, confirming the assessment. The `getattr(ep, "python_type", "float")` fallback is defensive but never triggered.
4. **Session-scoped `tmp_path_factory` works well for generation tests.** Unlike `tmp_path` (function-scoped), `tmp_path_factory` allows session-scoped fixtures to generate files once and share across all tests.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|

### Deviations from Plan
None. All 15 planned test cases implemented as specified, producing 28 test items (14 tests x 2 models + 2 model-specific count assertions).

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (continuing)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [ ] `git add` only the files listed in Build Plan + test file, plus IMPLEMENTATION_PLAN and COMPONENT_CHECKLIST (no unrelated changes)
- [ ] Commit message format:
  ```
  refactor(C25): JSON Template + Parameter Schema Generator conformance tests

  - Tests: N new conformance tests in tests/conformance/test_gen_json_templates.py
  - Refs: REQ-GEN-05, REQ-PY-07
  - Design intent: 08-generation.md, 21-pipeline-yaml-generation.md
  ```
- [ ] Committed successfully

---

## Progress Log

### Session: 2026-02-18 — Planning
**Phase**: PLANNING
**Work done**:
- Read design intent docs 08-generation.md and 21-pipeline-yaml-generation.md
- Read current source: `generation/entry_point.py` (645 lines), `generation/schemas.py` (275 lines)
- Reviewed ParameterGroup/EntryPoint data models in `resolution/models.py`
- Examined baseline ComputationGraph JSON for solar_battery (3 groups, including system_design with orphan EPs) and catf_mfe (8 groups, including magnets_params with 1 null-default EP)
- Reviewed learnings from C20-C24 (no cross-component impact on C25)
- Design consistency review: 4 issues identified and resolved
- Spike decision: SKIP (straightforward generator, no unknowns)
**Stopped at**: Plan complete, ready for build
**Next step**: Build agent should create `tests/conformance/test_gen_json_templates.py` with all 15 test cases
**Blockers**: None

### Session: 2026-02-18 — Build + Validate (DONE)
**Phase**: PLANNING → DONE (combined TEST/BUILD/VALIDATE — conformance-only)
**Work done**:
- Created `tests/conformance/test_gen_json_templates.py` with 28 test items (15 test cases, parametrized over 2 models)
- All 28 tests pass on first run
- No mocks (verified by grep)
- Full test suite: 1733 passed, 2 skipped, 6 xfailed, 0 failures
- Lint clean (no new issues)
- Updated COMPONENT_CHECKLIST (C25 ACs marked done)
- Updated IMPLEMENTATION_PLAN (6.6 marked complete, test count tracking row added)
**Stopped at**: Complete — ready for commit
**Next step**: Commit
**Blockers**: None
