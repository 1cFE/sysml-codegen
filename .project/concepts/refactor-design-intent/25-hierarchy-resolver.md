# 25 - Hierarchy Resolver

## What Problem It Solves

SysML v2 models express structural patterns — `:>>` redefinitions, child
multiplicity, `sum()` aggregation — that plain CalcUsage extraction ignores.
These patterns define HOW parts are assembled and HOW computed attributes
roll up through the hierarchy. Without extracting them, the pipeline cannot
generate aggregation modules, propagate literal overrides, or wire
parametric-multiply expressions.

The hierarchy resolver (`extraction/hierarchy_resolver.py`) is a **pure
extraction module** — it walks the SysIDE AST, classifies structural
patterns into typed data structures, and returns them for downstream
consumption. It does NOT resolve bindings or build modules.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-HR-01 | Every `:>>` redefinition SHALL be classified as exactly one [RedefinitionType](09-data-models.md) from {LITERAL, CHAIN, EXPRESSION} | `all(r.redefinition_type in RedefinitionType for r in redefs)` |
| REQ-HR-02 | Both `FeatureChainExpression` and `FeatureReferenceExpression` value expressions SHALL produce `RedefinitionType.CHAIN` | Lines 105-125: both FCE and FRE map to CHAIN |
| REQ-HR-03 | Deep-path redefinitions SHALL set `is_deep_path=True` and populate `target_path` from `chaining_features` | Line 78: `chaining_features` list → target_path segments |
| REQ-HR-04 | Multiplicity extraction SHALL use `cached_lower_bound` (not `cached_upper_bound`) due to SysIDE exclusive upper-bound convention | Line 221: `getattr(mult, "cached_lower_bound", None)` |
| REQ-HR-05 | `_walk_aggregation_ast()` SHALL check `FeatureChainExpression` BEFORE `OperatorExpression` per [AST dispatch invariant](19-ast-dispatch-invariant.md) | Lines 331-338: FCE check precedes OE check |
| REQ-HR-06 | `sum(child.attr)` SHALL be transformed to `(count_attr * child.attr)` using the `mult_lookup` dict | Lines 382-391: multiplicity_attr from mult_lookup |
| REQ-HR-07 | CHAIN-type sibling redefinitions that reference the aggregation attribute SHALL be added as aliases | Lines 550-557: `source_path.endswith(agg.attribute_name)` |

## The 4 Extraction Phases

`extract_hierarchy_data()` (line 490) orchestrates four phases per PartDef:

| Phase | Function | Input | Output |
|-------|----------|-------|--------|
| 1 | `extract_redefinitions()` | PartDef element | `list[RedefinitionData]` |
| 2 | `extract_design_overrides()` | Design PartUsages | `list[RedefinitionData]` (deep-path only) |
| 3 | `extract_multiplicities()` | PartDef element | `list[MultiplicityData]` |
| 4 | `build_aggregation_expression()` | EXPRESSION redefs + multiplicities | `list[AggregationExpressionData]` |

Additionally, the orchestrator builds two lookup structures:
- `part_usage_names: dict[str, set[str]]` — child PartUsage names per PartDef, used by [aggregation scoping](13-aggregation-scoping.md) for instance discovery
- `usage_type_map: dict[tuple[str, str], str]` — `(owning_qn, usage_name) → type_partdef_qn`, used by [literal value propagation](18-literal-value-propagation.md) to find redefinition defaults

## Phase 1: Redefinition Classification

`extract_redefinitions()` (line 139) scans a PartDef's `owned_members` for
`ReferenceUsage` elements with non-empty `owned_redefinitions`. Each is
classified by its right-hand-side expression via `_extract_single_redefinition()`:

```
:>> wattage = 400.0                    → LITERAL  (is_literal_expression)
:>> total_capex = capital_cost         → CHAIN    (FeatureReferenceExpression)
:>> total_capex = cost_model.total_cost → CHAIN   (FeatureChainExpression)
:>> capital_cost = sum(pv.capex) + bos → EXPRESSION (anything else)
```

Note: both FCE and FRE produce `CHAIN` type (REQ-HR-02). The distinction
between dotted-path and bare-name references is preserved in `source_path`
but the classification is the same.

