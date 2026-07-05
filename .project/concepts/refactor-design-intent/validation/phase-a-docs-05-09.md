# Validation: Docs 05-09 vs Source Code

Validated on: 2026-02-16
Branch: cost-pattern
Validator: claude-opus-4-6

---

## Doc 05: Module Factory

### Verified OK
- **PipelineModule fields**: All 8 fields documented in the code snippet match `resolution/models.py` lines 150-171 exactly: `name`, `module_type`, `inputs`, `outputs`, `execution_order`, `compilability`, `compiled_expression`, `is_computed_attribute`, `is_aggregation`.
- **ModuleInput fields**: `param_name`, `python_type`, `source: InputSource` match `resolution/models.py` lines 122-133 exactly.
- **ModuleOutput fields**: `field_name`, `python_type`, `channel_name` match `resolution/models.py` lines 136-148 exactly.
- **InputSource fields**: `source_type`, `param_group`, `qualified_name`, `producer_channel` match `resolution/models.py` lines 100-119 exactly.
- **`_build_pipeline_module()` function**: Exists at `graph_builder.py` line 1291. Key format `"{usage_qn}|{param_name}"` confirmed at line 1335. Fail-fast on missing resolution confirmed at line 1340-1345.
- **`_build_computed_attr_module()` function**: Exists at `graph_builder.py` line 641. FORMULA + FULLY_COMPILABLE filtering confirmed. Regex `inputs\.(\w+)` extraction from compiled_expression confirmed at line 670. Single output with `field_name="root"` confirmed at line 742. Flags `is_computed_attribute=True`, `FULLY_COMPILABLE` confirmed at lines 754-755.
- **`_build_aggregation_module()` function**: Exists at `graph_builder.py` line 922. SumTerm, SingletonTerm, LocalTerm processing confirmed. `is_aggregation=True` flag confirmed at line 1214. Multiplicity entry point creation confirmed at lines 1021-1046.
- **SumTerm dataclass fields**: `part_usage_name`, `attribute_name`, `multiplicity_attr`, `multiplicity_count` match `data_models.py` lines 274-280 exactly.
- **SingletonTerm dataclass field**: `source_path` matches `data_models.py` line 287 exactly.
- **LocalTerm dataclass field**: `attribute_name` matches `data_models.py` line 294 exactly.
- **LocalTerm resolution strategies**: Sibling aggregation output (line 1137-1146), EXPOSE_PURE alias (line 1148-1164), entry point fallback (line 1166-1182) -- all three strategies confirmed in order.
- **Pure data transformer pattern**: All three factory functions take pre-resolved inputs and produce PipelineModule without graph walking or registry mutation.

### Issues Found
- **Doc says `binding_resolutions` key format is `"{usage_qn}|{param_name}"`**: This is correct in the actual code (line 1335 of `graph_builder.py`), but the doc's Section 2 describes it without the `|` separator notation -- it uses `"...|capacity"` in the example, which is fine as abbreviated notation.
- **ScopedAggregationData described as "dataclass"**: Correct, it is a dataclass at `data_models.py` line 348.
- No issues found.

### Could Not Verify
- The behavioral claim that "Missing mapping = immediate raise (fail-fast, no fallback)" is confirmed by the code at line 1340-1345 (raises ValueError).

---

## Doc 06: Entry Point Classification

