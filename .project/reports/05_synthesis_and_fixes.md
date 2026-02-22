# Synthesis Report: Definitive Root Cause Analysis & Fix Plan

**Date**: 2026-02-12
**Investigator**: Claude (Opus 4.6)
**Status**: Complete — probe-validated against real SysIDE AST
**Supersedes**: All prior root cause hypotheses (including CollectExpression theory)

---

## Executive Summary

All **20 aggregation expressions** extracted from the solar_battery model are broken. Every single one has `has_unsupported_nodes = True`, `sum_terms = []`, `singleton_terms = []`, and `aliases = []`. The 4 E2E test failures are symptoms of **5 independent root causes**, all validated by running probe scripts against the real SysIDE AST.

The prior hypothesis (agent ab15303) that `CollectExpression` wraps sum() operands is **definitively refuted** — the probe shows no CollectExpression in the AST. The actual structure is simpler but has a different unexpected property: `FeatureReferenceExpression` nodes carry a `function.name='Evaluation'` attribute, and `FeatureChainExpression` nodes carry `function.name='.'`, causing them to be misidentified by code that uses `hasattr(node, "function")` as an InvocationExpression test.

---

## Probe-Validated AST Structure

### Real AST for `sum(pv_module.capital_cost)`:
```
InvocationExpression [function.name='sum']
  └── FeatureChainExpression [function.name='.', operator=Operator.Dot, target_feature.name='capital_cost']
       └── operand[0]:
            FeatureReferenceExpression [function.name='Evaluation', referent.name='pv_module']
```

### Real AST for `array_bos.capital_cost` (singleton):
```
FeatureChainExpression [function.name='.', operator=Operator.Dot, target_feature.name='capital_cost']
  └── operand[0]:
       FeatureReferenceExpression [function.name='Evaluation', referent.name='array_bos']
```

### Real AST for `misc_hardware_cost` (local term):
```
FeatureReferenceExpression [function.name='Evaluation', referent.name='misc_hardware_cost']
```

### Key Discovery

| AST Node Type | Has `function`? | `function.name` | Has `referent`? | Has `target_feature`? |
|---|---|---|---|---|
| `InvocationExpression` (sum, sqrt) | Yes | `"sum"`, `"sqrt"` | No | No |
| `FeatureChainExpression` (a.b path) | Yes | `"."` | No | Yes |
| `FeatureReferenceExpression` (name ref) | Yes | `"Evaluation"` | Yes | No |
| `OperatorExpression` (+, -, *, /) | No* | N/A | No | No |

*OperatorExpression uses `operator` attribute, not `function`.

**Critical insight**: In the SysIDE AST, `FeatureReferenceExpression` and `FeatureChainExpression` BOTH have a `function` attribute with a `name` property. This means any code that uses `hasattr(node, "function") and hasattr(node.function, "name")` as a test for InvocationExpression will produce **false positives** on these node types.

---

## Root Cause 1: `_unwrap_invocation()` Strips FeatureChainExpression

**File**: `hierarchy_resolver.py:278-298`
**Impact**: ALL sum() operands lose their `.attribute_name` part

### Trace

1. `_walk_aggregation_ast()` detects `func_name == "sum"` (line 351)
2. Calls `_unwrap_invocation(operands[0])` where operands[0] is a `FeatureChainExpression`
3. `_unwrap_invocation()` at line 294: `hasattr(node, "function") and hasattr(node.function, "name")` → **True** (function.name='.')
4. Recurses into `operands[0]` which is the inner `FeatureReferenceExpression`
5. That also matches (function.name='Evaluation'), but has no child operands → returns it
6. **Result**: Returns `FeatureReferenceExpression` (just `referent.name='pv_module'`) instead of the `FeatureChainExpression` (which had `target_feature.name='capital_cost'`)

### Consequence

```python
# After _unwrap_invocation, operand is FeatureReferenceExpression, not FeatureChainExpression
chain_name = extract_feature_reference_name(operand)  # Returns "pv_module"
parts = chain_name.split(".", 1)  # ["pv_module"] — only 1 part
# Falls to single-element path (line 388-389):
ctx.local_terms.append(LocalTerm(attribute_name="pv_module"))  # LocalTerm, NOT SumTerm!
```

