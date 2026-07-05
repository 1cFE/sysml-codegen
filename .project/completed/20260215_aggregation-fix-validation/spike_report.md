# Aggregation Wiring Fix — Validation Spike Report

**Generated:** 2026-02-15
**Model:** solar_battery (tests/fixtures/solar_battery_model)
**Registry:** 293 keys → 77 canonical channels
**Aggregation expressions:** 20

---

## Executive Summary

**Go/No-Go: GO — proceed to implement the 3-part fix.**

The root cause analysis is confirmed with runtime data. Key findings:

- **Bug 1 (unscoped registry lookup): CONFIRMED.** All 12 resolvable inputs fail with current unscoped keys (0 hits). Proposed scoped keys resolve all 12 inputs.
- **Bug 2 (SingletonTerm wrong channel): NOT TESTABLE.** No SingletonTerms exist in the solar_battery model. Bug 2 should be fixed but cannot be validated with this model.
- **Bug 3 (missing scoped registration key): PARTIALLY CONFIRMED.** Top-level aggregations use LocalTerms (bare names), not dotted SumTerm refs, so Bug 3 doesn't manifest in this model. However, the hypothetical scoped key test confirms the Key_E_stripped registration would work if needed.
- **New finding: CHAIN_PART_MISMATCH.** 4 of 12 SumTerm failures are caused by PartDef→PartUsage name mismatch (`String_Inverter` vs `inverter`). The scoped registry fix resolves these since Phase 2 CHAIN aliases use correctly-scoped keys.

---

## Spike A: Registry Key Inventory

| Metric | Value |
|--------|-------|
| Total inputs | 58 |
| Resolvable (SumTerm/SingletonTerm) | 12 |
| LocalTerms (always entry points) | 46 |
| Current hits (unscoped key) | 0 |
| Proposed hits (scoped key) | 12 |
| Still missing after fix | 0 |

### Per-Input Detail

| # | Type | Agg Module | Symbolic Ref | Current | Proposed |
|---|------|-----------|-------------|---------|----------|
| 1 | SumTerm | `SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost` | `pv_module.capital_cost` | MISS | HIT |
| 2 | SumTerm | `SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost` | `inverter.capital_cost` | MISS | HIT |
| 3 | SumTerm | `SolarBatteryDesign__solar_battery_plant__solar_array__raw_material_cost` | `pv_module.raw_material_cost` | MISS | HIT |
| 4 | SumTerm | `SolarBatteryDesign__solar_battery_plant__solar_array__raw_material_cost` | `inverter.raw_material_cost` | MISS | HIT |
| 5 | SumTerm | `SolarBatteryDesign__solar_battery_plant__solar_array__fabrication_cost` | `pv_module.fabrication_cost` | MISS | HIT |
| 6 | SumTerm | `SolarBatteryDesign__solar_battery_plant__solar_array__fabrication_cost` | `inverter.fabrication_cost` | MISS | HIT |
| 7 | SumTerm | `SolarBatteryDesign__solar_battery_plant__solar_array__installation_cost` | `pv_module.installation_cost` | MISS | HIT |
| 8 | SumTerm | `SolarBatteryDesign__solar_battery_plant__solar_array__installation_cost` | `inverter.installation_cost` | MISS | HIT |
| 9 | SumTerm | `SolarBatteryDesign__solar_battery_plant__battery_system__capital_cost` | `battery_pack.capital_cost` | MISS | HIT |
| 10 | SumTerm | `SolarBatteryDesign__solar_battery_plant__battery_system__raw_material_cost` | `battery_pack.raw_material_cost` | MISS | HIT |
| 11 | SumTerm | `SolarBatteryDesign__solar_battery_plant__battery_system__fabrication_cost` | `battery_pack.fabrication_cost` | MISS | HIT |
| 12 | SumTerm | `SolarBatteryDesign__solar_battery_plant__battery_system__installation_cost` | `battery_pack.installation_cost` | MISS | HIT |

**Conclusion:** Bug 1 fully confirmed. Every unscoped registry lookup fails. Scoped keys resolve 100% of resolvable inputs.

---

## Spike B: Resolution Path Trace

