# Implementation Plan: E2E Validation on Real Models (ATTR-EXPR Item 4)

**Status:** Complete
**Created:** 2026-02-09
**Last Updated:** 2026-02-09

## Source Documents
- **Spec:** `.project/active/attr-expr-e2e/spec.md`
- **Design:** `.project/active/attr-expr-e2e/design.md` ← See here for component details, ground truth table, helper patterns, YAML inspection approach

## Implementation Strategy

**Phasing Rationale:**
Single new test file built in 3 phases, ordered by risk. Phase 1 runs codegen on the probe fixture first -- this is the riskiest step because it's the first time the full pipeline processes a model with FORMULA + EXPOSE_PURE + EXPOSE_COMPUTED + CalcUsage patterns together. If something breaks, we find out immediately. Phase 2 validates the real-world solar_battery model (lighter, since the pattern is proven). Phase 3 adds regression guards and produces the validation report.

**Overall Validation Approach:**
- Each phase adds tests to `tests/integration/test_computed_attributes_e2e.py`
- After each phase: `uv run pytest tests/integration/test_computed_attributes_e2e.py -v`
- After Phase 3: `uv run pytest tests/` for full regression check

---

## Phase 1: Probe Fixture E2E Validation

### Goal
Run the full codegen pipeline on `tests/fixtures/attr_expr_probe/`, execute each FORMULA auto-implementation, and verify numerical correctness for all 9 ground-truth attributes. Also validate EXPOSE classification and backlog accuracy. This is the riskiest phase -- first real E2E execution of computed attribute codegen.

### Test Stencil (Write This First)
```python
class TestProbeComputedAttrsE2E:
    @pytest.fixture(scope="class")
    def probe_output(self, tmp_path_factory):
        output = tmp_path_factory.mktemp("probe")
        config = GenerationConfig(
            models_path=FIXTURES_DIR / "attr_expr_probe",
            output_path=output, package_name="attr_expr_probe",
        )
        success = run_codegen(config)
        assert success
        return output

    @pytest.mark.parametrize("attr_name,inputs,output_name,expected", PROBE_GROUND_TRUTH)
    def test_ground_truth(self, probe_output, attr_name, inputs, output_name, expected):
        impl = _find_computed_attr_impl(probe_output, attr_name)
        body = extract_function_body(impl)
        assert body is not None
        result = execute_impl_body(body, inputs, [output_name])
        assert_outputs_match(result, {output_name: expected})
```

### Changes Required

**See `design.md` for:**
- Ground truth data table → `design.md#probe-fixture-ground-truth-values`
- Impl lookup helper → `design.md#impl-lookup-helper`
- Test architecture → `design.md#component-1-probe-fixture-e2e`

**Specific file changes:**

#### 1. Test File
**File:** `tests/integration/test_computed_attributes_e2e.py` (NEW)
- [x] Create file with imports, constants (`FIXTURES_DIR`), `_find_computed_attr_impl` helper
- [x] Define `PROBE_GROUND_TRUTH` list with all 9 entries (see `design.md` ground truth table)
- [x] Implement `TestProbeComputedAttrsE2E` class with class-scoped `probe_output` fixture
- [x] `test_codegen_succeeds` -- assert True + handwritten dir exists
- [x] `test_formula_modules_auto_implemented` -- count >= 9 auto-implemented FORMULA impls
- [x] `test_ground_truth` (parametrized x9) -- execute each impl, assert numerical match
- [x] `test_expose_pure_no_module` -- no impl for `scale_result`, `half_vol`, `quarter_vol`
- [x] `test_expose_computed_no_module_no_error` -- no impl for `scaled_area`
- [x] `test_backlog_accuracy` -- "0 functions to implement" in backlog

### Validation

**Automated:**
- [x] `uv run pytest tests/integration/test_computed_attributes_e2e.py::TestProbeComputedAttrsE2E -v` → All 14 pass
- [x] `uv run pytest tests/` → 285 passed, 0 failures

