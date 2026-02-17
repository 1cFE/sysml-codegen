# 10 - Output Registry

## What Problem It Solves

SysML bindings reference upstream outputs using different string formats depending
on the AST node type and where the reference appears:

| AST node | What extraction produces as `source_path` | Example |
|----------|-------------------------------------------|---------|
| `FeatureChainExpression` | dotted local path (scope-relative) | `cost_model.total_cost` |
| `FeatureReferenceExpression` | SysML qualified name (global) | `SolarBatteryLibrary::Solar_Array::capital_cost` |
| `:>>` redefinition target | dotted hierarchy path | `solar_battery_plant.battery_system.battery_pack.capital_cost` |

These are all different strings that may refer to the **same output channel**.
The registry's job is to map every one of these reference formats to the single
canonical channel name for that output, so that the resolver can do O(1) lookup
regardless of which format the binding used.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-OR-01 | Registry SHALL map every reference format (FCE dotted path, FRE qualified name, redefinition target) to a canonical PQN [channel name](15-naming-conventions.md) | All Phase 1 key formats present in `_index` |
| REQ-OR-02 | `resolve()` SHALL perform exact-match dict lookup with no normalization or fallback | `resolve()` body is `return self._index.get(source_path)` |
| REQ-OR-03 | Collision policy SHALL refuse overwrites — first registration wins with warning logged | `register()` and `register_alias()` both check `key in self._index` |
| REQ-OR-04 | `register_alias()` SHALL enforce phase ordering — target must already be in `_canonical` | Guard: `if canonical_channel not in self._canonical: return` |
| REQ-OR-05 | Phase 1 SHALL register Key_A/B/C (CalcUsage), Key_D/E/bare (Aggregation), Key_F/bare/QN (FORMULA) | Key format tables in each sub-phase |
| REQ-OR-06 | Phase 2-4 aliases SHALL resolve through the registry before registering | `registry.resolve(alias.canonical_name)` precedes `register_alias()` |
| REQ-OR-07 | Key_C SHALL be constructed by stripping design prefix from EQN and joining with dots | `derive_key_c()`: split on `__`, drop `segments[0]`, join with `.` |

## What It Is

The `OutputRegistry` (in `core/output_registry.py`) is a **flat, scopeless**
`dict[str, str]` mapping every possible reference key to a **canonical channel
name**. `resolve(key)` does a single exact-match dict lookup -- no
normalization, no cascade, no fallback.

