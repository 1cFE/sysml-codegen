# Pipeline Overview

## What sysml-codegen does

sysml-codegen reads SysML v2 model files and produces a complete, runnable TEAx
simulation pipeline: Python module wrappers, Pydantic schemas, JSON input
templates, and pipeline YAML. The output is a working computation graph where
each calculation defined in SysML becomes an executable module wired to its
upstream dependencies and downstream consumers.

## Pipeline Requirements

These requirements span the entire pipeline. Each is verifiable.

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-PIPE-01 | The pipeline SHALL produce exactly one [ComputationGraph](09-data-models.md#resolution-models) from a set of SysML model files. | `isinstance(result, ComputationGraph)` and single return value from `build_computation_graph()` |
| REQ-PIPE-02 | Every [ModuleInput](09-data-models.md#resolution-models) SHALL be wired to exactly one source: `module_output` or `entry_point`. | `all(mi.source.source_type in {"module_output","entry_point"} for m in graph.modules for mi in m.inputs)` |
| REQ-PIPE-03 | Every `module_output` reference SHALL resolve to a canonical channel in the [OutputRegistry](10-output-registry.md). | Step 8 validation: `_validate_channel_references()` asserts all `producer_channel` values exist |
| REQ-PIPE-04 | `execution_order` SHALL be a valid topological sort -- no module reads from a module that executes later. | `for m in modules: for i in m.inputs: if i.source.source_type == "module_output": assert producer.execution_order < m.execution_order` |
| REQ-PIPE-05 | Every [EntryPoint](06-entry-point-classifier.md) SHALL be classified as exactly one of {`LIBRARY_DEFAULT`, `DESIGN_ATTRIBUTE`, `USAGE_LITERAL`}. | `all(ep.entry_type in EntryPointType for g in graph.entry_point_groups for ep in g.parameters)` |
| REQ-PIPE-06 | The graph SHALL tag each module with its `module_kind`; a calc-bearing model includes `CALCULATION`, `FORMULA`, and `AGGREGATION` modules. | `PipelineModule.module_kind` (`resolution/models.py`), checked per family. The two constraint-execution families `CONSTRAINT` / `REPORT_AGGREGATOR` appear when constraints are lowered (see [28](28-constraint-lowering-and-catalog.md)) |
| REQ-PIPE-07 | Generation SHALL produce output exclusively from `ComputationGraph` -- no back-references to extraction models. Requires PipelineModule expansion (see [26](26-pipeline-module-migration.md)). | All templates receive only `ComputationGraph` fields |

## The 7-step pipeline

```
SysML files
    |
    v
[Step 1] Extract         -- parse .sysml into data models        --> 01, 09
[Step 2] Build registry   -- catalog outputs for O(1) lookup      --> 10, 15
[Step 3] Trace deps       -- DFS + CalcUsage binding resolution   --> 11, 03, 24
[Step 4] Classify entries -- tag entry point types               --> 06, 17
[Step 5] Build modules    -- construct PipelineModules            --> 05, 04, 13, 16
[Step 6] Sort modules     -- topological sort + validation        --> 07
[Step 7] Render code      -- Jinja2 templates produce output      --> 08
    |
    v
Generated package (modules/, schemas/, inputs/, pipelines/, handwritten/)
```

*(Numbers reference document files in this directory, e.g., "01" = [01-extraction.md](01-extraction.md).)*

**Snapshot path.** Step 1 can run offline: `sysml-codegen snapshot` captures a
versioned extraction snapshot from live models (this capture needs the live
syside license), and `generate --from-snapshot` (mutually exclusive with
`--models`) rebuilds the same `PipelineContext` from that JSON, license-free --
Steps 2-7 run unchanged. The same split holds for the capture scripts: only
`scripts/capture_extraction_snapshots.py` needs the license;
`scripts/capture_pipeline_baselines.py` and `scripts/capture_baseline_yaml.py`
regenerate baselines from committed snapshots, license-free. See
[27-snapshot-generation](27-snapshot-generation.md).

## Running example: battery_pack cost_model

Trace a single calculation through all 7 steps. The library defines
`BatteryPackCostCalc` (5 inputs, 5 outputs). The design instantiates it:

```
SolarBatteryDesign > solar_battery_plant > battery_system > battery_pack > cost_model
```

### Step 1: Extract ([detail](01-extraction.md))

Produces a [CalculationDefinitionData](09-data-models.md#extraction-models) for
`BatteryPackCostCalc` and a [CalcUsageData](09-data-models.md#extraction-models)
with `qualified_name = "SolarBatteryDesign__...battery_pack__cost_model"` and a
[bindings](01-extraction.md#binding-types) list classifying each input.

### Step 2: Build output registry ([detail](10-output-registry.md))

SysML bindings reference the same output using different string formats depending
on AST node type and context. A `FeatureChainExpression` produces
`"cost_model.total_cost"` (a scope-relative local path); a `:>>` redefinition
target uses the hierarchy path `"solar_battery_plant...cost_model.total_cost"`.
These are different strings for the **same output**.

The [OutputRegistry](10-output-registry.md) maps each output to a canonical
channel name (`CanonicalChannel`) via three [typed registries](10-output-registry.md):

```
Canonical (PQN):   "SolarBatteryDesign__...cost_model__total_cost"    (CanonicalChannel, unique by construction)
Scoped (Key_C):    "solar_battery_plant.battery_system.battery_pack.cost_model.total_cost"
                                                                      (ScopedKey, unique by SysML ownership)
SysML QN:          "SolarBatteryLibrary::BatteryPackCostCalc::total_cost"
                                                                      (SysMLQN, for REFERENCE bindings)
```

**ScopedKey is the critical key.** It is both unique AND matchable from the
consumer's scope. The [backtracker](11-analysis-backtracker.md) constructs
`ScopedKey` lookups by prepending the consumer's scope to the `source_path`. See
[The Scope Problem](03-resolution-overview.md#the-scope-problem).

Keys follow a [strict 4-phase protocol](10-output-registry.md#the-4-phase-registration-protocol).
[CHAIN redefinitions](01-extraction.md#redefinitions-redefinitiondata) create
Phase 2 aliases (e.g., `battery_pack.capital_cost` -> same canonical).
Multi-hop EXPOSE aliases are registered tentatively and confirmed (or reverted
to FORMULA) in a Phase 3b pass of registry build
(`orchestration/output_registry_builder.py`).

### Step 3: Trace dependencies ([backtracker](11-analysis-backtracker.md) | [overview](03-resolution-overview.md))

The [DependencyBacktracker](11-analysis-backtracker.md) performs DFS from root calc
usages, resolving each binding via [type-directed dispatch](11-analysis-backtracker.md#type-directed-resolution-dispatch)
against the [typed registries](10-output-registry.md). Each binding resolves to
MODULE_OUTPUT (recurse into producer) or ENTRY_POINT (external input):

| Input              | Resolution           | Source                           |
|--------------------|----------------------|----------------------------------|
| `capacity_kwh`     | ENTRY_POINT          | Design attribute (user provides) |
| `chemistry_factor` | ENTRY_POINT          | Design attribute (user provides) |
| `cost_per_kwh`     | ENTRY_POINT          | Library default = 150.0          |
| `fab_factor`       | ENTRY_POINT          | Library default = 0.05           |
| `install_factor`   | ENTRY_POINT          | Library default = 0.10           |

An input can also resolve to `MODULE_OUTPUT` (upstream channel). CalcUsage bindings
are resolved here; FORMULA/Aggregation bindings are resolved during module building
(Step 5). See [24-dual-resolution-architecture](24-dual-resolution-architecture.md).

### Step 4: Classify entry points ([detail](06-entry-point-classifier.md))

Each entry-point input gets one of [three entry point types](06-entry-point-classifier.md):
`DESIGN_ATTRIBUTE`, `LIBRARY_DEFAULT`, or `USAGE_LITERAL`. This drives JSON file
placement and default values. Entry points are grouped into
[parameter groups](17-parameter-group-deriver.md). Classification runs BEFORE module
building because CalcUsage modules need classified entry points as inputs.

### Step 5: Build PipelineModules ([factory](05-module-factory.md) | [resolver](04-input-resolver.md))

A [PipelineModule](09-data-models.md#resolution-models) is constructed as pure
data -- no I/O, no side effects. The three calc [module kinds](05-module-factory.md)
are CalcUsage (`CALCULATION`), FORMULA ([computed attributes](16-computed-attributes.md)),
and Aggregation ([scoping rules](13-aggregation-scoping.md)). FORMULA and Aggregation
factories call the [consolidated resolver](04-input-resolver.md) to wire their inputs.

**Constraint lowering ([P1 RESOLVE], Step 5.7).** After the output registry and the
supplied-value materializer are final, `lower_constraints`
([`analysis/constraint_lowering.py`](28-constraint-lowering-and-catalog.md)) turns eligible
modeled assertions into two further `module_kind` families — `CONSTRAINT` (a lowered
predicate) and `REPORT_AGGREGATOR` (the run-report roll-up) — and assembles the
`ConstraintCatalog` embedded on the graph. A constraint-free model produces neither family and
a byte-identical graph. Lowering is default-on; the `lower_constraints_enabled` flag is landed
history (its GRANDFATHERED carve-out is now empty), not a live drop path. See
[28-constraint-lowering-and-catalog](28-constraint-lowering-and-catalog.md).

### Step 6: Sort modules ([detail](07-graph-assembly.md))

Kahn's algorithm topologically sorts all modules (REQ-PIPE-04). Battery_pack
cost_model has no upstream dependencies, so it appears early.

### Step 7: Render code ([detail](08-generation.md))

The [ComputationGraph](09-data-models.md#resolution-models) feeds Jinja2 templates
to produce: `modules/*.py`, `handwritten/*_impl.py`, `pipelines/*.yaml`,
`inputs/*.json`, and `schemas/*.py`.

Rendering is gated by a params-coverage check (V11): `collect_uncovered_params`
(`resolution/graph_builder.py`) runs at the generation boundary and aborts if a
wired module input references a params key that no JSON input file will carry.
Surfaced modeler names travel as `output_aliases` on the ComputationGraph and
override exit-point output filenames in the pipeline YAML (`generation/pipeline.py`).

## Package structure (post-refactor)

```
sysml_codegen/
  extraction/       Step 1 -- Parse .sysml into structured dataclasses
    extractor.py              SysMLDataExtractor: load models, extract calc defs
    usage_extractor.py        CalcUsages (CalcUsageData) and their bindings
    hierarchy_resolver.py     Redefinitions, aggregation expressions, design overrides
    data_models.py            CalculationDefinitionData, RedefinitionData, etc.

  orchestration/    Pipeline coordination: extract, resolve, generate
    pipeline_builder.py       build_pipeline_context(): multi-step orchestration
    output_registry_builder.py  build_output_registry(): 4-phase registration + Phase 3b confirm
    snapshot_context.py       build_pipeline_context_from_snapshot(): offline path
    pipeline_context.py       PipelineContext dataclass

  snapshot/         Extraction snapshot capture and offline rebuild
    capture.py / serializer.py / loader.py / graph_rebuild.py

  analysis/         Step 3 -- Dependency backtracking and parameter group derivation
    dependency_backtracker.py DependencyBacktracker: DFS + binding resolution
    parameter_groups.py       ParameterGroupDeriver: entry point grouping

  resolution/       Steps 4-6 -- Classify entries, build modules, sort
    graph_builder.py          build_computation_graph(), _classify_entry_points()
    models.py                 ComputationGraph, PipelineModule, EntryPoint

  generation/       Step 7 -- Render Python, YAML, JSON from the graph
    pipeline.py / modules.py / schemas.py / stencils.py / entry_point.py

  core/             Shared utilities (OutputRegistry, qualified_names, models)

  cli/              generate (--models | --from-snapshot) and snapshot subcommands
```

See [02-orchestration.md](02-orchestration.md) for orchestration detail.

## Navigation index

### Core pipeline (Steps 1-7)

| Doc | Topic | Key data models |
|-----|-------|-----------------|
| [01-extraction](01-extraction.md) | SysML model parsing: calc defs, usages, bindings, redefinitions | `CalculationDefinitionData`, `CalcUsageData`, `BindingInfo` |
| [02-orchestration](02-orchestration.md) | Pipeline builder: coordinating extract, resolve, generate | `PipelineContext` |
| [03-resolution-overview](03-resolution-overview.md) | Why input resolution is hard (270 combinations) | `BindingResolution` |
| [04-input-resolver](04-input-resolver.md) | Unified 5-strategy resolver | `InputSource`, `ResolutionContext` |
| [05-module-factory](05-module-factory.md) | The three calc module kinds as pure data transformers (constraint kinds: [28](28-constraint-lowering-and-catalog.md)) | `PipelineModule`, `ModuleKind` |
| [06-entry-point-classifier](06-entry-point-classifier.md) | Entry point classification: LIBRARY_DEFAULT, DESIGN_ATTRIBUTE, USAGE_LITERAL | `EntryPoint`, `EntryPointType` |
| [07-graph-assembly](07-graph-assembly.md) | Topological sort, validation, ComputationGraph assembly | `ComputationGraph` |
| [08-generation](08-generation.md) | Jinja2 rendering: Python, YAML, JSON | Templates |
| [09-data-models](09-data-models.md) | All data models and containment hierarchy | All |

### Deep-dive topics

| Doc | Topic |
|-----|-------|
| [10-output-registry](10-output-registry.md) | 4-phase registration: canonical channels, aliases, O(1) lookup |
| [11-analysis-backtracker](11-analysis-backtracker.md) | Dependency backtracking: tracing bindings to upstream sources |
| [12-virtual-binding-rewrite](12-virtual-binding-rewrite.md) | Template calc usage expansion and virtual binding construction |
| [13-aggregation-scoping](13-aggregation-scoping.md) | How `sum()` expressions are scoped to design instance paths |
| [14-expression-compiler](14-expression-compiler.md) | AST-to-Python compilation for calc def outputs |
| [15-naming-conventions](15-naming-conventions.md) | EQN, PQN, channel names, registry key formats |
| [16-computed-attributes](16-computed-attributes.md) | FORMULA and EXPOSE_PURE computed attribute classification |
| [17-parameter-group-deriver](17-parameter-group-deriver.md) | Grouping entry points into JSON input files |
| [18-literal-value-propagation](18-literal-value-propagation.md) | Carrying `:>>` literal values into JSON templates |
| [26-pipeline-module-migration](26-pipeline-module-migration.md) | REQ-PIPE-07 migration: PipelineModule field expansion |
| [27-snapshot-generation](27-snapshot-generation.md) | License-free generation from captured extraction snapshots |