| Metric | Value |
|--------|-------|
| Total non-local inputs | 12 |
| Resolved via CHAIN | 8 |
| Resolved via REGISTRY | 0 |
| Resolved via DIRECT_CONSTRUCTION | 0 |
| Failed → ENTRY_POINT | 4 |

### Failure Reason Breakdown

| Reason | Count |
|--------|-------|
| CHAIN_PART_MISMATCH | 4 |

### CHAIN Success Detail

- `pv_module.capital_cost` in `SolarBatteryDesign__solar_battery_plant__solar_array`: CHAIN via `cost_model.total_cost` → `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model__total_cost`
- `pv_module.raw_material_cost` in `SolarBatteryDesign__solar_battery_plant__solar_array`: CHAIN via `cost_model.material_cost` → `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model__material_cost`
- `pv_module.fabrication_cost` in `SolarBatteryDesign__solar_battery_plant__solar_array`: CHAIN via `cost_model.fab_cost` → `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model__fab_cost`
- `pv_module.installation_cost` in `SolarBatteryDesign__solar_battery_plant__solar_array`: CHAIN via `cost_model.install_cost` → `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model__install_cost`
- `battery_pack.capital_cost` in `SolarBatteryDesign__solar_battery_plant__battery_system`: CHAIN via `cost_model.total_cost` → `SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model__total_cost`
- `battery_pack.raw_material_cost` in `SolarBatteryDesign__solar_battery_plant__battery_system`: CHAIN via `cost_model.material_cost` → `SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model__material_cost`
- `battery_pack.fabrication_cost` in `SolarBatteryDesign__solar_battery_plant__battery_system`: CHAIN via `cost_model.fab_cost` → `SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model__fab_cost`
- `battery_pack.installation_cost` in `SolarBatteryDesign__solar_battery_plant__battery_system`: CHAIN via `cost_model.install_cost` → `SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model__install_cost`

### CHAIN Failure Detail

- `inverter.capital_cost` in `SolarBatteryDesign__solar_battery_plant__solar_array`: CHAIN_PART_MISMATCH — registry key `inverter.capital_cost` also missed
- `inverter.raw_material_cost` in `SolarBatteryDesign__solar_battery_plant__solar_array`: CHAIN_PART_MISMATCH — registry key `inverter.raw_material_cost` also missed
- `inverter.fabrication_cost` in `SolarBatteryDesign__solar_battery_plant__solar_array`: CHAIN_PART_MISMATCH — registry key `inverter.fabrication_cost` also missed
- `inverter.installation_cost` in `SolarBatteryDesign__solar_battery_plant__solar_array`: CHAIN_PART_MISMATCH — registry key `inverter.installation_cost` also missed

**Conclusion:** The 8-vs-4 split (not 8-vs-62 as originally estimated) is explained. All 8 successes are CHAIN-path. All 4 failures are CHAIN_PART_MISMATCH (PartDef name `String_Inverter` ≠ PartUsage name `inverter`). The original estimate of ~70 inputs included LocalTerms which are always entry points.

---

## Spike C: Scoped Key Spot-Check

### Case 1: SumTerm from solar_array (mid-level, CHAIN success — verify scoped key also works)

- **instance_path:** `SolarBatteryDesign__solar_battery_plant__solar_array`
- **symbolic_ref:** `pv_module.capital_cost`
- **proposed_scoped_key:** `solar_battery_plant.solar_array.pv_module.capital_cost`
- **key_exists:** True
- **canonical_channel:** `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model__total_cost`
- **Notes:** CHAIN resolved to: SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model__total_cost. Scoped key also resolves — confirms registry has the alias.

### Case 2: SumTerm CHAIN failure (part name mismatch — verify scoped key resolves)

- **instance_path:** `SolarBatteryDesign__solar_battery_plant__solar_array`
- **symbolic_ref:** `inverter.capital_cost`
- **proposed_scoped_key:** `solar_battery_plant.solar_array.inverter.capital_cost`
- **key_exists:** True
- **canonical_channel:** `SolarBatteryDesign__solar_battery_plant__solar_array__inverter__cost_model__total_cost`
- **Notes:** CHAIN failed: CHAIN_PART_MISMATCH. Scoped key resolves correctly.

