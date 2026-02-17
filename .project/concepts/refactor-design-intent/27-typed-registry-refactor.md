# 27 -- Typed Registry Refactor

## Why This Document Exists

The OutputRegistry is a `dict[str, str]` with ~12 key formats mashed into one
namespace. Resolution is a cascade of `dict.get()` calls against this pile. The
type system enforces nothing: a Key_A string, a canonical channel name, a SysML
QN, and a bare attribute name are all `str`. The Key_A fallback spike
(`.project/research/20260217-060000_key-a-fallback-spike.md`) proved that the
design docs were wrong in multiple places and that 5 key formats have zero
resolution hits across all 6 models. This document defines the typed replacement.

**Spec**: `.project/active/typed-registry-refactor/spec.md`

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| FR-1 | All identifier formats SHALL have distinct types: SysMLQN, EQN, PQN, CanonicalChannel, ScopedKey | Type definitions importable from `core/identifier_types.py`; mypy rejects cross-assignment |
| FR-2 | The single `OutputRegistry._index: dict[str, str]` SHALL be replaced with separate typed registries: Scoped, SysML QN, Alias | `OutputRegistry` exposes 3 typed dicts; no `dict[str, str]` internal state |
| FR-3 | Key_A, Key_D, Key_E full, Key_F, and bare keys SHALL NOT be registered | Registration code removed; grep for Key_A/D/F in registry builder returns zero |
| FR-4 | Resolution SHALL dispatch on `BindingType` to select the correct typed registry | Backtracker branches on `::` presence; `resolve_input()` strategies select registry by type |
| FR-5 | Key construction SHALL happen through typed constructors only — no ad-hoc f-string construction | Grep for f-string key construction outside typed constructors returns zero |
| FR-6 | If a key must exist, it MUST be unique — no "first registration wins" collision policy for scoped and SysML QN registries | Scoped and SysML QN registries raise on duplicate insertion |
| NFR-1 | Zero runtime cost — `NewType` wrappers add no overhead | `NewType` used (not dataclass); benchmark confirms identical perf |
| NFR-2 | `mypy --strict` SHALL pass on all typed registry code | CI gate: `mypy --strict` on modified files |
| NFR-3 | Incremental adoption — refactor MAY be staged as long as each stage is independently correct | Staged implementation plan in IMPLEMENTATION_PLAN.md Phase TRR |

## Typed Identifier Types (FR-1)

| Type | Format | Separator | Example | Constructor invariant |
|------|--------|-----------|---------|---------------------|
| `SysMLQN` | `Package::Element` | `::` | `SolarBatteryLibrary::BatteryPackCostCalc` | Rejects `__`; must contain `::` |
| `EQN` | `Package__Element` | `__` | `SolarBatteryDesign__solar_battery_plant__lcoe` | Rejects `::`; must contain `__` |
| `PQN` | `EQN__param` | `__` | `SBD__sbp__lcoe__lcoe_per_mwh` | Rejects `::`; extends an EQN |
| `CanonicalChannel` | PQN of output | `__` | `SBD__sbp__lcoe__lcoe_per_mwh` | Rejects `::` and `.`; must be a valid PQN |
| `ScopedKey` | dotted hierarchy | `.` | `solar_battery_plant.lcoe.lcoe_per_mwh` | Rejects `::`; uses `.` separator |

All types are `NewType` wrappers over `str` (NFR-1). They add zero runtime cost
but enable mypy to catch format mismatches at type-check time.

### Conversion Boundary

Raw SysML names (`SysMLQN`) are produced at extraction time. All downstream
processing uses typed identifiers:

```
SysMLQN (extraction) → EQN (analysis) → PQN (resolution) → CanonicalChannel (registry value)
                                                           → ScopedKey (registry key)
```

## Constructor Invariants (FR-5)

Each constructor validates format and rejects invalid input:

| Type | `from` method | Validates | Rejects |
|------|--------------|-----------|---------|
| `SysMLQN` | `SysMLQN(qn)` | Contains `::` | Strings with `__` |
| `EQN` | `EQN.from_sysml_qn(sysml_qn)` | Contains `__` after conversion | Strings with `::` |
| `PQN` | `PQN.from_eqn(eqn, param)` | Extends an EQN | Strings with `::` |
| `CanonicalChannel` | `CanonicalChannel.from_eqn(eqn, attr)` | Valid PQN format | Strings with `::` or `.` |
| `ScopedKey` | `ScopedKey.from_eqn(eqn, attr)` | Dotted format, design prefix stripped | Strings with `::` |

**`ScopedKey.from_eqn(usage_eqn, attr_name)`** replaces `OutputRegistry.derive_key_c()`:
split EQN on `__`, drop `segments[0]` (design prefix), join with `.`, append `.{attr}`.

**`CanonicalChannel.from_eqn(usage_eqn, attr_name)`** replaces `get_channel_name()`:
`f"{usage_eqn}__{attr_name}"` wrapped in the `CanonicalChannel` type.

