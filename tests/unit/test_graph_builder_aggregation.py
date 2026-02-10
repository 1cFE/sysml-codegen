"""Unit tests for graph builder aggregation module support (Phase 3).

Tests _extend_output_catalog_with_aggregation(), _resolve_aggregation_input_channel(),
_build_aggregation_module(), and topological ordering with aggregation modules.
"""

from sysml_codegen.core.identifier_types import derive_module_type
from sysml_codegen.core.qualified_names import get_channel_name, get_module_name
from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    LocalTerm,
    RedefinitionData,
    RedefinitionType,
    ScopedAggregationData,
    SingletonTerm,
    SumTerm,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.resolution.graph_builder import (
    _build_aggregation_module,
    _extend_output_catalog_with_aggregation,
    _resolve_aggregation_input_channel,
    _unified_topological_sort,
)
from sysml_codegen.resolution.models import (
    EntryPoint,
    EntryPointType,
    InputSource,
    ModuleInput,
    ModuleOutput,
    PipelineModule,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_scoped_agg(
    attribute_name: str = "capital_cost",
    owning_part_qn: str = "Lib__Solar_Array",
    owning_part_name: str = "Solar_Array",
    instance_path: str = "Design__plant__solar_array",
    sum_terms: list[SumTerm] | None = None,
    singleton_terms: list[SingletonTerm] | None = None,
    local_terms: list[LocalTerm] | None = None,
    transformed_expression: str = "module_count * pv_module_capital_cost",
    has_unsupported_nodes: bool = False,
    input_channels: list[str] | None = None,
    entry_points_list: list[str] | None = None,
) -> ScopedAggregationData:
    expr = AggregationExpressionData(
        owning_part_qn=owning_part_qn,
        owning_part_name=owning_part_name,
        attribute_name=attribute_name,
        raw_expression_text="sum(...)",
        transformed_expression=transformed_expression,
        sum_terms=sum_terms or [],
        singleton_terms=singleton_terms or [],
        local_terms=local_terms or [],
        input_channels=input_channels or [],
        entry_points=entry_points_list or [],
        has_unsupported_nodes=has_unsupported_nodes,
    )
    return ScopedAggregationData(expression=expr, instance_path=instance_path)


def _make_chain_redef(
    attribute_name: str,
    source_path: str,
    owning_part_qn: str,
) -> RedefinitionData:
    return RedefinitionData(
        owning_part_qn=owning_part_qn,
        attribute_name=attribute_name,
        redefinition_type=RedefinitionType.CHAIN,
        source_path=source_path,
    )


# ---------------------------------------------------------------------------
# TestExtendOutputCatalogWithAggregation
# ---------------------------------------------------------------------------


class TestExtendOutputCatalogWithAggregation:
    def test_adds_catalog_entry_with_correct_key(self):
        """Output catalog keyed by 'part_name.attribute_name'."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_array",
        )
        catalog: dict[str, tuple[str, str, str]] = {}
        _extend_output_catalog_with_aggregation(catalog, [agg])

        assert "solar_array.capital_cost" in catalog

    def test_channel_name_follows_pqn_format(self):
        """Channel is module_eqn__attribute_name."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_array",
        )
        catalog: dict[str, tuple[str, str, str]] = {}
        _extend_output_catalog_with_aggregation(catalog, [agg])

        _, channel, field = catalog["solar_array.capital_cost"]
        assert channel == "Design__plant__solar_array__capital_cost__capital_cost"
        assert field == "root"

    def test_multiple_aggregations(self):
        """Multiple aggregation expressions each get catalog entry."""
        agg1 = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_array",
        )
        agg2 = _make_scoped_agg(
            attribute_name="capital_cost",
            owning_part_qn="Lib__Battery_System",
            owning_part_name="Battery_System",
            instance_path="Design__plant__battery_system",
        )
        catalog: dict[str, tuple[str, str, str]] = {}
        _extend_output_catalog_with_aggregation(catalog, [agg1, agg2])

        assert "solar_array.capital_cost" in catalog
        assert "battery_system.capital_cost" in catalog

    def test_same_attr_name_different_parts_disambiguated(self):
        """Two PartDefs with same attribute_name produce distinct channels."""
        agg1 = _make_scoped_agg(
            attribute_name="capital_cost",
            owning_part_qn="Lib__Solar_Array",
            owning_part_name="Solar_Array",
            instance_path="Design__plant__solar_array",
        )
        agg2 = _make_scoped_agg(
            attribute_name="capital_cost",
            owning_part_qn="Lib__Battery_System",
            owning_part_name="Battery_System",
            instance_path="Design__plant__battery_system",
        )
        catalog: dict[str, tuple[str, str, str]] = {}
        _extend_output_catalog_with_aggregation(catalog, [agg1, agg2])

        _, ch1, _ = catalog["solar_array.capital_cost"]
        _, ch2, _ = catalog["battery_system.capital_cost"]
        assert ch1 != ch2
        assert "solar_array" in ch1
        assert "battery_system" in ch2

    def test_empty_list(self):
        """Empty aggregation list produces no catalog entries."""
        catalog: dict[str, tuple[str, str, str]] = {}
        _extend_output_catalog_with_aggregation(catalog, [])
        assert catalog == {}


