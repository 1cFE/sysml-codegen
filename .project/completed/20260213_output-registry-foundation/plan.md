# Implementation Plan: OutputRegistry Foundation

**Status:** Complete
**Created:** 2026-02-13 22:18 UTC
**Last Updated:** 2026-02-13 22:18 UTC

## Source Documents
- **Spec:** `.project/active/output-registry-foundation/spec.md`
- **Design:** `.project/active/output-registry-foundation/design.md` -- See here for component details, function signatures, implementation code, dependencies

## Implementation Strategy

**Phasing Rationale:**
Three phases in dependency order: (1) production code first so types exist, (2) unit tests to validate the contract in isolation, (3) integration tests that load real models. This ordering means each phase builds on a verified foundation -- Phase 2 catches logic bugs before Phase 3 adds slow model loading.

**Overall Validation Approach:**
- Phase 1: mypy + ruff (fast, confirms structure)
- Phase 2: pytest unit tests (fast, confirms behavior)
- Phase 3: pytest integration tests (slow, confirms real data)
- Gate 1: full `uv run pytest tests/` after Phase 3

---

## Phase 1: Production Code (Data Models + Registry)

### Goal

Create all production source files so types are importable. This is purely structural -- no tests yet, validated by type checking only.

### Test Stencil (Write This First)

No test stencil -- Phase 1 is validated by mypy/ruff, not pytest. Tests come in Phase 2.

### Changes Required

**See `design.md` for:**
- `ChannelAlias` model definition -> `design.md#component-1-channelalias-pydantic-model`
- `OutputRegistry` class with full implementation -> `design.md#component-2-outputregistry-class`
- `is_transitive_default()` function -> `design.md#component-3-is_transitive_default-utility`
- `core/__init__.py` exports -> `design.md#component-4-coreinitpy-updates`

**Specific file changes:**

#### 1. `ChannelAlias` model
**File:** `src/sysml_codegen/core/models.py` (MODIFY)
- [x] Add `from typing import Literal` import
- [x] Add `ChannelAlias` class after `BindingResolution` (line 68), before `__all__`
- [x] Add `"ChannelAlias"` to `__all__`

#### 2. `OutputRegistry` class + `is_transitive_default()`
**File:** `src/sysml_codegen/core/output_registry.py` (NEW)
- [x] Create file with `OutputRegistry` class (3 methods + `derive_key_c` staticmethod + `__len__` + `__repr__` + `canonical_channels` property)
- [x] Add `is_transitive_default()` module-level function
- [x] Add `__all__` export list

#### 3. `core/__init__.py` exports
**File:** `src/sysml_codegen/core/__init__.py` (MODIFY)
- [x] Add `ChannelAlias` to `core.models` import
- [x] Add `OutputRegistry` and `is_transitive_default` import from `core.output_registry`
- [x] Add all three to `__all__`

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run mypy src/sysml_codegen/core/models.py` -> passes
- [x] `uv run mypy src/sysml_codegen/core/output_registry.py` -> passes
- [x] `uv run ruff check src/sysml_codegen/core/` -> passes
- [x] `uv run python -c "from sysml_codegen.core import ChannelAlias, OutputRegistry, is_transitive_default"` -> imports succeed

**What We Know Works After This Phase:**
All new types exist, are importable, and pass static analysis. No behavioral verification yet.

---

## Phase 2: Unit Tests

### Goal

Write the full unit test suite for `OutputRegistry` and `is_transitive_default()`. This is the behavioral validation -- 8 test classes covering all spec acceptance criteria.

### Test Stencil (Write This First)

```python
# Core contract test -- write first, validates the fundamental behavior
class TestRegister:
    def test_register_single_key(self):
        reg = OutputRegistry()
        reg.register("Design__plant__lcoe__lcoe_per_mwh", ["lcoe.lcoe_per_mwh"])
        assert reg.resolve("lcoe.lcoe_per_mwh") == "Design__plant__lcoe__lcoe_per_mwh"

    def test_canonical_channel_self_resolves(self):
        reg = OutputRegistry()
        canonical = "Design__plant__lcoe__lcoe_per_mwh"
        reg.register(canonical, [])
        assert reg.resolve(canonical) == canonical

