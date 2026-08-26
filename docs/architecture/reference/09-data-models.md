# 09 -- Data Models Reference

> **Status: live models only.** The exact route is the only authority. Everything documented
> here exists in the tree and is reachable from `run_codegen`.
>
> The rows for the types the 2026-08-12 retirement deleted (`BacktrackingResult`,
> `DesignAttributeData`, `DerivedParameterGroup`, `ParameterSource`, the `OutputRegistry`
> types, `PipelineContext`) were removed with the retired reference documents that linked
> into them; git history keeps both.

## Why This Document Exists
14 documents in this set link here as the canonical field reference. When a doc
says "see [09-data-models](09-data-models.md#resolution-models)," the reader
expects the definitive field list. If a field exists in the code but not here,
it's a doc bug. If a value is missing from an enum, someone will implement
the wrong case coverage (this happened: BindingType was originally documented
with wrong values, caught in Phase A validation).

## Requirements
| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-DM-01 | Every model referenced by another doc in this set SHALL appear here or have an explicit delegation link | Grep `09-data-models` refs; verify each anchor resolves |
| REQ-DM-02 | Every enum SHALL list ALL values with no omissions | Diff enum tables against source enum definitions |
| REQ-DM-03 | Field lists SHALL match source code (name, type, optionality) | Field-by-field comparison with dataclass/BaseModel defs |
| REQ-DM-04 | Every model SHALL state its parent class and source file location | All entries include `(type, file)` notation |
| REQ-DM-05 | At least one populated `ComputationGraph` example SHALL demonstrate both `entry_point` and `module_output` wiring | Example section present with 2+ modules |
| REQ-DM-06 | Models with dedicated docs SHALL link to those docs, not duplicate detail | Delegation links for aggregation terms, expression compiler, etc. |
| REQ-DM-07 | The data flow diagram SHALL show all pipeline stages and their primary I/O models | Diagram covers extraction → analysis → core → resolution → generation |
| REQ-DM-08 | The typed-registry enforced surface SHALL use NewType wrappers: the wrappers are genuine `NewType`s, the four `OutputRegistry` registry dicts are annotated `dict[NewType, NewType]`, and `make_scoped_key`/`make_canonical_channel` return their NewType (model fields remain `str` by design — `[DM08-MODEL-FIELD-TYPING]`) | `test_dm08_enforced_surface.py` (AST-scan) |

## Data Flow
```
SysML Files
  |
  v
[Extraction]   → CalculationDefinitionData (extraction/extractor.py; the only licensed step)
  |
  v
[Elaboration]  → InstanceGraph (AttrNode, CalcNode, ConstraintNode; elaboration/graph.py)
  |
  v
[Projection]   → ComputationGraph (PipelineModule, ParameterGroup, EntryPoint, OutputAlias;
                  elaboration/project.py → resolution/models.py)
  |
  v
[Generation]   → Python modules, YAML, JSON templates, sealed contracts
```

## Enums
Every value listed (REQ-DM-02). These are the most common source of doc bugs.
| Enum | Values | Source |
|------|--------|--------|
| `BindingType` | `CHAIN`, `REFERENCE`, `LITERAL`, `EXPRESSION`, `UNBOUND` | `agentic_mbse` |
| `Compilability` | `FULLY_COMPILABLE`, `PARTIALLY_COMPILABLE`, `MANUAL_REQUIRED`, `UNKNOWN` | `extraction/expression_compiler.py` |
| `ModuleKind` ¹ | `CALCULATION`, `FORMULA`, `AGGREGATION`, `CONSTRAINT`, `REPORT_AGGREGATOR` | `resolution/models.py` |
| `EntryPointType` | `LIBRARY_DEFAULT`, `DESIGN_ATTRIBUTE`, `USAGE_LITERAL` | `resolution/models.py` |

> ¹ `ModuleKind` is set once at `PipelineModule` construction and dispatched on at every
> generation seam (`resolution/models.py`, CONSTRAINT-EXEC Item 6). It replaced the two
> accreted Boolean flags `is_computed_attribute` / `is_aggregation` the module carried
> before. (The retired `ExpressionNodeType` enum — `BINARY_OP` / `UNARY_OP` / … — went
> with the `ExpressionAST` path in Item 13; the current IR is agentic-mbse's
> `ExpressionIR`, see [14-expression-compiler](14-expression-compiler.md).)

