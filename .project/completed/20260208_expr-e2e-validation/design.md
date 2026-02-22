# Design: End-to-End Validation on Real Models

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-08
**Branch:** cost-pattern
**Epic:** EXPR-CODEGEN Item 5

## Overview

Design for end-to-end validation of expression-aware codegen on real SysML models (solar_battery, CATF MFE). Creates a CATF fixture from fusion_modeling repo, establishes Pattern B runtime ground truth via hand-computed expected values, and adds integration tests that run the full pipeline and validate output correctness.

## Related Artifacts

- **Spec:** `.project/active/expr-e2e-validation/spec.md`
- **Epic:** `.project/backlog/epic_expression_aware_codegen.md`
- **Item 2 Spike Report:** `.project/active/expr-spike-compile/report.md`
- **Item 4 Design:** `.project/active/expr-pipeline-integration/design.md`
- **Spike Comparison Script:** `scripts/spike_compile_expressions.py`

---

## Research Findings

### 1. Existing Integration Test Patterns

**File:** `tests/integration/test_full_pipeline.py`

The established pattern for end-to-end codegen tests:

```python
config = GenerationConfig(
    models_path=model_path,
    output_path=tmp_path / "output",
    package_name="test_pkg",
)
success = run_codegen(config)
assert success
```

Output validation uses file existence checks, content string assertions, `rglob()` for file counting, and JSON parsing. The `TestRunCodegenPhases` class tests 5 phases sequentially. `TestCodegenRuntimeGapFixes` tests specific acceptance criteria against the chain_spike_model.

**Key imports:** `GenerationConfig` from `sysml_codegen.cli`, `run_codegen` from `sysml_codegen.cli`.

**Fixtures:** Defined in `tests/conftest.py` -- `fixtures_path`, `chain_spike_model_path`, `sample_model_path`, `temp_output_dir`. Pattern is `fixtures_path / "model_name"`.

### 2. Auto-Impl Template Structure

**File:** `src/sysml_codegen/templates/auto_implementation.py.jinja2`

Generated auto-impl files have this structure:
```python
AUTO_IMPLEMENTED = True

from {package}.modules.{module_path} import {InputClass}

def run_{calcname}(inputs: {InputClass}) -> {return_type}:
    # Intermediate assignments (undeclared intermediates only)
    intermediate_var = (expression)
    # Return
    return (expression)           # single output
    return (expr1, expr2, ...)    # multi output
```

The function takes a Pydantic `inputs` object. All expressions reference inputs via `inputs.field_name` and intermediates via bare names.

### 3. Spike Script Execution Approach

**File:** `scripts/spike_compile_expressions.py:526-702`

The spike script executes generated code using `exec()` with `SimpleNamespace`:
- Compiled expressions: execute assignment lines via `exec()`, collect output values from `exec_globals`
- Handwritten impls: wrap body in `def _hw(inputs):`, `exec()` to define function, call with `SimpleNamespace(**input_dict)`
- Comparison: relative error `abs(compiled - handwritten) / abs(handwritten)` with 1e-10 threshold

This is the right approach for integration tests too -- we cannot `import` generated modules at test time because they depend on the generated package structure (e.g., `from solar_battery.modules.solarbatterylibrary.energyproductioncalc import EnergyProductionCalcInput`). Instead, we extract the function body and execute it with `SimpleNamespace` inputs.

### 4. Solar Battery Ground Truth

**Handwritten impls location:** `/home/reid/1cfe/fusion-tea/generated/solar_battery/handwritten/solarbatterylibrary/`

5 CalcDefs with real implementations (rest are `NotImplementedError` stubs):
- `EnergyProductionCalc` -- Pattern A, 1 output, `8760.0 * p_net_mw * n_mod * plant_availability`
- `AnnualizedOMCalc` -- Pattern A, 1 output, `om_rate_per_kw_year * p_net_kw`
- `AnnualizedFuelCalc` -- Pattern A, 1 output, simple multiplication
- `AnnualizedFinancialCalc` -- Pattern C, 2 outputs (CRF formula + annualized_capital_cost)
- `LCOECalc` -- Pattern C, 1 output, compound expression

These impls live in the *fusion-tea* repo, not sysml-codegen. Tests MUST NOT import from fusion-tea. The test approach reads the handwritten file, extracts the function body, wraps it in `exec()`, and compares numerically -- same as the spike script.