**Deep-path detection** (REQ-HR-03): When the AST's `redefined_feature` has
`chaining_features`, the redefinition targets a nested attribute. Example:

```sysml
part solar_battery_plant : Solar_Battery_Plant {
    :>> pv_module.wattage = 400.0;   /* deep path: ["pv_module", "wattage"] */
}
```

This sets `is_deep_path=True` and `target_path=["pv_module", "wattage"]`.
Deep-path redefinitions are consumed by [virtual binding rewrite](12-virtual-binding-rewrite.md)
to override inherited values at specific hierarchy positions.

**Type-only redefinitions** (no `feature_value_expression`) are skipped — they
declare type constraints, not value overrides.

## Phase 2: Design Override Extraction

`extract_design_overrides()` (line 162) scans design-level PartUsages for
`:>>` overrides. Unlike Phase 1 (which scans PartDef members), this scans
PartUsage elements that have `owned_redefinitions` — these are "part redefines"
instances where the design overrides library defaults.

The caller ([orchestration](02-orchestration.md)) is responsible for
providing the PartUsage elements. Design overrides become the
`design_overrides` field on [HierarchyExtractionResult](09-data-models.md).

## Phase 3: Multiplicity Extraction

`extract_multiplicities()` (line 195) detects child PartUsages with multiplicity
annotations. This data is CRITICAL for Phase 4: without multiplicity, `sum()`
cannot be transformed to parametric multiply.

**The SysIDE lower-bound convention** (REQ-HR-04): SysIDE's `cached_upper_bound`
is exclusive (N+1 for a `[N]` multiplicity), so we use `cached_lower_bound`
which gives the correct count. This was confirmed by spike Q5.

For a SysML declaration like:
```sysml
part def Solar_Array {
    attribute module_count : Integer = 20;
    part pv_module : PV_Module[module_count];
}
```

The extractor produces:
```python
MultiplicityData(
    part_usage_name="pv_module",
    owning_part_def_qn="SolarLib::Solar_Array",
    count=20,
    count_attribute_name="module_count",  # from upper_bound.referent
    default_value=20,                     # from referent's feature_value_expression
)
```

The `count_attribute_name` is extracted from `mult.upper_bound.referent.name` —
the actual attribute that controls the count. This becomes an entry point in the
generated pipeline (the user can change `module_count` at runtime).

Singletons (no multiplicity attribute) are excluded from the output.

## Phase 4: Aggregation Transformation

`build_aggregation_expression()` (line 439) takes an EXPRESSION-type
redefinition and transforms it into an [AggregationExpressionData](09-data-models.md).

### The mult_lookup Mechanism

First, a lookup dict is built from Phase 3 multiplicities:
```python
mult_lookup = {m.part_usage_name: m for m in multiplicities}
# e.g. {"pv_module": MultiplicityData(count=20, count_attribute_name="module_count")}
```

This is passed to `_walk_aggregation_ast()` which uses it to detect aggregated
parts and transform `sum()` calls.

### AST Walking and Term Classification

`_walk_aggregation_ast()` (line 305) recursively walks the expression AST.
The dispatch order follows the [AST dispatch invariant](19-ast-dispatch-invariant.md):

| Priority | AST Type | Classification | Example |
|----------|----------|----------------|---------|
| 1 | `FeatureChainExpression` | **SingletonTerm** | `inverter.install_cost` |
| 2 | `OperatorExpression` | recurse into operands | `a + b` |
| 3 | `FeatureReferenceExpression` | **LocalTerm** | `misc_cost` |
| 4 | InvocationExpression (`sum`) | **SumTerm** | `sum(pv.capital_cost)` |
| 4b | InvocationExpression (wrapper) | unwrap and retry | `Evaluation(expr)` |
| 5 | Literal | pass through | `1.05` |

**SumTerm creation** (REQ-HR-06): When `sum(child.attr)` is found, the
`child` part is looked up in `mult_lookup`. If multiplicity exists:
```
sum(pv_module.capital_cost) → (module_count * pv_module.capital_cost)
```
producing `SumTerm(part_usage_name="pv_module", attribute_name="capital_cost",
multiplicity_attr="module_count", multiplicity_count=20)`.

If multiplicity is missing, a warning is logged and an unresolved SumTerm
(with `multiplicity_attr=None`) is emitted.

