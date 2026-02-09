# Spec: E2E Validation on Real Models (ATTR-EXPR Item 4)

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-09 16:07 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Epic:** `.project/backlog/epic_attribute_expression_capture.md` (Item 4)

---

## Business Goals

### Why This Matters

Items 1-3 of the ATTR-EXPR epic built the computed attribute extraction, classification, compilation, and pipeline integration. The pipeline now generates synthetic modules for FORMULA computed attributes and wires them into the computation graph alongside CalcUsage modules. However, none of this has been validated end-to-end with numerical correctness checks against known expected values on real or realistic models.

This item is the validation gate: it proves the pipeline produces correct, executable outputs before documenting decisions (Item 5) and closing the epic.

### Success Criteria

- [x] Probe fixture FORMULA attributes produce correct numerical values (with tolerances)
- [x] Chain patterns resolve and execute in correct order with correct values
- [x] Solar_battery `p_net_kw` synthetic module generates and wires correctly
- [x] All existing tests pass with zero regressions (285 total, 0 failures)
- [x] Validation report documents per-pattern results

### Priority

P1 -- Blocks Item 5 (ADRs/documentation) and ATTR-EXPR epic closure. Sequential dependency on Item 3 (complete).

---

## Problem Statement

### Current State

- 264+ tests pass covering unit, integration, and Phase 1 E2E scenarios
- Integration tests (`test_computed_attribute_pipeline.py`) validate pipeline structure (module generation, wiring, ordering) but do NOT execute generated code or check numerical outputs
- Phase 1 E2E tests (`test_expression_compilation_e2e.py`) validate CalcDef auto-implementations with ground-truth assertions but do NOT cover computed attribute modules
- No test executes a FORMULA computed attribute's auto-implementation and verifies the numerical result
- No test validates the solar_battery `p_net_kw` computed attribute in the full pipeline context

### Desired Outcome

E2E tests that run the full pipeline on real/realistic SysML models, execute generated FORMULA auto-implementations, and assert numerical correctness against hand-computed ground truth values.

---

## Scope

### In Scope

1. **Probe fixture E2E tests** -- Run full pipeline on `tests/fixtures/attr_expr_probe/`, execute FORMULA auto-implementations, assert numerical correctness with tolerances for 9 attributes
2. **Chain resolution assertions** -- Verify execution order and correct value propagation through multi-hop chains
3. **EXPOSE classification assertions** -- Verify EXPOSE_PURE classified but no module generated; EXPOSE_COMPUTED classified but deferred (no module, no error)
4. **Solar_battery validation** -- Verify `p_net_kw` synthetic module generates, downstream `annualized_om` receives it as MODULE_OUTPUT, full pipeline correct
5. **Phase 1 regression** -- All existing 264+ tests pass with zero regressions
6. **Backlog accuracy** -- `IMPLEMENTATION_BACKLOG.md` lists computed attribute modules as auto-implemented with "0 functions to implement"
7. **Validation report** -- `.project/active/attr-expr-e2e/report.md` documenting per-pattern results (written manually by the executing agent after pipeline runs)

### Out of Scope

- Performance benchmarking
- Phase 3 patterns (hierarchy, multiplicity, aggregation)
- EXPOSE_COMPUTED execution validation (deferred -- documented as known gap)
- New fixture creation (reuse existing `attr_expr_probe/`)
- Production code changes (this is validation only; if bugs are found, they are fixed but tracked separately)

### Edge Cases & Considerations

- `p_alpha` involves division that produces a non-terminating decimal (`2600.0 * 3.52 / 17.58`); use `pytest.approx` with relative tolerance
- Chain ordering: `cost` depends on `area`, `marked_up_cost` depends on `cost`, `cost_density` depends on both `cost` and `volume` -- must verify topological order is respected
- Solar_battery `p_net_kw` is a single computed attribute among 15 CalcDefs -- must not disrupt existing CalcDef auto-implementations or their ground-truth values

---

## Requirements

### Functional Requirements

> Requirements below are from the epic definition unless marked [INFERRED].