**The registry has no concept of scope.** It does not know which module is asking.
A key like `cost_model.total_cost` (Key_A) is ambiguous if two scopes both
contain a `cost_model` instance -- the first registration wins, the second is
refused with a warning. This is intentional: scope-awareness is the
[resolver's](04-input-resolver.md) responsibility, not the registry's. The
resolver [prepends the consumer's scope](03-resolution-overview.md#the-scope-problem)
to produce a Key_C lookup that is unambiguous. The registry just needs to have
Key_C registered.

A canonical channel name is the PQN-format string produced by `get_channel_name()` (see [naming conventions](15-naming-conventions.md)):

```
"{usage_qualified_name}__{output_attr_name}"
e.g. "SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"
```

The registry replaces five ad-hoc indexes that lived in the backtracker. Its internal state
is two fields: `_index: dict[str, str]` (all keys -> canonical) and `_canonical: set[str]`
(the set of valid canonical channel names, used for phase-ordering enforcement).

## API

| Method | Phase | Purpose |
|---|---|---|
| `register(canonical, lookup_keys)` | 1 | Register a canonical channel + its Phase 1 lookup keys |
| `register_alias(alias, canonical)` | 2-4 | Register an alias pointing to an already-registered canonical |
| `resolve(source_path) -> str\|None` | runtime | Exact-match lookup; returns `None` on miss |
| `derive_key_c(usage_qn, attr_name)` | helper | Builds the dotted hierarchy key (strips design prefix) |
| `canonical_channels` (property) | read | `frozenset[str]` of all canonical channel names (used by graph builder for membership checks) |

**Collision policy**: both `register()` and `register_alias()` refuse overwrites. If a key
already maps to a different channel, a warning is logged and the first registration wins.

## The 4-Phase Registration Protocol

Phases must execute in order. `register_alias()` enforces this: the target canonical channel
must already exist in `_canonical`, or the alias is rejected with a warning.

### Phase 1 -- Canonical Channels

Three sub-phases populate the canonical channel set. Each sub-phase corresponds
to one of the three [module types](05-module-factory.md): CalcUsage, Aggregation, FORMULA.

**Phase 1a: CalcUsage outputs** (`build_output_registry`, lines 537-548)

For each CalcUsage + each output attribute on its CalcDef, three keys are registered:

| Key | Format | Example |
|---|---|---|
| Key_A | `{instance_name}.{attr}` | `lcoe.lcoe_per_mwh` |
| Key_B | canonical (self-registered) | `SBD__sbp__lcoe__lcoe_per_mwh` |
| Key_C | dotted hierarchy, design prefix stripped | `solar_battery_plant.lcoe.lcoe_per_mwh` |

Key_C is derived by `OutputRegistry.derive_key_c()` (REQ-OR-07): split the usage EQN on `__`,
drop `segments[0]`, join with `.`, append `.{attr}`. Key_C is the most critical key —
it is the [scoped key](03-resolution-overview.md#the-scope-problem) that the
[input resolver](04-input-resolver.md) constructs to disambiguate cross-scope references.
Empirically, ALL Phase 2 CHAIN aliases resolve exclusively via Key_C.

**Phase 1b: Aggregation outputs** (`build_output_registry`, lines 550-584)

For each [`ScopedAggregationData`](09-data-models.md), registered keys include:

| Key | Format | Example |
|---|---|---|
| Key_D | `{part_usage}.{attr}` | `solar_array.total_capex` |
| Key_E | full dotted instance path | `SBD.sbp.solar_array.total_capex` |
| Key_E_stripped | Key_E without design prefix | `sbp.solar_array.total_capex` |
| bare | just the attribute name | `total_capex` |
| alias variants | same patterns for each `agg.expression.aliases` entry | ... |

**Phase 1c: FORMULA outputs** (`build_output_registry`, lines 586-605)

For each [`ComputedAttributeData`](09-data-models.md) with classification `FORMULA` and
`FULLY_COMPILABLE` (see [computed attributes](16-computed-attributes.md)):

| Key | Format | Example |
|---|---|---|
| Key_F | `{owning_part}.{python_name}` | `Solar_Array.panel_cost` |
| bare | just the python name | `panel_cost` |
| SysML QN | `{owning_part_qn}::{name}` | `SolarBatteryLibrary::Solar_Array::panel_cost` |

### Phase 2 -- CHAIN Aliases (source="redefinition")

For each `ChannelAlias` with `source="redefinition"`, the alias's `canonical_name` is resolved
through the registry (hitting a Key_C from Phase 1), then the alias key is registered pointing
to whatever canonical that resolved to.

```python
resolved = registry.resolve(alias.canonical_name)  # uses Key_C
registry.register_alias(alias.alias_name, resolved)
```

This is why Phase 1 must be complete first: the `canonical_name` on a CHAIN alias is a
dotted path like `solar_battery_plant.solar_array.cost_model.total_cost` that only resolves
if Key_C is already in the index.

### Phase 3 -- EXPOSE_PURE Aliases (source="expose_pure")

For each `ChannelAlias` with `source="expose_pure"`, a scoped key is built from the owning
part's short name + the alias name, then registered:

```python
scoped_key = f"{owning_part_short}.{alias.alias_name}"
resolved = registry.resolve(alias.canonical_name)
registry.register_alias(scoped_key, resolved)
```

### Phase 4 -- Transitive Design Attribute Aliases

For each `DesignAttributeData` whose `default_value` is a dotted path (checked via
`is_transitive_default()` -- contains `.`, not numeric, not `None`):

```python
key = f"{attr.parent_part}.{attr.name}"
resolved = registry.resolve(str(attr.default_value))  # e.g. "cost_model.total_cost"
registry.register_alias(key, resolved)
```

This handles the rare case where a design attribute's default is a reference to a module
output rather than a literal value.

## Concrete Example

Trace the output `lcoe_per_mwh` from a CalcUsage named
`SolarBatteryDesign__solar_battery_plant__lcoe`:

```
CalcUsage.qualified_name = "SolarBatteryDesign__solar_battery_plant__lcoe"
CalcUsage.instance_name  = "lcoe"
output attribute          = "lcoe_per_mwh"
```

**Phase 1a** registers three keys, all pointing to the same canonical:

```
canonical = "SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"

Key_A: "lcoe.lcoe_per_mwh"                             -> canonical
Key_B: "SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"  -> canonical (self)
Key_C: "solar_battery_plant.lcoe.lcoe_per_mwh"         -> canonical
```

**Phase 2**: Suppose a CHAIN redefinition on `Solar_Battery_Plant` redefines
`levelized_cost :>> lcoe.lcoe_per_mwh`. This produces a `ChannelAlias`:

```
ChannelAlias(
    alias_name     = "solar_battery_plant.levelized_cost",
    canonical_name = "solar_battery_plant.lcoe.lcoe_per_mwh",   # matches Key_C
    source         = "redefinition",
)
```

Phase 2 resolves `canonical_name` via the registry (hits Key_C), gets the true canonical,
and registers:

```
"solar_battery_plant.levelized_cost" -> "SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"
```

**Phase 3**: If an EXPOSE_PURE alias existed (e.g., `lcoe_output` on `Solar_Battery_Plant`),
it would register:

```
"Solar_Battery_Plant.lcoe_output" -> canonical
```

**Phase 4**: If a design attribute `SolarBatteryDesign.levelized_cost` had
`default_value="solar_battery_plant.levelized_cost"`, the transitive alias would register:

```
"SolarBatteryDesign.levelized_cost" -> canonical
```

Note this depends on Phase 2 having already registered `solar_battery_plant.levelized_cost`.

## Data Models

| Type | Location | Role |
|---|---|---|
| `OutputRegistry` | `core/output_registry.py` | The registry itself |
| `ChannelAlias` | `core/models.py` | Alias descriptor with `alias_name`, `canonical_name`, `owning_part_qn`, `source` |
| `is_transitive_default()` | `core/output_registry.py` | Phase 4 filter: detects dotted-path default values |

## Construction Site

`build_output_registry()` in `generation/initialization.py` (lines 502-675) is the sole
constructor. It is called at Step 5.5 of [`build_pipeline_context()`](02-orchestration.md),
after calc usages, hierarchy data, [aggregation scoping](13-aggregation-scoping.md),
[computed attributes](16-computed-attributes.md), and [channel aliases](12-virtual-binding-rewrite.md)
are all available. The populated registry is then passed to the
[`DependencyBacktracker`](11-analysis-backtracker.md) (Step 6) and
[`build_computation_graph()`](07-graph-assembly.md) (Step 7) as their shared lookup mechanism.

## Related Documents

- **Upstream**: [02-orchestration](02-orchestration.md) — `build_pipeline_context()` calls `build_output_registry()`
- **Downstream**: [04-input-resolver](04-input-resolver.md) — uses `resolve()` for FORMULA/aggregation resolution
- **Downstream**: [11-analysis-backtracker](11-analysis-backtracker.md) — uses `resolve()` for CalcUsage resolution
- **Sub-processes**: [12-virtual-binding-rewrite](12-virtual-binding-rewrite.md) — produces `ChannelAlias` inputs for Phases 2-3
- **Sub-processes**: [13-aggregation-scoping](13-aggregation-scoping.md) — produces `ScopedAggregationData` for Phase 1b
- **Sub-processes**: [16-computed-attributes](16-computed-attributes.md) — produces `ComputedAttributeData` for Phase 1c
- **Naming**: [15-naming-conventions](15-naming-conventions.md) — PQN, Key_A through Key_F formats
- **Data models**: [09-data-models](09-data-models.md) — full field definitions
