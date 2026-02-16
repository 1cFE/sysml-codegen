# Implementation Plan: Aggregation Wiring Fix

**Status:** Complete
**Created:** 2026-02-16
**Last Updated:** 2026-02-16

## Source Documents
- **Spec:** `.project/active/aggregation-wiring-fix/spec.md`
- **Design:** `.project/active/aggregation-wiring-fix/design.md` — See here for component details, code diffs, algorithm descriptions
- **Research:** `.project/research/20260215-225131_aggregation-wiring-gap-analysis.md`
- **Spike Report:** `.project/active/aggregation-fix-validation/spike_report.md`

## Implementation Strategy

**Phasing Rationale:**
Phase 1 delivers the core fix (Changes 1 & 2) because it resolves all 12
resolvable inputs and is the highest-value, highest-risk change. Change 2
(registration) ships with Change 1 because it's a prerequisite for
agg-to-agg resolution (Test 4). Phase 2 adds SingletonTerm reordering
(Change 3), which builds on Phase 1's scoped lookup. Phase 3 adds
diagnostic logging and runs comprehensive validation.

**Overall Validation Approach:**
- Each phase starts with tests (write failing tests, then implement)
- Each phase runs full test suite to confirm no regressions
- Phase 3 includes optional spike re-run against real model

---

## Phase 1: Key_E_stripped Registration + Scoped Lookup

### Goal
Fix the core wiring bug: add Key_E_stripped to Phase 1b registration
(Change 2) and scope the registry lookup in
`_resolve_aggregation_input_channel` (Change 1). This resolves all 12
resolvable SumTerm inputs, fixes the CHAIN_PART_MISMATCH bug (4 inverter
inputs), and prevents Key_D collision mis-wiring.

### Test Stencil (Write This First)
```python
# Add to TestResolveAggregationInputChannel in test_graph_builder_aggregation.py

def test_scoped_registry_resolves_when_chain_fails(self):
    """Scoped key resolves when no CHAIN redef exists (AC-2)."""
    expected_channel = get_channel_name("Design__plant__array__pv_module__cost_model", "total_cost")
    registry = OutputRegistry()
    # Register with scoped Phase 2 alias (the key the fix constructs)
    registry.register(expected_channel, [])
    registry.register_alias("plant.array.pv_module.capital_cost", expected_channel)
    result = _resolve_aggregation_input_channel(
        "pv_module.capital_cost", "Design__plant__array", [], registry,
    )
    assert result == expected_channel

def test_scoped_registry_resolves_chain_part_mismatch(self):
    """Scoped key resolves when CHAIN fails due to PartDef/PartUsage name mismatch (AC-2)."""
    expected_channel = get_channel_name("Design__plant__array__inverter__cost_model", "total_cost")
    registry = OutputRegistry()
    registry.register(expected_channel, [])
    registry.register_alias("plant.array.inverter.capital_cost", expected_channel)
    # CHAIN redef on String_Inverter won't match "inverter" via sanitize_name
    redefs = [_make_chain_redef("capital_cost", "cost_model.total_cost", "Lib__String_Inverter")]
    result = _resolve_aggregation_input_channel(
        "inverter.capital_cost", "Design__plant__array", redefs, registry,
    )
    assert result == expected_channel

def test_scoped_before_unscoped_avoids_collision(self):
    """Scoped key wins over colliding Key_D (AC-7)."""
    correct_channel = "Design__plant__array__child__calc__cost"
    wrong_channel = "Design__other__child__calc__cost"
    registry = OutputRegistry()
    registry.register(correct_channel, [])
    registry.register(wrong_channel, ["child.cost"])  # Key_D collision
    registry.register_alias("plant.array.child.cost", correct_channel)  # scoped
    result = _resolve_aggregation_input_channel(
        "child.cost", "Design__plant__array", [], registry,
    )
    assert result == correct_channel

def test_agg_to_agg_via_key_e_stripped(self):
    """Plant-level resolves sub-assembly agg via Key_E_stripped (AC-3, AC-6)."""
    agg_channel = "Design__plant__array__capital_cost__capital_cost"
    registry = OutputRegistry()
    # Key_E_stripped: "plant.array.capital_cost" (registered by Change 2)
    registry.register(agg_channel, ["plant.array.capital_cost"])
    result = _resolve_aggregation_input_channel(
        "array.capital_cost", "Design__plant", [], registry,
    )
    assert result == agg_channel
```

