# Step 1: Extraction

Extraction reads SysML v2 model files (via the SysIDE adapter from agentic-mbse),
walks the parsed AST, and produces structured Python dataclasses. No analysis,
resolution, or generation happens here -- it is a pure data-harvesting step.
Source: `src/sysml_codegen/extraction/`

## The semantic-evidence boundary

Raw SysIDE nodes are not a license for downstream guessing. Agentic-mbse supplies mapped metatype,
exact referent/target, operand, origin, and `DocumentTier` evidence. Codegen consumes that evidence
through one public boundary: `elaborate_loaded_extractor` in
`orchestration/elaborated_pipeline.py`. It catches `SemanticEvidenceError` for both live and
admitted-source extraction and emits one `SI_EVIDENCE_INCOMPLETE` diagnostic with the operation,
reference, portable source referent, and line. The private graph builder does not expose or convert
the upstream exception.

Feature typing is exact too. A feature must have one qualified supported primitive type; zero,
multiple, user-defined lookalike, or unsupported primitive outcomes refuse as `SI_TYPE_INVALID`.
An otherwise valid indexed element expression currently refuses before graph construction as
`SI_INDEXED_SOURCE_UNSUPPORTED`; indexing is a filed capability, not a silently dropped operand.
The strict/lenient, live/admitted, typing, and indexed cases are pinned by
`tests/conformance/test_expression_evidence_integrity.py` and
`tests/conformance/test_feature_typing_integrity.py`.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-EXT-01 | Extraction SHALL produce exactly one [CalculationDefinitionData](09-data-models.md#extraction-models) per `calc def` in the SysML model. | `len(calc_defs) == count(CalcDef elements in AST)` |
| REQ-EXT-02 | Every parameter binding on a [CalcUsageData](09-data-models.md#extraction-models) SHALL have exactly one [BindingType](#binding-types) from {CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND}. | `all(b.binding_type in BindingType for u in usages for b in u.bindings)` |
| REQ-EXT-03 | Every `:>>` redefinition SHALL be classified as exactly one [RedefinitionType](#redefinitions-redefinitiondata) from {LITERAL, CHAIN, EXPRESSION}. | `all(r.redefinition_type in RedefinitionType for r in redefinitions)` |
| REQ-EXT-04 | Every aggregation expression SHALL be decomposed into typed terms: [SumTerm, SingletonTerm, LocalTerm](#aggregation-data-sumterm-singletonterm-localterm). | `all(len(a.sum_terms) + len(a.singleton_terms) + len(a.local_terms) > 0 for a in agg_exprs)` |
| REQ-EXT-05 | Template calc usages (`is_template=True`) SHALL produce one virtual [CalcUsageData](09-data-models.md#extraction-models) per PartUsage that instantiates the owning PartDef. | Count virtual usages == count of design-level PartUsage instances of that PartDef |
| REQ-EXT-06 | Extraction SHALL NOT import from `analysis/`, `resolution/`, or `generation/`. | Static import analysis of `extraction/` package |
| REQ-EXT-07 | Expression extraction SHALL preserve exact mapped metatype, operand, target, origin, and type evidence for downstream compilation; incomplete evidence refuses at the one public conversion boundary. | `tests/conformance/test_expression_evidence_integrity.py` |
| REQ-EXT-08 | A `calc def` that extracts with zero output attributes SHALL raise a `ValueError` at extraction (V7), never reaching generation. | `extract_calculation_definitions()` on the `zero_output_calc` fixture raises before the Jinja module template runs |
| REQ-EXT-09 | Every `ConstraintUsage` — **including** its `assert` (`AssertConstraintUsage`), `require`/plain subtypes, **and** `RequirementUsage` with its `satisfy` subtype — SHALL be a member of the constraint usage domain (`InstanceGraph.constraint_usages`, minted before owner-to-scope expansion) and SHALL carry exactly one disposition: `eligible`, `excluded`, or `non_reaching`. The requirement-side exclusion is a disposition *inside* the domain (`out_of_scope_satisfy`, `out_of_profile_owner`), not a boundary that removes the usage from it — a form outside the domain could not carry a named visible exclusion. Nothing is silently absent. | `test_constraint_population_oracle.py` — a reviewed expected-population file per constraint-bearing fixture directory, read from the `.sysml` source and asserted against the domain **by identity list**, plus the rule that a constraint-bearing directory with no expectation file fails by name. `test_constraint_usage_domain_totality.py` pins the headline: `catf_mfe_d5` authors 65 usages and the domain holds 65, where the pre-Item-2 catalog held 9. `test_constraint_catalog_totality.py` pins that the shipped catalog carries every member and that generation refuses a broken join before writing. See the [subtype-enumeration decision table](../../../../agentic-mbse/docs/subtype-enumeration-decision-table.md) (adapter docs, D4 home) for the per-call-site policy. |
| REQ-EXT-10 | A calc-def member that is a direction-carrying `ReferenceUsage` — a named `return y` (Out) or a bare `in x` (In) — SHALL be extracted as a parameter; a named inline `return y : Real = expr` SHALL populate `output_expression_asts` so the output auto-implements. | `test_return_style_extraction.py` — `NamedReturnB` yields output `y` with a captured AST; `BareInC` yields input `x`; offline snapshot I/O confirms both |
| REQ-EXT-11 | A calc def with an anonymous `return` (a result whose `declared_name` is empty) SHALL raise a `ValueError` naming the fix (V8), before the generic zero-output error (V7). | `test_return_style_extraction.py` — extraction of `anonymous_return` raises V8 ("Give the result a name"), not V7's zero-output text |
| REQ-EXT-12 | The `return attribute y : Real; y = expr;` form SHALL extract `y` exactly once, with the direction-None body-assignment `ReferenceUsage` excluded from the attribute lists and `member_expressions` (no double-ingestion). | `test_return_style_extraction.py` — `StyleD` has `y` once, no phantom member; offline snapshot confirms single output |
| REQ-EXT-13 | `_build_part_usage_index` SHALL index each PartUsage under **all** of its owned FeatureTyping targets and every user-model PartDefinition in `usage.types` (filtered to user packages), never by list position. | `test_type_indexing.py` — the retyped `Variant.driver` is keyed under both `IFE Driver` and `HIF Driver`; the plain sibling under `HIF Driver` only |
| REQ-EXT-14 | When two template calcs from different owners in a retyped usage's type set resolve to the same virtual QN, expansion SHALL keep the most-specific owner's (deterministic tiebreak) and emit a warning (V9) naming both candidates and the winner. Differently-named templates SHALL both instantiate with no warning. | `test_type_indexing.py` — same-named `shared_calc` resolves to one HIF-owned virtual + V9; `ife_calc`/`hif_calc` both instantiate |

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
| `input_attributes` | `[AttributeInfo(name="capacity", ...)]` | [Input resolver](04-producer-resolution.md): what needs wiring |
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

The instantiation index keys each PartUsage under **every user-model PartDefinition it
carries** — its owned FeatureTyping target(s) plus the user PartDefs in its (order-unstable)
type list, filtered to user packages (REQ-EXT-13). This is what lets a **retyped** usage
(`part :>> driver : 'HIF Driver'`) instantiate both the subtype's templates and the
supertype templates it already carried. When a subtype and its supertype own a **same-named**
template, both resolve to the same virtual QN; the most-specific owner wins and a **V9**
warning is emitted (REQ-EXT-14). Differently-named templates simply both instantiate. See
[modeling-assumptions §5](../modeling-assumptions.md#5-template-instantiation-convention).

### 3. Part Definitions ([PartDefinitionData](09-data-models.md#extraction-models))

Part definitions model the structural hierarchy. Literal attribute values like
`voltage = 48.0` become design attributes -- user-configurable inputs in the
generated pipeline. See [17-parameter-group-deriver](17-parameter-group-deriver.md).

Computed attributes are not classified in this extraction layer. The exact elaborator walks
their expressions directly; see [computed attributes](16-computed-attributes.md).

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

> **Note**: EXPRESSION bindings are rare in practice — no natural fixture model
> contains a calc usage that binds a parameter to an inline expression. The
> backtracker handles EXPRESSION bindings by creating an ENTRY_POINT with a
> warning (see [11-analysis-backtracker](11-analysis-backtracker.md)).

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