# ---------------------------------------------------------------------------
# TestResolveAggregationInputChannel
# ---------------------------------------------------------------------------


class TestResolveAggregationInputChannel:
    def test_chain_resolves_to_virtual_calc_channel(self):
        """'pv_module.capital_cost' -> CHAIN ':>> capital_cost = cost_model.total_cost'
        -> channel 'instance__pv_module__cost_model__total_cost'."""
        redefs = [
            _make_chain_redef("capital_cost", "cost_model.total_cost", "Lib__PV_Module")
        ]
        expected_channel = get_channel_name(
            "Design__plant__solar_array__pv_module__cost_model", "total_cost"
        )
        # Catalog must contain the channel for verification
        catalog: dict[str, tuple[str, str, str]] = {
            "cost_model.total_cost": ("CostModelModule", expected_channel, "root"),
        }
        result = _resolve_aggregation_input_channel(
            "pv_module.capital_cost",
            "Design__plant__solar_array",
            redefs,
            catalog,
        )
        assert result == expected_channel

    def test_agg_to_agg_falls_back_to_catalog(self):
        """'solar_array.capital_cost' with no CHAIN -> falls back to catalog."""
        agg_channel = "Design__plant__solar_array__capital_cost__capital_cost"
        catalog: dict[str, tuple[str, str, str]] = {
            "solar_array.capital_cost": ("AggType", agg_channel, "root"),
        }
        result = _resolve_aggregation_input_channel(
            "solar_array.capital_cost",
            "Design__plant",
            [],  # No redefinitions
            catalog,
        )
        assert result == agg_channel

    def test_circular_chain_returns_none(self):
        """Circular ':>> a.x -> b.y -> a.x' returns None."""
        redefs = [
            _make_chain_redef("x", "b.y", "Lib__A"),
            _make_chain_redef("y", "a.x", "Lib__B"),
        ]
        result = _resolve_aggregation_input_channel(
            "a.x",
            "instance",
            redefs,
            {},
        )
        assert result is None

    def test_no_match_returns_none(self):
        """No matching redef and no catalog entry returns None."""
        result = _resolve_aggregation_input_channel(
            "unknown.attr",
            "instance",
            [],
            {},
        )
        assert result is None

    def test_local_ref_returns_none(self):
        """No dot in symbolic ref returns None (local term)."""
        result = _resolve_aggregation_input_channel(
            "misc_cost",
            "instance",
            [],
            {},
        )
        assert result is None

    def test_chain_source_not_in_catalog_recurses(self):
        """If chain source channel not in catalog, recurse following the chain."""
        redefs = [
            _make_chain_redef("cost", "intermediate.value", "Lib__PV_Module"),
            _make_chain_redef("value", "calc.output", "Lib__Intermediate"),
        ]
        expected_channel = get_channel_name(
            "inst__intermediate__calc", "output"
        )
        catalog: dict[str, tuple[str, str, str]] = {
            "calc.output": ("CalcModule", expected_channel, "root"),
        }
        result = _resolve_aggregation_input_channel(
            "pv_module.cost",
            "inst",
            redefs,
            catalog,
        )
        assert result == expected_channel


