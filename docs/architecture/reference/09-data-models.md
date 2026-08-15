# 09 -- Data Models Reference

> **Status: mixed — read the model, then check which half it is in.** The exact route is the
> only authority, and this document's model set straddles the line.
>
> **Live, on the shipped route:** `ComputationGraph`, `PipelineModule`, `ModuleInput`,
> `ModuleOutput`, `InputSource`, `EntryPoint`, `EntryPointType`, `ParameterGroup`,
> `ModuleKind`, `OutputAlias`, and the constraint-catalog models — all in
> `resolution/models.py`, which projection produces and generation consumes. The extraction
> models `CalculationDefinitionData` and its enums are live too: the exact route loads and
> extracts through `extraction/extractor.py`. `BindingResolution` and `ChannelAlias` are in
> `core/models.py` and are read by generation.
>
> **Deleted with their owners** by the Item 7 retirement (2026-08-12, `19072ad` / `82c7951` /
> `882fc8d` / `3071fba`): `BacktrackingResult`, `DesignAttributeData`,
> `DerivedParameterGroup`, `ParameterSource`, and the `OutputRegistry` types. Their owners
> (`analysis/dependency_backtracker.py`, `analysis/parameter_groups.py`,
> `resolution/graph_builder.py`, `core/output_registry.py`) are not in the tree, and neither
> are the models. **The rows for them below describe types that no longer exist.**
>
> The hierarchy/aggregation extraction structures are the one survivor:
> `extraction/hierarchy_resolver.py` is still in the tree with its own conformance coverage,
> and is not on the exact route's construction closure.
>
> **The rows are kept, not removed.** The test that used to pin them,
> `tests/conformance/test_data_models.py`, was repointed by the retirement itself (ledger row
> **L-120**, executed at `82c7951`), so nothing now couples these rows to a test. They stay
> because the historical documents link into them — a reader following
> [11-analysis-backtracker](11-analysis-backtracker.md) to `BacktrackingResult` needs the
> field list to make sense of what it reads. This banner is what tells them the type is gone.

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
[Extraction]  → CalculationDefinitionData, CalcUsageData, PartDefinitionData,
                 RedefinitionData, AggregationExpressionData, ComputedAttributeData,
                 HierarchyExtractionResult
  |
  v
[Analysis]    → BacktrackingResult (binding_resolutions, entry_points)
                 DesignAttributeData, DerivedParameterGroup, PhantomDetectionReport
  |
  v
[Core]        → OutputRegistry, BindingResolution, ChannelAlias
  |
  v
[Resolution]  → ComputationGraph (PipelineModule, ParameterGroup, EntryPoint, OutputAlias)
  |
  v
