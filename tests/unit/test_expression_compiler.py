"""Unit tests for the expression compiler module."""

from types import SimpleNamespace

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


class TestExpressionNodeType:
    """Tests for ExpressionNodeType enum."""

    def test_enum_values(self):
        from sysml_codegen.extraction.expression_compiler import ExpressionNodeType

        assert ExpressionNodeType.BINARY_OP == "binary_op"
        assert ExpressionNodeType.UNARY_OP == "unary_op"
        assert ExpressionNodeType.LITERAL == "literal"
        assert ExpressionNodeType.INPUT_REF == "input_ref"
        assert ExpressionNodeType.INTERMEDIATE_REF == "intermediate_ref"
        assert ExpressionNodeType.UNSUPPORTED == "unsupported"

    def test_str_inheritance(self):
        from sysml_codegen.extraction.expression_compiler import ExpressionNodeType

        assert isinstance(ExpressionNodeType.BINARY_OP, str)


class TestExpressionASTFactories:
    """Tests for ExpressionAST factory classmethods."""

    def test_binary_factory(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            ExpressionNodeType,
        )

        left = ExpressionAST.input_ref("a")
        right = ExpressionAST.input_ref("b")
        node = ExpressionAST.binary("+", left, right)
        assert node.node_type == ExpressionNodeType.BINARY_OP
        assert node.operator == "+"
        assert node.left is left
        assert node.right is right

    def test_unary_factory(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            ExpressionNodeType,
        )

        operand = ExpressionAST.input_ref("x")
        node = ExpressionAST.unary("-", operand)
        assert node.node_type == ExpressionNodeType.UNARY_OP
        assert node.operator == "-"
        assert node.left is operand
        assert node.right is None

    def test_literal_factory(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            ExpressionNodeType,
        )

        node = ExpressionAST.literal(3.14)
        assert node.node_type == ExpressionNodeType.LITERAL
        assert node.value == 3.14

    def test_literal_int_factory(self):
        from sysml_codegen.extraction.expression_compiler import ExpressionAST

        node = ExpressionAST.literal(42)
        assert node.value == 42

    def test_input_ref_factory(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            ExpressionNodeType,
        )

        node = ExpressionAST.input_ref("wattage")
        assert node.node_type == ExpressionNodeType.INPUT_REF
        assert node.input_name == "wattage"

    def test_intermediate_ref_factory(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            ExpressionNodeType,
        )

        node = ExpressionAST.intermediate_ref("material_cost")
        assert node.node_type == ExpressionNodeType.INTERMEDIATE_REF
        assert node.intermediate_name == "material_cost"

    def test_unsupported_factory(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            ExpressionNodeType,
        )

        node = ExpressionAST.unsupported("foo.bar", "feature chain not supported")
        assert node.node_type == ExpressionNodeType.UNSUPPORTED
        assert node.raw_text == "foo.bar"
        assert node.reason == "feature chain not supported"


