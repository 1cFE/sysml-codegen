# Spec 02: OutputRegistry Class

**Epic**: OUTPUT-REGISTRY (Item 1)
**Target file**: `src/sysml_codegen/core/output_registry.py` (new file)
**Status**: Draft
**Created**: 2026-02-13

---

## 1. Overview

The `OutputRegistry` is a single lookup data structure that maps dotted binding source_paths to canonical pipeline channel names (PQN format). It replaces the backtracker's 5 ad-hoc indexes (`_computed_attr_index`, `_aggregation_output_index`, `_output_catalog`, `_design_attr_binding_index`, `_usage_by_name`) and 7-strategy cascade with one exact-match dictionary lookup.

### Design Principles

1. **Exact match only**: `resolve()` is a pure `dict.get()` call. No normalization, no bare-name extraction, no SysML QN handling, no cascade.
2. **Register once, refuse collisions**: If a key is already mapped to a different channel, log a WARNING and keep the first registration.
3. **Aliases are just keys**: `register_alias()` maps an alias key to an existing canonical channel. Internally, aliases and primary keys are stored in the same `_index` dict.
4. **Phase-ordered construction**: The registry is built in 4 phases with ordered dependencies. Each phase may resolve against keys registered by prior phases.

### Traceability

| Spike | Finding | How it informs this spec |
|-------|---------|--------------------------|
| Spike 1 | SysIDE always produces SYSML_QN for REFERENCE, DOTTED for CHAIN. Zero bare names. | No bare-name registration. No SYSML_QN normalization in resolve(). |
| Spike 4 | Zero bare-name references across 94 bindings, 4 models. K=5 ambiguous bare names per model. | Skip bare-name registration entirely. |
| Spike 5 | 4 REFERENCE->MODULE_OUTPUT cases. Naive `::` -> `__` normalization fails in all 4. | Remove SYSML_QN normalization from resolve(). Handle via secondary resolution in backtracker. |
| Spike 6 | 41 DOTTED CHAIN redefs, 13 BARE CAS codes. All DOTTED follow `cost_model.{output}` pattern. | CHAIN alias construction uses dotted source_path. Filter BARE non-references. |
| Spike 7 | 2 transitive defaults, both clean DOTTED_PATH, both resolve via direct catalog lookup. | Phase 4 transitive alias works with `_is_transitive_default()` filter. |
| Spike 8 | 77 channels, 217 keys in solar_battery. 15 channels, 33 keys in e2e_attr_expr. Zero collisions. | Key format contract validated. Collision policy is defensive, not expected to fire. |

---

## 2. Class Interface

### 2.1 Location

New file: `src/sysml_codegen/core/output_registry.py`

### 2.2 Full Interface

