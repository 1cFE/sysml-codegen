# Pipeline Overview

## What sysml-codegen does

sysml-codegen reads SysML v2 model files and produces a complete, runnable TEAx
simulation pipeline: Python module wrappers, Pydantic schemas, JSON input
templates, and pipeline YAML. The output is a working computation graph where
each calculation defined in SysML becomes an executable module wired to its
upstream dependencies and downstream consumers.

## The 7-step pipeline

The pipeline transforms `.sysml` files into a `ComputationGraph` -- a single
Pydantic model that is the source of truth for all generated code. After
refactoring, the steps decompose cleanly:

```
SysML files
    |
    v
[Step 1] Extract         -- parse .sysml into data models        --> 01, 09
[Step 2] Build registry   -- catalog outputs for O(1) lookup      --> 10, 15
[Step 3] Resolve inputs   -- wire inputs to channels or entries   --> 03, 04
[Step 4] Build modules    -- construct PipelineModules            --> 05, 13, 16
[Step 5] Classify entries -- tag entry point types (ADR-001)      --> 06, 17
[Step 6] Sort modules     -- topological sort + validation        --> 07
[Step 7] Render code      -- Jinja2 templates produce output      --> 08
    |
    v
Generated package (modules/, schemas/, inputs/, pipelines/, handwritten/)
```

*(Numbers reference document files in this directory, e.g., "01" = [01-extraction.md](01-extraction.md).)*

## Running example: battery_pack cost_model

To make this concrete, trace a single calculation through all 7 steps. In the
SolarBattery model, the library defines a `BatteryPackCostCalc` that computes
the total cost of a battery pack:

```sysml
calc def BatteryPackCostCalc {
    in capacity_kwh : Real;
    in chemistry_factor : Real;
    in cost_per_kwh : Real;       // library default: 150.0
    in fab_factor : Real;         // library default: 0.05
    in install_factor : Real;     // library default: 0.10
    return total_cost : Real = capacity_kwh * cost_per_kwh * chemistry_factor;
    // (also returns material_cost, fab_cost, install_cost, idiot_index)
}
```

The design file instantiates it inside a part hierarchy:

```
SolarBatteryDesign
  solar_battery_plant
    battery_system
      battery_pack
        cost_model : BatteryPackCostCalc   // <-- this is the CalcUsage
```

### Step 1: Extract ([detail](01-extraction.md))

`SysMLDataExtractor` parses the model and produces:

- A `CalculationDefinitionData` for `BatteryPackCostCalc` with 5 input
  attributes and 5 output attributes. ([data model](09-data-models.md))
