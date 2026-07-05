# 26 -- PipelineModule Migration: Achieving REQ-PIPE-07

## Motivation

[REQ-PIPE-07](00-pipeline-overview.md) states: "Generation SHALL produce output
exclusively from `ComputationGraph` — no back-references to extraction models."

Before this migration, only `pipeline.py` satisfied this requirement. The other
four generators consumed `CalculationDefinitionData` directly, which meant the
`ComputationGraph` was not the single source of truth for generation. Any change
to how graph building mapped CalcDef data had to be mirrored in the generators --
a drift hazard.

| Generator | File | Previously read from CalcDef | What it needs |
|-----------|------|------------------------------|---------------|
| Module wrapper | `modules.py` | `name`, `qualified_name`, `doc_comment`, inputs, outputs | Class name, docstrings, field descriptions |
| Stencil | `stencils.py` | `name`, `calc_expressions`, inputs, outputs | Function name, expression comments |
| Schema | `schemas.py` | `output_attributes` | Field names, types |
| Registry | `registry.py` | `qualified_name` | Import path derivation |
| Pipeline YAML | `pipeline.py` | Nothing | Already graph-only |

All five generators now consume `PipelineModule` exclusively. No generator
imports `CalculationDefinitionData`. REQ-PIPE-07 is satisfied.

## Requirements

| ID | Requirement | Status |
|----|-------------|--------|
| REQ-PMM-01 | `PipelineModule` SHALL carry all metadata needed by module wrapper generation (calc def name, qualified name, doc comment). | Satisfied: `generate_teax_module(module: PipelineModule)` -- no CalcDef arg |
| REQ-PMM-02 | `ModuleInput` and `ModuleOutput` SHALL carry `description` and `default_value` fields for template rendering. | Satisfied: template context built from ModuleInput/ModuleOutput fields only |
| REQ-PMM-03 | `PipelineModule` SHALL carry `calc_expressions` for stencil comment generation. | Satisfied: stencil template receives expressions from PipelineModule |
| REQ-PMM-04 | Migration SHALL produce byte-identical output compared to pre-migration baselines. | Satisfied: verified by `diff -r` on full generated output |
| REQ-PMM-05 | Migration SHALL proceed in phases: add fields, create variants, deprecate, remove. | Satisfied: no CalcDef imports remain in generators |

## Metadata Fields on PipelineModule

Six metadata fields were added to enable graph-only generation. These fields do
not affect pipeline wiring or execution semantics -- they are needed only for
human-readable output (docstrings, comments, Field descriptions).

| Field | Source | Used by | Location |
|-------|--------|---------|----------|
| `calc_def_name` | `CalculationDefinitionData.name` | `modules.py` (class name) | `PipelineModule.calc_def_name` |
| `calc_def_qualified_name` | `CalculationDefinitionData.qualified_name` | `registry.py` (import path) | `PipelineModule.calc_def_qualified_name` |
| `doc_comment` | `CalculationDefinitionData.doc_comment` | `modules.py` (docstring) | `PipelineModule.doc_comment` |
| `description` | `BaseAttributeInfo.description` | `modules.py` (field docs) | `ModuleInput.description`, `ModuleOutput.description` |
| `default_value` | `BaseAttributeInfo.default_value` | `modules.py` (field defaults) | `ModuleInput.default_value`, `ModuleOutput.default_value` |
| `calc_expressions` | `CalculationDefinitionData.calc_expressions` | `stencils.py` (comments) | `PipelineModule.calc_expressions` |

These fields are populated during graph building in `_build_pipeline_module()`,
`_build_computed_attr_module()`, and `_build_aggregation_module()`.

## How the Migration Was Executed

### Phase 1: Add fields to PipelineModule / ModuleInput / ModuleOutput

The 6 fields were added as `Optional[str]` / `Optional[list[str]]` with `None`
defaults. Graph builder functions populate them at construction time. Existing
generators continued to use CalcDef directly -- no behavior change.

### Phase 2: Create `_from_graph()` generator variants

For each generator, a parallel function was created that takes `PipelineModule`
instead of `CalculationDefinitionData`:

```python
def generate_teax_module_from_graph(module: PipelineModule, ...) -> str:
    # Build context dict from PipelineModule fields only
```

Both old and new variants produced identical output (verified by diff).

### Phase 3: Switch call sites and collapse variants

All call sites in the orchestrator were switched to the `_from_graph()` variants.
The old CalcDef-consuming functions were removed, and the `_from_graph` variants
were renamed to be the primary API. Backward-compatible aliases remain (e.g.,
`generate_teax_module_from_graph = generate_teax_module`).

### Phase 4: Remove CalcDef imports from generators

All `CalculationDefinitionData` imports were removed from the generation package.
No generator references extraction models. REQ-PIPE-07 is fully satisfied.

Note: `PipelineContext.calc_defs` still exists because it is consumed by analysis
and resolution stages (backtracker, graph builder). This is outside the scope of
REQ-PIPE-07, which constrains only generation.

## Risk: Metadata Drift

The 6 metadata fields are copied from CalcDef at graph-build time. If extraction
changes field names or semantics, the copy must be updated. Conformance tests
should verify that `PipelineModule.calc_def_name == calc_def.name` for every
module in the graph.

## Related Documents

- **Upstream**: [09-data-models](09-data-models.md) (PipelineModule definition), [05-module-factory](05-module-factory.md) (populates modules)
- **Downstream**: [08-generation](08-generation.md) (consumes modules for rendering)
- **Architecture**: [00-pipeline-overview](00-pipeline-overview.md) (REQ-PIPE-07), [07-graph-assembly](07-graph-assembly.md) (ComputationGraph assembly)
- **Extraction**: [01-extraction](01-extraction.md) (CalculationDefinitionData source)
