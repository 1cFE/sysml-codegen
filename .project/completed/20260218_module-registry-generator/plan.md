# Component: Module Registry Generator (C24)

**Status**: DONE
**Created**: 2026-02-18
**Last updated**: 2026-02-18
**Updated by**: Plan agent (C24 planning session)

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — C24
- **Design intent**: [20-module-registry-generation.md](../../concepts/refactor-design-intent/20-module-registry-generation.md)
- **Requirements**: REQ-REG-01 through REQ-REG-07
- **Depends on**: C18 (Graph Assembly), C19 (Orchestrator), C20 (Pipeline YAML), C22 (Schema Generator) — all complete

---

## 1. Assessment

### What This Component Does

The module registry generator (`generation/registry.py`) produces the `__init__.py` file that registers all pipeline modules with TEAx. It generates:
1. Import statements for every module class (CalcUsage, FORMULA, aggregation)
2. A `create_registry()` call with all module classes and `module_type_override` dict
3. `CUSTOM_SCHEMA_TYPES` list for entry point schemas and exit point primitive types

It consumes `CalculationDefinitionData` (CalcUsage), `ComputedAttributeData` (FORMULA), `ScopedAggregationData` (aggregation), `ParameterGroup` (schemas), and `PipelineModule` outputs (exit point types).

### Current State
- **Exists?** Yes — `src/sysml_codegen/generation/registry.py` (294 lines)
- **Needs extraction/refactoring?** Yes — two known bugs (Bug 8a and 8b from design doc):
  - **Bug 8a** (REQ-REG-01): Line 126 uses `agg.expression.owning_part_qn` (library QN with `__` separator) to derive aggregation import paths. Should use `agg.module_eqn.replace("__", "::")` (design-scoped). The current import paths produce a malformed directory name (e.g., `solarbatterylibrary__solar_array/capital_cost.py`) instead of the correct nested path (`solarbatterydesign/solar_battery_plant/solar_array/capital_cost.py`).
  - **Bug 8b** (REQ-REG-03/04): 20 aggregation modules across 4 assemblies share 5 class names (`capital_costModule`, `raw_material_costModule`, etc.). The `module_type_override` dict silently overwrites duplicate keys. No collision detection or aliased imports.
