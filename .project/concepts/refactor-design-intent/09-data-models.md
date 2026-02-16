# 09 -- Data Models Reference

All key data models in sysml-codegen, organized by pipeline stage.

## Data Flow

```
SysML Files
  |
  v
[Extraction] --> CalculationDefinitionData, CalcUsageData, PartDefinitionData,
                 RedefinitionData, AggregationExpressionData, ComputedAttributeData
  |
  v
[Analysis]   --> BacktrackingResult (binding_resolutions, entry_points)
                 DesignAttributeData, DerivedParameterGroup
  |
  v
[Core]       --> OutputRegistry, BindingResolution, ChannelAlias
  |
  v
[Resolution] --> ComputationGraph (PipelineModule, ParameterGroup, EntryPoint)
  |
  v
[Generation] --> Python files, YAML pipelines, JSON input templates
```

## Extraction Models

**CalculationDefinitionData** (dataclass) -- primary model for code generation.
Key fields: `name` ("AlphaNeutronSplit"), `qualified_name` ("FusionPhysics::AlphaNeutronSplit"),
`input_attributes: list[AttributeInfo]`, `output_attributes: list[AttributeInfo]`,
`calc_expressions: list[str]`, `output_expression_asts: dict[str, Any]`,
`all_member_names: set[str]`, `source_file: Path`, `source_hash: str`.

**CalcUsageData** (dataclass, `extraction/usage_extractor.py`) -- a calc usage instance.
Key fields: `instance_name` ("net_electric"), `calc_def_name` ("NetElectricPower"),
`qualified_name` ("Design__plant__net_electric"), `module_type` ("PowerBalance__NetElectricPower"),
`bindings: list[BindingInfo]`, `unbound_params: list[str]`,
`is_template: bool`, `owning_part_def_qn: str | None`.

**BindingInfo** (dataclass) -- one parameter binding on a CalcUsageData.
Fields: `param_name` ("p_fusion"), `source_path` ("alpha_neutron.p_neutron" or None),
`binding_type: BindingType` (CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND),
`literal_value: float | None`.

**PartDefinitionData** (dataclass) -- `name`, `qualified_name`, `attributes: list[AttributeInfo]`,
`constraints: list[ConstraintInfo]`, `source_file: Path`.

**RedefinitionData** (dataclass) -- a `:>>` redefinition on a PartDef/PartUsage.
Fields: `owning_part_qn` ("Lib__Solar_Array"), `attribute_name` ("capital_cost"),
`redefinition_type: RedefinitionType` (LITERAL | CHAIN | EXPRESSION),
`literal_value: float | None`, `source_path: str | None` ("cost_model.total_cost"),
`expression_ast: Any`, `target_path: list[str]`, `is_deep_path: bool`.

**SumTerm** -- sum() operand: `part_usage_name` ("pv_module"), `attribute_name` ("capital_cost"),
`multiplicity_attr` ("module_count"), `multiplicity_count` (20).

**SingletonTerm** -- non-sum child ref: `source_path` ("allocation_model.total_allocation").

**LocalTerm** -- PartDef-local attr: `attribute_name` ("misc_hardware_cost").

**AggregationExpressionData** (dataclass) -- decomposed sum()-based rollup expression.
Key fields: `owning_part_qn`, `attribute_name`, `transformed_expression` (symbolic Python),
`sum_terms: list[SumTerm]`, `singleton_terms: list[SingletonTerm]`, `local_terms: list[LocalTerm]`,
`input_channels: list[str]`, `entry_points: list[str]`, `compilability: Compilability`.

**ScopedAggregationData** (dataclass) -- scopes an AggregationExpressionData to one design instance.
Fields: `expression: AggregationExpressionData`, `instance_path` ("solar_battery_plant__solar_array").
Property `module_eqn` -> `"{instance_path}__{attribute_name}"`.

**HierarchyExtractionResult** (dataclass) -- complete hierarchy extraction output.
Fields: `redefinitions: list[RedefinitionData]`, `design_overrides: list[RedefinitionData]`,
`multiplicities: list[MultiplicityData]`, `aggregation_expressions: list[AggregationExpressionData]`,
`part_usage_names: dict[str, set[str]]`, `usage_type_map: dict[tuple[str, str], str]`,
`warnings: list[str]`.

## Analysis Models

