# Implementation Plan: Redefinition Resolution, Multiplicity, & Aggregation Expressions

**Status:** Complete
**Created:** 2026-02-10
**Last Updated:** 2026-02-10

## Source Documents
- **Spec:** `.project/active/hierarchy-resolution/spec.md`
- **Design:** `.project/active/hierarchy-resolution/design.md` ← See here for component details, dependencies, architecture

## Implementation Strategy

**Phasing Rationale:**
Phases are ordered by dependency chain: data models first (everything depends on them), then the riskiest extraction logic (redefinition scanning with AST traversal), then multiplicity (needed by aggregation), and finally the aggregation transformer which consumes all prior outputs. Each phase is independently testable and produces verifiable output.

**Overall Validation Approach:**
- Each phase starts with tests
- Each phase has automated + manual validation
- Continuous verification ensures no regressions
- Baseline: 261 tests must remain green throughout

---

## Phase 1: Data Models + Expression Utils Extension

### Goal
Add all new dataclasses and the `InvocationExpression` handler for `reconstruct_expression()`. This is pure additive work with zero behavioral changes to existing code — everything downstream depends on these types.

### Test Stencil (Write This First)
```python
# tests/unit/test_hierarchy_resolver.py — Phase 1 portion
# Test data model construction and expression utils extension

def test_redefinition_data_literal_construction():
    """RedefinitionData with LITERAL type has correct fields."""
    rd = RedefinitionData(
        owning_part_qn="Lib__PV_Module",
        attribute_name="wattage",
        redefinition_type=RedefinitionType.LITERAL,
        literal_value=400.0,
    )
    assert rd.redefinition_type == RedefinitionType.LITERAL
    assert rd.literal_value == 400.0
    assert rd.is_deep_path is False

def test_reconstruct_expression_invocation():
    """reconstruct_expression handles InvocationExpression (sum())."""
    mock_expr = MockInvocationExpression(name="sum", operands=[mock_chain])
    result = reconstruct_expression(mock_expr)
    assert "sum(" in result
```

### Changes Required

**See `design.md` for:**
- Data model definitions → `design.md#component-1-data-models`
- Expression utils extension → `design.md#component-7-expression-utils-extension`

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_hierarchy_resolver.py` (NEW - write first)
- [x] Create test file with imports and mock infrastructure
- [x] Add data model construction tests (RedefinitionData, MultiplicityData, AggregationExpressionData)
- [x] Add `reconstruct_expression` InvocationExpression test

#### 2. Data Models
**File:** `src/sysml_codegen/extraction/data_models.py`
- [x] Add `RedefinitionType` enum
- [x] Add `RedefinitionData` dataclass
- [x] Add `MultiplicityData` dataclass
- [x] Add `SumTerm`, `SingletonTerm`, `LocalTerm` dataclasses
- [x] Add `AggregationExpressionData` dataclass
- [x] Add `HierarchyExtractionResult` dataclass
- [x] Update `__all__` with all new exports

#### 3. Expression Utils
**File:** `src/sysml_codegen/extraction/expression_utils.py`
- [x] Add `InvocationExpression` handling in `reconstruct_expression()` (after OperatorExpression check, before FeatureReference)

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/unit/test_hierarchy_resolver.py` → 17 passed
- [x] `uv run pytest tests/` → 356 passed, zero regressions
- [x] `uv run mypy src/sysml_codegen/extraction/data_models.py` → pre-existing errors only (agentic_mbse stubs)
- [x] `uv run ruff check src/sysml_codegen/extraction/` → pre-existing I001 only (import sort in expression_utils)

**Manual:**
- [x] Verify new types importable: `from sysml_codegen.extraction.data_models import RedefinitionData, AggregationExpressionData`

**What We Know Works After This Phase:**
All data types exist and are constructable. `reconstruct_expression()` can produce text for `sum()` calls. No existing behavior changed.

---

## Phase 2: Redefinition Scanner + Deep-Path Resolver

### Goal
Implement `extract_redefinitions()` and `extract_design_overrides()` — the core `:>>` extraction logic. This is the riskiest part: AST traversal of `ReferenceUsage` with `owned_redefinitions` and `chaining_features`. Getting it right early de-risks the whole feature.