class TestCompileExpression:
    """Tests for compile_expression() IR→Python."""

    def test_input_ref(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            compile_expression,
        )

        ast = ExpressionAST.input_ref("wattage")
        assert compile_expression(ast) == "inputs.wattage"

    def test_intermediate_ref(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            compile_expression,
        )

        ast = ExpressionAST.intermediate_ref("material_cost")
        assert compile_expression(ast) == "material_cost"

    def test_literal_float(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            compile_expression,
        )

        ast = ExpressionAST.literal(3.14)
        assert compile_expression(ast) == "3.14"

    def test_literal_int(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            compile_expression,
        )

        ast = ExpressionAST.literal(42)
        assert compile_expression(ast) == "42"

    def test_binary_op_over_parenthesized(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            compile_expression,
        )

        ast = ExpressionAST.binary(
            "*",
            ExpressionAST.input_ref("length"),
            ExpressionAST.input_ref("width"),
        )
        assert compile_expression(ast) == "(inputs.length * inputs.width)"

    def test_unary_negation(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            compile_expression,
        )

        ast = ExpressionAST.unary("-", ExpressionAST.input_ref("x"))
        assert compile_expression(ast) == "(-inputs.x)"

    def test_unsupported_raises_compilation_error(self):
        from sysml_codegen.extraction.expression_compiler import (
            CompilationError,
            ExpressionAST,
            compile_expression,
        )

        ast = ExpressionAST.unsupported("foo.bar", "not supported")
        with pytest.raises(CompilationError):
            compile_expression(ast)

    def test_pattern_a_simple_binary(self):
        """Pattern A: area = length * width."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            compile_expression,
        )

        ast = ExpressionAST.binary(
            "*",
            ExpressionAST.input_ref("length"),
            ExpressionAST.input_ref("width"),
        )
        result = compile_expression(ast)
        assert result == "(inputs.length * inputs.width)"

    def test_pattern_c_nested_with_power(self):
        """Pattern C: CRF = (r * (1+r)**n) / ((1+r)**n - 1)."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            compile_expression,
        )

        # Build (1+r)**n subtree
        one_plus_r = ExpressionAST.binary(
            "+",
            ExpressionAST.literal(1.0),
            ExpressionAST.input_ref("discount_rate"),
        )
        power_term = ExpressionAST.binary(
            "**", one_plus_r, ExpressionAST.input_ref("plant_lifetime")
        )

        # Numerator: r * (1+r)**n
        numerator = ExpressionAST.binary(
            "*", ExpressionAST.input_ref("discount_rate"), power_term
        )

        # Denominator: (1+r)**n - 1
        one_plus_r_2 = ExpressionAST.binary(
            "+",
            ExpressionAST.literal(1.0),
            ExpressionAST.input_ref("discount_rate"),
        )
        power_term_2 = ExpressionAST.binary(
            "**", one_plus_r_2, ExpressionAST.input_ref("plant_lifetime")
        )
        denominator = ExpressionAST.binary(
            "-", power_term_2, ExpressionAST.literal(1.0)
        )

        crf = ExpressionAST.binary("/", numerator, denominator)
        result = compile_expression(crf)

        expected = (
            "((inputs.discount_rate * ((1.0 + inputs.discount_rate)"
            " ** inputs.plant_lifetime))"
            " / (((1.0 + inputs.discount_rate)"
            " ** inputs.plant_lifetime) - 1.0))"
        )
        assert result == expected

    def test_pattern_d_literal_mixed_with_input(self):
        """Pattern D: p_fusion * 3.52 / 17.58."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            compile_expression,
        )

        ast = ExpressionAST.binary(
            "/",
            ExpressionAST.binary(
                "*",
                ExpressionAST.input_ref("p_fusion"),
                ExpressionAST.literal(3.52),
            ),
            ExpressionAST.literal(17.58),
        )
        assert compile_expression(ast) == "((inputs.p_fusion * 3.52) / 17.58)"

    def test_nested_binary_ops_correct_parenthesization(self):
        """Verify nested ops produce correct nesting: ((a + b) * c)."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            compile_expression,
        )

        inner = ExpressionAST.binary(
            "+",
            ExpressionAST.input_ref("a"),
            ExpressionAST.input_ref("b"),
        )
        outer = ExpressionAST.binary("*", inner, ExpressionAST.input_ref("c"))
        assert compile_expression(outer) == "((inputs.a + inputs.b) * inputs.c)"

    def test_compile_expression_validates_with_ast_parse(self):
        """compile_expression output should be valid Python (parseable)."""
        import ast as python_ast

        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            compile_expression,
        )

        expr = ExpressionAST.binary(
            "+",
            ExpressionAST.input_ref("x"),
            ExpressionAST.literal(1.0),
        )
        result = compile_expression(expr)
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


class TestCollectRefs:
    """Tests for _collect_refs() AST traversal."""

    def test_single_input_ref(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            _collect_refs,
        )

        ast = ExpressionAST.input_ref("wattage")
        input_refs, intermediate_refs = _collect_refs(ast)
        assert input_refs == ["wattage"]
        assert intermediate_refs == []

    def test_single_intermediate_ref(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            _collect_refs,
        )

        ast = ExpressionAST.intermediate_ref("material_cost")
        input_refs, intermediate_refs = _collect_refs(ast)
        assert input_refs == []
        assert intermediate_refs == ["material_cost"]

    def test_mixed_tree(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            _collect_refs,
        )

        ast = ExpressionAST.binary(
            "+",
            ExpressionAST.input_ref("x"),
            ExpressionAST.intermediate_ref("y"),
        )
        input_refs, intermediate_refs = _collect_refs(ast)
        assert input_refs == ["x"]
        assert intermediate_refs == ["y"]

    def test_duplicate_refs_deduplicated(self):
        """(a + a) should produce [a] not [a, a]."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            _collect_refs,
        )

        ast = ExpressionAST.binary(
            "+",
            ExpressionAST.input_ref("a"),
            ExpressionAST.input_ref("a"),
        )
        input_refs, _ = _collect_refs(ast)
        assert input_refs == ["a"]

    def test_nested_binary_ops_left_to_right_preorder(self):
        """Refs collected in left-to-right pre-order traversal."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            _collect_refs,
        )

        # (a + b) * c
        inner = ExpressionAST.binary(
            "+",
            ExpressionAST.input_ref("a"),
            ExpressionAST.input_ref("b"),
        )
        outer = ExpressionAST.binary("*", inner, ExpressionAST.input_ref("c"))
        input_refs, _ = _collect_refs(outer)
        assert input_refs == ["a", "b", "c"]

    def test_literal_produces_no_refs(self):
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionAST,
            _collect_refs,
        )

        ast = ExpressionAST.literal(42.0)
        input_refs, intermediate_refs = _collect_refs(ast)
        assert input_refs == []
        assert intermediate_refs == []


