"""C04: Expression Compiler conformance tests.

Verifies that the expression compiler conforms to REQ-EC-01 through REQ-EC-07
and REQ-AST-01 from design intent docs 14-expression-compiler.md and
19-ast-dispatch-invariant.md.

Testing strategy:
- Pure renderer functions (render_calc_expression, collect_calc_refs,
  classify_compilability) tested with constructed ExpressionIR trees -- no mocks needed
  (CONSTRAINT-EXEC Item 13 re-anchored these from the retired ExpressionAST suite).
- SysIDE-dependent functions (compile_calc_def) tested with mock SysIDE adapter --
  acceptable per Ground Rule 1.
- Cross-model validation uses real calc def metadata (names, attributes) from
  extraction snapshots with mock ASTs.

Requirements: REQ-EC-01 through REQ-EC-07, REQ-AST-01.
"""

from __future__ import annotations

import ast as python_ast
from types import SimpleNamespace
from uuid import UUID

import pytest
from agentic_mbse.sysml import expression as shared_expression

from sysml_codegen.extraction import expression_utils as expression_utils_shim
from sysml_codegen.extraction.calc_compat_renderer import (
    render_calc_expression,
)
from sysml_codegen.extraction.expression_compiler import (
    Compilability,
    CompilationError,
    CompilationResult,
    classify_compilability,
)

# ---------------------------------------------------------------------------
# ExpressionIR construction helpers (render_calc_expression/collect_calc_refs fixtures)
# ---------------------------------------------------------------------------


def _ir_ref(name: str):
    from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, OperandTypeFact
    from agentic_mbse.sysml.expression_ir import FeatureReferenceNode

    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _ir_literal(value):
    from agentic_mbse.sysml.expression_facts import LiteralFact, OperandTypeFact
    from agentic_mbse.sysml.expression_ir import LiteralNode

    if isinstance(value, int):
        kind, category = "LiteralInteger", "integer"
    else:
        kind, category = "LiteralRational", "real"
    return LiteralNode(
        literal=LiteralFact(kind=kind, value=value, result_type=None),
        operand_type=OperandTypeFact(category=category, enumeration=None, unit=None),
    )


def _ir_binary(op: str, left, right):
    from agentic_mbse.sysml.expression_ir import OperatorNode

    return OperatorNode(operator=op, operands=[left, right], operand_type=None)


def _ir_unary(op: str, operand):
    from agentic_mbse.sysml.expression_ir import OperatorNode

    return OperatorNode(operator=op, operands=[operand], operand_type=None)


def _ir_nary(op: str, *ref_names: str):
    from agentic_mbse.sysml.expression_ir import OperatorNode

    return OperatorNode(operator=op, operands=[_ir_ref(n) for n in ref_names], operand_type=None)


def _ir_unit(value):
    from agentic_mbse.sysml.expression_facts import OperandTypeFact
    from agentic_mbse.sysml.expression_ir import UnitAnnotationNode

    return UnitAnnotationNode(
        value=value,
        unit_text="kg",
        operand_type=OperandTypeFact(category="quantity", enumeration=None, unit=None),
    )


def _ir_unsupported(source_text: str, diagnostic: str):
    from agentic_mbse.sysml.expression_ir import UnsupportedNode

    return UnsupportedNode(node_kind="Mock", diagnostic=diagnostic, source_text=source_text)


# ---------------------------------------------------------------------------
# Mock infrastructure (SysIDE adapter boundary stubs -- Ground Rule 1)
# ---------------------------------------------------------------------------


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


class MockFeatureChainExpression:
    """Mock syside FeatureChainExpression node."""

    pass


@pytest.fixture
def mock_syside_adapter(monkeypatch):
    """Monkeypatch SysideAdapter.is_instance to work with mock nodes."""
    type_map = {
        "MockOperatorExpression": "OperatorExpression",
        "MockFeatureReferenceExpression": "FeatureReferenceExpression",
        "MockLiteralRational": "LiteralRational",
        "MockFeatureChainExpression": "FeatureChainExpression",
    }

    def mock_is_instance(node, type_name):
        return type_map.get(type(node).__name__) == type_name

    monkeypatch.setattr(
        "agentic_mbse.sysml.syside_adapter.SysideAdapter.is_instance",
        staticmethod(mock_is_instance),
    )