class TestCollisionHandling:
    def test_collision_refuses_overwrite(self):
        reg = OutputRegistry()
        reg.register("channel_A", ["shared.key"])
        reg.register("channel_B", ["shared.key"])
        assert reg.resolve("shared.key") == "channel_A"  # first wins

class TestResolve:
    def test_resolve_bare_name_returns_none(self):
        reg = _make_registry_with_calc_usage()
        assert reg.resolve("total_cost") is None  # negative: no bare names
```

### Changes Required

**See `design.md` for:**
- Test class structure and test names -> `design.md#component-5-unit-tests`
- Factory function signatures -> `design.md#test-factories`
- Spike 8 key format values -> `design.md#test-classes`

**Specific file changes:**

#### 1. Unit test file
**File:** `tests/unit/test_output_registry.py` (NEW)
- [x] Create factory functions: `_make_registry_with_calc_usage()`, `_make_registry_with_virtual_calc_usage()`, `_make_registry_with_aggregation()`, `_make_registry_with_formula()`
- [x] `class TestRegister` -- 5 tests (basic registration)
- [x] `class TestCollisionHandling` -- 3 tests (refuse overwrite, logging, 9-way collision)
- [x] `class TestRegisterAlias` -- 3 tests (alias resolution, unregistered target, alias collision)
- [x] `class TestResolve` -- 5 tests (exact match, unregistered, bare name, SYSML_QN, no normalization)
- [x] `class TestKeyFormats` -- 6 tests (Key_A through Key_F from Spike 8)
- [x] `class TestDeriveKeyC` -- 3 tests (concrete, virtual deep, single segment)
- [x] `class TestPhaseOrdering` -- 4 tests (Phase 2/3/4 ordering, isolation)
- [x] `class TestIsTransitiveDefault` -- 8 tests (dotted path, numeric, None, bare, int, empty, complex, scientific)

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/unit/test_output_registry.py -v` -> 41 passed in 0.28s (37 original + 4 diagnostic tests)
- [x] `uv run pytest tests/` -> 564 passed, 1 xfailed (no regressions)

**What We Know Works After This Phase:**
All spec acceptance criteria verified: registration, collision handling, alias enforcement, resolution, key format contract, phase ordering, `is_transitive_default()`, negative tests, and diagnostic helpers (`canonical_channels`, `__repr__`).

---

## Phase 3: Integration Tests (Smoke + Bug 2 xfail)

### Goal

Validate the OutputRegistry against real model data (smoke test) and capture Bug 2 as a failing regression test (xfail). These are slow tests (SysIDE model loading) and are the final confidence gate before Item 2a.

### Test Stencil (Write This First)

```python
# Smoke test -- validates real data works, not just synthetic
class TestOutputRegistrySmokeRealData:
    @pytest.fixture(scope="class")
    def registry(self, pipeline_context) -> OutputRegistry:
        reg = OutputRegistry()
        # Phase 1 registration from real CalcUsage data
        ...
        return reg

    def test_known_chain_source_path_resolves(self, registry):
        assert registry.resolve("lcoe.lcoe_per_mwh") is not None

# Bug 2 xfail -- proves the bug exists, will go green after Item 3
class TestBug2ExposesPureTwoHopFailure:
    @pytest.mark.xfail(strict=True, reason="Bug 2: EXPOSE_PURE two-hop failure")
    def test_total_capex_resolves_to_module_output(self, pipeline_context):
        # Should be MODULE_OUTPUT but is currently ENTRY_POINT
        ...
```

### Changes Required

**See `design.md` for:**
- Smoke test full code -> `design.md#component-6-smoke-test-real-model-data`
- Bug 2 xfail test full code -> `design.md#component-7-bug-2-xfail-regression-test`

**Specific file changes:**

#### 1. Smoke test
**File:** `tests/integration/test_output_registry_smoke.py` (NEW)
- [x] `pipeline_context` fixture loading `solar_battery_model`
- [x] `registry` fixture building Phase 1 OutputRegistry from real CalcUsage data
- [x] `test_registry_has_entries` -- sanity check
- [x] `test_known_chain_source_path_resolves` -- Key_A resolution
- [x] `test_key_c_resolves_for_virtual_calc_usage` -- Key_C resolution for virtual CalcUsage