class TestClassifyCompilability:
    """Tests for classify_compilability() aggregation."""

    def test_all_fully_returns_fully(self):
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            CompilationResult,
            classify_compilability,
        )

        results = [
            CompilationResult("a", Compilability.FULLY_COMPILABLE, "expr_a"),
            CompilationResult("b", Compilability.FULLY_COMPILABLE, "expr_b"),
        ]
        assert classify_compilability(results) == Compilability.FULLY_COMPILABLE

    def test_any_manual_returns_manual(self):
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            CompilationResult,
            classify_compilability,
        )

        results = [
            CompilationResult("a", Compilability.FULLY_COMPILABLE, "expr_a"),
            CompilationResult("b", Compilability.MANUAL_REQUIRED),
        ]
        assert classify_compilability(results) == Compilability.MANUAL_REQUIRED

    def test_mix_fully_and_partial_returns_partial(self):
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            CompilationResult,
            classify_compilability,
        )

        results = [
            CompilationResult("a", Compilability.FULLY_COMPILABLE, "expr_a"),
            CompilationResult(
                "b", Compilability.PARTIALLY_COMPILABLE, "expr_b"
            ),
        ]
        assert (
            classify_compilability(results)
            == Compilability.PARTIALLY_COMPILABLE
        )

    def test_empty_list_returns_manual(self):
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            classify_compilability,
        )

        assert classify_compilability([]) == Compilability.MANUAL_REQUIRED

    def test_unknown_in_results_raises_assertion(self):
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            CompilationResult,
            classify_compilability,
        )

        results = [
            CompilationResult("a", Compilability.UNKNOWN),
        ]
        with pytest.raises(AssertionError, match="UNKNOWN"):
            classify_compilability(results)


# ---------------------------------------------------------------------------
# Phase 3: build_expression_ast() + syside mock infrastructure
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


class MockUnknownNode:
    """Mock unrecognized syside node."""

    pass


class MockFeatureChainExpressionOperatorExpression:
    """Mock that dual-matches both FeatureChainExpression and OperatorExpression.

    Reproduces the SysIDE subtype relationship where FCE is a subtype of OE,
    causing SysideAdapter.is_instance()'s name-based fallback to return True
    for both type checks on the same node.
    """

    def __init__(self, operator: str, operands: list):
        self.operator = operator
        self.operands = operands


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


