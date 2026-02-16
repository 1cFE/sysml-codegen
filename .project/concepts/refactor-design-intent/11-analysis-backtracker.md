# 11 - Analysis: DependencyBacktracker

## Purpose

`DependencyBacktracker` performs depth-first search (DFS) from root calc usages through
all transitive dependencies, producing a `BacktrackingResult` that tells downstream
stages exactly which modules are needed and how every input binding is wired.

Source: `src/sysml_codegen/analysis/dependency_backtracker.py`

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
separator avoids conflict with SysML's `::` delimiter).

## DFS Tracing Algorithm

`_trace_dependencies(usage, visited, path)` walks the dependency tree:

1. **Cycle detection** -- if `qualified_name` is already in `path`, raise `CircularDependencyError`.
2. **Skip visited** -- if `qualified_name` is already in `visited`, return empty dict.
3. **Process bindings** -- for each `BindingInfo` on the usage:
   - **LITERAL** bindings become ENTRY_POINTs immediately (no registry lookup).
   - **Non-literal** bindings with a `source_path` go through `_resolve_binding_via_registry()`.
     If the resolution is MODULE_OUTPUT, DFS recurses into the producing usage.
     If ENTRY_POINT, the binding is recorded as an external input.
4. **Unbound params** -- every item in `usage.unbound_params` becomes an ENTRY_POINT.

The `path` list is copied on each call (`path = path + [qualified_name]`) to avoid
mutation across sibling branches. The `visited` set is shared across branches to
prevent re-processing.

## The 4-Step Resolution Cascade

`_resolve_binding_via_registry(binding, usage)` is the sole resolution path for
non-literal bindings. It returns a `BindingResolution` with type MODULE_OUTPUT or
ENTRY_POINT.

### Step 1: Direct registry lookup

```python
channel = self._output_registry.resolve(source_path)
```

`OutputRegistry.resolve()` is pure exact-match dict lookup (no normalization). If the
binding's `source_path` (e.g., `"solar_array.cost_model.total_cost"`) matches a
registered key, this resolves immediately to a canonical channel name.

### Step 1b: SysML QN normalization + retry

If Step 1 fails and `source_path` contains `::` (SysML qualified name format):

```python
# "Package::solar_array::capital_cost" -> "solar_array.capital_cost"
sanitized_part = sanitize_name(parts[-2]).lower()
dotted = f"{sanitized_part}.{parts[-1]}"
channel = self._output_registry.resolve(dotted)
```

Takes the last two `::` segments, sanitizes the parent, and retries as dotted format.

Both Step 1 and 1b include a **self-reference guard**: if the resolved channel's
producing usage equals the current usage, the resolution is discarded (set to None).

### Step 2: REFERENCE secondary resolution (leaf + parent scope)

Only attempted for `BindingType.REFERENCE` bindings when Steps 1/1b fail.
`_resolve_reference_via_registry()` extracts the leaf name from the source path, combines
it with the consuming usage's parent part name, and resolves:

```python
leaf = source_path.rsplit("::", 1)[-1]     # or split on "."
parent_part = usage.qualified_name.split("__")[-2]
channel = registry.resolve(f"{parent_part}.{leaf}")
```

This handles FeatureReferenceExpression bindings where the source path is a fully
qualified SysML name but the registry key is scoped to the parent part.

### Step 3: Design attribute resolution (ENTRY_POINT)

`_resolve_to_design_attribute(source_path, usage)` searches the design attributes
dictionary for a matching attribute. Handles three source_path formats:

- **Dotted path** (`parent_part.attr_name`) -- match on both parent and name.
- **SysML QN** (`Package::Part::attr`) -- convert to Python QN and exact match.
- **Bare name** (`attr_name`) -- collect candidates, prefer same-file match.

Returns a design attribute qualified name for shared entry point deduplication.

### Step 4: Fallback ENTRY_POINT

If all steps fail, logs a warning and returns an ENTRY_POINT resolution using
`"{usage_qualified_name}__{param_name}"` as the qualified name. This ensures every
binding always resolves to something -- no binding is left dangling.

## BindingResolution Model

```python
class BindingResolution(BaseModel):          # from core/models.py
    resolution_type: BindingResolutionType   # ENTRY_POINT | MODULE_OUTPUT
    qualified_name: str                      # Target identifier (entry point QN or channel PQN)
    source_path: str | None                  # Original binding source (for debugging)
    is_transitive: bool                      # True if resolved through EXPOSE pattern
```

This is the single source of truth consumed by `graph_builder.build_computation_graph()`.

## Entry Point Discovery

Entry points are discovered in three places during DFS:

| Source | Where | Example QN |
|--------|-------|------------|
| Unbound param | `usage.unbound_params` loop | `Design__plant__lcoe__discount_rate` |
| Literal binding | `BindingType.LITERAL` branch | `Design__plant__battery__cycles__n_cycles` |
| Unresolvable reference | Steps 3-4 of cascade | `Design__plant__p_fusion` |

`entry_point_sources` maps each entry point QN to either `str(literal_value)` (for
literals) or the original `source_path` (for design attribute matching downstream).

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

The OutputRegistry has key `"battery.nameplate_capacity"` mapped to canonical channel
`"Design__solar_battery_plant__battery__sizing__nameplate_capacity"`.

**DFS trace for `component_cost`:**

1. Enter `_trace_dependencies(component_cost, visited={}, path=[])`.
2. `path = ["Design__...__component_cost"]`, `visited = {"Design__...__component_cost"}`.
3. **Binding 1: `unit_cost`** -- `BindingType.LITERAL`. Record as ENTRY_POINT:
   - `binding_resolutions["...component_cost|unit_cost"]` = `BindingResolution(ENTRY_POINT, "...component_cost__unit_cost")`.
   - `entry_point_sources["...component_cost__unit_cost"]` = `"150.0"`.
4. **Binding 2: `capacity`** -- `BindingType.CHAIN`, `source_path="battery.nameplate_capacity"`.
   - Enter `_resolve_binding_via_registry()`.
   - **Step 1**: `registry.resolve("battery.nameplate_capacity")` returns channel
     `"Design__...__sizing__nameplate_capacity"`. Self-reference guard passes (different usage).
   - Return `BindingResolution(MODULE_OUTPUT, "Design__...__sizing__nameplate_capacity")`.
   - `_find_usage_for_channel()` extracts EQN `"Design__...__sizing"` and finds the `BatterySizing` usage.
   - **DFS recurse** into `sizing` (new branch, no cycle).
5. `sizing` has no upstream bindings -- returns `{sizing: sizing_usage}`.
6. `component_cost` returns `{component_cost: ..., sizing: ...}`.

**Dependency graph:** `{component_cost: [sizing], sizing: []}`.

**Topological sort:** `[sizing, component_cost]` -- sizing runs first because it has
in-degree 0; component_cost depends on it.

**Final BacktrackingResult:**
- `required_usages`: `[sizing, component_cost]`
- `entry_points`: `{"...component_cost__unit_cost"}`
- `entry_point_sources`: `{"...component_cost__unit_cost": "150.0"}`
- `binding_resolutions`: two entries (one MODULE_OUTPUT for capacity, one ENTRY_POINT for unit_cost)