### Fix

Add function name filter to `_unwrap_invocation()`:

```python
def _unwrap_invocation(node: Any, _depth: int = 0) -> Any:
    if _depth >= 3:
        return node
    if hasattr(node, "function") and hasattr(node.function, "name"):
        func_name = node.function.name
        if func_name in _KNOWN_WRAPPER_FUNCTIONS:  # ← ADD THIS CHECK
            operands = list(getattr(node, "operands", []))
            if operands:
                return _unwrap_invocation(operands[0], _depth + 1)
    return node
```

With this fix, FeatureChainExpression (function.name='.') and FeatureReferenceExpression (function.name='Evaluation') are NOT in `_KNOWN_WRAPPER_FUNCTIONS`, so they won't be unwrapped. Only genuine wrappers like `collect()`, `select()`, `evaluate()` will be peeled.

**Note**: The `_KNOWN_WRAPPER_FUNCTIONS` already exists at line 275 but is never used by `_unwrap_invocation()`. It's only referenced at line 393 for the non-sum wrapper path.

> **UPDATE (Design Review 2026-02-12):** The `_KNOWN_WRAPPER_FUNCTIONS` filter is fragile — "Evaluation" IS in the set, and that's the exact `function.name` on FeatureReferenceExpression nodes. If `_unwrap_invocation()` is ever called on a FeatureReferenceExpression that happens to have operands, it would be incorrectly unwrapped. **Revised fix: use explicit `SysideAdapter.is_instance()` type guards** instead of the function-name set, matching the pattern used in RC2/RC3:
>
> ```python
> def _unwrap_invocation(node: Any, _depth: int = 0) -> Any:
>     if _depth >= 3:
>         return node
>     if SysideAdapter.is_instance(node, "FeatureChainExpression"):
>         return node
>     if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
>         return node
>     if hasattr(node, "function") and hasattr(node.function, "name"):
>         operands = list(getattr(node, "operands", []))
>         if operands:
>             return _unwrap_invocation(operands[0], _depth + 1)
>     return node
> ```
>
> This is more explicit, consistent with the rest of the codebase, and immune to the "Evaluation" name collision.

---

## Root Cause 2: `reconstruct_expression()` Check Ordering

**File**: `expression_utils.py:34-75`
**Impact**: ALL FeatureReferenceExpression nodes rendered as "Evaluation()" in text output

### Trace

```python
def reconstruct_expression(expr_node):
    ...
    # Line 44: OperatorExpression check — OK
    if SysideAdapter.is_instance(expr_node, "OperatorExpression"):
        return reconstruct_operator_expression(expr_node)

    # Line 47: InvocationExpression check — FIRES ON FeatureReferenceExpression!
    if hasattr(expr_node, "function") and hasattr(expr_node.function, "name"):
        func_name = expr_node.function.name  # "Evaluation"
        args = ", ".join(reconstruct_expression(op) for op in operands)
        return f"{func_name}({args})"  # Returns "Evaluation()" ← WRONG

    # Line 54: FeatureReferenceExpression check — NEVER REACHED
    if SysideAdapter.is_instance(expr_node, "FeatureReferenceExpression"):
        return extract_feature_reference_name(expr_node)  # Would return "pv_module"
```

### Consequence

- `extract_feature_chain_name()` calls `reconstruct_expression(operands[0])` on the chain's first operand
- That operand is a FeatureReferenceExpression with `referent.name='array_bos'`
- But `reconstruct_expression()` returns `"Evaluation()"` instead of `"array_bos"`
- Chain name becomes `"Evaluation().capital_cost"` instead of `"array_bos.capital_cost"`

This affects:
- **Singleton terms**: `array_bos.capital_cost` → `".(Evaluation())"` → not classified as SingletonTerm
- **Local terms**: `misc_hardware_cost` → `"Evaluation()"` → `has_unsupported = True`
- **All CHAIN redefs**: `cost_model.total_cost` → `"Evaluation().total_cost"` instead of `"cost_model.total_cost"`

### Fix

Reorder checks — FeatureReferenceExpression and FeatureChainExpression BEFORE InvocationExpression:

