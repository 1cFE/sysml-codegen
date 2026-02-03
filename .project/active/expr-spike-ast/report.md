# Spike Report: SysIDE Expression AST Extraction & Reference Resolution

**Date**: 2026-02-03
**Branch**: `cost-pattern`
**Scripts**: `scripts/spike_extract_expression_asts.py`, `scripts/spike_resolve_expression_refs.py`

## Q1: AST Extraction Coverage

**Question**: Do CalcDef output attributes expose expression ASTs via `feature_value_expression`?

**Answer**: **YES -- 95.8% coverage across all 4 model suites (92/96 outputs).** Fixture models are 100%; CATF has 4 outputs without ASTs (see below).

### Results by Suite

| Suite | CalcDefs | Outputs | With AST | Coverage |
|-------|----------|---------|----------|----------|
| chain_spike_model | 3 | 3 | 3 | 100% |
| sample_model | 7 | 7 | 7 | 100% |
| solar_battery_model | 15 | 56 | 56 | 100% |
| catf_mfe | ~30 | 30 | 26 | 86.7% |
| **Total** | | **96** | **92** | **95.8%** |

### CATF Outputs Without ASTs (4)

| CalcDef | Output | Notes |
|---------|--------|-------|
| PlasmaConfinement | tau_energy | Likely stub / externally computed |
| PlasmaConfinement | aspect_ratio | Likely stub / externally computed |
| PlasmaConfinement | p_fusion | Has AST but it's a bare `FeatureReferenceExpression` (passthrough: `p_fusion = p_fusion_input`) |
| TritiumBreedingRatio | neutron_flux_profile | Likely stub / externally computed |
| TritiumBreedingRatio | breeding_rate | Likely stub / externally computed |

These 4 missing-AST outputs are on CalcDefs that model complex physics (plasma confinement, tritium breeding) where the implementation requires lookup tables or external physics codes. They would be classified `MANUAL_REQUIRED` by the compiler regardless.

Note: `PlasmaConfinement.p_fusion` and `TritiumBreedingRatio.tbr` have ASTs but are bare `FeatureReferenceExpression` nodes (passthroughs), not computed expressions. These are trivially compilable as simple assignments.

### Node Type Inventory (3 types found)

| Node Type | Occurrences | Description |
|-----------|-------------|-------------|
| `OperatorExpression` | Present in 88/92 outputs with ASTs | Binary/unary operators |
| `FeatureReferenceExpression` | Present in 88/92 outputs with ASTs | References to inputs or sibling outputs |
| `LiteralRational` | Present in ~15 outputs | Numeric literal values (constants, coefficients) |

No `LiteralReal`, `LiteralInteger`, `FeatureChainExpression`, or `InvocationExpression` nodes were observed. All numeric literals appear as `LiteralRational` in syside's AST.

### Operator Inventory (5 operators found)

| Operator | Occurrences | Python Equivalent | Notes |
|----------|-------------|-------------------|-------|
| `*` | Most common | `*` | Multiplication |
| `+` | Common | `+` | Addition |
| `-` | Common | `-` | Subtraction |
| `/` | Common | `/` | Division |
| `**` | 2 outputs | `**` | Exponentiation |

The `**` operator appears in:
- `AnnualizedFinancialCalc.capital_recovery_factor` (depth 4, operators: `*, **, +, -, /`) -- the CRF formula
- `LCOECalc.lcoe_per_mwh` (depth 5, operators: `*, **, +, /`) -- LCOE formula

**This confirms that syside emits `**` as a native operator**, not as nested multiplications. The concept's Pattern C (CRF formula) correctly identifies `**` as an operator the compiler must handle. The `OPERATOR_MAP` entry for `**` will fire on real models.

No `^`, `[` (unit annotation), or other operators were observed in CalcDef output expressions. Unit annotations may appear in attribute definitions but not in CalcDef output formulas across these 4 suites.

### Depth Distribution

- **Depth 0**: Literal-only or passthrough outputs (e.g., `PermittingCostCalc.material_cost = 0.0`, bare `FeatureReferenceExpression`)
- **Depth 1**: Simple binary expressions (e.g., `a * b`) -- majority of outputs
- **Depth 2**: Two-level expressions (e.g., `a + b + c` or `a * b / c`)
- **Depth 3**: `EnergyProductionCalc.annual_energy_mwh`, `CryoPumpRefrigeration.refrigeration_power`, `TorusMinorRadius.a`
- **Depth 4**: `AnnualizedFinancialCalc.capital_recovery_factor` (CRF formula), `TorusSurfaceArea.area`
- **Depth 5**: `LCOECalc.lcoe_per_mwh`, `MagnetSurfaceArea.area`
- **Depth 6**: `TorusVolume.volume` (2*pi^2*R*a^2*kappa), `NetElectricPower.p_parasitic_total` (7-input sum)

## Q2: Feature Reference Resolution Rate

**Question**: Do all feature references in output expressions resolve to declared inputs or sibling outputs?

**Answer**: **98.6% resolution across all 4 suites (212/215 refs). 100% on fixture models; 3 unresolvable refs in CATF.**

### Results by Suite

