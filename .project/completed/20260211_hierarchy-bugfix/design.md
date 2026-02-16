# Design: Hierarchy Pipeline Bug Fixes

**Status:** Revised (post-review)
**Owner:** Reid Westwood
**Created:** 2026-02-11 04:02 UTC
**Branch:** cost-pattern
**Commit:** f49005c
**Complexity:** MEDIUM

---

## Overview

8 bug fixes across 6 source files to make the hierarchy-aware aggregation pipeline produce correct, executable output for the solar_battery model. Each fix targets a subsystem boundary integration gap discovered during E2E validation.

## Related Artifacts

- **Spec:** `.project/active/hierarchy-bugfix/spec.md`
- **Root Cause Report 1:** `.project/research/20260211-032608_hierarchy-e2e-bug-root-cause-analysis.md`
- **Root Cause Report 2:** `.project/research/20260211_035136_root-cause-hierarchy-deviations.md`
- **Epic:** `.project/backlog/epic_costed_component_pattern.md`

## Research Findings

### Files Analyzed

| File | Lines | Purpose |
|------|-------|---------|
| `hierarchy_resolver.py` | 275-498 | `_walk_aggregation_ast()` and `build_aggregation_expression()` |
| `expression_utils.py` | 1-197 | `reconstruct_expression()`, `extract_feature_chain_name()` |
| `cli/__init__.py` | 410-589 | `_generate_aggregation_modules()`, `_generate_aggregation_stencils()` |
| `initialization.py` | 296-347 | `_scope_aggregation_expressions()` Strategy 1 & 2 |
| `dependency_backtracker.py` | 113-248, 440-520, 760-855 | `__init__`, aggregation index, resolution strategies |
| `graph_builder.py` | 69-217, 794-818, 900-1086 | `build_computation_graph()`, output catalog, `_build_aggregation_module()` |
| `data_models.py` | 224-361 | `RedefinitionData`, `ScopedAggregationData`, `HierarchyExtractionResult` |
| `auto_implementation.py.jinja2` | 1-37 | Stencil template expects `inputs.X`-form expressions |

### Key Patterns Found

- **AST InvocationExpression dispatch** (`hierarchy_resolver.py:320-372`): The `sum()` handler at line 325 tests operands for `FeatureChainExpression` or falls back to `extract_feature_reference_name()`. Non-sum invocations at line 366-372 mark `has_unsupported=True`. This is the exact dispatch point for BF-1.
- **Module name lowercasing** (`qualified_names.py:get_module_name()`): Returns `eqn.lower()`. Dict keys in `_generate_aggregation_modules()` use `m.name` (lowered), but lookups use `agg.module_eqn` (mixed-case).
- **`PythonModulePath.from_sysml()`**: Used in both module wrapper and stencil generation. Takes a `SysMLQualifiedName` which determines the directory/file layout. Currently fed `owning_part_qn::attribute_name` (PartDef-scoped) instead of the instance-scoped EQN.
- **Aggregation output index** (`dependency_backtracker.py:153-183`): Builds 3 key patterns per aggregation: `part_usage_name.attribute_name`, bare `attribute_name`, and full instance dotted path. Does NOT register `:>>` redefinition aliases.
- **Step 6.6 param group rebuild** (`graph_builder.py:190-203`): Calls `group_deriver.derive_groups()` then filters by `all_ep_names`. The deriver only produces `ParameterSource` entries from 4 indices (`_attr_index`, `_binding_index`, `_unbound_index`, `_literal_index`). Multiplicity entry points from library PartDefs appear in none.
- **CHAIN-type redefinitions create EXPOSE_PURE aliases**: `:>> total_capex = capital_cost` is a CHAIN redef with `source_path` ending in the aggregation's `attribute_name`. These aliases must be surfaced on `AggregationExpressionData` at extraction time so the backtracker can register them without needing a separate `redefinitions` parameter.
- **`_scope_aggregation_expressions()` Strategy 2** (`initialization.py:330-338`): Exact string comparison `seg.lower() == owning_name`. Fails when PartDef name (`site_infrastructure`) differs from PartUsage QN segment (`site_infra`). Fix uses child-walk via `MultiplicityData` (parent-child structural data) instead of name-similarity heuristics.

---

## Proposed Design

### Fix Ordering & Dependencies

