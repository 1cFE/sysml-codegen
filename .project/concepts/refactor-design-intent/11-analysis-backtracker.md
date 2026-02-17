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
| REQ-BT-01 | Every non-literal binding SHALL be resolved via `_resolve_binding_via_registry()` through the [OutputRegistry](10-output-registry.md) | All resolution paths go through this single method |
| REQ-BT-02 | Scoped resolution (Step 0) SHALL be attempted BEFORE unscoped (Step 1) for non-QN source paths | Code order: lines 510-519 precede lines 521-523 |
| REQ-BT-03 | DFS SHALL detect cycles via path tracking and raise `CircularDependencyError` | `if qualified_name in path: raise CircularDependencyError(...)` |
| REQ-BT-04 | Every binding SHALL resolve to exactly one `BindingResolution` — no binding left dangling | Step 4 fallback guarantees resolution for all inputs |
| REQ-BT-05 | `binding_resolutions` key format SHALL be `"{usage_qn}\|{param_name}"` (pipe separator) | All `mapping_key` assignments use `f"{usage.qualified_name}\|{param_name}"` |
| REQ-BT-06 | Topological sort SHALL produce dependency-first ordering or raise on cycles | Kahn's algorithm with cycle detection at line 744 |
| REQ-BT-07 | Self-reference guard SHALL prevent a usage from wiring to its own output | `producing_usage_qn == usage.qualified_name` check at line 538 |

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
```

Key format for `binding_resolutions`: `"{usage_qualified_name}|{param_name}"` (pipe
separator avoids conflict with SysML's `::` delimiter). See [09-data-models](09-data-models.md#analysis-models).

## DFS Tracing Algorithm

`_trace_dependencies(usage, visited, path)` walks the dependency tree:

1. **Cycle detection** — if `qualified_name` is already in `path`, raise `CircularDependencyError`.
2. **Skip visited** — if `qualified_name` is already in `visited`, return empty dict.
3. **Process bindings** — for each [`BindingInfo`](09-data-models.md#extraction-models) on the usage:
   - **LITERAL** bindings become ENTRY_POINTs immediately (no registry lookup).
   - **Non-literal** bindings with a `source_path` go through `_resolve_binding_via_registry()`.
     If the resolution is MODULE_OUTPUT, DFS recurses into the producing usage.
     If ENTRY_POINT, the binding is recorded as an external input.
4. **Unbound params** — every item in `usage.unbound_params` becomes an ENTRY_POINT.

The `path` list is copied on each call (`path = path + [qualified_name]`) to avoid
mutation across sibling branches. The `visited` set is shared across branches to
prevent re-processing.

## The 5-Step Resolution Cascade

`_resolve_binding_via_registry(binding, usage)` is the sole resolution path for
non-literal bindings. It returns a [`BindingResolution`](09-data-models.md#core-models)
with type MODULE_OUTPUT or ENTRY_POINT. Steps are tried in order; the first match wins.

### Step 0: Scoped resolve (primary path for CHAIN bindings)

A CHAIN binding's `source_path` (e.g., `"cost_model.total_cost"`) is a **local reference**
— it only makes sense relative to the consumer's parent scope. Step 0 prepends the consumer
scope to produce a [Key_C-format](15-naming-conventions.md) path for exact match against the
[OutputRegistry](10-output-registry.md):

```python
consumer_scope = _consumer_scope_dotted(usage)   # EQN segments[1:-1] joined with "."
if consumer_scope and source_path and "::" not in source_path:
    scoped_key = f"{consumer_scope}.{source_path}"
    channel = self._output_registry.resolve(scoped_key)
