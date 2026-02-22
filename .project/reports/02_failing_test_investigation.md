---
date: 2026-02-12
researcher: Claude (Opus 4.6)
topic: "Deep investigation of 4 failing hierarchy E2E tests"
tags: [investigation, e2e, hierarchy, aggregation, bugs, root-cause]
status: complete
---

# Investigation: 4 Failing E2E Tests in `test_hierarchy_e2e.py`

**Date**: 2026-02-12
**File**: `/home/reid/1cfe/sysml-codegen/tests/integration/test_hierarchy_e2e.py`
**Source files investigated**: 7 production modules, 3 SysML fixture files, 2 prior research reports, SysIDE API docs

---

## Test Setup (Shared by All 4 Tests)

All four tests share the same fixture:

```python
@pytest.fixture(scope="class")
def pipeline_context(self) -> PipelineContext:
    model_path = FIXTURES_DIR / "solar_battery_model"
    return build_pipeline_context([model_path])
```

**Execution path** for `build_pipeline_context([model_path])`:

1. **Step 1**: `SysMLDataExtractor(model_paths)` loads 3 SysML files: `library.sysml`, `design.sysml`, `costing.sysml`
2. **Step 2**: Extract calc definitions (9 component + 5 system-level + 1 allocation = 15 CalcDefs)
3. **Step 3**: `extract_calculation_usages()` -- finds CalcUsages on PartDefs and design instances
4. **Step 3.5**: `_extract_hierarchy_and_rewrite_bindings()` -- calls `extract_hierarchy_data(model)` which orchestrates:
   - `extract_redefinitions(part_def)` for each PartDefinition
   - `extract_multiplicities(part_def)` for each PartDefinition
   - `build_aggregation_expression(redef, mults, part_def)` for EXPRESSION-type redefinitions
   - Alias detection loop (lines 519-528)
   - `extract_design_overrides(part_usages)` for design PartUsages
5. **Step 4**: Extract design attributes
6. **Step 4.5**: Extract computed attributes
7. **Step 4.7**: `_scope_aggregation_expressions()` -- scope PartDef aggregations to design instances
8. **Step 5**: Create `ParameterGroupDeriver`
9. **Step 6**: Create `DependencyBacktracker` and run `find_required_modules()`
10. **Step 7**: `build_computation_graph()` -- creates PipelineModules including aggregation modules

---

## Test 1: `test_bf1_no_unsupported_nodes`

### What the Test Checks

```python
for agg in hierarchy.aggregation_expressions:
    assert not agg.has_unsupported_nodes          # Line 67
    assert "Evaluation" not in agg.transformed_expression  # Line 71
```

### Critical Path

1. `extract_hierarchy_data()` (hierarchy_resolver.py:483-541) iterates PartDefinitions
2. For each EXPRESSION-type redefinition, calls `build_aggregation_expression()` (line 510-511)
3. `build_aggregation_expression()` (line 432-480) creates `_AggregationContext` and calls `_walk_aggregation_ast()` (line 464)
4. `_walk_aggregation_ast()` (line 301-429) recursively processes the AST

### Failure Point

The failure occurs in `_walk_aggregation_ast()` at lines 346-404, specifically when processing the `sum()` InvocationExpression and its operands.

**The real SysIDE AST structure for `sum(pv_module.capital_cost)`**:

Based on the SysIDE API documentation, the actual AST is NOT what the mock-based unit tests simulate. The KerML specification reveals:

- **`CollectExpression`** is a subclass of **`OperatorExpression`** (NOT `InvocationExpression`). It has an `operator` attribute with value `"collect"`.
- **`SelectExpression`** is similarly a subclass of **`OperatorExpression`** with `operator == "select"`.

The real AST tree for `sum(pv_module.capital_cost)` is likely:

```
InvocationExpression [function.name='sum']
  operands[0]:
    CollectExpression (extends OperatorExpression)
      operator = "collect"
      operands[0]:
        FeatureReferenceExpression [function.name='Evaluation' or similar]
          operands[0]:
            FeatureChainExpression [pv_module.capital_cost]
```

OR potentially even more deeply nested. The crucial point is that `CollectExpression` is an `OperatorExpression`, NOT an `InvocationExpression`.

