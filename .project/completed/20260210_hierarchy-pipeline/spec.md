# Spec: Pipeline Integration -- Hierarchy-Aware Module Generation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-10 19:49 UTC
**Complexity:** HIGH
**Branch:** cost-pattern
**Epic:** COST-PATTERN (Item 4)

---

## Business Goals

### Why This Matters

Items 2 and 3 built the data extraction and transformation layers for the Costed Component pattern -- template CalcUsage detection, virtual instantiation, `:>>` redefinition resolution, multiplicity detection, and `sum()` parametric multiply transformation. But none of this data flows through the pipeline yet. Virtual CalcUsages sit in the extraction output with unresolvable bare-name bindings. `AggregationExpressionData` is produced but never consumed. The backtracker has no awareness of hierarchy outputs. The graph builder cannot create aggregation modules.

Without this item, codegen on the solar_battery model still produces only the 5 system-level CalcUsage modules. The 9 leaf-part cost calculations, 4 assembly aggregation rollups, and all hierarchy wiring remain invisible to the pipeline.

### Success Criteria

- [ ] Running codegen produces virtual CalcUsage modules (e.g., `solar_array__pv_module__cost_model`) with correct bindings and auto-implementations
- [ ] Running codegen produces aggregation modules (e.g., `solar_array__capital_cost`) with correct input wiring, auto-implementations, and `# source: aggregation` YAML comments
- [ ] System-level CalcUsages wire correctly to aggregation module outputs (e.g., `annualized_financial.total_capex` wires to `solar_battery_plant__capital_cost` output)
- [ ] Pipeline YAML shows correct topological ordering: leaf cost calcs -> aggregation -> system-level calcs
- [ ] All existing tests pass with zero regressions (313 baseline after Phase 2 + bug fixes)

### Priority

P1. This is the critical-path item that enables E2E validation (Item 5). All upstream dependencies (Items 1-3) are complete.

---

## Problem Statement

### Current State

- `extract_calculation_usages()` produces virtual CalcUsages with `expand_templates=True` (Item 2), but `_create_virtual_calc_usage()` copies template bindings verbatim -- `source_path="wattage"` references the parent PartDef's attribute, not a pipeline-resolvable path
- `extract_hierarchy_data()` produces `HierarchyExtractionResult` with redefinitions, design overrides, multiplicities, and aggregation expressions (Item 3), but is never called in the pipeline
- The backtracker's 6 resolution strategies cannot resolve bare PartDef attribute names (`"wattage"`) or aggregation module outputs
- The graph builder has no `_build_aggregation_module()` function and no mechanism to resolve symbolic `input_channels` from `AggregationExpressionData` to actual pipeline channel names
- The CLI generation layer has no path for aggregation module wrappers, auto-implementations, or YAML entries

### Desired Outcome

The full extraction -> analysis -> resolution -> generation pipeline processes virtual CalcUsages and aggregation expressions end-to-end, producing correct modules, auto-implementations, pipeline YAML, registry entries, and entry point schemas for the Costed Component pattern.

---

## Scope

### In Scope

1. **Pipeline orchestration** (`generation/initialization.py`):
   - New **Step 3.5**: Call `extract_hierarchy_data()`, rewrite virtual CalcUsage bindings using redefinition and design-override data
   - New **Step 4.7**: Store `AggregationExpressionData` on `PipelineContext`
   - New `PipelineContext` fields: `hierarchy_data`, `aggregation_expressions`

2. **Virtual CalcUsage binding rewriting** (new function in pipeline or extraction layer):
   - Transform bare PartDef attribute references (`source_path="wattage"`) into resolved values
   - LITERAL redefinitions (`:>> wattage = 400.0`) -> rewrite binding to `binding_type=LITERAL`, `literal_value=400.0`
   - CHAIN redefinitions (`:>> capital_cost = cost_model.total_cost`) -> rewrite binding `source_path` to chain target
   - Design overrides with deep-path (`:>> pv_module.wattage = 400.0`) -> trace through `target_path` to reach leaf attribute, apply literal
   - Unresolved bindings (no `:>>` override, no CalcDef default) -> entry point (existing behavior)

3. **Backtracker integration** (`analysis/dependency_backtracker.py`):
   - Virtual CalcUsages (with rewritten bindings) SHOULD flow through existing resolution strategies without backtracker changes
   - Extend backtracker awareness for aggregation module outputs so downstream CalcUsages can wire to them (e.g., `solar_battery_plant.capital_cost` resolves to aggregation module output channel)

