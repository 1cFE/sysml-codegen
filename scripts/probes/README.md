# Diagnostic Probe Scripts

These scripts probe the real SysIDE AST structure for the solar_battery model to verify assumptions that mock-based tests may have gotten wrong.

## Running

All scripts are standalone and can be executed with:

```bash
uv run python scripts/probes/<script_name>.py
```

## Scripts

### probe_sum_ast_structure.py

Maps the FULL nesting structure of `sum()` InvocationExpression nodes. SysIDE may wrap `sum()` operands in an `InvocationExpression(function.name='Evaluation')` node that our code does not handle. This script finds ALL `sum()` invocations and recursively prints the exact AST path down to the terminal FeatureChainExpression or FeatureReferenceExpression leaf.

Key questions answered:
- What is the exact AST path from sum() to the actual feature reference?
- Is there an Evaluation wrapper? A collect wrapper?
- Does our `_unwrap_invocation()` handle the real structure?

### probe_redefinition_structure.py

Maps all `:>>` redefinition ReferenceUsage members across every PartDefinition. For each, prints the owning PartDef, redefined feature name, chaining_features, expression type, and value. Focuses on finding two patterns:
- `:>> total_capex = capital_cost` (ALIAS pattern: one attribute points to another)
- `:>> capital_cost = sum(...)` (AGGREGATION pattern: sum-based rollup)

Also scans design-level PartUsages for deep-path overrides like `:>> pv_module.wattage = 400.0`.

### probe_alias_resolution.py

Verifies alias resolution end-to-end. Divided into three parts:
1. Raw AST analysis of Solar Battery Plant redefinitions to find alias relationships
2. hierarchy_resolver.py output inspection (aliases list on AggregationExpressionData)
3. Full pipeline wiring check to ensure annualized_financial's `total_capex` input resolves to the correct aggregation module output

Critical path: `in total_capex = capital_cost` in design.sysml must wire to the capital_cost aggregation module output.

### probe_multiplicity_structure.py

Maps multiplicity structure on child PartUsages within each PartDef. Prints:
- Multiplicity object type and all accessible attributes
- cached_lower_bound vs cached_upper_bound (verifies exclusive upper bound convention)
- upper_bound referent chain (name, feature_value_expression, default value)
- Sibling count attributes (module_count, inverter_count, pack_count)
- Cross-checks against hierarchy_resolver's MultiplicityData output

### probe_backtracker_resolution.py

Runs the full pipeline via `build_pipeline_context()` and inspects:
1. All modules in the computation graph with is_aggregation flags
2. All scoped aggregation expressions with instance paths and module EQNs
3. Deep dive into the annualized_financial module's inputs and source types
4. Tracking of "total_capex" and "capital_cost" through the entire pipeline
5. Entry point groups and their parameters
6. Pipeline integrity checks: broken wires, missing entry points, LCOE chain completeness
