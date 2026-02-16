# 02 -- Orchestration: The Pipeline Builder

## What orchestration does

Orchestration is the conductor of the sysml-codegen pipeline. It does not
extract SysML data, resolve dependencies, or render templates. It calls
those layers in the right order and threads data between them:

```
  extraction  -->  orchestration  -->  resolution  -->  generation
                   (this layer)
```

Today, this logic lives in `generation/initialization.py` (860 lines).
After the refactor it moves to `orchestration/`, because it is not
generation code -- it is coordination code that produces the
`PipelineContext` that generation consumes.

## build_pipeline_context() -- the 7-step sequence

Everything the orchestrator builds ends up in a `PipelineContext` dataclass.
Generation templates primarily need `computation_graph`, but the context
carries all intermediate data for debugging and future generation modes.

Each step feeds into the next:

| Step | What it does | Produces |
|------|-------------|----------|
| 1 | Load SysML models via `SysMLDataExtractor` | `extractor` |
| 2 | Extract calc definitions from the model | `calc_defs` |
| 3 | Extract calc usages with binding info | `calc_usages` |
| 3.5 | Hierarchy extraction + binding rewrite + aggregation scoping + CHAIN aliases | `hierarchy_data`, `scoped_agg_data`, `chain_aliases` |
| 4 | Extract design attributes (literal values from PartDefs) | `design_attrs` |
| 4.5 | Extract computed attributes, remove FORMULAs from design attrs | `computed_attrs`, `expose_aliases` |
| 5 | Create `ParameterGroupDeriver` (classifies entry points) | `group_deriver` |
| 5.5 | Build `OutputRegistry` (4-phase lookup table) | `output_registry` |
| 6 | Run `DependencyBacktracker` (trace all input wiring) | `backtracking_result` |
| 6.5 | Compile SysML expressions to Python strings | `compilation_results` |
| 7 | Build `ComputationGraph` (single source of truth) | `computation_graph` |

Key ordering constraints:

- Step 3.5 before Step 4: binding rewriting mutates `calc_usages` in place;
  later steps must see rewritten bindings.
- Step 4.5 before Step 5: removes FORMULA attributes from `design_attrs`,
  preventing false entry points in the parameter group deriver.
- Step 5.5 before Step 6: the backtracker uses the `OutputRegistry` to
  resolve binding source paths to canonical channel names.

## build_output_registry() -- the 4-phase lookup table

The `OutputRegistry` is a flat `dict[str, str]` mapping every possible
way a binding might reference an output to that output's canonical channel
name. SysML bindings can reference the same output using different key
formats, so the registry normalizes all of them.

### Phase 1: Canonical channels

Registers the actual outputs that pipeline modules produce.

**Phase 1a -- CalcUsage outputs.** Three key variants per output:

```
Calc usage: SolarBatteryDesign__solar_battery_plant__solar_array__cost_model
Output:     total_cost

Canonical:  solar_battery_plant__solar_array__cost_model__total_cost
Key_A:      cost_model.total_cost           (instance_name.output)
Key_C:      solar_battery_plant.solar_array.cost_model.total_cost  (dotted QN)
```

**Phase 1b -- Aggregation outputs.** Registered with dotted keys at
multiple scoping levels (with and without the design prefix).

**Phase 1c -- FORMULA outputs.** Computed attributes classified as FORMULA
generate synthetic modules. Registered with `PartName.attr_name` and bare
`attr_name` keys.

### Phase 2: CHAIN aliases

For each `:>>` CHAIN redefinition, look up the canonical channel that the
chain target resolves to, then register the alias name pointing to the
same canonical. Example:

```
Redefinition:  total_capex :>> cost_model.total_cost
Alias name:    solar_battery_plant.solar_array.total_capex
Resolves to:   solar_battery_plant__solar_array__cost_model__total_cost
```

### Phase 3: EXPOSE_PURE aliases

Similar to Phase 2, but for attributes that expose another calculation's
output through a PartUsage. Scoped to the owning part name.

### Phase 4: Transitive design attribute aliases

Some design attributes have default values that reference other outputs
(e.g., `p_net = net_electric.p_net`). Phase 4 registers `DesignPart.p_net`
as an alias for whatever `net_electric.p_net` already resolved to.

### After construction

```python
registry.resolve("cost_model.total_cost")
# => "solar_battery_plant__solar_array__cost_model__total_cost"

registry.resolve("solar_array.total_capex")
# => "solar_battery_plant__solar_array__cost_model__total_cost"  (via alias)
```

Both keys resolve to the same canonical channel. The backtracker and graph
builder never need to know which key format a binding used.

## Virtual binding rewriting

A calc usage is "virtual" when it was instantiated by template expansion.
A PartDef acts as the template; each PartUsage creates a virtual copy.
The problem: virtual copies carry the template's generic bindings, which
reference template-level attributes. These must be rewritten for the
design instance.

`_rewrite_virtual_bindings()` builds an override index from
`hierarchy_data.design_overrides`, keyed by `(parent_path, leaf_attribute)`.
Then for each non-template calc usage, it extracts the leaf name from each
binding's `source_path` and matches against the index:

```
BEFORE (template binding):
  binding.source_path = "SolarBatteryLibrary::Solar_Array::panel_cost"
  binding.binding_type = REFERENCE

AFTER (LITERAL override -- design sets a concrete value):
  binding.binding_type = LITERAL
  binding.literal_value = 250.0

AFTER (CHAIN override -- design redirects to another output):
  binding.source_path = "cost_model.adjusted_cost"
```

This mutation happens in place, which is why Step 3.5 must run before
any downstream step that reads bindings.

## Aggregation scoping

SysML models define aggregation expressions at the PartDef level:

```sysml
part def Solar_Array {
    attribute total_capex = sum(cost_model.total_cost);
}
```

But the pipeline operates on concrete design instances, not abstract
PartDefs. `_scope_aggregation_expressions()` maps each PartDef-level
aggregation to its design instances by scanning virtual calc usages:
if a usage's `owning_part_def_qn` matches the aggregation's owning
PartDef, its parent path is an instance.

```
PartDef:   SolarBatteryLibrary__Solar_Array
Instance:  SolarBatteryDesign__solar_battery_plant__solar_array

=> ScopedAggregationData(expression=<sum>, instance_path="...solar_array")
```

CHAIN alias construction (`_build_chain_aliases()`) uses the same
instance-discovery mechanism: for each `:>>` CHAIN redefinition on a
PartDef, it finds the instance paths and produces scoped `ChannelAlias`
objects that Phase 2 of the registry builder consumes.

## Post-refactor structure

```
orchestration/
    pipeline_builder.py          -- build_pipeline_context() + PipelineContext
                                    Steps 1-7 coordination, no business logic
    output_registry_builder.py   -- build_output_registry()
                                    4-phase registration protocol
```

Supporting functions (`_rewrite_virtual_bindings`, `_scope_aggregation_expressions`,
`_build_chain_aliases`, `find_instance_paths_for_partdef`) move into
`pipeline_builder.py` as data-preparation helpers called exclusively by
the pipeline builder.

The exception classes `SysMLParsingError` and `CodeGenerationError` also
move to `orchestration/`, since they are raised by the pipeline builder,
not by the generation layer.
