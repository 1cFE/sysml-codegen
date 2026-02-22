# Implementation Plan: Pipeline Integration -- CalcDef Expression Compilation

**Status:** Draft
**Created:** 2026-02-07
**Last Updated:** 2026-02-07

## Source Documents
- **Spec:** `.project/active/expr-pipeline-integration/spec.md`
- **Design:** `.project/active/expr-pipeline-integration/design.md` -- See here for component details, function signatures, dependencies, architecture

## Implementation Strategy

**Phasing Rationale:**
The 4-phase plan follows data-flow order (producers before consumers) with zero-risk model additions first. Phase 1 adds all new fields with defaults so nothing breaks. Phase 2 populates those fields during extraction. Phase 3 wires compilation into orchestration/resolution. Phase 4 consumes everything in the generation layer. Each phase is independently testable and produces verifiable output.

**Overall Validation Approach:**
- Each phase starts with tests
- `uv run pytest tests/` after every phase (zero regressions)
- `uv run mypy src/` and `uv run ruff check src/` at each phase boundary

---

## Phase 1: Data Model Foundations

### Goal
Add all new fields to `CalculationDefinitionData`, `BindingInfo`, `PipelineModule`, and `PipelineContext`. Every field has a default, so existing code and tests are unaffected. This is the foundation every other phase depends on.

### Test Stencil (Write This First)
```python
# tests/unit/test_data_models.py -- extend existing test file

def test_calculation_definition_data_has_expression_ast_fields():
    """New fields exist with correct defaults (backward compat)."""
    from sysml_codegen.extraction.data_models import CalculationDefinitionData
    cd = CalculationDefinitionData(
        name="Test", qualified_name="Test", doc_comment="",
        calc_expressions=[], input_attributes=[], output_attributes=[],
        references=[], source_file=Path("test.sysml"),
    )
    assert cd.output_expression_asts == {}
    assert cd.all_member_names == set()
    assert cd.member_expressions == {}

def test_binding_info_has_expression_ast_field():
    from sysml_codegen.extraction.usage_extractor import BindingInfo
    from agentic_mbse.sysml.types import BindingType
    bi = BindingInfo(param_name="x", source_path=None, binding_type=BindingType.UNBOUND)
    assert bi.expression_ast is None

def test_pipeline_module_has_compilability_field():
    from sysml_codegen.resolution.models import PipelineModule
    from sysml_codegen.extraction.expression_compiler import Compilability
    m = PipelineModule(name="t", module_type="T", inputs=[], outputs=[], execution_order=0)
    assert m.compilability == Compilability.UNKNOWN
```

### Changes Required

**See `design.md` for:**
- Field definitions and rationale --> `design.md#component-1-extraction-layer-changes` (1A)
- BindingInfo field --> `design.md#1d-fix-operatorexpression-binding-classification`
- PipelineModule field --> `design.md#component-3-resolution-layer-changes` (3A)
- PipelineContext field --> `design.md#component-2-pipeline-orchestration-step-65` (2B)

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_data_models.py` (EXTEND)
- [x] Add tests for 3 new `CalculationDefinitionData` fields with defaults
- [x] Add test for `BindingInfo.expression_ast` default
- [x] Add test for `PipelineModule.compilability` default

#### 2. `CalculationDefinitionData`
**File:** `src/sysml_codegen/extraction/data_models.py:135` (after `source_hash`)
- [x] Add `output_expression_asts: dict[str, Any] = field(default_factory=dict)`
- [x] Add `all_member_names: set[str] = field(default_factory=set)`
- [x] Add `member_expressions: dict[str, Any] = field(default_factory=dict)`
- [x] Add `from typing import Any` import (already present)

#### 3. `BindingInfo`
**File:** `src/sysml_codegen/extraction/usage_extractor.py:66` (after `literal_value`)
- [x] Add `expression_ast: Any = None`
- [x] Add `from typing import Any` import (already present)

#### 4. `PipelineModule`
**File:** `src/sysml_codegen/resolution/models.py:165` (after `execution_order`)
- [x] Add `compilability: Compilability = Compilability.UNKNOWN`
- [x] Add `from sysml_codegen.extraction.expression_compiler import Compilability` import

#### 5. `PipelineContext`
**File:** `src/sysml_codegen/generation/initialization.py:79` (after `computation_graph`)
- [x] Add `compilation_results: dict[str, CalcDefCompilationResult] = field(default_factory=dict)`
- [x] Add `from sysml_codegen.extraction.expression_compiler import CalcDefCompilationResult` import

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/` --> All 112 pass (including 3 new tests)
- [x] `uv run mypy src/` --> No new errors (pre-existing only)
- [x] `uv run ruff check src/` --> No new errors (pre-existing only)