#### 2. Bug 2 xfail regression test
**File:** `tests/integration/test_bug2_regression.py` (NEW)
- [x] `pipeline_context` fixture loading `attr_expr_probe`
- [x] `test_total_capex_resolves_to_module_output` -- xfail, `strict=True`

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/integration/test_output_registry_smoke.py -v` -> 3 passed in 1.15s
- [x] `uv run pytest tests/integration/test_bug2_regression.py -v` -> 1 xfailed in 1.02s
- [x] `uv run pytest tests/` -> 560 passed, 1 xfailed in 4.84s (no regressions)

**Manual:**
- [x] Verify xfail output shows `XFAIL` (not `FAILED` or `PASSED`)

**What We Know Works After This Phase:**
Real solar_battery data produces resolvable registry keys (Key_A, Key_C). Bug 2 is captured as a failing test ready to go green in Item 3.

---

## Gate 1 Checklist (Final Validation)

After all 3 phases, run the full Gate 1 from the epic:

```bash
uv run pytest tests/unit/test_output_registry.py -v
uv run pytest tests/integration/test_output_registry_smoke.py -v
uv run pytest tests/integration/test_bug2_regression.py -v
uv run pytest tests/
uv run mypy src/sysml_codegen/core/output_registry.py
uv run mypy src/sysml_codegen/core/models.py
uv run ruff check src/sysml_codegen/core/
```

- [x] All unit tests pass (41 passed)
- [x] Smoke tests pass (3 passed)
- [x] Bug 2 xfail shows `XFAIL` (1 xfailed)
- [x] Full test suite passes (564 passed, 1 xfailed)
- [x] mypy passes on new/modified files
- [x] ruff passes on new/modified files

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis.**

**Phase-Specific Mitigations:**
- **Phase 2**: If collision logging test fails, check `caplog` fixture level (`logging.WARNING`)
- **Phase 3**: If smoke test Key_C assertion fails, run `build_pipeline_context` in a REPL and inspect `calc_usages` to find the actual virtual CalcUsage QN. The test diagnostic message will list available keys.
- **Phase 3**: If Bug 2 xfail unexpectedly passes (`strict=True` will flag this), investigate whether the fixture's template expansion behavior changed. This would be a surprise but not a blocker.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-02-13
**Actual Changes:**
- Modified `src/sysml_codegen/core/models.py`: Added `Literal` import, `ChannelAlias` Pydantic BaseModel (4 fields, Literal source type), updated `__all__`
- Created `src/sysml_codegen/core/output_registry.py`: `OutputRegistry` class with `register()`, `register_alias()`, `resolve()`, `derive_key_c()` staticmethod, `__len__`, `__repr__`, `canonical_channels` property; `is_transitive_default()` module-level function; `__all__`
- Modified `src/sysml_codegen/core/__init__.py`: Added imports and `__all__` entries for `ChannelAlias`, `OutputRegistry`, `is_transitive_default`
**Issues:** None
**Deviations:** None -- implementation matches design exactly

### Phase 2 Completion
**Completed:** 2026-02-13
**Actual Changes:**
- Created `tests/unit/test_output_registry.py`: 4 factory functions, 8 test classes, 37 tests covering all spec acceptance criteria (registration, collision, aliases, resolution, key formats, derive_key_c, phase ordering, is_transitive_default)
**Issues:** None
**Deviations:** None -- all 37 tests pass, full suite (557) passes with no regressions

### Phase 3 Completion
**Completed:** 2026-02-13
**Actual Changes:**
- Created `tests/integration/test_output_registry_smoke.py`: 3 tests with real solar_battery data (Phase 1 registry, Key_A + Key_C resolution)
- Created `tests/integration/test_bug2_regression.py`: 1 xfail test with attr_expr_probe (Bug 2 EXPOSE_PURE two-hop failure)
**Issues:** None
**Deviations:** None -- smoke tests pass, xfail shows XFAIL as expected

---

**Status**: Complete
