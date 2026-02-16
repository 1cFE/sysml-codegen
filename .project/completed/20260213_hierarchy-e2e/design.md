# Design: E2E Validation & Documentation -- Costed Component Pattern

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-10 23:15 UTC
**Branch:** cost-pattern
**Commit:** f49005c
**Epic:** COST-PATTERN (Item 5)

---

## Overview

End-to-end validation of the hierarchy-aware pipeline on the solar_battery model, regression guards for chain_spike and CATF MFE, and three ADRs documenting the architectural decisions from Items 1-4. No production code changes unless bugs are discovered.

## Related Artifacts

- **Spec:** `.project/active/hierarchy-e2e/spec.md`
- **Epic:** `.project/backlog/epic_costed_component_pattern.md`
- **Item 4 Design:** `.project/active/hierarchy-pipeline/design.md`
- **Spike Report:** `.project/active/hierarchy-spike/report.md`
- **Existing E2E Tests:** `tests/integration/test_expression_compilation_e2e.py`
- **Existing Computed Attr E2E:** `tests/integration/test_computed_attributes_e2e.py`
- **Test Helpers:** `tests/helpers/impl_execution.py`
- **Solar Battery Fixture:** `tests/fixtures/solar_battery_model/`
- **Existing ADRs:** `docs/architecture/ADR-001` through `ADR-005`

---

## Research Findings

### Existing Test Infrastructure

**Test patterns** (from `test_expression_compilation_e2e.py`, `test_computed_attributes_e2e.py`):
- Class-scoped fixtures (`scope="class"`) run `run_codegen()` once per test class
- `find_impl_files()` discovers `*_impl.py` in `handwritten/` (recursive glob)
- `is_auto_implemented()` checks for `AUTO_IMPLEMENTED = True` marker
- `extract_function_body()` extracts body from `def run_*()` functions
- `execute_impl_body()` wraps body in function, executes via `exec()` with `SimpleNamespace` inputs
- `assert_outputs_match()` uses relative tolerance of 1e-10
- Ground truth data is module-level constants (tuples of calc_name, inputs, outputs, expected)
- `_find_impl()` does case-insensitive substring match on impl filename

**Existing solar_battery test assertions** that need updating:
- `test_expression_compilation_e2e.py:148` — `TestSolarBatteryValidation.test_auto_implementation_count`: asserts `len(impls) == 16`
- `test_computed_attributes_e2e.py:241` — `TestSolarBatteryComputedAttrE2E.test_impl_count_includes_computed_attr`: asserts `len(impls) == 16`

Both must be updated to the new expected count once hierarchy modules are included.

### Solar Battery Model Structure

From reading `library.sysml`, `design.sysml`, `costing.sysml`:

**CalcDefs** (15 total):
- 9 leaf component cost CalcDefs (PVModuleCostCalc, InverterCostCalc, ArrayBOSCostCalc, BatteryPackCostCalc, HybridInverterCostCalc, BatteryBOSCostCalc, RackingCostCalc, ElectricalPanelCostCalc, PermittingCostCalc)
- 1 allocation CalcDef (AllocationCostCalc)
- 5 system-level CalcDefs (EnergyProductionCalc, AnnualizedOMCalc, AnnualizedFuelCalc, AnnualizedFinancialCalc, LCOECalc)

**Part hierarchy**:
- 9 leaf parts, each with embedded `cost_model` CalcUsage and `:>>` redefinitions
- 3 intermediate assemblies (Solar Array, Battery System, Site Infrastructure) with aggregation expressions
- 1 top-level assembly (Solar Battery Plant) aggregating the 3 subsystems

**Multiplicity**:
- `pv_module[module_count]` where `module_count : Integer default := 20`
- `inverter[inverter_count]` where `inverter_count : Integer default := 4`
- `battery_pack[pack_count]` where `pack_count : Integer default := 8`
- All other child parts are singletons

**Aggregation attributes per assembly** (each has 5: capital_cost, raw_material_cost, fabrication_cost, installation_cost, idiot_index):
- Solar Array: 5 aggregation expressions (4 cost + 1 ratio)
- Battery System: 5 aggregation expressions
- Site Infrastructure: 5 aggregation expressions (singletons only, no `sum()`)
- Solar Battery Plant: 5 aggregation expressions (singletons only)

**Total aggregation expressions**: 20 (4 assemblies x 5 attributes). However, `idiot_index = capital_cost / raw_material_cost` references the assembly's own aggregation outputs (capital_cost, raw_material_cost), which are local terms from other aggregation modules on the same assembly. This means each `idiot_index` aggregation depends on the other aggregation modules completing first.

