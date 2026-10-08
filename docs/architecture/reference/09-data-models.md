# 09 — Data Models Reference

The exact route consumes the models below. Source definitions own field types and defaults; this reference describes their responsibilities and identity boundaries. [The verification matrix](../verification-matrix.md#dm) records current and retired obligations.

## Data Flow

```text
SysML → CalculationDefinitionData + parser evidence
      → InstanceGraph → ComputationGraph → generated package/contracts
v6 envelope → InstanceGraph ────────┘
```

## Name Type Wrappers

`core/identifier_types.py` retains `SysMLQN`, `EQN`, `PQN`, `CanonicalChannel`, `ScopedKey`, and `ScopedAliasKey` NewTypes and the `make_scoped_key`/`make_canonical_channel` constructors. These describe name formats used in rendering; modeled source resolution uses declaration UUIDs and occurrence identity. There is no runtime output-registry dictionary to enforce. Model fields that remain `str` are not silently reclassified as typed wrappers. See [15-naming-conventions](15-naming-conventions.md).

## Extraction Models

`AttributeInfo` is a dataclass extending Agentic's `BaseAttributeInfo` (`extraction/data_models.py`). It adds Python type, description, source line, optionality, a retained optional unit field, and `element_id: UUID | None`. The unit field is not populated by guessing from comments, descriptions, or type names.

`CalculationDefinitionData` is a dataclass in the same file. It retains names, inputs/outputs, docs, source path/line/hash, and exact UUID sidecars: `element_id`, `output_expression_asts_by_id`, `all_member_ids`, `member_expressions_by_id`, and `member_names_by_id`. AST sidecars are in-memory extraction facts; v6 seals the normalized instance graph. See [14-expression-compiler](14-expression-compiler.md).

## Core Models

`InstanceGraph` and its attribute/calculation/constraint/occurrence nodes live in `elaboration/graph.py`. References identify concrete modeled occurrences before Python names are rendered. Name/path helpers live in `core/identifier_types.py`; see [15](15-naming-conventions.md) and [20](20-module-registry-generation.md).

## Resolution Models

All models in this section are Pydantic models in `resolution/models.py`.

- `ComputationGraph`: `modules`, `entry_point_groups`, `execution_order`, and serialized `output_aliases`. Its `fallback_entry_points` and `constraint_catalog` fields are excluded from the plain parent dump but included in the exact-context receipt's semantic digest.
- `PipelineModule`: name/type, inputs/outputs, execution order, required `module_kind`, compilability, optional compiled expression/output schema/auto-implementation context, and source/definition metadata. Definition names may be absent on constraint/report modules.
- `ModuleKind`: `CALCULATION`, `FORMULA`, `AGGREGATION`, `CONSTRAINT`, `REPORT_AGGREGATOR`.
- `ModuleInput`: parameter name/type, an `InputSource`, optional description/default, and excluded constraint-formal identity.
- `ModuleOutput`: field name/type/channel, optional description/default/unit.
- `InputSource`: `source_type` selects `entry_point` or `module_output`; the former carries group/key and the latter the producer channel.
- `EntryPoint`: qualified/simple names, `EntryPointType`, default/source/group/Python type, parser-native `unit_text`, and unresolved-default kind. `EntryPointType` is `LIBRARY_DEFAULT`, `DESIGN_ATTRIBUTE`, or `USAGE_LITERAL`.
- `ParameterGroup`: name, class name, declaring source file, and parameters; it derives schema and JSON filenames.
- `OutputAlias`: alias name, canonical channel, instance path, and `part_def`/`part_usage` provenance. Aliases refer to declared graph channels. See [16-computed-attributes](16-computed-attributes.md) and [21-pipeline-yaml-generation](21-pipeline-yaml-generation.md).

`ConstraintCatalog` contains four row lists: `source_records`, `usage_records`, `concrete_entries`, and `excluded_records`, plus a fingerprint over those lists. Projection derives it from the elaborated constraint domain. Generation consumes the embedded graph catalog; missing rows or a changed fingerprint refuse before output mutation. The catalog retains non-executed usages so reporting cannot imply assessment that never happened. See [29-contracts-and-sealing](29-contracts-and-sealing.md).

## Orchestration Model

`ExactPipelineContext` (`orchestration/exact_pipeline_context.py`) retains sealed instance-graph bytes and an immutable `ProjectionReceipt`. Every graph read decodes, projects, and verifies the receipt. `orchestration/pipeline_context.py` retains only error re-exports. See [02-orchestration](02-orchestration.md).

## Concrete Example

Keyword construction is required for Pydantic models. This two-module graph demonstrates both source kinds:

```python
from sysml_codegen.resolution.models import (
    ComputationGraph, InputSource, ModuleInput, ModuleKind, ModuleOutput, PipelineModule,
)

graph = ComputationGraph(
    modules=[
        PipelineModule(
            name="cost", module_type="CostModule", module_kind=ModuleKind.CALCULATION,
            calc_def_name="Cost", calc_def_qualified_name="Library::Cost",
            inputs=[ModuleInput(param_name="x", python_type="float",
                source=InputSource(source_type="entry_point", param_group="params", qualified_name="Design__x"))],
            outputs=[ModuleOutput(field_name="cost", python_type="float", channel_name="cost__cost")],
            execution_order=0,
        ),
        PipelineModule(
            name="total", module_type="TotalModule", module_kind=ModuleKind.AGGREGATION,
            inputs=[ModuleInput(param_name="cost", python_type="float",
                source=InputSource(source_type="module_output", producer_channel="cost__cost"))],
            outputs=[ModuleOutput(field_name="root", python_type="float", channel_name="total__root")],
            execution_order=1,
        ),
    ], entry_point_groups=[], execution_order=["cost", "total"],
)
```

## Related Documents

[Extraction](01-extraction.md), [orchestration](02-orchestration.md), [generation](08-generation.md), [expression compilation](14-expression-compiler.md), and [preservation](23-smart-regen-preservation.md).
