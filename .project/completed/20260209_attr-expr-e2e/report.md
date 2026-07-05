# Validation Report: E2E Validation on Real Models (ATTR-EXPR Item 4)

**Date:** 2026-02-09
**Branch:** cost-pattern
**Test File:** `tests/integration/test_computed_attributes_e2e.py`

## Summary

All 21 E2E tests pass. Full suite of 285 tests passes with 0 failures and 0 xfail. Computed attribute pipeline produces numerically correct auto-implementations for all validated patterns.

## Phase 1: Probe Fixture E2E Validation (14 tests)

### Ground Truth Results

| Attribute | Expression | Inputs | Expected | Actual | Status |
|-----------|-----------|--------|----------|--------|--------|
| area | length * width | 10.0, 5.0 | 50.0 | 50.0 | PASS |
| volume | length * width * height | 10.0, 5.0, 3.0 | 150.0 | 150.0 | PASS |
| cost | area * rate | 50.0, 12.0 | 600.0 | 600.0 | PASS |
| marked_up_cost | cost * markup | 600.0, 1.15 | 690.0 | 690.0 | PASS |
| cost_density | cost / volume | 600.0, 150.0 | 4.0 | 4.0 | PASS |
| q_scientific | p_fusion / p_input | 2600.0, 50.0 | 52.0 | 52.0 | PASS |
| perimeter | 2*length + 2*width | 10.0, 5.0 | 30.0 | 30.0 | PASS |
| minor_radius | (r_inner+r_outer)/2 - r_major | 4.2, 4.4, 3.0 | 1.3 | 1.3 | PASS |
| p_alpha | p_fusion * 3.52 / 17.58 | 2600.0 | 520.364... | 520.364... | PASS |

All 9 values match within 1e-10 relative tolerance.

### Classification Results

| Pattern | Attribute(s) | Expected Behavior | Status |
|---------|-------------|-------------------|--------|
| FORMULA (simple) | area, q_scientific | Auto-implemented module | PASS |
| FORMULA (multi-term) | volume, perimeter, minor_radius, p_alpha | Auto-implemented module | PASS |
| FORMULA (chain) | cost, marked_up_cost, cost_density | Correct upstream refs | PASS |
| EXPOSE_PURE | scale_result, half_vol, quarter_vol | No impl file | PASS |
| EXPOSE_COMPUTED | scaled_area | No impl file, no error | PASS |
| Backlog | -- | "0 functions to implement" | PASS |

### Chain Validation

- `area` (length*width=50) -> `cost` (area*rate=600) -> `marked_up_cost` (cost*markup=690): correct
- `cost` (600) + `volume` (150) -> `cost_density` (cost/volume=4.0): correct fan-in

## Phase 2: Solar Battery Computed Attribute Validation (5 tests)

| Test | Description | Status |
|------|------------|--------|
| test_p_net_kw_module_generated | p_net_kw impl exists and is auto-implemented | PASS |
| test_p_net_kw_ground_truth | 0.008 * 1000.0 = 8.0 | PASS |
| test_p_net_kw_wiring_in_pipeline_yaml | annualized_om.p_net_kw sourced from module output (FR-6) | PASS |
| test_impl_count_includes_computed_attr | 16 total impls (15 CalcDefs + 1 computed attr) | PASS |
| test_annualized_om_uses_computed_p_net_kw | 20.0 * 8.0 = 160.0 (end-to-end chain) | PASS |

## Phase 3: Regression Guards (2 tests)

| Test | Model | Expected Impls | Actual Impls | Status |
|------|-------|---------------|-------------|--------|
| test_chain_spike_still_works | chain_spike | 3 (all auto) | 3 (all auto) | PASS |
| test_catf_mfe_still_works | catf_mfe | 21 | 21 | PASS |

No false-positive computed attribute extraction on models without attribute expressions.

## Full Suite Regression

- **Total tests:** 285
- **Passed:** 285
- **Failed:** 0
- **xfail:** 0
- **Baseline:** 264 (21 new tests added by this item)

## Issues Encountered

- **YAML module key naming**: Initial test used CalcDef name (`annualizedomcalc`) for YAML key lookup, but YAML keys use full qualified names with `__` separators (e.g., `solarbatterylibrary__solar_battery_plant__annualized_om`). Fixed by searching for `annualized_om` substring in keys.

## Conclusion

ATTR-EXPR Item 4 validation complete. All computed attribute patterns (FORMULA simple, multi-term, chain, fan-in) produce numerically correct auto-implementations. EXPOSE_PURE and EXPOSE_COMPUTED correctly classified with no spurious modules. Solar battery `p_net_kw` generates, wires as MODULE_OUTPUT to downstream `annualized_om`, and existing models are unaffected. Item 4 acceptance criteria met.