### Verified OK
- **EntryPointType enum values**: `LIBRARY_DEFAULT`, `DESIGN_ATTRIBUTE`, `USAGE_LITERAL` match `resolution/models.py` lines 23-34 exactly.
- **EntryPointType location**: Doc says `resolution/models.py` -- confirmed.
- **`_classify_entry_points()` function**: Exists at `graph_builder.py` line 265. Signature matches: receives `entry_point_names: set[str]`, `entry_point_sources: dict[str, str]`.
- **BacktrackingResult fields**: `entry_points: set[str]` confirmed at `dependency_backtracker.py` line 75. `entry_point_sources: dict[str, str]` confirmed at line 76.
- **Classification precedence**: (1) design_attr_index check (line 319), (2) unbound_lookup check (line 329), (3) USAGE_LITERAL fallback (line 345) -- matches doc pseudocode exactly.
- **design_attr_index construction**: Built from `DesignAttributeData` by qualified_name at lines 297-301. Matches doc description.
- **unbound_lookup construction**: Built from `usage.unbound_params` as `"{usage_qn}__{param_name}" -> (usage, param_name)` at lines 304-308. Matches doc description.
- **USAGE_LITERAL default value**: Parsed from `entry_point_sources[qname]` via `float()` at lines 348-353. Matches doc.
- **EntryPoint model fields**: `qualified_name`, `simple_name`, `entry_type`, `default_value`, `source_calc_usage`, `param_group`, `python_type` -- all match `resolution/models.py` lines 37-59 exactly.
- **ParameterGroup model fields**: `name`, `class_name`, `source_file: Path`, `parameters: list[EntryPoint]` match `resolution/models.py` lines 70-87 exactly.
- **`_group_entry_points_via_deriver()` function**: Exists at `graph_builder.py` line 370. Calls `group_deriver.derive_groups_filtered()` confirmed at line 397. Calls `_convert_derived_groups()` confirmed at line 402.
- **Orphan entry points**: Fallback `"system_design"` group at lines 225-248 confirmed.
- **Step 6.6 rebuild**: Rebuilding param groups after Steps 6.5 and 6.7 confirmed at lines 199-212, using `derive_groups()` (unfiltered) and re-filtering.
- **`derive_groups_filtered()` method**: Exists at `parameter_groups.py` line 467.
- **`_convert_derived_groups()` function**: Exists at `graph_builder.py` line 405.

### Issues Found
- **Doc says initial grouping at "Step 5"**: In the code, the function `build_computation_graph()` labels this as "Step 5" (line 130 comment). Confirmed correct.
- **Doc says Steps 6.5, 6.7, and 6.6**: The code actually has the order: Step 6.5 (computed attrs, line 163), Step 6.6b (expose aliases, line 176), Step 6.7 (aggregation, line 191), Step 6.6 (rebuild, line 199). The doc omits Step 6.6b but this is a minor detail not central to the doc's claims.

### Could Not Verify
- Nothing. All claims verified.

---

## Doc 07: Graph Assembly

### Verified OK
- **`_unified_topological_sort` function**: Exists at `graph_builder.py` line 1218. Matches doc claim of "line 1218" exactly.
- **Kahn's algorithm implementation**: Channel-to-module index (lines 1234-1237), dependency graph build (lines 1243-1250), self-reference guard `dep_module != m.name` (line 1247), successor inversion (lines 1255-1258), deque-based queue (lines 1261-1273), cycle detection (lines 1275-1281), execution_order reassignment (lines 1283-1288) -- all match doc description.
- **Code snippet for dependency build**: Doc snippet at Section "2. Build the dependency graph" closely matches lines 1243-1250 of actual code. The actual code has an additional check `if dep_module not in graph[m.name]` (line 1248) to prevent duplicate edges, which the doc omits but is a minor implementation detail.
- **Code snippet for queue processing**: Doc snippet matches lines 1261-1273 almost exactly, including `deque`, `popleft()`, sorted_names accumulation, and in_degree decrement logic.
- **Cycle detection logic**: Doc snippet matches lines 1275-1281. The error class `CircularDependencyError` is confirmed (imported from `dependency_backtracker.py` line 35).
- **`_validate_channel_references` function**: Exists at `graph_builder.py` line 491. Logic matches doc description: builds `declared_channels` set, iterates all module inputs, checks `producer_channel` membership. The actual code shows extra diagnostic info in the error message (sample channels) vs the simpler doc version, but the logic is identical.
- **ComputationGraph model**: `modules: list[PipelineModule]`, `entry_point_groups: list[ParameterGroup]`, `execution_order: list[str]` match `resolution/models.py` lines 174-188 exactly.
- **DependencyBacktracker._topological_sort**: Exists at `dependency_backtracker.py` line 662. Confirmed.
- **Backtracker toposort uses `list.pop(0)`**: Confirmed at line 692: `current = queue.pop(0)`. Doc correctly identifies this as O(n) per pop.
- **Resolution layer toposort uses `deque`**: Confirmed at `graph_builder.py` line 1261.