**No ad-hoc f-string construction.** All identifier construction goes through these
constructors. If a new format is needed, a new constructor is added — never an
inline `f"{scope}.{name}"`.

## Typed Registries (FR-2)

The single `OutputRegistry._index: dict[str, str]` is replaced with three typed
dictionaries. The resolver MUST know which registry it is querying.

| Registry | Key type | Value type | Contents | Populated by |
|----------|----------|------------|----------|-------------|
| **Scoped** | `ScopedKey` | `CanonicalChannel` | Key_C (CalcUsage outputs), Key_E_stripped (Aggregation outputs) | Phase 1a, Phase 1b |
| **SysML QN** | `SysMLQN` | `CanonicalChannel` | Phase 1c `::` keys from FORMULA outputs | Phase 1c |
| **Alias** | `ScopedKey` | `CanonicalChannel` | Phase 2 CHAIN aliases, Phase 3 EXPOSE_PURE aliases, Phase 4 transitive aliases | Phases 2-4 |

### API

| Method | Registry | Purpose |
|--------|----------|---------|
| `scoped_lookup(ScopedKey) -> CanonicalChannel \| None` | Scoped | Primary lookup for CHAIN bindings |
| `sysml_qn_lookup(SysMLQN) -> CanonicalChannel \| None` | SysML QN | REFERENCE binding lookup |
| `alias_lookup(ScopedKey) -> CanonicalChannel \| None` | Alias | Cross-package EXPOSE_PURE lookup |
| `register_scoped(ScopedKey, CanonicalChannel)` | Scoped | Phase 1 registration |
| `register_sysml_qn(SysMLQN, CanonicalChannel)` | SysML QN | Phase 1c registration |
| `register_alias(ScopedKey, CanonicalChannel)` | Alias | Phase 2-4 registration (phase enforcement) |

`resolve()` as a single method taking `str` and returning `str | None` is
**PROHIBITED**. Each registry has its own typed lookup method.

Key_B (canonical self-registration) becomes the `_canonical: set[CanonicalChannel]`
membership set. It is not a lookup key — it exists only for phase-ordering enforcement
(`register_alias()` checks target is in `_canonical`).

## Eliminated Keys (FR-3)

The following key formats are NOT registered. Evidence from spike:

| Key | Format | Resolution hits | Reason for elimination |
|-----|--------|----------------|----------------------|
| Key_A | `{instance_name}.{attr}` | **0** across 6 models | Scope-ambiguous; collisions observed in catf_mfe (10+ collisions) |
| Key_D | `{part_usage}.{attr}` | **0** across 6 models | Same ambiguity as Key_A for aggregations |
| Key_E full | `{full_dotted_with_design_prefix}` | **0** across 6 models | Redundant with Key_E_stripped; nothing constructs a lookup with design prefix |
| Key_F | `{owning_part}.{python_name}` | **0** across 6 models | Same ambiguity as Key_A for FORMULAs |
| bare | `{attr_name}` alone | **0** across 6 models | Maximally ambiguous; already flagged REMOVAL_CANDIDATE |

**FR-6 applies**: if any eliminated key turns out to be load-bearing for a model
not currently tested, the key MUST be made unique (not re-added as ambiguous).

## Type-Directed Resolution Dispatch (FR-4)

The backtracker's `_resolve_binding_via_registry()` dispatches on the binding's
`source_path` format to select the correct registry:

### CHAIN Bindings (no `::` in source_path)

```
1. ScopedKey(consumer_scope, source_path) → scoped registry
2. ScopedKey(source_path) → alias registry (cross-package EXPOSE_PURE)
3. Design attribute match → ENTRY_POINT
4. Fallback → ENTRY_POINT
```

Step 1 constructs a `ScopedKey` by prepending the consumer's parent scope to the
source_path. This produces a Key_C-format path that is unique by SysML ownership.
Step 2 tries the alias registry for cross-package references that cannot be
scoped (the consumer and producer are in different packages).

### REFERENCE Bindings (`::` in source_path)

```
1. SysMLQN(source_path) → SysML QN registry
2. Normalized ScopedKey(leaf, parent) → scoped registry
3. Design attribute match → ENTRY_POINT
4. Fallback → ENTRY_POINT
```

Step 1 wraps the `::` source_path as a `SysMLQN` and queries the SysML QN registry
directly. Step 2 extracts the leaf and parent segments for a scoped fallback.

### What This Eliminates

- **Step 1 (unscoped Key_A fallback)**: Deleted entirely. No Key_A keys exist
  in the registry, so there is nothing to guard against.
- **`UnscopedResolutionError`**: Eliminated. The error existed to guard against
  Key_A hits; with Key_A not registered, the guard is moot.
- **"try everything in order" cascade**: Replaced by type-directed dispatch.
  CHAIN and REFERENCE bindings each have their own 2-step typed lookup sequence.

