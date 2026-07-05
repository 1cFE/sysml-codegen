# Spec: Template CalcUsage Detection & Virtual Instantiation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-10 06:49 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Epic:** COST-PATTERN Item 2

---

## Business Goals

### Why This Matters

Codegen currently treats every CalcUsage as a concrete, one-off instance. When a CalcUsage lives inside a PartDefinition (e.g., `calc cost_model : PVModuleCostCalc` inside `part def 'PV Module'`), it is extracted once as a template-level module. But the PartDef may be instantiated multiple times via PartUsages (e.g., `part pv_module : 'PV Module'` inside `Solar Array`, `part inverter : 'String Inverter'` inside `Solar Array`, etc.). Each of those PartUsages needs its own pipeline module with a distinct qualified name and bindings scoped to that instance.

Without template detection and virtual instantiation, the solar_battery model's 9 leaf-part cost CalcUsages produce only ~3-4 template-level modules instead of the 9+ concrete per-instance modules needed for a complete LCOE pipeline. This blocks the entire COST-PATTERN epic.

### Success Criteria

- [ ] Running `extract_calculation_usages()` on the solar_battery model produces virtual CalcUsageData instances for each PartUsage that instantiates a PartDef containing CalcUsages
- [ ] Template CalcUsages (owned by PartDefinitions) are replaced by their concrete virtual instances — templates do NOT appear in the output list
- [ ] Virtual CalcUsage qualified names follow ADR-003 hierarchy naming (e.g., `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model`)
- [ ] Internal bindings on virtual instances reference parent PartDef attributes (for later backtracker resolution in Item 4)
- [ ] All existing tests pass with zero regressions (313 baseline)

### Priority

P1 — critical path for COST-PATTERN epic. Items 3 (redefinition/multiplicity), 4 (pipeline integration), and 5 (E2E validation) all depend on this.

---

## Problem Statement

### Current State

`extract_calculation_usages()` iterates all `CalculationUsage` elements via `SysideAdapter.elements_of_type()` and calls `_extract_single_usage()` for each. It produces one `CalcUsageData` per CalcUsage element found in the model.

`CalcUsageData` has 10 fields: `instance_name`, `calc_def_name`, `calc_def_qualified_name`, `module_type`, `bindings`, `unbound_params`, `source_file`, `source_line`, `parent_part_path`, `qualified_name`. None track whether the CalcUsage is a template (owned by a PartDefinition) or concrete (owned by a PartUsage).

`_get_parent_part_path()` walks the AST owner chain collecting PartUsage names, but does not check the owning element's type (PartDefinition vs PartUsage). A CalcUsage owned by `part def 'PV Module'` gets a parent path that includes the PartDef's name but doesn't flag it as a template.

The spike report (Item 1) confirmed that `type(calc_usage.owning_type).__name__` cleanly returns `'PartDefinition'` for templates and `'PartUsage'` for concrete instances (Report Q1). Hierarchy traversal via alternating `.types` and `owned_members` works for the full 8-step chain in the solar_battery model (Report Q7).

### Desired Outcome

`extract_calculation_usages()` detects template CalcUsages, finds all PartUsages that instantiate the owning PartDef, and returns virtual `CalcUsageData` instances — one per (PartUsage, CalcUsage) pair — with hierarchy-aware qualified names and internal bindings intact. Templates are removed from the output list, replaced by their concrete virtual expansions.

---

## Scope

### In Scope

1. **Data model extensions** on `CalcUsageData`:
   - `is_template: bool` — whether this CalcUsage is owned by a PartDefinition
   - `owning_part_def_qn: str | None` — qualified name of the owning PartDefinition (if template)
   - `raw_element: Any` — the SysIDE AST element for re-inspection during instantiation

2. **Template detection** in `_extract_single_usage()`:
   - Check `type(elem.owning_type).__name__` for `'PartDefinition'` vs other
   - Set `is_template` and `owning_part_def_qn` on the returned CalcUsageData

3. **PartUsage finder**:
   - Given a PartDefinition, find all PartUsage elements in the model that instantiate it
   - Handle specialization chains (PartUsage types a specialization of the target PartDef)
   - Handle quoted SysML names (`'PV Module'`) via `sanitize_name()`
   - Return (PartUsage element, full qualified path) tuples