```
BF-1 (AST unwrap)          ← prerequisite for BF-2
BF-3 (case mismatch)       ← independent, trivial
BF-4 + BF-5 (path fixes)   ← independent, same pattern
BF-6 (site_infra scoping)  ← independent
BF-7 (total_capex alias)   ← independent
BF-8 (multiplicity EPs)    ← independent
BF-2 (expression compile)  ← depends on BF-1
```

All fixes are backward-compatible — they only change behavior for aggregation modules (non-aggregation CalcDef pipeline is untouched).

---

### BF-1: Unwrap InvocationExpression Wrapper in sum() Operands

**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py:320-372`

**Problem:** When `func_name == "sum"`, the operand is an `InvocationExpression[func='Evaluation']` wrapping the actual `FeatureChainExpression`. The code expects `FeatureChainExpression` directly.

**Design:** Insert an unwrap step between extracting the operand and type-testing it. The unwrap should handle ANY `InvocationExpression` wrapper (not just `Evaluation`), since SysIDE may use `collect`, `select`, or other semantics.

**Change at `hierarchy_resolver.py:325-330`:**

Current:
```python
if func_name == "sum" and operands:
    operand = operands[0]
    if SysideAdapter.is_instance(operand, "FeatureChainExpression"):
```

New logic:
```python
if func_name == "sum" and operands:
    operand = operands[0]
    # Unwrap InvocationExpression wrapper (e.g., Evaluation/collect/select)
    operand = _unwrap_invocation(operand)
    if SysideAdapter.is_instance(operand, "FeatureChainExpression"):
```

**New helper `_unwrap_invocation(node)`** (add near line 275, before `_walk_aggregation_ast`):
- If `node` has `function.name` attribute (i.e., is an InvocationExpression) AND has operands, recurse into `operands[0]`.
- Recurse up to a depth limit (e.g., 3) to handle nested wrappers.
- Return the innermost non-InvocationExpression node, or the original if no wrapper found.
- This is defensive: if the operand is already a `FeatureChainExpression`, it passes through unchanged.

**Also update the non-sum InvocationExpression branch** at line 366-372: Before marking `has_unsupported=True`, check if this invocation is a known wrapper pattern (Evaluation, collect, select). If so, unwrap and recurse into `_walk_aggregation_ast()` instead of marking unsupported. This handles singleton terms that may also be wrapped.

**Cascade effects:** Fixes Report 1 Bug 2B (`has_unsupported_nodes` will be `False`) and Report 1 Bug 3 (garbage `Evaluation()` param names).

**`expression_utils.py` — no update needed.** The spec (line 97) mentions updating `reconstruct_expression()` for display purposes. After investigation: `reconstruct_expression()` is a generic AST-to-text utility used to produce `AggregationExpressionData.raw_expression_text` (informational display string). It is NOT in the compilation path — `_walk_aggregation_ast()` handles all transform-critical AST dispatch independently and never delegates to `reconstruct_expression()` for its output. The `raw_expression_text` may still show `Evaluation(pv_module.capital_cost)` after this fix, but that text is purely diagnostic and does not affect generated code. Updating `reconstruct_expression()` would require an unwrap that mirrors `_unwrap_invocation()`, creating parallel logic in two files with no functional benefit.

**Testing:** Existing `test_hierarchy_resolver.py` tests for `_walk_aggregation_ast()` should be extended with a test that wraps a `FeatureChainExpression` in an `InvocationExpression(func='Evaluation')`. Verify `transformed_expression` shows real attribute names and `has_unsupported_nodes=False`.

---

### BF-2: Add Aggregation Expression Compilation Step

**Files:** `src/sysml_codegen/resolution/graph_builder.py:900-1086`, `src/sysml_codegen/resolution/models.py:149-169`, `src/sysml_codegen/cli/__init__.py:510-589`

**Problem:** `_generate_aggregation_stencils()` writes `transformed_expression` (symbolic text like `module_count * pv_module.capital_cost`) directly into the auto-impl template. The template expects `inputs.X`-form Python (e.g., `inputs.module_count * inputs.pv_module_capital_cost`).

**Design: Build the symbolic→param_name mapping inline during input construction in `_build_aggregation_module()`, compile the expression, and store on `PipelineModule`.**

The `param_name` for each input is already derived during input construction. Instead of re-deriving these mappings in a post-pass (which duplicates the derivation logic and creates divergence risk), build the `ref_to_inputs` dict alongside each `ModuleInput` creation.

**Step 1 — Initialize `ref_to_inputs` at the top of `_build_aggregation_module()`** (~line 920):

```python
ref_to_inputs: dict[str, str] = {}
```

**Step 2 — Populate inline during each input construction:**

For SumTerm processing (~line 935), after `param_name` is derived:
```python
param_name = f"{term.part_usage_name}_{term.attribute_name}"
ref_to_inputs[f"{term.part_usage_name}.{term.attribute_name}"] = f"inputs.{param_name}"
```

For multiplicity inputs (~line 988), after `param_name` is set:
```python
ref_to_inputs[term.multiplicity_attr] = f"inputs.{term.multiplicity_attr}"
```

For SingletonTerm processing (~line 999), after `param_name` is derived:
```python
param_name = s_term.source_path.replace(".", "_")
ref_to_inputs[s_term.source_path] = f"inputs.{param_name}"
```

For LocalTerm processing (~line 1045), after `param_name` is set:
```python
ref_to_inputs[l_term.attribute_name] = f"inputs.{l_term.attribute_name}"
```

This ensures each `ref_to_inputs` entry uses the exact same `param_name` derivation as the corresponding `ModuleInput` — no duplication, no divergence.

**Step 3 — Compile the expression** (after all inputs are built, ~line 1070):

Replace symbolic refs with `inputs.X` form. Sort replacements by length (longest first) to avoid partial matches:

```python
compiled = agg.expression.transformed_expression
for ref in sorted(ref_to_inputs, key=len, reverse=True):
    compiled = compiled.replace(ref, ref_to_inputs[ref])
