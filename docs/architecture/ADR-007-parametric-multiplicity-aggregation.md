# ADR-007: Parametric Multiplicity and Aggregation

## Status
**Accepted** - 2026-02-10

## Context

Assembly parts in the Costed Component pattern aggregate costs from child parts, some of which are arrays with multiplicity. For example, `Solar Array` contains `pv_module : 'PV Module' [module_count]` (20 instances) and aggregates their costs via `sum(pv_module.capital_cost)`.

Two strategies exist for handling arrayed children:

1. **Flat expansion**: Generate N individual modules (one per array element), each with its own parameter bindings. Correct for non-uniform arrays where each instance has different parameters.

2. **Parametric multiply**: Generate 1 module per array child type, multiply its output by the count. Correct for uniform arrays where all instances share the same parameters.

The solar_battery model uses uniform arrays exclusively — all 20 PV modules have the same wattage, efficiency, and cost parameters. Flat expansion would generate 20 identical modules, wasting computation and complicating the pipeline.

A spike (Item 1) confirmed that SysIDE provides:
- Multiplicity via `PartUsage.multiplicity` (`MultiplicityRange` with bounds)
- `sum()` as `InvocationExpression` with `function.name='sum'` and a `FeatureChainExpression` operand
- Default values via `feature_value.is_default=True` on multiplicity attributes

## Decision

### Decision 1: Parametric Multiply Strategy

For uniform arrays, `sum(child.attribute)` transforms to `count * child.attribute` at compile time. This produces one aggregation module per assembly attribute (not N modules per array element).

**Example:**
```
sum(pv_module.capital_cost) → module_count * pv_module__cost_model.total_cost
```

Multiplicity counts become Integer entry points in parameter schemas, defaulting to the PartDef-declared value.

**Result:** O(assemblies × attributes) modules instead of O(assemblies × max_children × attributes).

### Decision 2: `sum()` Transformation

The expression compiler transforms `sum()` invocations during aggregation expression processing:

1. **Detect**: `InvocationExpression` with `function.name == 'sum'`
2. **Extract**: Single operand is a `FeatureChainExpression` — extract `part_usage_name` and `attribute_name`
3. **Resolve**: Map `part_usage_name.attribute_name` through `:>>` redefinition chains to find the upstream MODULE_OUTPUT channel
4. **Transform**: Replace `sum(part.attr)` with `count_param * resolved_channel` in the compiled expression

Non-array children (singletons) are referenced directly without multiplication.

### Decision 3: Synthetic Aggregation Module Generation

One `PipelineModule` is generated per (aggregation expression, design instance) pair:

- **`ScopedAggregationData`** composes an `AggregationExpressionData` with an `instance_path`, scoping the expression to a specific design assembly
- **Module EQN**: `{instance_path}__{attribute_name}` (e.g., `solar_battery_plant__solar_array__capital_cost`)
- **`is_aggregation = True`** flag on the PipelineModule
- **YAML comment**: `# source: aggregation ({module_type})` for debuggability
- **Auto-implementation**: The compiled expression is directly executable Python

### Decision 4: AggregationExpressionData Model

Each aggregation expression is decomposed into three term types:

- **`sum_terms`**: Array children with multiplicity — `(part_usage_name, attribute_name, multiplicity_attr, multiplicity_count)`
- **`singleton_terms`**: Non-multiplied children — direct attribute reference via `source_path`
- **`local_terms`**: PartDef-local attributes (e.g., `misc_hardware_cost`) — resolved via alias or MODULE_OUTPUT wiring

The `transformed_expression` field contains the Python-compilable string after parametric multiply transformation. `has_unsupported_nodes` indicates whether all terms were successfully resolved.

### Decision 5: Uniform-Array Assumption

All instances in an array share the same parameter bindings. This assumption is:

- **Required**: Design overrides apply uniformly (`:>> pv_module.wattage = 400.0` applies to all 20 modules)
- **Validated**: The solar_battery model satisfies this — all arrayed PartUsages have uniform parameters
- **Documented**: Non-uniform arrays (different parameters per instance) require flat expansion, which is not implemented. Modelers needing non-uniform arrays should use Approach E (explicit CalcDef with multiplicity as input parameter and per-instance outputs).

## Consequences

### Positive
- O(assemblies × attributes) modules, not O(assemblies × max_children × attributes)
- Auto-implementable aggregation with simple multiply-and-sum expressions
- Multiplicity counts are parameterizable via JSON inputs (users can change array sizes without modifying SysML)
- Zero implementation backlog for aggregation modules in the solar_battery model

### Negative
- Uniform-array assumption limits applicability to non-uniform designs
- Non-uniform arrays require manual Approach E workaround (explicit CalcDef)
- Singleton term compilation currently produces `.(inputs.xxx)` syntax for some FeatureReferenceExpressions — 16 of 20 aggregation cost impls are syntactically invalid Python (the 4 idiot_index impls, which use only local terms, are valid)

## References

- **Spike Q4-Q6**: `.project/active/hierarchy-spike/report.md` — `sum()` InvocationExpression structure, multiplicity bounds, expression tree traversal
- **Item 3**: commit `7887d07` — Redefinition extraction, multiplicity detection, aggregation expression compilation
- **Item 4**: commit `f49005c` — Pipeline integration for aggregation module generation
- **`ScopedAggregationData`**: `src/sysml_codegen/generation/initialization.py`
- **`AggregationExpressionData`**: `src/sysml_codegen/extraction/data_models.py`

## Changelog

| Date | Change |
|------|--------|
| 2026-02-10 | Initial version |
