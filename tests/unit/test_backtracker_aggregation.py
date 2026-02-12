"""Unit tests for backtracker aggregation output awareness (Phase 2).

Tests the aggregation output index, three-level cascade lookup, and
_trace_dependencies() integration that resolves CalcUsage bindings
to aggregation module outputs as MODULE_OUTPUT.
"""

from dataclasses import dataclass, field

from agentic_mbse.sysml.types import BindingType

from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.core.models import BindingResolutionType
from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    ScopedAggregationData,
)
from sysml_codegen.extraction.usage_extractor import BindingInfo, CalcUsageData


# ---------------------------------------------------------------------------
# Test helpers (reused from test_backtracker_computed_attrs.py pattern)
# ---------------------------------------------------------------------------


def _make_scoped_agg(
    attribute_name: str = "capital_cost",
    owning_part_qn: str = "Lib__Solar_Array",
    owning_part_name: str = "Solar_Array",
    instance_path: str = "Design__plant__solar_array",
) -> ScopedAggregationData:
    expr = AggregationExpressionData(
        owning_part_qn=owning_part_qn,
        owning_part_name=owning_part_name,
        attribute_name=attribute_name,
        raw_expression_text="sum(...)",
        transformed_expression="...",
        sum_terms=[],
        singleton_terms=[],
        local_terms=[],
        input_channels=[],
        entry_points=[],
    )
    return ScopedAggregationData(expression=expr, instance_path=instance_path)


def _make_calc_usage(
    instance_name: str,
    calc_def_name: str,
    bindings: list[BindingInfo] | None = None,
    qualified_name: str = "",
) -> CalcUsageData:
    return CalcUsageData(
        instance_name=instance_name,
        calc_def_name=calc_def_name,
        calc_def_qualified_name=f"Lib__{calc_def_name}",
        module_type=f"{calc_def_name}Module",
        bindings=bindings or [],
        qualified_name=qualified_name or f"Pkg__Part__{instance_name}",
    )


@dataclass
class SimpleCalcDef:
    """Minimal calc def for backtracker tests."""

    name: str
    qualified_name: str
    output_attributes: list = field(default_factory=list)
    input_attributes: list = field(default_factory=list)


@dataclass
class SimpleAttrInfo:
    """Minimal attribute info for calc def outputs."""

    name: str


# ---------------------------------------------------------------------------
# Tests: Aggregation Output Index
# ---------------------------------------------------------------------------


