# Spike Report: Expression Compilation & Compilability Classification

**Date**: 2026-02-03
**Branch**: `cost-pattern`
**Scripts**: `scripts/spike_compile_expressions.py`, `scripts/spike_classify_compilability.py`
**Epic**: EXPR-CODEGEN Item 2
**Prerequisite**: Item 1 -- AST Extraction & Reference Resolution (GO)

---

## Executive Summary

**Recommendation: GO** -- All five go/no-go conditions are met.

Item 2 validates that syside expression ASTs can be compiled to correct, executable Python and that a compilability classifier can partition CalcDefs with zero false positives. Compiled expressions for all 5 ground-truth CalcDefs produce **exact numerical matches** (0.00e+00 relative error) against handwritten implementations.

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| Q3 syntactic validity | 98/102 outputs (96.1%) | 100% of compilable | **PASS** (4 failures are missing ASTs, correctly classified) |
| Q3 numerical accuracy | 5/5 MATCH at 0.00e+00 | 100% match within 1e-10 | **PASS** |
| Q4 false positive rate | 0/44 | 0% | **PASS** |
| Operator mapping validated | 5/5 operators | All 5 from Item 1 | **PASS** |
| Topological ordering | All multi-output CalcDefs | All multi-output | **PASS** |

---

## Q3 Results: Expression Compilation

### Per-Suite Summary

| Suite | CalcDefs | Outputs (incl. undeclared) | Outputs Compiled | Full Body Valid |
|-------|----------|---------------------------|------------------|-----------------|
| chain_spike_model | 3 | 3 | 3 (100%) | 3/3 (100%) |
| sample_model | 5 | 7 | 7 (100%) | 5/5 (100%) |
| solar_battery_model | 15 | 56 | 56 (100%) | 15/15 (100%) |
| catf_mfe | 21 | 36 | 32 (88.9%) | 19/21 (90.5%) |
| **Total** | **44** | **102** | **98 (96.1%)** | **42/44 (95.5%)** |

The output count (102) exceeds the Item 1 total (96) because the compiler now discovers and compiles undeclared intermediate members in CATF CalcDefs (6 additional). The 4 uncompiled outputs are on PlasmaConfinement (2) and TritiumBreedingRatio (2) -- CalcDefs modeling complex physics where SysIDE does not expose expression ASTs. These are correctly classified as PARTIALLY_COMPILABLE.

**Note on sample_model CalcDef count**: Item 1 reported sample_model has 7 CalcDefs; the actual count is 5 (SimpleCalc, MultiOutputCalc, FirstCalc, SecondCalc, FinalCalc). Item 1 conflated CalcDef count with output count. The 7 figure referred to the number of output attributes, not CalcDefs.

### Per-CalcDef Compilation Details (solar_battery)

| CalcDef | Pattern | Outputs | Execution Order | Body Valid | Ground Truth |
|---------|---------|---------|-----------------|------------|--------------|
| PVModuleCostCalc | B | 5 | material_cost → fab_cost → install_cost → total_cost → idiot_index | PASS | STUB |
| InverterCostCalc | B | 5 | material_cost → fab_cost → install_cost → total_cost → idiot_index | PASS | STUB |
| ArrayBOSCostCalc | B | 5 | material_cost → fab_cost → install_cost → total_cost → idiot_index | PASS | STUB |
| BatteryPackCostCalc | B | 5 | material_cost → fab_cost → install_cost → total_cost → idiot_index | PASS | STUB |
| HybridInverterCostCalc | B | 5 | material_cost → fab_cost → install_cost → total_cost → idiot_index | PASS | STUB |
| BatteryBOSCostCalc | B | 5 | material_cost → fab_cost → install_cost → total_cost → idiot_index | PASS | STUB |
| RackingCostCalc | B | 5 | material_cost → fab_cost → install_cost → total_cost → idiot_index | PASS | STUB |
| ElectricalPanelCostCalc | B | 5 | material_cost → fab_cost → install_cost → total_cost → idiot_index | PASS | STUB |
| PermittingCostCalc | D | 5 | (no inter-output deps, alphabetical order) | PASS | STUB |
| AllocationCostCalc | B | 5 | fastener_cost → seal_cost → wiring_cost → total_allocation → material_portion | PASS | STUB |
| EnergyProductionCalc | D+A | 1 | annual_energy_mwh | PASS | **MATCH** |
| AnnualizedOMCalc | A | 1 | annual_om_cost | PASS | **MATCH** |
| AnnualizedFuelCalc | A | 1 | annual_fuel_cost | PASS | **MATCH** |
| AnnualizedFinancialCalc | C | 2 | capital_recovery_factor → annualized_capital_cost | PASS | **MATCH** |
| LCOECalc | C | 1 | lcoe_per_mwh | PASS | **MATCH** |