### Test Stencil (Write This First)
```python
# Test redefinition scanning — LITERAL, CHAIN, EXPRESSION classification

def test_literal_redefinition():
    """`:>> wattage = 400.0` extracts as LITERAL with value."""
    part = mock_part_def_with_redef(literal=400.0, attr_name="wattage")
    result = extract_redefinitions(part)
    assert len(result) == 1
    assert result[0].redefinition_type == RedefinitionType.LITERAL
    assert result[0].literal_value == 400.0

def test_deep_path_extracts_chaining_features():
    """`:>> pv_module.wattage = 400.0` resolves through chaining_features."""
    usage = mock_design_usage_with_deep_path(
        path=["pv_module", "wattage"], value=400.0
    )
    result = extract_design_overrides(mock_model_with([usage]))
    assert result[0].target_path == ["pv_module", "wattage"]
    assert result[0].is_deep_path is True
```

### Changes Required

**See `design.md` for:**
- Redefinition scanner logic → `design.md#component-2-redefinition-scanner`
- Deep-path resolver logic → `design.md#component-3-deep-path-resolver`
- Shared helper `_extract_single_redefinition()` → `design.md#component-2-redefinition-scanner`

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_hierarchy_resolver.py`
- [x] Add mock helpers: `MockReferenceUsage`, `MockRedefinition`, `MockChainingFeature`, `_make_*_redef_member()` factories
- [x] Add Test Suite 1: Redefinition Scanning (6 tests per design validation approach)
- [x] Add Test Suite 2: Deep-Path Resolution (5 tests per design validation approach)

#### 2. Hierarchy Resolver
**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py` (NEW)
- [x] Create file with imports (SysideAdapter, expression_utils, data_models, sanitize_name)
- [x] Implement `_extract_single_redefinition(member, owning_qn) -> RedefinitionData | None`
- [x] Implement `extract_redefinitions(part_element) -> list[RedefinitionData]`
- [x] Implement `extract_design_overrides(part_usages) -> list[RedefinitionData]`

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/unit/test_hierarchy_resolver.py -k "redef or deep_path"` → 11 passed
- [x] `uv run pytest tests/` → 367 passed, zero regressions
- [x] `uv run mypy src/sysml_codegen/extraction/hierarchy_resolver.py` → pre-existing errors only (agentic_mbse stubs)
- [x] `uv run ruff check src/sysml_codegen/extraction/hierarchy_resolver.py` → All checks passed

**What We Know Works After This Phase:**
`:>>` redefinitions on PartDefs are correctly classified into LITERAL/CHAIN/EXPRESSION. Deep-path `chaining_features` traversal produces correct `target_path`. Design-level overrides are collected with correct `owning_part_qn`.

---

## Phase 3: Multiplicity Extractor

### Goal
Implement `extract_multiplicities()` — Component 4 from design. Small, focused phase that produces `MultiplicityData` needed by Phase 4's aggregation transformer.

### Test Stencil (Write This First)
```python
# Test multiplicity extraction — cached_lower_bound, attribute refs, defaults

def test_multiplicity_with_attribute_ref():
    """[module_count] with default 20 extracts correctly."""
    part = mock_part_def_with_arrayed_usage(
        usage_name="pv_module", count=20, attr_name="module_count"
    )
    result = extract_multiplicities(part)
    assert len(result) == 1
    assert result[0].count == 20
    assert result[0].count_attribute_name == "module_count"

def test_singleton_no_multiplicity():
    """PartUsage without multiplicity is not in results."""
    part = mock_part_def_with_singleton_usage("allocation_model")
    result = extract_multiplicities(part)
    assert len(result) == 0
