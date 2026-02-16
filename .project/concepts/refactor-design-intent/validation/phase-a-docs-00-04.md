# Validation Report: Docs 00-04 vs Source Code

Validated on: 2026-02-16
Branch: cost-pattern
Validator: Claude Opus 4.6

---

## Doc 00: Pipeline Overview

### Verified OK
- File `extraction/extractor.py` exists and contains `SysMLDataExtractor` class
- File `extraction/usage_extractor.py` exists and contains `CalcUsageData`
- File `extraction/hierarchy_resolver.py` exists and contains redefinition/aggregation extraction
- File `extraction/data_models.py` exists and contains `CalculationDefinitionData`, `CalcUsageData` (CalcUsageData is actually in usage_extractor.py; see issues)
- File `resolution/graph_builder.py` exists and contains `build_computation_graph()`, `_classify_entry_points()`
- File `resolution/models.py` exists and contains `ComputationGraph`, `PipelineModule`, `EntryPoint`
- File `generation/pipeline.py`, `generation/modules.py`, `generation/schemas.py`, `generation/stencils.py`, `generation/entry_point.py` all exist
- File `analysis/dependency_backtracker.py` exists with `DependencyBacktracker`
- File `analysis/parameter_groups.py` exists with `ParameterGroupDeriver`
- File `core/output_registry.py` exists with `OutputRegistry`
- `ComputationGraph` is correctly described as a Pydantic model and single source of truth (line 174 of models.py)
- The 7-step pipeline description accurately reflects `build_pipeline_context()` in `generation/initialization.py`
- Kahn's algorithm is used for topological sort (`_unified_topological_sort` in graph_builder.py line 1218)
- `PipelineModule` fields `name`, `module_type`, `inputs`, `outputs` match the Pydantic model (models.py line 150)
- `ModuleInput` has `param_name` and `source` (InputSource) -- matches models.py line 122
- `ModuleOutput` has `field_name` and `channel_name` -- matches models.py line 136
- `InputSource` has `source_type`, `producer_channel`, `qualified_name` -- matches models.py line 100
- Entry point types LIBRARY_DEFAULT, DESIGN_ATTRIBUTE, USAGE_LITERAL exist (models.py line 23)

### Issues Found
- **Package structure claim**: Doc says `orchestration/initialization.py` contains `build_pipeline_context()` and `build_output_registry()`. Reality: **`orchestration/` does not exist**. Both functions are in `generation/initialization.py`. The doc does note this at line 187-188 ("Note: `orchestration/` is the refactor target...") but the package structure diagram on lines 173-175 presents `orchestration/` as if it already exists. This is a **future-state vs current-state confusion**.
- **CalcUsageData location**: Doc's package structure (line 171) says `data_models.py` contains `CalcUsageData`. Reality: `CalcUsageData` is defined in `extraction/usage_extractor.py` (line 91), not in `data_models.py`.
- **`CalculationDefinitionData` in package structure**: Listed in `data_models.py` -- this is correct (line 122 of data_models.py).

### Could Not Verify
- SysML model examples (BatteryPackCostCalc with specific inputs/outputs) -- would require running the actual SysML model to verify field counts and names
- Generated output file names (e.g., `modules/battery_pack_cost_calc.py`) -- would need to run code generation on the SolarBattery model

---

## Doc 01: Extraction

