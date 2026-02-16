# 05 -- Module Factory: Building the 3 Types of Pipeline Modules

After the refactoring, module construction is separated from resolution -- each
factory function receives pre-resolved data and produces a pure PipelineModule.

## 1. The PipelineModule Data Model

```python
class PipelineModule(BaseModel):
    name: str                       # Lowercase EQN, e.g., "design__plant__battery_cost_calc"
    module_type: str                # PascalCase, e.g., "BatteryCostCalcModule"
    inputs: list[ModuleInput]       # What the module consumes
    outputs: list[ModuleOutput]     # What the module produces
    execution_order: int            # Position in topological sort
    compilability: Compilability    # FULLY_COMPILABLE | MANUAL_REQUIRED | UNKNOWN
    compiled_expression: str | None # Inlined expression for auto-gen modules
    is_computed_attribute: bool     # True for FORMULA modules
    is_aggregation: bool            # True for aggregation modules

class ModuleInput(BaseModel):
    param_name: str      # e.g., "capacity"
    python_type: str     # Always "float" for now
    source: InputSource  # WHERE the value comes from

class ModuleOutput(BaseModel):
    field_name: str    # "root" for single-output, attr name for multi-output
    python_type: str   # Always "float" for now
    channel_name: str  # PQN format, e.g., "design__plant__cost_calc__total_cost"

class InputSource(BaseModel):
    source_type: str                    # "entry_point" or "module_output"
    param_group: str | None = None      # entry_point: which JSON file
    qualified_name: str | None = None   # entry_point: the qualified param name
    producer_channel: str | None = None # module_output: upstream channel name
```

Every input is wired to exactly one source: an upstream module's output channel,
or a user-provided entry point (JSON input file).

## 2. CalcUsage Modules -- `_build_pipeline_module()`

**Source**: CalcUsageData + its CalculationDefinitionData. A named invocation of
a calculation definition. The function receives `binding_resolutions` mapping
`"{usage_qn}|{param_name}"` to a BindingResolution -- single source of truth.
Missing mapping = immediate raise (fail-fast, no fallback).

**Inputs**: Look up each calc def input_attribute in binding_resolutions.
MODULE_OUTPUT -> wire to upstream channel. ENTRY_POINT -> wire to entry point.

**Outputs**: PQN channel per output_attribute. Single output: field_name "root";
multi-output: attribute name.

```
_build_pipeline_module(
    usage=CalcUsageData(qualified_name="Design__plant__battery_cost_calc"),
    calc_def=CalcDef(inputs=[capacity, unit_cost], outputs=[battery_cost]),
    binding_resolutions={
        "...|capacity":  MODULE_OUTPUT -> "design__plant__size_calc__capacity",
        "...|unit_cost": ENTRY_POINT  -> "design__plant__unit_cost",
    },
)
-->
PipelineModule(
    name="design__plant__battery_cost_calc",
    module_type="BatteryCostCalcModule",
    inputs=[
        ModuleInput("capacity",  source=module_output("design__plant__size_calc__capacity")),
        ModuleInput("unit_cost", source=entry_point("design__plant__unit_cost")),
    ],
    outputs=[ModuleOutput("root", channel="design__plant__battery_cost_calc__battery_cost")],
    execution_order=3,
)
```

## 3. FORMULA Modules -- `_build_computed_attr_module()`

**Source**: ComputedAttributeData with classification FORMULA -- a PartDef
attribute with an inline expression. Synthetic module; no SysML calc usage. The
expression compiler already produced `compiled_expression` with `inputs.X` refs.

**Inputs**: Parse names from compiled expression via regex. Check resolution map:
FORMULA/EXPOSE_ALIAS with channel -> module_output. Otherwise -> entry point.

**Outputs**: Single output, field_name "root". **Flags**: `is_computed_attribute=True`, `FULLY_COMPILABLE`.

```
_build_computed_attr_module(
    ca=ComputedAttributeData(
        name="total_cost", owning_part_name="SolarPlant",
        compiled_expression="inputs.material_cost + inputs.labor_cost",
    ),
)
-->
PipelineModule(
    name="solarplant__total_cost",
    module_type="SolarPlantTotalCostModule",
    inputs=[
        ModuleInput("material_cost", source=module_output("solarplant__material_cost__material_cost")),
        ModuleInput("labor_cost",    source=entry_point("solarplant__labor_cost")),
    ],
    outputs=[ModuleOutput("root", channel="solarplant__total_cost__total_cost")],
    is_computed_attribute=True, compilability=FULLY_COMPILABLE,
)
```