### 5. CATF Model Structure

**Source:** `/home/reid/fusion_modeling/models/`

21 CalcDefs across library files (test CalcDefs like `ThermalEfficiency` in `tests/documented_calculation.sysml` are excluded from the fixture). 7 are Pattern B (multi-step intermediate). Per the Item 2 spike report: 19 FULLY_COMPILABLE, 2 PARTIALLY_COMPILABLE (PlasmaConfinement, TritiumBreedingRatio).

**Self-contained fixture** (21 SysML files):
- Library: `foundation.sysml`, `types.sysml`, `physics/geometry.sysml`, `physics/power_balance.sysml`, `physics/performance_metrics.sysml`, `physics/fusion_physics.sysml`, `physics/thermal.sysml`, `physics/confinement.sysml`, `physics/neutronics.sysml`, `analyses/thermal_loads.sysml`
- Design: `catf_mfe/radial_build.sysml`, `catf_mfe/magnets.sysml`, `catf_mfe/blanket.sysml`, `catf_mfe/heating.sysml`, `catf_mfe/shield.sysml`, `catf_mfe/vacuum.sysml`, `catf_mfe/tritium.sysml`, `catf_mfe/physics.sysml`, `catf_mfe/system.sysml`

All design files import from each other via cross-file EXPOSE pattern. physics.sysml imports from ALL subsystem design files. system.sysml is the top-level integrator. Omitting any design file would break import resolution.

### 6. Pattern B Ground Truth Expressions

**EngineeringQFactor** (`performance_metrics.sysml:140-164`):
- 3 declared outputs, 0 undeclared intermediates
- `q_eng = p_electric_gross / p_auxiliary_total`
- `f_recirculating = 1.0 / q_eng`
- `p_net = p_electric_gross * (1.0 - f_recirculating)`
- Dependency chain: `q_eng → f_recirculating → p_net`

**MagnetCryogenicLoad** (`thermal_loads.sysml:45-85`):
- 1 declared output, 4 undeclared intermediates
- `nuclear_heating = 0.05 * p_neutron * (magnet_surface_area / first_wall_area)`
- `ac_losses = 0.0`
- `heat_leak = magnet_volume * 0.05`
- `thermal_load_cryo = nuclear_heating + ac_losses + heat_leak`
- `cooling_power = (thermal_load_cryo / operating_temp) * (300.0 / carnot_efficiency)`
- Dependency chain: `nuclear_heating, ac_losses, heat_leak → thermal_load_cryo → cooling_power`

---

## Proposed Design

### Component 1: CATF MFE Test Fixture

**Location:** `tests/fixtures/catf_mfe_model/`

Copy the complete CATF model from `/home/reid/fusion_modeling/models/` preserving directory structure. The fixture MUST include all library and design files because SysIDE resolves imports globally -- missing any file could cause import resolution failures.

**Directory structure:**
```
tests/fixtures/catf_mfe_model/
  library/
    foundation.sysml
    types.sysml
    materials.sysml
    system_definition.sysml
    physics/
      fusion_physics.sysml
      power_balance.sysml
      performance_metrics.sysml
      geometry.sysml
      thermal.sysml
      confinement.sysml
      neutronics.sysml
    analyses/
      thermal_loads.sysml
  designs/
    catf_mfe/
      system.sysml
      physics.sysml
      radial_build.sysml
      magnets.sysml
      blanket.sysml
      heating.sysml
      shield.sysml
      vacuum.sysml
      tritium.sysml
```

**Rationale for copying all files**: The CATF design files have extensive cross-file imports (physics.sysml imports from magnets, blanket, heating, vacuum, tritium, and system). SysIDE loads all `.sysml` files in the model path. Trying to create a minimal subset risks breaking import resolution for no meaningful savings (~30KB total).

**Excluded:** `tests/`, `test/`, `simple_test.sysml`, `requirements.sysml`, `components/` -- these are test/reference files not part of the CATF design instance.

### Component 2: Test Fixtures (conftest.py)

**File:** `tests/conftest.py` (modify existing)

Add two new fixtures following the established pattern:

```python
@pytest.fixture
def solar_battery_model_path(fixtures_path: Path) -> Path:
    return fixtures_path / "solar_battery_model"

@pytest.fixture
def catf_mfe_model_path(fixtures_path: Path) -> Path:
    return fixtures_path / "catf_mfe_model"
```

