# Architecture Overview

sysml-codegen reads SysML v2 model files and produces a complete, runnable TEAx simulation pipeline: Python module wrappers, Pydantic schemas, JSON input templates, and pipeline YAML. The output is a working computation graph where each calculation defined in SysML becomes an executable module wired to its upstream dependencies and downstream consumers.

The pipeline transforms declarative SysML models into imperative Python in two halves. The front half **elaborates**: it turns the parsed model into an instance graph with one attribute node per modelled value occurrence, resolving every reference against typed node identity. The back half **projects and renders**: it renders that graph's public identifiers onto a `ComputationGraph` and feeds Jinja2 templates. Semantics are complete before rendering starts.

---

## Data Flow

```
SysML files (.sysml)                v6 instance-graph snapshot (.json)
    |                                        |
    v                                        v
[1] Parse             extraction/    [1'] Load + validate envelope    snapshot/envelope.py
    |                                        |
    +--------------------+-------------------+
                         v
[2] Elaborate    loaded model -> InstanceGraph                        elaboration/elaborate.py
                 one attribute node per modelled value occurrence
                         |
                         v
                 sealed into an ExactPipelineContext with a receipt    orchestration/
                         |
                         v
[3] Project      InstanceGraph -> ComputationGraph                    elaboration/project.py
                 render identifiers, classify resolved sources, order
                         |
                         v
[4] Render code  Jinja2 templates produce output                      generation/
                         |
                         v
[5] Seal         ModelContract + PackageContract over final bytes     contracts/
                         |
                         v
Generated package
  modules/        -- TEAx module wrappers (one per calculation)
  handwritten/    -- Implementation stencils (user fills in logic)
  schemas/        -- Pydantic parameter group schemas
  inputs/         -- JSON input templates with default values
  pipelines/      -- Pipeline YAML wiring modules together
  contracts/      -- Semantic model contract, physical seal, emitted verifier
```

`run_codegen` (`cli/__init__.py`) is the single public entry point and constructs one way. `--models` and `--from-snapshot` are two *sources* for the same authority, not two implementations: both seal into an `ExactPipelineContext` whose receipt binds the sealed instance graph to what it projects to. No flag, environment variable, or config field selects an implementation. See [02-orchestration](reference/02-orchestration.md).

Eligible modelled assertions become `CONSTRAINT` modules during projection, together with the `ConstraintCatalog` embedded on the graph. A `REPORT_AGGREGATOR` module is emitted only when there is at least one constraint output; a constraint-free model produces neither family. See [28-constraint-lowering-and-catalog](reference/28-constraint-lowering-and-catalog.md), whose lowering half describes `analysis/constraint_lowering.py` — a retiring component, not the public route.

The license-free path is the **v6 instance-graph snapshot**. `sysml-codegen snapshot` admits the sources, elaborates them once, and seals the resulting graph into an envelope (`capture_instance_graph_snapshot` in `snapshot/capture.py` — this capture step needs the live syside license). `generate --from-snapshot` loads that envelope with no license at runtime. A v5 extraction snapshot is refused at load, by name. See [27-snapshot-generation](reference/27-snapshot-generation.md).

### Where the legacy route went

The string-resolution stack — `orchestration/pipeline_builder.py`, `analysis/`, `resolution/graph_builder.py`, `core/output_registry.py`, and the v5 snapshot loader — is **present in the tree and importable, and unreachable from any public caller**. Its retirement is fully prepared and gated on owner acceptance. Two conformance nodes hold that state: `test_public_authority_switch.py::test_the_construction_path_reaches_no_legacy_authority_even_transitively` proves the construction closure is clean, and `::test_the_generation_half_still_reaches_v5_modules_and_that_residual_is_pinned` states the honest residual — the CLI's *import* closure still contains `pipeline_builder`, `snapshot.loader`, and `snapshot.graph_rebuild`, pinned by name so it cannot grow.

Reference documents 03, 04, 05, 07, 10, 11, 12, 13, 17, 24, and 25 describe that stack and open with a banner saying so. They remain accurate about the components they document.

---

## Key Architectural Principles

### ComputationGraph as Single Source of Truth

The `ComputationGraph` (a Pydantic model in `resolution/models.py`) is the sole data structure that code generation consumes. It contains all pipeline modules, their inputs wired to upstream outputs or entry points, execution order, parameter group schemas, and surfaced output aliases (`output_aliases`, serialized with the graph). Generation templates receive only `ComputationGraph` fields -- no back-references to extraction models (REQ-PIPE-07). Generation is also gated by a params-coverage check (V11): `collect_uncovered_params` (`resolution/uncovered_params.py`) runs at the generation boundary and aborts if a wired module input references a params key that no JSON input file will carry. See [09-data-models](reference/09-data-models.md).

### Identity, Not Strings

