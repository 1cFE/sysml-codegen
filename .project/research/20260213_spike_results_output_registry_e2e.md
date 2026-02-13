# Research: Spike 8 -- OutputRegistry E2E Key Format Validation

**Date:** 2026-02-13
**Script:** `scripts/spikes/spike_output_registry_e2e.py`
**Models:** solar_battery (77 channels), e2e_attr_expr (15 channels)
**Addresses:** design_revision_comments_v3.md Issues 15, 16, 17, 20

---

## Phase 1 Findings: Registration Key Formats

### CalcUsage Concrete Keys

Format: three registration keys per output attribute.

| Key | Format | Example (solar_battery `lcoe.lcoe_per_mwh`) |
|-----|--------|----------------------------------------------|
| Key_A | `{instance_name}.{output}` | `lcoe.lcoe_per_mwh` |
| Key_B | `{EQN}__{output}` | `SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh` |
| Key_C | `{dotted_hierarchy}.{output}` | `solar_battery_plant.lcoe.lcoe_per_mwh` |

For concrete CalcUsages, Key_A and Key_C are always **different** (Key_C includes
the parent PartUsage scope, Key_A is just the instance name). Both models confirm this.

### CalcUsage Virtual Keys

For virtual CalcUsages, `instance_name == qualified_name` (full `__`-separated path).
This produces a hybrid Key_A mixing `__` and `.`:

| Key | Example (pv_module cost_model) |
|-----|-------------------------------|
| Key_A | `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model.material_cost` |
| Key_B | `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model__material_cost` |
| Key_C | `solar_battery_plant.solar_array.pv_module.cost_model.material_cost` |

**Key_A is unusable for virtual CalcUsages** -- it mixes `__` and `.` separators.
Key_C is the only fully dotted key that Phase 2 CHAIN aliases can resolve against.

### Aggregation Keys

| Key | Format | Example |
|-----|--------|---------|
| Key_D | `{part_usage_name}.{attribute}` | `solar_array.capital_cost` |
| Key_E | `{full_dotted_instance_path}.{attribute}` | `SolarBatteryDesign.solar_battery_plant.solar_array.capital_cost` |
| Alias_D | `{part_usage_name}.{alias}` | `solar_array.total_capex` |
| Alias_E | `{full_dotted_instance_path}.{alias}` | `SolarBatteryDesign.solar_battery_plant.solar_array.total_capex` |

**Key_E includes the design prefix** (see instance_path findings below). This means
Key_E will NOT match CHAIN binding source_paths which lack the design prefix.

solar_battery: 20 aggregation outputs. e2e_attr_expr: 0 (no hierarchy).

### FORMULA Keys

| Key | Format | Example |
|-----|--------|---------|
| Key_F | `{owning_part_name}.{python_name}` | `e2e_plant.power_mw` |

Channel construction: `get_channel_name(sysml_to_python_qualified_name(owning_part_qn) + "__" + python_name, python_name)`.

solar_battery: 1 FORMULA (`p_net_kw`). e2e_attr_expr: 6 FORMULAs.

### instance_path Includes Design Prefix: YES

All `ScopedAggregationData.instance_path` values include the design PartDef prefix
as the first `__`-separated segment:

```
instance_path:      SolarBatteryDesign__solar_battery_plant__solar_array
split('__'):        ['SolarBatteryDesign', 'solar_battery_plant', 'solar_array']
dotted form:        SolarBatteryDesign.solar_battery_plant.solar_array
dotted (no prefix): solar_battery_plant.solar_array
```

The design prefix is PascalCase (PartDef name); subsequent segments are snake_case
(PartUsage names).

### Collision Report

**Zero collisions** across both models. No key maps to two different channels.

---

## Phase 2 Findings: CHAIN Alias Resolution

### solar_battery: 41/41 resolved (100%)

- Total CHAIN redefinitions: 54
- DOTTED CHAIN redefs (have `.` in source_path, excludable BARE CAS codes): 41
- All 41 resolved successfully

**All 41 resolved via `CalcUsage.Key_C(virtual)`.**

This is the critical Issue 15 finding: without Key_C (the dotted hierarchy path),
all 41 CHAIN aliases would fail to resolve. Key_A for virtual CalcUsages uses
the hybrid `__`+`.` format which doesn't match the fully dotted canonical names
constructed by Phase 2 alias scoping.

### e2e_attr_expr: 0 CHAIN redefs

No hierarchy, no CHAIN redefinitions.

### Issue 15 Fix Validation: CONFIRMED

The proposed fix (adding Key_C = `".".join(segments[1:]) + "." + output_attr.name`)
is necessary and sufficient for Phase 2 resolution. Key_C strips the design prefix
and replaces `__` with `.`, producing keys compatible with the Phase 2 canonical
name format.

### instance_path -> dotted conversion: REQUIRED