## Name Type Wrappers

The system uses 5+ name formats with incompatible semantics (REQ-DM-08).
Raw `str` fields prevent the type checker from catching format mismatches.
See [15-naming-conventions](15-naming-conventions.md) for format definitions.

Defined in `core/identifier_types.py`:

```python
from typing import NewType

SysMLQN = NewType('SysMLQN', str)                # "Package::Element" — extraction boundary only
EQN = NewType('EQN', str)                        # "Package__Element" — internal canonical form
PQN = NewType('PQN', str)                        # "EQN__param" — channel names, entry point QNs
CanonicalChannel = NewType('CanonicalChannel', str)  # PQN of output — registry values
ScopedKey = NewType('ScopedKey', str)            # dotted hierarchy — scoped/alias registry keys
ScopedAliasKey = NewType('ScopedAliasKey', tuple[str, str])  # structured (scope, leaf) — part-def EXPOSE / consumer-scoped aliases (Item 10)
```

`CanonicalChannel` wraps the PQN-format output channel name (e.g.,
`SBD__sbp__lcoe__lcoe_per_mwh`). It is the value type for all the typed registries.
Constructor: `make_canonical_channel(usage_eqn, attr_name)` — wraps `get_channel_name()`.

`ScopedKey` wraps the dotted hierarchy key used for scoped and alias registry lookups
(e.g., `solar_battery_plant.lcoe.lcoe_per_mwh`). Constructor: `make_scoped_key(usage_eqn, attr_name)`
— replaces `OutputRegistry.derive_key_c()`. Rejects strings containing `::`.

See 10-output-registry (retired doc; git history) for the full type system and [15-naming-conventions](15-naming-conventions.md) for identifier format definitions.

**Conversion boundary**: Raw SysML names (`SysMLQN`) are converted to `EQN` at extraction
time. All downstream indexes, lookups, and registrations use typed names only.

**Field format assignments.** The table below documents which semantic format each
field carries. At HEAD the NewType annotations are enforced on `OutputRegistry`
keys/values and the `make_*` constructors (`core/identifier_types.py`); the model
fields listed are still annotated `str` in their dataclass/BaseModel definitions
(a deliberate deferral, filed `[DM08-MODEL-FIELD-TYPING]`; REQ-DM-08 now pins the
enforced surface — `test_dm08_enforced_surface.py` — and its text names exactly that
surface, per the matrix). Fields with
no format constraint at all: `PipelineModule.name` (module name = lowered EQN,
could be typed later).

| Model | Field | Format |
|-------|-------|------|
| `CalculationDefinitionData` | `qualified_name` | `SysMLQN` |
| `ModuleOutput` | `channel_name` | `CanonicalChannel` |
| `EntryPoint` | `qualified_name` | `PQN` |
| `InputSource` | `producer_channel` | `CanonicalChannel \| None` |

## Extraction Models

**CalculationDefinitionData** (dataclass, `extraction/data_models.py`)
`name: str`, `qualified_name: str`, `doc_comment: str`, `calc_expressions: list[str]`,
`input_attributes: list[AttributeInfo]`, `output_attributes: list[AttributeInfo]`,
`references: list[str]`, `source_file: Path`, `source_line: int`, `source_hash: str`,
`output_expression_asts: dict[str, Any]`, `all_member_names: set[str]`,
`member_expressions: dict[str, Any]`.

**AttributeInfo** (dataclass, `extraction/data_models.py`, extends `BaseAttributeInfo`)
Inherited: `name`, `sysml_type`, `default_value`, `binding_type`, `is_input`, `is_output`.
Added: `python_type: str`, `description: str`, `unit: str | None`, `source_line: int`,
`is_optional: bool`.

*Delegated: expression compiler → [14](14-expression-compiler.md).*

## Core Models

*Delegated: Identifier types (SysMLQualifiedName, ModuleType, PythonModulePath, ElementQualifiedName) → [15](15-naming-conventions.md), [20](20-module-registry-generation.md).*