# ---------------------------------------------------------------------------
# TestBuildAggregationModule
# ---------------------------------------------------------------------------


class TestBuildAggregationModule:
    def test_sum_term_wires_to_module_output(self):
        """SumTerm produces ModuleInput wired to resolved channel."""
        agg = _make_scoped_agg(
            sum_terms=[SumTerm("pv_module", "capital_cost", "module_count", 20)],
            instance_path="Design__plant__solar_array",
        )
        expected_channel = get_channel_name(
            "Design__plant__solar_array__pv_module__cost_model", "total_cost"
        )
        redefs = [
            _make_chain_redef("capital_cost", "cost_model.total_cost", "Lib__PV_Module")
        ]
        catalog: dict[str, tuple[str, str, str]] = {
            "cost_model.total_cost": ("CostModelModule", expected_channel, "root"),
        }
        entry_points: dict[str, EntryPoint] = {}

        module = _build_aggregation_module(agg, redefs, catalog, entry_points, None)

        cost_inputs = [i for i in module.inputs if i.param_name == "pv_module_capital_cost"]
        assert len(cost_inputs) == 1
        assert cost_inputs[0].source.source_type == "module_output"
        assert cost_inputs[0].source.producer_channel == expected_channel
        assert cost_inputs[0].python_type == "float"

    def test_multiplicity_creates_int_entry_point(self):
        """SumTerm.multiplicity_attr becomes DESIGN_ATTRIBUTE entry point with int type."""
        agg = _make_scoped_agg(
            sum_terms=[SumTerm("pv_module", "capital_cost", "module_count", 20)],
            instance_path="Design__plant__solar_array",
        )
        expected_channel = get_channel_name(
            "Design__plant__solar_array__pv_module__cost_model", "total_cost"
        )
        redefs = [
            _make_chain_redef("capital_cost", "cost_model.total_cost", "Lib__PV_Module")
        ]
        catalog: dict[str, tuple[str, str, str]] = {
            "cost_model.total_cost": ("CostModelModule", expected_channel, "root"),
        }
        entry_points: dict[str, EntryPoint] = {}

        module = _build_aggregation_module(agg, redefs, catalog, entry_points, None)

        mult_inputs = [i for i in module.inputs if i.param_name == "module_count"]
        assert len(mult_inputs) == 1
        assert mult_inputs[0].python_type == "int"
        assert mult_inputs[0].source.source_type == "entry_point"

        ep_qn = "Design__plant__solar_array__module_count"
        assert ep_qn in entry_points
        assert entry_points[ep_qn].entry_type == EntryPointType.DESIGN_ATTRIBUTE
        assert entry_points[ep_qn].default_value == 20.0

    def test_sum_term_no_multiplicity(self):
        """SumTerm without multiplicity_attr creates no multiplicity input."""
        agg = _make_scoped_agg(
            sum_terms=[SumTerm("pv_module", "capital_cost", None, None)],
            instance_path="Design__plant__solar_array",
        )
        expected_channel = get_channel_name(
            "Design__plant__solar_array__pv_module__cost_model", "total_cost"
        )
        redefs = [
            _make_chain_redef("capital_cost", "cost_model.total_cost", "Lib__PV_Module")
        ]
        catalog: dict[str, tuple[str, str, str]] = {
            "cost_model.total_cost": ("CostModelModule", expected_channel, "root"),
        }
        entry_points: dict[str, EntryPoint] = {}

        module = _build_aggregation_module(agg, redefs, catalog, entry_points, None)

        # Only cost input, no multiplicity
        assert len(module.inputs) == 1
        assert module.inputs[0].param_name == "pv_module_capital_cost"

    def test_singleton_term_direct_channel(self):
        """SingletonTerm resolved to direct channel from catalog."""
        singleton_channel = get_channel_name(
            "Design__plant__solar_array__allocation_model", "total_allocation"
        )
        agg = _make_scoped_agg(
            singleton_terms=[SingletonTerm("allocation_model.total_allocation")],
            instance_path="Design__plant__solar_array",
            sum_terms=[],
        )
        catalog: dict[str, tuple[str, str, str]] = {
            "some_key": ("Type", singleton_channel, "root"),
        }
        entry_points: dict[str, EntryPoint] = {}

        module = _build_aggregation_module(agg, [], catalog, entry_points, None)

        singleton_inputs = [i for i in module.inputs if "allocation" in i.param_name]
        assert len(singleton_inputs) == 1
        assert singleton_inputs[0].source.source_type == "module_output"
        assert singleton_inputs[0].source.producer_channel == singleton_channel
        assert singleton_inputs[0].param_name == "allocation_model_total_allocation"

    def test_singleton_term_fallback_to_chain_resolution(self):
        """SingletonTerm falls back to _resolve_aggregation_input_channel when direct fails."""
        # Direct channel won't match, but chain resolution will
        resolved_channel = get_channel_name(
            "Design__plant__solar_array__pv_module__cost_model", "total_cost"
        )
        agg = _make_scoped_agg(
            singleton_terms=[SingletonTerm("pv_module.capital_cost")],
            instance_path="Design__plant__solar_array",
            sum_terms=[],
        )
        redefs = [
            _make_chain_redef("capital_cost", "cost_model.total_cost", "Lib__PV_Module")
        ]
        catalog: dict[str, tuple[str, str, str]] = {
            "cost_model.total_cost": ("CostModelModule", resolved_channel, "root"),
        }
        entry_points: dict[str, EntryPoint] = {}

        module = _build_aggregation_module(agg, redefs, catalog, entry_points, None)

        inputs = [i for i in module.inputs if "capital_cost" in i.param_name]
        assert len(inputs) == 1
        assert inputs[0].source.source_type == "module_output"
        assert inputs[0].source.producer_channel == resolved_channel

    def test_local_term_creates_entry_point(self):
        """LocalTerm becomes DESIGN_ATTRIBUTE entry point."""
        agg = _make_scoped_agg(
            local_terms=[LocalTerm("misc_hardware_cost")],
            instance_path="Design__plant__solar_array",
            sum_terms=[],
        )
        entry_points: dict[str, EntryPoint] = {}

        module = _build_aggregation_module(agg, [], {}, entry_points, None)

        local_inputs = [i for i in module.inputs if i.param_name == "misc_hardware_cost"]
        assert len(local_inputs) == 1
        assert local_inputs[0].source.source_type == "entry_point"

        ep_qn = "Design__plant__solar_array__capital_cost__misc_hardware_cost"
        assert ep_qn in entry_points
        assert entry_points[ep_qn].entry_type == EntryPointType.DESIGN_ATTRIBUTE

    def test_unsupported_nodes_manual_required(self):
        """has_unsupported_nodes=True -> Compilability.MANUAL_REQUIRED."""
        agg = _make_scoped_agg(has_unsupported_nodes=True, sum_terms=[])
        module = _build_aggregation_module(agg, [], {}, {}, None)
        assert module.compilability == Compilability.MANUAL_REQUIRED

    def test_module_is_aggregation_true(self):
        """PipelineModule.is_aggregation == True."""
        agg = _make_scoped_agg(sum_terms=[])
        module = _build_aggregation_module(agg, [], {}, {}, None)
        assert module.is_aggregation is True
        assert module.is_computed_attribute is False

    def test_module_naming(self):
        """Module name and type follow ADR-003."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            owning_part_qn="Lib__Solar_Array",
            instance_path="Design__plant__solar_array",
            sum_terms=[],
        )
        module = _build_aggregation_module(agg, [], {}, {}, None)

        expected_eqn = "Design__plant__solar_array__capital_cost"
        assert module.name == get_module_name(expected_eqn)
        assert module.module_type == derive_module_type("Lib__Solar_Array::capital_cost")

    def test_output_channel(self):
        """Output channel follows PQN format."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_array",
            sum_terms=[],
        )
        module = _build_aggregation_module(agg, [], {}, {}, None)

        assert len(module.outputs) == 1
        assert module.outputs[0].field_name == "root"
        assert module.outputs[0].channel_name == get_channel_name(
            "Design__plant__solar_array__capital_cost", "capital_cost"
        )

    def test_unresolvable_sum_term_creates_entry_point(self):
        """SumTerm with no matching chain/catalog becomes entry point + MANUAL_REQUIRED."""
        agg = _make_scoped_agg(
            sum_terms=[SumTerm("unknown_part", "cost", None, None)],
            instance_path="Design__plant__solar_array",
        )
        entry_points: dict[str, EntryPoint] = {}

        module = _build_aggregation_module(agg, [], {}, entry_points, None)

        cost_inputs = [i for i in module.inputs if i.param_name == "unknown_part_cost"]
        assert len(cost_inputs) == 1
        assert cost_inputs[0].source.source_type == "entry_point"
        assert module.compilability == Compilability.MANUAL_REQUIRED