4. **Virtual CalcUsage generation**:
   - For each template CalcUsage, expand to one concrete CalcUsageData per PartUsage instantiation
   - Virtual CalcUsage gets hierarchy-aware qualified name: `{design_path}__{part_usage_name}__{calc_name}`
   - Internal bindings (`in wattage = wattage`) are copied as-is — they reference parent PartDef attributes and will be resolved by the backtracker in Item 4
   - Unbound params are copied as-is

5. **Integration into `extract_calculation_usages()`**:
   - Add `expand_templates: bool = True` parameter
   - When enabled, call template expansion after initial extraction
   - Templates are replaced by their virtual instances in the returned list

### Out of Scope

- `:>>` redefinition resolution from design instances (Item 3)
- Multiplicity detection on PartUsages and `sum()` handling (Item 3)
- Backtracker changes for cross-hierarchy binding resolution (Item 4)
- Graph builder or generation layer changes (Item 4)
- Aggregation expression compilation (Item 3)
- Non-uniform array instances (assumption: all instances of a PartDef share the same CalcUsage structure)

### Edge Cases & Considerations

- **Multiple CalcUsages per PartDef**: A PartDef like `Solar Array` may contain both `cost_model` and `allocation_model`. Each MUST be independently instantiated per PartUsage. The expansion is per (PartUsage, CalcUsage) pair.
- **Nested templates**: `Solar Array` contains `part pv_module : 'PV Module'` which itself has `calc cost_model`. When expanding `Solar Array`'s CalcUsages, `pv_module`'s CalcUsages are found via the PartDef they live in (`PV Module`), not via `Solar Array`. Each PartDef level expands independently.
- **`part redefines` vs plain `part`**: Both are valid PartUsages. Design instances use `part redefines` (non-empty `owned_redefinitions`), library definitions use plain `part` (empty). The finder MUST match both since both instantiate the PartDef.
- **CalcUsages in design PartUsages (concrete)**: CalcUsages directly owned by PartUsages (e.g., `solar_battery_plant.energy_production`) are concrete and MUST NOT be treated as templates. `owning_type` check handles this.
- **PartDefs with no PartUsage instantiations**: If a PartDef contains CalcUsages but no PartUsage in the model instantiates it, the template CalcUsage is dropped with a warning. This is a valid edge case (abstract/unused PartDef).
- **Qualified name length**: Virtual CalcUsage names like `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model` can be long. This is expected and handled per ADR-003 (valid Python identifiers with `__` separator).

---

## Requirements

### Functional Requirements

> Requirements below are from the epic item and spike report unless marked [INFERRED].

**Data Model:**

1. **FR-1**: `CalcUsageData` MUST have an `is_template: bool` field (default `False`) indicating the CalcUsage is owned by a PartDefinition.
2. **FR-2**: `CalcUsageData` MUST have an `owning_part_def_qn: str | None` field (default `None`) containing the qualified name of the owning PartDefinition when `is_template=True`.
3. **FR-3**: `CalcUsageData` MUST have a `raw_element: Any` field (default `None`) storing the SysIDE AST element for re-inspection during instantiation.

**Template Detection:**

4. **FR-4**: `_extract_single_usage()` MUST detect whether a CalcUsage is owned by a PartDefinition by checking `type(elem.owning_type).__name__ == 'PartDefinition'` (spike Report Q1).
5. **FR-5**: When the owning type is a PartDefinition, `is_template` MUST be set to `True` and `owning_part_def_qn` MUST be set to the PartDefinition's qualified name.
6. **FR-6**: When the owning type is NOT a PartDefinition (e.g., PartUsage), `is_template` MUST remain `False` and the CalcUsageData is treated as concrete.

**PartUsage Finder:**

7. **FR-7**: A function MUST exist to find all PartUsage elements in the model that instantiate a given PartDefinition.
8. **FR-8**: The finder MUST match PartUsages by comparing `next(iter(usage.types))` to the target PartDefinition (spike Report Q7).
9. **FR-9**: The finder MUST handle quoted SysML names (e.g., `'PV Module'`) by comparing sanitized or qualified names, not raw name strings.
10. **FR-10**: The finder MUST traverse specialization chains — if a PartUsage types a PartDef that specializes the target PartDef, it SHOULD be included.
11. **FR-11**: The finder MUST return the full qualified path for each PartUsage (for building virtual qualified names).