**Pattern note on PermittingCostCalc**: This is pure Pattern D (all literals except one input-only formula: `material_cost = 0.0`, `fab_cost = 0.0`, `install_cost = 0.0`, `idiot_index = 0.0`, `total_cost = system_capacity_kw * cost_per_kw`). No output depends on any other output, so the topological sort produces alphabetical order. Not Pattern B despite having 5 outputs.

### Per-CalcDef Compilation Details (CATF)

| CalcDef | Outputs | Body Valid | Notes |
|---------|---------|------------|-------|
| MagnetCryogenicLoad | 5 (1 declared + 4 undeclared) | PASS | Undeclared: `nuclear_heating`, `heat_leak`, `ac_losses`, `thermal_load_cryo` -- all compiled and emitted |
| CoolantPumpPower | 1 | PASS | |
| HeatingWallPlugPower | 1 | PASS | |
| VacuumPumpPower | 2 (1 declared + 1 undeclared) | PASS | Undeclared: `pump_power_per_unit` -- compiled and emitted |
| CryoPumpRefrigeration | 2 (1 declared + 1 undeclared) | PASS | Undeclared: `thermal_load` -- compiled and emitted |
| TritiumProcessingPower | 1 | PASS | |
| AuxiliarySystemsPower | 1 | PASS | |
| ThermalCycleEfficiency | 2 | PASS | Intermediate: eta_carnot → eta_thermal |
| ScientificQFactor | 1 | PASS | |
| EngineeringQFactor | 3 | PASS | Intermediates: q_eng → f_recirculating → p_net |
| PlantEfficiency | 1 | PASS | |
| PlasmaConfinement | 3 | **FAIL** | 2 outputs missing ASTs (tau_energy, aspect_ratio); 1 passthrough (p_fusion) |
| TritiumBreedingRatio | 3 | **FAIL** | 2 outputs missing ASTs (breeding_rate, neutron_flux_profile); 1 passthrough (tbr) |
| TorusMinorRadius | 1 | PASS | |
| TorusVolume | 1 | PASS | Depth 6: `2.0 * pi * pi * R * a * a * kappa` |
| TorusSurfaceArea | 1 | PASS | Depth 4 |
| MagnetSurfaceArea | 1 | PASS | Depth 5 |
| AlphaNeutronSplit | 2 | PASS | Pattern D: literal constants 3.52, 14.06, 17.58 |
| BlanketThermalPower | 1 | PASS | |
| GrossElectricPower | 1 | PASS | |
| NetElectricPower | 2 | PASS | Depth 6: 7-input sum (p_parasitic_total) |

### Example Compiled Expressions

**Pattern A (simple binary):**
```python
area = (inputs.length * inputs.width)
```

**Pattern B (multi-step intermediate):**
```python
material_cost = (inputs.wattage * inputs.cost_per_watt)
fab_cost = (material_cost * inputs.fab_factor)
install_cost = (material_cost * inputs.install_factor)
total_cost = ((material_cost + fab_cost) + install_cost)
idiot_index = (total_cost / material_cost)
return (material_cost, fab_cost, install_cost, total_cost, idiot_index)
```

**Pattern C (CRF formula, depth 4):**
```python
capital_recovery_factor = ((inputs.discount_rate * ((1.0 + inputs.discount_rate) ** inputs.plant_lifetime)) / (((1.0 + inputs.discount_rate) ** inputs.plant_lifetime) - 1.0))
annualized_capital_cost = (capital_recovery_factor * inputs.total_capex)
return (capital_recovery_factor, annualized_capital_cost)
```

**Pattern D (literal constant):**
```python
annual_energy_mwh = (((8760.0 * inputs.p_net_mw) * inputs.n_mod) * inputs.plant_availability)
```

