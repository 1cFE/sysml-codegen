# Epic: Costed Component Pattern Support

**Epic ID**: COST-PATTERN
**Status**: In Progress
**Priority**: P1
**Created**: 2026-02-10
**Estimated Effort**: ~8-10.5 days

---

## Executive Summary

Enable codegen to natively support the **Costed Component pattern**: PartDefinitions with embedded CalcUsages, `:>>` redefinition chains, parameterized multiplicity (`[count]`), and `sum()` aggregation over arrayed children. This eliminates the need for flat, manually-wired cost pipelines and allows modelers to express hierarchical cost structures idiomatically in SysML v2.

**Critical Success Factor**: Running codegen on the solar_battery model produces a complete, executable LCOE pipeline -- from leaf-part cost calculations through assembly aggregation to system-level LCOE -- with zero handwritten `_impl.py` files and zero manually-authored CalcDefs for aggregation.

---

## Why This Epic?

**Current State**:
- CalcUsages inside PartDefinitions (e.g., `calc cost_model : PVModuleCostCalc` in `part def 'PV Module'`) are extracted but NOT instantiated per PartUsage -- codegen generates one module for the template, not per-instance modules
- `:>>` redefinition chains are not resolved -- `part redefines solar_array { :>> pv_module.wattage = 400.0; }` is invisible to codegen
- Multiplicity (`part pv_module : 'PV Module' [module_count]`) is ignored -- codegen assumes 1:1 usage-to-module mapping
- `sum()` aggregation expressions (`sum(pv_module.capital_cost)`) are classified as UNRESOLVABLE by the expression compiler
- Assembly aggregation expressions (`:>> capital_cost = sum(child.cost) + ...`) cannot be compiled -- they reference cross-hierarchy child attributes
- Modelers must flatten all hierarchy into explicit CalcDefs + CalcUsages (Approach E), creating ~100 lines of infrastructure per formula
- The solar_battery model has 9 leaf parts, 4 assembly parts, and 5 system-level CalcUsages that form a complete LCOE pipeline -- but codegen can only process the 5 system-level CalcUsages today

**Future State**:
- CalcUsages in PartDefs are automatically instantiated per PartUsage, producing modules like `solar_array__pv_module__cost_model`
- `:>>` redefinition chains resolve parameter bindings from design through hierarchy (e.g., `pv_module.wattage = 400.0` → literal entry point for `pv_module__cost_model`)
- Parameterized multiplicity handled via parametric multiply: one module per template, `sum()` over array becomes `count * single_instance_output`
- Assembly aggregation expressions compile to synthetic rollup modules with auto-implemented code
- Approach E Rules 1-4 become optional -- modelers can write idiomatic nested SysML
- The solar_battery model generates a complete, executable pipeline with no manual intervention

---

## Success Criteria

- [ ] Solar_battery model: all 9 leaf-part cost CalcUsages generate pipeline modules (e.g., `solar_array__pv_module__cost_model`)
- [ ] Solar_battery model: all 4 assembly aggregation expressions generate synthetic rollup modules (e.g., `solar_array__capital_cost`)
- [ ] Solar_battery model: 5 system-level CalcUsages wire correctly to aggregated cost outputs
- [ ] Solar_battery model: full LCOE pipeline executes end-to-end with correct numerical results
- [ ] `:>>` redefinition chains resolve literal values (`:>> pv_module.wattage = 400.0` → ENTRY_POINT)
- [ ] `:>>` redefinition chains resolve calc output aliases (`:>> capital_cost = cost_model.total_cost` → MODULE_OUTPUT wiring)
- [ ] Multiplicity handled via parametric multiply (`sum(pv_module.capital_cost)` → `module_count * pv_module__cost_model.total_cost`)
- [ ] All existing tests pass with zero regressions (313 baseline after Phase 2 + bug fixes)
- [ ] Template detection distinguishes CalcUsages in PartDefs (templates) from CalcUsages in design PartUsages (concrete)
- [ ] Deep hierarchy module naming follows ADR-003 (`solar_battery_plant__solar_array__pv_module__cost_model`)

---

## The Costed Component Pattern

The solar_battery model demonstrates a 4-level cost hierarchy that this epic targets:

### Pattern A: Leaf Parts with Embedded Cost Models

```sysml
part def 'PV Module' :> 'Costed Component' {
    attribute wattage : Real;
    attribute efficiency : Real;

    calc cost_model : PVModuleCostCalc {
        in wattage = wattage;      // Binds to parent PartDef attribute
        in efficiency = efficiency;
    }

    :>> capital_cost = cost_model.total_cost;   // EXPOSE via redefinition
    :>> idiot_index = capital_cost / raw_material_cost;  // FORMULA on redefined attrs
}
```

**Codegen must**: detect `cost_model` as a template CalcUsage, instantiate per PartUsage, resolve `in wattage = wattage` to the PartDef's `wattage` attribute, and resolve `:>> wattage = 400.0` from the design instance.

### Pattern B: Assembly Parts with Multiplicity and Aggregation

```sysml
part def 'Solar Array' :> 'Costed Component' {
    attribute module_count : Integer default := 20;
    part pv_module : 'PV Module' [module_count];

    :>> capital_cost =
        sum(pv_module.capital_cost) +
        sum(inverter.capital_cost) +
        array_bos.capital_cost +
        misc_hardware_cost;
}
```

**Codegen must**: detect `[module_count]` multiplicity, transform `sum(pv_module.capital_cost)` to `module_count * pv_module.capital_cost` (parametric multiply since all instances are uniform), resolve `pv_module.capital_cost` through the `:>> capital_cost = cost_model.total_cost` chain, and generate a synthetic aggregation module.

### Pattern C: Design Instance Redefinition