### Issues Found
- **Doc says backtracker toposort is at "line 662"**: Exact match. Confirmed.
- **Doc says `_unified_topological_sort` is at "line 1218"**: Exact match. Confirmed.
- **Doc says `core/graph_algorithms.py` for post-refactor convergence**: This file does NOT exist (`src/sysml_codegen/core/graph_algorithms.py` not found). However, the doc explicitly says this is a "post-refactor target" -- a planned future improvement, not a claim about current state. This is fine.
- No factual issues found.

### Could Not Verify
- The O(V^2) vs O(V+E) performance claims are theoretical analysis of the algorithms, not verifiable against source code. However, `list.pop(0)` is indeed O(n) and `deque.popleft()` is O(1) in CPython, so the claims are correct.

---

## Doc 08: Generation

### Verified OK
- **Source file paths**: `generation/pipeline.py`, `generation/modules.py`, `generation/schemas.py`, `generation/stencils.py` all exist as confirmed by the glob results.
- **`generate_pipeline_yaml()` signature**: Matches `pipeline.py` lines 24-28 exactly: `(graph: ComputationGraph, package_name: str, template_env: Environment) -> str`.
- **`pipeline.py` only consumes ComputationGraph**: Confirmed -- imports are only from `resolution.models` (lines 15-21), no extraction data models imported.
- **Pipeline YAML generation steps**: (1) Build channel_field_map (line 47), (2) entry points to dicts (line 56), (3) modules to context dicts (line 57), (4) exit points (line 58), (5) render template (line 62) -- matches doc's 5-step description.
- **`generate_teax_module(calc_def: CalculationDefinitionData, ...)`**: Confirmed at `modules.py` line 82-88. First param is `calc_def: CalculationDefinitionData`.
- **`generate_multioutput_model(calc_def: CalculationDefinitionData, ...)`**: Confirmed at `schemas.py` line 116-122. First param is `calc_def: CalculationDefinitionData`.
- **`generate_implementation(calc_def: CalculationDefinitionData, ...)`**: Confirmed at `stencils.py` line 234-240. First param is `calc_def: CalculationDefinitionData`.
- **Current gap**: Doc correctly identifies that modules.py, schemas.py, and stencils.py consume raw `CalculationDefinitionData` instead of `ComputationGraph`.
- **Each has its own `_map_input_type()`**: Confirmed -- `modules.py` line 171, `schemas.py` line 249, `stencils.py` line 320 each have independent `_map_input_type()` functions doing the same "Real" -> "float" mapping.
- **Template names**: `pipeline_yaml.jinja2`, `teax_module.py.jinja2`, `implementation_stencil.py.jinja2`, `auto_implementation.py.jinja2`, `multioutput_model.py.jinja2`, `entry_point_schema.py.jinja2`, `parameter_group_schema.py.jinja2`, `constraint_validator.py.jinja2`, `registry_function.py.jinja2`, `test_implementations.py.jinja2` -- all confirmed to exist in `templates/` directory.

### Issues Found
- **Doc claims "13 Jinja2 templates in `templates/`"**: Actually there are 12 templates. The templates directory contains: `pipeline_yaml.jinja2`, `teax_module.py.jinja2`, `teax_module_stub.py.jinja2`, `implementation_stencil.py.jinja2`, `auto_implementation.py.jinja2`, `multioutput_model.py.jinja2`, `pydantic_schema.py.jinja2`, `entry_point_schema.py.jinja2`, `parameter_group_schema.py.jinja2`, `constraint_validator.py.jinja2`, `registry_function.py.jinja2`, `test_implementations.py.jinja2`. Count is 12, not 13.
- **Template table lists 10 templates**: The table is missing `teax_module_stub.py.jinja2` and `pydantic_schema.py.jinja2` from the actual template set. The table has 10 entries; actual count is 12.
- **Table says `entry_point_schema.py.jinja2` generator is "schemas"**: This is technically correct but inconsistent -- other entries use the module filename (e.g., "pipeline.py", "modules.py"). This appears to be generated from `generation/entry_point.py` (which exists), not `schemas.py`.

### Could Not Verify
- The exact YAML output format shown in the doc is illustrative and not directly verifiable without running the generator.

