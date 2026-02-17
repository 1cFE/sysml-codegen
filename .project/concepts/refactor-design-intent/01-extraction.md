# Step 1: Extraction

Extraction reads SysML v2 model files (via the SysIDE adapter from agentic-mbse),
walks the parsed AST, and produces structured Python dataclasses. No analysis,
resolution, or generation happens here -- it is a pure data-harvesting step.
Source: `src/sysml_codegen/extraction/`

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-EXT-01 | Extraction SHALL produce exactly one [CalculationDefinitionData](09-data-models.md#extraction-models) per `calc def` in the SysML model. | `len(calc_defs) == count(CalcDef elements in AST)` |
| REQ-EXT-02 | Every parameter binding on a [CalcUsageData](09-data-models.md#extraction-models) SHALL have exactly one [BindingType](#binding-types) from {CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND}. | `all(b.binding_type in BindingType for u in usages for b in u.bindings)` |
| REQ-EXT-03 | Every `:>>` redefinition SHALL be classified as exactly one [RedefinitionType](#redefinitions-redefinitiondata) from {LITERAL, CHAIN, EXPRESSION}. | `all(r.redefinition_type in RedefinitionType for r in redefinitions)` |
| REQ-EXT-04 | Every aggregation expression SHALL be decomposed into typed terms: [SumTerm, SingletonTerm, LocalTerm](#aggregation-data-sumterm-singletonterm-localterm). | `all(len(a.sum_terms) + len(a.singleton_terms) + len(a.local_terms) > 0 for a in agg_exprs)` |
| REQ-EXT-05 | Template calc usages (`is_template=True`) SHALL produce one virtual [CalcUsageData](09-data-models.md#extraction-models) per PartUsage that instantiates the owning PartDef. | Count virtual usages == count of design-level PartUsage instances of that PartDef |
| REQ-EXT-06 | Extraction SHALL NOT import from `analysis/`, `resolution/`, or `generation/`. | Static import analysis of `extraction/` package |
| REQ-EXT-07 | `output_expression_asts` SHALL preserve raw SysIDE AST nodes for downstream [expression compilation](14-expression-compiler.md). | Nodes are stored as `Any` and passed unchanged to `compile_calc_def()` |

## The 4 Things Extracted

### 1. Calculation Definitions ([CalculationDefinitionData](09-data-models.md#extraction-models))

A calc def is a reusable formula. SysML input:
```sysml
calc def battery_cost_calc {
    in capacity : Real;  in unit_cost : Real;
    return total_cost : Real = capacity * unit_cost;
}
```

Key fields (see [09-data-models](09-data-models.md#extraction-models) for full spec):

| Field | Example | Consumed by |
|-------|---------|-------------|
| `name` | `"battery_cost_calc"` | [Module factory](05-module-factory.md): module_type derivation |
| `qualified_name` | `"SolarLib::battery_cost_calc"` | [Naming conventions](15-naming-conventions.md): EQN/PQN |
| `input_attributes` | `[AttributeInfo(name="capacity", ...)]` | [Input resolver](04-input-resolver.md): what needs wiring |
| `output_attributes` | `[AttributeInfo(name="total_cost", ...)]` | [Output registry](10-output-registry.md): channel registration |
| `output_expression_asts` | `{"total_cost": <raw AST>}` | [Expression compiler](14-expression-compiler.md): Python codegen |
| `all_member_names` | `{"capacity", "unit_cost", "total_cost"}` | [Expression compiler](14-expression-compiler.md): intermediate detection |

### 2. Calculation Usages ([CalcUsageData](09-data-models.md#extraction-models))

A calc usage instantiates a calc def with specific bindings. SysML input:
```sysml
part def SolarBattery {
    attribute capacity : Real = 100.0;
    calc battery_cost : battery_cost_calc {
        in capacity = SolarBattery::capacity;  in unit_cost = 4.5;
    }
}
```

Key fields:

| Field | Example | Consumed by |
|-------|---------|-------------|
| `instance_name` | `"battery_cost"` | [Naming](15-naming-conventions.md): used in EQN construction |
| `calc_def_name` | `"battery_cost_calc"` | [Module factory](05-module-factory.md): calc def lookup |
| `qualified_name` | `"solar_battery_plant__solar_battery__battery_cost"` | [Naming](15-naming-conventions.md): EQN |
| `bindings` | `[BindingInfo(param_name="capacity", ...)]` | [Backtracker](11-analysis-backtracker.md): resolution |
| `is_template` | `True` (if owned by a PartDef) | [Virtual binding rewrite](12-virtual-binding-rewrite.md) |

Template calc usages (REQ-EXT-05) are expanded: for each PartUsage instantiating
the owning PartDef, a virtual CalcUsageData is created with a design-relative
qualified name. See [12-virtual-binding-rewrite](12-virtual-binding-rewrite.md).

### 3. Part Definitions ([PartDefinitionData](09-data-models.md#extraction-models))

Part definitions model the structural hierarchy. Literal attribute values like
`voltage = 48.0` become design attributes -- user-configurable inputs in the
generated pipeline. See [17-parameter-group-deriver](17-parameter-group-deriver.md).

**Note**: [ComputedAttributeData](16-computed-attributes.md) is also produced
during extraction (from PartDef attribute expressions). See doc 16 for details.

> **Data gap (C3 finding, 2026-02-17)**: PartDefinitionData does not currently
> include **supertype chain information** (ancestor PartDef QNs). This data is
> needed by the downstream computed attribute classifier (C05) to correctly
> classify inherited attribute references as sibling refs instead of external
> calc refs. SysIDE provides supertype information via `part_element.types`,
> but it is not extracted or stored. See [16-computed-attributes](16-computed-attributes.md)
> Known Issues §Inherited Attribute Misclassification (Deferred Issue #9).

### 4. Hierarchy Data ([HierarchyExtractionResult](09-data-models.md#extraction-models))

`extract_hierarchy_data()` returns structural patterns beyond simple attributes:
`redefinitions`, `design_overrides`, `multiplicities`, `aggregation_expressions`,
`part_usage_names`, `usage_type_map`, `warnings`. See
[25-hierarchy-resolver](25-hierarchy-resolver.md) for the full 4-phase
decomposition. Consumed by [orchestration](02-orchestration.md) for registry
building, virtual binding rewrite, and aggregation scoping.

---

## Binding Types

Each parameter binding on a CalcUsageData is a `BindingInfo` classified by
`BindingType` (REQ-EXT-02). All five types:

**CHAIN** -- dotted path to another element's attribute:
```sysml
in capacity = solar_array.rated_capacity;
```
`BindingInfo(param_name="capacity", source_path="solar_array.rated_capacity", binding_type=CHAIN)`

**REFERENCE** -- direct reference to a sibling/ancestor attribute:
```sysml
in capacity = rated_capacity;
```
`BindingInfo(param_name="capacity", source_path="SolarLib::SolarBattery::rated_capacity", binding_type=REFERENCE)`

**LITERAL** -- hardcoded constant:
```sysml
in unit_cost = 4.5;
```
`BindingInfo(param_name="unit_cost", source_path="4.5", binding_type=LITERAL, literal_value=4.5)`

**EXPRESSION** -- computed value (OperatorExpression in the AST):
```sysml
in adjusted_cost = base_cost * inflation_factor;
```
`BindingInfo(param_name="adjusted_cost", source_path=None, binding_type=EXPRESSION, expression_ast=<node>)`

> **Coverage note (C03 conformance, 2026-02-17)**: EXPRESSION binding type has
> **zero coverage** in all natural fixture models (solar_battery, catf_mfe, sample,
> issue22, attr_expr_probe, alias_agg_probe). No calc usage in any fixture binds
> a parameter to an inline expression. Coverage is provided by the synthetic
> `expression_binding_probe` fixture. The backtracker handles EXPRESSION bindings
> by creating an ENTRY_POINT with a warning (see
> [11-analysis-backtracker](11-analysis-backtracker.md)).

**UNBOUND** -- no binding expression at all. These appear in
`CalcUsageData.unbound_params` as string names (not in the `bindings` list).
The backtracker processes `unbound_params` separately after the binding loop
(see [11-analysis-backtracker](11-analysis-backtracker.md)).

---

## Redefinitions ([RedefinitionData](09-data-models.md#extraction-models))

A `:>>` redefinition overrides an inherited attribute (REQ-EXT-03). Three types:

**LITERAL**: `:>> wattage = 400.0;` -- value override. Used by
[literal value propagation](18-literal-value-propagation.md).

**CHAIN**: `:>> total_capex = capital_cost;` -- delegation. Creates a Phase 2
alias in the [output registry](10-output-registry.md#phase-2----chain-aliases).

**EXPRESSION**: `:>> capital_cost = sum(pv_module.capital_cost) + bos_cost;` --
computed aggregation. Decomposed into typed terms (below).

Deep-path overrides (e.g., `:>> pv_module.wattage = 400.0`) are captured in
`design_overrides` with `is_deep_path=True` and `target_path=["pv_module", "wattage"]`.

---

## Aggregation Data ([SumTerm, SingletonTerm, LocalTerm](09-data-models.md#extraction-models))

When an EXPRESSION redefinition contains `sum()`, the hierarchy resolver
decomposes it into typed terms (REQ-EXT-04). Given:
```sysml
:>> capital_cost = sum(pv_module.capital_cost) + inverter.install_cost + misc_cost;
```

The resolver produces an `AggregationExpressionData` with:
- `sum_terms`: `[SumTerm("pv_module", "capital_cost", "module_count", 20)]`
- `singleton_terms`: `[SingletonTerm("inverter.install_cost")]`
- `local_terms`: `[LocalTerm("misc_cost")]`
- `transformed_expression`: `"(module_count * pv_module.capital_cost) + inverter.install_cost + misc_cost"`

The three term types and their downstream handling:
- **SumTerm**: `sum(child.attr)` -> `count * child.attr`. See [aggregation scoping](13-aggregation-scoping.md).
- **SingletonTerm**: `child.attr` to a singleton child. Direct channel wire.
- **LocalTerm**: Same-PartDef attribute. Entry point or sibling wire. See [module factory](05-module-factory.md#4c-localterm).

## Related Documents

- **Upstream**: [00-pipeline-overview](00-pipeline-overview.md) -- Step 1 in the pipeline
- **Downstream**: [02-orchestration](02-orchestration.md) (coordinates extraction), [03-resolution-overview](03-resolution-overview.md) (consumes extraction output), [10-output-registry](10-output-registry.md) (registers outputs), [11-analysis-backtracker](11-analysis-backtracker.md) (traces bindings), [12-virtual-binding-rewrite](12-virtual-binding-rewrite.md) (expands templates)
- **Data models**: [09-data-models](09-data-models.md) -- full field definitions for all extraction types
- **Expression handling**: [14-expression-compiler](14-expression-compiler.md) -- compiles `output_expression_asts` to Python
- **Hierarchy detail**: [25-hierarchy-resolver](25-hierarchy-resolver.md) -- redefinitions, multiplicities, aggregation transformation
