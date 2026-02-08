"""Unit tests for computed attribute extraction data models and logic."""

from pathlib import Path
from types import SimpleNamespace

import pytest


# ---------------------------------------------------------------------------
# Phase 1: Data model tests
# ---------------------------------------------------------------------------


class TestComputedAttributeClassification:
    """Tests for ComputedAttributeClassification enum."""

    def test_all_values_exist(self):
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
        )

        assert set(ComputedAttributeClassification) == {
            ComputedAttributeClassification.FORMULA,
            ComputedAttributeClassification.EXPOSE_PURE,
            ComputedAttributeClassification.EXPOSE_COMPUTED,
            ComputedAttributeClassification.LITERAL,
            ComputedAttributeClassification.UNRESOLVABLE,
        }

    def test_string_inheritance(self):
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
        )

        assert isinstance(ComputedAttributeClassification.FORMULA, str)
        assert ComputedAttributeClassification.FORMULA == "formula"
        assert ComputedAttributeClassification.EXPOSE_PURE == "expose_pure"
        assert ComputedAttributeClassification.EXPOSE_COMPUTED == "expose_computed"
        assert ComputedAttributeClassification.LITERAL == "literal"
        assert ComputedAttributeClassification.UNRESOLVABLE == "unresolvable"


class TestComputedAttributeData:
    """Tests for ComputedAttributeData dataclass."""

    def test_construction_all_fields(self):
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
            ComputedAttributeData,
        )
        from sysml_codegen.extraction.expression_compiler import Compilability

        data = ComputedAttributeData(
            name="area",
            python_name="area",
            owning_part_name="probe_design",
            owning_part_qualified_name="AttrExprProbeDesign::probe_design",
            expression_ast=None,
            expression_text="length * width",
            references=[],
            classification=ComputedAttributeClassification.FORMULA,
            compilability=Compilability.FULLY_COMPILABLE,
            compiled_expression="(inputs.length * inputs.width)",
            source_file=Path("design.sysml"),
            source_line=42,
        )
        assert data.name == "area"
        assert data.python_name == "area"
        assert data.owning_part_name == "probe_design"
        assert data.owning_part_qualified_name == "AttrExprProbeDesign::probe_design"
        assert data.expression_ast is None
        assert data.expression_text == "length * width"
        assert data.references == []
        assert data.classification == ComputedAttributeClassification.FORMULA
        assert data.compilability == Compilability.FULLY_COMPILABLE
        assert data.compiled_expression == "(inputs.length * inputs.width)"
        assert data.source_file == Path("design.sysml")
        assert data.source_line == 42

    def test_defaults(self):
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
            ComputedAttributeData,
        )
        from sysml_codegen.extraction.expression_compiler import Compilability

        data = ComputedAttributeData(
            name="area",
            python_name="area",
            owning_part_name="part",
            owning_part_qualified_name="Pkg::Part",
            expression_ast=None,
            expression_text="length * width",
            references=[],
            classification=ComputedAttributeClassification.FORMULA,
            compilability=Compilability.FULLY_COMPILABLE,
        )
        assert data.compiled_expression is None
        assert data.source_file == Path("unknown")
        assert data.source_line == 0


# ---------------------------------------------------------------------------
# Phase 2: Mock infrastructure + classification tests
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


class MockAttributeUsage:
    """Mock syside AttributeUsage element."""

    def __init__(self, name: str, expr=None, qualified_name: str = ""):
        self.name = name
        self.feature_value_expression = expr
        self.qualified_name = qualified_name or f"TestPkg::TestPart::{name}"


class MockCalculationUsage:
    """Mock syside CalculationUsage element."""

    def __init__(self, name: str, qualified_name: str = ""):
        self.name = name
        self.qualified_name = qualified_name or f"TestPkg::TestPart::{name}"


class MockPartElement:
    """Mock syside PartDef/PartUsage element."""

    def __init__(self, name: str, owned_members: list, qualified_name: str = ""):
        self.name = name
        self.owned_members = owned_members
        self.qualified_name = qualified_name or f"TestPkg::{name}"