Phase 2 alias scoping constructs `instance_path` by:
1. Finding virtual CalcUsages owned by the PartDef
2. Extracting parent QN (`rsplit("__", 1)[0]`)
3. Splitting on `__` and dropping the first segment (design prefix)
4. Joining with `.`

This produces dotted instance paths WITHOUT the design prefix, matching Key_C format.

---

## Phase 3 Findings: EXPOSE_PURE Alias Resolution

### e2e_attr_expr: 1/1 resolved

```
e2e_plant.total_capex -> component_cost.total_cost -> RESOLVED
  channel: E2EAttrExprDesign__e2e_plant__component_cost__total_cost
```

The `references` field reliably provides `[output_attr, instance_name]` ordering.
`references[1].name = "component_cost"`, `references[0].name = "total_cost"`.
Canonical name `component_cost.total_cost` matches Key_A for the concrete CalcUsage.

### solar_battery: 0/1 FAILED

```
Solar_Array.misc_hardware_cost -> allocation_model.total_allocation -> FAILED
```

**Root cause:** The EXPOSE_PURE is on PartDef `Solar_Array`, not a design PartUsage.
The `references` field gives PartDef-local names (`allocation_model.total_allocation`),
but the registry keys are instance-scoped (e.g.,
`solar_battery_plant.solar_array.pv_module.allocation_model.total_allocation` via Key_C).

This is **Issue 21** from the design review: EXPOSE_PURE on PartDefs produces unscoped
canonical names that can't resolve against instance-scoped registry keys.

### references Field Reliable: YES (for PartUsage EXPOSE_PURE)

For EXPOSE_PURE on PartUsages (like e2e_attr_expr), the references field correctly
identifies the CalcUsage instance and output attribute. For PartDef EXPOSE_PURE,
the field is correct but unscoped -- needs instance path prefixing or filtering.

---

## Phase 4 Findings: Transitive Default Resolution

### e2e_attr_expr: 1/1 resolved

```
e2e_plant.total_capex -> component_cost.total_cost -> RESOLVED
  channel: E2EAttrExprDesign__e2e_plant__component_cost__total_cost
```

### solar_battery: 0/1 FAILED

```
misc_hardware_cost -> allocation_model.total_allocation -> FAILED
```

**Same root cause as Phase 3:** `allocation_model.total_allocation` is PartDef-local.
This design attribute's `default_value` references a PartDef-level CalcUsage without
instance scoping.

### Both transitive defaults resolve: NO (1 of 2 fails)

The solar_battery failure shares the Issue 21 root cause. The design attribute
`misc_hardware_cost` on `Solar_Array` was likely originally an EXPOSE_PURE computed
attribute that was reclassified as a design attribute (with the expression text
preserved as `default_value`).

---

## Backtracker Comparison

### CHAIN Binding Match Rate: 6/6 (100%)

| Model | CHAIN Bindings | Matches | Rate |
|-------|---------------|---------|------|
| solar_battery | 4 | 4 | 100% |
| e2e_attr_expr | 2 | 2 | 100% |

All CHAIN bindings resolve via the prototype registry to the same channel as the
backtracker ground truth. The prototype registry is a correct replacement for the
backtracker's ad-hoc `_output_catalog` and `_aggregation_output_index`.

### REFERENCE Secondary Resolution: parent_part = segments[-2]

**4/4 cases confirmed across both models.**

| Model | Usage | Param | Leaf | segments[-2] | Resolves? |
|-------|-------|-------|------|-------------|-----------|
| solar_battery | annualized_om | p_net_kw | p_net_kw | solar_battery_plant | YES |
| solar_battery | annualized_financial | total_capex | capital_cost | solar_battery_plant | YES |
| e2e_attr_expr | energy | power_mw | power_mw | e2e_plant | YES |
| e2e_attr_expr | lcoe | annual_om | annual_om | e2e_plant | YES |

**Pattern:** `_get_parent_part_for_usage()` should return `segments[-2]` from
`usage.qualified_name.split("__")`. This is the **immediate parent PartUsage**
of the CalcUsage.

For all 4 observed cases, the consuming CalcUsage sits directly under the design root
PartUsage (depth 3: `Design__root_part__calc_usage`), so segments[-2] == segments[1]
(both are the design root). The algorithm `segments[-2]` is semantically correct
(immediate parent) and coincidentally produces the same result as `segments[1]`
(design root) for these cases.

No alternative candidate (deeper hierarchy segments, dotted combinations) produced
correct results. Only the immediate parent works.

---

## Design Comment Resolutions

