# 13 - Aggregation Scoping

## The Problem

SysML PartDefinitions define aggregation expressions at the **type level**: a `Solar_Array` PartDef
declares `capital_cost :>> sum(pv_module.capital_cost) * module_count + bos_cost`. This is abstract —
it says "any Solar_Array instance computes capital_cost this way." But the pipeline operates on
**concrete design instances** like `Design__plant__solar_array`. The aggregation scoping subsystem
bridges this gap: it discovers which design instances correspond to each PartDef and stamps out
one scoped aggregation module per instance.

Three functions in `orchestration/pipeline_builder.py` implement this, called during
[Step 3.5](00-pipeline-overview.md) of `build_pipeline_context()`:

1. `find_instance_paths_for_partdef()` — discovers design instance paths
2. `_scope_aggregation_expressions()` — produces [`ScopedAggregationData`](09-data-models.md#extraction-models) per instance
3. `_build_chain_aliases()` — produces [`ChannelAlias`](09-data-models.md#core-models) objects for `:>>` CHAIN redefinitions

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-AS-01 | Each PartDef-level aggregation SHALL produce one `ScopedAggregationData` per design instance | One-to-many expansion in `_scope_aggregation_expressions()` at line 456 |
| REQ-AS-02 | Instance discovery SHALL try direct match (Strategy 1) BEFORE child-walk fallback (Strategy 2) | Strategy 1 at line 366, Strategy 2 guarded by `if not instance_paths` at line 372 |
| REQ-AS-03 | Instance paths SHALL be converted from `__`-separated to dotted format with design prefix stripped | Prefix stripping + dot join at lines 388-396 |
| REQ-AS-04 | CHAIN aliases SHALL only be produced for non-deep-path redefinitions whose `source_path` contains `"."` | Three filters at lines 425-431: `!= CHAIN`, `is_deep_path`, `"." not in source_path` |
| REQ-AS-05 | [Phase 1b](10-output-registry.md) SHALL register a canonical channel for each `ScopedAggregationData` | `registry.register(canonical, keys)` at line 575 |
| REQ-AS-06 | [Phase 2](10-output-registry.md) SHALL resolve `ChannelAlias.canonical_name` in registry before registering alias | `resolved = registry.resolve(alias.canonical_name)` at line 617 |
| REQ-AS-07 | `module_eqn` property SHALL be `"{instance_path}__{attribute_name}"` | Property at line 360 in `data_models.py` |

## Data Models

Full definitions in [09-data-models](09-data-models.md). All models live in
`extraction/data_models.py` unless noted.

**[`AggregationExpressionData`](09-data-models.md#extraction-models)** — PartDef-level aggregation,
decomposed into typed terms. Key fields for scoping:
- `owning_part_qn: str` — e.g., `"SolarBatteryLibrary__Solar_Array"`
- `owning_part_name: str` — human-readable name
- `attribute_name: str` — e.g., `"capital_cost"`
- `sum_terms: list[SumTerm]` — multiplied child sums (used by [module factory](05-module-factory.md))
- `singleton_terms: list[SingletonTerm]` — non-sum child refs
- `local_terms: list[LocalTerm]` — PartDef-local sibling attributes
- `input_channels: list[str]` — all upstream channel references for wiring
- `entry_points: list[str]` — parameters that become [entry points](06-entry-point-classifier.md)
- `aliases: list[str]` — CHAIN redef aliases (e.g., `["total_capex"]`)
- `compilability`, `has_unsupported_nodes` — [expression compiler](14-expression-compiler.md) state

**`SumTerm`** — one `sum()` operand: `part_usage_name`, `attribute_name`, `multiplicity_attr`, `multiplicity_count`.

**`SingletonTerm`** — a non-sum child reference: `source_path` (e.g., `"cost_model.total_cost"`).

**`LocalTerm`** — a PartDef-local sibling attribute: `attribute_name` (e.g., `"misc_hardware_cost"`).

**[`ScopedAggregationData`](09-data-models.md#extraction-models)** — an `AggregationExpressionData` bound to a design instance:
- `expression: AggregationExpressionData` — the PartDef-level data (composition, not inheritance)
- `instance_path: str` — e.g., `"SolarBatteryDesign__solar_battery_plant__solar_array"`
- `module_eqn` property: `"{instance_path}__{attribute_name}"` — the [EQN](15-naming-conventions.md)

**[`ChannelAlias`](09-data-models.md#core-models)** (in `core/models.py`) — maps an alias key to a canonical channel:
- `alias_name: str` — scoped dotted key (e.g., `"solar_battery_plant.solar_array.total_capex"`)
- `canonical_name: str` — dotted target resolving to canonical channel
- `owning_part_qn: str` — PartDef where the alias originates
- `source: Literal["redefinition", "expose_pure", "design_override"]`

## find_instance_paths_for_partdef()

**File:** `src/sysml_codegen/orchestration/pipeline_builder.py`.

Given a PartDef QN, returns dotted, design-prefix-stripped instance paths by scanning virtual
calc usages. Two strategies:

**Strategy 1 (Direct):** Find virtual CalcUsages whose `owning_part_def_qn` matches the target
PartDef. Extract the parent QN (everything before the last `__` segment) from each usage's
`qualified_name`. These are the `__`-separated instance paths.

**Strategy 2 (Child-walk, fallback):** If Strategy 1 finds nothing and `part_usage_names` is
provided, look for CalcUsage QN segments that match known child PartUsage names of the target
PartDef. The segments before the matched child give the parent instance path. This handles
PartDef/PartUsage naming mismatches (BF-6).

Finally, `__`-separated paths are converted to dotted format with the design prefix (segment 0)
stripped. For `"SolarBatteryDesign__solar_battery_plant__solar_array__cost_model"`, this yields
`"solar_battery_plant.solar_array"` (the parent of the calc usage, prefix-stripped).

## _scope_aggregation_expressions()

**File:** `src/sysml_codegen/orchestration/pipeline_builder.py`.

For each `AggregationExpressionData` in `hierarchy_data.aggregation_expressions`:

1. Calls `find_instance_paths_for_partdef()` to get dotted instance paths.
2. Derives the design prefix from the first virtual CalcUsage QN (segment 0, e.g., `"SolarBatteryDesign"`).
3. Reconstructs the `__`-separated `instance_path` by prepending the design prefix.
4. Emits one `ScopedAggregationData(expression=agg_expr, instance_path=underscore_path)` per path.

This is a **one-to-many** expansion: a single PartDef-level aggregation can produce multiple
scoped modules if the PartDef is instantiated more than once in the design.

## _build_chain_aliases()

**File:** `src/sysml_codegen/orchestration/pipeline_builder.py`.

For each `:>>` CHAIN redefinition on a PartDef (filtered: `redefinition_type == CHAIN`,
not `is_deep_path`, and `source_path` contains a dot):

1. Groups qualifying redefinitions by `owning_part_qn`.
2. For each group, calls `find_instance_paths_for_partdef()` to get dotted instance paths.
3. For each `(redef, dotted_path)` pair, emits:
   ```
   ChannelAlias(
       alias_name=f"{dotted_path}.{redef.attribute_name}",
       canonical_name=f"{dotted_path}.{redef.source_path}",
       owning_part_qn=redef.owning_part_qn,
       source="redefinition",
   )
   ```

The filter `"." not in source_path` excludes bare CAS codes like `"CAS220101"` which are
[entry-point](06-entry-point-classifier.md) references, not channel chains.

### Edge case: zero instances found

If both strategies find zero instance paths for a PartDef, the aggregation
expression produces NO `ScopedAggregationData` and NO pipeline module. This is
silent — the only signal is the `logger.info("Scoped 0 aggregation module(s)")`
count. This can happen when:
- The design never instantiates the PartDef that declares the aggregation
- Instance discovery strategies fail to match (e.g., PartDef QN mismatch)

**REQ-AS-08**: The scoping function SHALL log a WARNING (not just info) when an
aggregation expression produces zero scoped modules, identifying the PartDef QN
and attribute name.

## How This Feeds Into the OutputRegistry

The [`build_output_registry()`](10-output-registry.md) function (same file, line 502) consumes
these outputs in its [4-phase registration protocol](10-output-registry.md):

- **Phase 1b:** Each `ScopedAggregationData` registers a canonical channel via
  `get_channel_name(agg.module_eqn, agg.expression.attribute_name)` producing
  a `CanonicalChannel`. Registered with `ScopedKey` in the scoped registry
  ([15-naming-conventions](15-naming-conventions.md), [10-output-registry](10-output-registry.md)).
- **Phase 2:** Each `ChannelAlias` with `source="redefinition"` is resolved — the registry
  looks up `alias.canonical_name`, and if found, registers `alias.alias_name` as an alias
  pointing to the same canonical channel. This is how downstream modules can wire to
  `solar_array.total_capex` instead of the fully-qualified aggregation output channel.

## Concrete Example

**SysML source (library PartDef):**
```sysml
part def Solar_Array {
    attribute total_capex :>> cost_model.total_cost;   // CHAIN redef
    attribute capital_cost = sum(pv_module.capital_cost) * module_count;  // aggregation
}
```

**Design instantiation:**
```sysml
part def SolarBatteryDesign {
    part solar_battery_plant : Solar_Battery_Plant {
        part solar_array : Solar_Array { ... }
    }
}
```

**Step 1: find_instance_paths_for_partdef("SolarBatteryLibrary__Solar_Array", calc_usages)**

A virtual CalcUsage exists with `qualified_name = "SolarBatteryDesign__solar_battery_plant__solar_array__cost_model"` and `owning_part_def_qn = "SolarBatteryLibrary__Solar_Array"`. Strategy 1 extracts parent `"SolarBatteryDesign__solar_battery_plant__solar_array"`, strips the design prefix, and returns `["solar_battery_plant.solar_array"]`.

**Step 2: _scope_aggregation_expressions()**

The `capital_cost` AggregationExpressionData is scoped:
```python
ScopedAggregationData(
    expression=<AggregationExpressionData for capital_cost>,
    instance_path="SolarBatteryDesign__solar_battery_plant__solar_array",
)
# module_eqn = "SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost"
```

**Step 3: _build_chain_aliases()**

The `total_capex :>> cost_model.total_cost` CHAIN redefinition produces:
```python
ChannelAlias(
    alias_name="solar_battery_plant.solar_array.total_capex",
    canonical_name="solar_battery_plant.solar_array.cost_model.total_cost",
    owning_part_qn="SolarBatteryLibrary__Solar_Array",
    source="redefinition",
)
```

**Step 4: OutputRegistry consumption**

Phase 1b registers the aggregation output as a canonical channel. Phase 2 resolves
`"solar_battery_plant.solar_array.cost_model.total_cost"` through the registry and maps
`"solar_battery_plant.solar_array.total_capex"` to the same canonical channel. Any downstream
module binding to `solar_array.total_capex` now resolves correctly.

## Key Source Files

| File | Elements |
|------|----------|
| `extraction/data_models.py` | `AggregationExpressionData`, `ScopedAggregationData`, `SumTerm`, `SingletonTerm`, `LocalTerm` |
| `core/models.py` | `ChannelAlias` |
| `orchestration/pipeline_builder.py` | `find_instance_paths_for_partdef()`, `_scope_aggregation_expressions()`, `_build_chain_aliases()` |
| `orchestration/output_registry_builder.py` | `build_output_registry()` |

## Related Documents

- **Upstream**: [01-extraction](01-extraction.md) — produces `AggregationExpressionData` and `RedefinitionData`, [12-virtual-binding-rewrite](12-virtual-binding-rewrite.md) — runs just before scoping in Step 3.5
- **Registry**: [10-output-registry](10-output-registry.md) — Phase 1b/2 consume scoping outputs, [15-naming-conventions](15-naming-conventions.md) — channel formats- **Downstream**: [05-module-factory](05-module-factory.md) — builds aggregation modules from `ScopedAggregationData`, [04-input-resolver](04-input-resolver.md) — resolves aggregation module inputs
- **Architecture**: [00-pipeline-overview](00-pipeline-overview.md) — Step 3.5 placement, [24-dual-resolution-architecture](24-dual-resolution-architecture.md) — aggregation as second resolution path
- **Data models**: [09-data-models](09-data-models.md) — `AggregationExpressionData`, `ScopedAggregationData`, `ChannelAlias`
