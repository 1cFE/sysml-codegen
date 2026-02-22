---
date: 2026-02-11T03:26:08+00:00
researcher: Claude
topic: "Root cause analysis of hierarchy pipeline bugs found during COST-PATTERN E2E discovery"
tags: [research, codegen, bugs, hierarchy, aggregation, pipeline]
status: complete
last_updated: 2026-02-11
---

# Research: Hierarchy Pipeline E2E Bug Root Cause Analysis

**Date**: 2026-02-11T03:26:08+00:00
**Researcher**: Claude
**Research Type**: Codebase / Bug Analysis

## Research Question

After completing Items 1-4 of the COST-PATTERN epic, the Phase 1 discovery run for E2E validation (Item 5) reveals that the hierarchy-aware pipeline is producing broken output. The plan's Phase 2 structural tests would fail extensively. What are the root causes, and how do they chain together?

## Summary

- **6 distinct bugs identified**, 3 of which are cascading (fixing upstream bugs may eliminate downstream symptoms)
- **The root cause of most failures is Bug 1: `_walk_aggregation_ast()` cannot parse SysIDE's actual AST representation of `sum()` expressions.** SysIDE wraps `sum()` operands in a `collect`-style `InvocationExpression` with `function.name='Evaluation'` rather than a simple `FeatureChainExpression`. The spike (Item 1) found InvocationExpression nodes and confirmed `function.name='sum'`, but did not probe the operand's internal structure deeply enough.
- **Fixing Bug 1 will cascade-fix Bugs 2 and 3** (aggregation modules will get correct inputs and auto-implementations). Bugs 4, 5, and 6 are independent.
- **Total: 16 impl files generated instead of expected ~36** (16 existing + ~20 aggregation). Zero aggregation impl files exist. Zero aggregation modules have inputs. `annualized_financial.total_capex` is an ENTRY_POINT instead of MODULE_OUTPUT.

## Detailed Findings

### Bug 1 (CRITICAL): `_walk_aggregation_ast()` Cannot Parse `sum()` Operand Structure

**Symptom**: All aggregation expressions show `sum(.(Evaluation()))` instead of `sum(pv_module.capital_cost)`. The `transformed_expression` contains `Evaluation()` strings. `has_unsupported_nodes` is set to `True` on all aggregation expressions.

**Evidence**: Pipeline YAML shows:
```yaml
  # source: aggregation (solarbatterylibrary__solar_array.capital_costModule)
```
Module wrappers show:
```
SysML Expression: sum(.(Evaluation())) + .(Evaluation()) + .(Evaluation())
```

