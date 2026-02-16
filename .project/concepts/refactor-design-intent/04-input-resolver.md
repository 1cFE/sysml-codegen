# 04 -- Unified Input Resolver

## Why this module exists

Today, resolving "what feeds this input?" is implemented in four separate
functions across two files:

| Function | File | What it does |
|----------|------|--------------|
| `_resolve_binding_via_registry` | `dependency_backtracker.py` | CalcUsage inputs: registry, QN normalization, scoped retry, design attr |
| `_resolve_reference_via_registry` | `dependency_backtracker.py` | REFERENCE bindings: leaf extraction + parent-scope retry |
| `_resolve_aggregation_input_channel` | `graph_builder.py` | Aggregation inputs: CHAIN follow, scoped registry, unscoped fallback |
| `_build_computed_attr_module` (inline) | `graph_builder.py` | ComputedAttribute inputs: resolution map lookup, entry point creation |

Each reimplements the same pattern: try the registry, normalize, follow a
redefinition chain, fall back to entry point. The Unified Input Resolver
replaces all four with one function and an explicit, ordered strategy chain.

---

## Function signature

```python
def resolve_input(
    ref: str,
    ctx: ResolutionContext,
    strategies: list[ResolutionStrategy] = STANDARD_STRATEGIES,
) -> InputSource
```

**`ref`**: Raw symbolic reference (binding `source_path`, SysML QN, dotted
path, or bare name). **`ctx`**: Immutable context bag (next section).
**`strategies`**: Ordered strategy list; defaults to `STANDARD_STRATEGIES`,
aggregation modules override with `AGG_STRATEGIES`.

Always returns an `InputSource`. Never raises on unresolved refs -- the
fallback produces an entry point.

---

## ResolutionContext

Immutable frozen dataclass. No strategy mutates it.

```python
@dataclass(frozen=True)
class ResolutionContext:
    output_registry: OutputRegistry       # Phase 1-4 lookup table; resolve(key) -> channel | None
    redefinitions: list[RedefinitionData]  # :>> chain/literal redefs from PartDefs
    design_attrs: dict[str, DesignAttributeData]  # QN -> design attr (for bare-name matching)
    module_eqn: str                       # Current module EQN (self-reference guard)
    instance_path: str                    # Aggregation scope, e.g. "Design__plant__solar_array"
```

`instance_path` is empty string for non-aggregation modules.

---

## The five strategies

Each strategy is a callable: `(ref, ctx) -> str | None`. Returns a canonical
channel name on success, `None` to defer to the next strategy.

### A: DirectRegistryLookup

`ctx.output_registry.resolve(ref)` -- exact match. The happy path when the
binding `source_path` was registered verbatim as a Key_A/B/C/D.

### B: SysmlQnNormalization

If `ref` contains `::`, normalize to registry format: split on `::`,
sanitize/lowercase the penultimate segment, join as dotted path, re-resolve.
Bridges SysML `Package::Part::attr` to the registry's `part.attr` format.

### C: ScopedRegistryLookup

Prepend instance scope to `ref` and retry. Strips the design prefix from
`ctx.instance_path`, builds a dotted scoped key, calls `resolve()`. Also
tries a secondary form: extract leaf from `ref`, combine with parent part,
retry. Subsumes the current `_resolve_reference_via_registry` logic.

### D: ChainRedefinitionFollow

Search `ctx.redefinitions` for a CHAIN (`:>>`) redefinition matching the
attribute in `ref`. If found, recursively resolve the chain's target.
Includes cycle detection via a visited set. This connects aggregation inputs
to CalcUsage outputs through part hierarchy redefinitions.

### E: DesignAttributeLookup

Match `ref` against `ctx.design_attrs` by name (bare, dotted, or SysML QN).
Returns the design attribute's QN, which becomes the entry point QN.
Enables entry point deduplication: multiple modules binding to the same
design attribute share one entry point.

---

## Truth table

| ref | instance_path | Strategy | Output |
|-----|---------------|----------|--------|
| `"solar_battery_plant.lcoe.lcoe_per_mwh"` | `""` | A | `module_output`, channel `"Design__plant__lcoe__lcoe_per_mwh"` |
| `"SolarBattery::calc_energy::output"` | `""` | B | normalized to `"solar_battery.calc_energy.output"`, found in registry |
| `"capacity"` | `"Design__plant__solar_array"` | C | tries `"plant.solar_array.capacity"`, finds channel |
| `"pv_module.capital_cost"` (`:>> calc_cost.total`) | `"Design__plant__solar_array"` | D | follows chain to `"calc_cost.total"`, resolves to channel |
| `"panel_efficiency"` (matches design attr) | `""` | E | `entry_point`, QN `"SolarArray__panel_efficiency"` |
| `"unknown_param"` | `""` | fallback | `entry_point`, QN `"<module_eqn>__unknown_param"` |

---

## Self-reference guard

After each strategy returns a channel, the resolver checks whether that
channel belongs to the current module:

```python
if channel is not None:
    producing_module = channel.rsplit("__", 1)[0]
    if producing_module == ctx.module_eqn:
        channel = None
        continue  # try next strategy
```

Without this, a module whose expression references its own output attribute
would wire its input to its own output, creating a cycle. The guard forces
fallthrough to a later strategy or the entry point fallback.

**Example**: Module `Design__plant__lcoe` outputs `lcoe_per_mwh` and its
expression references `lcoe_per_mwh`. Strategy A finds channel
`Design__plant__lcoe__lcoe_per_mwh`. Guard detects self-reference, skips,
falls through to create an entry point.

---

## Fallback

If no strategy matches:

```python
return InputSource(
    source_type="entry_point",
    qualified_name=f"{ctx.module_eqn}__{extract_param_name(ref)}",
)
```

The caller registers the entry point in the mutable `entry_points` dict.
The resolver itself is pure -- it decides the `InputSource`, never mutates.

---

## InputSource output model

```python
class InputSource(BaseModel):  # Pydantic BaseModel, not a dataclass
    source_type: Literal["module_output", "entry_point"]
    producer_channel: str | None = None   # set when source_type == "module_output"
    qualified_name: str | None = None     # set when source_type == "entry_point"
    param_group: str | None = None        # parameter group for entry points
```

Exactly one of `producer_channel` or `qualified_name` is set. This model
already exists in `resolution/models.py`; the refactoring does not change its shape.

---

## Per-module-type strategy overrides

```python
STANDARD_STRATEGIES = [
    DirectRegistryLookup, SysmlQnNormalization, ScopedRegistryLookup,
    ChainRedefinitionFollow, DesignAttributeLookup,
]

AGG_STRATEGIES = [
    DirectRegistryLookup, ChainRedefinitionFollow, ScopedRegistryLookup,
    SysmlQnNormalization, DesignAttributeLookup,
]
```

`AGG_STRATEGIES` promotes `ChainRedefinitionFollow` to position 2:
aggregation inputs (SumTerms like `pv_module.capital_cost`) almost always
resolve through `:>>` chains rather than direct registry keys.

```python
# In _build_aggregation_module:
source = resolve_input(symbolic_ref, ctx, strategies=AGG_STRATEGIES)

# In _build_computed_attr_module:
source = resolve_input(input_name, ctx)  # STANDARD_STRATEGIES
```

---

## What this eliminates

The four current functions collapse into call sites that build a
`ResolutionContext` and call `resolve_input()`. 160+ lines of duplicated
logic reduce to context construction and a single call. Bug fixes apply
uniformly. New strategies mean one callable in the list, not shotgun surgery.
