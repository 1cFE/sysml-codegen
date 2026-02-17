# 04 -- Consolidated Input Resolver

## Why this module exists

Aggregation modules (SumTerm/SingletonTerm inputs) reimplement input resolution
inline with different strategies and error handling. The consolidated input
resolver replaces these with one function and an explicit, ordered strategy chain.
CalcUsage resolution stays in the [backtracker](11-analysis-backtracker.md) (DFS
requires it — see [24](24-dual-resolution-architecture.md)). FORMULA modules use
a [pre-computed attribute resolution map](16-computed-attributes.md) (not this
resolver). LocalTerm uses a [factory-specific cascade](05-module-factory.md#4c-localterm).

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-IR-01 | `resolve_input()` SHALL always return an [InputSource](#inputsource-output-model) -- never raise on unresolved refs. | Return type annotation; fallback path always produces `entry_point` |
| REQ-IR-02 | Strategies SHALL execute in declared list order; first non-None result wins. | `for strategy in strategies: result = strategy(ref, ctx); if result: return ...` |
| REQ-IR-03 | Self-reference guard SHALL reject channels where the producing module [EQN](15-naming-conventions.md) matches `ctx.module_eqn`. | Guard check after each strategy: `channel.rsplit("__", 1)[0] == ctx.module_eqn` triggers skip |
| REQ-IR-04 | [ResolutionContext](#resolutioncontext) SHALL be immutable (`frozen=True`); no strategy mutates it. | `@dataclass(frozen=True)` on ResolutionContext; mutation raises `FrozenInstanceError` |
| REQ-IR-05 | Aggregation modules SHALL use `AGG_STRATEGIES` with `ChainRedefinitionFollow` at position 2 (after `ScopedRegistryLookup`, before `DirectRegistryLookup`). | `AGG_STRATEGIES[0] == ScopedRegistryLookup` and `AGG_STRATEGIES[1] == ChainRedefinitionFollow` |
| REQ-IR-06 | Fallback SHALL produce an `entry_point` [InputSource](#inputsource-output-model) with qualified name `"{module_eqn}__{param_name}"`. | `result.source_type == "entry_point"` and `result.qualified_name.startswith(ctx.module_eqn)` |
| REQ-IR-07 | Aggregation SumTerm and SingletonTerm inputs SHALL use `resolve_input()` with `AGG_STRATEGIES`. FORMULA modules use pre-computed [attribute resolution](16-computed-attributes.md) (not this resolver). LocalTerm uses [factory-specific cascade](05-module-factory.md#4c-localterm). CalcUsage uses the [backtracker cascade](11-analysis-backtracker.md). | Aggregation call sites use `AGG_STRATEGIES` |

## Function signature

```python
def resolve_input(
    ref: str,
    ctx: ResolutionContext,
    strategies: list[ResolutionStrategy] = STANDARD_STRATEGIES,
) -> InputSource
```

**`ref`**: Raw symbolic reference ([binding](01-extraction.md#binding-types) `source_path`,
SysML QN, dotted path, or bare name). **`ctx`**: Immutable context bag.
**`strategies`**: Ordered strategy list; defaults to `STANDARD_STRATEGIES`,
aggregation modules override with `AGG_STRATEGIES` (REQ-IR-05).

Always returns an [InputSource](#inputsource-output-model) (REQ-IR-01). Never raises on
unresolved refs -- the [fallback](#fallback) produces an entry point (REQ-IR-06).

## ResolutionContext

Immutable frozen dataclass (REQ-IR-04). No strategy mutates it.

```python
@dataclass(frozen=True)
class ResolutionContext:
    output_registry: OutputRegistry       # Phase 1-4 lookup table (10-output-registry)
    redefinitions: list[RedefinitionData]  # :>> chain/literal redefs (01-extraction)
    design_attrs: dict[str, DesignAttributeData]  # QN -> design attr (bare-name matching)
    module_eqn: str                       # Current module EQN (self-reference guard)
    consumer_scope: str                   # Consumer's parent scope (dotted, design prefix stripped)
    instance_path: str                    # Aggregation scope (15-naming-conventions)
```

**`consumer_scope`** is derived from `module_eqn` for ALL module types (REQ-RES-08).
Derivation: split `module_eqn` on `__`, drop `segments[0]` (design prefix) and
`segments[-1]` (self), join with `.`. Empty string only when `module_eqn` has
fewer than 3 segments.

This field exists because [extraction produces scope-relative references](03-resolution-overview.md#the-scope-problem).
A CHAIN `source_path` like `"cost_model.total_cost"` is local to the consumer's
parent scope. Without `consumer_scope`, Strategy C cannot re-attach the scope
needed for an unambiguous [Key_C](15-naming-conventions.md#7-output-registry-key-formats)
lookup.

`instance_path` is used only for aggregation-specific scoping (term resolution
within the aggregation's owning part hierarchy). It is empty string for
non-aggregation modules. See [09-data-models](09-data-models.md) for field types.

For aggregation modules, `module_eqn` always has 3+ segments (design prefix +
instance path + attribute), so `consumer_scope` is always non-empty.
Example: `module_eqn = "SolarBatteryDesign__solar_array__capital_cost"` →
`consumer_scope = "solar_array"`.

## The five strategies

Each strategy is a callable: `(ref, ctx) -> str | None`. Returns a canonical
channel name on success, `None` to defer to the next strategy (REQ-IR-02).

### A: DirectRegistryLookup

`ctx.output_registry.resolve(ref)` -- exact match. The happy path when the
binding `source_path` was registered verbatim as a [Key_B/C/D](15-naming-conventions.md#6-channel-name)
or a Phase 2-4 alias in the [OutputRegistry](10-output-registry.md).

> **Key_A ambiguity warning (cross-ref [REQ-OR-08](10-output-registry.md)):**
> Strategy A can hit Key_A (`{instance_name}.{attr}`), which is ambiguous when
> multiple scopes contain identically-named instances. In `AGG_STRATEGIES`,
> Strategy C (scoped) runs first, so Strategy A only fires when scoped
> resolution missed. If Strategy A resolves via a Key_A hit, the same silent
> wrong-answer risk applies as in the backtracker's former Step 1. The
> backtracker now raises `UnscopedResolutionError` for this case
> ([REQ-BT-08](11-analysis-backtracker.md)). Strategy A in `resolve_input()`
> should apply the same guard when implemented — flag for C12 implementation.

### B: SysmlQnNormalization

> **REMOVAL_CANDIDATE** — 0% success rate across 3 models (94 bindings).
> No tested model produces a `::` reference at resolution time; all SysML QNs
> are converted to EQN format at extraction. Retained for documentation
> completeness; flagged for Phase 7.4 dead code removal. See Research §5.#5.

If `ref` contains `::`, normalize to registry format: split on `::`,
sanitize/lowercase the penultimate segment, join as dotted path, re-resolve.
Bridges SysML `Package::Part::attr` to the registry's `part.attr` format.

### C: ScopedRegistryLookup

**Why this exists**: `ref` from a CHAIN binding is a scope-relative local
reference (e.g., `"cost_model.total_cost"`). It is only meaningful within the
consumer's parent scope. Without scoping, an unscoped registry lookup (Strategy A)
hits [Key_A](15-naming-conventions.md#7-output-registry-key-formats) which is
ambiguous when multiple scopes contain identically-named instances. See
[The Scope Problem](03-resolution-overview.md#the-scope-problem).

**Primary form** (REQ-RES-07): prepend `ctx.consumer_scope` to `ref`, producing
a [Key_C](15-naming-conventions.md#7-output-registry-key-formats)-format path:

```python
scoped_key = f"{ctx.consumer_scope}.{ref}"   # e.g. "plant.subsys.battery_pack.cost_model.total_cost"
channel = ctx.output_registry.resolve(scoped_key)
```

Key_C is unique by construction (derived from the SysML ownership chain via
`OutputRegistry.derive_key_c()`). This is the **correct** resolution path for
all CHAIN bindings.

**Aggregation form**: when `ctx.instance_path` is set, also tries the
aggregation-scoped key (strips design prefix from `instance_path`, prepends
to `ref`). This handles aggregation term resolution within the owning part
hierarchy.

**Secondary form**: extract leaf name from `ref` (after last `.` or `::`),
combine with parent part name from `ctx.consumer_scope`, retry. Subsumes the
current `_resolve_reference_via_registry` logic from the
[backtracker](11-analysis-backtracker.md). Handles REFERENCE bindings where the
ref is a fully-qualified SysML path but the relevant output is registered under
the parent part's short name.

### D: ChainRedefinitionFollow

Search `ctx.redefinitions` for a CHAIN (`:>>`) [redefinition](01-extraction.md#redefinitions-redefinitiondata)
matching the attribute in `ref`. If found, recursively resolve the chain's
target. Includes cycle detection via a visited set. This connects
[aggregation](13-aggregation-scoping.md) inputs to CalcUsage outputs through
part hierarchy redefinitions.

### E: DesignAttributeLookup

Match `ref` against `ctx.design_attrs` by name (bare, dotted, or SysML QN).
Returns the design attribute's QN, which becomes the [entry point](06-entry-point-classifier.md)
QN. Enables entry point deduplication: multiple modules binding to the same
design attribute share one entry point.

## Truth table

| ref | consumer_scope | Strategy | Output |
|-----|---------------|----------|--------|
| `"cost_model.total_cost"` (CHAIN binding) | `"plant.battery_pack"` | **C** | scoped key `"plant.battery_pack.cost_model.total_cost"` (Key_C) -> `module_output` |
| `"solar_battery_plant.lcoe.lcoe_per_mwh"` (already qualified) | `"plant.battery_pack"` | A | direct Key_C match in registry (C tried first, C's scoped form doesn't match) |
| `"SolarBattery::calc_energy::output"` | `"plant.battery_pack"` | B | normalized to `"solar_battery.calc_energy.output"`, found in registry *(never exercised in tested models — REMOVAL_CANDIDATE)* |
| `"pv_module.capital_cost"` (`:>> calc_cost.total`) | `"plant.solar_array"` (agg) | D | follows CHAIN redef to upstream channel |
| `"panel_efficiency"` (matches design attr) | `"plant.solar_array"` | E | `entry_point`, QN `"SolarArray__panel_efficiency"` |
| `"unknown_param"` | `"plant.battery_pack"` | fallback | `entry_point`, QN `"<module_eqn>__unknown_param"` |

Row 1 is the critical case: a bare CHAIN `source_path` disambiguated by prepending
`consumer_scope` to form a [Key_C](15-naming-conventions.md#7-output-registry-key-formats)
lookup. Without this, `"cost_model.total_cost"` would hit Key_A (ambiguous).
See [The Scope Problem](03-resolution-overview.md#the-scope-problem).

## Self-reference guard

After each strategy returns a channel (REQ-IR-03), the resolver checks whether
that channel belongs to the current module:

```python
if channel is not None:
    producing_module = channel.rsplit("__", 1)[0]
    if producing_module == ctx.module_eqn:
        channel = None
        continue  # try next strategy
```

Without this, a module whose expression references its own output attribute
would wire its input to its own output, creating a cycle. The guard forces
fallthrough to a later strategy or the [entry point fallback](#fallback).

**Example**: Module `Design__plant__lcoe` outputs `lcoe_per_mwh` and its
expression references `lcoe_per_mwh`. Strategy A finds channel
`Design__plant__lcoe__lcoe_per_mwh`. Guard detects self-reference, skips,
falls through to create an entry point.

## Fallback

If no strategy matches (REQ-IR-06):

```python
return InputSource(
    source_type="entry_point",
    qualified_name=f"{ctx.module_eqn}__{extract_param_name(ref)}",
)
```

The caller registers the entry point in the mutable `entry_points` dict.
The resolver itself is pure -- it decides the [InputSource](#inputsource-output-model),
never mutates shared state.

## InputSource output model

```python
class InputSource(BaseModel):  # Pydantic BaseModel, not a dataclass
    source_type: Literal["module_output", "entry_point"]
    producer_channel: str | None = None   # set when source_type == "module_output"
    qualified_name: str | None = None     # set when source_type == "entry_point"
    param_group: str | None = None        # parameter group for entry points
```

Exactly one of `producer_channel` or `qualified_name` is set. This model
already exists in `resolution/models.py` ([09-data-models](09-data-models.md#resolution-models));
the refactoring does not change its shape.

## Strategy chain

```python
AGG_STRATEGIES = [
    ScopedRegistryLookup, ChainRedefinitionFollow, DirectRegistryLookup,
    SysmlQnNormalization,    # REMOVAL_CANDIDATE — 0% success (Research §5.#5)
    DesignAttributeLookup,
]
```

**Why C is first** ([REQ-RES-07](03-resolution-overview.md#the-scope-problem)):
CHAIN `source_path` is a scope-relative reference. The scoped lookup (Key_C)
is the only correct resolution for models where instance names are not globally
unique. Strategy A (unscoped) is retained for references that are already
globally unambiguous (fully-qualified paths, Phase 2-4 alias hits), but must
guard against Key_A hits — see [REQ-OR-08](10-output-registry.md) and the
warning on Strategy A above. See [The Scope Problem](03-resolution-overview.md#the-scope-problem).

`AGG_STRATEGIES` promotes `ChainRedefinitionFollow` to position 2 (REQ-IR-05):
aggregation inputs ([SumTerms](05-module-factory.md#4a-sumterm)) almost always
resolve through `:>>` chains rather than direct registry keys.

```python
# In aggregation factory (05-module-factory):
source = resolve_input(ref, ctx, strategies=AGG_STRATEGIES)  # SumTerm/SingletonTerm
```

## What this eliminates

FORMULA and Aggregation resolution collapse into `resolve_input()` call sites.
CalcUsage resolution remains in the [backtracker](11-analysis-backtracker.md)
([24](24-dual-resolution-architecture.md)). For FORMULA/Agg, 160+ lines of
duplicated logic become context construction + a single call.

## Related Documents

- **Upstream**: [03-resolution-overview](03-resolution-overview.md), [01-extraction](01-extraction.md)
- **Downstream**: [05-module-factory](05-module-factory.md), [06-entry-point-classifier](06-entry-point-classifier.md)
- **Architecture**: [24-dual-resolution-architecture](24-dual-resolution-architecture.md) -- why two paths
- **Registry**: [10-output-registry](10-output-registry.md), [15-naming-conventions](15-naming-conventions.md)
- **Data models**: [09-data-models](09-data-models.md) -- InputSource, ResolutionContext
