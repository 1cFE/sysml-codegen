# ADR-006: Part Hierarchy and Template Instantiation

## Status
**Accepted** - 2026-02-10

## Context

The Costed Component pattern (COST-PATTERN epic) requires CalcUsages embedded inside PartDefinitions — for example, `calc cost_model : PVModuleCostCalc` inside `part def 'PV Module'`. These are *template* CalcUsages: they define the cost calculation shape for a component type, but must be instantiated once per design PartUsage that uses that PartDef.

Prior to this work, codegen treated all CalcUsages uniformly — extracting them once from the model and generating one pipeline module per CalcUsage. This fails for the Costed Component pattern because:

1. A single template CalcUsage (e.g., `PV Module.cost_model`) may have multiple design instances (e.g., `solar_array.pv_module`, each with different parameter bindings)
2. Parameter bindings come from `:>>` redefinition chains in the design instance, not from the CalcUsage's own bindings
3. Module qualified names must reflect the full hierarchy path (e.g., `solar_array__pv_module__cost_model`), not just the template name

A spike (Item 1) validated that SysIDE exposes sufficient AST information for template detection and hierarchy traversal. Specifically:
- `type(calc_usage.owning_type).__name__` distinguishes `'PartDefinition'` (template) from `'PartUsage'` (concrete)
- Hierarchy traversal uses alternating `.types` and `owned_members` to walk the PartUsage→PartDef→child chain
- `:>>` redefinitions are `ReferenceUsage` elements with non-empty `owned_redefinitions`

## Decision

### Decision 1: Template Detection via `owning_type`

CalcUsages with `owning_type` that is a `PartDefinition` are classified as templates. CalcUsages with `owning_type` that is a `PartUsage` are classified as concrete. Detection uses `type(calc_usage.owning_type).__name__ == 'PartDefinition'`.

Template CalcUsages are NOT directly converted to pipeline modules. Instead, they serve as prototypes for virtual CalcUsage generation.

### Decision 2: Virtual CalcUsage Generation

For each template CalcUsage, codegen finds all PartUsages that instantiate the owning PartDef and generates one virtual `CalcUsageData` per (template, instance) pair.

**Process:**
1. Scan all CalcUsages; partition into templates (`is_template=True`) and concrete
2. For each template, find all PartUsages whose type matches the owning PartDef
3. For each (template, PartUsage) pair, create a virtual CalcUsageData with:
   - Qualified name reflecting the full hierarchy path
   - Bindings resolved through the design instance's `:>>` redefinitions
   - `owning_part_def_qn` preserved for binding rewriting in Step 3.5

**Example:** `PV Module.cost_model` (template) + `solar_array.pv_module` (PartUsage) → virtual CalcUsage `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model`

### Decision 3: Hierarchy-Aware Naming (ADR-003 Extension)

Virtual CalcUsage qualified names use the full design hierarchy path with `__` separators (per ADR-003):

- **Module name**: Lowercased full execution qualified name (EQN)
  - Example: `solarbatterydesign__solar_battery_plant__solar_array__pv_module__cost_model`
- **Channel name**: PQN format = module EQN + `__` + output name
  - Example: `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model__total_cost`

Deep paths use `__` separators throughout, extending ADR-003's convention to arbitrary nesting depth.

### Decision 4: `part redefines` Handling

Design instances use `part redefines` to specialize PartDef children with literal parameter values. Three redefinition types are handled:

1. **LITERAL** (`:>> wattage = 400.0`): The virtual CalcUsage's binding is rewritten in Step 3.5 to use the literal value as a DESIGN_ATTRIBUTE entry point.

2. **CHAIN** (`:>> capital_cost = cost_model.total_cost`): Resolved in the graph builder (Step 6.7) as a MODULE_OUTPUT wiring — the redefined attribute aliases an upstream module's output channel.

3. **Deep-path overrides** (`:>> pv_module.wattage = 400.0`): The target path `pv_module.wattage` is traversed through the hierarchy using `owned_redefinitions[0].redefined_feature.chaining_features` to reach the leaf attribute on the child PartUsage.

## Consequences

### Positive
- Uniform treatment of template and concrete CalcUsages downstream — the backtracker, graph builder, and generation layer see only concrete CalcUsageData
- Existing backtracker and graph builder work unchanged for virtual CalcUsages (they have the same data model)
- No changes to Jinja2 templates needed — virtual CalcUsages produce standard pipeline modules
- Deep hierarchy module paths get correct `__init__.py` files via existing `_ensure_package_init_files()` helper

### Negative
- Virtual CalcUsage explosion for models with many instance paths (O(templates × instances))
- Uniform-array assumption: all instances of an arrayed PartUsage share the same bindings (e.g., all 20 PV modules get `wattage=400.0`)
- Very long qualified names for deep hierarchies (mitigated by ADR-003's `__` convention being valid Python)

## References

- **Spike**: `.project/active/hierarchy-spike/report.md` (Q1, Q2, Q3, Q4, Q7, Q8)
- **Item 2**: commit `93c3910` — Template CalcUsage detection and virtual instantiation
- **Item 3**: commit `7887d07` — Redefinition extraction and deep-path resolution
- **Item 4**: commit `f49005c` — Pipeline integration for hierarchy-aware generation
- **ADR-003**: `docs/architecture/ADR-003-signal-identifiers.md` — Signal identifier naming conventions

## Changelog

| Date | Change |
|------|--------|
| 2026-02-10 | Initial version |
