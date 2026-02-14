"""Unit tests for ChannelAlias production from EXPOSE_PURE and CHAIN sources.

Phase 1: EXPOSE_PURE alias production + is_on_part_definition field
Phase 2: find_instance_paths_for_partdef() + _build_chain_aliases()
"""

import logging
from types import SimpleNamespace

import pytest

from sysml_codegen.core.models import ChannelAlias
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ComputedAttributeData,
)
from sysml_codegen.extraction.expression_compiler import Compilability


# ---------------------------------------------------------------------------
# Mock infrastructure (reused from test_computed_attribute_extraction.py)
# ---------------------------------------------------------------------------


class MockOperatorExpression:
    def __init__(self, operator: str, operands: list):
        self.operator = operator
        self.operands = operands


class MockFeatureReferenceExpression:
    def __init__(self, name: str):
        self.referent = SimpleNamespace(name=name)


class MockLiteralRational:
    def __init__(self, value: float):
        self.value = value


class MockFeatureChainExpression:
    pass


class MockAttributeUsage:
    def __init__(self, name: str, expr=None, qualified_name: str = ""):
        self.name = name
        self.feature_value_expression = expr
        self.qualified_name = qualified_name or f"TestPkg::TestPart::{name}"


class MockCalculationUsage:
    def __init__(self, name: str, qualified_name: str = ""):
        self.name = name
        self.qualified_name = qualified_name or f"TestPkg::TestPart::{name}"


class MockPartElement:
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
    "MockPartElement": "PartDefinition",  # Default — overridden per test
}


def _make_refs(*ref_tuples):
    from agentic_mbse.sysml.types import ExpressionRef

    return [
        ExpressionRef(name=name, qualified_name=qn) for name, qn in ref_tuples
    ]


@pytest.fixture
def mock_syside_adapter(monkeypatch):
    """Monkeypatch SysideAdapter.is_instance to work with mock nodes.

    By default, MockPartElement maps to "PartDefinition". Tests that need
    PartUsage behavior should use the part_as_usage fixture instead.
    """
    type_map = dict(TYPE_MAP)

    def mock_is_instance(node, type_name):
        return type_map.get(type(node).__name__) == type_name

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
    return type_map


# ---------------------------------------------------------------------------
# Phase 1: EXPOSE_PURE Alias Production
# ---------------------------------------------------------------------------