---

## Doc 09: Data Models Reference

### Verified OK
- **CalculationDefinitionData fields**: `name`, `qualified_name`, `input_attributes: list[AttributeInfo]`, `output_attributes: list[AttributeInfo]`, `calc_expressions: list[str]`, `output_expression_asts: dict[str, Any]`, `all_member_names: set[str]`, `source_file: Path`, `source_hash: str` -- all confirmed in `data_models.py` lines 122-162.
- **CalculationDefinitionData is a dataclass**: Confirmed (line 122: `@dataclass`).
- **CalcUsageData location**: Doc says `extraction/usage_extractor.py` -- confirmed.
- **CalcUsageData is a dataclass**: Confirmed (line 91: `@dataclass`).
- **CalcUsageData fields**: `instance_name`, `calc_def_name`, `qualified_name`, `module_type`, `bindings: list[BindingInfo]`, `unbound_params: list[str]`, `is_template: bool`, `owning_part_def_qn: str | None` -- all confirmed in `usage_extractor.py` lines 91-121.
- **BindingInfo fields**: `param_name`, `source_path`, `binding_type: BindingType`, `literal_value: float | None` -- confirmed in `usage_extractor.py` lines 49-73.
- **BindingType enum values**: `CHAIN`, `LITERAL`, `REFERENCE`, `UNKNOWN` listed in doc. Actual values from `agentic_mbse/sysml/types.py`: `CHAIN`, `REFERENCE`, `LITERAL`, `EXPRESSION`, `UNBOUND`. See Issues.
- **PartDefinitionData fields**: `name`, `qualified_name`, `attributes: list[AttributeInfo]`, `constraints: list[ConstraintInfo]`, `source_file: Path` -- confirmed in `data_models.py` lines 97-118.
- **RedefinitionData fields**: `owning_part_qn`, `attribute_name`, `redefinition_type: RedefinitionType`, `literal_value`, `source_path`, `expression_ast`, `target_path: list[str]`, `is_deep_path: bool` -- all confirmed in `data_models.py` lines 233-255.
- **RedefinitionType enum values**: `LITERAL`, `CHAIN`, `EXPRESSION` -- confirmed in `data_models.py` lines 225-230.
- **SumTerm, SingletonTerm, LocalTerm**: All fields match `data_models.py` lines 274-294.
- **AggregationExpressionData fields**: `owning_part_qn`, `attribute_name`, `transformed_expression`, `sum_terms`, `singleton_terms`, `local_terms`, `input_channels`, `entry_points`, `compilability` -- all confirmed in `data_models.py` lines 298-328.
- **ScopedAggregationData fields**: `expression: AggregationExpressionData`, `instance_path`. Property `module_eqn` returns `"{instance_path}__{attribute_name}"` -- confirmed at `data_models.py` lines 348-367.
- **BacktrackingResult** is a Pydantic BaseModel: Confirmed at `dependency_backtracker.py` line 47.
- **BacktrackingResult fields**: `required_usages: list[CalcUsageData]`, `dependency_graph: dict[str, list[str]]`, `entry_points: set[str]`, `entry_point_sources: dict[str, str]`, `binding_resolutions: dict[str, BindingResolution]` -- all confirmed at lines 72-82. Key format `"{usage_qualified_name}|{param_name}"` documented in the docstring.
- **DesignAttributeData location**: Doc says `analysis/parameter_groups.py` -- confirmed.
- **DesignAttributeData fields**: `name`, `qualified_name`, `default_value: str | None`, `parent_part`, `source_file` -- confirmed at `parameter_groups.py` lines 47-57.
- **DerivedParameterGroup fields**: `name`, `class_name`, `source_type`, `parameters: list[ParameterSource]` -- confirmed at `parameter_groups.py` lines 74-81.
- **BindingResolution location**: Doc says `core/models.py` -- confirmed.
- **BindingResolution fields**: `resolution_type: BindingResolutionType` (ENTRY_POINT | MODULE_OUTPUT), `qualified_name: str`, `source_path: str | None`, `is_transitive: bool` -- confirmed at `core/models.py` lines 32-68.
- **ChannelAlias location**: Doc says `core/models.py` -- confirmed.
- **ChannelAlias fields**: `alias_name`, `canonical_name`, `owning_part_qn`, `source` -- confirmed at `core/models.py` lines 71-111.
- **OutputRegistry location**: Doc says `core/output_registry.py` -- confirmed.
- **OutputRegistry internals**: `_index: dict[str, str]`, `_canonical: set[str]` -- confirmed at `output_registry.py` lines 29-30.
- **OutputRegistry methods**: `register()`, `register_alias()`, `resolve()` -- all confirmed.
- **4-phase registration**: Phase 1 via `register()`, Phases 2-4 via `register_alias()` -- confirmed in docstrings at `output_registry.py` lines 21-26.
- **`resolve()` returns `str | None` with exact match only**: Confirmed at `output_registry.py` lines 107-124.
- **ComputationGraph fields**: `modules`, `entry_point_groups`, `execution_order` -- confirmed at `resolution/models.py` lines 174-188.
- **All Resolution Models (PipelineModule, ModuleInput, ModuleOutput, InputSource, EntryPoint, ParameterGroup)**: All fields and types match `resolution/models.py` exactly.