```python
def reconstruct_expression(expr_node):
    ...
    if SysideAdapter.is_instance(expr_node, "OperatorExpression"):
        return reconstruct_operator_expression(expr_node)

    # Check specific SysML types BEFORE generic function.name check
    if SysideAdapter.is_instance(expr_node, "FeatureReferenceExpression"):
        return extract_feature_reference_name(expr_node)

    if SysideAdapter.is_instance(expr_node, "FeatureChainExpression"):
        return extract_feature_chain_name(expr_node)

    # Now safe to check for InvocationExpression via function.name
    if hasattr(expr_node, "function") and hasattr(expr_node.function, "name"):
        func_name = expr_node.function.name
        operands = list(getattr(expr_node, "operands", []))
        args = ", ".join(reconstruct_expression(op) for op in operands)
        return f"{func_name}({args})"
    ...
```

---

## Root Cause 3: `_walk_aggregation_ast()` FeatureChainExpression/FeatureReferenceExpression Handling

**File**: `hierarchy_resolver.py:301-429`
**Impact**: Singleton terms and local terms not classified correctly

### Trace

After the InvocationExpression block (lines 346-401), the code checks for FeatureChainExpression at line 403 and FeatureReferenceExpression at line 412. But these checks are never reached for nodes that have `function.name` because the InvocationExpression block fires first (line 347).

Specifically, a standalone `FeatureChainExpression` like `array_bos.capital_cost` (not inside sum()) has `function.name='.'`, so it matches line 347 (`hasattr(node, "function")`) and enters the InvocationExpression handler. Since `func_name = "."` is NOT `"sum"` and NOT in `_KNOWN_WRAPPER_FUNCTIONS`, it falls to line 398-399: `ctx.has_unsupported = True`.

### Fix

Add explicit type checks before the `hasattr(function)` check, mirroring Root Cause 2's fix:

```python
def _walk_aggregation_ast(node, mult_lookup, ctx):
    ...
    # OperatorExpression check (existing, line 324)
    if SysideAdapter.is_instance(node, "OperatorExpression"):
        ...

    # ADD: Check FeatureChainExpression BEFORE InvocationExpression
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        chain_name = extract_feature_chain_name(node)
        parts = chain_name.split(".", 1)
        if len(parts) == 2:
            part_name, attr_name = parts
            ctx.singleton_terms.append(SingletonTerm(source_path=chain_name))
            ctx.input_channels.append(chain_name)
            return chain_name
        return chain_name

    # ADD: Check FeatureReferenceExpression BEFORE InvocationExpression
    if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
        ref_name = extract_feature_reference_name(node)
        ctx.local_terms.append(LocalTerm(attribute_name=ref_name))
        return ref_name

    # InvocationExpression (existing, line 347)
    if hasattr(node, "function") and hasattr(node.function, "name"):
        ...
```

**Note**: This requires Root Cause 2's fix to already be applied, since `extract_feature_chain_name()` calls `reconstruct_expression()` internally. Without Fix 2, the chain name would still contain "Evaluation()".

> **UPDATE (Design Review 2026-02-12):** The proposed code **rewrites** the existing FeatureChainExpression/FeatureReferenceExpression handlers (lines 407-417) with new split/classification logic. This is unnecessary and introduces risk. The existing handlers at lines 407-411 (FeatureChainExpression) and 414-417 (FeatureReferenceExpression) already work correctly — they just need to be **relocated** before the `hasattr(function)` check at line 347. **Revised fix: move the existing blocks, don't rewrite them.** No logic changes needed — just position change.

---

## Root Cause 4: `_scope_aggregation_expressions()` Misses All-Singleton Assemblies

**File**: `initialization.py:296-355`
**Impact**: Site Infrastructure and Solar Battery Plant have no aggregation modules in the pipeline

### Probe Data

```
Site_Infrastructure: 0 multiplicity children, 3 singletons (racking, electrical_panel, permitting)
Solar_Battery_Plant: 0 multiplicity children, 3 singletons (solar_array, battery_system, site_infra)
```

### Trace

