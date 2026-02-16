---
date: 2026-02-16T21:00:00-05:00
researcher: Claude
topic: "Resolution architecture refactoring: root cause analysis and decomposition proposal"
tags: [research, architecture, refactoring, resolution, graph-builder]
status: complete
last_updated: 2026-02-16
---

# Research: Resolution Architecture Refactoring

**Date**: 2026-02-16 21:00 EST
**Researcher**: Claude (7-agent parallel analysis)
**Research Type**: Architecture / Root Cause Analysis / Refactoring Design

## Research Question

Why does the resolution layer keep producing bugs despite 42 test files and 664+ passing tests? What architectural refactoring would make the system explainable, testable, and provably correct?

## Summary

- **Root cause confirmed**: `graph_builder.py` (1282 lines) and `dependency_backtracker.py` (715 lines) implement overlapping resolution logic through shared mutable state, with 10 documented areas of duplication
- **The system does something fundamentally simple** — it just resolves references. But that simplicity is buried under 3 independent resolution code paths (CalcUsage bindings, computed attributes, aggregation terms) that each reimplement "look up a reference in the registry, fall back to entry point"
- **The generation layer is mostly clean** — `pipeline.py` is the gold standard, purely consuming ComputationGraph. But `initialization.py` (860 lines of orchestration code) is misplaced inside `generation/`
- **The fix is decomposition into single-responsibility modules** with one shared resolution function, one module factory per type, and explicit strategy chains

---

## Part 1: What The System Actually Does (ELI5)

At its core, this system does 4 things:

```
1. EXTRACT:  Read SysML files → produce structured data
             (calc definitions, calc usages, part hierarchy, design attributes)

2. RESOLVE:  For every input of every module, answer ONE question:
             "Where does this value come from?"
             Answer is always one of:
               (a) From another module's output  → wire to that channel
               (b) From the user                 → create an entry point

3. ASSEMBLE: Collect all modules + all entry points → ComputationGraph

4. GENERATE: Render ComputationGraph → Python code, YAML, JSON
```

Step 2 is where ALL the bugs live. And Step 2 is fundamentally just a lookup function:

```python
def resolve_input(reference: str, context: ResolutionContext) -> InputSource:
    """Given a reference string, find what it points to."""
    # Try strategies in order until one works
    for strategy in resolution_strategies:
        result = strategy(reference, context)
        if result is not None:
            return result
    # Nothing worked → entry point (user must provide value)
    return InputSource.entry_point(reference)
```

That's it. Every bug in the system is a bug in this one conceptual function — either a strategy is tried in the wrong order, or a strategy produces the wrong result, or a strategy is missing for a particular SysML pattern.

---

## Part 2: How The Code Actually Works (Current State)

### 2.1 The God Module: `graph_builder.py` (1282 lines)

**13 functions, 8 logical phases, 3 module construction paths.**

The orchestrator `build_computation_graph()` (lines 70-241) runs these phases:

| Phase | Step | Lines | What it does | Mutable state touched |
|-------|------|-------|-------------|----------------------|
| 1 | Data prep | 105 | Build calc_def_map, calc_usage_names | Creates local dicts |
| 2 | Step 3 | 108-113 | Build attribute resolution map (FORMULA wiring) | Creates attr_resolution_map |
| 3 | Step 4 | 116-123 | Classify entry points | **Creates `entry_points` dict** |
| 4 | Step 5 | 127-132 | Initial parameter grouping | Creates param_groups |
| 5a | Step 6 | 136-156 | Build CalcUsage modules | Appends to modules list |
| 5b | Step 6.5 | 159-169 | Build FORMULA modules | Appends to modules, **MUTATES entry_points** |
| 5c | Step 6.7 | 172-177 | Build aggregation modules | Appends to modules, **MUTATES entry_points** |
| 6 | Step 6.6 | 184-228 | Rebuild parameter groups + orphan detection | Replaces param_groups |
| 7 | Step 7 | 231 | Topological sort | **MUTATES execution_order on each module** |
| 8 | Step 8 | 235-241 | Validate + assemble | Returns ComputationGraph |