The elaborator resolves every reference against typed node identity — occurrence enumeration and declared members — and never by reconstructing or matching a qualified-name string. An `InstanceGraph` consumer holds a typed reference to the node that supplies it, so "which thing produces this value?" is answered once, where the model says it, rather than by a lookup table asked with a key built from the consumer's scope.

Two consequences a reader should carry into the reference documents:

- **An arrayed child is enumerated, not multiplied.** Three occurrences produce three attribute nodes, three entry points, and three terms in an aggregation over them.
- **An unresolvable reference is a typed refusal.** `ElaborationError` (readiness findings) and `ElaborationDiagnosticError` (validation diagnostics) stay distinct all the way to the CLI log, and projection refuses on a rendering collision rather than letting two distinct things render as one name.

The four-typed-registry design and the one-authority `resolve_producer()` ladder that this section used to describe belong to the retiring stack. They are documented, accurately, in [10-output-registry](reference/10-output-registry.md), [04-producer-resolution](reference/04-producer-resolution.md), [03-resolution-overview](reference/03-resolution-overview.md), and [24-dual-resolution-architecture](reference/24-dual-resolution-architecture.md), each of which now opens with a banner.

### Test-First with Real SysML Data

Conformance tests use real SysML fixture models (parsed via SysIDE) and verify pipeline behavior against committed snapshots and hand-derived expectations. No mock adapters or synthetic data. This ensures tests exercise the same code paths as production. Every tracked requirement maps to its conformance tests in [verification-matrix.md](verification-matrix.md), which carries the authoritative counts.

---

## Package Structure

The public route, in the order it runs:

```
sysml_codegen/
  extraction/          [1] Parse
    extractor.py                 SysMLDataExtractor: load models, extract calc defs
    expression_compiler.py       AST-to-Python compilation
    source_manifest.py           admit_sources(): staged, verified source admission (capture)
    data_models.py               CalculationDefinitionData, RedefinitionData, etc.

  elaboration/         [2] Elaborate, [3] Project
    elaborate.py                 elaborate(): loaded model -> InstanceGraph
    graph.py                     InstanceGraph, AttrNode, CalcNode, ConstraintNode
    identity.py                  typed node identities (NodeId, OccurrenceId, port ids)
    occurrence.py                occurrence enumeration
    project.py                   project(): InstanceGraph -> ComputationGraph

  orchestration/       Public construction
    elaborated_pipeline.py       load + elaborate, live and from admitted sources
    exact_pipeline_context.py    ExactPipelineContext: sealed graph + projection receipt

  snapshot/            The v6 instance-graph snapshot
    envelope.py                  build, seal, validate, load
    instance_graph.py            the graph codec envelope and context share
    capture.py                   capture_instance_graph_snapshot(): admit, elaborate, seal

  resolution/
    models.py                    ComputationGraph, PipelineModule, EntryPoint
    uncovered_params.py          the V11 params-coverage collector

  core/                Shared types and utilities
    identifier_types.py          NewType wrappers and module-type derivation
    qualified_names.py           Name construction helpers

  generation/          [4] Render Python, YAML, JSON from the graph
    pipeline.py                  Pipeline YAML generator
    modules.py                   Module wrapper generator
    schemas.py                   Pydantic schema generator
    stencils.py                  Implementation stencil generator
    entry_point.py               JSON template + parameter schema generator
    registry.py                  Module registry generator
    preservation.py              Smart regeneration (preserve user edits)

  contracts/           [5] Seal: semantic ModelContract, physical PackageContract, verifier

  cli/                 Command-line interface
    __init__.py                  generate (--models | --from-snapshot), snapshot, seal
```

Present in the tree, publicly unreachable, retirement prepared and gated on owner acceptance:

```
  orchestration/pipeline_builder.py, orchestration/snapshot_context.py
  analysis/            dependency_backtracker.py, parameter_groups.py, constraint_lowering.py
  resolution/          graph_builder.py, producer_resolution.py, producer_completeness.py
  core/output_registry.py
  snapshot/            loader.py, serializer.py, graph_rebuild.py (the v5 format)
```

---

## Reading Guide

### For newcomers

1. **Start here** -- this document for the high-level picture
2. **Prerequisites** -- [modeling-assumptions.md](modeling-assumptions.md) for the SysML conventions the pipeline depends on
3. **Pipeline walkthrough** (recommended order):
   - [00-pipeline-overview](reference/00-pipeline-overview.md) -- the route, with a running example
   - [01-extraction](reference/01-extraction.md) -- how SysML becomes structured data
   - [02-orchestration](reference/02-orchestration.md) -- the public surface: one entry point, two sources, one receipt
   - [06-entry-point-classifier](reference/06-entry-point-classifier.md) -- the three entry point types and how the exact route keys them
   - [27-snapshot-generation](reference/27-snapshot-generation.md) -- the v6 snapshot and what it can prove
   - [08-generation](reference/08-generation.md) -- Jinja2 rendering to Python, YAML, JSON
   - [29-contracts-and-sealing](reference/29-contracts-and-sealing.md) -- what a sealed package promises

   For the retiring string-resolution stack, read [03](reference/03-resolution-overview.md),
   [11](reference/11-analysis-backtracker.md), [05](reference/05-module-factory.md), and
   [07](reference/07-graph-assembly.md) — accurate about those components, not about the
   public route.