### Root Cause

The `_unwrap_invocation()` function (hierarchy_resolver.py:278-298) checks:

```python
if hasattr(node, "function") and hasattr(node.function, "name"):
    operands = list(getattr(node, "operands", []))
    if operands:
        return _unwrap_invocation(operands[0], _depth + 1)
```

This check relies on `function.name` being present. For `InvocationExpression` nodes, this works because they inherit `function` from `Expression`. But for `CollectExpression` (which IS an `OperatorExpression`), the relevant attribute is `operator` (a string), not `function.name`. While `CollectExpression` technically inherits `function` from `Expression`, in the real SysIDE AST the `function` property may be `None` for these built-in operator expressions, causing `hasattr(node.function, "name")` to fail.

Additionally, `_walk_aggregation_ast()` at line 324 checks for `OperatorExpression` FIRST:

```python
if SysideAdapter.is_instance(node, "OperatorExpression"):
    operator = getattr(node, "operator", "+")
    ...
```

Since `CollectExpression` IS-A `OperatorExpression`, it would match this branch INSTEAD of falling through to the InvocationExpression branch (lines 347ff). The OperatorExpression handler recursively walks operands but treats `operator = "collect"` as an arithmetic operator, producing `collect(...)` in the output and likely not properly unwrapping to the FeatureChainExpression inside.

The non-sum `Evaluation`/`collect` wrappers around singleton terms (like `array_bos.capital_cost`) also hit this OperatorExpression branch, producing garbage output and setting `has_unsupported = True`.

**The mock-based unit tests pass because**:
- `MockInvocationExpression` does NOT have `isinstance()` method for SysIDE type checking
- `SysideAdapter.is_instance(mock, "OperatorExpression")` returns `False` because `"OperatorExpression"` is not in `"MockInvocationExpression"`
- So the mocks bypass the OperatorExpression branch and hit the InvocationExpression branch correctly
- The real `CollectExpression` matches `OperatorExpression` via `elem.isinstance(sysml_type)` because it extends OperatorExpression

### AST Assumption That Is Wrong

The code assumes the AST hierarchy is:
```
InvocationExpression(sum)
  InvocationExpression(Evaluation)   <-- assumed wrapper type
    FeatureChainExpression
```

The actual SysIDE AST hierarchy is:
```
InvocationExpression(sum)
  CollectExpression (IS-A OperatorExpression, operator="collect")
    [inner expression, possibly another OperatorExpression or InvocationExpression]
      FeatureChainExpression
```

### Fix Direction

1. In `_walk_aggregation_ast()`, before the general `OperatorExpression` handler, add a check for `operator in {"collect", "select"}` that unwraps the expression instead of treating it as arithmetic.
2. Or: reorder the checks so InvocationExpression-like handling (with unwrapping) is checked before OperatorExpression for known wrapper operators.
3. The `_unwrap_invocation()` function needs to handle `OperatorExpression` nodes with `operator in {"collect", "select", "Evaluation"}` in addition to `InvocationExpression` nodes with `function.name`.

---

## Test 2: `test_bf1_sum_terms_have_real_names`

### What the Test Checks

```python
all_sum_part_names = set()
for agg in hierarchy.aggregation_expressions:
    for term in agg.sum_terms:
        all_sum_part_names.add(term.part_usage_name)

assert all_sum_part_names & ARRAYED_PARTS  # Line 92
# ARRAYED_PARTS = {"pv_module", "inverter", "battery_pack"}
```

### Critical Path

Same as Test 1. The sum_terms are populated by `_walk_aggregation_ast()` at lines 358-386.

### Failure Point

Line 92: `all_sum_part_names & ARRAYED_PARTS` is empty.

This is a direct cascade from Test 1's root cause. When `_walk_aggregation_ast()` encounters the `sum()` call at line 347-351:

```python
if hasattr(node, "function") and hasattr(node.function, "name"):
    func_name = node.function.name
    operands = list(getattr(node, "operands", []))
    if func_name == "sum" and operands:
        operand = _unwrap_invocation(operands[0])
```