```python
"""OutputRegistry: single lookup for binding source_path -> canonical channel.

Replaces the backtracker's 5 ad-hoc indexes and 7-strategy cascade with
one exact-match dictionary. Built in 4 phases with ordered dependencies.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class OutputRegistry:
    """Maps dotted binding source_paths to canonical pipeline channel names.

    The registry is a flat dictionary mapping string keys to canonical channel
    names (PQN format: ``{EQN}__{output_attr_name}``). Multiple keys can map
    to the same canonical channel. Keys come from 6 format families (Key_A
    through Key_F) plus aliases from CHAIN redefinitions and EXPOSE_PURE
    classifications.

    Usage::

        registry = OutputRegistry()

        # Phase 1: register CalcUsage outputs
        registry.register(
            canonical_channel="Design__plant__lcoe__lcoe_per_mwh",
            lookup_keys=[
                "lcoe.lcoe_per_mwh",           # Key_A
                "Design__plant__lcoe__lcoe_per_mwh",  # Key_B
                "plant.lcoe.lcoe_per_mwh",      # Key_C
            ],
        )

        # Phase 2: register CHAIN alias
        registry.register_alias(
            alias="solar_array.total_capex",
            canonical_channel="Design__plant__solar_array__cost_model__total_cost",
        )

        # Resolve
        channel = registry.resolve("lcoe.lcoe_per_mwh")
        # => "Design__plant__lcoe__lcoe_per_mwh"
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        ...

    def register(self, canonical_channel: str, lookup_keys: list[str]) -> None:
        """Register a canonical channel with one or more lookup keys.

        Each key in ``lookup_keys`` is mapped to ``canonical_channel`` in the
        internal index. If a key is already mapped to a DIFFERENT channel,
        a WARNING is logged and the existing mapping is preserved (refuse
        overwrite). If a key is already mapped to the SAME channel, the
        duplicate registration is silently accepted.

        The ``canonical_channel`` is added to the canonical set.

        Args:
            canonical_channel: The PQN-format channel name (e.g.,
                ``"Design__plant__lcoe__lcoe_per_mwh"``).
            lookup_keys: List of string keys to register. May include
                Key_A, Key_B, Key_C, Key_D, Key_E, or Key_F formats.

        Raises:
            No exceptions. Collisions are logged as warnings, not errors.
        """
        ...

    def register_alias(self, alias: str, canonical_channel: str) -> None:
        """Register an alias key that maps to an existing canonical channel.

        The alias key is added to the internal index pointing to
        ``canonical_channel``. This method asserts that ``canonical_channel``
        is already in the canonical set (i.e., was previously registered
        via ``register()``).

        Collision policy is the same as ``register()``: if the alias key
        is already mapped to a different channel, log WARNING and refuse
        overwrite.

        Args:
            alias: The alias key (e.g., ``"solar_array.total_capex"``).
            canonical_channel: The PQN-format channel name that this alias
                maps to. Must already be registered.

        Raises:
            AssertionError: If ``canonical_channel`` is not in the canonical
                set (i.e., was never registered via ``register()``).
        """
        ...

    def resolve(self, source_path: str) -> str | None:
        """Resolve a binding source_path to a canonical channel name.

        This is a pure dictionary lookup: ``self._index.get(source_path)``.
        No normalization. No bare-name extraction. No SysML QN handling.
        No cascade. No fallback.

        Args:
            source_path: The binding source_path to look up. Expected to
                be in dotted format (CHAIN bindings) or a previously
                registered alias key.

        Returns:
            The canonical channel name (PQN format) if found, or ``None``
            if the key is not registered.
        """
        ...

    def __len__(self) -> int:
        """Return the number of registered lookup keys (not channels)."""
        ...

    def __contains__(self, key: str) -> bool:
        """Check if a key is registered in the index."""
        ...

    def channels(self) -> frozenset[str]:
        """Return the set of all registered canonical channel names."""
        ...

    def keys(self) -> frozenset[str]:
        """Return the set of all registered lookup keys."""
        ...
```

---

## 3. Internal State

### 3.1 Data Structures

```python
class OutputRegistry:
    def __init__(self) -> None:
        self._index: dict[str, str] = {}
        # Maps lookup key -> canonical channel name.
        # All keys (primary and alias) live in this single dict.

        self._canonical: set[str] = set()
        # Set of canonical channel names that have been registered
        # via register(). Used by register_alias() to assert the
        # target channel exists.
```

### 3.2 Why a Single Flat Dict?

The prior design used 5 separate indexes with different key formats, requiring a cascade of lookups across all indexes. The OutputRegistry unifies all keys into one dict because:

1. **All keys are strings**: No type-based dispatch needed.
2. **All keys are unique** (Spike 8: zero collisions across 250 keys): No conflict resolution needed beyond defensive collision logging.
3. **Lookup is always exact match**: No prefix matching, no normalization, no cascade.
4. **Phase ordering is construction-time only**: Once built, the registry is immutable in practice (no keys are removed or updated during backtracking).

---

## 4. Method Specifications

### 4.1 `register(canonical_channel, lookup_keys)`

**Behavior**:

```python
def register(self, canonical_channel: str, lookup_keys: list[str]) -> None:
    self._canonical.add(canonical_channel)
    # Self-referential: canonical name resolves to itself
    self._index[canonical_channel] = canonical_channel
    for key in lookup_keys:
        if key in self._index:
            if self._index[key] != canonical_channel:
                logger.warning(
                    "OutputRegistry collision: key %r already maps to %r, "
                    "refusing to overwrite with %r",
                    key, self._index[key], canonical_channel,
                )
            # Same channel: silently accept duplicate
            continue
        self._index[key] = canonical_channel
```

**Invariants**:
- After `register(ch, keys)`, `ch in self._canonical` is True.
- After `register(ch, keys)`, for each key `k` in `keys` where `k` was not previously registered: `self._index[k] == ch`.
- After `register(ch, keys)`, for each key `k` in `keys` where `k` WAS previously registered to a DIFFERENT channel: `self._index[k]` retains its original value (first-wins).

**Edge cases**:
- Empty `lookup_keys` list: The canonical channel is added to `_canonical` but no keys are indexed. This is valid (the channel exists but has no lookup keys yet; aliases may be added later via `register_alias()`).
- Duplicate key mapping to same channel: Silently accepted (idempotent).
- `canonical_channel` registered multiple times with different key lists: All keys are accumulated. The channel appears once in `_canonical`.

### 4.2 `register_alias(alias, canonical_channel)`

**Behavior**:

