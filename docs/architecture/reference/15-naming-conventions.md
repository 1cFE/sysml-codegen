# 15 - Naming Conventions

Definitive reference for every identifier format in sysml-codegen.
Authoritative sources: `core/qualified_names.py`, `core/identifier_types.py`.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-NC-01 | EQN SHALL be constructed by joining sanitized owner-chain segments with `__` | `build_element_qualified_name()` uses `__` separator; segments pass through `sanitize_name()` |
| REQ-NC-02 | PQN SHALL extend an EQN with `__{param_name}` | `build_parameter_qualified_name()` returns `f"{eqn}__{param}"` |
| REQ-NC-03 | Module name SHALL equal the EQN lowercased | `get_module_name()` returns `eqn.lower()` |
| REQ-NC-04 | Module type SHALL use `{namespace}.{ElementName}Module` format | `derive_module_type()` lowercases package, preserves element case, appends `Module` |
| REQ-NC-05 | Channel names SHALL be PQNs — no separate channel concept exists | `get_channel_name()` returns `f"{eqn}__{output_attr}"` which is a PQN |
| REQ-NC-06 | `sanitize_name()` SHALL apply 6 transforms in order: strip quotes, spaces→`_`, non-alnum→`_`, collapse `_` runs, strip edge `_`, reserved-word suffix | Unit test on each transform rule |
| REQ-NC-07 | Registry keys SHALL use typed wrappers: scoped and alias registries use `ScopedKey` (dotted format); SysML QN registry uses `SysMLQN` (`::` format) in its own typed registry | Typed registry API enforces key types; see [10-output-registry](10-output-registry.md) |
| REQ-NC-08 | Identifier derivation SHALL sanitize each qualified-name segment before it becomes a class name, module file path, or FORMULA module_eqn/channel | `ModuleType.from_sysml` / `PythonModulePath.from_sysml` sanitize per segment; FORMULA module_eqn sites use `sanitize_qualified_name()`; conformance: `test_alias_agg_probe_generation`, `test_formula_quoted_owner` |
| REQ-NC-09 | Generation SHALL fail fast when two distinct SysML names sanitize to one output path, naming both source names and the shared path, across module, stencil, and schema outputs (two key spaces — modules and stencils share the derived python path) | `_check_duplicate_output_paths()` runs before `_clear_output_directory`; conformance: `test_duplicate_path_failfast` |

## 1. SysML Qualified Name (SysML QN)

**Format**: `Package::PartDef::Element` (uses `::` separator, native SysML v2)
**Origin**: SysIDE adapter; stored in [`CalculationDefinitionData.qualified_name`](09-data-models.md)
**Example**: `SolarBatteryLibrary::BatteryPackCostCalc`