**Virtual CalcUsage Generation:**

12. **FR-12**: For each template CalcUsage, one virtual `CalcUsageData` MUST be generated per PartUsage that instantiates the owning PartDef.
13. **FR-13**: Virtual CalcUsage `qualified_name` MUST follow ADR-003 hierarchy naming using `__` separator (e.g., `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model`).
14. **FR-14**: Virtual CalcUsage `instance_name` MUST be derived from the qualified name (flattened with `__`).
15. **FR-15**: Virtual CalcUsage `calc_def_name`, `calc_def_qualified_name`, `module_type`, `source_file`, and `source_line` MUST be copied from the template.
16. **FR-16**: Virtual CalcUsage `bindings` MUST be copied from the template. Internal bindings referencing parent PartDef attributes (e.g., `in wattage = wattage`) are left as-is for later backtracker resolution (Item 4).
17. **FR-17**: Virtual CalcUsage `unbound_params` MUST be copied from the template.
18. **FR-18**: Virtual CalcUsage `is_template` MUST be `False` (it is now a concrete instance).
19. **FR-19**: [INFERRED] Virtual CalcUsage `parent_part_path` MUST reflect the full instantiation path (e.g., `solar_battery_plant.solar_array.pv_module`), not the template's original parent path.

**Integration:**

20. **FR-20**: `extract_calculation_usages()` MUST accept an `expand_templates: bool` parameter (default `True`).
21. **FR-21**: When `expand_templates=True`, template CalcUsages MUST be replaced by their virtual instances in the returned list. Templates MUST NOT appear in the output.
22. **FR-22**: When `expand_templates=False`, CalcUsages are returned as-is (including templates with `is_template=True`). This supports testing and debugging.
23. **FR-23**: When a template CalcUsage has zero PartUsage instantiations, it MUST be dropped from the output with a warning in the ExtractionReport.
24. **FR-24**: [INFERRED] All name sanitization MUST use the canonical `sanitize_name()` from `core/qualified_names.py`.

---

## Acceptance Criteria

### Core Functionality

- [ ] `CalcUsageData` has `is_template`, `owning_part_def_qn`, and `raw_element` fields
- [ ] Template CalcUsages (e.g., `PV Module.cost_model`) have `is_template=True` and correct `owning_part_def_qn`
- [ ] Concrete CalcUsages (e.g., `solar_battery_plant.energy_production`) have `is_template=False`
- [ ] PartUsage finder finds all instantiations of a PartDef across the model (including through `part redefines`)
- [ ] PartUsage finder handles quoted SysML names and specialization chains
- [ ] Virtual CalcUsages generated per (PartUsage, template CalcUsage) pair
- [ ] Virtual CalcUsage qualified names follow `{path}__{calc_name}` convention per ADR-003
- [ ] Virtual CalcUsage bindings copied from template, referencing parent PartDef attributes
- [ ] `extract_calculation_usages(expand_templates=True)` returns virtual instances, NOT templates
- [ ] `extract_calculation_usages(expand_templates=False)` returns templates with `is_template=True`
- [ ] Warning emitted when template has zero PartUsage instantiations

### Quality & Integration

- [ ] All existing tests pass with zero regressions (313 baseline)
- [ ] New unit tests cover: template detection, PartUsage finding, virtual generation, expand_templates flag
- [ ] `uv run mypy src/` passes
- [ ] `uv run ruff check src/` passes

### Design Phase Validation

- [ ] Design MUST verify the spike's `owning_type` access pattern against the actual codebase (spike used direct attribute access; usage_extractor may need adapter calls)
- [ ] Design MUST verify how `build_element_qualified_name()` handles virtual instances that don't have a real AST element at the instantiation point
- [ ] Design MUST verify that the PartUsage finder can correctly match PartUsages via `next(iter(usage.types))` using the SysIDE adapter API

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_costed_component_pattern.md` (Item 2)
- **Spike report:** `.project/active/hierarchy-spike/report.md`
- **Spike spec:** `.project/active/hierarchy-spike/spec.md`
- **Research:** `.project/research/20260109-205122_cost-modeling-codegen-changes.md`
- **Bug fixes:** `.project/active/codegen-bug-fixes/spec.md` (prerequisite, complete)
- **Design:** `.project/active/template-detection/design.md` (to be created)
- **Plan:** `.project/active/template-detection/plan.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