```python
def register_alias(self, alias: str, canonical_channel: str) -> None:
    assert canonical_channel in self._canonical, (
        f"Cannot register alias {alias!r}: canonical channel "
        f"{canonical_channel!r} is not registered"
    )
    if alias in self._index:
        if self._index[alias] != canonical_channel:
            logger.warning(
                "OutputRegistry alias collision: key %r already maps to %r, "
                "refusing to overwrite with %r",
                alias, self._index[alias], canonical_channel,
            )
        return
    self._index[alias] = canonical_channel
```

**Invariants**:
- `canonical_channel` MUST be in `_canonical` (asserted).
- After `register_alias(a, ch)` where `a` was not previously registered: `self._index[a] == ch`.
- The alias key is stored in `_index` alongside primary keys. There is no separate alias data structure.

**Why AssertionError (not ValueError)?**:
This represents a programming error (phase ordering violation), not a runtime data error. If `register_alias()` is called before the canonical channel is registered, the 4-phase construction protocol has been violated.

### 4.3 `resolve(source_path)`

**Behavior**:

```python
def resolve(self, source_path: str) -> str | None:
    return self._index.get(source_path)
```

That is the ENTIRE implementation. One line. No normalization, no cascade, no fallback.

**What resolve() does NOT do**:
- No bare-name extraction (Spike 4: zero bare-name references)
- No SysML QN normalization (`::` -> `__`) (Spike 5: broken for all 4 REFERENCE->MODULE_OUTPUT cases)
- No case-insensitive matching
- No prefix/suffix matching
- No multi-strategy cascade
- No fallback to other indexes

**Caller responsibilities**:
- CHAIN bindings: Pass `source_path` directly to `resolve()`. CHAIN source_paths are always DOTTED format (Spike 1).
- REFERENCE bindings: Do NOT pass raw SYSML_QN source_paths to `resolve()`. The backtracker handles REFERENCE bindings through secondary resolution (leaf extraction + scope matching), which constructs a dotted key before calling `resolve()`.
- Unresolved result (`None`): The backtracker decides the fallback behavior (e.g., `_resolve_to_design_attribute()` -> ENTRY_POINT).

### 4.4 Diagnostic Methods

```python
def __len__(self) -> int:
    return len(self._index)

def __contains__(self, key: str) -> bool:
    return key in self._index

def channels(self) -> frozenset[str]:
    return frozenset(self._canonical)

def keys(self) -> frozenset[str]:
    return frozenset(self._index.keys())
```

**Purpose**: Testing, debugging, and logging. The backtracker does not use these methods during normal resolution. They exist so tests can assert expected registry contents (e.g., "registry has 77 channels and 217 keys for solar_battery").

**Why `frozenset`?**: Prevents callers from mutating the internal state. The returned sets are snapshots.

---

## 5. Key Format Contract

All registration key formats, documented with examples from Spike 8 empirical data.

### 5.1 Key_A: Instance-Dotted Short Key

**Format**: `{instance_name}.{output_attr_name}`

**Producer**: Phase 1 CalcUsage registration.

**Derivation**: `f"{usage.instance_name}.{output_attr.name}"`

**Examples**:
| CalcUsage Type | instance_name | output | Key_A |
|----------------|---------------|--------|-------|
| Concrete | `lcoe` | `lcoe_per_mwh` | `lcoe.lcoe_per_mwh` |
| Virtual | `SolarBatteryDesign__...cost_model` | `total_cost` | `SolarBatteryDesign__...cost_model.total_cost` |

**Notes**:
- For concrete CalcUsages, Key_A is a clean dotted key (e.g., `"lcoe.lcoe_per_mwh"`).
- For virtual CalcUsages, Key_A is a HYBRID key mixing `__` and `.` separators (e.g., `"SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model.total_cost"`). This is unusable for Phase 2 CHAIN alias resolution but is kept for backward compatibility and direct CHAIN binding lookups against concrete producers.
- EXPOSE_PURE aliases (Phase 3) resolve against Key_A for concrete CalcUsages.

### 5.2 Key_B: Full Qualified Key (EQN)

**Format**: `{EQN}__{output_attr_name}`

**Producer**: Phase 1 CalcUsage registration.

**Derivation**: `f"{usage.qualified_name}__{output_attr.name}"` (this is the canonical channel name itself, so Key_B == canonical_channel).

**Examples**:
| Key_B |
|-------|
| `SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh` |
| `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model__total_cost` |

**Notes**:
- Key_B is always the canonical channel name. Registering it ensures the canonical channel can be resolved by its own PQN.
- This is the format used by `get_channel_name()` in `core/qualified_names.py`.

