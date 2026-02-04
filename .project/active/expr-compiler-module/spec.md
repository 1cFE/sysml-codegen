# Spec: Expression Compiler Module

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-03 02:48 UTC
**Complexity:** MEDIUM
**Branch:** `cost-pattern`
**Epic:** EXPR-CODEGEN Item 3

---

## Business Goals

### Why This Matters

Items 1 and 2 proved that SysIDE expression ASTs are extractable (95.8% coverage, 92/96 outputs) and compilable to correct Python (0% false positives, exact 0.00e+00 numerical matches against 5 ground-truth CalcDefs). The codegen pipeline currently generates `NotImplementedError` stubs for every CalcDef -- even those whose math is fully expressed in SysML. This item turns validated spike logic into a production-quality, unit-tested module that Item 4 will wire into the pipeline to auto-generate implementations.

### Success Criteria

- [ ] `expression_compiler.py` exists in `extraction/` with 5 data models and 4 compiler functions
- [ ] `expression_utils.py` exists in `extraction/` with shared AST-to-text logic extracted from `constraint_extractor.py`
- [ ] `constraint_extractor.py` imports from `expression_utils.py` (no duplicated reconstruction logic)
- [ ] Unit tests pass: `uv run pytest tests/unit/test_expression_compiler.py`
- [ ] Type check passes: `uv run mypy src/sysml_codegen/extraction/expression_compiler.py`
- [ ] Existing `constraint_extractor` tests still pass after refactor
- [ ] All existing tests pass with zero regressions

### Priority

P1 -- gates Item 4 (pipeline integration) and Item 5 (E2E validation). Sequential dependency chain. Items 1 and 2 (research spikes) are complete with GO recommendations.

---

## Problem Statement

### Current State

- Every generated `_impl.py` contains `raise NotImplementedError(...)`. The "GAP" comment in every module wrapper acknowledges this.
- SysML expressions ARE extracted as text strings (`calc_expressions: list[str]`) but never compiled to executable Python.
- Expression reconstruction code exists in 3 places (`extractor._extract_expression_text`, `constraint_extractor._reconstruct_expression`, `agentic_mbse.sysml.expression`) but none produce executable Python suitable for `_impl.py` code generation.
- No `ExpressionAST` intermediate representation, `CompilationResult` data model, `Compilability` enum, or formal expression-to-Python compiler exists.

### Desired Outcome

A standalone expression compiler module in `extraction/` that:
1. Converts raw SysIDE AST nodes into a clean `ExpressionAST` intermediate representation
2. Compiles `ExpressionAST` to Python expression strings (e.g., `inputs.wattage * inputs.cost_per_watt`)
3. Classifies CalcDef compilability with zero false positives
4. Handles all expression patterns validated in the spikes (Patterns A-F)
5. Is fully unit-testable without syside dependency

Additionally, shared AST-to-text logic is consolidated from `constraint_extractor.py` into `expression_utils.py`, eliminating duplicated reconstruction code.

---

## Scope

### In Scope

- **Data models** in `expression_compiler.py`:
  - `Compilability(str, Enum)`: `FULLY_COMPILABLE`, `PARTIALLY_COMPILABLE`, `MANUAL_REQUIRED`, `UNKNOWN`
  - `ExpressionNodeType(str, Enum)`: `BINARY_OP`, `UNARY_OP`, `LITERAL`, `INPUT_REF`, `INTERMEDIATE_REF`, `UNSUPPORTED`
  - `ExpressionAST` dataclass using `ExpressionNodeType`
  - `CompilationResult` dataclass with `compilability: Compilability` field
  - `CalcDefCompilationResult` dataclass: aggregates per-output results, carries `overall_compilability`, `output_results`, and `execution_order`
- **Compiler functions** in `expression_compiler.py`:
  - `build_expression_ast(syside_node, input_names, output_names) -> ExpressionAST`
  - `compile_expression(ast: ExpressionAST) -> str`
  - `classify_compilability(output_results: list[CompilationResult]) -> Compilability`
  - `compile_calc_def(calc_def, expression_asts) -> CalcDefCompilationResult`
- **Expression utils extraction** to `expression_utils.py`:
  - Extract core recursive AST-to-text dispatcher, `OPERATOR_MAP`, and helper functions from `constraint_extractor.py`
  - Refactor `constraint_extractor.py` to import from `expression_utils.py`
- **Undeclared intermediate handling** (core requirement -- see FR-6)
- **Defensive unary negation handling** (not encountered in real models but trivial to include)
- **Unit tests** in `tests/unit/test_expression_compiler.py`

