# Implementation Plan: Codegen Runtime Gap Fixes

**Status:** Complete
**Created:** 2026-02-01T22:20:00Z
**Last Updated:** 2026-02-01T22:20:00Z

## Source Documents
- **Spec:** `.project/active/codegen-runtime-gap-fixes/spec.md`
- **Design:** `.project/active/codegen-runtime-gap-fixes/design.md` ← See here for component details, dependencies, architecture

## Implementation Strategy

**Phasing Rationale:**
Start with test infrastructure and the zero-risk Gap 3 fix (Phase 1), then tackle the critical Gap 1 path filter fix (Phase 2), then Gap 2 exit point registration (Phase 3), and finally integration tests (Phase 4). Each phase is independently verifiable and builds on the previous. The test fixture is established first so all subsequent phases can use it.

**Overall Validation Approach:**
- Each phase starts with tests (or test infrastructure)
- Each phase has `uv run pytest tests/` regression check
- Final phase runs full suite + mypy + ruff

---

## Phase 1: Test Infrastructure + Gap 3 (Static FusionParams Removal)

### Goal
Set up the chain spike test fixture and eliminate the static FusionParams template. This is zero-risk, establishes infrastructure for later phases, and gets a quick win on Gap 3.

### Test Stencil (Write This First)
```python
# Update existing test_generates_schemas to assert NO FusionParams
def test_generates_schemas(self, tmp_path, sample_model_path):
    # ... run codegen ...
    ref_schema = output / "test_pkg_schemas.py"
    assert not ref_schema.exists(), "Static FusionParams schema should NOT be generated"
```

### Changes Required

**See `design.md#component-3` for:** Gap 3 removal details
**See `design.md#component-4` for:** Test fixture setup

**Specific file changes:**

#### 1. Copy chain spike model fixture
- [ ] Create `tests/fixtures/chain_spike_model/`
- [ ] Copy `library.sysml` from `/home/reid/1cfe/fusion-tea/models/tests/codegen_chain_spike/`
- [ ] Copy `design.sysml` from `/home/reid/1cfe/fusion-tea/models/tests/codegen_chain_spike/`

#### 2. Add conftest fixture
**File:** `tests/conftest.py`
- [ ] Add `chain_spike_model_path` fixture returning `fixtures_path / "chain_spike_model"`

#### 3. Delete static template
- [ ] Delete `src/sysml_codegen/templates/schemas_ref.py` (AC-6)

#### 4. Remove copy operation
**File:** `src/sysml_codegen/cli/__init__.py:137-143`
- [ ] Remove the `ref_schema` copy block in `_generate_schemas()` (see `design.md#component-3` for exact lines)

#### 5. Update existing schema test
**File:** `tests/integration/test_full_pipeline.py:256-276`
- [ ] Replace `ref_schema.exists() or len(multioutput_schemas) > 0` assertion with `not ref_schema.exists()` (see `design.md#component-6` for replacement code)

### Validation

**Automated:**
- [ ] `uv run pytest tests/integration/test_full_pipeline.py::TestRunCodegenPhases::test_generates_schemas -v` → passes with new assertion
- [ ] `uv run pytest tests/ -v` → all existing tests pass (AC-7)

**Manual:**
- [ ] Verify `templates/schemas_ref.py` does not exist: `ls src/sysml_codegen/templates/schemas_ref.py` → "No such file"
- [ ] Verify chain spike fixture exists: `ls tests/fixtures/chain_spike_model/` → shows `library.sysml`, `design.sysml`

**What We Know Works After This Phase:**
- Test fixture is in place for subsequent phases
- Gap 3 is fully resolved (AC-5, AC-6)
- No regressions in existing tests

---

## Phase 2: Gap 1 — Design Path Filter + Crash Guard

### Goal
Fix the empty `design_params.json` by changing the path filter default, wiring the `--design-path-filter` CLI flag, and adding the OperatorExpression crash guard.