### Component 3: Test Helpers Module

**File:** `tests/helpers/impl_execution.py` (new)

Shared utilities for executing generated impl code and comparing results. Extracted as a module (not private to the test file) to avoid duplicating the spike script's execution logic (`scripts/spike_compile_expressions.py:549-702`) and to allow future test files to reuse.

**`find_impl_files(output_path: Path) -> list[Path]`**
- `list((output_path / "handwritten").rglob("*_impl.py"))` excluding `__init__.py`
- Returns sorted list for deterministic ordering

**`is_auto_implemented(impl_path: Path) -> bool`**
- Reads file, returns `"AUTO_IMPLEMENTED = True" in content`

**`extract_function_body(impl_path: Path) -> str | None`**
- Extracts the function body (after `def run_*` line, skipping docstring)
- Adapted from spike script's `extract_handwritten_body()` (`scripts/spike_compile_expressions.py:549-606`)
- Returns dedented body string, or None if stub (contains `NotImplementedError`)

**`execute_impl_body(body: str, input_dict: dict[str, float], output_names: list[str]) -> dict[str, float]`**
- Wraps body in `def _fn(inputs):`, executes with `SimpleNamespace(**input_dict)`
- Handles single return (→ first output name) and tuple return (→ ordered output names)
- Returns `{output_name: value}` dict

**`assert_outputs_match(actual: dict, expected: dict, tolerance: float = 1e-10)`**
- For each output name, computes relative error
- Uses `abs(actual - expected) / abs(expected)` with special case for both-zero
- Raises `AssertionError` with detailed message on mismatch

Also create `tests/helpers/__init__.py` (empty).

### Component 4: Integration Test File

**File:** `tests/integration/test_expression_compilation_e2e.py` (new)

This is the main deliverable. Structured as three test classes, one per model suite.

**Fixture strategy:**
- **`TestChainSpikeAutoImpl`**: Uses function-scope helper (lightweight model, 3 CalcDefs, fast codegen)
- **`TestSolarBatteryValidation`**: Uses class-scoped fixture via `tmp_path_factory` (15 CalcDefs, one codegen run shared by ~8 tests)
- **`TestCATFMFEValidation`**: Uses class-scoped fixture via `tmp_path_factory` (21 CalcDefs, one codegen run shared by ~6 tests)

```python
# Class-scoped fixtures run codegen once per test class, not once per
# test method. This avoids redundant SysIDE model loading (~5-10s each)
# while keeping test isolation between classes.
@pytest.fixture(scope="class")
def solar_battery_output(solar_battery_model_path, tmp_path_factory):
    ...
```

#### 4.1 Test Class: `TestChainSpikeAutoImpl`

Quick smoke test that the simplest model produces auto-implementations. Follows existing `TestCodegenRuntimeGapFixes` pattern. Uses function-scope `tmp_path` (lightweight model -- no need for class-scoped caching).

**`test_all_three_calcdefs_auto_implemented(chain_spike_model_path, tmp_path)`**
- Run codegen on chain_spike via inline `GenerationConfig` + `run_codegen()`
- Find all `_impl.py` files, assert 3 found
- Assert all 3 have `AUTO_IMPLEMENTED = True`
- Assert none contain `NotImplementedError`

**`test_auto_impl_files_are_valid_python(chain_spike_model_path, tmp_path)`**
- For each impl file, `ast.parse(content)` -- no SyntaxError

**`test_backlog_empty_for_chain_spike(chain_spike_model_path, tmp_path)`**
- Read `IMPLEMENTATION_BACKLOG.md`
- Assert `"0 functions"` in content (all CalcDefs are FULLY_COMPILABLE)

#### 4.2 Test Class: `TestSolarBatteryValidation`

Validates the epic's primary success criteria: >=10/15 auto-implemented, 5 ground truth comparisons. Uses class-scoped `solar_battery_output` fixture (one codegen run shared by all tests in class).

**`test_auto_implementation_count(solar_battery_output)`**
- Count `_impl.py` files with `AUTO_IMPLEMENTED = True`
- Assert `count >= 10` (epic success criterion)
- Assert total impl files == 15

