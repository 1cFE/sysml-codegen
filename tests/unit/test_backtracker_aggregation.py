"""Unit tests for aggregation output registration and resolution.

Tests OutputRegistry registration of aggregation outputs (category a),
backtracker binding resolution via registry (category b), and integration
behavior (category c).

Migrated from internal index access to OutputRegistry API for Item 4 cut-over.
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
from tests.helpers.registry_compat import registry_resolve


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _build_test_registry(**kwargs):
    """Build OutputRegistry from synthetic test data."""
    from sysml_codegen.orchestration.output_registry_builder import build_output_registry

    return build_output_registry(
        calc_usages=kwargs.get("calc_usages", []),
        calc_defs=kwargs.get("calc_defs", []),
        aggregation_data=kwargs.get("aggregation_data", []),
        computed_attributes=kwargs.get("computed_attributes", []),
        channel_aliases=kwargs.get("channel_aliases", []),
        design_attributes=kwargs.get("design_attributes", {}),
    )


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
# Category (a): Aggregation Output Registration
# ---------------------------------------------------------------------------


class TestAggregationOutputRegistration:
    """Test OutputRegistry registration of aggregation outputs."""

    def test_dotted_reference_resolves(self):
        """Key_E_stripped resolves to aggregation module output channel."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_array",
        )
        registry = _build_test_registry(aggregation_data=[agg])
        # Key_E_stripped: instance_parts[1:] + attr = plant.solar_array.capital_cost
        assert registry_resolve(registry, "plant.solar_array.capital_cost") is not None

    def test_scoped_key_resolves(self):
        """Scoped key resolves with default instance path."""
        agg = _make_scoped_agg(attribute_name="capital_cost")
        registry = _build_test_registry(aggregation_data=[agg])
        # Default instance_path="Design__plant__solar_array"
        assert registry_resolve(registry, "plant.solar_array.capital_cost") is not None

    def test_key_e_stripped_is_only_typed_key(self):
        """Only Key_E_stripped (no design prefix) is registered in typed registry."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_array",
        )
        registry = _build_test_registry(aggregation_data=[agg])
        # Key_E_stripped works
        assert registry_resolve(registry, "plant.solar_array.capital_cost") is not None
        # Full path with design prefix does NOT work (no _compat)
        assert registry_resolve(registry, "Design.plant.solar_array.capital_cost") is None

    def test_channel_name_format(self):
        """Channel follows PQN format: {module_eqn}__{attribute_name}."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_array",
        )
        registry = _build_test_registry(aggregation_data=[agg])
        channel = registry_resolve(registry, "plant.solar_array.capital_cost")
        assert (
            channel
            == "Design__plant__solar_array__capital_cost__capital_cost"
        )

    def test_two_aggregations_each_resolve_via_key_e_stripped(self):
        """Two aggregations with same attribute_name each resolve via their own Key_E_stripped."""
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
        registry = _build_test_registry(aggregation_data=[agg1, agg2])

        # Both Key_E_stripped keys resolve to distinct channels
        ch1 = registry_resolve(registry, "plant.solar_array.capital_cost")
        ch2 = registry_resolve(registry, "plant.battery_system.capital_cost")
        assert ch1 is not None
        assert ch2 is not None
        assert ch1 != ch2

    def test_empty_aggregation_data(self):
        """Empty aggregation_data produces no aggregation registrations."""
        registry = _build_test_registry(aggregation_data=[])
        assert registry_resolve(registry, "plant.solar_array.capital_cost") is None

    def test_none_aggregation_data(self):
        """Default (no aggregation_data) produces no registrations."""
        registry = _build_test_registry()
        assert registry_resolve(registry, "plant.solar_array.capital_cost") is None


# ---------------------------------------------------------------------------
# Category (b): Resolution Tests
# ---------------------------------------------------------------------------


