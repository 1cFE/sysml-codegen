# 24 -- Dual Resolution Architecture: CalcUsage vs Aggregation Paths

## The One Question, Two Answers

Both paths answer: "Where does this input come from?" But they operate on
different input types with different strategies.

| Aspect | CalcUsage Path | Aggregation Path |
|--------|---------------|-----------------|
| Entry point | `_resolve_binding_via_registry()` | `_resolve_aggregation_input_channel()` |
| File | `analysis/dependency_backtracker.py:462` | `resolution/graph_builder.py:760` |
| Input type | `BindingInfo` (from CalcUsageData) | Term types (SumTerm, SingletonTerm, LocalTerm) |
| Output type | `BindingResolution` object | `str \| None` (channel name) |
| When | Backtracking phase (before graph) | Graph building phase (during module construction) |

---

## CalcUsage Path: 4-Stage Resolution

Resolves calc usage parameter bindings to upstream module outputs or entry points.

```
Stage 1: Direct registry lookup
          registry.resolve(binding.source_path)
          → channel or None

Stage 1b: Normalize SysML QN
          "Package::Part::attr" → "package.part.attr"
          registry.resolve(normalized)
          → channel or None

Stage 2: REFERENCE secondary resolution
          (only for REFERENCE bindings)
          Extract leaf name, combine with parent scope
          → channel or None

Stage 3: Design attribute transitive
          Match source_path to DesignAttributeData
          → ENTRY_POINT (design attribute becomes the value source)

Stage 4: Fallback entry point
          → ENTRY_POINT with warning (all else failed)
```

**Result**: `BindingResolution(resolution_type, qualified_name, source_path, is_transitive)`

Stored in `BacktrackingResult.binding_resolutions` dict keyed by
`"{usage_qn}|{param_name}"`. Consumed later by `_build_pipeline_module()`.

---

## Aggregation Path: Term-Type Resolution

Resolves aggregation expression terms to upstream channels or entry points.

### SumTerms and SingletonTerms

```
Stage 1: CHAIN redefinition lookup
          Match part_usage.attr to RedefinitionData where type=CHAIN
          Follow source_path chain (with cycle guard)
          → channel or None

Stage 2: Scoped registry lookup
          Strip design prefix from instance_path
          Build scoped key: "scope.part_usage.attribute"
          registry.resolve(scoped_key)
          → channel or None

Stage 3: Unscoped Key_D fallback
          catalog_key: "part_usage.attribute"
          registry.resolve(catalog_key)
          → channel or None

Fallback: LITERAL :>> redefinition check
          _find_literal_redefinition(part_usage, attr, ...)
          → float (becomes entry point default) or None
          → If None: entry point with MANUAL_REQUIRED
```

### LocalTerms (same-PartDef attributes)

```
Strategy 1: Sibling aggregation output
            Build sibling_eqn = "{instance_path}__{attr}"
            Check "{sibling_eqn}__{attr}" in canonical_channels
            → module_output or None

Strategy 2: EXPOSE_PURE alias
            expose_aliases map provides dotted path
            _resolve_aggregation_input_channel(dotted_path, ...)
            → module_output or None

Strategy 3: Entry point fallback
            → entry point (user provides value)
```

---

## Shared Infrastructure: OutputRegistry

Both paths converge on `OutputRegistry.resolve(key) -> str | None`:

```python
# core/output_registry.py:107-124
def resolve(self, key: str) -> str | None:
    return self._lookup.get(key)
```

Pure dict lookup, no normalization, no fallback. Keys are registered during
Phase 1-4 of the registry protocol (see doc 10).

**CalcUsage** passes `binding.source_path` as key (Stages 1-2).
**Aggregation** passes scoped or catalog keys (Stages 2-3).

Both use `canonical_channels` (`frozenset` of all registered channels) for
existence checks, but aggregation uses it explicitly while CalcUsage relies
on `resolve()` returning `None`.

---

## Why Two Paths Exist

### Different Input Types

