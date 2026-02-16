# Spec: E2E Validation & Documentation -- Costed Component Pattern

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-10 22:20 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Epic:** COST-PATTERN (Item 5)

---

## Business Goals

### Why This Matters

Items 1-4 built the complete extraction, analysis, resolution, and generation layers for the Costed Component pattern. There are 69 unit tests on synthetic data proving each algorithm works in isolation. But nothing has been validated end-to-end on a real SysML model. Virtual CalcUsage QN strings were hardcoded in tests; redefinition data was mocked; aggregation channel resolution used synthetic catalogs. The solar_battery model -- the reference implementation for this pattern -- has never been run through the updated pipeline.

Without this item, we ship code that passes all unit tests but has zero proof it produces a working pipeline from real SysML input. The Item 4 implementation audit identified 10 specific integration scenarios that can only be validated with real models. This item closes those gaps and formalizes the architectural decisions in ADRs.

### Success Criteria

- [ ] Solar_battery model: codegen succeeds and produces all expected modules
- [ ] Solar_battery model: all 9 leaf-part cost modules generate with auto-implementations
- [ ] Solar_battery model: allocation CalcUsages generate (e.g., `solar_array__allocation_model`)
- [ ] Solar_battery model: all 4 assembly aggregation modules generate with auto-implementations
- [ ] Solar_battery model: 5 system-level CalcUsages wire correctly to hierarchy outputs
- [ ] Solar_battery model: auto-implementations are valid Python and produce numerically correct results
- [ ] Solar_battery model: `IMPLEMENTATION_BACKLOG.md` shows "0 functions to implement"
- [ ] Solar_battery model: pipeline YAML shows correct topological ordering (leaf -> aggregation -> system)
- [ ] chain_spike regression: 3 CalcDefs still auto-implemented, backlog still empty
- [ ] CATF MFE regression: 19 auto-impls, 2 stubs still correct
- [ ] All existing tests pass with zero regressions (450 baseline after Item 4)
- [ ] ADR-006 drafted (Part Hierarchy and Template Instantiation)
- [ ] ADR-007 drafted (Parametric Multiplicity and Aggregation)
- [ ] ADR-002 amendment drafted (relaxed Approach E Rules 1, 3, 4)

### Priority

P1. This is the final item in the COST-PATTERN epic. All upstream dependencies (Items 1-4) are complete. Closing this item enables the team to use the Costed Component pattern on real models.

---

## Problem Statement

### Current State

- Items 1-4 are complete with 450 passing tests (381 baseline + 69 new)
- All tests use synthetic/mocked data models -- no real SysML model has been run through the hierarchy-aware pipeline
- The Item 4 audit identified 10 integration scenarios that are only testable with real models:
  1. QN format compatibility (SysIDE adapter may produce unexpected formats)
  2. Template detection accuracy (`is_template=True/False` correctness)
  3. Redefinition extraction (`:>>` patterns in real models)
  4. Multi-level hierarchy depth (solar_battery has 4+ levels)
  5. Multiplicity count extraction (real model multiplicity expressions)
  6. CHAIN redefinition tracing (multi-hop chains in practice)
  7. Full module count verification (18+ modules expected)
  8. Auto-implementation compilability (generated Python actually runs)
  9. Entry point classification in parameter schemas (correct types/defaults)
  10. Pipeline YAML topological ordering (full end-to-end ordering)
- No ADRs document the template instantiation or parametric multiplicity decisions
- ADR-002 still mandates Approach E rules that are now optional

### Desired Outcome

The solar_battery model produces a complete, executable LCOE pipeline through codegen. All integration gaps are validated. Architectural decisions are documented in ADRs. The epic is closed.

---

## Scope

### In Scope

1. **E2E integration test file** (`tests/integration/test_costed_component_e2e.py` -- NEW):
   - Run `run_codegen()` on `tests/fixtures/solar_battery_model/`
   - Validate module counts, auto-implementation counts, and file generation
   - Execute auto-implementations with known inputs and verify numerical correctness
   - Validate pipeline YAML structure and topological ordering
   - Validate `IMPLEMENTATION_BACKLOG.md` content
   - Validate entry point schemas (parameter group YAML)
   - Cover all 10 audit-identified integration gaps

2. **Regression guards** (in same file or existing files):
   - chain_spike model: 3 CalcDefs still auto-implemented, backlog still empty
   - Existing solar_battery tests: 15+1 system-level auto-impls still correct
   - CATF MFE: 19 auto-impls, 2 stubs still correct