TYPE_MAP = {
    "MockOperatorExpression": "OperatorExpression",
    "MockFeatureReferenceExpression": "FeatureReferenceExpression",
    "MockLiteralRational": "LiteralRational",
    "MockFeatureChainExpression": "FeatureChainExpression",
    "MockAttributeUsage": "AttributeUsage",
    "MockCalculationUsage": "CalculationUsage",
}


@pytest.fixture
def mock_syside_adapter(monkeypatch):
    """Monkeypatch SysideAdapter.is_instance to work with mock nodes."""

    def mock_is_instance(node, type_name):
        return TYPE_MAP.get(type(node).__name__) == type_name

    # Patch in both modules that use SysideAdapter.is_instance
    monkeypatch.setattr(
        "sysml_codegen.extraction.expression_compiler.SysideAdapter.is_instance",
        staticmethod(mock_is_instance),
    )
    monkeypatch.setattr(
        "sysml_codegen.extraction.computed_attribute_extractor.SysideAdapter.is_instance",
        staticmethod(mock_is_instance),
    )
    monkeypatch.setattr(
        "sysml_codegen.extraction.expression_utils.SysideAdapter.is_instance",
        staticmethod(mock_is_instance),
    )


def _make_refs(*ref_tuples):
    """Helper to create ExpressionRef objects from (name, qualified_name) tuples."""
    from agentic_mbse.sysml.types import ExpressionRef

    return [
        ExpressionRef(name=name, qualified_name=qn) for name, qn in ref_tuples
    ]