**Allocation CalcUsage**: `solar_array.allocation_model : AllocationCostCalc` with literal bindings `child_count = 25.0`, `total_child_mass = 50.0`. Also `misc_hardware_cost : Real = allocation_model.total_allocation` is an EXPOSE_PURE attribute.

**Computed attribute**: `p_net_kw : Real = p_net_mw * 1000.0` (FORMULA)

### Expected Module Count

The exact module count depends on how many virtual CalcUsages, aggregation modules, computed attributes, and allocation CalcUsages the pipeline generates. Based on the architecture:

**Virtual CalcUsages from leaf parts** (9 template CalcUsages × 1 instance each = 9 concrete):
1. `pv_module__cost_model` (PVModuleCostCalc)
2. `inverter__cost_model` (InverterCostCalc)
3. `array_bos__cost_model` (ArrayBOSCostCalc)
4. `battery_pack__cost_model` (BatteryPackCostCalc)
5. `hybrid_inverter__cost_model` (HybridInverterCostCalc)
6. `battery_bos__cost_model` (BatteryBOSCostCalc)
7. `racking__cost_model` (RackingCostCalc)
8. `electrical_panel__cost_model` (ElectricalPanelCostCalc)
9. `permitting__cost_model` (PermittingCostCalc)

**Allocation CalcUsage** (1 instance in design):
10. `solar_array__allocation_model` (AllocationCostCalc)

**System-level CalcUsages** (5 concrete in design):
11. `energy_production` (EnergyProductionCalc)
12. `annualized_om` (AnnualizedOMCalc)
13. `annualized_fuel` (AnnualizedFuelCalc)
14. `annualized_financial` (AnnualizedFinancialCalc)
15. `lcoe` (LCOECalc)

**Computed attribute**:
16. `p_net_kw` (FORMULA)

**Aggregation modules**: This is the key unknown. The scoping algorithm creates one `ScopedAggregationData` per (aggregation expression, design instance) pair. With 4 assemblies × 5 attributes each = up to 20 aggregation modules. However, `idiot_index` may not generate as a separate aggregation module if it references only local terms from the same assembly (depends on pipeline implementation). Also, the `misc_hardware_cost` EXPOSE_PURE attribute is handled as an alias, not a module.

**Estimated total**: 16 (existing) + N aggregation modules. The exact N will be determined during the first E2E run. The test should discover and assert the actual count rather than hardcoding a guess.

### Ground Truth Computation

#### Leaf Part Cost Modules

All 9 leaf cost CalcDefs follow the same pattern. Using design parameter bindings from `design.sysml`:

**1. PV Module (wattage=400.0, efficiency=0.21)**
- material_cost = 400.0 * 1.07 = 428.0
- fab_cost = 428.0 * 0.45 = 192.6
- install_cost = 428.0 * 0.30 = 128.4
- total_cost = 428.0 + 192.6 + 128.4 = 749.0
- idiot_index = 749.0 / 428.0 = 1.75

**2. Inverter (power_rating=2000.0)**
- material_cost = 2000.0 * 0.286 = 572.0
- fab_cost = 572.0 * 0.45 = 257.4
- install_cost = 572.0 * 0.30 = 171.6
- total_cost = 572.0 + 257.4 + 171.6 = 1001.0
- idiot_index = 1001.0 / 572.0 = 1.75

**3. Array BOS (string_count=4.0, panel_count=20.0)**
- material_cost = 4.0 * 150.0 + 20.0 * 30.0 = 600.0 + 600.0 = 1200.0
- fab_cost = 1200.0 * 0.45 = 540.0
- install_cost = 1200.0 * 0.30 = 360.0
- total_cost = 1200.0 + 540.0 + 360.0 = 2100.0
- idiot_index = 2100.0 / 1200.0 = 1.75

**4. Battery Pack (capacity_kwh=5.0, chemistry_factor=1.0)**
- material_cost = 5.0 * 171.5 * 1.0 = 857.5
- fab_cost = 857.5 * 0.45 = 385.875
- install_cost = 857.5 * 0.30 = 257.25
- total_cost = 857.5 + 385.875 + 257.25 = 1500.625
- idiot_index = 1500.625 / 857.5 = 1.75

**5. Hybrid Inverter (power_rating=10000.0)**
- material_cost = 10000.0 * 0.1714 = 1714.0
- fab_cost = 1714.0 * 0.45 = 771.3
- install_cost = 1714.0 * 0.30 = 514.2
- total_cost = 1714.0 + 771.3 + 514.2 = 2999.5
- idiot_index = 2999.5 / 1714.0 = 1.75

