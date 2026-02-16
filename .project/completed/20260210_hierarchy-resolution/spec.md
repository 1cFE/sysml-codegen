# Spec: Redefinition Resolution, Multiplicity, & Aggregation Expressions

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-10 14:18 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Epic:** COST-PATTERN Item 3

---

## Business Goals

### Why This Matters

Item 2 produces virtual CalcUsages per PartUsage instantiation -- structurally correct pipeline module candidates with hierarchy-aware qualified names. But those virtual instances still carry unresolved bindings. A binding like `in wattage = wattage` references the parent PartDef's attribute, which in turn gets its value from a design-level `:>> pv_module.wattage = 400.0` redefinition chain. Without resolving these chains, the backtracker (Item 4) has no way to determine what literal values or upstream module outputs feed into each virtual CalcUsage.

Similarly, assembly PartDefs contain aggregation expressions like `:>> capital_cost = sum(pv_module.capital_cost) + sum(inverter.capital_cost) + allocation_model.total_allocation + misc_hardware_cost`. The expression compiler classifies `sum()` as UNRESOLVABLE because `InvocationExpression` has no handler. These expressions need to be extracted, their `sum()` calls transformed to parametric multiply (`count * single_value`), and the result modeled as data that Item 4 can feed into synthetic pipeline modules.

Item 3 bridges the gap between "virtual CalcUsages exist" (Item 2) and "the pipeline can wire and execute them" (Item 4).

### Success Criteria

- [ ] `:>>` redefinition chains on PartDefs and design PartUsages are extracted with correct values and paths
- [ ] Deep-path `:>>` overrides (`:>> pv_module.wattage = 400.0`) are resolved through the hierarchy using structured `chaining_features` access
- [ ] Multiplicity detected on all arrayed PartUsages in the solar_battery model (3 multiplicities: `module_count=20`, `inverter_count=4`, `pack_count=8`)
- [ ] `sum(pv_module.capital_cost)` transformed to `module_count * pv_module.capital_cost` (parametric multiply)
- [ ] `AggregationExpressionData` correctly models `Solar Array.:>> capital_cost` aggregation with all input channels and multiplicity entry points
- [ ] All existing tests pass with zero regressions (313 baseline)

### Priority

P1 -- critical path for COST-PATTERN epic. Item 4 (pipeline integration) depends directly on this.

---

## Problem Statement

### Current State

**`:>>` redefinitions invisible to extraction:**
The computed attribute extractor (`computed_attribute_extractor.py`) scans `AttributeUsage` members for `feature_value_expression`. But `:>>` creates `ReferenceUsage` (spike Q2, Q8) -- a fundamentally different element type. All 4 `:>>` patterns (EXPOSE, FORMULA, aggregation, enum literal) are `ReferenceUsage` with non-empty `owned_redefinitions`. The extraction layer has no code that processes `ReferenceUsage` members for their redefinition semantics.

**Deep-path overrides from design not traversed:**
Design instances like `part redefines solar_array { :>> pv_module.wattage = 400.0; }` contain unnamed `ReferenceUsage` elements with `name=None`. The path information (`pv_module.wattage`) lives on `owned_redefinitions[0].redefined_feature.chaining_features` (spike Q4). No code in the extraction or analysis layers accesses this chain.

**Multiplicity not detected:**
PartUsages like `part pv_module : 'PV Module' [module_count]` have a `multiplicity` attribute (a `MultiplicityRange`), but no extraction code reads it. The multiplicity count is needed for parametric multiply transformation.

**`sum()` classified as UNRESOLVABLE:**
The expression compiler (`expression_compiler.py`) has no handler for `InvocationExpression`. When `build_expression_ast()` encounters a `sum()` call, it falls through to the unknown type handler and produces an `UNSUPPORTED` node. The spike (Q6) confirmed `sum()` is an `InvocationExpression` with `.function.name='sum'` and a single `FeatureChainExpression` operand.

**No aggregation expression data model:**
Assembly PartDefs have `:>> capital_cost = sum(child.cost) + ...` expressions that combine `sum()` over arrayed children, singleton child references, and literal attributes. There is no data model to capture these after transformation.

### Desired Outcome

