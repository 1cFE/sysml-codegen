# Implementation Plan: Aggregation Wiring Bugfix (Bug A + Bug B)

**Status:** Complete
**Created:** 2026-02-16
**Last Updated:** 2026-02-16

## Source Documents
- **Spec:** `.project/active/aggregation-wiring-bugfix/spec.md`
- **Design:** `.project/active/aggregation-wiring-bugfix/design.md` — See here for component details, spike evidence, resolution approach, and risk analysis

## Implementation Strategy

**Phasing Rationale:**
Phase 1 tackles Bug A (3 FCE/OE reorder sites) first because it's the highest-impact fix (37 of 45 broken inputs) and purely mechanical block moves. Integration tests must use the real solar_battery fixture since mocks can't reproduce the SysIDE FCE/OE subtype relationship. Phase 2 adds Bug B (LocalTerm sibling resolution) independently — unit-testable with existing helpers. Phase 3 is full-suite validation.

**Overall Validation Approach:**
- Each phase starts with tests
- Integration tests for Bug A (real fixture required), unit tests for Bug B (resolution logic)
- Full pytest suite after each phase to catch regressions

---

## Phase 1: Bug A — FCE/OE Check Reordering + Integration Tests

### Goal
Fix the root cause affecting 37 aggregation inputs plus 2 latent FCE mishandling bugs. This is first because it's the highest-impact fix and de-risks the core type-dispatch issue.

### Test Stencil (Write This First)
```python
# tests/integration/test_hierarchy_e2e.py — new class at end
class TestAggregationFCEOrdering:
    @pytest.fixture(scope="class")
    def pipeline_context(self) -> PipelineContext:
        model_path = FIXTURES_DIR / "solar_battery_model"
        return build_pipeline_context([model_path])

    def test_fce_nodes_classified_as_singleton_terms(self, pipeline_context):
        """Bug A1: FCE→SingletonTerm, not LocalTerm. Spike B counts."""
        hierarchy = pipeline_context.hierarchy_data
        total_sum = sum(len(a.sum_terms) for a in hierarchy.aggregation_expressions)
        total_singleton = sum(len(a.singleton_terms) for a in hierarchy.aggregation_expressions)
        total_local = sum(len(a.local_terms) for a in hierarchy.aggregation_expressions)
        assert total_sum == 12
        assert total_singleton == 37
        assert total_local == 9
```

### Changes Required

**See `design.md` for:**
- Full before/after code blocks → `design.md#change-1-a1`
- Spike evidence → `design.md#research-findings`
- Why sum() is unaffected → `design.md#bug-a-site-_walk_aggregation_ast-check-ordering`

**Specific file changes:**

#### 1. Test File
**File:** `tests/integration/test_hierarchy_e2e.py` (MODIFY — write first)
- [ ] Add `TestAggregationFCEOrdering` class with `scope="class"` fixture
- [ ] Test A-1: `test_fce_nodes_classified_as_singleton_terms` — assert {sum:12, singleton:37, local:9}
- [ ] Test A-2: `test_singleton_terms_have_dotted_source_paths` — all SingletonTerms have `"."` in source_path
- [ ] Test A-3: `test_no_unsupported_dot_operator_in_expressions` — no `"unsupported operator: ."` in CalcDef outputs
- [ ] Test A-4: `test_no_mangled_dot_parenthesized_expressions` — no `".(name)"` patterns in transformed_expression

#### 2. A1: hierarchy_resolver.py
**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py:327-355`
- [ ] Move FCE block (lines 350-355) before OE block (line 328), add subtype comment
- [ ] See `design.md#change-1-a1` for exact before/after

#### 3. A2: expression_compiler.py
**File:** `src/sysml_codegen/extraction/expression_compiler.py:312-399`
- [ ] Move FCE block (lines 394-399) before OE block (line 313), add subtype comment
- [ ] See `design.md#change-2-a2` for exact before/after

#### 4. A3: expression_utils.py
**File:** `src/sysml_codegen/extraction/expression_utils.py:44-51`
- [ ] Move FCE block (lines 50-51) before OE block (line 44), add subtype comment
- [ ] See `design.md#change-3-a3` for exact before/after

### Validation (How to Verify This Phase)

