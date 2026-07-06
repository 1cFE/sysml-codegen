# 11 - Analysis: DependencyBacktracker

## Purpose

`DependencyBacktracker` performs depth-first search (DFS) from root calc usages through
all transitive dependencies, producing a [`BacktrackingResult`](09-data-models.md#analysis-models)
that tells downstream stages exactly which modules are needed and how every input binding
is wired. This is the **CalcUsage resolution path** — one of the two resolution architectures
described in [24-dual-resolution-architecture](24-dual-resolution-architecture.md). The
backtracker MUST resolve bindings during DFS because the resolution result (MODULE_OUTPUT
vs ENTRY_POINT) determines whether to recurse or stop.

Source: `src/sysml_codegen/analysis/dependency_backtracker.py`

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-BT-01 | Every non-literal binding SHALL be resolved via `_resolve_binding_via_registry()` through the typed [OutputRegistry](10-output-registry.md) | All resolution paths go through this single method |
| REQ-BT-02 | Resolution SHALL dispatch on binding format: CHAIN bindings (no `::` in source_path) query scoped then alias registries; REFERENCE bindings (`::` in source_path) query SysML QN then scoped registries | Code branches on `"::" in source_path` |
| REQ-BT-03 | DFS SHALL detect cycles via path tracking and raise `CircularDependencyError` | `if qualified_name in path: raise CircularDependencyError(...)` |
| REQ-BT-04 | Every binding SHALL resolve to exactly one `BindingResolution` — no binding left dangling | Fallback guarantees resolution for all inputs |
| REQ-BT-05 | `binding_resolutions` key format SHALL be `"{usage_qn}\|{param_name}"` (pipe separator) | All `mapping_key` assignments use `f"{usage.qualified_name}\|{param_name}"` |
| REQ-BT-06 | Topological sort SHALL produce dependency-first ordering or raise on cycles | Kahn's algorithm with cycle detection |
| REQ-BT-07 | Self-reference guard SHALL prevent a usage from wiring to its own output | `producing_usage_qn == usage.qualified_name` check after each lookup |
| REQ-BT-08 | Resolution SHALL use type-directed dispatch on `BindingType` format to select the correct typed registry. CHAIN bindings query `scoped_lookup(ScopedKey)` then `alias_lookup(ScopedKey)`. REFERENCE bindings query `sysml_qn_lookup(SysMLQN)` then `scoped_lookup(ScopedKey)`. | Dispatch branches verified; see [10-output-registry](10-output-registry.md) Design Rationale |
| REQ-BT-09 | The FORMULA `::`-QN REFERENCE path SHALL per-segment sanitize (`sanitize_qualified_name`) before comparison/lookup so a quoted-owner QN matches the sanitized design-attribute QN (Bug A; six-site lockstep flip, INV-1) | `test_matcher_fixes_item7.py`, `test_dual_resolution.py` |
| REQ-BT-10 | A design attribute owned by a part **def** (empty `parent_part`) SHALL match its binding via a leaf-unique fallback over design-part attributes (calc-def I/O excluded), returning a QN only when exactly one candidate exists, else None (Bug B; INV-2, no cross-wire) | `test_matcher_fixes_item7.py` |
| REQ-BT-11 | CHAIN dispatch SHALL, after both scoped steps and before the unscoped alias step, query the structured `_scoped_alias` namespace with `ScopedAliasKey((prefix, leaf))` split from `source_path` at the last dot — trying the consumer-scope-prefixed key `(consumer_scope + "." + prefix, leaf)` first (D-D sibling disambiguation), then the bare `(prefix, leaf)`. Additive only (INV-A): it adds a hit where the ladder fell through, never overrides one. | Sibling disambiguation: `test_sibling_channel_ambiguity.py::test_chamber_power_disambiguated_to_chamber_b`; part-def EXPOSE consumer: `test_wi014_toy.py::test_wi014_toy_shape_a_resolves_offline_via_scoped_alias` |

## BacktrackingResult Output Model

```python
class BacktrackingResult(BaseModel):
    required_usages: list[CalcUsageData]       # Topologically sorted (deps first)
    dependency_graph: dict[str, list[str]]      # qualified_name -> [dep qualified_names]
    entry_points: set[str]                      # External input qualified names
    entry_point_sources: dict[str, str]         # qname -> source path or literal value
    binding_resolutions: dict[str, BindingResolution]  # SINGLE SOURCE OF TRUTH
    phantom_report: PhantomDetectionReport      # Suspected phantom entry points
    trace_log: list[str]                        # Debug trace of resolution steps
    binding_to_entry_point: dict[str, str]      # DEPRECATED - use binding_resolutions
    fallback_entry_points: set[str]             # Step-4 fall-through entry point QNs
```

Key format for `binding_resolutions`: `"{usage_qualified_name}|{param_name}"` (pipe
separator avoids conflict with SysML's `::` delimiter). See [09-data-models](09-data-models.md#analysis-models).

`fallback_entry_points` records the bound bindings that matched no resolution strategy
and no design attribute (Step 4 of both dispatch paths). The V11 params-coverage
collector (`collect_uncovered_params`, `resolution/graph_builder.py`) intersects this
set with valueless + wired entry points to find genuinely uncovered pipeline inputs
at the generation boundary.

## DFS Tracing Algorithm

`_trace_dependencies(usage, visited, path)` walks the dependency tree:

1. **Cycle detection** — if `qualified_name` is already in `path`, raise `CircularDependencyError`.
2. **Skip visited** — if `qualified_name` is already in `visited`, return empty dict.
3. **Process bindings** — for each [`BindingInfo`](09-data-models.md#extraction-models) on the usage:
   - **LITERAL** bindings become ENTRY_POINTs immediately (no registry lookup).
   - **EXPRESSION** bindings (`source_path=None`, `BindingType.EXPRESSION`) are handled as
     ENTRY_POINTs with a warning. These represent inline operator expressions (e.g., `in x = a + b`)
     where the extractor cannot decompose the expression into a single source path. The backtracker
     logs a warning and creates an ENTRY_POINT resolution. No registry lookup is attempted.
     Zero EXPRESSION bindings occur in natural fixture models — covered by `expression_binding_probe`.
   - **Non-literal** bindings with a `source_path` go through `_resolve_binding_via_registry()`.
     If the resolution is MODULE_OUTPUT, DFS recurses into the producing usage.
     If ENTRY_POINT, the binding is recorded as an external input.
4. **Unbound params** — every item in `usage.unbound_params` becomes an ENTRY_POINT.

The `path` list is copied on each call (`path = path + [qualified_name]`) to avoid
mutation across sibling branches. The `visited` set is shared across branches to
prevent re-processing.

## Type-Directed Resolution Dispatch

`_resolve_binding_via_registry(binding, usage)` is the sole resolution path for
non-literal bindings. It returns a [`BindingResolution`](09-data-models.md#core-models)
with type MODULE_OUTPUT or ENTRY_POINT. The dispatch is determined by the binding's
`source_path` format (REQ-BT-08):

### CHAIN Bindings (no `::` in source_path)

CHAIN bindings use dotted local paths (e.g., `"cost_model.total_cost"`). These are
scope-relative references. Resolution constructs a typed `ScopedKey` and queries
the appropriate registries:

```
Step 1: Consumer-scoped lookup (primary path)
  ScopedKey(consumer_scope + "." + source_path) → scoped registry
  → CanonicalChannel or None

Step 1b: Direct scoped lookup (no consumer-scope prefix)
  ScopedKey(source_path) → scoped registry
  → CanonicalChannel or None (covers FORMULA outputs registered as owning_part.attr)

Step 1c: Structured scoped-alias lookup (REQ-BT-11)
  Split source_path at the last dot → ScopedAliasKey((prefix, leaf))
  → _scoped_alias namespace, consumer-scope-prefixed key first, then bare
  → CanonicalChannel or None (part-def EXPOSE, sibling disambiguation — see below)

Step 2: Alias lookup (cross-package path)
  ScopedKey(source_path) → alias registry
  → CanonicalChannel or None (handles EXPOSE_PURE cross-package refs)

Step 3: Design attribute resolution
  Match source_path to DesignAttributeData
  → ENTRY_POINT

Step 4: Fallback entry point
  → ENTRY_POINT (DEBUG line; QN recorded in fallback_entry_points)
```

**Step 1** prepends the consumer scope to produce a
[ScopedKey](15-naming-conventions.md)-format path for exact match against the
scoped registry:

```python
consumer_scope = _consumer_scope_dotted(usage)   # EQN segments[1:-1] joined with "."
if consumer_scope and source_path:
    scoped_key = ScopedKey(f"{consumer_scope}.{source_path}")
    channel = self._output_registry.scoped_lookup(scoped_key)
```

For a consumer at `Design__plant__subsys__my_calc`, the scope is `"plant.subsys"`. A
`source_path` of `"other_calc.result"` becomes `ScopedKey("plant.subsys.other_calc.result")`
— unique by SysML ownership. This is the fix for [The Scope Problem](03-resolution-overview.md#the-scope-problem).

**Step 1b** retries the scoped registry with the `source_path` as-is, no consumer-scope
prefix. This covers FORMULA outputs registered under their owning part
(`owning_part.attr`), which a consumer in a different scope references directly.

**Step 2** tries the alias registry for cross-package references. When the consumer
and producer are in different SysML packages, Step 1 structurally cannot work
(prepending the consumer's scope produces a key that will never exist). The alias
registry contains Phase 3 EXPOSE_PURE aliases that bridge this gap:

```python
channel = self._output_registry.alias_lookup(ScopedKey(source_path))
```

#### Structured Scoped-Alias Lookup — Step 1c (REQ-BT-11)

Between the scoped steps and the unscoped alias step (Step 2) sits a structured lookup
against the `_scoped_alias` namespace — a tuple-keyed registry (`ScopedAliasKey =
(prefix, leaf)`) distinct from the flat `_alias` dict. It reaches two things a flat
string key cannot construct:

- **Part-def EXPOSE consumers** (shape A). `_register_partdef_expose_scoped_aliases`
  writes `(instance_path, leaf) → channel` per design instance (Item 10 #4,
  [16-computed-attributes](16-computed-attributes.md#part-def-expose-scoped-aliases-shape-a-req-ca-03)).
  A consumer of `demo_plant.total_cost` splits to `("demo_plant", "total_cost")` and
  hits it. Registration and lookup derive the tuple from the *same* last-dot split, so
  they meet by construction.

- **Sibling disambiguation** (D-D). Two same-type siblings both expose `power`, so #4
  registers `("twin_plant.chamber_a", "power")` and `("twin_plant.chamber_b", "power")`.
  The consumer binds `chamber_b.power`; the bare split `("chamber_b", "power")` misses
  the instance-scoped key, and the def-level `power` name first-wins-collides. Step 1c
  therefore tries the consumer-scope-prefixed key first — `("twin_plant.chamber_b",
  "power")` — mirroring Step 1's `consumer_scope + "." + source_path` prepend, then
  falls back to the bare key.

```python
if "." in source_path:
    prefix, leaf = source_path.rsplit(".", 1)
    channel = None
    if consumer_scope:
        channel = self._output_registry.scoped_alias_lookup(
            ScopedAliasKey((f"{consumer_scope}.{prefix}", leaf)))
    if channel is None:
        channel = self._output_registry.scoped_alias_lookup(
            ScopedAliasKey((prefix, leaf)))
```

Ordered after both scoped steps and before Step 2, this is additive (INV-A): it only
adds a hit where the ladder previously fell through to a fallback entry point. The
self-reference guard applies as in every other step.

### REFERENCE Bindings (`::` in source_path)

REFERENCE bindings use SysML qualified names (e.g., `"AttrExprProbeDesign::probe_design::area"`).
These are globally unique identifiers. Resolution constructs typed keys:

```
Step 1: SysML QN lookup (primary path)
  SysMLQN(sanitize_qualified_name(source_path)) → SysML QN registry
  → CanonicalChannel or None

Step 2: Leaf + consumer-scope lookup (secondary path)
  Extract leaf from source_path; pair with the consumer's parent part,
  then with the full consumer scope
  → scoped registry, then alias registry (each key)
  → CanonicalChannel or None

Step 3: Design attribute resolution
  → ENTRY_POINT

Step 4: Fallback entry point
  → ENTRY_POINT (DEBUG line; QN recorded in fallback_entry_points)
```

**Step 1** per-segment sanitizes the `::` source_path via `sanitize_qualified_name`
before wrapping it as a `SysMLQN` (REQ-BT-09, Bug A fix). The registry key was
registered per-segment sanitized, so the lookup key must be sanitized in lockstep
(INV-1) — otherwise a quoted-owner QN like `Lib::'Magnet Part'::attr` never matches:

```python
channel = self._output_registry.sysml_qn_lookup(
    SysMLQN(sanitize_qualified_name(source_path))
)
```

**Step 2** (if Step 1 misses) delegates to `_resolve_reference_via_registry`. It
extracts only the leaf of the source_path and pairs it with scopes derived from the
*consumer's* qualified name — first the immediate parent part (EQN `segments[-2]`),
then the full consumer scope. Each candidate `ScopedKey` is tried against the scoped
registry, then the alias registry:

```python
leaf = source_path.rsplit("::", 1)[-1]
# Try ScopedKey(f"{parent_part}.{leaf}"), then ScopedKey(f"{consumer_scope}.{leaf}"),
# each via scoped_lookup() then alias_lookup()
```

> **Limitation**: Step 2 discards the source path's owner segments entirely — it
> keeps only the leaf and assumes the producer sits in the consumer's own parent
> part or scope. A `::` QN pointing into a different branch of the hierarchy will
> not match here and falls to Steps 3-4. This is acceptable for current models:
> idiomatic SysML v2 cross-scope references use `import` + `.` chain (CHAIN
> binding), not deep `::` paths (REFERENCE). Deep REFERENCE bindings are
> non-idiomatic and may only arise from programmatic model generation.

### Self-Reference Guard

After each lookup step returns a channel, the resolver calls
`_is_self_reference(channel, usage)` — it checks whether the channel's producing-usage
prefix equals the consuming usage's qualified name:

```python
producing_usage_qn = channel.rsplit("__", 1)[0]
if producing_usage_qn == usage.qualified_name:
    # discard hit (logged at DEBUG), continue down the ladder
```

This prevents a calc from wiring to its own output when a name happens to match.

### Design Attribute Resolution (Step 3, both paths)

`_resolve_to_design_attribute(source_path, usage)` searches the design attributes
dictionary for a matching attribute. Handles three `source_path` formats:

- **Dotted path** (`parent_part.attr_name`) — exact match on both parent and name
  first. If that misses, a **leaf-unique fallback** (REQ-BT-10, Bug B fix): a design
  attribute owned by a part *def* extracts with an empty `parent_part`, so the exact
  parent match can never fire for it. The fallback gathers design-part attributes
  carrying the leaf name — excluding calc-def I/O attributes via `_is_calc_def_owned`
  — and returns a QN only when exactly one candidate exists. Zero or multiple
  candidates return None (fall to Step 4, kept loud; INV-2, no cross-wire). The
  calc-def exclusion is what keeps a dotted reference to a calc *output* unresolved
  and visible instead of silently cross-wired into a DESIGN_ATTRIBUTE entry point.
- **SysML QN** (`Package::Part::attr`) — per-segment sanitize via
  `sanitize_qualified_name`, then exact match against the attribute's qualified name
  (REQ-BT-09, Bug A fix). A bare `::`→`__` swap would keep the quotes in a
  quoted-owner QN and never match.
- **Bare name** (`attr_name`) — collect candidates, prefer same-file match; if
  still ambiguous, use the first candidate and log a WARNING.

Returns a design attribute qualified name for shared [entry point](06-entry-point-classifier.md) deduplication.

### Fallback (Step 4, both paths)

If all steps fail, the resolver logs a DEBUG line (`"Registry unresolved: ..."`) and
returns an ENTRY_POINT resolution using `"{usage_qualified_name}__{param_name}"` as
the qualified name. This guarantees REQ-BT-04 — every binding always resolves to
something.

The per-binding line is DEBUG, not WARNING (Item 7): it fired per binding and was the
primary benign noise. The fall-through QN is recorded in `fallback_entry_points`, and
the operator-facing digest moved to the generation boundary
(`_reconcile_params_coverage`, `cli/__init__.py`): one WARNING reconciliation summary
for the unwired remainder, and a V11 hard error (via `collect_uncovered_params`) for
any fell-through, valueless entry point that the pipeline wiring still references.

## Entry Point Discovery

Entry points are discovered in three places during DFS:

| Source | Where | Example QN |
|--------|-------|------------|
| Unbound param | `usage.unbound_params` loop | `Design__plant__lcoe__discount_rate` |
| Literal binding | `BindingType.LITERAL` branch | `Design__plant__battery__cycles__n_cycles` |
| Unresolvable reference | Steps 3-4 of both paths | `Design__plant__p_fusion` |

`entry_point_sources` maps each entry point QN to either `str(literal_value)` (for
literals) or the original `source_path` (for design attribute matching in
[entry point classification](06-entry-point-classifier.md)).

## Topological Sort

`_topological_sort(graph)` implements Kahn's algorithm:

1. Compute in-degree for each node (count of in-graph dependencies).
2. Seed a queue with all zero-in-degree nodes.
3. Pop from queue, append to result, decrement in-degrees of dependents.
4. If `len(result) != len(graph)`, a cycle exists (raises `CircularDependencyError`).

Current implementation uses `queue.pop(0)` which is O(n) per pop, making the overall
sort O(n^2) for n modules. Adequate for typical pipeline sizes (< 50 modules).

## Concrete Walkthrough: CHAIN Resolution

Consider a pipeline with two calc usages:

```
Design__solar_battery_plant__battery__component_cost   (ComponentCostCalc)
  - bindings: [BindingInfo(param="unit_cost", source_path=None, type=LITERAL, literal_value=150.0),
               BindingInfo(param="capacity", source_path="sizing.nameplate_capacity", type=CHAIN)]
  - unbound_params: []

Design__solar_battery_plant__battery__sizing            (BatterySizing)
  - outputs: [nameplate_capacity]
```

The typed [OutputRegistry](10-output-registry.md) has these entries:

- Scoped: `ScopedKey("solar_battery_plant.battery.sizing.nameplate_capacity")` → `CanonicalChannel("Design__...__sizing__nameplate_capacity")`
- Alias: `ScopedKey("battery.nameplate_capacity")` → same canonical (from CHAIN redefinition)

**DFS trace for `component_cost`:**

1. Enter `_trace_dependencies(component_cost, visited={}, path=[])`.
2. `path = ["Design__...__component_cost"]`, `visited = {"Design__...__component_cost"}`.
3. **Binding 1: `unit_cost`** — `BindingType.LITERAL`. Record as ENTRY_POINT:
   - `binding_resolutions["...component_cost|unit_cost"]` = `BindingResolution(ENTRY_POINT, ...)`.
   - `entry_point_sources["...component_cost__unit_cost"]` = `"150.0"`.
4. **Binding 2: `capacity`** — `BindingType.CHAIN`, `source_path="sizing.nameplate_capacity"`.
   - Enter `_resolve_binding_via_registry()`.
   - No `::` in source_path → **CHAIN path**.
   - **Step 1**: consumer scope = `"solar_battery_plant.battery"`. Scoped key =
     `ScopedKey("solar_battery_plant.battery.sizing.nameplate_capacity")`.
     `scoped_lookup()` → `CanonicalChannel("Design__...__sizing__nameplate_capacity")`. **HIT.**
   - Self-reference guard passes (different usage).
   - Return `BindingResolution(MODULE_OUTPUT, "Design__...__sizing__nameplate_capacity")`.
   - **DFS recurse** into `sizing` (new branch, no cycle).
5. `sizing` has no upstream bindings — returns `{sizing: sizing_usage}`.

**Dependency graph:** `{component_cost: [sizing], sizing: []}`.

**Topological sort:** `[sizing, component_cost]` — sizing runs first (in-degree 0).

## Concrete Walkthrough: Cross-Package CHAIN Resolution

From catf_mfe: consumer in `CATFMFEMagnets` package, producer in `CATFMFERadialBuild`:

```
Consumer:  CATFMFEMagnets__catf_tf_system__cryo_load
  consumer_scope = "catf_tf_system"
  source_path    = "catf_radial_build.magnet_surface_area"
```

**CHAIN path:**

- **Step 1**: `ScopedKey("catf_tf_system.catf_radial_build.magnet_surface_area")`
  → `scoped_lookup()` → None (catf_radial_build is NOT a child of catf_tf_system)
- **Steps 1b/1c**: direct scoped key and structured scoped-alias keys → None
  (no FORMULA registration, no part-def EXPOSE for this producer)
- **Step 2**: `ScopedKey("catf_radial_build.magnet_surface_area")`
  → `alias_lookup()` → `CanonicalChannel(...)` via Phase 3 EXPOSE_PURE alias. **HIT.**

This is why the alias registry exists: cross-package references where Step 1
structurally cannot work.

## Concrete Walkthrough: REFERENCE Resolution

From attr_expr_probe:

```
Consumer:  AttrExprProbeDesign__probe_design__scale_calc
  source_path = "AttrExprProbeDesign::probe_design::area"
```

**REFERENCE path** (`::` detected):

- **Step 1**: `SysMLQN("AttrExprProbeDesign::probe_design::area")`
  → `sysml_qn_lookup()` → `CanonicalChannel(...)` via Phase 1c SysML QN key. **HIT.**

No normalization needed — the SysML QN key is in its own typed registry.

## Related Documents

- **Upstream**: [02-orchestration](02-orchestration.md) — calls `find_required_modules()`, [10-output-registry](10-output-registry.md) — provides the typed registry queried by all steps
- **Architecture**: [03-resolution-overview](03-resolution-overview.md) — The Scope Problem, [24-dual-resolution-architecture](24-dual-resolution-architecture.md) — why CalcUsage resolution stays here
- **Downstream**: [07-graph-assembly](07-graph-assembly.md) — consumes `BacktrackingResult`, [05-module-factory](05-module-factory.md) — builds modules from resolved bindings
- **Cross-cutting**: [06-entry-point-classifier](06-entry-point-classifier.md) — classifies EPs discovered here, [15-naming-conventions](15-naming-conventions.md) — ScopedKey/CanonicalChannel formats
- **Data models**: [09-data-models](09-data-models.md) — `BacktrackingResult`, `BindingResolution`, `BindingInfo`