### Verified OK
- Source path `src/sysml_codegen/extraction/` is correct (line 6)
- **CalculationDefinitionData fields**: `name`, `qualified_name`, `input_attributes`, `output_attributes`, `calc_expressions`, `output_expression_asts`, `all_member_names`, `member_expressions` -- all verified in data_models.py lines 122-161
- **AttributeInfo fields**: `name`, `sysml_type`, `python_type`, `default_value`, `binding_type`, `is_input`, `is_output`, `unit` -- verified in data_models.py lines 46-74 (inherits from BaseAttributeInfo)
- **CalcUsageData fields**: `instance_name`, `calc_def_name`, `module_type`, `bindings`, `unbound_params`, `qualified_name`, `is_template`, `owning_part_def_qn` -- all verified in usage_extractor.py lines 91-120
- **BindingInfo fields**: `param_name`, `source_path`, `binding_type`, `literal_value`, `expression_ast` -- all verified in usage_extractor.py lines 48-73
- **BindingType enum**: CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND -- all 5 values confirmed via runtime check of `agentic_mbse.sysml.types.BindingType`
- **PartDefinitionData fields**: `name`, `qualified_name`, `doc_comment`, `attributes`, `constraints`, `source_file` -- all verified in data_models.py lines 97-118
- **RedefinitionType enum**: LITERAL, CHAIN, EXPRESSION -- verified in data_models.py lines 225-230
- **RedefinitionData fields**: `owning_part_qn`, `attribute_name`, `redefinition_type`, `literal_value`, `source_path`, `expression_ast`, `expression_text`, `target_path`, `is_deep_path` -- all verified in data_models.py lines 233-255
- **HierarchyExtractionResult fields**: `redefinitions`, `design_overrides`, `multiplicities`, `aggregation_expressions`, `part_usage_names`, `usage_type_map`, `warnings` -- all verified in data_models.py lines 332-344
- **AggregationExpressionData fields**: `owning_part_qn`, `owning_part_name`, `attribute_name`, `transformed_expression`, `sum_terms`, `singleton_terms`, `local_terms`, `input_channels`, `entry_points`, `has_unsupported_nodes` -- all verified in data_models.py lines 298-328
- **SumTerm fields**: `part_usage_name`, `attribute_name`, `multiplicity_attr`, `multiplicity_count` -- verified in data_models.py lines 274-280
- **SingletonTerm fields**: `source_path` -- verified in data_models.py lines 284-287
- **LocalTerm fields**: `attribute_name` -- verified in data_models.py lines 291-294
- **MultiplicityData fields**: `part_usage_name`, `owning_part_def_qn`, `count`, `count_attribute_name`, `default_value` -- verified in data_models.py lines 258-270
- **extract_hierarchy_data()** exists in hierarchy_resolver.py (line 490)
- **Expression compiler** exists in `expression_compiler.py` with `build_expression_ast()` (line 290), `compile_expression()` (line 187), and `compile_calc_def()` (line 455)
- **Compilability enum**: `FULLY_COMPILABLE`, `PARTIALLY_COMPILABLE`, `MANUAL_REQUIRED`, `UNKNOWN` -- verified in expression_compiler.py lines 25-35
- **Template expansion** claim: CalcUsageData has `is_template` (line 118) and `owning_part_def_qn` (line 119) fields -- confirmed

### Issues Found
- **UNBOUND binding type description**: Doc says "These appear in `CalcUsageData.unbound_params` (not in `bindings`)". This is partially correct -- looking at usage_extractor.py, UNBOUND params are indeed added to `unbound_params` (line 495-516 area), but they may also appear as BindingInfo objects with `binding_type=BindingType.UNBOUND` in `bindings`. The code creates explicit UNBOUND BindingInfo objects at line 516 and 569. **The doc's claim that UNBOUND bindings don't appear in `bindings` is misleading** -- they appear in both.

### Could Not Verify
- Specific SysML syntax examples and their extraction results -- would require running extraction on actual models
- The `expression_compiler.py` three-phase description (build AST, compile, classify) -- confirmed functions exist, but the exact phase decomposition would need detailed code reading beyond the function signatures

---

## Doc 02: Orchestration