4. **Graph builder aggregation module generation** (`resolution/graph_builder.py`):
   - New `_build_aggregation_module()` producing `PipelineModule` from `AggregationExpressionData`
   - Symbolic channel resolution: resolve `AggregationExpressionData.input_channels` (e.g., `"pv_module.capital_cost"`) through `:>>` CHAIN redefinitions to actual pipeline channel names (e.g., `solar_array__pv_module__cost_model__total_cost`)
   - Multiplicity count entry points (e.g., `module_count = 20`) as DESIGN_ATTRIBUTE Integer entry points
   - New **Step 6.7**: Build aggregation modules, add to modules list before unified topological sort
   - Extend output catalog (Step 2.5 or new Step 2.7) with aggregation module output channels
   - Verify Step 6.6 picks up aggregation module entry points

5. **Generation layer** (`cli/__init__.py`):
   - Extend `_generate_computed_attr_modules()` to also handle aggregation modules
   - Extend `_generate_computed_attr_stencils()` to also produce aggregation auto-implementations
   - Aggregation modules marked with `# source: aggregation` comment in pipeline YAML for debuggability
   - Module registry, `IMPLEMENTATION_BACKLOG.md`, and test generation include aggregation modules
   - Existing `_ensure_package_init_files()` handles deep hierarchy directories (no new logic)
   - Existing smart-regen logic upgrades stubs to auto-impls for virtual CalcUsage modules (no new logic)

6. **Entry point classification**:
   - `:>>` literal redefinitions (e.g., `wattage = 400.0`) -> DESIGN_ATTRIBUTE entry points
   - Multiplicity counts (e.g., `module_count = 20`) -> DESIGN_ATTRIBUTE entry points with Integer type
   - CalcDef defaults (e.g., `fastener_cost_per_child default := 0.50`) -> LIBRARY_DEFAULT entry points (existing behavior)

7. **Resolution models** (`resolution/models.py`):
   - Whether to add `is_aggregation: bool` or reuse `is_computed_attribute` is deferred to design phase

### Out of Scope

- Non-uniform array instances (all solar_battery arrays are uniform; document assumption)
- TEAx runtime changes
- Inline expressions in module wrappers (future optimization)
- Changes to CalcDef or computed attribute expression compilation (Phase 1 and Phase 2 reused as-is)
- `InvocationExpression` handling beyond `sum()` (sqrt, sin, etc.)
- New Jinja2 templates (existing templates reused)
- E2E validation on solar_battery model (Item 5)
- ADRs and documentation (Item 5)

### Edge Cases & Considerations

- **Unresolvable bindings on virtual CalcUsages**: If a template binding references a PartDef attribute with no `:>>` redefinition and no CalcDef default, it MUST become an entry point. The binding rewriting step MUST NOT silently drop unresolved bindings.
- **Multiple instantiation paths**: A PartDef like `PV Module` may be instantiated through multiple paths (e.g., both `solar_array.pv_module` and hypothetically `battery_system.pv_module`). Each path produces distinct virtual CalcUsages with potentially different design overrides.
- **Aggregation module naming collisions**: If two PartDefs have the same aggregation attribute name (e.g., both `Solar Array.capital_cost` and `Battery System.capital_cost`), module names MUST be disambiguated by owning part QN per ADR-003 (`solar_array__capital_cost` vs `battery_system__capital_cost`).
- **Circular `:>>` chains**: `:>> capital_cost = cost_model.total_cost` on a PartDef where `cost_model` references `capital_cost` back could create a cycle. The binding rewriting step SHOULD detect and warn on circular chains rather than infinite-looping.
- **Aggregation expressions with `has_unsupported_nodes=True`**: When `AggregationExpressionData.has_unsupported_nodes` is True, compilability MUST be set to MANUAL_REQUIRED after channel resolution. The module still generates, but with a stub implementation instead of auto-impl.
- **FORMULA module input types**: Aggregation module inputs SHOULD use `float` type (consistent with Bug 3 fix convention for FORMULA modules).

---

## Requirements

### Functional Requirements

> Requirements below are from user's request (epic Item 4 description) unless marked [INFERRED] or [FROM INVESTIGATION].

1. **FR-1**: Virtual CalcUsages MUST flow through the full pipeline (Steps 3-7) and produce `PipelineModule` instances with correct qualified names, module types, input/output wiring, and auto-implementations.

2. **FR-2**: A new pipeline step (Step 3.5) MUST call `extract_hierarchy_data()` and rewrite virtual CalcUsage bindings before the backtracker runs. Bare PartDef attribute references MUST be resolved through `:>>` redefinition chains and design-override deep-paths.

3. **FR-3**: A new pipeline step (Step 4.7) MUST store `AggregationExpressionData` on `PipelineContext` for downstream consumption by the graph builder.

4. **FR-4**: The graph builder MUST generate `PipelineModule` from `AggregationExpressionData` via a new `_build_aggregation_module()` function. Module naming MUST follow ADR-003: `{assembly_part_qn}__{attribute_name}`.