### 5.3 Key_C: Dotted Hierarchy Key (Design-Prefix-Stripped)

**Format**: `".".join(EQN.split("__")[1:]) + "." + output_attr_name`

**Producer**: Phase 1 CalcUsage registration.

**Derivation**:
```python
segments = usage.qualified_name.split("__")
dotted_hierarchy = ".".join(segments[1:])  # Strip design PartDef prefix
key_c = f"{dotted_hierarchy}.{output_attr.name}"
```

**Examples**:
| EQN | Key_C |
|-----|-------|
| `SolarBatteryDesign__solar_battery_plant__lcoe` | `solar_battery_plant.lcoe.lcoe_per_mwh` |
| `SolarBatteryDesign__...__pv_module__cost_model` | `solar_battery_plant.solar_array.pv_module.cost_model.total_cost` |

**Notes**:
- **CRITICAL**: Key_C is the ONLY key format that Phase 2 CHAIN aliases can resolve against for virtual CalcUsages. Without Key_C, all 41 CHAIN aliases in solar_battery fail (Spike 8, Issue 15).
- Key_C strips the PascalCase design PartDef prefix and replaces `__` with `.`, producing a fully dotted path compatible with the Phase 2 alias scoping format.
- For concrete CalcUsages, Key_C differs from Key_A by including the parent PartUsage scope (e.g., `"solar_battery_plant.lcoe.lcoe_per_mwh"` vs `"lcoe.lcoe_per_mwh"`).

### 5.4 Key_D: Part-Usage-Dotted Aggregation Key

**Format**: `{part_usage_name}.{attribute_name}`

**Producer**: Phase 1 Aggregation registration.

**Derivation**: `f"{scoped_agg.expression.owning_part_name}.{scoped_agg.expression.attribute_name}"`

Note: Here `owning_part_name` is the PartDef short name (not the PartUsage instance name). In practice, for aggregation expressions, the part_usage_name used for Key_D comes from the scoped instance context.

**Examples**:
| Key_D |
|-------|
| `solar_array.capital_cost` |
| `battery_pack.capital_cost` |

**Notes**:
- Key_D uses the part_usage_name (instance scope), not the PartDef name.
- Alias variants of Key_D are also registered for each alias in `AggregationExpressionData.aliases` (e.g., `"solar_array.total_capex"` as an alias for `"solar_array.capital_cost"`).

### 5.5 Key_E: Full-Dotted Aggregation Key (With Design Prefix)

**Format**: `".".join(instance_path.split("__")) + "." + attribute_name`

**Producer**: Phase 1 Aggregation registration.

**Derivation**:
```python
dotted_full = ".".join(scoped_agg.instance_path.split("__"))
key_e = f"{dotted_full}.{scoped_agg.expression.attribute_name}"
```

**Examples**:
| Key_E |
|-------|
| `SolarBatteryDesign.solar_battery_plant.solar_array.capital_cost` |

**Notes**:
- Key_E INCLUDES the design prefix (from `instance_path`). This means Key_E will NOT match CHAIN binding source_paths which lack the design prefix.
- Key_E exists for completeness and backward compatibility, not as a primary resolution target.
- Alias variants of Key_E are also registered for each alias.

### 5.6 Key_F: FORMULA Computed Attribute Key

**Format**: `{owning_part_name}.{python_name}`

**Producer**: Phase 1 FORMULA registration.

**Derivation**: `f"{computed_attr.owning_part_name}.{computed_attr.python_name}"`

**Examples**:
| Key_F |
|-------|
| `e2e_plant.power_mw` |
| `solar_battery_plant.p_net_kw` |

**Notes**:
- `owning_part_name` is the short name of the PartUsage that owns the FORMULA computed attribute.
- Channel construction for FORMULA uses: `get_channel_name(sysml_to_python_qualified_name(owning_part_qn) + "__" + python_name, python_name)`.
- REFERENCE bindings that resolve to FORMULA computed attributes use the secondary resolution path in the backtracker (leaf + parent scope), which constructs a Key_F-compatible lookup key.

### 5.7 Summary Table