```sysml
part solar_battery_plant : 'Solar Battery Plant' {
    part redefines solar_array : 'Solar Array' {
        :>> pv_module.wattage = 400.0;       // Deep path literal
        :>> pv_module.efficiency = 0.21;
        :>> inverter.power_rating = 2000.0;
    }
}
```

**Codegen must**: resolve `part redefines` as specialization of the PartDef, traverse `:>> pv_module.wattage = 400.0` through the hierarchy (design → assembly → leaf part → CalcUsage binding), and produce a literal ENTRY_POINT for `solar_array__pv_module__cost_model.wattage = 400.0`.

---

## Backlog Items

### Item 1: Spike -- SysIDE AST Discovery for Hierarchy Patterns

**Status**: Complete
**Type**: Research
**Effort**: ~1 day (spec 0.5h, execute 5-6h, report 1h)
**Dependencies**: None
**Completed**: 2026-02-10

**Objective**: Validate that SysIDE exposes sufficient AST information for all Costed Component sub-patterns, using the solar_battery model as the probe target. Determine the exact AST node types, attribute names, and traversal patterns needed for Items 2-4.

**Result**: **GO** -- 10/10 questions passed, all 7 syside metamodel types available and populated. SysIDE AST provides sufficient structure for Items 2-4.

**Key Learnings** (see full report: `.project/active/hierarchy-spike/report.md`):

1. **`:>>` creates `ReferenceUsage`, NOT `AttributeUsage`** (Q2, Q8). All code processing `:>>` must filter on `ReferenceUsage` with non-empty `owned_redefinitions`. New attributes are `AttributeUsage`; redefined `:>>` attributes are `ReferenceUsage`. This is the single most important finding for Items 2-3.

2. **Deep-path chaining lives on the redefined feature** (Q4). `owned_redefinitions[0].redefined_feature.chaining_features` returns path components (e.g., `[PartUsage 'pv_module', AttributeUsage 'wattage']`). The redefining element itself has `name=None` and empty `owned_feature_chainings`. No heuristic value-matching needed.

3. **Multiplicity `cached_upper_bound` is N+1** (Q5). Syside uses exclusive upper bound convention despite KerML spec saying "inclusive." Use `cached_lower_bound` (correct for `[N]` syntax) or resolve via `upper_bound.referent.feature_value_expression.value`. Confirmed systematic across all 3 multiplicities in the model (20→21, 4→5, 8→9).

4. **Hierarchy traversal uses alternating `.types` and `owned_members`** (Q7). Full 8-step chain from `solar_battery_plant` to `PVModuleCostCalc` works via `next(iter(elem.types))` to get definition, then `owned_members` name lookup to get child usage.

5. **`sum()` is `InvocationExpression` with `function.name='sum'`** (Q6). Single operand is a `FeatureChainExpression` for the collection path. Both `walk_expression_tree()` and `traverse_expression()` visit it successfully.

6. **Template detection via `owning_type`** (Q1). `type(calc_usage.owning_type).__name__` cleanly returns `'PartDefinition'` (template) or `'PartUsage'` (concrete).

7. **agentic-mbse needs minimal extensions** (FR-11). Only `extract_invocation_info()` recommended for expression.py. Hierarchy traversal belongs in sysml-codegen. No changes needed to binding.py or helpers.py.

**Deliverables**:
- `scripts/spike_hierarchy_ast.py`
- `.project/active/hierarchy-spike/spec.md`
- `.project/active/hierarchy-spike/report.md`

---

### Item 2: Template CalcUsage Detection & Virtual Instantiation

**Status**: Complete
**Type**: Implementation
**Effort**: ~1.5-2 days (spec 1h, design 2h, plan 1h, execute 6-8h)
**Dependencies**: Item 1 (needs validated AST traversal patterns)

**Objective**: Detect CalcUsages owned by PartDefinitions, find all PartUsages that instantiate those PartDefs, and generate virtual `CalcUsageData` per instantiation -- with internal bindings resolved to parent-PartDef attributes.

**Current State**:
- ✅ `CalcUsageData` exists with `parent_part_path`, `qualified_name`, `bindings` (Phase 1)
- ✅ `_get_parent_part_path()` walks AST owner chain and collects PartUsage names
- ✅ `_extract_single_usage()` extracts data for each CalcUsage
- ✅ Expression compiler auto-implements compilable CalcDefs (Phase 1)
- ✅ `sanitize_name()` handles special chars (`&`, `$`, `@`, `-`) robustly (Bug 6 fix) -- use canonical `sanitize_name()` from `core/qualified_names.py` for all name sanitization (duplicate in `extractor.py` was removed)
- ❌ No detection of whether CalcUsage owner is PartDefinition (template) vs PartUsage (concrete)
- ❌ No `is_template` or `owning_part_def_qn` fields on CalcUsageData
- ❌ No function to find PartUsages of a given PartDefinition
- ❌ No virtual CalcUsage generation for per-instance expansion

**Spike Findings (Item 1) -- Key Inputs for This Item**:
- **Template detection**: `type(calc_usage.owning_type).__name__` returns `'PartDefinition'` (template) or `'PartUsage'` (concrete) -- clean distinguisher (Report Q1)
- **Hierarchy traversal**: Use alternating `.types` and `owned_members` to walk PartUsage→PartDef→child PartUsage chains. Specifically, `next(iter(usage.types))` gets the PartDefinition, then `owned_members` name lookup gets child usages (Report Q7)
- **`part redefines` vs plain `part`**: `part redefines` has non-empty `owned_redefinitions`; plain `part` has empty `owned_redefinitions` -- use `len(elem.owned_redefinitions) > 0` to distinguish (Report Q3)

**Scope**:

1. **Data model extensions** (`extraction/data_models.py` or `usage_extractor.py`):
   - Add `is_template: bool = False` to CalcUsageData
   - Add `owning_part_def_qn: str | None = None` to CalcUsageData
   - Add `raw_element: Any = None` to CalcUsageData (for re-inspection during instantiation)