**6. Battery BOS (pack_count=8.0)**
- material_cost = 8.0 * 71.5 = 572.0
- fab_cost = 572.0 * 0.45 = 257.4
- install_cost = 572.0 * 0.30 = 171.6
- total_cost = 572.0 + 257.4 + 171.6 = 1001.0
- idiot_index = 1001.0 / 572.0 = 1.75

**7. Racking (panel_count=20.0, tilt_angle=30.0)**
- material_cost = 20.0 * 57.0 = 1140.0
- fab_cost = 1140.0 * 0.45 = 513.0
- install_cost = 1140.0 * 0.30 = 342.0
- total_cost = 1140.0 + 513.0 + 342.0 = 1995.0
- idiot_index = 1995.0 / 1140.0 = 1.75

**8. Electrical Panel (circuit_count=4.0)**
- material_cost = 150.0 + 4.0 * 34.0 = 150.0 + 136.0 = 286.0
- fab_cost = 286.0 * 0.45 = 128.7
- install_cost = 286.0 * 0.30 = 85.8
- total_cost = 286.0 + 128.7 + 85.8 = 500.5
- idiot_index = 500.5 / 286.0 = 1.75

**9. Permitting (system_capacity_kw=8.0)**
- material_cost = 0.0
- fab_cost = 0.0
- install_cost = 0.0
- total_cost = 8.0 * 187.5 = 1500.0
- idiot_index = 0.0

#### Allocation Module

**AllocationCostCalc (child_count=25.0, total_child_mass=50.0)**
- fastener_cost = 25.0 * 0.50 = 12.5
- seal_cost = 25.0 * 0.30 = 7.5
- wiring_cost = 50.0 * 2.0 = 100.0
- total_allocation = 12.5 + 7.5 + 100.0 = 120.0
- material_portion = 120.0 * 0.8 = 96.0

#### Aggregation Module Ground Truth

Aggregation modules use parametric multiply: `sum(child.attr)` → `count * single_instance_attr`.

**Solar Array capital_cost:**
- `module_count * pv_module.total_cost + inverter_count * inverter.total_cost + array_bos.total_cost + misc_hardware_cost`
- = 20 * 749.0 + 4 * 1001.0 + 2100.0 + 120.0 = 14980.0 + 4004.0 + 2100.0 + 120.0 = 21204.0

**Solar Array raw_material_cost:**
- = 20 * 428.0 + 4 * 572.0 + 1200.0 + 96.0 = 8560.0 + 2288.0 + 1200.0 + 96.0 = 12144.0

**Solar Array fabrication_cost:**
- = 20 * 192.6 + 4 * 257.4 + 540.0 = 3852.0 + 1029.6 + 540.0 = 5421.6

**Solar Array installation_cost:**
- = 20 * 128.4 + 4 * 171.6 + 360.0 = 2568.0 + 686.4 + 360.0 = 3614.4

**Solar Array idiot_index:**
- = 21204.0 / 12144.0 = 1.74604...

**Battery System capital_cost:**
- = 8 * 1500.625 + 2999.5 + 1001.0 = 12005.0 + 2999.5 + 1001.0 = 16005.5

**Battery System raw_material_cost:**
- = 8 * 857.5 + 1714.0 + 572.0 = 6860.0 + 1714.0 + 572.0 = 9146.0

**Battery System fabrication_cost:**
- = 8 * 385.875 + 771.3 + 257.4 = 3087.0 + 771.3 + 257.4 = 4115.7

**Battery System installation_cost:**
- = 8 * 257.25 + 514.2 + 171.6 = 2058.0 + 514.2 + 171.6 = 2743.8

**Battery System idiot_index:**
- = 16005.5 / 9146.0 = 1.74994...

**Site Infrastructure capital_cost:**
- = 1995.0 + 500.5 + 1500.0 = 3995.5

**Site Infrastructure raw_material_cost:**
- = 1140.0 + 286.0 + 0.0 = 1426.0

**Site Infrastructure fabrication_cost:**
- = 513.0 + 128.7 + 0.0 = 641.7

**Site Infrastructure installation_cost:**
- = 342.0 + 85.8 + 0.0 = 427.8

**Site Infrastructure idiot_index:**
- = 3995.5 / 1426.0 = 2.80119...

**Solar Battery Plant capital_cost:**
- = 21204.0 + 16005.5 + 3995.5 = 41205.0

**Solar Battery Plant raw_material_cost:**
- = 12144.0 + 9146.0 + 1426.0 = 22716.0

