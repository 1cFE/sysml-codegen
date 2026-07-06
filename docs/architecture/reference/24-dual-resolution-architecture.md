# 24 -- Why Resolution Has Two Paths (and Must Stay That Way)

## The Structural Constraint

Resolution answers one question for every input: "where does this value come
from?" ([03-resolution-overview](03-resolution-overview.md)). It would be
cleaner to answer it with one function. But a structural constraint prevents
full unification: **CalcUsage resolution must happen during DFS traversal.**

The [backtracker](11-analysis-backtracker.md)'s DFS discovers which modules are
needed by tracing bindings. To trace a binding, it must resolve it -- only then
can it know whether to recurse into an upstream module (MODULE_OUTPUT) or stop
(ENTRY_POINT). Resolution and discovery are inseparable:

```python
# dependency_backtracker.py, _trace_dependencies:
resolution = self._resolve_binding_via_registry(binding, usage)
if resolution.resolution_type == MODULE_OUTPUT:
    producing_usage = self._find_usage_for_channel(resolution.qualified_name)
    self._trace_dependencies(producing_usage, visited, path)  # RECURSE
```

FORMULA and Aggregation modules are discovered differently -- not by tracing
bindings but by scanning computed attributes and aggregation expressions. They
are built AFTER the DFS completes. Their resolution CAN be extracted into a
standalone [`resolve_input()`](04-input-resolver.md).

This gives us two resolution paths. Not by accident, but by necessity.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-DRA-01 | CalcUsage resolution SHALL happen during backtracker DFS; the DFS decision (recurse vs stop) depends on the resolution result. | `_trace_dependencies` calls `_resolve_binding_via_registry`; branches on `resolution_type` to decide recurse vs stop |
| REQ-DRA-02 | FORMULA SHALL use pre-computed [attribute resolution map](16-computed-attributes.md). Aggregation SumTerm/SingletonTerm SHALL use [`resolve_input()`](04-input-resolver.md) with `AGG_STRATEGIES`. LocalTerm SHALL use factory-specific cascade. | Factory call sites use appropriate resolution mechanism |
| REQ-DRA-03 | Both paths SHALL use typed registries ([10-output-registry](10-output-registry.md)): `scoped_lookup(ScopedKey)` for CHAIN bindings, `sysml_qn_lookup(SysMLQN)` for REFERENCE bindings, `alias_lookup(ScopedKey)` for cross-package. No untyped `dict.get()`. | Backtracker: type-directed dispatch (REQ-BT-08). resolve_input(): Strategy A uses `scoped_lookup()`, Strategy B uses `sysml_qn_lookup()`. |
| REQ-DRA-04 | Both paths SHALL produce the same wiring for the same reference. A binding `"cost_model.total_cost"` in scope `"plant.battery_pack"` SHALL resolve to the same channel regardless of path. | Integration test: same reference through both paths → identical `InputSource` |
| REQ-DRA-05 | The backtracker SHALL produce `BindingResolution` objects; `resolve_input()` SHALL produce `InputSource` objects. Both encode the same two-valued answer (module_output or entry_point). | `BindingResolution.resolution_type` maps to `InputSource.source_type` |

---

## Path 1: CalcUsage Resolution (Backtracker)

