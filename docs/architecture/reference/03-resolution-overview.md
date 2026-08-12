# 03 - Resolution Overview

> **Status: historical.** The string-resolution layer this document describes —
> `analysis/dependency_backtracker.py`, `resolution/graph_builder.py`,
> `resolution/producer_resolution.py`, `core/output_registry.py` — was **deleted** by the
> Item 7 retirement (2026-08-12, `19072ad` / `82c7951` / `882fc8d` / `3071fba`). None of
> those modules is in the tree. What ships is one authority: source admission → strict
> elaboration → `InstanceGraph` → one-way projection → generation, with v6 instance-graph
> snapshots as the only offline source.
>
> **The shipped route answers the same question differently.** The elaborator resolves every
> reference against typed node identity — occurrence enumeration, never a key built from a
> scope-prefixed string — so the scope problem this document opens with does not arise: a
> consumer holds a typed reference to the node that supplies it. An unresolvable reference is a
> typed refusal, not a fall-through to an entry point.
>
> Everything below is retained as the record of the deleted design. It is accurate about the
> code that was removed and is **not a description of what the product does**. For that, read
> [00-pipeline-overview](00-pipeline-overview.md) and
> [02-orchestration](02-orchestration.md).
>
> This document also cites `resolution/input_resolver.py`, which was deleted before the
> recovery began (at `936315c`).

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
| REQ-RES-02 | Positive resolution has one authority, `resolve_producer()` ([04](04-producer-resolution.md)), called by three consumers: CalcUsage bindings during backtracker DFS ([11](11-analysis-backtracker.md)), constraint actuals, and aggregation terms via the `_build_agg_input_source()` choke point + the LocalTerm expose reroute ([05](05-module-factory.md)). FORMULA is the one exception — it uses the pre-computed attribute resolution map ([16](16-computed-attributes.md)), no resolver call. | Call site inspection per module type |
| REQ-RES-03 | Factory functions SHALL return `(PipelineModule, dict[str, EntryPoint])` -- no mutation of shared state (REQ-RES-03a: no side effects). | Type signature + no external dict mutation in [module factory](05-module-factory.md) |
| REQ-RES-04 | Every `module_output` reference SHALL resolve to a canonical channel in the [OutputRegistry](10-output-registry.md). | `_validate_channel_references()` in [graph assembly](07-graph-assembly.md) |
| REQ-RES-05 | The orchestrator SHALL be a linear sequence: classify -> build modules -> rebuild groups -> toposort -> validate. | Source-order pin: `test_orchestrator.py::TestInnerStepOrdering` ("rebuild groups" = `derive_groups()`) |
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