class TestExposePureAliasProduction:
    """Tests for EXPOSE_PURE → ChannelAlias production in extract_computed_attributes()."""

    def test_partusage_expose_pure_produces_channel_alias(
        self, mock_syside_adapter, monkeypatch
    ):
        """EXPOSE_PURE on PartUsage with 2 refs → ChannelAlias with bare alias_name."""
        # Make MockPartElement map to PartUsage (not PartDefinition)
        mock_syside_adapter["MockPartElement"] = "PartUsage"

        from sysml_codegen.extraction.computed_attribute_extractor import (
            extract_computed_attributes,
        )

        expose_expr = MockFeatureChainExpression()
        part = MockPartElement(
            "e2e_plant",
            [
                MockAttributeUsage(
                    "total_capex",
                    expr=expose_expr,
                    qualified_name="E2EDesign::e2e_plant::total_capex",
                ),
                MockCalculationUsage(
                    "component_cost",
                    qualified_name="E2EDesign::e2e_plant::component_cost",
                ),
            ],
            qualified_name="E2EDesign::e2e_plant",
        )

        def mock_extract_feature_refs(expr_node, ignore_std_lib=True):
            if expr_node is expose_expr:
                return _make_refs(
                    ("total_cost", "Library::CostCalc::total_cost"),
                    ("component_cost", "E2EDesign::e2e_plant::component_cost"),
                )
            return []

        monkeypatch.setattr(
            "sysml_codegen.extraction.computed_attribute_extractor.extract_feature_refs",
            mock_extract_feature_refs,
        )

        results, aliases = extract_computed_attributes(
            None, part, calc_usage_names={"component_cost"}
        )

        assert len(aliases) == 1
        alias = aliases[0]
        assert alias.alias_name == "total_capex"  # bare, per C2
        assert alias.canonical_name == "component_cost.total_cost"
        assert alias.owning_part_qn == "E2EDesign::e2e_plant"
        assert alias.source == "expose_pure"

    def test_partdef_expose_pure_filtered(self, mock_syside_adapter, monkeypatch):
        """EXPOSE_PURE on PartDef (is_on_part_definition=True) → no alias produced."""
        # MockPartElement defaults to "PartDefinition" — keep that
        from sysml_codegen.extraction.computed_attribute_extractor import (
            extract_computed_attributes,
        )

        expose_expr = MockFeatureChainExpression()
        part = MockPartElement(
            "Solar_Array",
            [
                MockAttributeUsage(
                    "misc_hardware_cost",
                    expr=expose_expr,
                    qualified_name="Lib::Solar_Array::misc_hardware_cost",
                ),
                MockCalculationUsage(
                    "cost_model",
                    qualified_name="Lib::Solar_Array::cost_model",
                ),
            ],
            qualified_name="Lib::Solar_Array",
        )

        def mock_extract_feature_refs(expr_node, ignore_std_lib=True):
            if expr_node is expose_expr:
                return _make_refs(
                    ("total_cost", "Library::CostCalc::total_cost"),
                    ("cost_model", "Lib::Solar_Array::cost_model"),
                )
            return []

        monkeypatch.setattr(
            "sysml_codegen.extraction.computed_attribute_extractor.extract_feature_refs",
            mock_extract_feature_refs,
        )

        results, aliases = extract_computed_attributes(
            None, part, calc_usage_names={"cost_model"}
        )

        # EXPOSE_PURE still in CAD list (graph builder compat)
        assert len(results) == 1
        assert results[0].classification == ComputedAttributeClassification.EXPOSE_PURE
        # But NO alias produced (PartDef-level filtered)
        assert len(aliases) == 0

    def test_expose_pure_fewer_than_2_refs_skipped(
        self, mock_syside_adapter, monkeypatch, caplog
    ):
        """EXPOSE_PURE with < 2 refs → warning logged, no alias."""
        mock_syside_adapter["MockPartElement"] = "PartUsage"

        from sysml_codegen.extraction.computed_attribute_extractor import (
            extract_computed_attributes,
        )

        expose_expr = MockFeatureChainExpression()
        part = MockPartElement(
            "test_part",
            [
                MockAttributeUsage(
                    "broken_expose",
                    expr=expose_expr,
                    qualified_name="Pkg::test_part::broken_expose",
                ),
                MockCalculationUsage(
                    "some_calc",
                    qualified_name="Pkg::test_part::some_calc",
                ),
            ],
            qualified_name="Pkg::test_part",
        )

        def mock_extract_feature_refs(expr_node, ignore_std_lib=True):
            if expr_node is expose_expr:
                # Only 1 ref (the calc usage instance) — after filtering, 0 semantic refs
                # But we need 2 total refs where one is in calc_usage_names for EXPOSE_PURE
                # Actually, the classification needs: calc_refs present + FeatureChainExpression
                # With only 1 ref that's a calc_usage_name, it gets filtered in step 2a,
                # leaving 0 calc_refs → FORMULA (not EXPOSE_PURE).
                # For EXPOSE_PURE with < 2 refs, we need it to classify as EXPOSE_PURE first.
                # The simplest way: 1 calc_ref (different namespace) + FeatureChainExpression
                return _make_refs(
                    ("result", "Library::Calc::result"),
                )
            return []

        monkeypatch.setattr(
            "sysml_codegen.extraction.computed_attribute_extractor.extract_feature_refs",
            mock_extract_feature_refs,
        )

        with caplog.at_level(logging.WARNING):
            results, aliases = extract_computed_attributes(
                None, part, calc_usage_names={"some_calc"}
            )

        # Should be EXPOSE_PURE (calc_ref present, FeatureChainExpression, no sibling_refs)
        assert len(results) == 1
        assert results[0].classification == ComputedAttributeClassification.EXPOSE_PURE

        # But < 2 refs → no alias, warning logged
        assert len(aliases) == 0
        assert any("fewer than 2 references" in r.message for r in caplog.records)

    def test_expose_pure_stays_in_cad_list(self, mock_syside_adapter, monkeypatch):
        """EXPOSE_PURE still appears in ComputedAttributeData list (graph builder compat)."""
        mock_syside_adapter["MockPartElement"] = "PartUsage"

        from sysml_codegen.extraction.computed_attribute_extractor import (
            extract_computed_attributes,
        )

        expose_expr = MockFeatureChainExpression()
        part = MockPartElement(
            "test_part",
            [
                MockAttributeUsage(
                    "output_val",
                    expr=expose_expr,
                    qualified_name="Pkg::test_part::output_val",
                ),
                MockCalculationUsage(
                    "my_calc",
                    qualified_name="Pkg::test_part::my_calc",
                ),
            ],
            qualified_name="Pkg::test_part",
        )

        def mock_extract_feature_refs(expr_node, ignore_std_lib=True):
            if expr_node is expose_expr:
                return _make_refs(
                    ("result", "Library::MyCalc::result"),
                    ("my_calc", "Pkg::test_part::my_calc"),
                )
            return []

        monkeypatch.setattr(
            "sysml_codegen.extraction.computed_attribute_extractor.extract_feature_refs",
            mock_extract_feature_refs,
        )

        results, aliases = extract_computed_attributes(
            None, part, calc_usage_names={"my_calc"}
        )

        # EXPOSE_PURE in CAD list
        assert len(results) == 1
        assert results[0].classification == ComputedAttributeClassification.EXPOSE_PURE
        assert results[0].python_name == "output_val"

        # AND alias produced
        assert len(aliases) == 1

    def test_expose_pure_canonical_name_uses_refs_not_expression_text(
        self, mock_syside_adapter, monkeypatch
    ):
        """canonical_name is built from refs (instance.output), not expression_text."""
        mock_syside_adapter["MockPartElement"] = "PartUsage"

        from sysml_codegen.extraction.computed_attribute_extractor import (
            extract_computed_attributes,
        )

        expose_expr = MockFeatureChainExpression()
        part = MockPartElement(
            "design_part",
            [
                MockAttributeUsage(
                    "total_cost",
                    expr=expose_expr,
                    qualified_name="Design::design_part::total_cost",
                ),
                MockCalculationUsage(
                    "cost_calc",
                    qualified_name="Design::design_part::cost_calc",
                ),
            ],
            qualified_name="Design::design_part",
        )

        def mock_extract_feature_refs(expr_node, ignore_std_lib=True):
            if expr_node is expose_expr:
                return _make_refs(
                    ("result_total", "Library::CostCalc::result_total"),
                    ("cost_calc", "Design::design_part::cost_calc"),
                )
            return []

        monkeypatch.setattr(
            "sysml_codegen.extraction.computed_attribute_extractor.extract_feature_refs",
            mock_extract_feature_refs,
        )

        results, aliases = extract_computed_attributes(
            None, part, calc_usage_names={"cost_calc"}
        )

        assert len(aliases) == 1
        # canonical_name from refs: "instance_name.output_name"
        assert aliases[0].canonical_name == "cost_calc.result_total"

    def test_formula_does_not_produce_alias(self, mock_syside_adapter, monkeypatch):
        """FORMULA attributes do not produce aliases (only EXPOSE_PURE does)."""
        mock_syside_adapter["MockPartElement"] = "PartUsage"

        from sysml_codegen.extraction.computed_attribute_extractor import (
            extract_computed_attributes,
        )

        formula_expr = MockOperatorExpression("*", [
            MockFeatureReferenceExpression("length"),
            MockFeatureReferenceExpression("width"),
        ])
        part = MockPartElement(
            "test_part",
            [
                MockAttributeUsage(
                    "length",
                    expr=MockLiteralRational(5.0),
                    qualified_name="Pkg::test_part::length",
                ),
                MockAttributeUsage(
                    "width",
                    expr=MockLiteralRational(3.0),
                    qualified_name="Pkg::test_part::width",
                ),
                MockAttributeUsage(
                    "area",
                    expr=formula_expr,
                    qualified_name="Pkg::test_part::area",
                ),
            ],
            qualified_name="Pkg::test_part",
        )

        def mock_extract_feature_refs(expr_node, ignore_std_lib=True):
            if isinstance(expr_node, MockOperatorExpression):
                return _make_refs(
                    ("length", "Pkg::test_part::length"),
                    ("width", "Pkg::test_part::width"),
                )
            return []

        monkeypatch.setattr(
            "sysml_codegen.extraction.computed_attribute_extractor.extract_feature_refs",
            mock_extract_feature_refs,
        )

        results, aliases = extract_computed_attributes(
            None, part, calc_usage_names=set()
        )

        assert len(results) == 1  # area (FORMULA)
        assert len(aliases) == 0  # No aliases from FORMULA