- **Current test coverage**: No conformance tests. No unit tests for registry generation.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc
- [x] No contradictions with other component specs
- [ ] Input/output interfaces match what upstream/downstream components expect *(see Issue #1)*
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

**Issue #1: graph_builder module_type mismatch for aggregation**

The graph_builder (`resolution/graph_builder.py:970-972`) also uses `agg.expression.owning_part_qn` to derive `module_type` for aggregation `PipelineModule` objects:
```python
module_type = derive_module_type(
    f"{agg.expression.owning_part_qn}::{agg.expression.attribute_name}"
)
```
This produces module_types like `"solarbatterylibrary__solar_array.capital_costModule"` (with `__` in the namespace, malformed).

If we fix registry.py to use design-scoped module_types (e.g., `"solarbatterydesign.solar_battery_plant.solar_array.capital_costModule"`), the registry's `module_type_override` values will NOT match the `PipelineModule.module_type` stored in the ComputationGraph (used by YAML generator).

**Resolution**: Fix Bug 8a in registry.py only for C24 scope. The graph_builder fix should be coordinated with C26 (PipelineModule Field Expansion) in Phase 7, since it changes ComputationGraph JSON baselines, YAML baselines, and all downstream consumers. Document the module_type inconsistency between registry and graph as a finding.

The C24 conformance tests can verify that the registry's import paths are internally consistent (paths match the SysMLQualifiedName derivation used by CLI for filesystem generation), independently of the graph_builder's module_type.

**Issue #2: REQ-REG-05 interpretation — "design-scoped" for CalcUsage**

REQ-REG-05 says all module types "SHALL derive paths from design-scoped qualified names." But CalcUsage modules correctly use library-scoped calc_def QNs (e.g., `SolarBatteryLibrary::PVModuleCostCalc`), matching the CLI's filesystem generation. The intent is that all three module types use the same `SysMLQualifiedName → PythonModulePath` pipeline with the correct input QN for their type, not that all must be design-scoped.

**Resolution**: Interpret REQ-REG-05 as "all module types use the same QN derivation pipeline, and the input QN must match what CLI uses for filesystem generation." Test by verifying all three types produce import paths consistent with `PythonModulePath.from_sysml()`.

**Issue #3: FORMULA module_type derivation uses `owning_part_qualified_name` (correct)**

FORMULA modules in registry.py:110 use `ca.owning_part_qualified_name` (already `::` separated, design-scoped like `AttrExprProbeDesign::probe_design`). This is correct and matches graph_builder. No fix needed for FORMULA.

### Risks & Unknowns

1. **Alias format for name collisions**: The design doc example shows `SolarArray_Capital_CostModule`. The actual class names are `capital_costModule` (lowercase element name). Need to decide exact aliasing format.
2. **Graph_builder module_type mismatch**: After fixing registry, the module_type_override values in registry won't match PipelineModule.module_type from graph_builder for aggregation. This is a runtime issue but not a conformance testing issue.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: The fix for Bug 8a is a single-line change (well-specified in design doc). Bug 8b requires collision detection + alias generation, which is a bounded algorithmic problem with a clear approach from the design doc examples. The existing codebase patterns (`SysMLQualifiedName`, `PythonModulePath`, `derive_module_type`) are well-understood from prior components. No unknowns that could invalidate the build plan.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_gen_registry.py`
**Fixture data**: solar_battery_model (CalcUsage + FORMULA + aggregation, exercises Bug 8a/8b), catf_mfe_model (42 CalcUsage, no collisions), chain_spike_model (3 CalcUsage, simple), attr_expr_probe_model (CalcUsage + FORMULA)

### Test Cases

> Every requirement (REQ-REG-01 through REQ-REG-07) must have at least one test case.
> Every test uses real data — no mocks.

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_req_reg_01_aggregation_paths_use_design_scoped_eqn` | REQ-REG-01 | For solar_battery, all aggregation import paths start with `solarbatterydesign.solar_battery_plant.` (design scope), not `solarbatterylibrary` (library scope). Verify 20 aggregation imports. |
| `test_req_reg_02_import_paths_match_filesystem[solar_battery]` | REQ-REG-02 | For each import in the generated registry, verify the import path matches `PythonModulePath.from_sysml()` using the same QN that CLI uses. Parametrized over models. |
| `test_req_reg_02_import_paths_match_filesystem[catf_mfe]` | REQ-REG-02 | Same as above for catf_mfe (42 CalcUsage, no FORMULA/aggregation). |
| `test_req_reg_03_globally_unique_class_names[solar_battery]` | REQ-REG-03 | Parse generated code, extract all class names from `module_type_override` dict. Assert `len(unique_names) == len(all_names)` — no duplicate keys. solar_battery is the critical case (20 aggregation modules with 5 shared element names). |
| `test_req_reg_03_globally_unique_class_names[catf_mfe]` | REQ-REG-03 | Same for catf_mfe (no collisions expected — all CalcUsage with unique names). |
| `test_req_reg_04_aliased_imports_for_collisions` | REQ-REG-04 | For solar_battery, verify aggregation modules with colliding element names get aliased imports. Check that `import X as Alias` appears for each collision. Verify the alias format includes the assembly name prefix. |
| `test_req_reg_05_all_types_use_sqn_derivation[solar_battery]` | REQ-REG-05 | For solar_battery (all 3 module types), verify every import path is derivable from `SysMLQualifiedName → PythonModulePath.from_sysml()`. No ad-hoc path construction. |
| `test_req_reg_05_all_types_use_sqn_derivation[attr_expr_probe]` | REQ-REG-05 | Same for attr_expr_probe (CalcUsage + FORMULA, verifies FORMULA uses same pipeline). |
| `test_req_reg_06_custom_schema_types_includes_exit_primitives[solar_battery]` | REQ-REG-06 | For solar_battery, verify CUSTOM_SCHEMA_TYPES includes `Float` (used by single-output modules). |
| `test_req_reg_06_custom_schema_types_includes_exit_primitives[catf_mfe]` | REQ-REG-06 | For catf_mfe, same check. |
| `test_req_reg_07_collision_detection_before_rendering` | REQ-REG-07 | Call the registry generator for solar_battery, verify it detects the 5 colliding class names and reports them (via warning or return value) before template rendering. |
| `test_generated_code_valid_python[solar_battery]` | REQ-REG-01-07 | Parse generated code with `ast.parse()`. Parametrized over models. |
| `test_generated_code_valid_python[catf_mfe]` | REQ-REG-01-07 | Same for catf_mfe. |
| `test_generated_code_valid_python[chain_spike]` | REQ-REG-01-07 | Same for chain_spike. |
| `test_generated_code_valid_python[attr_expr_probe]` | REQ-REG-01-07 | Same for attr_expr_probe. |
| `test_module_count_matches_graph[solar_battery]` | REQ-REG-02 | Number of modules in registry matches `len(graph.modules)`. Parametrized. |
| `test_module_count_matches_graph[catf_mfe]` | REQ-REG-02 | Same for catf_mfe. |
| `test_schema_imports_match_entry_point_groups[solar_battery]` | REQ-REG-06 | Number of schema imports matches `len(graph.entry_point_groups)`. Parametrized. |
| `test_schema_imports_match_entry_point_groups[catf_mfe]` | REQ-REG-06 | Same for catf_mfe. |
| `test_no_collisions_model[catf_mfe]` | REQ-REG-03 | catf_mfe has zero collisions (all CalcUsage). Verify no aliased imports generated. |
| `test_no_collisions_model[chain_spike]` | REQ-REG-03 | Same for chain_spike. |
| `test_graph_builder_module_type_mismatch_documented` | Cross-ref | Static analysis: verify `graph_builder.py:970-972` still uses `owning_part_qn` for aggregation module_type. Documents the known mismatch for Phase 7 fix. |

### Test Infrastructure Needed
- Reuse `build_full_graph_from_snapshot()` from `tests/conformance/test_entry_point_classifier.py`
- Reuse `build_classifier_inputs_from_snapshot()` for snapshot data (calc_defs, computed_attributes, aggregation_data)
- Session-scoped fixtures to build graphs + generate registry code for each model (expensive)
- Helper to parse generated registry code and extract import statements, class names, module_type_override entries

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written
- [x] Tests run (expected: most/all FAIL at this point) — 5 failed, 17 passed pre-fix
- [x] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify
| File | Change | Why |
|------|--------|-----|
| `src/sysml_codegen/generation/registry.py:126` | Change aggregation QN derivation from `agg.expression.owning_part_qn` to `agg.module_eqn.replace("__", "::")` | REQ-REG-01: Bug 8a fix — use design-scoped EQN for aggregation import paths |
| `src/sysml_codegen/generation/registry.py:93-137` | Add collision detection + alias generation before building `all_modules` list and imports | REQ-REG-03/04/07: Bug 8b fix — globally unique class names via aliased imports |
| `tests/fixtures/baseline_outputs/solar_battery/registry_init.py` | Regenerate with fixed import paths and aliased names | Baseline update after Bug 8a/8b fix |
| `tests/fixtures/baseline_outputs/chain_spike/registry_init.py` | Regenerate (should be unchanged — no aggregation) | Verify no regression |
| `tests/fixtures/baseline_outputs/attr_expr_probe/registry_init.py` | Regenerate (should be unchanged — no aggregation) | Verify no regression |

### Files to Create
| File | Purpose |
|------|---------|
| `tests/conformance/test_gen_registry.py` | C24 conformance tests (~22 test cases) |

### Implementation Notes

**Bug 8a fix** (registry.py:126):
```python
# Current (buggy):
sysml_qn = f"{agg.expression.owning_part_qn}::{agg.expression.attribute_name}"

# Fixed:
sysml_qn = agg.module_eqn.replace("__", "::")
```
This changes the QN from `SolarBatteryLibrary__Solar_Array::capital_cost` (malformed `__` in package) to `SolarBatteryDesign::solar_battery_plant::solar_array::capital_cost` (proper `::` separated segments).

**Bug 8b fix** (collision detection + aliasing):
1. After building the initial `all_modules` list, group entries by `class_name`
2. For groups with >1 entry, derive alias: `{PascalCase(parent_segment)}_{class_name}` where `parent_segment` is the second-to-last segment of the module_type (the assembly name)
3. Update import statements to use `import X as Alias` format
4. Replace `class_name` in `all_modules` with the alias
5. Emit a warning via `logging.warning()` listing all detected collisions

**Alias format example**:
- module_type: `solarbatterydesign.solar_battery_plant.solar_array.capital_costModule`
- parent_segment: `solar_array`
- PascalCase: `SolarArray`
- alias: `SolarArray_capital_costModule`
- import: `from pkg.modules.solarbatterydesign.solar_battery_plant.solar_array.capital_cost import capital_costModule as SolarArray_capital_costModule`

**No changes to**:
- `graph_builder.py` — defer module_type fix to Phase 7 (documented in Issue #1)
- Template `registry_function.py.jinja2` — the template already uses `module.class_name`, which will be the alias when set
- Other baselines (ComputationGraph JSON, YAML) — unchanged since graph_builder is not modified

### Gate: Ready for VALIDATE
- [x] All test cases pass — 22/22 passed
- [x] No regressions in full test suite (`uv run pytest tests/`) — 1675 passed, 2 skipped, 6 xfailed
- [x] Lint clean (`uv run ruff check src/`) — only pre-existing UP037

---

## 5. Validation

- [x] Every acceptance criterion from COMPONENT_CHECKLIST is satisfied:
  - [x] Uses design-scoped EQN (module_eqn), not library QN
  - [x] Import paths match actual filesystem paths
  - [x] Globally unique class names via module_type_override
  - [x] Aliased imports when names collide
  - [x] Name collision detection and reporting before rendering
- [x] Every REQ-REG-NN has at least one passing test
- [x] Full test suite passes (record count: 1675 tests, 0 failures, 2 skipped, 6 xfailed)
- [x] Cross-check: re-read design intent doc, verify implementation matches
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### Baseline Impact
- `tests/fixtures/baseline_outputs/solar_battery/registry_init.py` — expected to change significantly:
  - Aggregation import paths change from `solarbatterylibrary__solar_array.*` to `solarbatterydesign.solar_battery_plant.solar_array.*`
  - Aggregation class names gain assembly prefix aliases
  - module_type_override values change to design-scoped namespaces
- `chain_spike/registry_init.py` — no change expected (no aggregation)
- `attr_expr_probe/registry_init.py` — no change expected (no aggregation)

---

## 6. Learnings

### Findings
- Bug 8a fix was a single-line change at `registry.py:130` as planned — `agg.module_eqn.replace("__", "::")` replaces `agg.expression.owning_part_qn`.
- Bug 8b fix added `_resolve_class_name_collisions()` (~70 lines) — groups by class_name, derives PascalCase parent-segment aliases, updates import statements to `import X as Alias`, emits `logging.warning()`.
- Alias format uses lowercase element name (e.g., `SolarArray_capital_costModule`) rather than the PascalCase shown in design doc examples (`SolarArray_Capital_CostModule`). This is because `derive_module_type()` preserves the element name casing from SysML, and the actual SysML element names are lowercase (`capital_cost`). Consistent with all other module types.
- Baselines for chain_spike and attr_expr_probe gained `Float` in CUSTOM_SCHEMA_TYPES — this was a pre-existing gap where the baseline capture didn't pass `exit_point_primitive_types`, not a C24 change.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| 20-module-registry-generation.md | Alias examples use PascalCase element names (`Capital_CostModule`) but actual output is lowercase (`capital_costModule`). Update examples to match real output. | Cosmetic — avoids confusion for future readers |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| graph_builder (7.5a) | `module_type` for aggregation PipelineModules still uses `owning_part_qn` — creates module_type mismatch between registry and YAML | Fix `graph_builder.py:970-972` to use `agg.module_eqn.replace("__", "::")` — tracked as IMPLEMENTATION_PLAN step 7.5a |

### Deviations from Plan
- No deviations from the build plan. All files modified/created as listed. Implementation approach matched plan exactly.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (continuing)
**Commit convention**: one commit per component, message references component code

- [ ] All validation checks above are green
- [ ] `git add` only the files listed in Build Plan + test file, plus IMPLEMENTATION_PLAN and COMPONENT_CHECKLIST (no unrelated changes)
- [ ] Commit message format:
  ```
  refactor(C24): Module Registry Generator conformance tests

  - Tests: N new conformance tests in tests/conformance/test_gen_registry.py
  - Bug 8a fix: aggregation import paths use design-scoped EQN (module_eqn)
  - Bug 8b fix: collision detection + aliased imports for duplicate class names
  - Refs: REQ-REG-01 through REQ-REG-07
  - Design intent: 20-module-registry-generation.md
  ```
- [ ] Committed successfully

---

## Progress Log

### Session: 2026-02-18 — Planning
**Phase**: PLANNING
**Work done**:
- Read design intent doc (20-module-registry-generation.md)
- Read current source (registry.py, graph_builder.py, identifier_types.py)
- Reviewed existing baselines (solar_battery, chain_spike, attr_expr_probe registry_init.py)
- Reviewed accumulated learnings from C20-C22
- Identified 3 design consistency issues (documented in Assessment)
- Produced full test plan (22 test cases) and build plan
**Stopped at**: Plan complete, ready for BUILD
**Next step**: Write test file, then fix registry.py
**Blockers**: None

### Session: 2026-02-18 — TEST + BUILD
**Phase**: BUILD (TEST gate passed, BUILD in progress)
**Work done**:
- Wrote `tests/conformance/test_gen_registry.py` with 22 test cases
- Pre-fix results: 5 FAILED (Bug 8a/8b), 17 PASSED — test gate satisfied
- Bug 8a fix: `registry.py:126` changed from `agg.expression.owning_part_qn` to `agg.module_eqn.replace("__", "::")`
- Bug 8b fix: Added `_resolve_class_name_collisions()` function — groups modules by class_name, generates `{PascalCase(parent_segment)}_{class_name}` aliases, updates import statements to `import X as Alias`, emits `logging.warning()` listing collision names
- All 22 C24 conformance tests pass
- Baselines regenerated: solar_battery changed significantly (design-scoped paths + aliases), chain_spike and attr_expr_probe added `Float` to CUSTOM_SCHEMA_TYPES (pre-existing gap from baseline capture not passing exit_point_primitive_types)
- Lint: only pre-existing UP037 (quoted type annotation in `_generate_schema_imports_from_entry_points`)
**Stopped at**: Full test suite run pending
**Next step**: Run full test suite, validate, update IMPLEMENTATION_PLAN.md
**Blockers**: None

### Session: 2026-02-18 — VALIDATE
**Phase**: DONE (VALIDATE completed)
**Work done**:
- Verified all 22 C24 conformance tests pass
- Full test suite: 1675 passed, 2 skipped, 6 xfailed
- No TODOs or FIXMEs in registry.py or test_gen_registry.py
- Cross-checked implementation against design intent doc (20-module-registry-generation.md) — all 7 REQs satisfied
- Noted alias casing deviation from design doc examples (lowercase vs PascalCase) — documented in Design Doc Updates Needed
- Checked all validation boxes in Section 5
- Filled in Section 6 (Learnings): findings, design doc updates, deviations
- Updated COMPONENT_CHECKLIST.md: 5 AC boxes checked for C24
- Updated IMPLEMENTATION_PLAN.md: step 6.4 marked complete with acceptance note
**Stopped at**: Validation complete, ready for commit
**Next step**: Commit (Section 7)
**Blockers**: None
