# 07 -- Graph Assembly

After resolution, module construction, and entry point classification, every
piece of the pipeline exists as a separate data structure. Graph assembly is
the final step: it sorts the modules into a valid execution order, validates
that every wire connects to something real, and packs everything into the
`ComputationGraph` -- the single artifact the generation layer consumes.

## Why topological sorting matters

A pipeline module cannot execute until every module it depends on has already
run. If `battery_cost` reads `capacity` from an upstream module, that
upstream module must appear earlier in the execution list. Topological
sorting produces exactly this ordering -- or proves no valid ordering exists.

### A concrete example

Consider four modules with these dependencies:

```
  site_prep            capacity
     |                   |
     v                   v
  permitting -------> battery_cost
```

`site_prep` and `capacity` have no upstream dependencies. `permitting`
depends on `site_prep`. `battery_cost` depends on both `capacity` and
`permitting`. After topological sort, one valid execution order is:

```
  [0] site_prep     [1] capacity     [2] permitting     [3] battery_cost
```

Another valid order swaps `site_prep` and `capacity` (they are independent).
Kahn's algorithm produces a deterministic order based on insertion sequence.

## Kahn's algorithm in `_unified_topological_sort`

The implementation lives in `graph_builder.py` (line 1218). It operates on
the fully-constructed list of `PipelineModule` objects -- CalcUsage modules,
computed attribute modules, and aggregation modules all together.

**1. Build the channel-to-module index.** Map every output channel name back
to the module that produces it.

**2. Build the dependency graph.** For each module, scan its inputs. If an
input's source type is `"module_output"`, look up the producing module via
the channel index. That producer is a dependency. A self-reference guard
(`dep_module != m.name`) prevents a module from depending on itself -- this
can happen when channel names collide during aggregation wiring.

```python
for m in modules:
    for inp in m.inputs:
        if inp.source.source_type == "module_output":
            dep_module = channel_to_module.get(inp.source.producer_channel)
            if dep_module and dep_module != m.name:  # self-reference guard
                graph[m.name].append(dep_module)
                in_degree[m.name] += 1
```

**3. Invert to get successors.** Kahn's needs to know "which modules become
unblocked when I finish module X?" -- the successor relationship.

**4. Process the queue.** Start with all zero-in-degree modules (no unmet
dependencies). For each, decrement the in-degree of its successors. When a
successor reaches zero, it joins the queue. Uses `collections.deque` for
O(1) popleft -- total runtime is O(V + E).

```python
queue: deque[str] = deque(
    m_name for m_name, degree in in_degree.items() if degree == 0
)
sorted_names: list[str] = []
while queue:
    current = queue.popleft()
    sorted_names.append(current)
    for successor in successors[current]:
        in_degree[successor] -= 1
        if in_degree[successor] == 0:
            queue.append(successor)
```

**5. Detect cycles.** If `len(sorted_names) != len(modules)`, some modules
could never reach zero in-degree -- they form a cycle.

```python
if len(sorted_names) != len(modules):
    cycle_modules = [m.name for m in modules if m.name not in sorted_names]
    raise CircularDependencyError(...)
```

`CircularDependencyError` means the SysML model has a real circular
dependency (A needs B which needs A). This is a modeling error, not a
tooling bug.

**6. Reassign execution order.** Each module's `execution_order` field is
updated to its position in the sorted list. The list is returned sorted.

## Channel reference validation

After sorting, `_validate_channel_references` checks every wiring
connection. For every `ModuleInput` with source type `"module_output"`, the
referenced `producer_channel` must exist as an actual `ModuleOutput` channel
somewhere in the graph.

```python
declared_channels = {out.channel_name for m in modules for out in m.outputs}

for module in modules:
    for input_def in module.inputs:
        if input_def.source.source_type == "module_output":
            channel = input_def.source.producer_channel
            if channel and channel not in declared_channels:
                raise ValueError(f"...references unknown channel '{channel}'.")
```

This catches wiring bugs -- misspelled channel names, missing modules,
transitive binding resolution failures -- before any code is generated.
Without this, bad wiring would surface as mysterious runtime errors in TEAx.

## ComputationGraph: the final data model

The assembly step returns a `ComputationGraph` (defined in
`resolution/models.py`):

```python
class ComputationGraph(BaseModel):
    modules: list[PipelineModule]             # in execution order
    entry_point_groups: list[ParameterGroup]  # grouped entry points
    execution_order: list[str]                # module names in order
```

### Concrete example

A small solar-battery model might produce:

```
ComputationGraph(
    modules=[
        PipelineModule(name="capacity_calc",  execution_order=0, ...),
        PipelineModule(name="battery_sizing", execution_order=1, ...),
        PipelineModule(name="cost_rollup",    execution_order=2, ...),
    ],
    entry_point_groups=[
        ParameterGroup(name="physics_params", class_name="PhysicsParams",
                       parameters=[ep_energy_density, ep_charge_rate]),
        ParameterGroup(name="system_design",  class_name="SystemDesign",
                       parameters=[ep_target_capacity]),
    ],
    execution_order=["capacity_calc", "battery_sizing", "cost_rollup"],
)
```

`capacity_calc` runs first (reads from entry points only). `battery_sizing`
reads capacity from `capacity_calc`'s output. `cost_rollup` reads from both
upstream modules.

## What the ComputationGraph contract means

The `ComputationGraph` is the **only** thing the generation layer should
see. Every Jinja2 template -- pipeline YAML, module wrappers, schemas, JSON
templates -- derives its content from the graph's fields.

**The ideal**: generators never reach back into extraction-layer data.
Everything needed for code generation is in the graph's modules, their
inputs/outputs, and the entry point groups.

**The current state**: some generators bypass the graph to access extraction
data (for example, docstrings or unit annotations). Enriching
`ComputationGraph` and `PipelineModule` with these fields is a planned
improvement. The direction is clear: every new piece of information the
generators need should be added to the graph, not fetched from extraction.

## The duplicated topological sort (post-refactor target)

The codebase currently has two implementations of Kahn's algorithm:

1. **`DependencyBacktracker._topological_sort`** (analysis layer, line 662)
   -- operates on `dict[str, list[str]]`, uses `list.pop(0)` which is O(n)
   per pop, making the sort O(V^2).

2. **`_unified_topological_sort`** (resolution layer, line 1218) -- operates
   on `PipelineModule` objects, uses `deque` for O(1) popleft, O(V + E).

Post-refactor, these converge into one canonical implementation in
`core/graph_algorithms.py`:

```python
def topological_sort(
    nodes: Iterable[str],
    edges: Iterable[tuple[str, str]],  # (dependency, dependent)
) -> list[str]:
    """Kahn's algorithm. Raises CircularDependencyError on cycles."""
```

Both call sites adapt their data into the `(nodes, edges)` interface. One
implementation, one set of tests, one place to fix bugs.