**Root Cause**: The spike (Item 1, Q6) confirmed that `sum()` appears as `InvocationExpression` with `function.name='sum'` and its operand is described as a "FeatureChainExpression for the collection path." However, the actual SysIDE AST structure wraps the `sum()` operand in an intermediate `InvocationExpression` node whose `function.name` is `'Evaluation'` (SysML's collect/select semantics).

The actual tree is:
```
InvocationExpression [func='sum']
  InvocationExpression [func='Evaluation']     <-- NOT FeatureChainExpression!
    FeatureChainExpression                      <-- actual pv_module.capital_cost
```

In `hierarchy_resolver.py:325-330`, the code expects the `sum()` operand to be directly a `FeatureChainExpression` or `FeatureReferenceExpression`:

```python
if func_name == "sum" and operands:
    operand = operands[0]
    if SysideAdapter.is_instance(operand, "FeatureChainExpression"):
        chain_name = extract_feature_chain_name(operand)
    else:
        chain_name = extract_feature_reference_name(operand)
```

When the operand is an `InvocationExpression` (function='Evaluation'), neither check matches. `extract_feature_reference_name()` falls through all its checks and returns `str(expr_node)` which produces `"Evaluation()"` or similar.

This cascades:
1. `chain_name` = `"Evaluation()"` (not `"pv_module.capital_cost"`)
2. `chain_name.split(".", 1)` produces 1 part (no dot) or wrong parts
3. `SumTerm` gets garbage `part_usage_name="Evaluation()"`
4. Multiplicity lookup fails (no part named "Evaluation()")
5. Expression text = `"Evaluation()"` instead of real expression

Furthermore, singleton terms (non-sum children like `array_bos.capital_cost`) go through the `FeatureChainExpression` branch at line 374-379, which works correctly. But `allocation_model.total_allocation` may also be wrapped in an intermediate expression depending on the SysML AST.

Additionally, the `Evaluation()` InvocationExpression at line 366-372 triggers the "Non-sum invocation" branch:
```python
# Non-sum invocation -- mark as unsupported, still reconstruct
ctx.has_unsupported = True
```

This sets `has_unsupported_nodes=True`, which blocks all stencil generation (Bug 2).

**Files affected**: `src/sysml_codegen/extraction/hierarchy_resolver.py:320-372`

**Fix approach**: When `func_name == "sum"`, unwrap the operand if it is itself an `InvocationExpression`. The pattern should be:
```python
if func_name == "sum" and operands:
    operand = operands[0]
    # SysIDE wraps sum() operand in collect/Evaluation — unwrap
    if hasattr(operand, "function") and hasattr(operand.function, "name"):
        # Unwrap Evaluation() wrapper to get actual collection expression
        inner_operands = list(getattr(operand, "operands", []))
        if inner_operands:
            operand = inner_operands[0]
    # Now operand should be FeatureChainExpression
    if SysideAdapter.is_instance(operand, "FeatureChainExpression"):
        chain_name = extract_feature_chain_name(operand)
    else:
        chain_name = extract_feature_reference_name(operand)
```

Also, `reconstruct_expression()` in `expression_utils.py:47-52` should handle this pattern for display purposes, but the critical fix is in `_walk_aggregation_ast()`.

**Validation**: After fix, `transformed_expression` should show `(module_count * pv_module.capital_cost)` instead of `Evaluation()`. `has_unsupported_nodes` should be `False` for all solar_battery aggregation expressions.

---

### Bug 2 (CASCADE from Bug 1): Aggregation Modules Have Zero Inputs and No Auto-Implementation

**Symptom**: All 15 aggregation module wrappers have empty `Input` classes. All say "GAP: Code generator does NOT implement calc logic." No `_impl.py` files generated for aggregation modules. Only 16 impl files total (same as pre-hierarchy).

**Root Cause (Part A — inputs)**: In `cli/__init__.py:427-453`, the lookup dict `agg_modules_by_name` is keyed by `m.name` (lowercased via `get_module_name()`), but the lookup query uses `agg.module_eqn` (mixed-case, from `ScopedAggregationData.module_eqn` property). The case mismatch causes every lookup to return `None`, so the `else` branch generates with `input_names = []`.

```python
# Line 427-431: Dict keyed by m.name (lowercase)
agg_modules_by_name = {m.name: m for m in ctx.computation_graph.modules if m.is_aggregation}

# Line 453: Lookup with agg.module_eqn (mixed-case)
pipeline_module = agg_modules_by_name.get(agg.module_eqn)  # ALWAYS None
```

`m.name = get_module_name(agg.module_eqn) = agg.module_eqn.lower()`, so `"SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost" != "solarbatterydesign__solar_battery_plant__solar_array__capital_cost"`.

**Root Cause (Part B — stencils)**: In `cli/__init__.py:526-530`, the guard conditions block ALL stencil generation:

```python
for agg in (ctx.aggregation_expressions or []):
    if agg.expression.has_unsupported_nodes:   # True due to Bug 1 → SKIP
        continue
    if not agg.expression.transformed_expression:
        continue
```

Because Bug 1 sets `has_unsupported_nodes=True` on every aggregation expression, the loop body never executes.

**Root Cause (Part C — stencil path scoping)**: Even if stencils were generated, the file path is derived from the PartDef-level SysML QN (`cli/__init__.py:533`), NOT the instance-scoped module EQN. Multiple instances of the same PartDef aggregation would write to the same file path. This would produce at most 5 unique files per PartDef (not per-instance).

**Files affected**: `src/sysml_codegen/cli/__init__.py:427-453` (input lookup), `:526-530` (stencil guard), `:533` (stencil path)

**Fix approach**:
- Part A: Change lookup to `agg_modules_by_name.get(get_module_name(agg.module_eqn))` or key the dict by the raw `module_eqn` used during graph building.
- Part B: Will be fixed automatically when Bug 1 is fixed (expressions become compilable → `has_unsupported_nodes=False`).
- Part C: Use instance-scoped module EQN for stencil path derivation, matching how the module wrapper uses instance-scoped naming.

---

### Bug 3 (CASCADE from Bug 1): Aggregation Module Pipeline YAML Inputs are Broken

**Symptom**: Pipeline YAML for aggregation modules shows:
```yaml
solarbatterydesign__solar_battery_plant__solar_array__capital_cost:
    input: Evaluation()_capital_cost = float SolarBatteryDesign__...
```

The input parameter name `Evaluation()_capital_cost` is not a valid Python identifier.

**Root Cause**: The garbage `SumTerm(part_usage_name="Evaluation()")` from Bug 1 propagates through the graph builder's `_build_aggregation_module()` where:
```python
param_name = f"{term.part_usage_name}_{term.attribute_name}"
```
becomes `"Evaluation()_capital_cost"`.

**Files affected**: `src/sysml_codegen/resolution/graph_builder.py` (graph builder propagates Bug 1 data)

**Fix approach**: Fixing Bug 1 eliminates this — `SumTerm.part_usage_name` will correctly be `"pv_module"`, producing valid param names like `"pv_module_capital_cost"`.

---

### Bug 4 (INDEPENDENT): Site Infrastructure Aggregation Modules are MISSING

**Symptom**: Pipeline YAML shows aggregation modules for `solar_array` (5), `battery_system` (5), and `solar_battery_plant` (5), but ZERO for `site_infra`. Expected: 4 assemblies x 5 attributes = 20 total. Actual: 15.

**Root Cause**: `_scope_aggregation_expressions()` in `initialization.py:296-347` uses two strategies to find design instance paths for PartDef-level aggregation expressions, both of which fail for Site Infrastructure:

**Strategy 1** (line 322-326): Looks for virtual CalcUsages whose `owning_part_def_qn` matches the aggregation expression's `owning_part_qn`. Site Infrastructure's PartDef has NO CalcUsages (no `cost_model` calcusage on the PartDef itself — only its children have them). So `virtual_qns_by_partdef.get(agg_expr.owning_part_qn)` returns `[]`.

**Strategy 2** (line 329-338): Searches all virtual CalcUsage QN segments for a match against `owning_name`. The code looks for `"site_infra"` as a segment in CalcUsage QNs like `"SolarBatteryDesign__solar_battery_plant__site_infra__racking__cost_model"`. If the QN contains `"site_infra"` as a segment, it would be found. However:
- The `owning_name` is derived from `agg_expr.owning_part_name`, which comes from `sanitize_name(getattr(part_element, "name", ""))`. If the PartDef's name is `'Site Infrastructure'`, then `sanitize_name("Site Infrastructure") = "Site_Infrastructure"` and `owning_name = "site_infrastructure"` (lowered).
- The QN segment would be `"site_infra"` (as shown in pipeline YAML), NOT `"site_infrastructure"`.
- `"site_infra" != "site_infrastructure"` → Strategy 2 also fails.

The mismatch is between the PartDef's full name (`Site Infrastructure` → `site_infrastructure`) and the abbreviated PartUsage name in the design (`site_infra`).

**Files affected**: `src/sysml_codegen/generation/initialization.py:296-347`

**Fix approach**: Strategy 2 needs a more robust matching approach. Options:
1. Fuzzy match (e.g., check if segment starts with owning_name prefix or vice versa)
2. Use the PartDef's QN to match against CalcUsage QN prefixes (not just name segments)
3. Add a third strategy that walks the design hierarchy directly using `hierarchy_data.design_overrides` or PartUsage elements to find which PartUsages specialize which PartDefs
4. Most robust: build a direct `PartDef QN → design instance paths` mapping from the PartUsage type hierarchy (same traversal used in template instantiation), rather than reverse-engineering from CalcUsage QNs

---

### Bug 5 (INDEPENDENT): `annualized_financial.total_capex` Wired as ENTRY_POINT

**Symptom**: Pipeline YAML shows:
```yaml
solarbatterydesign__solar_battery_plant__annualized_financial:
    input: total_capex = float design_params.SolarBatteryDesign__...total_capex
```

`total_capex` should be wired to the plant's `capital_cost` aggregation module output channel (MODULE_OUTPUT), not to `design_params` (ENTRY_POINT).

**Root Cause**: The backtracker resolves `annualized_financial`'s `total_capex` binding BEFORE the aggregation module outputs are available in the resolution context. The sequencing is:

1. Step 6 in `build_pipeline_context()`: Backtracker traces dependencies for all CalcUsages
2. Step 7: `build_computation_graph()` creates modules including aggregation modules

The backtracker at step 6 builds its resolution context from:
- CalcUsage outputs (from calc defs)
- Computed attribute outputs (FORMULA/EXPOSE)
- Design attribute bindings

Aggregation module outputs are NOT in any of these — they're created later by the graph builder at step 7. So when the backtracker encounters `annualized_financial.total_capex = capital_cost` (a binding to a PartDef attribute), it:
1. Checks `_computed_attr_index` → no match (capital_cost is not a FORMULA)
2. Checks `_design_attr_binding_index` → may find a transitive path through the `:>> capital_cost = sum(...)` redefinition, but this is an EXPRESSION type, not a direct binding
3. Falls through to ENTRY_POINT

Even though `dependency_backtracker.py:156-158` registers aggregation channels:
```python
for agg in (aggregation_data or []):
    channel = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
```

The binding source path for `total_capex` is likely a bare name or SysML QN that doesn't match the aggregation channel format. The aggregation channel would be something like `solarbatterydesign__solar_battery_plant__capital_cost__capital_cost`, but the binding source path might be just `capital_cost` or `Solar_Battery_Plant::capital_cost`.

**Files affected**: `src/sysml_codegen/analysis/dependency_backtracker.py` (binding resolution logic)

**Fix approach**: The backtracker needs a lookup path that resolves bare-name or SysML QN bindings to aggregation module output channels. Options:
1. Build an `_aggregation_output_index` in the backtracker's `__init__` that maps multiple key formats (bare name, dotted path, SysML QN) to aggregation channel names
2. In `_resolve_binding_to_usage()`, add a strategy that checks if the binding target matches an aggregation expression's `attribute_name` on the same assembly PartDef
3. After the graph builder creates aggregation modules, re-resolve any ENTRY_POINT bindings that match aggregation outputs (post-processing step)

---

### Bug 6 (INDEPENDENT): Aggregation Module EQN Uses PartDef Path, Not Design Instance Path

**Symptom**: Module wrapper directories use PartDef-scoped names like `solarbatterylibrary__solar_array/` instead of design-instance-scoped names like `solarbatterydesign__solar_battery_plant__solar_array/`. The YAML keys use design-instance-scoped names correctly, but the module wrapper file paths use PartDef-scoped names.

**Evidence**: From discovery:
```
MODULES DIR:
  solarbatterylibrary__battery_system/capital_cost.py
  solarbatterylibrary__solar_array/capital_cost.py
  solarbatterylibrary__solar_battery_plant/capital_cost.py

PIPELINE YAML:
  solarbatterydesign__solar_battery_plant__solar_array__capital_cost
  solarbatterydesign__solar_battery_plant__battery_system__capital_cost
```

The YAML module key (design-scoped) doesn't match the module wrapper import path (PartDef-scoped). This means the pipeline would fail at runtime — the YAML references a module name that doesn't match the directory/file where the wrapper lives.

**Root Cause**: In `_generate_aggregation_modules()` (`cli/__init__.py:433-443`), the `sysml_qn` used for `PythonModulePath.from_sysml()` is:
```python
sysml_qn = f"{agg.expression.owning_part_qn}::{agg.expression.attribute_name}"
```

This uses `owning_part_qn` (the PartDef's QN, e.g., `SolarBatteryLibrary::Solar Array`) instead of the instance-scoped `agg.module_eqn` (e.g., `SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost`).

**Files affected**: `src/sysml_codegen/cli/__init__.py:433-443`

**Fix approach**: Use the instance-scoped module EQN for Python path derivation, not the PartDef QN. The `PythonModulePath.from_sysml()` call should use a QN derived from `agg.module_eqn`.

---

## Bug Dependency Graph

```
Bug 1 (AST parsing)
  ├─ causes → Bug 2 (no inputs, no auto-impl)
  └─ causes → Bug 3 (broken YAML input names)

Bug 4 (site_infra scoping) — independent
Bug 5 (total_capex wiring) — independent
Bug 6 (module path mismatch) — independent
```

Fixing Bug 1 eliminates Bugs 2 and 3. Bugs 4, 5, and 6 require separate fixes.

## Priority Order

| Priority | Bug | Effort | Impact | Blocks |
|----------|-----|--------|--------|--------|
| 1 | Bug 1 (AST parsing) | Medium | Critical — ALL aggregation broken | Bugs 2, 3 |
| 2 | Bug 6 (path mismatch) | Low | Module wrapper import paths wrong | Runtime |
| 3 | Bug 2A (input lookup case) | Trivial | Module wrappers have no inputs | Wiring |
| 4 | Bug 4 (site_infra scoping) | Medium | 5 aggregation modules missing | Completeness |
| 5 | Bug 5 (total_capex wiring) | Medium | System-level chain broken | LCOE |
| 6 | Bug 2C (stencil path) | Low | Stencil paths PartDef-scoped | File collisions |

## Code References

### Bug 1 (AST Parsing)
- `src/sysml_codegen/extraction/hierarchy_resolver.py:320-372` — `_walk_aggregation_ast()` InvocationExpression handling
- `src/sysml_codegen/extraction/expression_utils.py:47-52` — `reconstruct_expression()` InvocationExpression fallback
- `.project/active/hierarchy-spike/report.md` Q6 — spike validated `sum()` with `function.name='sum'` but didn't probe nested operand structure

### Bug 2 (Inputs/Auto-Impl)
- `src/sysml_codegen/cli/__init__.py:427-453` — `_generate_aggregation_modules()` input lookup
- `src/sysml_codegen/cli/__init__.py:526-530` — `_generate_aggregation_stencils()` guard conditions
- `src/sysml_codegen/cli/__init__.py:533` — stencil path derivation (PartDef-scoped)
- `src/sysml_codegen/core/qualified_names.py:93-95` — `get_module_name()` lowercases

### Bug 3 (Broken YAML Names)
- `src/sysml_codegen/resolution/graph_builder.py` — `_build_aggregation_module()` param_name construction

### Bug 4 (Site Infra Scoping)
- `src/sysml_codegen/generation/initialization.py:296-347` — `_scope_aggregation_expressions()`
- Strategy 1 (line 322-326): Direct PartDef match
- Strategy 2 (line 329-338): Name segment match (fails due to name abbreviation)

### Bug 5 (Total Capex Wiring)
- `src/sysml_codegen/analysis/dependency_backtracker.py:156-158` — aggregation channel registration
- Backtracker binding resolution: multiple strategies in `_trace_dependencies()` and `_resolve_binding_to_usage()`

### Bug 6 (Path Mismatch)
- `src/sysml_codegen/cli/__init__.py:433-443` — `sysml_qn` derivation in `_generate_aggregation_modules()`
- Same pattern at `:533` in `_generate_aggregation_stencils()`

## Recommendations

### Immediate Actions (Ordered)

1. **Fix Bug 1**: Unwrap `InvocationExpression(Evaluation)` wrapper in `_walk_aggregation_ast()` when processing `sum()` operands. Add a helper that recursively unwraps known wrapper patterns (Evaluation, collect, select) to extract the underlying FeatureChainExpression.

2. **Fix Bug 6**: Use `agg.module_eqn` for PythonModulePath derivation in both `_generate_aggregation_modules()` and `_generate_aggregation_stencils()`. This ensures file paths match YAML module names.

3. **Fix Bug 2A**: Change lookup to `agg_modules_by_name.get(get_module_name(agg.module_eqn))` to match the lowercased key format.

4. **Fix Bug 4**: Add a third scoping strategy that directly matches PartDef QNs to design instance paths using the hierarchy data (PartUsage type specialization chains), bypassing CalcUsage-based reverse-engineering.

5. **Fix Bug 5**: Add aggregation output channel resolution in the backtracker. Build an `_aggregation_attr_index` that maps `(assembly_part_name, attribute_name)` → aggregation channel, and use it when resolving bindings to PartDef attributes that are redefined as EXPRESSION type.

6. **Fix Bug 2C**: Use instance-scoped module EQN for stencil path derivation to avoid file collisions.

### Testing Strategy

After fixes:
1. Re-run discovery tests (`test_discovery_tmp.py`, `test_discovery2_tmp.py`)
2. Verify: 36 impl files (16 existing + 20 aggregation)
3. Verify: all aggregation module wrappers have correct inputs
4. Verify: pipeline YAML shows valid Python identifiers for all input names
5. Verify: `annualized_financial.total_capex` wires to MODULE_OUTPUT
6. Verify: site_infra has 5 aggregation modules
7. Verify: `IMPLEMENTATION_BACKLOG.md` shows "0 functions to implement"
8. Full regression: `uv run pytest tests/`

## Open Questions

1. **What is the exact AST structure inside `sum()` operands?** I cannot run the SysIDE adapter directly (license key required). The fix assumes an `InvocationExpression(Evaluation)` wrapper based on the `reconstruct_expression()` output. This should be verified by adding debug logging to `_walk_aggregation_ast()` that dumps the operand type and structure when processing `sum()` calls.

2. **Does `allocation_model.total_allocation` also get wrapped?** The `FeatureChainExpression` for singleton terms (line 374-379) may also be affected if SysIDE wraps `allocation_model.total_allocation` in a similar pattern. Need to check if singleton terms in the aggregation expression are correctly resolved.

3. **Are there other "wrapper" InvocationExpression patterns?** Beyond `Evaluation`, SysIDE might use `collect`, `select`, or other function names as wrappers. The fix should handle any InvocationExpression wrapping `sum()` operands, not just specifically `Evaluation`.

4. **How should `solar_battery_plant` aggregation resolve its children?** The plant-level aggregation expression is `:>> capital_cost = solar_array.capital_cost + battery_system.capital_cost + site_infra.capital_cost`. These reference assembly PartUsages whose `capital_cost` is itself an aggregation output. The backtracker needs to resolve these as MODULE_OUTPUT from downstream aggregation modules.