### Changes Required

**See `design.md` for:**
- Change 1 algorithm and code diff → `design.md#change-1-scoped-registry-lookup`
- Change 2 algorithm and code diff → `design.md#change-2-key_e_stripped-registration`
- Key format table → `design.md#change-2` (Key_D, Key_E, Key_E_stripped, Bare)

**Specific file changes:**

#### 1. Test File (write first)
**File:** `tests/unit/test_graph_builder_aggregation.py`
- [x] Add `test_scoped_registry_resolves_when_chain_fails` to `TestResolveAggregationInputChannel`
- [x] Add `test_scoped_registry_resolves_chain_part_mismatch`
- [x] Add `test_scoped_before_unscoped_avoids_collision`
- [x] Add `test_agg_to_agg_via_key_e_stripped`
- [x] Run tests → confirm 4 new tests FAIL (scoped lookup not yet implemented)

#### 2. Registration (Change 2)
**File:** `src/sysml_codegen/generation/initialization.py:560-572`
- [x] Add Key_E_stripped after Key_D/Key_E (see `design.md#change-2` for exact code)
- [x] Add alias Key_E_stripped in BF-7 alias loop
- [x] Guard both with `if len(instance_parts) > 1`

#### 3. Scoped Lookup (Change 1)
**File:** `src/sysml_codegen/resolution/graph_builder.py:814-821`
- [x] Replace unscoped fallback with scoped-then-unscoped sequence (see `design.md#change-1` for exact code)
- [x] Add `len(instance_parts) > 1` guard

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/unit/test_graph_builder_aggregation.py -v` → 34 pass (4 new + 30 existing)
- [x] `uv run pytest tests/ -v` → 645 passed, 0 failed (baseline YAML regenerated)

**Manual:**
- [x] Verify `test_agg_to_agg_falls_back_to_registry` (line 114) still passes — it exercises Key_D fallback after scoped miss
- [x] Verify all existing `TestResolveAggregationInputChannel` tests still pass via CHAIN path

**What We Know Works After This Phase:**
- Scoped registry lookup resolves SumTerms when CHAIN fails
- CHAIN_PART_MISMATCH (String_Inverter vs inverter) resolved
- Key_D collision avoidance works (scoped wins)
- Agg-to-agg via Key_E_stripped works for plant-level references
- All existing behavior preserved (CHAIN path, Key_D fallback)

---

## Phase 2: SingletonTerm Registry-First + Module-Level Tests

### Goal
Fix SingletonTerm resolution order (Change 3) so registry-first handles
aggregation targets. Add module-level integration tests that exercise
Changes 1-3 through `_build_aggregation_module`.

### Test Stencil (Write This First)
```python
# Add to TestBuildAggregationModule in test_graph_builder_aggregation.py

def test_singleton_term_registry_first_for_aggregation_target(self):
    """SingletonTerm resolves aggregation output via registry-first (AC-5)."""
    # Aggregation output has double-attr channel format
    agg_channel = "Design__plant__array__cost__cost"
    agg = _make_scoped_agg(
        singleton_terms=[SingletonTerm("array.cost")],
        instance_path="Design__plant",
        sum_terms=[],
    )
    registry = self._make_registry({agg_channel: ["plant.array.cost"]})
    entry_points: dict[str, EntryPoint] = {}
    module = _build_aggregation_module(agg, [], registry, entry_points, None)
    singleton_inputs = [i for i in module.inputs if "cost" in i.param_name]
    assert len(singleton_inputs) == 1
    assert singleton_inputs[0].source.source_type == "module_output"
    assert singleton_inputs[0].source.producer_channel == agg_channel

