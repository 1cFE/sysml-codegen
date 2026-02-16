# Implementation Plan: Expression Compiler Module

**Status:** Complete
**Created:** 2026-02-06
**Last Updated:** 2026-02-06

## Source Documents
- **Spec:** `.project/active/expr-compiler-module/spec.md`
- **Design:** `.project/active/expr-compiler-module/design.md` ← See here for component details, dependencies, architecture
- **Algorithm Diagram:** `.project/active/expr-compiler-module/algorithm-diagram.md`

## Implementation Strategy

**Phasing Rationale:**
Phase 1 de-risks by refactoring the existing `constraint_extractor.py` first — if this breaks anything, we catch it before writing new code. Phase 2 builds the pure data models and IR-to-Python compiler functions that are fully testable without syside. Phase 3 adds the syside→IR boundary (`build_expression_ast`) with mock infrastructure. Phase 4 completes the orchestrator with dependency graph, topological sort, and edge cases. Each phase is independently verifiable.

**Overall Validation Approach:**
- Each phase starts with tests
- Each phase has automated + manual validation
- Continuous verification ensures no regressions

---

## Phase 1: Expression Utils Extraction

### Goal
Extract shared AST-to-text logic from `constraint_extractor.py` into new `expression_utils.py` and rewire imports. This is the riskiest change (modifying existing working code), so it goes first.

### Test Stencil (Write This First)
```python
# No new tests needed — validation is that ALL existing tests pass unchanged.
# Run: uv run pytest tests/
# The refactor is a pure move + import alias — zero logic changes.
```

### Changes Required

**See `design.md#component-1-extractionexpression_utilspy` for:** full public API, function list, implementation notes.

**See `design.md#component-3-modified-constraint_extractorpy` for:** import aliasing strategy, what stays vs. moves.

**Specific file changes:**

#### 1. New Shared Utility
**File:** `src/sysml_codegen/extraction/expression_utils.py` (NEW)
- [x] Create file with module docstring
- [x] Move `OPERATOR_MAP` from `constraint_extractor.py:33-50`
- [x] Move `_reconstruct_expression()` from `constraint_extractor.py:137-171` → rename to `reconstruct_expression()`
- [x] Move `_reconstruct_operator_expression()` from `constraint_extractor.py:174-203` → rename to `reconstruct_operator_expression()`
- [x] Move `_extract_feature_reference_name()` from `constraint_extractor.py:206-226` → rename to `extract_feature_reference_name()`
- [x] Move `_extract_feature_chain_name()` from `constraint_extractor.py:229-257` → rename to `extract_feature_chain_name()`
- [x] Add necessary imports (`Any`, `SysideAdapter`)
- [x] Add `__all__` export list

#### 2. Refactored Constraint Extractor
**File:** `src/sysml_codegen/extraction/constraint_extractor.py` (MODIFIED)
- [x] Remove `OPERATOR_MAP` constant and 4 function bodies
- [x] Verify `KEYWORDS` constant (line 53) remains — it sits between removed items
- [x] Add aliased import (only `_reconstruct_expression` needed — see Phase 1 deviation notes)
- [x] Verify all internal call sites unchanged (they still call `_reconstruct_expression(...)` etc.)

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/` → All 42 tests pass with zero regressions
- [x] `uv run mypy` → Only pre-existing errors (import-untyped, no-any-return); no new errors
- [x] `uv run ruff check` → Only pre-existing warnings + I001 (import sort, same as usage_extractor.py)

**Manual:**
- [x] Verify `KEYWORDS` constant is still present in `constraint_extractor.py` (line 41)
- [x] Verify `_extract_referenced_variables()` (which uses `KEYWORDS`) is untouched (line 126)
- [x] Verify `expression_utils.py` has no constraint-specific logic

**What We Know Works After This Phase:**
The shared utility extraction is safe. `constraint_extractor.py` works identically through aliased imports. `expression_utils.py` is available for `expression_compiler.py` to import from.

---

## Phase 2: Data Models + Pure Compiler Functions

### Goal
Implement the 5 data models, `CompilationError`, `compile_expression()`, `_sanitize_name()`, `_collect_refs()`, and `classify_compilability()`. These are all pure functions on the `ExpressionAST` IR — no syside dependency. Create the test file and write tests first.

### Test Stencil (Write This First)
```python
# tests/unit/test_expression_compiler.py