### Issues Found
- **BindingType values listed as `CHAIN, LITERAL, REFERENCE, UNKNOWN`**: The actual enum has `CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND`. The doc lists `UNKNOWN` which does not exist -- the correct value is `UNBOUND`. The doc also omits `EXPRESSION` which is a valid BindingType used for `OperatorExpression` bindings. This is a factual error.
- **BindingInfo doc says `binding_type: BindingType` with values `(CHAIN, LITERAL, REFERENCE, UNKNOWN)`**: Should be `(CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND)`.
- **HierarchyExtractionResult fields**: Doc lists `usage_type_map: dict[tuple[str, str], str]` -- confirmed at `data_models.py` line 344. But the doc OMITS the `part_usage_names: dict[str, set[str]]` field which exists at line 340. The doc also lists `warnings: list[str]` -- confirmed at line 339.
- **DesignAttributeData**: Doc omits `sysml_type`, `unit`, `source_line` fields that exist in the actual dataclass (lines 52-56). The doc's field list is incomplete but not wrong -- it is described as "Key fields" so omissions are understandable.
- **DerivedParameterGroup**: Doc omits the `source_identifier` field (line 81 of `parameter_groups.py`). The `parameters` field type is listed as `list[ParameterSource]` which is correct.
- **ChannelAlias source field**: Doc says `source: ("redefinition" | "expose_pure" | "design_override")`. Actual type is `Literal["redefinition", "expose_pure", "design_override"]`. This is equivalent.

### Could Not Verify
- The data flow diagram at the top is a conceptual overview and is consistent with the architecture but not directly verifiable as executable code.
- The "Model Containment" tree at the bottom is an accurate structural summary.

---

## Summary

| Doc | Verified OK | Issues | Cannot Verify |
|-----|-------------|--------|---------------|
| 05  | 12 claims   | 0      | 0             |
| 06  | 14 claims   | 0      | 0             |
| 07  | 10 claims   | 0      | 1             |
| 08  | 10 claims   | 3      | 1             |
| 09  | 26 claims   | 4      | 2             |

### Critical Issues (factual errors)
1. **Doc 08**: Claims "13 Jinja2 templates" but there are 12.
2. **Doc 09**: Lists BindingType values as `CHAIN, LITERAL, REFERENCE, UNKNOWN` -- should be `CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND`. `UNKNOWN` does not exist; `UNBOUND` is the correct value.

### Minor Issues (omissions, not errors)
3. **Doc 08**: Template table lists 10 of 12 templates (missing `teax_module_stub.py.jinja2` and `pydantic_schema.py.jinja2`).
4. **Doc 09**: `HierarchyExtractionResult` omits the `part_usage_names` field.
5. **Doc 09**: `DesignAttributeData` and `DerivedParameterGroup` field lists are incomplete (missing secondary fields).

### Line Number Accuracy
- Doc 07 claims backtracker toposort at line 662: **exact match**.
- Doc 07 claims `_unified_topological_sort` at line 1218: **exact match**.
