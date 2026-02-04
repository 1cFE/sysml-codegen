# Design: Expression Compiler Module

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-03
**Branch:** `cost-pattern`
**Epic:** EXPR-CODEGEN Item 3

---

## Overview

Production-quality expression compiler module (`extraction/expression_compiler.py`) and shared AST-to-text utility (`extraction/expression_utils.py`), with `constraint_extractor.py` refactored to import from the shared utility. The compiler converts raw SysIDE AST nodes into a clean `ExpressionAST` IR, compiles to Python expression strings, classifies CalcDef compilability, and handles undeclared intermediates -- all validated in Items 1-2 spike scripts.

## Related Artifacts

- **Spec:** `.project/active/expr-compiler-module/spec.md`
- **Concept:** `.project/concepts/expression-aware-codegen.md`
- **Epic:** `.project/backlog/epic_expression_aware_codegen.md`
- **Spike reports:** `.project/active/expr-spike-ast/report.md`, `.project/active/expr-spike-compile/report.md`
- **Spike scripts:** `scripts/spike_compile_expressions.py`, `scripts/spike_classify_compilability.py`

---

## Research Findings

### Existing Patterns to Follow

**Enum convention (`str, Enum`):** Used throughout the codebase for JSON-serializable enums with lowercase underscore values:
- `BindingResolutionType` at `core/models.py:12-28` — `ENTRY_POINT = "entry_point"`, `MODULE_OUTPUT = "module_output"`
- `EntryPointType` at `resolution/models.py:22-33` — `LIBRARY_DEFAULT = "library_default"`, etc.

Note: `BindingType` in agentic-mbse (`types.py:18-49`) inherits from `Enum` only (not `str, Enum`). Our new enums follow the codegen convention, not agentic-mbse.

**Dataclass convention:** `CalculationDefinitionData` at `data_models.py:107-135` and all extraction-layer models use `@dataclass` (not Pydantic). The expression compiler's models follow this convention since they are extraction-layer data structures.

**Test convention:** Pytest class-based tests with descriptive docstrings, fixtures from `tests/conftest.py`. See `tests/unit/test_parameter_groups.py` for representative pattern: class-organized tests, `fixtures_path` fixture, lazy imports inside test methods.

### AST-to-Text Logic in constraint_extractor.py

Functions to extract into `expression_utils.py` (pure AST-to-text, no constraint-specific logic):

| Function | Location | Purpose |
|----------|----------|---------|
| `OPERATOR_MAP` | `constraint_extractor.py:33-50` | Operator string mapping constant |
| `_reconstruct_expression()` | `constraint_extractor.py:137-171` | Recursive AST-to-text dispatcher |
| `_reconstruct_operator_expression()` | `constraint_extractor.py:174-203` | Operator expression reconstruction |
| `_extract_feature_reference_name()` | `constraint_extractor.py:206-226` | Feature reference name extraction |
| `_extract_feature_chain_name()` | `constraint_extractor.py:229-257` | Feature chain (dotted path) extraction |

Functions that stay in `constraint_extractor.py` (constraint-specific):

| Function | Location | Reason stays |
|----------|----------|-------------|
| `extract_all_constraints()` | `constraint_extractor.py:56-80` | Public API, constraint-specific |
| `_extract_constraint()` | `constraint_extractor.py:83-110` | Constraint extraction logic |
| `_extract_constraint_expression()` | `constraint_extractor.py:113-134` | Constraint-specific AST access patterns |
| `_extract_referenced_variables()` | `constraint_extractor.py:260-281` | Regex-based variable extraction (different from AST-based) |
| `_find_owner()`, `_get_qualified_name()`, etc. | `constraint_extractor.py:284-395` | Constraint metadata extraction |

### Spike Script Validated Logic

The spike scripts (`spike_compile_expressions.py`, `spike_classify_compilability.py`) contain the working compilation logic. Key elements to formalize:

1. **`PYTHON_OPERATOR_MAP`** at `spike_compile_expressions.py:42-50` — differs from constraint extractor's `OPERATOR_MAP` in that `^` maps to ` ** ` (Python power) and `[` maps to `None` (strip). The expression compiler needs its own Python-specific operator map.

2. **`compile_expression()`** at `spike_compile_expressions.py:148-262` — recursive syside-AST-to-Python compiler. In the production module, this function is split into two responsibilities: `build_expression_ast()` (syside → IR) and `compile_expression()` (IR → Python string).

3. **`build_dependency_graph()`** at `spike_compile_expressions.py:311-377` — builds output dependency graph including undeclared intermediates via `owned_members` discovery. Uses `extract_feature_refs()` from agentic-mbse.

4. **`topological_sort()`** at `spike_compile_expressions.py:380-415` — Kahn's algorithm with deterministic tie-breaking (sorted queue).

5. **`compile_calc_def_body()`** at `spike_compile_expressions.py:418-523` — orchestrator that builds dependency graph, topologically sorts, compiles each output, and constructs the full function body with return statement.

### agentic-mbse Expression Utilities

Functions the compiler will call (not duplicate):

- `extract_feature_refs(expr, ignore_std_lib=True) -> list[ExpressionRef]` at `expression.py:119-222` — extracts all `FeatureReferenceExpression` and `FeatureChainExpression` refs. Returns `ExpressionRef` objects with `.name`, `.qualified_name`, `.element`.
- `extract_operators(expr) -> list[str]` at `expression.py:225-254` — extracts all operator strings from `OperatorExpression` nodes.
- `SysideAdapter.is_instance(node, type_name)` — duck-type checking for syside AST nodes.

### Key Data Type: CalculationDefinitionData

At `data_models.py:107-135`, provides:
- `name: str` — CalcDef name
- `input_attributes: list[AttributeInfo]` — each has `.name`, `.default_value`
- `output_attributes: list[AttributeInfo]` — each has `.name`
- `calc_expressions: list[str]` — existing text expression strings (not used by compiler; compiler works from ASTs)

The compiler receives `CalculationDefinitionData` objects but also needs access to raw syside elements for AST extraction (specifically `feature_value_expression` on output attributes, and `owned_members` for undeclared intermediate discovery). In Item 3, the compiler functions accept these as explicit parameters. In Item 4, the pipeline will be modified to pass raw ASTs via a new `output_expression_asts` field on `CalculationDefinitionData`.

---

## Proposed Design

### Architecture

Three files, two new and one modified:

```
extraction/
  expression_utils.py      NEW: shared AST-to-text utilities
  expression_compiler.py   NEW: data models + compiler functions
  constraint_extractor.py  MODIFIED: imports from expression_utils

tests/unit/
  test_expression_compiler.py  NEW: unit tests
```

The expression compiler has a clear two-phase design:

```
Phase 1: build_expression_ast()
  syside AST node → ExpressionAST (clean IR)
  - N-ary to binary left-fold conversion
  - Reference resolution (input vs intermediate vs undeclared vs unsupported)
  - Literal extraction
  - Unit annotation stripping

Phase 2: compile_expression()
  ExpressionAST → Python expression string
  - Input refs → "inputs.<name>"
  - Intermediate refs → bare "<name>"
  - Literals → str(value)
  - Binary ops → "(left op right)"
  - Unary ops → "(-operand)"
  - Unsupported → raises or returns sentinel

Orchestrator: compile_calc_def()
  (calc_def, expression_asts) → CalcDefCompilationResult
  - Builds dependency graph (outputs + undeclared intermediates)
  - Topological sort with cycle detection
  - Compiles each output/intermediate in order
  - Aggregates per-output results
  - Computes worst-case overall compilability
```

### Component 1: `extraction/expression_utils.py`

**Purpose:** Shared AST-to-text reconstruction logic, extracted from `constraint_extractor.py`.

**Public API:**