### Verified OK
- **`generation/initialization.py` contains orchestration logic**: Confirmed. `build_pipeline_context()` is at line 678 and `build_output_registry()` is at line 502
- **Line count claim "860 lines"**: initialization.py is exactly 860 lines (`wc -l` confirmed). **Perfectly accurate.**
- **`build_pipeline_context()` exists**: Confirmed at line 678
- **`build_output_registry()` exists**: Confirmed at line 502
- **PipelineContext dataclass**: Exists at line 76 with fields: `extractor`, `calc_defs`, `calc_usages`, `design_attributes`, `group_deriver`, `backtracker`, `backtracking_result`, `computation_graph`, `compilation_results`, `computed_attributes`, `hierarchy_data`, `aggregation_expressions`, `channel_aliases`, `output_registry` -- all match doc's description
- **SysMLParsingError and CodeGenerationError**: Both exist in initialization.py (lines 51, 63)
- **Step sequence**: The 7-step sequence with steps 3.5, 4.5, 5.5, 6.5 matches the code in `build_pipeline_context()` (lines 712-831)
- **Step 3.5 before Step 4**: Confirmed -- `_extract_hierarchy_and_rewrite_bindings()` is called at line 737, before `extract_design_attributes()` at line 742
- **Step 4.5 before Step 5**: Confirmed -- `_extract_and_filter_computed_attributes()` at line 745, `ParameterGroupDeriver` at line 753
- **Step 5.5 before Step 6**: Confirmed -- `build_output_registry()` at line 756, backtracker at line 766
- **4-phase registration protocol**: Phase 1 (canonical channels), Phase 2 (CHAIN aliases), Phase 3 (EXPOSE_PURE aliases), Phase 4 (transitive design attrs) -- all confirmed in `build_output_registry()` lines 533-673
- **`_rewrite_virtual_bindings()` exists**: Confirmed at line 260
- **`_scope_aggregation_expressions()` exists**: Confirmed at line 456
- **`_build_chain_aliases()` exists**: Confirmed at line 400
- **`find_instance_paths_for_partdef()` exists**: Confirmed at line 331
- **Virtual binding rewriting logic**: The override index and leaf extraction logic described in the doc matches the implementation in `_rewrite_virtual_bindings()` (lines 260-327)
- **OutputRegistry is a flat `dict[str, str]`**: Confirmed -- `self._index: dict[str, str]` in output_registry.py line 29

### Issues Found
- **Doc claims `orchestration/` directory will exist post-refactor** (lines 174-180): `orchestration/` does not yet exist. The doc correctly frames this as post-refactor, but the section heading "Post-refactor structure" might mislead readers into thinking it already exists. **This is an aspirational claim, not a current-state error.**
- **Doc table Step 3.5 mentions `chain_aliases`**: The code calls the variable `chain_aliases` at line 243 of initialization.py. Correct.
- **Phase 1a/1b/1c naming**: Doc uses Key_A, Key_B, Key_C, Key_D, Key_E, Key_F naming which matches the code comments in `build_output_registry()` (lines 537, 544, 546, 551, 560-562, 586-597). Verified.

### Could Not Verify
- The specific alias examples in the doc (e.g., `"cost_model.total_cost"` resolving to a canonical name) -- would require running on actual model data

---

## Doc 03: Resolution Overview

