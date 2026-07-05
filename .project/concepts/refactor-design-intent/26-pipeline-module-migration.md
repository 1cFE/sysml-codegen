# 26 -- PipelineModule Migration: Making REQ-PIPE-07 Achievable

## The Problem

[REQ-PIPE-07](00-pipeline-overview.md) states: "Generation SHALL produce output
exclusively from `ComputationGraph` — no back-references to extraction models."
Today, only `pipeline.py` satisfies this. The other 4 generators still consume
`CalculationDefinitionData` directly:

| Generator | File | Reads from CalcDef | What it needs |
|-----------|------|-------------------|---------------|
| Module wrapper | `modules.py` | `name`, `qualified_name`, `doc_comment`, inputs, outputs | Class name, docstrings, field descriptions |
| Stencil | `stencils.py` | `name`, `calc_expressions`, inputs, outputs | Function name, expression comments |
| Schema | `schemas.py` | `output_attributes` | Field names, types |
| Registry | `registry.py` | `qualified_name` | Import path derivation |
| Pipeline YAML | `pipeline.py` | **Nothing** (gold standard) | Already graph-only |

This means the `ComputationGraph` is NOT the single source of truth for generation.
Any change to how graph building maps CalcDef data must be mirrored in the
generators — a drift hazard.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-PMM-01 | `PipelineModule` SHALL carry all metadata needed by module wrapper generation (calc def name, qualified name, doc comment). | `generate_teax_module(module: PipelineModule)` signature — no CalcDef arg |
| REQ-PMM-02 | `ModuleInput` and `ModuleOutput` SHALL carry `description` and `default_value` fields for template rendering. | Template context built from ModuleInput/ModuleOutput fields only |
| REQ-PMM-03 | `PipelineModule` SHALL carry `calc_expressions` for stencil comment generation. | Stencil template receives expressions from PipelineModule |
| REQ-PMM-04 | Migration SHALL produce byte-identical output compared to pre-migration baselines. | `diff -r` on full generated output |
| REQ-PMM-05 | Migration SHALL proceed in phases: add fields → create variants → deprecate → remove. | No CalcDef imports in generators after final phase |

## Missing Fields on PipelineModule

| Field | Currently on | Needed by | Proposed location |
|-------|-------------|-----------|-------------------|
| `calc_def_name` | `CalculationDefinitionData.name` | `modules.py` (class name) | `PipelineModule.calc_def_name` |
| `qualified_name` | `CalculationDefinitionData.qualified_name` | `registry.py` (import path) | `PipelineModule.qualified_name` |
| `doc_comment` | `CalculationDefinitionData.doc_comment` | `modules.py` (docstring) | `PipelineModule.doc_comment` |
| `description` | `BaseAttributeInfo.description` | `modules.py` (field docs) | `ModuleInput.description`, `ModuleOutput.description` |
| `default_value` | `BaseAttributeInfo.default_value` | `modules.py` (field defaults) | `ModuleInput.default_value` |
| `calc_expressions` | `CalculationDefinitionData.calc_expressions` | `stencils.py` (comments) | `PipelineModule.calc_expressions` |

All 6 fields are metadata — they do not affect pipeline wiring or execution
semantics. They are needed only for human-readable output (docstrings, comments,
Field descriptions).

## Migration Strategy

### Phase 1: Add fields to PipelineModule / ModuleInput / ModuleOutput

Add the 6 fields as `Optional[str]` / `Optional[list[str]]` with `None`
defaults. Populate them during graph building in `_build_pipeline_module()`,
`_build_computed_attr_module()`, and `_build_aggregation_module()`. Existing
generators continue to use CalcDef directly — no behavior change.

### Phase 2: Create `_from_graph()` generator variants

For each generator, create a parallel function that takes `PipelineModule`
instead of `CalculationDefinitionData`:

```python
def generate_teax_module_from_graph(module: PipelineModule, ...) -> str:
    # Build context dict from PipelineModule fields only
```

Both old and new variants produce identical output (verified by diff).

### Phase 3: Deprecate CalcDef-consuming variants

Switch all call sites in the orchestrator to use `_from_graph()` variants.
Mark old functions with `@deprecated`. Run full baseline comparison.

### Phase 4: Remove CalculationDefinitionData from PipelineContext

Remove `calc_defs` from `PipelineContext`. Remove CalcDef imports from all
generators. REQ-PIPE-07 is now satisfied.

## Impact on Other Documents

- [09-data-models](09-data-models.md): PipelineModule, ModuleInput, ModuleOutput
  field lists need 6 new fields
- [05-module-factory](05-module-factory.md): Factory functions populate new fields
- [08-generation](08-generation.md): Generators consume only PipelineModule
- [00-pipeline-overview](00-pipeline-overview.md): REQ-PIPE-07 fully achieved

## Risk: Metadata Drift

The 6 new fields are copied from CalcDef at graph-build time. If extraction
changes field names or semantics, the copy must be updated. Conformance tests
should verify that `PipelineModule.calc_def_name == calc_def.name` for every
module in the graph.

## Related Documents

- **Upstream**: [09-data-models](09-data-models.md) (PipelineModule definition), [05-module-factory](05-module-factory.md) (populates modules)
- **Downstream**: [08-generation](08-generation.md) (consumes modules for rendering)
- **Architecture**: [00-pipeline-overview](00-pipeline-overview.md) (REQ-PIPE-07), [07-graph-assembly](07-graph-assembly.md) (ComputationGraph assembly)
- **Extraction**: [01-extraction](01-extraction.md) (CalculationDefinitionData source)