**Solar Battery Plant fabrication_cost:**
- = 5421.6 + 4115.7 + 641.7 = 10179.0

**Solar Battery Plant installation_cost:**
- = 3614.4 + 2743.8 + 427.8 = 6786.0

**Solar Battery Plant idiot_index:**
- = 41205.0 / 22716.0 = 1.81389...

#### System-Level CalcUsage Ground Truth (with design values)

These are already partially tested in existing ground truth, but using design-specific parameter values:

**EnergyProductionCalc** (p_net_mw=0.008, n_mod=1.0, plant_availability=0.159):
- annual_energy_mwh = 8760.0 * 0.008 * 1.0 * 0.159 = 11.13696

**AnnualizedOMCalc** (om_rate_per_kw_year=20.0, p_net_kw=8.0):
- annual_om_cost = 20.0 * 8.0 = 160.0

**AnnualizedFuelCalc** (fuel_unit_cost=0.0, fuel_consumption=0.0):
- annual_fuel_cost = 0.0 * 0.0 = 0.0

**AnnualizedFinancialCalc** (total_capex=41205.0, discount_rate=0.05, plant_lifetime=25.0):
- capital_recovery_factor = 0.05 * (1.05)^25 / ((1.05)^25 - 1.0)
  - (1.05)^25 = 3.38635494...
  - CRF = 0.05 * 3.38635494 / (3.38635494 - 1.0) = 0.16931775 / 2.38635494 = 0.07095...
- annualized_capital_cost = 0.07095... * 41205.0 = 2923.44...

**LCOECalc** (annualized_capital_cost, annual_om_cost=160.0, annual_fuel_cost=0.0, yearly_inflation=0.0245, plant_lifetime=25.0, annual_energy_mwh=11.13696):
- lcoe_per_mwh = (2923.44 + (160.0 + 0.0) * (1.0245)^25) / 11.13696
  - (1.0245)^25 = 1.83167...
  - = (2923.44 + 160.0 * 1.83167) / 11.13696
  - = (2923.44 + 293.067) / 11.13696
  - = 3216.51 / 11.13696 = 288.87...

**Note**: These system-level ground truth values depend on `total_capex` from the Solar Battery Plant aggregation. The `annualized_financial` CalcUsage binds `in total_capex = capital_cost`, which should wire to the plant's aggregation output channel. Testing this chain validates FR-5 (system-level CalcUsages wire correctly to hierarchy outputs).

### ADR Format

All existing ADRs follow: Status, Context, Decision, Consequences, Examples, References, Changelog. ADR-002 is the most complex with Rules, Amendments, and Implementation Notes sections. Each ADR uses the `## Section` and `### Subsection` Markdown hierarchy.

---

## Proposed Design

### Component 1: E2E Integration Test File

**File**: `tests/integration/test_costed_component_e2e.py` (NEW)

**Structure**: Three test classes following the existing pattern from `test_expression_compilation_e2e.py`:

```python
class TestSolarBatteryCostPatternE2E:
    """E2E validation of the complete Costed Component pipeline."""

    @pytest.fixture(scope="class")
    def solar_battery_output(self, tmp_path_factory) -> Path:
        # Run codegen once, shared across all test methods
        ...
```

#### Test Methods (mapped to FRs):

**FR-1: Codegen succeeds**
- `test_codegen_succeeds` — asserts `run_codegen(config)` returns True, `handwritten/` exists

**FR-2: Leaf-part cost modules**
- `test_leaf_part_cost_modules_generated` — finds all 9 leaf-part cost module impl files by expected name substrings, asserts all are auto-implemented

**FR-3: Allocation CalcUsages**
- `test_allocation_model_generated` — finds `allocation` impl, asserts auto-implemented

**FR-4: Assembly aggregation modules**
- `test_assembly_aggregation_modules_generated` — finds aggregation impl files for all 4 assemblies. The spec says "all 4 assembly aggregation modules" (one per assembly, capital_cost only), but the model has 5 aggregation attributes per assembly (capital_cost, raw_material_cost, fabrication_cost, installation_cost, idiot_index) = up to 20 total. **Spec deviation**: the actual count will be up to 20 aggregation modules (not 4). The test will discover the actual count on first run and assert all found aggregation impls are auto-implemented. The `capital_cost` aggregation for each of the 4 assemblies is the minimum check; additional aggregation modules are a bonus validated by ground truth

