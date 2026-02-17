# Component: FORMULA Module Factory (C15)

**Status**: DONE
**Created**: 2026-02-17
**Last updated**: 2026-02-17
**Updated by**: Planning session

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` -- C15
- **Design intent**: [05-module-factory.md](../../concepts/refactor-design-intent/05-module-factory.md) (Section 3), [16-computed-attributes.md](../../concepts/refactor-design-intent/16-computed-attributes.md)
- **Requirements**: REQ-MF-01, REQ-MF-03, REQ-MF-05
- **Depends on**: C08 (OutputRegistry -- done), C05 (ComputedAttributeData + classification -- done), C14 (CalcUsage factory -- done, helper reusable)

---

## 1. Assessment

### What This Component Does

`_build_computed_attr_module()` (graph_builder.py:643-758) builds a PipelineModule from a FORMULA ComputedAttributeData. It extracts input names from the `compiled_expression` via `inputs\.(\w+)` regex, looks up each in the pre-computed attribute resolution map, wires FORMULA/EXPOSE_ALIAS entries to upstream `module_output` channels and LITERAL/unresolved entries to `entry_point` sources, then produces a single-output PipelineModule with `is_computed_attribute=True` and `compilability=FULLY_COMPILABLE`.

### Current State

- **Exists?** Yes -- `src/sysml_codegen/resolution/graph_builder.py` lines 643-758
- **Needs extraction/refactoring?** No structural changes needed for C15. Extraction to a standalone module is deferred to Phase 7.
- **Current test coverage**: Existing unit tests in `tests/unit/test_graph_builder.py` use mocks and constructed data. The X02 dual resolution tests verify the attribute resolution map consistency. No conformance tests exercise `_build_computed_attr_module()` directly with real FORMULA data.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc(s)
- [x] No contradictions with other component specs (one deviation documented below)
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **Entry points mutation deviates from REQ-MF-01 "pure data transformer" claim.** The function signature says `entry_points: dict[str, EntryPoint]` is "Mutable dict -- new entry points may be added" (docstring line 655). Lines 720-726 mutate the shared entry_points dict by adding new entry points for LITERAL/unresolved inputs. REQ-MF-01 says "no mutation of shared state" and the target interface is `return (PipelineModule, dict[str, EntryPoint])`. **This is the same pattern as C14 Issue #1** -- the current implementation achieves the right outcome (factory-created entry points surface in the final graph) via mutation rather than the target return-tuple interface. **Resolution**: Test current behavior. Verify that new entry points ARE created with correct type (DESIGN_ATTRIBUTE). Note the mutation as a known deviation from REQ-MF-01's "pure" property for Phase 7 when the return-tuple interface is adopted.

2. **`compiled_expression` not copied from ComputedAttributeData to PipelineModule.** The factory at line 750 creates PipelineModule without setting `compiled_expression`, so it defaults to None. But `ComputedAttributeData.compiled_expression` has the full Python expression (e.g., `"(inputs.panel_count * inputs.panel_wattage)"`). The design doc (Section 3) says the expression compiler "already produced compiled_expression with inputs.X refs" -- implying it should be available on the module. **Resolution**: Document this as a gap. The compiled expression IS available on the ComputedAttributeData passed to the factory; the stencil generator may read it from there rather than from PipelineModule. Test the actual behavior (PipelineModule.compiled_expression is None).

3. **catf_mfe_model has zero FULLY_COMPILABLE FORMULAs.** The 2 FORMULA attrs in catf_mfe are MANUAL_REQUIRED (compilation failed). Only attr_expr_probe (14) and solar_battery_model (1) produce FORMULA modules. **Resolution**: Use attr_expr_probe as primary fixture, solar_battery_model as secondary. Exclude catf_mfe from parametrization (no FORMULA modules to build).

4. **FORMULA-to-FORMULA wiring testable in attr_expr_probe.** The `cost = area * rate` attribute references `area` (another FORMULA) and `rate` (a literal). The resolution map classifies `area` as `kind=FORMULA` with a channel. So `inputs.area` wires to `module_output`, while `inputs.rate` wires to `entry_point`. Similarly, `marked_up_cost` references `cost` (FORMULA) + `markup` (literal), and `cost_density` references `cost` (FORMULA) + `volume` (FORMULA). These are natural test cases for mixed wiring.

### Risks & Unknowns

- **Low risk**: The function is 115 lines, well-understood from the C14 pattern. Resolution map building is verified by X02.
- **Known**: attr_expr_probe has rich FORMULA data (14 attrs, including FORMULA-to-FORMULA chains). solar_battery_model has 1 simple FORMULA (`p_net_kw = p_net_mw * 1000.0`).
- **Risk #6 from IMPLEMENTATION_PLAN applies**: "The attribute resolution map is pre-computed at classification time. If classification logic changes, FORMULA wiring can silently break. Conformance tests must verify map -> module wiring chain end-to-end."

---

## 2. Spike

**Decision**: SKIP
**Rationale**: The FORMULA factory follows the same pattern as C14 (lookup + wire), with the resolution map as the pre-computed data source instead of binding_resolutions. The resolution map building is already tested in X02 (FORMULA channels in SysML QN registry, EXPOSE_PURE channels in canonical_channels). attr_expr_probe has 14 FORMULA attrs with known compiled expressions (locked down by C05). No unknowns that need empirical investigation.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_factory_formula.py`
**Fixture data**: attr_expr_probe (primary, 14 FORMULA+FULLY_COMPILABLE), solar_battery_model (secondary, 1 FORMULA+FULLY_COMPILABLE)

