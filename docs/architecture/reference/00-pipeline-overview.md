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
| REQ-PIPE-01 | The pipeline SHALL produce exactly one [ComputationGraph](09-data-models.md#resolution-models) from a set of SysML model files. | `project()` (`elaboration/project.py`) returns one graph per instance graph; `ExactPipelineContext.computation_graph` re-derives it and refuses a graph its receipt disagrees with |
| REQ-PIPE-02 | Every [ModuleInput](09-data-models.md#resolution-models) SHALL be wired to exactly one source: `module_output` or `entry_point`. | `all(mi.source.source_type in {"module_output","entry_point"} for m in graph.modules for mi in m.inputs)` |
| REQ-PIPE-03 | Every `module_output` reference SHALL resolve to a declared output channel. | Projection claims each channel name exactly once (`_claim_channel`) and refuses a producer reference with no output (`SI_EDGE_DANGLING`, `elaboration/project.py:418-427`) |
| REQ-PIPE-04 | `execution_order` SHALL be a valid topological sort -- no module reads from a module that executes later. | `for m in modules: for i in m.inputs: if i.source.source_type == "module_output": assert producer.execution_order < m.execution_order` |
| REQ-PIPE-05 | Every [EntryPoint](06-entry-point-classifier.md) SHALL be classified as exactly one of {`LIBRARY_DEFAULT`, `DESIGN_ATTRIBUTE`, `USAGE_LITERAL`}. | `all(ep.entry_type in EntryPointType for g in graph.entry_point_groups for ep in g.parameters)`. The type is decided where the entry point is minted (`elaboration/project.py`, `_source_for_edge` / `_unbound_source`), not by a later classification pass |
| REQ-PIPE-06 | The graph SHALL tag each module with its `module_kind`; a calc-bearing model includes `CALCULATION`, `FORMULA`, and `AGGREGATION` modules. | `PipelineModule.module_kind` (`resolution/models.py`), checked per family. The two constraint-execution families `CONSTRAINT` / `REPORT_AGGREGATOR` appear when constraints are lowered (see [28](28-constraint-lowering-and-catalog.md)) |
| REQ-PIPE-07 | Generation SHALL produce output exclusively from `ComputationGraph` -- no back-references to extraction models. Requires PipelineModule expansion (see [26](26-pipeline-module-migration.md)). | All templates receive only `ComputationGraph` fields |

## The route

There is one public route from a model to a package, and it constructs one way.

```
SysML files                        v6 instance-graph snapshot
    |                                        |
    v                                        v
[1] Parse            SysMLDataExtractor      load + validate envelope   --> 27
    |                                        |
    v                                        v
[2] Elaborate        one attribute node per modelled value occurrence   --> (elaboration/)
    |
    v
   InstanceGraph  ── sealed into an ExactPipelineContext with a receipt  --> 02
    |
    v
[3] Project          render public identifiers, classify already-resolved
                     sources, order the modules                          --> 06, 07, 15
    |
    v
   ComputationGraph  (resolution/models.py -- the generation seam)       --> 09
    |
    v
[4] Render code      Jinja2 templates produce output                     --> 08
    |
    v
[5] Seal             ModelContract + PackageContract over final bytes    --> 29
    |
    v
Generated package (modules/, schemas/, inputs/, pipelines/, handwritten/, contracts/)
```

*(Numbers in the right column reference document files in this directory, e.g., "01" =
[01-extraction.md](01-extraction.md).)*

**Semantics are complete before projection runs.** The elaborator resolves every reference
against typed node identity — occurrence enumeration, never qualified-name string surgery — and
hands projection a graph in which every consumer already points at the node that supplies it.
Projection only renders names, classifies what elaboration already resolved, and orders the
result (`elaboration/project.py:1-6`). That split is why a wiring question has exactly one place
to be answered.

The resolution mechanism is one semantic-owner walk followed by exact indexes. For occurrence
sources, `ContainmentAddress` records the closed owner and containment steps and `OccurrenceIndex`
instantiates that address only inside the consumer domain. For calculation results, the
calculation-output producer index records the usage declaration, exact scope, calculation node,
and result port. Neither path retries a nearest, descendant, root, or globally sole candidate.
`tests/conformance/test_occurrence_domain_derivation.py` and
`tests/conformance/test_occurrence_calc_domain_derivation.py` are the real-model matrices.

Live models and admitted sources also share one public evidence conversion boundary:
`elaborate_loaded_extractor` turns an upstream `SemanticEvidenceError` into the exact
`SI_EVIDENCE_INCOMPLETE` diagnostic. Exact primitive typing and unsupported indexed-source refusal
finish before an `InstanceGraph` is admitted. See
`tests/conformance/test_expression_evidence_integrity.py` and
`tests/conformance/test_feature_typing_integrity.py`.

Generation keeps the sealed graph authoritative too. The registry's exported seams accept the graph,
derive the complete root-output wrapper set themselves, and reject an unsupported token as
`EXIT_POINT_TYPE_UNSUPPORTED` before output mutation. No caller-supplied wrapper set exists. See
[20-module-registry-generation](20-module-registry-generation.md).

**Two sources, one authority.** `--models` and `--from-snapshot` are two ways to obtain the
instance graph, not two implementations of the pipeline. Both seal into an
`ExactPipelineContext` whose receipt binds the sealed graph to what it projects to, and
`run_codegen` (`cli/__init__.py:956`) is the single public entry point — there is no flag,
environment variable, or config field that selects an authority. See
[02-orchestration](02-orchestration.md).

**The offline source is the v6 instance-graph snapshot.** `sysml-codegen snapshot` admits the
sources, elaborates them once, and seals the graph into an envelope (this capture needs the live
syside license); `generate --from-snapshot` loads that envelope license-free. A v5 extraction
snapshot is refused by name at load. See [27-snapshot-generation](27-snapshot-generation.md).

**What the legacy route is now: gone.** The string-resolution stack this document used to
describe — `orchestration/pipeline_builder.py`, `analysis/`'s backtracker and parameter groups,
`resolution/graph_builder.py`, `resolution/producer_resolution.py`, `core/output_registry.py`,
and the v5 snapshot loader/serializer/rebuild — was deleted by the Item 7 retirement
(2026-08-12, `19072ad` / `82c7951` / `882fc8d` / `3071fba`). Two conformance nodes now pin the
**absence**: `test_public_authority_switch.py` checks that the construction closure reaches no
legacy authority and that the modules do not exist, and
`tests/unit/test_elaboration_import_boundaries.py` checks that the CLI names none of them.
Documents 03, 04, 05, 07, 10, 11, 12, 13, 17, and 24 describe that deleted stack and open with
a historical banner; 25 describes `extraction/hierarchy_resolver.py`, which survived the
retirement but is off the shipped route.

## Running example: battery_pack cost_model

Trace a single calculation through the route. The library defines
`BatteryPackCostCalc` (5 inputs, 5 outputs). The design instantiates it:

```
SolarBatteryDesign > solar_battery_plant > battery_system > battery_pack > cost_model
```

### [1] Parse ([detail](01-extraction.md))

`SysMLDataExtractor` loads the model and extracts the calculation definitions
(`orchestration/elaborated_pipeline.py:46-57`). This is the same extractor the
tree has always used, and it is the only step that needs a syside licence.

### [2] Elaborate

`elaborate()` (`elaboration/elaborate.py`) turns the loaded model into an
`InstanceGraph`: **one attribute node per modelled value occurrence**, with consumers
holding typed node references rather than strings. Three things follow that matter to a
reader coming from the legacy description:

- **Occurrences are enumerated, not multiplied.** A child declared `part cell [3]` produces
  three occurrence nodes, each with its own attribute nodes, and an aggregation over them
  expands into three terms. There is no `count * child.attribute` rewrite.
- **There is no lookup table to miss.** Where the legacy route asked a registry "which
  channel does the string `cost_model.total_cost` mean, read from here?", the elaborator
  resolves the reference against the occurrence that declares it. A reference that cannot be
  resolved is a typed refusal, not a fall-through to an entry point.
- **A model that does not elaborate cleanly is refused**, with `ElaborationError` carrying
  readiness findings and `ElaborationDiagnosticError` carrying validation diagnostics. The two
  classes stay distinct all the way to the CLI log — collapsing them would lose which gate
  refused.

### [3] Project ([entry points](06-entry-point-classifier.md) | [assembly order](07-graph-assembly.md))

`project()` (`elaboration/project.py`) renders the resolved graph onto the
[ComputationGraph](09-data-models.md#resolution-models) seam. For `cost_model`:

| Input | Wiring | Public key |
|---|---|---|
| `capacity_kwh` | entry point, `DESIGN_ATTRIBUTE` | the supplying attribute's display path, occurrence index included |
| `chemistry_factor` | entry point, `DESIGN_ATTRIBUTE` | as above |
| `cost_per_kwh` | entry point, `LIBRARY_DEFAULT` (150.0) | `{consumer}__cost_per_kwh` |
| `fab_factor` | entry point, `LIBRARY_DEFAULT` (0.05) | `{consumer}__fab_factor` |
| `install_factor` | entry point, `LIBRARY_DEFAULT` (0.10) | `{consumer}__install_factor` |

An input supplied by an upstream calculation wires to that module's output channel instead.
Two consumers reading the *same* modelled attribute share one key — the key names the
attribute that supplies the value, not the formal that consumes it. Groups are named after the
file that **declares** the owner node. Both rules, with their measured consequences, are in
[06-entry-point-classifier](06-entry-point-classifier.md).

Projection also orders the modules (REQ-PIPE-04), claims each channel name exactly once, and
refuses on a rendering collision rather than letting two distinct things render as one name.

**Constraints.** Eligible modelled assertions become `CONSTRAINT` modules and the
`ConstraintCatalog` embedded on the graph. A `REPORT_AGGREGATOR` module is emitted **only when
there is at least one constraint output** (`elaboration/project.py:887`); the legacy route
emitted one whenever the constraint pathway ran at all, including for a model that asserts
nothing. A constraint-free model produces neither family. See
[28-constraint-lowering-and-catalog](28-constraint-lowering-and-catalog.md) for the catalog's
shape, and read its lowering half as a description of `analysis/constraint_lowering.py`, which
is not the public route.

### [4] Render code ([detail](08-generation.md))

The [ComputationGraph](09-data-models.md#resolution-models) feeds Jinja2 templates
to produce: `modules/*.py`, `handwritten/*_impl.py`, `pipelines/*.yaml`,
`inputs/*.json`, and `schemas/*.py`.

Rendering is gated by four checks that all run **before** any output is written or cleared
(`cli/__init__.py:1042-1060`): constraint name safety, duplicate output paths, params coverage
(V11 — `collect_uncovered_params`, `resolution/uncovered_params.py`, aborts if a wired module
input references a params key no JSON input file will carry), and registry class-name
collisions. Fail-before-mutate is the point: a refusal leaves the target tree exactly as it was.
Surfaced modeler names travel as `output_aliases` on the ComputationGraph and override
exit-point output filenames in the pipeline YAML (`generation/pipeline.py`).

### [5] Seal ([detail](29-contracts-and-sealing.md))

Generation ends by sealing the package: a `ModelContract` over the graph's semantic identity
and a `PackageContract` over the final on-disk bytes, on the live and from-snapshot paths
alike.

## Package structure

The public route, in the order it runs:

```
sysml_codegen/
  extraction/       [1] Parse
    extractor.py              SysMLDataExtractor: load models, extract calc defs
    expression_compiler.py    SysIDE AST -> ExpressionIR -> Python string
    source_manifest.py        admit_sources(): staged, verified source admission (capture)

  elaboration/      [2] Elaborate, [3] Project
    elaborate.py              elaborate(): loaded model -> InstanceGraph
    graph.py / identity.py    InstanceGraph and the typed node identities
    occurrence.py             occurrence enumeration
    project.py                project(): InstanceGraph -> ComputationGraph

  orchestration/
    elaborated_pipeline.py    load + elaborate, live and from admitted sources
    exact_pipeline_context.py ExactPipelineContext: sealed graph + projection receipt

  snapshot/
    envelope.py               the v6 instance-graph snapshot: build, seal, load
    instance_graph.py         the graph codec the envelope and the context share
    capture.py                capture_instance_graph_snapshot(): admit, elaborate, seal

  resolution/
    models.py                 ComputationGraph, PipelineModule, EntryPoint
    uncovered_params.py       the V11 params-coverage collector

  generation/       [4] Render Python, YAML, JSON from the graph
    pipeline.py / modules.py / schemas.py / stencils.py / entry_point.py / registry.py

  contracts/        [5] Seal: ModelContract (semantic) + PackageContract (physical)

  core/             Shared identifiers and utilities (qualified_names, identifier_types)

  cli/              generate (--models | --from-snapshot), snapshot, seal subcommands
```

Deleted by the Item 7 retirement and no longer in the tree:
`orchestration/pipeline_builder.py`, `orchestration/snapshot_context.py`, `analysis/`'s
backtracker, parameter groups and constraint lowering, `resolution/graph_builder.py`,
`resolution/producer_resolution.py`, `core/output_registry.py`, and the v5 snapshot
`loader.py` / `serializer.py` / `graph_rebuild.py`. `analysis/` now holds one module,
`source_referent.py`; `orchestration/pipeline_context.py` survives as the
`SysMLParsingError` / `CodeGenerationError` re-export point and carries no `PipelineContext`.

See [02-orchestration.md](02-orchestration.md) for the public surface and its pins.

## Navigation index

### Core pipeline

| Doc | Topic | Key data models |
|-----|-------|-----------------|
| [01-extraction](01-extraction.md) | SysML model parsing: calc defs, usages, bindings, redefinitions | `CalculationDefinitionData`, `CalcUsageData`, `BindingInfo` |
| [02-orchestration](02-orchestration.md) | The public surface: one entry point, two sources, one receipt | `ExactPipelineContext`, `ProjectionReceipt` |
| [03-resolution-overview](03-resolution-overview.md) | Why input resolution is hard (270 combinations) | `BindingResolution` |
| [04-producer-resolution](04-producer-resolution.md) | Unified 5-strategy resolver | `InputSource`, `ResolutionContext` |
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
| [19-ast-dispatch-invariant](19-ast-dispatch-invariant.md) | FCE-before-OE AST dispatch ordering, and the totality generalization |
| [20-module-registry-generation](20-module-registry-generation.md) | Import paths and module-type derivation for the generated registry |
| [21-pipeline-yaml-generation](21-pipeline-yaml-generation.md) | Channel formats, type rules, and the exit-point filename override |
| [22-output-schema-rules](22-output-schema-rules.md) | `MultiOutput` versus `RootModel`, field names, type mapping |
| [23-smart-regen-preservation](23-smart-regen-preservation.md) | Signature comparison and the six-case regeneration decision tree |
| [24-dual-resolution-architecture](24-dual-resolution-architecture.md) | One resolution authority, called at two pipeline stages |
| [25-hierarchy-resolver](25-hierarchy-resolver.md) | `:>>`, multiplicity, and `sum()` extraction into typed structures |
| [27-snapshot-generation](27-snapshot-generation.md) | The v6 instance-graph snapshot: what it seals, what it can prove |
| [28-constraint-lowering-and-catalog](28-constraint-lowering-and-catalog.md) | Lowering eligible modeled assertions to constraint modules and assembling the catalog |
| [29-contracts-and-sealing](29-contracts-and-sealing.md) | Package integrity: semantic `ModelContract`, physical seal, emitted verifier |
| [30-diagnostic-severity](30-diagnostic-severity.md) | Extraction-diagnostic severity: writer-set field, blocking vs advisory, fail-closed skew |

**Reading the index after the retirement.** Documents 03, 04, 05, 07, 10, 11, 12, 13, 17, and
24 describe the string-resolution stack that was deleted, and open with a historical banner
saying so. They are accurate about the code that was removed; they are not descriptions of what
the product does. Document 09 is mixed and carries a scoped banner naming which model rows are
live and which are history. Document 25's subject, `extraction/hierarchy_resolver.py`, is still
in the tree but is not on the shipped route.