[Generation]  → PipelineContext → Python files, YAML, JSON templates
```

## Enums
Every value listed (REQ-DM-02). These are the most common source of doc bugs.
| Enum | Values | Source |
|------|--------|--------|
| `BindingType` | `CHAIN`, `REFERENCE`, `LITERAL`, `EXPRESSION`, `UNBOUND` | `agentic_mbse` |
| `RedefinitionType` | `LITERAL`, `CHAIN`, `EXPRESSION` | `extraction/data_models.py` |
| `ComputedAttributeClassification` ¹ | `FORMULA`, `EXPOSE_PURE`, `EXPOSE_COMPUTED`, `EXPOSE_CHAIN_TENTATIVE`, `LITERAL`, `UNRESOLVABLE` | `extraction/data_models.py` |
| `Compilability` | `FULLY_COMPILABLE`, `PARTIALLY_COMPILABLE`, `MANUAL_REQUIRED`, `UNKNOWN` | `extraction/expression_compiler.py` |
| `ModuleKind` ² | `CALCULATION`, `FORMULA`, `AGGREGATION`, `CONSTRAINT`, `REPORT_AGGREGATOR` | `resolution/models.py` |
| `BindingResolutionType` | `ENTRY_POINT`, `MODULE_OUTPUT` | `core/models.py` |
| `EntryPointType` | `LIBRARY_DEFAULT`, `DESIGN_ATTRIBUTE`, `USAGE_LITERAL` | `resolution/models.py` |

> ¹ `EXPOSE_CHAIN_TENTATIVE` is a transient value (Item 10): tagged at extraction
> for a well-formed multi-hop feature chain, then finalized by the Phase-3b confirm
> pass (`build_output_registry`, `orchestration/output_registry_builder.py`) to
> `EXPOSE_PURE` or reverted to `FORMULA`. No downstream reader ever observes it
> (INV-F raises). `UNRESOLVABLE` is likely unreachable for well-formed SysML (SysIDE
> always resolves attribute QNs). It exists as a defensive fallback. An attribute
> referencing only inherited and/or local attributes classifies `FORMULA` (Step-2b now
> prefix-matches the owning part QN OR any ancestor PartDef QN — the inherited-attr fix,
> TRUTH-DEBT Item 4) — see [16-computed-attributes](16-computed-attributes.md) Known
> Issues §Inherited Attribute Classification.
>
> ² `ModuleKind` is set once at `PipelineModule` construction and dispatched on at every
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

See [10-output-registry](10-output-registry.md) for the full type system and [15-naming-conventions](15-naming-conventions.md) for identifier format definitions.

**Conversion boundary**: Raw SysML names (`SysMLQN`) are converted to `EQN` at extraction
time. All downstream indexes, lookups, and registrations use typed names only.

**Field format assignments.** The table below documents which semantic format each
field carries. At HEAD the NewType annotations are enforced on `OutputRegistry`
keys/values and the `make_*` constructors (`core/identifier_types.py`); the model
fields listed are still annotated `str` in their dataclass/BaseModel definitions
(a deliberate deferral, filed `[DM08-MODEL-FIELD-TYPING]`; REQ-DM-08 now pins the
enforced surface — `test_dm08_enforced_surface.py` — and its text names exactly that
surface, per the matrix). Fields with
no format constraint at all: `BindingInfo.param_name` (simple name),
`PipelineModule.name` (module name = lowered EQN, could be typed later).

| Model | Field | Format |
|-------|-------|------|
| `CalculationDefinitionData` | `qualified_name` | `SysMLQN` |
| `CalcUsageData` | `qualified_name` | `EQN` |
| `CalcUsageData` | `calc_def_qualified_name` | `SysMLQN` |
| `PartDefinitionData` | `qualified_name` | `SysMLQN` |
| `RedefinitionData` | `owning_part_qn` | `EQN` |
| `DesignAttributeData` | `qualified_name` | `EQN` |
| `BindingResolution` | `qualified_name` | `PQN` (module_output channel); EQN or PQN for entry_point |
| `ModuleOutput` | `channel_name` | `CanonicalChannel` |
| `EntryPoint` | `qualified_name` | `PQN` |
| `InputSource` | `producer_channel` | `CanonicalChannel \| None` |
| `OutputRegistry` | scoped registry keys | `ScopedKey` |
| `OutputRegistry` | SysML QN registry keys | `SysMLQN` |
| `OutputRegistry` | alias registry keys | `ScopedKey` |
| `OutputRegistry` | scoped-alias registry keys | `ScopedAliasKey` |
| `OutputRegistry` | all registry values | `CanonicalChannel` |
| `ChannelAlias` | `alias_name` | `ScopedKey` (CHAIN redefs); bare name for `expose_pure` — scoped at registration |
| `ChannelAlias` | `canonical_name` | dotted `ScopedKey`-format target, resolved to a `CanonicalChannel` at registration |

## Extraction Models

**CalculationDefinitionData** (dataclass, `extraction/data_models.py`)
`name: str`, `qualified_name: str`, `doc_comment: str`, `calc_expressions: list[str]`,
`input_attributes: list[AttributeInfo]`, `output_attributes: list[AttributeInfo]`,
`references: list[str]`, `source_file: Path`, `source_line: int`, `source_hash: str`,
`output_expression_asts: dict[str, Any]`, `all_member_names: set[str]`,
`member_expressions: dict[str, Any]`.

**CalcUsageData** (dataclass, `extraction/usage_extractor.py`)
`instance_name: str`, `calc_def_name: str`, `calc_def_qualified_name: str`,
`module_type: str`, `bindings: list[BindingInfo]`, `unbound_params: list[str]`,
`source_file: Path`, `source_line: int`, `parent_part_path: str`,
`qualified_name: str`, `is_template: bool`, `owning_part_def_qn: str | None`,
`raw_element: object | None`.
Properties: `parameter_bindings`, `has_cross_file_bindings`.

**BindingInfo** (dataclass, `extraction/usage_extractor.py`)
`param_name: str`, `source_path: str | None`, `binding_type: BindingType`,
`is_cross_file: bool`, `raw_expression: str`, `source_instance_elem: object | None`,
`source_attribute_elem: object | None`, `literal_value: float | int | str | bool | None`,
`expression_ast: Any`. Properties: `source_instance_name`, `source_attribute_name`.

**PartDefinitionData** (dataclass, `extraction/data_models.py`)
`name: str`, `qualified_name: str`, `doc_comment: str`, `attributes: list[AttributeInfo]`,
`constraints: list[ConstraintInfo]`, `source_file: Path`, `source_line: int`, `source_hash: str`.

**RedefinitionData** (dataclass, `extraction/data_models.py`)
`owning_part_qn: str`, `attribute_name: str`, `redefinition_type: RedefinitionType`,
`literal_value: float | int | str | bool | None`, `source_path: str | None`,
`expression_ast: Any`, `expression_text: str`, `target_path: list[str]`,
`is_deep_path: bool`, `source_file: Path`, `source_line: int`.

**MultiplicityData** (dataclass, `extraction/data_models.py`)
`part_usage_name: str`, `owning_part_def_qn: str`, `count: int | None`,
`count_attribute_name: str | None`, `default_value: int | None`.

**HierarchyExtractionResult** (dataclass, `extraction/data_models.py`)
`redefinitions: list[RedefinitionData]`, `design_overrides: list[RedefinitionData]`,
`multiplicities: list[MultiplicityData]`, `aggregation_expressions: list[AggregationExpressionData]`,
`warnings: list[str]`, `part_usage_names: dict[str, set[str]]`,
`usage_type_map: dict[tuple[str, str], str]`.

**AttributeInfo** (dataclass, `extraction/data_models.py`, extends `BaseAttributeInfo`)
Inherited: `name`, `sysml_type`, `default_value`, `binding_type`, `is_input`, `is_output`.
Added: `python_type: str`, `description: str`, `unit: str | None`, `source_line: int`,
`is_optional: bool`.

**AggregationExpressionData** (dataclass, `extraction/data_models.py`)
`owning_part_qn`, `owning_part_name`, `attribute_name`, `raw_expression_text`,
`transformed_expression`, `sum_terms: list[SumTerm]`, `singleton_terms: list[SingletonTerm]`,
`local_terms: list[LocalTerm]`, `input_channels: list[str]`, `entry_points: list[str]`,
`aliases: list[str]`, `compilability`, `has_unsupported_nodes: bool`, `source_file`, `source_line`.
See [13](13-aggregation-scoping.md), [25](25-hierarchy-resolver.md) for semantics.

*Delegated: ComputedAttributeData → [16](16-computed-attributes.md). Expression compiler → [14](14-expression-compiler.md).*

## Analysis Models

**BacktrackingResult** (BaseModel, `analysis/dependency_backtracker.py`)
`required_usages: list[CalcUsageData]`, `dependency_graph: dict[str, list[str]]`,
`entry_points: set[str]`, `entry_point_sources: dict[str, str]`,
`binding_resolutions: dict[str, BindingResolution]`, `phantom_report: PhantomDetectionReport`,
`trace_log: list[str]`,
`fallback_entry_points: set[str]` (Item 7 / D4 — Step-4 fall-through entry-point QNs;
carried onto the ComputationGraph for the V11 `collect_uncovered_params` collector).
Key format: `"{usage_qualified_name}|{param_name}"`.

**DesignAttributeData** (dataclass, `analysis/parameter_groups.py`)
`name: str`, `sysml_type: str`, `default_value: str | None`, `unit: str | None`,
`source_file: Path`, `source_line: int`, `parent_part: str`, `qualified_name: str`.

**DerivedParameterGroup** (dataclass, `analysis/parameter_groups.py`)
`name: str`, `class_name: str`, `source_type: Literal["design", "library"]`,
`source_identifier: str`, `parameters: list[ParameterSource]`.

**ScopedAggregationData** (dataclass, `extraction/data_models.py`)
`expression: AggregationExpressionData`, `instance_path: str`.
Property: `module_eqn` = `"{instance_path}__{attribute_name}"`.
Bridge from extraction to pipeline — wraps an aggregation with a concrete design
instance path. See [13](13-aggregation-scoping.md).

*Delegated: PhantomDetectionReport → `analysis/phantom_detector.py`. FunctionSignature → [23](23-smart-regen-preservation.md).*

## Core Models

**BindingResolution** (BaseModel, `core/models.py`)
`resolution_type: BindingResolutionType`, `qualified_name: str`,
`source_path: str | None`, `is_transitive: bool`.

**ChannelAlias** (BaseModel, `core/models.py`)
`alias_name: str`, `canonical_name: str`, `owning_part_qn: str`,
`source: Literal["redefinition", "expose_pure", "design_override"]`.

**OutputRegistry** (class, `core/output_registry.py`)
Internal: 4 typed registries — `_scoped: dict[ScopedKey, CanonicalChannel]`,
`_sysml_qn: dict[SysMLQN, CanonicalChannel]`, `_alias: dict[ScopedKey, CanonicalChannel]`,
`_scoped_alias: dict[ScopedAliasKey, CanonicalChannel]` (Item 10 — structured
`(scope, leaf)` namespace for part-def EXPOSE and consumer-scoped aliases,
kept distinct from the flat `_alias` so tuple keys can never collide with string keys).
Membership set: `_canonical: set[CanonicalChannel]` (for phase-ordering enforcement).
API: `register_scoped(ScopedKey, CanonicalChannel)`,
`register_sysml_qn(SysMLQN, CanonicalChannel)`,
`register_alias(ScopedKey, CanonicalChannel)`,
`register_scoped_alias(ScopedAliasKey, CanonicalChannel)`,
`scoped_lookup(ScopedKey) → CanonicalChannel | None`,
`sysml_qn_lookup(SysMLQN) → CanonicalChannel | None`,
`alias_lookup(ScopedKey) → CanonicalChannel | None`,
`scoped_alias_lookup(ScopedAliasKey) → CanonicalChannel | None`,
`scoped_alias_items() → list[tuple[ScopedAliasKey, CanonicalChannel]]`,
`canonical_channels → frozenset[CanonicalChannel]`.
See [10-output-registry](10-output-registry.md) for the 4-phase protocol and type system.

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
[28-constraint-lowering-and-catalog](28-constraint-lowering-and-catalog.md).

**OutputAlias** (BaseModel, `resolution/models.py`)
`alias_name: str`, `canonical_channel: str`, `instance_path: str`,
`shape: Literal["part_def", "part_usage"]`. Property: `output_filename` →
`{instance_path}__{alias_name}.json`. One EXPOSE_PURE modeler name surfaced onto the
canonical channel the value already flows on (Item 11 / SC-7 / REQ-DM-09). `shape`
tags provenance: `part_def` from the `_scoped_alias` registry (shape A), `part_usage`
from an `expose_pure` `ChannelAlias` (shape B). `canonical_channel` is read from the
registry, never re-derived (INV-2), and is validated to be a declared graph output
channel (INV-3). See [16-computed-attributes](16-computed-attributes.md) and
[21-pipeline-yaml-generation](21-pipeline-yaml-generation.md).

**PipelineModule** (BaseModel, `resolution/models.py`)
`name: str`, `module_type: str`, `inputs: list[ModuleInput]`, `outputs: list[ModuleOutput]`,
`execution_order: int`, `compilability: Compilability`, `compiled_expression: str | None`,
`module_kind: ModuleKind` (**required**), `output_schema_type: str | None`,
`auto_impl_context: dict | None`.
Metadata carried from CalcDef / ComputedAttributeData / AggregationExpressionData:
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

**PipelineContext** (dataclass, `orchestration/pipeline_context.py`)
`extractor`, `calc_defs`, `calc_usages`, `design_attributes`, `group_deriver`,
`backtracker`, `backtracking_result`, `computation_graph`, `compilation_results`,
`computed_attributes`, `hierarchy_data`, `aggregation_expressions: list[ScopedAggregationData]`,
`channel_aliases: list[ChannelAlias]`, `output_registry: OutputRegistry | None`.

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
BacktrackingResult ── required_usages: [CalcUsageData] ── bindings: [BindingInfo]
                   ├─ binding_resolutions: dict[str, BindingResolution]
                   └─ phantom_report: PhantomDetectionReport
HierarchyExtractionResult ── redefinitions/design_overrides: [RedefinitionData]
                          ├─ multiplicities: [MultiplicityData]
                          └─ aggregation_expressions: [AggregationExpressionData]
```

## Related Documents

- **Upstream**: [00](00-pipeline-overview.md), [01](01-extraction.md), [02](02-orchestration.md), [03](03-resolution-overview.md)
- **Delegated**: [13](13-aggregation-scoping.md), [14](14-expression-compiler.md), [15](15-naming-conventions.md), [16](16-computed-attributes.md), [17](17-parameter-group-deriver.md), [23](23-smart-regen-preservation.md), [25](25-hierarchy-resolver.md)
- **Consumers**: [10](10-output-registry.md) (typed registries, identifier types), [11](11-analysis-backtracker.md), [07](07-graph-assembly.md), [08](08-generation.md)
