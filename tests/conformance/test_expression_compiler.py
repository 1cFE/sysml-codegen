"""C04: Expression Compiler conformance tests.

Verifies that the expression compiler conforms to REQ-EC-01 through REQ-EC-07
and REQ-AST-01 from design intent docs 14-expression-compiler.md and
19-ast-dispatch-invariant.md.

Testing strategy:
- Pure renderer functions and ``classify_compilability`` use constructed ExpressionIR trees.
- Cross-model validation uses real calculation metadata from live extraction; those nodes are
  license-gated by the fixture.
- The sole compiler core is covered by ``test_exact_compiler_core.py``.

Requirements: REQ-EC-01 through REQ-EC-07, REQ-AST-01.
"""

from __future__ import annotations

import ast as python_ast

import pytest
from agentic_mbse.sysml import expression as shared_expression

from sysml_codegen.extraction import expression_utils as expression_utils_shim
from sysml_codegen.extraction.calc_compat_renderer import (
    render_calc_expression,
)
from sysml_codegen.extraction.expression_compiler import (
    Compilability,
    CompilationError,
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


def _extract_name_sets(calc_def):
    """Derive input/output attribute name sets from a snapshot CalculationDefinitionData."""
    input_names = {a.name for a in calc_def.input_attributes}
    output_names = {a.name for a in calc_def.output_attributes}
    return input_names, output_names
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
        verdicts = [
            Compilability.FULLY_COMPILABLE,
            Compilability.FULLY_COMPILABLE,
        ]
        assert classify_compilability(verdicts) == Compilability.FULLY_COMPILABLE

    def test_rollup_any_manual_returns_manual(self):
        """[FULLY, MANUAL] → MANUAL."""
        verdicts = [
            Compilability.FULLY_COMPILABLE,
            Compilability.MANUAL_REQUIRED,
        ]
        assert classify_compilability(verdicts) == Compilability.MANUAL_REQUIRED

    def test_rollup_mixed_returns_partially(self):
        """[FULLY, PARTIALLY] → PARTIALLY."""
        verdicts = [
            Compilability.FULLY_COMPILABLE,
            Compilability.PARTIALLY_COMPILABLE,
        ]
        assert classify_compilability(verdicts) == Compilability.PARTIALLY_COMPILABLE

    def test_rollup_empty_returns_manual(self):
        """[] → MANUAL."""
        assert classify_compilability([]) == Compilability.MANUAL_REQUIRED

    def test_rollup_unknown_raises_assertion(self):
        """[UNKNOWN] → AssertionError (UNKNOWN is sentinel, not valid result)."""
        verdicts = [Compilability.UNKNOWN]
        with pytest.raises(AssertionError, match="UNKNOWN"):
            classify_compilability(verdicts)


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


# ---------------------------------------------------------------------------
# Cross-model validation
# ---------------------------------------------------------------------------

CROSS_MODEL_IDS = ["solar_battery_model", "catf_mfe_model", "chain_spike_model"]


class TestCrossModelValidation:
    """Verify rendering behavior against real model metadata from live extraction."""

    @pytest.mark.req("REQ-EC-04")
    @pytest.mark.parametrize(
        "model_name",
        CROSS_MODEL_IDS,
        ids=["solar_battery", "catf_mfe", "chain_spike"],
    )
    def test_reference_resolution_with_real_attribute_names(
        self, live_extraction_facts, model_name
    ):
        """Build IR FRE nodes using real attribute names → verify correct classification
        (re-anchored onto render_calc_expression -- CONSTRAINT-EXEC Item 13; classification
        is now a render-time policy over caller-supplied name sets, not baked into the tree)."""
        snapshot = live_extraction_facts[model_name]
        for cd in snapshot["calc_defs"]:
            input_names, output_names = _extract_name_sets(cd)

            for name in input_names:
                ir = _ir_ref(name)
                rendered = render_calc_expression(ir, input_names, output_names)
                assert rendered == f"inputs.{name}", (
                    f"{model_name}/{cd.name}: input '{name}' rendered as {rendered!r}, "
                    f"expected 'inputs.{name}'"
                )

            for name in output_names:
                ir = _ir_ref(name)
                rendered = render_calc_expression(ir, input_names, output_names)
                assert rendered == name, (
                    f"{model_name}/{cd.name}: output '{name}' rendered as {rendered!r}, "
                    f"expected bare {name!r}"
                )
