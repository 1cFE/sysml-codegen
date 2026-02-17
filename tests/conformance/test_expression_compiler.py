"""C04: Expression Compiler conformance tests.

Verifies that the expression compiler conforms to REQ-EC-01 through REQ-EC-07
and REQ-AST-01 from design intent docs 14-expression-compiler.md and
19-ast-dispatch-invariant.md.

Testing strategy:
- Pure compiler functions (compile_expression, classify_compilability, _collect_refs)
  tested with constructed ExpressionAST IR -- no mocks needed.
- SysIDE-dependent functions (build_expression_ast, compile_calc_def) tested with
  mock SysIDE adapter -- acceptable per Ground Rule 1.
- Cross-model validation uses real calc def metadata (names, attributes) from
  extraction snapshots with mock ASTs.
- Static analysis tests parse source files with Python ast module.

Requirements: REQ-EC-01 through REQ-EC-07, REQ-AST-01.
"""

from __future__ import annotations

import ast as python_ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from sysml_codegen.extraction.expression_compiler import (
    Compilability,
    CompilationError,
    CompilationResult,
    ExpressionAST,
    ExpressionNodeType,
    build_expression_ast,
    classify_compilability,
    compile_calc_def,
    compile_expression,
)

# ---------------------------------------------------------------------------
# Source paths for static analysis
# ---------------------------------------------------------------------------

SRC_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "extraction"
EXPRESSION_COMPILER_PATH = SRC_DIR / "expression_compiler.py"
EXPRESSION_UTILS_PATH = SRC_DIR / "expression_utils.py"


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


class MockFeatureChainExpressionOperatorExpression:
    """Mock that dual-matches both FeatureChainExpression and OperatorExpression.

    Class name contains both type names, triggering SysideAdapter.is_instance()'s
    name-based fallback for both type checks.
    """

    def __init__(self, operator: str = ".", operands: list | None = None):
        self.operator = operator
        self.operands = operands or []


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
        "sysml_codegen.extraction.expression_compiler.SysideAdapter.is_instance",
        staticmethod(mock_is_instance),
    )


@pytest.fixture
def mock_extract_feature_refs(monkeypatch):
    """Monkeypatch extract_feature_refs to return pre-computed refs."""
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


def _make_calc_def(name, input_names, output_names, all_member_names=None):
    """Helper to construct a CalculationDefinitionData for testing."""
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
        all_member_names=set(all_member_names) if all_member_names else set(),
    )


def _extract_name_sets(calc_def):
    """Derive input/output attribute name sets from a snapshot CalculationDefinitionData."""
    input_names = {a.name for a in calc_def.input_attributes}
    output_names = {a.name for a in calc_def.output_attributes}
    return input_names, output_names


# ---------------------------------------------------------------------------
# Static analysis helpers
# ---------------------------------------------------------------------------


def _find_is_instance_calls_in_function(
    source_path: Path, function_name: str
) -> dict[str, int]:
    """Parse source file and find SysideAdapter.is_instance() calls in a function.

    Returns dict mapping type_name argument to line number (first occurrence only).
    """
    source = source_path.read_text()
    tree = python_ast.parse(source, filename=str(source_path))

    results: dict[str, int] = {}

    for node in python_ast.walk(tree):
        if isinstance(node, python_ast.FunctionDef) and node.name == function_name:
            for child in python_ast.walk(node):
                if isinstance(child, python_ast.Call) and _is_syside_is_instance_call(child):
                    if len(child.args) >= 2:
                        type_arg = child.args[1]
                        if isinstance(type_arg, python_ast.Constant) and isinstance(
                            type_arg.value, str
                        ):
                            if type_arg.value not in results:
                                results[type_arg.value] = child.lineno
            break

    return results


def _is_syside_is_instance_call(call_node) -> bool:
    """Check if an ast.Call node is SysideAdapter.is_instance(...)."""
    func = call_node.func
    if isinstance(func, python_ast.Attribute) and func.attr == "is_instance":
        if isinstance(func.value, python_ast.Name) and func.value.id == "SysideAdapter":
            return True
    return False


