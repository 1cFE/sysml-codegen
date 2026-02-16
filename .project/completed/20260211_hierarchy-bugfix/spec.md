# Spec: Hierarchy Pipeline Bug Fixes

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-11 03:57 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Epic:** COST-PATTERN (Item 5 — deviations discovered during E2E validation)

---

## Business Goals

### Why This Matters

Items 1-4 of the COST-PATTERN epic built the hierarchy-aware pipeline across extraction, resolution, and generation layers with 69 unit tests on synthetic data. When run against the real solar_battery model during Item 5 E2E validation, the pipeline produces broken output across all aggregation modules. Two independent root cause analyses identified 8 unique bugs at subsystem boundaries — the individual subsystems work correctly in isolation but have integration gaps where they connect. Zero aggregation auto-implementations exist, module file paths don't match pipeline YAML keys, one assembly is missing entirely, and a critical system-level wiring (`total_capex`) falls through to ENTRY_POINT instead of connecting to the aggregation output chain.

Without these fixes, none of the Item 5 success criteria for aggregation modules can pass and the COST-PATTERN epic cannot close.

### Success Criteria

- [ ] All aggregation `transformed_expression` fields contain correct symbolic text (no `Evaluation()` garbage)
- [ ] All aggregation modules have auto-implemented `_impl.py` files with executable `inputs.X`-form Python
- [ ] All aggregation module wrapper file paths match their pipeline YAML module keys
- [ ] All aggregation stencil file paths are instance-scoped (no PartDef-level collisions)
- [ ] All 4 assemblies produce aggregation modules (including Site Infrastructure)
- [ ] `annualized_financial.total_capex` wires to `MODULE_OUTPUT` (aggregation chain), not `ENTRY_POINT`
- [ ] Multiplicity entry points (`module_count`, `inverter_count`, `pack_count`, etc.) appear in parameter group schemas
- [ ] All existing tests pass with zero regressions

### Priority

P0. Blocks COST-PATTERN epic closure. All 8 bugs are production code defects in Items 2-4 code discovered during Item 5 E2E validation.

---

## Problem Statement

### Current State

The hierarchy-aware pipeline generates 15 aggregation module wrappers but:
- All 15 have empty `Input` classes (zero inputs)
- Zero `_impl.py` files exist for aggregation modules (only 16 total, same as pre-hierarchy)
- All `transformed_expression` fields contain `sum(.(Evaluation()))` instead of real expressions
- All expressions have `has_unsupported_nodes=True`, blocking stencil generation
- Module wrapper directories use PartDef-scoped paths (`solarbatterylibrary__solar_array/`) that don't match pipeline YAML keys (`solarbatterydesign__solar_battery_plant__solar_array__capital_cost`)
- Site Infrastructure (1 of 4 assemblies) is missing entirely from aggregation output
- `annualized_financial.total_capex` is an ENTRY_POINT instead of MODULE_OUTPUT
- Multiplicity parameters (`module_count`, etc.) don't appear in parameter group schemas

### Desired Outcome

`run_codegen()` on solar_battery produces ~36 impl files (16 existing + ~20 aggregation), all with correct auto-implementations, correct file paths matching YAML keys, all 4 assemblies represented, correct wiring to downstream consumers, and multiplicity parameters surfaced in input schemas.

---

## Scope

### In Scope

8 bug fixes across 6 source files, consolidated from two independent root cause analyses.

### Out of Scope

- E2E test writing (remains in Item 5 proper, after these fixes)
- ADR writing (remains in Item 5)
- New feature work
- Non-uniform array support
- TEAx runtime validation

### Edge Cases & Considerations

- **Cascade relationships:** Fixing BF-1 eliminates the `has_unsupported_nodes=True` guard that blocks stencil generation (Report 1 Bug 2B) and the garbage `Evaluation()_capital_cost` YAML input names (Report 1 Bug 3). These are symptoms, not independent bugs.
- **BF-1 → BF-2 dependency:** BF-2 (expression compilation) depends on BF-1 (AST parsing) producing correct symbolic text. BF-2 cannot be validated until BF-1 is fixed.
- **BF-4 and BF-5 are the same pattern** in two locations (module wrappers and stencils). Both use `owning_part_qn` where they should use the instance-scoped module EQN. SHOULD be fixed together.
- **Singleton term wrapping:** Report 1 Open Question 2 asks whether singleton terms (non-sum children like `allocation_model.total_allocation`) are also wrapped in `InvocationExpression(Evaluation)`. The BF-1 fix SHOULD handle this defensively by unwrapping any InvocationExpression wrapper on sum() operands, not just specifically `Evaluation`.
- **Other wrapper patterns:** Report 1 Open Question 3 notes SysIDE might use `collect`, `select`, or other function names. The unwrap logic SHOULD handle any InvocationExpression wrapping, not be hardcoded to `Evaluation`.