| Key | Format | Phase | Source | Example | Count (solar_battery) | Count (e2e_attr_expr) |
|-----|--------|-------|--------|---------|----------------------|----------------------|
| Key_A | `instance.output` | 1 | CalcUsage | `lcoe.lcoe_per_mwh` | 56 | 9 |
| Key_B | `EQN__output` | 1 | CalcUsage | `Design__plant__lcoe__lcoe_per_mwh` | 56 | 9 |
| Key_C | `dotted_hierarchy.output` | 1 | CalcUsage | `plant.lcoe.lcoe_per_mwh` | 56 | 9 |
| Key_D | `part_usage.attr` | 1 | Aggregation | `solar_array.capital_cost` | 20 | 0 |
| Key_E | `full_dotted.attr` | 1 | Aggregation | `Design.plant.solar_array.capital_cost` | 20 | 0 |
| Key_F | `owning_part.python_name` | 1 | FORMULA | `e2e_plant.power_mw` | 1 | 6 |
| Alias (CHAIN) | scoped dotted | 2 | ChannelAlias | `solar_array.total_capex` | 41 | 0 |
| Alias (EXPOSE_PURE) | `part.python_name` | 3 | ChannelAlias | `e2e_plant.total_capex` | 0 | 1 |
| Alias (transitive) | `part.attr` | 4 | design attr | `e2e_plant.total_capex` | 0 | 1 |

**Empirical totals** (Spike 8):
- solar_battery: 77 channels, 217 keys. Zero collisions.
- e2e_attr_expr: 15 channels, 33 keys. Zero collisions.

---

## 6. 4-Phase Registration Protocol

The OutputRegistry is built in 4 phases during `build_pipeline_context()` (Step 5, Item 3). Each phase may resolve its alias canonical_names against keys registered in prior phases.

### Phase 1: Primary Channel Registration

Register all CalcUsage outputs, aggregation outputs, and FORMULA computed attributes.

**CalcUsage outputs** (per output attribute on each CalcUsage):
```python
for usage in calc_usages:
    for output_attr in usage.calc_def.output_attributes:
        canonical = get_channel_name(usage.qualified_name, output_attr.name)
        segments = usage.qualified_name.split("__")
        key_a = f"{usage.instance_name}.{output_attr.name}"
        key_b = canonical  # EQN__output
        key_c = ".".join(segments[1:]) + "." + output_attr.name
        registry.register(canonical, [key_a, key_b, key_c])
```

**Aggregation outputs** (per ScopedAggregationData):
```python
for scoped_agg in scoped_aggregations:
    canonical = get_channel_name(scoped_agg.module_eqn, scoped_agg.expression.attribute_name)
    part_usage = scoped_agg.instance_path.split("__")[-1]
    key_d = f"{part_usage}.{scoped_agg.expression.attribute_name}"
    dotted_full = ".".join(scoped_agg.instance_path.split("__"))
    key_e = f"{dotted_full}.{scoped_agg.expression.attribute_name}"
    keys = [key_d, key_e]
    # Also register alias variants from expression.aliases
    for alias_name in scoped_agg.expression.aliases:
        keys.append(f"{part_usage}.{alias_name}")
        keys.append(f"{dotted_full}.{alias_name}")
    registry.register(canonical, keys)
```

**FORMULA outputs** (per FORMULA ComputedAttributeData):
```python
for computed_attr in formula_computed_attrs:
    qn = sysml_to_python_qualified_name(computed_attr.owning_part_qualified_name)
    eqn = f"{qn}__{computed_attr.python_name}"
    canonical = get_channel_name(eqn, computed_attr.python_name)
    key_f = f"{computed_attr.owning_part_name}.{computed_attr.python_name}"
    registry.register(canonical, [key_f])
```

### Phase 2: CHAIN Alias Registration

Register `ChannelAlias` objects from `:>>` CHAIN redefinitions (produced by Step 3.5D).

```python
for alias in chain_aliases:
    resolved = registry.resolve(alias.canonical_name)
    if resolved is not None:
        registry.register_alias(alias.alias_name, resolved)
    else:
        logger.warning(
            "CHAIN alias %r -> %r: canonical name not found in registry",
            alias.alias_name, alias.canonical_name,
        )
```

**Key dependency**: CHAIN alias canonical_names (e.g., `"solar_battery_plant.solar_array.pv_module.cost_model.total_cost"`) resolve against Phase 1 Key_C keys. Without Key_C, all 41 CHAIN aliases in solar_battery would fail.

### Phase 3: EXPOSE_PURE Alias Registration

Register `ChannelAlias` objects from EXPOSE_PURE computed attributes (produced by Step 4.5). Only PartUsage-level aliases (PartDef EXPOSE_PURE filtered at production time).

```python
for alias in expose_pure_aliases:
    resolved = registry.resolve(alias.canonical_name)
    if resolved is not None:
        registry.register_alias(alias.alias_name, resolved)
    else:
        logger.warning(
            "EXPOSE_PURE alias %r -> %r: canonical name not found in registry",
            alias.alias_name, alias.canonical_name,
        )
```

**Key dependency**: EXPOSE_PURE canonical_names (e.g., `"component_cost.total_cost"`) resolve against Phase 1 Key_A keys (concrete CalcUsage instance.output format).