def test_sum_term_scoped_resolution_no_chain(self):
    """SumTerm resolves via scoped registry when no CHAIN exists (AC-2)."""
    expected_channel = get_channel_name(
        "Design__plant__array__pv_module__cost_model", "total_cost"
    )
    agg = _make_scoped_agg(
        sum_terms=[SumTerm("pv_module", "capital_cost", None, None)],
        instance_path="Design__plant__array",
    )
    registry = self._make_registry({expected_channel: []})
    # Register scoped alias (as Phase 2 CHAIN alias registration would)
    registry.register_alias("plant.array.pv_module.capital_cost", expected_channel)
    entry_points: dict[str, EntryPoint] = {}
    module = _build_aggregation_module(agg, [], registry, entry_points, None)
    cost_inputs = [i for i in module.inputs if i.param_name == "pv_module_capital_cost"]
    assert len(cost_inputs) == 1
    assert cost_inputs[0].source.source_type == "module_output"
    assert cost_inputs[0].source.producer_channel == expected_channel
```

### Changes Required

**See `design.md` for:**
- Change 3 code diff → `design.md#change-3-singletonterm-registry-first-resolution`
- Behavioral note on CalcUsage fallback → `design.md#change-3` ("Behavioral note for CalcUsage targets")

**Specific file changes:**