The extraction layer:
1. Scans `:>>` `ReferenceUsage` members on PartDefs and design PartUsages, extracting redefinition bindings (literal, chain, and expression patterns)
2. Resolves deep-path `:>>` overrides through the hierarchy using `chaining_features`
3. Detects multiplicity on PartUsages and resolves to literal counts
4. Transforms `sum(array.attr)` to `count * attr` (parametric multiply)
5. Produces `AggregationExpressionData` for assembly aggregation expressions

All output is data -- no pipeline, backtracker, or generation changes. Item 4 consumes this data.

---

## Scope

### In Scope

1. **`:>>` redefinition extraction and resolution** on PartDefs and design PartUsages
2. **Deep-path `:>>` resolution** using `redefined_feature.chaining_features` (spike Q4)
3. **Multiplicity detection** on PartUsages via `cached_lower_bound` (spike Q5)
4. **`sum()` to parametric multiply transformation** (spike Q6)
5. **`AggregationExpressionData` data model** for assembly aggregation expressions
6. **Unit tests** for all new extraction functions

### Out of Scope

- Pipeline integration / graph builder changes (Item 4)
- Backtracker changes for cross-hierarchy binding resolution (Item 4)
- Generation layer changes (Item 4)
- Non-uniform array instances (all solar_battery arrays are uniform; document assumption)
- `InvocationExpression` handling beyond `sum()` (sqrt, sin, etc.)
- Changes to `CalcDef` or computed attribute expression compilation (Phase 1 and Phase 2 reused as-is)

### Edge Cases & Considerations

- **Multiple `:>>` redefinitions on one PartDef**: A PartDef like `PV Module` may have `:>> capital_cost`, `:>> idiot_index`, and `:>> cas_category` -- each a separate `ReferenceUsage`. All MUST be independently extracted.
- **`:>>` with no value expression**: Some `:>>` redefinitions may only declare type conformance without assigning a value. These SHOULD be skipped (no `feature_value_expression`).
- **Multiplicity via attribute reference vs literal**: `[module_count]` references a sibling attribute with `default := 20`. `[3]` is a direct literal. Both MUST be handled. For attribute references, the default value MUST be extracted via `upper_bound.referent.feature_value_expression.value`.
- **`sum()` over singleton (no multiplicity)**: If `array_bos` has no multiplicity (singleton), `array_bos.capital_cost` in an aggregation expression is a direct reference (multiplicity = 1). No `sum()` wrapping needed -- this is a plain `FeatureChainExpression`, not an `InvocationExpression`.
- **Mixed aggregation operands**: `Solar Array.:>> capital_cost` mixes `sum()` calls, singleton child references (`allocation_model.total_allocation`), and PartDef-local attributes (`misc_hardware_cost`). The transformation MUST handle all operand types in a single expression.
- **`:>>` chain resolving to a CalcUsage output**: `:>> capital_cost = cost_model.total_cost` is an EXPOSE pattern that chains a PartDef attribute to a CalcUsage output. This is a MODULE_OUTPUT reference for the downstream pipeline. Item 3 extracts this as a chain redefinition; Item 4 wires it.
- **Design-level deep-path `:>>` targeting nested children**: `:>> pv_module.wattage = 400.0` on design's `solar_array` traverses two levels (solar_array → PV Module → wattage). Deeper chains are possible in principle but the solar_battery model maxes out at 2-level paths. The implementation SHOULD support arbitrary depth.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic and spike report unless marked [INFERRED].

**`:>>` Redefinition Extraction:**

1. **FR-1**: A function MUST scan `ReferenceUsage` members on a PartDef or PartUsage that have non-empty `owned_redefinitions` (spike Q2, Q8). These are `:>>` redefinitions.

2. **FR-2**: Each `:>>` redefinition MUST be classified into one of three patterns:
   - **LITERAL**: RHS is a `LiteralInteger`, `LiteralRational`, `LiteralString`, or `LiteralBoolean` (e.g., `:>> wattage = 400.0`)
   - **CHAIN**: RHS is a `FeatureChainExpression` or `FeatureReferenceExpression` pointing to a calc output or sibling attribute (e.g., `:>> capital_cost = cost_model.total_cost`)
   - **EXPRESSION**: RHS is an `OperatorExpression` or contains `InvocationExpression` (e.g., `:>> capital_cost = sum(pv_module.capital_cost) + ...`)