**`test_non_compilable_calcdefs_get_stubs(solar_battery_output)`**
- For each impl file WITHOUT `AUTO_IMPLEMENTED = True`, assert `NotImplementedError` present
- These should be 0 (all 15 solar_battery CalcDefs have expressions) or the few that fail compilation

**`test_ground_truth[parametrized x5]`**

A single parametrized test covering all 5 ground truth CalcDefs. Uses `@pytest.mark.parametrize` to reduce repetition while keeping per-CalcDef failure isolation:

```python
SOLAR_BATTERY_GROUND_TRUTH = [
    # (calc_name_lower, handwritten_filename, input_dict, output_names)
    ("energyproductioncalc", "energyproductioncalc_impl.py",
     {"p_net_mw": 100.0, "n_mod": 2.0, "plant_availability": 0.9},
     ["annual_energy_mwh"]),
    ("annualizedomcalc", "annualizedomcalc_impl.py",
     {"om_rate_per_kw_year": 20.0, "p_net_kw": 8.0},
     ["annual_om_cost"]),
    ("annualizedfuelcalc", "annualizedfuelcalc_impl.py",
     {"fuel_unit_cost": 10.0, "fuel_consumption": 50.0},
     ["annual_fuel_cost"]),
    ("annualizedfinancialcalc", "annualizedfinancialcalc_impl.py",
     {"total_capex": 1000.0, "discount_rate": 0.05, "plant_lifetime": 25.0},
     ["capital_recovery_factor", "annualized_capital_cost"]),
    ("lcoecalc", "lcoecalc_impl.py",
     {"annualized_capital_cost": 100.0, "annual_om_cost": 20.0,
      "annual_fuel_cost": 5.0, "yearly_inflation": 0.025,
      "plant_lifetime": 25.0, "annual_energy_mwh": 1000.0},
     ["lcoe_per_mwh"]),
]

@pytest.mark.parametrize("calc_name,hw_file,inputs,outputs", SOLAR_BATTERY_GROUND_TRUTH)
def test_ground_truth(self, solar_battery_output, calc_name, hw_file, inputs, outputs):
```

Each parametrized instance:
1. Finds the auto-impl file matching `calc_name` in the codegen output
2. Extracts function body via `extract_function_body()`
3. Executes with test inputs via `execute_impl_body()`
4. Reads the handwritten impl from `SOLAR_BATTERY_HANDWRITTEN_DIR / hw_file`
5. Extracts handwritten body, executes with same inputs
6. Asserts outputs match within 1e-10 via `assert_outputs_match()`

**`test_backlog_excludes_auto_implemented(solar_battery_output)`**
- Read `IMPLEMENTATION_BACKLOG.md`
- If any CalcDefs are non-compilable, they should appear in backlog
- FULLY_COMPILABLE CalcDefs MUST NOT appear

**Handwritten impl path handling**: The handwritten impl directory is a constant:

```python
SOLAR_BATTERY_HANDWRITTEN_DIR = Path(
    "/home/reid/1cfe/fusion-tea/generated/solar_battery/"
    "handwritten/solarbatterylibrary"
)
```

The parametrized ground truth test uses `pytest.mark.skipif(not SOLAR_BATTERY_HANDWRITTEN_DIR.exists(), ...)`. This keeps the tests runnable on machines without the fusion-tea repo -- the non-ground-truth tests (auto-impl count, backlog, syntax validity) still run.

#### 4.3 Test Class: `TestCATFMFEValidation`

Validates CATF model and Pattern B ground truth. Uses class-scoped `catf_mfe_output` fixture (one codegen run shared by all tests in class).

The fixture contains 21 CalcDefs: 19 FULLY_COMPILABLE, 2 PARTIALLY_COMPILABLE. ThermalEfficiency (no-expression CalcDef) is NOT present -- it lives in `tests/documented_calculation.sysml` which is excluded from the fixture.

**`test_codegen_succeeds(catf_mfe_output)`**
- Implicitly validated by the class-scoped fixture (asserts success during setup)
- Basic smoke test that the fixture is self-contained

**`test_auto_implementation_classification(catf_mfe_output)`**
- Count auto-implemented vs stub files
- Assert `auto_count >= 19` (19 FULLY_COMPILABLE per Item 2 spike report)
- Assert `stub_count == 2` (PlasmaConfinement, TritiumBreedingRatio)
- Assert `total_count == 21` (all CalcDefs in the fixture)

