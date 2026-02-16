# 15 - Naming Conventions

Definitive reference for every identifier format in sysml-codegen.
Authoritative sources: ADR-003, ADR-008, `core/qualified_names.py`, `core/identifier_types.py`.

## 1. SysML Qualified Name (SysML QN)

**Format**: `Package::PartDef::Element` (uses `::` separator, native SysML v2)
**Origin**: SysIDE adapter; stored in `CalculationDefinitionData.qualified_name`
**Example**: `SolarBatteryLibrary::BatteryPackCostCalc`

Used only at extraction boundaries. Immediately converted to internal formats downstream.

## 2. Element Qualified Name (EQN)

**Format**: `Package__PartDef__SubPart__Element` (uses `__` separator)
**Source of truth**: `build_element_qualified_name()` in `core/qualified_names.py`
**Stored in**: `CalcUsageData.qualified_name`, `DesignAttributeData.qualified_name`
**Uniqueness**: Guaranteed by SysML v2 ownership chain.

Constructed by traversing the AST owner chain and sanitizing each segment
(`sanitize_name()`: strip quotes, replace spaces/specials with `_`, collapse runs,
strip leading/trailing `_`). Segments are joined with `__`.

## 3. Parameter Qualified Name (PQN)

**Format**: `{EQN}__{param_name}` (extends an EQN with a parameter)
**Source of truth**: `build_parameter_qualified_name()` / `get_channel_name()`
**Stored in**: `EntryPoint.qualified_name`, `ModuleOutput.channel_name`
**Scope**: Entry points, channel names, module input wiring.

Key insight: when a calc input binds to a design attribute at a *different* scope,
the PQN is the design attribute's EQN, not `{usage_eqn}__{param_name}`. The
`binding_resolutions` mapping (ADR-003 Phase 7) is the single source of truth.

## 4. Module Name

**Format**: `{EQN}.lower()` (full EQN, lowercased)
**Source of truth**: `get_module_name()` in `core/qualified_names.py`
**Stored in**: `PipelineModule.name`
**YAML role**: Pipeline module instance key.

Previous approach used "last 2 segments" for readability but required collision
detection. Full EQN eliminates this complexity.

## 5. Module Type

**Format**: `{namespace}.{CalcDefName}Module`
**Source of truth**: `derive_module_type()` in `core/identifier_types.py`
**Stored in**: `PipelineModule.module_type`

Derivation from SysML QN:
1. Split on `::`
2. Package segments joined with `.`, lowercased (namespace)
3. Last segment (element name) gets `Module` suffix, case preserved

| SysML QN | Module Type |
|----------|-------------|
| `SolarBatteryLibrary::BatteryPackCostCalc` | `solarbatterylibrary.BatteryPackCostCalcModule` |
| `Standalone` (no package) | `StandaloneModule` |

Python file path derived the same way: `solarbatterylibrary/batterypackcostcalc.py`.

## 6. Channel Name

**Format**: PQN of the output = `{usage_EQN}__{output_attr_name}`
**Source of truth**: `get_channel_name()` in `core/qualified_names.py`
**Stored in**: `ModuleOutput.channel_name`, `InputSource.producer_channel`

Channels ARE PQNs. There is no separate "channel name" concept.

## 7. Output Registry Key Formats

The `OutputRegistry` (`core/output_registry.py`) maps lookup keys to canonical
channel names. Keys are registered in a strict 4-phase protocol. All keys use
dotted format; no SYSML_QN (`::`) keys are registered.

### Phase 1: Canonical Channels

**CalcUsage outputs** register three key formats:

| Key | Format | Example |
|-----|--------|---------|
| Key_A | `{instance_name}.{output}` | `cost_model.total_cost` |
| Key_B | (self-registered canonical) | `SBD__sbp__bs__bp__cost_model__total_cost` |
| Key_C | dotted hierarchy (strip design prefix) | `solar_battery_plant.battery_system.battery_pack.cost_model.total_cost` |

Key_C derivation (`OutputRegistry.derive_key_c()`): split EQN on `__`, drop
`segments[0]` (design PartDef prefix), join with `.`, append `.{output_attr}`.
Key_C is critical: ALL Phase 2 CHAIN aliases resolve exclusively via Key_C.

**Aggregation outputs** register:

| Key | Format | Example |
|-----|--------|---------|
| Key_D | `{part_usage}.{attr}` | `battery_system.capital_cost` |
| Key_E | full dotted instance path | `SolarBatteryDesign.solar_battery_plant.battery_system.capital_cost` |
| Key_E_stripped | Key_E minus design prefix | `solar_battery_plant.battery_system.capital_cost` |