class TestClassifyAttributeExpression:
    """Tests for _classify_attribute_expression() classification logic."""

    def test_formula_simple(self, mock_syside_adapter, monkeypatch):
        """area = length * width → FORMULA (classification only, no compilation)."""
        from sysml_codegen.extraction.computed_attribute_extractor import (
            _classify_attribute_expression,
        )
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
        )

        expr = MockOperatorExpression("*", [
            MockFeatureReferenceExpression("length"),
            MockFeatureReferenceExpression("width"),
        ])
        refs = _make_refs(
            ("length", "TestPkg::TestPart::length"),
            ("width", "TestPkg::TestPart::width"),
        )
        result = _classify_attribute_expression(
            refs=refs,
            owning_part_qualified_name="TestPkg::TestPart",
            calc_usage_names=set(),
            sibling_attr_names={"length", "width", "area"},
            expression_ast=expr,
        )
        assert result == ComputedAttributeClassification.FORMULA

    def test_expose_pure(self, mock_syside_adapter, monkeypatch):
        """p_alpha_out = alpha_split.p_alpha → EXPOSE_PURE.

        FeatureChainExpression produces two refs:
        1. calc output ref (different namespace) → calc_ref
        2. calc usage instance ref (same part namespace) → filtered by step 2a
        """
        from sysml_codegen.extraction.computed_attribute_extractor import (
            _classify_attribute_expression,
        )
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
        )

        expr = MockFeatureChainExpression()
        refs = _make_refs(
            ("p_alpha", "Library::AlphaSplitCalc::p_alpha"),
            ("alpha_split", "Pkg::Part::alpha_split"),
        )
        result = _classify_attribute_expression(
            refs=refs,
            owning_part_qualified_name="Pkg::Part",
            calc_usage_names={"alpha_split"},
            sibling_attr_names={"p_alpha_out", "some_attr"},
            expression_ast=expr,
        )
        assert result == ComputedAttributeClassification.EXPOSE_PURE

    def test_expose_computed(self, mock_syside_adapter, monkeypatch):
        """scaled_area = scale_calc.result * 2.0 → EXPOSE_COMPUTED.

        Root is OperatorExpression (not FeatureChainExpression), so this
        is EXPOSE_COMPUTED even though the only semantic ref is a calc_ref.
        """
        from sysml_codegen.extraction.computed_attribute_extractor import (
            _classify_attribute_expression,
        )
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
        )

        expr = MockOperatorExpression("*", [
            MockFeatureChainExpression(),
            MockLiteralRational(2.0),
        ])
        refs = _make_refs(
            ("result", "Library::ScaleCalc::result"),
            ("scale_calc", "Pkg::Part::scale_calc"),
        )
        result = _classify_attribute_expression(
            refs=refs,
            owning_part_qualified_name="Pkg::Part",
            calc_usage_names={"scale_calc"},
            sibling_attr_names={"scaled_area"},
            expression_ast=expr,
        )
        assert result == ComputedAttributeClassification.EXPOSE_COMPUTED

    def test_literal_no_refs(self, mock_syside_adapter, monkeypatch):
        """length = 10.0 → LITERAL (no feature references)."""
        from sysml_codegen.extraction.computed_attribute_extractor import (
            _classify_attribute_expression,
        )
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
        )

        expr = MockLiteralRational(10.0)
        result = _classify_attribute_expression(
            refs=[],
            owning_part_qualified_name="Pkg::Part",
            calc_usage_names=set(),
            sibling_attr_names={"length"},
            expression_ast=expr,
        )
        assert result == ComputedAttributeClassification.LITERAL

    def test_unresolvable(self, mock_syside_adapter, monkeypatch):
        """broken = length * mystery → UNRESOLVABLE.

        'mystery' has empty qualified_name and is not in sibling_attr_names
        or calc_usage_names.
        """
        from sysml_codegen.extraction.computed_attribute_extractor import (
            _classify_attribute_expression,
        )
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
        )

        expr = MockOperatorExpression("*", [
            MockFeatureReferenceExpression("length"),
            MockFeatureReferenceExpression("mystery"),
        ])
        refs = _make_refs(
            ("length", "Pkg::Part::length"),
            ("mystery", ""),  # empty QN → falls to step 2d → not in siblings → unresolvable
        )
        result = _classify_attribute_expression(
            refs=refs,
            owning_part_qualified_name="Pkg::Part",
            calc_usage_names=set(),
            sibling_attr_names={"length", "broken"},
            expression_ast=expr,
        )
        assert result == ComputedAttributeClassification.UNRESOLVABLE

    def test_qualified_name_collision(self, mock_syside_adapter, monkeypatch):
        """Regression test for 19-CATF bug.

        Sibling attribute 'p_alpha' exists AND a CalcDef output is also
        named 'p_alpha'. The ref's qualified_name is in the CalcDef
        namespace (Library::CalcDef::p_alpha), NOT the owning part namespace.
        Must be classified as calc_ref, not sibling_ref.
        """
        from sysml_codegen.extraction.computed_attribute_extractor import (
            _classify_attribute_expression,
        )
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
        )

        expr = MockFeatureChainExpression()
        refs = _make_refs(
            # QN is in CalcDef namespace, NOT owning part namespace
            ("p_alpha", "CATFLibrary::AlphaNeutronSplitCalc::p_alpha"),
            ("alpha_neutron_split", "CATFDesign::FusionPlasmaPhysics::alpha_neutron_split"),
        )
        result = _classify_attribute_expression(
            refs=refs,
            owning_part_qualified_name="CATFDesign::FusionPlasmaPhysics",
            calc_usage_names={"alpha_neutron_split"},
            # p_alpha exists as a sibling! But QN says it's from CalcDef namespace.
            sibling_attr_names={"p_alpha", "p_alpha_out", "some_other"},
            expression_ast=expr,
        )
        # Must be EXPOSE (calc_ref), NOT FORMULA (sibling_ref)
        assert result == ComputedAttributeClassification.EXPOSE_PURE


# ---------------------------------------------------------------------------
# Phase 3: FORMULA compilation tests + integration test
# ---------------------------------------------------------------------------