**Manual:**
- [x] Inspect each modified file: confirm new fields have defaults, imports are clean

**What We Know Works After This Phase:**
All data models have the new fields with backward-compatible defaults. Zero behavioral change. Every downstream phase can reference these fields.

---

## Phase 2: Extraction Layer -- AST Capture, Expression Text, OperatorExpression Fix

### Goal
Populate the new fields during extraction: capture raw ASTs for outputs and members, replace `_extract_expression_text()` with `expression_utils.reconstruct_expression()`, fix OperatorExpression classification. These are the data producers that Phase 3 and 4 consume.

### Test Stencil (Write This First)
```python
# tests/unit/test_extractor.py -- extend

def test_extract_expression_text_replaced_by_reconstruct_expression():
    """calc_expressions text populated via expression_utils, not legacy method."""
    # Use a mock CalcDef element with known OperatorExpression on an output
    # Verify calc_expressions contains the reconstructed text string

def test_output_expression_asts_captured():
    """output_expression_asts populated for outputs with feature_value_expression."""
    # Mock element with output attribute having feature_value_expression
    # Verify output_expression_asts[attr_name] == raw AST node

def test_all_member_names_captured():
    """all_member_names includes inputs, outputs, AND intermediates."""
    # Mock element with 3 AttributeUsage members (1 in, 1 out, 1 undeclared)
    # Verify all 3 names in all_member_names

def test_member_expressions_captured_for_non_io():
    """member_expressions populated for non-input/non-output members with expressions."""

# tests/unit/test_usage_extractor.py or test_extractor.py -- new test class

def test_operator_expression_classified_as_expression():
    """OperatorExpression binding → BindingType.EXPRESSION, not UNBOUND."""
    # Mock param_elem with OperatorExpression feature_value_expression
    # Call _extract_single_binding()
    # Assert binding_type == BindingType.EXPRESSION
    # Assert expression_ast is the raw expr

def test_operator_expression_stores_ast():
    """OperatorExpression binding stores raw AST on BindingInfo."""
```

### Changes Required

**See `design.md` for:**
- AST capture logic --> `design.md#1b-modify-_extract_calculation_definition-to-capture-asts`
- Expression text replacement --> `design.md#1c-replace-_extract_expression_text-with-expression_utilsreconstruct_expression`
- OperatorExpression fix --> `design.md#1d-fix-operatorexpression-binding-classification`
- Dead code removal rationale --> `design.md` DD-3

**Specific file changes:**

#### 1. Test Files
**File:** `tests/unit/test_extractor.py` (EXTEND)
- [x] Add test for `_extract_expression_text()` removal (ensure no callers remain)
- [x] Add test for `reconstruct_expression` import presence
- [x] Add test for OperatorExpression → `BindingType.EXPRESSION` classification
- [x] Add test for `expression_ast` stored on `BindingInfo`
- Note: AST capture field tests (output_expression_asts, all_member_names, member_expressions) require full syside model mocking; validated structurally via Phase 1 tests and integration tests

#### 2. AST Capture in `_extract_calculation_definition()`
**File:** `src/sysml_codegen/extraction/extractor.py:127-191`
- [x] In first `owned_members` loop: collect `all_member_names` for every `AttributeUsage`
- [x] In first loop: for output attributes with `feature_value_expression`, store AST in `output_expression_asts`
- [x] Second pass: for non-input/non-output members with `feature_value_expression`, store in `member_expressions`
- [x] Pass new fields to `CalculationDefinitionData()` constructor

#### 3. Replace `_extract_expression_text()`
**File:** `src/sysml_codegen/extraction/extractor.py`
- [x] Replace `self._extract_expression_text(expr)` call with `reconstruct_expression(expr)` from `expression_utils`
- [x] Change filter from `expr_text != "???"` to `not expr_text.startswith("<")` (DD-4)
- [x] Add `logger.debug()` for filtered repr-like strings
- [x] Add import: `from sysml_codegen.extraction.expression_utils import reconstruct_expression`

