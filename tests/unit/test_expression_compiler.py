"""Unit tests for the expression compiler module."""

from types import SimpleNamespace
from uuid import UUID

import pytest

# ---------------------------------------------------------------------------
# Phase 2: Data models + pure compiler functions
# ---------------------------------------------------------------------------


class TestCompilability:
    """Tests for Compilability enum."""

    def test_enum_values(self):
        from sysml_codegen.extraction.expression_compiler import Compilability

        assert Compilability.FULLY_COMPILABLE == "fully_compilable"
        assert Compilability.PARTIALLY_COMPILABLE == "partially_compilable"
        assert Compilability.MANUAL_REQUIRED == "manual_required"
        assert Compilability.UNKNOWN == "unknown"

    def test_str_inheritance(self):
        from sysml_codegen.extraction.expression_compiler import Compilability

        assert isinstance(Compilability.FULLY_COMPILABLE, str)

    def test_unknown_is_sentinel(self):
        """UNKNOWN is a construction default, not a compiler output."""
        from sysml_codegen.extraction.expression_compiler import Compilability

        assert Compilability.UNKNOWN == "unknown"
        assert Compilability.UNKNOWN != Compilability.FULLY_COMPILABLE


def _ir_ref(name: str):
    from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, OperandTypeFact
    from agentic_mbse.sysml.expression_ir import FeatureReferenceNode

    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _ir_chain_ref(name: str):
    """A FeatureReferenceNode with non-empty chain_segments (an unsupported feature chain)."""
    from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, OperandTypeFact
    from agentic_mbse.sysml.expression_ir import FeatureReferenceNode

    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=["a", "b"]
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


def _ir_unsupported(source_text: str, diagnostic: str):
    from agentic_mbse.sysml.expression_ir import UnsupportedNode

    return UnsupportedNode(node_kind="Mock", diagnostic=diagnostic, source_text=source_text)


