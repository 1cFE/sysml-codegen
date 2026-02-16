# 03 - Resolution Overview

## The One Question

Resolution has a single job. For every input of every module in the pipeline,
it answers: **where does this value come from?**

The answer is always one of two things:

1. **From another module's output** -- wire to that channel (e.g., `alpha_split__p_neutron`).
2. **From the user** -- create an entry point in a JSON input file (e.g., `physics_params.json`).

That is the entire contract. Everything else in the resolution layer exists to
answer this question correctly across all reachable combinations.

## Why Resolution Is Hard

The combinatorial space is the problem:

- **3 module types**: CalcUsage, ComputedAttribute (FORMULA), Aggregation
- **5 binding types**: CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND
- **3 redefinition types**: CHAIN (delegation), LITERAL (value override), EXPRESSION (computed)
- **2 registry outcomes**: channel found, channel not found
- **3 entry point types**: LIBRARY_DEFAULT, DESIGN_ATTRIBUTE, USAGE_LITERAL

That is 3 x 5 x 3 x 2 x 3 = 270 combinations. Not all are reachable, but the
code must handle every reachable one correctly. A missed combination is a silent
wiring bug -- the pipeline compiles and runs, but produces wrong numbers.

## Current State: Three Code Paths

The current `graph_builder.py` is 1418 lines containing three independent
module construction functions, each reimplementing input resolution differently.

**`_build_pipeline_module`** (CalcUsage, line 1291) -- Looks up pre-computed
`BindingResolution` objects keyed by `"{usage_qn}|{param_name}"`. Clean and
fail-fast, but the resolution was computed upstream by the backtracker.

```python
resolution = binding_resolutions[mapping_key]
if resolution.resolution_type == MODULE_OUTPUT:
    source = InputSource(source_type="module_output", producer_channel=resolution.qualified_name)
elif resolution.resolution_type == ENTRY_POINT:
    source = InputSource(source_type="entry_point", qualified_name=resolution.qualified_name)
```

**`_build_computed_attr_module`** (FORMULA, line 641) -- Parses `inputs.X`
references from compiled expressions via regex. Checks an `AttributeResolution`
map (FORMULA -> synthetic channel, EXPOSE_PURE -> upstream alias, fallback ->
entry point). Creates new entry points by mutating the shared `entry_points`
dict as a side effect.

**`_build_aggregation_module`** (Aggregation, line 922) -- The most complex
path. Three term types, each with its own resolution strategy: SumTerms chase
CHAIN redefinitions with cycle detection; SingletonTerms try registry-first
then direct channel construction; LocalTerms check sibling aggregation outputs,
then EXPOSE_PURE aliases, then fall back to entry points. All mutate
`entry_points` in place.

### The Problems