#### 4. Delete `_extract_expression_text()`
**File:** `src/sysml_codegen/extraction/extractor.py`
- [x] Delete the entire `_extract_expression_text()` method (DD-3: dead code removal)

#### 5. OperatorExpression Fix
**File:** `src/sysml_codegen/extraction/usage_extractor.py:330`
- [x] Add `elif SysideAdapter.is_instance(expr, "OperatorExpression")` branch before fallthrough
- [x] Return `BindingInfo` with `binding_type=BindingType.EXPRESSION`, `expression_ast=expr`

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/` --> All 116 pass (4 new tests)
- [x] `uv run mypy src/` --> No new errors (pre-existing only)
- [x] `uv run ruff check src/` --> No new errors (pre-existing only)

**Manual:**
- [x] Verify `_extract_expression_text` method is fully deleted
- [x] Grep for any remaining calls to `_extract_expression_text` -- zero results in src/

**What We Know Works After This Phase:**
Extraction captures raw ASTs, expression text uses shared utilities, OperatorExpression is correctly classified. All data for the expression compiler is available on `CalculationDefinitionData`.

---

## Phase 3: Pipeline Orchestration + Resolution (Step 6.5 + Graph Builder)

### Goal
Add Step 6.5 in `build_pipeline_context()` that compiles expressions via `compile_calc_def()`. Pass `compilation_results` to `build_computation_graph()` which sets `PipelineModule.compilability`. This is the bridge between extraction and generation.

### Test Stencil (Write This First)
```python
# tests/unit/test_graph_builder.py or extend existing tests

def test_compilation_results_set_module_compilability():
    """build_computation_graph sets compilability from compilation_results."""
    from sysml_codegen.extraction.expression_compiler import (
        CalcDefCompilationResult, Compilability,
    )
    # Build a minimal BacktrackingResult + calc_defs
    # Provide compilation_results with FULLY_COMPILABLE for one CalcDef
    # Call build_computation_graph(... compilation_results=compilation_results)
    # Assert module.compilability == Compilability.FULLY_COMPILABLE

def test_compilation_results_none_leaves_unknown():
    """Without compilation_results, modules stay UNKNOWN (backward compat)."""

def test_step_6_5_populates_compilation_results():
    """PipelineContext.compilation_results populated for CalcDefs with ASTs."""
    # Requires mock model or minimal integration test
```

### Changes Required

**See `design.md` for:**
- Step 6.5 logic --> `design.md#2a-add-step-65-to-build_pipeline_context`
- PipelineContext field --> `design.md#2b-add-compilation_results-to-pipelinecontext`
- Graph builder parameter --> `design.md#2c-pass-compilation_results-to-graph-builder`
- Compilability assignment --> `design.md#3b-set-compilability-in-build_computation_graph`
- Key invariant (name keying) --> `design.md#3b-set-compilability-in-build_computation_graph`

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_graph_builder.py` (NEW or extend existing)
- [x] Test: `compilation_results` sets `PipelineModule.compilability`
- [x] Test: `compilation_results=None` leaves `UNKNOWN` (backward compat)
- [x] Test: `MANUAL_REQUIRED` propagates correctly

#### 2. Graph Builder
**File:** `src/sysml_codegen/resolution/graph_builder.py:49-54`
- [x] Add `compilation_results: dict | None = None` parameter to `build_computation_graph()`
- [x] In Step 5 loop, after `_build_pipeline_module()`: set `module.compilability` from `compilation_results[usage.calc_def_name].overall_compilability`
- [x] Guard with `if compilation_results and usage.calc_def_name in compilation_results`

#### 3. Pipeline Orchestration
**File:** `src/sysml_codegen/generation/initialization.py`
- [x] Between Step 6 and Step 7: insert Step 6.5 compilation loop
- [x] Import `compile_calc_def` and `CalcDefCompilationResult` from `expression_compiler`
- [x] Iterate `calc_defs`, call `compile_calc_def()` for those with `output_expression_asts`
- [x] Store results in `compilation_results` dict keyed by `calc_def.name`
- [x] Pass `compilation_results=compilation_results` to `build_computation_graph()`
- [x] Pass `compilation_results=compilation_results` to `PipelineContext()` constructor

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/` --> All 119 pass (3 new graph builder tests)
- [x] `uv run mypy src/` --> No new errors (pre-existing only)
- [x] `uv run ruff check src/` --> No new errors (pre-existing only)