### Out of Scope

- Pipeline wiring -- no changes to `initialization.py`, `graph_builder.py`, `stencils.py`, or `resolution/models.py` (Item 4)
- Modifying `extractor.py` or `usage_extractor.py` (Item 4)
- Attribute expression handling / `ComputedAttributeData` (Phase 2)
- `InvocationExpression` / function call support
- `SelectExpression` / conditional expression support
- `math.pi` or named constant substitution (compiler faithfully reproduces literals per concept Section 3.7)
- Operator precedence optimization for minimal parenthesization (defensive over-parenthesization is correct and sufficient)

### Edge Cases & Considerations

- **Unresolved references** (Edge 1): Expression references a name not in declared inputs, outputs, or discoverable members. Verdict escalates to `PARTIALLY_COMPILABLE` or `MANUAL_REQUIRED`.
- **Circular intermediate references** (Edge 2): Two outputs reference each other. Topological sort detects cycle. Verdict: `MANUAL_REQUIRED`.
- **Missing AST** (Edge 3): `feature_value_expression` not populated for an output. That output gets `MANUAL_REQUIRED`. Other outputs in same CalcDef may still compile.
- **Unsupported operator** (Edge 4): Operator not in supported set (`+`, `-`, `*`, `/`, `**`, `^`→`**`, `[`→strip). Node becomes `UNSUPPORTED`.
- **FeatureChainExpression in CalcDef output** (Edge 5): References like `subsystem.value` in a CalcDef output. Verdict: `MANUAL_REQUIRED` (structured type input, not a scalar).
- **EXPOSE-with-operators** (Edge 6): Attribute expression with operators is a computed attribute, not a pure EXPOSE. Relevant for Phase 2 classification; the compiler itself handles the expression normally.

---

## Requirements

### Functional Requirements

> Requirements below are from user's request and epic unless marked [INFERRED].

1. **FR-1: Compilability Enum**: The compiler MUST define `Compilability(str, Enum)` with values `FULLY_COMPILABLE`, `PARTIALLY_COMPILABLE`, `MANUAL_REQUIRED`, and `UNKNOWN`. The `UNKNOWN` value is the default-before-compilation sentinel (needed when `PipelineModule.compilability` is set at construction time in Step 7, before Step 6.5 runs). It is not part of the concept's three-verdict classification but is required as a construction default.

2. **FR-2: ExpressionNodeType Enum**: The compiler MUST define `ExpressionNodeType(str, Enum)` with values `BINARY_OP`, `UNARY_OP`, `LITERAL`, `INPUT_REF`, `INTERMEDIATE_REF`, `UNSUPPORTED`. No bare strings for node types.

3. **FR-3: ExpressionAST Intermediate Representation**: The compiler MUST define an `ExpressionAST` dataclass as a clean, testable IR that decouples compilation logic from syside's opaque AST nodes. The IR uses binary tree structure (`left`, `right` children) even though syside emits n-ary nodes (see FR-5). Fields:
   - `node_type: ExpressionNodeType`
   - `operator: str | None` -- for `BINARY_OP` / `UNARY_OP`
   - `left: ExpressionAST | None`, `right: ExpressionAST | None` -- `right` is None for unary
   - `value: float | int | str | None` -- for `LITERAL`
   - `input_name: str | None` -- for `INPUT_REF`
   - `intermediate_name: str | None` -- for `INTERMEDIATE_REF`
   - `raw_text: str | None`, `reason: str | None` -- for `UNSUPPORTED`

4. **FR-4: CompilationResult and CalcDefCompilationResult**: The compiler MUST define:
   - `CompilationResult` dataclass: per-output result with `output_name`, `compilability`, `python_expression`, `input_refs`, `intermediate_refs`, `unsupported_reason`, `is_undeclared_intermediate`.
   - `CalcDefCompilationResult` dataclass: aggregate result with `calc_def_name`, `overall_compilability` (worst-case across outputs), `output_results: list[CompilationResult]`, `execution_order: list[str]` (topological order of outputs including undeclared intermediates).

5. **FR-5: N-ary to Binary Conversion**: The compiler MUST handle `OperatorExpression` nodes with >2 operands by left-folding into nested binary applications of the operator. The conversion from n-ary to binary MUST happen at AST construction time (`build_expression_ast`), not at code emission time. The `ExpressionAST` IR always uses binary nodes. This is a correctness boundary: SysIDE represents `a + b + c` as a single `OperatorExpression` with 3 operands, not as nested binary trees. Without left-folding, 15+ real CalcDef outputs would produce incorrect results (the most dramatic being `NetElectricPower.p_parasitic_total`, a 7-input sum at depth 6).