@pytest.fixture
def mock_extract_feature_refs(monkeypatch):
    """Monkeypatch extract_feature_refs to return pre-computed refs."""
    ref_map: dict[int, list[str]] = {}

    def mock_efr(expr, ignore_std_lib=True):
        names = ref_map.get(id(expr), [])
        return [SimpleNamespace(name=n, qualified_name=n, element=None) for n in names]

    monkeypatch.setattr(
        "sysml_codegen.extraction.expression_compiler.extract_feature_refs",
        mock_efr,
    )
    return ref_map




# ---------------------------------------------------------------------------
# REQ-EC-01 retired (CONSTRAINT-EXEC Item 13): its FCE-before-OE dispatch tests exercised
# build_expression_ast directly. That raw-node dispatch responsibility moved cross-repo to
# agentic-mbse's extract_expression_ir (its own tests); REQ-AST-01 in
# test_ast_dispatch_invariant.py still audits every remaining in-repo dual-check site.
# ---------------------------------------------------------------------------
# REQ-EC-02: N-ary left-fold
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EC-02")
class TestReqEc02NaryLeftFold:
    """N-ary operators render as left-folded binary parenthesization (re-anchored from the
    retired build_expression_ast fold-structure suite onto render_calc_expression fed IR
    directly -- CONSTRAINT-EXEC Item 13; agentic-mbse's extract_expression_ir does the actual
    n-ary OperatorNode construction now, covered by its own tests)."""

    def test_3_operand_left_fold_structure(self):
        """3 operands → ((a + b) + c)."""
        ir = _ir_nary("+", "a", "b", "c")
        assert render_calc_expression(ir, {"a", "b", "c"}, set()) == (
            "((inputs.a + inputs.b) + inputs.c)"
        )

    def test_7_operand_left_fold_structure(self):
        """7 operands → 6 levels of nesting, all left-associated."""
        names = [f"p{i}" for i in range(1, 8)]
        ir = _ir_nary("+", *names)
        compiled = render_calc_expression(ir, set(names), set())
        expected = (
            "((((((inputs.p1 + inputs.p2) + inputs.p3)"
            " + inputs.p4) + inputs.p5) + inputs.p6) + inputs.p7)"
        )
        assert compiled == expected

    def test_2_operand_not_folded(self):
        """2 operands → single binary node, no extra nesting."""
        ir = _ir_binary("*", _ir_ref("x"), _ir_ref("y"))
        assert render_calc_expression(ir, {"x", "y"}, set()) == "(inputs.x * inputs.y)"


# ---------------------------------------------------------------------------
# REQ-EC-03: Unit annotation stripping
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EC-03")
class TestReqEc03UnitStripping:
    """Unit annotations wrap a value node; the renderer strips to the value only
    (re-anchored onto render_calc_expression fed a UnitAnnotationNode -- CONSTRAINT-EXEC
    Item 13). The old no-operands-unsupported case tested build_expression_ast's raw-node
    dispatch shape, which moved cross-repo with the extractor; a UnitAnnotationNode's
    `value` field is non-optional by construction, so that case has no IR analogue here."""

    def test_unit_annotation_strips_unit_preserves_value(self):
        """A unit-annotated literal renders as just the value."""
        ir = _ir_unit(_ir_literal(42.0))
        assert render_calc_expression(ir, set(), set()) == "42.0"