### Test Infrastructure Needed

**Helper**: `build_formula_factory_inputs_from_snapshot(model_name)` -- extends the C14 pattern:
1. Load extraction snapshot
2. Build OutputRegistry via `build_output_registry()`
3. Run DependencyBacktracker to get BacktrackingResult
4. Build calc_def_map, ParameterGroupDeriver, design_attrs
5. Classify entry points via `_classify_entry_points()`
6. Build calc_usage_names from `result.required_usages`
7. Build `attr_resolution_map` via `_build_attribute_resolution_map()`
8. Filter `computed_attributes` to FORMULA + FULLY_COMPILABLE only
9. Return `(formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap)`

This helper reuses the C14 `build_factory_inputs_from_snapshot` pattern and adds Steps 6-8 for the FORMULA-specific data.

### Test Cases

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_returns_pipeline_module[model]` | REQ-MF-01 | Return type is PipelineModule with non-empty name, module_type, outputs. Parametrized over 2 models. |
| `test_module_name_from_ca_qn[model]` | REQ-MF-01 | `module.name == get_module_name(sysml_to_python_qualified_name(f"{ca.owning_part_qualified_name}::{ca.name}"))` for every FORMULA module. |
| `test_module_type_from_ca_qn[model]` | REQ-MF-01 | `module.module_type == derive_module_type(f"{ca.owning_part_qualified_name}::{ca.name}")` for every FORMULA module. |
| `test_entry_point_creation[model]` | REQ-MF-01 | Factory adds new entry points to the entry_points dict for LITERAL inputs. New EPs have expected `ep_qname` format (`{part_eqn}__{input_name}`). |
| `test_is_computed_attribute_true[model]` | REQ-MF-03 | `module.is_computed_attribute == True` for every FORMULA module. |
| `test_compilability_fully_compilable[model]` | REQ-MF-03 | `module.compilability == Compilability.FULLY_COMPILABLE` for every FORMULA module. |
| `test_is_aggregation_false[model]` | REQ-MF-03 | `module.is_aggregation == False` for every FORMULA module. |
| `test_raises_on_missing_compiled_expression` | REQ-MF-03 | `ValueError` raised when `ca.compiled_expression is None` (guarded at line 667-670). Uses constructed data with real QNs. |
| `test_every_input_has_one_source[model]` | REQ-MF-05 | Each `input.source.source_type in {"module_output", "entry_point"}` for every FORMULA module. |
| `test_input_names_match_compiled_expression[model]` | REQ-MF-05 | Input `param_name` set matches unique `inputs\.(\w+)` regex results from `ca.compiled_expression`. Order preserved. |
| `test_formula_inputs_wire_to_module_output[model]` | REQ-MF-05 | For inputs resolved as FORMULA/EXPOSE_ALIAS in the resolution map: `source.source_type == "module_output"` and `source.producer_channel == attr_res.channel_name`. |
| `test_literal_inputs_wire_to_entry_point[model]` | REQ-MF-05 | For inputs not in resolution map (or kind=LITERAL): `source.source_type == "entry_point"` with correct `qualified_name`. |
| `test_single_output_field_name_root[model]` | REQ-MF-05 | `len(module.outputs) == 1` and `module.outputs[0].field_name == "root"`. |
| `test_output_channel_name_pqn[model]` | REQ-MF-05 | `module.outputs[0].channel_name == get_channel_name(module_eqn, ca.python_name)`. |
| `test_factory_entry_points_design_attribute[model]` | REQ-MF-05 | Every entry point created by the factory has `entry_type == EntryPointType.DESIGN_ATTRIBUTE`. Track new EP keys before/after factory call. |
| `test_formula_to_formula_wiring` | REQ-MF-05 | In attr_expr_probe: `cost` module's `inputs.area` wires to `module_output` (area's FORMULA channel). `marked_up_cost` module's `inputs.cost` wires to `module_output`. `cost_density` module's `inputs.cost` and `inputs.volume` both wire to `module_output`. |
| `test_expose_alias_input_wiring` | REQ-MF-05 | In attr_expr_probe: if any FORMULA input resolves via EXPOSE_ALIAS in the resolution map, verify `source.source_type == "module_output"` with the alias channel. |
| `test_default_value_from_design_attrs[model]` | REQ-MF-05 | Entry points created for LITERAL inputs have `default_value` populated from design_attrs when available (e.g., `panel_count=20`, `panel_wattage=400.0` in solar_battery). |
| `test_execution_order_zero` | REQ-MF-01 | `module.execution_order == 0` for all FORMULA modules (reassigned during unified toposort). |

**Model parametrization**: `["attr_expr_probe", "solar_battery_model"]`
- attr_expr_probe: 14 FORMULA+FULLY_COMPILABLE, 3 EXPOSE_PURE, rich FORMULA-to-FORMULA chains
- solar_battery_model: 1 FORMULA+FULLY_COMPILABLE (p_net_kw = p_net_mw * 1000.0), 1 EXPOSE_PURE (on PartDef, no alias)

### Gate: Ready for BUILD

- [x] Test file exists with all test cases written
- [x] Tests run (expected: all PASS -- conformance-only, no code changes)
- [x] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify

None -- C15 is conformance-only. No production code changes.

### Files to Create

| File | Purpose |
|------|---------|
| `tests/conformance/test_factory_formula.py` | C15 conformance tests (~20 test cases, ~36 collected with parametrization) |

### Implementation Notes

1. **Helper pattern**: Build `build_formula_factory_inputs_from_snapshot()` at the top of the test file. Reuses the C14 pattern (load snapshot → build registry → run backtracker → classify entry points) and adds resolution map building + FORMULA filtering. This is the C14 learning: "build_factory_inputs_from_snapshot() is a clean superset of build_backtracker_from_snapshot(). Reusable for C15-C18."

2. **Import `_build_computed_attr_module` directly**: In `__all__` of graph_builder.py (line 1418). Also import `_build_attribute_resolution_map`, `AttributeResolution`, `AttributeResolutionKind`.

3. **Session-scoped fixtures**: Each model's factory inputs are expensive to build (snapshot load + registry + backtracker + resolution map). Use `@pytest.fixture(scope="session")`.

4. **Track entry point creation**: Before calling `_build_computed_attr_module()`, snapshot `set(entry_points.keys())`. After, diff to find new entry points created by the factory. This is how we verify DESIGN_ATTRIBUTE typing without asserting purity.

5. **FORMULA-to-FORMULA chain verification**: In attr_expr_probe:
   - `cost` (inputs: area[FORMULA], rate[LITERAL]) -- mixed wiring
   - `marked_up_cost` (inputs: cost[FORMULA], markup[LITERAL]) -- chain depth 2
   - `cost_density` (inputs: cost[FORMULA], volume[FORMULA]) -- both FORMULA

   Build all 14 FORMULA modules, then verify specific wiring for these 3 chain cases against the resolution map.

6. **Test class grouping** (following C14 pattern):
   - `TestPipelineModuleConstruction` (REQ-MF-01): return type, naming, execution_order, entry point creation
   - `TestFormulaFlags` (REQ-MF-03): is_computed_attribute, compilability, is_aggregation, ValueError guard
   - `TestInputWiring` (REQ-MF-05): source types, resolution map fidelity, FORMULA-to-FORMULA, EXPOSE_ALIAS
   - `TestOutputNaming` (REQ-MF-05): single output, field_name="root", channel PQN, default values

7. **Building modules for all FORMULA CAs**: Create a `_build_all_formula_modules()` helper that iterates over the FORMULA CAs and calls `_build_computed_attr_module()` for each, returning `list[(PipelineModule, ComputedAttributeData)]`.

### Gate: Ready for VALIDATE

- [x] All test cases pass (34 passed, 2 skipped)
- [x] No regressions in full test suite (1431 passed, 2 skipped, 5 xfailed)
- [x] Lint clean (no new lint issues in test file)

---

## 5. Validation

- [x] Every acceptance criterion from COMPONENT_CHECKLIST is satisfied (7/7 ACs covered)
- [x] Every REQ-MF-01, REQ-MF-03, REQ-MF-05 has at least one passing test
- [x] Full test suite passes (record count: 1431 tests, 0 failures, 2 skipped, 5 xfailed)
- [x] Cross-check: re-read design intent doc, verify implementation matches
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### Baseline Impact

None expected. C15 is conformance-only -- no production code changes, no output changes.

---

## 6. Learnings

### Findings

1. **solar_battery has zero FORMULA-to-FORMULA wiring.** Its single FORMULA (`p_net_kw = p_net_mw * 1000.0`) has only a LITERAL input. All FORMULA-to-FORMULA chain tests (cost→area, marked_up_cost→cost, cost_density→cost+volume) run on attr_expr_probe only. Test uses `pytest.skip()` for solar_battery's `test_formula_inputs_wire_to_module_output`.

2. **No EXPOSE_ALIAS inputs found in attr_expr_probe FORMULA modules.** The 3 EXPOSE_PURE attrs in attr_expr_probe resolve to channels, but no FORMULA's `compiled_expression` references an EXPOSE_PURE attr by python_name. The resolution map has EXPOSE_ALIAS entries, but they're not consumed as FORMULA inputs. Test skips gracefully.

3. **Entry point mutation confirmed.** Assessment Issue #1 verified: `_build_computed_attr_module()` mutates the shared `entry_points` dict (lines 720-726). 15+ new entry points created for attr_expr_probe's LITERAL inputs (rate, markup, height, r_inner, r_outer, r_major, eta_thermal, eta_direct, m_neutron, f_pump, eta_pump, f_subsystem, p_input, length, width). All typed DESIGN_ATTRIBUTE as expected.

4. **36 tests collected (34 passed, 2 skipped).** 20 unique test methods, parametrized over 2 models = ~36 collected. The 2 skips are expected (solar_battery has no module_output FORMULA inputs, no EXPOSE_ALIAS in FORMULA expressions).

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| 05-module-factory.md | Note `_build_computed_attr_module()` does not copy `compiled_expression` from ComputedAttributeData to PipelineModule | Issue #2 from Assessment. Stencil generation may read from CA directly. |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| C16 (Aggregation Factory) | Same helper pattern applies | Extend helper with aggregation data |
| C17 (Entry Point Classification) | Factory-created EPs must not be re-classified | Verify factory EPs retain DESIGN_ATTRIBUTE |

### Deviations from Plan

1. **Plan said "~19 test cases, ~40+ collected with parametrization"** — actual: 20 test methods, 36 collected (2 skipped). Slightly under 40 because some tests (FORMULA-to-FORMULA wiring, EXPOSE_ALIAS, ValueError, default_value) are not parametrized. 20th test (`test_entry_points_mutated_by_factory`) added during review.

2. **`test_formula_inputs_wire_to_module_output` uses `pytest.skip()` instead of hard assertion for solar_battery.** The plan expected this test to pass for both models, but solar_battery has only LITERAL inputs. Changed assertion to skip for models with no module_output wiring.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (continuing existing branch)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [x] `git add` only the files listed in Build Plan + test file, plus IMPLEMENTATION_PLAN and COMPONENT_CHECKLIST (no unrelated changes)
- [x] Commit message format:
  ```
  refactor(C15): FORMULA Module Factory conformance tests

  - Tests: 34 new conformance tests in tests/conformance/test_factory_formula.py
  - Refs: REQ-MF-01, REQ-MF-03, REQ-MF-05
  - Design intent: 05-module-factory.md, 16-computed-attributes.md
  ```
- [x] Committed successfully

---

## Progress Log

### Session: 2026-02-17 -- Planning
**Phase**: PLANNING
**Work done**:
- Read all context: IMPLEMENTATION_PLAN (step 4.2), COMPONENT_CHECKLIST (C15), design docs 05 + 16, graph_builder.py source (lines 526-758), C14 plan + test file for patterns
- Explored fixture data: attr_expr_probe has 14 FORMULA+FULLY_COMPILABLE, solar_battery has 1, catf_mfe has 0 (both FORMULAs are MANUAL_REQUIRED)
- Completed design consistency review -- 4 issues found (entry_points mutation, compiled_expression gap, catf_mfe exclusion, FORMULA-to-FORMULA test opportunity)
- Designed 19 test cases covering all 3 requirements (REQ-MF-01, REQ-MF-03, REQ-MF-05)
- Made SKIP decision for spike (resolution map verified by X02, attr_expr_probe data well-understood from C05)
- Checked accumulated learnings: C14 helper reusable, X02 resolution map verified, C05 FORMULA expressions locked down
**Stopped at**: Plan complete, ready for build
**Next step**: Build phase -- create test file, run tests, validate
**Blockers**: None

### Session: 2026-02-17 -- Build + Validate
**Phase**: PLANNING → VALIDATE
**Work done**:
- Created `tests/conformance/test_factory_formula.py` with 19 test methods (34 collected, 32 passed, 2 skipped)
- Helper: `build_formula_factory_inputs_from_snapshot()` extending C14 pattern with resolution map + FORMULA filtering
- Helper: `_build_all_formula_modules()` for building all FORMULA modules from CAs
- 4 test classes: TestPipelineModuleConstruction (REQ-MF-01), TestFormulaFlags (REQ-MF-03), TestInputWiring (REQ-MF-05), TestOutputNaming (REQ-MF-05)
- FORMULA-to-FORMULA chain tests: cost(area+rate), marked_up_cost(cost+markup), cost_density(cost+volume) -- all verified
- Full suite: 1429 passed, 2 skipped, 5 xfailed, 0 failures
- No mocks (grep verified), no TODOs/FIXMEs, no lint issues in test file
- All 7 COMPONENT_CHECKLIST ACs verified
**Stopped at**: Validation complete, ready for review fixes and commit
**Next step**: Address review findings, update status docs, commit
**Blockers**: None

### Session: 2026-02-17 -- Review Fixes + Commit
**Phase**: VALIDATE → COMMIT
**Work done**:
- Addressed 3 review findings (1 MEDIUM, 2 LOW):
  - Finding #1 (MEDIUM): Added `test_entry_points_mutated_by_factory` — explicit purity-deviation test symmetric to C14's `test_no_mutation_of_entry_points`. Verifies mutation occurs and existing EPs are unmodified.
  - Finding #2 (LOW): No action needed — resolution map coverage from C05 + X02 is sufficient cross-component coverage for Risk #6.
  - Finding #3 (LOW): Replaced fragile `len(formula_cas) > 1` model-name heuristic with explicit `snap["_model_name"]` tracking in `build_formula_factory_inputs_from_snapshot()`.
- Test count: 36 collected (34 passed, 2 skipped) — up from 34 collected (32 passed)
- Full suite verified: 1431 passed, 2 skipped, 5 xfailed, 0 failures
- Updated IMPLEMENTATION_PLAN test count, plan.md learnings + progress log
**Stopped at**: Commit ready
**Next step**: None — C15 complete
**Blockers**: None