class TestCompilability:
    def test_enum_values(self):
        from sysml_codegen.extraction.expression_compiler import Compilability
        assert Compilability.FULLY_COMPILABLE == "fully_compilable"
        assert Compilability.UNKNOWN == "unknown"

class TestCompileExpression:
    def test_input_ref_produces_inputs_prefix(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST, compile_expression,
        )
        ast = ExpressionAST.input_ref("wattage")
        assert compile_expression(ast) == "inputs.wattage"

    def test_binary_op_over_parenthesized(self):
        ast = ExpressionAST.binary("*",
            ExpressionAST.input_ref("length"),
            ExpressionAST.input_ref("width"),
        )
        assert compile_expression(ast) == "(inputs.length * inputs.width)"

class TestClassifyCompilability:
    def test_all_fully_returns_fully(self):
        # ... results with all FULLY_COMPILABLE
        assert classify_compilability(results) == Compilability.FULLY_COMPILABLE
```

### Changes Required

**See `design.md#component-2-extractionexpression_compilerpy` for:**
- All data model definitions (enums, dataclasses, factory classmethods)
- `compile_expression()` algorithm
- `_sanitize_name()` implementation
- `_collect_refs()` implementation
- `classify_compilability()` implementation
- `CompilationError` exception class

**See `design.md#component-4-testsunittest_expression_compilerpy` for:**
- Test class organization
- Full test list per class

**Specific file changes:**

#### 1. Test File (Write First)
**File:** `tests/unit/test_expression_compiler.py` (NEW)
- [x] Create file with test classes:
  - `TestCompilability` — enum values, `str` inheritance, `UNKNOWN` sentinel
  - `TestExpressionNodeType` — enum values, `str` inheritance
  - `TestExpressionASTFactories` — all 6 factory classmethods
  - `TestCompileExpression` — `INPUT_REF`, `INTERMEDIATE_REF`, `LITERAL`, `BINARY_OP`, `UNARY_OP`, `UNSUPPORTED` → `CompilationError`, over-parenthesization nesting, Patterns A/C/D
  - `TestSanitizeName` — quotes stripped, spaces→underscores, empty string, clean name
  - `TestCollectRefs` — single input, single intermediate, mixed tree, deduplication, nested pre-order
  - `TestClassifyCompilability` — all FULLY, mix FULLY+MANUAL, mix FULLY+PARTIAL, empty list, UNKNOWN assertion error

#### 2. Implementation File (Partial)
**File:** `src/sysml_codegen/extraction/expression_compiler.py` (NEW)
- [x] Create file with module docstring and imports
- [x] `Compilability(str, Enum)` — 4 values per `design.md`
- [x] `ExpressionNodeType(str, Enum)` — 6 values per `design.md`
- [x] `ExpressionAST` dataclass with 6 factory classmethods per `design.md`
- [x] `CompilationResult` dataclass per `design.md`
- [x] `CalcDefCompilationResult` dataclass per `design.md`
- [x] `CompilationError(Exception)` per `design.md`
- [x] `_sanitize_name()` per `design.md`
- [x] `compile_expression()` — recursive IR→Python with `ast.parse()` validation per `design.md`
- [x] `_collect_refs()` — recursive tree walk per `design.md`
- [x] `classify_compilability()` — worst-case aggregation per `design.md`

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/unit/test_expression_compiler.py` → All 41 tests pass
- [x] `uv run mypy src/sysml_codegen/extraction/expression_compiler.py` → Clean (no issues)
- [x] `uv run pytest tests/` → No regressions (all 83 tests pass)

**Manual:**
- [x] Verify `ExpressionAST` factory classmethods set correct node_type (tested in TestExpressionASTFactories)
- [x] Verify `compile_expression` on UNSUPPORTED node raises `CompilationError` (tested)

**What We Know Works After This Phase:**
All data models are correct, the IR-to-Python compiler produces correct Python strings with proper `inputs.` prefixing and over-parenthesization, `classify_compilability` aggregates correctly, `_collect_refs` extracts references in pre-order, `_sanitize_name` normalizes names.

---

## Phase 3: `build_expression_ast()` + Syside Mock Tests

### Goal
Implement `build_expression_ast()` with n-ary left-fold, reference resolution, unit stripping. Add mock syside node classes and monkeypatched `SysideAdapter.is_instance` fixture. Test all expression patterns.

### Test Stencil (Write This First)
```python
# Add to tests/unit/test_expression_compiler.py

