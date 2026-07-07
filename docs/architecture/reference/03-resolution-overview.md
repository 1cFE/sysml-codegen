# 03 - Resolution Overview

## The One Question

Resolution has a single job. For every input of every module in the pipeline,
it answers: **where does this value come from?**

The answer is always one of two things:

1. **From another module's output** -- wire to that channel (e.g., `alpha_split__p_neutron`).
2. **From the user** -- create an [entry point](06-entry-point-classifier.md) in a JSON input file.

That is the entire contract. Everything else in the resolution layer exists to
answer this question correctly across all reachable combinations.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-RES-01 | Every [ModuleInput](09-data-models.md#resolution-models) SHALL resolve to exactly one of {`module_output`, `entry_point`}. | `all(mi.source.source_type in {"module_output","entry_point"} for m in modules for mi in m.inputs)` |
| REQ-RES-02 | Three live resolution mechanisms: CalcUsage uses backtracker DFS cascade ([11](11-analysis-backtracker.md)). FORMULA uses pre-computed attribute resolution map ([16](16-computed-attributes.md)). Aggregation SumTerm/SingletonTerm uses `resolve_input()`/`AGG_STRATEGIES` ([04](04-input-resolver.md)) via the `_build_agg_input_source()` choke point ([05](05-module-factory.md)). Aggregation LocalTerm uses a factory-specific 3-strategy cascade, with its expose-alias reroute calling `resolve_input()` ([05](05-module-factory.md#4c-localterm)). | Call site inspection per module type |
| REQ-RES-03 | Factory functions SHALL return `(PipelineModule, dict[str, EntryPoint])` -- no mutation of shared state (REQ-RES-03a: no side effects). | Type signature + no external dict mutation in [module factory](05-module-factory.md) |
| REQ-RES-04 | Every `module_output` reference SHALL resolve to a canonical channel in the [OutputRegistry](10-output-registry.md). | `_validate_channel_references()` in [graph assembly](07-graph-assembly.md) |
| REQ-RES-05 | The orchestrator SHALL be a linear sequence: classify -> build modules -> rebuild groups -> toposort -> validate. | Code structure of `build_computation_graph()` |
| REQ-RES-06 | `binding_resolutions` from the [backtracker](11-analysis-backtracker.md) SHALL be the single source of truth for CalcUsage input wiring. Key format: `"{usage_qn}\|{param_name}"`. | Every CalcUsage input looked up in this dict; missing key = immediate `ValueError` |

## The Scope Problem

Every binding in SysML is written **relative to a scope**. When a calc usage
inside `battery_pack` says `cost_model.total_cost`, that is a local reference
to the `cost_model` instance that is a sibling within `battery_pack`. It is NOT
a global identifier.

But extraction (`_parse_chain_expression`) strips the scope context and produces
a bare `source_path = "cost_model.total_cost"`. If `solar_array` also contains
a `cost_model`, the string `"cost_model.total_cost"` is ambiguous -- it could
refer to either one.

The [OutputRegistry](10-output-registry.md) uses three typed registries
([10-output-registry](10-output-registry.md)): scoped
(`dict[ScopedKey, CanonicalChannel]`), SysML QN (`dict[SysMLQN, CanonicalChannel]`),
and alias (`dict[ScopedKey, CanonicalChannel]`), plus a structured
`_scoped_alias` namespace (`dict[ScopedAliasKey, CanonicalChannel]`, a
`(scope, leaf)` tuple key) that holds part-def EXPOSE aliases expanded per
design instance. The scoped registry does not
contain ambiguous keys — only `ScopedKey` entries derived from the SysML
ownership chain. But the registry still has no concept of which module is asking.

**This is the central design constraint of the resolution layer:**

> `source_path` from extraction is a scope-relative reference.
> The resolver MUST bridge the gap by re-attaching scope before lookup.

The mechanism: both the backtracker and `resolve_input()` know the consumer's
identity. From this they derive the consumer's parent scope as a dotted path.
Prepending that scope to `source_path` produces a
`ScopedKey` for exact match against the scoped registry. See
[Strategy A: ScopedRegistryLookup](04-input-resolver.md#a-scopedregistrylookup).

| What | Example |
|------|---------|
| Consumer EQN | `Design__plant__subsys__battery_pack__sizing` |
| Parent scope (dotted, design prefix stripped) | `plant.subsys.battery_pack` |
| source_path (from extraction) | `cost_model.total_cost` |
| `ScopedKey` | `ScopedKey("plant.subsys.battery_pack.cost_model.total_cost")` |

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-RES-07 | Resolution of scope-relative references (CHAIN `source_path`) SHALL use the consumer's parent scope to construct a `ScopedKey` lookup against the typed scoped registry ([10-output-registry](10-output-registry.md)). REFERENCE bindings (`::` in source_path) SHALL use `SysMLQN` lookup against the SysML QN registry. Cross-package CHAIN references fall through to the alias registry. | Typed dispatch in backtracker (REQ-BT-08) and typed strategies in `AGG_STRATEGIES` |
| REQ-RES-08 | Consumer scope derivation SHALL apply to ALL live resolution paths: backtracker (CalcUsage), attribute resolution map (FORMULA), and `resolve_input()` (Aggregation) via `ResolutionContext.consumer_scope`. | Backtracker: `_consumer_scope_dotted()` in `dependency_backtracker.py`. resolve_input(): `ResolutionContext.consumer_scope`. FORMULA: scope via owning part QN. |

## Why Resolution Is Hard

The combinatorial space is the problem:

- **3 module types**: CalcUsage, ComputedAttribute (FORMULA), Aggregation
- **5 [binding types](01-extraction.md#binding-types)**: CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND
- **3 [redefinition types](01-extraction.md#redefinitions-redefinitiondata)**: CHAIN, LITERAL, EXPRESSION
- **2 registry outcomes**: channel found, channel not found
- **3 [entry point types](06-entry-point-classifier.md)**: LIBRARY_DEFAULT, DESIGN_ATTRIBUTE, USAGE_LITERAL

**Note on EXPRESSION**: EXPRESSION bindings have `source_path=None` because their
source is the expression AST itself, not an external reference. The backtracker
skips them during DFS — they contribute to the module's `compiled_expression`
(see [14-expression-compiler](14-expression-compiler.md)), not to its wiring.

That is 3 x 5 x 3 x 2 x 3 = 270 combinations. Not all are reachable, but the
code must handle every reachable one correctly.

## Current State: Three Code Paths

The current `graph_builder.py` has three independent module construction
functions, each reimplementing input resolution differently. See
[24-dual-resolution-architecture](24-dual-resolution-architecture.md) for the
full breakdown.

### The Problems

1. **Three resolution implementations.** Same question answered by three paths
   with different strategies and error handling.
2. **Shared mutable state.** `entry_points` was mutated as a side effect.
   (Violated REQ-RES-03; since fixed -- all three factories now return
   `(module, new_entry_points)` per REQ-MF-01.)
3. **Untestable resolution.** Could not test "does input X resolve to channel Y?"
   without constructing a full module. (Since fixed for `resolve_input()`, which
   is unit-tested in isolation.)

## Why CalcUsage Resolution Stays in the Backtracker

The [backtracker](11-analysis-backtracker.md)'s DFS must resolve bindings
**during traversal** to decide which usages to recurse into:

```python
# In _trace_dependencies (backtracker DFS):
resolution = self._resolve_binding_via_registry(binding, usage)
if resolution.resolution_type == MODULE_OUTPUT:
    producing_usage = self._find_usage_for_channel(resolution.qualified_name)
    self._trace_dependencies(producing_usage, visited, path)  # RECURSE
# If ENTRY_POINT: stop -- no upstream module to trace
```

Without resolving each binding, the DFS cannot know whether to recurse (it's
a MODULE_OUTPUT, trace the producer) or stop (it's an ENTRY_POINT, nothing to
trace). This makes CalcUsage resolution **structurally inseparable** from
dependency discovery.

The backtracker implements type-directed dispatch (REQ-BT-08, in
`_resolve_binding_via_registry` in `dependency_backtracker.py`). CHAIN bindings
try, in order: consumer-scoped `scoped_lookup(ScopedKey)`, direct
`scoped_lookup` on the bare path, a scoped-alias lookup
(`scoped_alias_lookup(ScopedAliasKey)`, splitting the path at the last dot --
this reaches part-def EXPOSE channels expanded per design instance, and tries
the consumer-scope-prefixed key first for sibling disambiguation, REQ-BT-11),
then cross-scope `alias_lookup(ScopedKey)`. REFERENCE bindings (`::` paths)
try `sysml_qn_lookup(SysMLQN)` with the key per-segment sanitized via
`sanitize_qualified_name` (so quoted-owner QNs match, REQ-BT-09), then a
leaf + parent-scope secondary lookup (`_resolve_reference_via_registry`).
Either dispatch then falls back to design-attribute matching
(`_resolve_to_design_attribute`) and finally an entry point; the per-binding
"Registry unresolved" line is DEBUG, with a single post-assembly WARNING
summary for genuine residue. Some cross-part CHAIN bindings are rewritten
before the backtracker sees them: `_rewrite_specialized_chain` (in
`orchestration/pipeline_builder.py`) rewrites `part_usage.attr` chains through
a retyped part's specialized-def `:>>` chain. See
[10-output-registry](10-output-registry.md).

FORMULA and Aggregation modules do NOT participate in DFS -- they are built
after dependency discovery. Their resolution CAN be extracted into a standalone
[`resolve_input()`](04-input-resolver.md) function.

## Consolidated Resolution (landed)

> **Status (F4 cutover landed, TRUTH-DEBT Item 1):** the consolidation below is
> live. FORMULA uses the pre-computed attribute resolution map, and **aggregation
> SumTerm/SingletonTerm now runs through `resolve_input()`** via the
> `_build_agg_input_source()` choke point in `graph_builder.py`. The old
> `_resolve_aggregation_input_channel` is **deleted**. The cutover was
> parity-validated against the backtracker (`test_dual_resolution.py`) and landed
> byte-identical baselines. Spec/design/plan in `.project/active/f4-cutover/`.

The consolidation reduces three resolution paths to **two well-defined paths**:

| Path | Module type | Where | Status |
|------|------------|-------|--------|
| **Backtracker** | CalcUsage | `analysis/dependency_backtracker.py` | live (DFS requires resolution during traversal) |
| **attribute resolution map** | FORMULA | `resolution/graph_builder.py` | live |
| **resolve_input()** | Aggregation | `resolution/input_resolver.py` (called via `_build_agg_input_source()` in `graph_builder.py`) | live |

The code structure:

```
analysis/
  dependency_backtracker.py   -- DFS + CalcUsage resolution (existing)   --> 11
resolution/
  graph_builder.py            -- orchestrator + the three factory functions
                                 + entry point classification            --> 05, 06, 07
  input_resolver.py           -- resolve_input() consolidated resolver   --> 04
  models.py                   -- ComputationGraph (unchanged)            --> 09
```

The factory functions and `_classify_entry_points()` live in
`graph_builder.py` (they were not split into separate files); docs 05 and 06
describe them.

### The Orchestrator (REQ-RES-05)

```python
def build_computation_graph(result, calc_defs, design_attrs, ...) -> ComputationGraph:
    entry_points = _classify_entry_points(...)             # 06 -- from backtracker results
    modules = []
    for usage in result.required_usages:
        module, new_eps = _build_pipeline_module(          # 05 -- lookup binding_resolutions
            usage, binding_resolutions=result.binding_resolutions)
        modules.append(module); entry_points.update(new_eps)
    for ca in computed_attributes:
        module, new_eps = _build_computed_attr_module(      # 05 -- uses attr resolution map
            ca, resolution_map=...)
        modules.append(module); entry_points.update(new_eps)
    for agg in aggregation_data:
        module, new_eps = _build_aggregation_module(        # 05 -- resolve_input via
            agg, redefinitions=..., output_registry=...)     # _build_agg_input_source()
        modules.append(module); entry_points.update(new_eps)
    param_groups = rebuild_groups(entry_points)             # 17
    modules = topological_sort(modules)                     # 07
    validate_channel_references(modules)                    # 07
    return ComputationGraph(...)
```

CalcUsage modules look up pre-computed `binding_resolutions` (REQ-RES-06).
FORMULA modules use the pre-computed [attribute resolution map](16-computed-attributes.md).
Aggregation modules resolve SumTerm/SingletonTerm inputs through
[`resolve_input()`](04-input-resolver.md) via the `_build_agg_input_source()`
choke point. All factory functions return `(module, new_entry_points)` (REQ-RES-03).

### What Changed vs. What Stayed

| Aspect | Before | After |
|--------|--------|-------|
| CalcUsage resolution | Backtracker 5-step cascade against flat `dict[str, str]` | Backtracker [type-directed dispatch](11-analysis-backtracker.md#type-directed-resolution-dispatch): CHAIN/REFERENCE paths with typed registries |
| FORMULA resolution | Ad-hoc regex + attr map + mutation | Pre-computed [attribute resolution map](16-computed-attributes.md) (no registry lookup) |
| Aggregation resolution | 3 term-type-specific functions + mutation | `resolve_input()` with `AGG_STRATEGIES` using typed registries |
| Registry | `dict[str, str]` with 12+ key formats | 3 typed registries: `dict[ScopedKey, CanonicalChannel]`, `dict[SysMLQN, CanonicalChannel]`, `dict[ScopedKey, CanonicalChannel]` -- plus the structured `_scoped_alias` namespace (`dict[ScopedAliasKey, CanonicalChannel]`) for part-def EXPOSE aliases |
| Entry point creation | Side-effect mutation of shared dict | Returned as tuple second element |
| Testability | Full module construction required | `resolve_input()` testable in isolation |

## Concrete Example: Tracing Two Inputs

A CalcUsage `alpha_split` has two inputs:
- `p_total` -- bound to upstream `plasma_power.p_total` (should wire to channel)
- `f_alpha` -- unbound param with library default 0.2 (should become entry point)

**CalcUsage path**: The backtracker resolves both during DFS. `p_total` hits the
registry → MODULE_OUTPUT → DFS recurses into `plasma_power`. `f_alpha` has no
binding → ENTRY_POINT. Results stored in `binding_resolutions`. Then
`build_calc_usage_module` looks up each:

```python
binding_resolutions["alpha_split|p_total"]  → MODULE_OUTPUT, channel="plasma_power__p_total"
binding_resolutions["alpha_split|f_alpha"]  → ENTRY_POINT, qn="Physics__alpha_split__f_alpha"
```

**Aggregation path**: Same question, now answered by `resolve_input()` (via
`_build_agg_input_source()`), parity-validated to give the same answer:

```python
resolve_input("p_total", ctx)  → InputSource(module_output, "plasma_power__p_total")
resolve_input("f_alpha", ctx)  → InputSource(entry_point, "Physics__alpha_split__f_alpha")
```

Both paths produce the same wiring. FORMULA uses the attribute resolution map
instead, but reaches equivalent answers for shared references.

## Related Documents

- **Upstream**: [00-pipeline-overview](00-pipeline-overview.md) (Steps 3-6), [01-extraction](01-extraction.md) (provides bindings and redefinitions), [11-analysis-backtracker](11-analysis-backtracker.md) (CalcUsage resolution + DFS)
- **Sub-modules**: [04-input-resolver](04-input-resolver.md) (FORMULA/Agg resolution), [05-module-factory](05-module-factory.md), [06-entry-point-classifier](06-entry-point-classifier.md), [07-graph-assembly](07-graph-assembly.md)
- **Architecture**: [24-dual-resolution-architecture](24-dual-resolution-architecture.md) (why two paths exist)
- **Registry**: [10-output-registry](10-output-registry.md) (channel lookup, typed registries), [15-naming-conventions](15-naming-conventions.md) (key formats, identifier types)
- **Data models**: [09-data-models](09-data-models.md) -- ComputationGraph, PipelineModule, InputSource, BindingResolution
- **Deep dives**: [13-aggregation-scoping](13-aggregation-scoping.md), [16-computed-attributes](16-computed-attributes.md), [18-literal-value-propagation](18-literal-value-propagation.md)