```python
# Constant
OPERATOR_MAP: dict[str, str]
# Same as current constraint_extractor.OPERATOR_MAP (lines 33-50)
# Used by constraint_extractor for SysML text reconstruction
# NOT used by expression_compiler (which has its own PYTHON_OPERATOR_MAP)

# Functions (names kept with leading underscore dropped since they're now module-level public)
def reconstruct_expression(expr_node: Any) -> str
def reconstruct_operator_expression(expr_node: Any) -> str
def extract_feature_reference_name(expr_node: Any) -> str
def extract_feature_chain_name(expr_node: Any) -> str
```

**Implementation notes:**
- Move the 5 items from `constraint_extractor.py` verbatim
- Drop leading underscores since they're now public module functions
- `constraint_extractor.py` imports them with the original `_` prefix for backward compatibility within that file: `from .expression_utils import reconstruct_expression as _reconstruct_expression`, etc.
- The `KEYWORDS` constant stays in `constraint_extractor.py` (only used by `_extract_referenced_variables` which is constraint-specific regex logic, not AST-based)

### Component 2: `extraction/expression_compiler.py`

**Purpose:** Expression compilation data models and functions.

#### Data Models

**`Compilability(str, Enum)`** — follows `EntryPointType` pattern at `resolution/models.py:22-33`:

```python
class Compilability(str, Enum):
    """Compilability verdict for a CalcDef or individual output expression.

    Determined by the expression compiler at Step 6.5 of the pipeline.
    UNKNOWN is the sentinel for modules that have not yet been compiled.
    """
    FULLY_COMPILABLE = "fully_compilable"
    PARTIALLY_COMPILABLE = "partially_compilable"
    MANUAL_REQUIRED = "manual_required"
    UNKNOWN = "unknown"
```

**`ExpressionNodeType(str, Enum)`**:

```python
class ExpressionNodeType(str, Enum):
    """Node types in the compiler's intermediate representation."""
    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    LITERAL = "literal"
    INPUT_REF = "input_ref"
    INTERMEDIATE_REF = "intermediate_ref"
    UNSUPPORTED = "unsupported"
```

**`ExpressionAST`** — `@dataclass`, not Pydantic (follows extraction-layer convention):

```python
@dataclass
class ExpressionAST:
    """Compiler's intermediate representation of a SysML expression.

    Constructed during compilation from syside AST nodes, used to produce
    a Python expression string, then discarded. Not stored long-term.

    Binary tree structure: n-ary syside OperatorExpressions are left-folded
    into nested binary nodes at construction time (build_expression_ast).
    """
    node_type: ExpressionNodeType
    operator: str | None = None          # BINARY_OP / UNARY_OP: "+", "-", "*", "/", "**"
    left: "ExpressionAST | None" = None  # BINARY_OP / UNARY_OP: left operand
    right: "ExpressionAST | None" = None # BINARY_OP: right operand (None for UNARY_OP)
    value: float | int | str | None = None       # LITERAL
    input_name: str | None = None        # INPUT_REF: "wattage"
    intermediate_name: str | None = None # INTERMEDIATE_REF: "material_cost"
    raw_text: str | None = None          # UNSUPPORTED: best-effort text
    reason: str | None = None            # UNSUPPORTED: why unsupported
```

**`CompilationResult`** — per-output result:

```python
@dataclass
class CompilationResult:
    """Result of compiling one output attribute's expression."""
    output_name: str
    compilability: Compilability
    python_expression: str | None = None
    input_refs: list[str] = field(default_factory=list)
    intermediate_refs: list[str] = field(default_factory=list)
    unsupported_reason: str | None = None
    is_undeclared_intermediate: bool = False  # True if this is a discovered member, not a declared output
```

**`CalcDefCompilationResult`** — aggregate result:

```python
@dataclass
class CalcDefCompilationResult:
    """Aggregate compilation result for an entire CalcDef.

    Carried alongside PipelineContext from Step 6.5 to generation.
    Keyed by calc_def.name so the generator can look up expression
    strings without them living on the resolution model.
    """
    calc_def_name: str
    overall_compilability: Compilability
    output_results: list[CompilationResult]
    execution_order: list[str]  # topological order including undeclared intermediates
```