**Wrapper unwrapping**: SysIDE sometimes wraps expressions in
`Evaluation`, `evaluate`, `collect`, or `select` InvocationExpressions.
The `_unwrap_invocation()` helper (line 278) peels these off recursively
(max depth 3) to reach the inner FCE/FRE node.

### Alias Detection (REQ-HR-07)

After building an `AggregationExpressionData`, the orchestrator scans sibling
redefinitions for CHAIN-type aliases. If a sibling's `source_path` ends with
the aggregation's `attribute_name` and has a different name, it's an alias:

```sysml
:>> capital_cost = sum(pv_module.capital_cost) + bos_cost;  /* aggregation */
:>> total_capex = capital_cost;                              /* alias */
```

Here `total_capex` becomes an alias for the `capital_cost` aggregation,
registered in the [output registry](10-output-registry.md) as a Phase 2
CHAIN alias.

> **Coverage note (C06 conformance + C5 probe, 2026-02-17)**: The positive
> case for alias detection is exercised by `alias_agg_probe` fixture
> (`:>> reported_cost = total_cost` → `agg.aliases = ["reported_cost"]`).
> **Edge case**: The `endswith()` check on `source_path` may false-positive
> on dotted source_paths (e.g., `parent.capital_cost` would match
> `attribute_name="capital_cost"`). This is not triggered by any current
> fixture but could produce spurious aliases for hierarchical CHAIN
> redefinitions.

## Concrete Example

Given this SysML:
```sysml
part def Solar_Array {
    attribute module_count : Integer = 20;
    part pv_module : PV_Module[module_count];
    :>> capital_cost = sum(pv_module.capital_cost) + inverter.install_cost + misc_cost;
    :>> total_capex = capital_cost;
}
```

**Phase 1** produces 2 redefinitions:
- `RedefinitionData(attribute_name="capital_cost", type=EXPRESSION, expression_ast=<node>)`
- `RedefinitionData(attribute_name="total_capex", type=CHAIN, source_path="capital_cost")`

**Phase 3** produces:
- `MultiplicityData(part_usage_name="pv_module", count=20, count_attribute_name="module_count")`

**Phase 4** transforms the EXPRESSION redefinition:
```python
AggregationExpressionData(
    attribute_name="capital_cost",
    sum_terms=[SumTerm("pv_module", "capital_cost", "module_count", 20)],
    singleton_terms=[SingletonTerm("inverter.install_cost")],
    local_terms=[LocalTerm("misc_cost")],
    transformed_expression="(module_count * pv_module.capital_cost) + inverter.install_cost + misc_cost",
    aliases=["total_capex"],  # from CHAIN sibling detection
)
```

## Data Models

| Type | Location | Role |
|------|----------|------|
| [`RedefinitionData`](09-data-models.md) | `extraction/data_models.py` | Single `:>>` with type, value, target_path |
| [`MultiplicityData`](09-data-models.md) | `extraction/data_models.py` | Child count + count_attribute_name |
| [`AggregationExpressionData`](09-data-models.md) | `extraction/data_models.py` | Decomposed aggregation with SumTerm/SingletonTerm/LocalTerm |
| [`HierarchyExtractionResult`](09-data-models.md) | `extraction/data_models.py` | Top-level container for all hierarchy data |

## Related Documents

- **Upstream**: [00-pipeline-overview](00-pipeline-overview.md) — Step 1 in the pipeline
- **Upstream**: [01-extraction](01-extraction.md) — extraction layer overview; Section 4 references this module
- **Downstream**: [02-orchestration](02-orchestration.md) — consumes HierarchyExtractionResult at Step 3.5
- **Downstream**: [12-virtual-binding-rewrite](12-virtual-binding-rewrite.md) — uses design_overrides for hierarchy overrides
- **Downstream**: [13-aggregation-scoping](13-aggregation-scoping.md) — uses aggregation expressions + part_usage_names
- **Downstream**: [18-literal-value-propagation](18-literal-value-propagation.md) — uses usage_type_map for type-aware defaults
- **Cross-cutting**: [19-ast-dispatch-invariant](19-ast-dispatch-invariant.md) — FCE-before-OE ordering rule
- **Data models**: [09-data-models](09-data-models.md) — full field definitions for all hierarchy types