## Uniqueness Guarantee (FR-6)

| Registry | Uniqueness | Collision policy |
|----------|-----------|-----------------|
| Scoped | **Unique by construction.** ScopedKey is derived from the SysML ownership chain (EQN). Two different outputs cannot produce the same ScopedKey. | Raise on duplicate (indicates a bug in key construction). |
| SysML QN | **Unique by construction.** SysML qualified names are globally unique in the SysML model. | Raise on duplicate (indicates a bug in extraction). |
| Alias | **Not guaranteed unique.** Different alias sources (CHAIN, EXPOSE_PURE, transitive) may produce the same ScopedKey. | First-wins with warning (same as current). |

The "first registration wins" collision policy is a symptom of ambiguous keys.
It is eliminated for the scoped and SysML QN registries where uniqueness is
guaranteed. It is retained only for the alias registry where different sources
may legitimately produce the same alias.

## NFR Notes

**NFR-1: Zero runtime cost.** All typed identifiers use `NewType` from `typing`.
`NewType` creates a callable that returns its argument unchanged at runtime — it
is a type-checker-only construct. No `isinstance` checks, no wrapping overhead.

```python
from typing import NewType

ScopedKey = NewType('ScopedKey', str)
CanonicalChannel = NewType('CanonicalChannel', str)
SysMLQN = NewType('SysMLQN', str)
EQN = NewType('EQN', str)
PQN = NewType('PQN', str)
```

**NFR-2: mypy strict mode.** All typed registries and constructors pass
`mypy --strict` without `type: ignore` comments. Cross-assignment (e.g., passing
a `ScopedKey` where a `SysMLQN` is expected) is a type error.

**NFR-3: Incremental adoption.** The refactor may be staged:
1. Define types and constructors (no registry changes yet)
2. Split registry into 3 typed dicts (constructors produce typed keys)
3. Eliminate dead key registrations (Key_A, Key_D, Key_E full, Key_F, bare)
4. Update resolution dispatch (CHAIN/REFERENCE type-directed paths)

Each stage is independently correct and can be validated against the 6 model
snapshots.

## Evidence Base

All claims are supported by the Key_A fallback spike:

| Claim | Evidence |
|-------|---------|
| Zero Key_A hits | Spike: 0/150 backtracker resolutions hit Key_A across 6 models |
| 12 Step 1 hits are EXPOSE_PURE/SysML QN | Spike: 10 catf_mfe EXPOSE_PURE + 2 attr_expr_probe SysML QN |
| Key_A collisions exist | Spike: catf_mfe has 10+ Key_A collisions (pump_load.pump_power, minor_calc.a, etc.) |
| Zero Key_D hits | Spike: 0/46 aggregation term resolutions use Key_D (all scoped) |
| Zero Key_E/Key_F/bare hits | Spike: no code path constructs a lookup that matches these formats |
| REQ-BT-08 would break 12 resolutions | Spike: Step 1 raises on `channel is not None`, catching EXPOSE_PURE and SysML QN |
| REQ-NC-07 factually wrong | Spike: 14 SysML QN keys with `::` registered in attr_expr_probe |

**Source**: `.project/research/20260217-060000_key-a-fallback-spike.md`

## Cross-References

This document amends or is referenced by:

| Doc | What changes |
|-----|-------------|
| [03-resolution-overview](03-resolution-overview.md) | Scope Problem uses typed registries; Key_A refs removed |
| [04-input-resolver](04-input-resolver.md) | Strategies query typed registries; Key_A warning removed |
| [09-data-models](09-data-models.md) | CanonicalChannel, ScopedKey added to type wrappers |
| [10-output-registry](10-output-registry.md) | Typed registries replace flat dict; resolve() → typed lookups |
| [11-analysis-backtracker](11-analysis-backtracker.md) | Type-directed dispatch replaces cascade; Step 1 deleted |
| [15-naming-conventions](15-naming-conventions.md) | REQ-NC-07 corrected; dead keys removed from tables |
| [24-dual-resolution-architecture](24-dual-resolution-architecture.md) | Strategy tables reflect typed registries |

## Related Documents

- **Spec**: `.project/active/typed-registry-refactor/spec.md`
- **Evidence**: `.project/research/20260217-060000_key-a-fallback-spike.md`
- **Data models**: [09-data-models](09-data-models.md) — typed identifier definitions
- **Registry**: [10-output-registry](10-output-registry.md) — typed registry architecture
- **Naming**: [15-naming-conventions](15-naming-conventions.md) — format definitions
- **Backtracker**: [11-analysis-backtracker](11-analysis-backtracker.md) — type-directed dispatch
- **Input resolver**: [04-input-resolver](04-input-resolver.md) — typed strategy chain
- **Revision backlog**: `revision_backlog.md` — supersedes RB-01 (CanonicalName type wrappers)