### Test Stencil (Write This First)
```python
# tests/unit/test_parameter_groups.py
class TestExtractDesignAttributes:
    def test_default_filter_includes_test_models(self, chain_spike_model_path):
        # Load model, call extract_design_attributes() with default args
        # Assert >= 3 attrs with non-None defaults (length, width, rate)

class TestExtractDefaultValueCrashGuard:
    def test_operator_expression_does_not_crash(self, chain_spike_model_path):
        # Load model, call extract_design_attributes(model, design_path_filter="")
        # Assert no exception raised

class TestBuildPipelineContextDefaults:
    def test_entry_points_have_defaults(self, chain_spike_model_path):
        # Call build_pipeline_context([chain_spike_model_path])
        # Assert >= 3 entry point params with non-None default_value
```

### Changes Required

**See `design.md#component-1` for:** All Gap 1 changes (1a through 1d)

**Specific file changes:**

#### 1. Unit tests (write first)
**File:** `tests/unit/test_parameter_groups.py` (NEW)
- [ ] Create file with test classes from `design.md#component-5` (5a)
- [ ] `TestExtractDesignAttributes` — 3 tests for path filter behavior
- [ ] `TestExtractDefaultValueCrashGuard` — 1 test for crash guard
- [ ] `TestBuildPipelineContextDefaults` — 1 test for populated entry points

#### 2. Change default filter
**File:** `src/sysml_codegen/analysis/parameter_groups.py:89`
- [ ] Change `design_path_filter: str = "models/designs"` → `design_path_filter: str = ""`

#### 3. Add crash guard
**File:** `src/sysml_codegen/analysis/parameter_groups.py:186-189`
- [ ] Wrap `evaluate_true_static_expression()` in try/except (see `design.md#component-1` 1d)

#### 4. Wire through initialization
**File:** `src/sysml_codegen/generation/initialization.py:82-86,140`
- [ ] Add `design_path_filter: str = ""` param to `build_pipeline_context()` signature
- [ ] Pass `design_path_filter=design_path_filter` to `extract_design_attributes()` at line 140

#### 5. Add to GenerationConfig + CLI
**File:** `src/sysml_codegen/cli/__init__.py`
- [ ] Add `design_path_filter: str = ""` to `GenerationConfig` dataclass (after line 59)
- [ ] Add `--design-path-filter` argument to `gen_parser` (after `--verbose`)
- [ ] Wire `design_path_filter=args.design_path_filter` in `cmd_generate()` (line ~442)
- [ ] Wire `design_path_filter=config.design_path_filter` in `run_codegen()` call to `build_pipeline_context()` (line ~610)

### Validation

**Automated:**
- [ ] `uv run pytest tests/unit/test_parameter_groups.py -v` → all 5 tests pass
- [ ] `uv run pytest tests/ -v` → no regressions (AC-7)

**Manual:**
- [ ] `uv run sysml-codegen generate --help` → shows `--design-path-filter` flag (FR-4)

**What We Know Works After This Phase:**
- Design attributes extracted correctly from any model location (AC-1)
- OperatorExpressions don't crash (AC-2)
- CLI flag is wired and functional (FR-4)
- Safety net in `graph_builder.py` can populate defaults

---

## Phase 3: Gap 2 — Exit Point Type Registration

### Goal
Register `RootModel[float]` exit point types in `CUSTOM_SCHEMA_TYPES` so TEAx's output router has handlers for them.

### Test Stencil (Write This First)
```python
# tests/unit/test_registry_generation.py
class TestCollectExitPointTypes:
    def test_single_output_modules_produce_float(self):
        # Create PipelineModule with field_name="root", python_type="float"
        # Assert _collect_exit_point_primitive_types() returns ["Float"]

class TestRegistryTemplateRendering:
    def test_custom_schema_types_includes_exit_point_types(self):
        # Render template with exit_point_types=["Float"]
        # Assert "Float" in CUSTOM_SCHEMA_TYPES
        # Assert "from test_pkg.primitives import Float" in output
```