```

### Changes Required

**See `design.md` for:**
- Multiplicity extraction logic → `design.md#component-4-multiplicity-extractor`
- Why `cached_lower_bound` → `design.md#component-4-multiplicity-extractor` ("Why cached_lower_bound")

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_hierarchy_resolver.py`
- [x] Add mock helpers: `MockMultiplicityReferent`, `MockUpperBound`, `MockMultiplicityRange`, `MockPartUsageForMultiplicity`
- [x] Add Test Suite 3: Multiplicity (4 tests per design validation approach)

#### 2. Hierarchy Resolver
**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py`
- [x] Implement `extract_multiplicities(part_element) -> list[MultiplicityData]`

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/unit/test_hierarchy_resolver.py -k "multiplicity"` → 6 passed
- [x] `uv run pytest tests/` → 371 passed, zero regressions
- [x] `uv run mypy src/sysml_codegen/extraction/hierarchy_resolver.py` → pre-existing errors only (agentic_mbse stubs)

**What We Know Works After This Phase:**
Multiplicity correctly extracted via `cached_lower_bound`. Attribute reference names and defaults resolved. Singletons excluded from results.

---

## Phase 4: Aggregation Expression Transformer + Orchestrator

### Goal
Implement `build_aggregation_expression()` and `extract_hierarchy_data()` — the most complex phase. Depends on all prior phases: uses EXPRESSION-type redefinitions from Phase 2 and multiplicities from Phase 3 to transform `sum()` calls into parametric multiply expressions.

### Test Stencil (Write This First)
```python
# Test sum() transformation and full aggregation decomposition

def test_sum_parametric_multiply():
    """sum(pv_module.capital_cost) → module_count * pv_module.capital_cost."""
    redef = make_expression_redef(sum_expr("pv_module", "capital_cost"))
    mults = [MultiplicityData("pv_module", "Lib__Solar_Array", 20, "module_count", 20)]
    result = build_aggregation_expression(redef, mults, mock_part)
    assert len(result.sum_terms) == 1
    assert "module_count * pv_module.capital_cost" in result.transformed_expression

def test_mixed_expression_full_decomposition():
    """Solar Array capital_cost: 2 SumTerms + 1 SingletonTerm + 1 LocalTerm."""
    # Full mock of: sum(pv.cc) + sum(inv.cc) + alloc.total + misc
    result = build_aggregation_expression(full_redef, full_mults, mock_part)
    assert len(result.sum_terms) == 2
    assert len(result.singleton_terms) == 1
    assert len(result.local_terms) == 1
    assert result.entry_points == ["module_count", "inverter_count"]
