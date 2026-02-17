# 07 -- Graph Assembly

After [resolution](03-resolution-overview.md), [module construction](05-module-factory.md),
and [entry point classification](06-entry-point-classifier.md), every piece of the
pipeline exists as a separate data structure. Graph assembly is the final step: it
sorts the modules into a valid execution order, validates that every wire connects
to something real, and packs everything into the
[`ComputationGraph`](09-data-models.md#resolution-models) -- the single artifact
the [generation layer](08-generation.md) consumes.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-GA-01 | `execution_order` SHALL be a valid topological sort: no module reads from a module that executes later. | `for m in modules: for i in m.inputs: if i.source.source_type == "module_output": assert producer.execution_order < m.execution_order` |
| REQ-GA-02 | If a cycle exists, `_unified_topological_sort` SHALL raise `CircularDependencyError` listing the participating modules. | `len(sorted_names) != len(modules)` triggers `CircularDependencyError(cycle_modules)` |
| REQ-GA-03 | Every `module_output` `producer_channel` SHALL resolve to a declared output channel. | `_validate_channel_references()` raises `ValueError` if any channel is missing |
| REQ-GA-04 | A module SHALL NOT depend on itself, even if its own output channel name appears in its inputs. | Self-reference guard: `dep_module != m.name` (line 1248) |
| REQ-GA-05 | The returned `ComputationGraph` SHALL contain exactly: sorted `modules`, `entry_point_groups`, and `execution_order` names list. | `ComputationGraph` Pydantic model has exactly 3 fields |
| REQ-GA-06 | `execution_order` list SHALL equal `[m.name for m in modules]` (names match module ordering). | Assembly: `execution_order=[m.name for m in modules]` (line 259) |
| REQ-GA-07 | The topological sort SHALL run in O(V + E) time using Kahn's algorithm with `deque`. | Implementation uses `collections.deque` with `popleft()` |

---

## Why topological sorting matters

A [PipelineModule](09-data-models.md#resolution-models) cannot execute until every
module it depends on has already run. If `battery_cost` reads `capacity` from an
upstream module, that upstream module must appear earlier in the execution list.
Topological sorting produces exactly this ordering -- or proves no valid ordering
exists (REQ-GA-02).

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
the fully-constructed list of [PipelineModule](09-data-models.md#resolution-models)
objects -- [CalcUsage, FORMULA, and aggregation](05-module-factory.md) modules
all together.

**1. Build the channel-to-module index.** Map every output channel name back
to the module that produces it.

```python
channel_to_module: dict[str, str] = {}
for m in modules:
    for out in m.outputs:
        channel_to_module[out.channel_name] = m.name
```

**2. Build the dependency graph.** For each module, scan its inputs. If an
input's source type is `"module_output"`, look up the producing module via
the channel index. The self-reference guard (REQ-GA-04) prevents a module from
depending on itself -- this can happen when channel names collide during
[aggregation wiring](13-aggregation-scoping.md).

```python
for m in modules:
    for inp in m.inputs:
        if inp.source.source_type == "module_output" and inp.source.producer_channel:
            dep_module = channel_to_module.get(inp.source.producer_channel)
            if dep_module and dep_module != m.name:  # self-reference guard
                graph[m.name].append(dep_module)
                in_degree[m.name] += 1
```

**3. Invert to get successors.** Kahn's needs to know "which modules become
unblocked when I finish module X?" -- the successor relationship.

```python
successors: dict[str, list[str]] = {m.name: [] for m in modules}
for m_name, deps in graph.items():
    for dep in deps:
        successors[dep].append(m_name)
```

**4. Process the queue.** Start with all zero-in-degree modules (no unmet
dependencies). For each, decrement the in-degree of its successors. When a
successor reaches zero, it joins the queue (REQ-GA-07).

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
    raise CircularDependencyError(
        f"Circular dependency detected among modules: {cycle_modules}. "
        f"Sorted {len(sorted_names)} of {len(modules)} modules."
    )
```

`CircularDependencyError` is a custom exception defined in
`analysis/dependency_backtracker.py`. It means the SysML model has a real
circular dependency (A needs B which needs A) -- a modeling error, not a
tooling bug.

**6. Reassign execution order.** Each module's `execution_order` field is
updated to its position in the sorted list (REQ-GA-06).

```python
name_to_order = {name: i for i, name in enumerate(sorted_names)}
for m in modules:
    m.execution_order = name_to_order[m.name]
```

## Channel reference validation (REQ-GA-03)

After sorting (Step 7), `_validate_channel_references` (Step 8) checks every
wiring connection. For every [`ModuleInput`](09-data-models.md#resolution-models)
with source type `"module_output"`, the referenced `producer_channel` must
exist as an actual [`ModuleOutput`](09-data-models.md#resolution-models)
channel somewhere in the graph.

```python
declared_channels = {out.channel_name for m in modules for out in m.outputs}

for module in modules:
    for input_def in module.inputs:
        if input_def.source.source_type == "module_output":
            channel = input_def.source.producer_channel
            if channel and channel not in declared_channels:
                raise ValueError(
                    f"Module '{module.name}' input '{input_def.param_name}' "
                    f"references unknown channel '{channel}'."
                )
```

This catches wiring bugs -- misspelled channel names, missing modules,
transitive [binding resolution](04-input-resolver.md) failures -- before any
code is generated. Without this, bad wiring would surface as mysterious
runtime errors in TEAx.

## ComputationGraph: the final data model (REQ-GA-05)

The assembly step returns a [`ComputationGraph`](09-data-models.md#resolution-models)
(defined in `resolution/models.py`):

```python
class ComputationGraph(BaseModel):
    modules: list[PipelineModule]             # in execution order
    entry_point_groups: list[ParameterGroup]  # from 06-entry-point-classifier
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

`capacity_calc` runs first (reads from [entry points](06-entry-point-classifier.md)
only). `battery_sizing` reads capacity from `capacity_calc`'s output.
`cost_rollup` reads from both upstream modules.

## What the ComputationGraph contract means

The `ComputationGraph` is the **only** thing the [generation layer](08-generation.md)
should see. Every Jinja2 template -- [pipeline YAML](21-pipeline-yaml-generation.md),
[module wrappers](08-generation.md#b-teax-module-wrappers-modules----generated-by-modulespy),
[schemas](22-output-schema-rules.md),
[JSON templates](08-generation.md#e-json-input-templates-inputs) -- derives its
content from the graph's fields.

**The ideal**: generators never reach back into [extraction-layer](01-extraction.md)
data. Everything needed for code generation is in the graph.

**The current state**: some generators bypass the graph to access
[CalculationDefinitionData](09-data-models.md#extraction-models) directly
(for docstrings, unit annotations, type info). Enriching `PipelineModule` with
these fields is a planned improvement. See [08-generation](08-generation.md#current-gap).

## The duplicated topological sort (post-refactor target)

The codebase currently has two Kahn's implementations:

1. **`DependencyBacktracker._topological_sort`** (analysis layer) --
   operates on `dict[str, list[str]]`, uses `list.pop(0)` which is O(n)
   per pop, making the sort O(V^2).

2. **`_unified_topological_sort`** (resolution layer) -- operates on
   `PipelineModule` objects, uses `deque` for O(1) popleft, O(V + E).

Post-refactor, these converge into one canonical `topological_sort(nodes, edges)`
in `core/graph_algorithms.py`. Both call sites adapt their data into the
`(nodes, edges)` interface. One implementation, one set of tests, one place
to fix bugs.

## Related Documents

- **Upstream**: [05-module-factory](05-module-factory.md) -- produces `PipelineModule` list; [06-entry-point-classifier](06-entry-point-classifier.md) -- produces `ParameterGroup` list
- **Downstream**: [08-generation](08-generation.md) -- consumes `ComputationGraph` for code rendering
- **Registry**: [10-output-registry](10-output-registry.md) -- channel names validated here must match registry entries
- **Data models**: [09-data-models](09-data-models.md) -- `ComputationGraph`, `PipelineModule`, `ModuleInput`, `ModuleOutput`
- **Pipeline context**: [00-pipeline-overview](00-pipeline-overview.md) -- Step 6 in the 7-step pipeline