**BacktrackingResult** (Pydantic BaseModel) -- output of dependency backtracking.
Fields: `required_usages: list[CalcUsageData]` (topological order),
`dependency_graph: dict[str, list[str]]`, `entry_points: set[str]`,
`entry_point_sources: dict[str, str]` (QN -> source value),
`binding_resolutions: dict[str, BindingResolution]` (THE source of truth for wiring).
Key format: `"{usage_qualified_name}|{param_name}"`.

**DesignAttributeData** (dataclass, `analysis/parameter_groups.py`) -- design attr with default.
Fields: `name`, `qualified_name`, `default_value: str | None`, `parent_part`, `source_file`.

**DerivedParameterGroup** (dataclass) -- auto-derived parameter group.
Fields: `name` ("solar_battery_params"), `class_name` ("SolarBatteryParams"),
`source_type` ("design" | "library"), `parameters: list[ParameterSource]`.

## Core Models (shared across layers)

**BindingResolution** (Pydantic BaseModel, `core/models.py`) -- single binding wiring decision.
Fields: `resolution_type: BindingResolutionType` (ENTRY_POINT | MODULE_OUTPUT),
`qualified_name: str` (entry point QN or upstream channel name),
`source_path: str | None` (original binding path, for debug), `is_transitive: bool`.

**ChannelAlias** (Pydantic BaseModel, `core/models.py`) -- alias -> canonical channel mapping.
Fields: `alias_name` ("solar_array.total_capex"), `canonical_name` ("solar_array.cost_model.total_cost"),
`owning_part_qn`, `source` ("redefinition" | "expose_pure" | "design_override").

**OutputRegistry** (class, `core/output_registry.py`) -- the master lookup table.
Internal: `_index: dict[str, str]` (key -> canonical), `_canonical: set[str]`.
4-phase registration: (1) CalcUsage/aggregation/FORMULA outputs via `register()`,
(2) CHAIN aliases, (3) EXPOSE_PURE aliases, (4) transitive design aliases via `register_alias()`.
`resolve(source_path) -> str | None` -- exact match only, no normalization.

## Resolution Models (the key output)

**ComputationGraph** (Pydantic BaseModel, `resolution/models.py`) -- THE single source of truth.
Fields: `modules: list[PipelineModule]`, `entry_point_groups: list[ParameterGroup]`,
`execution_order: list[str]`.

**PipelineModule** -- `name` ("alphaneutronsplit"), `module_type` ("AlphaNeutronSplitModule"),
`inputs: list[ModuleInput]`, `outputs: list[ModuleOutput]`, `execution_order: int`,
`compilability: Compilability`, `compiled_expression: str | None`,
`is_computed_attribute: bool`, `is_aggregation: bool`.

**ModuleInput** -- `param_name` ("p_fusion"), `python_type` ("float"), `source: InputSource`.

**ModuleOutput** -- `field_name` ("p_neutron" or "root"), `python_type`, `channel_name` ("alphaneutronsplit_p_neutron").

**InputSource** -- `source_type` ("entry_point" | "module_output"),
`param_group: str | None`, `qualified_name: str | None` (entry_point),
`producer_channel: str | None` (module_output).

**EntryPoint** -- `qualified_name` ("Design__plant__catf_physics__p_fusion"),
`simple_name` ("p_fusion"), `entry_type: EntryPointType` (LIBRARY_DEFAULT | DESIGN_ATTRIBUTE | USAGE_LITERAL),
`default_value: float | None`, `param_group: str | None`, `python_type: str`.

**ParameterGroup** -- `name` ("physics_params"), `class_name` ("PhysicsParams"),
`source_file: Path`, `parameters: list[EntryPoint]`.

## Model Containment

```
ComputationGraph
  +-- modules: list[PipelineModule]
  |     +-- inputs: list[ModuleInput]
  |     |     +-- source: InputSource
  |     +-- outputs: list[ModuleOutput]
  +-- entry_point_groups: list[ParameterGroup]
  |     +-- parameters: list[EntryPoint]
  +-- execution_order: list[str]

BacktrackingResult
  +-- required_usages: list[CalcUsageData]
  |     +-- bindings: list[BindingInfo]
  +-- binding_resolutions: dict[str, BindingResolution]

HierarchyExtractionResult
  +-- redefinitions / design_overrides: list[RedefinitionData]
  +-- multiplicities: list[MultiplicityData]
  +-- aggregation_expressions: list[AggregationExpressionData]
        +-- sum_terms / singleton_terms / local_terms
```