# ---------------------------------------------------------------------------
# TestTopologicalOrderWithAggregation
# ---------------------------------------------------------------------------


class TestTopologicalOrderWithAggregation:
    def test_leaf_before_aggregation_before_system(self):
        """Unified toposort: leaf CalcUsage < aggregation < system CalcUsage."""
        leaf_channel = "leaf__cost__total_cost"
        agg_channel = "agg__capital_cost__capital_cost"

        leaf_module = PipelineModule(
            name="leaf__cost",
            module_type="CostModule",
            inputs=[],
            outputs=[
                ModuleOutput(
                    field_name="root", python_type="float", channel_name=leaf_channel
                )
            ],
            execution_order=0,
        )
        agg_module = PipelineModule(
            name="agg__capital_cost",
            module_type="CapitalCostModule",
            inputs=[
                ModuleInput(
                    param_name="child_cost",
                    python_type="float",
                    source=InputSource(
                        source_type="module_output", producer_channel=leaf_channel
                    ),
                ),
            ],
            outputs=[
                ModuleOutput(
                    field_name="root", python_type="float", channel_name=agg_channel
                )
            ],
            execution_order=0,
            is_aggregation=True,
        )
        system_module = PipelineModule(
            name="system__financial",
            module_type="FinancialModule",
            inputs=[
                ModuleInput(
                    param_name="total_capex",
                    python_type="float",
                    source=InputSource(
                        source_type="module_output", producer_channel=agg_channel
                    ),
                ),
            ],
            outputs=[
                ModuleOutput(
                    field_name="root",
                    python_type="float",
                    channel_name="system__financial__lcoe",
                )
            ],
            execution_order=0,
        )

        # Pass in reverse order to verify sort works
        sorted_modules = _unified_topological_sort(
            [system_module, agg_module, leaf_module]
        )
        names = [m.name for m in sorted_modules]
        assert names.index("leaf__cost") < names.index("agg__capital_cost")
        assert names.index("agg__capital_cost") < names.index("system__financial")

    def test_execution_order_reassigned(self):
        """execution_order fields are reassigned after sort."""
        m1 = PipelineModule(
            name="m1",
            module_type="T1",
            inputs=[],
            outputs=[
                ModuleOutput(
                    field_name="root", python_type="float", channel_name="m1__out"
                )
            ],
            execution_order=99,
        )
        m2 = PipelineModule(
            name="m2",
            module_type="T2",
            inputs=[
                ModuleInput(
                    param_name="x",
                    python_type="float",
                    source=InputSource(
                        source_type="module_output", producer_channel="m1__out"
                    ),
                ),
            ],
            outputs=[
                ModuleOutput(
                    field_name="root", python_type="float", channel_name="m2__out"
                )
            ],
            execution_order=99,
            is_aggregation=True,
        )

        sorted_modules = _unified_topological_sort([m2, m1])

        assert sorted_modules[0].name == "m1"
        assert sorted_modules[0].execution_order == 0
        assert sorted_modules[1].name == "m2"
        assert sorted_modules[1].execution_order == 1