2. **Template detection** (`extraction/usage_extractor.py`):
   - New function: `_get_owning_type_info(elem) -> tuple[str | None, Any | None]` -- check `type(elem.owning_type).__name__` for `'PartDefinition'` vs `'PartUsage'` (Report Q1)
   - Update `_extract_single_usage()` to set `is_template` and `owning_part_def_qn`
   - Unit tests: verify detection on leaf-part CalcUsages vs design-level CalcUsages

3. **PartUsage finder** (`extraction/usage_extractor.py`):
   - New function: `_find_part_usages_of_definition(model, part_def) -> list[tuple[Any, str]]` -- returns (PartUsage element, full qualified path) tuples
   - Helper: `_usage_instantiates_definition(usage, part_def, part_def_qn) -> bool` -- use `next(iter(usage.types))` to get the PartDefinition and compare (Report Q7). Must handle quoted names (`'PV Module'`)
   - Helper: `_build_full_part_path(elem) -> str` -- builds full dot-separated path from root to element
   - Unit tests: verify detection of `pv_module` as instantiation of `PV Module`

4. **Virtual CalcUsage generation** (`extraction/usage_extractor.py`):
   - New function: `_instantiate_template_calc_usages(model, calc_usages, warnings) -> list[CalcUsageData]` -- expands templates to concrete instances
   - New function: `_create_virtual_calc_usage(template, part_usage, part_def, part_path, model) -> CalcUsageData` -- creates one virtual instance with updated paths and qualified names
   - Virtual CalcUsage gets qualified name like `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model`
   - Internal bindings (`in wattage = wattage`) resolved: `wattage` maps to parent PartDef's attribute, which the backtracker will later resolve to a design entry point or module output
   - Update `extract_calculation_usages()` to call `_instantiate_template_calc_usages()` with `expand_templates=True` (default)
   - Unit tests: verify virtual CalcUsage generation for `PV Module.cost_model` across multiple PartUsages

**Out of Scope**:
- `:>>` redefinition resolution from design instances (Item 3)
- Multiplicity detection and `sum()` handling (Item 3)
- Pipeline integration (Item 4)
- Aggregation expression compilation

**Success Criteria**:
- [ ] CalcUsageData has `is_template`, `owning_part_def_qn`, `raw_element` fields
- [ ] Template detection correctly identifies CalcUsages in PartDefs vs PartUsages
- [ ] PartUsage finder traverses specialization chains to find all instances of a PartDef
- [ ] Virtual CalcUsages generated per PartUsage instantiation with correct qualified names
- [ ] Internal bindings (`in wattage = wattage`) reference parent PartDef attributes
- [ ] `extract_calculation_usages()` returns expanded list (templates replaced by concrete instances)
- [ ] All existing tests pass with zero regressions (313 baseline)
- [ ] `uv run mypy` passes on modified code

**Deliverables**:
- Modified: `src/sysml_codegen/extraction/usage_extractor.py`
- Modified: `src/sysml_codegen/extraction/data_models.py` (or usage_extractor dataclass)
- New: `tests/unit/test_template_detection.py`
- `.project/active/template-detection/spec.md`
- `.project/active/template-detection/design.md`
- `.project/active/template-detection/plan.md`

---

### Item 3: Redefinition Resolution, Multiplicity, & Aggregation Expressions

**Status**: Complete
**Type**: Implementation
**Effort**: ~1.5-2 days (spec 1h, design 2h, plan 1h, execute 6-8h)
**Completed**: 2026-02-10
**Dependencies**: Item 2 (needs template detection and virtual CalcUsage infrastructure)

**Objective**: Resolve `:>>` redefinition chains to bind design parameters through the hierarchy, detect multiplicity on PartUsages, handle `sum()` aggregation via parametric multiply, and compile assembly aggregation expressions into synthetic module data.

**Current State**:
- ✅ Template CalcUsages detected and virtual instances generated (Item 2)
- ✅ Expression compiler handles `+`, `-`, `*`, `/`, `**` operators (Phase 1)
- ✅ Computed attribute extraction handles FORMULA and EXPOSE_PURE (Phase 2)
- ✅ Backtracker has `::` qualified name handling infrastructure (Bug 2 fix): `_computed_attr_index` keyed by SysML QN, `_resolve_binding_to_usage()` Strategy 5 normalizes `::` → dotted format, `_determine_output_attr()` normalizes `::` paths. Deep-path `:>>` resolution can build on this foundation.
- ✅ Backtracker has self-referential binding guard (Bug 2 fix): prevents self-loops when `::` qualified names resolve to the same usage. Relevant for `:>>` chains where redefined attributes might reference themselves through a definition chain.
- ❌ `:>>` redefinition chains not resolved (neither literal nor chain)
- ❌ Multiplicity (`[count]`) not detected on PartUsages
- ❌ `sum()` classified as UNRESOLVABLE by expression compiler (InvocationExpression)
- ❌ No aggregation expression compilation (cross-child attribute references)

