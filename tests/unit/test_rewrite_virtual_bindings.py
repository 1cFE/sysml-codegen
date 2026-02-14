"""Unit tests for _rewrite_virtual_bindings() leaf extraction and CHAIN override support.

Phase 4: Virtual binding rewrite enhancement — the only behavioral change in Item 2.
"""

from agentic_mbse.sysml.types import BindingType

from sysml_codegen.extraction.data_models import (
    HierarchyExtractionResult,
    RedefinitionData,
    RedefinitionType,
)
from sysml_codegen.extraction.usage_extractor import BindingInfo, CalcUsageData
from sysml_codegen.generation.initialization import _rewrite_virtual_bindings


def _make_virtual_calc_usage(
    qn: str = "Design__plant__calc",
    bindings: list[BindingInfo] | None = None,
) -> CalcUsageData:
    return CalcUsageData(
        instance_name=qn,
        calc_def_name="CostModel",
        calc_def_qualified_name="Lib__CostModel",
        module_type="CostModelModule",
        bindings=bindings or [],
        qualified_name=qn,
        is_template=False,
        owning_part_def_qn=None,
    )


def _make_hierarchy(
    design_overrides: list[RedefinitionData] | None = None,
) -> HierarchyExtractionResult:
    return HierarchyExtractionResult(
        redefinitions=[],
        design_overrides=design_overrides or [],
        multiplicities=[],
        aggregation_expressions=[],
        warnings=[],
    )