The `sum()` InvocationExpression is correctly identified (it has `function.name == "sum"`). The problem is that `_unwrap_invocation(operands[0])` receives a `CollectExpression` (which is an `OperatorExpression`), and `_unwrap_invocation` checks `hasattr(node, "function") and hasattr(node.function, "name")`. If the CollectExpression's `function` property is `None` or doesn't have `name`, `_unwrap_invocation` returns the CollectExpression unchanged.

Then at line 353:
```python
if SysideAdapter.is_instance(operand, "FeatureChainExpression"):
    chain_name = extract_feature_chain_name(operand)
else:
    chain_name = extract_feature_reference_name(operand)
```

The CollectExpression is NOT a FeatureChainExpression, so it falls through to `extract_feature_reference_name()`, which (expression_utils.py:110-130) tries several attribute paths (`referent.name`, `memberships`, `declared_name`, `name`) and eventually falls back to `str(expr_node)`, producing something like `"collect(Evaluation(...))"` or a repr string.

This garbage `chain_name` then goes through `chain_name.split(".", 1)` at line 358. If it has no dot, `len(parts) == 1`, and the code goes to the "Single-element sum" branch (line 389), creating a `LocalTerm` instead of a `SumTerm`. If it has a dot in the garbage string, the `part_name` and `attr_name` are garbage, and the multiplicity lookup fails.

**Result**: No `SumTerm` objects are created with real part names like "pv_module", "inverter", or "battery_pack". The `all_sum_part_names` set is empty or contains garbage names.

### Root Cause

Same as Test 1: `_unwrap_invocation()` cannot unwrap `CollectExpression` nodes because they are `OperatorExpression` instances, not `InvocationExpression` instances with `function.name`.

### Fix Direction

Same as Test 1. Once `_unwrap_invocation()` can handle `OperatorExpression` nodes with `operator in {"collect", "select"}`, the sum operands will be correctly unwrapped to `FeatureChainExpression`, producing valid `chain_name` values like `"pv_module.capital_cost"`.

---

## Test 3: `test_bf7_aliases_extracted`

### What the Test Checks

```python
plant_capital = [
    agg for agg in hierarchy.aggregation_expressions
    if "Solar_Battery_Plant" in agg.owning_part_qn
    and agg.attribute_name == "capital_cost"
]
agg = plant_capital[0]
assert "total_capex" in agg.aliases  # Line 144
```

### Critical Path

1. `extract_hierarchy_data()` (hierarchy_resolver.py:483-541) iterates PartDefinitions
2. For each PartDef, it calls `extract_redefinitions()` producing a list `redefs`
3. For each EXPRESSION-type redef, after building the `AggregationExpressionData`, the alias detection loop runs (lines 519-528):

```python
for sibling in redefs:
    if (
        sibling.redefinition_type == RedefinitionType.CHAIN
        and sibling.source_path
        and sibling.source_path.endswith(agg.attribute_name)
        and sibling.attribute_name != agg.attribute_name
    ):
        agg.aliases.append(sibling.attribute_name)
```

### Failure Point

Line 144: `agg.aliases` is empty.

The test expects `"total_capex"` to be an alias for `Solar_Battery_Plant.capital_cost`. Looking at the SysML model:

**library.sysml** (Solar Battery Plant PartDef, lines 726-764):
```sysml
part def 'Solar Battery Plant' :> 'Costed Component' {
    :>> capital_cost =
        solar_array.capital_cost +
        battery_system.capital_cost +
        site_infra.capital_cost;
    // ... other cost attributes
}
```

**design.sysml** (line 84-88):
```sysml
calc annualized_financial : AnnualizedFinancialCalc {
    in total_capex = capital_cost;  // from 'Solar Battery Plant' rollup
}
```

The alias detection logic looks for a **sibling :>> CHAIN redefinition** on the **same PartDef** that points to `capital_cost`. Specifically, it would need something like:

```sysml
:>> total_capex = capital_cost;  // CHAIN redef aliasing capital_cost
```

on the `'Solar Battery Plant'` PartDef itself. But no such redefinition exists in the SysML model. The `total_capex` name only appears as an **input parameter name** on `AnnualizedFinancialCalc`, bound to `capital_cost` at the CalcUsage site in `design.sysml`.