**Manual:**
- [x] Inspect one generated impl file (e.g., `area_impl.py`) in the tmp output to verify it looks correct

**What We Know Works After This Phase:**
- Full pipeline processes FORMULA + EXPOSE + CalcUsage models without error
- All 9 FORMULA computed attributes produce numerically correct values
- EXPOSE_PURE and EXPOSE_COMPUTED don't produce spurious modules
- Backlog correctly reports 0 functions to implement
- Chain resolution works (cost→area, marked_up_cost→cost, cost_density→cost+volume proven by correct intermediate values)

---

## Phase 2: Solar Battery Computed Attribute Validation

### Goal
Validate that `p_net_kw = p_net_mw * 1000.0` generates a correct synthetic module in the real solar_battery model, and that downstream `annualized_om` receives it via MODULE_OUTPUT wiring (not ENTRY_POINT).

### Test Stencil (Write This First)
```python
class TestSolarBatteryComputedAttrE2E:
    @pytest.fixture(scope="class")
    def solar_battery_output(self, tmp_path_factory):
        output = tmp_path_factory.mktemp("solar_battery")
        config = GenerationConfig(
            models_path=FIXTURES_DIR / "solar_battery_model",
            output_path=output, package_name="solar_battery",
        )
        success = run_codegen(config)
        assert success
        return output

    def test_p_net_kw_ground_truth(self, solar_battery_output):
        impl = _find_computed_attr_impl(solar_battery_output, "p_net_kw")
        body = extract_function_body(impl)
        result = execute_impl_body(body, {"p_net_mw": 0.008}, ["p_net_kw"])
        assert_outputs_match(result, {"p_net_kw": 8.0})
```

### Changes Required

**See `design.md` for:**
- Solar battery analysis → `design.md#solar-battery-p_net_kw`
- YAML inspection approach → `design.md#pipeline-yaml-inspection`
- Test list → `design.md#component-2-solar-battery-computed-attr-e2e`

**Specific file changes:**

#### 1. Test File (append to existing)
**File:** `tests/integration/test_computed_attributes_e2e.py` (MODIFY)
- [x] Add `TestSolarBatteryComputedAttrE2E` class with class-scoped fixture
- [x] `test_p_net_kw_module_generated` -- find impl, assert auto-implemented
- [x] `test_p_net_kw_ground_truth` -- execute with `p_net_mw=0.008`, assert result `8.0`
- [x] `test_p_net_kw_wiring_in_pipeline_yaml` -- parse YAML, verify `annualized_om` p_net_kw input sourced from computed attr module (not entry point)
- [x] `test_impl_count_includes_computed_attr` -- assert 16 total impls
- [x] `test_annualized_om_uses_computed_p_net_kw` -- execute annualizedomcalc with `p_net_kw=8.0`, assert `annual_om_cost=160.0`

### Validation

**Automated:**
- [x] `uv run pytest tests/integration/test_computed_attributes_e2e.py::TestSolarBatteryComputedAttrE2E -v` → All 5 pass
- [ ] `uv run pytest tests/` → No regressions

**Manual:**
- [x] Inspect generated pipeline YAML to visually confirm `p_net_kw` wiring

**What We Know Works After This Phase:**
- Real-world model with computed attribute generates correctly
- `p_net_kw` synthetic module produces `8.0` from `p_net_mw=0.008`
- Downstream CalcUsage wiring correct (MODULE_OUTPUT, not ENTRY_POINT)
- Computed attribute doesn't disrupt existing CalcDef generation (16 impls total)

---

## Phase 3: Regression Guard + Full Suite + Report

### Goal
Add lightweight regression tests for chain_spike and CATF models (confirm no false-positive computed attribute extraction), run the full test suite, and write the validation report.