**The critical coupling hazard**: The `entry_points` dict is created in Phase 3, then silently mutated as a side effect in Phases 5b and 5c, then re-read in Phase 6. Two different functions (`_build_computed_attr_module` and `_build_aggregation_module`) each add new entries to this shared dict.

**Three independent module construction functions**:

| Function | Lines | Builds | Resolution method |
|----------|-------|--------|------------------|
| `_build_pipeline_module` | 1155-1267 | CalcUsage modules | Reads pre-resolved `binding_resolutions` from backtracker |
| `_build_computed_attr_module` | 621-736 | FORMULA modules | Its own resolution via `attr_resolution_map` |
| `_build_aggregation_module` | 850-1079 | Aggregation modules | Its own resolution via `_resolve_aggregation_input_channel` + registry |

Each reimplements the pattern: "create InputSource, handle entry point fallback, register new entry points." There is no shared abstraction.

### 2.2 The Backtracker: `dependency_backtracker.py` (715 lines)

**Resolution cascade** (4 steps in `_resolve_binding_via_registry`):

```
Step 1:  registry.resolve(source_path)                    → direct exact match
Step 1b: Normalize :: to dotted, retry registry.resolve() → SYSML_QN normalization
         Self-reference guard
Step 2:  _resolve_reference_via_registry()                → leaf + parent scope (REFERENCE only)
Step 3:  _resolve_to_design_attribute()                   → ENTRY_POINT fallback
Step 4:  ENTRY_POINT with warning                         → final fallback
```

### 2.3 Ten Areas of Duplication Between graph_builder.py and dependency_backtracker.py