**FR-5: System-level wiring**
- `test_system_level_calcusage_wiring` — loads `pipeline.yaml`, verifies two key wiring paths:
  1. `annualized_financial.total_capex` is wired to a MODULE_OUTPUT channel from the plant's `capital_cost` aggregation (not an ENTRY_POINT) — validates hierarchy→system-level path
  2. `annualized_om.p_net_kw` is wired to a MODULE_OUTPUT channel from the `p_net_kw` computed attribute module (not an ENTRY_POINT) — validates computed-attribute→system-level path

**FR-6: Leaf-part numerical ground truth**
- `test_leaf_part_ground_truth` — parametrized test executing each leaf cost module's auto-implementation with design parameter values and comparing against hand-computed ground truth (see Research Findings above)
- Ground truth data as module-level constant `LEAF_PART_GROUND_TRUTH` with tuples of (name_pattern, input_dict, expected_outputs_dict)
- Follows existing pattern: `extract_function_body()` → `execute_impl_body()` → `assert_outputs_match()`

**FR-7: Aggregation numerical ground truth**
- `test_aggregation_ground_truth` — parametrized test for aggregation module auto-implementations
- Note: aggregation module inputs use symbolic channel names internally, but the auto-implementation function body takes `inputs.param_name`. The input names correspond to the `ModuleInput.name` fields. We need to determine exact input parameter names from the generated code (will be discovered during first E2E run).
- Ground truth data as module-level constant `AGGREGATION_GROUND_TRUTH`
- **Design decision**: Test aggregation modules with known upstream outputs as direct inputs (isolated execution), not with the full chained pipeline

**FR-8: Zero-backlog**
- `test_zero_backlog` — reads `IMPLEMENTATION_BACKLOG.md`, asserts "0 functions to implement"

**FR-9: Pipeline YAML topological ordering**
- `test_pipeline_yaml_topological_ordering` — loads `pipeline.yaml`, extracts module execution order, verifies:
  1. Leaf cost calcs appear before aggregation modules
  2. Aggregation modules appear before system-level CalcUsages
  3. Within each assembly, `capital_cost` and `raw_material_cost` aggregation modules appear before `idiot_index` aggregation module (since `idiot_index = capital_cost / raw_material_cost` depends on the other two as local-term inputs)

**FR-10: Valid Python**
- `test_all_impls_valid_python` — iterates all impl files, calls `ast.parse()` on each

**FR-11: Total impl file count**
- `test_total_impl_count` — asserts total impl count = expected (to be determined during first run, then hardcoded)

**FR-12: Aggregation YAML comments**
- `test_aggregation_yaml_source_comments` — loads `pipeline.yaml`, finds aggregation module entries, verifies `source: aggregation` appears in the module name/source field

**FR-13: Multiplicity entry points**
- `test_multiplicity_entry_points_in_schema` — examines generated parameter group schemas or entry point JSON, verifies multiplicity counts (module_count, inverter_count, pack_count) appear as Integer-type entry points

**FR-14: Update existing impl count**
- Handled in Component 2 (not in this file)

#### Ground Truth Data Constants

```python
# Each entry: (name_pattern, input_dict, expected_outputs_dict)
# Hand-computed from SysML model literals (library.sysml + design.sysml)

LEAF_PART_GROUND_TRUTH = [
    ("pvmodulecostcalc", {"wattage": 400.0, "efficiency": 0.21,
     "cost_per_watt": 1.07, "fab_factor": 0.45, "install_factor": 0.30},
     {"material_cost": 428.0, "fab_cost": 192.6, "install_cost": 128.4,
      "total_cost": 749.0, "idiot_index": 1.75}),
    # ... 8 more entries per Research Findings
]

ALLOCATION_GROUND_TRUTH = (
    "allocationcostcalc",
    {"child_count": 25.0, "total_child_mass": 50.0,
     "fastener_cost_per_child": 0.50, "seal_cost_per_child": 0.30,
     "wiring_cost_per_kg": 2.0},
    {"fastener_cost": 12.5, "seal_cost": 7.5, "wiring_cost": 100.0,
     "total_allocation": 120.0, "material_portion": 96.0}
)
```

**Note on aggregation ground truth**: The exact input parameter names for aggregation modules depend on how the graph builder names the `ModuleInput` fields. These will be discovered from the generated impl function signatures during the first E2E run. The expected output values are hand-computed above — only the input field names need empirical discovery.

**Note on full-chain LCOE validation**: The spec's epic success criteria mention "full LCOE pipeline executes end-to-end." This design tests each layer in isolation (leaf modules, aggregation modules, system-level modules) which validates numerical correctness at each stage. Full runtime chain execution (leaf → aggregation → system → LCOE) is out of scope per the spec ("TEAx runtime validation" is out of scope). However, the wiring tests (FR-5) and topological ordering test (FR-9) together verify the chain *would* produce correct results if executed at runtime.