**`test_partially_compilable_stubs_have_accurate_reasons(catf_mfe_output)`**
- Find impl files for PlasmaConfinement and TritiumBreedingRatio
- Assert both contain `NotImplementedError` (PARTIALLY_COMPILABLE falls through to stub per FR-12 in Item 4)
- Assert neither has `AUTO_IMPLEMENTED = True`
- Assert stub content mentions the CalcDef name in the NotImplementedError message (e.g., `"PlasmaConfinement"` in the error string)
- Assert stub content contains a SysML source reference (e.g., `"See SysML source:"`)
- Assert `IMPLEMENTATION_BACKLOG.md` lists both CalcDefs by name with their source file references

This satisfies FR-9 (stub reason accuracy). The stub template (`implementation_stencil.py.jinja2:15-18`) generates `raise NotImplementedError("Manual implementation required for {calc_name}. See SysML source: {sysml_source}")`, so the CalcDef name and SysML source path are the verifiable "reason" content.

**`test_pattern_b_engineering_q_factor(self, catf_mfe_output)`**

Pattern B ground truth -- 3-level declared output cascade:

```python
# Hand-computed from SysML expressions:
# q_eng = p_electric_gross / p_auxiliary_total = 1500.0 / 200.0 = 7.5
# f_recirculating = 1.0 / q_eng = 1.0 / 7.5 = 0.13333333333333333
# p_net = p_electric_gross * (1.0 - f_recirculating) = 1500.0 * 0.8666... = 1300.0

inputs = {"p_electric_gross": 1500.0, "p_auxiliary_total": 200.0}
expected = {
    "q_eng": 7.5,
    "f_recirculating": 1.0 / 7.5,  # 0.13333333333333333
    "p_net": 1300.0,
}
```

Steps:
1. Run codegen on CATF fixture
2. Find the `engineeringqfactor` impl file
3. Assert `AUTO_IMPLEMENTED = True` (it should be FULLY_COMPILABLE)
4. Extract function body
5. Execute with test inputs via `_execute_impl_body()`
6. Assert all 3 outputs match within 1e-10

This tests that the topological sort correctly orders `q_eng → f_recirculating → p_net` and that intermediate output references compile to bare variable names (not `inputs.q_eng`).

**`test_pattern_b_magnet_cryogenic_load(self, catf_mfe_output)`**

Pattern B ground truth -- 4 undeclared intermediates:

```python
# Hand-computed from SysML expressions:
# nuclear_heating = 0.05 * p_neutron * (magnet_surface_area / first_wall_area)
#                 = 0.05 * 2000.0 * (500.0 / 800.0) = 62.5
# ac_losses = 0.0
# heat_leak = magnet_volume * 0.05 = 100.0 * 0.05 = 5.0
# thermal_load_cryo = nuclear_heating + ac_losses + heat_leak = 62.5 + 0.0 + 5.0 = 67.5
# cooling_power = (thermal_load_cryo / operating_temp) * (300.0 / carnot_efficiency)
#               = (67.5 / 20.0) * (300.0 / 0.3) = 3.375 * 1000.0 = 3375.0

inputs = {
    "magnet_volume": 100.0,
    "magnet_surface_area": 500.0,
    "first_wall_area": 800.0,
    "p_neutron": 2000.0,
    "b_field": 12.0,
    "operating_temp": 20.0,
    "carnot_efficiency": 0.3,
}
expected = {"cooling_power": 3375.0}
```

Steps: same as EngineeringQFactor. This tests that:
1. Undeclared intermediates (`nuclear_heating`, `ac_losses`, `heat_leak`, `thermal_load_cryo`) are discovered, compiled, and emitted as local variables
2. The topological sort places them before `cooling_power`
3. Only `cooling_power` appears in the return statement (undeclared intermediates excluded)

**`test_backlog_lists_only_non_compilable(self, catf_mfe_output)`**
- Read `IMPLEMENTATION_BACKLOG.md`
- Assert it lists exactly PlasmaConfinement and TritiumBreedingRatio (the 2 PARTIALLY_COMPILABLE CalcDefs)
- Assert `"2 functions to implement"` in content
- Assert it does NOT list any FULLY_COMPILABLE CalcDef names (spot-check: assert "EngineeringQFactor" not in content, "MagnetCryogenicLoad" not in content)

### Component 5: Validation Report

**File:** `.project/active/expr-e2e-validation/report.md` (generated after tests run)