**Manual:**
- [x] Verify `build_computation_graph()` signature includes `compilation_results` param with default
- [x] Verify Step 6.5 placement: after backtracker, before graph builder

**What We Know Works After This Phase:**
Expression compilation runs at Step 6.5, results flow through to `PipelineModule.compilability`. The full extraction→compilation→resolution data path is functional. Only generation remains.

---

## Phase 4: Generation -- Auto-Impl Template + Unified Dispatch + CLI + Backlog Report

### Goal
Create the auto-implementation Jinja2 template. Add `generate_implementation()` to `stencils.py` with internal template dispatch. Update CLI to call the unified function. Update backlog report to exclude auto-implemented CalcDefs. This completes the end-to-end feature.

### Test Stencil (Write This First)
```python
# tests/unit/test_stencils.py (NEW)

def test_auto_impl_template_produces_valid_python():
    """Auto-impl template output passes ast.parse()."""
    import ast
    from sysml_codegen.generation.stencils import generate_implementation
    # Setup: FULLY_COMPILABLE CalcDefCompilationResult with known expressions
    # Call generate_implementation(calc_def, template_env, path, pkg, compilation_result)
    code = generate_implementation(...)
    ast.parse(code)  # Must not raise SyntaxError
    assert "AUTO_IMPLEMENTED = True" in code

def test_stub_template_used_for_manual_required():
    """MANUAL_REQUIRED falls through to NotImplementedError stub."""
    code = generate_implementation(..., compilation_result=manual_result)
    assert "NotImplementedError" in code

def test_stub_template_used_when_no_compilation_result():
    """None compilation_result → stub template."""
    code = generate_implementation(..., compilation_result=None)
    assert "NotImplementedError" in code

def test_partially_compilable_falls_through_to_stub():
    """FR-12: PARTIALLY_COMPILABLE gets stub, not auto-impl."""
    code = generate_implementation(..., compilation_result=partial_result)
    assert "NotImplementedError" in code

def test_auto_impl_same_function_signature_as_stub():
    """Auto-impl and stub produce identical function signatures for preservation."""
    auto_code = generate_implementation(..., compilation_result=compilable_result)
    stub_code = generate_implementation(..., compilation_result=None)
    # Extract function signature lines -- must match

def test_backlog_report_excludes_fully_compilable():
    """generate_backlog_report skips FULLY_COMPILABLE CalcDefs."""
```

### Changes Required

**See `design.md` for:**
- Template structure --> `design.md#4a-new-auto-implementation-template`
- Unified dispatch function --> `design.md#4b-unified-generation-function-with-internal-dispatch`
- CLI integration --> `design.md#4c-cli-calls-unified-generation-function`
- Backlog report update --> `design.md#4d-update-backlog-report-to-exclude-auto-implemented-calcdefs`
- Preservation verification --> `design.md#component-5-preservation-verification`

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_stencils.py` (NEW)
- [x] Test auto-impl template produces valid Python (`ast.parse()`)
- [x] Test auto-impl has `AUTO_IMPLEMENTED = True` sentinel
- [x] Test stub used for `MANUAL_REQUIRED`, `UNKNOWN`, `None`
- [x] Test `PARTIALLY_COMPILABLE` falls through to stub (FR-12)
- [x] Test auto-impl and stub share identical function signatures
- [x] Test backlog report excludes `FULLY_COMPILABLE` CalcDefs

#### 2. Auto-Implementation Template
**File:** `src/sysml_codegen/templates/auto_implementation.py.jinja2` (NEW)
- [x] Create template per `design.md#4a`
- [x] Same function signature pattern as `implementation_stencil.py.jinja2`
- [x] Module-level `AUTO_IMPLEMENTED = True` constant
- [x] Undeclared intermediates as local variables in topological order
- [x] Single-output: bare `return expr`; multi-output: `return (expr1, expr2, ...)`

#### 3. Unified Dispatch in `stencils.py`
**File:** `src/sysml_codegen/generation/stencils.py`
- [x] Add `generate_implementation()` function per `design.md#4b`
- [x] Extract `_build_stencil_context()` from existing `generate_implementation_stencil()` body
- [x] Add `_build_auto_impl_context()` for execution_steps, output_count, single_output_expression
- [x] Import `CalcDefCompilationResult`, `Compilability` from `expression_compiler`
- [x] Preserve existing `generate_implementation_stencil()` (refactored to use `_build_stencil_context()`)