1. **Three resolution implementations.** The same question ("where does this
   come from?") is answered by three code paths with different strategies,
   fallback chains, and error handling. A fix to one does not fix the others.

2. **Shared mutable state.** `entry_points` is passed into all three builders
   and mutated as a side effect. The orchestrator rebuilds `param_groups` after
   all mutations. Ordering dependencies are implicit.

3. **Untestable resolution.** You cannot test "does input X resolve to channel
   Y?" without constructing a full module.

## Refactored State: The Thin Orchestrator

The refactoring decomposes the god module into focused sub-modules:

```
resolution/
  graph_builder.py           -- thin orchestrator (< 100 lines)
  input_resolver.py          -- ONE unified resolution function
  module_factory.py          -- THREE pure construction functions
  entry_point_classifier.py  -- entry point collection + classification
  models.py                  -- ComputationGraph (unchanged)
```

### The Orchestrator

```python
def build_computation_graph(result, calc_defs, design_attrs, ...) -> ComputationGraph:
    entry_points = classify_entry_points(result.entry_points, result.entry_point_sources,
                                         design_attrs, calc_defs, group_deriver)
    modules = []
    for usage in result.required_usages:
        module, new_eps = build_calc_usage_module(usage, calc_defs, result.binding_resolutions)
        modules.append(module); entry_points.update(new_eps)
    for ca in computed_attributes:
        module, new_eps = build_formula_module(ca, resolution_map, design_attrs)
        modules.append(module); entry_points.update(new_eps)
    for agg in aggregation_data:
        module, new_eps = build_aggregation_module(agg, redefinitions, output_registry)
        modules.append(module); entry_points.update(new_eps)
    param_groups = group_entry_points(entry_points, group_deriver)
    modules = topological_sort(modules)
    validate_channel_references(modules)
    return ComputationGraph(modules=modules, entry_point_groups=param_groups,
                            execution_order=[m.name for m in modules])
```

The key structural change: factory functions return `(module, new_entry_points)`
instead of mutating a shared dict. Data flows down, results flow up.

### Mutable vs. Pure Data Flow

Current (shared mutable state):
```
entry_points = classify(...)
build_calc_usage(entry_points)      # reads
build_formula(entry_points)         # reads AND MUTATES
build_aggregation(entry_points)     # reads AND MUTATES
param_groups = rebuild(entry_points)
```

Refactored (pure returns):
```
entry_points = classify(...)
m1, eps1 = build_calc_usage(...)    # returns new EPs
m2, eps2 = build_formula(...)       # returns new EPs
m3, eps3 = build_aggregation(...)   # returns new EPs
all_eps = entry_points | eps1 | eps2 | eps3
param_groups = group(all_eps)
```

No function mutates its inputs. Every contribution is visible at the call site.

## The Four Sub-Modules

**input_resolver.py** (detailed in 04) -- One function:
`resolve_input(symbolic_ref, context) -> InputSource`. All three module types
call this same function. Returns `module_output` with a channel name, or
`entry_point` with a qualified name.

**module_factory.py** (detailed in 05) -- Three pure construction functions,
one per module type. Each calls `resolve_input()` for every input and returns
`(PipelineModule, dict[str, EntryPoint])`. No shared mutable state.

**entry_point_classifier.py** (detailed in 06) -- Classifies entry point names
into the three ADR-001 types and resolves default values. Handles post-build
grouping into parameter groups for JSON file generation.

**graph_builder.py** (detailed in 07) -- The thin orchestrator. Under 100 lines.
Calls the other three modules in order and assembles the `ComputationGraph`.

## Concrete Example: Tracing Two Inputs

A calc usage `alpha_split` has two inputs:
- `p_total` -- bound to upstream `plasma_power.p_total` (should wire to channel)
- `f_alpha` -- unbound param with library default 0.2 (should become entry point)

**Current flow:** The backtracker produces binding resolutions. `_classify_entry_points`
finds `f_alpha` in `unbound_lookup`, classifies it as LIBRARY_DEFAULT with default
0.2. Then `_build_pipeline_module` looks up each resolution and builds `ModuleInput`
objects. This works, but the resolution pattern differs from FORMULA and aggregation.

**Refactored flow:** Same binding resolutions from the backtracker. Then
`build_calc_usage_module` calls `resolve_input()` for each input:

- `resolve_input("p_total", ctx)` -> binding resolution found ->
  `InputSource(module_output, "plasma_power__p_total")`
- `resolve_input("f_alpha", ctx)` -> binding resolution found ->
  `InputSource(entry_point, "Physics__alpha_split__f_alpha")`

Factory returns `(PipelineModule, {})`. Orchestrator merges and continues.

The critical difference: both inputs go through `resolve_input()`. A bug fix
in that function fixes it for all module types. In the current code, you would
need to find and fix the same bug in each of the three builders independently.

## What This Enables

With resolution extracted into `input_resolver.py`:

```python
def test_bound_input_resolves_to_channel():
    source = resolve_input("p_total", context_with_binding("plasma_power.p_total"))
    assert source.source_type == "module_output"
    assert source.producer_channel == "plasma_power__p_total"

def test_unbound_input_resolves_to_entry_point():
    source = resolve_input("f_alpha", context_without_binding())
    assert source.source_type == "entry_point"
    assert source.qualified_name == "Physics__alpha_split__f_alpha"
```

Today these tests are impossible -- resolution is embedded inside module
construction. After the refactoring, the 270-combination space can be tested
as a matrix against a single function.