**Spike Findings (Item 1) -- Key Inputs for This Item**:
- **CRITICAL: `:>>` creates `ReferenceUsage`, NOT `AttributeUsage`** (Report Q2, Q8). All `:>>` scanning code must filter on `ReferenceUsage` with non-empty `owned_redefinitions`. New attributes are `AttributeUsage` with empty `owned_redefinitions` -- this is the clean distinguisher.
- **Deep-path chaining lives on the redefined feature, not the redefining element** (Report Q4). Access via `owned_redefinitions[0].redefined_feature.chaining_features` which returns `[PartUsage 'pv_module', AttributeUsage 'wattage']`. The redefining element has `name=None` and empty `owned_feature_chainings`. No heuristic value-matching needed -- resolution is fully structured.
- **Multiplicity `cached_upper_bound` is N+1 (exclusive convention)** (Report Q5). Systematic across all 3 model multiplicities (20→21, 4→5, 8→9). `_extract_multiplicity()` MUST use `cached_lower_bound` (correct for `[N]` syntax) or resolve via `upper_bound.referent.feature_value_expression.value`. DO NOT use `cached_upper_bound`.
- **`sum()` is `InvocationExpression` with `.function.name='sum'`** (Report Q6). Single operand is `FeatureChainExpression` for the collection path. Expression tree for aggregation is `OperatorExpression(+)` containing `InvocationExpression(sum)` children.
- **`default :=` uses `feature_value.is_default=True`** (Report Q9). Uniform across CalcDef params and part attributes. Can extract default literal via `feature_value_expression.value`.
- **Binding to redefined attr resolves to concrete PartDef** (Report Q10). `in total_capex = capital_cost` resolves to `Solar Battery Plant`'s redefined attribute, NOT the abstract `Costed Component`. The backtracker can follow this chain.
- **agentic-mbse extension**: Consider adding `extract_invocation_info()` to `agentic-mbse/expression.py` for function name extraction from `InvocationExpression` nodes (Report FR-11).

**Scope**:

1. **`:>>` redefinition chain resolution** (`extraction/`):
   - New function: `_resolve_binding_through_redefinition(original_binding, part_usage, part_def) -> BindingInfo` -- walks `:>>` chain on PartUsage to resolve template bindings
   - **All `:>>` elements are `ReferenceUsage` with non-empty `owned_redefinitions`** -- scan accordingly
   - Handle three `:>>` patterns:
     - **Literal redefinition**: `:>> wattage = 400.0` → `BindingType.LITERAL` with value 400.0
     - **Chain redefinition**: `:>> input_value = power_balance.p_net` → `BindingType.CHAIN` with source path
     - **Expression redefinition**: `:>> idiot_index = capital_cost / raw_material_cost` → `BindingType.EXPRESSION` with AST
   - Handle deep-path redefinitions from design: `part redefines solar_array { :>> pv_module.wattage = 400.0; }` → use `owned_redefinitions[0].redefined_feature.chaining_features` to resolve path components (e.g., `[PartUsage 'pv_module', AttributeUsage 'wattage']`), then traverse PartUsage→PartDef chain to reach leaf attribute
   - Helper: `_member_redefines_attribute(member, attr_name, part_def) -> bool` -- check `type(member).__name__ == 'ReferenceUsage'` and `owned_redefinitions[0].redefined_feature` name/chain match
   - Helper: `_extract_redefinition_value(member) -> float | None` -- extracts literal value from `feature_value_expression` on the `ReferenceUsage`
   - Unit tests: all three `:>>` patterns + deep-path traversal

2. **Multiplicity detection** (`extraction/`):
   - New function: `_extract_multiplicity(part_usage) -> int | str | None` -- returns literal count, attribute reference name, or None
   - Access via `part_usage.multiplicity` (returns `MultiplicityRange`)
   - **Use `multiplicity.cached_lower_bound`** (correct for `[N]`) **or `multiplicity.upper_bound.referent.feature_value_expression.value`** (most robust). **DO NOT use `cached_upper_bound`** -- it is N+1 due to syside exclusive convention
   - Add `multiplicity: int | None = None` to CalcUsageData (or to a new data model)
   - Unit tests: literal multiplicity (`[3]`), attribute-reference multiplicity (`[module_count]`), no multiplicity (singleton)

3. **`sum()` → parametric multiply transformation** (`extraction/`):
   - New function: `_transform_sum_to_parametric_multiply(expression_ast, part_usages) -> TransformedExpression`
   - Detect `InvocationExpression` with `function.name == 'sum'` and single operand (`FeatureChainExpression` for `array_part.attribute`)
   - Transform `sum(pv_module.capital_cost)` → `module_count * pv_module.capital_cost` (compile-time rewrite)
   - Resolve `pv_module.capital_cost` through `:>> capital_cost = cost_model.total_cost` chain to get the MODULE_OUTPUT channel name
   - Result: aggregation expression becomes compilable by the Phase 1 expression compiler (all operators are `+` and `*`, all operands are MODULE_OUTPUT channels or entry points)
   - Unit tests: sum over array, sum over singleton (identity), mixed sum + singleton + literal

4. **Aggregation expression data models**:
   - New: `AggregationExpressionData` dataclass:
     - `owning_part_qn: str` -- qualified name of the assembly PartDef
     - `attribute_name: str` -- the redefined attribute (e.g., `capital_cost`)
     - `transformed_expression: str` -- compiled Python expression after parametric multiply
     - `input_channels: list[str]` -- resolved MODULE_OUTPUT channel names
     - `entry_points: list[str]` -- multiplicity counts that become entry points
     - `compilability: Compilability`
   - Unit tests: verify data model construction for solar_array.capital_cost aggregation

**Out of Scope**:
- Pipeline integration (Item 4)
- Graph builder changes (Item 4)
- Non-uniform array instances (all instances in solar_battery model share same parameters)
- `InvocationExpression` handling beyond `sum()` (sqrt, sin, etc.)

**Success Criteria**:
- [ ] `:>>` literal redefinitions resolve to correct values
- [ ] `:>>` chain redefinitions resolve to correct source paths
- [ ] Deep-path `:>>` chains traverse through PartUsage→PartDef hierarchy
- [ ] Multiplicity detected on PartUsages and resolved to literal count
- [ ] `sum(array.attr)` transformed to `count * attr` (parametric multiply)
- [ ] `pv_module.capital_cost` resolved through `:>> capital_cost = cost_model.total_cost` chain
- [ ] `AggregationExpressionData` correctly models solar_array.capital_cost aggregation
- [ ] All existing tests pass with zero regressions (313 baseline)
- [ ] `uv run mypy` passes on modified code