### Test Stencil (Write This First)
```python
class TestPhase1Regression:
    def test_chain_spike_still_works(self, chain_spike_model_path, tmp_path):
        config = GenerationConfig(
            models_path=chain_spike_model_path,
            output_path=tmp_path / "output", package_name="chain_spike",
        )
        assert run_codegen(config)
        impls = find_impl_files(tmp_path / "output")
        assert len(impls) == 3
        assert all(is_auto_implemented(p) for p in impls)
```

### Changes Required

**See `design.md` for:**
- Regression guard rationale → `design.md#component-3-phase-1-regression-guard`

**Specific file changes:**

#### 1. Test File (append to existing)
**File:** `tests/integration/test_computed_attributes_e2e.py` (MODIFY)
- [x] Add `TestPhase1Regression` class
- [x] `test_chain_spike_still_works` -- codegen succeeds, 3 impls, all auto-implemented
- [x] `test_catf_mfe_still_works` -- codegen succeeds, 21 impls (no false-positive computed attrs)

#### 2. Full Suite Run
- [x] `uv run pytest tests/` → 285 passed, 0 failures, 0 xfail

#### 3. Validation Report
**File:** `.project/active/attr-expr-e2e/report.md` (NEW -- manual)
- [x] Write per-pattern results table with pass/fail and numerical accuracy
- [x] Document any issues found and how they were resolved
- [x] Include test counts and regression summary

### Validation

**Automated:**
- [x] `uv run pytest tests/integration/test_computed_attributes_e2e.py -v` → All 21 tests pass
- [ ] `uv run pytest tests/` → Full suite passes, no regressions

**What We Know Works After This Phase:**
- All computed attribute E2E tests pass
- Phase 1 models unaffected (chain_spike 3 impls, CATF 21 impls)
- No false-positive computed attribute extraction
- Full 264+ test suite green
- Validation report documents all results -- Item 4 complete

---

## Environment Setup

**See CLAUDE.md for full environment rules**

Key commands:
```bash
uv run pytest tests/integration/test_computed_attributes_e2e.py -v  # New tests
uv run pytest tests/                                                 # Full suite
uv run mypy src/                                                     # Type check (no src changes expected)
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: If probe codegen fails, inspect logs for EXPOSE_COMPUTED handling. This is the most likely failure point. Fix production code if needed (tracked separately per spec out-of-scope note).
- **Phase 2**: If `p_net_kw` not extracted, check Step 4.5 logging. Solar_battery is a well-tested model -- failure here means regression in Items 1-3.
- **Phase 3**: CATF impl count assertion (==21) catches false-positive computed attribute extraction. If count differs, investigate which attributes were falsely classified as FORMULA.

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Created `tests/integration/test_computed_attributes_e2e.py` with `TestProbeComputedAttrsE2E` (14 tests)
- `_find_computed_attr_impl` helper with exact-name matching
- `PROBE_GROUND_TRUTH` with all 9 entries, parametrized test IDs
- EXPOSE_PURE/EXPOSE_COMPUTED/backlog tests
**Issues:** None
**Deviations:** None

### Phase 2 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Added `TestSolarBatteryComputedAttrE2E` (5 tests) to same file
- YAML wiring test parses pipeline.yaml and verifies MODULE_OUTPUT sourcing
- `annualized_om` chain test validates end-to-end: p_net_mw=0.008 -> p_net_kw=8.0 -> annual_om_cost=160.0
**Issues:** YAML module keys use full qualified names with `__` separators, not CalcDef names. Initial test searched for `annualizedomcalc` but needed `annualized_om` substring match.
**Deviations:** None

### Phase 3 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Added `TestPhase1Regression` (2 tests): chain_spike (3 impls), catf_mfe (21 impls)
- Full suite: 285 passed, 0 failures, 0 xfail
- Validation report: `.project/active/attr-expr-e2e/report.md`
**Issues:** None
**Deviations:** None

---

**Status**: Complete