```

**Assumption:** `transformed_expression` is pure arithmetic extracted from SysML AST (operators, dotted references, numeric literals). It will never contain string literals, comments, or other contexts where a symbolic ref could appear as a non-semantic substring. This is guaranteed by the structure of `_walk_aggregation_ast()` which only emits operator expressions and symbolic references. If this assumption is violated in the future (e.g., SysML expressions with string operations), the compilation step would need to be upgraded to a proper AST transform.

**Step 4 — Store on PipelineModule.** Add `compiled_expression: str | None = None` to `PipelineModule` in `resolution/models.py`. Set it during module construction at ~line 1078. This follows the same pattern as `ComputedAttributeData.compiled_expression` in the CalcDef pipeline.

**Step 5 — Read in `_generate_aggregation_stencils()`** (`cli/__init__.py:553-566`). Look up the `PipelineModule` for this aggregation (using the same fixed lookup from BF-3) and use `pipeline_module.compiled_expression` instead of `agg.expression.transformed_expression` for the `single_output_expression` and `output_expressions[0].expression` template variables.

**Testing:** Unit test that `_build_aggregation_module()` produces a `compiled_expression` containing `inputs.` prefixed references. Integration test that generated `_impl.py` files pass `ast.parse()`.

---

### BF-3: Fix Aggregation Module Input Lookup Case Mismatch

**File:** `src/sysml_codegen/cli/__init__.py:427-453`

**Problem:** `agg_modules_by_name` is keyed by `m.name` (lowercased via `get_module_name()`), but lookup uses `agg.module_eqn` (mixed-case).

**Design — One-line fix at line 453:**

Current:
```python
pipeline_module = agg_modules_by_name.get(agg.module_eqn)
```

Fix:
```python
pipeline_module = agg_modules_by_name.get(get_module_name(agg.module_eqn))
```

`get_module_name()` is already imported at line 421. This normalizes the lookup key to match the dict key format.

**Testing:** Existing tests should pass. Add a test that verifies aggregation module wrappers have non-empty `Input` classes.

---

### BF-4 + BF-5: Use Instance-Scoped EQN for Module Wrapper and Stencil Paths

**Files:** `src/sysml_codegen/cli/__init__.py:433-443` (wrappers), `:533` (stencils)

**Problem:** Both functions derive `sysml_qn` from `agg.expression.owning_part_qn` (PartDef QN), producing PartDef-scoped directory paths that don't match the pipeline YAML module keys.

**Design — Use `agg.module_eqn` for path derivation in both locations.**

**BF-4 change at `cli/__init__.py:434`:**

Current:
```python
sysml_qn = f"{agg.expression.owning_part_qn}::{agg.expression.attribute_name}"
```

Fix: Derive the SysML QN from the instance-scoped module EQN. The `module_eqn` is already in Python-qualified form (`instance_path__attribute_name`). We need to convert it to a `SysMLQualifiedName`-compatible format. Since `PythonModulePath.from_sysml()` expects a `::` separated QN, and `module_eqn` uses `__`:

```python
sysml_qn = agg.module_eqn.replace("__", "::")
```

This produces `SolarBatteryDesign::solar_battery_plant::solar_array::capital_cost` which `PythonModulePath.from_sysml()` will translate to a directory path matching the YAML key.

**BF-5 — identical change** at `cli/__init__.py:533` in `_generate_aggregation_stencils()`:

Same replacement: `sysml_qn = agg.module_eqn.replace("__", "::")`.

Also update the `module_eqn` derivation at line 536-537 (which recomputes it) to just use `agg.module_eqn` directly instead of recalculating from the now-changed `sysml_qn`.

**Testing:** Verify module wrapper directories use instance-scoped paths (e.g., `solarbatterydesign__solar_battery_plant__solar_array/capital_cost.py`). Verify stencil paths match.

---

### BF-6: Fix Site Infrastructure Missing from Aggregation Scoping

**File:** `src/sysml_codegen/generation/initialization.py:296-347`

**Problem:** Strategy 2 at line 336 does exact string comparison: `seg.lower() == owning_name`. PartDef name `"Site Infrastructure"` sanitizes to `"site_infrastructure"`, but the PartUsage QN segment is `"site_infra"`. Exact match fails.

**Design — Replace Strategy 2 with child-walk using `MultiplicityData`.**

The key insight: when a PartDef has no direct virtual CalcUsages (Strategy 1 fails), its *children* will have virtual CalcUsages. `MultiplicityData` records each PartDef's children: `owning_part_def_qn` is the parent PartDef, `part_usage_name` is the child PartUsage. By finding the child's name in a virtual CalcUsage QN, we can derive the parent's instance path (the segment immediately before the child).

This uses structural parent-child relationships from the SysML model rather than name-similarity heuristics. It handles arbitrary naming differences (e.g., `site_infra` typed by `SiteInfrastructure`) because it never compares PartDef names to PartUsage names — it only uses the child's `part_usage_name` which is the actual name used in the design tree.

**Implementation — Replace Strategy 2 body** (`initialization.py:330-338`):

```python
# Strategy 2: Child-walk — find parent instance path via child PartUsages
if not instance_paths:
    # Get children of this PartDef from multiplicities
    children = {
        m.part_usage_name.lower()
        for m in hierarchy_data.multiplicities
        if m.owning_part_def_qn == agg_expr.owning_part_qn
    }
    if children:
        for _partdef_qn, qns in virtual_qns_by_partdef.items():
            for qn in qns:
                segments = qn.split("__")
                for i, seg in enumerate(segments):
                    if seg.lower() in children and i > 0:
                        # Parent is the segment before the child
                        parent_path = "__".join(segments[:i])
                        instance_paths.add(parent_path)
                        break
