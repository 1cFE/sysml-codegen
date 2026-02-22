"""Unit tests for graph builder aggregation module support (Phase 3 & 4).

Tests _resolve_aggregation_input_channel(),
_build_aggregation_module(), topological ordering with aggregation modules,
orphan entry point surfacing (BF-8), and expression compilation (BF-2).
"""

import ast
from pathlib import Path

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
from sysml_codegen.core.output_registry import OutputRegistry
from tests.helpers.registry_compat import registry_register
from sysml_codegen.resolution.graph_builder import (
    _build_aggregation_module,
    _resolve_aggregation_input_channel,
    _unified_topological_sort,
)
from sysml_codegen.resolution.models import (
    EntryPoint,
    EntryPointType,
    InputSource,
    ModuleInput,
    ModuleOutput,
    ParameterGroup,
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
        # Registry must contain the channel as canonical for verification
        registry = OutputRegistry()
        registry_register(registry,expected_channel, ["cost_model.total_cost"])
        result = _resolve_aggregation_input_channel(
            "pv_module.capital_cost",
            "Design__plant__solar_array",
            redefs,
            registry,
        )
        assert result == expected_channel

    def test_agg_to_agg_falls_back_to_registry(self):
        """'solar_array.capital_cost' with no CHAIN -> falls back to registry resolve."""
        agg_channel = "Design__plant__solar_array__capital_cost__capital_cost"
        registry = OutputRegistry()
        registry_register(registry,agg_channel, ["solar_array.capital_cost"])
        result = _resolve_aggregation_input_channel(
            "solar_array.capital_cost",
            "Design__plant",
            [],  # No redefinitions
            registry,
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
            OutputRegistry(),
        )
        assert result is None

    def test_no_match_returns_none(self):
        """No matching redef and no registry entry returns None."""
        result = _resolve_aggregation_input_channel(
            "unknown.attr",
            "instance",
            [],
            OutputRegistry(),
        )
        assert result is None

    def test_local_ref_returns_none(self):
        """No dot in symbolic ref returns None (local term)."""
        result = _resolve_aggregation_input_channel(
            "misc_cost",
            "instance",
            [],
            OutputRegistry(),
        )
        assert result is None

    def test_chain_source_not_in_registry_recurses(self):
        """If chain source channel not in registry, recurse following the chain."""
        redefs = [
            _make_chain_redef("cost", "intermediate.value", "Lib__PV_Module"),
            _make_chain_redef("value", "calc.output", "Lib__Intermediate"),
        ]
        expected_channel = get_channel_name(
            "inst__intermediate__calc", "output"
        )
        registry = OutputRegistry()
        registry_register(registry,expected_channel, ["calc.output"])
        result = _resolve_aggregation_input_channel(
            "pv_module.cost",
            "inst",
            redefs,
            registry,
        )
        assert result == expected_channel

    def test_scoped_registry_resolves_when_chain_fails(self):
        """Scoped key resolves when no CHAIN redef exists (AC-2)."""
        expected_channel = get_channel_name(
            "Design__plant__array__pv_module__cost_model", "total_cost"
        )
        registry = OutputRegistry()
        registry_register(registry,expected_channel, [])
        registry.register_alias(
            "plant.array.pv_module.capital_cost", expected_channel
        )
        result = _resolve_aggregation_input_channel(
            "pv_module.capital_cost",
            "Design__plant__array",
            [],
            registry,
        )
        assert result == expected_channel

    def test_scoped_registry_resolves_chain_part_mismatch(self):
        """Scoped key resolves when CHAIN fails due to PartDef/PartUsage name mismatch (AC-2)."""
        expected_channel = get_channel_name(
            "Design__plant__array__inverter__cost_model", "total_cost"
        )
        registry = OutputRegistry()
        registry_register(registry,expected_channel, [])
        registry.register_alias(
            "plant.array.inverter.capital_cost", expected_channel
        )
        # CHAIN redef on String_Inverter won't match "inverter" via sanitize_name
        redefs = [
            _make_chain_redef(
                "capital_cost", "cost_model.total_cost", "Lib__String_Inverter"
            )
        ]
        result = _resolve_aggregation_input_channel(
            "inverter.capital_cost",
            "Design__plant__array",
            redefs,
            registry,
        )
        assert result == expected_channel

    def test_scoped_before_unscoped_avoids_collision(self):
        """Scoped key wins over colliding Key_D (AC-7)."""
        correct_channel = "Design__plant__array__child__calc__cost"
        wrong_channel = "Design__other__child__calc__cost"
        registry = OutputRegistry()
        registry_register(registry,correct_channel, [])
        registry_register(registry,wrong_channel, ["child.cost"])  # Key_D collision
        registry.register_alias(
            "plant.array.child.cost", correct_channel
        )  # scoped
        result = _resolve_aggregation_input_channel(
            "child.cost",
            "Design__plant__array",
            [],
            registry,
        )
        assert result == correct_channel

    def test_agg_to_agg_via_key_e_stripped(self):
        """Plant-level resolves sub-assembly agg via Key_E_stripped (AC-3, AC-6)."""
        agg_channel = "Design__plant__array__capital_cost__capital_cost"
        registry = OutputRegistry()
        # Key_E_stripped: "plant.array.capital_cost" (registered by Change 2)
        registry_register(registry,agg_channel, ["plant.array.capital_cost"])
        result = _resolve_aggregation_input_channel(
            "array.capital_cost",
            "Design__plant",
            [],
            registry,
        )
        assert result == agg_channel


# ---------------------------------------------------------------------------
# TestBuildAggregationModule
# ---------------------------------------------------------------------------


class TestBuildAggregationModule:
    def _make_registry(self, entries: dict[str, list[str]] | None = None) -> OutputRegistry:
        """Build an OutputRegistry from {canonical_channel: [alias_keys]}."""
        registry = OutputRegistry()
        for channel, keys in (entries or {}).items():
            registry_register(registry,channel, keys)
        return registry

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
        registry = self._make_registry({expected_channel: ["cost_model.total_cost"]})
        entry_points: dict[str, EntryPoint] = {}

        module, _new_eps = _build_aggregation_module(agg, redefs, registry, entry_points, None)

        cost_inputs = [i for i in module.inputs if i.param_name == "pv_module_capital_cost"]
        assert len(cost_inputs) == 1
        assert cost_inputs[0].source.source_type == "module_output"
        assert cost_inputs[0].source.producer_channel == expected_channel
        assert cost_inputs[0].python_type == "float"

    def test_multiplicity_creates_float_entry_point(self):
        """SumTerm.multiplicity_attr becomes DESIGN_ATTRIBUTE entry point with float type."""
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
        registry = self._make_registry({expected_channel: ["cost_model.total_cost"]})
        entry_points: dict[str, EntryPoint] = {}

        module, _new_eps = _build_aggregation_module(agg, redefs, registry, entry_points, None)
        entry_points.update(_new_eps)

        mult_inputs = [i for i in module.inputs if i.param_name == "module_count"]
        assert len(mult_inputs) == 1
        assert mult_inputs[0].python_type == "float"
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
        registry = self._make_registry({expected_channel: ["cost_model.total_cost"]})
        entry_points: dict[str, EntryPoint] = {}

        module, _new_eps = _build_aggregation_module(agg, redefs, registry, entry_points, None)

        # Only cost input, no multiplicity
        assert len(module.inputs) == 1
        assert module.inputs[0].param_name == "pv_module_capital_cost"

    def test_singleton_term_direct_channel(self):
        """SingletonTerm resolved to direct channel from registry."""
        singleton_channel = get_channel_name(
            "Design__plant__solar_array__allocation_model", "total_allocation"
        )
        agg = _make_scoped_agg(
            singleton_terms=[SingletonTerm("allocation_model.total_allocation")],
            instance_path="Design__plant__solar_array",
            sum_terms=[],
        )
        # Register the channel as canonical so `channel in canonical_channels` passes
        registry = self._make_registry({singleton_channel: []})
        entry_points: dict[str, EntryPoint] = {}

        module, _new_eps = _build_aggregation_module(agg, [], registry, entry_points, None)

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
        registry = self._make_registry({resolved_channel: ["cost_model.total_cost"]})
        entry_points: dict[str, EntryPoint] = {}

        module, _new_eps = _build_aggregation_module(agg, redefs, registry, entry_points, None)

        inputs = [i for i in module.inputs if "capital_cost" in i.param_name]
        assert len(inputs) == 1
        assert inputs[0].source.source_type == "module_output"
        assert inputs[0].source.producer_channel == resolved_channel

    def test_singleton_term_registry_first_for_aggregation_target(self):
        """SingletonTerm resolves aggregation output via registry-first (AC-5)."""
        # Aggregation output has double-attr channel format
        agg_channel = "Design__plant__array__cost__cost"
        agg = _make_scoped_agg(
            singleton_terms=[SingletonTerm("array.cost")],
            instance_path="Design__plant",
            sum_terms=[],
        )
        registry = self._make_registry({agg_channel: ["plant.array.cost"]})
        entry_points: dict[str, EntryPoint] = {}
        module, _new_eps = _build_aggregation_module(agg, [], registry, entry_points, None)
        singleton_inputs = [i for i in module.inputs if "cost" in i.param_name]
        assert len(singleton_inputs) == 1
        assert singleton_inputs[0].source.source_type == "module_output"
        assert singleton_inputs[0].source.producer_channel == agg_channel

    def test_sum_term_scoped_resolution_no_chain(self):
        """SumTerm resolves via scoped registry when no CHAIN exists (AC-2)."""
        expected_channel = get_channel_name(
            "Design__plant__array__pv_module__cost_model", "total_cost"
        )
        agg = _make_scoped_agg(
            sum_terms=[SumTerm("pv_module", "capital_cost", None, None)],
            instance_path="Design__plant__array",
        )
        registry = self._make_registry({expected_channel: []})
        # Register scoped alias (as Phase 2 CHAIN alias registration would)
        registry.register_alias("plant.array.pv_module.capital_cost", expected_channel)
        entry_points: dict[str, EntryPoint] = {}
        module, _new_eps = _build_aggregation_module(agg, [], registry, entry_points, None)
        cost_inputs = [i for i in module.inputs if i.param_name == "pv_module_capital_cost"]
        assert len(cost_inputs) == 1
        assert cost_inputs[0].source.source_type == "module_output"
        assert cost_inputs[0].source.producer_channel == expected_channel

    def test_local_term_creates_entry_point(self):
        """LocalTerm becomes DESIGN_ATTRIBUTE entry point."""
        agg = _make_scoped_agg(
            local_terms=[LocalTerm("misc_hardware_cost")],
            instance_path="Design__plant__solar_array",
            sum_terms=[],
        )
        entry_points: dict[str, EntryPoint] = {}

        module, _new_eps = _build_aggregation_module(agg, [], OutputRegistry(), entry_points, None)
        entry_points.update(_new_eps)

        local_inputs = [i for i in module.inputs if i.param_name == "misc_hardware_cost"]
        assert len(local_inputs) == 1
        assert local_inputs[0].source.source_type == "entry_point"

        ep_qn = "Design__plant__solar_array__capital_cost__misc_hardware_cost"
        assert ep_qn in entry_points
        assert entry_points[ep_qn].entry_type == EntryPointType.DESIGN_ATTRIBUTE

    def test_unsupported_nodes_manual_required(self):
        """has_unsupported_nodes=True -> Compilability.MANUAL_REQUIRED."""
        agg = _make_scoped_agg(has_unsupported_nodes=True, sum_terms=[])
        module, _new_eps = _build_aggregation_module(agg, [], OutputRegistry(), {}, None)
        assert module.compilability == Compilability.MANUAL_REQUIRED

    def test_module_is_aggregation_true(self):
        """PipelineModule.is_aggregation == True."""
        agg = _make_scoped_agg(sum_terms=[])
        module, _new_eps = _build_aggregation_module(agg, [], OutputRegistry(), {}, None)
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
        module, _new_eps = _build_aggregation_module(agg, [], OutputRegistry(), {}, None)

        expected_eqn = "Design__plant__solar_array__capital_cost"
        assert module.name == get_module_name(expected_eqn)
        assert module.module_type == derive_module_type("Design::plant::solar_array::capital_cost")

    def test_output_channel(self):
        """Output channel follows PQN format."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_array",
            sum_terms=[],
        )
        module, _new_eps = _build_aggregation_module(agg, [], OutputRegistry(), {}, None)

        assert len(module.outputs) == 1
        assert module.outputs[0].field_name == "root"
        assert module.outputs[0].channel_name == get_channel_name(
            "Design__plant__solar_array__capital_cost", "capital_cost"
        )

    def test_unresolvable_sum_term_creates_entry_point(self):
        """SumTerm with no matching chain/registry becomes entry point + MANUAL_REQUIRED."""
        agg = _make_scoped_agg(
            sum_terms=[SumTerm("unknown_part", "cost", None, None)],
            instance_path="Design__plant__solar_array",
        )
        entry_points: dict[str, EntryPoint] = {}

        module, _new_eps = _build_aggregation_module(agg, [], OutputRegistry(), entry_points, None)

        cost_inputs = [i for i in module.inputs if i.param_name == "unknown_part_cost"]
        assert len(cost_inputs) == 1
        assert cost_inputs[0].source.source_type == "entry_point"
        assert module.compilability == Compilability.MANUAL_REQUIRED

    def test_local_term_resolves_to_sibling_agg_output(self):
        """Bug B: LocalTerm resolves to sibling aggregation module output
        via canonical_channels membership check (double-attr channel format)."""
        sibling_channel = get_channel_name(
            "Design__plant__solar_array__capital_cost", "capital_cost"
        )  # → "Design__plant__solar_array__capital_cost__capital_cost"
        agg = _make_scoped_agg(
            local_terms=[LocalTerm("capital_cost")],
            attribute_name="idiot_index",
            instance_path="Design__plant__solar_array",
            sum_terms=[],
            transformed_expression="capital_cost",
        )
        registry = self._make_registry({sibling_channel: []})
        entry_points: dict[str, EntryPoint] = {}

        module, _new_eps = _build_aggregation_module(agg, [], registry, entry_points, None)

        cost_inputs = [i for i in module.inputs if i.param_name == "capital_cost"]
        assert len(cost_inputs) == 1
        assert cost_inputs[0].source.source_type == "module_output"
        assert cost_inputs[0].source.producer_channel == sibling_channel
        # No entry point created for resolved LocalTerm
        assert not any("capital_cost" in k for k in entry_points)

    def test_unresolvable_local_term_still_entry_point(self):
        """Bug B regression guard: LocalTerm with no sibling agg module
        still becomes DESIGN_ATTRIBUTE entry point (e.g., misc_hardware_cost)."""
        agg = _make_scoped_agg(
            local_terms=[LocalTerm("misc_hardware_cost")],
            instance_path="Design__plant__solar_array",
            sum_terms=[],
            transformed_expression="misc_hardware_cost",
        )
        entry_points: dict[str, EntryPoint] = {}

        module, _new_eps = _build_aggregation_module(agg, [], OutputRegistry(), entry_points, None)
        entry_points.update(_new_eps)

        local_inputs = [i for i in module.inputs if i.param_name == "misc_hardware_cost"]
        assert len(local_inputs) == 1
        assert local_inputs[0].source.source_type == "entry_point"

        ep_qn = "Design__plant__solar_array__capital_cost__misc_hardware_cost"
        assert ep_qn in entry_points
        assert entry_points[ep_qn].entry_type == EntryPointType.DESIGN_ATTRIBUTE

    def test_mixed_local_terms_partial_resolution(self):
        """Bug B: Mixed LocalTerms — some resolve to sibling agg outputs,
        some fall back to entry points."""
        cc_channel = get_channel_name(
            "Design__plant__solar_array__capital_cost", "capital_cost"
        )
        rmc_channel = get_channel_name(
            "Design__plant__solar_array__raw_material_cost", "raw_material_cost"
        )
        agg = _make_scoped_agg(
            local_terms=[
                LocalTerm("capital_cost"),
                LocalTerm("raw_material_cost"),
                LocalTerm("misc_hardware_cost"),
            ],
            attribute_name="idiot_index",
            instance_path="Design__plant__solar_array",
            sum_terms=[],
            transformed_expression="capital_cost / raw_material_cost + misc_hardware_cost",
        )
        registry = self._make_registry({cc_channel: [], rmc_channel: []})
        entry_points: dict[str, EntryPoint] = {}

        module, _new_eps = _build_aggregation_module(agg, [], registry, entry_points, None)

        # capital_cost → module_output
        cc_inputs = [i for i in module.inputs if i.param_name == "capital_cost"]
        assert len(cc_inputs) == 1
        assert cc_inputs[0].source.source_type == "module_output"
        assert cc_inputs[0].source.producer_channel == cc_channel

        # raw_material_cost → module_output
        rmc_inputs = [i for i in module.inputs if i.param_name == "raw_material_cost"]
        assert len(rmc_inputs) == 1
        assert rmc_inputs[0].source.source_type == "module_output"
        assert rmc_inputs[0].source.producer_channel == rmc_channel

        # misc_hardware_cost → entry_point (no sibling agg)
        misc_inputs = [i for i in module.inputs if i.param_name == "misc_hardware_cost"]
        assert len(misc_inputs) == 1
        assert misc_inputs[0].source.source_type == "entry_point"


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


# ---------------------------------------------------------------------------
# BF-8: TestOrphanEntryPointsSurfaced
# ---------------------------------------------------------------------------


class TestOrphanEntryPointsSurfaced:
    """BF-8: Orphan entry points (e.g., multiplicity) appear in parameter groups."""

    def _collect_orphans(
        self,
        modules: list[PipelineModule],
        entry_points: dict[str, EntryPoint],
        param_groups: list[ParameterGroup],
    ) -> list[ParameterGroup]:
        """Reproduce the orphan EP collection logic from graph_builder Step 6.6.

        This mirrors the code we're adding to graph_builder.py so we can unit-test
        the logic directly without calling the full build_computation_graph().
        """
        covered_ep_names: set[str] = set()
        for group in param_groups:
            for p in group.parameters:
                covered_ep_names.add(p.qualified_name)

        orphan_eps = {
            qn: ep for qn, ep in entry_points.items()
            if qn not in covered_ep_names
        }

        if orphan_eps:
            ep_type_lookup: dict[str, str] = {}
            for m in modules:
                for inp in m.inputs:
                    if inp.source.source_type == "entry_point" and inp.source.qualified_name:
                        ep_type_lookup[inp.source.qualified_name] = inp.python_type

            orphan_params = []
            for qn, ep in orphan_eps.items():
                orphan_params.append(EntryPoint(
                    qualified_name=qn,
                    simple_name=ep.simple_name,
                    entry_type=ep.entry_type,
                    default_value=ep.default_value,
                    python_type=ep_type_lookup.get(qn, "float"),
                ))
            if orphan_params:
                param_groups.append(ParameterGroup(
                    name="system_design",
                    class_name="SystemDesign",
                    source_file=Path("hierarchy"),
                    parameters=orphan_params,
                ))

        return param_groups

    def test_multiplicity_ep_in_system_design_group(self):
        """module_count entry point appears in 'system_design' parameter group."""
        ep_qn = "Design__plant__solar_array__module_count"
        entry_points = {
            ep_qn: EntryPoint(
                qualified_name=ep_qn,
                simple_name="module_count",
                entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                default_value=20.0,
            ),
        }
        module = PipelineModule(
            name="design__plant__solar_array__capital_cost",
            module_type="CapitalCostModule",
            inputs=[ModuleInput(
                param_name="module_count",
                python_type="float",
                source=InputSource(
                    source_type="entry_point",
                    qualified_name=ep_qn,
                ),
            )],
            outputs=[],
            execution_order=0,
            is_aggregation=True,
        )

        result = self._collect_orphans([module], entry_points, [])

        assert len(result) == 1
        assert result[0].name == "system_design"
        param_names = [p.qualified_name for p in result[0].parameters]
        assert ep_qn in param_names
        # Type should be "float" from ModuleInput.python_type (Bug 10 fix: int→float)
        mc_param = next(p for p in result[0].parameters if p.qualified_name == ep_qn)
        assert mc_param.python_type == "float"

    def test_non_multiplicity_orphan_also_captured(self):
        """Any orphan entry point (not just multiplicity) gets captured."""
        ep_qn = "Design__plant__solar_array__capital_cost__misc_hardware_cost"
        entry_points = {
            ep_qn: EntryPoint(
                qualified_name=ep_qn,
                simple_name="misc_hardware_cost",
                entry_type=EntryPointType.DESIGN_ATTRIBUTE,
            ),
        }
        module = PipelineModule(
            name="design__plant__solar_array__capital_cost",
            module_type="CapitalCostModule",
            inputs=[ModuleInput(
                param_name="misc_hardware_cost",
                python_type="float",
                source=InputSource(
                    source_type="entry_point",
                    qualified_name=ep_qn,
                ),
            )],
            outputs=[],
            execution_order=0,
            is_aggregation=True,
        )

        result = self._collect_orphans([module], entry_points, [])

        assert len(result) == 1
        param_names = [p.qualified_name for p in result[0].parameters]
        assert ep_qn in param_names

    def test_covered_ep_not_orphaned(self):
        """Entry point already in a param group is NOT collected as orphan."""
        ep_qn = "SomeCalc__param__x"
        ep = EntryPoint(
            qualified_name=ep_qn,
            simple_name="x",
            entry_type=EntryPointType.LIBRARY_DEFAULT,
            default_value=1.0,
        )
        entry_points = {ep_qn: ep}
        existing_group = ParameterGroup(
            name="existing_group",
            class_name="ExistingGroup",
            source_file=Path("existing.sysml"),
            parameters=[ep],
        )

        result = self._collect_orphans([], entry_points, [existing_group])

        # No synthetic group created; only the existing group
        assert len(result) == 1
        assert result[0].name == "existing_group"

    def test_mixed_covered_and_orphan(self):
        """Covered EPs stay in existing groups; orphans go to system_design."""
        covered_ep_qn = "SomeCalc__param__x"
        orphan_ep_qn = "Design__plant__solar_array__module_count"
        covered_ep = EntryPoint(
            qualified_name=covered_ep_qn,
            simple_name="x",
            entry_type=EntryPointType.LIBRARY_DEFAULT,
            default_value=1.0,
        )
        orphan_ep = EntryPoint(
            qualified_name=orphan_ep_qn,
            simple_name="module_count",
            entry_type=EntryPointType.DESIGN_ATTRIBUTE,
            default_value=20.0,
        )
        entry_points = {covered_ep_qn: covered_ep, orphan_ep_qn: orphan_ep}
        existing_group = ParameterGroup(
            name="existing",
            class_name="Existing",
            source_file=Path("existing.sysml"),
            parameters=[covered_ep],
        )
        module = PipelineModule(
            name="agg_module",
            module_type="AggModule",
            inputs=[ModuleInput(
                param_name="module_count",
                python_type="float",
                source=InputSource(
                    source_type="entry_point",
                    qualified_name=orphan_ep_qn,
                ),
            )],
            outputs=[],
            execution_order=0,
            is_aggregation=True,
        )

        result = self._collect_orphans([module], entry_points, [existing_group])

        assert len(result) == 2
        group_names = [g.name for g in result]
        assert "existing" in group_names
        assert "system_design" in group_names
        sys_group = next(g for g in result if g.name == "system_design")
        assert len(sys_group.parameters) == 1
        assert sys_group.parameters[0].python_type == "float"

    def test_no_orphans_no_synthetic_group(self):
        """When all entry points are covered, no synthetic group is created."""
        ep_qn = "SomeCalc__param__x"
        ep = EntryPoint(
            qualified_name=ep_qn,
            simple_name="x",
            entry_type=EntryPointType.LIBRARY_DEFAULT,
        )
        entry_points = {ep_qn: ep}
        existing_group = ParameterGroup(
            name="existing",
            class_name="Existing",
            source_file=Path("existing.sysml"),
            parameters=[ep],
        )

        result = self._collect_orphans([], entry_points, [existing_group])

        assert len(result) == 1
        assert result[0].name == "existing"


# ---------------------------------------------------------------------------
# BF-2: TestAggregationExpressionCompilation
# ---------------------------------------------------------------------------


class TestAggregationExpressionCompilation:
    """BF-2: Aggregation modules have compiled_expression with inputs.X form."""

    def test_compiled_expression_has_inputs_prefix(self):
        """_build_aggregation_module() produces compiled_expression with inputs.X refs."""
        agg = _make_scoped_agg(
            sum_terms=[SumTerm("pv_module", "capital_cost", "module_count", 20)],
            instance_path="Design__plant__solar_array",
            transformed_expression="module_count * pv_module.capital_cost",
        )
        expected_channel = get_channel_name(
            "Design__plant__solar_array__pv_module__cost_model", "total_cost"
        )
        redefs = [
            _make_chain_redef("capital_cost", "cost_model.total_cost", "Lib__PV_Module")
        ]
        registry = OutputRegistry()
        registry_register(registry,expected_channel, ["cost_model.total_cost"])

        module, _new_eps = _build_aggregation_module(agg, redefs, registry, {}, None)

        assert module.compiled_expression is not None
        assert "inputs.module_count" in module.compiled_expression
        assert "inputs.pv_module_capital_cost" in module.compiled_expression
        # No raw refs should remain
        assert "pv_module.capital_cost" not in module.compiled_expression

    def test_compiled_expression_ast_parses(self):
        """compiled_expression is valid Python (ast.parse succeeds)."""
        agg = _make_scoped_agg(
            sum_terms=[SumTerm("pv_module", "capital_cost", "module_count", 20)],
            instance_path="Design__plant__solar_array",
            transformed_expression="module_count * pv_module.capital_cost",
        )
        expected_channel = get_channel_name(
            "Design__plant__solar_array__pv_module__cost_model", "total_cost"
        )
        redefs = [
            _make_chain_redef("capital_cost", "cost_model.total_cost", "Lib__PV_Module")
        ]
        registry = OutputRegistry()
        registry_register(registry,expected_channel, ["cost_model.total_cost"])

        module, _new_eps = _build_aggregation_module(agg, redefs, registry, {}, None)

        assert module.compiled_expression is not None
        # Should not raise
        ast.parse(module.compiled_expression, mode="eval")

    def test_singleton_term_compiled_correctly(self):
        """Singleton term ref replaced with inputs.X form."""
        agg = _make_scoped_agg(
            sum_terms=[SumTerm("pv_module", "capital_cost", "module_count", 20)],
            singleton_terms=[SingletonTerm("allocation_model.total_allocation")],
            instance_path="Design__plant__solar_array",
            transformed_expression=(
                "module_count * pv_module.capital_cost + allocation_model.total_allocation"
            ),
        )
        # Channel for sum term
        cost_channel = get_channel_name(
            "Design__plant__solar_array__pv_module__cost_model", "total_cost"
        )
        # Channel for singleton (direct)
        alloc_channel = get_channel_name(
            "Design__plant__solar_array__allocation_model", "total_allocation"
        )
        redefs = [
            _make_chain_redef("capital_cost", "cost_model.total_cost", "Lib__PV_Module")
        ]
        registry = OutputRegistry()
        registry_register(registry,cost_channel, ["cost_model.total_cost"])
        registry_register(registry,alloc_channel, [])

        module, _new_eps = _build_aggregation_module(agg, redefs, registry, {}, None)

        assert module.compiled_expression is not None
        assert "inputs.allocation_model_total_allocation" in module.compiled_expression

    def test_local_term_compiled_correctly(self):
        """Local term ref replaced with inputs.X form."""
        agg = _make_scoped_agg(
            sum_terms=[],
            local_terms=[LocalTerm("misc_cost")],
            instance_path="Design__plant__solar_array",
            transformed_expression="misc_cost",
        )

        module, _new_eps = _build_aggregation_module(agg, [], OutputRegistry(), {}, None)

        assert module.compiled_expression is not None
        assert module.compiled_expression == "inputs.misc_cost"

    def test_unsupported_nodes_no_compilation(self):
        """has_unsupported_nodes=True -> compiled_expression is None."""
        agg = _make_scoped_agg(
            has_unsupported_nodes=True,
            sum_terms=[],
            transformed_expression="unknown()",
        )

        module, _new_eps = _build_aggregation_module(agg, [], OutputRegistry(), {}, None)

        assert module.compiled_expression is None

    def test_multi_sum_term_expression(self):
        """Expression with multiple sum terms compiles all refs."""
        agg = _make_scoped_agg(
            sum_terms=[
                SumTerm("pv_module", "capital_cost", "module_count", 20),
                SumTerm("inverter", "cost", "inverter_count", 5),
            ],
            instance_path="Design__plant__solar_array",
            transformed_expression=(
                "module_count * pv_module.capital_cost + inverter_count * inverter.cost"
            ),
        )
        cost_channel = get_channel_name(
            "Design__plant__solar_array__pv_module__cost_model", "total_cost"
        )
        inv_channel = get_channel_name(
            "Design__plant__solar_array__inverter__cost_calc", "cost"
        )
        redefs = [
            _make_chain_redef("capital_cost", "cost_model.total_cost", "Lib__PV_Module"),
            _make_chain_redef("cost", "cost_calc.cost", "Lib__Inverter"),
        ]
        registry = OutputRegistry()
        registry_register(registry,cost_channel, ["cost_model.total_cost"])
        registry_register(registry,inv_channel, ["cost_calc.cost"])

        module, _new_eps = _build_aggregation_module(agg, redefs, registry, {}, None)

        assert module.compiled_expression is not None
        assert "inputs.pv_module_capital_cost" in module.compiled_expression
        assert "inputs.inverter_cost" in module.compiled_expression
        assert "inputs.module_count" in module.compiled_expression
        assert "inputs.inverter_count" in module.compiled_expression
        # Valid Python
        ast.parse(module.compiled_expression, mode="eval")