class TestBuildExpressionAST:
    """Tests for build_expression_ast() syside→IR conversion."""

    def test_pattern_a_simple_binary(self, mock_syside_adapter):
        """Pattern A: area = length * width."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionNodeType,
            build_expression_ast,
            compile_expression,
        )

        node = MockOperatorExpression(
            "*",
            [
                MockFeatureReferenceExpression("length"),
                MockFeatureReferenceExpression("width"),
            ],
        )
        ast = build_expression_ast(
            node, input_names={"length", "width"}, output_names=set()
        )
        assert ast.node_type == ExpressionNodeType.BINARY_OP
        assert ast.operator == "*"
        assert ast.left.node_type == ExpressionNodeType.INPUT_REF
        assert ast.left.input_name == "length"
        assert ast.right.node_type == ExpressionNodeType.INPUT_REF
        assert ast.right.input_name == "width"
        assert compile_expression(ast) == "(inputs.length * inputs.width)"

    def test_pattern_c_nested_with_power(self, mock_syside_adapter):
        """Pattern C: CRF-like nested expression with **."""
        from sysml_codegen.extraction.expression_compiler import (
            build_expression_ast,
            compile_expression,
        )

        # (1.0 + r) ** n
        one_plus_r = MockOperatorExpression(
            "+",
            [
                MockLiteralRational(1.0),
                MockFeatureReferenceExpression("discount_rate"),
            ],
        )
        power = MockOperatorExpression(
            "**", [one_plus_r, MockFeatureReferenceExpression("n")]
        )
        # r * ((1+r)**n)
        numerator = MockOperatorExpression(
            "*",
            [MockFeatureReferenceExpression("discount_rate"), power],
        )
        ast = build_expression_ast(
            numerator, input_names={"discount_rate", "n"}, output_names=set()
        )
        result = compile_expression(ast)
        assert (
            result
            == "(inputs.discount_rate * ((1.0 + inputs.discount_rate) ** inputs.n))"
        )

    def test_pattern_d_literal_mixed_with_input(self, mock_syside_adapter):
        """Pattern D: p_fusion * 3.52 / 17.58."""
        from sysml_codegen.extraction.expression_compiler import (
            build_expression_ast,
            compile_expression,
        )

        inner = MockOperatorExpression(
            "*",
            [
                MockFeatureReferenceExpression("p_fusion"),
                MockLiteralRational(3.52),
            ],
        )
        outer = MockOperatorExpression("/", [inner, MockLiteralRational(17.58)])
        ast = build_expression_ast(
            outer, input_names={"p_fusion"}, output_names=set()
        )
        assert compile_expression(ast) == "((inputs.p_fusion * 3.52) / 17.58)"

    def test_pattern_f_unit_annotation_stripping(self, mock_syside_adapter):
        """Pattern F: [kg] annotation stripped, value preserved."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionNodeType,
            build_expression_ast,
        )

        # value [unit] is represented as OperatorExpression("[", [value, unit])
        inner = MockLiteralRational(42.0)
        unit_node = MockFeatureReferenceExpression("kg")
        node = MockOperatorExpression("[", [inner, unit_node])
        ast = build_expression_ast(
            node, input_names=set(), output_names=set()
        )
        assert ast.node_type == ExpressionNodeType.LITERAL
        assert ast.value == 42.0

    def test_nary_3_operand_left_fold(self, mock_syside_adapter):
        """3-operand: a + b + c → ((a + b) + c)."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionNodeType,
            build_expression_ast,
            compile_expression,
        )

        node = MockOperatorExpression(
            "+",
            [
                MockFeatureReferenceExpression("a"),
                MockFeatureReferenceExpression("b"),
                MockFeatureReferenceExpression("c"),
            ],
        )
        ast = build_expression_ast(
            node, input_names={"a", "b", "c"}, output_names=set()
        )
        assert ast.node_type == ExpressionNodeType.BINARY_OP
        # Left child: (a + b)
        assert ast.left.node_type == ExpressionNodeType.BINARY_OP
        assert ast.left.left.input_name == "a"
        assert ast.left.right.input_name == "b"
        # Right child: c
        assert ast.right.input_name == "c"
        assert compile_expression(ast) == "((inputs.a + inputs.b) + inputs.c)"

    def test_nary_7_operand_left_fold(self, mock_syside_adapter):
        """7-operand sum (NetElectricPower pattern): left-folded."""
        from sysml_codegen.extraction.expression_compiler import (
            build_expression_ast,
            compile_expression,
        )

        names = ["p1", "p2", "p3", "p4", "p5", "p6", "p7"]
        node = MockOperatorExpression(
            "+",
            [MockFeatureReferenceExpression(n) for n in names],
        )
        ast = build_expression_ast(
            node, input_names=set(names), output_names=set()
        )
        result = compile_expression(ast)
        expected = (
            "((((((inputs.p1 + inputs.p2) + inputs.p3)"
            " + inputs.p4) + inputs.p5) + inputs.p6) + inputs.p7)"
        )
        assert result == expected

    def test_unary_negation(self, mock_syside_adapter):
        """Unary negation: -(x) → (-inputs.x)."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionNodeType,
            build_expression_ast,
            compile_expression,
        )

        node = MockOperatorExpression(
            "-", [MockFeatureReferenceExpression("x")]
        )
        ast = build_expression_ast(
            node, input_names={"x"}, output_names=set()
        )
        assert ast.node_type == ExpressionNodeType.UNARY_OP
        assert ast.operator == "-"
        assert compile_expression(ast) == "(-inputs.x)"

    def test_feature_chain_unsupported(self, mock_syside_adapter):
        """FeatureChainExpression → UNSUPPORTED."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionNodeType,
            build_expression_ast,
        )

        node = MockFeatureChainExpression()
        ast = build_expression_ast(
            node, input_names=set(), output_names=set()
        )
        assert ast.node_type == ExpressionNodeType.UNSUPPORTED
        assert "feature chain" in ast.reason

    def test_unknown_node_type_unsupported(self, mock_syside_adapter):
        """Unknown node type → UNSUPPORTED."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionNodeType,
            build_expression_ast,
        )

        node = MockUnknownNode()
        ast = build_expression_ast(
            node, input_names=set(), output_names=set()
        )
        assert ast.node_type == ExpressionNodeType.UNSUPPORTED
        assert "unknown node type" in ast.reason

    def test_unresolved_reference_unsupported(self, mock_syside_adapter):
        """Reference not in inputs, outputs, or members → UNSUPPORTED."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionNodeType,
            build_expression_ast,
        )

        node = MockFeatureReferenceExpression("unknown_var")
        ast = build_expression_ast(
            node, input_names={"x"}, output_names={"y"}
        )
        assert ast.node_type == ExpressionNodeType.UNSUPPORTED
        assert "unresolved reference" in ast.reason
        assert "unknown_var" in ast.reason

    def test_undeclared_member_becomes_intermediate_ref(
        self, mock_syside_adapter
    ):
        """Reference in all_member_names → INTERMEDIATE_REF."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionNodeType,
            build_expression_ast,
        )

        node = MockFeatureReferenceExpression("hidden_var")
        ast = build_expression_ast(
            node,
            input_names={"x"},
            output_names={"y"},
            all_member_names={"hidden_var", "x", "y"},
        )
        assert ast.node_type == ExpressionNodeType.INTERMEDIATE_REF
        assert ast.intermediate_name == "hidden_var"

    def test_output_ref_becomes_intermediate_ref(self, mock_syside_adapter):
        """Reference to a declared output → INTERMEDIATE_REF."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionNodeType,
            build_expression_ast,
        )

        node = MockFeatureReferenceExpression("material_cost")
        ast = build_expression_ast(
            node,
            input_names=set(),
            output_names={"material_cost", "total_cost"},
        )
        assert ast.node_type == ExpressionNodeType.INTERMEDIATE_REF
        assert ast.intermediate_name == "material_cost"

    def test_unsupported_operator(self, mock_syside_adapter):
        """Unknown operator → UNSUPPORTED node."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionNodeType,
            build_expression_ast,
        )

        node = MockOperatorExpression(
            "??",
            [
                MockFeatureReferenceExpression("a"),
                MockFeatureReferenceExpression("b"),
            ],
        )
        ast = build_expression_ast(
            node, input_names={"a", "b"}, output_names=set()
        )
        assert ast.node_type == ExpressionNodeType.UNSUPPORTED
        assert "unsupported operator" in ast.reason

    def test_caret_power_alias(self, mock_syside_adapter):
        """^ operator maps to ** (Python power)."""
        from sysml_codegen.extraction.expression_compiler import (
            build_expression_ast,
            compile_expression,
        )

        node = MockOperatorExpression(
            "^",
            [
                MockFeatureReferenceExpression("base"),
                MockFeatureReferenceExpression("exp"),
            ],
        )
        ast = build_expression_ast(
            node, input_names={"base", "exp"}, output_names=set()
        )
        assert compile_expression(ast) == "(inputs.base ** inputs.exp)"

    def test_sanitize_name_in_reference_resolution(self, mock_syside_adapter):
        """Syside referent name with quotes gets sanitized before lookup."""
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionNodeType,
            build_expression_ast,
        )

        node = MockFeatureReferenceExpression("'my var'")
        ast = build_expression_ast(
            node, input_names={"my_var"}, output_names=set()
        )
        assert ast.node_type == ExpressionNodeType.INPUT_REF
        assert ast.input_name == "my_var"


