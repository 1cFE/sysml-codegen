# 12 - Virtual Binding Rewriting

## What Are "Virtual" Calc Usages?

A SysML library PartDef (e.g., `Solar_Array`) owns calculation usages that reference
template-level attributes. When a design PartDef (e.g., `SolarBatteryDesign`) instantiates
that library part via a PartUsage, the pipeline creates **virtual** copies of those calc
usages scoped to the design instance. Each virtual [`CalcUsageData`](09-data-models.md#extraction-models)
carries:

- `is_template = False` (the original library copy has `is_template = True`)
- `owning_part_def_qn` pointing back to the library PartDef
- `qualified_name` scoped to the design instance
  (e.g., `SolarBatteryDesign__solar_array__calc_cost`)

Template copies (`is_template = True`) are excluded from the pipeline entirely. Only
virtual (non-template) copies become pipeline modules.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-VBR-01 | Override index SHALL be keyed by `(full_parent_path, leaf_attribute_name)` | `override_index: dict[tuple[str, str], RedefinitionData]` at line 273 |
| REQ-VBR-02 | Deep-path overrides SHALL join intermediate `target_path` segments with `__` to form `full_parent` | `f"{owning_part_qn}__{intermediate}"` at line 279 |
| REQ-VBR-03 | LITERAL override SHALL set `binding_type=LITERAL`, copy `literal_value`, clear `source_path=None` | Three mutations at lines 319-321 |
| REQ-VBR-04 | CHAIN override SHALL replace `source_path` with the redefinition's `source_path` | `binding.source_path = matched.source_path` at line 324 |
| REQ-VBR-05 | Template copies (`is_template=True`) SHALL be skipped during rewriting | `if usage.is_template: continue` at line 291 |
| REQ-VBR-06 | Bindings already LITERAL or with no `source_path` SHALL be skipped (no double-rewrite) | Guard at lines 300-303 |
| REQ-VBR-07 | Rewriting SHALL complete BEFORE any downstream processing (Step 3.5 ordering) | Called at line 736 in `build_pipeline_context()`, before Steps 4-7 |

## Why Binding Rewriting Is Needed

Template bindings reference template-level attributes using SysML qualified names:

```
source_path = "Lib::Solar_Array::wattage"
```

But at the design level, a `:>>` redefinition may override that attribute:

```sysml
part solar_array : Solar_Array {
    :>> wattage = 400.0;              // LITERAL override
    :>> efficiency = tracker.eta;     // CHAIN override
}
```

Without rewriting, the virtual CalcUsage would still look up `Lib::Solar_Array::wattage`,
missing the design-specific value `400.0`. The rewrite step patches each virtual
CalcUsage's [`BindingInfo`](09-data-models.md#extraction-models) objects **in place** so
downstream steps ([backtracking](11-analysis-backtracker.md),
[graph building](07-graph-assembly.md)) see the design-intent values.

## Implementation: `_rewrite_virtual_bindings()`

**File:** `src/sysml_codegen/generation/initialization.py`, lines 260-327.

### Phase 1 -- Build the Override Index

The function iterates `hierarchy_data.design_overrides` (a `list[`[`RedefinitionData`](09-data-models.md#extraction-models)`]`)
and builds a lookup dict:

```python
override_index: dict[tuple[str, str], RedefinitionData]
```

The key is `(full_target_parent_path, leaf_attribute_name)`.

**Deep-path overrides** (`redef.is_deep_path = True`, e.g., `:>> pv_module.wattage = 400`):
- `target_path = ["pv_module", "wattage"]`
- Intermediate segments joined: `"pv_module"` (all but last)
- `full_parent = f"{owning_part_qn}__pv_module"`
- `leaf_attr = "wattage"`

**Flat overrides** (`is_deep_path = False`, e.g., `:>> efficiency = 0.22`):
- `full_parent = owning_part_qn`
- `leaf_attr = attribute_name`

If the index is empty, the function returns `0` immediately.

### Phase 2 -- Match and Rewrite Bindings

For each `CalcUsageData` where `is_template = False`:

1. Extract `parent_path` from `usage.qualified_name.rsplit("__", 1)[0]`
2. Skip bindings that are already `LITERAL` or have no `source_path`
3. Extract the leaf name from `binding.source_path`:
   - SysML QN (`"::"` separator): `"Lib::Solar_Array::wattage"` -> leaf `"wattage"`
   - Dotted path (`"."` separator): `"tracker.eta"` -> leaf `"eta"`
   - Bare name (fallback): `"wattage"` -> leaf `"wattage"`
4. Lookup `(parent_path, leaf)` in the override index

### The Three Mutation Cases

| Case | Condition | Mutations | Downstream effect |
|------|-----------|-----------|-------------------|
| **LITERAL override** | `matched.redefinition_type == RedefinitionType.LITERAL` | `binding_type = LITERAL`, `literal_value = matched.literal_value`, `source_path = None` | Becomes [DESIGN_ATTRIBUTE entry point](06-entry-point-classifier.md) |
| **CHAIN override** | `matched.redefinition_type == RedefinitionType.CHAIN` | `source_path = matched.source_path` (e.g., `"tracker.eta"`) | Resolved via [OutputRegistry](10-output-registry.md) as MODULE_OUTPUT |
| **No match** | Key not in override index | Binding unchanged | Original template binding used |

## Concrete Before/After Example

**Setup:** Library PartDef `Lib__Solar_Array` owns `calc_cost` with two inputs.
Design PartDef `SolarBatteryDesign` instantiates it as `solar_array` with overrides:

```sysml
part solar_array : Solar_Array {
    :>> wattage = 400.0;
    :>> efficiency = tracker.eta;
}
```

This produces two `design_overrides`:
- `RedefinitionData(owning_part_qn="SolarBatteryDesign", target_path=["solar_array","wattage"], is_deep_path=True, redefinition_type=LITERAL, literal_value=400.0)`
- `RedefinitionData(owning_part_qn="SolarBatteryDesign", target_path=["solar_array","efficiency"], is_deep_path=True, redefinition_type=CHAIN, source_path="tracker.eta")`

**Override index after Phase 1:**
```
("SolarBatteryDesign__solar_array", "wattage")   -> LITERAL(400.0)
("SolarBatteryDesign__solar_array", "efficiency") -> CHAIN("tracker.eta")
```

**Virtual CalcUsage before rewrite:**
```python
CalcUsageData(
    qualified_name="SolarBatteryDesign__solar_array__calc_cost",
    is_template=False,
    owning_part_def_qn="Lib__Solar_Array",
    bindings=[
        BindingInfo(param_name="wattage",   source_path="Lib::Solar_Array::wattage",
                    binding_type=BindingType.REFERENCE, literal_value=None),
        BindingInfo(param_name="efficiency", source_path="Lib::Solar_Array::efficiency",
                    binding_type=BindingType.REFERENCE, literal_value=None),
    ],
)
```

**After rewrite (in-place mutation):**
```python
CalcUsageData(
    qualified_name="SolarBatteryDesign__solar_array__calc_cost",
    is_template=False,
    owning_part_def_qn="Lib__Solar_Array",
    bindings=[
        BindingInfo(param_name="wattage",   source_path=None,
                    binding_type=BindingType.LITERAL, literal_value=400.0),
        BindingInfo(param_name="efficiency", source_path="tracker.eta",
                    binding_type=BindingType.REFERENCE, literal_value=None),
    ],
)
```

The `wattage` binding flipped from REFERENCE to LITERAL with value `400.0`.
The `efficiency` binding kept its type but `source_path` was rewritten to `"tracker.eta"`.

## Ordering Constraint: In-Place Mutation Before Downstream Steps

`_rewrite_virtual_bindings()` is called inside `_extract_hierarchy_and_rewrite_bindings()`
at **Step 3.5** of [`build_pipeline_context()`](00-pipeline-overview.md), which runs **before**:

- Step 4 -- `extract_design_attributes()` ([parameter group derivation](17-parameter-group-deriver.md))
- Step 5 -- `ParameterGroupDeriver` construction
- Step 5.5 -- [`build_output_registry()`](10-output-registry.md) (channel registration)
- Step 6 -- [`DependencyBacktracker.find_required_modules()`](11-analysis-backtracker.md) (dependency analysis)
- Step 7 -- [`build_computation_graph()`](07-graph-assembly.md) (graph assembly)

The mutations are in-place on the shared `calc_usages` list, so every downstream
consumer automatically sees the rewritten bindings. No return value carries the
modified list -- the same list object is passed through the entire pipeline.

## Key Data Model References

All models fully defined in [09-data-models](09-data-models.md).

| Model | Key Fields Used Here |
|-------|---------------------|
| [`CalcUsageData`](09-data-models.md#extraction-models) | `.is_template`, `.owning_part_def_qn`, `.qualified_name`, `.bindings` |
| [`BindingInfo`](09-data-models.md#extraction-models) | `.param_name`, `.source_path`, `.binding_type`, `.literal_value` |
| [`RedefinitionData`](09-data-models.md#extraction-models) | `.owning_part_qn`, `.attribute_name`, `.redefinition_type`, `.target_path`, `.is_deep_path`, `.literal_value`, `.source_path` |
| [`RedefinitionType`](09-data-models.md#extraction-models) | `LITERAL`, `CHAIN`, `EXPRESSION` |
| [`BindingType`](09-data-models.md#extraction-models) | `CHAIN`, `REFERENCE`, `LITERAL`, `EXPRESSION`, `UNBOUND` |
| [`HierarchyExtractionResult`](09-data-models.md#extraction-models) | `.design_overrides` (list of `RedefinitionData`) |

## Related Documents

- **Upstream**: [01-extraction](01-extraction.md) — produces `CalcUsageData` and `RedefinitionData`, [02-orchestration](02-orchestration.md) — calls rewriting at Step 3.5
- **Architecture**: [00-pipeline-overview](00-pipeline-overview.md) — Step 3.5 placement in pipeline, [24-dual-resolution-architecture](24-dual-resolution-architecture.md) — why rewriting feeds both resolution paths
- **Downstream**: [11-analysis-backtracker](11-analysis-backtracker.md) — DFS sees rewritten bindings, [10-output-registry](10-output-registry.md) — CHAIN rewrites become registry lookups, [13-aggregation-scoping](13-aggregation-scoping.md) — scoped aggregations also use rewritten data
- **Cross-cutting**: [06-entry-point-classifier](06-entry-point-classifier.md) — LITERAL rewrites become entry points, [18-literal-value-propagation](18-literal-value-propagation.md) — literal defaults for entry points
- **Data models**: [09-data-models](09-data-models.md) — `CalcUsageData`, `BindingInfo`, `RedefinitionData`