---

## Requirements

### Bug Inventory

> Consolidated from `.project/research/20260211-032608_hierarchy-e2e-bug-root-cause-analysis.md` (Report 1, 6 bugs) and `.project/research/20260211_035136_root-cause-hierarchy-deviations.md` (Report 2, 4 deviations). Two overlaps identified; two cascade symptoms eliminated; 8 unique bugs remain.

#### BF-1: sum() AST Evaluation() Wrapper Not Unwrapped

**Source:** Report 1 Bug 1 (CRITICAL)
**Cascade:** Fixes Report 1 Bugs 2B (has_unsupported_nodes guard) and 3 (garbage YAML names)
**Symptom:** All aggregation expressions show `sum(.(Evaluation()))` instead of `sum(pv_module.capital_cost)`. `has_unsupported_nodes` is `True` on all.
**Root cause:** `_walk_aggregation_ast()` in `hierarchy_resolver.py:320-372` expects `sum()` operand to be directly a `FeatureChainExpression`. SysIDE wraps it in `InvocationExpression[func='Evaluation']` (collect semantics). The code hits the `else` branch, gets `str(expr_node)` = `"Evaluation()"`, and marks `has_unsupported=True`.
**Affected file:** `src/sysml_codegen/extraction/hierarchy_resolver.py:320-372`

**Proposed fix (from Report 1):** When `func_name == "sum"`, unwrap operand if it is itself an `InvocationExpression`. Recurse into its operands to find the actual `FeatureChainExpression`. Handle any wrapper function name, not just `Evaluation`.

Also update `reconstruct_expression()` in `expression_utils.py:47-52` for display purposes.

---

#### BF-2: Missing Aggregation Expression Compilation Step

**Source:** Report 2 Deviation 1 (NEW — architecture gap in Item 4)
**Depends on:** BF-1 (needs correct symbolic text as input)
**Symptom:** Even if symbolic text is correct (e.g., `module_count * pv_module.capital_cost`), no compilation step converts it to executable Python (`inputs.module_count * inputs.pv_module_capital_cost`). Zero `_impl.py` files for aggregation modules.
**Root cause:** CalcDef expressions go through a two-phase pipeline: (1) extraction → symbolic text, (2) compilation via `compile_calc_def()` in Step 6.5 → `inputs.X` Python. Aggregation expressions only go through phase 1. `_generate_aggregation_stencils()` writes symbolic text directly into templates, but templates expect `inputs.X` form.
**Affected files:** `src/sysml_codegen/cli/__init__.py:510-589` (stencil generation), `src/sysml_codegen/resolution/graph_builder.py:900-1086` (has the param_name mappings needed)

**Proposed fix (from Report 2):** Add a compilation step that maps symbolic refs to `inputs.X` form using the `ModuleInput.param_name` mappings already computed in `_build_aggregation_module()`. Report 2 recommends Option A: compile in `_build_aggregation_module()` and store on the module, so `_generate_aggregation_stencils()` reads it.

---

#### BF-3: Aggregation Module Input Lookup Case Mismatch

**Source:** Report 1 Bug 2A
**Symptom:** All aggregation module wrappers have empty `Input` classes despite inputs existing on the `PipelineModule`.
**Root cause:** `agg_modules_by_name` dict is keyed by `m.name` (lowercased via `get_module_name()`), but lookup uses `agg.module_eqn` (mixed-case). `"SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost" != "solarbatterydesign__..."`.
**Affected file:** `src/sysml_codegen/cli/__init__.py:427-453`

**Proposed fix (from Report 1):** Change lookup to `agg_modules_by_name.get(get_module_name(agg.module_eqn))` or key the dict by raw `module_eqn`.

---

#### BF-4: Module Wrapper Paths Use PartDef QN, Not Design Instance EQN

**Source:** Report 1 Bug 6
**Symptom:** Module wrapper directories use `solarbatterylibrary__solar_array/` but pipeline YAML keys use `solarbatterydesign__solar_battery_plant__solar_array__capital_cost`. Runtime import would fail.
**Root cause:** `sysml_qn` in `_generate_aggregation_modules()` (`cli/__init__.py:433-443`) is derived from `agg.expression.owning_part_qn` (PartDef QN) instead of the instance-scoped `agg.module_eqn`.
**Affected file:** `src/sysml_codegen/cli/__init__.py:433-443`