#### 4. CLI Integration
**File:** `src/sysml_codegen/cli/__init__.py:206-284`
- [x] Import `generate_implementation` from `stencils`
- [x] In `_generate_stencils()`: look up `ctx.compilation_results.get(calc_def.name)` for each CalcDef
- [x] Replace `generate_implementation_stencil()` calls with `generate_implementation()` passing `compilation_result`
- [x] All 3 code paths (smart-regen regenerate, fresh, non-smart-regen) use the unified function

#### 5. Backlog Report Update
**File:** `src/sysml_codegen/generation/stencils.py:188`
- [x] Add `compilation_results: dict | None = None` parameter to `generate_backlog_report()`
- [x] Skip CalcDefs whose compilation result is `FULLY_COMPILABLE` in items loop
- [x] Update CLI caller to pass `compilation_results=ctx.compilation_results`

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/` --> All 129 pass (10 new + 119 existing)
- [x] `uv run mypy src/` --> No new errors (pre-existing only)
- [x] `uv run ruff check src/` --> No new errors (pre-existing only)

**Manual:**
- [ ] Run codegen on chain_spike model if available: verify `_impl.py` files contain actual code, not `NotImplementedError`
- [ ] Verify auto-impl files contain `AUTO_IMPLEMENTED = True`
- [ ] Verify non-compilable CalcDefs still produce stub files
- [ ] Verify backlog report no longer lists auto-implemented CalcDefs

**What We Know Works After This Phase:**
End-to-end: extraction captures ASTs → Step 6.5 compiles → resolution tags compilability → generation dispatches to auto-impl or stub. All success criteria from the spec are met.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

```bash
uv run pytest tests/      # Run all tests
uv run mypy src/          # Type check
uv run ruff check src/    # Lint
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Zero risk -- all fields have defaults, purely additive
- **Phase 2**: `_extract_expression_text()` replacement must be output-equivalent. Test by comparing `calc_expressions` before/after on known inputs. The `startswith("<")` filter (DD-4) prevents garbage output.
- **Phase 3**: `compile_calc_def()` is already well-tested (Item 3). Step 6.5 is a straightforward loop. Guard with `if calc_def.output_expression_asts` to skip CalcDefs without ASTs.
- **Phase 4**: Template produces syntactically valid Python -- validated by `ast.parse()` in tests. Function signatures match stub template -- tested by signature comparison.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-02-07
**Actual Changes:**
- Modified `src/sysml_codegen/extraction/data_models.py:135`: Added `output_expression_asts`, `all_member_names`, `member_expressions` fields with `field(default_factory=...)` defaults. `Any` import was already present.
- Modified `src/sysml_codegen/extraction/usage_extractor.py:66`: Added `expression_ast: Any = None` to `BindingInfo`. `Any` import was already present.
- Modified `src/sysml_codegen/resolution/models.py:165`: Added `compilability: Compilability = Compilability.UNKNOWN` to `PipelineModule`. Added import of `Compilability` from `expression_compiler`.
- Modified `src/sysml_codegen/generation/initialization.py:79`: Added `compilation_results: dict[str, CalcDefCompilationResult] = field(default_factory=dict)` to `PipelineContext`. Added import of `CalcDefCompilationResult` from `expression_compiler`. Changed `dataclass` import to include `field`.
- Extended `tests/unit/test_data_models.py`: Added 3 tests: `test_calculation_definition_data_has_expression_ast_fields`, `test_binding_info_has_expression_ast_field`, `test_pipeline_module_has_compilability_field`.

**Issues:** None. All 112 tests pass. mypy and ruff show only pre-existing errors (no new errors introduced).
**Deviations:** None. Implementation matches plan exactly.

### Phase 2 Completion
**Completed:** 2026-02-07
**Actual Changes:**
- Modified `src/sysml_codegen/extraction/extractor.py`: Rewrote `_extract_calculation_definition()` to capture `all_member_names`, `output_expression_asts`, `member_expressions` during owned_members iteration. Replaced `_extract_expression_text(expr)` with `reconstruct_expression(expr)`. Changed filter from `!= "???"` to `not startswith("<")` (DD-4). Added `logger.debug()` for filtered repr-like strings. Deleted `_extract_expression_text()` method entirely (DD-3). Added import of `reconstruct_expression` from `expression_utils`.
- Modified `src/sysml_codegen/extraction/usage_extractor.py:330`: Added `elif SysideAdapter.is_instance(expr, "OperatorExpression")` branch returning `BindingInfo` with `BindingType.EXPRESSION` and `expression_ast=expr`.
- Extended `tests/unit/test_extractor.py`: Added 4 tests: `test_extract_expression_text_deleted`, `test_extractor_imports_reconstruct_expression`, `test_operator_expression_classified_as_expression`, `test_operator_expression_stores_ast`.