```

### Changes Required

**See `design.md` for:**
- AST walk logic → `design.md#component-5-aggregation-expression-transformer`
- Expected AST structure → `design.md#component-5-aggregation-expression-transformer` (AST tree diagram)
- Orchestrator logic → `design.md#component-6-top-level-extraction-orchestrator`
- Term decomposition rationale → `design.md#component-1-data-models` (bottom)

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_hierarchy_resolver.py`
- [x] Add mock helpers: `_make_sum_invocation()`, `_make_solar_array_expression_ast()`, `_make_solar_array_redef()`, `_make_solar_array_multiplicities()`, `_make_solar_array_part()`
- [x] Add Test Suite 4: Sum Transformation (5 tests per design validation approach)
- [x] Add Test Suite 5: AggregationExpressionData (4 tests per design validation approach)
- [x] Add Test Suite 6: Integration — `test_extract_hierarchy_data` full mock (1 test)

#### 2. Hierarchy Resolver
**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py`
- [x] Implement `_walk_aggregation_ast()` recursive walker (dispatches on node type)
- [x] Implement `build_aggregation_expression(redef, multiplicities, part_element) -> AggregationExpressionData | None`
- [x] Implement `extract_hierarchy_data(model) -> HierarchyExtractionResult` orchestrator

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/unit/test_hierarchy_resolver.py` → 42 passed (all suites)
- [x] `uv run pytest tests/` → 381 passed, zero regressions
- [x] `uv run mypy src/sysml_codegen/extraction/hierarchy_resolver.py` → pre-existing errors only (agentic_mbse stubs)
- [x] `uv run ruff check src/sysml_codegen/extraction/hierarchy_resolver.py` → All checks passed

**Manual:**
- [x] Verify transformed expression for solar_array.capital_cost: `((((module_count * pv_module.capital_cost) + (inverter_count * inverter.capital_cost)) + allocation_model.total_allocation) + misc_hardware_cost)` — matches design expectation (outer parens from binary OperatorExpression wrapping)

**What We Know Works After This Phase:**
`sum()` → parametric multiply transformation works. Mixed expressions fully decomposed into typed terms. `HierarchyExtractionResult` populated with all data structures. Full test suite green. Item 4 can consume this data.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 2**: `chaining_features` may return empty iterator on unexpected patterns → wrap in `list()`, fall back to `member.name`
- **Phase 4**: Expression AST structure may vary beyond the solar_battery canonical pattern → log unrecognized node types as warnings via `has_unsupported_nodes` flag rather than failing

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Created `tests/unit/test_hierarchy_resolver.py` with 17 tests (4 test classes: data model construction + expression utils InvocationExpression)
- Modified `src/sysml_codegen/extraction/data_models.py`: Added `RedefinitionType`, `RedefinitionData`, `MultiplicityData`, `SumTerm`, `SingletonTerm`, `LocalTerm`, `AggregationExpressionData`, `HierarchyExtractionResult`. Updated `__all__` with 8 new exports.
- Modified `src/sysml_codegen/extraction/expression_utils.py:47-52`: Added `InvocationExpression` handling via `hasattr(expr_node, "function")` dispatch, before FeatureReferenceExpression check.
**Issues:** None
**Deviations:** None

### Phase 2 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Created `src/sysml_codegen/extraction/hierarchy_resolver.py` with `_extract_single_redefinition()`, `extract_redefinitions()`, `extract_design_overrides()`
- Added 11 tests to `tests/unit/test_hierarchy_resolver.py` (6 redefinition scanning + 5 deep-path resolution)
- Added 8 mock classes and 4 factory helpers for Phase 2 test infrastructure
**Issues:** None
**Deviations:**
- `extract_design_overrides()` accepts `Iterable[Any]` (list of PartUsage elements) instead of `model: Any` as in design. This makes it testable without mocking `SysideAdapter.elements_of_type()`. The orchestrator (Phase 4) will call `elements_of_type()` and pass results. Cleaner separation of concerns.
- Used `collections.abc.Iterable` instead of `typing.Iterable` per ruff UP035.

### Phase 3 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Modified `src/sysml_codegen/extraction/hierarchy_resolver.py`: Added `MultiplicityData` import, implemented `extract_multiplicities()` with `cached_lower_bound`, defensive `int()` cast, `upper_bound.referent` attribute name extraction, and default value extraction.
- Added 4 tests + 4 mock classes to `tests/unit/test_hierarchy_resolver.py` (TestMultiplicityExtraction suite)
**Issues:** None
**Deviations:** None — implementation matches design exactly.

### Phase 4 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Modified `src/sysml_codegen/extraction/hierarchy_resolver.py`: Added `_AggregationContext` collector class, `_walk_aggregation_ast()` recursive AST walker (handles OperatorExpression, InvocationExpression/sum, FeatureChainExpression, FeatureReferenceExpression, literals, unknown nodes), `build_aggregation_expression()` transformer, `extract_hierarchy_data()` orchestrator. Updated imports to add `AggregationExpressionData`, `HierarchyExtractionResult`, `SumTerm`, `SingletonTerm`, `LocalTerm`, `OPERATOR_MAP`.
- Added 10 tests + 5 factory helpers to `tests/unit/test_hierarchy_resolver.py` (TestSumTransformation 5 tests, TestAggregationExpressionProperties 4 tests, TestExtractHierarchyData 1 integration test with SysideAdapter.elements_of_type patching)
**Issues:** None
**Deviations:**
- Transformed expression has one extra layer of outer parentheses vs design expected text due to consistent binary OperatorExpression wrapping: `(((...) + alloc) + misc)` instead of `((...) + alloc) + misc`. Mathematically equivalent. Downstream Item 4 consumes structured term data, not the text string.
- `extract_hierarchy_data()` passes `SysideAdapter.elements_of_type(model, "PartUsage")` result to `extract_design_overrides()`, consistent with Phase 2 deviation where that function accepts `Iterable[Any]` instead of model directly.

---

**Status**: Complete