class TestLeafExtraction:
    """Tests for leaf extraction from SYSML_QN and DOTTED source_path formats."""

    def test_sysml_qn_format_leaf_extraction(self):
        """SYSML_QN source_path (Lib::CostModel::total_cost) → leaf 'total_cost' matched."""
        usage = _make_virtual_calc_usage(
            qn="Design__plant__cost_model",
            bindings=[
                BindingInfo(
                    param_name="total_cost",
                    source_path="Lib::CostModel::total_cost",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
        )
        override = RedefinitionData(
            owning_part_qn="Design__plant",
            attribute_name="total_cost",
            redefinition_type=RedefinitionType.LITERAL,
            literal_value=999.0,
            is_deep_path=False,
        )
        hierarchy = _make_hierarchy(design_overrides=[override])

        count = _rewrite_virtual_bindings([usage], hierarchy)

        assert count == 1
        assert usage.bindings[0].binding_type == BindingType.LITERAL
        assert usage.bindings[0].literal_value == 999.0
        assert usage.bindings[0].source_path is None

    def test_dotted_format_leaf_extraction(self):
        """DOTTED source_path (cost_model.total_cost) → leaf 'total_cost' matched."""
        usage = _make_virtual_calc_usage(
            qn="Design__plant__cost_model",
            bindings=[
                BindingInfo(
                    param_name="total_cost",
                    source_path="cost_model.total_cost",
                    binding_type=BindingType.CHAIN,
                ),
            ],
        )
        override = RedefinitionData(
            owning_part_qn="Design__plant",
            attribute_name="total_cost",
            redefinition_type=RedefinitionType.LITERAL,
            literal_value=500.0,
            is_deep_path=False,
        )
        hierarchy = _make_hierarchy(design_overrides=[override])

        count = _rewrite_virtual_bindings([usage], hierarchy)

        assert count == 1
        assert usage.bindings[0].binding_type == BindingType.LITERAL
        assert usage.bindings[0].literal_value == 500.0

    def test_bare_name_still_works(self):
        """Bare-name source_path ('total_cost') → leaf extraction is identity."""
        usage = _make_virtual_calc_usage(
            qn="Design__plant__cost_model",
            bindings=[
                BindingInfo(
                    param_name="total_cost",
                    source_path="total_cost",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
        )
        override = RedefinitionData(
            owning_part_qn="Design__plant",
            attribute_name="total_cost",
            redefinition_type=RedefinitionType.LITERAL,
            literal_value=42.0,
            is_deep_path=False,
        )
        hierarchy = _make_hierarchy(design_overrides=[override])

        count = _rewrite_virtual_bindings([usage], hierarchy)

        assert count == 1
        assert usage.bindings[0].literal_value == 42.0


class TestChainOverrideSupport:
    """Tests for CHAIN override rewrite behavior."""

    def test_chain_override_rewrites_source_path(self):
        """CHAIN override → binding.source_path = matched.source_path, type unchanged."""
        usage = _make_virtual_calc_usage(
            qn="Design__plant__cost_model",
            bindings=[
                BindingInfo(
                    param_name="capital_cost",
                    source_path="capital_cost",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
        )
        override = RedefinitionData(
            owning_part_qn="Design__plant",
            attribute_name="capital_cost",
            redefinition_type=RedefinitionType.CHAIN,
            source_path="cost_model.total_cost",
            is_deep_path=False,
        )
        hierarchy = _make_hierarchy(design_overrides=[override])

        count = _rewrite_virtual_bindings([usage], hierarchy)

        assert count == 1
        # source_path rewritten to the CHAIN target
        assert usage.bindings[0].source_path == "cost_model.total_cost"
        # binding_type is NOT changed to LITERAL
        assert usage.bindings[0].binding_type == BindingType.REFERENCE

    def test_literal_override_still_works(self):
        """LITERAL override → existing behavior (binding_type → LITERAL)."""
        usage = _make_virtual_calc_usage(
            qn="Design__plant__cost_model",
            bindings=[
                BindingInfo(
                    param_name="wattage",
                    source_path="wattage",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
        )
        override = RedefinitionData(
            owning_part_qn="Design__plant",
            attribute_name="wattage",
            redefinition_type=RedefinitionType.LITERAL,
            literal_value=400.0,
            is_deep_path=False,
        )
        hierarchy = _make_hierarchy(design_overrides=[override])

        count = _rewrite_virtual_bindings([usage], hierarchy)

        assert count == 1
        assert usage.bindings[0].binding_type == BindingType.LITERAL
        assert usage.bindings[0].literal_value == 400.0
        assert usage.bindings[0].source_path is None

    def test_no_match_binding_unchanged(self):
        """No matching override → binding left as-is."""
        usage = _make_virtual_calc_usage(
            qn="Design__plant__cost_model",
            bindings=[
                BindingInfo(
                    param_name="efficiency",
                    source_path="Lib::CostModel::efficiency",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
        )
        # Override is for 'wattage', not 'efficiency'
        override = RedefinitionData(
            owning_part_qn="Design__plant",
            attribute_name="wattage",
            redefinition_type=RedefinitionType.LITERAL,
            literal_value=400.0,
            is_deep_path=False,
        )
        hierarchy = _make_hierarchy(design_overrides=[override])

        count = _rewrite_virtual_bindings([usage], hierarchy)

        assert count == 0
        assert usage.bindings[0].source_path == "Lib::CostModel::efficiency"
        assert usage.bindings[0].binding_type == BindingType.REFERENCE

    def test_chain_override_with_dotted_source_path(self):
        """CHAIN override matched via dotted leaf extraction."""
        usage = _make_virtual_calc_usage(
            qn="Design__plant__cost_model",
            bindings=[
                BindingInfo(
                    param_name="area",
                    source_path="panel.area",
                    binding_type=BindingType.CHAIN,
                ),
            ],
        )
        override = RedefinitionData(
            owning_part_qn="Design__plant",
            attribute_name="area",
            redefinition_type=RedefinitionType.CHAIN,
            source_path="solar_panel.surface_area",
            is_deep_path=False,
        )
        hierarchy = _make_hierarchy(design_overrides=[override])

        count = _rewrite_virtual_bindings([usage], hierarchy)

        assert count == 1
        assert usage.bindings[0].source_path == "solar_panel.surface_area"