**Implementation approach**: Write the test skeleton first with all structural assertions (FR-1, 2, 3, 4, 5, 8, 9, 10, 12, 13). Run codegen once manually to discover exact module names, input parameter names, and total counts. Then fill in the parametrized ground truth data and count assertions.

### Component 2: Existing Test Updates (FR-14)

**File**: `tests/integration/test_expression_compilation_e2e.py`
- Line 148: Update `assert len(impls) == 16` to new expected count

**File**: `tests/integration/test_computed_attributes_e2e.py`
- Line 241: Update `assert len(impls) == 16` to new expected count

Both assertions need the same new count (they test the same model). The count will be determined during the first E2E run.

### Component 3: Regression Guards (FR-15)

**No new regression test class.** The existing `TestPhase1Regression` in `test_computed_attributes_e2e.py:261-295` already covers:
- chain_spike: 3 impls, all auto-implemented (`test_chain_spike_still_works`)
- CATF MFE: 21 impls, no false-positive computed attrs (`test_catf_mfe_still_works`)

And `TestChainSpikeAutoImpl` in `test_expression_compilation_e2e.py:70-121` covers:
- chain_spike: all 3 auto-implemented, valid Python, backlog empty

And `TestCATFMFEValidation` in `test_expression_compilation_e2e.py:205-327` covers:
- CATF MFE: >= 19 auto, 2 stubs (PlasmaConfinement, TritiumBreedingRatio), backlog lists 2

These existing guards are sufficient for FR-15. Adding a duplicate class would create maintenance burden without additional coverage. The full `uv run pytest tests/` regression run validates all existing guards still pass.

### Component 4: ADR-006 — Part Hierarchy and Template Instantiation

**File**: `docs/architecture/ADR-006-part-hierarchy-template-instantiation.md` (NEW)

**Structure**:

```
# ADR-006: Part Hierarchy and Template Instantiation

## Status
Accepted - 2026-02-10

## Context
- Costed Component pattern requires CalcUsages in PartDefs (templates)
- Templates must be instantiated per design PartUsage with correct hierarchical QNs
- Redefinition (`:>>`) patterns bind template parameters via design overrides
- Spike (Item 1) validated SysIDE AST structure for all these patterns

## Decision

### Template Detection
- CalcUsages with `owning_type` that is a `PartDefinition` are templates
- CalcUsages with `owning_type` that is a `PartUsage` are concrete
- Detection: `type(calc_usage.owning_type).__name__ == 'PartDefinition'`

### Virtual CalcUsage Generation
- For each template CalcUsage, find all PartUsages instantiating the PartDef
- Generate one virtual CalcUsageData per (template, instance) pair
- QN format: `Design__plant__solar_array__pv_module__cost_model` (ADR-003 extension)
- Preserve `owning_part_def_qn` for binding rewriting

### Hierarchy-Aware Naming (ADR-003 Extension)
- Deep paths use `__` separator through full hierarchy
- Module name: lowercased full EQN
- Channel name: PQN = module_eqn + `__` + output_name

### `part redefines` Handling
- Three redefinition types: LITERAL, CHAIN, EXPRESSION
- LITERAL (`:>> wattage = 400.0`): rewrites virtual CalcUsage binding in Step 3.5
- CHAIN (`:>> capital_cost = cost_model.total_cost`): resolved in graph builder (Step 6.7)
- Deep-path overrides (`:>> pv_module.wattage = 400.0`): traverses target_path through hierarchy

## Consequences
### Positive
- Uniform treatment of template and concrete CalcUsages downstream
- Existing backtracker and graph builder work unchanged for virtual CalcUsages
- No changes to Jinja2 templates needed
### Negative
- Virtual CalcUsage explosion for models with many instance paths
- Uniform-array assumption: all instances share same bindings

## References
- Spike: `.project/active/hierarchy-spike/report.md`
- Item 2: commit 93c3910
- Item 4: commit 7887d07
- ADR-003: `docs/architecture/ADR-003-signal-identifiers.md`

## Changelog
| Date | Change |
|------|--------|
| 2026-02-10 | Initial version |
```

### Component 5: ADR-007 — Parametric Multiplicity and Aggregation

**File**: `docs/architecture/ADR-007-parametric-multiplicity-aggregation.md` (NEW)

**Structure**:

```
# ADR-007: Parametric Multiplicity and Aggregation

## Status
Accepted - 2026-02-10

## Context
- Assembly parts aggregate costs from child parts, some of which are arrays
- SysML uses `sum(child.attribute)` for array aggregation
- Two strategies: flat expansion (N individual modules) vs parametric multiply (1 module × count)
- Uniform arrays: all instances of pv_module share same parameters

## Decision

### Parametric Multiply Strategy
- `sum(pv_module.capital_cost)` → `module_count * pv_module__cost_model.total_cost`
- Single module per array child type (not N individual modules)
- Multiplicity count becomes Integer entry point in parameter schema
- Result: 1 aggregation module per assembly attribute, not N*M modules

### `sum()` Transformation
- SysIDE: `InvocationExpression` with function name `'sum'`
- Operand: `FeatureChainExpression` (e.g., `pv_module.capital_cost`)
- Transform: extract part_usage_name + attribute_name → `SumTerm`
- Compile: `count_param * resolved_channel` in generated expression

### Synthetic Aggregation Module Generation
- One `PipelineModule` per (aggregation expression, design instance) pair
- `ScopedAggregationData` composes `AggregationExpressionData` with `instance_path`
- Module EQN: `{instance_path}__{attribute_name}`
- `is_aggregation = True` flag on PipelineModule
- YAML comment: `# source: aggregation ({module_type})`

### AggregationExpressionData Model
- `sum_terms`: Array children with multiplicity (part_usage_name, attribute_name, multiplicity_attr, multiplicity_count)
- `singleton_terms`: Non-multiplied children (source_path)
- `local_terms`: PartDef-local attributes (e.g., misc_hardware_cost)
- `transformed_expression`: Python-compilable string after parametric multiply
- `has_unsupported_nodes`: False if fully compilable

### Uniform-Array Assumption
- All instances in an array share same parameter bindings
- Required condition: design overrides apply uniformly (`:>> pv_module.wattage = 400.0` applies to all 20 modules)
- Non-uniform arrays (different parameters per instance) would require flat expansion — not implemented, would need Approach E CalcDef

## Consequences
### Positive
- O(assemblies) modules, not O(assemblies × max_children)
- Auto-implementable with simple multiply-and-sum expressions
- Multiplicity counts are parameterizable via JSON inputs
### Negative
- Uniform-array assumption limits non-uniform designs
- Non-uniform arrays require manual CalcDef workaround

## References
- Spike Q4-Q5: `.project/active/hierarchy-spike/report.md`
- Item 3: commit 7887d07
- `ScopedAggregationData`: `src/sysml_codegen/generation/initialization.py`
- `AggregationExpressionData`: `src/sysml_codegen/extraction/data_models.py`

## Changelog
| Date | Change |
|------|--------|
| 2026-02-10 | Initial version |
```

### Component 6: ADR-002 Amendment (FR-18)

**File**: `docs/architecture/ADR-002-calculation-architecture.md` (EDIT)

**Two insertion points**:
1. **Amendment section**: Insert before the References section (before line 664, after the FORMULA amendment's "Modeling Guidance" section ends at ~line 662). This keeps all amendment sections grouped together before References/Changelog.
2. **Changelog entry**: Append a new row to the existing changelog table (after line 683).

**Amendment section content**:

```markdown
## Amendment: Hierarchy Pattern Relaxations (2026-02-10)

### Context

The COST-PATTERN epic (Items 1-4) introduces the Costed Component pattern where:
- Calculation definitions live in PartDefs (templates) rather than standalone library packages
- Assembly parts aggregate child costs via `:>>` redefinition expressions (not explicit CalcDefs)
- Multiplicity counts are structural properties (not user-parameterized values)

These patterns relax Rules 1, 3, and 4 under specific conditions.

### Rule 1 Relaxation: CalcDefs in PartDefs

**Original Rule 1**: All `calc def` declarations SHALL be in `models/library/` ONLY.

**Relaxation**: CalcDefs embedded within PartDefs in library packages are permitted. These are template CalcUsages, not standalone CalcDefs — they are instantiated per design PartUsage via virtual CalcUsage generation (see ADR-006).

**Condition**: The CalcDef must be in a library package (not a design package). It is embedded inside a PartDef which is also in the library.

**Example**:
```sysml
// library/solar_battery.sysml — PERMITTED
part def 'PV Module' :> 'Costed Component' {
    calc cost_model : PVModuleCostCalc { ... }  // Embedded in PartDef
}
```

### Rule 3 Relaxation: Aggregation via Redefinition

**Original Rule 3**: Design attributes SHALL contain literal values or bindings to calc outputs ONLY.

**Relaxation**: PartDef attributes MAY use `:>>` redefinition with aggregation expressions combining `sum()` of child costs and direct child attribute references.