```

**Why this works for `SiteInfrastructure`:** The PartDef `SiteInfrastructure` has children like `grid_connection`, `substation`, etc. (from multiplicities). Virtual CalcUsage QNs contain segments like `...site_infra__grid_connection__...`. When we find `grid_connection` in the QN, the preceding segment `site_infra` is the parent's instance name. We take all segments up to (but not including) the child to get the parent instance path.

**What gets removed:** The existing Strategy 2 name-matching code at lines 330-338. No prefix/containment heuristic is needed.

**Testing:** Verify all 4 assemblies produce aggregation modules (including Site Infrastructure). Total scoped aggregation count should be ~20 (4 assemblies x 5 attributes).

---

### BF-7: Register EXPOSE_PURE Aliases in Aggregation Output Index

**Files:** `src/sysml_codegen/extraction/hierarchy_resolver.py:400-448`, `src/sysml_codegen/extraction/data_models.py:296-326`, `src/sysml_codegen/analysis/dependency_backtracker.py:153-183, 464-470`

**Problem:** Two sub-problems:
1. **Alias mismatch:** The aggregation output index keys on `capital_cost` (underlying attribute), but CalcUsage bindings reference `total_capex` (the `:>>` EXPOSE_PURE alias created by a CHAIN-type redefinition: `:>> total_capex = capital_cost`).
2. **Sanitization mismatch:** The `::` fallback at `dependency_backtracker.py:464-470` constructs `"Solar Battery Plant.total_capex"` (unsanitized) but the index has `"solar_battery_plant.capital_cost"` (sanitized).

**Design — Resolve aliases at extraction time, store on `AggregationExpressionData`, read in backtracker.**

This keeps alias resolution in the extraction layer where all redefinitions are already in scope, avoids threading a new `redefinitions` parameter into the backtracker, and makes the alias relationship explicit in the data model.

**Change 1: Add `aliases` field to `AggregationExpressionData`** (`data_models.py:296-326`):

```python
aliases: list[str] = field(default_factory=list)  # CHAIN redef aliases (e.g., ["total_capex"])
```

**Change 2: Populate aliases in `build_aggregation_expression()`** (`hierarchy_resolver.py:400-448`):

The function already receives the `RedefinitionData` it's processing and has access to all redefinitions on the same PartDef. After building the `AggregationExpressionData`, scan sibling redefinitions for CHAIN-type entries whose `source_path` ends with this aggregation's `attribute_name`:

```python
# Find CHAIN-type aliases for this aggregation attribute
aliases = []
for sibling_redef in all_redefs_on_part:
    if (sibling_redef.redefinition_type == RedefinitionType.CHAIN
            and sibling_redef.source_path
            and sibling_redef.source_path.endswith(agg_data.attribute_name)
            and sibling_redef.attribute_name != agg_data.attribute_name):
        aliases.append(sibling_redef.attribute_name)