5. **FR-5**: Symbolic channel references in `AggregationExpressionData.input_channels` (e.g., `"pv_module.capital_cost"`) MUST be resolved to actual pipeline channel names by tracing through `:>>` CHAIN redefinitions to virtual CalcUsage output channels.

6. **FR-6**: Multiplicity counts MUST become DESIGN_ATTRIBUTE entry points with Integer type. `:>>` literal redefinitions MUST become DESIGN_ATTRIBUTE entry points. CalcDef defaults MUST remain LIBRARY_DEFAULT entry points.

7. **FR-7**: The backtracker MUST be able to resolve downstream CalcUsage bindings that reference aggregation module outputs (e.g., `solar_battery_plant.capital_cost` -> aggregation module output channel).

8. **FR-8**: Topological ordering MUST be correct: leaf cost calc modules -> aggregation modules -> system-level CalcUsage modules.

9. **FR-9**: The generation layer MUST produce TEAx module wrappers, auto-implementation files, pipeline YAML entries (with `# source: aggregation` comments), module registry entries, and IMPLEMENTATION_BACKLOG entries for aggregation modules by extending the existing computed attribute generation functions.

10. **FR-10**: [INFERRED] `PipelineContext` MUST be extended with `hierarchy_data: HierarchyExtractionResult | None` and `aggregation_expressions: list[AggregationExpressionData]` fields.

11. **FR-11**: [FROM INVESTIGATION] The binding rewriting step MUST handle three `:>>` resolution patterns:
    - LITERAL: `:>> wattage = 400.0` -> binding becomes `LITERAL` with value `400.0`
    - CHAIN: `:>> capital_cost = cost_model.total_cost` -> binding `source_path` updated to `cost_model.total_cost`
    - Design deep-path: `:>> pv_module.wattage = 400.0` -> trace `target_path` through hierarchy, apply literal to leaf CalcUsage binding

12. **FR-12**: [FROM INVESTIGATION] Aggregation module output channels MUST be registered in the backtracker's resolution infrastructure (e.g., `_output_catalog` or `_design_attr_binding_index` extension) so system-level CalcUsages can wire to them.

---

## Acceptance Criteria

### Core Functionality
- [ ] Virtual CalcUsages generate PipelineModules with correct qualified names (e.g., `solar_array__pv_module__cost_model`)
- [ ] Virtual CalcUsage bindings are rewritten: `source_path="wattage"` resolves to literal `400.0` via `:>>` chain
- [ ] Aggregation modules generate with correct input/output wiring (e.g., `solar_array__capital_cost` wires to child module outputs)
- [ ] Symbolic channel resolution works: `pv_module.capital_cost` -> `solar_array__pv_module__cost_model__total_cost`
- [ ] Multiplicity count entry points appear in parameter group schemas (e.g., `module_count: int = 20`)
- [ ] System-level CalcUsages wire to aggregation module outputs (e.g., `total_capex` -> `solar_battery_plant__capital_cost`)
- [ ] Topological ordering correct in pipeline YAML: leaf -> aggregation -> system
- [ ] Auto-implementations generated for virtual CalcUsage modules (reusing Phase 1 CalcDef expressions)
- [ ] Auto-implementations generated for aggregation modules (using transformed parametric-multiply expressions)
- [ ] Aggregation modules marked `# source: aggregation` in pipeline YAML
- [ ] Module registry includes all virtual CalcUsage and aggregation modules

### Quality & Integration
- [ ] All existing tests pass with zero regressions (313 baseline)
- [ ] `uv run mypy` passes on all modified code
- [ ] `uv run ruff check src/` passes on all modified code
- [ ] Integration tests cover: virtual CalcUsage through pipeline, aggregation module generation, topological ordering, symbolic channel resolution
- [ ] Unresolvable virtual CalcUsage bindings become entry points (not silently dropped)
- [ ] `has_unsupported_nodes=True` aggregation expressions generate with MANUAL_REQUIRED compilability

---

## Related Artifacts

- **Research:** `.project/research/20260202-180000_expression-compilation-and-inline-math-strategy.md`
- **Research:** `.project/research/20260109-205122_cost-modeling-codegen-changes.md`
- **Spike Report:** `.project/active/hierarchy-spike/report.md`
- **Item 2 Spec:** `.project/active/template-detection/spec.md`
- **Item 3 Spec:** `.project/active/hierarchy-resolution/spec.md`
- **Design:** `.project/active/hierarchy-pipeline/design.md` (to be created)
- **Epic:** `.project/backlog/epic_costed_component_pattern.md`

---

**Next Steps:** After approval, proceed to `/_my_design`