1. **Strategy 1** (line 322-326): Looks for virtual CalcUsages owned by same PartDef → Site_Infrastructure and Solar_Battery_Plant have no virtual CalcUsages directly on them → `instance_paths` empty
2. **Strategy 2** (line 332-345): `children` = multiplicities where `owning_part_def_qn == agg_expr.owning_part_qn` → Both have **zero multiplicity children** → `children` is empty → `if children:` guard at line 338 skips entirely
3. **Result**: No instance_paths found → no ScopedAggregationData created

### Fix

Add Strategy 3: Use owned PartUsage members (not just multiplicities) to find parent instance paths:

```python
# Strategy 3: Singleton-child walk — for all-singleton assemblies (e.g., Site Infra)
if not instance_paths:
    # Get owned PartUsage names from the PartDef
    singleton_children = set()
    for member in getattr(part_def_element, "owned_members", []):
        if SysideAdapter.is_instance(member, "PartUsage"):
            name = sanitize_name(getattr(member, "name", ""))
            if name:
                singleton_children.add(name.lower())
    if singleton_children:
        for _partdef_qn, qns in virtual_qns_by_partdef.items():
            for qn in qns:
                segments = qn.split("__")
                for i, seg in enumerate(segments):
                    if seg.lower() in singleton_children and i > 0:
                        parent_path = "__".join(segments[:i])
                        instance_paths.add(parent_path)
                        break
```

**Alternative (simpler)**: Store child PartUsage names in `HierarchyExtractionResult` during extraction, alongside multiplicities. Then Strategy 2 can use ALL children (with and without multiplicity) instead of just multiplicity children.

> **UPDATE (Design Review 2026-02-12):** The Strategy 3 code as written **will not work**. `_scope_aggregation_expressions()` receives only extracted data (`HierarchyExtractionResult`, `list[CalcUsageData]`) — it has **no access to AST elements or `part_def_element`**. The `getattr(part_def_element, "owned_members", [])` call has no `part_def_element` in scope. Additionally, putting AST iteration into a generation-layer function breaks the extraction/generation boundary that the codebase consistently respects.
>
> **Revised fix: use the "Alternative (simpler)" approach.** Three steps:
> 1. Add a `part_usage_names: dict[str, set[str]]` field to `HierarchyExtractionResult` (maps `owning_part_def_qn` → set of ALL child PartUsage names, including singletons)
> 2. Populate it during `extract_hierarchy_data()` by scanning `owned_members` for PartUsage elements (alongside existing `extract_multiplicities()`)
> 3. Modify Strategy 2 in `_scope_aggregation_expressions()` to use `hierarchy_data.part_usage_names.get(agg_expr.owning_part_qn, set())` instead of filtering `multiplicities` — this naturally handles both multiplicity and singleton children

---

## Root Cause 5: Alias Detection Searches Wrong Data Source

**File**: `hierarchy_resolver.py:519-528`
**Impact**: `total_capex` not found in `aliases`, breaking wiring to aggregation output

### Probe Data

```
Design-level binding check:
  Found annualized_financial CalcUsage
    param: total_capex direction=FeatureDirectionKind.In
      expr type: FeatureReferenceExpression
      referent name: capital_cost
      referent owner: Solar_Battery_Plant
```

No `:>> total_capex = capital_cost` redefinition exists on `Solar_Battery_Plant`. The alias is established by a **CalcUsage binding**: `calc annualized_financial { in total_capex = capital_cost; }`.

### Trace

```python
# hierarchy_resolver.py lines 519-528
for sibling in redefs:
    if (
        sibling.redefinition_type == RedefinitionType.CHAIN
        and sibling.source_path
        and sibling.source_path.endswith(agg.attribute_name)
        and sibling.attribute_name != agg.attribute_name
    ):
        agg.aliases.append(sibling.attribute_name)
```

This only looks at `:>>` CHAIN redefinitions on the **same PartDef**. `total_capex` is a CalcUsage parameter, not a PartDef redefinition → never found.

### Fix Options

**Option A (Recommended)**: Enhance backtracker index with CalcUsage binding aliases

In `DependencyBacktracker.__init__()`, after building the standard aggregation output index, scan CalcUsage bindings for parameter names that reference aggregation attribute names:

```python
# After _aggregation_output_index construction (line ~197):
for usage in self._calc_usages:
    for binding in usage.bindings:
        if binding.source_path and binding.param_name:
            # Check if source_path matches an aggregation attribute
            if binding.source_path in self._aggregation_output_index:
                # Register param_name as alias key
                alias_key = binding.param_name
                if alias_key not in self._aggregation_output_index:
                    self._aggregation_output_index[alias_key] = \
                        self._aggregation_output_index[binding.source_path]
```

**Option B**: Populate aliases during extraction by also scanning CalcUsages owned by the same PartDef.

> **UPDATE (Design Review 2026-02-12):** Option A alone **will NOT pass `test_bf7_aliases_extracted`**. That test asserts `"total_capex" in agg.aliases` on extraction-layer `AggregationExpressionData` (via `pipeline_context.hierarchy_data`), not on the backtracker's `_aggregation_output_index`. Option A enriches the index but leaves `agg.aliases` empty. Option B requires the hierarchy resolver to have CalcUsage data, breaking its extraction-only contract.
>
> **Revised fix: add a post-extraction alias enrichment step** in `build_pipeline_context()` between Step 3.5 (hierarchy extraction) and Step 4.7 (scoping). Add `_enrich_aliases_from_bindings(hierarchy_data, calc_usages)`:
> 1. Build a set of aggregation `attribute_name` values from `hierarchy_data.aggregation_expressions`
> 2. Scan `calc_usages` for bindings where `source_path` (bare name) matches an aggregation `attribute_name`
> 3. For matches where `binding.param_name != attribute_name`, add `param_name` to the matching aggregation's `.aliases` list
>
> This populates `agg.aliases` so the test passes, AND the backtracker's existing BF-7 alias code (lines 189-197) automatically propagates aliases into `_aggregation_output_index`. No backtracker changes needed — the existing code already handles aliases if they're populated on the data model.

---

## Bug Dependency Graph

```
Root Cause 1 (_unwrap_invocation strips FeatureChainExpression)
  ├── sum_terms always empty
  ├── arrayed parts classified as LocalTerm
  └── multiplicity entry points never created

Root Cause 2 (reconstruct_expression check ordering)
  ├── FeatureReferenceExpression → "Evaluation()"
  ├── FeatureChainExpression first operand → "Evaluation()"
  └── has_unsupported_nodes = True on all expressions

Root Cause 3 (_walk_aggregation_ast doesn't check FeatureChain/Ref types first)
  ├── singleton_terms always empty
  ├── standalone chains/refs hit "unsupported" path
  └── cascades with Root Cause 2

Root Cause 4 (_scope_aggregation_expressions misses all-singleton assemblies)
  ├── No aggregation modules for Site Infrastructure
  ├── No aggregation modules for Solar Battery Plant
  └── total_capex can never wire to nonexistent aggregation

Root Cause 5 (alias detection wrong data source)
  ├── aliases always empty
  ├── backtracker aggregation index missing alias keys
  └── total_capex falls through to entry_point

E2E Test Failures:
  test_bf1_no_unsupported_nodes    ← RC 2, RC 3
  test_bf1_sum_terms_have_real_names ← RC 1
  test_bf7_aliases_extracted         ← RC 5 (+ RC 4 = no Solar Battery Plant agg module)
  test_bf7_total_capex_wired_to_module_output ← RC 4, RC 5
```

---

## Fix Implementation Priority

| Priority | Root Cause | Fix Location | Complexity | Impact |
|---|---|---|---|---|
| **P0** | RC 1: `_unwrap_invocation` | `hierarchy_resolver.py:294` | 1 line (add `if func_name in _KNOWN_WRAPPER_FUNCTIONS:`) | Fixes sum_terms extraction for all assemblies |
| **P0** | RC 2: `reconstruct_expression` | `expression_utils.py:47-58` | Reorder ~10 lines | Fixes all text rendering, eliminates "Evaluation()" artifacts |
| **P1** | RC 3: `_walk_aggregation_ast` | `hierarchy_resolver.py:346` | Add 15-line block before line 347 | Fixes singleton/local term classification |
| **P1** | RC 4: Scoping all-singleton assemblies | `initialization.py:332` | Add ~15-line Strategy 3 | Fixes Site Infra + Solar Battery Plant scoping |
| **P2** | RC 5: Alias detection | `dependency_backtracker.py:~197` | Add ~10-line CalcUsage binding scan | Fixes total_capex alias wiring |