# ---------------------------------------------------------------------------
# REQ-EC-01: FCE before OE at dispatch site
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EC-01")
class TestReqEc01FceBeforeOe:
    """FCE must be checked before OE in build_expression_ast to prevent mis-dispatch."""

    def test_fce_dispatch_before_oe_in_source(self):
        """Static analysis: FCE is_instance check precedes OE is_instance check."""
        calls = _find_is_instance_calls_in_function(
            EXPRESSION_COMPILER_PATH, "build_expression_ast"
        )
        assert "FeatureChainExpression" in calls, (
            "No is_instance call for FeatureChainExpression in build_expression_ast"
        )
        assert "OperatorExpression" in calls, (
            "No is_instance call for OperatorExpression in build_expression_ast"
        )
        assert calls["FeatureChainExpression"] < calls["OperatorExpression"], (
            f"FCE check at line {calls['FeatureChainExpression']} must precede "
            f"OE check at line {calls['OperatorExpression']}"
        )

    def test_fce_invariant_comment_present(self):
        """The invariant comment 'MUST be before OperatorExpression' is present."""
        source = EXPRESSION_COMPILER_PATH.read_text()
        assert "MUST be before OperatorExpression" in source, (
            "Missing invariant comment at FCE dispatch site in expression_compiler.py"
        )

    def test_fce_node_produces_unsupported_not_oe_error(self):
        """Dual-match FCE+OE mock node produces 'feature chain' diagnostic.

        Uses real SysideAdapter.is_instance name-based fallback (no monkeypatch).
        """
        node = MockFeatureChainExpressionOperatorExpression(
            operator=".", operands=[MockFeatureReferenceExpression("x")]
        )
        result = build_expression_ast(node, input_names=set(), output_names=set())
        assert result.node_type == ExpressionNodeType.UNSUPPORTED
        assert "feature chain" in result.reason
        assert "unsupported operator" not in result.reason

    def test_pure_oe_still_dispatches_correctly(self, mock_syside_adapter):
        """Regression: OE-only mock node still handled by OE handler after FCE guard."""
        node = MockOperatorExpression(
            "+",
            [
                MockFeatureReferenceExpression("a"),
                MockFeatureReferenceExpression("b"),
            ],
        )
        result = build_expression_ast(node, input_names={"a", "b"}, output_names=set())
        assert result.node_type == ExpressionNodeType.BINARY_OP
        assert result.operator == "+"


# ---------------------------------------------------------------------------
# REQ-EC-02: N-ary left-fold
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EC-02")
class TestReqEc02NaryLeftFold:
    """N-ary operands must be left-folded into binary nodes."""

    def test_3_operand_left_fold_structure(self, mock_syside_adapter):
        """3 operands → ((a + b) + c) binary tree."""
        node = MockOperatorExpression(
            "+",
            [
                MockFeatureReferenceExpression("a"),
                MockFeatureReferenceExpression("b"),
                MockFeatureReferenceExpression("c"),
            ],
        )
        result = build_expression_ast(
            node, input_names={"a", "b", "c"}, output_names=set()
        )
        assert result.node_type == ExpressionNodeType.BINARY_OP
        assert result.left.node_type == ExpressionNodeType.BINARY_OP
        assert result.left.left.input_name == "a"
        assert result.left.right.input_name == "b"
        assert result.right.input_name == "c"
        assert compile_expression(result) == "((inputs.a + inputs.b) + inputs.c)"

    def test_7_operand_left_fold_structure(self, mock_syside_adapter):
        """7 operands → 6 levels of nesting, all left-associated."""
        names = [f"p{i}" for i in range(1, 8)]
        node = MockOperatorExpression(
            "+",
            [MockFeatureReferenceExpression(n) for n in names],
        )
        result = build_expression_ast(
            node, input_names=set(names), output_names=set()
        )
        compiled = compile_expression(result)
        expected = (
            "((((((inputs.p1 + inputs.p2) + inputs.p3)"
            " + inputs.p4) + inputs.p5) + inputs.p6) + inputs.p7)"
        )
        assert compiled == expected

    def test_2_operand_not_folded(self, mock_syside_adapter):
        """Binary OE → single binary node, no extra nesting."""
        node = MockOperatorExpression(
            "*",
            [
                MockFeatureReferenceExpression("x"),
                MockFeatureReferenceExpression("y"),
            ],
        )
        result = build_expression_ast(
            node, input_names={"x", "y"}, output_names=set()
        )
        assert result.node_type == ExpressionNodeType.BINARY_OP
        assert result.left.node_type == ExpressionNodeType.INPUT_REF
        assert result.right.node_type == ExpressionNodeType.INPUT_REF
        assert compile_expression(result) == "(inputs.x * inputs.y)"


