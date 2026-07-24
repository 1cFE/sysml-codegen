# Architecture Overview

sysml-codegen reads SysML v2 model files and produces a complete, runnable TEAx simulation pipeline: Python module wrappers, Pydantic schemas, JSON input templates, and pipeline YAML. The output is a working computation graph where each calculation defined in SysML becomes an executable module wired to its upstream dependencies and downstream consumers.

The pipeline transforms declarative SysML models into imperative Python through a 7-step process: extract structured data from SysML ASTs, build a typed output registry, trace dependencies via DFS, classify entry points, construct pipeline modules, topologically sort them, and render code via Jinja2 templates.

---

## Data Flow

```
SysML files (.sysml)
    |
    v
[Step 1] Extract         -- parse .sysml into data models           --> extraction/
[Step 2] Build registry   -- catalog outputs for O(1) lookup          --> core/
[Step 3] Trace deps       -- DFS + CalcUsage binding resolution       --> analysis/
[Step 4] Classify entries -- tag entry point types                    --> resolution/
[Step 5] Build modules    -- construct PipelineModules                --> resolution/
[Step 6] Sort modules     -- topological sort + validation            --> resolution/
[Step 7] Render code      -- Jinja2 templates produce output          --> generation/
    |
    v
Generated package
  modules/        -- TEAx module wrappers (one per calculation)
  handwritten/    -- Implementation stencils (user fills in logic)
  schemas/        -- Pydantic parameter group schemas
  inputs/         -- JSON input templates with default values
  pipelines/      -- Pipeline YAML wiring modules together
```

Orchestration (`orchestration/pipeline_builder.py`) coordinates these steps, threading intermediate data through a `PipelineContext`. See [02-orchestration](reference/02-orchestration.md) for the step-by-step sequence and ordering constraints.

Within Step 5, after the output registry is final, a **constraint-lowering phase** ([P1 RESOLVE], `analysis/constraint_lowering.py`) turns eligible modeled assertions into two further module kinds — `CONSTRAINT` (a lowered predicate) and `REPORT_AGGREGATOR` (the run-report roll-up) — and assembles the `ConstraintCatalog` embedded on the graph. A constraint-free model produces neither and a byte-identical graph. See [28-constraint-lowering-and-catalog](reference/28-constraint-lowering-and-catalog.md).

There is a second, license-free path into the same pipeline. `sysml-codegen snapshot` captures a versioned extraction snapshot from live models (`capture_snapshot` in `snapshot/capture.py` -- this capture step needs the live syside license). `generate --from-snapshot` (mutually exclusive with `--models`) then rebuilds the same `PipelineContext` from that JSON via `build_pipeline_context_from_snapshot` (`orchestration/snapshot_context.py`) -- Steps 2-7 run unchanged, with no license at runtime. The snapshot format carries a `snapshot_format_version` that hard-errors on mismatch. See [27-snapshot-generation](reference/27-snapshot-generation.md).

---

## Key Architectural Principles

### ComputationGraph as Single Source of Truth

The `ComputationGraph` (a Pydantic model in `resolution/models.py`) is the sole data structure that code generation consumes. It contains all pipeline modules, their inputs wired to upstream outputs or entry points, execution order, parameter group schemas, and surfaced output aliases (`output_aliases`, serialized with the graph). Generation templates receive only `ComputationGraph` fields -- no back-references to extraction models (REQ-PIPE-07). Generation is also gated by a params-coverage check (V11): `collect_uncovered_params` (`resolution/graph_builder.py`) runs at the generation boundary and aborts if a wired module input references a params key that no JSON input file will carry. See [09-data-models](reference/09-data-models.md).

### Typed Registries

SysML bindings reference the same output using different string formats depending on AST node type and context. The `OutputRegistry` resolves this ambiguity using four typed registries, each keyed by a `NewType` wrapper:

| Registry | Key Type | Resolves |
|----------|----------|----------|
| Scoped | `ScopedKey` (dotted hierarchy path) | CHAIN bindings via scope-prepend lookup |
| SysML QN | `SysMLQN` (`Package::Element::attr`) | REFERENCE bindings (library-qualified) |
| Alias | `ScopedKey` | `:>>` redefinition aliases and EXPOSE_PURE aliases |
| Scoped alias | `ScopedAliasKey` (`(scope, leaf)` tuple) | Part-def EXPOSE aliases, expanded per design instance |

All four map to `CanonicalChannel` (the unique PQN-format output name). Type-directed dispatch selects the correct registry based on binding type. Multi-hop EXPOSE aliases are registered tentatively and confirmed (or reverted to FORMULA) in a Phase 3b pass of registry build (`orchestration/output_registry_builder.py`). See [10-output-registry](reference/10-output-registry.md) and [15-naming-conventions](reference/15-naming-conventions.md).

### Producer Resolution Architecture

Positive input resolution -- answering "which real thing produces this value?" for every consumed input -- runs through one authority, `resolve_producer()` in `resolution/producer_resolution.py` (lifecycle Item 2). Three consumers build a request and read a result:

