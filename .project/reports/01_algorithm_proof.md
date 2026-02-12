# Architectural Proof: Aggregation Pipeline Algorithm Trace

**Date:** 2026-02-12
**Branch:** cost-pattern
**Scope:** 4 critical algorithms in the aggregation data-flow path

---

## Table of Contents

1. [Algorithm 1: Hierarchy Extraction (`_walk_aggregation_ast` / `_unwrap_invocation` / `build_aggregation_expression`)](#algorithm-1-hierarchy-extraction)
2. [Algorithm 2: Aggregation Scoping (`_scope_aggregation_expressions`)](#algorithm-2-aggregation-scoping)
3. [Algorithm 3: Backtracker Aggregation Index (`_aggregation_output_index`)](#algorithm-3-backtracker-aggregation-index)
4. [Algorithm 4: Graph Builder Aggregation Module (`_build_aggregation_module`)](#algorithm-4-graph-builder-aggregation-module)
5. [Cross-Algorithm Sequencing Analysis](#cross-algorithm-sequencing)
6. [Specific Question Answers](#specific-question-answers)
7. [Invariant Violation Summary](#invariant-violation-summary)

---

## Algorithm 1: Hierarchy Extraction

### Files
- `/home/reid/1cfe/sysml-codegen/src/sysml_codegen/extraction/hierarchy_resolver.py`
- `/home/reid/1cfe/sysml-codegen/src/sysml_codegen/extraction/expression_utils.py`

### 1.1 `_unwrap_invocation()` (Lines 278-298)

#### Input Contract
- `node`: Any AST node, potentially an `InvocationExpression` wrapper
- `_depth`: Recursion depth counter (max 3)

#### Processing Steps
1. **Line 292**: Guard: if `_depth >= 3`, return node unchanged (prevents infinite recursion)
2. **Line 294**: Check if node has `function` attribute AND `function.name` attribute
3. **Line 295**: Extract operands as a list via `getattr(node, "operands", [])`
4. **Line 296-297**: If operands non-empty, recurse on `operands[0]` with `_depth + 1`
5. **Line 298**: Otherwise return node unchanged

#### Branching Conditions
| Condition | Branch | Result |
|-----------|--------|--------|
| `_depth >= 3` | Early return | Returns original node |
| `hasattr(node, "function") and hasattr(node.function, "name")` is True, operands non-empty | Recurse | Peels one InvocationExpression layer |
| Above is True but operands empty | Fall through | Returns original node |
| Node has no `function.name` | Fall through | Returns original node |

#### Output Contract
Returns the innermost non-InvocationExpression node, or the original node if unwrapping fails.

#### CRITICAL ASSUMPTION GAP: No function name filtering
The function does NOT check `node.function.name` against `_KNOWN_WRAPPER_FUNCTIONS`. It unconditionally recurses into `operands[0]` for ANY node with `function.name`. This means:
- A `sum(Evaluation(FeatureChainExpression))` node: `_unwrap_invocation` is called on the `sum()` node. It sees `function.name == "sum"`, checks operands, finds `operands[0]` is the `Evaluation(...)` InvocationExpression, and recurses. On the Evaluation node, it sees `function.name == "Evaluation"`, extracts its `operands[0]` which is the `FeatureChainExpression`, and returns it. This WORKS correctly because the Evaluation wrapper IS unwrapped.
- **However**, `_unwrap_invocation` would also unwrap a legitimate function call like `sqrt(x)` -- it does not distinguish wrappers from real invocations. This is benign only because the callers at lines 352 and 394 handle the two cases separately.

### 1.2 `_walk_aggregation_ast()` (Lines 301-429)

#### Input Contract
- `node`: AST node (OperatorExpression, InvocationExpression, FeatureChainExpression, FeatureReferenceExpression, Literal, or unknown)
- `mult_lookup`: `dict[str, MultiplicityData]` keyed by `part_usage_name`
- `ctx`: Mutable `_AggregationContext` accumulator

#### Processing Steps (Decision Tree)

```
node == None? -> return ""
|
is OperatorExpression?
|  -> Binary (2 operands): recurse left/right, join with operator
|  -> Unary (1 operand): recurse, prefix operator
|  -> N-ary (>2 operands): recurse all, join with operator
|  -> No operands: return operator string
|
has function.name? (InvocationExpression)
|  -> function.name == "sum" AND operands?
|     -> _unwrap_invocation(operands[0])
|     -> if result is FeatureChainExpression: extract_feature_chain_name()
|     -> else: extract_feature_reference_name()
|     -> split chain_name on "." (max 1 split)
|     -> if 2 parts (part.attr):
|        -> lookup mult_data for part_name
|        -> if mult_data has count_attribute_name:
|           -> Append SumTerm WITH multiplicity_attr
|           -> Append input_channel
|           -> Append entry_point (multiplicity count attr)
|           -> Return "(count_attr * chain_name)"
|        -> else (no multiplicity):
|           -> Append SumTerm WITHOUT multiplicity_attr (None)
|           -> Append input_channel
|           -> Return chain_name (UNTRANSFORMED)
|     -> if 1 part (bare name):
|        -> Append LocalTerm
|        -> Return chain_name
|  -> function.name in _KNOWN_WRAPPER_FUNCTIONS AND operands?
|     -> _unwrap_invocation(node) -> if different node, recurse
|  -> else: mark unsupported, reconstruct as "func(args)"
|
is FeatureChainExpression?
|  -> extract name, append SingletonTerm, append input_channel, return name
|
is FeatureReferenceExpression?
|  -> extract name, append LocalTerm, return name
|
is literal?
|  -> return reconstruct_expression()
|
unknown:
|  -> mark unsupported, return str(node)
```

#### Critical Line-by-Line for sum() path (Lines 351-390)

**Line 351**: `if func_name == "sum" and operands:`
**Line 352**: `operand = _unwrap_invocation(operands[0])`

Here is the critical unwrapping. When the AST looks like:
```
InvocationExpression(function.name="sum")
  operands[0] = InvocationExpression(function.name="Evaluation")
    operands[0] = FeatureChainExpression(target="capital_cost", operands=[FeatureRef("pv_module")])
```

`_unwrap_invocation(operands[0])` receives the Evaluation InvocationExpression. It has `function.name`, so line 294 passes. It extracts `operands` of the Evaluation node. If those operands are non-empty, it recurses on `operands[0]` which is the FeatureChainExpression. The FeatureChainExpression does NOT have `function.name`, so line 294 fails, and it returns the FeatureChainExpression directly. **This is correct behavior.**

**Line 353-356**: Type dispatch on unwrapped operand:
- FeatureChainExpression -> `extract_feature_chain_name()`
- Otherwise -> `extract_feature_reference_name()`

**Line 358**: `parts = chain_name.split(".", 1)` -- splits "pv_module.capital_cost" into ["pv_module", "capital_cost"]

**Lines 359-370**: If 2 parts, do multiplicity lookup and create SumTerm with full data.
**Lines 379-386**: If no multiplicity, still create SumTerm but with `multiplicity_attr=None`, `multiplicity_count=None`. The chain_name is returned raw (no parametric multiply transformation).

#### ASSUMPTION GAP 1: `_unwrap_invocation` vs nested wrappers

If the real AST has deeper nesting like `sum(collect(Evaluation(FeatureChainExpr)))`, the `_unwrap_invocation` function handles it -- it recurses up to depth 3. But `_walk_aggregation_ast` calls `_unwrap_invocation(operands[0])` at line 352 which starts the recursion from the first operand of `sum()`. If that first operand is `collect(Evaluation(FCE))`, `_unwrap_invocation` will:
1. See `collect` has `function.name`, recurse on its `operands[0]` (the Evaluation node)
2. See `Evaluation` has `function.name`, recurse on its `operands[0]` (the FCE)
3. FCE has no `function.name`, return it.

This works for up to 3 layers. If there are 4+ layers, it returns the 3rd-layer node which may still be an InvocationExpression. Then at line 353, `SysideAdapter.is_instance(operand, "FeatureChainExpression")` fails, and it falls through to `extract_feature_reference_name(operand)` which may return garbage (the `name` attribute of the 3rd wrapper's referent).

#### ASSUMPTION GAP 2: `extract_feature_chain_name` operand structure

In `expression_utils.py` lines 133-161, `extract_feature_chain_name` assumes:
1. `expr_node.operands[0]` exists and can be reconstructed (line 138-143)
2. `expr_node.target_feature.name` exists (lines 145-148)

If the unwrapped node is actually a `FeatureReferenceExpression` (not a chain), the code correctly falls to line 356 and uses `extract_feature_reference_name`. But if the node is something unexpected (e.g., a nested OperatorExpression that was mistakenly left after unwrapping), `extract_feature_reference_name` would try `referent.name` which may not exist, falling through multiple fallback strategies before returning `str(expr_node)` -- a garbage string.

### 1.3 `build_aggregation_expression()` (Lines 432-480)

#### Input Contract
- `redef`: `RedefinitionData` with `redefinition_type == EXPRESSION` and non-None `expression_ast`
- `multiplicities`: `list[MultiplicityData]` for the same PartDef
- `part_element`: The owning PartDefinition AST element

#### Processing Steps
1. **Line 454-457**: Guard: return None if not EXPRESSION type or no AST
2. **Line 460**: Build `mult_lookup` dict keyed by `part_usage_name`
3. **Lines 463-466**: Create `_AggregationContext`, walk AST with `_walk_aggregation_ast`
4. **Lines 468-480**: Construct `AggregationExpressionData` from context

#### Output Contract
Returns `AggregationExpressionData` with:
- `sum_terms`: list of SumTerm (possibly empty if expression has no sum() calls)
- `singleton_terms`: list of SingletonTerm
- `local_terms`: list of LocalTerm
- `input_channels`: ALL upstream channel references (union of sum + singleton channels)
- `entry_points`: multiplicity count attribute names only
- `transformed_expression`: the rewritten expression text
- `has_unsupported_nodes`: True if any node couldn't be processed

#### Invariant: Multiplicity data must be co-located
`mult_lookup` is built from multiplicities extracted from the SAME PartDef (line 460). This means `_walk_aggregation_ast` can only resolve multiplicities for child PartUsages that are direct children of the owning PartDef. If a sum() references a grandchild or a part from a different scope, the lookup will fail, producing a SumTerm with `multiplicity_attr=None`.

### 1.4 `extract_hierarchy_data()` (Lines 483-541)

#### Processing Steps
1. **Lines 501-529**: For each PartDefinition:
   a. Extract redefinitions (line 502)
   b. Extract multiplicities (line 505)
   c. For each EXPRESSION redef, build aggregation expression (line 511)
   d. If aggregation has unsupported nodes, add warning (line 513-518)
   e. **BF-7 alias detection** (lines 521-528): scan sibling redefs for CHAIN type whose `source_path` ends with the aggregation `attribute_name` and has a different `attribute_name` -- those are aliases

2. **Lines 532-533**: Extract design overrides from PartUsages

#### ASSUMPTION GAP 3: BF-7 alias detection is fragile
Line 525: `sibling.source_path.endswith(agg.attribute_name)` -- this checks if the chain source path ENDS WITH the attribute name. Example: `:>> total_capex = capital_cost` has `source_path="capital_cost"` and `agg.attribute_name="capital_cost"`, so `"capital_cost".endswith("capital_cost")` is True. But if the source_path were a dotted path like `self.capital_cost`, it would also match `endswith("capital_cost")`. This could produce false positive aliases in some AST structures.

---

## Algorithm 2: Aggregation Scoping

### File
- `/home/reid/1cfe/sysml-codegen/src/sysml_codegen/generation/initialization.py` lines 296-355

### 2.1 `_scope_aggregation_expressions()` (Lines 296-355)

#### Input Contract
- `hierarchy_data`: `HierarchyExtractionResult | None`
- `calc_usages`: `list[CalcUsageData]` -- all usages including virtual (template-instantiated) ones

#### Processing Steps

1. **Lines 305-306**: Guard: return empty if no hierarchy data or no aggregation expressions

2. **Lines 311-317**: Build `virtual_qns_by_partdef` index:
   - Key: `usage.owning_part_def_qn` (the PartDef QN that owns the CalcUsage)
   - Value: list of `usage.qualified_name` strings
   - Skips templates (`is_template=True`) and usages with no `owning_part_def_qn`

3. **Lines 319-351**: For each `agg_expr` in `hierarchy_data.aggregation_expressions`:

   **Strategy 1 (Lines 323-326)**: Direct match
   - Look up `virtual_qns_by_partdef[agg_expr.owning_part_qn]`
   - For each QN, extract parent path via `qn.rsplit("__", 1)[0]`
   - Add parent path to `instance_paths` set

   **Strategy 2 (Lines 332-345)**: Child-walk (BF-6 fix)
   - Only runs if Strategy 1 found NOTHING (`if not instance_paths`)
   - Builds `children` set: lowercase `part_usage_name` from multiplicities where `owning_part_def_qn == agg_expr.owning_part_qn`
   - Searches ALL virtual CalcUsage QNs (across ALL PartDefs)
   - For each QN, splits on `__` and checks if any segment matches a child name
   - If match found at segment index `i > 0`, constructs parent path as `"__".join(segments[:i])`

4. **Lines 348-352**: For each found instance_path, create `ScopedAggregationData`

#### Branching Conditions for Strategy 2

| Step | Condition | Effect |
|------|-----------|--------|
| Line 332 | `if not instance_paths` | Strategy 2 ONLY runs if Strategy 1 found nothing |
| Line 333-336 | Build children from multiplicities | Only multiplicities owned by `agg_expr.owning_part_qn` |
| Line 337 | `if children` | Skip if PartDef has no multiplicity children |
| Lines 339-345 | Nested loop over ALL virtual QNs | O(N*M) search |
| Line 343 | `if seg.lower() in children and i > 0` | Case-insensitive match, must not be first segment |

#### CRITICAL ASSUMPTION GAP: Strategy 2 name matching

Strategy 2 matches CalcUsage QN segments against child PartUsage names from multiplicities. This is the BF-6 fix for handling cases where the PartDef name differs from the PartUsage name (e.g., `SiteInfrastructure` typed as `site_infra`).

**The mechanism**: If a SysML model has:
```
part def SiteInfrastructure { ... }
part solar_battery_plant : Solar_Battery_Plant {
    part site_infra : SiteInfrastructure [1];
}
```
Then the CalcUsage QNs for calculations INSIDE `SiteInfrastructure` would contain `site_infra` as a segment. The multiplicity children of `SiteInfrastructure` would include its own child usage names (e.g., `transformer`). Strategy 2 searches QN segments for those child names.

**Failure mode**: Strategy 2 searches for child PartUsage names of the owning PartDef in the QN segments. But the QN segments come from the design instance tree, not the library definition tree. If:
- The aggregation is on `Lib__Solar_Array` (owning_part_qn)
- Solar_Array has children `pv_module` and `inverter` (from multiplicities)
- But in the design tree, the usage is named differently or has a renaming redefinition

Then the segment matching would fail. The code uses `seg.lower() in children` which is case-insensitive but requires exact substring match.

**Specific "site_infra" vs "site_infrastructure" scenario**: If `agg_expr.owning_part_qn` is for a PartDef whose child multiplicities have `part_usage_name = "site_infra"`, and the CalcUsage QN segments contain `"site_infra"`, it matches. But if the PartDef name is `SiteInfrastructure` while the usage name is `site_infra`, Strategy 1 would fail (because `owning_part_def_qn` on the CalcUsage would be `SiteInfrastructure`'s QN, not matching the aggregation's `owning_part_qn` which might be the parent assembly). Strategy 2 would then look for multiplicity children of the parent assembly and try to match them. If the child of the parent assembly is `site_infra` (lowercase from multiplicity), the segment match works.

**The gap**: Strategy 2 ONLY runs if Strategy 1 found nothing. If Strategy 1 partially matches (finds SOME instance paths but misses others), Strategy 2 never runs, and some instances are silently dropped.

---

## Algorithm 3: Backtracker Aggregation Index

### File
- `/home/reid/1cfe/sysml-codegen/src/sysml_codegen/analysis/dependency_backtracker.py` lines 157-197

### 3.1 Index Construction (Lines 157-197)

#### Input Contract
- `aggregation_data`: `list[ScopedAggregationData]` (from Step 4.7)

#### Index Keys Built (per aggregation)

For each `agg` in `aggregation_data`:

```python
channel = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
# channel = f"{agg.module_eqn}__{agg.expression.attribute_name}"
# e.g., "solar_battery_plant__solar_array__capital_cost__capital_cost"

instance_parts = agg.instance_path.split("__")
part_usage_name = instance_parts[-1]  # e.g., "solar_array"
```

| Key Pattern | Example Key | Line |
|-------------|-------------|------|
| Key 1: `part_usage_name.attribute_name` | `"solar_array.capital_cost"` | 173-175 |
| Key 2: bare `attribute_name` (if not already present) | `"capital_cost"` | 178-181 |
| Key 3: full instance path dotted | `"solar_battery_plant.solar_array.capital_cost"` | 184-187 |
| BF-7 Key 4: `part_usage_name.alias_name` | `"solar_array.total_capex"` | 191-193 |
| BF-7 Key 5: bare alias (if not already present) | `"total_capex"` | 194-195 |
| BF-7 Key 6: full instance path dotted alias | `"solar_battery_plant.solar_array.total_capex"` | 196-197 |

All keys map to the SAME `channel` value.

### 3.2 Index Querying During Binding Resolution (Lines 471-498)

#### Resolution Cascade

When a CalcUsage binding has `source_path` (e.g., `"solar_array.total_capex"`):

1. **Line 472-473**: Direct lookup: `_aggregation_output_index.get(binding.source_path)`
2. **Lines 475-477**: If None and has ".": try bare name: `binding.source_path.split(".")[-1]`
3. **Lines 478-486**: If None and has "::": BF-7 sanitize: extract last two `::` segments, sanitize, build dotted format, look up

If any lookup succeeds, the binding is resolved as `MODULE_OUTPUT` with the channel name from the index.

### 3.3 Why "total_capex" succeeds but other names might fail

#### Scenario: Binding source_path = "Solar_Battery_Plant::total_capex"

Resolution cascade:
1. Direct lookup for `"Solar_Battery_Plant::total_capex"` -- MISS (index keys don't use `::`).
2. Has `.`? No. Skip.
3. Has `::`? Yes. Split: `parts = ["Solar_Battery_Plant", "total_capex"]`. `sanitized = sanitize_name("total_capex").lower() = "total_capex"`. `dotted = "total_capex.total_capex"`. Lookup -- likely MISS (this produces a nonsensical key).

Wait -- re-reading lines 479-486 more carefully:
```python
parts = binding.source_path.split("::")
if len(parts) >= 2:
    sanitized = sanitize_name(parts[-2]).lower()
    dotted = f"{sanitized}.{parts[-1]}"
    agg_channel = self._aggregation_output_index.get(dotted)
```

For `"Solar_Battery_Plant::total_capex"`:
- `parts = ["Solar_Battery_Plant", "total_capex"]`
- `sanitized = sanitize_name("Solar_Battery_Plant").lower() = "solar_battery_plant"`
- `dotted = "solar_battery_plant.total_capex"`

This matches Key 6 (full instance path dotted alias) IF the instance_path is `"solar_battery_plant"`. But Key 6 is `".".join(instance_parts + [alias_name])`. If `instance_parts = ["solar_battery_plant"]`, then Key 6 = `"solar_battery_plant.total_capex"`. **This matches!**

#### Scenario: Binding source_path = "solar_array.capital_cost" vs index for "capital_cost"

1. Direct lookup for `"solar_array.capital_cost"` -- matches Key 1 (`part_usage_name.attribute_name`). **SUCCESS**.

#### CRITICAL ASSUMPTION GAP: Key 2 (bare attribute_name) is first-writer-wins

Line 178: `if agg.expression.attribute_name not in self._aggregation_output_index`. If two different aggregations both have `attribute_name = "capital_cost"` (e.g., Solar_Array.capital_cost AND Battery_System.capital_cost), only the FIRST one gets the bare "capital_cost" key. The second one loses. This means a bare-name binding resolution for "capital_cost" will always resolve to whichever aggregation was processed first.

This is a **race condition** based on iteration order of `aggregation_data`. The order comes from `_scope_aggregation_expressions()` which iterates `hierarchy_data.aggregation_expressions` and sorts `instance_paths` (line 348). This makes the order deterministic but potentially wrong for the second+ aggregation with the same attribute name.

Similarly for BF-7 alias bare keys (line 194): `if alias_name not in self._aggregation_output_index` -- first-writer-wins.

---

## Algorithm 4: Graph Builder Aggregation Module

### File
- `/home/reid/1cfe/sysml-codegen/src/sysml_codegen/resolution/graph_builder.py` lines 936-1136

### 4.1 `_build_aggregation_module()` (Lines 936-1136)

#### Input Contract
- `agg`: `ScopedAggregationData` (one design-instance-scoped aggregation)
- `redefinitions`: `list[RedefinitionData]` (all PartDef-level redefinitions)
- `output_catalog`: full output catalog (from Steps 2, 2.5, 2.7)
- `entry_points`: mutable dict of `EntryPoint` objects (new EPs may be added)
- `group_deriver`: for classifying new entry points

#### Processing Steps

**Naming (Lines 957-960)**:
```python
module_name = get_module_name(agg.module_eqn)  # lowercase EQN
module_type = derive_module_type(f"{agg.expression.owning_part_qn}::{agg.expression.attribute_name}")
```

**SumTerm processing (Lines 970-1034)**:
For each `term` in `agg.expression.sum_terms`:
1. Build `symbolic_ref = f"{term.part_usage_name}.{term.attribute_name}"` (e.g., `"pv_module.capital_cost"`)
2. Build `param_name = f"{term.part_usage_name}_{term.attribute_name}"` (e.g., `"pv_module_capital_cost"`)
3. Call `_resolve_aggregation_input_channel(symbolic_ref, ...)` to find upstream channel
4. If channel found: create `InputSource(source_type="module_output", producer_channel=channel)`
5. If NOT found: mark `compilability = MANUAL_REQUIRED`, create entry_point fallback
6. Create `ModuleInput` with `param_name` and source
7. Register in `ref_to_inputs` dict for expression compilation
8. If `term.multiplicity_attr` is set: create additional multiplicity entry point input

**SingletonTerm processing (Lines 1037-1087)**:
For each `s_term` in `agg.expression.singleton_terms`:
1. Build `param_name = s_term.source_path.replace(".", "_")`
2. If source_path has ".": attempt direct channel build, then fall back to `_resolve_aggregation_input_channel`
3. If unresolvable: entry point fallback + MANUAL_REQUIRED

**LocalTerm processing (Lines 1090-1110)**:
For each `l_term` in `agg.expression.local_terms`:
1. Always creates an entry point (LocalTerms are PartDef-local attributes)
2. Entry point QN: `f"{agg.module_eqn}__{l_term.attribute_name}"`

**Expression compilation (Lines 1112-1118)**:
- Only if no unsupported nodes and transformed_expression exists
- Replace each symbolic ref with `inputs.X` form using `ref_to_inputs` dict
- Sort refs by length descending (longest first) to avoid partial replacement

**Output (Lines 1121-1136)**:
- Single output channel: `get_channel_name(agg.module_eqn, agg.expression.attribute_name)`
- Returns `PipelineModule` with `is_aggregation=True`

### 4.2 `_resolve_aggregation_input_channel()` (Lines 856-933)

#### Resolution Chain
1. **Line 888**: If no "." in symbolic_ref, return None (LocalTerm)
2. **Line 891**: Parse `part_usage, attr = symbolic_ref.rsplit(".", 1)`
3. **Lines 903-910**: Find CHAIN redefinition: scan ALL redefinitions for one where:
   - `redef.redefinition_type == CHAIN`
   - `redef.attribute_name == attr`
   - `sanitize_name(redef.owning_part_qn.split("__")[-1]).lower() == part_usage.lower()`
4. **Lines 912-926**: If CHAIN found and has source_path:
   - Parse source_path as `"calc_usage.output"`, build channel, verify in catalog
   - If not found, recurse with cycle guard
5. **Lines 929-931**: Fallback: lookup `"part_usage.attr"` in output_catalog

#### ASSUMPTION GAP: CHAIN redefinition matching is case-insensitive and suffix-based

Line 907-908: The match extracts the last `__` segment of the redefinition's owning QN and compares case-insensitively with `part_usage`. This assumes:
1. The redefinition's owning QN uses `__` separators (not `::`)
2. The last segment corresponds to the part usage name

If the PartDef QN is `Lib__PV_Module`, then `parts[-1] = "PV_Module"`, `sanitize_name("PV_Module").lower() = "pv_module"`. If `part_usage = "pv_module"`, this matches. But if the PartDef is named differently from the usage (e.g., `Lib__PhotovoltaicModule` used as `pv_module`), this would NOT match.

### 4.3 What happens if sum_terms is empty?

If `agg.expression.sum_terms` is an empty list, the for loop at line 970 simply does not execute. No SumTerm-based inputs are created. The module may still have inputs from SingletonTerms or LocalTerms. If ALL term lists are empty (no sum_terms, no singleton_terms, no local_terms), the module has zero inputs. This would be a valid scenario (constant aggregation) but the module would just return a constant output. The E2E test `test_aggregation_modules_in_graph` at line 226 explicitly checks that cost-attribute aggregation modules (excluding idiot_index) have non-empty inputs.

---

## Cross-Algorithm Sequencing

### File
- `/home/reid/1cfe/sysml-codegen/src/sysml_codegen/generation/initialization.py` lines 358-515

### Pipeline Execution Order

```
Step 1:   Load models
Step 2:   Extract calc definitions
Step 3:   Extract calc usages
Step 3.5: Extract hierarchy data + rewrite virtual bindings
Step 4:   Extract design attributes
Step 4.5: Extract computed attributes (removes FORMULAs from design attrs)
Step 4.7: _scope_aggregation_expressions()  --> list[ScopedAggregationData]
Step 5:   Create ParameterGroupDeriver (uses filtered design attrs)
Step 6:   Create backtracker (receives scoped_agg_data) + run
          --> builds _aggregation_output_index from scoped_agg_data
          --> resolves bindings (uses index for aggregation output wiring)
Step 6.5: Compile expressions
Step 7:   build_computation_graph()
          --> Step 2: build output catalog
          --> Step 2.7: extend catalog with aggregation outputs
          --> Step 6: build CalcUsage pipeline modules (uses binding_resolutions)
          --> Step 6.7: _build_aggregation_module() for each agg
          --> Step 7: _unified_topological_sort()
          --> Step 8: _validate_channel_references()
```

### Critical Data Flow

```
hierarchy_resolver.extract_hierarchy_data()
    --> HierarchyExtractionResult
        .aggregation_expressions: list[AggregationExpressionData]
        .redefinitions: list[RedefinitionData]
        .multiplicities: list[MultiplicityData]

_scope_aggregation_expressions(hierarchy_data, calc_usages)
    --> list[ScopedAggregationData]
        Each wraps an AggregationExpressionData + instance_path

DependencyBacktracker.__init__(aggregation_data=scoped_agg_data)
    --> builds _aggregation_output_index

DependencyBacktracker.find_required_modules()
    --> BacktrackingResult
        .binding_resolutions: includes MODULE_OUTPUT entries for agg channels

build_computation_graph(aggregation_data=scoped_agg_data, hierarchy_redefinitions=...)
    --> _extend_output_catalog_with_aggregation() populates catalog
    --> _build_aggregation_module() creates PipelineModule per agg
    --> _unified_topological_sort() orders everything
```

### Sequencing Invariant

The backtracker (Step 6) receives `scoped_agg_data` and builds its index. It then resolves bindings during `find_required_modules()`. The graph builder (Step 7) also receives `scoped_agg_data` and uses it to build aggregation modules.

**Both Step 6 and Step 7 must agree on channel names.** The backtracker builds channels via:
```python
channel = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
```

The graph builder's `_extend_output_catalog_with_aggregation` (line 847) builds:
```python
channel_name = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
```

And `_build_aggregation_module` (line 1124) creates the output:
```python
channel_name = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
```

All three use the same function with the same inputs. **This invariant holds.**

However, the backtracker and graph builder use different mechanisms to match binding sources to channels:
- Backtracker: multi-key index with fallback strategies (dotted, bare, `::` sanitized)
- Graph builder: `_resolve_aggregation_input_channel()` with CHAIN redefinition resolution

These two mechanisms could produce different results for the same input, leading to:
- Backtracker resolves a binding as MODULE_OUTPUT (found in index)
- Graph builder creates an aggregation module whose input does NOT wire to that channel

Or vice versa. This would cause `_validate_channel_references()` to fail.

---

## Specific Question Answers

### Question 1: _walk_aggregation_ast sum() handling of Evaluation wrapper

When `_walk_aggregation_ast` encounters a `sum()` InvocationExpression at line 351:

1. It calls `_unwrap_invocation(operands[0])` (line 352)
2. If `operands[0]` is itself an InvocationExpression with `function.name='Evaluation'`:
   - `_unwrap_invocation` at depth 0: node has `function.name`, recurses on `operands[0]` at depth 1
   - At depth 1: if the Evaluation's operand is a FeatureChainExpression, it has no `function.name`, returns it
3. The result is the FeatureChainExpression

**Yes, this correctly handles the Evaluation wrapper.** The key insight is that `_unwrap_invocation` does NOT filter by function name -- it recursively peels ANY InvocationExpression. This is correct for unwrapping, though it also means it would unwrap legitimate nested function calls (this is acceptable because `_walk_aggregation_ast` only calls it on operands of known wrappers).

### Question 2: Strategy 1 and Strategy 2 in _scope_aggregation_expressions

**Strategy 1** (line 323-326): Direct match. Looks up `agg_expr.owning_part_qn` in the `virtual_qns_by_partdef` index. If virtual CalcUsages exist that are owned by the same PartDef as the aggregation, extract their parent paths.

**Strategy 2** (lines 332-345): Child-walk. Only runs when Strategy 1 found nothing. Uses multiplicity data to find child PartUsage names of the aggregation's PartDef, then searches ALL virtual CalcUsage QN segments for those child names.

**How Strategy 2 can fail for "site_infra" vs "site_infrastructure":**

Strategy 2 matches `seg.lower()` against `children` (a set of lowercase `part_usage_name` values from multiplicities). If the multiplicity record has `part_usage_name = "transformer"` (a child of SiteInfrastructure), Strategy 2 searches for QN segments containing "transformer". If the CalcUsage QN is `...solar_battery_plant__site_infra__transformer__some_calc`, segment "transformer" matches.

The issue is NOT about "site_infra" vs "site_infrastructure" directly -- Strategy 2 doesn't compare the aggregation's PartDef name against the usage name. It compares the CHILDREN of the PartDef against QN segments. The failure would occur if:

1. The PartDef has no multiplicity children (all singletons) -- then `children` is empty, `if children:` fails, Strategy 2 is skipped entirely
2. The PartDef's child names don't appear as QN segments (naming mismatch)
3. Strategy 1 partially succeeded (found some but not all paths) -- Strategy 2 doesn't run

### Question 3: _aggregation_output_index key formats and "total_capex" vs "capital_cost"

The index supports 6 key patterns per aggregation (3 base + 3 alias). See Algorithm 3 section 3.1 above.

**Why a binding to "total_capex" would match:** If `total_capex` is registered as an alias on the `capital_cost` aggregation, then Keys 4/5/6 provide the mapping. The bare key "total_capex" (Key 5) would directly match a binding with `source_path="total_capex"`.

**Why a binding to "total_capex" could FAIL to match:**
1. If the alias was never detected during extraction (BF-7 alias detection at lines 521-528 didn't find a matching CHAIN redef)
2. If the bare key was already claimed by another aggregation (first-writer-wins)
3. If the binding source_path uses a different format (e.g., `"Plant::total_capex"`) that doesn't match any of the 6 key patterns exactly

**Why "capital_cost" could fail:** If two aggregations both have `attribute_name="capital_cost"`, the bare key "capital_cost" (Key 2) points to whichever was indexed first. A binding to `"solar_array.capital_cost"` would need to match Key 1 exactly. If the part_usage_name doesn't match (e.g., `instance_parts[-1]` is `"solar_array"` but the binding says `"Solar_Array"`), case sensitivity matters: the index stores exact `instance_parts[-1]` which comes from `agg.instance_path.split("__")[-1]`. The binding source path comes from the AST. If one is lowercase and the other has mixed case, the lookup fails.

### Question 4: SumTerm/SingletonTerm/LocalTerm to ModuleInput translation

| Term Type | ModuleInput.param_name | Source Resolution | Entry Point? |
|-----------|----------------------|-------------------|--------------|
| SumTerm | `"{part_usage}_{attr}"` | `_resolve_aggregation_input_channel(symbolic_ref)` | Only if unresolvable (+ multiplicity_attr is always an EP) |
| SingletonTerm | `source_path.replace(".", "_")` | Direct channel build or `_resolve_aggregation_input_channel` | Only if unresolvable |
| LocalTerm | `l_term.attribute_name` | Always entry point | Always |

If `sum_terms` is empty: No SumTerm inputs are created. No multiplicity entry points. The module still gets inputs from SingletonTerms and LocalTerms. If all lists are empty, the module has zero inputs and its `compiled_expression` would be the `transformed_expression` with zero substitutions. The module would be valid but functionally a constant.

### Question 5: Backtracker-to-GraphBuilder sequencing for aggregation outputs

**Step 6 (Backtracker):**
1. Constructor receives `scoped_agg_data` (line 441)
2. Builds `_aggregation_output_index` with 6 key patterns per aggregation (lines 159-197)
3. During `find_required_modules()`, when processing CalcUsage bindings:
   - Checks `_aggregation_output_index` at lines 472-486
   - If match: creates `BindingResolution(type=MODULE_OUTPUT, qualified_name=agg_channel)`
   - This means the CalcUsage input will be wired to the aggregation module's output

**Step 7 (Graph Builder):**
1. `_extend_output_catalog_with_aggregation()` at line 115 adds agg outputs to catalog
2. `_build_pipeline_module()` at line 154 uses `binding_resolutions` from backtracker
   - For aggregation-resolved bindings: source_type="module_output", producer_channel=agg_channel
3. `_build_aggregation_module()` at line 184 creates the aggregation PipelineModule with the matching output channel

The key invariant: the aggregation module's output channel (created in Step 7 at line 1124) must match the channel stored in `_aggregation_output_index` (created in Step 6 at line 161-163). Both use `get_channel_name(agg.module_eqn, agg.expression.attribute_name)`. **This invariant holds as long as the same ScopedAggregationData object is used in both steps** -- which it is, since both receive the same `scoped_agg_data` list.

---

## Invariant Violation Summary

### Confirmed Invariants (Hold)

| ID | Invariant | Where Verified |
|----|-----------|----------------|
| I-1 | Backtracker and graph builder use same channel formula | Both call `get_channel_name(agg.module_eqn, ...)` |
| I-2 | `_unwrap_invocation` correctly peels Evaluation wrappers | Depth-bounded recursion on any InvocationExpression |
| I-3 | ScopedAggregationData.module_eqn is deterministic | Derived from `instance_path + "__" + attribute_name` |
| I-4 | Aggregation modules always have exactly one output | Lines 1121-1125 in graph_builder.py |

### Potential Violations (Assumption Gaps)

| ID | Gap | Risk | Affected Tests |
|----|-----|------|----------------|
| G-1 | `_unwrap_invocation` max depth of 3 may be insufficient for deeply nested ASTs | Low -- real SysML unlikely to have 4+ wrapper layers | BF-1 tests |
| G-2 | Strategy 2 in `_scope_aggregation_expressions` only runs if Strategy 1 finds NOTHING | Medium -- partial matches silence Strategy 2 | BF-6 test (`test_bf6_all_assemblies_scoped`) |
| G-3 | Bare attribute_name keys in `_aggregation_output_index` are first-writer-wins | Medium -- multiple aggregations with same attr name | BF-7 test (`test_bf7_total_capex_wired_to_module_output`) |
| G-4 | `_resolve_aggregation_input_channel` CHAIN matching compares sanitized last-segment of owning QN against part_usage_name | Medium -- breaks if PartDef name diverges from PartUsage name | `test_aggregation_modules_in_graph` |
| G-5 | BF-7 alias detection uses `endswith()` which could match substring false positives | Low -- requires coincidental suffix matching | BF-7 tests |
| G-6 | `_scope_aggregation_expressions` Strategy 2 child-walk is O(N*M) | Low -- only runs if Strategy 1 fails | Performance only |
| G-7 | Multiplicity data must be co-located with the aggregation PartDef for sum() to resolve | High -- cross-scope sum() references produce SumTerm with null multiplicity | BF-1/3 tests |
| G-8 | Expression compilation sort-by-length-descending (line 1116) could still produce incorrect replacements if one symbolic ref is a suffix of another | Low -- would require `"a.b"` and `"c.a.b"` in same expression | BF-2 stencil tests |
| G-9 | `extract_feature_chain_name` assumes `operands[0]` + `target_feature.name` structure | Medium -- real AST may vary per SysIDE version | All extraction tests |

### Root Causes of Likely E2E Failures

Based on the 4 E2E test classes in `test_hierarchy_e2e.py`:

1. **`test_bf1_no_unsupported_nodes`**: Could fail if real AST has unexpected InvocationExpression structures beyond depth 3 or with operand patterns not matching the `function.name` check.

2. **`test_bf6_all_assemblies_scoped`**: Could fail if Strategy 1 partially succeeds for some assemblies (preventing Strategy 2 from running for the remainder), or if a PartDef has zero multiplicity children (Strategy 2's `if children:` guard at line 337 skips it).

3. **`test_bf7_total_capex_wired_to_module_output`**: Could fail if (a) alias detection at lines 521-528 doesn't find the CHAIN sibling, (b) the bare key is already claimed by another aggregation, or (c) the binding source_path format doesn't match any of the 6 index key patterns.

4. **`test_bf3_aggregation_wrappers_have_inputs`**: Could fail if `_resolve_aggregation_input_channel` fails for all SumTerms/SingletonTerms (creating entry point fallbacks instead of module_output wiring), which would still produce inputs but with `source_type="entry_point"` rather than `"module_output"`. The test checks for `Field(` declarations in wrapper files, which exist regardless of wiring type, so this test should pass if any inputs exist at all. More likely to fail if the entire aggregation expression has zero terms.