### Changes Required

**See `design.md#component-2` for:** All Gap 2 changes (2a through 2c)

**Specific file changes:**

#### 1. Unit tests (write first)
**File:** `tests/unit/test_registry_generation.py` (NEW)
- [ ] Create file with test classes from `design.md#component-5` (5b)
- [ ] `TestCollectExitPointTypes` — 3 tests (single-output, multi-output, deduplication)
- [ ] `TestRegistryTemplateRendering` — 2 tests (with and without exit point types)

#### 2. Add helper function + update signature
**File:** `src/sysml_codegen/generation/registry.py`
- [ ] Add `_collect_exit_point_primitive_types()` function (see `design.md#component-2` 2a)
- [ ] Add `exit_point_primitive_types: list[str] | None = None` param to `generate_registry_function()`
- [ ] Add `"package_name": package_name` to template context dict
- [ ] Add `"exit_point_types": exit_point_primitive_types or []` to template context dict

#### 3. Update Jinja2 template
**File:** `src/sysml_codegen/templates/registry_function.py.jinja2`
- [ ] Add primitives import block: `{% if exit_point_types %}from {{ package_name }}.primitives import ...{% endif %}`
- [ ] Change `CUSTOM_SCHEMA_TYPES` condition from `{% if parameter_groups %}` to `{% if parameter_groups or exit_point_types %}`
- [ ] Add exit point types loop inside `CUSTOM_SCHEMA_TYPES` list
- [ ] Use trailing commas on all items (see `design.md#component-2` 2b)

#### 4. Wire through CLI orchestrator
**File:** `src/sysml_codegen/cli/__init__.py:317-343`
- [ ] Import `_collect_exit_point_primitive_types` in `_generate_registry()`
- [ ] Call it with `ctx.computation_graph.modules`
- [ ] Pass `exit_point_primitive_types=exit_point_types` to `generate_registry_function()`

### Validation

**Automated:**
- [ ] `uv run pytest tests/unit/test_registry_generation.py -v` → all 5 tests pass
- [ ] `uv run pytest tests/ -v` → no regressions (AC-7)

**What We Know Works After This Phase:**
- Exit point types collected from ComputationGraph modules
- Template renders primitives import + CUSTOM_SCHEMA_TYPES with both entry point and exit point types (AC-3)
- Backward compatible — empty exit_point_types produces same output as before

---

## Phase 4: Integration Tests + Final Validation

### Goal
Add end-to-end integration tests that verify all three gaps are fixed in combination, run full validation suite.

### Test Stencil (Write This First)
```python
# tests/integration/test_full_pipeline.py
class TestCodegenRuntimeGapFixes:
    def test_design_params_json_populated(self, tmp_path, chain_spike_model_path):
        # Run full codegen, verify JSON has >= 3 populated numeric values

    def test_custom_schema_types_includes_exit_point_types(self, tmp_path, chain_spike_model_path):
        # Run full codegen, verify __init__.py has Float in CUSTOM_SCHEMA_TYPES

    def test_no_fusion_params_schema(self, tmp_path, chain_spike_model_path):
        # Run full codegen, verify no FusionParams anywhere in output
```

### Changes Required

**See `design.md#component-6` for:** Integration test code (6b)

**Specific file changes:**

#### 1. Add E2E test class
**File:** `tests/integration/test_full_pipeline.py`
- [ ] Add `TestCodegenRuntimeGapFixes` class with 5 tests from `design.md#component-6` (6b)
- [ ] `test_design_params_json_populated` (AC-1)
- [ ] `test_custom_schema_types_includes_exit_point_types` (AC-3)
- [ ] `test_no_fusion_params_schema` (AC-5)
- [ ] `test_design_path_filter_cli_flag` (FR-4)
- [ ] `test_generation_config_has_design_path_filter` (FR-4)

### Validation

**Automated:**
- [ ] `uv run pytest tests/ -v` → ALL tests pass (AC-7, AC-8, AC-9)
- [ ] `uv run mypy src/` → passes (AC-10)
- [ ] `uv run ruff check src/` → passes (AC-11)

