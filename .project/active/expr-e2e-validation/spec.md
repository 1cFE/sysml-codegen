# Spec: End-to-End Validation on Real Models

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-08 01:41 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Epic:** EXPR-CODEGEN Item 5

---

## Business Goals

### Why This Matters

Items 1-4 of the EXPR-CODEGEN epic built and integrated an expression compiler into the codegen pipeline. All components are unit-tested and the chain_spike model (3 simple CalcDefs) is validated end-to-end. But the epic's critical success factor -- >=10/15 solar_battery CalcDefs auto-implemented, outputs matching handwritten implementations within 1e-10 -- remains unverified against real-world models.

More critically, **Pattern B (multi-step intermediate) has zero runtime ground truth.** The Item 2 spike report explicitly flagged this: all 10 solar_battery cost CalcDef handwritten impls are `NotImplementedError` stubs, so the most topological-sort-sensitive pattern has only syntax validation. This item closes that gap by creating hand-computed ground truth for Pattern B CalcDefs from the CATF fusion models.

### Success Criteria

- [ ] Solar_battery: >=10 of 15 CalcDefs auto-implemented
- [ ] Solar_battery: 5 ground truth CalcDefs (Patterns A, C, D) match handwritten impls within 1e-10
- [ ] CATF: Pattern B ground truth for EngineeringQFactor (3-level cascade) and MagnetCryogenicLoad (4 undeclared intermediates) match hand-computed values within 1e-10
- [ ] Non-compilable CalcDefs have accurate MANUAL_REQUIRED / PARTIALLY_COMPILABLE reasons
- [ ] IMPLEMENTATION_BACKLOG.md lists only genuinely manual work
- [ ] Integration tests added and passing
- [ ] Validation report documents per-CalcDef results

### Priority

P1 -- final item in the in-progress P1 EXPR-CODEGEN epic. Items 1-4 are complete (including follow-up bug fixes in commit a1d0028). All 144 automated tests pass. Manual tests 1-7 all pass.

---

## Problem Statement

### Current State

- Pipeline integration is complete and unit-tested (Item 4)
- chain_spike model (3 Pattern A CalcDefs) validated in manual testing
- Manual tests 1-7 all pass after bug fix commit a1d0028
- **No integration test exists** that runs codegen on real models and validates output
- **Pattern B has zero runtime ground truth** -- the 10 solar_battery cost CalcDefs with intermediate dependencies all have stub handwritten impls
- Unknown: whether CATF model's 22 CalcDefs classify correctly through the full pipeline
- Unknown: whether auto-generated code for CATF Pattern B CalcDefs produces numerically correct results

### Desired Outcome

- Codegen validated on solar_battery (15 CalcDefs) and CATF MFE (22 CalcDefs) models
- Pattern B runtime ground truth established via hand-computed expected values
- Integration test suite prevents regressions
- Validation report documents per-CalcDef results for both model suites

---

## Scope

### In Scope

1. **Solar_battery model validation**
   - Run codegen on `tests/fixtures/solar_battery_model/`
   - Verify >=10 of 15 CalcDefs auto-implemented (FULLY_COMPILABLE)
   - Execute 5 ground truth CalcDefs (EnergyProductionCalc, AnnualizedOMCalc, AnnualizedFuelCalc, AnnualizedFinancialCalc, LCOECalc) with test inputs and compare against handwritten impl output within 1e-10 tolerance
   - Verify non-compilable CalcDefs get proper stubs with accurate reasons

2. **CATF MFE model fixture creation**
   - Copy relevant SysML files from `/home/reid/fusion_modeling/models` into `tests/fixtures/catf_mfe_model/`
   - Include library files (physics, geometry, thermal loads) and design files needed for a viable codegen run
   - Validate fixture is self-contained (codegen runs without external dependencies)

3. **CATF MFE model validation**
   - Run codegen on `tests/fixtures/catf_mfe_model/`
   - Verify auto-implementation count across 22 CalcDefs
   - Verify PlasmaConfinement and TritiumBreedingRatio classified as PARTIALLY_COMPILABLE with accurate reasons
   - Verify ThermalEfficiency (no expression) classified as MANUAL_REQUIRED

4. **Pattern B ground truth** (hand-computed expected values)
   - **EngineeringQFactor** (3-level declared output cascade):
     - Inputs: `p_electric_gross=1500.0`, `p_auxiliary_total=200.0`
     - Expected: `q_eng=7.5`, `f_recirculating=0.1333...`, `p_net=1300.0`
     - Tests topological sort of declared output-to-output references
   - **MagnetCryogenicLoad** (4 undeclared intermediates):
     - Inputs: `p_neutron`, `magnet_surface_area`, `first_wall_area`, `magnet_volume`, `operating_temp`, `carnot_efficiency` (specific values TBD in design)
     - Expected: hand-computed from `nuclear_heating → heat_leak → ac_losses → thermal_load_cryo → cooling_power`
     - Tests undeclared intermediate discovery, compilation, emission ordering, and exclusion from return statement
   - Execute auto-generated `_impl.py` code with test inputs, assert outputs within 1e-10 tolerance

5. **Backlog report validation**
   - solar_battery: IMPLEMENTATION_BACKLOG.md excludes auto-implemented CalcDefs, lists only genuinely manual work
   - CATF: IMPLEMENTATION_BACKLOG.md lists only non-compilable CalcDefs (PlasmaConfinement, TritiumBreedingRatio, ThermalEfficiency)

6. **Regression integration tests**
   - Add `tests/integration/test_expression_compilation_e2e.py`
   - Follow existing patterns: `GenerationConfig` + `run_codegen()` + `tmp_path` + content assertions
   - Test chain_spike: all 3 CalcDefs auto-implemented, AUTO_IMPLEMENTED sentinel present, no NotImplementedError
   - Test solar_battery: >=10 auto-implemented, 5 ground truth numerical comparisons
   - Test CATF: auto-implementation count, Pattern B ground truth, non-compilable stub accuracy