#### Compiler Functions

**`PYTHON_OPERATOR_MAP`** — module-level constant, distinct from `expression_utils.OPERATOR_MAP`:

```python
PYTHON_OPERATOR_MAP: dict[str, str | None] = {
    "+": " + ",
    "-": " - ",
    "*": " * ",
    "/": " / ",
    "**": " ** ",
    "^": " ** ",     # SysML power alias → Python power
    "[": None,       # unit annotation → strip, use value operand
}
```

**`build_expression_ast(syside_node, input_names, output_names, all_member_names=None) -> ExpressionAST`**:

Converts a raw syside AST node into the clean `ExpressionAST` IR. This is the function where n-ary to binary left-folding happens.

- **Input:** syside AST node (duck-typed), sets of known input/output/member names
- **Output:** `ExpressionAST` tree
- **Algorithm:**
  1. Check node type via `SysideAdapter.is_instance()`
  2. For `OperatorExpression`:
     - Extract operator string and operands list
     - If operator is `[` (unit annotation): recurse on value operand (first), ignore unit operand
     - If 1 operand: `UNARY_OP` node
     - If 2 operands: `BINARY_OP` node with left/right recursion
     - If >2 operands: **left-fold** — recursively build `BINARY_OP(BINARY_OP(op[0], op[1]), op[2])` etc.
     - If operator not in `PYTHON_OPERATOR_MAP`: `UNSUPPORTED` node
  3. For `FeatureReferenceExpression`:
     - Extract name via `expression_utils.extract_feature_reference_name()` (the expression compiler does NOT define its own feature reference name extraction — it delegates to the shared utility, consolidating the spike script's `_extract_feature_ref_name` which is NOT carried forward)
     - If name in `input_names`: `INPUT_REF` node
     - If name in `output_names`: `INTERMEDIATE_REF` node (declared output used as intermediate)
     - If name in `all_member_names`: `INTERMEDIATE_REF` node (undeclared intermediate)
     - Otherwise: `UNSUPPORTED` node with reason `"unresolved reference: {name}"`
  4. For `LiteralRational` / `LiteralInteger` / `LiteralReal`: `LITERAL` node with `value=node.value`
  5. For `FeatureChainExpression`: `UNSUPPORTED` node with reason `"feature chain expression not supported in CalcDef output"`
  6. For anything else: `UNSUPPORTED` node with reason `"unknown node type: {type_name}"`

**`compile_expression(ast: ExpressionAST) -> str`**:

Converts `ExpressionAST` to Python expression string. Pure recursive descent on the IR — no syside dependency.

- `BINARY_OP`: `f"({compile(left)}{PYTHON_OPERATOR_MAP[op]}{compile(right)})"`
- `UNARY_OP`: `f"(-{compile(left)})"` (only `-` supported as unary)
- `LITERAL`: `str(value)`
- `INPUT_REF`: `f"inputs.{input_name}"`
- `INTERMEDIATE_REF`: `intermediate_name` (bare)
- `UNSUPPORTED`: raises `CompilationError` (a simple Exception subclass)

**`CompilationError`** — simple exception for unsupported nodes encountered during compilation:

```python
class CompilationError(Exception):
    """Raised when an ExpressionAST contains UNSUPPORTED nodes."""
    pass
```

**`classify_compilability(output_results: list[CompilationResult]) -> Compilability`**:

Worst-case aggregation over a list of `CompilationResult` objects:

```python
def classify_compilability(output_results: list[CompilationResult]) -> Compilability:
    if not output_results:
        return Compilability.MANUAL_REQUIRED
    if all(r.compilability == Compilability.FULLY_COMPILABLE for r in output_results):
        return Compilability.FULLY_COMPILABLE
    if any(r.compilability == Compilability.MANUAL_REQUIRED for r in output_results):
        return Compilability.MANUAL_REQUIRED
    return Compilability.PARTIALLY_COMPILABLE
```

**`compile_calc_def(calc_def, expression_asts, all_member_names=None, member_expressions=None) -> CalcDefCompilationResult`**:

The orchestrator. Takes a `CalculationDefinitionData`, a dict of output-name → syside AST, and optional undeclared intermediate discovery context.

- **Parameters:**
  - `calc_def: CalculationDefinitionData` — structured CalcDef with `input_attributes`, `output_attributes`
  - `expression_asts: dict[str, Any]` — keyed by output attribute name, values are raw syside AST nodes (or `None` if no expression)
  - `all_member_names: set[str] | None` — all `owned_member` names from raw CalcDef element, for undeclared intermediate resolution
  - `member_expressions: dict[str, Any] | None` — mapping from member name → syside AST for undeclared intermediates

- **Algorithm:**
  1. Build name sets: `input_names`, `output_names`
  2. Build dependency graph:
     - For each output, extract refs using `extract_feature_refs()` from agentic-mbse
     - For each ref, classify as input (skip), output (dependency edge), or undeclared intermediate (discover + add node)
     - Recursively discover undeclared intermediate chains (intermediates that reference other intermediates)
  3. Topological sort via Kahn's algorithm with deterministic tie-breaking (`sorted()` on queue)
  4. If cycle detected: return `CalcDefCompilationResult` with `MANUAL_REQUIRED` and reason string
  5. For each name in topological order:
     - Get syside AST from `expression_asts` (declared outputs) or `member_expressions` (undeclared intermediates)
     - If no AST: create `CompilationResult` with `MANUAL_REQUIRED`
     - Otherwise: call `build_expression_ast()` then `compile_expression()`, handle `CompilationError`
     - Record `input_refs` and `intermediate_refs` on the result
     - Mark `is_undeclared_intermediate` for non-declared outputs
  6. Compute `overall_compilability` via `classify_compilability()`
  7. Return `CalcDefCompilationResult`

- **Return statement logic:** The `execution_order` on `CalcDefCompilationResult` includes all names (declared outputs + undeclared intermediates) in topological order. The `is_undeclared_intermediate` flag on individual `CompilationResult` entries tells the generator which names to include in the `return` statement (only declared outputs) vs. which to emit as local-only variable assignments.

### Component 3: Modified `constraint_extractor.py`

**Changes:**
1. Remove `OPERATOR_MAP` constant (moved to `expression_utils.py`)
2. Remove `_reconstruct_expression()`, `_reconstruct_operator_expression()`, `_extract_feature_reference_name()`, `_extract_feature_chain_name()` function bodies
3. Add imports at top of file:
   ```python
   from .expression_utils import (
       OPERATOR_MAP,
       reconstruct_expression as _reconstruct_expression,
       reconstruct_operator_expression as _reconstruct_operator_expression,
       extract_feature_reference_name as _extract_feature_reference_name,
       extract_feature_chain_name as _extract_feature_chain_name,
   )
   ```
4. All call sites within `constraint_extractor.py` remain unchanged (they still call `_reconstruct_expression(...)`, etc.) because the imports use `as` aliases.

**Risk mitigation:** No test files exist for `constraint_extractor.py` directly, but the overall test suite exercises constraint extraction indirectly. The refactor is a pure move + import — no logic changes.

### Component 4: `tests/unit/test_expression_compiler.py`

**Test strategy:** All tests construct `ExpressionAST` objects directly — no syside dependency. This makes the tests fast, deterministic, and isolated.

**Test organization:**

```python
class TestCompilability:
    """Tests for Compilability enum."""
    # Verify enum values, str inheritance, UNKNOWN sentinel

class TestExpressionNodeType:
    """Tests for ExpressionNodeType enum."""
    # Verify enum values, str inheritance

class TestBuildExpressionAST:
    """Tests for build_expression_ast() syside→IR conversion."""
    # Pattern A: simple binary (2 operands)
    # Pattern C: nested parenthesized with **
    # Pattern D: literal + input ref mix
    # Pattern F: unit annotation stripping ([ operator)
    # N-ary 3-operand left-fold
    # N-ary 7-operand left-fold
    # Unary negation
    # FeatureChainExpression → UNSUPPORTED
    # Unknown node type → UNSUPPORTED
    # Unresolved reference → UNSUPPORTED

class TestCompileExpression:
    """Tests for compile_expression() IR→Python."""
    # INPUT_REF → "inputs.<name>"
    # INTERMEDIATE_REF → bare "<name>"
    # LITERAL → str(value)
    # BINARY_OP → "(left op right)"
    # UNARY_OP → "(-operand)"
    # UNSUPPORTED → CompilationError
    # Pattern A through F compiled output verification
    # Over-parenthesization: nested ops produce correct nesting

class TestCompileCalcDef:
    """Tests for compile_calc_def() orchestrator."""
    # Pattern B: multi-step intermediate with topological ordering
    # Pattern E: pi as repeated literal
    # Edge 1: unresolved reference → UNSUPPORTED, verdict escalation
    # Edge 2: circular intermediate → MANUAL_REQUIRED
    # Edge 3: missing AST for one output → partial compilability
    # Edge 4: unsupported operator → verdict escalation
    # Edge 5: FeatureChainExpression → MANUAL_REQUIRED
    # Undeclared intermediates: MagnetCryogenicLoad 4-intermediate pattern
    #   Test constructs: all_member_names as set[str] of all member names,
    #   member_expressions as dict[str, MockOperatorExpression] mapping each
    #   undeclared intermediate name to its mock AST. Both passed directly to
    #   compile_calc_def -- no syside model loading needed.
    # Undeclared intermediates excluded from return, included in execution_order
    # Overall compilability is worst-case

class TestClassifyCompilability:
    """Tests for classify_compilability() aggregation."""
    # All FULLY → FULLY
    # Mix of FULLY + MANUAL → MANUAL
    # Mix of FULLY + PARTIAL → PARTIAL
    # Empty list → MANUAL
```

**Mock syside nodes for `TestBuildExpressionAST`:** Since `build_expression_ast` takes raw syside nodes and uses `SysideAdapter.is_instance()`, the tests need lightweight mocks. The approach follows the spike scripts' duck-typing:

```python
class MockOperatorExpression:
    """Mock syside OperatorExpression node."""
    def __init__(self, operator: str, operands: list):
        self.operator = operator
        self.operands = operands

class MockFeatureReferenceExpression:
    """Mock syside FeatureReferenceExpression node."""
    def __init__(self, name: str):
        self.referent = SimpleNamespace(name=name)

class MockLiteralRational:
    """Mock syside LiteralRational node."""
    def __init__(self, value: float):
        self.value = value
```

These mocks need `SysideAdapter.is_instance()` to recognize them. Two options:
1. **Monkeypatch `SysideAdapter.is_instance`** to check class name instead of syside type hierarchy
2. **Test `build_expression_ast` through constructed `ExpressionAST` objects**, testing the syside→IR layer separately with an integration test

**Recommended:** Option 1 with a pytest fixture that monkeypatches `SysideAdapter.is_instance` to use `type(node).__name__` matching. This keeps the test isolated while exercising the real `build_expression_ast` logic. The monkeypatch fixture:

```python
@pytest.fixture
def mock_syside_adapter(monkeypatch):
    """Monkeypatch SysideAdapter.is_instance to work with mock nodes."""
    TYPE_MAP = {
        "MockOperatorExpression": "OperatorExpression",
        "MockFeatureReferenceExpression": "FeatureReferenceExpression",
        "MockLiteralRational": "LiteralRational",
        "MockFeatureChainExpression": "FeatureChainExpression",
    }
    def mock_is_instance(node, type_name):
        return TYPE_MAP.get(type(node).__name__) == type_name
    monkeypatch.setattr(
        "sysml_codegen.extraction.expression_compiler.SysideAdapter.is_instance",
        staticmethod(mock_is_instance),
    )
```

---

## Potential Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `constraint_extractor.py` refactor breaks existing functionality | Medium | Pure move+import refactor, no logic change. Full test suite run before/after. No dedicated constraint_extractor tests exist, but extraction is exercised by integration tests. |
| Mock syside nodes don't faithfully represent real syside behavior | Low | Mocks are based on actual syside patterns observed in spike scripts across 4 model suites (102 outputs). `build_expression_ast` only accesses `.operator`, `.operands`, `.referent.name`, `.value`, and `.memberships` — all validated by spike Item 1. |
| `ExpressionAST` binary tree doesn't accommodate future n-ary operators (e.g., ternary `if/else`) | Low | `SelectExpression` is explicitly out of scope. If added later, a new `ExpressionNodeType.TERNARY` or `CONDITIONAL` can be added with a `condition` field. The dataclass is easily extensible. |
| Undeclared intermediate discovery misses members in edge cases | Low | Spike Item 2 validated discovery via `owned_members` across all 4 model suites. The 3 CATF CalcDefs with undeclared intermediates (MagnetCryogenicLoad, VacuumPumpPower, CryoPumpRefrigeration) all compiled correctly. |
| `compile_calc_def` signature takes raw syside data alongside structured `CalculationDefinitionData` | Low | This is a deliberate design choice for Item 3 (standalone module). In Item 4, the pipeline integration will add `output_expression_asts` to `CalculationDefinitionData`, simplifying the call site. For now, the separate parameters make the module testable without pipeline changes. |

---

## Integration Strategy

### This Module's Boundaries

The expression compiler is a **leaf module** in the extraction layer. It:
- Imports from `extraction/expression_utils.py` (shared AST-to-text)
- Imports from `agentic_mbse.sysml.expression` (feature ref/operator extraction)
- Imports from `agentic_mbse.sysml.syside_adapter` (duck-type checking)
- Does NOT import from `analysis/`, `resolution/`, or `generation/`
- Does NOT modify any existing data models

### Item 4 Integration Points

When Item 4 wires this module into the pipeline, it will:
1. Add `output_expression_asts: dict[str, Any]` field to `CalculationDefinitionData` (`data_models.py`)
2. Call `compile_calc_def()` at Step 6.5 in `build_pipeline_context()` (`generation/initialization.py`)
3. Store `dict[str, CalcDefCompilationResult]` on `PipelineContext`
4. Add `compilability: Compilability` field to `PipelineModule` (`resolution/models.py`)
5. Use `CalcDefCompilationResult` in `stencils.py` to choose auto-impl vs stub template

The expression compiler module does not need to anticipate these changes. Its public API (`compile_calc_def`, `Compilability`, `CalcDefCompilationResult`) is designed for Item 4 consumption.

---

## Validation Approach

### Unit Tests (Item 3 scope)

- `uv run pytest tests/unit/test_expression_compiler.py` — all tests pass
- Coverage of all 6 expression patterns (A-F) and 6 edge cases
- N-ary left-fold verified for 3-operand and 7-operand cases
- Undeclared intermediate chain verified (4-intermediate MagnetCryogenicLoad pattern)
- Topological ordering verified (Pattern B: material_cost → fab_cost → total_cost)
- Circular dependency detection verified

### Type Checking

- `uv run mypy src/sysml_codegen/extraction/expression_compiler.py` — passes
- `uv run mypy src/sysml_codegen/extraction/expression_utils.py` — passes

### Regression

- `uv run pytest tests/` — all existing tests pass with zero regressions
- Specifically validates that the `constraint_extractor.py` refactor doesn't break anything

---

**Next Step:** After approval → `/_my_plan` for implementation task list, or `/_my_implement` for direct implementation.