3. **Numerical ground truth validation**:
   - Derive expected values for leaf-part cost modules from SysML model literals
   - Derive expected values for aggregation modules from SysML model expressions
   - Execute auto-implementations and compare against hand-computed ground truth
   - Follow existing pattern from `test_expression_compilation_e2e.py` (parametrized tests with `execute_impl_body()`)

4. **ADR-006: Part Hierarchy and Template Instantiation**:
   - Template detection strategy (`owning_type` check)
   - Virtual CalcUsage generation (per-PartUsage instantiation)
   - Hierarchy-aware naming (ADR-003 extension for deep paths)
   - `part redefines` handling (design-level override resolution)
   - References spike findings (Item 1) for empirical grounding

5. **ADR-007: Parametric Multiplicity and Aggregation**:
   - Parametric multiply strategy for uniform arrays
   - `sum()` transformation to `count * single_instance_output`
   - Synthetic aggregation module generation
   - Uniform-array assumption and when flat expansion would be needed
   - `AggregationExpressionData` model and pipeline integration points

6. **ADR-002 Amendment**:
   - Rule 1 ("multiplicity is a parameter") -> optional for uniform arrays
   - Rule 3 ("aggregation is an explicit CalcDef") -> optional for `:>>` aggregation expressions
   - Rule 4 ("context is a parameter") -> optional for `:>>` redefinition patterns
   - Documents conditions: all array instances must be uniform; non-uniform arrays still require Approach E

7. **Epic closure**:
   - Update epic status to Complete
   - Fill in Lessons Learned section
   - Update Item 4 and Item 5 statuses

### Out of Scope

- TEAx runtime validation (executing the full TEAx pipeline at runtime)
- Non-uniform array support
- New SysML model creation
- Changes to production code (this is testing + documentation only; if bugs are found during E2E validation, they are fixed as part of this item but tracked as deviations)
- Performance benchmarking
- New Jinja2 templates

### Edge Cases & Considerations

- **Existing test count regression**: The existing `TestSolarBatteryValidation.test_auto_implementation_count` expects 16 impl files (15 CalcDef + 1 computed attr). With hierarchy modules added, this count MUST be updated. The assertion change SHOULD be in the existing test file, not duplicated in the new file.
- **Ground truth derivation**: Aggregation module ground truth values depend on the SysML model's literal values for multiplicity counts, `:>>` overrides, and CalcDef defaults. These MUST be hand-computed from the fixture files during design, not reverse-engineered from codegen output.
- **Partial compilation**: If any aggregation expression in the solar_battery model has `has_unsupported_nodes=True`, the zero-backlog criterion still applies -- the solar_battery model specifically SHOULD have all expressions compilable. If not, this is a bug in Items 2-3 that must be fixed.
- **Test execution time**: Full codegen on solar_battery takes ~2-5 seconds. The new test file SHOULD use `scope="class"` fixtures to run codegen once per test class (following the existing pattern in `test_expression_compilation_e2e.py`).
- **Existing ground truth tests**: The 5 existing `SOLAR_BATTERY_GROUND_TRUTH` entries (energy_production, annualized_om, annualized_fuel, annualized_financial, lcoe) are guarded by `@pytest.mark.skipif` on the handwritten impl directory. New hierarchy module ground truth tests SHOULD NOT depend on external handwritten impls -- they SHOULD use hand-computed expected values directly.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic's Item 5 description unless marked [INFERRED] or [FROM AUDIT].

1. **FR-1**: E2E integration tests MUST run `run_codegen()` on the solar_battery model and verify codegen succeeds.

2. **FR-2**: Tests MUST verify that all 9 leaf-part cost modules generate as auto-implemented `_impl.py` files. Expected modules: `pv_module__cost_model`, `inverter__cost_model` (solar_array), `array_bos__cost_model`, `battery_pack__cost_model`, `hybrid_inverter__cost_model`, `battery_bos__cost_model`, `racking__cost_model`, `electrical_panel__cost_model`, `permitting__cost_model` (names are approximate -- exact names derived during design from SysML model QNs).

3. **FR-3**: Tests MUST verify that allocation CalcUsages generate (e.g., `solar_array__allocation_model`).

4. **FR-4**: Tests MUST verify that all 4 assembly aggregation modules generate as auto-implemented `_impl.py` files: `solar_array__capital_cost`, `battery_system__capital_cost`, `site_infra__capital_cost`, `solar_battery_plant__capital_cost`.

5. **FR-5**: Tests MUST verify that 5 system-level CalcUsages wire correctly to hierarchy outputs (e.g., `annualized_financial.total_capex` wires to `solar_battery_plant__capital_cost` output).