4. **Data models** -- [09-data-models](reference/09-data-models.md) as a reference companion to any of the above

### Deep dives by topic

| Topic | Documents |
|-------|-----------|
| Output registry and naming | [10](reference/10-output-registry.md), [15](reference/15-naming-conventions.md) |
| Resolution internals | [04](reference/04-producer-resolution.md), [24](reference/24-dual-resolution-architecture.md) |
| Template instantiation | [12](reference/12-virtual-binding-rewrite.md), [13](reference/13-aggregation-scoping.md) |
| Computed attributes | [16](reference/16-computed-attributes.md), [14](reference/14-expression-compiler.md) |
| Literal value propagation | [18](reference/18-literal-value-propagation.md) |
| AST dispatch invariant | [19](reference/19-ast-dispatch-invariant.md) |
| Generation details | [20](reference/20-module-registry-generation.md), [21](reference/21-pipeline-yaml-generation.md), [22](reference/22-output-schema-rules.md), [23](reference/23-smart-regen-preservation.md) |
| Hierarchy resolution | [25](reference/25-hierarchy-resolver.md) |
| PipelineModule migration | [26](reference/26-pipeline-module-migration.md) |
| Snapshot-driven generation | [27](reference/27-snapshot-generation.md) |
| Constraint execution & contracts | [28](reference/28-constraint-lowering-and-catalog.md), [29](reference/29-contracts-and-sealing.md) |

---

## Component Index

**Read this index with the cutover in mind.** C05, C06, C08–C19, C27, and X02 name components
of the retiring string-resolution stack (`extraction/computed_attribute_extractor.py`,
`extraction/hierarchy_resolver.py`, `core/output_registry.py`, `analysis/`,
`orchestration/pipeline_builder.py`, `resolution/graph_builder.py` and its resolver). Their
documents are accurate about those components and are not descriptions of the public route.
C02, C03, C04, C07, C20–C26, C28, C29, and X01 are live on the exact route; C01's models are
mixed and doc 09 says which are which.

| ID | Component | Doc | Package |
|----|-----------|-----|---------|
| C01 | Data Models | [09](reference/09-data-models.md) | `extraction/data_models.py`, `core/models.py`, `resolution/models.py` |
| C02 | Naming Conventions | [15](reference/15-naming-conventions.md) | `core/qualified_names.py`, `core/identifier_types.py` |
| C03 | SysMLDataExtractor | [01](reference/01-extraction.md) | `extraction/extractor.py`, `extraction/usage_extractor.py` |
| C04 | Expression Compiler | [14](reference/14-expression-compiler.md) | `extraction/expression_compiler.py` |
| C05 | Computed Attribute Extractor | [16](reference/16-computed-attributes.md) | `extraction/computed_attribute_extractor.py` |
| C06 | Hierarchy Resolver | [25](reference/25-hierarchy-resolver.md) | `extraction/hierarchy_resolver.py` |
| C07 | AST Dispatch Invariant | [19](reference/19-ast-dispatch-invariant.md) | Cross-cutting (C04, C05, C06) |
| C08 | Output Registry (Typed) | [10](reference/10-output-registry.md) | `core/output_registry.py` |
| C09 | Virtual Binding Rewrite | [12](reference/12-virtual-binding-rewrite.md) | `orchestration/pipeline_builder.py` |
| C10 | Aggregation Scoping | [13](reference/13-aggregation-scoping.md) | `orchestration/pipeline_builder.py` |
| C11 | DependencyBacktracker | [11](reference/11-analysis-backtracker.md) | `analysis/dependency_backtracker.py` |
| C12 | Producer Resolution | [04](reference/04-producer-resolution.md) | `resolution/producer_resolution.py` |
| C13 | ParameterGroupDeriver | [17](reference/17-parameter-group-deriver.md) | `analysis/parameter_groups.py` |
| C14 | Module Factory: CalcUsage | [05](reference/05-module-factory.md) | `resolution/graph_builder.py` |
| C15 | Module Factory: FORMULA | [05](reference/05-module-factory.md) | `resolution/graph_builder.py` |
| C16 | Module Factory: Aggregation | [05](reference/05-module-factory.md) | `resolution/graph_builder.py` |
| C17 | Entry Point Classification | [06](reference/06-entry-point-classifier.md) | `resolution/graph_builder.py` |
| C18 | Graph Assembly | [07](reference/07-graph-assembly.md) | `resolution/graph_builder.py` |
| C19 | Pipeline Builder | [02](reference/02-orchestration.md) | `orchestration/pipeline_builder.py` |
| C20 | Pipeline YAML Generator | [21](reference/21-pipeline-yaml-generation.md) | `generation/pipeline.py` |
| C21 | Module Wrapper Generator | [08](reference/08-generation.md) | `generation/modules.py` |
| C22 | Schema Generator | [22](reference/22-output-schema-rules.md) | `generation/schemas.py` |
| C23 | Stencil Generator + Smart Regen | [23](reference/23-smart-regen-preservation.md) | `generation/stencils.py`, `generation/preservation.py` |
| C24 | Module Registry Generator | [20](reference/20-module-registry-generation.md) | `generation/registry.py` |
| C25 | JSON Template + Schema Generator | [08](reference/08-generation.md) | `generation/entry_point.py` |
| C26 | PipelineModule Migration | [26](reference/26-pipeline-module-migration.md) | Cross-cutting (resolution + generation) |
| C27 | Typed Registry Design Intent | [10](reference/10-output-registry.md) | Cross-cutting (core + analysis + resolution) |
| C28 | Constraint Lowering & Catalog | [28](reference/28-constraint-lowering-and-catalog.md) | `analysis/constraint_lowering.py`, `generation/constraint_catalog.py`, `generation/predicate_compiler.py` |
| C29 | Contracts & Sealing | [29](reference/29-contracts-and-sealing.md) | `contracts/model_contract.py`, `contracts/seal.py`, `contracts/verify.py` |
| X01 | Type Mapping Consistency | [08](reference/08-generation.md) | `generation/type_mapping.py` |
| X02 | Resolution Consistency | [24](reference/24-dual-resolution-architecture.md) | Cross-cutting (C11, C12, C14-C16) |

