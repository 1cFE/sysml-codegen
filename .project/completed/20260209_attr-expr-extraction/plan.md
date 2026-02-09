# Implementation Plan: Computed Attribute Extraction & Data Models

**Status:** Complete
**Created:** 2026-02-08
**Last Updated:** 2026-02-08

## Source Documents
- **Spec:** `.project/active/attr-expr-extraction/spec.md`
- **Design:** `.project/active/attr-expr-extraction/design.md` ← See here for component details, function signatures, classification algorithm, worked examples

## Implementation Strategy

**Phasing Rationale:**
Phase 1 lays foundation types (zero risk, pure additive). Phase 2 tackles the riskiest piece — qualified-name classification — early, with full mock infrastructure and 6 targeted tests. Phase 3 adds compilation (reusing proven Phase 1 compiler) and the end-to-end integration test. Each phase is independently verifiable and builds on the previous.

**Overall Validation Approach:**
- Each phase starts with tests
- Each phase ends with `uv run pytest tests/` (full regression) + `uv run mypy src/`
- No existing code is modified except `data_models.py` (additive only)

---

## Phase 1: Data Models + Enum Tests

### Goal
Add `ComputedAttributeClassification` enum and `ComputedAttributeData` dataclass to `data_models.py`. Write data model tests. This is pure additive — zero risk to existing code.

### Test Stencil (Write This First)
```python
# tests/unit/test_computed_attribute_extraction.py

class TestComputedAttributeClassification:
    def test_all_values_exist(self):
        assert set(ComputedAttributeClassification) == {
            ComputedAttributeClassification.FORMULA,
            ComputedAttributeClassification.EXPOSE_PURE,
            ComputedAttributeClassification.EXPOSE_COMPUTED,
            ComputedAttributeClassification.LITERAL,
            ComputedAttributeClassification.UNRESOLVABLE,
        }

    def test_string_inheritance(self):
        assert ComputedAttributeClassification.FORMULA == "formula"

class TestComputedAttributeData:
    def test_construction_all_fields(self):
        data = ComputedAttributeData(
            name="area", python_name="area", owning_part_name="part",
            owning_part_qualified_name="Pkg::Part",
            expression_ast=None, expression_text="length * width",
            references=[], classification=ComputedAttributeClassification.FORMULA,
            compilability=Compilability.FULLY_COMPILABLE,
        )
        assert data.compiled_expression is None  # default
        assert data.source_line == 0             # default

    def test_defaults(self):
        # compiled_expression=None, source_file=Path("unknown"), source_line=0
        ...
```

### Changes Required

**See `design.md#component-1-data-models` for:** enum values, dataclass fields, `__all__` update pattern

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_computed_attribute_extraction.py` (NEW — write first)
- [x] Create test file with imports
- [x] Implement `TestComputedAttributeClassification` (2 tests: values exist, string inheritance)
- [x] Implement `TestComputedAttributeData` (2 tests: full construction, defaults)

#### 2. Data Models
**File:** `src/sysml_codegen/extraction/data_models.py` (MODIFY)
- [x] Add `from enum import Enum` import
- [x] Add `ExpressionRef` import from `agentic_mbse.sysml.types`
- [x] Add `Compilability` import from `.expression_compiler`
- [x] Add `ComputedAttributeClassification(str, Enum)` with 5 values (see `design.md#computedattributeclassification`)
- [x] Add `ComputedAttributeData` dataclass with 13 fields (see `design.md#computedattributedata`)
- [x] Update `__all__` to include both new types

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_computed_attribute_extraction.py -v` → 4 tests pass
- [x] `uv run pytest tests/ --tb=short` → All 171 tests pass (171, not 167 — 4 new)
- [x] `uv run mypy src/sysml_codegen/extraction/data_models.py` → Clean (with --ignore-missing-imports; agentic_mbse untyped stubs are pre-existing)

**What We Know Works After This Phase:**
New types import correctly. `ExpressionRef` and `Compilability` cross-module imports work. `__all__` exports are correct. Zero regressions.

---

## Phase 2: Classification Logic + Core Tests (Riskiest)

### Goal
Implement `_classify_attribute_expression()` and the mock infrastructure. Test all 5 classification categories plus the qualified-name collision regression test. This is the novel algorithm — de-risking it early is critical.

### Test Stencil (Write This First)
```python
# Add to tests/unit/test_computed_attribute_extraction.py