class TestRenderCalcExpression:
    """Tests for render_calc_expression() ExpressionIR -> Python (re-anchored from the
    retired ExpressionAST-based compile_expression() dialect suite, CONSTRAINT-EXEC Item 13)."""

    def test_input_ref(self):
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        ir = _ir_ref("wattage")
        assert render_calc_expression(ir, {"wattage"}, set()) == "inputs.wattage"

    def test_intermediate_ref(self):
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        ir = _ir_ref("material_cost")
        assert render_calc_expression(ir, set(), {"material_cost"}) == "material_cost"

    def test_literal_float(self):
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        ir = _ir_literal(3.14)
        assert render_calc_expression(ir, set(), set()) == "3.14"

    def test_literal_int(self):
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        ir = _ir_literal(42)
        assert render_calc_expression(ir, set(), set()) == "42"

    def test_binary_op_over_parenthesized(self):
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        ir = _ir_binary("*", _ir_ref("length"), _ir_ref("width"))
        assert (
            render_calc_expression(ir, {"length", "width"}, set())
            == "(inputs.length * inputs.width)"
        )

    def test_unary_negation(self):
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        ir = _ir_unary("-", _ir_ref("x"))
        assert render_calc_expression(ir, {"x"}, set()) == "(-inputs.x)"

    def test_unary_plus_renders_as_identity(self):
        """Profile v2 admits unary sign, so `+x` preserves the operand."""
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        ir = _ir_unary("+", _ir_ref("x"))
        assert render_calc_expression(ir, {"x"}, set()) == "(+inputs.x)"

    def test_zero_operand_arithmetic_raises_compilation_error(self):
        from agentic_mbse.sysml.expression_ir import OperatorNode

        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression
        from sysml_codegen.extraction.expression_compiler import CompilationError

        ir = OperatorNode(operator="+", operands=[], operand_type=None)
        with pytest.raises(CompilationError, match="operator with no operands"):
            render_calc_expression(ir, set(), set())

    def test_unsupported_raises_compilation_error(self):
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression
        from sysml_codegen.extraction.expression_compiler import CompilationError

        ir = _ir_unsupported("foo.bar", "not supported")
        with pytest.raises(CompilationError):
            render_calc_expression(ir, set(), set())

    def test_feature_chain_raises_compilation_error(self):
        """A FeatureReferenceNode with chain_segments is an unsupported feature chain."""
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression
        from sysml_codegen.extraction.expression_compiler import CompilationError

        ir = _ir_chain_ref("array.bos")
        with pytest.raises(CompilationError, match="feature chain"):
            render_calc_expression(ir, set(), {"array.bos"})

    def test_unresolved_reference_raises_compilation_error(self):
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression
        from sysml_codegen.extraction.expression_compiler import CompilationError

        ir = _ir_ref("unknown_var")
        with pytest.raises(CompilationError, match="unresolved reference"):
            render_calc_expression(ir, {"x"}, {"y"})

    def test_unsupported_operator_raises_compilation_error(self):
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression
        from sysml_codegen.extraction.expression_compiler import CompilationError

        ir = _ir_binary("??", _ir_ref("a"), _ir_ref("b"))
        with pytest.raises(CompilationError, match="unsupported operator"):
            render_calc_expression(ir, {"a", "b"}, set())

    def test_caret_power_alias(self):
        """^ operator maps to ** (Python power)."""
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        ir = _ir_binary("^", _ir_ref("base"), _ir_ref("exp"))
        assert render_calc_expression(ir, {"base", "exp"}, set()) == "(inputs.base ** inputs.exp)"

    def test_pattern_a_simple_binary(self):
        """Pattern A: area = length * width."""
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        ir = _ir_binary("*", _ir_ref("length"), _ir_ref("width"))
        result = render_calc_expression(ir, {"length", "width"}, set())
        assert result == "(inputs.length * inputs.width)"

    def test_pattern_c_nested_with_power(self):
        """Pattern C: CRF = (r * (1+r)**n) / ((1+r)**n - 1)."""
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        one_plus_r = _ir_binary("+", _ir_literal(1.0), _ir_ref("discount_rate"))
        power_term = _ir_binary("**", one_plus_r, _ir_ref("plant_lifetime"))
        numerator = _ir_binary("*", _ir_ref("discount_rate"), power_term)

        one_plus_r_2 = _ir_binary("+", _ir_literal(1.0), _ir_ref("discount_rate"))
        power_term_2 = _ir_binary("**", one_plus_r_2, _ir_ref("plant_lifetime"))
        denominator = _ir_binary("-", power_term_2, _ir_literal(1.0))

        crf = _ir_binary("/", numerator, denominator)
        result = render_calc_expression(crf, {"discount_rate", "plant_lifetime"}, set())

        expected = (
            "((inputs.discount_rate * ((1.0 + inputs.discount_rate)"
            " ** inputs.plant_lifetime))"
            " / (((1.0 + inputs.discount_rate)"
            " ** inputs.plant_lifetime) - 1.0))"
        )
        assert result == expected

    def test_pattern_d_literal_mixed_with_input(self):
        """Pattern D: p_fusion * 3.52 / 17.58."""
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        ir = _ir_binary(
            "/", _ir_binary("*", _ir_ref("p_fusion"), _ir_literal(3.52)), _ir_literal(17.58)
        )
        assert (
            render_calc_expression(ir, {"p_fusion"}, set()) == "((inputs.p_fusion * 3.52) / 17.58)"
        )

    def test_nested_binary_ops_correct_parenthesization(self):
        """Verify nested ops produce correct nesting: ((a + b) * c)."""
        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        inner = _ir_binary("+", _ir_ref("a"), _ir_ref("b"))
        outer = _ir_binary("*", inner, _ir_ref("c"))
        assert (
            render_calc_expression(outer, {"a", "b", "c"}, set())
            == "((inputs.a + inputs.b) * inputs.c)"
        )

    def test_nary_3_operand_left_fold(self):
        """3-operand n-ary operator, a + b + c -> ((a + b) + c) (agentic-mbse's extractor
        already n-ary-folds at OperatorNode construction; the renderer left-folds the
        operand list the same way build_expression_ast used to fold pairwise)."""
        from agentic_mbse.sysml.expression_ir import OperatorNode

        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        ir = OperatorNode(
            operator="+", operands=[_ir_ref("a"), _ir_ref("b"), _ir_ref("c")], operand_type=None
        )
        assert (
            render_calc_expression(ir, {"a", "b", "c"}, set())
            == "((inputs.a + inputs.b) + inputs.c)"
        )

    def test_nary_7_operand_left_fold(self):
        """7-operand sum (NetElectricPower pattern): left-folded."""
        from agentic_mbse.sysml.expression_ir import OperatorNode

        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        names = ["p1", "p2", "p3", "p4", "p5", "p6", "p7"]
        ir = OperatorNode(operator="+", operands=[_ir_ref(n) for n in names], operand_type=None)
        result = render_calc_expression(ir, set(names), set())
        expected = (
            "((((((inputs.p1 + inputs.p2) + inputs.p3)"
            " + inputs.p4) + inputs.p5) + inputs.p6) + inputs.p7)"
        )
        assert result == expected

    def test_render_calc_expression_validates_with_ast_parse(self):
        """render_calc_expression output should be valid Python (parseable)."""
        import ast as python_ast

        from sysml_codegen.extraction.calc_compat_renderer import render_calc_expression

        expr = _ir_binary("+", _ir_ref("x"), _ir_literal(1.0))
        result = render_calc_expression(expr, {"x"}, set())
        # Should not raise — result is valid Python expression
        python_ast.parse(result, mode="eval")