This is a manual artifact, not auto-generated. Created after running the test suite by recording:
- Per-CalcDef results table for solar_battery (15 rows)
- Per-CalcDef results table for CATF MFE (21 rows)
- Pattern coverage summary
- Pass/fail status for each acceptance criterion

---

## Potential Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| CATF fixture SysIDE import resolution failure | High -- tests can't run | Copy ALL library + design files, not a minimal subset. Validate fixture works before writing tests. |
| Solar_battery handwritten impl path doesn't exist on CI/other machines | Medium -- ground truth tests fail | Use `pytest.mark.skipif` to skip ground truth tests when path absent. Non-ground-truth tests (count, backlog, syntax) still run. |
| CATF model produces different CalcDef count than expected (21) | Medium -- assertion fails | Pinned to exact counts from Item 2 spike (19 FULLY_COMPILABLE, 2 PARTIALLY_COMPILABLE). If codegen discovers additional/fewer CalcDefs, investigate root cause rather than loosening assertions. |
| FR-11 (self-contained fixture) cannot be fully validated on dev machine where source path still exists | Low -- false confidence | Validate by running codegen on fixture path only (not source path). True validation requires a clean machine or CI. |
| `exec()`-based execution masks import errors in generated code | Low -- false positive | Separate tests validate syntax via `ast.parse()`. The `exec()` tests specifically target numerical correctness, not importability. |
| Pattern B hand-computed values have arithmetic errors | Medium -- false failure | Show full derivation chain in test comments. Use simple integer-friendly inputs (avoid floating-point surprises). Keep derivation independently verifiable. |

---

## Integration Strategy

### How This Fits Into Existing Tests

The new test file (`test_expression_compilation_e2e.py`) sits alongside the existing `test_full_pipeline.py` in `tests/integration/`. It follows the same patterns:
- Uses `GenerationConfig` + `run_codegen()`
- Uses `tmp_path` fixture for output isolation
- Uses `conftest.py` fixtures for model paths
- Tests are independent (each runs its own codegen invocation)

### What It Complements

- **Unit tests** (`test_stencils.py`, `test_expression_compiler.py`) validate individual components in isolation
- **Existing integration tests** (`test_full_pipeline.py`) validate pipeline structure (directories, file existence, registries)
- **New E2E tests** validate pipeline *correctness* -- that generated code computes the right values

### Execution Cost

Each model's codegen invokes SysIDE model loading (~5-10s per model). The class-scoped fixture strategy (described in Component 4, Section 4.2/4.3) amortizes this cost: one codegen run per test class, not per test method. TestChainSpikeAutoImpl uses function-scope since it's lightweight (3 CalcDefs).

---

## Validation Approach

### Automated Validation

Run the full test suite:
```bash
uv run pytest tests/ -v
```

The new tests are self-validating -- they assert every acceptance criterion:
- AC-1: `test_auto_implementation_count` asserts >= 10
- AC-2: `test_ground_truth[parametrized x5]` asserts 1e-10 tolerance against handwritten impls
- AC-3: `test_codegen_succeeds` on CATF fixture (implicit via class-scoped fixture)
- AC-4: `test_auto_implementation_classification` (>= 19 auto, == 2 stubs, == 21 total) + `test_partially_compilable_stubs_have_accurate_reasons` (FR-9: CalcDef name + SysML source in stub)
- AC-5: `test_pattern_b_engineering_q_factor`
- AC-6: `test_pattern_b_magnet_cryogenic_load`
- AC-7: `test_backlog_excludes_auto_implemented`
- AC-8: `test_backlog_lists_only_non_compilable` (exactly 2: PlasmaConfinement, TritiumBreedingRatio)
- AC-9: Existing 144 tests still pass
- AC-10: New test file exists and passes

### Manual Validation

After tests pass, create the validation report (AC-11) by running codegen with `--verbose` on both models and recording per-CalcDef compilability classifications.

### Pattern B Ground Truth Verification (AC-12)

The hand-computed values in `test_pattern_b_engineering_q_factor` and `test_pattern_b_magnet_cryogenic_load` are derived from the SysML expressions verbatim. The derivation chain is shown in comments within each test. A reviewer can verify the arithmetic independently by reading the SysML source and the test comments side-by-side.

---

**Next Step:** After approval → `/_my_plan`