---

## Known Limitations

The following open issues are documented in the codebase. Items 2, 3, and 6 are limitations of
the **retiring** extraction/resolution classifier; the exact route reaches those shapes by a
different mechanism and its behaviour on each has not been separately re-derived, so read them
as history rather than as current public limits. Items 1, 4, 5, and 7 are modelling- or
package-level and hold on either route.

1. **EXPOSE_COMPUTED pattern not supported.** Design attributes that combine a calc output reference with arithmetic (e.g., `= calc.output * 1.15`) are not handled. Workaround: extract to a CalcDef in `library/` -- the pipeline auto-implements simple arithmetic. See [16-computed-attributes](reference/16-computed-attributes.md).

2. **Inherited attribute misclassification.** The computed attribute classifier (`_classify_attribute_expression`) assumes a flat namespace. SysIDE resolves inherited attributes to their supertype QN, causing the namespace prefix check to fail. 5 of 6 test patterns are affected. Fix requires supertype chain walk. See [16-computed-attributes](reference/16-computed-attributes.md) Known Issues.

3. **Deeply-nested cross-scope REFERENCE bindings.** Step 1b normalization drops intermediate QN segments for 5+ segment paths, which may cause resolution failure. Idiomatic SysML uses import + `.` chain (CHAIN binding), not deep `::` paths (REFERENCE). A probe fixture exists but the edge case is not fully resolved.

4. **`sum()` is the only recognized aggregation function.** Other aggregation patterns (e.g., `max()`, `min()`, `avg()`) are not extracted. Models requiring these should use explicit CalcDefs.

5. **Two `BindingInfo` classes remain un-consolidated.** A local `@dataclass` in `extraction/` coexists with an upstream Pydantic `BaseModel` in `agentic-mbse`. They serve different purposes and the duplication is isolated behind `TYPE_CHECKING`.

6. **UNRESOLVABLE computed attribute classification is likely unreachable.** SysIDE always resolves attribute QNs for well-formed SysML, making the empty-QN fallback in Step 2d a defensive path. Retained as a safety net.

7. **Upstream agentic-mbse V2 validation rejects valid FORMULA expressions.** Tracked in the agentic-mbse package; does not affect the sysml-codegen pipeline directly.

---

## Verification

REQ-* tags are tracked across 32 requirement families; the [verification matrix](verification-matrix.md) summary carries the authoritative counts. A small remainder is marked UNTESTED there (design-only constraints or cross-cutting principles verified indirectly).

See [verification-matrix.md](verification-matrix.md) for the full REQ-to-test traceability matrix.

---

## Related Documents

- [Modeling Assumptions](modeling-assumptions.md) -- SysML conventions the pipeline depends on
- [Verification Matrix](verification-matrix.md) -- REQ-to-test traceability
- [Reference Documentation](reference/) -- 31 detailed design documents (docs 00-30)