- A `CalcUsageData` with `qualified_name =
  "SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model"`,
  `calc_def_name = "BatteryPackCostCalc"`, and a [bindings](01-extraction.md#binding-types) list showing which
  inputs have literal values vs. references vs. are unbound.

### Step 2: Build output registry ([detail](10-output-registry.md))

`OutputRegistry` catalogs every output channel that any module will produce.
For our battery pack module, it registers a **canonical channel name** (the
PQN-format string -- see [naming conventions](15-naming-conventions.md#6-channel-name))
plus multiple **lookup keys** so that downstream modules can find this channel
using different reference formats:

```
canonical (Key_B): "SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model__total_cost"
Key_A:             "cost_model.total_cost"                      (instance_name.output)
Key_C:             "solar_battery_plant.battery_system.battery_pack.cost_model.total_cost"  (dotted hierarchy)
```

Keys are registered in a [strict 4-phase protocol](10-output-registry.md#the-4-phase-registration-protocol):
Phase 1 registers canonical channels (CalcUsage, Aggregation, FORMULA outputs).
Phases 2-4 register **aliases** -- additional keys that resolve to an existing
canonical. For example, a `:>>` CHAIN [redefinition](01-extraction.md#redefinitions-redefinitiondata)
like `capital_cost :>> cost_model.total_cost` creates a Phase 2 alias so that
`battery_pack.capital_cost` resolves to the same canonical channel. See the
[concrete trace](10-output-registry.md#concrete-example) for a full walkthrough.

Later, when a downstream aggregation module references `battery_pack.capital_cost`,
the registry resolves that alias to the canonical channel name in O(1).

### Step 3: Resolve inputs ([overview](03-resolution-overview.md) | [resolver detail](04-input-resolver.md))

For each of the 5 inputs on cost_model, the [unified input resolver](04-input-resolver.md)
determines the source by running an ordered [strategy chain](04-input-resolver.md#the-five-strategies)
(direct registry lookup, SysML QN normalization, scoped lookup, CHAIN redefinition
follow, design attribute match):

| Input              | Resolution           | Source                           |
|--------------------|----------------------|----------------------------------|
| `capacity_kwh`     | ENTRY_POINT          | Design attribute (user provides) |
| `chemistry_factor` | ENTRY_POINT          | Design attribute (user provides) |
| `cost_per_kwh`     | ENTRY_POINT          | Library default = 150.0          |
| `fab_factor`       | ENTRY_POINT          | Library default = 0.05           |
| `install_factor`   | ENTRY_POINT          | Library default = 0.10           |

In a more complex case, an input might resolve to `MODULE_OUTPUT` -- meaning it
reads the output channel of an upstream module instead of a JSON entry point.
For example, the `AnnualizedFinancialCalc.total_capex` input resolves to the
`capital_cost` aggregation module's output channel. See the
[truth table](04-input-resolver.md#truth-table) for representative examples of
each strategy in action.

### Step 4: Build the PipelineModule ([detail](05-module-factory.md))

A `PipelineModule` is constructed with:

```python
PipelineModule(
    name="solarbatterydesign__solar_battery_plant__battery_system__battery_pack__cost_model",
    module_type="solarbatterylibrary.BatteryPackCostCalcModule",
    inputs=[
        ModuleInput(param_name="capacity_kwh", source=InputSource(source_type="entry_point", ...)),
        ModuleInput(param_name="cost_per_kwh", source=InputSource(source_type="entry_point", ...)),
        # ... 3 more
    ],
    outputs=[
        ModuleOutput(field_name="material_cost", channel_name="...battery_pack__cost_model__material_cost"),
        ModuleOutput(field_name="total_cost",    channel_name="...battery_pack__cost_model__total_cost"),
        # ... 3 more
    ],
)
```

This is pure data construction. No I/O, no side effects. There are
[3 module types](05-module-factory.md) -- CalcUsage, FORMULA ([computed attributes](16-computed-attributes.md)),
and Aggregation ([scoping rules](13-aggregation-scoping.md)) -- each with its own
factory function but sharing the same `PipelineModule` output shape
([data models](09-data-models.md)).

### Step 5: Classify entry points ([detail](06-entry-point-classifier.md))

Each entry-point input is classified into one of the [three ADR-001 types](06-entry-point-classifier.md):

- `capacity_kwh` --> `DESIGN_ATTRIBUTE` (literal from the design part definition)
- `cost_per_kwh` --> `LIBRARY_DEFAULT` (unbound param; calc def provides a default)

This classification drives which JSON input file the parameter lands in
(`design_params.json` vs. `library_params.json`) and whether the JSON template
is pre-populated with a default value. Entry points are then grouped into
[parameter groups](17-parameter-group-deriver.md) for the generated JSON files.

### Step 6: Sort modules ([detail](07-graph-assembly.md))

Kahn's algorithm topologically sorts all modules. The battery_pack cost_model
has no upstream module dependencies (all inputs are entry points), so it appears
early in the execution order. The plant-level `capital_cost` aggregation, which
consumes this module's `total_cost` output, appears later.

### Step 7: Render code ([detail](08-generation.md))

The `ComputationGraph` is handed to Jinja2 templates. For our battery pack
module, generation produces:

- `modules/battery_pack_cost_calc.py` -- TEAx module wrapper class
- `handwritten/battery_pack_cost_calc_impl.py` -- implementation stencil
- Entry in `pipelines/solar_battery.yaml`:
  ```yaml
  solarbatterydesign__solar_battery_plant__battery_system__battery_pack__cost_model:
    module_type: solarbatterylibrary.BatteryPackCostCalcModule
    inputs:
      capacity_kwh: float design_params....capacity_kwh
      cost_per_kwh: float library_params....cost_per_kwh
    outputs:
      total_cost: float ...battery_pack__cost_model__total_cost
  ```
- Entry in `inputs/library_params.json` with `cost_per_kwh: 150.0`
- Entry in `inputs/design_params.json` with `capacity_kwh: null`

## Package structure (post-refactor)

```
sysml_codegen/
  extraction/       Step 1 -- Parse .sysml into structured dataclasses
    extractor.py              SysMLDataExtractor: load models, extract calc defs
    usage_extractor.py        Find CalcUsages (CalcUsageData) and their bindings
    hierarchy_resolver.py     Redefinitions, aggregation expressions, design overrides
    data_models.py            CalculationDefinitionData, RedefinitionData, etc.

  generation/       Currently hosts orchestration (refactor target: move to orchestration/)
    initialization.py         build_pipeline_context(), build_output_registry()

  resolution/       Steps 3-6 -- Wire inputs, build modules, sort
    graph_builder.py          build_computation_graph(), _classify_entry_points()
    models.py                 ComputationGraph, PipelineModule, EntryPoint

  generation/       Step 7 -- Render Python, YAML, JSON from the graph
    pipeline.py / modules.py / schemas.py / stencils.py / entry_point.py

  core/             Shared utilities (OutputRegistry, qualified_names, models)
  analysis/         Dependency backtracking and parameter group derivation
```

Note: `orchestration/` does not yet exist. Today, all orchestration code lives
in `generation/initialization.py`. The refactor will move it to a dedicated
`orchestration/` package so that generation becomes a pure rendering step.
See [02-orchestration.md](02-orchestration.md) for the refactored orchestrator design.

## Navigation index

### Core pipeline (Steps 1-7)

- **[01-extraction.md](01-extraction.md)** -- Reading SysML models into structured data (CalculationDefinitionData, CalcUsageData, bindings, redefinitions)
- **[02-orchestration.md](02-orchestration.md)** -- The pipeline builder: coordinating extract, resolve, generate
- **[03-resolution-overview.md](03-resolution-overview.md)** -- How input resolution works (the heart of the system); why 3 code paths is a problem
- **[04-input-resolver.md](04-input-resolver.md)** -- The unified resolver and its 5-strategy chain (direct, SysML QN, scoped, CHAIN, design attr)
- **[05-module-factory.md](05-module-factory.md)** -- Building the 3 module types (CalcUsage, FORMULA, aggregation) as pure data transformers
- **[06-entry-point-classifier.md](06-entry-point-classifier.md)** -- Classifying unresolved inputs as LIBRARY_DEFAULT, DESIGN_ATTRIBUTE, or USAGE_LITERAL
- **[07-graph-assembly.md](07-graph-assembly.md)** -- Topological sort, validation, and ComputationGraph assembly
- **[08-generation.md](08-generation.md)** -- Rendering Python code, YAML, and JSON from the graph via Jinja2 templates
- **[09-data-models.md](09-data-models.md)** -- All key data models and their relationships

### Deep-dive topics

- **[10-output-registry.md](10-output-registry.md)** -- The 4-phase registration protocol: canonical channels, CHAIN/EXPOSE_PURE/transitive aliases, O(1) lookup
- **[11-analysis-backtracker.md](11-analysis-backtracker.md)** -- Dependency backtracking: tracing calc usage bindings to upstream sources
- **[12-virtual-binding-rewrite.md](12-virtual-binding-rewrite.md)** -- Template calc usage expansion and virtual binding construction
- **[13-aggregation-scoping.md](13-aggregation-scoping.md)** -- How `sum()` expressions are scoped to design instance paths
- **[14-expression-compiler.md](14-expression-compiler.md)** -- AST-to-Python compilation for calc def outputs and computed attributes
- **[15-naming-conventions.md](15-naming-conventions.md)** -- EQN, PQN, module names, channel names, registry key formats (ADR-003/008)
- **[16-computed-attributes.md](16-computed-attributes.md)** -- FORMULA and EXPOSE_PURE computed attribute classification
- **[17-parameter-group-deriver.md](17-parameter-group-deriver.md)** -- Grouping entry points into JSON input files
- **[18-literal-value-propagation.md](18-literal-value-propagation.md)** -- Carrying `:>>` literal redefinition values into JSON templates