## Resolution Models

**ComputationGraph** (BaseModel, `resolution/models.py`)
`modules: list[PipelineModule]`, `entry_point_groups: list[ParameterGroup]`,
`execution_order: list[str]`, `output_aliases: list[OutputAlias]`.
The model also declares two `exclude=True` fields, both in-memory generation-boundary
artifacts kept out of the serialized graph (so a constraint-free corpus's committed baselines
stay byte-identical): `fallback_entry_points: set[str]` (Item 7) and
`constraint_catalog: ConstraintCatalog | None` (CONSTRAINT-EXEC Item 7 / D6 — the assembled
constraint catalog embedded on the graph, `None` when no constraint facts were admitted).
Both are omitted from the serialized set. `output_aliases` is the deliberate contrast (Item 11
/ REQ-DM-09): a genuine schema field with **no** `exclude`, so it serializes on every graph
(empty `[]` when the model has no EXPOSE_PURE derived attribute) and appears in the field-set
conformance test. `ComputationGraph.model_fields` therefore has 6 entries; the serialized set
is 4.

**ConstraintCatalog** (BaseModel, `resolution/models.py`)
`source_records: list[ConstraintCatalogSourceRecord]`, `concrete_entries:
list[ConstraintCatalogEntry]`, `fingerprint: str`. Assembled once from the pipeline context's
concrete constraints (eligible entries) and constraint facts (source records), fingerprinted
(sha256 of canonical JSON over the two lists), and set on the graph before generation — every
seam that needs catalog data reads it from the graph, never from the context (CONSTRAINT-EXEC
Item 7 / D6, "generation reads only the graph"). See
28-constraint-lowering-and-catalog (retired doc; git history).

**OutputAlias** (BaseModel, `resolution/models.py`)
`alias_name: str`, `canonical_channel: str`, `instance_path: str`,
`shape: Literal["part_def", "part_usage"]`. Property: `output_filename` →
`{instance_path}__{alias_name}.json`. One EXPOSE_PURE modeler name surfaced onto the
canonical channel the value already flows on (Item 11 / SC-7 / REQ-DM-09). `shape`
tags provenance: `part_def` from the `_scoped_alias` registry (shape A), `part_usage`
from an `expose_pure` channel alias (shape B). `canonical_channel` is read from the
registry, never re-derived (INV-2), and is validated to be a declared graph output
channel (INV-3). See [16-computed-attributes](16-computed-attributes.md) and
[21-pipeline-yaml-generation](21-pipeline-yaml-generation.md).

**PipelineModule** (BaseModel, `resolution/models.py`)
`name: str`, `module_type: str`, `inputs: list[ModuleInput]`, `outputs: list[ModuleOutput]`,
`execution_order: int`, `compilability: Compilability`, `compiled_expression: str | None`,
`module_kind: ModuleKind` (**required**), `output_schema_type: str | None`,
`auto_impl_context: dict | None`.
Metadata carried from the calc def:
`calc_def_name: str | None`, `calc_def_qualified_name: str | None`, `doc_comment: str | None`,
`calc_expressions: list[str] | None`, `source_file: str | None`, `source_line: int | None`.

`module_kind` is the module's family, set once at construction and dispatched on at every
generation seam (see [08-generation](08-generation.md)). It has five values —
`CALCULATION`, `FORMULA`, `AGGREGATION`, `CONSTRAINT`, `REPORT_AGGREGATOR` — and **replaced**
the two accreted Boolean flags `is_computed_attribute` / `is_aggregation` the module carried
before CONSTRAINT-EXEC Item 6. `CONSTRAINT` (a lowered modeled assertion) and
`REPORT_AGGREGATOR` (the run-report roll-up) are the two families the flag pair could not
name.

**ModuleInput** (BaseModel, `resolution/models.py`)
`param_name: str`, `python_type: str`, `source: InputSource`,
`description: str | None`, `default_value: float | int | str | bool | None`.

**ModuleOutput** (BaseModel, `resolution/models.py`)
`field_name: str`, `python_type: str`, `channel_name: str`,
`description: str | None`, `default_value: float | int | str | bool | None`,
`unit: str | None`.