**Manual:**
- [ ] Run codegen on chain spike model from fusion-tea repo (see `design.md#validation-approach` for commands)
- [ ] Verify `design_params.json` has 3 populated entries (AC-1)
- [ ] Verify `__init__.py` has `Float` in `CUSTOM_SCHEMA_TYPES` (AC-3)
- [ ] Verify no `FusionParams` in output (AC-5)

**What We Know Works After This Phase:**
- All 11 acceptance criteria verified
- Full codegen output is TEAx-executable without manual intervention
- Items 4-5 of the derisking epic are unblocked

---

## Environment Setup

**See CLAUDE.md for full environment rules**

```bash
# Install dependencies
uv pip install -e ~/agentic-mbse && uv pip install -e ".[dev]"

# Run tests
uv run pytest tests/

# Type check
uv run mypy src/

# Lint
uv run ruff check src/
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Gap 3 removal is zero-risk — file is unused. Verify with existing test suite.
- **Phase 2**: Path filter change is more permissive (not restrictive), so backward compatible. Crash guard is pure error handling.
- **Phase 3**: Template change is additive — `exit_point_types=[]` produces identical output to before. Unit tests verify both with and without.
- **Phase 4**: Integration tests use `pytest.skip()` pattern if syside can't load models.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION - Leave empty now]

### Phase 1 Completion
**Completed:** 2026-02-01
**Actual Changes:**
- Created `tests/fixtures/chain_spike_model/` with `library.sysml` and `design.sysml`
- Added `chain_spike_model_path` fixture to `tests/conftest.py`
- Deleted `src/sysml_codegen/templates/schemas_ref.py`
- Removed `ref_schema` copy block from `_generate_schemas()` in `cli/__init__.py:127-143`
- Updated `test_generates_schemas` to assert `not ref_schema.exists()`
**Issues:** None
**Deviations:** None

### Phase 2 Completion
**Completed:** 2026-02-01
**Actual Changes:**
- Changed `design_path_filter` default from `"models/designs"` to `""` in `parameter_groups.py:89`
- Added try/except crash guard around `evaluate_true_static_expression()` in `parameter_groups.py:186-189`
- Added `design_path_filter: str = ""` param to `build_pipeline_context()` in `initialization.py`
- Passed `design_path_filter` to `extract_design_attributes()` call at `initialization.py:140`
- Added `design_path_filter: str = ""` to `GenerationConfig` dataclass
- Added `--design-path-filter` CLI argument to `gen_parser`
- Wired `design_path_filter` through `cmd_generate()` and `run_codegen()`
- Created `tests/unit/test_parameter_groups.py` with 5 tests
**Issues:** None
**Deviations:** None

### Phase 3 Completion
**Completed:** 2026-02-01
**Actual Changes:**
- Added `_collect_exit_point_primitive_types()` function to `registry.py`
- Added `exit_point_primitive_types` param to `generate_registry_function()`
- Added `package_name` and `exit_point_types` to template context dict
- Updated `registry_function.py.jinja2` with primitives import block, expanded `CUSTOM_SCHEMA_TYPES` condition, trailing commas
- Wired `_collect_exit_point_primitive_types` through `_generate_registry()` in `cli/__init__.py`
- Created `tests/unit/test_registry_generation.py` with 5 tests
- Fixed ruff N806 violation (renamed `TYPE_MAP` to `type_map`)
**Issues:** None
**Deviations:** Minor — renamed `TYPE_MAP` to `type_map` to satisfy ruff N806

### Phase 4 Completion
**Completed:** 2026-02-01
**Actual Changes:**
- Added `TestCodegenRuntimeGapFixes` class to `tests/integration/test_full_pipeline.py` with 5 tests
- All 42 tests pass, mypy and ruff clean (no new issues)
**Issues:** None
**Deviations:** None

---

**Status**: Complete