6. **FR-6**: Tests MUST execute auto-implementations for leaf-part cost modules with known inputs and verify numerically correct outputs against hand-computed ground truth.

7. **FR-7**: Tests MUST execute auto-implementations for aggregation modules with known inputs and verify numerically correct outputs against hand-computed ground truth.

8. **FR-8**: Tests MUST verify `IMPLEMENTATION_BACKLOG.md` shows "0 functions to implement" for the solar_battery model.

9. **FR-9**: Tests MUST verify pipeline YAML shows correct topological ordering: leaf cost calcs -> aggregation -> system-level calcs.

10. **FR-10**: [FROM AUDIT] Tests MUST verify that generated auto-implementation files are valid Python (parseable by `ast.parse()`).

11. **FR-11**: [FROM AUDIT] Tests MUST verify the total impl file count matches the expected sum of leaf + allocation + aggregation + system-level + computed attr modules.

12. **FR-12**: [FROM AUDIT] Tests MUST verify that aggregation modules have `# source: aggregation` comments in pipeline YAML.

13. **FR-13**: [FROM AUDIT] Tests MUST verify that multiplicity count entry points appear in parameter group schemas with `int` type.

14. **FR-14**: [INFERRED] The existing `TestSolarBatteryValidation.test_auto_implementation_count` MUST be updated to expect the new total impl count (was 16, will increase).

15. **FR-15**: Regression tests MUST verify chain_spike (3 CalcDefs auto-implemented, backlog empty) and CATF MFE (19 auto/2 stub) are unchanged.

16. **FR-16**: ADR-006 MUST document: template detection strategy, virtual CalcUsage generation, hierarchy-aware naming, `part redefines` handling, with references to spike findings.

17. **FR-17**: ADR-007 MUST document: parametric multiply strategy, `sum()` transformation, synthetic aggregation module generation, uniform-array assumption, `AggregationExpressionData` model.

18. **FR-18**: ADR-002 amendment MUST document relaxed Rules 1, 3, 4 with conditions under which Approach E is still required (non-uniform arrays).

---

## Acceptance Criteria

### Core Functionality
- [ ] `test_costed_component_e2e.py` exists with tests covering FR-1 through FR-13
- [ ] All new tests pass on first run (no flaky tests)
- [ ] Solar_battery codegen produces correct module count (to be determined during design)
- [ ] All auto-implementations are valid Python (`ast.parse()` succeeds)
- [ ] Numerical ground truth validated for leaf-part cost modules
- [ ] Numerical ground truth validated for aggregation modules
- [ ] Pipeline YAML has correct ordering and `# source: aggregation` comments
- [ ] `IMPLEMENTATION_BACKLOG.md` shows "0 functions to implement"
- [ ] Entry point schemas include multiplicity counts with `int` type

### Regression
- [ ] Existing `TestSolarBatteryValidation` updated with correct expected count
- [ ] chain_spike regression: 3 auto-impls, empty backlog
- [ ] CATF MFE regression: 19 auto/2 stub
- [ ] All 450+ existing tests pass with zero regressions

### Documentation
- [ ] ADR-006 follows existing ADR format (Status, Context, Decision, Consequences)
- [ ] ADR-007 follows existing ADR format
- [ ] ADR-002 amended with new section for relaxed rules
- [ ] All ADRs reference relevant spike findings and implementation commits

### Quality & Integration
- [ ] `uv run mypy src/` passes (only pre-existing issues)
- [ ] `uv run ruff check src/` passes (only pre-existing issues)
- [ ] Test execution time < 30 seconds for the new test file
- [ ] No production code changes (unless bugs discovered during validation)

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_costed_component_pattern.md`
- **Item 4 Spec:** `.project/active/hierarchy-pipeline/spec.md`
- **Item 4 Design:** `.project/active/hierarchy-pipeline/design.md`
- **Item 4 Plan:** `.project/active/hierarchy-pipeline/plan.md`
- **Spike Report:** `.project/active/hierarchy-spike/report.md`
- **Existing E2E Tests:** `tests/integration/test_expression_compilation_e2e.py`
- **Existing Computed Attr E2E:** `tests/integration/test_computed_attributes_e2e.py`
- **Test Helpers:** `tests/helpers/impl_execution.py`
- **Solar Battery Fixture:** `tests/fixtures/solar_battery_model/`
- **Existing ADRs:** `docs/architecture/ADR-001` through `ADR-005`
- **Design:** `.project/active/hierarchy-e2e/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
