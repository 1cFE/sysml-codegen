# 10 - Output Registry

> **Status: historical.** `core/output_registry.py` and the 4-phase registration protocol in
> `orchestration/output_registry_builder.py` were **deleted** by the Item 7 retirement
> (2026-08-12, `19072ad` / `82c7951` / `882fc8d` / `3071fba`). Neither is in the tree.
>
> **The problem it solves does not arise on the shipped route.** The registry exists because
> extraction produced `source_path` strings in several formats that might name the same output.
> The elaborator resolves a reference against the node that declares it, so there is no string
> to disambiguate; projection indexes output channels straight from the instance graph and
> claims each channel name exactly once (`_index_output_channels`, `_claim_channel` in
> `elaboration/project.py`).
>
> Everything below is retained as the record of the deleted design. It is accurate about the
> code that was removed and is **not a description of what the product does**. For that, read
> [00-pipeline-overview](00-pipeline-overview.md).

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
| REQ-OR-02 | Each typed registry SHALL have its own exact-match lookup method — no single `resolve()` method that accepts any string format | `scoped_lookup(ScopedKey)`, `sysml_qn_lookup(SysMLQN)`, `alias_lookup(ScopedKey)`, `scoped_alias_lookup(ScopedAliasKey)` |
| REQ-OR-03 | Collision policy: scoped and SysML QN registries SHALL raise on duplicate (unique by construction); alias registry SHALL refuse overwrites (first wins, warning logged) | `register_scoped()` and `register_sysml_qn()` raise; `register_alias()` warns |
| REQ-OR-04 | `register_alias()` SHALL enforce phase ordering — target must already be in `_canonical` | Guard: `if canonical_channel not in self._canonical: return` |
| REQ-OR-05 | Phase 1 SHALL register: Key_C as `ScopedKey` and Key_A as a guarded first-wins alias (Phase 1a); Key_E_stripped as `ScopedKey` (Phase 1b, Aggregation); SysML QN as `SysMLQN` and Key_F as `ScopedKey` (Phase 1c, FORMULA). The ambiguous formats (Key_A, Key_D, Key_E full, Key_F, bare) SHALL NOT enter the **scoped** registry; Key_A lands only as a guarded alias and Key_F only as the REFERENCE-secondary scoped key. | Key format tables in each sub-phase; see [Key Formats Excluded From the Scoped Registry](#key-formats-excluded-from-the-scoped-registry) |
| REQ-OR-06 | Phase 2-4 aliases SHALL resolve their canonical target through typed **resolution-time** lookup before registering; the construction-time `instance_attr_to_channel` Key_A dict is a build-time helper feeding only guarded `register_alias` calls | `registry.scoped_lookup(ScopedKey(alias.canonical_name))` / `alias_lookup` precedes `register_alias()`; the dict registers nothing itself |
| REQ-OR-07 | Key_C SHALL be constructed via `make_scoped_key()` — strip design prefix from EQN, join with dots | `make_scoped_key()`: split on `__`, drop `segments[0]`, join with `.` |
| REQ-OR-08 | Key_A SHALL NOT be registered as a scoped key — the ambiguous format is kept out of the scoped registry (Key_C is its scoped form). Key_A IS registered as a guarded first-wins alias (Phase 1a `register_alias`), reachable via `alias_lookup` for cross-scope CHAIN resolution | Key_A absent from `_scoped`; present in `_alias` — see [Key Formats Excluded From the Scoped Registry](#key-formats-excluded-from-the-scoped-registry) |
| REQ-OR-09 | The FORMULA sysml-QN key SHALL be registered per-segment sanitized (`sanitize_qualified_name`), and the per-collision alias line SHALL be DEBUG with one WARNING count-summary at build (Item 7 / D5, lockstep site 1) | Phase 1c wraps the key in `sanitize_qualified_name()`; `register_alias()` logs collisions at DEBUG; `build_output_registry()` emits the count-summary |

## What It Is

The `OutputRegistry` (in `core/output_registry.py`) provides **typed, scoped**
lookup from reference keys to **canonical channel names** ([CanonicalChannel](09-data-models.md)).
Four separate typed registries replace the former flat `dict[str, str]` — three
keyed by flat strings, plus a structured tuple-keyed namespace added by Item 10:

| Registry | Key type | Value type | Contents |
|----------|----------|------------|----------|
| **Scoped** | `ScopedKey` | `CanonicalChannel` | Key_C (CalcUsage outputs), Key_E_stripped (Aggregation outputs) |
| **SysML QN** | `SysMLQN` | `CanonicalChannel` | Phase 1c `::` keys from FORMULA outputs |
| **Alias** | `ScopedKey` | `CanonicalChannel` | Phase 2 CHAIN aliases, Phase 3/3b EXPOSE_PURE aliases, Phase 4 transitive aliases |
| **Scoped alias** | `ScopedAliasKey` | `CanonicalChannel` | Part-def (shape A) EXPOSE aliases, expanded per design instance (see Step 5.55 below) |

The scoped-alias namespace keeps its keys as unjoined `(scope, leaf)` tuples so
a tuple key can never collapse into or collide with a flat string key — the
scope carries the full instance path, making the key unique by construction.

**The registry has no concept of scope.** It does not know which module is asking.
Scope-awareness is the [resolver's](04-producer-resolution.md) responsibility. The
resolver [prepends the consumer's scope](03-resolution-overview.md#the-scope-problem)
to produce a `ScopedKey` lookup that is unambiguous. The registry just needs to have
the scoped key registered. The scoped-alias namespace follows the same rule: its
keys carry an instance path as data, but the caller (the
[backtracker's](11-analysis-backtracker.md) chain dispatch) supplies that scope
when it builds the lookup key.

A canonical channel name is the PQN-format string produced by
`make_canonical_channel()` (see [naming conventions](15-naming-conventions.md)):

```
make_canonical_channel("SolarBatteryDesign__solar_battery_plant__lcoe", "lcoe_per_mwh")
→ CanonicalChannel("SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh")
```

The registry's internal state is six fields:
- `_scoped: dict[ScopedKey, CanonicalChannel]` — scoped key lookups
- `_sysml_qn: dict[SysMLQN, CanonicalChannel]` — SysML qualified name lookups
- `_alias: dict[ScopedKey, CanonicalChannel]` — alias lookups
- `_scoped_alias: dict[ScopedAliasKey, CanonicalChannel]` — structured `(scope, leaf)` alias lookups
- `_canonical: set[CanonicalChannel]` — valid canonical channels (phase-ordering enforcement)
- `_alias_collisions: list[ScopedKey]` — first-wins alias collisions, recorded for the one WARNING count-summary the builder emits (per-collision lines are DEBUG)

See Design Rationale below for type system design decisions.

## API

| Method | Phase | Purpose |
|---|---|---|
| `register_scoped(ScopedKey, CanonicalChannel)` | 1a, 1b | Register a scoped key (Key_C, Key_E_stripped) |
| `register_sysml_qn(SysMLQN, CanonicalChannel)` | 1c | Register a SysML QN key |
| `register_alias(ScopedKey, CanonicalChannel)` | 2-4 | Register an alias pointing to an already-registered canonical |
| `register_scoped_alias(ScopedAliasKey, CanonicalChannel)` | Step 5.55 | Register a structured `(scope, leaf)` alias; same phase-ordering guard as `register_alias()` |
| `scoped_lookup(ScopedKey) -> CanonicalChannel \| None` | runtime | Exact-match in scoped registry |
| `sysml_qn_lookup(SysMLQN) -> CanonicalChannel \| None` | runtime | Exact-match in SysML QN registry |
| `alias_lookup(ScopedKey) -> CanonicalChannel \| None` | runtime | Exact-match in alias registry |
| `scoped_alias_lookup(ScopedAliasKey) -> CanonicalChannel \| None` | runtime | Exact-match in scoped-alias registry |
| `scoped_alias_items()` | read | `(ScopedAliasKey, CanonicalChannel)` pairs — the shape-A source for [Item 11 `output_aliases`](09-data-models.md) |
| `make_scoped_key(usage_eqn, attr_name)` | constructor | Builds the dotted hierarchy key (replaces `derive_key_c()`) |
| `make_canonical_channel(usage_eqn, attr_name)` | constructor | Builds the canonical channel name (replaces `get_channel_name()`) |
| `canonical_channels` (property) | read | `frozenset[CanonicalChannel]` of all canonical channel names |
| `alias_collision_count` / `alias_collision_distinct_keys` (properties) | read | Collision totals backing the builder's WARNING count-summary |

**Collision policy**: Scoped, SysML QN, and scoped-alias registries are unique by
construction (ScopedKey derives from the SysML ownership chain; SysML QN is
globally unique in the model; ScopedAliasKey carries the instance path in its
scope element). Duplicate insertion with a different channel raises — this
indicates a bug in key construction. The alias registry retains first-wins,
since different alias sources may legitimately produce the same key. Each
collision is logged at DEBUG and recorded; after all phases run,
`build_output_registry()` emits a single WARNING count-summary
(`"OutputRegistry: N alias collision(s) resolved first-wins (M distinct
key(s))."`) — a collision-free build stays silent (Item 7 / D5, REQ-OR-09).

## The 4-Phase Registration Protocol

Phases must execute in order. `register_alias()` and `register_scoped_alias()`
enforce this: the target canonical channel must already exist in `_canonical`,
or the alias is rejected with a warning. Item 10 added a confirm pass (Phase 3b)
between Phases 3 and 4, and a post-build expansion step (Step 5.55) that
populates the structured scoped-alias namespace; both are described below.

### Phase 1 -- Canonical Channels

Three sub-phases populate the canonical channel set. Each sub-phase corresponds
to one of the three [module types](05-module-factory.md): CalcUsage, Aggregation, FORMULA.

**Phase 1a: CalcUsage outputs** (`build_output_registry`)

For each CalcUsage + each output attribute on its CalcDef, two registrations:

| Registration | Type | Format | Example |
|---|---|---|---|
| Canonical | `CanonicalChannel` | PQN (self-registered in `_canonical` set) | `SBD__sbp__lcoe__lcoe_per_mwh` |
| Scoped key | `ScopedKey` | dotted hierarchy, design prefix stripped | `solar_battery_plant.lcoe.lcoe_per_mwh` |

Scoped key is derived by `make_scoped_key()` (REQ-OR-07): split the usage EQN on `__`,
drop `segments[0]`, join with `.`, append `.{attr}`. This is the most critical key —
it is the [scoped key](03-resolution-overview.md#the-scope-problem) that the
[resolver](04-producer-resolution.md) constructs to disambiguate cross-scope references.
Empirically, ALL Phase 2 CHAIN aliases resolve exclusively via scoped keys.

**Phase 1b: Aggregation outputs** (`build_output_registry`)

For each [`ScopedAggregationData`](09-data-models.md), one registration:

| Registration | Type | Format | Example |
|---|---|---|---|
| Scoped key (Key_E_stripped) | `ScopedKey` | dotted instance path, design prefix stripped | `sbp.solar_array.total_capex` |

Alias names carried on the aggregation expression register additional scoped keys
in the same Key_E_stripped format (BF-7), all pointing at the same canonical channel.

**Phase 1c: FORMULA outputs** (`build_output_registry`)

For each [`ComputedAttributeData`](09-data-models.md) with classification `FORMULA` and
`FULLY_COMPILABLE` (see [computed attributes](16-computed-attributes.md)):

| Registration | Type | Format | Example |
|---|---|---|---|
| SysML QN | `SysMLQN` | `{owning_part_qn}::{name}`, per-segment sanitized | `SolarBatteryLibrary::Solar_Array::panel_cost` |

The key is passed through `sanitize_qualified_name()` (`core/qualified_names.py`)
before registration, so a quoted-owner QN registers in its sanitized form and
matches the REFERENCE consumer, which sanitizes its lookup key the same way
(REQ-OR-09, Item 7 lockstep site 1).

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

The owning part's short name comes from `owning_part_leaf()`
(`core/qualified_names.py`), which accepts either `::` or `__` separators.

### Phase 3b -- Confirm Multi-Hop EXPOSE Tentatives

**Phase 3b is a registry-build phase** — it runs inside `build_output_registry()`
(`orchestration/output_registry_builder.py`), after Phase 3 and before Phase 4.
It is NOT a [backtracker](11-analysis-backtracker.md) phase.

A derived attribute that is a pure multi-hop FeatureChainExpression (e.g.
`radial_build.magnet_volume_total = tf_coil.volume_calc.volume`) is classified
`EXPOSE_CHAIN_TENTATIVE` at extraction (see
[computed attributes](16-computed-attributes.md), REQ-CA-10): the extraction leaf
can see the chain is structurally pure but cannot decide whether it reaches a real
output channel. Phase 3b decides. With Phase 1 channels and Phase 2/3 aliases
registered, it walks each tentative's `reference_chain`
(`_resolve_reference_chain` in the same file):

- Prefix the owning part's short name and try `scoped_lookup` on the full dotted
  chain — the direct calc-output terminal.
- On a miss, if the terminal segment names an attribute that is itself an EXPOSE
  alias, substitute that attribute's own `reference_chain` and recurse (with a
  visited-set cycle guard). Resolution always lands on a **scoped** calc-output
  channel, never the flat alias registry (whose same-named-sibling entries are
  first-wins).

Each tentative then takes exactly one of two exits:

- **Resolved** → the transitive channel is registered as an alias
  (`{owning_part_short}.{python_name}` → channel) and the computed attribute is
  finalized to `EXPOSE_PURE` in place.
- **Unresolvable** → the computed attribute reverts to `FORMULA` in place
  (the pre-Item-10 behavior).

After the pass, **INV-F** is enforced: if any `EXPOSE_CHAIN_TENTATIVE`
classification survives, `build_output_registry()` raises `ValueError` rather
than let a tentative leak to a downstream reader. When the pass processed any
tentatives, one INFO line reports the confirmed/reverted counts.

**Offline parity**: snapshots serialize the post-confirm `EXPOSE_PURE` state, so
a re-tag pre-pass at the top of `build_output_registry()` reconstructs the
tentative state for multi-hop candidates (an `EXPOSE_PURE` computed attribute
whose `reference_chain` is part-rooted with 2+ segments) before Phase 1 runs.
Snapshot rebuilds therefore run the same confirm walk as live extraction; on the
live path the pre-pass is a no-op because those attributes are still tentative.

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

### After the Phases -- Part-Def EXPOSE Scoped Aliases (Step 5.55)

The structured `_scoped_alias` namespace is populated after `build_output_registry()`
returns, by `_register_partdef_expose_scoped_aliases()`
(`orchestration/pipeline_builder.py`), on BOTH build paths (live, and snapshot
rebuild in `snapshot/graph_rebuild.py`).

A derived attribute like `total_cost = cost_calc.cost` on a part **definition**
(shape A) is a template — the part def has no instances at extraction time. Step
5.55 expands it per design instance (REQ-CA-03 revised): for each `EXPOSE_PURE`
computed attribute with `is_on_part_definition` and a 2+ segment
`reference_chain`, every instance path of the owning part def (via
`find_instance_paths_for_partdef()`) gets one registration:

```python
channel = registry.scoped_lookup(ScopedKey(f"{inst}.{rel}"))  # rel = joined reference_chain
registry.register_scoped_alias(ScopedAliasKey((inst, ca.python_name)), channel)
```

The consumer-side reader is the backtracker's `_resolve_chain_dispatch()`
(`analysis/dependency_backtracker.py`): it splits the consumer's `source_path` at
the last dot into `(prefix, leaf)`, then tries the consumer-scope-prepended key
`(consumer_scope.prefix, leaf)` before the bare `(prefix, leaf)` — the
consumer-scope prepend is what disambiguates same-named siblings (REQ-BT-11).
Part *usage* exposes (shape B) are untouched by this step.

The same namespace also backs the self-named-binding rescue
(`_rescue_self_named_bindings()`, Step 5.56): an `in x = x` binding is rewritten
to the instance-scoped attribute path only when a scoped alias proves an outer
EXPOSE channel exists; otherwise it is left as-is (a genuine modeling error).

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
canonical = make_canonical_channel(
    "SolarBatteryDesign__solar_battery_plant__lcoe", "lcoe_per_mwh"
)  # → CanonicalChannel("SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh")

scoped_key = make_scoped_key(
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
| `OutputRegistry` | `core/output_registry.py` | The registry itself (4 typed dicts + canonical set + collision record) |
| `ScopedKey` | `core/identifier_types.py` | Typed wrapper for dotted hierarchy keys |
| `ScopedAliasKey` | `core/identifier_types.py` | `NewType` over `tuple[str, str]` — structured `(scope, leaf)` alias key |
| `CanonicalChannel` | `core/identifier_types.py` | Typed wrapper for PQN-format channel names |
| `SysMLQN` | `core/identifier_types.py` | Typed wrapper for SysML qualified names |
| `ChannelAlias` | `core/models.py` | Alias descriptor with `alias_name: ScopedKey`, `canonical_name: CanonicalChannel`, `owning_part_qn`, `source` |
| `is_transitive_default()` | `core/output_registry.py` | Phase 4 filter: detects dotted-path default values |

## Construction Site

`build_output_registry()` in `orchestration/output_registry_builder.py` is the sole
constructor. On the live path it is called at Step 5.5 of
[`build_pipeline_context()`](02-orchestration.md),
after calc usages, hierarchy data, [aggregation scoping](13-aggregation-scoping.md),
[computed attributes](16-computed-attributes.md), and [channel aliases](12-virtual-binding-rewrite.md)
are all available; the snapshot path (`snapshot/graph_rebuild.py`) calls the same
function from serialized data. Both paths then run the Step 5.55 part-def EXPOSE
scoped-alias expansion and the Step 5.56 self-named-binding rescue (see above)
before the populated registry is passed to the
[`DependencyBacktracker`](11-analysis-backtracker.md) (Step 6) and
[`build_computation_graph()`](07-graph-assembly.md) (Step 7) as their shared lookup mechanism.

## Design Rationale

### Conversion Boundary

Raw SysML names (`SysMLQN`) are produced at extraction time. All downstream
processing uses typed identifiers:

```
SysMLQN (extraction) → EQN (analysis) → PQN (resolution) → CanonicalChannel (registry value)
                                                           → ScopedKey (registry key)
```

### Key Formats Excluded From the Scoped Registry

The following ambiguous formats have zero resolution hits across all 6 model
snapshots and are **never registered as scoped keys** — the scoped registry holds
only Key_C and Key_E_stripped. Two of them do have a narrow non-scoped
registration, called out in the last column:

| Key | Format | Scoped-registry status | Where else it lands |
|-----|--------|------------------------|---------------------|
| Key_A | `{instance_name}.{attr}` | never scoped (scope-ambiguous; catf_mfe has 10+ collisions) | Phase 1a registers it as a guarded first-wins **alias** (`register_alias`) for cross-scope CHAIN resolution |
| Key_D | `{part_usage}.{attr}` | never registered | — (same ambiguity as Key_A for aggregations) |
| Key_E full | `{full_dotted_with_design_prefix}` | never registered | — (redundant with Key_E_stripped; nothing constructs a design-prefixed lookup) |
| Key_F | `{owning_part}.{python_name}` | Phase 1c registers it as a **scoped** key for REFERENCE-secondary resolution (spike Q5) | scoped registry |
| bare | `{attr_name}` alone | never registered | — (maximally ambiguous; flagged REMOVAL_CANDIDATE) |

**FR-6 applies**: if an excluded ambiguous key turns out to be load-bearing for a
model not currently tested, it MUST be made unique (not re-added as ambiguous).

**Build-time helper (not a registration).** Phases 3–4 consult a construction-time
Key_A-format dict (`instance_attr_to_channel`) to *resolve* a Key_A name to its
canonical channel, then register that channel through the guarded `register_alias`
(which warns+skips when the target is not yet in `_canonical`). The dict feeds only
those guarded calls; it registers nothing itself and is discarded after
construction. `register_alias`'s phase-order guard (REQ-OR-04) means an alias whose
canonical target is not yet registered is dropped, so a phase-order regression
loses aliases rather than registering bad ones — pinned by
`test_orchestrator.py::TestRegistryPhaseOrdering::test_expected_key_a_aliases_present_solar_battery`
(Item 7, F2). This section describes actual HEAD behavior; the earlier
"eliminated entirely" reading was the F2 divergence, reconciled by Item 7.

### Evidence Base

All claims are supported by empirical analysis across the 6 model snapshots:

| Claim | Evidence |
|-------|---------|
| Zero Key_A hits | 0/150 backtracker resolutions hit Key_A across 6 models |
| 12 Step 1 hits are EXPOSE_PURE/SysML QN | 10 catf_mfe EXPOSE_PURE + 2 attr_expr_probe SysML QN |
| Key_A collisions exist | catf_mfe has 10+ Key_A collisions (pump_load.pump_power, minor_calc.a, etc.) |
| Zero Key_D hits | 0/46 aggregation term resolutions use Key_D (all scoped) |
| Zero Key_E/Key_F/bare hits | No code path constructs a lookup that matches these formats |
| REQ-BT-08 would break 12 resolutions | Step 1 raises on `channel is not None`, catching EXPOSE_PURE and SysML QN |
| REQ-NC-07 factually wrong | 14 SysML QN keys with `::` registered in attr_expr_probe |

### NewType Zero-Cost Design

All typed identifiers use `NewType` from `typing`, which creates a callable that
returns its argument unchanged at runtime -- zero overhead. No `isinstance` checks,
no wrapping cost. This is a type-checker-only construct (NFR-1).

```python
from typing import NewType

ScopedKey = NewType('ScopedKey', str)
CanonicalChannel = NewType('CanonicalChannel', str)
SysMLQN = NewType('SysMLQN', str)
EQN = NewType('EQN', str)
PQN = NewType('PQN', str)
ScopedAliasKey = NewType('ScopedAliasKey', tuple[str, str])
```

`ScopedAliasKey` is the one non-string wrapper: an unjoined `(scope, leaf)` tuple,
so `("a.b", "c")` and `("a", "b.c")` can never collapse into the same key (the
leaf is always a single segment, so the second form cannot even arise).

See the type wrapper definitions in `core/identifier_types.py` for constructor
invariants and resolution dispatch design.

## Related Documents

- **Upstream**: [02-orchestration](02-orchestration.md) — `build_pipeline_context()` calls `build_output_registry()`
- **Downstream**: [04-producer-resolution](04-producer-resolution.md) — uses typed lookups for FORMULA/aggregation resolution
- **Downstream**: [11-analysis-backtracker](11-analysis-backtracker.md) — uses typed lookups for CalcUsage resolution
- **Sub-processes**: [12-virtual-binding-rewrite](12-virtual-binding-rewrite.md) — produces `ChannelAlias` inputs for Phases 2-3
- **Sub-processes**: [13-aggregation-scoping](13-aggregation-scoping.md) — produces `ScopedAggregationData` for Phase 1b
- **Sub-processes**: [16-computed-attributes](16-computed-attributes.md) — produces `ComputedAttributeData` for Phase 1c
- **Naming**: [15-naming-conventions](15-naming-conventions.md) — PQN, ScopedKey, CanonicalChannel formats
- **Data models**: [09-data-models](09-data-models.md) — full field definitions