| Consumer | Module type | Call site | Policy |
|------|------------|----------|-----------|
| Calculation binding | CalcUsage | `analysis/dependency_backtracker.py` (during DFS) | LENIENT |
| Constraint actual | Constraint | `analysis/constraint_lowering.py` | STRICT |
| Aggregation term | Aggregation | `resolution/graph_builder.py` | LENIENT |

Each input resolves to `module_output` (wire to upstream channel), `design_attribute`/`entry_point` (user provides value via JSON), or -- under STRICT -- a raise. FORMULA modules are the one exception: they use a pre-computed attribute resolution map, not the resolver. See [04-producer-resolution](reference/04-producer-resolution.md), [03-resolution-overview](reference/03-resolution-overview.md), and [24-dual-resolution-architecture](reference/24-dual-resolution-architecture.md).

### Test-First with Real SysML Data

Conformance tests use real SysML fixture models (extracted via SysIDE) and verify pipeline behavior against extraction snapshots. No mock adapters or synthetic data. This ensures tests exercise the same code paths as production. Every tracked requirement maps to its conformance tests in [verification-matrix.md](verification-matrix.md), which carries the authoritative counts.

---

## Package Structure

```
sysml_codegen/
  extraction/          Step 1 -- Parse .sysml into structured dataclasses
    extractor.py                 SysMLDataExtractor: load models, extract calc defs
    usage_extractor.py           CalcUsages and their bindings
    hierarchy_resolver.py        Redefinitions, aggregation expressions, design overrides
    computed_attribute_extractor.py  FORMULA/EXPOSE classification
    expression_compiler.py       AST-to-Python compilation
    data_models.py               CalculationDefinitionData, RedefinitionData, etc.

  orchestration/       Pipeline coordination
    pipeline_builder.py          build_pipeline_context(): multi-step orchestration
    output_registry_builder.py   build_output_registry(): 4-phase registration + Phase 3b multi-hop EXPOSE confirm
    snapshot_context.py          build_pipeline_context_from_snapshot(): offline path
    pipeline_context.py          PipelineContext dataclass

  snapshot/            Extraction snapshot capture and offline rebuild
    capture.py                   capture_snapshot(): versioned snapshot from live models
    serializer.py / loader.py    Snapshot (de)serialization; format-version gate
    graph_rebuild.py             build_full_graph_from_snapshot(): rebuild extraction data offline

  analysis/            Step 3 -- Dependency backtracking and parameter groups
    dependency_backtracker.py    DependencyBacktracker: DFS + binding resolution
    parameter_groups.py          ParameterGroupDeriver: entry point grouping

  core/                Shared types and utilities
    output_registry.py           OutputRegistry: 3 typed registries
    identifier_types.py          NewType wrappers (ScopedKey, CanonicalChannel, etc.)
    qualified_names.py           Name construction helpers
    models.py                    BindingResolution, ChannelAlias

  resolution/          Steps 4-6 -- Classify entries, build modules, sort
    graph_builder.py             build_computation_graph(), topological sort
    producer_resolution.py       resolve_producer(): the one resolution authority
    producer_completeness.py     check_producer_completeness(): one-intended-producer check
    models.py                    ComputationGraph, PipelineModule, EntryPoint

  generation/          Step 7 -- Render Python, YAML, JSON from the graph
    pipeline.py                  Pipeline YAML generator
    modules.py                   Module wrapper generator
    schemas.py                   Pydantic schema generator
    stencils.py                  Implementation stencil generator
    entry_point.py               JSON template + parameter schema generator
    preservation.py              Smart regeneration (preserve user edits)

  cli/                 Command-line interface
    __init__.py                  generate (--models | --from-snapshot) and snapshot subcommands
```

---

## Reading Guide

### For newcomers

1. **Start here** -- this document for the high-level picture
2. **Prerequisites** -- [modeling-assumptions.md](modeling-assumptions.md) for the SysML conventions the pipeline depends on
3. **Pipeline walkthrough** (recommended order):
   - [00-pipeline-overview](reference/00-pipeline-overview.md) -- the 7-step pipeline with a running example
   - [01-extraction](reference/01-extraction.md) -- how SysML becomes structured data
   - [11-analysis-backtracker](reference/11-analysis-backtracker.md) -- dependency tracing via DFS
   - [03-resolution-overview](reference/03-resolution-overview.md) -- why input resolution is hard (270 combinations)
   - [06-entry-point-classifier](reference/06-entry-point-classifier.md) -- three entry point types
   - [05-module-factory](reference/05-module-factory.md) -- the three calc module kinds as pure data (constraint kinds in [28](reference/28-constraint-lowering-and-catalog.md))
   - [07-graph-assembly](reference/07-graph-assembly.md) -- topological sort and validation
   - [08-generation](reference/08-generation.md) -- Jinja2 rendering to Python, YAML, JSON
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

The following open issues are documented in the codebase. None block current pipeline functionality for well-formed SysML models.

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
- [Reference Documentation](reference/) -- 28 detailed design documents (docs 00-27)