agg_data.aliases = aliases
```

This requires `build_aggregation_expression()` to receive the list of all redefinitions on the same `owning_part_qn`. Currently it receives a single `RedefinitionData`. Adjust the caller in `extract_hierarchy_patterns()` to pass the sibling list, or build the alias lookup at the call site and pass the result. The simplest approach: after `build_aggregation_expression()` returns, do the alias scan at the call site using the already-available `redefinitions` list filtered by `owning_part_qn`.

**Change 3: Register alias entries in `_aggregation_output_index`** (`dependency_backtracker.py:153-183`):

After the existing 3-key registration loop, add an alias pass that reads from `agg.expression.aliases`:

```python
# Register :>> EXPOSE_PURE aliases
for alias_name in agg.expression.aliases:
    self._aggregation_output_index[
        f"{part_usage_name}.{alias_name}"
    ] = channel
    if alias_name not in self._aggregation_output_index:
        self._aggregation_output_index[alias_name] = channel
    dotted_alias = ".".join(instance_parts + [alias_name])
    self._aggregation_output_index[dotted_alias] = channel
```

No new constructor parameter needed — the backtracker already receives `aggregation_data` which carries the aliases.

**Change 4: Sanitize PartDef names in `::` fallback** (`dependency_backtracker.py:464-470`):

This is orthogonal to alias registration but required for the `::` lookup path to work.

Current:
```python
dotted = f"{parts[-2]}.{parts[-1]}"
```

Fix:
```python
dotted = f"{sanitize_name(parts[-2]).lower()}.{parts[-1]}"
```

This handles `"Solar Battery Plant::total_capex"` → `"solar_battery_plant.total_capex"` which matches the alias registered above.

**Testing:** Verify `annualized_financial.total_capex` resolves to `MODULE_OUTPUT` (aggregation chain) not `ENTRY_POINT`.

---

### BF-8: Surface Multiplicity Entry Points in Parameter Groups

**File:** `src/sysml_codegen/resolution/graph_builder.py:190-203`

**Problem:** `derive_groups()` only produces `ParameterSource` entries from 4 indices. Multiplicity attributes are library PartDef attributes that appear in none of these indices. The Step 6.6 filter drops them.

**Design — Collect orphan entry points and assign to a synthetic group. Use `ModuleInput.python_type` for authoritative type information.**

The type information already exists: `_build_aggregation_module()` sets `python_type="int"` on multiplicity `ModuleInput`s (graph_builder.py:989) and `python_type="float"` on others. Rather than guessing types from naming conventions, build a lookup from the modules that consume these entry points.

After the Step 6.6 filter at `graph_builder.py:190-203`, add:

```python
# Collect entry points covered by param_groups
covered_ep_names = set()
for group in param_groups:
    for p in group.parameters:
        covered_ep_names.add(p.qualified_name)

# Find orphan entry points (in entry_points dict but not in any group)
orphan_eps = {
    qn: ep for qn, ep in entry_points.items()
    if qn not in covered_ep_names
}