6. **FR-6: Undeclared Intermediate Discovery and Emission**: The compiler MUST discover undeclared CalcDef members referenced in output expressions (members not in `input_attributes` or `output_attributes`), compile their expressions, include them in topological ordering, and emit them as local variable assignments (not in the return statement). This is required for 3 CATF CalcDefs (MagnetCryogenicLoad with 4 undeclared intermediates, VacuumPumpPower with 1, CryoPumpRefrigeration with 1). Without this, those CalcDefs drop from `FULLY_COMPILABLE` to `PARTIALLY_COMPILABLE` or `MANUAL_REQUIRED` -- a 14% regression on CATF coverage.

7. **FR-7: Topological Ordering**: The compiler MUST topologically sort outputs (both declared and undeclared intermediates) within a CalcDef by their dependencies. Outputs that reference sibling outputs MUST be emitted after their dependencies. Circular dependencies MUST be detected and result in `MANUAL_REQUIRED` verdict.

8. **FR-8: Operator Set**: The compiler MUST support the 5 operators validated in the spikes: `+`, `-`, `*`, `/`, `**`. The `^` operator MUST be treated as an alias for `**`. The `[` operator (unit annotation) MUST be handled by stripping the unit and using the value operand only.

9. **FR-9: Defensive Unary Negation**: The compiler MUST handle unary negation (`OperatorExpression` with 1 operand and operator `-`) by emitting `(-operand)`. [INFERRED] This was not encountered in any of the 102 outputs across 4 model suites, but the implementation is trivial and the concept's `ExpressionAST` already includes `UNARY_OP`.

10. **FR-10: Defensive Over-Parenthesization**: The compiler MUST wrap every binary expression in parentheses: `(left op right)`. This is safe (Python ignores redundant parentheses) and produces correct results for all nesting depths tested (up to depth 6).

11. **FR-11: Expression Utils Extraction**: Shared AST-to-text logic MUST be extracted from `constraint_extractor.py` into `expression_utils.py`. Specifically: `_reconstruct_expression()`, `_reconstruct_operator_expression()`, `_extract_feature_reference_name()`, `_extract_feature_chain_name()`, and `OPERATOR_MAP`. After extraction, `constraint_extractor.py` MUST import these from `expression_utils.py`. No duplicated reconstruction logic.

12. **FR-12: LiteralRational Handling**: `LiteralRational.value` is a Python `float` in syside's API. The compiler MUST emit `str(node.value)` to produce correct Python numeric literals. No string-to-float conversion needed.

13. **FR-13: Input Reference Prefixing**: For `INPUT_REF` nodes, the compiler MUST emit `inputs.<param_name>` to align with the existing `_impl.py` function signature pattern where inputs arrive as a Pydantic model attribute.

14. **FR-14: Intermediate Reference Bare Names**: For `INTERMEDIATE_REF` nodes (both declared outputs and undeclared intermediates), the compiler MUST emit the bare variable name (e.g., `material_cost`, not `inputs.material_cost`), since these are local variables in the generated function body.

15. **FR-15: Overall Compilability is Worst-Case**: `classify_compilability(output_results)` MUST return the worst-case `Compilability` across a list of `CompilationResult` objects. It is a pure aggregation function -- it does not access `CalculationDefinitionData` or expression ASTs. `CalcDefCompilationResult.overall_compilability` is set by calling this function on the output results. If any output is `MANUAL_REQUIRED`, the overall verdict is `MANUAL_REQUIRED`. If any is `PARTIALLY_COMPILABLE` (and none are `MANUAL_REQUIRED`), the overall is `PARTIALLY_COMPILABLE`.

16. **FR-16: No Pipeline Dependencies**: The expression compiler module MUST NOT import from `analysis/`, `resolution/`, or `generation/`. It MAY import from `extraction/expression_utils.py` and from `agentic_mbse.sysml.expression` for semantic analysis utilities (`extract_feature_refs`, `extract_operators`).

---

## Acceptance Criteria

### Core Functionality