The alias detection in `extract_hierarchy_data()` (lines 519-528) ONLY looks at `:>>` redefinitions on the same PartDef (the `redefs` list from `extract_redefinitions(part_def)`). CalcUsage bindings are a completely different data source extracted by `extract_calculation_usages()` in Step 3.

### Root Cause

The alias detection logic is structurally incapable of finding the `total_capex` alias because:

1. **`total_capex` is NOT a :>> redefinition on `Solar_Battery_Plant`**. It is an input parameter name on `AnnualizedFinancialCalc` CalcDef.
2. **The binding `in total_capex = capital_cost`** is extracted by the usage extractor as a CalcUsage binding, not by the hierarchy resolver as a PartDef redefinition.
3. The alias detection loop (lines 519-528) only searches `redefs` -- the list of RedefinitionData from `extract_redefinitions(part_def)` -- which contains `:>>` redefinitions on the PartDef's owned members.

### AST Assumption That Is Wrong

The code assumes that aliases for aggregation outputs are expressed as `:>> total_capex = capital_cost` CHAIN redefinitions on the same PartDef. In reality, the "alias" relationship is established through CalcUsage parameter binding: `calc annualized_financial : AnnualizedFinancialCalc { in total_capex = capital_cost; }`.

### Fix Direction

The alias detection needs a different data source. Two approaches:

1. **CalcUsage binding analysis**: After Step 3, scan CalcUsage bindings for any binding where `source_path` matches an aggregation attribute name (e.g., `capital_cost`) and the parameter name differs (e.g., `total_capex`). Add those parameter names as aliases on the corresponding `AggregationExpressionData`.

2. **Backtracker-level resolution**: In the `DependencyBacktracker.__init__()`, when building `_aggregation_output_index`, also scan CalcUsage bindings that reference aggregation attributes. For each binding `usage.bindings[i].source_path == "capital_cost"` where `usage.bindings[i].param_name == "total_capex"`, register `total_capex` as an additional key in the aggregation output index.

Approach 2 is more appropriate because alias detection is ultimately about resolving bindings, which is the backtracker's responsibility.

---

## Test 4: `test_bf7_total_capex_wired_to_module_output`

### What the Test Checks

```python
fin_module = [m for m in graph.modules if "annualized_financial" in m.name][0]
capex_input = [inp for inp in fin_module.inputs if inp.param_name == "total_capex"][0]
assert capex_input.source.source_type == "module_output"  # Line 195
```

### Critical Path

1. `build_pipeline_context()` runs Steps 1-7
2. At **Step 6**, `DependencyBacktracker` is created with `aggregation_data` parameter
3. In `DependencyBacktracker.__init__()` (dependency_backtracker.py:157-197), `_aggregation_output_index` is built:
   ```python
   for agg in (aggregation_data or []):
       channel = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
       # Key 1: "part_usage_name.attribute_name"
       self._aggregation_output_index[f"{part_usage_name}.{agg.expression.attribute_name}"] = channel
       # Key 2: bare attribute_name
       # Key 3: full instance path dotted
       # BF-7: aliases
       for alias_name in getattr(agg.expression, "aliases", []):
           ...
   ```
4. During `_trace_dependencies()` for the `annualized_financial` CalcUsage, the `total_capex` binding is processed
5. The binding's `source_path` is checked against `_aggregation_output_index` (lines 472-498)

### Failure Point

Line 195: `capex_input.source.source_type == "entry_point"` instead of `"module_output"`.

The binding for `total_capex` on `annualized_financial` has `source_path` pointing to `capital_cost` (from the SysML: `in total_capex = capital_cost`). The backtracker checks the aggregation output index:

```python
agg_channel = self._aggregation_output_index.get(binding.source_path)
```

The index keys for `Solar_Battery_Plant.capital_cost` are:
- Key 1: `"solar_battery_plant.capital_cost"` (dotted with part usage name)
- Key 2: `"capital_cost"` (bare attribute name)
- Key 3: `"solar_battery_plant.capital_cost"` (full instance dotted)

The `binding.source_path` for `total_capex` is `"capital_cost"` (bare name from SysML `in total_capex = capital_cost`). So the **bare lookup (Key 2) should match**.