**CATF undeclared intermediates (MagnetCryogenicLoad):**
```python
ac_losses = 0.0
heat_leak = (inputs.magnet_volume * 0.05)
nuclear_heating = ((0.05 * inputs.p_neutron) * (inputs.magnet_surface_area / inputs.total_first_wall_area))
thermal_load_cryo = ((nuclear_heating + ac_losses) + heat_leak)
cooling_power = ((thermal_load_cryo / inputs.operating_temp) * (300.0 - inputs.operating_temp))
return cooling_power
```

**CATF depth 6 (7-input sum, n-ary left-fold):**
```python
p_parasitic_total = ((((((inputs.p_coils + inputs.p_heating) + inputs.p_pumps) + inputs.p_vacuum) + inputs.p_cryo) + inputs.p_tritium) + inputs.p_aux)
p_net = (inputs.p_electric_gross - p_parasitic_total)
```

---

## Q3: Ground Truth Comparison

### Methodology

For the 5 solar_battery CalcDefs with implemented (non-stub) handwritten `_impl.py` files:
1. Generate deterministic test inputs (SHA256-based synthetic values, all strictly positive)
2. Execute compiled expressions via `exec()` with `SimpleNamespace` inputs
3. Execute handwritten impl via function wrapping and `exec()` with same inputs
4. Compare per-output values within `1e-10` relative tolerance

### Results

| CalcDef | Pattern | Status | Max Rel Error | Output Values |
|---------|---------|--------|---------------|---------------|
| EnergyProductionCalc | D+A | **MATCH** | 0.00e+00 | annual_energy_mwh = 1,922,749,920 |
| AnnualizedOMCalc | A | **MATCH** | 0.00e+00 | annual_om_cost = 4,640 |
| AnnualizedFuelCalc | A | **MATCH** | 0.00e+00 | annual_fuel_cost = 560 |
| AnnualizedFinancialCalc | C | **MATCH** | 0.00e+00 | capital_recovery_factor = 19, annualized_capital_cost = 1,558 |
| LCOECalc | C | **MATCH** | 0.00e+00 | lcoe_per_mwh = 1.50e+34 |

All 5 CalcDefs produce **exact matches** (0.00e+00 relative error). The compiled CRF formula `(r * (1 + r) ** n) / ((1 + r) ** n - 1)` is semantically equivalent to the handwritten version.

### Stubs Correctly Identified (10 CalcDefs)

PVModuleCostCalc, InverterCostCalc, ArrayBOSCostCalc, BatteryPackCostCalc, HybridInverterCostCalc, BatteryBOSCostCalc, RackingCostCalc, ElectricalPanelCostCalc, PermittingCostCalc, AllocationCostCalc -- all correctly identified as `NotImplementedError` stubs and skipped.

### Limitations and Coverage Gaps

- **Only 5/44 CalcDefs (11%) have numerical ground truth.** The remaining 37 FULLY_COMPILABLE CalcDefs are validated syntactically only (`ast.parse()`).
- **Pattern B has zero runtime ground truth.** The 10 cost CalcDefs with genuine intermediate dependencies (PVModuleCostCalc, InverterCostCalc, etc.) all have stub handwritten impls. Their topological ordering is validated by `ast.parse()` and manual inspection. The sort algorithm is standard Kahn's and the ordering visually matches the SysML dependency chain, but no CalcDef with intermediate references has been numerically validated against an independent implementation.
- The 5 ground truth CalcDefs cover Patterns A, C, and D (simple binary, complex parenthesized, literal+input). Pattern B (multi-step intermediate) is the pattern most sensitive to topological ordering errors and has no ground truth coverage.

---

## Q4 Results: Compilability Classification

### Per-Suite Classification Summary

| Suite | Total | FULLY_COMPILABLE | PARTIALLY_COMPILABLE | MANUAL_REQUIRED |
|-------|-------|------------------|---------------------|-----------------|
| chain_spike_model | 3 | 3 | 0 | 0 |
| sample_model | 5 | 5 | 0 | 0 |
| solar_battery_model | 15 | 15 | 0 | 0 |
| catf_mfe | 21 | 19 | 2 | 0 |
| **Total** | **44** | **42** | **2** | **0** |