The mechanism: every consumer knows its own identity and passes it to
`resolve_producer()`. From this the resolver derives the consumer's parent scope as a dotted path.
Prepending that scope to `source_path` produces a
`ScopedKey` for exact match against the scoped registry. See
[Strategy A: ScopedRegistryLookup](04-producer-resolution.md#a-scopedregistrylookup).

| What | Example |
|------|---------|
| Consumer EQN | `Design__plant__subsys__battery_pack__sizing` |
| Parent scope (dotted, design prefix stripped) | `plant.subsys.battery_pack` |
| source_path (from extraction) | `cost_model.total_cost` |
| `ScopedKey` | `ScopedKey("plant.subsys.battery_pack.cost_model.total_cost")` |

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-RES-07 | Resolution of scope-relative references (CHAIN `source_path`) SHALL use the consumer's parent scope to construct a `ScopedKey` lookup against the typed scoped registry ([10-output-registry](10-output-registry.md)). REFERENCE bindings (`::` in source_path) SHALL use `SysMLQN` lookup against the SysML QN registry. Cross-package CHAIN references fall through to the alias registry. | Typed dispatch in backtracker (REQ-BT-08) and the shared `KEY_FORMS` scoped/alias/sysml-qn forms ([04](04-producer-resolution.md)) |
| REQ-RES-08 | Consumer-scope application SHALL hold on each live resolution path, per that path's own mechanism: backtracker base leg (`_consumer_scope_dotted`), backtracker ancestor-scope climb (Step CLIMB), aggregation (`ResolutionContext.consumer_scope`, Strategy A primary form), and FORMULA (owner-keyed map — the owner IS the consumer; no dotted scope string). Per-path application over the enumerated paths, not an exhaustiveness proof. | `test_res08_consumer_scope_paths.py` (four legs, hand-authored expectations) |

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

## The Problem This Solved

`graph_builder.py` once had three independent module construction functions, each
reimplementing input resolution with its own strategy list and error handling. The
problems that drove the consolidation (lifecycle Item 2, see
[24-dual-resolution-architecture](24-dual-resolution-architecture.md)):

1. **Three resolution implementations.** One question — "which real thing produces
   this value?" — answered by three ladders with different order, guard placement,
   and terminal behavior, which drifted apart. Now one ordered `KEY_FORMS` table
   in `resolve_producer()` ([04](04-producer-resolution.md)).
2. **Shared mutable state.** `entry_points` was mutated as a side effect.
   (Violated REQ-RES-03; since fixed -- all three factories now return
   `(module, new_entry_points)` per REQ-MF-01.)
3. **Untestable resolution.** Could not test "does input X resolve to channel Y?"
   without constructing a full module. Now `resolve_producer()` is a pure
   function of `(ProducerRequest, ProducerContext)`, unit-tested in isolation.

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
after dependency discovery. The aggregation consumer runs through the shared
[`resolve_producer()`](04-producer-resolution.md) table after the DFS completes;
FORMULA uses the pre-computed attribute resolution map. The DFS-timing distinction
between the calc consumer and the others is the only structural reason resolution
touches more than one call site — the resolver itself is one authority.

## Consolidated Resolution (landed)

Positive resolution is one authority, `resolve_producer()`
([04-producer-resolution](04-producer-resolution.md)), called by three consumers.
FORMULA is the one mechanism that does not call it:

| Consumer | Module type | Where | Policy |
|------|------------|-------|--------|
| Calculation binding | CalcUsage | `analysis/dependency_backtracker.py` (during DFS) | LENIENT |
| Constraint actual | Constraint | `analysis/constraint_lowering.py` | STRICT |
| Aggregation term | Aggregation | `resolution/graph_builder.py` (`_build_agg_input_source` + LocalTerm expose reroute) | LENIENT |
| — (not a consumer) | FORMULA | `resolution/graph_builder.py` (pre-computed attribute resolution map) | n/a |

The code structure:

```
analysis/
  dependency_backtracker.py   -- DFS + calc-binding resolution (calls resolve_producer)  --> 11
  constraint_lowering.py      -- constraint-actual resolution (calls resolve_producer)
resolution/
  graph_builder.py            -- orchestrator + the three factory functions
                                 + entry point classification            --> 05, 06, 07
  producer_resolution.py      -- resolve_producer(): the one resolution authority  --> 04
  producer_completeness.py    -- one-intended-producer check                       --> 04
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
        module, new_eps = _build_aggregation_module(        # 05 -- resolve_producer via
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
[`resolve_producer()`](04-producer-resolution.md) via the `_build_agg_input_source()`
choke point. All factory functions return `(module, new_entry_points)` (REQ-RES-03).

### What Changed vs. What Stayed

| Aspect | Before | After |
|--------|--------|-------|
| CalcUsage resolution | Backtracker 5-step cascade against flat `dict[str, str]` | Backtracker [type-directed dispatch](11-analysis-backtracker.md#type-directed-resolution-dispatch): CHAIN/REFERENCE paths with typed registries |
| FORMULA resolution | Ad-hoc regex + attr map + mutation | Pre-computed [attribute resolution map](16-computed-attributes.md) (no registry lookup) |
| Aggregation resolution | 3 term-type-specific functions + mutation | `resolve_producer()` shared `KEY_FORMS` table using typed registries |
| Registry | `dict[str, str]` with 12+ key formats | 3 typed registries: `dict[ScopedKey, CanonicalChannel]`, `dict[SysMLQN, CanonicalChannel]`, `dict[ScopedKey, CanonicalChannel]` -- plus the structured `_scoped_alias` namespace (`dict[ScopedAliasKey, CanonicalChannel]`) for part-def EXPOSE aliases |
| Entry point creation | Side-effect mutation of shared dict | Returned as tuple second element |
| Testability | Full module construction required | `resolve_producer()` testable in isolation |

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

**Aggregation path**: Same question, now answered by the same authority,
`resolve_producer()` (via `_build_agg_input_source()`):

```python
resolve_producer(ProducerRequest(reference="p_total", ...), ctx)  → MODULE_OUTPUT, "plasma_power__p_total"
resolve_producer(ProducerRequest(reference="f_alpha", ...), ctx)  → ENTRY_POINT, "Physics__alpha_split__f_alpha"
```

Both consumers run the one shared table, so they produce the same wiring by
construction. FORMULA uses the attribute resolution map instead, but reaches
equivalent answers for shared references.

## Related Documents

- **Upstream**: [00-pipeline-overview](00-pipeline-overview.md) (Steps 3-6), [01-extraction](01-extraction.md) (provides bindings and redefinitions), [11-analysis-backtracker](11-analysis-backtracker.md) (CalcUsage resolution + DFS)
- **Sub-modules**: [04-producer-resolution](04-producer-resolution.md) (FORMULA/Agg resolution), [05-module-factory](05-module-factory.md), [06-entry-point-classifier](06-entry-point-classifier.md), [07-graph-assembly](07-graph-assembly.md)
- **Architecture**: [24-dual-resolution-architecture](24-dual-resolution-architecture.md) (why two paths exist)
- **Registry**: [10-output-registry](10-output-registry.md) (channel lookup, typed registries), [15-naming-conventions](15-naming-conventions.md) (key formats, identifier types)
- **Data models**: [09-data-models](09-data-models.md) -- ComputationGraph, PipelineModule, InputSource, BindingResolution
- **Deep dives**: [13-aggregation-scoping](13-aggregation-scoping.md), [16-computed-attributes](16-computed-attributes.md), [18-literal-value-propagation](18-literal-value-propagation.md)