# ---------------------------------------------------------------------------
# REQ-EC-03: Unit annotation stripping
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EC-03")
class TestReqEc03UnitStripping:
    """Unit annotations ([value, unit]) must be stripped, preserving only value."""

    def test_unit_bracket_strips_unit_preserves_value(self, mock_syside_adapter):
        """`[` operator OE with [value, unit] → returns value subtree only."""
        inner = MockLiteralRational(42.0)
        unit_node = MockFeatureReferenceExpression("kg")
        node = MockOperatorExpression("[", [inner, unit_node])
        result = build_expression_ast(node, input_names=set(), output_names=set())
        assert result.node_type == ExpressionNodeType.LITERAL
        assert result.value == 42.0

    def test_unit_bracket_no_operands_unsupported(self, mock_syside_adapter):
        """`[` operator OE with no operands → UNSUPPORTED."""
        node = MockOperatorExpression("[", [])
        result = build_expression_ast(node, input_names=set(), output_names=set())
        assert result.node_type == ExpressionNodeType.UNSUPPORTED
        assert "unit annotation" in result.reason


# ---------------------------------------------------------------------------
# REQ-EC-04: ast.parse() validation
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EC-04")
class TestReqEc04AstParseValidation:
    """Every compiled expression must validate via ast.parse()."""

    def test_all_compilable_node_types_produce_parseable_python(self):
        """Compile one expression from each compilable node type → ast.parse succeeds."""
        test_cases = {
            "BINARY_OP": ExpressionAST.binary(
                "+", ExpressionAST.input_ref("a"), ExpressionAST.input_ref("b")
            ),
            "UNARY_OP": ExpressionAST.unary("-", ExpressionAST.input_ref("x")),
            "LITERAL": ExpressionAST.literal(3.14),
            "INPUT_REF": ExpressionAST.input_ref("voltage"),
            "INTERMEDIATE_REF": ExpressionAST.intermediate_ref("material_cost"),
        }
        for label, ast_node in test_cases.items():
            result = compile_expression(ast_node)
            python_ast.parse(result, mode="eval")

    def test_complex_nested_expression_parseable(self):
        """CRF-pattern (Pattern C) nested expression → ast.parse succeeds."""
        one_plus_r = ExpressionAST.binary(
            "+", ExpressionAST.literal(1.0), ExpressionAST.input_ref("r")
        )
        power_term = ExpressionAST.binary("**", one_plus_r, ExpressionAST.input_ref("n"))
        numerator = ExpressionAST.binary("*", ExpressionAST.input_ref("r"), power_term)
        denominator = ExpressionAST.binary(
            "-",
            ExpressionAST.binary(
                "**",
                ExpressionAST.binary(
                    "+", ExpressionAST.literal(1.0), ExpressionAST.input_ref("r")
                ),
                ExpressionAST.input_ref("n"),
            ),
            ExpressionAST.literal(1.0),
        )
        crf = ExpressionAST.binary("/", numerator, denominator)
        result = compile_expression(crf)
        python_ast.parse(result, mode="eval")

    def test_unsupported_node_raises_compilation_error(self):
        """UNSUPPORTED node → CompilationError (not invalid Python)."""
        node = ExpressionAST.unsupported("foo.bar", "not supported")
        with pytest.raises(CompilationError):
            compile_expression(node)