# ---------------------------------------------------------------------------
# Phase 4: compile_calc_def() orchestrator + edge cases
# ---------------------------------------------------------------------------


def _make_calc_def(name, input_names, output_names):
    """Helper to construct a CalculationDefinitionData for testing."""
    from pathlib import Path

    from sysml_codegen.extraction.data_models import (
        AttributeInfo,
        CalculationDefinitionData,
    )

    return CalculationDefinitionData(
        name=name,
        qualified_name=f"Test::{name}",
        doc_comment="",
        calc_expressions=[],
        input_attributes=[AttributeInfo(name=n) for n in input_names],
        output_attributes=[AttributeInfo(name=n) for n in output_names],
        references=[],
        source_file=Path("test.sysml"),
    )


@pytest.fixture
def mock_extract_feature_refs(monkeypatch):
    """Monkeypatch extract_feature_refs to return pre-computed refs.

    Usage: set ref_map[id(mock_ast_node)] = ["ref_name_1", "ref_name_2"]
    before calling compile_calc_def.
    """
    ref_map: dict[int, list[str]] = {}

    def mock_efr(expr, ignore_std_lib=True):
        names = ref_map.get(id(expr), [])
        return [
            SimpleNamespace(name=n, qualified_name=n, element=None)
            for n in names
        ]

    monkeypatch.setattr(
        "sysml_codegen.extraction.expression_compiler.extract_feature_refs",
        mock_efr,
    )
    return ref_map