Used at [extraction](01-extraction.md) boundaries and in the SysML QN typed registry
([10-output-registry](10-output-registry.md)). Converted to internal
formats for scoped lookups downstream.
**Type wrapper**: `SysMLQN` ([09-data-models](09-data-models.md#name-type-wrappers))

## 2. Element Qualified Name (EQN)

**Format**: `Package__PartDef__SubPart__Element` (uses `__` separator)
**Source of truth**: `build_element_qualified_name()` in `core/qualified_names.py`
**Stored in**: [`CalcUsageData.qualified_name`](09-data-models.md), `DesignAttributeData.qualified_name`
**Uniqueness**: Guaranteed by SysML v2 ownership chain.

Constructed by traversing the AST owner chain and sanitizing each segment
(`sanitize_name()`: strip quotes, replace spaces/specials with `_`, collapse runs,
strip leading/trailing `_`). Segments are joined with `__`.
**Type wrapper**: `EQN` ([09-data-models](09-data-models.md#name-type-wrappers))

## 3. Parameter Qualified Name (PQN)

**Format**: `{EQN}__{param_name}` (extends an EQN with a parameter)
**Source of truth**: `build_parameter_qualified_name()` / `get_channel_name()`
**Stored in**: [`EntryPoint.qualified_name`](09-data-models.md), [`ModuleOutput.channel_name`](09-data-models.md)
**Scope**: [Entry points](06-entry-point-classifier.md), channel names, module input wiring.

Key insight: when a calc input binds to a design attribute at a *different* scope,
the PQN is the design attribute's EQN, not `{usage_eqn}__{param_name}`. The
`binding_resolutions` mapping is the single source of truth.
See [input resolver](04-input-resolver.md) for how bindings determine PQN selection.
**Type wrapper**: `PQN` ([09-data-models](09-data-models.md#name-type-wrappers))

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
**Stored in**: [`PipelineModule.module_type`](09-data-models.md)

Derivation from SysML QN:
1. Split on `::`
2. Each segment passes through `sanitize_name()` (Item 5 / REQ-NC-08)
3. Package segments joined with `.`, lowercased (namespace)
4. Last segment (element name) gets `Module` suffix, case preserved

| SysML QN | Module Type |
|----------|-------------|
| `SolarBatteryLibrary::BatteryPackCostCalc` | `solarbatterylibrary.BatteryPackCostCalcModule` |
| `Standalone` (no package) | `StandaloneModule` |

Python file path derived the same way: `solarbatterylibrary/batterypackcostcalc.py`.

## 6. Channel Name

**Format**: PQN of the output = `{usage_EQN}__{output_attr_name}`
**Source of truth**: `get_channel_name()` in `core/qualified_names.py`
**Stored in**: [`ModuleOutput.channel_name`](09-data-models.md), [`InputSource.producer_channel`](09-data-models.md)

Channels ARE PQNs. There is no separate "channel name" concept (REQ-NC-05).

## 7. Output Registry Key Formats

The [`OutputRegistry`](10-output-registry.md) (`core/output_registry.py`) maps typed lookup keys
to canonical channel names (REQ-NC-07). Keys are registered in a strict 4-phase protocol
using four typed registries ([10-output-registry](10-output-registry.md)):
scoped (`ScopedKey` → `CanonicalChannel`), SysML QN (`SysMLQN` → `CanonicalChannel`),
alias (`ScopedKey` → `CanonicalChannel`), and the structured scoped-alias registry
(`ScopedAliasKey`, a `(scope, leaf)` tuple in `core/identifier_types.py`, →
`CanonicalChannel`) which holds the per-instance part-def EXPOSE aliases (Item 10).
**Type wrappers**: `ScopedKey` for scoped/alias keys, `SysMLQN` for SysML QN keys,
`CanonicalChannel` for all registry values ([09-data-models](09-data-models.md#name-type-wrappers))

### Phase 1: Canonical Channels

**CalcUsage outputs** register in the scoped registry:

| Key | Type | Format | Example |
|-----|------|--------|---------|
| Key_B | `CanonicalChannel` | canonical (self-registered) | `SBD__sbp__bs__bp__cost_model__total_cost` |
| Key_C | `ScopedKey` | dotted hierarchy (strip design prefix) | `solar_battery_plant.battery_system.battery_pack.cost_model.total_cost` |

Key_C derivation (`make_scoped_key()`): split EQN on `__`, drop
`segments[0]` (design PartDef prefix), join with `.`, append `.{output_attr}`.
Key_C is critical: ALL Phase 2 CHAIN aliases resolve exclusively via Key_C.
See [The Scope Problem](03-resolution-overview.md) for why Key_C is the primary resolution path.

**Aggregation outputs** register in the scoped registry:

| Key | Type | Format | Example |
|-----|------|--------|---------|
| Key_E_stripped | `ScopedKey` | dotted instance path (design prefix stripped) | `solar_battery_plant.battery_system.capital_cost` |

**FORMULA outputs** register in the SysML QN registry:

| Key | Type | Format | Example |
|-----|------|--------|---------|
| SysML QN | `SysMLQN` | `{owning_part_qn}::{name}` | `SolarBatteryLibrary::Solar_Array::panel_cost` |

### Phase 2-4: Aliases

| Phase | Source | Alias Type | Alias Format | Resolves Against |
|-------|--------|-----------|-------------|-----------------|
| 2 | `:>>` CHAIN [redefinitions](12-virtual-binding-rewrite.md) | `ScopedKey` | `{instance_path}.{attr}` | Phase 1 scoped (via Key_C) |
| 3 | [EXPOSE_PURE](16-computed-attributes.md) attributes | `ScopedKey` | `{owning_part_short}.{attr}` | Phase 1+2 |
| 4 | Transitive design attrs | `ScopedKey` | `{parent_part}.{attr}` | Phase 1-3 |

Collision policy for the alias registry: refuse overwrite, keep first registration;
each collision is recorded and logged at DEBUG, with a single WARNING count summary
per run (Item 7). The scoped, SysML QN, and scoped-alias registries are unique by
construction, so a duplicate key with a different channel raises.

## 8. SysML `::` to `__` Conversion

`sysml_to_python_qualified_name()`: straight `replace("::", "__")`.
Reverse: `python_to_sysml_qualified_name()`: `replace("__", "::")`.

`sanitize_name()` is applied per-segment *before* joining with `__`:
- Strip surrounding quotes
- Replace spaces with `_`
- Replace non-alphanumeric (except `_`) with `_`
- Collapse runs of `_` to single `_`
- Strip leading/trailing `_`
- Append `_` to Python reserved words (`class`, `def`, `import`, `from`, `return`, `yield`)

The `__` separator is applied *after* sanitization, so it is never collapsed.

`sysml_to_python_qualified_name()` itself does **not** sanitize — it is a bare
separator swap kept for the QN-**matching** sites that compare against raw keys.
The name-**emission** sites (the FORMULA module_eqn: `output_registry_builder.py`
producer + `graph_builder.py` consumer/`part_eqn`, and the EXPOSE_PURE
normalization) use `sanitize_qualified_name()` — split on `::`, `sanitize_name`
each segment, join with `__` — so a quoted owner (`Lib::'Margin Part'`) emits a
valid identifier (`Lib__Margin_Part`) instead of leaking quotes (REQ-NC-08). The
FORMULA module_eqn leaf is built from `ca.python_name`, never by re-sanitizing
`ca.name`, so the registry-produced and graph-consumed channels are identical by
construction.

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
| **CanonicalChannel** | PQN of output | `SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model__total_cost` |
| **ScopedKey (Key_C)** | dotted hierarchy (no design prefix) | `solar_battery_plant.battery_system.battery_pack.cost_model.total_cost` |

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

| Name | Separator | Case | Type | Example |
|------|-----------|------|------|---------|
| SysML QN | `::` | Original | `SysMLQN` | `SolarBatteryLibrary::BatteryPackCostCalc` |
| EQN | `__` | Mixed (sanitized) | `EQN` | `SolarBatteryDesign__solar_battery_plant__cost_model` |
| PQN | `__` | Mixed | `PQN` | `{EQN}__total_cost` |
| Module Name | `__` | lowercase | `str` | `solarbatterydesign__solar_battery_plant__cost_model` |
| Module Type | `.` + PascalCase | namespace lower, name original | `str` | `solarbatterylibrary.BatteryPackCostCalcModule` |
| CanonicalChannel | `__` | Mixed (is a PQN) | `CanonicalChannel` | `SBD__sbp__bs__bp__cost_model__total_cost` |
| ScopedKey (Key_C) | `.` | original | `ScopedKey` | `solar_battery_plant.battery_system.battery_pack.cost_model.total_cost` |

## Related Documents

- **Pipeline context**: [00-pipeline-overview](00-pipeline-overview.md) — where naming applies across all 7 steps
- **Extraction (origin)**: [01-extraction](01-extraction.md) — SysML QN is produced here
- **Resolution (consumer)**: [03-resolution-overview](03-resolution-overview.md) — The Scope Problem relies on Key_C
- **Input resolver**: [04-input-resolver](04-input-resolver.md) — strategies use typed registry lookups (ScopedKey, SysMLQN)
- **Module factory**: [05-module-factory](05-module-factory.md) — EQN → module name/type derivation
- **Entry points**: [06-entry-point-classifier](06-entry-point-classifier.md) — PQN used for entry point QN
- **Registry**: [10-output-registry](10-output-registry.md) — Key format details, 4-phase protocol
- **Backtracker**: [11-analysis-backtracker](11-analysis-backtracker.md) — Key_C scoped resolution (Step 0)
- **Virtual bindings**: [12-virtual-binding-rewrite](12-virtual-binding-rewrite.md) — Phase 2 CHAIN aliases
- **Computed attributes**: [16-computed-attributes](16-computed-attributes.md) — Phase 3 EXPOSE_PURE aliases
- **Registry generation**: [20-module-registry-generation](20-module-registry-generation.md) — import paths from module type
- **Pipeline YAML**: [21-pipeline-yaml-generation](21-pipeline-yaml-generation.md) — channel format in YAML
- **Data models**: [09-data-models](09-data-models.md) — field definitions for all named entities