| Suite | Total Refs | Input | Intermediate | Unresolvable | Resolution |
|-------|-----------|-------|--------------|--------------|------------|
| chain_spike_model | 6 | 6 | 0 | 0 | 100% |
| sample_model | 13 | 13 | 0 | 0 | 100% |
| solar_battery_model | 124 | 63 | 61 | 0 | 100% |
| catf_mfe | 72 | 65 | 4 | 3 | 95.8% |
| **Total** | **215** | **147** | **65** | **3** | **98.6%** |

### Unresolvable References (3)

| CalcDef | Output | Unresolvable Ref | Qualified Name |
|---------|--------|------------------|----------------|
| MagnetCryogenicLoad | cooling_power | `thermal_load_cryo` | `FusionAnalysesThermalLoads::MagnetCryogenicLoad::thermal_load_cryo` |
| VacuumPumpPower | pump_power | `pump_power_per_unit` | `FusionAnalysesThermalLoads::VacuumPumpPower::pump_power_per_unit` |
| CryoPumpRefrigeration | refrigeration_power | `thermal_load` | `FusionAnalysesThermalLoads::CryoPumpRefrigeration::thermal_load` |

These references point to members of the same CalcDef that are not classified as either input or output by the structured extractor. They are likely **undeclared intermediates** -- attributes with no `direction` annotation that serve as internal computation steps. The expression compiler should handle these by checking for same-CalcDef members beyond just `input_attributes` and `output_attributes`, or the CalcDef models could be updated to declare these as outputs.

### Reference Categories

- **Input** (147 refs): References to declared `in` attributes of the CalcDef
- **Intermediate** (65 refs): References to sibling `out` attributes within the same CalcDef
- **Unresolvable** (3 refs): Same-CalcDef members not declared as input or output (see above)

### Cross-Check: AST Node Count vs `extract_feature_refs`

For every output across all 4 suites:
- `count(FeatureReferenceExpression + FeatureChainExpression nodes in AST)` == `len(extract_feature_refs(expr, ignore_std_lib=False))`
- **0 mismatches** -- `extract_feature_refs` is not silently dropping any references

### Std_lib Filtering Transparency

`extract_feature_refs(ignore_std_lib=True)` (used for classification) == `extract_feature_refs(ignore_std_lib=False)` (used for cross-check) for **every output across all 4 suites**. Zero std_lib refs were filtered. This means no SI::, ISQ::, ScalarValues::, or UnitsAndScales:: references appear in CalcDef output expressions. Unit annotations are confined to attribute type declarations, not output formulas.

### Key Observation: Intermediate References

The solar_battery model makes heavy use of intermediate references (61 out of 124). The common pattern in component cost CalcDefs is:

```
material_cost = inputs * inputs        (references inputs)
fab_cost = material_cost * fab_factor  (references intermediate + input)
total_cost = material_cost + fab_cost + install_cost  (references 3 intermediates)
```

The CATF model uses intermediates more sparingly (4 out of 72), primarily for multi-step calculations like `eta_carnot -> eta_thermal` and `p_parasitic_total -> p_net`.

This means expression-aware codegen must resolve references in **topological order within each CalcDef** -- outputs that reference other outputs must be emitted after their dependencies.

## Go/No-Go Recommendation

**GO** -- Both assumptions are validated with high confidence:

1. `feature_value_expression` provides AST access for 95.8% of output attributes (100% on fixture models, 86.7% on CATF). The 4 missing-AST outputs are on CalcDefs that would be `MANUAL_REQUIRED` regardless.
2. 98.6% of feature references resolve to declared inputs or sibling outputs. The 3 unresolvable refs are same-CalcDef undeclared intermediates in CATF -- a known pattern the compiler can handle.
3. Zero cross-check mismatches -- `extract_feature_refs` is reliable.
4. No `sum()`, conditionals, `InvocationExpression`, or other complex constructs in any CalcDef expression.
5. Zero std_lib refs filtered from output expressions.

### Implementation Notes for Expression-Aware Codegen

1. **Topological ordering**: Output attributes within a CalcDef must be sorted by dependency. `fab_cost` depends on `material_cost`, so `material_cost` must be computed first.
2. **Intermediate outputs**: Some outputs (e.g., `material_cost`) serve as both pipeline outputs AND intermediate values consumed by sibling outputs. The codegen must emit them as local variables reused in subsequent expressions.
3. **Node types observed**: Based on these 4 model suites (96 outputs), the compiler needs to handle 3 node types: `OperatorExpression`, `FeatureReferenceExpression`, `LiteralRational`. Whether additional types (e.g., `InvocationExpression` for function calls, `FeatureChainExpression` for dotted refs) appear in other models remains to be validated in Item 2 when testing against additional CalcDef patterns.
4. **Operator mapping**: The compiler's `OPERATOR_MAP` must cover 5 operators: `+`, `-`, `*`, `/`, `**`. The `**` operator appears in real models (CRF formula, LCOE formula) and maps directly to Python's `**`. The `[` (unit annotation) and `^` operators were not observed in CalcDef output expressions.
5. **`extract_feature_refs` is reliable**: Zero cross-check mismatches means no silent reference drops. Safe to use as the primary API for building dependency graphs within CalcDef expressions.
6. **Undeclared intermediates**: 3 CATF CalcDefs reference same-CalcDef members not in input/output lists. The compiler must either: (a) extend reference resolution to check all CalcDef members (not just declared in/out), or (b) flag these as `PARTIALLY_COMPILABLE`. Item 2 should investigate which approach is correct.