| # | What | Backtracker | Graph Builder | Semantic |
|---|------|-------------|---------------|----------|
| 1 | Topological sort (Kahn's) | `_topological_sort` (662-706), O(n²) | `_unified_topological_sort` (1082-1152), O(n) deque | Same algorithm, different efficiency |
| 2 | Dependency graph construction | `_build_dependency_graph` (618-660) | Embedded in `_unified_topological_sort` (1097-1114) | Identical purpose |
| 3 | Channel→usage resolution | `_find_usage_for_channel` (418-427) | `channel_to_module` dict (1098-1101) | String parse vs pre-built index |
| 4 | Self-reference guard | Lines 494-501, 456-458 | Line 1111 | Both prevent self-wiring |
| 5 | Entry point identification | `_trace_dependencies` (340-404) | `_classify_entry_points` (245-347) | Backtracker finds them, graph builder classifies |
| 6 | Design attribute index | `_resolve_to_design_attribute` (571-574) | `_classify_entry_points` (277-281), `_build_computed_attr_module` (662-666) | Same `{qn: attr}` dict built 3× |
| 7 | SysML QN normalization | Lines 486-491 (manual), line 583 (utility) | Lines 639, 599 (utility) | Two methods in backtracker alone |
| 8 | Binding resolution key format | Line 338: `f"{usage.qualified_name}\|{param_name}"` | Line 1199: same format | Identical key construction |
| 9 | `calc_def_map` construction | `__init__` line 133 | `build_computation_graph` line 105 | Same `{name: cd}` dict |
| 10 | `CircularDependencyError` | Defined line 35, raised lines 318, 703 | Imported line 22, raised line 1142 | Shared exception |

### 2.4 The Misplaced Orchestrator: `initialization.py` (860 lines in generation/)

This file contains the **entire upstream pipeline** — model loading, binding rewriting, registry construction, hierarchy extraction, aggregation scoping, alias building — inside the `generation/` package. Key functions:

- `build_pipeline_context()` — the 7-step initialization sequence
- `build_output_registry()` — 4-phase registration protocol (173 lines)
- `_rewrite_virtual_bindings()` — mutates binding objects in-place
- `_scope_aggregation_expressions()` — maps PartDef aggregation to design instances
- `_build_chain_aliases()` — builds ChannelAlias from CHAIN redefinitions

This is a massive layer violation. None of this is generation code.

### 2.5 The Generation Layer: Mostly Clean

| File | Lines | Consumes ComputationGraph? | Resolution logic? |
|------|-------|---------------------------|-------------------|
| `pipeline.py` | 239 | **Yes** (gold standard) | No |
| `constraint_comments.py` | 165 | No (utility) | No |
| `preservation.py` | 100 | No (utility) | No |
| `modules.py` | 202 | No (raw CalcDefData) | No |
| `schemas.py` | 275 | No (raw CalcDefData) | No |
| `stencils.py` | 579 | No (raw CalcDefData) | No |
| `test_gen.py` | 102 | No (raw CalcDefData) | No |
| `entry_point.py` | 646 | Partial | **Yes** (`collect_entry_point_attributes`) |
| `registry.py` | 295 | Partial | Minor (module inventory assembly) |
| `initialization.py` | 860 | N/A | **Entirely** |

**Key finding**: Only `pipeline.py` actually consumes the ComputationGraph. Most generators bypass it and consume raw extraction data directly. If ComputationGraph were enriched, generation would "just work."

---

## Part 3: Why The Bugs Keep Happening

### 3.1 The Bug Pattern

```
1. Encounter new SysML pattern (e.g., LITERAL redefinitions in aggregation)
2. Add special case to one of the 3 module construction functions
3. The special case interacts with shared mutable state (entry_points dict)
4. Or it interacts with a different resolution path (backtracker vs graph_builder)
5. Fix the interaction
6. Repeat
```

### 3.2 Why Tests Don't Catch It

The 664+ tests are **example-based unit tests with mock SysML AST nodes**. They test individual functions in isolation with hand-crafted inputs. They cover the cases the developer thought of.

What they DON'T cover:
- **Combinatorial interactions** between resolution paths (CalcUsage binding + CHAIN redefinition + aggregation term on the same attribute)
- **Shared mutable state mutations** — no test verifies that `_build_aggregation_module` adding to `entry_points` doesn't break `_classify_entry_points`'s earlier work
- **Real model integration** — no automated test runs the full pipeline on the solar_battery model
- **The specific resolution cascade ordering** — the 4-step cascade in `_resolve_binding_via_registry` has tests for individual steps but not for the interaction between them

### 3.3 The Surface Area Problem

The number of possible interactions is the **product** of resolution paths, not the sum:

- 3 module types × 4 binding types × 3 redefinition types × 2 registry outcomes × 3 entry point types = **216 combinations**
- Tests cover maybe 30-40 specific examples

The real model keeps surfacing the untested 176+ combinations.

---

## Part 4: The Refactoring Proposal

### 4.0 Design Principles

1. **One function, one job.** No function should do more than one of: resolve, classify, construct, sort, validate.
2. **Explicit data flow.** No shared mutable state. Each function takes immutable inputs, returns immutable outputs.
3. **Testable in isolation.** Each function can be unit-tested with a truth table of inputs → expected outputs.
4. **ELI5-explainable.** The entire algorithm should be expressible as a short sequence of named steps that a junior developer can follow.

### 4.1 The Target Architecture

```
resolution/
├── graph_builder.py          # THIN orchestrator (< 100 lines)
│                              # Calls: resolver → factory → classifier → sort → validate → assemble
│
├── input_resolver.py          # ONE function: resolve_input(ref, context) → InputSource
│                              # Strategy chain: registry → chain_follow → scoped → design_attr → entry_point
│
├── module_factory.py          # THREE functions, one per module type
│   ├── build_calcusage_module(usage, resolved_inputs) → PipelineModule
│   ├── build_formula_module(ca, resolved_inputs) → PipelineModule
│   └── build_aggregation_module(agg, resolved_inputs) → PipelineModule
│
├── entry_point_classifier.py  # ONE function: classify_entry_points(unresolved_refs, design_attrs, calc_defs) → dict[str, EntryPoint]
│                              # + grouping into ParameterGroups
│
├── models.py                  # Unchanged — the ComputationGraph contract
└── identifier_types.py        # Unchanged — re-export shim
```

Plus moving orchestration out of generation:

```
orchestration/
├── pipeline_builder.py        # Moved from generation/initialization.py
│                              # The 7-step pipeline: extract → analyze → resolve → assemble
└── output_registry_builder.py # 4-phase registry construction (extracted from initialization.py)
```

And shared utilities:

```
core/
├── graph_algorithms.py        # ONE topological sort (Kahn's with deque), used by both backtracker and graph_builder
├── resolution_utils.py        # resolve_scoped() — try with prefix, then without
└── output_registry.py         # Unchanged
```

### 4.2 The Unified Input Resolver

This is the heart of the refactoring. Today, resolution logic is spread across:
- `dependency_backtracker._resolve_binding_via_registry()` — CalcUsage bindings
- `graph_builder._resolve_aggregation_input_channel()` — aggregation SumTerm/SingletonTerm
- `graph_builder._build_computed_attr_module()` — FORMULA attribute references
- `graph_builder._build_aggregation_module()` (LocalTerm section) — local terms

All four do variations of the same thing: "given a reference, try the registry, fall back to entry point."

**Proposed unified resolver:**

```python
# resolution/input_resolver.py

@dataclass(frozen=True)
class ResolutionContext:
    """Immutable context for input resolution."""
    output_registry: OutputRegistry
    redefinitions: list[RedefinitionData]
    design_attrs: dict[str, DesignAttributeData]  # keyed by qualified_name
    module_eqn: str  # self-reference guard
    instance_path: str | None = None  # for aggregation scoping

class ResolutionStrategy(Protocol):
    """A single resolution strategy. Returns channel name or None."""
    def resolve(self, ref: str, ctx: ResolutionContext) -> str | None: ...

# The strategies, in priority order:
STANDARD_STRATEGIES: list[ResolutionStrategy] = [
    DirectRegistryLookup(),      # registry.resolve(ref)
    SysmlQnNormalization(),      # normalize :: to dotted, retry
    ScopedRegistryLookup(),      # scope_prefix + ref, retry
    ChainRedefinitionFollow(),   # follow :>> CHAIN to target, resolve that
    DesignAttributeLookup(),     # match to design attribute → entry point QN
]

def resolve_input(
    ref: str,
    ctx: ResolutionContext,
    strategies: list[ResolutionStrategy] = STANDARD_STRATEGIES,
) -> InputSource:
    """Resolve a single input reference.

    Tries each strategy in order. First match wins.
    If nothing matches, returns an entry point.
    """
    for strategy in strategies:
        channel = strategy.resolve(ref, ctx)
        if channel is not None:
            # Self-reference guard
            if _is_self_reference(channel, ctx.module_eqn):
                continue
            return InputSource(source_type="module_output", producer_channel=channel)

    # Nothing resolved → entry point
    return InputSource(source_type="entry_point", qualified_name=ref)
```

**Why this is better:**
- **One function** to test, not 4.
- **Strategy chain is explicit and visible** — you can read the list and know the precedence.
- **Each strategy is independently testable** — mock the registry, test one strategy at a time.
- **New SysML patterns = new strategy** — add to the list, don't add a branch to a 230-line function.
- **Self-reference guard is in one place**, not duplicated.

### 4.3 The Module Factory

Today, `_build_pipeline_module`, `_build_computed_attr_module`, and `_build_aggregation_module` each:
1. Resolve their inputs (differently)
2. Construct PipelineModule
3. Handle entry point creation as a side effect

After refactoring, they only do step 2. Resolution is done upstream by `resolve_input`. Entry point collection is done downstream by `entry_point_classifier`.

```python
# resolution/module_factory.py

def build_calcusage_module(
    usage: CalcUsageData,
    calc_def: CalculationDefinitionData,
    resolved_inputs: dict[str, InputSource],  # param_name → InputSource (pre-resolved)
    execution_order: int,
) -> PipelineModule:
    """Construct a PipelineModule from a CalcUsage with pre-resolved inputs.

    Pure construction — no resolution logic, no side effects.
    """
    ...

def build_formula_module(
    ca: ComputedAttributeData,
    resolved_inputs: dict[str, InputSource],
) -> PipelineModule:
    """Construct a FORMULA synthetic module."""
    ...

def build_aggregation_module(
    agg: ScopedAggregationData,
    resolved_inputs: dict[str, InputSource],
    compiled_expression: str,
) -> PipelineModule:
    """Construct an aggregation synthetic module."""
    ...
```

**Why this is better:**
- **No side effects.** These functions don't touch `entry_points`.
- **Testable with a truth table.** Given these inputs, expect this PipelineModule.
- **No resolution logic.** Resolution already happened upstream.

### 4.4 The Thin Orchestrator

After extraction, `graph_builder.build_computation_graph()` becomes:

```python
def build_computation_graph(
    result: BacktrackingResult,
    calc_defs: list,
    design_attrs: dict[Path, list[DesignAttributeData]],
    output_registry: OutputRegistry,
    # ... other params
) -> ComputationGraph:
    """Build the computation graph. Thin orchestrator."""

    # Phase 1: Resolve all inputs for all module types
    all_resolved_inputs = resolve_all_inputs(result, aggregation_data, computed_attrs, ...)

    # Phase 2: Build all modules (pure construction, no side effects)
    modules = []
    modules.extend(build_calcusage_modules(result.required_usages, all_resolved_inputs, ...))
    modules.extend(build_formula_modules(computed_attrs, all_resolved_inputs, ...))
    modules.extend(build_aggregation_modules(aggregation_data, all_resolved_inputs, ...))

    # Phase 3: Collect and classify entry points
    unresolved = collect_unresolved_references(all_resolved_inputs)
    entry_points = classify_entry_points(unresolved, design_attrs, calc_defs)
    param_groups = group_entry_points(entry_points)

    # Phase 4: Sort and validate
    modules = topological_sort(modules)
    validate_channel_references(modules)

    return ComputationGraph(modules=modules, entry_point_groups=param_groups, ...)
```

**~50 lines instead of 172.** Every step is a named function. The data flow is visible. No mutable shared state.

### 4.5 Entry Point Classification

Today, entry points are identified during backtracking (scattered through `_trace_dependencies`), then classified in `graph_builder._classify_entry_points`, then mutated by `_build_computed_attr_module` and `_build_aggregation_module`, then regrouped.

After refactoring:

```python
# resolution/entry_point_classifier.py

def collect_unresolved_references(
    all_resolved_inputs: dict[str, dict[str, InputSource]],
) -> set[str]:
    """Find all references that resolved to entry_point."""
    return {
        inp.qualified_name
        for module_inputs in all_resolved_inputs.values()
        for inp in module_inputs.values()
        if inp.source_type == "entry_point"
    }

def classify_entry_points(
    unresolved: set[str],
    design_attrs: dict[str, DesignAttributeData],
    calc_def_map: dict[str, CalculationDefinitionData],
    entry_point_sources: dict[str, str],
) -> dict[str, EntryPoint]:
    """Classify each unresolved reference as DESIGN_ATTRIBUTE, LIBRARY_DEFAULT, or USAGE_LITERAL."""
    ...
```

**Why this is better:**
- Entry points are identified as a **consequence of resolution**, not a **side effect of module construction**.
- Classification happens **once**, not scattered across 3 functions.
- No mutation of a shared dict — the set is computed from resolution results.

### 4.6 Shared Topological Sort

Today there are two implementations of Kahn's algorithm. After refactoring, one in `core/`:

```python
# core/graph_algorithms.py

def topological_sort(
    nodes: list[str],
    edges: dict[str, list[str]],
) -> list[str]:
    """Kahn's algorithm topological sort. Raises CircularDependencyError on cycles."""
    ...
```

Both the backtracker and graph_builder use this.

---

## Part 5: Migration Strategy

### 5.1 Phase 0: Preparation (Non-Breaking)

1. **Create `core/graph_algorithms.py`** with the shared topological sort.
2. **Create `resolution/input_resolver.py`** with the unified resolver and strategy chain.
3. **Create `resolution/module_factory.py`** with the three build functions.
4. **Create `resolution/entry_point_classifier.py`** with classification logic.

All new files. No existing code changes. Write tests for all new modules.

### 5.2 Phase 1: Wire New Code (Incremental)

1. Modify `build_computation_graph()` to use the new resolver for **one module type** (start with CalcUsage — the simplest).
2. Run all 664+ tests. If they pass, proceed.
3. Migrate FORMULA modules to new resolver.
4. Migrate aggregation modules to new resolver.

### 5.3 Phase 2: Cleanup

1. Remove the old `_build_pipeline_module`, `_build_computed_attr_module`, `_build_aggregation_module` from graph_builder.py.
2. Move `initialization.py` out of `generation/` to `orchestration/`.
3. Remove duplicate topological sort from backtracker.
4. Delete dead code (the old functions, unused resolution paths).

### 5.4 Phase 3: Testing

1. **Matrix tests for the unified resolver**: all strategy × reference_type × registry_state combinations.
2. **Integration test**: full pipeline on solar_battery model, assert no `default_value=None` entry points.
3. **Property-based tests**: random combinations of term types × redefinition types → verify invariants.

---

## Part 6: Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Behavioral regression during migration | Wrong wiring in generated code | Phase 1 is incremental — one module type at a time. All 664+ tests must pass at each step. |
| Strategy chain ordering is wrong | Same class of bug we have today | But now it's **visible** — a list of named strategies, not nested if/elif. And testable with a truth table. |
| New SysML patterns still need new strategies | We'll still add code for new patterns | But adding a strategy to a list is O(1) risk. Adding a branch to a 230-line function is O(n) risk (interactions with existing branches). |
| `initialization.py` move breaks imports | Build failures | Do the move + update imports in one commit. Run mypy. |
| The resolver needs different strategies for different module types | Strategy chain isn't universal | Allow per-module-type strategy overrides: `resolve_input(ref, ctx, strategies=AGG_STRATEGIES)` |

---

## Part 7: What This Doesn't Fix

1. **sum() is still hardcoded.** The aggregation decomposer only handles `sum()`. Other aggregation functions (min, max, mean) will still produce `has_unsupported_nodes = True`. This is a domain limitation, not an architecture problem.

2. **The extraction layer's AST dispatch.** The existing refactoring plan (`.project/active/ast-dispatch-resolution-cleanup/design.md`) addresses this with `ASTNodeKind` + `classify_ast_node()`. That plan is complementary to this one and should proceed independently.

3. **Template expansion complexity.** Virtual CalcUsage creation from template PartDefs is in `initialization.py`'s `_rewrite_virtual_bindings()`. This is domain complexity that will move to the new orchestration module but won't be simplified by the resolution refactoring.

4. **Generation layer doesn't fully consume ComputationGraph.** Most generators still consume raw `CalculationDefinitionData`. Enriching ComputationGraph to carry all generation-needed data is a separate effort.

---

## Part 8: The Explainability Test

After this refactoring, the algorithm should be explainable as:

> **How does sysml-codegen work?**
>
> 1. **Extract** SysML files into structured data (calc definitions, calc usages, part hierarchy, design attributes).
>
> 2. **Build an output registry** — a lookup table mapping every possible reference to a canonical channel name.
>
> 3. **Resolve every input** of every module by trying strategies in order:
>    - Look up in the registry (direct match)
>    - Normalize the reference format and try again
>    - Follow any `:>>` chain redefinition and try again
>    - Match to a design attribute (becomes a user-provided entry point)
>    - If nothing works, it's a user-provided entry point
>
> 4. **Build modules** from the resolved inputs — one PipelineModule per calc usage, FORMULA attribute, and aggregation expression.
>
> 5. **Classify entry points** — everything that resolved to "user must provide" is categorized as design attribute, library default, or usage literal.
>
> 6. **Sort modules** in dependency order (topological sort).
>
> 7. **Render code** from the ComputationGraph — YAML pipeline, Python modules, JSON templates, Pydantic schemas.

Every step is one function. Every function is independently testable. The only step with combinatorial complexity (Step 3) has an explicit strategy chain that makes the precedence visible.

---

## Code References

### Resolution Layer
- `src/sysml_codegen/resolution/graph_builder.py` — 1282-line god module (the target)
- `src/sysml_codegen/resolution/models.py` — ComputationGraph and related Pydantic models
- `src/sysml_codegen/resolution/identifier_types.py` — re-export shim

### Analysis Layer
- `src/sysml_codegen/analysis/dependency_backtracker.py:462-535` — the 4-step resolution cascade
- `src/sysml_codegen/analysis/parameter_groups.py` — ParameterGroupDeriver and DesignAttributeData

### Generation Layer (misplaced orchestration)
- `src/sysml_codegen/generation/initialization.py` — 860 lines of orchestration code

### Core
- `src/sysml_codegen/core/output_registry.py` — the OutputRegistry
- `src/sysml_codegen/core/models.py` — BindingResolution, ChannelAlias

### Extraction Layer
- `src/sysml_codegen/extraction/hierarchy_resolver.py` — aggregation AST walking
- `src/sysml_codegen/extraction/expression_compiler.py` — expression compilation
- `src/sysml_codegen/extraction/data_models.py` — SumTerm, SingletonTerm, LocalTerm, RedefinitionData

---

## Recommendations

1. **Start with the unified resolver** (`input_resolver.py`). This is the highest-value change — it eliminates the class of bug where resolution logic is duplicated across 3-4 functions with subtle differences.

2. **Move `initialization.py` out of `generation/`** early. This is a pure file move + import update that clarifies the architecture immediately.

3. **Don't boil the ocean.** The extraction layer and generation layer are structurally sound. Focus the refactoring entirely on the resolution layer and the misplaced orchestration code.

4. **The existing AST dispatch plan is complementary.** The `classify_ast_node()` refactoring (in `.project/active/ast-dispatch-resolution-cleanup/design.md`) addresses a different bug class (dispatch ordering). It should proceed on its own timeline.

5. **Add the integration test.** "Regenerate solar_battery, assert no `default_value=None` entry points" should be an automated test. This catches bugs that unit tests miss.

## Open Questions

1. **Should the backtracker's resolution logic also be unified?** The backtracker's `_resolve_binding_via_registry` and the graph_builder's aggregation resolution do the same thing differently. Should the backtracker also use `resolve_input()`, or should it keep its own implementation since it has the DFS recursion concern?

2. **Should ComputationGraph be enriched to serve all generators?** Today, most generators bypass the graph. Is it worth adding `calc_def` references, compilation results, and import path data to PipelineModule so generators can consume only the graph?

3. **How to handle the backtracker's entry point discovery?** Currently the backtracker discovers entry points during DFS tracing. In the new architecture, should it just mark unresolved references and let the classifier handle them downstream?