class TestIsOnPartDefinition:
    """Tests for is_on_part_definition field population."""

    def test_partdef_element_sets_true(self, mock_syside_adapter, monkeypatch):
        """PartDef element → is_on_part_definition=True on all extracted attrs."""
        # MockPartElement defaults to "PartDefinition"
        from sysml_codegen.extraction.computed_attribute_extractor import (
            extract_computed_attributes,
        )

        expose_expr = MockFeatureChainExpression()
        part = MockPartElement(
            "MyPartDef",
            [
                MockAttributeUsage(
                    "some_attr",
                    expr=expose_expr,
                    qualified_name="Lib::MyPartDef::some_attr",
                ),
                MockCalculationUsage(
                    "calc_inst",
                    qualified_name="Lib::MyPartDef::calc_inst",
                ),
            ],
            qualified_name="Lib::MyPartDef",
        )

        def mock_extract_feature_refs(expr_node, ignore_std_lib=True):
            if expr_node is expose_expr:
                return _make_refs(
                    ("output", "Library::Calc::output"),
                    ("calc_inst", "Lib::MyPartDef::calc_inst"),
                )
            return []

        monkeypatch.setattr(
            "sysml_codegen.extraction.computed_attribute_extractor.extract_feature_refs",
            mock_extract_feature_refs,
        )

        results, _aliases = extract_computed_attributes(
            None, part, calc_usage_names={"calc_inst"}
        )

        assert len(results) == 1
        assert results[0].is_on_part_definition is True

    def test_partusage_element_sets_false(self, mock_syside_adapter, monkeypatch):
        """PartUsage element → is_on_part_definition=False."""
        mock_syside_adapter["MockPartElement"] = "PartUsage"

        from sysml_codegen.extraction.computed_attribute_extractor import (
            extract_computed_attributes,
        )

        expose_expr = MockFeatureChainExpression()
        part = MockPartElement(
            "my_usage",
            [
                MockAttributeUsage(
                    "some_attr",
                    expr=expose_expr,
                    qualified_name="Pkg::my_usage::some_attr",
                ),
                MockCalculationUsage(
                    "calc_inst",
                    qualified_name="Pkg::my_usage::calc_inst",
                ),
            ],
            qualified_name="Pkg::my_usage",
        )

        def mock_extract_feature_refs(expr_node, ignore_std_lib=True):
            if expr_node is expose_expr:
                return _make_refs(
                    ("output", "Library::Calc::output"),
                    ("calc_inst", "Pkg::my_usage::calc_inst"),
                )
            return []

        monkeypatch.setattr(
            "sysml_codegen.extraction.computed_attribute_extractor.extract_feature_refs",
            mock_extract_feature_refs,
        )

        results, _aliases = extract_computed_attributes(
            None, part, calc_usage_names={"calc_inst"}
        )

        assert len(results) == 1
        assert results[0].is_on_part_definition is False