class TestAggregationOutputIndex:
    def test_dotted_reference_resolves(self):
        """'solar_array.capital_cost' resolves to aggregation module output channel."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_array",
        )
        bt = DependencyBacktracker([], [], aggregation_data=[agg])
        assert "solar_array.capital_cost" in bt._aggregation_output_index

    def test_bare_reference_resolves(self):
        """Bare 'capital_cost' resolves when only one aggregation has that name."""
        agg = _make_scoped_agg(attribute_name="capital_cost")
        bt = DependencyBacktracker([], [], aggregation_data=[agg])
        assert "capital_cost" in bt._aggregation_output_index

    def test_full_instance_dotted_resolves(self):
        """Full dotted instance path resolves."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_array",
        )
        bt = DependencyBacktracker([], [], aggregation_data=[agg])
        assert (
            "Design.plant.solar_array.capital_cost"
            in bt._aggregation_output_index
        )

    def test_channel_name_format(self):
        """Channel follows PQN format: {module_eqn}__{attribute_name}."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_array",
        )
        bt = DependencyBacktracker([], [], aggregation_data=[agg])
        channel = bt._aggregation_output_index["solar_array.capital_cost"]
        assert (
            channel
            == "Design__plant__solar_array__capital_cost__capital_cost"
        )

    def test_bare_key_no_collision(self):
        """If two aggregations share same attribute_name, first wins bare key."""
        agg1 = _make_scoped_agg(
            attribute_name="capital_cost",
            owning_part_name="Solar_Array",
            instance_path="Design__plant__solar_array",
        )
        agg2 = _make_scoped_agg(
            attribute_name="capital_cost",
            owning_part_name="Battery_System",
            instance_path="Design__plant__battery_system",
        )
        bt = DependencyBacktracker([], [], aggregation_data=[agg1, agg2])

        # Both dotted keys present
        assert "solar_array.capital_cost" in bt._aggregation_output_index
        assert "battery_system.capital_cost" in bt._aggregation_output_index
        # Bare key only stores first
        assert "capital_cost" in bt._aggregation_output_index
        assert (
            bt._aggregation_output_index["capital_cost"]
            == bt._aggregation_output_index["solar_array.capital_cost"]
        )

    def test_empty_aggregation_data(self):
        """Empty aggregation_data produces empty index."""
        bt = DependencyBacktracker([], [], aggregation_data=[])
        assert bt._aggregation_output_index == {}

    def test_none_aggregation_data(self):
        """None aggregation_data produces empty index."""
        bt = DependencyBacktracker([], [], aggregation_data=None)
        assert bt._aggregation_output_index == {}


# ---------------------------------------------------------------------------
# Tests: _trace_dependencies() with Aggregation
# ---------------------------------------------------------------------------


class TestSystemCalcWiresToAggregation:
    def test_dotted_binding_resolves_to_module_output(self):
        """System-level CalcUsage with binding source_path='solar_array.capital_cost'
        resolves to MODULE_OUTPUT pointing at aggregation channel."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_array",
        )

        usage = _make_calc_usage(
            "financial_calc",
            "FinancialCalc",
            bindings=[
                BindingInfo(
                    param_name="total_capex",
                    source_path="solar_array.capital_cost",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
            qualified_name="Pkg__Part__financial_calc",
        )

        calc_def = SimpleCalcDef(
            name="FinancialCalc",
            qualified_name="Lib__FinancialCalc",
            output_attributes=[SimpleAttrInfo("lcoe")],
        )

        bt = DependencyBacktracker(
            [usage],
            [calc_def],
            aggregation_data=[agg],
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__financial_calc|total_capex"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
        assert (
            resolution.qualified_name
            == "Design__plant__solar_array__capital_cost__capital_cost"
        )
        assert resolution.source_path == "solar_array.capital_cost"
        assert resolution.is_transitive is False

    def test_bare_reference_resolves_for_top_level(self):
        """Bare 'capital_cost' resolves when only one aggregation has that name."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_array",
        )

        usage = _make_calc_usage(
            "system_calc",
            "SystemCalc",
            bindings=[
                BindingInfo(
                    param_name="capex",
                    source_path="capital_cost",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
            qualified_name="Pkg__Part__system_calc",
        )

        calc_def = SimpleCalcDef(
            name="SystemCalc",
            qualified_name="Lib__SystemCalc",
            output_attributes=[SimpleAttrInfo("result")],
        )

        bt = DependencyBacktracker(
            [usage],
            [calc_def],
            aggregation_data=[agg],
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__system_calc|capex"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT

    def test_sysml_qn_reference_normalizes(self):
        """'Package::solar_array::capital_cost' normalizes to dotted and resolves."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_array",
        )

        usage = _make_calc_usage(
            "sys_calc",
            "SysCalc",
            bindings=[
                BindingInfo(
                    param_name="cost_input",
                    source_path="Package::solar_array::capital_cost",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
            qualified_name="Pkg__Part__sys_calc",
        )

        calc_def = SimpleCalcDef(
            name="SysCalc",
            qualified_name="Lib__SysCalc",
            output_attributes=[SimpleAttrInfo("out")],
        )

        bt = DependencyBacktracker(
            [usage],
            [calc_def],
            aggregation_data=[agg],
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__sys_calc|cost_input"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT

    def test_trace_log_contains_aggregation_entry(self):
        """Trace log records AGGREGATION resolution for debugging."""
        agg = _make_scoped_agg(attribute_name="capital_cost")

        usage = _make_calc_usage(
            "sys_calc",
            "SysCalc",
            bindings=[
                BindingInfo(
                    param_name="cost",
                    source_path="solar_array.capital_cost",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
            qualified_name="Pkg__Part__sys_calc",
        )

        calc_def = SimpleCalcDef(
            name="SysCalc",
            qualified_name="Lib__SysCalc",
            output_attributes=[SimpleAttrInfo("out")],
        )

        bt = DependencyBacktracker(
            [usage],
            [calc_def],
            aggregation_data=[agg],
        )
        result = bt.find_required_modules([], include_all=True)

        agg_entries = [
            line for line in result.trace_log if "AGGREGATION" in line
        ]
        assert len(agg_entries) == 1
        assert "capital_cost" in agg_entries[0]

    def test_literal_binding_not_affected(self):
        """LITERAL bindings still handled before aggregation check."""
        agg = _make_scoped_agg(attribute_name="capital_cost")

        usage = _make_calc_usage(
            "calc",
            "Calc",
            bindings=[
                BindingInfo(
                    param_name="x",
                    source_path="42.0",
                    binding_type=BindingType.LITERAL,
                    literal_value=42.0,
                ),
            ],
            qualified_name="Pkg__Part__calc",
        )

        calc_def = SimpleCalcDef(
            name="Calc",
            qualified_name="Lib__Calc",
            output_attributes=[SimpleAttrInfo("out")],
        )

        bt = DependencyBacktracker(
            [usage],
            [calc_def],
            aggregation_data=[agg],
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__calc|x"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.ENTRY_POINT


# ---------------------------------------------------------------------------
# Tests: No Aggregation Data (backward compat)
# ---------------------------------------------------------------------------


class TestNoAggregationDataGraceful:
    def test_none_aggregation_data_works(self):
        """aggregation_data=None works same as before."""
        usage = _make_calc_usage(
            "calc",
            "Calc",
            bindings=[
                BindingInfo(
                    param_name="x",
                    source_path="some.output",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
            qualified_name="Pkg__Part__calc",
        )

        calc_def = SimpleCalcDef(
            name="Calc",
            qualified_name="Lib__Calc",
            output_attributes=[SimpleAttrInfo("out")],
        )

        # Should not raise
        bt = DependencyBacktracker(
            [usage],
            [calc_def],
            aggregation_data=None,
        )
        bt.find_required_modules([], include_all=True)

        # Binding goes to entry point (no aggregation, no other resolution)
        key = "Pkg__Part__calc|x"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.ENTRY_POINT

    def test_empty_list_aggregation_data_works(self):
        """aggregation_data=[] works same as before."""
        bt = DependencyBacktracker([], [], aggregation_data=[])
        assert bt._aggregation_output_index == {}


# ---------------------------------------------------------------------------
# BF-7: Aggregation Alias Resolution
# ---------------------------------------------------------------------------


class TestAggregationAliasResolution:
    """BF-7: EXPOSE_PURE aliases registered in aggregation output index."""

    def test_alias_in_index_resolves_to_module_output(self):
        """':>> total_capex = capital_cost' alias resolves to aggregation output."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_battery_plant",
        )
        agg.expression.aliases = ["total_capex"]

        bt = DependencyBacktracker([], [], aggregation_data=[agg])

        # Both original and alias should resolve
        assert "solar_battery_plant.capital_cost" in bt._aggregation_output_index
        assert "solar_battery_plant.total_capex" in bt._aggregation_output_index

    def test_bare_alias_resolves(self):
        """Bare alias name resolves when unambiguous."""
        agg = _make_scoped_agg(attribute_name="capital_cost")
        agg.expression.aliases = ["total_capex"]

        bt = DependencyBacktracker([], [], aggregation_data=[agg])
        assert "total_capex" in bt._aggregation_output_index

    def test_alias_channel_matches_original(self):
        """Alias points to the same channel as the original attribute."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_battery_plant",
        )
        agg.expression.aliases = ["total_capex"]

        bt = DependencyBacktracker([], [], aggregation_data=[agg])
        original_channel = bt._aggregation_output_index["solar_battery_plant.capital_cost"]
        alias_channel = bt._aggregation_output_index["solar_battery_plant.total_capex"]
        assert original_channel == alias_channel

    def test_full_dotted_alias_resolves(self):
        """Full dotted instance path with alias resolves."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_battery_plant",
        )
        agg.expression.aliases = ["total_capex"]

        bt = DependencyBacktracker([], [], aggregation_data=[agg])
        assert "Design.plant.solar_battery_plant.total_capex" in bt._aggregation_output_index

    def test_no_aliases_no_extra_keys(self):
        """Aggregation with no aliases only has original 3 keys."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_battery_plant",
        )
        # No aliases set (default empty list)

        bt = DependencyBacktracker([], [], aggregation_data=[agg])
        assert "total_capex" not in bt._aggregation_output_index

    def test_sanitized_partdef_name_in_fallback(self):
        """:: fallback sanitizes PartDef names ('Solar Battery Plant' → 'solar_battery_plant')."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_battery_plant",
        )
        agg.expression.aliases = ["total_capex"]

        usage = _make_calc_usage(
            "annualized_financial",
            "AnnualizedFinancial",
            bindings=[
                BindingInfo(
                    param_name="total_capex",
                    source_path="Solar Battery Plant::total_capex",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
            qualified_name="Pkg__Part__annualized_financial",
        )

        calc_def = SimpleCalcDef(
            name="AnnualizedFinancial",
            qualified_name="Lib__AnnualizedFinancial",
            output_attributes=[SimpleAttrInfo("lcoe")],
        )

        bt = DependencyBacktracker(
            [usage],
            [calc_def],
            aggregation_data=[agg],
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__annualized_financial|total_capex"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