class TestSanitizeName:
    """Tests for _sanitize_name() reference normalization."""

    def test_strips_single_quotes(self):
        from sysml_codegen.extraction.expression_compiler import _sanitize_name

        assert _sanitize_name("'foo'") == "foo"

    def test_strips_double_quotes(self):
        from sysml_codegen.extraction.expression_compiler import _sanitize_name

        assert _sanitize_name('"foo"') == "foo"

    def test_replaces_spaces(self):
        from sysml_codegen.extraction.expression_compiler import _sanitize_name

        assert _sanitize_name("my var") == "my_var"

    def test_empty_string(self):
        from sysml_codegen.extraction.expression_compiler import _sanitize_name

        assert _sanitize_name("") == ""

    def test_already_clean(self):
        from sysml_codegen.extraction.expression_compiler import _sanitize_name

        assert _sanitize_name("wattage") == "wattage"

    def test_combined_quotes_and_spaces(self):
        from sysml_codegen.extraction.expression_compiler import _sanitize_name

        assert _sanitize_name("'my var'") == "my_var"


class TestCollectCalcRefs:
    """Tests for collect_calc_refs() IR traversal (re-anchored from the retired
    ExpressionAST-based _collect_refs() suite, CONSTRAINT-EXEC Item 13)."""

    def test_single_input_ref(self):
        from sysml_codegen.extraction.calc_compat_renderer import collect_calc_refs

        ir = _ir_ref("wattage")
        input_refs, intermediate_refs = collect_calc_refs(ir, {"wattage"}, set())
        assert input_refs == ["wattage"]
        assert intermediate_refs == []

    def test_single_intermediate_ref(self):
        from sysml_codegen.extraction.calc_compat_renderer import collect_calc_refs

        ir = _ir_ref("material_cost")
        input_refs, intermediate_refs = collect_calc_refs(ir, set(), {"material_cost"})
        assert input_refs == []
        assert intermediate_refs == ["material_cost"]

    def test_mixed_tree(self):
        from sysml_codegen.extraction.calc_compat_renderer import collect_calc_refs

        ir = _ir_binary("+", _ir_ref("x"), _ir_ref("y"))
        input_refs, intermediate_refs = collect_calc_refs(ir, {"x"}, {"y"})
        assert input_refs == ["x"]
        assert intermediate_refs == ["y"]

    def test_duplicate_refs_deduplicated(self):
        """(a + a) should produce [a] not [a, a]."""
        from sysml_codegen.extraction.calc_compat_renderer import collect_calc_refs

        ir = _ir_binary("+", _ir_ref("a"), _ir_ref("a"))
        input_refs, _ = collect_calc_refs(ir, {"a"}, set())
        assert input_refs == ["a"]

    def test_nested_binary_ops_left_to_right_preorder(self):
        """Refs collected in left-to-right pre-order traversal."""
        from sysml_codegen.extraction.calc_compat_renderer import collect_calc_refs

        # (a + b) * c
        inner = _ir_binary("+", _ir_ref("a"), _ir_ref("b"))
        outer = _ir_binary("*", inner, _ir_ref("c"))
        input_refs, _ = collect_calc_refs(outer, {"a", "b", "c"}, set())
        assert input_refs == ["a", "b", "c"]

    def test_literal_produces_no_refs(self):
        from sysml_codegen.extraction.calc_compat_renderer import collect_calc_refs

        ir = _ir_literal(42.0)
        input_refs, intermediate_refs = collect_calc_refs(ir, set(), set())
        assert input_refs == []
        assert intermediate_refs == []


