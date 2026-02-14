"""Unit tests for Phase 1: hierarchy pipeline data models and algorithms.

Tests ScopedAggregationData, _rewrite_virtual_bindings(), and
_scope_aggregation_expressions() -- the foundation for hierarchy-aware
module generation.
"""

from pathlib import Path

from agentic_mbse.sysml.types import BindingType

from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    HierarchyExtractionResult,
    MultiplicityData,
    RedefinitionData,
    RedefinitionType,
    ScopedAggregationData,
    SumTerm,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.usage_extractor import BindingInfo, CalcUsageData
from sysml_codegen.generation.initialization import (
    PipelineContext,
    _rewrite_virtual_bindings,
    _scope_aggregation_expressions,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_agg_expr(**kwargs) -> AggregationExpressionData:
    defaults = {
        "owning_part_qn": "Lib__Solar_Array",
        "owning_part_name": "Solar_Array",
        "attribute_name": "capital_cost",
        "raw_expression_text": "sum(pv_module.capital_cost * module_count)",
        "transformed_expression": "module_count * pv_module_capital_cost",
        "sum_terms": [],
        "singleton_terms": [],
        "local_terms": [],
        "input_channels": [],
        "entry_points": [],
    }
    defaults.update(kwargs)
    return AggregationExpressionData(**defaults)


def _make_virtual_calc_usage(
    qn: str = "Design__part__calc",
    owning_part_def_qn: str | None = None,
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
        owning_part_def_qn=owning_part_def_qn,
    )


def _make_hierarchy_with_override(
    owning_part_qn: str,
    target_path: list[str],
    literal_value: float | int,
) -> HierarchyExtractionResult:
    override = RedefinitionData(
        owning_part_qn=owning_part_qn,
        attribute_name=target_path[-1],
        redefinition_type=RedefinitionType.LITERAL,
        literal_value=literal_value,
        target_path=target_path,
        is_deep_path=len(target_path) >= 2,
    )
    return HierarchyExtractionResult(
        redefinitions=[],
        design_overrides=[override],
        multiplicities=[],
        aggregation_expressions=[],
        warnings=[],
    )


def _make_hierarchy(
    agg_exprs: list[AggregationExpressionData] | None = None,
    design_overrides: list[RedefinitionData] | None = None,
    multiplicities: list[MultiplicityData] | None = None,
    part_usage_names: dict[str, set[str]] | None = None,
) -> HierarchyExtractionResult:
    return HierarchyExtractionResult(
        redefinitions=[],
        design_overrides=design_overrides or [],
        multiplicities=multiplicities or [],
        aggregation_expressions=agg_exprs or [],
        warnings=[],
        part_usage_names=part_usage_names or {},
    )


# ---------------------------------------------------------------------------
# TestScopedAggregationData
# ---------------------------------------------------------------------------


class TestScopedAggregationData:
    def test_module_eqn_property(self):
        agg = ScopedAggregationData(
            expression=_make_agg_expr(
                owning_part_qn="Lib__Solar_Array", attribute_name="capital_cost"
            ),
            instance_path="SolarBatteryDesign__solar_battery_plant__solar_array",
        )
        assert (
            agg.module_eqn
            == "SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost"
        )

    def test_expression_composition_access(self):
        """Delegated fields accessible via agg.expression.*"""
        agg = ScopedAggregationData(
            expression=_make_agg_expr(
                attribute_name="weight",
                sum_terms=[SumTerm("pv_module", "weight", "module_count", 20)],
            ),
            instance_path="Design__plant",
        )
        assert agg.expression.attribute_name == "weight"
        assert len(agg.expression.sum_terms) == 1
        assert agg.expression.sum_terms[0].multiplicity_count == 20


# ---------------------------------------------------------------------------
# TestRewriteVirtualBindings
# ---------------------------------------------------------------------------


class TestRewriteVirtualBindings:
    def test_literal_override_rewrites_binding(self):
        """Deep-path :>> pv_module.wattage = 400.0 rewrites bare 'wattage' binding to LITERAL."""
        usage = _make_virtual_calc_usage(
            qn="Design__plant__solar_array__pv_module__cost_model",
            bindings=[
                BindingInfo(
                    param_name="wattage",
                    source_path="wattage",
                    binding_type=BindingType.REFERENCE,
                )
            ],
        )
        # Override lives on solar_array PartUsage, deep-path to pv_module.wattage
        hierarchy = _make_hierarchy_with_override(
            owning_part_qn="Design__plant__solar_array",
            target_path=["pv_module", "wattage"],
            literal_value=400.0,
        )
        count = _rewrite_virtual_bindings([usage], hierarchy)
        assert count == 1
        assert usage.bindings[0].binding_type == BindingType.LITERAL
        assert usage.bindings[0].literal_value == 400.0
        assert usage.bindings[0].source_path is None

    def test_no_override_leaves_binding_unchanged(self):
        """Binding with no matching override remains as-is (becomes entry point downstream)."""
        usage = _make_virtual_calc_usage(
            qn="Design__plant__solar_array__pv_module__cost_model",
            bindings=[
                BindingInfo(
                    param_name="efficiency",
                    source_path="efficiency",
                    binding_type=BindingType.REFERENCE,
                )
            ],
        )
        # Override is for 'wattage', not 'efficiency'
        hierarchy = _make_hierarchy_with_override(
            owning_part_qn="Design__plant__solar_array",
            target_path=["pv_module", "wattage"],
            literal_value=400.0,
        )
        count = _rewrite_virtual_bindings([usage], hierarchy)
        assert count == 0
        assert usage.bindings[0].binding_type == BindingType.REFERENCE
        assert usage.bindings[0].source_path == "efficiency"

    def test_already_literal_binding_skipped(self):
        """LITERAL bindings are not re-processed."""
        usage = _make_virtual_calc_usage(
            qn="Design__plant__solar_array__pv_module__cost_model",
            bindings=[
                BindingInfo(
                    param_name="wattage",
                    source_path=None,
                    binding_type=BindingType.LITERAL,
                    literal_value=300.0,
                )
            ],
        )
        hierarchy = _make_hierarchy_with_override(
            owning_part_qn="Design__plant__solar_array",
            target_path=["pv_module", "wattage"],
            literal_value=400.0,
        )
        count = _rewrite_virtual_bindings([usage], hierarchy)
        assert count == 0
        assert usage.bindings[0].literal_value == 300.0  # Unchanged

    def test_dotted_source_path_no_match_unchanged(self):
        """Dotted paths with no matching override remain unchanged."""
        usage = _make_virtual_calc_usage(
            qn="Design__plant__solar_array__pv_module__cost_model",
            bindings=[
                BindingInfo(
                    param_name="area",
                    source_path="panel.area",
                    binding_type=BindingType.CHAIN,
                )
            ],
        )
        hierarchy = _make_hierarchy(design_overrides=[])
        count = _rewrite_virtual_bindings([usage], hierarchy)
        assert count == 0
        assert usage.bindings[0].source_path == "panel.area"

    def test_template_usages_skipped(self):
        """Template CalcUsages (is_template=True) are not processed."""
        usage = CalcUsageData(
            instance_name="cost_model",
            calc_def_name="CostModel",
            calc_def_qualified_name="Lib__CostModel",
            module_type="CostModelModule",
            bindings=[
                BindingInfo(
                    param_name="wattage",
                    source_path="wattage",
                    binding_type=BindingType.REFERENCE,
                )
            ],
            qualified_name="Lib__PV_Module__cost_model",
            is_template=True,
            owning_part_def_qn="Lib__PV_Module",
        )
        hierarchy = _make_hierarchy_with_override(
            owning_part_qn="Lib__PV_Module",
            target_path=["wattage"],
            literal_value=400.0,
        )
        count = _rewrite_virtual_bindings([usage], hierarchy)
        assert count == 0

    def test_simple_override_no_deep_path(self):
        """Simple override :>> wattage = 400.0 directly on PartUsage."""
        usage = _make_virtual_calc_usage(
            qn="Design__plant__cost_model",
            bindings=[
                BindingInfo(
                    param_name="wattage",
                    source_path="wattage",
                    binding_type=BindingType.REFERENCE,
                )
            ],
        )
        override = RedefinitionData(
            owning_part_qn="Design__plant",
            attribute_name="wattage",
            redefinition_type=RedefinitionType.LITERAL,
            literal_value=500.0,
            is_deep_path=False,
        )
        hierarchy = _make_hierarchy(design_overrides=[override])
        count = _rewrite_virtual_bindings([usage], hierarchy)
        assert count == 1
        assert usage.bindings[0].literal_value == 500.0

    def test_multiple_usages_same_template(self):
        """Multiple virtual instances from same template all get rewritten."""
        bindings_a = [
            BindingInfo(
                param_name="wattage",
                source_path="wattage",
                binding_type=BindingType.REFERENCE,
            )
        ]
        bindings_b = [
            BindingInfo(
                param_name="wattage",
                source_path="wattage",
                binding_type=BindingType.REFERENCE,
            )
        ]
        usage_a = _make_virtual_calc_usage(
            qn="Design__plant__array_1__pv_module__cost_model",
            bindings=bindings_a,
        )
        usage_b = _make_virtual_calc_usage(
            qn="Design__plant__array_2__pv_module__cost_model",
            bindings=bindings_b,
        )
        # Overrides for both arrays
        overrides = [
            RedefinitionData(
                owning_part_qn="Design__plant__array_1",
                attribute_name="wattage",
                redefinition_type=RedefinitionType.LITERAL,
                literal_value=400.0,
                target_path=["pv_module", "wattage"],
                is_deep_path=True,
            ),
            RedefinitionData(
                owning_part_qn="Design__plant__array_2",
                attribute_name="wattage",
                redefinition_type=RedefinitionType.LITERAL,
                literal_value=350.0,
                target_path=["pv_module", "wattage"],
                is_deep_path=True,
            ),
        ]
        hierarchy = _make_hierarchy(design_overrides=overrides)
        count = _rewrite_virtual_bindings([usage_a, usage_b], hierarchy)
        assert count == 2
        assert usage_a.bindings[0].literal_value == 400.0
        assert usage_b.bindings[0].literal_value == 350.0

    def test_chain_override_rewrites_source_path(self):
        """CHAIN redefinitions rewrite binding.source_path to the chain target."""
        usage = _make_virtual_calc_usage(
            qn="Design__plant__cost_model",
            bindings=[
                BindingInfo(
                    param_name="capital_cost",
                    source_path="capital_cost",
                    binding_type=BindingType.REFERENCE,
                )
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
        assert usage.bindings[0].source_path == "cost_model.total_cost"
        # binding_type preserved (not changed to LITERAL)
        assert usage.bindings[0].binding_type == BindingType.REFERENCE


# ---------------------------------------------------------------------------
# TestScopeAggregationExpressions
# ---------------------------------------------------------------------------


class TestScopeAggregationExpressions:
    def test_child_match_strategy(self):
        """Solar_Array agg found via child PV_Module virtual CalcUsage QN segments."""
        agg_expr = _make_agg_expr(
            owning_part_qn="Lib__Solar_Array", owning_part_name="Solar_Array"
        )
        multiplicities = [
            MultiplicityData("pv_module", "Lib__Solar_Array", 20, "module_count", 20),
        ]
        usages = [
            _make_virtual_calc_usage(
                qn="SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model",
                owning_part_def_qn="Lib__PV_Module",
            )
        ]
        result = _scope_aggregation_expressions(
            _make_hierarchy(
                agg_exprs=[agg_expr],
                multiplicities=multiplicities,
                part_usage_names={"Lib__Solar_Array": {"pv_module"}},
            ), usages
        )
        assert len(result) == 1
        assert (
            result[0].instance_path
            == "SolarBatteryDesign__solar_battery_plant__solar_array"
        )

    def test_direct_match_strategy(self):
        """PartDef with its own CalcUsage matches directly via owning_part_def_qn."""
        agg_expr = _make_agg_expr(
            owning_part_qn="Lib__PV_Module", owning_part_name="PV_Module"
        )
        usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__pv_module__cost_model",
                owning_part_def_qn="Lib__PV_Module",
            )
        ]
        result = _scope_aggregation_expressions(
            _make_hierarchy(agg_exprs=[agg_expr]), usages
        )
        assert len(result) == 1
        assert result[0].instance_path == "Design__plant__solar_array__pv_module"

    def test_deduplicates_instance_paths(self):
        """Multiple child CalcUsages on same PartDef produce single ScopedAggregationData."""
        agg_expr = _make_agg_expr(
            owning_part_qn="Lib__Solar_Array", owning_part_name="Solar_Array"
        )
        multiplicities = [
            MultiplicityData("pv_module", "Lib__Solar_Array", 20, "module_count", 20),
            MultiplicityData("inverter", "Lib__Solar_Array", 4, "inverter_count", 4),
        ]
        usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__pv_module__cost_model",
                owning_part_def_qn="Lib__PV_Module",
            ),
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__inverter__cost_model",
                owning_part_def_qn="Lib__Inverter",
            ),
        ]
        result = _scope_aggregation_expressions(
            _make_hierarchy(
                agg_exprs=[agg_expr],
                multiplicities=multiplicities,
                part_usage_names={"Lib__Solar_Array": {"pv_module", "inverter"}},
            ), usages
        )
        assert len(result) == 1
        assert result[0].instance_path == "Design__plant__solar_array"

    def test_no_match_returns_empty(self):
        """Aggregation expression with no matching virtual CalcUsages returns empty."""
        agg_expr = _make_agg_expr(
            owning_part_qn="Lib__Wind_Turbine", owning_part_name="Wind_Turbine"
        )
        usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__pv_module__cost_model",
                owning_part_def_qn="Lib__PV_Module",
            )
        ]
        result = _scope_aggregation_expressions(
            _make_hierarchy(agg_exprs=[agg_expr]), usages
        )
        assert len(result) == 0

    def test_none_hierarchy_returns_empty(self):
        """None hierarchy_data returns empty list without error."""
        result = _scope_aggregation_expressions(None, [])
        assert result == []

    def test_module_eqn_from_scoped_data(self):
        """ScopedAggregationData.module_eqn produces correct ADR-003 name."""
        agg_expr = _make_agg_expr(
            owning_part_qn="Lib__Solar_Array",
            owning_part_name="Solar_Array",
            attribute_name="capital_cost",
        )
        multiplicities = [
            MultiplicityData("pv_module", "Lib__Solar_Array", 20, "module_count", 20),
        ]
        usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__pv_module__cost_model",
                owning_part_def_qn="Lib__PV_Module",
            )
        ]
        result = _scope_aggregation_expressions(
            _make_hierarchy(
                agg_exprs=[agg_expr],
                multiplicities=multiplicities,
                part_usage_names={"Lib__Solar_Array": {"pv_module"}},
            ), usages
        )
        assert len(result) == 1
        assert result[0].module_eqn == "Design__plant__solar_array__capital_cost"

    def test_direct_match_preferred_over_child(self):
        """If PartDef has its own CalcUsage, direct match is used (no child match)."""
        agg_expr = _make_agg_expr(
            owning_part_qn="Lib__Solar_Array", owning_part_name="Solar_Array"
        )
        usages = [
            # Direct match: CalcUsage owned by Solar_Array itself
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__agg_calc",
                owning_part_def_qn="Lib__Solar_Array",
            ),
            # Child match candidate (should not be used)
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__pv_module__cost_model",
                owning_part_def_qn="Lib__PV_Module",
            ),
        ]
        result = _scope_aggregation_expressions(
            _make_hierarchy(agg_exprs=[agg_expr]), usages
        )
        assert len(result) == 1
        # Direct match produces parent of the direct CalcUsage
        assert result[0].instance_path == "Design__plant__solar_array"