# ---------------------------------------------------------------------------
# REQ-EC-05: Cycle detection
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EC-05")
class TestReqEc05CycleDetection:
    """Circular dependencies must mark all outputs MANUAL_REQUIRED."""

    def _make_cycle(self, mock_extract_feature_refs):
        """Helper: create a calc def with mutual dependency (a→b, b→a)."""
        calc_def = _make_calc_def("CycleCalc", input_names=["x"], output_names=["a", "b"])
        a_ast = MockOperatorExpression(
            "+",
            [MockFeatureReferenceExpression("b"), MockFeatureReferenceExpression("x")],
        )
        b_ast = MockOperatorExpression(
            "+",
            [MockFeatureReferenceExpression("a"), MockFeatureReferenceExpression("x")],
        )
        ref_map = mock_extract_feature_refs
        ref_map[id(a_ast)] = ["b", "x"]
        ref_map[id(b_ast)] = ["a", "x"]
        return calc_def, {"a": a_ast, "b": b_ast}

    def test_cycle_marks_all_outputs_manual_required(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Mutual dependency (a→b, b→a) → all outputs MANUAL_REQUIRED."""
        calc_def, expr_asts = self._make_cycle(mock_extract_feature_refs)
        result = compile_calc_def(calc_def, expr_asts)
        assert result.overall_compilability == Compilability.MANUAL_REQUIRED
        assert all(
            r.compilability == Compilability.MANUAL_REQUIRED
            for r in result.output_results
        )

    def test_cycle_produces_empty_execution_order(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Cycle → CalcDefCompilationResult.execution_order == []."""
        calc_def, expr_asts = self._make_cycle(mock_extract_feature_refs)
        result = compile_calc_def(calc_def, expr_asts)
        assert result.execution_order == []

    def test_cycle_unsupported_reason_mentions_circular(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Each MANUAL output from a cycle has 'circular' in unsupported_reason."""
        calc_def, expr_asts = self._make_cycle(mock_extract_feature_refs)
        result = compile_calc_def(calc_def, expr_asts)
        for r in result.output_results:
            assert "circular" in (r.unsupported_reason or ""), (
                f"Output {r.output_name} missing 'circular' in reason: "
                f"{r.unsupported_reason}"
            )


# ---------------------------------------------------------------------------
# REQ-EC-06: Worst-case roll-up
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EC-06")
class TestReqEc06WorstCaseRollup:
    """CalcDef compilability is worst-case across all output results."""

    def test_rollup_all_fully_returns_fully(self):
        """[FULLY, FULLY] → FULLY."""
        results = [
            CompilationResult("a", Compilability.FULLY_COMPILABLE, "expr_a"),
            CompilationResult("b", Compilability.FULLY_COMPILABLE, "expr_b"),
        ]
        assert classify_compilability(results) == Compilability.FULLY_COMPILABLE

    def test_rollup_any_manual_returns_manual(self):
        """[FULLY, MANUAL] → MANUAL."""
        results = [
            CompilationResult("a", Compilability.FULLY_COMPILABLE, "expr_a"),
            CompilationResult("b", Compilability.MANUAL_REQUIRED),
        ]
        assert classify_compilability(results) == Compilability.MANUAL_REQUIRED

    def test_rollup_mixed_returns_partially(self):
        """[FULLY, PARTIALLY] → PARTIALLY."""
        results = [
            CompilationResult("a", Compilability.FULLY_COMPILABLE, "expr_a"),
            CompilationResult("b", Compilability.PARTIALLY_COMPILABLE, "expr_b"),
        ]
        assert classify_compilability(results) == Compilability.PARTIALLY_COMPILABLE

    def test_rollup_empty_returns_manual(self):
        """[] → MANUAL."""
        assert classify_compilability([]) == Compilability.MANUAL_REQUIRED

    def test_rollup_unknown_raises_assertion(self):
        """[UNKNOWN] → AssertionError (UNKNOWN is sentinel, not valid result)."""
        results = [CompilationResult("a", Compilability.UNKNOWN)]
        with pytest.raises(AssertionError, match="UNKNOWN"):
            classify_compilability(results)


# ---------------------------------------------------------------------------
# REQ-EC-07: Undeclared intermediates
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EC-07")
class TestReqEc07UndeclaredIntermediates:
    """Undeclared intermediates must be discovered iteratively from member_expressions."""

    def test_undeclared_intermediate_discovered_from_members(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Output references member not in inputs/outputs → discovered as intermediate."""
        calc_def = _make_calc_def(
            "IntermCalc",
            input_names=["x"],
            output_names=["result"],
            all_member_names=["x", "result", "hidden"],
        )

        hidden_ast = MockOperatorExpression(
            "*",
            [MockFeatureReferenceExpression("x"), MockLiteralRational(2.0)],
        )
        result_ast = MockOperatorExpression(
            "+",
            [MockFeatureReferenceExpression("hidden"), MockLiteralRational(1.0)],
        )

        ref_map = mock_extract_feature_refs
        ref_map[id(result_ast)] = ["hidden"]
        ref_map[id(hidden_ast)] = ["x"]

        result = compile_calc_def(
            calc_def,
            {"result": result_ast},
            all_member_names={"x", "result", "hidden"},
            member_expressions={"hidden": hidden_ast},
        )

        by_name = {r.output_name: r for r in result.output_results}
        assert "hidden" in by_name
        assert by_name["hidden"].is_undeclared_intermediate is True
        assert by_name["hidden"].compilability == Compilability.FULLY_COMPILABLE

    def test_iterative_chain_discovery(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """4-deep chain: inter_a → inter_b → inter_c → inter_d → final_result."""
        calc_def = _make_calc_def(
            "ChainCalc",
            input_names=["i1", "i2"],
            output_names=["final_result"],
            all_member_names=[
                "i1", "i2", "final_result", "inter_a", "inter_b", "inter_c", "inter_d"
            ],
        )

        inter_a_ast = MockOperatorExpression(
            "*",
            [MockFeatureReferenceExpression("i1"), MockLiteralRational(2.0)],
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
            [MockFeatureReferenceExpression("inter_b"), MockLiteralRational(1.5)],
        )
        inter_d_ast = MockOperatorExpression(
            "+",
            [MockFeatureReferenceExpression("inter_c"), MockLiteralRational(100.0)],
        )
        final_ast = MockOperatorExpression(
            "*",
            [MockFeatureReferenceExpression("inter_d"), MockLiteralRational(0.5)],
        )

        all_members = {"i1", "i2", "final_result", "inter_a", "inter_b", "inter_c", "inter_d"}
        member_exprs = {
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
            {"final_result": final_ast},
            all_member_names=all_members,
            member_expressions=member_exprs,
        )

        assert result.execution_order == [
            "inter_a", "inter_b", "inter_c", "inter_d", "final_result"
        ]
        assert result.overall_compilability == Compilability.FULLY_COMPILABLE

    def test_undeclared_flag_set_correctly(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """is_undeclared_intermediate=True for discovered members, False for declared outputs."""
        calc_def = _make_calc_def(
            "FlagCalc",
            input_names=["x"],
            output_names=["result"],
            all_member_names=["x", "result", "hidden"],
        )

        hidden_ast = MockOperatorExpression(
            "*",
            [MockFeatureReferenceExpression("x"), MockLiteralRational(2.0)],
        )
        result_ast = MockOperatorExpression(
            "+",
            [MockFeatureReferenceExpression("hidden"), MockLiteralRational(1.0)],
        )

        ref_map = mock_extract_feature_refs
        ref_map[id(result_ast)] = ["hidden"]
        ref_map[id(hidden_ast)] = ["x"]

        result = compile_calc_def(
            calc_def,
            {"result": result_ast},
            all_member_names={"x", "result", "hidden"},
            member_expressions={"hidden": hidden_ast},
        )

        by_name = {r.output_name: r for r in result.output_results}
        assert by_name["hidden"].is_undeclared_intermediate is True
        assert by_name["result"].is_undeclared_intermediate is False

    def test_undeclared_without_member_expression_gets_manual(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Undeclared intermediate with no member_expressions entry → MANUAL_REQUIRED."""
        calc_def = _make_calc_def(
            "NoExprCalc",
            input_names=["x"],
            output_names=["result"],
            all_member_names=["x", "result", "missing_inter"],
        )

        result_ast = MockOperatorExpression(
            "+",
            [MockFeatureReferenceExpression("missing_inter"), MockLiteralRational(1.0)],
        )

        ref_map = mock_extract_feature_refs
        ref_map[id(result_ast)] = ["missing_inter"]

        result = compile_calc_def(
            calc_def,
            {"result": result_ast},
            all_member_names={"x", "result", "missing_inter"},
            member_expressions={},
        )

        by_name = {r.output_name: r for r in result.output_results}
        assert by_name["missing_inter"].compilability == Compilability.MANUAL_REQUIRED
        assert "no expression AST" in by_name["missing_inter"].unsupported_reason


# ---------------------------------------------------------------------------
# REQ-AST-01: FCE before OE dispatch ordering (static analysis)
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-AST-01")
class TestReqAst01DispatchOrdering:
    """Static analysis: FCE checked before OE at every dispatch site."""

    def test_dispatch_ordering_in_expression_compiler(self):
        """expression_compiler.py build_expression_ast: FCE line < OE line."""
        calls = _find_is_instance_calls_in_function(
            EXPRESSION_COMPILER_PATH, "build_expression_ast"
        )
        assert "FeatureChainExpression" in calls
        assert "OperatorExpression" in calls
        assert calls["FeatureChainExpression"] < calls["OperatorExpression"], (
            f"FCE at line {calls['FeatureChainExpression']} must precede "
            f"OE at line {calls['OperatorExpression']}"
        )

    def test_dispatch_ordering_in_expression_utils(self):
        """expression_utils.py reconstruct_expression: FCE line < OE line."""
        calls = _find_is_instance_calls_in_function(
            EXPRESSION_UTILS_PATH, "reconstruct_expression"
        )
        assert "FeatureChainExpression" in calls
        assert "OperatorExpression" in calls
        assert calls["FeatureChainExpression"] < calls["OperatorExpression"], (
            f"FCE at line {calls['FeatureChainExpression']} must precede "
            f"OE at line {calls['OperatorExpression']}"
        )


# ---------------------------------------------------------------------------
# Cross-model validation
# ---------------------------------------------------------------------------

CROSS_MODEL_IDS = ["solar_battery_model", "catf_mfe_model", "chain_spike_model"]


class TestCrossModelValidation:
    """Verify compiler behavior against real model metadata from snapshots."""

    @pytest.mark.req("REQ-EC-04")
    @pytest.mark.parametrize(
        "model_name",
        CROSS_MODEL_IDS,
        ids=["solar_battery", "catf_mfe", "chain_spike"],
    )
    def test_reference_resolution_with_real_attribute_names(
        self, extraction_snapshots, model_name, mock_syside_adapter
    ):
        """Build mock FRE nodes using real attribute names → verify correct classification."""
        snapshot = extraction_snapshots[model_name]
        for cd in snapshot["calc_defs"]:
            input_names, output_names = _extract_name_sets(cd)

            for name in input_names:
                node = MockFeatureReferenceExpression(name)
                result = build_expression_ast(
                    node, input_names=input_names, output_names=output_names
                )
                assert result.node_type == ExpressionNodeType.INPUT_REF, (
                    f"{model_name}/{cd.name}: input '{name}' classified as "
                    f"{result.node_type}, expected INPUT_REF"
                )
                assert result.input_name == name

            for name in output_names:
                node = MockFeatureReferenceExpression(name)
                result = build_expression_ast(
                    node, input_names=input_names, output_names=output_names
                )
                assert result.node_type == ExpressionNodeType.INTERMEDIATE_REF, (
                    f"{model_name}/{cd.name}: output '{name}' classified as "
                    f"{result.node_type}, expected INTERMEDIATE_REF"
                )
                assert result.intermediate_name == name

    @pytest.mark.req("REQ-EC-06")
    @pytest.mark.parametrize(
        "model_name",
        ["solar_battery_model", "catf_mfe_model"],
        ids=["solar_battery", "catf_mfe"],
    )
    def test_compile_calc_def_with_real_metadata(
        self,
        extraction_snapshots,
        model_name,
        mock_syside_adapter,
        mock_extract_feature_refs,
    ):
        """compile_calc_def with real calc def metadata → valid compilation result."""
        snapshot = extraction_snapshots[model_name]
        ref_map = mock_extract_feature_refs

        for cd in snapshot["calc_defs"]:
            input_names, output_names = _extract_name_sets(cd)
            if not output_names:
                continue

            expression_asts = {}
            for out_name in output_names:
                if input_names:
                    first_input = sorted(input_names)[0]
                    ast_node = MockOperatorExpression(
                        "*",
                        [
                            MockFeatureReferenceExpression(first_input),
                            MockLiteralRational(1.0),
                        ],
                    )
                    ref_map[id(ast_node)] = [first_input]
                else:
                    ast_node = MockLiteralRational(1.0)
                    ref_map[id(ast_node)] = []
                expression_asts[out_name] = ast_node

            result = compile_calc_def(cd, expression_asts)

            assert result.calc_def_name == cd.name, (
                f"{model_name}/{cd.name}: calc_def_name mismatch"
            )
            assert result.overall_compilability in (
                Compilability.FULLY_COMPILABLE,
                Compilability.MANUAL_REQUIRED,
            ), (
                f"{model_name}/{cd.name}: unexpected compilability "
                f"{result.overall_compilability}"
            )
            assert len(result.execution_order) > 0, (
                f"{model_name}/{cd.name}: empty execution_order"
            )
            assert len(result.output_results) == len(output_names), (
                f"{model_name}/{cd.name}: expected {len(output_names)} output_results, "
                f"got {len(result.output_results)}"
            )
