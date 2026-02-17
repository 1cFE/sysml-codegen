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
| REQ-OR-01 | Registry SHALL map every reference format (FCE dotted path, FRE qualified name, redefinition target) to a canonical [CanonicalChannel](09-data-models.md) | All Phase 1 key formats present in typed registries |
| REQ-OR-02 | Each typed registry SHALL have its own exact-match lookup method — no single `resolve()` method that accepts any string format | `scoped_lookup(ScopedKey)`, `sysml_qn_lookup(SysMLQN)`, `alias_lookup(ScopedKey)` |
| REQ-OR-03 | Collision policy: scoped and SysML QN registries SHALL raise on duplicate (unique by construction); alias registry SHALL refuse overwrites (first wins, warning logged) | `register_scoped()` and `register_sysml_qn()` raise; `register_alias()` warns |
| REQ-OR-04 | `register_alias()` SHALL enforce phase ordering — target must already be in `_canonical` | Guard: `if canonical_channel not in self._canonical: return` |
| REQ-OR-05 | Phase 1 SHALL register only non-ambiguous keys: Key_C as `ScopedKey` (CalcUsage), Key_E_stripped as `ScopedKey` (Aggregation), SysML QN as `SysMLQN` (FORMULA). Key_A, Key_D, Key_E full, Key_F, and bare keys SHALL NOT be registered. | Key format tables in each sub-phase; see [27-typed-registry-refactor](27-typed-registry-refactor.md) for elimination rationale |
| REQ-OR-06 | Phase 2-4 aliases SHALL resolve through typed lookup before registering | `registry.scoped_lookup(ScopedKey(alias.canonical_name))` precedes `register_alias()` |
| REQ-OR-07 | Key_C SHALL be constructed via `ScopedKey.from_eqn()` — strip design prefix from EQN, join with dots | `ScopedKey.from_eqn()`: split on `__`, drop `segments[0]`, join with `.` |
| REQ-OR-08 | Key_A SHALL NOT be registered. The ambiguous key format is eliminated entirely — no registration, no guard, no diagnostic-only entry. | Key_A registration code removed; see [27-typed-registry-refactor](27-typed-registry-refactor.md) FR-3 |

## What It Is

The `OutputRegistry` (in `core/output_registry.py`) provides **typed, scoped**
lookup from reference keys to **canonical channel names** ([CanonicalChannel](09-data-models.md)).
Three separate typed registries replace the former flat `dict[str, str]`:

| Registry | Key type | Value type | Contents |
|----------|----------|------------|----------|
| **Scoped** | `ScopedKey` | `CanonicalChannel` | Key_C (CalcUsage outputs), Key_E_stripped (Aggregation outputs) |
| **SysML QN** | `SysMLQN` | `CanonicalChannel` | Phase 1c `::` keys from FORMULA outputs |
| **Alias** | `ScopedKey` | `CanonicalChannel` | Phase 2 CHAIN aliases, Phase 3 EXPOSE_PURE aliases, Phase 4 transitive aliases |