```

For a consumer at `Design__plant__subsys__my_calc`, the scope is `"plant.subsys"`. A
`source_path` of `"other_calc.result"` becomes `"plant.subsys.other_calc.result"` (Key_C
format) — unique by SysML ownership. This is the fix for [The Scope Problem](03-resolution-overview.md#the-scope-problem):
two scopes with identically-named calc usages resolve to different Key_C paths.

Step 0 is skipped for `::` source paths (SysML QN format — handled by Step 1b instead).

### Step 1: Direct registry lookup (unscoped fallback)

```python
channel = self._output_registry.resolve(source_path)
```

Pure exact-match against [Key_A/alias](10-output-registry.md) format. Works when instance
names are globally unique but is **NOT correct** when two scopes contain identically-named
usages. This is why Step 0 runs first (REQ-BT-02).

### Step 1b: SysML QN normalization + retry

If Step 1 fails and `source_path` contains `::` (SysML qualified name format):

```python
# "Package::solar_array::capital_cost" -> "solar_array.capital_cost"
sanitized_part = sanitize_name(parts[-2]).lower()
dotted = f"{sanitized_part}.{parts[-1]}"
channel = self._output_registry.resolve(dotted)
```

Takes the last two `::` segments, sanitizes the parent, and retries as dotted format.

**Self-reference guard** (applies after Steps 0, 1, and 1b): if the resolved channel's
producing usage equals the current usage, the resolution is discarded (set to None). This
prevents a calc from wiring to its own output when an intermediate name happens to match.

### Step 2: REFERENCE secondary resolution (leaf + parent scope)

Only attempted for [`BindingType.REFERENCE`](01-extraction.md#binding-types) bindings
when Steps 0/1/1b fail. `_resolve_reference_via_registry()` extracts the leaf name
from the source path and combines it with the consuming usage's parent part name:

```python
leaf = source_path.rsplit("::", 1)[-1]     # or split on "."
parent_part = usage.qualified_name.split("__")[-2]
channel = registry.resolve(f"{parent_part}.{leaf}")
```

This handles `FeatureReferenceExpression` bindings where the source path is a fully
qualified SysML name but the registry key is scoped to the parent part.

### Step 3: Design attribute resolution (ENTRY_POINT)

`_resolve_to_design_attribute(source_path, usage)` searches the design attributes
dictionary for a matching attribute. Handles three `source_path` formats:

- **Dotted path** (`parent_part.attr_name`) — match on both parent and name.
- **SysML QN** (`Package::Part::attr`) — convert to Python QN and exact match.
- **Bare name** (`attr_name`) — collect candidates, prefer same-file match.

Returns a design attribute qualified name for shared [entry point](06-entry-point-classifier.md) deduplication.

### Step 4: Fallback ENTRY_POINT

If all steps fail, logs a warning and returns an ENTRY_POINT resolution using
`"{usage_qualified_name}__{param_name}"` as the qualified name. This guarantees
REQ-BT-04 — every binding always resolves to something.

## Entry Point Discovery

Entry points are discovered in three places during DFS:

| Source | Where | Example QN |
|--------|-------|------------|
| Unbound param | `usage.unbound_params` loop | `Design__plant__lcoe__discount_rate` |
| Literal binding | `BindingType.LITERAL` branch | `Design__plant__battery__cycles__n_cycles` |
| Unresolvable reference | Steps 3-4 of cascade | `Design__plant__p_fusion` |

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

## Concrete Walkthrough: battery_cost_calc

Consider a pipeline with two calc usages:

```
Design__solar_battery_plant__battery__component_cost   (ComponentCostCalc)
  - bindings: [BindingInfo(param="unit_cost", source_path=None, type=LITERAL, literal_value=150.0),
               BindingInfo(param="capacity", source_path="battery.nameplate_capacity", type=CHAIN)]
  - unbound_params: []

Design__solar_battery_plant__battery__sizing            (BatterySizing)
  - outputs: [nameplate_capacity]
```

The [OutputRegistry](10-output-registry.md) has these keys for the sizing output:
- Key_A: `"sizing.nameplate_capacity"` → canonical `"Design__...__sizing__nameplate_capacity"`
- Alias: `"battery.nameplate_capacity"` → same canonical (from [virtual binding rewrite](12-virtual-binding-rewrite.md))

**DFS trace for `component_cost`:**

1. Enter `_trace_dependencies(component_cost, visited={}, path=[])`.
2. `path = ["Design__...__component_cost"]`, `visited = {"Design__...__component_cost"}`.
3. **Binding 1: `unit_cost`** — `BindingType.LITERAL`. Record as ENTRY_POINT:
   - `binding_resolutions["...component_cost|unit_cost"]` = `BindingResolution(ENTRY_POINT, ...)`.
   - `entry_point_sources["...component_cost__unit_cost"]` = `"150.0"`.
4. **Binding 2: `capacity`** — `BindingType.CHAIN`, `source_path="battery.nameplate_capacity"`.
   - Enter `_resolve_binding_via_registry()`.
   - **Step 0**: consumer scope = `"solar_battery_plant.battery"`. Scoped key =
     `"solar_battery_plant.battery.battery.nameplate_capacity"`. Not in registry — fall through.
   - **Step 1**: `registry.resolve("battery.nameplate_capacity")` → matches alias →
     canonical `"Design__...__sizing__nameplate_capacity"`. Self-reference guard passes.
   - Return `BindingResolution(MODULE_OUTPUT, "Design__...__sizing__nameplate_capacity")`.
   - **DFS recurse** into `sizing` (new branch, no cycle).
5. `sizing` has no upstream bindings — returns `{sizing: sizing_usage}`.

**Dependency graph:** `{component_cost: [sizing], sizing: []}`.

**Topological sort:** `[sizing, component_cost]` — sizing runs first (in-degree 0).

## Related Documents

- **Upstream**: [02-orchestration](02-orchestration.md) — calls `find_required_modules()`, [10-output-registry](10-output-registry.md) — provides the registry queried by all steps
- **Architecture**: [03-resolution-overview](03-resolution-overview.md) — The Scope Problem, [24-dual-resolution-architecture](24-dual-resolution-architecture.md) — why CalcUsage resolution stays here
- **Downstream**: [07-graph-assembly](07-graph-assembly.md) — consumes `BacktrackingResult`, [05-module-factory](05-module-factory.md) — builds modules from resolved bindings
- **Cross-cutting**: [06-entry-point-classifier](06-entry-point-classifier.md) — classifies EPs discovered here, [15-naming-conventions](15-naming-conventions.md) — Key_A/Key_C formats
- **Data models**: [09-data-models](09-data-models.md) — `BacktrackingResult`, `BindingResolution`, `BindingInfo`