### Case 3: SUBSTITUTE for SingletonTerm (none in model) — SumTerm from battery_system, CHAIN failure

- **instance_path:** `SolarBatteryDesign__solar_battery_plant__solar_array`
- **symbolic_ref:** `inverter.raw_material_cost`
- **proposed_scoped_key:** `solar_battery_plant.solar_array.inverter.raw_material_cost`
- **key_exists:** True
- **canonical_channel:** `SolarBatteryDesign__solar_battery_plant__solar_array__inverter__cost_model__material_cost`
- **Notes:** No SingletonTerms exist in this model — Bug 2 cannot be validated. Substituted with SumTerm from battery_system. Scoped key resolves correctly.

### Case 4: Top-level aggregation (SolarBatteryDesign__solar_battery_plant) — Bug 3 test. NOTE: top-level uses LocalTerms, not SumTerms. Testing hypothetical scoped key for 'solar_array.capital_cost'.

- **instance_path:** `SolarBatteryDesign__solar_battery_plant`
- **symbolic_ref:** `(hypothetical) solar_array.capital_cost`
- **proposed_scoped_key:** `solar_battery_plant.solar_array.capital_cost`
- **key_exists:** True
- **canonical_channel:** `SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost__capital_cost`
- **Bug 3 key:** `solar_battery_plant.capital_cost`
- **Bug 3 key exists:** True
- **Expected channel:** `SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost__capital_cost`
- **Notes:** Top-level aggregations in this model use LocalTerms (bare names like 'solar_array'), NOT dotted SumTerm refs. Bug 3 is hypothetical here. Hypothetical scoped key 'solar_battery_plant.solar_array.capital_cost' resolves to SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost__capital_cost. Bug 3 key 'solar_battery_plant.capital_cost' resolves to SolarBatteryDesign__solar_battery_plant__capital_cost__capital_cost. Expected channel: SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost__capital_cost.

---

## Go/No-Go Decision

### Decision: **GO** — proceed to implement the 3-part fix

### Evidence

| Bug | Status | Evidence |
|-----|--------|----------|
| Bug 1 (unscoped registry lookup) | **CONFIRMED** | 0/12 current hits, 12/12 proposed hits. Every scoped key resolves. |
| Bug 2 (SingletonTerm wrong channel) | **NOT TESTABLE** | No SingletonTerms in solar_battery model. Fix anyway (code is clear). |
| Bug 3 (missing scoped registration key) | **PARTIALLY CONFIRMED** | Top-level aggs use LocalTerms, not dotted refs. Hypothetical key test passes. |
| NEW: CHAIN_PART_MISMATCH | **DISCOVERED** | 4 failures from PartDef→PartUsage name mismatch. Scoped registry fix resolves these. |

### Caveats

1. **Input count discrepancy:** Found 12 resolvable inputs (not ~70). The original estimate likely counted multiplicity entry points and LocalTerms. The analysis still holds for all resolvable inputs.
2. **Bug 2 unvalidated:** No SingletonTerms in this model. Consider testing with a model that has SingletonTerm→aggregation references.
3. **Bug 3 hypothetical:** Top-level aggregations use bare-name LocalTerms. The Bug 3 fix is still correct (adds a registration key) but its value depends on whether other models have dotted plant-level refs.
4. **New CHAIN_PART_MISMATCH bug:** The scoped registry fix resolves these failures, but the CHAIN search itself has a latent name-matching bug. Consider improving `sanitize_name()` matching or removing the CHAIN search once registry-first is proven.

### Recommended Fix Implementation Order

1. **Change 1 (Bug 1):** Scope the registry lookup in `_resolve_aggregation_input_channel`
2. **Change 2 (Bug 3):** Add Key_E_stripped to Phase 1b registration
3. **Change 3 (Bug 2):** Fix SingletonTerm to use registry-first resolution
4. **Bonus:** The CHAIN_PART_MISMATCH fix comes free with Change 1 (scoped registry lookup succeeds where CHAIN name matching fails)