3. **FR-3**: For LITERAL redefinitions, the literal value MUST be extracted from `feature_value_expression.value`.

4. **FR-4**: For CHAIN redefinitions, the source path MUST be extracted (e.g., `cost_model.total_cost`).

5. **FR-5**: For EXPRESSION redefinitions, the expression AST MUST be captured for downstream transformation.

6. **FR-6**: The redefined attribute name MUST be extracted from `owned_redefinitions[0].redefined_feature.name` (or from `chaining_features` for deep-path).

**Deep-Path `:>>` Resolution:**

7. **FR-7**: Deep-path `:>>` overrides (unnamed `ReferenceUsage` with `name=None`) MUST be resolved using `owned_redefinitions[0].redefined_feature.chaining_features` (spike Q4). This returns path components like `[PartUsage 'pv_module', AttributeUsage 'wattage']`.

8. **FR-8**: Each path component's name MUST be extracted to build the full dot-separated path (e.g., `pv_module.wattage`).

9. **FR-9**: Deep-path resolution SHOULD support arbitrary nesting depth (not hardcoded to 2 levels).

10. **FR-10**: Deep-path overrides MUST be associated with the design PartUsage they appear on (for later application to virtual CalcUsage bindings in Item 4).

**Multiplicity Detection:**

11. **FR-11**: A function MUST extract multiplicity from a PartUsage element, returning a literal count (`int`), an attribute reference name (`str`), or `None` (singleton).

12. **FR-12**: Multiplicity count MUST be obtained via `cached_lower_bound` or `upper_bound.referent.feature_value_expression.value`. `cached_upper_bound` MUST NOT be used (spike Q5 -- it is N+1 due to syside exclusive convention).

13. **FR-13**: When multiplicity is an attribute reference (e.g., `[module_count]`), the attribute name and its default value MUST both be extractable. The default is accessed via `feature_value.is_default=True` and `feature_value_expression.value` (spike Q9).

14. **FR-14**: [INFERRED] Multiplicity data MUST be associated with the PartUsage it belongs to, keyed by the PartUsage's qualified path, so Item 4 can look up multiplicity when resolving `sum()` expressions.

**`sum()` to Parametric Multiply Transformation:**

15. **FR-15**: A function MUST detect `InvocationExpression` nodes with `function.name == 'sum'` within an expression AST.

16. **FR-16**: For each `sum()` call, the single operand (`FeatureChainExpression`) MUST be decomposed into the array part name and attribute name (e.g., `pv_module.capital_cost` → part=`pv_module`, attr=`capital_cost`).

17. **FR-17**: `sum(pv_module.capital_cost)` MUST be transformed to `module_count * pv_module.capital_cost`, where `module_count` is the multiplicity attribute of the `pv_module` PartUsage.

18. **FR-18**: The `pv_module.capital_cost` reference in the transformed expression MUST be noted as requiring resolution through the `:>> capital_cost = cost_model.total_cost` chain (actual resolution deferred to Item 4).

19. **FR-19**: [INFERRED] The transformation MUST handle expressions with mixed operand types: `sum()` calls, singleton child references (`FeatureChainExpression`), and local attribute references (`FeatureReferenceExpression`).

**Aggregation Expression Data Model:**

20. **FR-20**: A new `AggregationExpressionData` dataclass MUST be created with at minimum:
    - `owning_part_qn: str` -- qualified name of the assembly PartDef
    - `attribute_name: str` -- the redefined attribute (e.g., `capital_cost`)
    - `raw_expression_text: str` -- original expression text before transformation
    - `transformed_expression: str` -- expression text after parametric multiply
    - `sum_terms: list` -- the `sum()` operands with their resolved part/attr/multiplicity info
    - `singleton_terms: list` -- non-`sum()` child attribute references
    - `local_terms: list` -- PartDef-local attribute references
    - `input_channels: list[str]` -- all resolved upstream channel references (for Item 4 wiring)
    - `entry_points: list[str]` -- multiplicity count attributes that become pipeline entry points
    - `compilability: Compilability`