class TestCompileCalcDef:
    """Tests for compile_calc_def() orchestrator.

    Uses both mock_syside_adapter (for build_expression_ast) and
    mock_extract_feature_refs (for dependency graph construction).
    """

    def test_pattern_b_multi_step_topological_order(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Pattern B: material_cost → fab_cost → total_cost."""
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            compile_calc_def,
        )

        calc_def = _make_calc_def(
            "CostCalc",
            input_names=["unit_cost", "quantity", "margin"],
            output_names=["material_cost", "fab_cost", "total_cost"],
        )

        # Build mock ASTs
        material_ast = MockOperatorExpression(
            "*",
            [
                MockFeatureReferenceExpression("unit_cost"),
                MockFeatureReferenceExpression("quantity"),
            ],
        )
        fab_ast = MockOperatorExpression(
            "*",
            [
                MockFeatureReferenceExpression("material_cost"),
                MockLiteralRational(1.2),
            ],
        )
        total_ast = MockOperatorExpression(
            "+",
            [
                MockFeatureReferenceExpression("fab_cost"),
                MockOperatorExpression(
                    "*",
                    [
                        MockFeatureReferenceExpression("fab_cost"),
                        MockFeatureReferenceExpression("margin"),
                    ],
                ),
            ],
        )

        expression_asts = {
            "material_cost": material_ast,
            "fab_cost": fab_ast,
            "total_cost": total_ast,
        }

        # Set up dependency graph refs
        ref_map = mock_extract_feature_refs
        ref_map[id(material_ast)] = ["unit_cost", "quantity"]
        ref_map[id(fab_ast)] = ["material_cost"]
        ref_map[id(total_ast)] = ["fab_cost", "margin"]

        result = compile_calc_def(calc_def, expression_asts)

        assert result.overall_compilability == Compilability.FULLY_COMPILABLE
        assert result.execution_order == [
            "material_cost",
            "fab_cost",
            "total_cost",
        ]
        assert len(result.output_results) == 3

        # Verify individual expressions
        by_name = {r.output_name: r for r in result.output_results}
        assert (
            by_name["material_cost"].python_expression
            == "(inputs.unit_cost * inputs.quantity)"
        )
        assert (
            by_name["fab_cost"].python_expression
            == "(material_cost * 1.2)"
        )
        assert (
            by_name["total_cost"].python_expression
            == "(fab_cost + (fab_cost * inputs.margin))"
        )

    def test_pattern_e_pi_as_repeated_literal(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Pattern E: pi faithfully reproduced as literal, no math.pi."""
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            compile_calc_def,
        )

        calc_def = _make_calc_def(
            "CircleCalc", input_names=["radius"], output_names=["area"]
        )

        # area = 3.14159265 * radius * radius (3-operand left-fold)
        area_ast = MockOperatorExpression(
            "*",
            [
                MockLiteralRational(3.14159265),
                MockFeatureReferenceExpression("radius"),
                MockFeatureReferenceExpression("radius"),
            ],
        )
        expression_asts = {"area": area_ast}

        ref_map = mock_extract_feature_refs
        ref_map[id(area_ast)] = ["radius"]

        result = compile_calc_def(calc_def, expression_asts)

        assert result.overall_compilability == Compilability.FULLY_COMPILABLE
        by_name = {r.output_name: r for r in result.output_results}
        assert (
            by_name["area"].python_expression
            == "((3.14159265 * inputs.radius) * inputs.radius)"
        )

    def test_edge1_unresolved_reference_verdict_escalation(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Edge 1: unresolved ref → MANUAL_REQUIRED, escalates overall."""
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            compile_calc_def,
        )

        calc_def = _make_calc_def(
            "MixedCalc",
            input_names=["a", "b"],
            output_names=["good", "bad"],
        )

        good_ast = MockOperatorExpression(
            "*",
            [
                MockFeatureReferenceExpression("a"),
                MockFeatureReferenceExpression("b"),
            ],
        )
        # "ghost" is not in inputs, outputs, or members → UNSUPPORTED
        bad_ast = MockOperatorExpression(
            "+",
            [
                MockFeatureReferenceExpression("a"),
                MockFeatureReferenceExpression("ghost"),
            ],
        )

        expression_asts = {"good": good_ast, "bad": bad_ast}

        ref_map = mock_extract_feature_refs
        ref_map[id(good_ast)] = ["a", "b"]
        ref_map[id(bad_ast)] = ["a", "ghost"]

        result = compile_calc_def(calc_def, expression_asts)

        assert result.overall_compilability == Compilability.MANUAL_REQUIRED
        by_name = {r.output_name: r for r in result.output_results}
        assert (
            by_name["good"].compilability == Compilability.FULLY_COMPILABLE
        )
        assert by_name["bad"].compilability == Compilability.MANUAL_REQUIRED
        assert "unresolved reference" in by_name["bad"].unsupported_reason

    def test_edge2_circular_dependency_returns_manual(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Edge 2: circular dependency → MANUAL_REQUIRED."""
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            compile_calc_def,
        )

        calc_def = _make_calc_def(
            "CircularCalc",
            input_names=["x"],
            output_names=["a", "b"],
        )

        a_ast = MockOperatorExpression(
            "+",
            [
                MockFeatureReferenceExpression("b"),
                MockFeatureReferenceExpression("x"),
            ],
        )
        b_ast = MockOperatorExpression(
            "+",
            [
                MockFeatureReferenceExpression("a"),
                MockFeatureReferenceExpression("x"),
            ],
        )

        expression_asts = {"a": a_ast, "b": b_ast}

        ref_map = mock_extract_feature_refs
        ref_map[id(a_ast)] = ["b", "x"]
        ref_map[id(b_ast)] = ["a", "x"]

        result = compile_calc_def(calc_def, expression_asts)

        assert result.overall_compilability == Compilability.MANUAL_REQUIRED
        assert all(
            r.compilability == Compilability.MANUAL_REQUIRED
            for r in result.output_results
        )
        assert any(
            "circular" in (r.unsupported_reason or "")
            for r in result.output_results
        )

    def test_edge3_missing_ast_partial_compilability(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Edge 3: missing AST for one output → that output MANUAL."""
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            compile_calc_def,
        )

        calc_def = _make_calc_def(
            "PartialCalc",
            input_names=["x"],
            output_names=["compiled", "missing"],
        )

        compiled_ast = MockOperatorExpression(
            "*",
            [
                MockFeatureReferenceExpression("x"),
                MockLiteralRational(2.0),
            ],
        )

        # missing has no AST (None)
        expression_asts = {"compiled": compiled_ast, "missing": None}

        ref_map = mock_extract_feature_refs
        ref_map[id(compiled_ast)] = ["x"]

        result = compile_calc_def(calc_def, expression_asts)

        assert result.overall_compilability == Compilability.MANUAL_REQUIRED
        by_name = {r.output_name: r for r in result.output_results}
        assert (
            by_name["compiled"].compilability
            == Compilability.FULLY_COMPILABLE
        )
        assert (
            by_name["missing"].compilability == Compilability.MANUAL_REQUIRED
        )
        assert "no expression AST" in by_name["missing"].unsupported_reason

    def test_edge4_unsupported_operator_verdict_escalation(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Edge 4: unsupported operator → MANUAL_REQUIRED."""
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            compile_calc_def,
        )

        calc_def = _make_calc_def(
            "BadOpCalc",
            input_names=["x", "y"],
            output_names=["result"],
        )

        result_ast = MockOperatorExpression(
            "??",
            [
                MockFeatureReferenceExpression("x"),
                MockFeatureReferenceExpression("y"),
            ],
        )

        expression_asts = {"result": result_ast}

        ref_map = mock_extract_feature_refs
        ref_map[id(result_ast)] = ["x", "y"]

        result = compile_calc_def(calc_def, expression_asts)

        assert result.overall_compilability == Compilability.MANUAL_REQUIRED
        assert (
            result.output_results[0].compilability
            == Compilability.MANUAL_REQUIRED
        )
        assert "unsupported" in result.output_results[0].unsupported_reason

    def test_edge5_feature_chain_returns_manual(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Edge 5: FeatureChainExpression → MANUAL_REQUIRED."""
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            compile_calc_def,
        )

        calc_def = _make_calc_def(
            "ChainCalc",
            input_names=["x"],
            output_names=["result"],
        )

        result_ast = MockFeatureChainExpression()
        # A real FeatureChainExpression always carries >=1 operand (the dotted-path
        # segments); give the mock one so agentic-mbse's extractor populates
        # chain_segments the way it would for a live node, not an empty-class stand-in.
        result_ast.operands = [MockFeatureReferenceExpression("sensor")]
        expression_asts = {"result": result_ast}

        ref_map = mock_extract_feature_refs
        ref_map[id(result_ast)] = []

        result = compile_calc_def(calc_def, expression_asts)

        assert result.overall_compilability == Compilability.MANUAL_REQUIRED
        assert "feature chain" in (
            result.output_results[0].unsupported_reason or ""
        )

    def test_undeclared_intermediates_4_chain(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Undeclared intermediates: 4-chain (MagnetCryogenicLoad pattern)."""
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            compile_calc_def,
        )

        calc_def = _make_calc_def(
            "MagnetCryoLoad",
            input_names=["i1", "i2"],
            output_names=["final_result"],
        )

        # Build mock ASTs for each node
        inter_a_ast = MockOperatorExpression(
            "*",
            [
                MockFeatureReferenceExpression("i1"),
                MockLiteralRational(2.0),
            ],
        )
        inter_b_ast = MockOperatorExpression(
            "+",
            [
                MockFeatureReferenceExpression("inter_a"),
                MockFeatureReferenceExpression("i2"),
            ],
        )
        inter_c_ast = MockOperatorExpression(
            "*",
            [
                MockFeatureReferenceExpression("inter_b"),
                MockLiteralRational(1.5),
            ],
        )
        inter_d_ast = MockOperatorExpression(
            "+",
            [
                MockFeatureReferenceExpression("inter_c"),
                MockLiteralRational(100.0),
            ],
        )
        final_ast = MockOperatorExpression(
            "*",
            [
                MockFeatureReferenceExpression("inter_d"),
                MockLiteralRational(0.5),
            ],
        )

        expression_asts = {"final_result": final_ast}
        all_member_names = {
            "i1",
            "i2",
            "final_result",
            "inter_a",
            "inter_b",
            "inter_c",
            "inter_d",
        }
        member_expressions = {
            "inter_a": inter_a_ast,
            "inter_b": inter_b_ast,
            "inter_c": inter_c_ast,
            "inter_d": inter_d_ast,
        }

        ref_map = mock_extract_feature_refs
        ref_map[id(final_ast)] = ["inter_d"]
        ref_map[id(inter_d_ast)] = ["inter_c"]
        ref_map[id(inter_c_ast)] = ["inter_b"]
        ref_map[id(inter_b_ast)] = ["inter_a", "i2"]
        ref_map[id(inter_a_ast)] = ["i1"]

        result = compile_calc_def(
            calc_def,
            expression_asts,
            all_member_names=all_member_names,
            member_expressions=member_expressions,
        )

        assert result.overall_compilability == Compilability.FULLY_COMPILABLE
        assert result.execution_order == [
            "inter_a",
            "inter_b",
            "inter_c",
            "inter_d",
            "final_result",
        ]

        # Verify undeclared flag
        by_name = {r.output_name: r for r in result.output_results}
        assert by_name["inter_a"].is_undeclared_intermediate is True
        assert by_name["inter_b"].is_undeclared_intermediate is True
        assert by_name["inter_c"].is_undeclared_intermediate is True
        assert by_name["inter_d"].is_undeclared_intermediate is True
        assert by_name["final_result"].is_undeclared_intermediate is False

        # Verify compiled expressions
        assert by_name["inter_a"].python_expression == "(inputs.i1 * 2.0)"
        assert (
            by_name["inter_b"].python_expression
            == "(inter_a + inputs.i2)"
        )
        assert (
            by_name["final_result"].python_expression
            == "(inter_d * 0.5)"
        )

    def test_overall_compilability_is_worst_case(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Overall compilability is worst-case across all outputs."""
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            compile_calc_def,
        )

        calc_def = _make_calc_def(
            "WorstCase",
            input_names=["x"],
            output_names=["good", "bad"],
        )

        good_ast = MockOperatorExpression(
            "*",
            [
                MockFeatureReferenceExpression("x"),
                MockLiteralRational(1.0),
            ],
        )

        expression_asts = {"good": good_ast, "bad": None}

        ref_map = mock_extract_feature_refs
        ref_map[id(good_ast)] = ["x"]

        result = compile_calc_def(calc_def, expression_asts)

        # One FULLY + one MANUAL → overall MANUAL
        assert result.overall_compilability == Compilability.MANUAL_REQUIRED

    def test_single_output_fully_compilable(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Simple single-output CalcDef compiles to FULLY_COMPILABLE."""
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            compile_calc_def,
        )

        calc_def = _make_calc_def(
            "SimpleCalc", input_names=["a", "b"], output_names=["result"]
        )

        result_ast = MockOperatorExpression(
            "+",
            [
                MockFeatureReferenceExpression("a"),
                MockFeatureReferenceExpression("b"),
            ],
        )
        expression_asts = {"result": result_ast}

        ref_map = mock_extract_feature_refs
        ref_map[id(result_ast)] = ["a", "b"]

        result = compile_calc_def(calc_def, expression_asts)

        assert result.overall_compilability == Compilability.FULLY_COMPILABLE
        assert result.calc_def_name == "SimpleCalc"
        assert result.execution_order == ["result"]
        assert (
            result.output_results[0].python_expression
            == "(inputs.a + inputs.b)"
        )
        assert result.output_results[0].input_refs == ["a", "b"]