| Issue | Finding | Resolution |
|-------|---------|------------|
| **15** | All 41 Phase 2 CHAIN aliases resolve exclusively via Key_C. Without Key_C, all fail. | **FIX CONFIRMED:** Add Key_C = `".".join(qn.split("__")[1:]) + "." + output` to Phase 1 CalcUsage registration. |
| **16** | `instance_path` uses `__` separator and INCLUDES design PartDef prefix as first segment. | **SPEC:** `instance_path` format is `{DesignPartDef}__{part_usage1}__{part_usage2}__...`. For consumer-facing dotted keys, strip first segment and replace `__` with `.`. |
| **17** | All 4 REFERENCE->MODULE_OUTPUT cases resolve with `segments[-2]` (immediate parent). | **SPEC:** `_get_parent_part_for_usage(usage) = usage.qualified_name.split("__")[-2]`. |
| **20** | Phase 2 CHAIN aliases have no DIRECT consumer (no CHAIN binding targets virtual CalcUsage outputs). But Key_C registration + Phase 2 alias registration creates a complete alias chain for future use. | **DECISION:** Keep Phase 2 with Issue 15 fix (Option A). Zero implementation cost since Key_C is already needed for CHAIN binding resolution. |

### Additional Finding: Issue 21 Confirmed

Phase 3 (EXPOSE_PURE) and Phase 4 (transitive defaults) both fail on solar_battery
for the same root cause: PartDef-level attribute references are unscoped. The design
should filter out EXPOSE_PURE on PartDefs (CHAIN aliases from Step 3.5 handle the
same semantics) or expand them per design instance.

**Recommendation:** Filter EXPOSE_PURE on PartDefs. CHAIN aliases already handle this
role (all 41 CHAIN aliases on solar_battery resolve correctly). EXPOSE_PURE should
only fire for PartUsage (concrete design) attributes.

---

## Key Format Specification (for design doc update)

### Phase 1 Registration Keys

```
CalcUsage outputs (per output attribute):
  Key_A: "{instance_name}.{output_attr_name}"
         Concrete: "lcoe.lcoe_per_mwh"
         Virtual:  "SolarBatteryDesign__...cost_model.total_cost" (HYBRID -- for backward compat only)
  Key_B: "{EQN}__{output_attr_name}"
         "SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"
  Key_C: "{dotted_hierarchy_path}.{output_attr_name}"    [NEW -- Issue 15 fix]
         "solar_battery_plant.lcoe.lcoe_per_mwh"
         Derivation: ".".join(EQN.split("__")[1:]) + "." + output_attr_name
         Strips design PartDef prefix, replaces __ with .

Aggregation outputs (per ScopedAggregationData):
  Key_D: "{part_usage_name}.{attribute_name}"
         "solar_array.capital_cost"
  Key_E: ".".join(instance_path.split("__")) + "." + attribute_name
         "SolarBatteryDesign.solar_battery_plant.solar_array.capital_cost"
         NOTE: includes design prefix (from instance_path)
  + Alias variants of Key_D and Key_E for each alias in expression.aliases

FORMULA computed attribute outputs:
  Key_F: "{owning_part_name}.{python_name}"
         "e2e_plant.power_mw"
  Channel: get_channel_name(sysml_to_python_qualified_name(owning_part_qn) + "__" + python_name, python_name)
```

### Phase 2 Alias Construction (CHAIN)

```
For each DOTTED CHAIN redefinition on a PartDef:
  instance_path = find_instance_paths_for_partdef(owning_part_qn)
    -> dotted, design prefix stripped
  alias_key    = instance_path + "." + redef.attribute_name
  canonical_key = instance_path + "." + redef.source_path (already dotted)
  Resolves against: Key_C (CalcUsage dotted hierarchy path)
```

### Phase 3 Alias Construction (EXPOSE_PURE)

```
For each EXPOSE_PURE on a PartUsage (NOT PartDef):
  canonical_name = "{references[1].name}.{references[0].name}"
  scoped_alias   = "{owning_part_name}.{python_name}"
  Resolves against: Key_A (CalcUsage instance.output)
```

### Secondary Resolution (REFERENCE bindings)

```
leaf_name  = source_path.rsplit("::", 1)[-1].strip("'")
parent_part = usage.qualified_name.split("__")[-2]
resolve_key = "{parent_part}.{leaf_name}"
Resolves against: Key_F (FORMULA) or Key_D (Aggregation) or Key_A (CalcUsage)
```

---

## Summary Statistics

| Metric | solar_battery | e2e_attr_expr |
|--------|--------------|---------------|
| Phase 1 channels | 77 | 15 |
| Phase 1 keys | 217 | 33 |
| Phase 1 collisions | 0 | 0 |
| Phase 2 CHAIN aliases | 41/41 (100%) | 0 (n/a) |
| Phase 3 EXPOSE_PURE | 0/1 (Issue 21) | 1/1 (100%) |
| Phase 4 transitive | 0/1 (Issue 21) | 1/1 (100%) |
| CHAIN binding match | 4/4 (100%) | 2/2 (100%) |
| REF secondary resolution | 2/2 via segments[-2] | 2/2 via segments[-2] |