**Proposed fix (from Report 1):** Use instance-scoped module EQN for `PythonModulePath.from_sysml()`.

---

#### BF-5: Stencil Paths Use PartDef Scope

**Source:** Report 1 Bug 2C
**Symptom:** Stencil file paths derived from PartDef-level SysML QN. Multiple instances of the same PartDef aggregation would write to the same file (collision). At most 5 unique files per PartDef instead of per-instance.
**Affected file:** `src/sysml_codegen/cli/__init__.py:533`

**Proposed fix (from Report 1):** Use instance-scoped module EQN for stencil path derivation, matching module wrapper convention. Same pattern as BF-4.

---

#### BF-6: Site Infrastructure Missing from Aggregation Scoping

**Source:** Report 1 Bug 4 = Report 2 Deviation 2 (identical root cause)
**Symptom:** Only 3 of 4 assemblies produce aggregation modules. Site Infrastructure is missing. Expected ~20 aggregation modules, got ~15.
**Root cause:** `_scope_aggregation_expressions()` Strategy 2 (`initialization.py:330-338`) does exact name comparison: `seg.lower() == owning_name`. The PartDef name `"Site Infrastructure"` sanitizes to `"site_infrastructure"`, but the PartUsage QN segment is the abbreviated `"site_infra"`. Exact match fails. The other 3 assemblies match by coincidence (PartDef names equal PartUsage names).
**Affected file:** `src/sysml_codegen/generation/initialization.py:296-347`

**Proposed fix options:**
- Report 1: (1) Fuzzy match, (2) PartDef QN → PartUsage name mapping from hierarchy data, (3) Walk design hierarchy via `hierarchy_data.design_overrides`, (4) Direct PartDef QN → design instance path mapping from PartUsage type hierarchy
- Report 2: (1) `startswith`/substring, (2) PartDef QN → PartUsage name mapping from hierarchy data, (3) Normalize both names
- Both reports agree Option 2 (PartDef→PartUsage mapping from hierarchy data) is most robust.

---

#### BF-7: total_capex Wires to ENTRY_POINT Instead of Aggregation Output

**Source:** Report 1 Bug 5 ≈ Report 2 Deviation 4 (same symptom, Report 2 has more precise root cause)
**Symptom:** `annualized_financial.total_capex` resolves to `ENTRY_POINT` (design_params) instead of `MODULE_OUTPUT` from the plant-level aggregation module.
**Root cause (from Report 2):** Composition failure between EXPOSE_PURE alias resolution and aggregation output indexing. The aggregation output index (`dependency_backtracker.py:153-183`) keys on `"solar_battery_plant.capital_cost"` (the underlying attribute name). But the CalcUsage binding references `"total_capex"` (the `:>>` EXPOSE_PURE alias). Two sub-bugs:
  1. **Alias mismatch:** Index has `capital_cost`, binding references `total_capex`
  2. **Case/sanitization mismatch:** `::` fallback uses raw PartDef name `"Solar Battery Plant"` but index uses sanitized `"solar_battery_plant"`

**Affected file:** `src/sysml_codegen/analysis/dependency_backtracker.py:153-183` (index building), `:457-482` (lookup fallbacks)

**Proposed fix (from Report 2):** Register `:>>` redefinition aliases in the aggregation output index. For each aggregation expression, check if the owning PartDef has redefinitions that alias the `attribute_name`, and add index entries for those aliases. Normalize the `::` fallback to sanitize PartDef names. Data source: `hierarchy_data.redefinitions` (already available in graph builder context).

---

#### BF-8: Multiplicity Entry Points Not Surfaced in Parameter Groups

**Source:** Report 2 Deviation 3
**Symptom:** `module_count`, `inverter_count`, `pack_count` etc. don't appear in parameter group schemas or generated JSON input files.
**Root cause:** `_build_aggregation_module()` correctly creates multiplicity entry points in the `entry_points` dict (graph_builder.py:970-995). But `ParameterGroupDeriver.derive_groups()` only produces `ParameterSource` entries from 4 indices (`_attr_index`, `_binding_index`, `_unbound_index`, `_literal_index`). Multiplicity attributes are library PartDef attributes — they appear in none of these indices. Step 6.6 intersection filter (`if p.name in all_ep_names`) has nothing to match against.
**Affected files:** `src/sysml_codegen/resolution/graph_builder.py:190-203` (Step 6.6 rebuild), `src/sysml_codegen/analysis/parameter_groups.py:445-465` (`derive_groups()` indices)