class TestCompileCalcDefEdge6:
    """Tests for EXPOSE-with-operators (Edge 6).

    An expression that has operators is a computed value, not a passthrough.
    The compiler should handle it as a normal expression and produce
    FULLY_COMPILABLE, not misclassify it as a passthrough or MANUAL_REQUIRED.
    """

    def test_expression_with_operators_compiles_normally(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Expression with operators (a * 2.0) → FULLY_COMPILABLE."""
        from sysml_codegen.extraction.expression_compiler import (
            Compilability,
            compile_calc_def,
        )

        calc_def = _make_calc_def(
            "ExposeCalc", input_names=["a"], output_names=["result"]
        )

        result_ast = MockOperatorExpression(
            "*",
            [
                MockFeatureReferenceExpression("a"),
                MockLiteralRational(2.0),
            ],
        )
        expression_asts = {"result": result_ast}

        ref_map = mock_extract_feature_refs
        ref_map[id(result_ast)] = ["a"]

        result = compile_calc_def(calc_def, expression_asts)

        assert result.overall_compilability == Compilability.FULLY_COMPILABLE
        assert (
            result.output_results[0].python_expression
            == "(inputs.a * 2.0)"
        )


# ---------------------------------------------------------------------------
# Bug A2: FCE/OE dispatch ordering in build_expression_ast()
# ---------------------------------------------------------------------------


class TestFCEBeforeOEOrdering:
    """Bug A2: build_expression_ast() must dispatch FCE before OE.

    These tests do NOT use the mock_syside_adapter monkeypatch — they rely on
    SysideAdapter.is_instance()'s name-based fallback (type_name in
    type(elem).__name__) to reproduce the real dual-match behavior where
    FeatureChainExpression nodes also match OperatorExpression.
    """

    def test_dual_match_node_hits_fce_handler(self):
        """A node matching both FCE and OE must produce the FCE diagnostic.

        Without the fix, a dual-match node with operator='.' enters the OE
        handler, producing 'unsupported operator: .' (since '.' is not in
        PYTHON_OPERATOR_MAP). With the fix, FCE is checked first.
        """
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionNodeType,
            build_expression_ast,
        )

        node = MockFeatureChainExpressionOperatorExpression(
            operator=".",
            operands=[MockFeatureReferenceExpression("array_bos")],
        )
        ast = build_expression_ast(node, input_names=set(), output_names=set())

        assert ast.node_type == ExpressionNodeType.UNSUPPORTED
        assert "feature chain expression" in ast.reason
        assert "unsupported operator: ." not in ast.reason

    def test_dual_match_node_raw_text_is_type_name(self):
        """The unsupported node's raw_text should be the actual class name."""
        from sysml_codegen.extraction.expression_compiler import (
            build_expression_ast,
        )

        node = MockFeatureChainExpressionOperatorExpression(
            operator=".",
            operands=[MockFeatureReferenceExpression("array_bos")],
        )
        ast = build_expression_ast(node, input_names=set(), output_names=set())

        assert ast.raw_text == "MockFeatureChainExpressionOperatorExpression"

    def test_pure_oe_still_dispatches_after_reorder(self):
        """An OperatorExpression that is NOT an FCE subtype still works.

        Regression guard: the FCE-before-OE reorder must not break normal
        OE handling for nodes that only match OperatorExpression.
        """
        from sysml_codegen.extraction.expression_compiler import (
            ExpressionNodeType,
            build_expression_ast,
        )

        node = MockOperatorExpression(
            "??",
            [
                MockFeatureReferenceExpression("a"),
                MockFeatureReferenceExpression("b"),
            ],
        )
        ast = build_expression_ast(
            node, input_names={"a", "b"}, output_names=set()
        )

        assert ast.node_type == ExpressionNodeType.UNSUPPORTED
        assert "unsupported operator: ??" in ast.reason