# ---------------------------------------------------------------------------
# BF-6: Scope Aggregation via Child-Walk
# ---------------------------------------------------------------------------


class TestScopeAggregationSiteInfra:
    """BF-6: _scope_aggregation_expressions() finds Site Infrastructure via child-walk."""

    def test_partdef_with_mismatched_usage_name_scoped_via_children(self):
        """PartDef 'SiteInfrastructure' typed by usage 'site_infra' is found via child-walk."""
        agg_expr = _make_agg_expr(
            owning_part_qn="Lib__SiteInfrastructure",
            owning_part_name="SiteInfrastructure",
            attribute_name="capital_cost",
        )
        multiplicities = [
            MultiplicityData(
                owning_part_def_qn="Lib__SiteInfrastructure",
                part_usage_name="grid_connection",
                count=2,
                count_attribute_name="connection_count",
                default_value=2,
            ),
        ]
        virtual_usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__site_infra__grid_connection__cost_model",
                owning_part_def_qn="Lib__GridConnection",
            ),
        ]
        hierarchy = _make_hierarchy(
            agg_exprs=[agg_expr],
            multiplicities=multiplicities,
            part_usage_names={"Lib__SiteInfrastructure": {"grid_connection"}},
        )

        result = _scope_aggregation_expressions(hierarchy, virtual_usages)

        assert len(result) == 1
        assert "site_infra" in result[0].instance_path

    def test_child_walk_does_not_duplicate_with_strategy1(self):
        """If Strategy 1 (direct match) already found paths, child-walk is skipped."""
        agg_expr = _make_agg_expr(
            owning_part_qn="Lib__Solar_Array",
            owning_part_name="Solar_Array",
        )
        multiplicities = [
            MultiplicityData(
                owning_part_def_qn="Lib__Solar_Array",
                part_usage_name="pv_module",
                count=20,
                count_attribute_name="module_count",
                default_value=20,
            ),
        ]
        usages = [
            # Direct match via owning_part_def_qn
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__agg_calc",
                owning_part_def_qn="Lib__Solar_Array",
            ),
            # Child usages that child-walk could also find
            _make_virtual_calc_usage(
                qn="Design__plant__solar_array__pv_module__cost_model",
                owning_part_def_qn="Lib__PV_Module",
            ),
        ]
        hierarchy = _make_hierarchy(
            agg_exprs=[agg_expr],
            multiplicities=multiplicities,
        )

        result = _scope_aggregation_expressions(hierarchy, usages)
        assert len(result) == 1  # Strategy 1 found it, no duplicate from child-walk

    def test_all_four_assemblies_scoped(self):
        """With 4 assembly PartDefs (including mismatched name), all 4 get scoped."""
        agg_exprs = [
            _make_agg_expr(owning_part_qn="Lib__Solar_Array", owning_part_name="Solar_Array", attribute_name="capital_cost"),
            _make_agg_expr(owning_part_qn="Lib__Battery_System", owning_part_name="Battery_System", attribute_name="capital_cost"),
            _make_agg_expr(owning_part_qn="Lib__Inverter_Array", owning_part_name="Inverter_Array", attribute_name="capital_cost"),
            _make_agg_expr(owning_part_qn="Lib__SiteInfrastructure", owning_part_name="SiteInfrastructure", attribute_name="capital_cost"),
        ]
        multiplicities = [
            MultiplicityData("pv_module", "Lib__Solar_Array", 20, "module_count", 20),
            MultiplicityData("battery_pack", "Lib__Battery_System", 8, "pack_count", 8),
            MultiplicityData("inverter", "Lib__Inverter_Array", 4, "inverter_count", 4),
            MultiplicityData("grid_connection", "Lib__SiteInfrastructure", 2, "connection_count", 2),
        ]
        usages = [
            # Child CalcUsages — each child's QN contains the parent instance path segment
            _make_virtual_calc_usage(qn="Design__plant__solar_array__pv_module__cost_model", owning_part_def_qn="Lib__PV_Module"),
            _make_virtual_calc_usage(qn="Design__plant__battery_system__battery_pack__cost_model", owning_part_def_qn="Lib__BatteryPack"),
            _make_virtual_calc_usage(qn="Design__plant__inverter_array__inverter__cost_model", owning_part_def_qn="Lib__Inverter"),
            _make_virtual_calc_usage(qn="Design__plant__site_infra__grid_connection__cost_model", owning_part_def_qn="Lib__GridConnection"),
        ]
        hierarchy = _make_hierarchy(
            agg_exprs=agg_exprs,
            multiplicities=multiplicities,
            part_usage_names={
                "Lib__Solar_Array": {"pv_module"},
                "Lib__Battery_System": {"battery_pack"},
                "Lib__Inverter_Array": {"inverter"},
                "Lib__SiteInfrastructure": {"grid_connection"},
            },
        )

        result = _scope_aggregation_expressions(hierarchy, usages)
        assert len(result) == 4

        instance_paths = {r.instance_path for r in result}
        assert "Design__plant__solar_array" in instance_paths
        assert "Design__plant__battery_system" in instance_paths
        assert "Design__plant__inverter_array" in instance_paths
        assert "Design__plant__site_infra" in instance_paths


# ---------------------------------------------------------------------------
# Tests: FR-10 PipelineContext Fields (direct assertion)
# ---------------------------------------------------------------------------


class TestPipelineContextHierarchyFields:
    """FR-10: PipelineContext has hierarchy_data and aggregation_expressions fields."""

    def test_hierarchy_data_field_exists(self):
        """PipelineContext has hierarchy_data field defaulting to None."""
        import dataclasses

        field_names = [f.name for f in dataclasses.fields(PipelineContext)]
        assert "hierarchy_data" in field_names

    def test_aggregation_expressions_field_exists(self):
        """PipelineContext has aggregation_expressions field defaulting to empty list."""
        import dataclasses

        fields = {f.name: f for f in dataclasses.fields(PipelineContext)}
        assert "aggregation_expressions" in fields
        assert fields["aggregation_expressions"].default_factory == list
