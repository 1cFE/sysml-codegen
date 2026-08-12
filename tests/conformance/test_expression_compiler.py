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
- Cross-model validation uses real calc def metadata (names, attributes) from live
  extraction (``tests/helpers/live_extraction.py``), not the retiring v5 extraction
  snapshots, with mock ASTs; those nodes are license-gated by the fixture.

Requirements: REQ-EC-01 through REQ-EC-07, REQ-AST-01.
"""

from __future__ import annotations

import ast as python_ast
from pathlib import Path
from types import SimpleNamespace

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


def test_exact_compiler_surface_does_not_replace_the_legacy_adapter():
    """The exact route has an explicit UUID API; legacy callers retain their adapter."""
    from sysml_codegen.extraction.expression_compiler import (
        compile_calc_def,
        compile_calc_def_exact,
    )

    assert compile_calc_def_exact is not compile_calc_def


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
        from sysml_codegen.extraction.expression_compiler import compile_calc_def

        calc_def, expr_asts = self._make_cycle(mock_extract_feature_refs)
        result = compile_calc_def(calc_def, expr_asts)
        assert result.overall_compilability == Compilability.MANUAL_REQUIRED
        assert all(r.compilability == Compilability.MANUAL_REQUIRED for r in result.output_results)

    def test_cycle_produces_empty_execution_order(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Cycle → CalcDefCompilationResult.execution_order == []."""
        from sysml_codegen.extraction.expression_compiler import compile_calc_def

        calc_def, expr_asts = self._make_cycle(mock_extract_feature_refs)
        result = compile_calc_def(calc_def, expr_asts)
        assert result.execution_order == []

    def test_cycle_unsupported_reason_mentions_circular(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Each MANUAL output from a cycle has 'circular' in unsupported_reason."""
        from sysml_codegen.extraction.expression_compiler import compile_calc_def

        calc_def, expr_asts = self._make_cycle(mock_extract_feature_refs)
        result = compile_calc_def(calc_def, expr_asts)
        for r in result.output_results:
            assert "circular" in (r.unsupported_reason or ""), (
                f"Output {r.output_name} missing 'circular' in reason: {r.unsupported_reason}"
            )


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
# REQ-EC-07: Undeclared intermediates
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-EC-07")
class TestReqEc07UndeclaredIntermediates:
    """Undeclared intermediates must be discovered iteratively from member_expressions."""

    def test_undeclared_intermediate_discovered_from_members(
        self, mock_syside_adapter, mock_extract_feature_refs
    ):
        """Output references member not in inputs/outputs → discovered as intermediate."""
        from sysml_codegen.extraction.expression_compiler import compile_calc_def

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

    def test_iterative_chain_discovery(self, mock_syside_adapter, mock_extract_feature_refs):
        """4-deep chain: inter_a → inter_b → inter_c → inter_d → final_result."""
        from sysml_codegen.extraction.expression_compiler import compile_calc_def

        calc_def = _make_calc_def(
            "ChainCalc",
            input_names=["i1", "i2"],
            output_names=["final_result"],
            all_member_names=[
                "i1",
                "i2",
                "final_result",
                "inter_a",
                "inter_b",
                "inter_c",
                "inter_d",
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
            "inter_a",
            "inter_b",
            "inter_c",
            "inter_d",
            "final_result",
        ]
        assert result.overall_compilability == Compilability.FULLY_COMPILABLE

    def test_undeclared_flag_set_correctly(self, mock_syside_adapter, mock_extract_feature_refs):
        """is_undeclared_intermediate=True for discovered members, False for declared outputs."""
        from sysml_codegen.extraction.expression_compiler import compile_calc_def

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
        from sysml_codegen.extraction.expression_compiler import compile_calc_def

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
    """Verify compiler behavior against real model metadata from snapshots."""

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

    @pytest.mark.req("REQ-EC-06")
    @pytest.mark.parametrize(
        "model_name",
        ["solar_battery_model", "catf_mfe_model"],
        ids=["solar_battery", "catf_mfe"],
    )
    def test_compile_calc_def_with_real_metadata(
        self,
        live_extraction_facts,
        model_name,
        mock_syside_adapter,
        mock_extract_feature_refs,
    ):
        """compile_calc_def with real calc def metadata → valid compilation result."""
        from sysml_codegen.extraction.expression_compiler import compile_calc_def

        snapshot = live_extraction_facts[model_name]
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
            ), f"{model_name}/{cd.name}: unexpected compilability {result.overall_compilability}"
            assert len(result.execution_order) > 0, f"{model_name}/{cd.name}: empty execution_order"
            assert len(result.output_results) == len(output_names), (
                f"{model_name}/{cd.name}: expected {len(output_names)} output_results, "
                f"got {len(result.output_results)}"
            )