if orphan_eps:
    # Build ep_qn -> python_type lookup from ModuleInput sources
    ep_type_lookup: dict[str, str] = {}
    for m in modules:
        for inp in m.inputs:
            if inp.source.source_type == "entry_point":
                ep_type_lookup[inp.source.qualified_name] = inp.python_type

    orphan_params = []
    for qn, ep in orphan_eps.items():
        orphan_params.append(EntryPoint(
            qualified_name=qn,
            simple_name=ep.simple_name,
            entry_type=ep.entry_type,
            default_value=ep.default_value,
            python_type=ep_type_lookup.get(qn, "float"),
        ))
    if orphan_params:
        param_groups.append(ParameterGroup(
            name="system_design",
            class_name="SystemDesign",
            source_file=Path("hierarchy"),
            parameters=orphan_params,
        ))
```

This catches ANY orphan entry point, not just multiplicity — making it robust against future entry point types that the deriver doesn't know about. The `ep_type_lookup` ensures types are authoritative (from the `ModuleInput` that consumes the entry point) rather than heuristic.

**Note:** This requires `EntryPoint` to have a `python_type` field, or the synthetic group must use `ParameterGroup` with `EntryPoint` parameters directly (which already exist in `entry_points` dict). Check the existing `ParameterGroup.parameters` type — it's `list[EntryPoint]` (resolution/models.py:84), so we append `EntryPoint` objects directly. If `EntryPoint` lacks `python_type`, we need to either (a) add it as an optional field, or (b) carry the type on a parallel dict and have the schema generator read from `ep_type_lookup`.

**Testing:** Verify `module_count`, `inverter_count`, `pack_count` appear in parameter group schemas. Verify multiplicity params have `int` type, not `float`.

---

## Potential Risks

| Risk | Mitigation |
|------|-----------|
| BF-1 unwrap may miss other wrapper patterns beyond Evaluation | Unwrap ANY InvocationExpression, not just Evaluation. Depth limit prevents infinite recursion. |
| BF-2 string replacement may cause partial matches | Sort replacements by length (longest first). All symbolic refs use dotted notation (`a.b`) which is unlikely to be a substring of another. `transformed_expression` is guaranteed to be pure arithmetic from `_walk_aggregation_ast()` — no string literals or comments. |
| BF-4/5 `module_eqn.replace("__", "::")` may break if EQN contains segments with `__` | Module EQNs are built from `instance_path__attribute_name` where instance_path uses `__` as the canonical separator. This is the same format throughout the codebase. |
| BF-6 child-walk may miss PartDefs with no children in `MultiplicityData` | Such a PartDef would have no child PartUsages with multiplicity, meaning it's a leaf node. Leaf assembly PartDefs without multiplicities wouldn't produce `sum()` aggregations (nothing to sum over), so they wouldn't appear in `aggregation_expressions` in the first place. |
| BF-7 CHAIN redef alias matching may be too broad | Scoped to same `owning_part_qn` and `source_path` ending with the exact `attribute_name`. Aliases are resolved at extraction time and stored explicitly on the data model — visible and testable. |
| BF-8 synthetic group may mix unrelated parameters | Only collects true orphans. Types are authoritative from `ModuleInput.python_type`, not heuristic. |

## Integration Strategy

- All fixes target the existing hierarchy-aware pipeline added in Items 2-4
- No public API changes — all fixes are internal to the pipeline
- Non-aggregation CalcDef pipeline is completely untouched
- Fixes should be applied in the order specified (BF-1 first, BF-2 last) due to the BF-1→BF-2 dependency
- Each fix can be independently tested before proceeding to the next

## Validation Approach

### Per-Fix Unit Tests
- BF-1: Mock `InvocationExpression(Evaluation)` AST wrapper, verify `_walk_aggregation_ast()` produces correct `SumTerm` and `transformed_expression`
- BF-2: Verify `compiled_expression` contains `inputs.` prefixed references; `ast.parse()` succeeds
- BF-3: Verify aggregation module lookup finds the correct `PipelineModule`
- BF-4/5: Verify generated file paths use instance-scoped names
- BF-6: Verify 4 assemblies in scoped aggregation output (not 3)
- BF-7: Verify `total_capex` binding resolves to `MODULE_OUTPUT`
- BF-8: Verify orphan entry points appear in `system_design` parameter group

### Integration Validation (E2E)
- Total impl file count: ~36 (16 existing + ~20 aggregation)
- `IMPLEMENTATION_BACKLOG.md` shows "0 functions to implement"
- Pipeline YAML has valid Python identifiers for all input parameter names
- All existing tests pass: `uv run pytest tests/`

---

Next Step: After approval → `/_my_implement` or `/_my_plan`