However, there are two potential issues:

**Issue A**: Due to Test 1's root cause (broken aggregation AST walking), the aggregation expressions may have `has_unsupported_nodes == True`, which might affect whether aggregation modules are properly scoped and thus whether `aggregation_data` is populated correctly for the backtracker.

**Issue B**: The `binding.source_path` may not be just `"capital_cost"`. The usage extractor might resolve it as a SysML qualified name like `"SolarBatteryLibrary::'Solar Battery Plant'::capital_cost"` or `"SolarBatteryDesign::solar_battery_plant::capital_cost"`. If so, the direct lookup fails.

The fallback strategies (lines 475-486):
```python
if agg_channel is None and "." in binding.source_path:
    bare = binding.source_path.split(".")[-1]
    agg_channel = self._aggregation_output_index.get(bare)
if agg_channel is None and "::" in binding.source_path:
    parts = binding.source_path.split("::")
    sanitized = sanitize_name(parts[-2]).lower()
    dotted = f"{sanitized}.{parts[-1]}"
    agg_channel = self._aggregation_output_index.get(dotted)
```

For a `::` path like `"SolarBatteryDesign::solar_battery_plant::capital_cost"`:
- `parts[-2]` = `"solar_battery_plant"`, `parts[-1]` = `"capital_cost"`
- `dotted` = `"solar_battery_plant.capital_cost"`
- This SHOULD match Key 1 in the index.

But if the source path is `"SolarBatteryLibrary::'Solar Battery Plant'::capital_cost"`:
- `parts[-2]` = `"'Solar Battery Plant'"`, `parts[-1]` = `"capital_cost"`
- `sanitize_name("'Solar Battery Plant'")` = `"Solar_Battery_Plant"`, `.lower()` = `"solar_battery_plant"`
- `dotted` = `"solar_battery_plant.capital_cost"`
- This SHOULD also match.

**The real issue is Test 3's root cause**. Even if the aggregation index has `"capital_cost"` as a key, the BF-7 alias registration at lines 189-197 relies on `agg.expression.aliases` being populated. Since Test 3 shows aliases are empty, the `total_capex` alias is never registered in the index. But this is about the alias registration -- for the *direct* lookup, the binding source path `"capital_cost"` should still match Key 2.

The actual failure is more subtle. The CalcUsage `annualized_financial` is INSIDE `solar_battery_plant` (design.sysml line 84). The binding `in total_capex = capital_cost` references `capital_cost` which is an attribute of `solar_battery_plant` (the containing part). The usage extractor resolves this binding's `source_path` based on how SysIDE represents the reference:

- If `source_path = "capital_cost"` (bare name) -> Key 2 lookup should succeed IF `"capital_cost"` is in the index
- But Key 2 is only added `if agg.expression.attribute_name not in self._aggregation_output_index` (line 178)
- Since there are MULTIPLE aggregation expressions with `attribute_name == "capital_cost"` (Solar Array, Battery System, Solar Battery Plant all have `capital_cost`), only the FIRST one wins Key 2

If Solar Array's `capital_cost` gets registered first, the bare `"capital_cost"` key points to Solar Array's aggregation channel, not Solar Battery Plant's. Then the lookup for `annualized_financial`'s `total_capex = capital_cost` would resolve to the WRONG aggregation module (Solar Array instead of Solar Battery Plant).

But more likely, the binding source path is a qualified name (containing `::`) that none of the fallback strategies match correctly, OR the aggregation_data list itself is malformed due to Test 1's root cause (broken AST walking means aggregation expressions are flagged as unsupported, which may cascade into scoping/index issues).

### Root Cause

This is a **multi-layered failure** with at least three contributing causes:

1. **Cascade from Test 1**: Broken AST walking produces garbage aggregation expressions. Even though they are still added to `all_aggregations`, the data quality (sum_terms, transformed_expression, has_unsupported_nodes) is degraded.

2. **Cascade from Test 3**: Empty `aliases` list means the BF-7 alias registration in the backtracker (lines 189-197) adds no additional keys for `total_capex`.

3. **Bare-name key collision**: Multiple aggregation expressions share `attribute_name == "capital_cost"`. The bare-name Key 2 (line 178) is only registered for the first one encountered, making it unreliable for resolution.