**Automated:**
- [ ] `uv run pytest tests/integration/test_hierarchy_e2e.py::TestAggregationFCEOrdering -v` → 4 tests pass
- [ ] `uv run pytest tests/` → full suite passes (647+ tests, 0 regressions)

**Manual:**
- [ ] Verify SumTerm count unchanged at 12 (from test output)
- [ ] Verify SingletonTerm count jumps from 0 to 37

**What We Know Works After This Phase:**
- FCE nodes correctly dispatched before OE in all 3 extraction sites
- 37 aggregation inputs reclassified from LocalTerm to SingletonTerm
- No regression in sum() handling or existing extraction
- FCE diagnostic text and expression reconstruction are correct

---

## Phase 2: Bug B — LocalTerm Sibling Agg Resolution + Unit Tests

### Goal
Wire 8 remaining idiot_index inputs (`capital_cost`, `raw_material_cost` on 4 assemblies) to sibling aggregation module outputs instead of creating entry points.

### Test Stencil (Write This First)
```python
# tests/unit/test_graph_builder_aggregation.py — new tests at end
def test_local_term_resolves_to_sibling_agg_output(self):
    """LocalTerm resolves to sibling agg module output via canonical_channels."""
    sibling_channel = get_channel_name(
        "Design__plant__solar_array__capital_cost", "capital_cost"
    )
    agg = _make_scoped_agg(
        local_terms=[LocalTerm("capital_cost")],
        attribute_name="idiot_index",
        instance_path="Design__plant__solar_array",
        sum_terms=[],
    )
    registry = self._make_registry({sibling_channel: []})
    entry_points: dict[str, EntryPoint] = {}
    module = _build_aggregation_module(agg, [], registry, entry_points, None)
    cost_inputs = [i for i in module.inputs if i.param_name == "capital_cost"]
    assert cost_inputs[0].source.source_type == "module_output"
    assert cost_inputs[0].source.producer_channel == sibling_channel
```

### Changes Required

**See `design.md` for:**
- Full before/after code → `design.md#change-4-b`
- Design decisions (direct canonical_channels check, no Key_D) → `design.md#change-4-b`
- Spike C evidence → `design.md#bug-b-site-localterm-processing`

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_graph_builder_aggregation.py` (MODIFY — write first)
- [ ] Test B-4: `test_local_term_resolves_to_sibling_agg_output` — capital_cost → MODULE_OUTPUT
- [ ] Test B-5: `test_unresolvable_local_term_still_entry_point` — misc_hardware_cost → ENTRY_POINT (regression guard, extends existing test_local_term_creates_entry_point)
- [ ] Test B-6: `test_mixed_local_terms_partial_resolution` — capital_cost + raw_material_cost resolve, misc_hardware_cost doesn't

#### 2. graph_builder.py LocalTerm block
**File:** `src/sysml_codegen/resolution/graph_builder.py:1015-1036`
- [ ] Add sibling agg resolution before entry point creation per `design.md#change-4-b`
- [ ] Uses `canonical_channels` (already in scope from line 955)
- [ ] Constructs `sibling_channel` via `get_channel_name(f"{agg.instance_path}__{l_term.attribute_name}", l_term.attribute_name)`
- [ ] Falls back to entry point if not in `canonical_channels`

### Validation (How to Verify This Phase)

**Automated:**
- [ ] `uv run pytest tests/unit/test_graph_builder_aggregation.py -v` → all tests pass (existing + 3 new)
- [ ] `uv run pytest tests/` → full suite passes

**Manual:**
- [ ] Verify `misc_hardware_cost` still creates entry point (from test output)

