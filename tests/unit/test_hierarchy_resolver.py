"""Unit tests for hierarchy resolver: redefinition extraction, multiplicity, aggregation.

Tests use mock AST elements — no real SysML models required. Mock class names
include the SysML type name so SysideAdapter.is_instance() fallback works
(type_name in type(elem).__name__).

Test Suites:
Phase 1:
  - Data model construction (RedefinitionData, MultiplicityData, AggregationExpressionData)
  - reconstruct_expression() InvocationExpression handling
Phase 2:
  - Redefinition scanning (6 tests)
  - Deep-path resolution (5 tests)
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    HierarchyExtractionResult,
    LocalTerm,
    MultiplicityData,
    RedefinitionData,
    RedefinitionType,
    SingletonTerm,
    SumTerm,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.expression_utils import reconstruct_expression
from sysml_codegen.extraction.hierarchy_resolver import (
    build_aggregation_expression,
    extract_design_overrides,
    extract_hierarchy_data,
    extract_multiplicities,
    extract_redefinitions,
)


# ---------------------------------------------------------------------------
# Mock AST Elements for expression_utils InvocationExpression tests
# ---------------------------------------------------------------------------


class MockFeatureReferenceExpression:
    """Mock FeatureReferenceExpression — is_instance fallback matches."""

    def __init__(self, name: str):
        self.referent = type("Referent", (), {"name": name})()


class MockFeatureChainExpression:
    """Mock FeatureChainExpression — is_instance fallback matches."""

    def __init__(self, parts: list[str]):
        self.operands = [MockFeatureReferenceExpression(parts[0])] if parts else []
        self.target_feature = type("Target", (), {"name": parts[-1]})() if len(parts) > 1 else None
        self.memberships = []


class MockInvocationExpression:
    """Mock InvocationExpression with function.name and operands."""

    def __init__(self, func_name: str, operands: list):
        self.function = type("Function", (), {"name": func_name})()
        self.operands = operands


class MockOperatorExpression:
    """Mock OperatorExpression — is_instance fallback matches."""

    def __init__(self, operator: str, operands: list):
        self.operator = operator
        self.operands = operands


# ---------------------------------------------------------------------------
# Phase 1 — Test Suite: Data Model Construction
# ---------------------------------------------------------------------------


class TestRedefinitionDataConstruction:
    """Test RedefinitionData dataclass construction and field defaults."""

    def test_literal_construction(self):
        """RedefinitionData with LITERAL type has correct fields."""
        rd = RedefinitionData(
            owning_part_qn="Lib__PV_Module",
            attribute_name="wattage",
            redefinition_type=RedefinitionType.LITERAL,
            literal_value=400.0,
        )
        assert rd.redefinition_type == RedefinitionType.LITERAL
        assert rd.literal_value == 400.0
        assert rd.is_deep_path is False
        assert rd.target_path == []
        assert rd.source_path is None
        assert rd.expression_ast is None

    def test_chain_construction(self):
        """RedefinitionData with CHAIN type has source_path."""
        rd = RedefinitionData(
            owning_part_qn="Lib__PV_Module",
            attribute_name="capital_cost",
            redefinition_type=RedefinitionType.CHAIN,
            source_path="cost_model.total_cost",
        )
        assert rd.redefinition_type == RedefinitionType.CHAIN
        assert rd.source_path == "cost_model.total_cost"
        assert rd.literal_value is None

    def test_expression_construction(self):
        """RedefinitionData with EXPRESSION type has AST and text."""
        rd = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="capital_cost",
            redefinition_type=RedefinitionType.EXPRESSION,
            expression_ast="<mock_ast>",
            expression_text="sum(pv_module.capital_cost) + misc",
        )
        assert rd.redefinition_type == RedefinitionType.EXPRESSION
        assert rd.expression_ast == "<mock_ast>"
        assert rd.expression_text == "sum(pv_module.capital_cost) + misc"

    def test_deep_path_construction(self):
        """RedefinitionData with deep-path fields set."""
        rd = RedefinitionData(
            owning_part_qn="Design__solar_array",
            attribute_name="wattage",
            redefinition_type=RedefinitionType.LITERAL,
            literal_value=400.0,
            target_path=["pv_module", "wattage"],
            is_deep_path=True,
        )
        assert rd.is_deep_path is True
        assert rd.target_path == ["pv_module", "wattage"]

    def test_redefinition_type_values(self):
        """RedefinitionType enum has exactly 3 values with correct strings."""
        assert RedefinitionType.LITERAL == "literal"
        assert RedefinitionType.CHAIN == "chain"
        assert RedefinitionType.EXPRESSION == "expression"
        assert len(RedefinitionType) == 3


class TestMultiplicityDataConstruction:
    """Test MultiplicityData dataclass construction."""

    def test_basic_construction(self):
        """MultiplicityData with all fields."""
        md = MultiplicityData(
            part_usage_name="pv_module",
            owning_part_def_qn="Lib__Solar_Array",
            count=20,
            count_attribute_name="module_count",
            default_value=20,
        )
        assert md.part_usage_name == "pv_module"
        assert md.owning_part_def_qn == "Lib__Solar_Array"
        assert md.count == 20
        assert md.count_attribute_name == "module_count"
        assert md.default_value == 20

    def test_none_count(self):
        """MultiplicityData with unresolvable count."""
        md = MultiplicityData(
            part_usage_name="pv_module",
            owning_part_def_qn="Lib__Solar_Array",
            count=None,
            count_attribute_name=None,
            default_value=None,
        )
        assert md.count is None
        assert md.count_attribute_name is None


class TestAggregationExpressionDataConstruction:
    """Test AggregationExpressionData and term dataclasses."""

    def test_sum_term_construction(self):
        """SumTerm has correct fields."""
        st = SumTerm(
            part_usage_name="pv_module",
            attribute_name="capital_cost",
            multiplicity_attr="module_count",
            multiplicity_count=20,
        )
        assert st.part_usage_name == "pv_module"
        assert st.attribute_name == "capital_cost"
        assert st.multiplicity_attr == "module_count"
        assert st.multiplicity_count == 20

    def test_singleton_term_construction(self):
        """SingletonTerm has source_path."""
        st = SingletonTerm(source_path="allocation_model.total_allocation")
        assert st.source_path == "allocation_model.total_allocation"

    def test_local_term_construction(self):
        """LocalTerm has attribute_name."""
        lt = LocalTerm(attribute_name="misc_hardware_cost")
        assert lt.attribute_name == "misc_hardware_cost"

    def test_full_aggregation_construction(self):
        """AggregationExpressionData with all term types."""
        aed = AggregationExpressionData(
            owning_part_qn="Lib__Solar_Array",
            owning_part_name="Solar_Array",
            attribute_name="capital_cost",
            raw_expression_text="sum(pv_module.capital_cost) + sum(inverter.capital_cost) + allocation_model.total_allocation + misc_hardware_cost",
            transformed_expression="(((module_count * pv_module.capital_cost) + (inverter_count * inverter.capital_cost)) + allocation_model.total_allocation) + misc_hardware_cost",
            sum_terms=[
                SumTerm("pv_module", "capital_cost", "module_count", 20),
                SumTerm("inverter", "capital_cost", "inverter_count", 4),
            ],
            singleton_terms=[
                SingletonTerm("allocation_model.total_allocation"),
            ],
            local_terms=[
                LocalTerm("misc_hardware_cost"),
            ],
            input_channels=["pv_module.capital_cost", "inverter.capital_cost", "allocation_model.total_allocation"],
            entry_points=["module_count", "inverter_count"],
        )
        assert aed.owning_part_qn == "Lib__Solar_Array"
        assert len(aed.sum_terms) == 2
        assert len(aed.singleton_terms) == 1
        assert len(aed.local_terms) == 1
        assert aed.compilability == Compilability.UNKNOWN
        assert aed.has_unsupported_nodes is False
        assert len(aed.entry_points) == 2

    def test_hierarchy_extraction_result_construction(self):
        """HierarchyExtractionResult bundles all data."""
        result = HierarchyExtractionResult(
            redefinitions=[],
            design_overrides=[],
            multiplicities=[],
            aggregation_expressions=[],
            warnings=["test warning"],
        )
        assert result.redefinitions == []
        assert result.warnings == ["test warning"]


# ---------------------------------------------------------------------------
# Phase 1 — Test Suite: reconstruct_expression InvocationExpression
# ---------------------------------------------------------------------------


class TestReconstructExpressionInvocation:
    """Test that reconstruct_expression handles InvocationExpression."""

    def test_sum_with_chain_operand(self):
        """reconstruct_expression handles sum(pv_module.capital_cost)."""
        chain = MockFeatureChainExpression(["pv_module", "capital_cost"])
        invoc = MockInvocationExpression("sum", [chain])
        result = reconstruct_expression(invoc)
        assert "sum(" in result
        assert ")" in result

    def test_sum_with_reference_operand(self):
        """reconstruct_expression handles sum(some_attr)."""
        ref = MockFeatureReferenceExpression("some_attr")
        invoc = MockInvocationExpression("sum", [ref])
        result = reconstruct_expression(invoc)
        assert "sum(" in result
        assert "some_attr" in result

    def test_invocation_in_operator_expression(self):
        """reconstruct_expression handles sum() inside an operator expression."""
        chain = MockFeatureChainExpression(["pv_module", "capital_cost"])
        invoc = MockInvocationExpression("sum", [chain])
        ref = MockFeatureReferenceExpression("misc_cost")
        op = MockOperatorExpression("+", [invoc, ref])
        result = reconstruct_expression(op)
        assert "sum(" in result
        assert "+" in result
        assert "misc_cost" in result

    def test_non_sum_invocation(self):
        """reconstruct_expression handles non-sum invocations like sqrt()."""
        ref = MockFeatureReferenceExpression("value")
        invoc = MockInvocationExpression("sqrt", [ref])
        result = reconstruct_expression(invoc)
        assert "sqrt(" in result
        assert "value" in result

    def test_zero_arg_invocation(self):
        """reconstruct_expression handles zero-argument invocation."""
        invoc = MockInvocationExpression("now", [])
        result = reconstruct_expression(invoc)
        assert result == "now()"


# ---------------------------------------------------------------------------
# Phase 2 — Mock Helpers for Redefinition Scanning & Deep-Path Resolution
# ---------------------------------------------------------------------------


class MockLiteralInteger:
    """Mock LiteralInteger — is_instance fallback matches."""

    def __init__(self, value: int):
        self.value = value


class MockLiteralReal:
    """Mock LiteralReal — is_instance fallback matches."""

    def __init__(self, value: float):
        self.value = value


class MockRedefinition:
    """Mock Redefinition object with a redefined_feature."""

    def __init__(self, redefined_feature):
        self.redefined_feature = redefined_feature


class MockRedefinedFeature:
    """Mock redefined feature with name and optional chaining_features."""

    def __init__(self, name: str | None = None, chaining_features=None):
        self.name = name
        self.chaining_features = chaining_features or []


class MockChainingFeature:
    """Mock chaining feature element (PartUsage or AttributeUsage) with a name."""

    def __init__(self, name: str):
        self.name = name


class MockReferenceUsage:
    """Mock ReferenceUsage — is_instance fallback matches 'ReferenceUsage'.

    Simulates a :>> redefinition member on a PartDef.
    """

    def __init__(
        self,
        name: str | None = None,
        owned_redefinitions=None,
        feature_value_expression=None,
    ):
        self.name = name
        self.owned_redefinitions = owned_redefinitions or []
        self.feature_value_expression = feature_value_expression


class MockAttributeUsage:
    """Mock AttributeUsage — is_instance fallback matches 'AttributeUsage'."""

    def __init__(self, name: str = "some_attr"):
        self.name = name
        self.owned_redefinitions = []


class MockPartDefinitionForRedef:
    """Mock PartDefinition with owned_members for redefinition scanning.

    Class name contains 'PartDefinition' for is_instance fallback.
    """

    def __init__(self, name: str, owned_members=None, owner=None):
        self.name = name
        self.owned_members = owned_members or []
        self.owner = owner


class MockPartUsageForDesign:
    """Mock PartUsage for design-level overrides.

    Has owned_redefinitions (marking it as 'part redefines')
    and owned_members containing :>> ReferenceUsage members.
    Class name contains 'PartUsage' for is_instance fallback.
    """

    def __init__(
        self,
        name: str,
        owned_redefinitions=None,
        owned_members=None,
        owner=None,
    ):
        self.name = name
        self.owned_redefinitions = owned_redefinitions or []
        self.owned_members = owned_members or []
        self.owner = owner


class MockOwnership:
    """Mock ownership for QN building."""

    def __init__(self, owning_related_element=None, owner=None, name=None):
        self.owning_related_element = owning_related_element
        self.owner = owner
        self.name = name


def _make_literal_redef_member(
    attr_name: str,
    value: float | int,
    member_name: str | None = None,
) -> MockReferenceUsage:
    """Build a ReferenceUsage mock for :>> attr_name = <literal>."""
    redefined = MockRedefinedFeature(name=attr_name)
    redef = MockRedefinition(redefined_feature=redefined)
    if isinstance(value, float):
        expr = MockLiteralReal(value)
    else:
        expr = MockLiteralInteger(value)
    return MockReferenceUsage(
        name=member_name or attr_name,
        owned_redefinitions=[redef],
        feature_value_expression=expr,
    )


def _make_chain_redef_member(
    attr_name: str,
    chain_parts: list[str],
) -> MockReferenceUsage:
    """Build a ReferenceUsage mock for :>> attr_name = part.attr (chain)."""
    redefined = MockRedefinedFeature(name=attr_name)
    redef = MockRedefinition(redefined_feature=redefined)
    expr = MockFeatureChainExpression(chain_parts)
    return MockReferenceUsage(
        name=attr_name,
        owned_redefinitions=[redef],
        feature_value_expression=expr,
    )


def _make_expression_redef_member(
    attr_name: str,
    operator: str = "+",
    operands: list | None = None,
) -> MockReferenceUsage:
    """Build a ReferenceUsage mock for :>> attr_name = <expression>."""
    redefined = MockRedefinedFeature(name=attr_name)
    redef = MockRedefinition(redefined_feature=redefined)
    if operands is None:
        operands = [
            MockInvocationExpression("sum", [MockFeatureChainExpression(["pv_module", "capital_cost"])]),
            MockFeatureReferenceExpression("misc_cost"),
        ]
    expr = MockOperatorExpression(operator, operands)
    return MockReferenceUsage(
        name=attr_name,
        owned_redefinitions=[redef],
        feature_value_expression=expr,
    )


def _make_deep_path_redef_member(
    path: list[str],
    value: float,
) -> MockReferenceUsage:
    """Build a ReferenceUsage mock for deep-path :>> pv_module.wattage = 400.0."""
    chaining = [MockChainingFeature(name=p) for p in path]
    redefined = MockRedefinedFeature(name=None, chaining_features=chaining)
    redef = MockRedefinition(redefined_feature=redefined)
    expr = MockLiteralReal(value)
    return MockReferenceUsage(
        name=None,  # deep-path overrides have name=None
        owned_redefinitions=[redef],
        feature_value_expression=expr,
    )


# ---------------------------------------------------------------------------
# Phase 2 — Test Suite 1: Redefinition Scanning
# ---------------------------------------------------------------------------


class TestRedefinitionScanning:
    """Test extract_redefinitions() — LITERAL, CHAIN, EXPRESSION classification."""

    def test_literal_redefinition(self):
        """:>> wattage = 400.0 extracts as LITERAL with value."""
        member = _make_literal_redef_member("wattage", 400.0)
        part = MockPartDefinitionForRedef("PV_Module", owned_members=[member])
        result = extract_redefinitions(part)
        assert len(result) == 1
        assert result[0].redefinition_type == RedefinitionType.LITERAL
        assert result[0].literal_value == 400.0
        assert result[0].attribute_name == "wattage"

    def test_chain_redefinition(self):
        """:>> capital_cost = cost_model.total_cost extracts as CHAIN."""
        member = _make_chain_redef_member("capital_cost", ["cost_model", "total_cost"])
        part = MockPartDefinitionForRedef("PV_Module", owned_members=[member])
        result = extract_redefinitions(part)
        assert len(result) == 1
        assert result[0].redefinition_type == RedefinitionType.CHAIN
        assert result[0].source_path == "cost_model.total_cost"

    def test_expression_redefinition(self):
        """:>> capital_cost = sum(...) + ... extracts as EXPRESSION with AST."""
        member = _make_expression_redef_member("capital_cost")
        part = MockPartDefinitionForRedef("Solar_Array", owned_members=[member])
        result = extract_redefinitions(part)
        assert len(result) == 1
        assert result[0].redefinition_type == RedefinitionType.EXPRESSION
        assert result[0].expression_ast is not None
        assert "sum(" in result[0].expression_text

    def test_skip_no_value_expression(self):
        """:>> with no RHS value expression is skipped."""
        redefined = MockRedefinedFeature(name="some_type")
        redef = MockRedefinition(redefined_feature=redefined)
        member = MockReferenceUsage(
            name="some_type",
            owned_redefinitions=[redef],
            feature_value_expression=None,
        )
        part = MockPartDefinitionForRedef("SomePart", owned_members=[member])
        result = extract_redefinitions(part)
        assert len(result) == 0

    def test_skip_attribute_usage(self):
        """AttributeUsage members are not processed (only ReferenceUsage)."""
        attr = MockAttributeUsage("some_attr")
        member = _make_literal_redef_member("wattage", 400.0)
        part = MockPartDefinitionForRedef("PV_Module", owned_members=[attr, member])
        result = extract_redefinitions(part)
        assert len(result) == 1  # Only the ReferenceUsage, not the AttributeUsage

    def test_multiple_redefs_per_part(self):
        """3 :>> on one PartDef produces 3 RedefinitionData."""
        members = [
            _make_literal_redef_member("wattage", 400.0),
            _make_chain_redef_member("capital_cost", ["cost_model", "total_cost"]),
            _make_literal_redef_member("efficiency", 0.21),
        ]
        part = MockPartDefinitionForRedef("PV_Module", owned_members=members)
        result = extract_redefinitions(part)
        assert len(result) == 3
        types = {r.redefinition_type for r in result}
        assert RedefinitionType.LITERAL in types
        assert RedefinitionType.CHAIN in types


# ---------------------------------------------------------------------------
# Phase 2 — Test Suite 2: Deep-Path Resolution
# ---------------------------------------------------------------------------


class TestDeepPathResolution:
    """Test extract_design_overrides() — deep-path :>> resolution."""

    def test_deep_path_extracts_chaining_features(self):
        """chaining_features [PartUsage 'pv_module', AttributeUsage 'wattage'] → target_path."""
        member = _make_deep_path_redef_member(["pv_module", "wattage"], 400.0)
        usage = MockPartUsageForDesign(
            name="solar_array",
            owned_redefinitions=[MockRedefinition(MockRedefinedFeature(name="solar_array"))],
            owned_members=[member],
        )
        result = extract_design_overrides([usage])
        assert len(result) == 1
        assert result[0].target_path == ["pv_module", "wattage"]

    def test_deep_path_literal_value(self):
        """:>> pv_module.wattage = 400.0 extracts as LITERAL with value and path."""
        member = _make_deep_path_redef_member(["pv_module", "wattage"], 400.0)
        usage = MockPartUsageForDesign(
            name="solar_array",
            owned_redefinitions=[MockRedefinition(MockRedefinedFeature(name="solar_array"))],
            owned_members=[member],
        )
        result = extract_design_overrides([usage])
        assert result[0].redefinition_type == RedefinitionType.LITERAL
        assert result[0].literal_value == 400.0

    def test_deep_path_is_deep_path_flag(self):
        """is_deep_path=True when chaining_features non-empty."""
        member = _make_deep_path_redef_member(["pv_module", "wattage"], 400.0)
        usage = MockPartUsageForDesign(
            name="solar_array",
            owned_redefinitions=[MockRedefinition(MockRedefinedFeature(name="solar_array"))],
            owned_members=[member],
        )
        result = extract_design_overrides([usage])
        assert result[0].is_deep_path is True

    def test_same_level_redef_not_deep_path(self):
        """Named :>> on design part usage → is_deep_path=False."""
        member = _make_literal_redef_member("efficiency", 0.95)
        usage = MockPartUsageForDesign(
            name="solar_array",
            owned_redefinitions=[MockRedefinition(MockRedefinedFeature(name="solar_array"))],
            owned_members=[member],
        )
        result = extract_design_overrides([usage])
        assert len(result) == 1
        assert result[0].is_deep_path is False
        assert result[0].attribute_name == "efficiency"

    def test_design_overrides_multiple(self):
        """5 deep-path overrides on mock design solar_array → 5 RedefinitionData."""
        members = [
            _make_deep_path_redef_member(["pv_module", "wattage"], 400.0),
            _make_deep_path_redef_member(["pv_module", "efficiency"], 0.21),
            _make_deep_path_redef_member(["pv_module", "power_rating"], 350.0),
            _make_deep_path_redef_member(["inverter", "string_count"], 10),
            _make_deep_path_redef_member(["inverter", "panel_count"], 20),
        ]
        usage = MockPartUsageForDesign(
            name="solar_array",
            owned_redefinitions=[MockRedefinition(MockRedefinedFeature(name="solar_array"))],
            owned_members=members,
        )
        result = extract_design_overrides([usage])
        assert len(result) == 5
        assert all(r.is_deep_path for r in result)


# ---------------------------------------------------------------------------
# Phase 3 — Mock Helpers for Multiplicity Extraction
# ---------------------------------------------------------------------------


class MockMultiplicityReferent:
    """Mock referent for a multiplicity attribute reference."""

    def __init__(self, name: str, default_value: int | None = None):
        self.name = name
        if default_value is not None:
            self.feature_value_expression = type(
                "FVE", (), {"value": default_value}
            )()
        else:
            self.feature_value_expression = None


class MockUpperBound:
    """Mock upper_bound with a referent."""

    def __init__(self, referent: MockMultiplicityReferent):
        self.referent = referent


class MockMultiplicityRange:
    """Mock MultiplicityRange with cached_lower_bound and upper_bound."""

    def __init__(
        self,
        cached_lower_bound: int | float | None = None,
        cached_upper_bound: int | float | None = None,
        upper_bound: MockUpperBound | None = None,
    ):
        self.cached_lower_bound = cached_lower_bound
        self.cached_upper_bound = cached_upper_bound
        self.upper_bound = upper_bound


class MockPartUsageForMultiplicity:
    """Mock PartUsage with optional multiplicity.

    Class name contains 'PartUsage' for is_instance fallback.
    """

    def __init__(
        self,
        name: str,
        multiplicity: MockMultiplicityRange | None = None,
    ):
        self.name = name
        self.multiplicity = multiplicity


# ---------------------------------------------------------------------------
# Phase 3 — Test Suite 3: Multiplicity Extraction
# ---------------------------------------------------------------------------


class TestMultiplicityExtraction:
    """Test extract_multiplicities() — cached_lower_bound, attribute refs, defaults."""

    def test_multiplicity_with_attribute_ref(self):
        """[module_count] with default 20 extracts correctly."""
        referent = MockMultiplicityReferent("module_count", default_value=20)
        upper = MockUpperBound(referent)
        mult = MockMultiplicityRange(
            cached_lower_bound=20, cached_upper_bound=21, upper_bound=upper
        )
        usage = MockPartUsageForMultiplicity("pv_module", multiplicity=mult)
        part = MockPartDefinitionForRedef("Solar_Array", owned_members=[usage])
        result = extract_multiplicities(part)
        assert len(result) == 1
        assert result[0].count == 20
        assert result[0].count_attribute_name == "module_count"
        assert result[0].part_usage_name == "pv_module"

    def test_singleton_no_multiplicity(self):
        """PartUsage without multiplicity is not in results."""
        usage = MockPartUsageForMultiplicity("allocation_model", multiplicity=None)
        part = MockPartDefinitionForRedef("Solar_Array", owned_members=[usage])
        result = extract_multiplicities(part)
        assert len(result) == 0

    def test_multiplicity_uses_cached_lower_bound(self):
        """Verify cached_lower_bound used (20), NOT cached_upper_bound (21)."""
        referent = MockMultiplicityReferent("module_count", default_value=20)
        upper = MockUpperBound(referent)
        mult = MockMultiplicityRange(
            cached_lower_bound=20.0,  # Float — defensive int() cast expected
            cached_upper_bound=21,
            upper_bound=upper,
        )
        usage = MockPartUsageForMultiplicity("pv_module", multiplicity=mult)
        part = MockPartDefinitionForRedef("Solar_Array", owned_members=[usage])
        result = extract_multiplicities(part)
        assert result[0].count == 20  # cached_lower_bound, not 21
        assert isinstance(result[0].count, int)  # Defensive int() cast

    def test_multiplicity_extracts_default_value(self):
        """pack_count default := 8 → default_value=8."""
        referent = MockMultiplicityReferent("pack_count", default_value=8)
        upper = MockUpperBound(referent)
        mult = MockMultiplicityRange(
            cached_lower_bound=8, upper_bound=upper
        )
        usage = MockPartUsageForMultiplicity("battery_pack", multiplicity=mult)
        part = MockPartDefinitionForRedef("Battery_System", owned_members=[usage])
        result = extract_multiplicities(part)
        assert result[0].default_value == 8
        assert result[0].count_attribute_name == "pack_count"


# ---------------------------------------------------------------------------
# Phase 4 — Mock Helpers for Aggregation Expression Transformation
# ---------------------------------------------------------------------------


def _make_sum_invocation(part_name: str, attr_name: str) -> MockInvocationExpression:
    """Build a mock sum(part.attr) InvocationExpression."""
    chain = MockFeatureChainExpression([part_name, attr_name])
    return MockInvocationExpression("sum", [chain])


def _make_solar_array_expression_ast() -> MockOperatorExpression:
    """Build the full Solar Array capital_cost expression AST.

    Structure:
        OperatorExpression(+)
        +-- OperatorExpression(+)
        |   +-- OperatorExpression(+)
        |   |   +-- InvocationExpression(sum) <- pv_module.capital_cost
        |   |   +-- InvocationExpression(sum) <- inverter.capital_cost
        |   +-- FeatureChainExpression <- allocation_model.total_allocation
        +-- FeatureReferenceExpression <- misc_hardware_cost
    """
    sum1 = _make_sum_invocation("pv_module", "capital_cost")
    sum2 = _make_sum_invocation("inverter", "capital_cost")
    alloc = MockFeatureChainExpression(["allocation_model", "total_allocation"])
    misc = MockFeatureReferenceExpression("misc_hardware_cost")
    inner = MockOperatorExpression("+", [sum1, sum2])
    mid = MockOperatorExpression("+", [inner, alloc])
    return MockOperatorExpression("+", [mid, misc])


def _make_solar_array_redef() -> RedefinitionData:
    """Build a RedefinitionData for Solar Array capital_cost EXPRESSION."""
    ast = _make_solar_array_expression_ast()
    return RedefinitionData(
        owning_part_qn="Lib__Solar_Array",
        attribute_name="capital_cost",
        redefinition_type=RedefinitionType.EXPRESSION,
        expression_ast=ast,
        expression_text="sum(pv_module.capital_cost) + sum(inverter.capital_cost) + allocation_model.total_allocation + misc_hardware_cost",
    )


def _make_solar_array_multiplicities() -> list[MultiplicityData]:
    """Build multiplicities for pv_module and inverter."""
    return [
        MultiplicityData("pv_module", "Lib__Solar_Array", 20, "module_count", 20),
        MultiplicityData("inverter", "Lib__Solar_Array", 4, "inverter_count", 4),
    ]


def _make_solar_array_part() -> MockPartDefinitionForRedef:
    """Build a mock Solar_Array PartDef with child PartUsages."""
    return MockPartDefinitionForRedef(
        "Solar_Array",
        owned_members=[
            MockPartUsageForMultiplicity("pv_module"),
            MockPartUsageForMultiplicity("inverter"),
            MockPartUsageForMultiplicity("allocation_model"),
        ],
    )


# ---------------------------------------------------------------------------
# Phase 4 — Test Suite 4: Sum Transformation
# ---------------------------------------------------------------------------


class TestSumTransformation:
    """Test build_aggregation_expression for sum() handling."""

    def test_sum_detected(self):
        """InvocationExpression with function.name='sum' produces SumTerm."""
        sum_expr = _make_sum_invocation("pv_module", "capital_cost")
        redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="cost",
            redefinition_type=RedefinitionType.EXPRESSION,
            expression_ast=sum_expr,
            expression_text="sum(pv_module.capital_cost)",
        )
        mults = [MultiplicityData("pv_module", "Lib__Solar_Array", 20, "module_count", 20)]
        part = MockPartDefinitionForRedef(
            "Solar_Array", owned_members=[MockPartUsageForMultiplicity("pv_module")]
        )
        result = build_aggregation_expression(redef, mults, part)
        assert result is not None
        assert len(result.sum_terms) == 1
        assert result.sum_terms[0].part_usage_name == "pv_module"
        assert result.sum_terms[0].attribute_name == "capital_cost"

    def test_sum_parametric_multiply(self):
        """sum(pv_module.capital_cost) -> module_count * pv_module.capital_cost."""
        sum_expr = _make_sum_invocation("pv_module", "capital_cost")
        redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="cost",
            redefinition_type=RedefinitionType.EXPRESSION,
            expression_ast=sum_expr,
            expression_text="sum(pv_module.capital_cost)",
        )
        mults = [MultiplicityData("pv_module", "Lib__Solar_Array", 20, "module_count", 20)]
        part = MockPartDefinitionForRedef(
            "Solar_Array", owned_members=[MockPartUsageForMultiplicity("pv_module")]
        )
        result = build_aggregation_expression(redef, mults, part)
        assert result is not None
        assert "module_count * pv_module.capital_cost" in result.transformed_expression
        assert result.sum_terms[0].multiplicity_attr == "module_count"
        assert result.sum_terms[0].multiplicity_count == 20

    def test_singleton_term(self):
        """FeatureChainExpression (non-sum) -> SingletonTerm."""
        chain = MockFeatureChainExpression(["allocation_model", "total_allocation"])
        redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="cost",
            redefinition_type=RedefinitionType.EXPRESSION,
            expression_ast=chain,
            expression_text="allocation_model.total_allocation",
        )
        part = MockPartDefinitionForRedef(
            "Solar_Array", owned_members=[MockPartUsageForMultiplicity("allocation_model")]
        )
        result = build_aggregation_expression(redef, [], part)
        assert result is not None
        assert len(result.singleton_terms) == 1
        assert result.singleton_terms[0].source_path == "allocation_model.total_allocation"

    def test_local_term(self):
        """FeatureReferenceExpression (sibling attr) -> LocalTerm."""
        ref = MockFeatureReferenceExpression("misc_hardware_cost")
        redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="cost",
            redefinition_type=RedefinitionType.EXPRESSION,
            expression_ast=ref,
            expression_text="misc_hardware_cost",
        )
        part = MockPartDefinitionForRedef("Solar_Array", owned_members=[])
        result = build_aggregation_expression(redef, [], part)
        assert result is not None
        assert len(result.local_terms) == 1
        assert result.local_terms[0].attribute_name == "misc_hardware_cost"

    def test_mixed_expression(self):
        """Full solar_array.capital_cost -> 2 SumTerms + 1 SingletonTerm + 1 LocalTerm."""
        redef = _make_solar_array_redef()
        mults = _make_solar_array_multiplicities()
        part = _make_solar_array_part()
        result = build_aggregation_expression(redef, mults, part)
        assert result is not None
        assert len(result.sum_terms) == 2
        assert len(result.singleton_terms) == 1
        assert len(result.local_terms) == 1


# ---------------------------------------------------------------------------
# Phase 4 — Test Suite 5: AggregationExpressionData Properties
# ---------------------------------------------------------------------------


class TestAggregationExpressionProperties:
    """Test AggregationExpressionData properties from build_aggregation_expression."""

    def test_aggregation_has_correct_terms(self):
        """Verify term details for full Solar Array expression."""
        redef = _make_solar_array_redef()
        mults = _make_solar_array_multiplicities()
        part = _make_solar_array_part()
        result = build_aggregation_expression(redef, mults, part)
        assert result is not None
        assert result.sum_terms[0].part_usage_name == "pv_module"
        assert result.sum_terms[1].part_usage_name == "inverter"
        assert result.singleton_terms[0].source_path == "allocation_model.total_allocation"
        assert result.local_terms[0].attribute_name == "misc_hardware_cost"

    def test_aggregation_input_channels(self):
        """All child references collected in input_channels."""
        redef = _make_solar_array_redef()
        mults = _make_solar_array_multiplicities()
        part = _make_solar_array_part()
        result = build_aggregation_expression(redef, mults, part)
        assert result is not None
        assert "pv_module.capital_cost" in result.input_channels
        assert "inverter.capital_cost" in result.input_channels
        assert "allocation_model.total_allocation" in result.input_channels
        # Local terms should NOT be in input_channels
        assert "misc_hardware_cost" not in result.input_channels

    def test_aggregation_entry_points(self):
        """Multiplicity attrs collected in entry_points."""
        redef = _make_solar_array_redef()
        mults = _make_solar_array_multiplicities()
        part = _make_solar_array_part()
        result = build_aggregation_expression(redef, mults, part)
        assert result is not None
        assert "module_count" in result.entry_points
        assert "inverter_count" in result.entry_points

    def test_aggregation_transformed_expression(self):
        """Transformed expression contains parametric multiply terms."""
        redef = _make_solar_array_redef()
        mults = _make_solar_array_multiplicities()
        part = _make_solar_array_part()
        result = build_aggregation_expression(redef, mults, part)
        assert result is not None
        assert "module_count * pv_module.capital_cost" in result.transformed_expression
        assert "inverter_count * inverter.capital_cost" in result.transformed_expression
        assert "allocation_model.total_allocation" in result.transformed_expression
        assert "misc_hardware_cost" in result.transformed_expression


# ---------------------------------------------------------------------------
# Phase 4 — Test Suite 6: Integration (extract_hierarchy_data orchestrator)
# ---------------------------------------------------------------------------


class TestExtractHierarchyData:
    """Test extract_hierarchy_data() orchestrator."""

    def test_extract_hierarchy_data_full_mock(self):
        """Full mock hierarchy -> all data structures populated."""
        # PartDef with literal redef + expression redef + arrayed child
        referent = MockMultiplicityReferent("module_count", default_value=20)
        upper = MockUpperBound(referent)
        mult_range = MockMultiplicityRange(cached_lower_bound=20, upper_bound=upper)
        pv_usage = MockPartUsageForMultiplicity("pv_module", multiplicity=mult_range)

        sum_expr = _make_sum_invocation("pv_module", "capital_cost")
        expr_member = MockReferenceUsage(
            name="capital_cost",
            owned_redefinitions=[MockRedefinition(MockRedefinedFeature(name="capital_cost"))],
            feature_value_expression=sum_expr,
        )
        literal_member = _make_literal_redef_member("wattage", 400.0)

        part_def = MockPartDefinitionForRedef(
            "Solar_Array",
            owned_members=[literal_member, expr_member, pv_usage],
        )

        # Design override
        deep_member = _make_deep_path_redef_member(["pv_module", "wattage"], 400.0)
        design_usage = MockPartUsageForDesign(
            name="solar_array",
            owned_redefinitions=[MockRedefinition(MockRedefinedFeature(name="solar_array"))],
            owned_members=[deep_member],
        )

        def side_effect(model, type_name):
            if type_name == "PartDefinition":
                return [part_def]
            if type_name == "PartUsage":
                return [design_usage]
            return []

        with patch(
            "sysml_codegen.extraction.hierarchy_resolver.SysideAdapter.elements_of_type",
            side_effect=side_effect,
        ):
            result = extract_hierarchy_data("mock_model")

        assert len(result.redefinitions) == 2  # literal + expression
        assert len(result.multiplicities) == 1  # pv_module
        assert len(result.aggregation_expressions) == 1  # capital_cost
        assert len(result.design_overrides) == 1  # pv_module.wattage
        assert result.aggregation_expressions[0].attribute_name == "capital_cost"
        assert len(result.aggregation_expressions[0].sum_terms) == 1


# ---------------------------------------------------------------------------
# BF-1 — Test Suite: _walk_aggregation_ast() Evaluation Unwrap
# ---------------------------------------------------------------------------


def _make_wrapped_sum_invocation(
    part_name: str,
    attr_name: str,
    wrapper_name: str = "Evaluation",
) -> MockInvocationExpression:
    """Build a mock sum(Wrapper(part.attr)) InvocationExpression."""
    chain = MockFeatureChainExpression([part_name, attr_name])
    wrapper = MockInvocationExpression(wrapper_name, [chain])
    return MockInvocationExpression("sum", [wrapper])


class TestWalkAggregationAstEvaluationUnwrap:
    """BF-1: _walk_aggregation_ast() unwraps InvocationExpression around sum() operands."""

    def test_sum_with_evaluation_wrapper_produces_correct_sum_term(self):
        """sum(Evaluation(pv_module.capital_cost)) → SumTerm(part_usage_name='pv_module', ...)."""
        sum_expr = _make_wrapped_sum_invocation("pv_module", "capital_cost")
        redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="capital_cost",
            redefinition_type=RedefinitionType.EXPRESSION,
            expression_ast=sum_expr,
            expression_text="sum(Evaluation(pv_module.capital_cost))",
        )
        mults = [MultiplicityData("pv_module", "Lib__Solar_Array", 20, "module_count", 20)]
        part = MockPartDefinitionForRedef(
            "Solar_Array", owned_members=[MockPartUsageForMultiplicity("pv_module")]
        )
        result = build_aggregation_expression(redef, mults, part)
        assert result is not None
        assert len(result.sum_terms) == 1
        assert result.sum_terms[0].part_usage_name == "pv_module"
        assert result.sum_terms[0].attribute_name == "capital_cost"
        assert result.has_unsupported_nodes is False

    def test_sum_without_wrapper_still_works(self):
        """sum(pv_module.capital_cost) — no wrapper — still produces correct SumTerm."""
        sum_expr = _make_sum_invocation("pv_module", "capital_cost")
        redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="capital_cost",
            redefinition_type=RedefinitionType.EXPRESSION,
            expression_ast=sum_expr,
            expression_text="sum(pv_module.capital_cost)",
        )
        mults = [MultiplicityData("pv_module", "Lib__Solar_Array", 20, "module_count", 20)]
        part = MockPartDefinitionForRedef(
            "Solar_Array", owned_members=[MockPartUsageForMultiplicity("pv_module")]
        )
        result = build_aggregation_expression(redef, mults, part)
        assert result is not None
        assert len(result.sum_terms) == 1
        assert result.has_unsupported_nodes is False

    def test_nested_wrapper_unwrapped(self):
        """collect(Evaluation(chain)) — nested invocations are unwrapped."""
        chain = MockFeatureChainExpression(["inverter", "cost"])
        eval_wrap = MockInvocationExpression("Evaluation", [chain])
        collect_wrap = MockInvocationExpression("collect", [eval_wrap])
        sum_expr = MockInvocationExpression("sum", [collect_wrap])

        redef = RedefinitionData(
            owning_part_qn="Lib__Inverter_Array",
            attribute_name="capital_cost",
            redefinition_type=RedefinitionType.EXPRESSION,
            expression_ast=sum_expr,
            expression_text="sum(collect(Evaluation(inverter.cost)))",
        )
        mults = [MultiplicityData("inverter", "Lib__Inverter_Array", 4, "inverter_count", 4)]
        part = MockPartDefinitionForRedef(
            "Inverter_Array", owned_members=[MockPartUsageForMultiplicity("inverter")]
        )
        result = build_aggregation_expression(redef, mults, part)
        assert result is not None
        assert len(result.sum_terms) == 1
        assert result.sum_terms[0].part_usage_name == "inverter"
        assert result.has_unsupported_nodes is False

    def test_non_sum_evaluation_wrapper_unwrapped_not_marked_unsupported(self):
        """Standalone Evaluation(chain) outside sum() is unwrapped, not marked unsupported."""
        chain = MockFeatureChainExpression(["allocation_model", "total_allocation"])
        eval_wrapper = MockInvocationExpression("Evaluation", [chain])

        redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="total",
            redefinition_type=RedefinitionType.EXPRESSION,
            expression_ast=eval_wrapper,
            expression_text="Evaluation(allocation_model.total_allocation)",
        )
        part = MockPartDefinitionForRedef("Solar_Array", owned_members=[])
        result = build_aggregation_expression(redef, [], part)
        assert result is not None
        assert result.has_unsupported_nodes is False
        assert len(result.singleton_terms) == 1
        assert result.singleton_terms[0].source_path == "allocation_model.total_allocation"

    def test_transformed_expression_contains_real_attribute_names(self):
        """After unwrap, transformed_expression has real names, not 'Evaluation()'."""
        sum_expr = _make_wrapped_sum_invocation("pv_module", "capital_cost")
        redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="capital_cost",
            redefinition_type=RedefinitionType.EXPRESSION,
            expression_ast=sum_expr,
            expression_text="sum(Evaluation(pv_module.capital_cost))",
        )
        mults = [MultiplicityData("pv_module", "Lib__Solar_Array", 20, "module_count", 20)]
        part = MockPartDefinitionForRedef(
            "Solar_Array", owned_members=[MockPartUsageForMultiplicity("pv_module")]
        )
        result = build_aggregation_expression(redef, mults, part)
        assert result is not None
        assert "Evaluation" not in result.transformed_expression
        assert "pv_module" in result.transformed_expression or "capital_cost" in result.transformed_expression

    def test_mixed_expression_with_evaluation_wrappers(self):
        """Full expression with Evaluation wrappers on both sum() terms."""
        sum1 = _make_wrapped_sum_invocation("pv_module", "capital_cost")
        sum2 = _make_wrapped_sum_invocation("inverter", "capital_cost")
        alloc = MockFeatureChainExpression(["allocation_model", "total_allocation"])
        misc = MockFeatureReferenceExpression("misc_hardware_cost")
        inner = MockOperatorExpression("+", [sum1, sum2])
        mid = MockOperatorExpression("+", [inner, alloc])
        full_ast = MockOperatorExpression("+", [mid, misc])

        redef = RedefinitionData(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="capital_cost",
            redefinition_type=RedefinitionType.EXPRESSION,
            expression_ast=full_ast,
            expression_text="sum(Evaluation(pv_module.capital_cost)) + sum(Evaluation(inverter.capital_cost)) + allocation_model.total_allocation + misc_hardware_cost",
        )
        mults = _make_solar_array_multiplicities()
        part = _make_solar_array_part()
        result = build_aggregation_expression(redef, mults, part)
        assert result is not None
        assert len(result.sum_terms) == 2
        assert len(result.singleton_terms) == 1
        assert len(result.local_terms) == 1
        assert result.has_unsupported_nodes is False
        assert "module_count * pv_module.capital_cost" in result.transformed_expression
        assert "inverter_count * inverter.capital_cost" in result.transformed_expression
        assert "Evaluation" not in result.transformed_expression