7. **Validation report**
   - `.project/active/expr-e2e-validation/report.md`
   - Per-CalcDef results table for both model suites
   - Pattern coverage summary (which patterns have runtime ground truth)

### Out of Scope

- Performance benchmarking
- Phase 2 (attribute expression) validation
- CI/CD integration
- Creating handwritten `_impl.py` files for the fusion models (hand-computed values used instead)
- Fixing any bugs discovered during validation (separate follow-up items if needed)

### Edge Cases & Considerations

- CATF fixture must include enough library files for SysIDE to resolve all imports (physics, geometry, thermal loads, materials, types, foundation)
- Cross-file EXPOSE pattern bindings in CATF design files may require all 9 design files to be present
- PlasmaConfinement and TritiumBreedingRatio are Phase 1 passthroughs -- their compilable outputs (p_fusion, tbr) are trivial assignments, not real Pattern B
- Hand-computed ground truth values must be independently derived from the SysML expressions, not from running the compiler (to avoid circular validation)

---

## Requirements

### Functional Requirements

> Requirements below are from user's request unless marked [INFERRED] or [FROM INVESTIGATION]

1. **FR-1**: Run codegen on solar_battery model and verify >=10 of 15 CalcDefs are auto-implemented
2. **FR-2**: Compare 5 solar_battery ground truth CalcDefs (Patterns A, C, D) against handwritten impls within 1e-10 tolerance
3. **FR-3**: Create CATF MFE fixture by copying relevant SysML files from `/home/reid/fusion_modeling/models` into `tests/fixtures/catf_mfe_model/`
4. **FR-4**: Run codegen on CATF MFE model and verify auto-implementation classification across 22 CalcDefs
5. **FR-5**: Create hand-computed Pattern B ground truth for EngineeringQFactor (3-level declared output cascade)
6. **FR-6**: Create hand-computed Pattern B ground truth for MagnetCryogenicLoad (4 undeclared intermediates)
7. **FR-7**: Execute auto-generated Pattern B code and assert outputs match hand-computed values within 1e-10
8. **FR-8**: Verify IMPLEMENTATION_BACKLOG.md excludes FULLY_COMPILABLE CalcDefs for both model suites
9. **FR-9**: Verify non-compilable CalcDefs (PlasmaConfinement, TritiumBreedingRatio) have accurate stub reasons
10. **FR-10**: Add integration test file `tests/integration/test_expression_compilation_e2e.py` with regression tests
11. **FR-11**: [INFERRED] Verify CATF fixture is self-contained (codegen runs without referencing `/home/reid/fusion_modeling/models`)
12. **FR-12**: [INFERRED] Produce validation report with per-CalcDef results table

---

## Acceptance Criteria

### Core Functionality
- [ ] AC-1: solar_battery codegen produces >=10 auto-implemented `_impl.py` files with `AUTO_IMPLEMENTED = True` (FR-1)
- [ ] AC-2: 5 solar_battery ground truth CalcDefs produce outputs matching handwritten impls within 1e-10 relative tolerance (FR-2)
- [ ] AC-3: `tests/fixtures/catf_mfe_model/` exists with self-contained SysML files; `uv run sysml-codegen generate --models tests/fixtures/catf_mfe_model/ --output /tmp/catf-test --package-name catf_mfe` succeeds (FR-3, FR-11)
- [ ] AC-4: CATF codegen correctly classifies all 21 CalcDefs: 19 FULLY_COMPILABLE, 2 PARTIALLY_COMPILABLE (PlasmaConfinement, TritiumBreedingRatio) (FR-4, FR-9). ThermalEfficiency (no expression) is excluded -- it lives in `tests/documented_calculation.sysml`, not in the CATF library/design files.
- [ ] AC-5: EngineeringQFactor auto-generated code with inputs `(1500.0, 200.0)` produces `q_eng=7.5, f_recirculating=0.1333..., p_net=1300.0` within 1e-10 (FR-5, FR-7)
- [ ] AC-6: MagnetCryogenicLoad auto-generated code with chosen test inputs produces hand-computed expected values within 1e-10 (FR-6, FR-7)
- [ ] AC-7: solar_battery IMPLEMENTATION_BACKLOG.md lists only non-auto-implemented CalcDefs (FR-8)
- [ ] AC-8: CATF IMPLEMENTATION_BACKLOG.md lists only PlasmaConfinement and TritiumBreedingRatio (FR-8)

### Quality & Integration
- [ ] AC-9: All existing 144 tests continue to pass with zero regressions
- [ ] AC-10: `tests/integration/test_expression_compilation_e2e.py` exists and passes (FR-10)
- [ ] AC-11: Validation report at `.project/active/expr-e2e-validation/report.md` documents per-CalcDef results (FR-12)
- [ ] AC-12: Pattern B ground truth values are independently derived from SysML expressions (not from running the compiler)

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_expression_aware_codegen.md`
- **Item 2 Spike Report:** `.project/active/expr-spike-compile/report.md` (compilation proof, Pattern B coverage gap flagged)
- **Item 4 Manual Test Plan:** `.project/active/expr-pipeline-integration/manual-test-plan.md` (7/7 PASS)
- **Item 4 Spec:** `.project/active/expr-pipeline-integration/spec.md`
- **Item 4 Design:** `.project/active/expr-pipeline-integration/design.md`
- **CATF Source Models:** `/home/reid/fusion_modeling/models` (source for fixture creation)
- **Design:** `.project/active/expr-e2e-validation/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