### Phase 4: Transitive Design Attribute Alias Registration

Register aliases from design attributes whose `default_value` is a dotted path referencing a CalcUsage output (transitive EXPOSE pattern).

```python
for attr in design_attributes:
    if _is_transitive_default(attr):
        val = str(attr.default_value)
        resolved = registry.resolve(val)
        if resolved is not None:
            attr_key = f"{attr.parent_part}.{attr.name}"
            registry.register_alias(attr_key, resolved)
```

**`_is_transitive_default()` filter**:
```python
def _is_transitive_default(attr) -> bool:
    """Identify design attributes with dotted-path default_values.

    Returns True if default_value looks like a channel reference
    (contains '.' and is not a numeric float like '3.14').

    Spike 7: 128 attributes tested, 2 transitive defaults found,
    filter correct for all. No false positives or false negatives.
    """
    if attr.default_value is None:
        return False
    val = str(attr.default_value)
    if "." not in val:
        return False
    try:
        float(val)
        return False  # numeric like "3.14"
    except (ValueError, TypeError):
        return True   # dotted path like "component_cost.total_cost"
```

**Note**: `_is_transitive_default()` is a module-level utility function in `output_registry.py`, not a method on the `OutputRegistry` class. It is used only during Phase 4 construction and is not part of the registry's public interface. It is exported for testing purposes.

---

## 7. Error Handling

### 7.1 `register()` Collision

**Trigger**: A lookup key is already mapped to a DIFFERENT canonical channel.

**Behavior**: Log `logger.warning()` with the key, existing channel, and new channel. Refuse to overwrite. Keep the first registration.

**Rationale**: Spike 8 found zero collisions across 250 keys in 2 models. Collisions indicate a bug in key construction, not a normal runtime condition. WARNING level is appropriate because: (a) the system continues to function (first-wins produces correct results if the first registration is correct), (b) the warning surfaces the issue for investigation.

**Example log output**:
```
WARNING:sysml_codegen.core.output_registry:OutputRegistry collision: key 'cost_model.total_cost' already maps to 'Design__plant__mod1__cost_model__total_cost', refusing to overwrite with 'Design__plant__mod2__cost_model__total_cost'
```

### 7.2 `register_alias()` to Unregistered Channel

**Trigger**: `canonical_channel` is not in `_canonical` (was never registered via `register()`).

**Behavior**: Raise `AssertionError`.

**Rationale**: This is a programming error -- the 4-phase construction protocol guarantees that canonical channels are registered in Phase 1 before aliases are registered in Phases 2-4. An AssertionError signals a protocol violation, not a data issue.

### 7.3 `resolve()` Miss

**Trigger**: The `source_path` key is not in `_index`.

**Behavior**: Return `None`. No fallback, no cascade, no warning.

**Rationale**: A resolve miss is NOT an error in the OutputRegistry -- it means the binding does not wire to a pipeline output. The backtracker decides what to do with a miss (e.g., try `_resolve_to_design_attribute()`, or fall through to ENTRY_POINT). The OutputRegistry is a lookup table, not a decision-maker.

---

## 8. What OutputRegistry Does NOT Do

These are deliberate exclusions based on empirical spike findings.

| Excluded Feature | Spike | Rationale |
|-----------------|-------|-----------|
| Bare-name registration | Spike 4 | Zero bare-name references across 94 bindings, 4 models. K=5 ambiguous bare names per model would cause collisions. |
| SysML QN normalization (`::` -> `__`) | Spike 5 | Naive `replace("::", "__")` fails in all 4 REFERENCE->MODULE_OUTPUT cases. The consuming path differs from the producing path. |
| Multi-strategy cascade | All | The cascade exists to bridge key format mismatches across 5 indexes. With one unified index and consistent key formats, exact match suffices. |
| Removal/update of keys | N/A | The registry is built once and used read-only. No keys are removed or updated during backtracking. |
| REFERENCE binding resolution | Spike 5 | REFERENCE bindings use SYSML_QN format which cannot be directly resolved. The backtracker's secondary resolution constructs a dotted lookup key before calling `resolve()`. |

---

## 9. Module-Level Exports

```python
__all__ = [
    "OutputRegistry",
    "_is_transitive_default",  # Exported for testing
]
```

The `_is_transitive_default()` function uses a leading underscore to indicate it is not part of the public API, but is included in `__all__` because tests need to import and verify it independently.

---

## 10. Test Requirements

### 10.1 Unit Tests for OutputRegistry

All tests go in `tests/unit/test_output_registry.py`.

#### Core Registration Tests