#### 1. Test File (write first)
**File:** `tests/unit/test_graph_builder_aggregation.py`
- [x] Add `test_singleton_term_registry_first_for_aggregation_target` to `TestBuildAggregationModule`
- [x] Add `test_sum_term_scoped_resolution_no_chain` to `TestBuildAggregationModule`
- [x] Run tests → both PASSED already (see deviation note below)
- [x] Note: Test 7 already PASSED (Phase 1's Changes 1 & 2 handle SumTerm resolution)

#### 2. SingletonTerm Reorder (Change 3)
**File:** `src/sysml_codegen/resolution/graph_builder.py:955-978`
- [x] Swap resolution order: `_resolve_aggregation_input_channel()` first, direct construction second (see `design.md#change-3` for exact code)
- [x] Keep direct construction as fallback for CalcUsage targets

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/unit/test_graph_builder_aggregation.py -v` → 36 passed (6 new + 30 existing)
- [x] `uv run pytest tests/ -v` → 647 passed, 0 failed

**Manual:**
- [x] Verify `test_singleton_term_direct_channel` still passes — exercises direct-construction fallback (registry-first returns None, then direct construction succeeds via canonical membership check)
- [x] Verify `test_singleton_term_fallback_to_chain_resolution` still passes

**What We Know Works After This Phase:**
- SingletonTerm resolves aggregation targets via registry (double-attr format)
- SingletonTerm CalcUsage fallback still works via direct construction
- SumTerm module-level wiring works end-to-end through `_build_aggregation_module`
- All 6 acceptance criteria tested (AC-1 via existing tests, AC-2/3/5/6/7 via new tests)
- AC-4 validated by existing `test_singleton_term_direct_channel`

---

## Phase 3: Diagnostic Logging + Full Validation

### Goal
Add diagnostic logging (Change 4) for future debuggability and run
comprehensive validation including optional spike re-run.

### Test Stencil (Write This First)
```python
# No new test file needed. Logging is validated by:
# 1. Existing tests still pass (logging doesn't change behavior)
# 2. Manual inspection of log output at DEBUG level
```

### Changes Required

**See `design.md` for:**
- Change 4 log messages → `design.md#change-4-diagnostic-logging`

**Specific file changes:**

#### 1. Resolution Function Logging (Change 1 already includes DEBUG logs)
**File:** `src/sysml_codegen/resolution/graph_builder.py`
- [x] Verify Change 1's DEBUG logs are in place (scoped hit, Key_D hit, unresolved)
- [x] Add WARNING log to SumTerm failure path (line 901)
- [x] Add WARNING log to SingletonTerm failure path (line 989)

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/ -v` → 647 passed, 0 failed (AC-8)
- [x] `uv run pytest tests/unit/test_graph_builder_aggregation.py -v` → 36 passed, 6 new (AC-9)

**Manual:**
- [x] Verify no files changed outside `graph_builder.py`, `initialization.py`, and test file (AC-10):
      Only: `graph_builder.py`, `initialization.py`, `test_graph_builder_aggregation.py`, `baseline_yaml/solar_battery.yaml`
- [x] Optional: Re-run spike script to verify 12/12 against real model:
      `uv run python scripts/spike_aggregation_validation.py`
      Result: 12/12 proposed scoped keys resolve. All 4 spot-checks pass.

**What We Know Works After This Phase:**
- All acceptance criteria satisfied (AC-1 through AC-10)
- Diagnostic logging aids future debugging
- Ready to proceed to COST-PATTERN Item 5 (E2E Validation)

---

## Environment Setup

**Per CLAUDE.md:**
```bash
# Install (if needed)
uv pip install -e ~/agentic-mbse && uv pip install -e ".[dev]"

# Run tests
uv run pytest tests/
uv run pytest tests/unit/test_graph_builder_aggregation.py -v

# Type check (after all changes)
uv run mypy src/

# Lint
uv run ruff check src/
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: If `test_agg_to_agg_falls_back_to_registry` (line 114) fails, it means the unscoped Key_D fallback path broke. Check that the unscoped lookup is still attempted after the scoped miss.
- **Phase 2**: If `test_singleton_term_direct_channel` (line 265) fails, it means `_resolve_aggregation_input_channel` is unexpectedly returning a result for a canonical-only registration. Check that the function correctly returns None when no CHAIN redefs or scoped aliases exist.
- **Phase 3**: If spike re-run shows fewer than 12/12 hits, compare scoped keys against actual registry contents to identify which key format is missing.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-02-16
**Actual Changes:**
- Added 4 tests to `TestResolveAggregationInputChannel` in `tests/unit/test_graph_builder_aggregation.py` (lines 180-255)
- Added Key_E_stripped registration + alias Key_E_stripped to Phase 1b in `src/sysml_codegen/generation/initialization.py:563-568,575-576`
- Replaced unscoped fallback with scoped-then-unscoped lookup in `src/sysml_codegen/resolution/graph_builder.py:815-847`
- Regenerated baseline YAML via `scripts/capture_baseline_yaml.py` (solar_battery wiring changes expected)

**Issues:**
- Baseline YAML diff test (`test_yaml_matches_baseline[solar_battery]`) failed as expected — the fix changes aggregation input wiring from ENTRY_POINT to MODULE_OUTPUT. Regenerated baseline.

**Deviations:** None — implementation matches design.md exactly.

### Phase 2 Completion
**Completed:** 2026-02-16
**Actual Changes:**
- Added 2 tests to `TestBuildAggregationModule` in `tests/unit/test_graph_builder_aggregation.py` (lines 385-420)
- Swapped SingletonTerm resolution order in `src/sysml_codegen/resolution/graph_builder.py:955-978`: registry-first, direct construction as fallback

**Issues:** None.

**Deviations:**
- Plan expected Test 5 (`test_singleton_term_registry_first_for_aggregation_target`) to FAIL before Change 3. It actually PASSED already because direct construction produces the wrong channel format for aggregation targets (single-attr vs double-attr), so it falls through to the chain fallback which uses Phase 1's scoped lookup. Change 3 is still correct — it prevents direct construction from ever accidentally matching aggregation targets and makes the resolution path more robust.

### Phase 3 Completion
**Completed:** 2026-02-16
**Actual Changes:**
- Verified 3 DEBUG logs from Change 1 already in place (lines 825-828, 835-838, 841-846)
- Added WARNING log to SumTerm failure path at `graph_builder.py:901`
- Added WARNING log to SingletonTerm failure path at `graph_builder.py:989`

**Issues:** None.

**Deviations:** None.

---

**Status**: Draft