class TestFormulaCompilation:
    """Tests for FORMULA compilation via extract_computed_attributes()."""

    def test_formula_simple_binary(self, mock_syside_adapter, monkeypatch):
        """area = length * width → compiled to (inputs.length * inputs.width).

        Full end-to-end: classification + compilation through
        extract_computed_attributes().
        """
        from sysml_codegen.extraction.computed_attribute_extractor import (
            extract_computed_attributes,
        )
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
        )
        from sysml_codegen.extraction.expression_compiler import Compilability

        expr = MockOperatorExpression("*", [
            MockFeatureReferenceExpression("length"),
            MockFeatureReferenceExpression("width"),
        ])
        part = MockPartElement(
            "test_part",
            [
                MockAttributeUsage("length", expr=MockLiteralRational(5.0),
                                   qualified_name="Pkg::test_part::length"),
                MockAttributeUsage("width", expr=MockLiteralRational(3.0),
                                   qualified_name="Pkg::test_part::width"),
                MockAttributeUsage("area", expr=expr,
                                   qualified_name="Pkg::test_part::area"),
            ],
            qualified_name="Pkg::test_part",
        )

        refs_map = {
            id(MockLiteralRational): [],  # literals have no refs
        }

        def mock_extract_feature_refs(expr_node, ignore_std_lib=True):
            # area's expression → sibling refs
            if isinstance(expr_node, MockOperatorExpression):
                return _make_refs(
                    ("length", "Pkg::test_part::length"),
                    ("width", "Pkg::test_part::width"),
                )
            # literal expressions → no refs
            return []

        monkeypatch.setattr(
            "sysml_codegen.extraction.computed_attribute_extractor.extract_feature_refs",
            mock_extract_feature_refs,
        )

        results = extract_computed_attributes(None, part, calc_usage_names=set())

        # length and width are LITERAL (no refs) → excluded
        # area is FORMULA → included and compiled
        assert len(results) == 1
        area = results[0]
        assert area.name == "area"
        assert area.classification == ComputedAttributeClassification.FORMULA
        assert area.compiled_expression == "(inputs.length * inputs.width)"
        assert area.compilability == Compilability.FULLY_COMPILABLE

    def test_formula_complex_nested(self, mock_syside_adapter, monkeypatch):
        """p_blanket = m_n * p_f + p_in → correct nested compilation.

        Tests n-ary left-fold: (m_n * p_f) + p_in → ((inputs.m_n * inputs.p_f) + inputs.p_in)
        """
        from sysml_codegen.extraction.computed_attribute_extractor import (
            extract_computed_attributes,
        )
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
        )
        from sysml_codegen.extraction.expression_compiler import Compilability

        # m_n * p_f
        multiply = MockOperatorExpression("*", [
            MockFeatureReferenceExpression("m_n"),
            MockFeatureReferenceExpression("p_f"),
        ])
        # (m_n * p_f) + p_in
        add = MockOperatorExpression("+", [multiply, MockFeatureReferenceExpression("p_in")])

        part = MockPartElement(
            "physics_part",
            [
                MockAttributeUsage("m_n", expr=MockLiteralRational(1.0),
                                   qualified_name="Pkg::physics_part::m_n"),
                MockAttributeUsage("p_f", expr=MockLiteralRational(2.0),
                                   qualified_name="Pkg::physics_part::p_f"),
                MockAttributeUsage("p_in", expr=MockLiteralRational(3.0),
                                   qualified_name="Pkg::physics_part::p_in"),
                MockAttributeUsage("p_blanket", expr=add,
                                   qualified_name="Pkg::physics_part::p_blanket"),
            ],
            qualified_name="Pkg::physics_part",
        )

        def mock_extract_feature_refs(expr_node, ignore_std_lib=True):
            if isinstance(expr_node, MockOperatorExpression):
                return _make_refs(
                    ("m_n", "Pkg::physics_part::m_n"),
                    ("p_f", "Pkg::physics_part::p_f"),
                    ("p_in", "Pkg::physics_part::p_in"),
                )
            return []

        monkeypatch.setattr(
            "sysml_codegen.extraction.computed_attribute_extractor.extract_feature_refs",
            mock_extract_feature_refs,
        )

        results = extract_computed_attributes(None, part, calc_usage_names=set())

        # Only p_blanket is non-LITERAL
        assert len(results) == 1
        p_blanket = results[0]
        assert p_blanket.name == "p_blanket"
        assert p_blanket.classification == ComputedAttributeClassification.FORMULA
        assert p_blanket.compiled_expression == "((inputs.m_n * inputs.p_f) + inputs.p_in)"
        assert p_blanket.compilability == Compilability.FULLY_COMPILABLE

    def test_formula_chain_no_special_handling(self, mock_syside_adapter, monkeypatch):
        """cost = area * rate where area is also computed → no chain awareness.

        Both 'area' and 'rate' are sibling attributes. The fact that 'area'
        is itself computed is irrelevant at extraction time — it compiles
        to inputs.area just like any other sibling ref. Chain resolution
        is Item 3's concern.
        """
        from sysml_codegen.extraction.computed_attribute_extractor import (
            extract_computed_attributes,
        )
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
        )
        from sysml_codegen.extraction.expression_compiler import Compilability

        cost_expr = MockOperatorExpression("*", [
            MockFeatureReferenceExpression("area"),
            MockFeatureReferenceExpression("rate"),
        ])
        area_expr = MockOperatorExpression("*", [
            MockFeatureReferenceExpression("length"),
            MockFeatureReferenceExpression("width"),
        ])

        part = MockPartElement(
            "cost_part",
            [
                MockAttributeUsage("length", expr=MockLiteralRational(5.0),
                                   qualified_name="Pkg::cost_part::length"),
                MockAttributeUsage("width", expr=MockLiteralRational(3.0),
                                   qualified_name="Pkg::cost_part::width"),
                MockAttributeUsage("rate", expr=MockLiteralRational(10.0),
                                   qualified_name="Pkg::cost_part::rate"),
                MockAttributeUsage("area", expr=area_expr,
                                   qualified_name="Pkg::cost_part::area"),
                MockAttributeUsage("cost", expr=cost_expr,
                                   qualified_name="Pkg::cost_part::cost"),
            ],
            qualified_name="Pkg::cost_part",
        )

        def mock_extract_feature_refs(expr_node, ignore_std_lib=True):
            if expr_node is cost_expr:
                return _make_refs(
                    ("area", "Pkg::cost_part::area"),
                    ("rate", "Pkg::cost_part::rate"),
                )
            if expr_node is area_expr:
                return _make_refs(
                    ("length", "Pkg::cost_part::length"),
                    ("width", "Pkg::cost_part::width"),
                )
            return []

        monkeypatch.setattr(
            "sysml_codegen.extraction.computed_attribute_extractor.extract_feature_refs",
            mock_extract_feature_refs,
        )

        results = extract_computed_attributes(None, part, calc_usage_names=set())

        # area and cost are FORMULA; length, width, rate are LITERAL
        assert len(results) == 2
        by_name = {r.name: r for r in results}

        area = by_name["area"]
        assert area.classification == ComputedAttributeClassification.FORMULA
        assert area.compiled_expression == "(inputs.length * inputs.width)"
        assert area.compilability == Compilability.FULLY_COMPILABLE

        cost = by_name["cost"]
        assert cost.classification == ComputedAttributeClassification.FORMULA
        # No chain awareness — area is just another input ref
        assert cost.compiled_expression == "(inputs.area * inputs.rate)"
        assert cost.compilability == Compilability.FULLY_COMPILABLE


    def test_formula_compilation_graceful_degradation(self, mock_syside_adapter, monkeypatch):
        """FR-10: FORMULA with unsupported operator → MANUAL_REQUIRED, not exception.

        The expression classifies as FORMULA (all sibling refs), but the
        'mod' operator is not in PYTHON_OPERATOR_MAP, so build_expression_ast
        produces an UNSUPPORTED node and compile_expression raises
        CompilationError. The extractor must catch this and degrade to
        MANUAL_REQUIRED rather than propagating the exception.
        """
        from sysml_codegen.extraction.computed_attribute_extractor import (
            extract_computed_attributes,
        )
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
        )
        from sysml_codegen.extraction.expression_compiler import Compilability

        # 'mod' is not in PYTHON_OPERATOR_MAP → triggers UNSUPPORTED → CompilationError
        expr = MockOperatorExpression("mod", [
            MockFeatureReferenceExpression("a"),
            MockFeatureReferenceExpression("b"),
        ])
        part = MockPartElement(
            "test_part",
            [
                MockAttributeUsage("a", expr=MockLiteralRational(10.0),
                                   qualified_name="Pkg::test_part::a"),
                MockAttributeUsage("b", expr=MockLiteralRational(3.0),
                                   qualified_name="Pkg::test_part::b"),
                MockAttributeUsage("remainder", expr=expr,
                                   qualified_name="Pkg::test_part::remainder"),
            ],
            qualified_name="Pkg::test_part",
        )

        def mock_extract_feature_refs(expr_node, ignore_std_lib=True):
            if isinstance(expr_node, MockOperatorExpression):
                return _make_refs(
                    ("a", "Pkg::test_part::a"),
                    ("b", "Pkg::test_part::b"),
                )
            return []

        monkeypatch.setattr(
            "sysml_codegen.extraction.computed_attribute_extractor.extract_feature_refs",
            mock_extract_feature_refs,
        )

        # Must not raise — graceful degradation
        results = extract_computed_attributes(None, part, calc_usage_names=set())

        assert len(results) == 1
        remainder = results[0]
        assert remainder.name == "remainder"
        assert remainder.classification == ComputedAttributeClassification.FORMULA
        assert remainder.compiled_expression is None
        assert remainder.compilability == Compilability.MANUAL_REQUIRED