1. **register() stores keys**: Register a channel with 3 keys. Assert all 3 keys resolve to the canonical channel.
2. **register() adds to canonical set**: Register a channel. Assert it appears in `channels()`.
3. **register() with empty keys**: Register a channel with `[]`. Assert it appears in `channels()` but no keys are added.
4. **register() idempotent for same channel**: Register the same key->channel mapping twice. No warning logged.
5. **register() collision warning**: Register key `"a.b"` to channel `"ch1"`, then register `"a.b"` to channel `"ch2"`. Assert WARNING logged. Assert `resolve("a.b")` returns `"ch1"` (first wins).

#### Alias Tests

6. **register_alias() maps to canonical**: Register channel `"ch1"` with key `"a.b"`. Then `register_alias("x.y", "ch1")`. Assert `resolve("x.y")` returns `"ch1"`.
7. **register_alias() asserts canonical exists**: Call `register_alias("x.y", "nonexistent")`. Assert `AssertionError` raised.
8. **register_alias() collision warning**: Register `"x.y"` -> `"ch1"` via primary key. Then `register_alias("x.y", "ch2")`. Assert WARNING logged. Assert original mapping preserved.

#### Resolve Tests

9. **resolve() exact match**: Register key `"a.b"` -> `"ch1"`. Assert `resolve("a.b")` returns `"ch1"`.
10. **resolve() miss returns None**: Assert `resolve("nonexistent")` returns `None`.
11. **resolve() no normalization**: Register key `"a.b"`. Assert `resolve("A.B")` returns `None` (case-sensitive). Assert `resolve("a::b")` returns `None` (no QN normalization).

#### Diagnostic Tests

12. **__len__**: Register 3 keys for 1 channel. Assert `len(registry) == 3`.
13. **__contains__**: Register key `"a.b"`. Assert `"a.b" in registry`. Assert `"x.y" not in registry`.
14. **channels()**: Register 2 channels. Assert `channels()` returns both.
15. **keys()**: Register 3 keys. Assert `keys()` returns all 3.

### 10.2 Phase Ordering Tests

16. **Phase 2 resolves against Phase 1**: Register Phase 1 CalcUsage with Key_C = `"plant.cost_model.total_cost"`. Then register Phase 2 CHAIN alias `"solar_array.capital_cost"` -> resolve `"plant.cost_model.total_cost"` -> register alias. Assert `resolve("solar_array.capital_cost")` returns the canonical channel.

17. **Phase 3 resolves against Phase 1**: Register Phase 1 CalcUsage with Key_A = `"component_cost.total_cost"`. Then register Phase 3 EXPOSE_PURE alias `"e2e_plant.total_capex"` -> resolve `"component_cost.total_cost"` -> register alias. Assert `resolve("e2e_plant.total_capex")` returns the canonical channel.

18. **Phase 4 resolves against Phase 1-3**: Register Phase 1 CalcUsage. Register Phase 3 EXPOSE_PURE alias. Then register Phase 4 transitive alias resolving through Phase 3. Assert full chain resolves.

### 10.3 Key Format Tests (Using Spike 8 Data)

19. **Key_A resolves for concrete CalcUsage**: Synthetic concrete CalcUsage with `instance_name="lcoe"`, output `"lcoe_per_mwh"`. Assert `resolve("lcoe.lcoe_per_mwh")` returns canonical channel.

20. **Key_B resolves for all CalcUsages**: Assert `resolve("Design__plant__lcoe__lcoe_per_mwh")` returns canonical channel.

21. **Key_C resolves for virtual CalcUsage**: Synthetic virtual CalcUsage with `qualified_name="Design__plant__solar_array__pv_module__cost_model"`, output `"total_cost"`. Assert `resolve("plant.solar_array.pv_module.cost_model.total_cost")` returns canonical channel.

22. **Key_D resolves for aggregation**: Synthetic `ScopedAggregationData` with part_usage `"solar_array"`, attribute `"capital_cost"`. Assert `resolve("solar_array.capital_cost")` returns canonical channel.

23. **Key_F resolves for FORMULA**: Synthetic FORMULA with `owning_part_name="e2e_plant"`, `python_name="power_mw"`. Assert `resolve("e2e_plant.power_mw")` returns canonical channel.

### 10.4 `_is_transitive_default()` Tests

24. **Dotted path returns True**: `_is_transitive_default(attr_with_default="component_cost.total_cost")` returns True.
25. **Numeric float returns False**: `_is_transitive_default(attr_with_default="3.14")` returns False.
26. **None returns False**: `_is_transitive_default(attr_with_default=None)` returns False.
27. **No dot returns False**: `_is_transitive_default(attr_with_default="total_cost")` returns False.
28. **Integer returns False**: `_is_transitive_default(attr_with_default=42)` returns False.