class MockOperatorExpression:
    def __init__(self, operator, operands):
        self.operator = operator
        self.operands = operands

@pytest.fixture
def mock_syside_adapter(monkeypatch):
    """Monkeypatch SysideAdapter.is_instance for mock nodes."""
    # ... per design.md#component-4

class TestBuildExpressionAST:
    def test_simple_binary_two_operands(self, mock_syside_adapter):
        ast = build_expression_ast(
            MockOperatorExpression("*", [
                MockFeatureReferenceExpression("length"),
                MockFeatureReferenceExpression("width"),
            ]),
            input_names={"length", "width"},
            output_names=set(),
        )
        assert ast.node_type == ExpressionNodeType.BINARY_OP
        assert ast.left.input_name == "length"

    def test_nary_3_operand_left_folds(self, mock_syside_adapter):
        # a + b + c → ((a + b) + c)
        ...

    def test_nary_7_operand_left_folds(self, mock_syside_adapter):
        # NetElectricPower pattern
        ...
```

### Changes Required

**See `design.md#component-2` for:** `build_expression_ast()` algorithm (6-step dispatch), `PYTHON_OPERATOR_MAP` constant.

**See `design.md#component-4` for:** mock node classes (`MockOperatorExpression`, `MockFeatureReferenceExpression`, `MockLiteralRational`), `mock_syside_adapter` fixture.

**Specific file changes:**

#### 1. Test File (Add Tests First)
**File:** `tests/unit/test_expression_compiler.py` (ADD)
- [x] Add mock syside node classes: `MockOperatorExpression`, `MockFeatureReferenceExpression`, `MockLiteralRational`, `MockFeatureChainExpression`
- [x] Add `mock_syside_adapter` fixture per `design.md`
- [x] Add `TestBuildExpressionAST` class with tests for:
  - Pattern A: simple binary (2 operands)
  - Pattern C: nested parenthesized with `**`
  - Pattern D: literal + input ref mix
  - Pattern F: unit annotation stripping (`[` operator)
  - N-ary 3-operand left-fold: `a + b + c` → `((a + b) + c)`
  - N-ary 7-operand left-fold (NetElectricPower pattern)
  - Unary negation: `-(x)` → `(-inputs.x)`
  - `FeatureChainExpression` → `UNSUPPORTED`
  - Unknown node type → `UNSUPPORTED`
  - Unresolved reference → `UNSUPPORTED`
  - Undeclared member reference → `INTERMEDIATE_REF`