- [ ] `Compilability` enum has 4 values: `FULLY_COMPILABLE`, `PARTIALLY_COMPILABLE`, `MANUAL_REQUIRED`, `UNKNOWN`
- [ ] `ExpressionNodeType` enum has 6 values: `BINARY_OP`, `UNARY_OP`, `LITERAL`, `INPUT_REF`, `INTERMEDIATE_REF`, `UNSUPPORTED`
- [ ] `ExpressionAST` dataclass uses `ExpressionNodeType` (not bare strings)
- [ ] `CompilationResult` uses `Compilability` (no separate "verdict" terminology)
- [ ] `CalcDefCompilationResult` carries `execution_order` with topological ordering
- [ ] `build_expression_ast` left-folds n-ary `OperatorExpression` nodes into binary `ExpressionAST` nodes
- [ ] `compile_expression` produces Python expression strings with `inputs.` prefix on input refs and bare names on intermediate refs
- [ ] `compile_expression` uses defensive over-parenthesization
- [ ] `compile_calc_def` discovers undeclared intermediates, compiles them, emits as local variables, excludes from return
- [ ] `classify_compilability` returns worst-case verdict across all outputs
- [ ] Circular dependency detection produces `MANUAL_REQUIRED`

### Expression Patterns (Unit Tests)

- [ ] Pattern A: Simple binary (`area = inputs.length * inputs.width`)
- [ ] Pattern B: Multi-step intermediate with topological ordering (`material_cost` before `fab_cost` before `total_cost`)
- [ ] Pattern C: Complex parenthesized with `**` operator (CRF formula)
- [ ] Pattern D: Literals mixed with input refs (`inputs.p_fusion * 3.52 / 17.58`)
- [ ] Pattern E: Pi as repeated literal (faithful reproduction, no `math.pi` substitution)
- [ ] Pattern F: Unit-annotated literal (`[` operator stripped, value preserved)

### Edge Cases (Unit Tests)

- [ ] Edge 1: Unresolved reference -> `UNSUPPORTED` node, verdict escalation
- [ ] Edge 2: Circular intermediate -> `MANUAL_REQUIRED` with descriptive reason
- [ ] Edge 3: Missing AST for one output -> that output `MANUAL_REQUIRED`, others may still compile
- [ ] Edge 4: Unsupported operator -> `UNSUPPORTED` node, verdict escalation
- [ ] Edge 5: `FeatureChainExpression` in CalcDef output -> `MANUAL_REQUIRED`
- [ ] Edge 6: EXPOSE-with-operators -> handled as normal expression (operators present means not a passthrough)

### N-ary and Special Cases (Unit Tests)

- [ ] 3-operand `OperatorExpression` left-folds correctly: `a + b + c` -> `((a + b) + c)`
- [ ] 7-operand `OperatorExpression` left-folds correctly (NetElectricPower pattern)
- [ ] Unary negation: `-(x)` produces `(-inputs.x)`
- [ ] Undeclared intermediates: 4-intermediate chain (MagnetCryogenicLoad pattern) with correct topological ordering and local variable emission

### Expression Utils Extraction

- [ ] `expression_utils.py` exists in `extraction/` with `OPERATOR_MAP`, `_reconstruct_expression`, and helper functions
- [ ] `constraint_extractor.py` imports from `expression_utils.py`
- [ ] Existing `constraint_extractor` tests pass unchanged

### Quality & Integration

- [ ] `uv run pytest tests/unit/test_expression_compiler.py` passes
- [ ] `uv run mypy src/sysml_codegen/extraction/expression_compiler.py` passes
- [ ] `uv run mypy src/sysml_codegen/extraction/expression_utils.py` passes
- [ ] All existing tests pass with zero regressions (`uv run pytest tests/`)
- [ ] No imports from `analysis/`, `resolution/`, or `generation/` in the new modules

---

## Related Artifacts

- **Research (Item 1):** `.project/active/expr-spike-ast/report.md`
- **Research (Item 2):** `.project/active/expr-spike-compile/report.md`
- **Concept:** `.project/concepts/expression-aware-codegen.md`
- **Epic:** `.project/backlog/epic_expression_aware_codegen.md`
- **Spike scripts:** `scripts/spike_compile_expressions.py`, `scripts/spike_classify_compilability.py`
- **Design:** `.project/active/expr-compiler-module/design.md` (to be created)

---

## Deliverables

- `src/sysml_codegen/extraction/expression_compiler.py`
- `src/sysml_codegen/extraction/expression_utils.py`
- Modified: `src/sysml_codegen/extraction/constraint_extractor.py` (imports from `expression_utils`)
- `tests/unit/test_expression_compiler.py`

---

**Next Steps:** After approval, proceed to `/_my_design`