1. **FR-1**: Probe fixture FORMULA attributes MUST produce correct numerical values when their auto-implementations are executed with the fixture's literal input values:

   | Attribute | Expression | Expected Value |
   |-----------|-----------|----------------|
   | area | 10.0 * 5.0 | 50.0 |
   | volume | 10.0 * 5.0 * 3.0 | 150.0 |
   | cost | 50.0 * 12.0 | 600.0 |
   | marked_up_cost | 600.0 * 1.15 | 690.0 |
   | cost_density | 600.0 / 150.0 | 4.0 |
   | q_scientific | 2600.0 / 50.0 | 52.0 |
   | perimeter | 2.0 * 10.0 + 2.0 * 5.0 | 30.0 |
   | minor_radius | (4.2 + 4.4) / 2.0 - 3.0 | 1.3 |
   | p_alpha | 2600.0 * 3.52 / 17.58 | ~520.36 |

2. **FR-2**: Chain resolution MUST produce correct values when downstream attributes depend on upstream computed attributes: `cost` depends on `area`, `marked_up_cost` depends on `cost`, `cost_density` depends on `cost` and `volume`.

3. **FR-3**: EXPOSE_PURE attributes MUST be classified correctly with no module generated for them.

4. **FR-4**: EXPOSE_COMPUTED attributes MUST be classified correctly with no module generated and no error raised.

5. **FR-5**: Solar_battery `p_net_kw` MUST generate a synthetic pipeline module (`solar_battery_plant__p_net_kw` or equivalent) with auto-implementation producing `inputs.p_net_mw * 1000.0`.

6. **FR-6**: Solar_battery downstream CalcUsage `annualized_om` binding `in p_net_kw = p_net_kw` MUST resolve as MODULE_OUTPUT from the synthetic computed attribute module, not as an ENTRY_POINT.

7. **FR-7**: All existing tests (264+ baseline) MUST pass with zero regressions, zero new xfail markers.

8. **FR-8**: `IMPLEMENTATION_BACKLOG.md` MUST list computed attribute modules as auto-implemented with "0 functions to implement"; manual-required count MUST be unchanged from Phase 1.

9. **FR-9**: [INFERRED] Numerical assertions SHOULD use `pytest.approx` with appropriate tolerances to handle floating-point arithmetic.

10. **FR-10**: [INFERRED] E2E tests SHOULD follow the existing pattern in `test_expression_compilation_e2e.py` for consistency (fixture-scoped pipeline execution, parametrized ground-truth assertions).

---

## Acceptance Criteria

### Core Functionality

- [x] New E2E test file `tests/integration/test_computed_attributes_e2e.py` exists and passes
- [x] All 9 probe fixture FORMULA attributes produce correct numerical values (within tolerance)
- [x] Chain patterns execute in correct topological order and produce correct values
- [x] EXPOSE_PURE and EXPOSE_COMPUTED classifications verified (no modules, no errors)
- [x] Solar_battery `p_net_kw` synthetic module generates with correct auto-implementation
- [x] Solar_battery downstream wiring resolves `p_net_kw` as MODULE_OUTPUT from computed attribute module

### Quality & Integration

- [x] All existing tests pass (285 total, 0 xfail, 0 failures)
- [x] Phase 1 CalcDef auto-implementations unchanged (solar_battery 16 impls, CATF 21 impls, regression guards pass)
- [x] `IMPLEMENTATION_BACKLOG.md` accurate for computed attribute modules
- [x] Validation report (`.project/active/attr-expr-e2e/report.md`) documents per-pattern results with pass/fail and numerical accuracy

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_attribute_expression_capture.md` (Item 4)
- **Predecessor specs:** `.project/active/attr-expr-extraction/spec.md` (Item 2), `.project/active/attr-expr-pipeline/spec.md` (Item 3)
- **Probe fixture:** `tests/fixtures/attr_expr_probe/design.sysml`, `tests/fixtures/attr_expr_probe/library.sysml`
- **Solar_battery fixture:** `tests/fixtures/solar_battery_model/`
- **Existing E2E tests:** `tests/integration/test_expression_compilation_e2e.py`
- **Existing integration tests:** `tests/integration/test_computed_attribute_pipeline.py`
- **Design:** `.project/active/attr-expr-e2e/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