21. **FR-21**: [INFERRED] `AggregationExpressionData` SHOULD capture `source_file` and `source_line` for traceability.

**Integration:**

22. **FR-22**: A top-level extraction function MUST exist that takes the model and returns all `:>>` redefinition data and aggregation expression data.

23. **FR-23**: [INFERRED] All name sanitization MUST use the canonical `sanitize_name()` from `core/qualified_names.py`.

24. **FR-24**: The output data structures MUST be sufficient for Item 4 to:
    - Apply resolved literal `:>>` values to virtual CalcUsage bindings
    - Generate synthetic aggregation pipeline modules from `AggregationExpressionData`
    - Wire multiplicity counts as ENTRY_POINT parameters

### Non-Functional Requirements

- `uv run mypy src/` MUST pass on all modified/new code
- `uv run ruff check src/` MUST pass

---

## Design Phase Decisions

The following decisions are deferred to the design phase:

1. **Data structure vs in-place mutation for `:>>` resolution**: Should Item 3 produce standalone data structures (e.g., `RedefinitionData` mapping paths to values) that Item 4 applies to virtual CalcUsage bindings? Or should Item 3 directly modify virtual CalcUsage bindings in-place? The design MUST evaluate both approaches against the Item 4 integration boundary.

2. **New module vs extending existing modules**: Should `:>>` extraction live in a new `hierarchy_resolver.py` module, be integrated into `usage_extractor.py`, or extend `computed_attribute_extractor.py`? The design MUST consider cohesion with existing extraction patterns.

3. **Expression compiler extension**: Should `build_expression_ast()` be extended with an `InvocationExpression` handler (returning a new IR node type), or should `sum()` transformation happen entirely outside the compiler at the extraction layer? The design MUST evaluate impact on the Phase 1 expression compiler contract.

4. **Aggregation expression extraction scope**: Should aggregation expressions be extracted from ALL PartDefs (library + design), or only from PartDefs that have PartUsage instantiations? The design MUST consider the interaction with Item 2's template expansion.

---

## Acceptance Criteria

### Core Functionality

- [ ] `:>>` LITERAL redefinitions extract correct values (e.g., `wattage = 400.0`)
- [ ] `:>>` CHAIN redefinitions extract correct source paths (e.g., `capital_cost → cost_model.total_cost`)
- [ ] `:>>` EXPRESSION redefinitions capture the expression AST
- [ ] Deep-path `:>>` chains resolve through `chaining_features` (e.g., `pv_module.wattage` from design's `solar_array`)
- [ ] All 5 deep-path overrides on design's `solar_array` correctly extracted (wattage, efficiency, power_rating, string_count, panel_count)
- [ ] Multiplicity detected on `pv_module` (20), `inverter` (4), `battery_pack` (8) via `cached_lower_bound`
- [ ] Multiplicity attribute names extracted (`module_count`, `inverter_count`, `pack_count`)
- [ ] `sum(pv_module.capital_cost)` transformed to `module_count * pv_module.capital_cost`
- [ ] Mixed aggregation expression (`sum() + sum() + singleton + local_attr`) fully decomposed
- [ ] `AggregationExpressionData` correctly models `Solar Array.:>> capital_cost` with 2 sum terms, 1 singleton term, 1 local term

### Quality & Integration

- [ ] All existing tests pass with zero regressions (313 baseline)
- [ ] New unit tests cover: `:>>` classification (3 patterns), deep-path resolution, multiplicity extraction, `sum()` transformation, `AggregationExpressionData` construction
- [ ] `uv run mypy src/` passes
- [ ] `uv run ruff check src/` passes

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_costed_component_pattern.md` (Item 3)
- **Spike report:** `.project/active/hierarchy-spike/report.md`
- **Item 2 spec:** `.project/active/template-detection/spec.md`
- **Item 2 design:** `.project/active/template-detection/design.md`
- **Research:** `.project/research/20260109-205122_cost-modeling-codegen-changes.md`
- **Design:** `.project/active/hierarchy-resolution/design.md` (to be created)
- **Plan:** `.project/active/hierarchy-resolution/plan.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