**Deliverables**:
- Modified: `src/sysml_codegen/extraction/data_models.py` (RedefinitionType, RedefinitionData, MultiplicityData, SumTerm, SingletonTerm, LocalTerm, AggregationExpressionData, HierarchyExtractionResult)
- Modified: `src/sysml_codegen/extraction/expression_utils.py` (InvocationExpression handling in reconstruct_expression)
- New: `src/sysml_codegen/extraction/hierarchy_resolver.py` (extract_redefinitions, extract_design_overrides, extract_multiplicities, build_aggregation_expression, extract_hierarchy_data)
- New: `tests/unit/test_hierarchy_resolver.py` (42 tests)
- `.project/active/hierarchy-resolution/spec.md`
- `.project/active/hierarchy-resolution/design.md`
- `.project/active/hierarchy-resolution/plan.md`

---

### Item 4: Pipeline Integration -- Hierarchy-Aware Module Generation

**Status**: Not Started
**Type**: Integration
**Effort**: ~2-2.5 days (spec 2h, design 3h, plan 2h, execute 9-12h)
**Dependencies**: Items 2 + 3 (template instantiation and redefinition/aggregation resolution must be built)

**Objective**: Wire template CalcUsage instantiation, redefinition resolution, and aggregation expression compilation into the full extraction→resolution→generation pipeline, producing correct modules, auto-implementations, and pipeline YAML for the Costed Component pattern.

**Current State**:
- ✅ Template CalcUsages detected and virtual instances generated (Item 2)
- ✅ `:>>` redefinitions resolved, multiplicity detected, `sum()` transformed (Item 3)
- ✅ `AggregationExpressionData` models assembly aggregation expressions (Item 3)
- ✅ Pipeline has 7 steps + Step 4.5 (computed attributes) + Step 6.5 (expression compilation) + Step 6.6 (param_groups rebuild)
- ✅ Backtracker resolves MODULE_OUTPUT and ENTRY_POINT bindings, including `::` qualified name normalization (Bug 2 fix)
- ✅ Graph builder generates PipelineModules from CalcUsageData and ComputedAttributeData; `_build_pipeline_module()` and `_build_computed_attr_module()` no longer take `param_groups` parameter (Bug 1 fix refactored this)
- ✅ Step 6.6 rebuilds `param_groups` after ALL modules built (Bug 1 fix) — ensures late-discovered entry points (from FORMULA modules and, in future, aggregation modules) are included in schemas
- ✅ `_convert_derived_groups()` extracted as shared helper for param_group rebuilding (Bug 1 fix)
- ✅ `_ensure_package_init_files()` helper creates `__init__.py` in all intermediate directories (Bug 7 fix) — deep hierarchy module paths will get correct package structure automatically
- ✅ Smart-regen upgrades stubs to auto-impls when FULLY_COMPILABLE (Bug 5 fix) — previous partial codegen stubs will be automatically upgraded
- ❌ Pipeline doesn't process template CalcUsages (virtual instances not wired in)
- ❌ Backtracker doesn't resolve cross-hierarchy bindings (`:>>` chains through PartUsage→PartDef)
- ❌ Graph builder doesn't generate modules from `AggregationExpressionData`
- ❌ Generation layer doesn't produce auto-impls for aggregation modules

**Scope**:

1. **Pipeline orchestration** (`generation/initialization.py`):
   - Template expansion already happens in `extract_calculation_usages()` (Item 2, `expand_templates=True`) -- verify virtual CalcUsages flow through Steps 3-7
   - Add **Step 3.5**: Process `:>>` redefinition chains on virtual CalcUsages using design-level redefinition data. Resolve template bindings (`in wattage = wattage`) through the design's `:>> pv_module.wattage = 400.0` chain to produce literal or MODULE_OUTPUT binding resolutions.
   - Add **Step 4.7**: Extract aggregation expressions from assembly PartDefs (`:>>` attributes with `sum()` and cross-child references). Generate `AggregationExpressionData` for each. These become synthetic pipeline modules.
   - Store aggregation expressions on `PipelineContext` (new field)
   - Pass all data through to backtracker and graph builder