CalcUsage bindings are `BindingInfo` objects with `source_path`, `binding_type`,
and `literal_value`. Aggregation terms are `SumTerm(part_usage, attribute)`,
`SingletonTerm(source_path)`, or `LocalTerm(attribute)`.

### Different Domain Strategies

| Strategy | CalcUsage | Aggregation |
|----------|-----------|-------------|
| REFERENCE secondary | Yes | No |
| Design attr transitive | Yes | No |
| CHAIN recursion | No | Yes |
| Scoped key construction | No | Yes |
| LocalTerm sibling | No | Yes |
| EXPOSE_PURE alias | No | Yes |
| LITERAL fallback | No | Yes |

CHAIN recursion traces `:>>` redefinition chains through part hierarchy --
only meaningful for aggregation where `pv_module.capital_cost` might
redirect through `cost_model.total_cost`. CalcUsage bindings are direct.

### Different Output Designs

CalcUsage produces `BindingResolution` objects stored in a persistent dict
for inter-stage consumption. Aggregation returns channel strings consumed
immediately by `_build_aggregation_module()`.

### Different Timing

CalcUsage resolution happens during the backtracking phase (before graph
construction). Aggregation resolution happens during graph construction
(Step 6.7 in `build_computation_graph()`).

---

## Concrete Trace: Same Reference, Both Paths

**Reference**: `"solar_array.capital_cost"` (an aggregation output channel)

### CalcUsage Path (if this were a binding)

```
_resolve_binding_via_registry("solar_array.capital_cost", ...)
  Stage 1: registry.resolve("solar_array.capital_cost")
           → HIT: "Design__solar_array__capital_cost__capital_cost"
  Return: BindingResolution(MODULE_OUTPUT,
           "Design__solar_array__capital_cost__capital_cost")

_build_pipeline_module():
  InputSource(source_type="module_output",
              producer_channel="Design__solar_array__capital_cost__capital_cost")
```

### Aggregation Path (SingletonTerm)

```
_resolve_aggregation_input_channel("solar_array.capital_cost",
                                    "Design__plant", ...)
  Stage 1 (CHAIN): No match in redefinitions
  Stage 2 (Scoped): scoped_key="plant.solar_array.capital_cost"
                     registry.resolve() → MISS
  Stage 3 (Unscoped): catalog_key="solar_array.capital_cost"
                       registry.resolve() → HIT
  Return: "Design__solar_array__capital_cost__capital_cost"

_build_aggregation_module():
  InputSource(source_type="module_output",
              producer_channel="Design__solar_array__capital_cost__capital_cost")
```

**Result**: Both paths produce identical `InputSource` wiring.

---

## Data Flow Summary

```
CalcUsage:
  CalcUsageData.bindings[]
    → _resolve_binding_via_registry()
    → BindingResolution
    → BacktrackingResult.binding_resolutions["{usage}|{param}"]
    → _build_pipeline_module()
    → ModuleInput(source=InputSource(...))

Aggregation:
  ScopedAggregationData.expression.{sum,singleton,local}_terms
    → _resolve_aggregation_input_channel()
    → str (channel) | None
    → _build_aggregation_module()
    → ModuleInput(source=InputSource(...))
```

---

## Data Models

| Model | File | Role |
|-------|------|------|
| `BindingResolution` | `core/models.py` | CalcUsage resolution result |
| `BindingInfo` | `extraction/data_models.py` | Calc usage binding |
| `SumTerm` | `extraction/data_models.py` | `sum(part.attr * count)` |
| `SingletonTerm` | `extraction/data_models.py` | `part.attr` (no sum) |
| `LocalTerm` | `extraction/data_models.py` | Same-PartDef attribute |
| `RedefinitionData` | `extraction/data_models.py` | `:>>` CHAIN/LITERAL/EXPRESSION |
| `OutputRegistry` | `core/output_registry.py` | Shared lookup table |
| `BacktrackingResult` | `analysis/dependency_backtracker.py` | CalcUsage resolution store |