**When**: During DFS traversal, before graph construction.
**File**: `analysis/dependency_backtracker.py`, `_resolve_binding_via_registry()`.
**Input**: `BindingInfo` from [CalcUsageData](09-data-models.md#extraction-models).
**Output**: `BindingResolution` stored in `binding_resolutions` dict.

### Type-directed dispatch (REQ-BT-08)

Resolution dispatches on the binding's `source_path` format, selecting the
appropriate typed registry. See [10-output-registry](10-output-registry.md) Design Rationale.

**CHAIN bindings** (no `::` in source_path) — `_resolve_chain_dispatch`:

```
Step 1:  Scoped lookup (primary)
         ScopedKey(consumer_scope + "." + source_path) → scoped registry
         → CanonicalChannel or None

Step 1b: Direct scoped lookup (no consumer-scope prefix)
         ScopedKey(source_path) → scoped registry
         (covers Key_F FORMULA outputs registered as owning_part.attr)

Step 1c: Structured scoped-alias lookup (REQ-BT-11, Item 10)
         Split source_path at the LAST dot into (scope, leaf); query the
         structured _scoped_alias namespace with the consumer-scope-prefixed
         key first, then the bare ScopedAliasKey((scope, leaf))
         (reaches a part-def EXPOSE that no flat string key constructs;
         the consumer-scope prepend disambiguates same-named siblings)

Step 2:  Alias lookup (cross-scope)
         ScopedKey(source_path) → alias registry
         → CanonicalChannel or None

Step 3:  Design attribute match → ENTRY_POINT

Step 4:  Fallback → ENTRY_POINT (recorded for V11)
```

**REFERENCE bindings** (`::` in source_path) — `_resolve_reference_dispatch`:

```
Step 1: SysML QN lookup (primary)
        SysMLQN(sanitize_qualified_name(source_path)) → SysML QN registry
        (the key is per-segment sanitized to match the registration key,
        REQ-BT-09 — a quoted-owner QN like Lib::'Magnet Part'::attr matches)

Step 2: Leaf + scope lookup (secondary, _resolve_reference_via_registry)
        Extract the leaf; try ScopedKey(parent_part.leaf), then
        ScopedKey(consumer_scope.leaf) — scoped registry, then alias registry

Step 3: Design attribute match → ENTRY_POINT

Step 4: Fallback → ENTRY_POINT (recorded for V11)
```

Each lookup step includes a **self-reference guard**: if the resolved channel
belongs to the current usage, the resolution is discarded.

Step 3 (`_resolve_to_design_attribute`) carries the Item 7 matcher fixes:

- A `::` source_path is per-segment sanitized before the exact qualified-name
  match (REQ-BT-09), so a quoted-owner QN matches the design attribute's
  per-segment-sanitized `qualified_name`.
- A dotted path whose exact `parent_part` match fails falls back to a
  leaf-unique match over design-part attributes (REQ-BT-10) — an attribute
  owned by a part *def* extracts with empty `parent_part`, so the exact match
  never fires for it. The fallback excludes calc-def I/O attributes
  (`_is_calc_def_owned`) and refuses ambiguous candidates, so a dotted
  calc-output reference stays unresolved and loud rather than cross-wired.

Step 4 logs its per-binding "Registry unresolved" line at DEBUG, not WARNING,
and records the fall-through in `BacktrackingResult.fallback_entry_points`.
That set feeds the V11 params-coverage collector
(`collect_uncovered_params`, `resolution/graph_builder.py`) and the
post-assembly reconciliation summary — the single-WARNING operator digest for
genuine residue.

**Result**: `BindingResolution(resolution_type, qualified_name, source_path, is_transitive)`.
Stored in `BacktrackingResult.binding_resolutions` keyed by
`"{usage_qn}|{param_name}"`. Consumed by `_build_pipeline_module()` in the
[module factory](05-module-factory.md#2-calcusage-modules).

---

## Path 2: FORMULA/Aggregation Resolution

**When**: During graph construction, after DFS.
**File**: `resolution/input_resolver.py`, `resolve_input()`.
**Input**: Symbolic reference string + [ResolutionContext](04-input-resolver.md#resolutioncontext).
**Output**: `InputSource` (consumed immediately by the factory).

### Strategy chain

FORMULA uses a pre-computed [attribute resolution map](16-computed-attributes.md),
not `resolve_input()`. Aggregation SumTerm/SingletonTerm inputs use:

```
AGG_STRATEGIES:
  A: ScopedRegistryLookup     — ScopedKey → scoped registry + alias registry
  C: ChainRedefinitionFollow   — :>> chain → ScopedKey → scoped registry
  B: SysMLQNLookup            — SysMLQN → SysML QN registry (for :: refs)
  D: DesignAttributeLookup    — design attr match → entry point
```

`ChainRedefinitionFollow` (C) is promoted because aggregation inputs almost
always resolve through `:>>` chains. All strategies use typed registry methods.
LocalTerm uses a factory-specific cascade
(see [05](05-module-factory.md#4c-localterm)).
See [04-input-resolver](04-input-resolver.md) for strategy details.

---

## Strategy Overlap Between Paths

Both paths solve the same problem with overlapping (but not identical) strategies:

| Strategy | Backtracker (CalcUsage) | Agg resolve_input() / FORMULA attr map |
|----------|:-:|:-:|
| Scoped lookup (`scoped_lookup(ScopedKey)`) | CHAIN Steps 1/1b | Strategy A (primary form) |
| Scoped-alias lookup (`scoped_alias_lookup(ScopedAliasKey)`) | CHAIN Step 1c | -- |
| Alias lookup (`alias_lookup(ScopedKey)`) | CHAIN Step 2 | Strategy A (cross-package form) |
| SysML QN lookup (`sysml_qn_lookup(SysMLQN)`) | REFERENCE Step 1 | Strategy B |
| Leaf + scope lookup | REFERENCE Step 2 | -- |
| CHAIN redefinition follow | -- | Strategy C |
| Design attr transitive | Step 3 (both paths) | Strategy D |
| LITERAL :>> fallback | -- | In factory (REQ-MF-06) |
| Self-reference guard | After each step | After each strategy |

The overlap is intentional. Both paths must reach the same answer for the same
reference (REQ-DRA-04). The difference is which strategies are relevant:
- CHAIN redefinition follow is aggregation-specific (`:>>` chains through part hierarchy)
- Scoped-alias lookup is CalcUsage-specific (part-def EXPOSE consumers, REQ-BT-11)
- SysML QN lookup handles REFERENCE bindings (`::` source paths) in both paths,
  and both paths sanitize the lookup key per-segment to match the registration
  key (the Item 7 lockstep, REQ-BT-09) — quoted-owner QNs match on both
- LITERAL fallback is aggregation-specific (`:>> attr = 42.0` defaults)

Both paths use the same typed [OutputRegistry](10-output-registry.md) with typed
lookup methods. No untyped `dict.get()` calls remain. See
[10-output-registry](10-output-registry.md).

### Known Asymmetry: REFERENCE Step 2

The backtracker's REFERENCE Step 2 (leaf + scope lookup) has **no counterpart**
in `resolve_input()`. `_resolve_reference_via_registry()` extracts the leaf from
the `::` path and tries scoped keys built from the consuming usage's parent part
and full consumer scope, which can resolve secondary REFERENCE paths
(e.g., solar_battery `annualized_om|p_net_kw` via Key_F scoped registration).

Strategy B in `resolve_input()` is the sanitized SysML QN lookup only — it has
no leaf + scope fallback. This is **not a consistency violation** — REFERENCE
bindings are a CalcUsage concern (no aggregation term ref contains `::` in any
fixture model). The asymmetry only matters for the backtracker path, which has
its own Step 2 implementation.

---

## Concrete Trace: Same Reference, Both Paths

**Reference**: `"cost_model.total_cost"` in scope `"plant.battery_pack"`.
**Registry**: Key_C `"plant.battery_pack.cost_model.total_cost"` →
canonical `"Design__plant__battery_pack__cost_model__total_cost"`.

**CalcUsage** (backtracker): CHAIN Step 1 scoped lookup →
`"plant.battery_pack.cost_model.total_cost"` → HIT →
`BindingResolution(MODULE_OUTPUT, canonical)`.

**Aggregation** (resolve_input with AGG_STRATEGIES): Strategy A scoped lookup →
`"plant.battery_pack.cost_model.total_cost"` → HIT →
`InputSource(module_output, canonical)`.

**Result**: Identical wiring. Different objects, same answer (REQ-DRA-04).

---

## Cross-Part Wiring: Two Cooperating Resolvers (Item 10)

A cross-part binding — a consumer that references a calc output through a nested part —
is wired by two mechanisms that run at different pipeline stages, not by one lookup. They
stay in their existing homes; nothing new is unified.

**Resolver A — the pre-resolution rewrite (`orchestration/pipeline_builder.py`).** Before
the backtracker runs, `_rewrite_virtual_bindings` rewrites a `part_usage.attr` binding
through the retyped part usage's specialized-def `:>>` redefinition (the three-tier merge,
REQ-VBR-10/REQ-VBR-11, [12-virtual-binding-rewrite](12-virtual-binding-rewrite.md)), and
`_rescue_self_named_bindings` redirects a self-named `in x = x` to its upstream EXPOSE. Both
mutate `source_path` in place, so the backtracker sees an already-corrected binding.

**Resolver B — the backtracker dispatch (`analysis/dependency_backtracker.py`).**
`_resolve_chain_dispatch` Step 1c then resolves the (possibly rewritten) CHAIN binding
against the structured `_scoped_alias` namespace (REQ-BT-11,
[11-analysis-backtracker](11-analysis-backtracker.md)), which
`_register_partdef_expose_scoped_aliases` (`orchestration/pipeline_builder.py`, Step 5.55)
populated per design instance for part-def EXPOSE consumers (REQ-CA-03). Confirmed
multi-hop aliases (REQ-CA-10, [16-computed-attributes](16-computed-attributes.md)) register
in the flat alias registry during the registry builder's Phase-3b confirm pass and are
reached by CHAIN Step 2, not Step 1c.

They compose: Resolver A turns `driver.cost_per_joule` into `driver.meier_cost.gamma` or a
self-named binding into `{instance}.{leaf}`; Resolver B's Step 1c wires the result to the
canonical channel. Each is additive (INV-A) — it only adds a hit where the old ladder fell
through to a fallback entry point.

### Offline == Live Parity (D-C)

Both resolvers must produce the same wiring from a committed snapshot as from a live
extraction (REQ-DRA-04 extended to the offline path). The multi-hop EXPOSE confirm walk is
the risk: M6 serializes the post-confirm `EXPOSE_PURE` state, but the confirm walk gates on
the transient tentative marker, so on reload it would skip the CA and Phase 3's naive
2-segment path would resolve the ambiguous terminal through the first-wins-corrupted flat
`_alias` — the wrong channel, a lying sim. `build_output_registry` reconstructs the
pre-confirm tentative state for exactly the multi-hop candidates before Phase 3
(see [16-computed-attributes](16-computed-attributes.md#multi-hop-expose-tentative-leaf-tag--confirm-pass-req-ca-10)),
so the confirm pass reproduces the live registration order on both paths.

Resolver A splits across the snapshot boundary. The specialized-def rewrite
(`_rewrite_virtual_bindings`) runs at hierarchy-extraction time, so its result is baked
into the recaptured snapshot. The part-def scoped-alias registration and the self-named
rescue need a built registry, so the snapshot path re-runs both on load —
`build_classifier_inputs_from_snapshot` (`snapshot/graph_rebuild.py`) calls
`_register_partdef_expose_scoped_aliases` and `_rescue_self_named_bindings` before the
backtracker, mirroring the live Steps 5.55/5.56.

Alias surfacing has the same both-sites guarantee: `build_computation_graph` receives
`channel_aliases` at both build sites (live `orchestration/pipeline_builder.py` and
snapshot `graph_rebuild.py`), so `ComputationGraph.output_aliases` is populated
identically offline and live rather than silently empty in committed artifacts.

## Data Models

| Model | File | Role |
|-------|------|------|
| `BindingResolution` | `core/models.py` | CalcUsage resolution result (backtracker) |
| `InputSource` | `resolution/models.py` | FORMULA/Agg resolution result (resolve_input) |
| `BindingInfo` | `extraction/usage_extractor.py` | CalcUsage binding input |
| `SumTerm` / `SingletonTerm` / `LocalTerm` | `extraction/data_models.py` | Aggregation term inputs |
| `ResolutionContext` | `resolution/input_resolver.py` | Immutable context for resolve_input() (holds typed OutputRegistry) |
| `OutputRegistry` | `core/output_registry.py` | Typed registries: scoped, SysML QN, alias (both paths) |
| `ScopedKey` | `core/identifier_types.py` | Typed key for scoped/alias registry lookups |
| `ScopedAliasKey` | `core/identifier_types.py` | Typed `(scope, leaf)` key for the structured scoped-alias namespace (CHAIN Step 1c) |
| `SysMLQN` | `core/identifier_types.py` | Typed key for SysML QN registry lookups |
| `CanonicalChannel` | `core/identifier_types.py` | Typed value for all registry lookups |

## Related Documents

- **Architecture**: [03-resolution-overview](03-resolution-overview.md) -- consolidated design and why CalcUsage stays separate
- **Backtracker**: [11-analysis-backtracker](11-analysis-backtracker.md) -- DFS algorithm and CalcUsage type-directed dispatch
- **Resolver**: [04-input-resolver](04-input-resolver.md) -- resolve_input() typed strategies for FORMULA/Agg
- **Factories**: [05-module-factory](05-module-factory.md) -- how each path feeds module construction
- **Registry**: [10-output-registry](10-output-registry.md) -- typed O(1) lookup
- **Scope**: [15-naming-conventions](15-naming-conventions.md) -- ScopedKey format for scoped resolution
- **Data models**: [09-data-models](09-data-models.md) -- BindingResolution, InputSource, BacktrackingResult