## 4. Aggregation Modules -- `_build_aggregation_module()`

**Source**: ScopedAggregationData -- a PartDef `:>>` expression with `sum()`
calls, scoped to a design instance path. Rollup across child part usages.
Additional inputs: `expose_aliases` (EXPOSE_PURE alias map for LocalTerms),
`usage_type_map` (type-aware PartDef QN resolution -- see doc 18).
Expression is decomposed into three term types:

### 4a. SumTerm -- `sum(child.attr * count)`

```python
SumTerm(part_usage_name="pv_module", attribute_name="capital_cost",
        multiplicity_attr="module_count", multiplicity_count=20)
```

Resolution chain:
1. `_resolve_aggregation_input_channel()` -- CHAIN redefinition tracing + registry
2. **LITERAL fallback** -- `_find_literal_redefinition()` checks for `:>> attr = value`
   on the child PartDef. If found, the value becomes the entry point's `default_value`
   and the module stays `FULLY_COMPILABLE` (see doc 18).
3. Entry point (no default) + `MANUAL_REQUIRED` compilability.

When `multiplicity_attr` is present, adds a second input for the count
(entry point, default = multiplicity_count).

### 4b. SingletonTerm -- `child.attr` (no multiplication)

```python
SingletonTerm(source_path="allocation_model.total_allocation")
```

Resolution chain:
1. `_resolve_aggregation_input_channel()` -- CHAIN redefinition tracing + registry
2. Direct channel construction -- `instance_path__prefix__output_name`
3. **LITERAL fallback** -- same as SumTerm, found value becomes EP default (doc 18)
4. Entry point (no default) + `MANUAL_REQUIRED` compilability.

### 4c. LocalTerm -- same-PartDef attribute

```python
LocalTerm(attribute_name="misc_hardware_cost")
```

Tries three strategies in order:
1. **Sibling aggregation output** -- another aggregation module at the same scope
   produces a channel with the double-attr format `{ip}__{attr}__{attr}`.
2. **EXPOSE_PURE alias** -- the `expose_aliases` map (built in Step 6.6b from
   EXPOSE_PURE ComputedAttributes) provides a dotted expression path
   (e.g., `"allocation_model.total_allocation"`). That path is then resolved
   through `_resolve_aggregation_input_channel()` to find the upstream channel.
3. **Entry point fallback** -- user-provided value.

After all terms are processed, symbolic references (`pv_module.capital_cost`)
are replaced with input references (`inputs.pv_module_capital_cost`) to produce
`compiled_expression`. **Flags**: `is_aggregation=True`.

### Concrete example

SysML: `total_cost :>> sum(pv_module.capital_cost * module_count) + inverter.install_cost + misc_cost`
Scope: `Design__plant__solar_array`

```
Input:  sum_terms=[SumTerm("pv_module", "capital_cost", "module_count", 20)]
        singleton_terms=[SingletonTerm("inverter.install_cost")]
        local_terms=[LocalTerm("misc_cost")]
-->
PipelineModule(
    name="design__plant__solar_array__total_cost",
    module_type="SolarArrayTotalCostModule",
    inputs=[
        ModuleInput("pv_module_capital_cost",       source=module_output("...pv_module__cost_calc__capital_cost")),
        ModuleInput("module_count",                 source=entry_point("...solar_array__module_count", default=20)),
        ModuleInput("inverter_install_cost",        source=module_output("...inverter__install_calc__install_cost")),
        ModuleInput("misc_cost",                    source=entry_point("...total_cost__misc_cost")),
    ],
    outputs=[ModuleOutput("root", channel="...solar_array__total_cost__total_cost")],
    is_aggregation=True,
    compiled_expression="inputs.pv_module_capital_cost * inputs.module_count
                       + inputs.inverter_install_cost + inputs.misc_cost",
)
```

## 5. The Key Insight: Pure Data Transformers

All three factory functions follow the same contract:

    pre-resolved inputs + metadata  -->  PipelineModule

No graph walking, no registry mutation, no entry point discovery inside these
functions. Resolution is done upstream (by the input resolver, the backtracker,
or the aggregation channel resolver). The factories are pure data transformers.

This means each can be tested with a simple truth table: given these inputs,
assert this exact PipelineModule output. No mocking of registries, no setup of
global state, no dependency on execution order. The complexity of resolution is
factored out; what remains is structural mapping.