# ---------------------------------------------------------------------------
# Phase 2: Instance Path Utility + CHAIN Alias Production
# ---------------------------------------------------------------------------


def _make_virtual_calc_usage(
    qn: str = "Design__part__calc",
    owning_part_def_qn: str | None = None,
) -> "CalcUsageData":
    from sysml_codegen.extraction.usage_extractor import CalcUsageData

    return CalcUsageData(
        instance_name=qn,
        calc_def_name="CostModel",
        calc_def_qualified_name="Lib__CostModel",
        module_type="CostModelModule",
        bindings=[],
        qualified_name=qn,
        is_template=False,
        owning_part_def_qn=owning_part_def_qn,
    )


class TestFindInstancePathsForPartdef:
    """Tests for find_instance_paths_for_partdef() utility."""

    def test_direct_match_strategy(self):
        """Virtual CalcUsage on same PartDef → correct dotted path."""
        from sysml_codegen.generation.initialization import find_instance_paths_for_partdef

        usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__cost_model",
                owning_part_def_qn="Lib__Solar_Array",
            ),
        ]
        paths = find_instance_paths_for_partdef(
            "Lib__Solar_Array", usages,
        )
        # "Design__plant__solar_array" → dotted, prefix-stripped: "plant.solar_array"
        assert paths == ["plant.solar_array"]

    def test_child_walk_strategy(self):
        """Child PartUsage name match → correct dotted path."""
        from sysml_codegen.generation.initialization import find_instance_paths_for_partdef

        usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__pv_module__cost_model",
                owning_part_def_qn="Lib__PV_Module",
            ),
        ]
        paths = find_instance_paths_for_partdef(
            "Lib__Solar_Array",
            usages,
            part_usage_names={"Lib__Solar_Array": {"pv_module"}},
        )
        # Child "pv_module" found at segment index 3 → parent is segments[:3]
        # "Design__plant__solar_array" → dotted: "plant.solar_array"
        assert paths == ["plant.solar_array"]

    def test_no_match_returns_empty(self):
        """No matching CalcUsages → empty list."""
        from sysml_codegen.generation.initialization import find_instance_paths_for_partdef

        usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__pv_module__cost_model",
                owning_part_def_qn="Lib__PV_Module",
            ),
        ]
        paths = find_instance_paths_for_partdef(
            "Lib__Wind_Turbine", usages,
        )
        assert paths == []

    def test_deduplicates_paths(self):
        """Multiple CalcUsages producing same parent path → deduplicated."""
        from sysml_codegen.generation.initialization import find_instance_paths_for_partdef

        usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__calc_a",
                owning_part_def_qn="Lib__Solar_Array",
            ),
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__calc_b",
                owning_part_def_qn="Lib__Solar_Array",
            ),
        ]
        paths = find_instance_paths_for_partdef(
            "Lib__Solar_Array", usages,
        )
        assert paths == ["plant.solar_array"]