**Condition**: All of the following must hold:
- Expression uses only `sum()` calls on child PartUsage attributes and direct child attribute references
- All array children are uniform (same parameters per instance)
- Expression is on a PartDef in library/ (not design/)
- The resulting aggregation expression is auto-compilable

**Example**:
```sysml
// PERMITTED: aggregation redefinition on PartDef
:>> capital_cost = sum(pv_module.capital_cost) + array_bos.capital_cost + misc_hardware_cost;
```

### Rule 4 Relaxation: Multiplicity as Structural Property

**Original Rule 4 (implicit)**: Multiplicity is a parameter that users may override per scenario.

**Relaxation**: For uniform arrays under parametric multiply, multiplicity counts are Integer entry points in parameter schemas but default to the PartDef-declared value. Users MAY override them, but the default correctly reflects the design model.

**Condition**: Non-uniform arrays still require Approach E (explicit CalcDef with multiplicity as input parameter and per-instance outputs).

### When Approach E Is Still Required

The original rules (no relaxation) apply when ANY of:
- Array children have non-uniform parameters (different values per instance)
- Aggregation logic involves conditionals, functions, or non-arithmetic operators
- Context-dependent calculations need per-instance differentiation
- The aggregation expression has `has_unsupported_nodes = True`
```

**Changelog entry** (append to existing table):

```
| 2026-02-10 | **Amendment: Hierarchy pattern relaxations** (Rules 1, 3, 4). CalcDefs embedded in library PartDefs permitted. Aggregation redefinition expressions on PartDefs permitted. Multiplicity as structural property with Integer entry point. Approach E still required for non-uniform arrays. See ADR-006, ADR-007. |
```

### Component 7: Epic Closure

**File**: `.project/backlog/epic_costed_component_pattern.md` (EDIT)
- Update epic status to Complete
- Update Item 5 status to Complete
- Fill in Lessons Learned section

---

## Potential Risks

1. **Exact module count unknown until first run**: The total impl count depends on how many aggregation modules the pipeline actually generates from the solar_battery model. Mitigation: run codegen once in the first implementation step to discover the count, then hardcode assertions.

2. **Aggregation input parameter names unknown**: The `ModuleInput.name` fields for aggregation modules are generated by the graph builder's channel resolution logic. Mitigation: inspect generated impl files to discover actual parameter names before writing parametrized ground truth tests.

3. **Ground truth sensitivity to floating-point**: Aggregation expressions chain multiple multiplications. The 1e-10 tolerance should be sufficient for the calculations involved (all are simple arithmetic on small numbers). No mitigation needed.

4. **`annualized_financial.total_capex` wiring**: This is the key integration test — system-level CalcUsage must wire `total_capex` to the Solar Battery Plant's `capital_cost` aggregation output. If this wiring fails, it indicates a binding resolution bug in the backtracker. Mitigation: test this explicitly in FR-5.

5. **Existing test count update**: If the updated count in `test_expression_compilation_e2e.py` is wrong, it will break the existing test suite. Mitigation: determine correct count from the E2E run before updating.

---

## Integration Strategy

The new test file is additive — it doesn't modify existing test infrastructure. The only modifications to existing files are:
- Two count assertion updates (FR-14)
- ADR-002 amendment (append-only)

All other deliverables are new files. No production code changes.

**Dependency ordering**:
1. Run codegen on solar_battery to discover exact counts and parameter names
2. Write structural tests (FR-1, 2, 3, 4, 5, 8, 9, 10, 12, 13)
3. Write ground truth tests (FR-6, FR-7)
4. Update existing test counts (FR-14)
5. Verify existing regression guards pass (FR-15) — no new code needed
6. Write ADRs (FR-16, 17, 18)
7. Close epic

---

## Validation Approach

**Testing strategy**: All validation is via pytest.
- `uv run pytest tests/integration/test_costed_component_e2e.py -v` for the new file
- `uv run pytest tests/` for full regression
- `uv run mypy src/` and `uv run ruff check src/` for static analysis (no changes expected)

**Success criteria**:
- All new tests pass on first run
- All existing 450+ tests pass with zero regressions
- `IMPLEMENTATION_BACKLOG.md` shows "0 functions to implement" for solar_battery
- All auto-implementations are valid Python (`ast.parse()`)
- Numerical ground truth matches hand-computed values within 1e-10

**Manual verification**:
- Inspect generated `pipeline.yaml` to visually confirm topological ordering
- Inspect generated impl files to confirm `AUTO_IMPLEMENTED = True` marker

---

Next Step: After approval → `/_my_plan` or `/_my_implement`