### Verified OK
- **"graph_builder.py is 1418 lines"**: Confirmed -- `wc -l` returns exactly 1418 lines. **Perfectly accurate.**
- **`_build_pipeline_module` at line 1291**: Confirmed at line 1291 of graph_builder.py
- **`_build_computed_attr_module` at line 641**: Confirmed at line 641 of graph_builder.py
- **`_build_aggregation_module` at line 922**: Confirmed at line 922 of graph_builder.py
- **3 module types**: CalcUsage, ComputedAttribute (FORMULA), Aggregation -- confirmed by the three `_build_*` functions
- **CalcUsage resolution via `BindingResolution` keyed by `"{usage_qn}|{param_name}"`**: Confirmed in `_build_pipeline_module` at line 1335: `mapping_key = f"{usage.qualified_name}|{param_name}"`
- **CalcUsage resolution checks `MODULE_OUTPUT` vs `ENTRY_POINT`**: Confirmed at lines 1349-1370 using `BindingResolutionType.MODULE_OUTPUT` and `BindingResolutionType.ENTRY_POINT`
- **FORMULA module parses `inputs.X` via regex**: Confirmed at line 670: `raw_inputs = re.findall(r"inputs\.(\w+)", ca.compiled_expression)`
- **FORMULA module uses `AttributeResolution` map**: Confirmed, `_build_attribute_resolution_map` at line 585 and usage at line 679
- **Aggregation module has SumTerm/SingletonTerm/LocalTerm processing**: Confirmed: SumTerms at line 960, SingletonTerms at line 1048, LocalTerms at line 1133
- **Aggregation SumTerms chase CHAIN redefinitions with cycle detection**: `_resolve_aggregation_input_channel` at line 760 has cycle detection via `_visited` set
- **SingletonTerms try registry-first then direct channel construction**: Confirmed at lines 1054-1078
- **LocalTerms check sibling aggregation outputs, then EXPOSE_PURE aliases, then fall back**: Confirmed at lines 1133-1182
- **`entry_points` is passed into all three builders and mutated**: Confirmed -- `entry_points` dict passed to all three `_build_*` functions and mutated in `_build_computed_attr_module` (line 718) and `_build_aggregation_module` (line 990+)
- **Entry point types**: LIBRARY_DEFAULT, DESIGN_ATTRIBUTE, USAGE_LITERAL -- confirmed in models.py lines 23-34
- **3 entry point types, 4 binding types**: Doc says "4 binding types: direct, transitive, unbound param, literal". The actual BindingType enum has 5 values (CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND). The doc's "4 binding types" uses different labels and a different count. See issues.
- **`ComputationGraph` fields**: `modules`, `entry_point_groups`, `execution_order` -- confirmed in models.py lines 174-188
- **Topological sort and channel validation**: `_unified_topological_sort` at line 1218 and `_validate_channel_references` at line 491 -- both confirmed
- **Refactored sub-modules list**: `input_resolver.py`, `module_factory.py`, `entry_point_classifier.py` -- these are aspirational (refactor targets), not yet created. The doc correctly frames them as the target state.

### Issues Found
- **"4 binding types: direct, transitive, unbound param, literal"**: The actual `BindingType` enum has **5** values: CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND. The doc's labels don't match the enum names and the count is wrong (4 vs 5). This should say "5 binding types: CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND".
- **"3 redefinition types: CHAIN (delegation), LITERAL (value override), none"**: `RedefinitionType` has 3 values: CHAIN, LITERAL, EXPRESSION. The doc uses "none" as a third type, but the actual third enum value is EXPRESSION. **Should be "3 redefinition types: CHAIN, LITERAL, EXPRESSION"**.
- **"3 x 4 x 3 x 2 x 3 = 216 combinations"**: Since the actual binding type count is 5 (not 4), the math would be 3 x 5 x 3 x 2 x 3 = 270, not 216. **The combinatorial count is wrong.**
- **Pseudocode for refactored orchestrator**: The pseudocode shows `classify_entry_points()` called before module building, `build_calc_usage_module()`, `build_formula_module()`, `build_aggregation_module()`, `group_entry_points()`, `topological_sort()`, `validate_channel_references()`. The actual code has a different flow: classify first, then build in sequence, then rebuild groups, then sort. The pseudocode is conceptually correct as a target but slightly simplified vs the actual current implementation which also has steps 6.5, 6.6, 6.6b, 6.7, 6.8 interspersed.

### Could Not Verify
- The specific example tracing (`alpha_split` with `p_total` and `f_alpha`) -- would need actual model data to verify

---

## Doc 04: Unified Input Resolver