class TestBuildChainAliases:
    """Tests for _build_chain_aliases() function."""

    def test_chain_redef_with_dot_produces_alias(self):
        """CHAIN redef with '.' in source_path → ChannelAlias with scoped names."""
        from sysml_codegen.extraction.data_models import (
            HierarchyExtractionResult,
            RedefinitionData,
            RedefinitionType,
        )
        from sysml_codegen.generation.initialization import _build_chain_aliases

        redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="total_capex",
            redefinition_type=RedefinitionType.CHAIN,
            source_path="cost_model.total_cost",
            is_deep_path=False,
        )
        hierarchy = HierarchyExtractionResult(
            redefinitions=[redef],
            design_overrides=[],
            multiplicities=[],
            aggregation_expressions=[],
            warnings=[],
            part_usage_names={},
        )
        usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__cost_model",
                owning_part_def_qn="Lib__Solar_Array",
            ),
        ]
        aliases = _build_chain_aliases(hierarchy, usages)

        assert len(aliases) == 1
        alias = aliases[0]
        assert alias.alias_name == "plant.solar_array.total_capex"
        assert alias.canonical_name == "plant.solar_array.cost_model.total_cost"
        assert alias.owning_part_qn == "Lib__Solar_Array"
        assert alias.source == "redefinition"

    def test_bare_cas_code_filtered(self):
        """CHAIN redef with no '.' in source_path (CAS220101) → filtered out."""
        from sysml_codegen.extraction.data_models import (
            HierarchyExtractionResult,
            RedefinitionData,
            RedefinitionType,
        )
        from sysml_codegen.generation.initialization import _build_chain_aliases

        redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="cas_code",
            redefinition_type=RedefinitionType.CHAIN,
            source_path="CAS220101",  # bare CAS code, no dot
            is_deep_path=False,
        )
        hierarchy = HierarchyExtractionResult(
            redefinitions=[redef],
            design_overrides=[],
            multiplicities=[],
            aggregation_expressions=[],
            warnings=[],
        )
        usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__cost_model",
                owning_part_def_qn="Lib__Solar_Array",
            ),
        ]
        aliases = _build_chain_aliases(hierarchy, usages)
        assert len(aliases) == 0

    def test_deep_path_redef_filtered(self):
        """CHAIN redef with is_deep_path=True → filtered (design overrides, not aliases)."""
        from sysml_codegen.extraction.data_models import (
            HierarchyExtractionResult,
            RedefinitionData,
            RedefinitionType,
        )
        from sysml_codegen.generation.initialization import _build_chain_aliases

        redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="wattage",
            redefinition_type=RedefinitionType.CHAIN,
            source_path="pv_module.wattage",
            is_deep_path=True,
            target_path=["pv_module", "wattage"],
        )
        hierarchy = HierarchyExtractionResult(
            redefinitions=[redef],
            design_overrides=[],
            multiplicities=[],
            aggregation_expressions=[],
            warnings=[],
        )
        usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__cost_model",
                owning_part_def_qn="Lib__Solar_Array",
            ),
        ]
        aliases = _build_chain_aliases(hierarchy, usages)
        assert len(aliases) == 0

    def test_multiple_instance_paths_produce_multiple_aliases(self):
        """CHAIN redef with multiple instance paths → one alias per path."""
        from sysml_codegen.extraction.data_models import (
            HierarchyExtractionResult,
            RedefinitionData,
            RedefinitionType,
        )
        from sysml_codegen.generation.initialization import _build_chain_aliases

        redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="total_capex",
            redefinition_type=RedefinitionType.CHAIN,
            source_path="cost_model.total_cost",
            is_deep_path=False,
        )
        hierarchy = HierarchyExtractionResult(
            redefinitions=[redef],
            design_overrides=[],
            multiplicities=[],
            aggregation_expressions=[],
            warnings=[],
        )
        usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__array_1__cost_model",
                owning_part_def_qn="Lib__Solar_Array",
            ),
            _make_virtual_calc_usage(
                qn="Design__plant__array_2__cost_model",
                owning_part_def_qn="Lib__Solar_Array",
            ),
        ]
        aliases = _build_chain_aliases(hierarchy, usages)

        assert len(aliases) == 2
        alias_names = sorted(a.alias_name for a in aliases)
        assert alias_names == [
            "plant.array_1.total_capex",
            "plant.array_2.total_capex",
        ]

    def test_only_chain_redefs_processed(self):
        """LITERAL and EXPRESSION redefs are ignored — only CHAIN produces aliases."""
        from sysml_codegen.extraction.data_models import (
            HierarchyExtractionResult,
            RedefinitionData,
            RedefinitionType,
        )
        from sysml_codegen.generation.initialization import _build_chain_aliases

        literal_redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="wattage",
            redefinition_type=RedefinitionType.LITERAL,
            literal_value=400.0,
        )
        expression_redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="total",
            redefinition_type=RedefinitionType.EXPRESSION,
            expression_text="sum(pv_module.cost)",
        )
        hierarchy = HierarchyExtractionResult(
            redefinitions=[literal_redef, expression_redef],
            design_overrides=[],
            multiplicities=[],
            aggregation_expressions=[],
            warnings=[],
        )
        usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__cost_model",
                owning_part_def_qn="Lib__Solar_Array",
            ),
        ]
        aliases = _build_chain_aliases(hierarchy, usages)
        assert len(aliases) == 0