### Cross-Reference Validation

| Metric | Result |
|--------|--------|
| CalcDefs cross-referenced | 44/44 |
| Cross-reference PASS | 44/44 |
| Cross-reference FAIL (false positives) | **0** |
| False negative inventory | 0 (no MANUAL_REQUIRED with compilable outputs) |

**Validation breakdown for 42 FULLY_COMPILABLE CalcDefs:**
- **5 semantically validated** (ground truth numerical match confirmed)
- **37 syntax-validated only** (no ground truth available; `ast.parse()` pass only)

The cross-reference function checks both syntax validity (body + per-output `ast.parse()`) and, where ground truth exists, numerical comparison results. A FULLY_COMPILABLE CalcDef that fails either syntax or semantic checks is flagged as a false positive.

### PARTIALLY_COMPILABLE CalcDefs

| CalcDef | Compilable Outputs | Non-Compilable Outputs | Reason |
|---------|-------------------|----------------------|--------|
| PlasmaConfinement | p_fusion (passthrough) | tau_energy, aspect_ratio | Missing expression ASTs (complex physics, externally computed) |
| TritiumBreedingRatio | tbr (passthrough) | neutron_flux_profile, breeding_rate | Missing expression ASTs (complex physics, externally computed) |

Both are physics CalcDefs where the SysML model intentionally leaves outputs as stubs for external computation. The classifier correctly identifies which outputs compile and which don't.

---

## Operator Mapping Validation

| Operator | Python Mapping | Encountered | Example Expression |
|----------|---------------|-------------|-------------------|
| `+` | ` + ` | **Yes** | `(material_cost + fab_cost)` |
| `-` | ` - ` | **Yes** | `(((1.0 + inputs.discount_rate) ** inputs.plant_lifetime) - 1.0)` |
| `*` | ` * ` | **Yes** | `(inputs.wattage * inputs.cost_per_watt)` |
| `/` | ` / ` | **Yes** | `(total_cost / material_cost)` |
| `**` | ` ** ` | **Yes** | `((1.0 + inputs.discount_rate) ** inputs.plant_lifetime)` |
| `^` | ` ** ` (alias) | No | Not observed in any model suite |
| `[` | STRIP (unit annotation) | No | Not observed in CalcDef output expressions |

All 5 operators from Item 1 are validated with correct Python mappings. The `^` alias and `[` unit annotation were not encountered in any of the 102 outputs across 4 suites, confirming Item 1's finding. Defensive handling is implemented but untested against real models.

---

## LiteralRational.value Type Documentation

`LiteralRational.value` is a **Python `float`** in syside's API. No string-to-float conversion is needed. All literal values observed (`0.0`, `0.05`, `0.8`, `1.0`, `2.0`, `3.14159265359`, `3.52`, `8760.0`, `14.06`, `17.58`, `300.0`) are native floats.

The compiler emits `str(node.value)` which produces correct Python numeric literals (e.g., `0.0`, `3.14159265359`).

---

## Unary Negation

**Not encountered** in any of the 102 outputs across all 4 model suites. Defensive handling is implemented (`OperatorExpression` with 1 operand and operator `-` emits `(-operand)`), but no real model exercises this path.

**Recommendation for Item 3**: Include defensive handling for unary negation in the expression compiler module. The implementation is trivial and the concept doc's `ExpressionAST` already includes `UNARY_OP`.

---

## Undeclared Intermediates

### Finding

3 CATF CalcDefs reference members that are not classified as either input or output by the structured extractor. Extended resolution (checking all `owned_members`) discovers these members and their expressions, allowing full compilation.

| CalcDef | Undeclared Intermediates | All Have Expressions | Compiled Successfully |
|---------|------------------------|---------------------|----------------------|
| MagnetCryogenicLoad | `nuclear_heating`, `heat_leak`, `ac_losses`, `thermal_load_cryo` | Yes | Yes |
| VacuumPumpPower | `pump_power_per_unit` | Yes | Yes |
| CryoPumpRefrigeration | `thermal_load` | Yes | Yes |

### Code Emission Fix