**InputSource** (BaseModel, `resolution/models.py`)
`source_type: str` ("entry_point" | "module_output"), `param_group: str | None`,
`qualified_name: str | None`, `producer_channel: str | None`.

**EntryPoint** (BaseModel, `resolution/models.py`)
`qualified_name: str`, `simple_name: str`, `entry_type: EntryPointType`,
`default_value: float | None`, `source_calc_usage: str | None`,
`param_group: str | None`, `python_type: str`. Property: `json_field_name`.

**ParameterGroup** (BaseModel, `resolution/models.py`)
`name: str`, `class_name: str`, `source_file: Path`, `parameters: list[EntryPoint]`.
Properties: `json_filename`, `schema_filename`.

## Orchestration Model

**ExactPipelineContext** (`orchestration/exact_pipeline_context.py`)
The sealed instance-graph bytes plus a `ProjectionReceipt`: immutable, and every read
re-decodes, re-projects, and refuses a graph the receipt disagrees with. (The former
`PipelineContext` dataclass retired 2026-08-12; `orchestration/pipeline_context.py`
survives only as the `SysMLParsingError` / `CodeGenerationError` re-export point.)

## Concrete Example

2-module graph with both `entry_point` and `module_output` wiring (REQ-DM-05):

```python
ComputationGraph(modules=[
  PipelineModule(name="battery_pack__cost_model", module_type="BatteryPackCostCalcModule",
    inputs=[
      ModuleInput("capacity_kwh", "float",
        source=InputSource("entry_point", param_group="design_params",
          qualified_name="Design__battery_pack__capacity_kwh")),
      ModuleInput("cost_per_kwh", "float",
        source=InputSource("entry_point", param_group="library_params",
          qualified_name="BatteryPackCostCalc__cost_per_kwh")),
    ],
    outputs=[ModuleOutput("total_cost", "float", "battery_pack__cost_model__total_cost")],
    execution_order=0, module_kind=ModuleKind.CALCULATION,
    compilability=Compilability.FULLY_COMPILABLE,
    compiled_expression="capacity_kwh * cost_per_kwh"),
  PipelineModule(name="battery_system__total_cost", module_type="BatterySystemTotalCostModule",
    inputs=[
      ModuleInput("battery_cost", "float",
        source=InputSource("module_output",
          producer_channel="battery_pack__cost_model__total_cost")),
    ],
    outputs=[ModuleOutput("root", "float", "battery_system__total_cost__root")],
    execution_order=1, module_kind=ModuleKind.AGGREGATION),
], entry_point_groups=[
  ParameterGroup(name="design_params", class_name="DesignParams",
    source_file=Path("SolarBatteryDesign.sysml"), parameters=[
      EntryPoint("Design__battery_pack__capacity_kwh", "capacity_kwh",
        EntryPointType.DESIGN_ATTRIBUTE, default_value=100.0, param_group="design_params")]),
  ParameterGroup(name="library_params", class_name="LibraryParams",
    source_file=Path("BatteryPackCostCalc.sysml"), parameters=[
      EntryPoint("BatteryPackCostCalc__cost_per_kwh", "cost_per_kwh",
        EntryPointType.LIBRARY_DEFAULT, default_value=150.0, param_group="library_params")]),
], execution_order=["battery_pack__cost_model", "battery_system__total_cost"])
```

## Model Containment

```
ComputationGraph ── modules: [PipelineModule] ── inputs: [ModuleInput] ── source: InputSource
                 │                             └─ outputs: [ModuleOutput]
                 ├─ entry_point_groups: [ParameterGroup] ── parameters: [EntryPoint]
                 ├─ output_aliases: [OutputAlias]
                 └─ execution_order: [str]
```

## Related Documents

- **Upstream**: [00](00-pipeline-overview.md), [01](01-extraction.md), [02](02-orchestration.md)
- **Delegated**: [14](14-expression-compiler.md), [15](15-naming-conventions.md), [16](16-computed-attributes.md), [23](23-smart-regen-preservation.md)
- **Consumers**: [08](08-generation.md)