**Proposed fix (from Report 2):** After Step 6.6 filtering, collect orphan entry points (in `entry_points` dict but not covered by any `ParameterGroup`). Either (A) assign to nearest matching group by instance_path prefix, or (B) create a synthetic group for multiplicity/count parameters.

---

### Fix Ordering

Recommended order based on dependency analysis and effort:

| Order | Bug | Effort | Rationale |
|-------|-----|--------|-----------|
| 1 | BF-1 (AST Evaluation() unwrap) | Medium | Prerequisite for BF-2; cascade-fixes 2 symptoms |
| 2 | BF-4 + BF-5 (path PartDef → instance) | Low | Same pattern in 2 locations; fixes runtime-fatal import mismatch |
| 3 | BF-3 (case mismatch lookup) | Trivial | One-line fix |
| 4 | BF-6 (site_infra scoping) | Small | Unblocks 4th assembly; both reports agree on approach |
| 5 | BF-7 (total_capex EXPOSE_PURE alias) | Medium | Needs redefinition data threaded into backtracker |
| 6 | BF-8 (multiplicity EPs) | Small | Post-filtering step; independent |
| 7 | BF-2 (expression compilation) | Medium-Large | Largest fix; depends on BF-1 producing correct symbolic text |

### Dependency Graph

```
BF-1 (AST parsing)
  |
  +--[prerequisite]--> BF-2 (expression compilation)
  |
  +--[cascade-fixes]--> Report 1 Bug 2B (has_unsupported guard)
  +--[cascade-fixes]--> Report 1 Bug 3 (garbage YAML names)

BF-3 (case mismatch)     -- independent
BF-4 + BF-5 (path fixes) -- independent
BF-6 (site_infra)        -- independent
BF-7 (total_capex)       -- independent
BF-8 (multiplicity EPs)  -- independent
```

### Non-Functional Requirements

- All 8 fixes MUST maintain backward compatibility with existing CalcDef-based pipeline (chain_spike, CATF MFE models)
- Fixes MUST NOT change any public API signatures
- Each fix SHOULD be independently testable with existing unit test infrastructure

---

## Acceptance Criteria

### Per-Bug Verification

- [ ] **BF-1:** `transformed_expression` shows real expressions (e.g., `module_count * pv_module.capital_cost`), not `Evaluation()`. `has_unsupported_nodes` is `False` for all solar_battery aggregation expressions.
- [ ] **BF-2:** Aggregation `_impl.py` files exist with executable `inputs.X`-form Python. `ast.parse()` succeeds on all.
- [ ] **BF-3:** All aggregation module wrappers have populated `Input` classes matching their `PipelineModule.inputs`.
- [ ] **BF-4:** Module wrapper directories use design-instance-scoped names (e.g., `solarbatterydesign__solar_battery_plant__solar_array/`).
- [ ] **BF-5:** Stencil file paths are instance-scoped. No file collisions for same PartDef.
- [ ] **BF-6:** Site Infrastructure produces aggregation modules (total assembly count = 4).
- [ ] **BF-7:** `annualized_financial.total_capex` wires to `MODULE_OUTPUT` from plant-level aggregation, not `ENTRY_POINT`.
- [ ] **BF-8:** `module_count`, `inverter_count`, `pack_count` (and any other multiplicity attrs) appear in parameter group schemas with appropriate types.

### Integration

- [ ] Total impl file count increases from 16 to expected ~36 (16 existing + ~20 aggregation)
- [ ] `IMPLEMENTATION_BACKLOG.md` shows "0 functions to implement"
- [ ] Pipeline YAML has valid Python identifiers for all input parameter names
- [ ] All existing tests pass (`uv run pytest tests/`) with zero regressions

---

## Related Artifacts

- **Root Cause Report 1:** `.project/research/20260211-032608_hierarchy-e2e-bug-root-cause-analysis.md`
- **Root Cause Report 2:** `.project/research/20260211_035136_root-cause-hierarchy-deviations.md`
- **Original Strategy:** `.project/research/20260202-180000_expression-compilation-and-inline-math-strategy.md`
- **E2E Validation Spec:** `.project/active/hierarchy-e2e/spec.md` (Item 5 — these fixes are deviations from that spec)
- **Epic:** `.project/backlog/epic_costed_component_pattern.md`
- **Design:** `.project/active/hierarchy-bugfix/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