**Recommended order**: Fix RC 1 + RC 2 first (they're independent and P0). Then RC 3 (depends on RC 2). Then RC 4 and RC 5 (independent of each other, both P1/P2).

> **UPDATE (Design Review 2026-02-12):** Revised implementation approach:
>
> | Priority | Root Cause | Revised Fix | Complexity |
> |---|---|---|---|
> | **P0** | RC 1 | Type guards in `_unwrap_invocation()` (not `_KNOWN_WRAPPER_FUNCTIONS`) | ~4 lines |
> | **P0** | RC 2 | Reorder checks in `expression_utils.py` (as proposed) | ~10 lines |
> | **P1** | RC 3 | **Move** existing handlers up in `_walk_aggregation_ast()` (don't rewrite) | 0 new lines |
> | **P1** | RC 4 | Add `part_usage_names` field to `HierarchyExtractionResult` + populate in extraction + widen Strategy 2 | ~20 lines across 3 files |
> | **P1** | RC 5 | Add `_enrich_aliases_from_bindings()` in `initialization.py` between Step 3.5 and 4.7 | ~15 lines |
>
> **Revised order**: RC2 → RC1 → RC3 → RC4 → RC5. RC2 first (unblocks RC3's `extract_feature_chain_name()` correctness). RC1 independent. RC3 is just a block relocation after RC2. RC4 and RC5 independent.

---

## Expected Results After All Fixes

### Solar Array capital_cost:
```
sum_terms: [SumTerm(pv_module, capital_cost, module_count, 20), SumTerm(inverter, capital_cost, inverter_count, 4)]
singleton_terms: [SingletonTerm(array_bos.capital_cost)]
local_terms: [LocalTerm(misc_hardware_cost)]
has_unsupported: False
transformed: (module_count * pv_module.capital_cost) + (inverter_count * inverter.capital_cost) + array_bos.capital_cost + misc_hardware_cost
aliases: []
```

### Solar Battery Plant capital_cost:
```
sum_terms: []
singleton_terms: [SingletonTerm(solar_array.capital_cost), SingletonTerm(battery_system.capital_cost), SingletonTerm(site_infra.capital_cost)]
local_terms: []
has_unsupported: False
transformed: solar_array.capital_cost + battery_system.capital_cost + site_infra.capital_cost
aliases: [total_capex]  (after RC 5 fix, or via backtracker index)
```

### Scoped aggregation count:
- Currently: 10 (Solar Array × 5 + Battery System × 5)
- Expected: 20 (+ Site Infrastructure × 5 + Solar Battery Plant × 5)

### annualized_financial.total_capex:
- Currently: `source_type = entry_point`
- Expected: `source_type = module_output`, `producer_channel = SolarBatteryDesign__solar_battery_plant__capital_cost__capital_cost`

---

## Validation Plan

After implementing fixes, run in order:

1. `uv run python scripts/probes/probe_sum_ast_structure.py` — Verify `extract_feature_chain_name()` returns "pv_module.capital_cost"
2. `uv run python scripts/probes/probe_redefinition_structure.py` — Verify CHAIN redefs show "cost_model.total_cost" not "Evaluation().total_cost"
3. `uv run python scripts/probes/probe_alias_resolution.py` — Verify aliases populated and wiring correct
4. `uv run pytest tests/integration/test_hierarchy_e2e.py -v` — All 10 tests should pass
5. `uv run pytest tests/ -v` — Full regression

---

## Appendix: Why Agent ab15303's CollectExpression Theory Was Wrong

The investigation agent hypothesized that SysIDE wraps sum() operands in `CollectExpression` (a subclass of `OperatorExpression`). The probe definitively refutes this:

- The actual sum() operand is a **FeatureChainExpression** (not CollectExpression)
- FeatureChainExpression IS-NOT-A OperatorExpression in the type hierarchy
- There is NO CollectExpression node anywhere in the solar_battery model AST
- The agent was reasoning from KerML specification documentation, not actual SysIDE runtime data
- The SysIDE Java implementation apparently resolves the collect/select semantics differently from the abstract KerML spec

**Lesson**: Always validate AST hypotheses against probe output, never rely solely on specification documentation.