**What We Know Works After This Phase:**
- LocalTerms with sibling agg outputs wire to MODULE_OUTPUT
- LocalTerms without siblings still become entry points
- Mixed scenarios (some resolve, some don't) handled correctly

---

## Phase 3: Full Validation + Spike Rerun

### Goal
Confirm zero regressions across the entire test suite and validate final wiring counts with the spike script.

### Changes Required
No code changes. Validation only.

### Validation

**Automated:**
- [ ] `uv run pytest tests/ -v` → all 647+ tests pass
- [ ] `uv run ruff check src/` → no lint errors
- [ ] `uv run mypy src/` → no type errors

**Manual:**
- [ ] `uv run python scripts/spike_agg_wiring_h1_h4.py` → verify wiring counts:
  - 57 of 70 aggregation inputs wired to MODULE_OUTPUT
  - 13 remain as ENTRY_POINTs (12 multiplicity counts + 1 misc_hardware_cost)

**What We Know Works After This Phase:**
- All acceptance criteria from spec met
- No regressions across entire codebase
- Spike script confirms end-to-end wiring counts

---

## Environment Setup

**See CLAUDE.md for full environment rules**

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Run integration tests against real fixture (mocks can't validate FCE/OE subtype). Assert SumTerm count=12 as explicit regression guard.
- **Phase 2**: Existing `test_local_term_creates_entry_point` serves as regression guard for unresolvable LocalTerms. Test B-6 validates mixed resolution.

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-16
**Actual Changes:**
- Moved FCE check before OE in `hierarchy_resolver.py:327-355` (A1)
- Moved FCE check before OE in `expression_compiler.py:312-399` (A2)
- Moved FCE check before OE in `expression_utils.py:44-51` (A3)
- Added `TestAggregationFCEOrdering` class (4 tests) to `tests/integration/test_hierarchy_e2e.py`
- Updated YAML baselines via `scripts/capture_baseline_yaml.py` (entry point ordering changed)
**Issues:** YAML baseline diff test failed as expected — baselines updated to reflect new wiring.
**Deviations:** Test A-3 adapted from design: checks `compilation_results[].unsupported_reason` instead of nonexistent `output.expression_text`.

### Phase 2 Completion
**Completed:** 2026-02-16
**Actual Changes:**
- Added sibling agg resolution block in `graph_builder.py:1015-1036` (Bug B)
- Added 3 tests to `TestBuildAggregationModule` in `tests/unit/test_graph_builder_aggregation.py`
- Updated YAML baselines again (8 idiot_index inputs now wired)
**Issues:** None.
**Deviations:** None.

### Phase 3 Completion
**Completed:** 2026-02-16
**Actual Changes:** No code changes. Validation only.
**Results:**
- 654 tests pass, 0 failures
- Lint: no new issues (pre-existing import ordering only)
- Mypy: no new issues (pre-existing untyped stubs only)
- Spike rerun: all 4 hypotheses CONFIRMED
- Wiring counts: 54/70 wired (not 57/70 as spec projected)
**Deviations:** Spec projected 57/70 but actual is 54/70. The 3 `permitting.*` SingletonTerms
  (`permitting.raw_material_cost`, `permitting.fabrication_cost`, `permitting.installation_cost`
  in site_infra) are genuinely unresolvable — no upstream CalcUsage or aggregation module produces
  those outputs in the current model. These are correct ENTRY_POINTs, not a bug.
  Breakdown: 12 multiplicity + 1 misc_hardware_cost + 3 permitting = 16 entry points.

### Post-Completion: Test Coverage Hardening
**Completed:** 2026-02-16
**Trigger:** Implementation audit found tests A-3 and A-4 (integration) were not
exercising the code paths they claimed to protect:
- **A-3** (Bug A2): Vacuously passing — solar_battery has zero CalcDef outputs with
  FCE nodes, so `unsupported_reason` is always None and the assert never fires.
- **A-4** (Bug A3): Tests the wrong code path — `transformed_expression` is built by
  `_walk_aggregation_ast()` directly, not via `reconstruct_expression()`. Validates
  the A1 fix (already well-covered), not the A3 fix.

**Fix:** Added targeted unit tests using dual-name mock classes whose `__name__`
contains both `"FeatureChainExpression"` and `"OperatorExpression"`, reproducing
the real SysIDE subtype dual-match via `SysideAdapter.is_instance()`'s name-based
fallback.

**New tests:**
- `tests/unit/test_expression_compiler.py::TestFCEBeforeOEOrdering` (3 tests) —
  Bug A2: dual-match node produces FCE diagnostic, not `"unsupported operator: ."`
- `tests/unit/test_hierarchy_resolver.py::TestFCEBeforeOEOrdering` (3 tests) —
  Bug A3: dual-match node produces `"array_bos.capital_cost"`, not `".(array_bos)"`

**Validation:** 660 tests pass (6 new), 0 failures. Verified mocks reproduce the
exact bug artifacts when handlers are called directly.

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete**