### 10.5 Collision Test (Spike 8 Scenario)

29. **Virtual CalcUsage Key_A collision**: Two virtual CalcUsages with same `instance_name="Design__plant__mod1__cost_model"` and `instance_name="Design__plant__mod2__cost_model"` but different qualified_names. They produce different Key_B and Key_C but their Key_A format for outputs like `total_cost` would collide if instance_names were the same short name. Verify collision is logged and first-wins.

### 10.6 Test Fixtures

Factory functions in `tests/unit/test_output_registry.py` (or `tests/conftest_output_registry.py`) that produce synthetic data objects:

```python
def make_concrete_calc_usage(instance_name: str, qualified_name: str, outputs: list[str]) -> ...:
    """Synthetic concrete CalcUsage for testing Key_A, Key_B, Key_C registration."""

def make_virtual_calc_usage(qualified_name: str, outputs: list[str]) -> ...:
    """Synthetic virtual CalcUsage for testing Key_C critical path."""

def make_scoped_aggregation(instance_path: str, attribute: str, aliases: list[str]) -> ...:
    """Synthetic ScopedAggregationData for testing Key_D, Key_E + alias registration."""

def make_formula_computed_attr(owning_part_name: str, owning_part_qn: str, python_name: str) -> ...:
    """Synthetic FORMULA ComputedAttributeData for testing Key_F registration."""
```

---

## 11. File Structure

### `src/sysml_codegen/core/output_registry.py`

```
output_registry.py
|-- module docstring
|-- imports (logging)
|-- logger = logging.getLogger(__name__)
|-- class OutputRegistry:
|     |-- __init__(self) -> None
|     |-- register(self, canonical_channel, lookup_keys) -> None
|     |-- register_alias(self, alias, canonical_channel) -> None
|     |-- resolve(self, source_path) -> str | None
|     |-- __len__(self) -> int
|     |-- __contains__(self, key) -> bool
|     |-- channels(self) -> frozenset[str]
|     |-- keys(self) -> frozenset[str]
|-- def _is_transitive_default(attr) -> bool
|-- __all__ = ["OutputRegistry", "_is_transitive_default"]
```

### `src/sysml_codegen/core/__init__.py`

Add `OutputRegistry` and `_is_transitive_default` to the core package exports (if a public `__init__.py` exists with re-exports).

---

## 12. Integration Points (Out of Scope for Item 1)

These are documented for traceability but implemented in later items.

### Item 2: Alias Producers

- `extraction/computed_attribute_extractor.py` produces `list[ChannelAlias]` for EXPOSE_PURE
- `extraction/hierarchy_resolver.py` (or `generation/initialization.py`) produces `list[ChannelAlias]` for CHAIN redefinitions

### Item 3: Registry Construction + Backtracker Integration

- `generation/initialization.py` Step 5 builds the OutputRegistry using the 4-phase protocol
- `analysis/dependency_backtracker.py` accepts `OutputRegistry` in constructor
- `PipelineContext` gains an `output_registry: OutputRegistry` field

### Item 4: Cleanup

- Remove old backtracker indexes (`_computed_attr_index`, `_aggregation_output_index`, etc.)
- Remove `_resolve_binding_to_usage()` cascade
- Remove `_enrich_aliases_from_bindings()` (Step 3.6)

---

## 13. Design Rationale

### Why Not a More Sophisticated Lookup?

The 7-strategy cascade exists because 5 indexes use incompatible key formats. With one index and consistent key construction, exact match suffices. Spike 8 proved this empirically: every CHAIN binding source_path in solar_battery and e2e_attr_expr matches a registered key via exact lookup. Zero missed resolutions.

### Why Defensive Collision Policy Instead of Strict?

Spike 8 found zero collisions, but the models tested (solar_battery, e2e_attr_expr) may not cover all edge cases. A strict policy (raise on collision) would crash codegen on an unexpected model. A defensive policy (warn + first-wins) allows codegen to proceed while surfacing the issue. In the zero-collision expected case, the warning is never triggered.

### Why `frozenset` for `channels()` and `keys()`?

The OutputRegistry is built once and used read-only. Returning `frozenset` enforces this contract at the API level. Callers cannot accidentally mutate the registry's state through the diagnostic methods.

### Why Is `_is_transitive_default()` a Module Function?

It is a pure predicate on a design attribute object. It has no dependency on `OutputRegistry` state. Making it a method would add a method to the class that uses none of its fields. Module-level placement follows the project pattern (e.g., `sanitize_name()` in `qualified_names.py`).

---

**Last Updated**: 2026-02-13