#### 2. Implementation (Add Function)
**File:** `src/sysml_codegen/extraction/expression_compiler.py` (ADD)
- [x] Add `PYTHON_OPERATOR_MAP` module-level constant per `design.md` (done in Phase 2)
- [x] Add imports: `SysideAdapter` from `agentic_mbse.sysml.syside_adapter`
- [x] Add import: `extract_feature_reference_name` from `.expression_utils`
- [x] Implement `build_expression_ast()` per `design.md` algorithm:
  - `SysideAdapter.is_instance()` dispatch
  - N-ary to binary left-fold for >2 operands
  - `[` operator unit stripping
  - Reference resolution: input → `INPUT_REF`, output/member → `INTERMEDIATE_REF`, else → `UNSUPPORTED`
  - `_sanitize_name()` after `extract_feature_reference_name()`
  - `FeatureChainExpression` → `UNSUPPORTED`
  - Literal extraction

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/unit/test_expression_compiler.py::TestBuildExpressionAST` → All 15 pass
- [x] `uv run mypy src/sysml_codegen/extraction/expression_compiler.py` → Only pre-existing import-untyped
- [x] `uv run pytest tests/` → No regressions (all 98 tests pass)

**Manual:**
- [x] Verify 3-operand fold produces `((a + b) + c)` not `(a + (b + c))` (tested in test_nary_3_operand_left_fold)
- [x] Verify `[` operator strips unit and recurses on value (first operand) (tested in test_pattern_f_unit_annotation_stripping)
- [x] Verify unresolved refs produce `UNSUPPORTED` with descriptive reason string (tested in test_unresolved_reference_unsupported)

**What We Know Works After This Phase:**
The full syside→IR→Python pipeline works for all 6 expression patterns. N-ary left-fold is correct. Reference resolution classifies inputs, outputs, and undeclared members correctly. Unit annotations are stripped. The mock infrastructure is proven and ready for Phase 4.

---

## Phase 4: `compile_calc_def()` Orchestrator + Edge Cases

### Goal
Implement the full orchestrator: dependency graph construction with undeclared intermediate discovery, Kahn's topological sort with cycle detection, per-output compilation, worst-case aggregation. Test all edge cases (1-6) and the undeclared intermediate pattern.

### Test Stencil (Write This First)
```python
# Add to tests/unit/test_expression_compiler.py

@pytest.fixture
def mock_extract_feature_refs(monkeypatch):
    """Monkeypatch extract_feature_refs for dependency graph control."""
    # ... per design.md#component-4

class TestCompileCalcDef:
    def test_pattern_b_multi_step_topological_order(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        # material_cost → fab_cost → total_cost
        # Verify execution_order and correct python_expression for each
        ...

    def test_circular_dependency_returns_manual_required(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        # a depends on b, b depends on a
        result = compile_calc_def(calc_def, asts)
        assert result.overall_compilability == Compilability.MANUAL_REQUIRED

    def test_undeclared_intermediates_4_chain(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        # MagnetCryogenicLoad pattern: 4 undeclared intermediates
        # Verify all discovered, topologically sorted, is_undeclared_intermediate=True
        ...
```

### Changes Required

**See `design.md#component-2` for:** `compile_calc_def()` algorithm (7 steps), dependency graph construction, Kahn's algorithm, undeclared intermediate discovery, return statement logic.

**See `design.md#component-4` for:** `TestCompileCalcDef` test list, `TestCompileCalcDefEdge6` test list, `mock_extract_feature_refs` fixture.

**Specific file changes:**

#### 1. Test File (Add Tests First)
**File:** `tests/unit/test_expression_compiler.py` (ADD)
- [x] Add `mock_extract_feature_refs` fixture per `design.md`
- [x] Add `TestCompileCalcDef` class with tests for:
  - Pattern B: multi-step intermediate with topological ordering
  - Pattern E: pi as repeated literal
  - Edge 1: unresolved reference → verdict escalation
  - Edge 2: circular intermediate → `MANUAL_REQUIRED`
  - Edge 3: missing AST for one output → partial compilability
  - Edge 4: unsupported operator → verdict escalation
  - Edge 5: `FeatureChainExpression` → `MANUAL_REQUIRED`
  - Undeclared intermediates: 4-chain (MagnetCryogenicLoad) with correct topo order
  - Undeclared intermediates excluded from return, included in `execution_order`
  - Overall compilability is worst-case
- [x] Add `TestCompileCalcDefEdge6` class:
  - EXPOSE-with-operators compiles normally → `FULLY_COMPILABLE`

#### 2. Implementation (Add Function)
**File:** `src/sysml_codegen/extraction/expression_compiler.py` (ADD)
- [x] Add import: `extract_feature_refs` from `agentic_mbse.sysml.expression`
- [x] Implement `compile_calc_def()` per `design.md` algorithm:
  - Build `input_names`, `output_names` sets
  - Build dependency graph with `extract_feature_refs()` for each output
  - Undeclared intermediate discovery via `all_member_names` / `member_expressions`
  - Recursive discovery of intermediate chains
  - Kahn's topological sort with deterministic tie-breaking (`sorted()`)
  - Cycle detection (len(result) != len(graph))
  - Per-output compilation: `build_expression_ast()` → `compile_expression()` → `_collect_refs()`
  - `CompilationError` handling → `MANUAL_REQUIRED` result
  - Missing AST handling → `MANUAL_REQUIRED` result
  - `is_undeclared_intermediate` flag for non-declared outputs
  - `classify_compilability()` for overall verdict

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/unit/test_expression_compiler.py` → ALL 67 tests pass (full file)
- [x] `uv run mypy src/sysml_codegen/extraction/expression_compiler.py` → Only pre-existing import-untyped
- [x] `uv run mypy src/sysml_codegen/extraction/expression_utils.py` → Only pre-existing issues
- [x] `uv run ruff check src/sysml_codegen/extraction/` → No new warnings from expression_compiler.py
- [x] `uv run pytest tests/` → ALL 109 tests pass with zero regressions

**Manual:**
- [x] Verify Pattern B execution_order is `["material_cost", "fab_cost", "total_cost"]` (tested)
- [x] Verify circular dependency returns descriptive reason string (tested: "circular dependency detected")
- [x] Verify undeclared intermediates have `is_undeclared_intermediate=True` and are in `execution_order` (tested in 4-chain)
- [x] Verify no imports from `analysis/`, `resolution/`, or `generation/` in new modules (verified programmatically)

**What We Know Works After This Phase:**
The complete expression compiler module is functional: data models, syside→IR conversion with n-ary left-fold, IR→Python compilation with over-parenthesization, dependency graph with undeclared intermediate discovery, topological sorting with cycle detection, worst-case compilability classification. All 6 patterns and 6 edge cases are tested. The module is ready for Item 4 pipeline integration.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

Key commands:
- `uv run pytest tests/` — full test suite
- `uv run pytest tests/unit/test_expression_compiler.py` — new module tests
- `uv run mypy src/sysml_codegen/extraction/expression_compiler.py` — type check
- `uv run ruff check src/sysml_codegen/extraction/` — lint

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Pure move+import refactor. Immediate full test suite run. Verify `KEYWORDS` constant survives (sits between removed items).
- **Phase 2**: No syside dependency — pure IR tests. Factory classmethods enforce correct construction.
- **Phase 3**: Mock nodes based on spike-validated patterns (102 outputs across 4 model suites). Monkeypatch `SysideAdapter.is_instance` for isolation.
- **Phase 4**: Monkeypatch both `SysideAdapter.is_instance` AND `extract_feature_refs` for full isolation. Kahn's algorithm is well-understood; deterministic tie-breaking via `sorted()`.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION - Leave empty now]

### Phase 1 Completion
**Completed:** 2026-02-06
**Actual Changes:**
- Created `src/sysml_codegen/extraction/expression_utils.py` with `OPERATOR_MAP`, `reconstruct_expression`, `reconstruct_operator_expression`, `extract_feature_reference_name`, `extract_feature_chain_name` (all moved from `constraint_extractor.py` with leading underscores dropped)
- Modified `src/sysml_codegen/extraction/constraint_extractor.py`: removed 5 moved items, added single aliased import `from .expression_utils import reconstruct_expression as _reconstruct_expression`

**Issues:**
- None. Pure move+import refactor. All 42 tests pass.

**Deviations:**
- Design called for importing all 5 items with aliases into `constraint_extractor.py`. In practice, only `_reconstruct_expression` is called directly in that file — the other 4 (`OPERATOR_MAP`, `_reconstruct_operator_expression`, `_extract_feature_reference_name`, `_extract_feature_chain_name`) were only called by `_reconstruct_expression` itself, which now lives in `expression_utils.py`. Importing unused symbols would trigger ruff F401 warnings, so only the one needed import was added.

### Phase 2 Completion
**Completed:** 2026-02-06
**Actual Changes:**
- Created `tests/unit/test_expression_compiler.py` with 41 tests across 8 test classes (TestCompilability, TestExpressionNodeType, TestExpressionASTFactories, TestCompileExpression, TestSanitizeName, TestCollectRefs, TestClassifyCompilability)
- Created `src/sysml_codegen/extraction/expression_compiler.py` with: `Compilability`, `ExpressionNodeType`, `ExpressionAST` (6 factory classmethods), `CompilationResult`, `CalcDefCompilationResult`, `CompilationError`, `PYTHON_OPERATOR_MAP`, `_sanitize_name()`, `compile_expression()`, `_collect_refs()`, `classify_compilability()`

**Issues:**
- None. All 41 tests pass. Mypy clean. 83 total tests pass.

**Deviations:**
- Added `TestExpressionASTFactories` class (not explicitly in plan but implied by design — validates factory classmethods set correct node_type and fields)
- `PYTHON_OPERATOR_MAP` included in Phase 2 (plan listed it under Phase 3) since it's needed by `compile_expression()` for operator string lookup

### Phase 3 Completion
**Completed:** 2026-02-06
**Actual Changes:**
- Added mock syside classes (`MockOperatorExpression`, `MockFeatureReferenceExpression`, `MockLiteralRational`, `MockFeatureChainExpression`, `MockUnknownNode`) and `mock_syside_adapter` fixture to `tests/unit/test_expression_compiler.py`
- Added `TestBuildExpressionAST` class with 15 tests covering all 6 patterns (A/C/D/F + n-ary + unary), reference resolution (input/output/undeclared member/unresolved), unsupported types (chain, unknown, bad operator), caret alias, and name sanitization
- Added `build_expression_ast()` to `src/sysml_codegen/extraction/expression_compiler.py` with full 6-step dispatch: OperatorExpression (binary/unary/n-ary left-fold/unit strip), FeatureReferenceExpression (with sanitization and resolution), LiteralRational/Integer/Real, FeatureChainExpression → UNSUPPORTED, unknown → UNSUPPORTED
- Added imports: `Any` from typing, `SysideAdapter` from agentic_mbse, `extract_feature_reference_name` from expression_utils

**Issues:**
- None. All 15 Phase 3 tests pass. All 98 total tests pass.

**Deviations:**
- Added `MockUnknownNode` class (not in design) for testing unknown node type handling
- Added `test_output_ref_becomes_intermediate_ref`, `test_caret_power_alias`, and `test_sanitize_name_in_reference_resolution` tests beyond the design's explicit list — these validate important behaviors (output→intermediate classification, FR-8 caret alias, and the sanitization bridge described in design.md)
- `SysideAdapter.is_instance` monkeypatch uses `staticmethod()` wrapping as designed, verified to work correctly with the classmethod's fallback path

### Phase 4 Completion
**Completed:** 2026-02-06
**Actual Changes:**
- Added `_make_calc_def` helper function and `mock_extract_feature_refs` fixture to test file
- Added `TestCompileCalcDef` class with 10 tests: Pattern B (topological ordering), Pattern E (pi as literal), Edge 1-5 (unresolved ref, circular dep, missing AST, unsupported op, feature chain), undeclared intermediates 4-chain, overall worst-case, single output
- Added `TestCompileCalcDefEdge6` class with 1 test: EXPOSE-with-operators
- Added `from agentic_mbse.sysml.expression import extract_feature_refs` to expression_compiler.py
- Added `_topological_sort()` private function (Kahn's algorithm with deterministic sorted() tie-breaking)
- Added `compile_calc_def()` orchestrator function: dependency graph construction with undeclared intermediate discovery, topological sort with cycle detection, per-output compilation pipeline, worst-case aggregation

**Issues:**
- Mypy flagged `output_results: list[CompilationResult]` as redefinition (first in circular branch, second in main path). Fixed by removing type annotation from the second definition since mypy infers type from the circular branch.

**Deviations:**
- Added `test_single_output_fully_compilable` and `test_overall_compilability_is_worst_case` tests beyond design's list — validates the happy path and the aggregation logic at the orchestrator level
- `_topological_sort` extracted as a private module-level function (design showed it inline in compile_calc_def). Separation improves readability and testability.

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete**