### Verified OK
- **`_resolve_binding_via_registry` in `dependency_backtracker.py`**: Confirmed at line 462
- **`_resolve_reference_via_registry` in `dependency_backtracker.py`**: Confirmed at line 429
- **`_resolve_aggregation_input_channel` in `graph_builder.py`**: Confirmed at line 760
- **`_build_computed_attr_module` (inline resolution) in `graph_builder.py`**: Confirmed at line 641 -- inline resolution logic at lines 670-738
- **InputSource model exists**: Confirmed in `resolution/models.py` line 100
- **InputSource fields**: `source_type`, `producer_channel`, `qualified_name`, `param_group` -- all confirmed at lines 100-119

### Issues Found
- **InputSource described as `@dataclass(frozen=True)`**: Doc 04 line 154 says `@dataclass(frozen=True)`. Reality: `InputSource` is a **Pydantic BaseModel** (line 100 of models.py: `class InputSource(BaseModel):`), not a frozen dataclass. The shape is correct but the type system is wrong.
- **InputSource field `producer_channel: str | None`**: Doc says it's the only field set for module_output, and `qualified_name` for entry_point. The actual model matches this behavior, but the doc describes it as a dataclass when it's a Pydantic model.
- **ResolutionContext described as `@dataclass(frozen=True)`**: This class does not exist in the codebase. It is a **proposed refactor target**, not an existing class. The doc presents it as if describing the target architecture, which is consistent with the doc's purpose, but readers may expect to find it in the code.
- **`resolve_input()` function does not exist**: This is the proposed unified resolver function. It does not currently exist in the codebase. The doc correctly describes this as the refactoring target. The five strategies (DirectRegistryLookup, SysmlQnNormalization, ScopedRegistryLookup, ChainRedefinitionFollow, DesignAttributeLookup) are also proposed abstractions, not existing code.
- **Claim about "160+ lines of duplicated logic"**: Cannot precisely verify the duplication count, but the four existing functions do implement similar patterns (registry lookup, normalization, chain follow, entry point fallback), so the claim of significant overlap is credible.

### Could Not Verify
- The truth table examples (specific ref values and their resolution outcomes) -- these describe target behavior, not existing tests
- Strategy ordering claims (AGG_STRATEGIES promotes ChainRedefinitionFollow) -- these describe proposed behavior

---

## Summary of All Issues

| Doc | Severity | Issue |
|-----|----------|-------|
| 00 | Medium | Package structure shows `orchestration/` as existing; it does not. Partially acknowledged in note but diagram misleads. |
| 00 | Low | `CalcUsageData` listed in `data_models.py` but actually lives in `usage_extractor.py`. |
| 01 | Low | UNBOUND binding type doc says they only appear in `unbound_params`, but code also creates UNBOUND BindingInfo objects in `bindings`. |
| 03 | Medium | Says "4 binding types" but BindingType enum has 5 values. Combinatorial count 216 should be 270. |
| 03 | Low | Third redefinition type listed as "none" but actual enum has EXPRESSION as third value. |
| 04 | Medium | `InputSource` described as `@dataclass(frozen=True)` but is actually a Pydantic `BaseModel`. |
| 04 | Info | `resolve_input()`, `ResolutionContext`, and the 5 strategy classes are proposed refactor targets, not existing code. Doc is clear about this being a design doc, but worth noting for readers. |

### Accuracy Rating

- **Doc 00**: 90% -- mostly accurate, minor location errors and aspirational package structure
- **Doc 01**: 97% -- highly accurate, only minor nuance about UNBOUND binding placement
- **Doc 02**: 98% -- excellent accuracy, line counts exactly right, all functions verified
- **Doc 03**: 88% -- good structural accuracy, but binding type count and redefinition type labels are wrong
- **Doc 04**: 75% -- accurate about existing code locations, but the proposed architecture (resolve_input, ResolutionContext, strategies) is clearly future-state. The InputSource dataclass-vs-Pydantic error is a factual mistake.