**The registry has no concept of scope.** It does not know which module is asking.
Scope-awareness is the [resolver's](04-input-resolver.md) responsibility. The
resolver [prepends the consumer's scope](03-resolution-overview.md#the-scope-problem)
to produce a `ScopedKey` lookup that is unambiguous. The registry just needs to have
the scoped key registered.

A canonical channel name is the PQN-format string produced by
`CanonicalChannel.from_eqn()` (see [naming conventions](15-naming-conventions.md)):

```
CanonicalChannel.from_eqn("SolarBatteryDesign__solar_battery_plant__lcoe", "lcoe_per_mwh")
→ CanonicalChannel("SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh")
```

The registry's internal state is four fields:
- `_scoped: dict[ScopedKey, CanonicalChannel]` — scoped key lookups
- `_sysml_qn: dict[SysMLQN, CanonicalChannel]` — SysML qualified name lookups
- `_alias: dict[ScopedKey, CanonicalChannel]` — alias lookups
- `_canonical: set[CanonicalChannel]` — valid canonical channels (phase-ordering enforcement)

See [27-typed-registry-refactor](27-typed-registry-refactor.md) for the full type system.

## API

| Method | Phase | Purpose |
|---|---|---|
| `register_scoped(ScopedKey, CanonicalChannel)` | 1a, 1b | Register a scoped key (Key_C, Key_E_stripped) |
| `register_sysml_qn(SysMLQN, CanonicalChannel)` | 1c | Register a SysML QN key |
| `register_alias(ScopedKey, CanonicalChannel)` | 2-4 | Register an alias pointing to an already-registered canonical |
| `scoped_lookup(ScopedKey) -> CanonicalChannel \| None` | runtime | Exact-match in scoped registry |
| `sysml_qn_lookup(SysMLQN) -> CanonicalChannel \| None` | runtime | Exact-match in SysML QN registry |
| `alias_lookup(ScopedKey) -> CanonicalChannel \| None` | runtime | Exact-match in alias registry |
| `ScopedKey.from_eqn(usage_eqn, attr_name)` | constructor | Builds the dotted hierarchy key (replaces `derive_key_c()`) |
| `CanonicalChannel.from_eqn(usage_eqn, attr_name)` | constructor | Builds the canonical channel name (replaces `get_channel_name()`) |
| `canonical_channels` (property) | read | `frozenset[CanonicalChannel]` of all canonical channel names |

**Collision policy**: Scoped and SysML QN registries are unique by construction
(ScopedKey derives from the SysML ownership chain; SysML QN is globally unique in
the model). Duplicate insertion raises — this indicates a bug in key construction.
Alias registry retains first-wins with warning, since different alias sources may
legitimately produce the same key.

## The 4-Phase Registration Protocol

Phases must execute in order. `register_alias()` enforces this: the target canonical channel
must already exist in `_canonical`, or the alias is rejected with a warning.

### Phase 1 -- Canonical Channels

Three sub-phases populate the canonical channel set. Each sub-phase corresponds
to one of the three [module types](05-module-factory.md): CalcUsage, Aggregation, FORMULA.

**Phase 1a: CalcUsage outputs** (`build_output_registry`)

For each CalcUsage + each output attribute on its CalcDef, two registrations:

| Registration | Type | Format | Example |
|---|---|---|---|
| Canonical | `CanonicalChannel` | PQN (self-registered in `_canonical` set) | `SBD__sbp__lcoe__lcoe_per_mwh` |
| Scoped key | `ScopedKey` | dotted hierarchy, design prefix stripped | `solar_battery_plant.lcoe.lcoe_per_mwh` |

Scoped key is derived by `ScopedKey.from_eqn()` (REQ-OR-07): split the usage EQN on `__`,
drop `segments[0]`, join with `.`, append `.{attr}`. This is the most critical key —
it is the [scoped key](03-resolution-overview.md#the-scope-problem) that the
[resolver](04-input-resolver.md) constructs to disambiguate cross-scope references.
Empirically, ALL Phase 2 CHAIN aliases resolve exclusively via scoped keys.

**Phase 1b: Aggregation outputs** (`build_output_registry`)

For each [`ScopedAggregationData`](09-data-models.md), one registration:

| Registration | Type | Format | Example |
|---|---|---|---|
| Scoped key (Key_E_stripped) | `ScopedKey` | dotted instance path, design prefix stripped | `sbp.solar_array.total_capex` |

**Phase 1c: FORMULA outputs** (`build_output_registry`)

For each [`ComputedAttributeData`](09-data-models.md) with classification `FORMULA` and
`FULLY_COMPILABLE` (see [computed attributes](16-computed-attributes.md)):

| Registration | Type | Format | Example |
|---|---|---|---|
| SysML QN | `SysMLQN` | `{owning_part_qn}::{name}` | `SolarBatteryLibrary::Solar_Array::panel_cost` |

### Phase 2 -- CHAIN Aliases (source="redefinition")

For each `ChannelAlias` with `source="redefinition"`, the alias's `canonical_name` is resolved
through the scoped registry (hitting a scoped key from Phase 1), then the alias key is
registered in the alias registry:

```python
resolved = registry.scoped_lookup(ScopedKey(alias.canonical_name))  # uses scoped key
registry.register_alias(ScopedKey(alias.alias_name), resolved)
```

This is why Phase 1 must be complete first: the `canonical_name` on a CHAIN alias is a
dotted path like `solar_battery_plant.solar_array.cost_model.total_cost` that only resolves
if the scoped key is already registered.

### Phase 3 -- EXPOSE_PURE Aliases (source="expose_pure")

For each `ChannelAlias` with `source="expose_pure"`, a scoped key is built from the owning
part's short name + the alias name, then registered in the alias registry:

```python
scoped_key = ScopedKey(f"{owning_part_short}.{alias.alias_name}")
resolved = registry.scoped_lookup(ScopedKey(alias.canonical_name))
registry.register_alias(scoped_key, resolved)
```

### Phase 4 -- Transitive Design Attribute Aliases

For each `DesignAttributeData` whose `default_value` is a dotted path (checked via
`is_transitive_default()` -- contains `.`, not numeric, not `None`):

```python
key = ScopedKey(f"{attr.parent_part}.{attr.name}")
resolved = registry.scoped_lookup(ScopedKey(str(attr.default_value)))
if resolved is None:
    resolved = registry.alias_lookup(ScopedKey(str(attr.default_value)))
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

**Phase 1a** registers using typed constructors:

```python
canonical = CanonicalChannel.from_eqn(
    "SolarBatteryDesign__solar_battery_plant__lcoe", "lcoe_per_mwh"
)  # → CanonicalChannel("SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh")

scoped_key = ScopedKey.from_eqn(
    "SolarBatteryDesign__solar_battery_plant__lcoe", "lcoe_per_mwh"
)  # → ScopedKey("solar_battery_plant.lcoe.lcoe_per_mwh")

registry.register_scoped(scoped_key, canonical)
# _canonical set also gets: canonical
```

**Phase 2**: Suppose a CHAIN redefinition on `Solar_Battery_Plant` redefines
`levelized_cost :>> lcoe.lcoe_per_mwh`. This produces a `ChannelAlias`:

```python
ChannelAlias(
    alias_name     = ScopedKey("solar_battery_plant.levelized_cost"),
    canonical_name = CanonicalChannel("SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"),
    source         = "redefinition",
)
```

Phase 2 resolves `canonical_name` via the scoped registry and registers in alias:

```python
registry.register_alias(
    ScopedKey("solar_battery_plant.levelized_cost"),
    canonical  # already known from Phase 1a
)
```

**Phase 3**: If an EXPOSE_PURE alias existed (e.g., `lcoe_output` on `Solar_Battery_Plant`),
it would register in the alias registry:

```python
registry.register_alias(
    ScopedKey("Solar_Battery_Plant.lcoe_output"),
    canonical
)
```

**Phase 4**: If a design attribute `SolarBatteryDesign.levelized_cost` had
`default_value="solar_battery_plant.levelized_cost"`, the transitive alias would register
in the alias registry:

```python
registry.register_alias(
    ScopedKey("SolarBatteryDesign.levelized_cost"),
    canonical
)
```

Note this depends on Phase 2 having already registered `solar_battery_plant.levelized_cost`.

## Data Models

| Type | Location | Role |
|---|---|---|
| `OutputRegistry` | `core/output_registry.py` | The registry itself (3 typed dicts + canonical set) |
| `ScopedKey` | `core/identifier_types.py` | Typed wrapper for dotted hierarchy keys |
| `CanonicalChannel` | `core/identifier_types.py` | Typed wrapper for PQN-format channel names |
| `SysMLQN` | `core/identifier_types.py` | Typed wrapper for SysML qualified names |
| `ChannelAlias` | `core/models.py` | Alias descriptor with `alias_name: ScopedKey`, `canonical_name: CanonicalChannel`, `owning_part_qn`, `source` |
| `is_transitive_default()` | `core/output_registry.py` | Phase 4 filter: detects dotted-path default values |

## Construction Site

`build_output_registry()` in `generation/initialization.py` is the sole
constructor. It is called at Step 5.5 of [`build_pipeline_context()`](02-orchestration.md),
after calc usages, hierarchy data, [aggregation scoping](13-aggregation-scoping.md),
[computed attributes](16-computed-attributes.md), and [channel aliases](12-virtual-binding-rewrite.md)
are all available. The populated registry is then passed to the
[`DependencyBacktracker`](11-analysis-backtracker.md) (Step 6) and
[`build_computation_graph()`](07-graph-assembly.md) (Step 7) as their shared lookup mechanism.

## Related Documents

- **Upstream**: [02-orchestration](02-orchestration.md) — `build_pipeline_context()` calls `build_output_registry()`
- **Downstream**: [04-input-resolver](04-input-resolver.md) — uses typed lookups for FORMULA/aggregation resolution
- **Downstream**: [11-analysis-backtracker](11-analysis-backtracker.md) — uses typed lookups for CalcUsage resolution
- **Sub-processes**: [12-virtual-binding-rewrite](12-virtual-binding-rewrite.md) — produces `ChannelAlias` inputs for Phases 2-3
- **Sub-processes**: [13-aggregation-scoping](13-aggregation-scoping.md) — produces `ScopedAggregationData` for Phase 1b
- **Sub-processes**: [16-computed-attributes](16-computed-attributes.md) — produces `ComputedAttributeData` for Phase 1c
- **Naming**: [15-naming-conventions](15-naming-conventions.md) — PQN, ScopedKey, CanonicalChannel formats
- **Type system**: [27-typed-registry-refactor](27-typed-registry-refactor.md) — full type system and registry architecture
- **Data models**: [09-data-models](09-data-models.md) — full field definitions