**FORMULA outputs** register:

| Key | Format | Example |
|-----|--------|---------|
| Key_F | `{owning_part_name}.{attr}` | `Solar_Array.dc_capacity` |
| bare | `{attr}` alone | `dc_capacity` |

### Phase 2-4: Aliases

| Phase | Source | Alias Format | Resolves Against |
|-------|--------|-------------|-----------------|
| 2 | `:>>` CHAIN redefinitions | `{instance_path}.{attr}` | Phase 1 (via Key_C) |
| 3 | EXPOSE_PURE attributes | `{owning_part_short}.{attr}` | Phase 1+2 |
| 4 | Transitive design attrs | `{parent_part}.{attr}` | Phase 1-3 |

Collision policy: refuse overwrite, log warning, keep first registration.

## 8. SysML `::` to `__` Conversion

`sysml_to_python_qualified_name()`: straight `replace("::", "__")`.
Reverse: `python_to_sysml_qualified_name()`: `replace("__", "::")`.

`sanitize_name()` is applied per-segment *before* joining with `__`:
- Strip surrounding quotes
- Replace spaces with `_`
- Replace non-alphanumeric (except `_`) with `_`
- Collapse runs of `_` to single `_`
- Strip leading/trailing `_`
- Append `_` to Python reserved words

The `__` separator is applied *after* sanitization, so it is never collapsed.

## 9. Concrete Trace Example

SysML element: the `cost_model` CalcUsage inside the battery pack subsystem.

### SysML source (conceptual)
```sysml
package SolarBatteryLibrary {
    calc def BatteryPackCostCalc { in capacity_kwh; out total_cost; }
}
part def SolarBatteryDesign {
    part solar_battery_plant {
        part battery_system {
            part battery_pack {
                calc cost_model : BatteryPackCostCalc { ... }
            }
        }
    }
}
```

### Stage-by-stage naming

| Stage | Format | Value |
|-------|--------|-------|
| **SysML QN** (calc def) | `Pkg::CalcDef` | `SolarBatteryLibrary::BatteryPackCostCalc` |
| **EQN** (calc usage) | `__`-joined owner chain | `SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model` |
| **Module Name** | EQN lowercased | `solarbatterydesign__solar_battery_plant__battery_system__battery_pack__cost_model` |
| **Module Type** | namespace.CalcDefModule | `solarbatterylibrary.BatteryPackCostCalcModule` |
| **Channel (total_cost)** | PQN = EQN__output | `SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model__total_cost` |
| **Entry point (capacity_kwh)** | PQN = EQN__param | `SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model__capacity_kwh` |
| **Registry Key_A** | instance.output | `cost_model.total_cost` |
| **Registry Key_C** | dotted hierarchy (no design prefix) | `solar_battery_plant.battery_system.battery_pack.cost_model.total_cost` |

### In generated YAML

```yaml
solarbatterydesign__solar_battery_plant__battery_system__battery_pack__cost_model:
  module_type: solarbatterylibrary.BatteryPackCostCalcModule
  inputs:
    capacity_kwh: float design_params.SolarBatteryDesign__...__cost_model__capacity_kwh
  outputs:
    total_cost: float SolarBatteryDesign__...__cost_model__total_cost
```

### Downstream consumer wiring

When an aggregation module sums `battery_pack.capital_cost` and that attribute
has a `:>>` CHAIN redefinition to `cost_model.total_cost`, the Phase 2 alias
`solar_battery_plant.battery_system.battery_pack.capital_cost` resolves via
Key_C to the canonical channel
`SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model__total_cost`.

## 10. Summary Table

| Name | Separator | Case | Example |
|------|-----------|------|---------|
| SysML QN | `::` | Original | `SolarBatteryLibrary::BatteryPackCostCalc` |
| EQN | `__` | Mixed (sanitized) | `SolarBatteryDesign__solar_battery_plant__cost_model` |
| PQN | `__` | Mixed | `{EQN}__total_cost` |
| Module Name | `__` | lowercase | `solarbatterydesign__solar_battery_plant__cost_model` |
| Module Type | `.` + PascalCase | namespace lower, name original | `solarbatterylibrary.BatteryPackCostCalcModule` |
| Channel | `__` | Mixed (is a PQN) | `SBD__sbp__bs__bp__cost_model__total_cost` |
| Key_A | `.` | original | `cost_model.total_cost` |
| Key_C | `.` | original | `solar_battery_plant.battery_system.battery_pack.cost_model.total_cost` |
| Key_D | `.` | original | `battery_system.capital_cost` |