# ---------------------------------------------------------------------------
# REQ-EC-04: ast.parse() validation
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EC-04")
class TestReqEc04AstParseValidation:
    """Every rendered expression must validate via ast.parse() (re-anchored onto
    render_calc_expression fed IR -- CONSTRAINT-EXEC Item 13)."""

    def test_all_renderable_node_kinds_produce_parseable_python(self):
        """Render one expression from each renderable node kind → ast.parse succeeds."""
        input_names = {"a", "b", "x", "voltage"}
        member_names = {"material_cost"}
        test_cases = {
            "BINARY_OP": _ir_binary("+", _ir_ref("a"), _ir_ref("b")),
            "UNARY_OP": _ir_unary("-", _ir_ref("x")),
            "LITERAL": _ir_literal(3.14),
            "INPUT_REF": _ir_ref("voltage"),
            "INTERMEDIATE_REF": _ir_ref("material_cost"),
        }
        for label, ir in test_cases.items():
            result = render_calc_expression(ir, input_names, member_names)
            python_ast.parse(result, mode="eval")

    def test_complex_nested_expression_parseable(self):
        """CRF-pattern (Pattern C) nested expression → ast.parse succeeds."""
        one_plus_r = _ir_binary("+", _ir_literal(1.0), _ir_ref("r"))
        power_term = _ir_binary("**", one_plus_r, _ir_ref("n"))
        numerator = _ir_binary("*", _ir_ref("r"), power_term)
        denominator = _ir_binary(
            "-",
            _ir_binary("**", _ir_binary("+", _ir_literal(1.0), _ir_ref("r")), _ir_ref("n")),
            _ir_literal(1.0),
        )
        crf = _ir_binary("/", numerator, denominator)
        result = render_calc_expression(crf, {"r", "n"}, set())
        python_ast.parse(result, mode="eval")

    def test_unsupported_node_raises_compilation_error(self):
        """UnsupportedNode → CompilationError (not invalid Python)."""
        ir = _ir_unsupported("foo.bar", "not supported")
        with pytest.raises(CompilationError):
            render_calc_expression(ir, set(), set())

    def test_internal_gate_raises_on_invalid_emitted_python(self):
        """A binary operator absent from the renderer's operator map raises
        CompilationError before any caller-side ast.parse() would even run -- there is no
        caller here, only the direct call to render_calc_expression."""
        ir = _ir_binary("~~", _ir_ref("a"), _ir_ref("b"))
        with pytest.raises(CompilationError, match="unsupported operator"):
            render_calc_expression(ir, {"a", "b"}, set())



# ---------------------------------------------------------------------------
# REQ-EC-06: Worst-case roll-up
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EC-06")
class TestReqEc06WorstCaseRollup:
    """CalcDef compilability is worst-case across all output results."""

    def test_rollup_all_fully_returns_fully(self):
        """[FULLY, FULLY] → FULLY."""
        results = [
            CompilationResult(UUID(int=1), "a", Compilability.FULLY_COMPILABLE, "expr_a"),
            CompilationResult(UUID(int=2), "b", Compilability.FULLY_COMPILABLE, "expr_b"),
        ]
        assert classify_compilability(results) == Compilability.FULLY_COMPILABLE

    def test_rollup_any_manual_returns_manual(self):
        """[FULLY, MANUAL] → MANUAL."""
        results = [
            CompilationResult(UUID(int=1), "a", Compilability.FULLY_COMPILABLE, "expr_a"),
            CompilationResult(UUID(int=2), "b", Compilability.MANUAL_REQUIRED),
        ]
        assert classify_compilability(results) == Compilability.MANUAL_REQUIRED

    def test_rollup_mixed_returns_partially(self):
        """[FULLY, PARTIALLY] → PARTIALLY."""
        results = [
            CompilationResult(UUID(int=1), "a", Compilability.FULLY_COMPILABLE, "expr_a"),
            CompilationResult(UUID(int=2), "b", Compilability.PARTIALLY_COMPILABLE, "expr_b"),
        ]
        assert classify_compilability(results) == Compilability.PARTIALLY_COMPILABLE

    def test_rollup_empty_returns_manual(self):
        """[] → MANUAL."""
        assert classify_compilability([]) == Compilability.MANUAL_REQUIRED

    def test_rollup_unknown_raises_assertion(self):
        """[UNKNOWN] → AssertionError (UNKNOWN is sentinel, not valid result)."""
        results = [CompilationResult(UUID(int=1), "a", Compilability.UNKNOWN)]
        with pytest.raises(AssertionError, match="UNKNOWN"):
            classify_compilability(results)



# ---------------------------------------------------------------------------
# REQ-AST-01: FCE before OE dispatch ordering (static analysis)
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-AST-01")
class TestReqAst01DispatchOrdering:
    """Static analysis: FCE checked before OE at every dispatch site.

    The expression_compiler.py dispatch-ordering case retired (CONSTRAINT-EXEC Item 13):
    build_expression_ast is gone, its dispatch responsibility moved cross-repo to
    agentic-mbse's extract_expression_ir. test_ast_dispatch_invariant.py's REQ-AST-01 still
    audits every remaining in-repo dual-check site.
    """

    def test_expression_utils_delegates_reconstruction_to_shared_api(self):
        """expression_utils.py keeps the compatibility path, not the moved body."""
        assert (
            expression_utils_shim.reconstruct_expression is shared_expression.reconstruct_expression
        )