class TestSystemCalcWiresToAggregation:
    """Test backtracker resolution of bindings to aggregation outputs."""

    def test_dotted_binding_resolves_to_module_output(self):
        """System-level CalcUsage with binding source_path='solar_array.capital_cost'
        resolves to MODULE_OUTPUT pointing at aggregation channel.

        Consumer QN 'Design__plant__financial_calc' produces consumer_scope='plant',
        so scoped_lookup tries 'plant.solar_array.capital_cost' which matches
        the Key_E_stripped for instance_path='Design__plant__solar_array'.
        """
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
            qualified_name="Design__plant__financial_calc",
        )

        calc_def = SimpleCalcDef(
            name="FinancialCalc",
            qualified_name="Lib__FinancialCalc",
            output_attributes=[SimpleAttrInfo("lcoe")],
        )

        registry = _build_test_registry(
            aggregation_data=[agg], calc_usages=[usage], calc_defs=[calc_def],
        )
        bt = DependencyBacktracker(
            [usage],
            [calc_def],
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = "Design__plant__financial_calc|total_capex"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
        assert (
            resolution.qualified_name
            == "Design__plant__solar_array__capital_cost__capital_cost"
        )
        assert resolution.source_path == "solar_array.capital_cost"
        assert resolution.is_transitive is False

    def test_direct_key_e_stripped_resolves_for_top_level(self):
        """Direct Key_E_stripped source_path resolves via scoped_lookup (Step 1b).

        source_path='plant.solar_array.capital_cost' is the full Key_E_stripped
        and resolves directly without consumer_scope prefix.
        """
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
                    source_path="plant.solar_array.capital_cost",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
            qualified_name="Design__system_calc",
        )

        calc_def = SimpleCalcDef(
            name="SystemCalc",
            qualified_name="Lib__SystemCalc",
            output_attributes=[SimpleAttrInfo("result")],
        )

        registry = _build_test_registry(
            aggregation_data=[agg], calc_usages=[usage], calc_defs=[calc_def],
        )
        bt = DependencyBacktracker(
            [usage],
            [calc_def],
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = "Design__system_calc|capex"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT

    # test_sysml_qn_reference_normalizes removed — Step 1b normalization is dead code (7.4)

    # -- Category (c): Integration Tests --

    def test_trace_log_contains_aggregation_resolution(self):
        """Trace log records resolution for debugging (checks outcome, not label).

        Consumer QN 'Design__plant__sys_calc' yields consumer_scope='plant',
        so scoped_lookup('plant.solar_array.capital_cost') matches Key_E_stripped.
        """
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
            qualified_name="Design__plant__sys_calc",
        )

        calc_def = SimpleCalcDef(
            name="SysCalc",
            qualified_name="Lib__SysCalc",
            output_attributes=[SimpleAttrInfo("out")],
        )

        registry = _build_test_registry(
            aggregation_data=[agg], calc_usages=[usage], calc_defs=[calc_def],
        )
        bt = DependencyBacktracker(
            [usage],
            [calc_def],
            output_registry=registry,
        )
        result = bt.find_required_modules([], include_all=True)

        # Verify the binding resolved to MODULE_OUTPUT
        key = "Design__plant__sys_calc|cost"
        assert bt._binding_resolutions[key].resolution_type == BindingResolutionType.MODULE_OUTPUT

        # Verify trace log mentions the attribute (resilient to label changes)
        capital_cost_entries = [
            line for line in result.trace_log if "capital_cost" in line.lower()
        ]
        assert len(capital_cost_entries) >= 1

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

        registry = _build_test_registry(
            aggregation_data=[agg], calc_usages=[usage], calc_defs=[calc_def],
        )
        bt = DependencyBacktracker(
            [usage],
            [calc_def],
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__calc|x"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.ENTRY_POINT


# ---------------------------------------------------------------------------
# Category (c): No Aggregation Data (backward compat)
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

        registry = _build_test_registry(
            calc_usages=[usage], calc_defs=[calc_def],
        )
        bt = DependencyBacktracker(
            [usage],
            [calc_def],
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__calc|x"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.ENTRY_POINT

    def test_empty_list_aggregation_data_works(self):
        """aggregation_data=[] produces no registrations."""
        registry = _build_test_registry(aggregation_data=[])
        assert registry_resolve(registry, "plant.solar_array.capital_cost") is None


# ---------------------------------------------------------------------------
# Category (a): BF-7 Aggregation Alias Registration
# ---------------------------------------------------------------------------


class TestAggregationAliasRegistration:
    """BF-7: EXPOSE_PURE aliases registered in OutputRegistry."""

    def test_alias_resolves(self):
        """':>> total_capex = capital_cost' alias resolves to aggregation output."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_battery_plant",
        )
        agg.expression.aliases = ["total_capex"]

        registry = _build_test_registry(aggregation_data=[agg])

        # Both original and alias should resolve via Key_E_stripped
        assert registry_resolve(registry, "plant.solar_battery_plant.capital_cost") is not None
        assert registry_resolve(registry, "plant.solar_battery_plant.total_capex") is not None

    def test_key_e_stripped_alias_resolves(self):
        """Key_E_stripped alias resolves via scoped registry.

        Default instance_path='Design__plant__solar_array' produces
        Key_E_stripped alias 'plant.solar_array.total_capex'.
        """
        agg = _make_scoped_agg(attribute_name="capital_cost")
        agg.expression.aliases = ["total_capex"]

        registry = _build_test_registry(aggregation_data=[agg])
        assert registry_resolve(registry, "plant.solar_array.total_capex") is not None

    def test_alias_channel_matches_original(self):
        """Alias points to the same channel as the original attribute."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_battery_plant",
        )
        agg.expression.aliases = ["total_capex"]

        registry = _build_test_registry(aggregation_data=[agg])
        original_channel = registry_resolve(registry, "plant.solar_battery_plant.capital_cost")
        alias_channel = registry_resolve(registry, "plant.solar_battery_plant.total_capex")
        assert original_channel == alias_channel

    def test_design_prefix_alias_does_not_resolve(self):
        """Full path with Design prefix does NOT resolve (Key_E_stripped strips it)."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_battery_plant",
        )
        agg.expression.aliases = ["total_capex"]

        registry = _build_test_registry(aggregation_data=[agg])
        # Design prefix is stripped — full path should NOT resolve
        assert registry_resolve(registry, "Design.plant.solar_battery_plant.total_capex") is None
        # Key_E_stripped (no Design prefix) SHOULD resolve
        assert registry_resolve(registry, "plant.solar_battery_plant.total_capex") is not None

    def test_no_aliases_no_extra_keys(self):
        """Aggregation with no aliases only has original keys."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_battery_plant",
        )
        # No aliases set (default empty list)

        registry = _build_test_registry(aggregation_data=[agg])
        # Alias key should not resolve when no aliases registered
        assert registry_resolve(registry, "plant.solar_battery_plant.total_capex") is None

    # -- Category (b): Alias resolution through backtracker --

    def test_sanitized_partdef_name_in_reference_dispatch(self):
        """REFERENCE dispatch normalizes 'Solar Battery Plant::total_capex'.

        Step 1b normalizes to 'solar_battery_plant.total_capex', which doesn't
        directly match Key_E_stripped 'plant.solar_battery_plant.total_capex'.
        But Step 2 combines consumer_scope 'plant.solar_battery_plant' with
        leaf 'total_capex', yielding 'plant.solar_battery_plant.total_capex'
        which matches the BF-7 alias in the scoped registry.
        """
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
            qualified_name="Design__plant__solar_battery_plant__annualized_financial",
        )

        calc_def = SimpleCalcDef(
            name="AnnualizedFinancial",
            qualified_name="Lib__AnnualizedFinancial",
            output_attributes=[SimpleAttrInfo("lcoe")],
        )

        registry = _build_test_registry(
            aggregation_data=[agg], calc_usages=[usage], calc_defs=[calc_def],
        )
        bt = DependencyBacktracker(
            [usage],
            [calc_def],
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = "Design__plant__solar_battery_plant__annualized_financial|total_capex"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