class TestClassifyCompilability:
    """Tests for classify_compilability() aggregation."""

    def test_all_fully_returns_fully(self):
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            classify_compilability,
        )

        verdicts = [
            Compilability.FULLY_COMPILABLE,
            Compilability.FULLY_COMPILABLE,
        ]
        assert classify_compilability(verdicts) == Compilability.FULLY_COMPILABLE

    def test_any_manual_returns_manual(self):
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            classify_compilability,
        )

        verdicts = [
            Compilability.FULLY_COMPILABLE,
            Compilability.MANUAL_REQUIRED,
        ]
        assert classify_compilability(verdicts) == Compilability.MANUAL_REQUIRED

    def test_mix_fully_and_partial_returns_partial(self):
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            classify_compilability,
        )

        verdicts = [
            Compilability.FULLY_COMPILABLE,
            Compilability.PARTIALLY_COMPILABLE,
        ]
        assert classify_compilability(verdicts) == Compilability.PARTIALLY_COMPILABLE

    def test_empty_list_returns_manual(self):
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            classify_compilability,
        )

        assert classify_compilability([]) == Compilability.MANUAL_REQUIRED

    def test_unknown_in_results_raises_assertion(self):
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            classify_compilability,
        )

        verdicts = [
            Compilability.UNKNOWN,
        ]
        with pytest.raises(AssertionError, match="UNKNOWN"):
            classify_compilability(verdicts)


# ---------------------------------------------------------------------------
# SysIDE mock infrastructure for the exact compiler boundary
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


@pytest.fixture
def mock_syside_adapter(monkeypatch):
    """Monkeypatch SysideAdapter.is_instance to work with mock nodes."""
    type_map = {
        "MockOperatorExpression": "OperatorExpression",
        "MockFeatureReferenceExpression": "FeatureReferenceExpression",
    }

    def mock_is_instance(node, type_name):
        return type_map.get(type(node).__name__) == type_name

    monkeypatch.setattr(
        "agentic_mbse.sysml.syside_adapter.SysideAdapter.is_instance",
        staticmethod(mock_is_instance),
    )


# ---------------------------------------------------------------------------
# Exact compiler boundary
# ---------------------------------------------------------------------------


def test_exact_compiler_keeps_colliding_reference_ids_distinct(
    mock_syside_adapter, monkeypatch
):
    """Rendered-name collisions cannot collapse exact compiler dependencies."""
    from pathlib import Path
    from types import SimpleNamespace

    from sysml_codegen.extraction.data_models import AttributeInfo, CalculationDefinitionData
    from sysml_codegen.extraction.expression_compiler import compile_calc_def_exact

    definition_id = UUID("00000000-0000-5000-8000-000000000100")
    first_id = UUID("00000000-0000-5000-8000-000000000101")
    second_id = UUID("00000000-0000-5000-8000-000000000102")
    output_id = UUID("00000000-0000-5000-8000-000000000103")
    expression = MockOperatorExpression(
        "+",
        [
            MockFeatureReferenceExpression("same_name"),
            MockFeatureReferenceExpression("same_name"),
        ],
    )
    references = [
        SimpleNamespace(
            name="same_name",
            qualified_name="A::same_name",
            element=SimpleNamespace(element_id=first_id),
        ),
        SimpleNamespace(
            name="same_name",
            qualified_name="B::same_name",
            element=SimpleNamespace(element_id=second_id),
        ),
    ]
    monkeypatch.setattr(
        "sysml_codegen.extraction.expression_compiler.extract_feature_refs",
        lambda _expression, ignore_std_lib=True: references,
    )
    calc_def = CalculationDefinitionData(
        name="Collision",
        qualified_name="Test::Collision",
        doc_comment="",
        calc_expressions=[],
        input_attributes=[
            AttributeInfo(name="same_name", element_id=first_id),
            AttributeInfo(name="same_name", element_id=second_id),
        ],
        output_attributes=[AttributeInfo(name="result", element_id=output_id)],
        references=[],
        source_file=Path("test.sysml"),
        element_id=definition_id,
        output_expression_asts_by_id={output_id: expression},
        all_member_ids={first_id, second_id, output_id},
        member_names_by_id={
            first_id: "same_name",
            second_id: "same_name",
            output_id: "result",
        },
    )

    result = compile_calc_def_exact(calc_def)

    output = result.output_results[0]
    assert output.output_id == output_id
    assert output.input_ids == (first_id, second_id)