class TestClassifyAttributeExpression:
    def test_formula_simple_binary(self, mock_syside_adapter, monkeypatch):
        """area = length * width → FORMULA"""
        expr = MockOperatorExpression("*", [
            MockFeatureReferenceExpression("length"),
            MockFeatureReferenceExpression("width"),
        ])
        # Mock extract_feature_refs to return sibling refs
        # Assert: classification == FORMULA

    def test_expose_pure(self, mock_syside_adapter, monkeypatch):
        """p_alpha_out = alpha_split.p_alpha → EXPOSE_PURE"""
        expr = MockFeatureChainExpression()
        # Refs: calc_ref (p_alpha from Library ns) + filtered calc_usage ref
        # Assert: classification == EXPOSE_PURE

    def test_qualified_name_collision(self, mock_syside_adapter, monkeypatch):
        """p_alpha ref with CalcDef QN, sibling also named p_alpha → calc_ref, not sibling"""
        # Regression test for 19-CATF bug
        # Assert: classified as EXPOSE, not FORMULA
```

### Changes Required

**See `design.md#component-2-extraction-module` for:** function signatures, classification algorithm (steps 1-3), worked examples, EXPOSE_PURE vs EXPOSE_COMPUTED distinction

**See `design.md#component-3-unit-tests` for:** mock classes, TYPE_MAP extension, `extract_feature_refs` monkeypatch pattern

**Specific file changes:**

#### 1. Test Infrastructure + Classification Tests
**File:** `tests/unit/test_computed_attribute_extraction.py` (MODIFY — add to Phase 1 file)
- [x] Add mock classes: `MockAttributeUsage`, `MockCalculationUsage`, `MockPartElement` (see `design.md#mock-infrastructure`)
- [x] Duplicate expression mocks: `MockOperatorExpression`, `MockFeatureReferenceExpression`, `MockLiteralRational`, `MockFeatureChainExpression`
- [x] Add `mock_syside_adapter` fixture with extended TYPE_MAP (see `design.md#mock-infrastructure`)
- [x] Add `_make_refs` helper for creating ExpressionRef objects (design called for monkeypatch of extract_feature_refs; direct ref construction was simpler — see deviations)
- [x] Implement `TestClassifyAttributeExpression` with 6 tests:
  - `test_expose_pure` (test case 4 in design)
  - `test_expose_computed` (test case 5)
  - `test_literal_no_refs` (test case 6)
  - `test_unresolvable` (test case 7)
  - `test_qualified_name_collision` (test case 8 — CATF regression)
  - `test_formula_simple` (classification only, not compilation)