The compiler now handles undeclared intermediates end-to-end:
1. **Discovery**: `build_dependency_graph()` detects references to members not in `input_names` or `output_names`, recursively discovers their own dependencies
2. **Graph inclusion**: Undeclared intermediates are added as graph nodes with their expressions and dependencies
3. **Topological sort**: They appear in the correct position in execution order (before outputs that reference them)
4. **Code emission**: Their assignments are emitted as local variables in the function body
5. **Return statement**: Only declared outputs appear in the return statement

### Recommendation for Item 3

**Expand `INTERMEDIATE_REF` definition** to include undeclared same-CalcDef members, AND ensure code emission handles them:
- The `ExpressionAST.INTERMEDIATE_REF` node type already handles sibling output references with bare names
- Undeclared intermediates behave identically -- they're local variables in the function body
- The key addition beyond reference resolution is **code emission**: undeclared intermediates must be extracted, compiled, and emitted as local variable assignments before the outputs that depend on them
- No new node type needed; extend the resolution lookup to check `owned_members` and include discovered intermediates in the dependency graph

---

## Multi-Operand Expression Handling

SysIDE represents n-ary expressions (e.g., `a + b + c`) as `OperatorExpression` nodes with >2 operands, not as nested binary trees. The compiler handles both:
- **Binary (2 operands)**: `(left op right)` -- standard case
- **N-ary (>2 operands)**: Left-fold `((a op b) op c)` -- produces correct, parenthesized Python

Example: `total_cost = material_cost + fab_cost + install_cost` compiles to `((material_cost + fab_cost) + install_cost)`.

The 7-input sum in CATF's `NetElectricPower.p_parasitic_total` (depth 6) compiles correctly as a left-fold: `((((((p_coils + p_heating) + p_pumps) + p_vacuum) + p_cryo) + p_tritium) + p_aux)`.

---

## Parenthesization

The compiler uses defensive over-parenthesization: every binary expression is wrapped in `(left op right)`. This is safe (Python ignores redundant parentheses) and produces correct results for all nesting depths tested (up to depth 6).

For Item 3, this could be optimized to emit minimal parentheses based on operator precedence, but the current approach is correct and readable.

---

## Existing Tests

All 42 existing tests pass with zero regressions. The spike scripts are self-contained and do not modify any pipeline code.

---

## Go/No-Go Decision

### All Go Conditions Met

1. **Q3 syntactic validity = 100%** of compilable outputs -- **MET** (98/98 outputs with ASTs pass `ast.parse()`)
2. **Q3 numerical accuracy = 100%** match for all ground truth -- **MET** (5/5 CalcDefs at 0.00e+00)
3. **Q4 false positive rate = 0%** -- **MET** (0/44 false positives; 5 semantic + 37 syntax-only)
4. **Operator mapping validated for all 5 operators** -- **MET** (all encountered, correct mappings)
5. **Topological ordering works for all multi-output CalcDefs** -- **MET** (all solar_battery + CATF multi-output CalcDefs including undeclared intermediates)

### No No-Go Conditions Triggered

- No Q3 numerical mismatch
- No Q4 false positive
- No operator mapping error

### Caveats

- **37/42 FULLY_COMPILABLE verdicts are syntax-validated only** (no ground truth). The 5 semantically validated CalcDefs cover Patterns A, C, and D. Pattern B (multi-step intermediate, the most topological-sort-sensitive pattern) has zero runtime ground truth because all 10 Pattern B handwritten impls are `NotImplementedError` stubs.
- **Undeclared intermediates require end-to-end handling.** Reference resolution alone is not sufficient -- Item 3 must also extract, compile, and emit undeclared intermediate expressions as local variables in the function body.

### Recommendation

**GO** -- proceed to Item 3 (Expression Compiler Module). The spike has validated:
- The recursive AST-to-Python compilation approach is correct
- Topological sorting handles all multi-output patterns (including undeclared intermediates)
- The classifier produces zero false positives
- Undeclared intermediates are fully resolvable and compilable
- All 3 node types and 5 operators are handled
- Ground truth comparison confirms semantic correctness for Patterns A, C, D

---

## Deliverables

- [x] `scripts/spike_compile_expressions.py` -- Q3 script (compilation + ground truth comparison)
- [x] `scripts/spike_classify_compilability.py` -- Q4 script (classification + cross-reference)
- [x] `.project/active/expr-spike-compile/report.md` -- this report