2. **Backtracker** (`analysis/dependency_backtracker.py`):
   - Accept virtual CalcUsages (they're regular CalcUsageData, just with longer qualified names) -- verify existing logic handles them
   - Extend `_resolve_binding_to_usage()` for deep-path resolution:
     - When a binding references `pv_module.capital_cost`, resolve through the `:>>` chain to find the MODULE_OUTPUT channel from `pv_module__cost_model`
     - Support arbitrary nesting depth (not just 2-level dotted paths)
     - **Build on existing `::` normalization infrastructure** (Bug 2 fix): Strategy 5 already normalizes `Package::Part::attr` → `Part.attr` for design attr transitive resolution. Deep-path hierarchy resolution extends this pattern with additional strategies for PartUsage→PartDef→child traversal.
   - Accept `AggregationExpressionData` for aggregation module dependency resolution:
     - Each `input_channel` on the aggregation expression is a dependency on an upstream module
     - Each `entry_point` (multiplicity count) is an ENTRY_POINT
   - Build extended binding index that includes inherited attributes from PartDefs via `:>>`

3. **Graph builder** (`resolution/graph_builder.py`):
   - Virtual CalcUsages should generate PipelineModules via existing `_build_pipeline_module()` -- verify qualified names, module types, and input/output wiring. **Note**: `_build_pipeline_module()` no longer takes `param_groups` (removed in Bug 1 fix); entry points are added to shared `entry_points` dict and Step 6.6 rebuilds param_groups after all modules are built.
   - New: `_build_aggregation_module(agg_expr: AggregationExpressionData) -> PipelineModule` -- generates a synthetic module for each assembly aggregation expression:
     - Module name: `{assembly_part_qn}__{attribute_name}` (e.g., `solar_array__capital_cost`)
     - Module type: PascalCase (e.g., `SolarArrayCapitalCost`)
     - Inputs: MODULE_OUTPUT channels from child modules + multiplicity counts as ENTRY_POINTs
     - Output: the aggregated cost attribute value
     - `is_computed_attribute = True` (reuse Phase 2 marker) or new `is_aggregation = True`
     - `compilability = FULLY_COMPILABLE`
     - Compiled expression: the parametric-multiply-transformed expression string
     - **Do NOT pass `param_groups`** -- follow the Bug 1 fix pattern where modules add entry points to the shared dict and Step 6.6 handles param_group rebuilding
   - Topological ordering: aggregation modules after their dependency modules (child cost calcs) and before their consumers (parent aggregation or system-level CalcUsages)
   - **Verify Step 6.6** picks up aggregation module entry points (multiplicity counts) -- the existing rebuild logic should work since it re-derives from the shared `entry_points` dict, but must be verified

4. **Generation layer** (`cli/__init__.py`, templates):
   - Virtual CalcUsage modules: reuse Phase 1 auto-impl template (CalcDef expressions are already compilable)
   - Aggregation modules: reuse Phase 2 computed attribute auto-impl template (aggregation expression compiles to Python)
   - Include all modules in pipeline YAML, module registry, `IMPLEMENTATION_BACKLOG.md`
   - Aggregation modules marked with `# source: aggregation` comment in YAML for debuggability
   - Deep hierarchy directory creation handled by existing `_ensure_package_init_files()` (Bug 7 fix) -- no new directory logic needed
   - Smart-regen stub-to-auto-impl upgrade handled by existing Bug 5 fix logic -- stubs from previous runs will be upgraded automatically
   - FORMULA module input types already use `float` (Bug 3 fix) -- aggregation module inputs should follow same convention

5. **Entry point handling**:
   - Resolved literal `:>>` redefinitions (e.g., `wattage = 400.0`) become DESIGN_ATTRIBUTE entry points
   - Multiplicity counts (e.g., `module_count = 20`) become DESIGN_ATTRIBUTE entry points with Integer type
   - CalcDef defaults (e.g., `fastener_cost_per_child default := 0.50`) remain LIBRARY_DEFAULT entry points

**Out of Scope**:
- Non-uniform array instances (all solar_battery arrays are uniform)
- TEAx runtime changes
- Inline expressions in module wrappers (future optimization)
- Changes to CalcDef or computed attribute expression compilation (Phase 1 and Phase 2 reused as-is)

**Success Criteria**:
- [ ] Virtual CalcUsages flow through full pipeline and produce PipelineModules
- [ ] Deep-path binding resolution works for arbitrary nesting depth
- [ ] Aggregation modules generate with correct input/output wiring
- [ ] Topological ordering correct: leaf cost calcs → aggregation → system-level calcs
- [ ] Pipeline YAML includes all module types in correct dependency order
- [ ] Auto-implementations generated for all template CalcUsage instances
- [ ] Auto-implementations generated for all aggregation modules
- [ ] Entry points correctly classified (DESIGN_ATTRIBUTE for `:>>` literals, LIBRARY_DEFAULT for defaults)
- [ ] Module registry includes all template and aggregation modules
- [ ] All existing tests pass with zero regressions (313 baseline)
- [ ] Integration tests for: simple template, deep hierarchy, aggregation with sum()

**Deliverables**:
- Modified: `src/sysml_codegen/generation/initialization.py` (Steps 3.5, 4.7, PipelineContext)
- Modified: `src/sysml_codegen/analysis/dependency_backtracker.py` (deep-path resolution, aggregation awareness)
- Modified: `src/sysml_codegen/resolution/graph_builder.py` (aggregation module generation)
- Modified: `src/sysml_codegen/resolution/models.py` (if new fields needed on PipelineModule)
- Modified: `src/sysml_codegen/cli/__init__.py` (if template/generation adjustments needed)
- New: `tests/integration/test_hierarchy_pipeline.py`
- `.project/active/hierarchy-pipeline/spec.md`
- `.project/active/hierarchy-pipeline/design.md`
- `.project/active/hierarchy-pipeline/plan.md`

---

### Item 5: E2E Validation & Documentation

**Status**: Not Started
**Type**: Testing + Documentation
**Effort**: ~1.5-2 days (spec 0.5h, design 1h, plan 0.5h, execute 6-8h, ADRs 3-4h)
**Dependencies**: Item 4 (pipeline integration must be complete)

**Objective**: Validate that the complete Costed Component pattern produces correct, executable pipelines on the solar_battery model, and formalize architectural decisions in ADRs.

**Scope**:

1. **Solar_battery model E2E validation**:
   - Run codegen on complete solar_battery model (library.sysml + costing.sysml + design.sysml)
   - Verify all 9 leaf parts generate cost modules with auto-implementations:
     - `PV Module` → `solar_array__pv_module__cost_model`
     - `String Inverter` → `solar_array__inverter__cost_model`
     - `Array BOS` → `solar_array__array_bos__cost_model`
     - `Battery Pack` → `battery_system__battery_pack__cost_model`
     - `Hybrid Inverter` → `battery_system__hybrid_inverter__cost_model`
     - `Battery BOS` → `battery_system__battery_bos__cost_model`
     - `Racking & Mounting` → `site_infra__racking__cost_model`
     - `Electrical Panel` → `site_infra__electrical_panel__cost_model`
     - `Permitting & Interconnect` → `site_infra__permitting__cost_model`
   - Verify allocation CalcUsages generate:
     - `solar_array__allocation_model`
   - Verify all 4 assembly aggregation modules generate:
     - `solar_array__capital_cost` (with `module_count` and `inverter_count` multipliers)
     - `battery_system__capital_cost` (with `pack_count` multiplier)
     - `site_infra__capital_cost` (singletons only, no multipliers)
     - `solar_battery_plant__capital_cost` (top-level aggregation)
   - Verify 5 system-level CalcUsages wire correctly:
     - `annualized_financial.total_capex` wires to `solar_battery_plant__capital_cost` output
     - `annualized_om.p_net_kw` wires to `p_net_kw` computed attribute module (Phase 2)
     - `lcoe` inputs wire to upstream CalcUsage outputs
   - Numerical validation: execute generated auto-impls with known input parameters and verify outputs
   - Integration tests as part of test suite (pattern: similar to Phase 1 and Phase 2 E2E tests)

2. **Regression validation**:
   - chain_spike model: all 3 CalcDefs still auto-implemented
   - solar_battery system-level CalcUsages: still correct (15 Phase 1 auto-impls)
   - CATF MFE: 19 auto-impls, 2 manual_required
   - All 313+ tests pass (baseline after Phase 2 + bug fixes)
   - TEAx primitive type support is complete (Bug 4 fix in TEAx) -- multi-output CalcUsage `float` channels are serializable without workarounds

3. **ADR-006: Part Hierarchy and Template Instantiation**:
   - Captures: Template detection strategy, virtual CalcUsage generation, hierarchy-aware naming, `part redefines` handling
   - Documents the decision to instantiate templates per-PartUsage (not keep as shared template)
   - References spike findings for empirical grounding

4. **ADR-007: Parametric Multiplicity and Aggregation**:
   - Captures: Parametric multiply strategy for uniform arrays, `sum()` transformation, synthetic aggregation module generation
   - Documents the uniform-array assumption and when flat expansion would be needed
   - Documents the `AggregationExpressionData` model and pipeline integration points

5. **ADR-002 Amendment: Aggregation Expressions**:
   - Rule 1 ("multiplicity is a parameter") → optional for uniform arrays (codegen handles parametric multiply)
   - Rule 3 ("aggregation is an explicit CalcDef") → optional (`:>> capital_cost = sum(children) + ...` works natively)
   - Rule 4 ("context is a parameter") → optional for `:>>` redefinition patterns (design binds through hierarchy)
   - Documents conditions: all array instances must be uniform; non-uniform arrays still require Approach E

6. **Epic closure**: Lessons Learned, status update, archive

**Success Criteria**:
- [ ] Solar_battery: all 9 leaf-part cost modules generate and auto-implement
- [ ] Solar_battery: all 4 assembly aggregation modules generate and auto-implement
- [ ] Solar_battery: all 5 system-level CalcUsages wire correctly to hierarchy outputs
- [ ] Solar_battery: LCOE pipeline produces numerically correct result
- [ ] `IMPLEMENTATION_BACKLOG.md` for solar_battery shows "0 functions to implement"
- [ ] All existing tests pass with zero regressions
- [ ] ADR-006 drafted with template instantiation decisions
- [ ] ADR-007 drafted with parametric multiply strategy
- [ ] ADR-002 amendment drafted with relaxed Rules 1, 3, 4

**Deliverables**:
- New: `tests/integration/test_costed_component_e2e.py`
- New: `docs/architecture/ADR-006-part-hierarchy-template-instantiation.md`
- New: `docs/architecture/ADR-007-parametric-multiplicity-aggregation.md`
- Modified: `docs/architecture/ADR-002-calculation-architecture.md` (amendment)
- `.project/active/hierarchy-e2e/report.md`
- `.project/active/hierarchy-e2e/spec.md`
- `.project/active/hierarchy-e2e/design.md`
- `.project/active/hierarchy-e2e/plan.md`

---

## Dependencies

**External**:
- `agentic-mbse` package: SysIDE adapter. **Minor extension recommended**: add `extract_invocation_info()` to `expression.py` for `sum()` function name extraction. No changes needed to `binding.py`, `helpers.py`, or `syside_adapter.py` type map (validated by Item 1 spike).
- SysIDE: All required AST information confirmed available and populated -- `:>>` redefinitions, `PartDefinition`/`PartUsage` owner types, multiplicity, `sum()` InvocationExpression, specialization chains. **Validated by Item 1 spike (10/10 PASS).**
- Solar_battery model: Must be accessible and correct (already in `tests/fixtures/solar_battery_model/`)

**Internal**:
- **Epic EXPR-CODEGEN (Phase 1)**: Complete. Provides expression compiler, auto-implementation templates, compilability classification, Step 6.5 pipeline integration.
- **Epic ATTR-EXPR (Phase 2)**: Complete. Provides computed attribute extraction (Step 4.5), FORMULA classification, synthetic module generation, backtracker computed attribute awareness.
- **Bug fixes (Phases 1+2)**: Complete (commit `93f0a55`). Fixed 6 codegen bugs: FORMULA entry point omission, FORMULA/EXPOSE backtracker wiring (including `::` QN infrastructure), FORMULA module input types, smart-regen stub upgrade, special char sanitization, intermediate `__init__.py` generation. These fixes provide reusable infrastructure for Items 2-4 (see per-item Current State sections).
- **TEAx ExitPoint primitive types**: Complete (TEAx commit `b2f91f2`). Fixed Bug 4 -- bare `float`/`int`/`str`/`bool` are now first-class ExitPoint and EntryPoint types. E2E validation (Item 5) will not need workarounds for multi-output channel serialization.
- Research: `.project/research/20260202-180000_expression-compilation-and-inline-math-strategy.md` (Phase 3 roadmap)
- Research: `.project/research/20260109-205122_cost-modeling-codegen-changes.md` (Costed Component gap analysis)

**Item Dependency Graph**:
```
Item 1: Spike -- AST Discovery (no dependencies)
  └─> Item 2: Template Detection & Instantiation (needs AST patterns from Item 1)
        └─> Item 3: Redefinition, Multiplicity, Aggregation (needs template infrastructure from Item 2)
              └─> Item 4: Pipeline Integration (needs Items 2 + 3)
                    └─> Item 5: E2E Validation & Documentation (needs integrated pipeline from Item 4)
```

All items are sequential. Item 1's go/no-go gate passed (GO) -- subsequent items proceed as designed with spike-informed adjustments noted in each item's "Spike Findings" section.

---

## Risks

| Risk | Likelihood | Impact | Mitigation | Status |
|------|-----------|--------|------------|--------|
| SysIDE doesn't expose `:>>` redefinition AST info | ~~Medium~~ | ~~High~~ | ~~Item 1 spike validates~~ | **RESOLVED** (Item 1): All 4 `:>>` patterns have `owned_redefinitions` linking to abstract interface. Element type is `ReferenceUsage`. |
| SysIDE doesn't expose multiplicity on PartUsages | ~~Low~~ | ~~Medium~~ | ~~Item 1 spike validates~~ | **RESOLVED** (Item 1): `MultiplicityRange` with `cached_lower_bound` and `upper_bound` expression chain. Note: `cached_upper_bound` is N+1 (exclusive). |
| `sum()` InvocationExpression structure is opaque | ~~Medium~~ | ~~Medium~~ | ~~Item 1 spike validates~~ | **RESOLVED** (Item 1): `InvocationExpression` with `function.name='sum'`, single `FeatureChainExpression` operand. |
| Deep-path `:>>` chains have ambiguous resolution | ~~Medium~~ | ~~High~~ | ~~Test with real models in spike~~ | **RESOLVED** (Item 1): Fully structured via `redefined_feature.chaining_features`. No heuristic needed. |
| Phase 1+2 bugs compound in Phase 3 | ~~High~~ | ~~High~~ | ~~Must fix before proceeding~~ | **RESOLVED**: All 7 bugs fixed (commit `93f0a55` + TEAx `b2f91f2`). Fixes provide reusable infrastructure: `::` QN handling, Step 6.6 param_groups rebuild, `_ensure_package_init_files()`, smart-regen stub upgrade, robust `sanitize_name()`. |
| Parametric multiply assumption fails (non-uniform arrays) | Low | Low | Solar_battery arrays ARE uniform. Document assumption in ADR-007. Add warning if non-uniform detected (fall back to Approach E). | Open |
| Virtual CalcUsage qualified names become very long | Low | Low | ADR-003 already uses `__` separator. Long names are valid Python identifiers. | Open |
| Performance impact from template expansion | Low | Low | Solar_battery has ~10 template CalcUsages × ~1-3 instantiations each. O(n*m) where n and m are small. | Open |
| Aggregation module generation conflicts with Phase 2 computed attributes | ~~Medium~~ | ~~Medium~~ | ~~Spike should verify no overlap~~ | **RESOLVED** (Item 1): Aggregation uses `ReferenceUsage` with `owned_redefinitions`; computed attributes use `AttributeUsage` with empty `owned_redefinitions`. Clean distinguisher (Q8). |
| agentic-mbse SysideAdapter needs extensions | ~~Medium~~ | ~~Medium~~ | ~~Item 1 spike determines~~ | **RESOLVED** (Item 1): Minimal -- only `extract_invocation_info()` recommended for expression.py. No type map, binding.py, or helpers.py changes needed. |

---

## Relationship to Research Roadmap

This epic implements **Phase 3** from the research report's phased roadmap:

| Research Roadmap Phase 3 Scope | Epic Item | Notes |
|-------------------------------|-----------|-------|
| "Part hierarchy extraction with multiplicity" | Items 1, 2, 3 | Spike validates, Item 2 extracts templates, Item 3 handles multiplicity |
| ":>> redefinition chain resolution" | Items 1, 3 | Spike validates AST, Item 3 implements resolution |
| "Tree-to-DAG flattening with synthetic rollup modules" | Item 4 | Graph builder generates aggregation modules from AggregationExpressionData |
| "Per-instance parameter context" | Items 3, 4 | Redefinition resolution provides per-instance parameter values; backtracker resolves through hierarchy |

**Approach E Rules becoming optional**:

| Rule | Status After This Epic |
|------|----------------------|
| Rule 1: Multiplicity is a parameter | Optional for uniform arrays (parametric multiply) |
| Rule 2: No nested CalcUsage-in-PartDef | Optional (template instantiation handles it) |
| Rule 3: Aggregation is an explicit CalcDef | Optional (`:>>` aggregation expressions compile to synthetic modules) |
| Rule 4: Context is a parameter | Optional for `:>>` patterns (design binds through hierarchy) |
| Rule 5: Every formula is a CalcDef | Already optional (Phase 2 FORMULA computed attributes) |

---

## Timeline

**Total Effort**: ~8-10.5 days (sequential)

| Item | Effort | Dependencies | Gate |
|------|--------|--------------|------|
| Item 1: Spike -- AST Discovery | ~1 day | None | Go/no-go on SysIDE capabilities |
| Item 2: Template Detection & Instantiation | ~1.5-2 days | Item 1 | Virtual CalcUsages generated correctly |
| Item 3: Redefinition, Multiplicity, Aggregation | ~1.5-2 days | Item 2 | `:>>` chains resolved, `sum()` transformed |
| Item 4: Pipeline Integration | ~2-2.5 days | Items 2 + 3 | Full pipeline produces correct modules |
| Item 5: E2E Validation & Documentation | ~1.5-2 days | Item 4 | Solar_battery validates end-to-end |

**Critical path**: All items are sequential. Item 1 is a gate: if SysIDE lacks critical capabilities, subsequent items are re-scoped before investing in implementation.

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

**What Went Well**:
- TBD

**What Could Improve**:
- TBD

**Surprises**:
- TBD

---

**Last Updated**: 2026-02-10 (Item 3 complete)
**Next Action**: Item 4 -- Pipeline Integration: Hierarchy-Aware Module Generation