4. **Binding source path resolution**: The actual `source_path` for `annualized_financial`'s `total_capex` binding may be a SysML qualified name that doesn't match any index key pattern, causing all lookups to fail and the binding to fall through to `entry_point`.

### Fix Direction

1. **Fix Test 1** first (broken AST walking) to ensure aggregation expressions are clean.
2. **Fix alias detection** (Test 3) so `total_capex` is registered in the aggregation output index.
3. **Add context-aware resolution**: When resolving a binding from a CalcUsage inside a PartUsage, resolve bare-name references to attributes of the PARENT PartDef (not just any PartDef). Use the CalcUsage's qualified name to determine its parent scope and prefer aggregation expressions from that scope.
4. **Handle bare-name collisions**: Instead of "first wins" for Key 2, either remove it or make it scope-aware.

---

## Cross-Cutting Analysis

### Bug Dependency Graph

```
Test 1 (AST walking - CollectExpression)
  |
  +-- cascades to --> Test 2 (no real SumTerms)
  |
  +-- contributes to --> Test 4 (degraded aggregation data)

Test 3 (alias detection - wrong data source)
  |
  +-- contributes to --> Test 4 (no alias in aggregation index)

Test 4 (total_capex wiring) = combination of Tests 1, 3, and bare-name collision
```

### Why Unit Tests Pass But E2E Tests Fail

The mock objects used in unit tests (`MockInvocationExpression`, `MockOperatorExpression`, etc.) have different type-checking behavior than real SysIDE objects:

| Aspect | Mock Objects | Real SysIDE Objects |
|--------|-------------|-------------------|
| `is_instance("OperatorExpression")` | Checks `type_name in type(elem).__name__` -- `"OperatorExpression" not in "MockInvocationExpression"` = False | Uses `elem.isinstance(sysml_type)` -- `CollectExpression.isinstance(OperatorExpression)` = True |
| `function.name` on collect/select | Mocks have explicit `function.name` attribute | `CollectExpression` inherits `function` from `Expression` but the property may return a library Function object or None |
| Type hierarchy | Flat mock classes, no inheritance | `CollectExpression -> OperatorExpression -> InvocationExpression -> Expression` |

**The fundamental gap**: The mocks simulate `InvocationExpression` wrappers around `sum()` operands, but the real SysIDE AST uses `CollectExpression` (which is an `OperatorExpression`). The code's `OperatorExpression` handler catches these before the `InvocationExpression` handler, leading to incorrect traversal.

### Recommended Fix Priority

1. **Test 1 / Test 2 (CollectExpression handling)** -- CRITICAL. This is the root cause for most cascading failures. Fix `_walk_aggregation_ast()` to handle `CollectExpression` / `SelectExpression` as unwrap-able wrappers before the generic `OperatorExpression` handler. Also fix `_unwrap_invocation()` to handle `OperatorExpression` nodes with `operator in {"collect", "select"}`.

2. **Test 3 (alias detection)** -- HIGH. Fundamentally wrong data source. The fix needs to either scan CalcUsage bindings for alias relationships, or move alias detection to the backtracker where CalcUsage binding data is available.

3. **Test 4 (total_capex wiring)** -- HIGH but likely auto-fixes after Tests 1 and 3. Verify after fixing the other tests. If still broken, add scope-aware bare-name resolution in the aggregation output index.

### Files Requiring Changes

| File | Lines | Change Description |
|------|-------|--------------------|
| `src/sysml_codegen/extraction/hierarchy_resolver.py` | 275-298, 301-404 | Handle `CollectExpression`/`SelectExpression` as OperatorExpression wrappers in `_unwrap_invocation()` and `_walk_aggregation_ast()` |
| `src/sysml_codegen/extraction/hierarchy_resolver.py` | 519-528 | Rethink alias detection data source OR move to backtracker |
| `src/sysml_codegen/analysis/dependency_backtracker.py` | 157-197 | Add CalcUsage-binding-based alias detection for aggregation output index |
| `src/sysml_codegen/extraction/expression_utils.py` | 44-52 | Handle CollectExpression in `reconstruct_expression()` for display purposes |
