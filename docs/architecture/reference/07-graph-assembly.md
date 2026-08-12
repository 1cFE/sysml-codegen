# 07 -- Graph Assembly

> **Status: historical.** `build_computation_graph()` and its helpers lived in
> `resolution/graph_builder.py`, **deleted** by the Item 7 retirement (2026-08-12, `19072ad` /
> `82c7951` / `882fc8d` / `3071fba`).
>
> **The subject survives; the owner does not.** The shipped route still topologically sorts the
> modules, still refuses a producer reference with no output, and still packs one
> `ComputationGraph` — projection does it (`elaboration/project.py`, `_topological_modules` and
> `_claim_channel`). The V11 params-coverage check is unchanged and still runs at the generation
> boundary, from `resolution/uncovered_params.py`, which is in the tree.
>
> Everything below is retained as the record of the deleted design. It is accurate about the
> code that was removed and is **not a description of what the product does**. For that, read
> [00-pipeline-overview](00-pipeline-overview.md).
>
> This document also cites `core/graph_algorithms.py`, which has never existed in this tree.
> Recorded rather than fixed: it predates the recovery and needs an owner.

After [resolution](03-resolution-overview.md), [module construction](05-module-factory.md),
and [entry point classification](06-entry-point-classifier.md), every piece of the
pipeline exists as a separate data structure. Graph assembly is the final step: it
sorts the modules into a valid execution order, validates that every wire connects
to something real, surfaces EXPOSE_PURE modeler names as output aliases, and packs
everything into the
[`ComputationGraph`](09-data-models.md#resolution-models) -- the single artifact
the [generation layer](08-generation.md) consumes. Assembly also carries the
Step-4 fall-through entry points onto the graph so the generation boundary can
run the params-coverage check (V11) without reaching back into analysis data.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-GA-01 | `execution_order` SHALL be a valid topological sort: no module reads from a module that executes later. | `for m in modules: for i in m.inputs: if i.source.source_type == "module_output": assert producer.execution_order < m.execution_order` |
| REQ-GA-02 | If a cycle exists, `_unified_topological_sort` SHALL raise `CircularDependencyError` listing the participating modules. | `len(sorted_names) != len(modules)` triggers `CircularDependencyError(cycle_modules)` |
| REQ-GA-03 | Every `module_output` `producer_channel` SHALL resolve to a declared output channel. | `_validate_channel_references()` raises `ValueError` if any channel is missing |
| REQ-GA-04 | A module SHALL NOT depend on itself, even if its own output channel name appears in its inputs. | Self-reference guard: `dep_module != m.name` in `_unified_topological_sort` |
| REQ-GA-05 | The returned `ComputationGraph` SHALL contain exactly the reviewed field set: sorted `modules`, `entry_point_groups`, `execution_order`, in-memory `fallback_entry_points` (REQ-GA-08), serialized `output_aliases` (REQ-DM-09); any field-set change is a deliberate reviewed rev. | Exact-set conformance test flips red on any field change -- see the model section below |
| REQ-GA-06 | `execution_order` list SHALL equal `[m.name for m in modules]` (names match module ordering). | Assembly: `execution_order=[m.name for m in modules]` in `build_computation_graph` |
| REQ-GA-07 | The topological sort SHALL run in O(V + E) time using Kahn's algorithm with `deque`. | Implementation uses `collections.deque` with `popleft()` |
| REQ-GA-08 | A two-layer params-coverage check SHALL exist: a pure collector `collect_uncovered_params(graph)` returning the wired fell-through-valueless violations (sibling to REQ-GA-03), and an always-strict generation boundary raising V11 on any violation. `ComputationGraph.fallback_entry_points` (in-memory, `exclude=True`) feeds it. | `test_uncovered_params.py`, `test_graph_assembly.py`, `test_data_models.py` |

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

The implementation is `_unified_topological_sort` in
`src/sysml_codegen/resolution/graph_builder.py`. It operates on
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
                if dep_module not in graph[m.name]:  # dedupe repeated edges
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
transitive [binding resolution](04-producer-resolution.md) failures -- before any
code is generated. Without this, bad wiring would surface as mysterious
runtime errors in TEAx.

## Step 8.5: Surfacing EXPOSE names as output aliases (REQ-DM-09)

After channel validation, `_build_output_aliases` (called at the end of
`build_computation_graph` in `src/sysml_codegen/resolution/graph_builder.py`)
turns every resolvable EXPOSE_PURE modeler name into an
[`OutputAlias`](09-data-models.md#resolution-models) on the graph. An alias
says: this canonical output channel also carries a modeler-chosen name on a
specific instance, and the generated pipeline should write its capture file
under that name (`{instance_path}__{alias_name}.json` via the
`OutputAlias.output_filename` property in `resolution/models.py`).

Two sources feed it, matching the two EXPOSE shapes:

- **Shape A (part-def EXPOSE)**: read from the registry's structured
  `_scoped_alias` namespace, already expanded per design instance and keyed
  `(instance_path, python_name) -> channel`.
- **Shape B (part-usage EXPOSE)**: read from the `expose_pure`
  `ChannelAlias` objects threaded in via the `channel_aliases` argument, each
  resolved to its canonical channel through the registry.

Both build sites must thread `channel_aliases`, and both do: the live path
(`build_pipeline_context` in `src/sysml_codegen/orchestration/pipeline_builder.py`)
and the snapshot path (`build_full_graph_from_snapshot` in
`src/sysml_codegen/snapshot/graph_rebuild.py`). If a caller omitted it, shape B
would silently not surface -- which is why the parameter is wired at both sites
rather than defaulted away.

Two invariants hold on the result:

- **Every alias points at a real output.** An alias whose channel is not a
  declared graph output is a wiring regression on a full run
  (`include_all=True`, raises `ValueError`); on a targeted run the channel may
  be legitimately pruned, so the alias is dropped with a DEBUG log.
- **Deterministic order.** The list is stable-sorted by
  `(instance_path, alias_name)` so regeneration never produces an
  ordering-only diff in committed baselines.

The alias list is consumed by [pipeline YAML
generation](21-pipeline-yaml-generation.md) (`_build_alias_filename_map` /
`_build_exit_points` in `src/sysml_codegen/generation/pipeline.py`): the exit
point stays keyed by the canonical channel; only its capture filename changes.

## ComputationGraph: the final data model (REQ-GA-05)

The assembly step returns a [`ComputationGraph`](09-data-models.md#resolution-models)
(defined in `resolution/models.py`):

```python
class ComputationGraph(BaseModel):
    modules: list[PipelineModule]             # in execution order
    entry_point_groups: list[ParameterGroup]  # from 06-entry-point-classifier
    execution_order: list[str]                # module names in order
    fallback_entry_points: set[str] = Field(default_factory=set, exclude=True)
    output_aliases: list[OutputAlias] = Field(default_factory=list)
```

The three core fields (REQ-GA-05) describe the pipeline itself. The two later
additions differ deliberately in serialization:

- `fallback_entry_points` is **in-memory only** (`exclude=True`). It records
  the QNs of Step-4 fall-through entry points -- bound bindings that matched no
  resolution strategy and no design attribute -- so the params-coverage check
  (below) can run over the graph alone. It is an analysis artifact consumed at
  the generation boundary; excluding it keeps committed graph baselines from
  churning.
- `output_aliases` is a **serialized** schema field (REQ-DM-09). It describes
  real generated output (the named exit-point captures), so it appears in every
  serialized graph and in committed baselines.

Before the graph is returned, entry-point groups are sorted by name and the
parameters within each group by qualified name (Step 9, REQ-BASE-06). Discovery
order shifts between runs and between the live and snapshot paths; sorting the
graph itself, not just the rendered YAML, keeps every consumer deterministic.

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

## The params-coverage check (V11, REQ-GA-08)

Some entry points fall through Step-4 binding resolution: the binding is bound,
but no resolution strategy and no design attribute produced a value for it.
Assembly copies their QNs onto `graph.fallback_entry_points`. If such an entry
point also carries no default value AND a module input is wired to it, the
generated JSON never mints the params key while the pipeline still references
it -- a guaranteed `KeyError` when TEAx loads the inputs. V11 exists to catch
that at generation time instead.

The check is two-layered:

- **Pure collector.** `collect_uncovered_params` in
  `src/sysml_codegen/resolution/graph_builder.py` walks the graph and returns
  an `UncoveredInput` per violation. A module `entry_point` input is a
  violation when all three hold: its QN is in `fallback_entry_points`
  (fell through), its entry point's `default_value is None` (valueless), and a
  surviving module input references it (wired). Fell-through entry points that
  got a value, and non-fall-through null-default entry points (legitimate
  user-fill), are not violations. The collector raises nothing -- it just
  reports.
- **Always-strict generation boundary.** `_reconcile_params_coverage` in
  `src/sysml_codegen/cli/__init__.py` runs before the output directory is
  cleared, beside the duplicate-output-path check. Any wired violation raises
  `CodeGenerationError` (the V11 message) and aborts the run. There is no
  escape-hatch flag.

The unwired remainder gets softer treatment. `collect_unwired_fallthrough`
(same module) returns the fell-through, valueless entry points that no module
input references. Nothing will `KeyError` at runtime, so the boundary logs them
as a single WARNING reconciliation summary -- and logs it before the V11 check,
so the digest reaches the operator even when generation aborts.

## Step 6.9: param_group propagation

After Step 6.8 orphan handling ensures every entry point belongs to some
`ParameterGroup`, Step 6.9 propagates the group name back to `InputSource`
objects. Some entry points created during module construction (particularly
multiplicity EPs from aggregation factories) have `param_group=None` on
their `InputSource` because the group wasn't known at creation time. Step 6.9
builds a `qn_to_group` reverse map from the final `ParameterGroup` list and
walks all module inputs to fill in any `None` values.

```python
# Step 6.9: Propagate param_group to all entry_point InputSources.
qn_to_group: dict[str, str] = {}
for group in param_groups:
    for param in group.parameters:
        qn_to_group[param.qualified_name] = group.name
for m in modules:
    for inp in m.inputs:
        if (
            inp.source.source_type == "entry_point"
            and inp.source.param_group is None
            and inp.source.qualified_name in qn_to_group
        ):
            inp.source.param_group = qn_to_group[inp.source.qualified_name]
```

This is required by REQ-PY-01 and REQ-PY-02 (see
[21-pipeline-yaml-generation](21-pipeline-yaml-generation.md)): the YAML
generator uses `param_group` to prefix entry point sources, and a `None`
value produces bare qualified names that TEAx cannot resolve.

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