**Issues:** None. All 116 tests pass. No new mypy/ruff errors.
**Deviations:** `member_expressions` capture uses a second pass over `owned_members` rather than being integrated in the first loop. This is because we need `input_names` and `output_names` to be fully built before determining which members are "non-input/non-output". The design said "no new iteration needed" but the second pass is cleaner than trying to retroactively classify members. Performance impact is negligible (the owned_members list is small).

### Phase 3 Completion
**Completed:** 2026-02-07
**Actual Changes:**
- Modified `src/sysml_codegen/resolution/graph_builder.py`: Added `compilation_results: dict | None = None` parameter to `build_computation_graph()`. In Step 5 module-building loop, after `_build_pipeline_module()`, set `module.compilability` from compilation results with guard.
- Modified `src/sysml_codegen/generation/initialization.py`: Added Step 6.5 compilation loop between Steps 6 and 7. Iterates `calc_defs`, calls `compile_calc_def()` for those with `output_expression_asts`. Passes `compilation_results` to both `build_computation_graph()` and `PipelineContext()`. Added `compile_calc_def` import.
- Created `tests/unit/test_graph_builder.py`: 3 tests with shared `_make_minimal_graph_inputs()` fixture -- tests UNKNOWN default, FULLY_COMPILABLE propagation, and MANUAL_REQUIRED propagation.

**Issues:** BacktrackingResult requires `_ensure_backtracking_result_rebuilt()` call before construction due to Pydantic forward-ref resolution. Used the existing helper function.
**Deviations:** None. Implementation matches plan exactly.

### Phase 4 Completion
**Completed:** 2026-02-07
**Actual Changes:**
- Created `src/sysml_codegen/templates/auto_implementation.py.jinja2`: New Jinja2 template with `AUTO_IMPLEMENTED = True` sentinel, undeclared intermediate local variable assignments, single-output bare return, and multi-output tuple return. Same function signature as stub template for preservation compatibility.
- Rewrote `src/sysml_codegen/generation/stencils.py`: Extracted `_build_stencil_context()` from existing `generate_implementation_stencil()` body. Added `_build_auto_impl_context()` for execution_steps (intermediates in topological order) and output_expressions (in output_attributes order). Added `generate_implementation()` as unified entry point with internal template dispatch. Refactored `generate_implementation_stencil()` to use `_build_stencil_context()`. Updated `generate_backlog_report()` to accept `compilation_results` and skip `FULLY_COMPILABLE` CalcDefs. Added imports of `CalcDefCompilationResult` and `Compilability`.
- Modified `src/sysml_codegen/cli/__init__.py`: Updated `_generate_stencils()` to import and use `generate_implementation` instead of `generate_implementation_stencil`. Added compilation_result lookup via `ctx.compilation_results.get(calc_def.name)`. Both smart-regen and fresh code paths use the unified function. Updated `_generate_backlog()` to pass `compilation_results=ctx.compilation_results`.
- Modified `src/sysml_codegen/generation/__init__.py`: Added `generate_implementation` to imports and `__all__`.
- Created `tests/unit/test_stencils.py`: 10 tests covering auto-impl valid Python, sentinel, return expression, stub for MANUAL_REQUIRED/None/PARTIALLY_COMPILABLE, function signature preservation, backlog report filtering, undeclared intermediates, and multi-output tuple return.

**Issues:** mypy flagged `CalcDefCompilationResult | None` passed to `_build_auto_impl_context()` which expects non-None. Fixed with an assert for type narrowing after the `is_auto_impl` guard.
**Deviations:**
- Template uses separate `execution_steps` (intermediates only) and `output_expressions` (declared outputs only) instead of a single `execution_steps` list with `is_undeclared_intermediate` filtering as specified in the design. This is cleaner in the template (no conditional checks) and ensures declared outputs in the return tuple follow `output_attributes` order (important for multi-output positional unpacking in TEAx module wrappers). Semantically equivalent behavior.

---

**Status**: Complete
