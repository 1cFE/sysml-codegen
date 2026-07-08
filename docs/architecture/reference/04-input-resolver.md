# 04 -- Consolidated Input Resolver

> **Status (F4 cutover landed, TRUTH-DEBT Item 1): this IS the live aggregation
> path.** Aggregation SumTerm/SingletonTerm resolution runs through
> `resolve_input(ref, ctx, AGG_STRATEGIES)`, called via the choke-point helper
> `_build_agg_input_source()` in `_build_aggregation_module` (`graph_builder.py`).
> The old channel-only function `_resolve_aggregation_input_channel` is **deleted**.
> The cutover reconciled the fallback's entry-point key to the live call sites'
> part-usage-prefixed key, so baselines came out byte-identical, and it is
> parity-validated against the backtracker DFS over the corpus
> (`test_dual_resolution.py`). LocalTerm keeps its own simpler inline fallback,
> but its expose-alias channel reroute now calls `resolve_input` (D5 guard).
> Spec/design/plan in `.project/active/f4-cutover/`.

## Why this module exists

Aggregation modules (SumTerm/SingletonTerm inputs) reimplement input resolution
inline with different strategies and error handling. The consolidated input
resolver replaces these with one function and an explicit, ordered strategy
chain — it is the live SumTerm/SingletonTerm path (see the status note above).
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
| REQ-IR-05 | `AGG_STRATEGIES` SHALL order `ChainRedefinitionFollow` at position 2 (after `ScopedRegistryLookup`, before `SysMLQNLookup`) — the strategy list the live aggregation caller passes. | `AGG_STRATEGIES[0] == ScopedRegistryLookup` and `AGG_STRATEGIES[1] == ChainRedefinitionFollow` |
| REQ-IR-06 | Fallback SHALL produce an `entry_point` [InputSource](#inputsource-output-model) with qualified name `"{module_eqn}__{param_name}"`. | `result.source_type == "entry_point"` and `result.qualified_name.startswith(ctx.module_eqn)` |
| REQ-IR-07 | `resolve_input()` with `AGG_STRATEGIES` SHALL resolve a SumTerm/SingletonTerm ref to the same channel the backtracker DFS resolves it to (parity, and now the live path via `_build_agg_input_source()`). FORMULA modules use pre-computed [attribute resolution](16-computed-attributes.md) (not this resolver). CalcUsage uses the [backtracker cascade](11-analysis-backtracker.md). | `test_dual_resolution.py::TestResolveInputParityExtended` + committed corpus suite |

## Function signature

```python
def resolve_input(
    ref: str,
    ctx: ResolutionContext,
    strategies: list[ResolutionStrategy],
) -> InputSource
```

**`ref`**: Raw symbolic reference ([binding](01-extraction.md#binding-types) `source_path`,
SysML QN, or dotted path). The format of `ref` determines which typed registry
path the strategies will query. **`ctx`**: Immutable context bag with typed
[OutputRegistry](10-output-registry.md). **`strategies`**: Ordered strategy list;
callers must pass explicitly. The live aggregation caller
(`_build_agg_input_source()` in `graph_builder.py`) passes `AGG_STRATEGIES`
(REQ-IR-05). No default.

Always returns an [InputSource](#inputsource-output-model) (REQ-IR-01). Never raises on
unresolved refs -- the [fallback](#fallback) produces an entry point (REQ-IR-06).

## ResolutionContext

Immutable frozen dataclass (REQ-IR-04). No strategy mutates it.

```python
@dataclass(frozen=True)
class ResolutionContext:
    output_registry: OutputRegistry       # Typed registries (10-output-registry)
    redefinitions: list[RedefinitionData]  # :>> chain/literal redefs (01-extraction)
    design_attrs: dict[str, DesignAttributeData]  # QN -> design attr (bare-name matching)
    module_eqn: str                       # Current module EQN (self-reference guard)
    consumer_scope: str                   # Consumer's parent scope (dotted, design prefix stripped)
    instance_path: str                    # Aggregation scope (15-naming-conventions)
```

The `output_registry` provides typed lookups: `scoped_lookup(ScopedKey)`,
`sysml_qn_lookup(SysMLQN)`, and `alias_lookup(ScopedKey)`. Strategies select
the appropriate lookup method based on the reference format.

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

## The four strategies

Each strategy is a callable: `(ref, ctx) -> CanonicalChannel | None`. Returns a
canonical channel on success, `None` to defer to the next strategy (REQ-IR-02).

### A: ScopedRegistryLookup

**Why this exists**: `ref` from a CHAIN binding is a scope-relative local
reference (e.g., `"cost_model.total_cost"`). It is only meaningful within the
consumer's parent scope. Without scoping, a flat lookup is ambiguous when
multiple scopes contain identically-named instances. See
[The Scope Problem](03-resolution-overview.md#the-scope-problem).

**Primary form** (REQ-RES-07): prepend `ctx.consumer_scope` to `ref`, producing
a `ScopedKey`-format path for typed lookup:

```python
scoped_key = ScopedKey(f"{ctx.consumer_scope}.{ref}")
channel: CanonicalChannel | None = ctx.output_registry.scoped_lookup(scoped_key)
```

`ScopedKey` is unique by construction (derived from the SysML ownership chain via
`make_scoped_key()`). The return type is `CanonicalChannel | None`. This is the
**correct** resolution path for all CHAIN bindings. See
[10-output-registry](10-output-registry.md).

At each form, if the scoped registry misses, the same key is retried against
the alias registry (`alias_lookup`) -- this is what resolves EXPOSE_PURE
cross-package references.

**Unscoped fallback**: if the consumer-scoped lookup misses, tries `ref`
directly as a `ScopedKey` (e.g., `"solar_array.capital_cost"` referenced at
plant level), again querying the scoped registry then the alias registry:

```python
catalog_key = ScopedKey(ref)
channel = ctx.output_registry.scoped_lookup(catalog_key)
if channel is None:
    channel = ctx.output_registry.alias_lookup(catalog_key)
```

Refs without a dot return `None` immediately -- Strategy A only handles
dotted paths.

### B: SysMLQNLookup

If `ref` contains `::`, query the SysML QN typed registry directly:

```python
channel: CanonicalChannel | None = ctx.output_registry.sysml_qn_lookup(SysMLQN(ref))
```

This handles REFERENCE bindings where extraction produces a SysML qualified name
(e.g., `"AttrExprProbeDesign::probe_design::area"`). The return type is
`CanonicalChannel | None`. The SysML QN registry contains Phase 1c FORMULA keys.
See [10-output-registry](10-output-registry.md).

The lookup key is per-segment sanitized via `sanitize_qualified_name` before
the query, matching the per-segment-sanitized registration key (so
quoted-owner QNs match). On a miss, Strategy B returns `None` and defers to
the next strategy -- there is no fallback lookup inside it.

> **Note**: Strategy B has zero exercise for aggregation scope — no aggregation
> term ref contains `::` across current fixture models. The backtracker's
> REFERENCE Step 2 (leaf + parent_part scoped lookup,
> `_resolve_reference_via_registry`) is more capable than Strategy B's single
> direct lookup — see
> [24-dual-resolution-architecture](24-dual-resolution-architecture.md).

### C: ChainRedefinitionFollow

Search `ctx.redefinitions` for a CHAIN (`:>>`) [redefinition](01-extraction.md#redefinitions-redefinitiondata)
matching the attribute in `ref`. If found, construct the candidate channel from
the chain's target (via `get_channel_name` under `ctx.instance_path`) and verify
it exists in the registry's canonical channels; if it does not, recurse on the
chain's target. Includes cycle detection
via a visited set. This connects [aggregation](13-aggregation-scoping.md) inputs
to CalcUsage outputs through part hierarchy redefinitions.

### E: DirectChannelConstruction

Reproduces the SingletonTerm "Try 2" direct channel construction that no
registry lookup covers. If `ref` is dotted, build a CalcUsage-format channel
`get_channel_name("{instance_path}__{prefix-with-dots-as-__}", output_name)` and
return it only if it exists in the registry's canonical channels; otherwise
`None`. This resolves CalcUsage EQN-format targets and is a no-op for refs whose
constructed channel is not registered (SumTerm array-child costs, LocalTerms).
It is in-idiom with Strategy C's `{instance_path}__…` construction.

(The former Strategy D `DesignAttributeLookup` was **deleted** in the F4 cutover:
it was a return-None stub with zero live surface — design attributes are entry
points, not module outputs, so it never had a `CanonicalChannel` to return.
Unresolved refs still fall through to the [fallback](#fallback), which builds
the entry point QN from `ctx.module_eqn`.)

## Truth table

| ref | consumer_scope | Strategy | Output |
|-----|---------------|----------|--------|
| `"cost_model.total_cost"` (CHAIN binding) | `"plant.battery_pack"` | **A** | `ScopedKey("plant.battery_pack.cost_model.total_cost")` → `scoped_lookup()` → `module_output` |
| `"catf_radial_build.magnet_surface_area"` (cross-package CHAIN) | `"catf_tf_system"` | **A** (alias) | scoped miss → `alias_lookup(ScopedKey("catf_radial_build.magnet_surface_area"))` → EXPOSE_PURE alias → `module_output` |
| `"AttrExprProbeDesign::probe_design::area"` (REFERENCE) | `"probe_design"` | **B** | `sysml_qn_lookup(SysMLQN("AttrExprProbeDesign::probe_design::area"))` → Phase 1c key → `module_output` |
| `"pv_module.capital_cost"` (`:>> calc_cost.total`) | `"plant.solar_array"` (agg) | **C** | follows CHAIN redef → `ScopedKey` → `scoped_lookup()` → upstream channel |
| `"panel_efficiency"` (matches design attr) | `"plant.solar_array"` | fallback (no strategy matches) | `entry_point`, QN `"<module_eqn>__panel_efficiency"` |
| `"unknown_param"` | `"plant.battery_pack"` | fallback | `entry_point`, QN `"<module_eqn>__unknown_param"` |

Row 1 is the critical case: a bare CHAIN `source_path` disambiguated by prepending
`consumer_scope` to form a `ScopedKey` lookup. This is the typed equivalent of the
former Key_C lookup. See [The Scope Problem](03-resolution-overview.md#the-scope-problem).

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
param_name = ref.replace(".", "_")
return InputSource(
    source_type="entry_point",
    qualified_name=f"{ctx.module_eqn}__{param_name}",
)
```

The fallback QN was reconciled at the F4 cutover from a leaf-only rsplit to the
part-usage-prefixed key `{module_eqn}__{ref-with-dots-as-underscores}` — the key
the live call sites already minted. A leaf-only key would collide sibling
part-usage inputs and clash with the module's own output channel; the
reconciled key is what made the cutover baselines byte-identical.

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
    ScopedRegistryLookup,       # A: ScopedKey → scoped registry + alias registry
    ChainRedefinitionFollow,    # C: :>> chain → ScopedKey → scoped registry
    SysMLQNLookup,              # B: SysMLQN → SysML QN registry (for :: refs)
    DirectChannelConstruction,  # E: CalcUsage-format channel construction (Try 2)
]
```

**Why A is first** ([REQ-RES-07](03-resolution-overview.md#the-scope-problem)):
CHAIN `source_path` is a scope-relative reference. The scoped lookup using
`ScopedKey` is the only correct resolution for models where instance names are
not globally unique. With typed registries, there is no ambiguity risk — the
scoped registry contains only `ScopedKey` entries (scope-qualified by
construction). See [10-output-registry](10-output-registry.md).

`AGG_STRATEGIES` promotes `ChainRedefinitionFollow` to position 2 (REQ-IR-05):
aggregation inputs ([SumTerms](05-module-factory.md#4a-sumterm)) almost always
resolve through `:>>` chains rather than direct registry keys.

```python
# Live aggregation call site (05-module-factory), inside _build_agg_input_source():
source = resolve_input(ref, ctx, strategies=AGG_STRATEGIES)  # SumTerm/SingletonTerm
```

## What this eliminated

The cutover collapsed aggregation resolution into `resolve_input()` behind the
`_build_agg_input_source()` choke point. CalcUsage resolution remains in the
[backtracker](11-analysis-backtracker.md)
([24](24-dual-resolution-architecture.md)); FORMULA uses the pre-computed
attribute resolution map, not this resolver. For aggregation, ~160 lines of
inline logic (the deleted `_resolve_aggregation_input_channel` + the three
per-call-site term-type fallbacks) became context construction + a single call.

## Related Documents

- **Upstream**: [03-resolution-overview](03-resolution-overview.md), [01-extraction](01-extraction.md)
- **Downstream**: [05-module-factory](05-module-factory.md), [06-entry-point-classifier](06-entry-point-classifier.md)
- **Architecture**: [24-dual-resolution-architecture](24-dual-resolution-architecture.md) -- why two paths
- **Registry**: [10-output-registry](10-output-registry.md), [15-naming-conventions](15-naming-conventions.md) -- typed identifier definitions
- **Data models**: [09-data-models](09-data-models.md) -- InputSource, ResolutionContext