#### 2. Classification Implementation
**File:** `src/sysml_codegen/extraction/computed_attribute_extractor.py` (NEW)
- [x] Create file with imports (`SysideAdapter`, `extract_feature_refs`, `ExpressionRef`, data models, `_sanitize_name`, `reconstruct_expression`)
- [x] Implement `_classify_attribute_expression()` per `design.md#internal-classification-function`
- [x] Implement skeleton of `extract_computed_attributes()` — enough to call classification and return results (compilation stubbed as `compiled_expression=None`, `compilability=Compilability.MANUAL_REQUIRED` for now)
- [x] Add logging per `design.md#logging`

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_computed_attribute_extraction.py -v` → 10 tests pass (4 Phase 1 + 6 Phase 2)
- [x] `uv run pytest tests/ --tb=short` → 177 passed (full regression green)
- [x] `uv run mypy src/sysml_codegen/extraction/computed_attribute_extractor.py` → Clean (--ignore-missing-imports)

**Manual:**
- [x] Verify `test_qualified_name_collision` specifically passes — confirmed

**What We Know Works After This Phase:**
All 5 classification categories correctly identified. Qualified-name resolution handles the FeatureChainExpression two-ref pattern. CalcUsage instance refs are correctly filtered (step 2a). QN collision bug is prevented. Mock infrastructure is proven.

---

## Phase 3: Compilation + Full Integration Test

### Goal
Wire FORMULA compilation into `extract_computed_attributes()` using `build_expression_ast` + `compile_expression`. Add the 3 FORMULA compilation tests and the `TestExtractComputedAttributes` integration test. This completes the feature.

### Test Stencil (Write This First)
```python
class TestClassifyAttributeExpression:
    # Add to existing class:
    def test_formula_simple_binary(self, mock_syside_adapter, monkeypatch):
        """area = length * width → compiled to (inputs.length * inputs.width)"""
        # Full end-to-end: classification + compilation
        # Assert: compiled_expression == "(inputs.length * inputs.width)"
        # Assert: compilability == FULLY_COMPILABLE

    def test_formula_complex_nested(self, mock_syside_adapter, monkeypatch):
        """p_blanket = m_n * p_f + p_in + eta * ... → correct nested compilation"""
        # Build nested MockOperatorExpression tree
        # Assert: compiled expression matches expected

class TestExtractComputedAttributes:
    def test_mixed_part_element(self, mock_syside_adapter, monkeypatch):
        """Part with FORMULA + LITERAL + EXPOSE attrs → correct filtering and count"""
        part = MockPartElement("test_part", [
            MockAttributeUsage("area", expr=..., ),    # FORMULA
            MockAttributeUsage("length", expr=literal), # LITERAL → excluded
            MockAttributeUsage("out", expr=chain),       # EXPOSE → included
        ])
        results = extract_computed_attributes(adapter, part, calc_usage_names)
        assert len(results) == 2  # LITERAL excluded
```

### Changes Required

**See `design.md#compilation-flow-formula-only` for:** compilation pattern, self-exclusion, graceful degradation, `build_expression_ast` parameters

**Specific file changes:**

#### 1. FORMULA Compilation Tests
**File:** `tests/unit/test_computed_attribute_extraction.py` (MODIFY)
- [x] Add `test_formula_simple_binary` — full end-to-end compilation via `extract_computed_attributes()`
- [x] Add `test_formula_complex_nested` (test case 2 in design)
- [x] Add `test_formula_chain_no_special_handling` (test case 3 in design)
- [x] Add `TestExtractComputedAttributes` integration test class