class TestExtractComputedAttributes:
    """Integration test for extract_computed_attributes() with mixed attribute types."""

    def test_mixed_part_element(self, mock_syside_adapter, monkeypatch):
        """Part with FORMULA + LITERAL + EXPOSE attrs → correct filtering and count."""
        from sysml_codegen.extraction.computed_attribute_extractor import (
            extract_computed_attributes,
        )
        from sysml_codegen.extraction.data_models import (
            ComputedAttributeClassification,
        )
        from sysml_codegen.extraction.expression_compiler import Compilability

        # FORMULA: area = length * width
        area_expr = MockOperatorExpression("*", [
            MockFeatureReferenceExpression("length"),
            MockFeatureReferenceExpression("width"),
        ])
        # LITERAL: length = 5.0
        literal_expr = MockLiteralRational(5.0)
        # EXPOSE_PURE: out = scale_calc.result
        expose_expr = MockFeatureChainExpression()

        part = MockPartElement(
            "mixed_part",
            [
                MockAttributeUsage("length", expr=literal_expr,
                                   qualified_name="Pkg::mixed_part::length"),
                MockAttributeUsage("width", expr=MockLiteralRational(3.0),
                                   qualified_name="Pkg::mixed_part::width"),
                MockAttributeUsage("area", expr=area_expr,
                                   qualified_name="Pkg::mixed_part::area"),
                MockAttributeUsage("out", expr=expose_expr,
                                   qualified_name="Pkg::mixed_part::out"),
                MockCalculationUsage("scale_calc",
                                     qualified_name="Pkg::mixed_part::scale_calc"),
            ],
            qualified_name="Pkg::mixed_part",
        )

        def mock_extract_feature_refs(expr_node, ignore_std_lib=True):
            if expr_node is area_expr:
                return _make_refs(
                    ("length", "Pkg::mixed_part::length"),
                    ("width", "Pkg::mixed_part::width"),
                )
            if expr_node is expose_expr:
                return _make_refs(
                    ("result", "Library::ScaleCalc::result"),
                    ("scale_calc", "Pkg::mixed_part::scale_calc"),
                )
            # literals → no refs
            return []

        monkeypatch.setattr(
            "sysml_codegen.extraction.computed_attribute_extractor.extract_feature_refs",
            mock_extract_feature_refs,
        )

        results = extract_computed_attributes(
            None, part, calc_usage_names={"scale_calc"}
        )

        # LITERAL (length, width) excluded → 2 results: area + out
        assert len(results) == 2
        by_name = {r.name: r for r in results}

        # FORMULA: area compiled
        area = by_name["area"]
        assert area.classification == ComputedAttributeClassification.FORMULA
        assert area.compiled_expression == "(inputs.length * inputs.width)"
        assert area.compilability == Compilability.FULLY_COMPILABLE

        # EXPOSE_PURE: out not compiled
        out = by_name["out"]
        assert out.classification == ComputedAttributeClassification.EXPOSE_PURE
        assert out.compiled_expression is None
        assert out.compilability == Compilability.MANUAL_REQUIRED