#### 2. Compilation Flow
**File:** `src/sysml_codegen/extraction/computed_attribute_extractor.py` (MODIFY)
- [x] Add imports: `build_expression_ast`, `compile_expression`, `CompilationError` from `expression_compiler`
- [x] Replace compilation stub with real flow per `design.md#compilation-flow-formula-only`
- [x] Implement self-exclusion: `input_names = sibling_attr_names - {attr_name}`
- [x] Implement graceful degradation: `except CompilationError` → `MANUAL_REQUIRED`

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_computed_attribute_extraction.py -v` → 14 tests pass
- [x] `uv run pytest tests/ --tb=short` → 181 passed (full regression green)
- [x] `uv run mypy src/sysml_codegen/extraction/computed_attribute_extractor.py` → Clean

**Manual:**
- [x] Verify `test_formula_complex_nested` produces correct nested parenthesization: `((inputs.m_n * inputs.p_f) + inputs.p_in)`
- [x] Verify LITERAL attributes are excluded from `extract_computed_attributes()` output (confirmed in all 4 Phase 3 tests)
- [x] Verify EXPOSE attributes have `compiled_expression=None` (confirmed in `test_mixed_part_element`)

**What We Know Works After This Phase:**
Complete feature: extraction, classification, compilation, graceful degradation. All acceptance criteria from spec met. Ready for Item 3 pipeline integration.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

```bash
uv run pytest tests/unit/test_computed_attribute_extraction.py -v  # new tests
uv run pytest tests/ --tb=short                                    # full regression
uv run mypy src/                                                   # type check
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 2**: Classification logic is the riskiest piece. Mitigated by 4 worked examples in design, dedicated QN collision regression test, and positive-identification approach (calc_usage_names check) rather than negative inference.
- **Phase 3**: Compilation reuses proven Phase 1 functions — low risk. Graceful degradation (`CompilationError` → `MANUAL_REQUIRED`) ensures no hard failures.

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-08
**Actual Changes:**
- Created `tests/unit/test_computed_attribute_extraction.py` with `TestComputedAttributeClassification` (2 tests) and `TestComputedAttributeData` (2 tests)
- Modified `src/sysml_codegen/extraction/data_models.py`: added `Enum` import, `ExpressionRef` import from `agentic_mbse.sysml.types`, `Compilability` import from `.expression_compiler`
- Added `ComputedAttributeClassification(str, Enum)` with 5 values: FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE
- Added `ComputedAttributeData` dataclass with 13 fields (10 required, 3 with defaults)
- Updated `__all__` to include both new types
**Issues:** None. All pre-existing mypy `import-untyped` errors from `agentic_mbse` — no new errors introduced.
**Deviations:** None.

### Phase 2 Completion
**Completed:** 2026-02-08
**Actual Changes:**
- Created `src/sysml_codegen/extraction/computed_attribute_extractor.py` with `_classify_attribute_expression()` (steps 1-3 of design algorithm) and skeleton `extract_computed_attributes()` (compilation stubbed)
- Modified `tests/unit/test_computed_attribute_extraction.py`: added 7 mock classes, `mock_syside_adapter` fixture with extended TYPE_MAP (6 entries), `_make_refs` helper, and `TestClassifyAttributeExpression` with 6 tests
- `mock_syside_adapter` patches 3 modules: `expression_compiler`, `computed_attribute_extractor`, `expression_utils`
**Issues:** None.
**Deviations:**
- Plan called for monkeypatching `extract_feature_refs` in tests. Instead, tests call `_classify_attribute_expression()` directly with pre-constructed `ExpressionRef` lists via `_make_refs()` helper. This is simpler and tests the classification logic in isolation without coupling to the `extract_feature_refs` call site. The monkeypatch approach will be used in Phase 3's `TestExtractComputedAttributes` integration test where the full `extract_computed_attributes()` function is exercised.

### Phase 3 Completion
**Completed:** 2026-02-08
**Actual Changes:**
- Modified `src/sysml_codegen/extraction/computed_attribute_extractor.py`: added `build_expression_ast`, `compile_expression`, `CompilationError` imports; replaced compilation stub with real FORMULA compilation flow including self-exclusion and graceful degradation
- Modified `tests/unit/test_computed_attribute_extraction.py`: added `TestFormulaCompilation` class (3 tests) and `TestExtractComputedAttributes` integration class (1 test). All use `monkeypatch.setattr` for `extract_feature_refs`.
**Issues:**
- Initial test run failed because `extract_computed_attributes()` called `adapter.is_instance()` on a `None` adapter. Fixed by changing to `SysideAdapter.is_instance()` (static method call, matching `expression_compiler.py` pattern). The `adapter` parameter is retained in the function signature for API compatibility with Item 3.
**Deviations:**
- Plan said "Update `test_formula_simple_binary`" (extend Phase 2 classification-only test). Instead, kept the Phase 2 `test_formula_simple` as classification-only and created new `TestFormulaCompilation` class with separate compilation tests. This provides clearer separation between classification and compilation testing.
- Changed `adapter.is_instance()` calls to `SysideAdapter.is_instance()` (static method) to match the pattern used throughout the codebase (`expression_compiler.py`, `expression_utils.py`). The `adapter` parameter is still accepted for future use.

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete** (2026-02-08)
