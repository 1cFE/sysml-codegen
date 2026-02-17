"""Unit tests for computed attribute registration and resolution.

Tests OutputRegistry registration of FORMULA computed attributes (category a),
backtracker binding resolution via registry (category b), and integration
behavior (category c).

Migrated from internal index access to OutputRegistry API for Item 4 cut-over.
"""

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from agentic_mbse.sysml.types import BindingType

from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.core.models import BindingResolutionType
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ComputedAttributeData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.usage_extractor import BindingInfo, CalcUsageData
from tests.helpers.registry_compat import registry_resolve


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _build_test_registry(**kwargs):
    """Build OutputRegistry from synthetic test data."""
    from sysml_codegen.generation.initialization import build_output_registry

    return build_output_registry(
        calc_usages=kwargs.get("calc_usages", []),
        calc_defs=kwargs.get("calc_defs", []),
        aggregation_data=kwargs.get("aggregation_data", []),
        computed_attributes=kwargs.get("computed_attributes", []),
        channel_aliases=kwargs.get("channel_aliases", []),
        design_attributes=kwargs.get("design_attributes", {}),
    )


def _make_computed_attr(
    name: str,
    owning_part_name: str,
    owning_part_qn: str,
    classification: ComputedAttributeClassification = ComputedAttributeClassification.FORMULA,
    compilability: Compilability = Compilability.FULLY_COMPILABLE,
) -> ComputedAttributeData:
    return ComputedAttributeData(
        name=name,
        python_name=name,
        owning_part_name=owning_part_name,
        owning_part_qualified_name=owning_part_qn,
        expression_ast=None,
        expression_text=f"{name} expression",
        references=[],
        classification=classification,
        compilability=compilability,
    )


def _make_calc_usage(
    instance_name: str,
    calc_def_name: str,
    bindings: list[BindingInfo] | None = None,
    unbound_params: list[str] | None = None,
    qualified_name: str = "",
) -> CalcUsageData:
    return CalcUsageData(
        instance_name=instance_name,
        calc_def_name=calc_def_name,
        calc_def_qualified_name=f"Lib::{calc_def_name}",
        module_type=f"{calc_def_name}Module",
        bindings=bindings or [],
        unbound_params=unbound_params or [],
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
# Category (a): FORMULA Registration Tests
# ---------------------------------------------------------------------------


class TestComputedAttrRegistration:
    """Test OutputRegistry registration of FORMULA computed attributes."""

    def test_dotted_and_sysml_qn_keys_resolve(self):
        """Registry resolves ScopedKey('part.attr') and SysMLQN('Pkg::part::attr') for FORMULA.

        Bare keys (just 'attr') are NOT registered in the typed registry.
        """
        ca = _make_computed_attr("p_net_kw", "plant", "Pkg::plant")
        registry = _build_test_registry(computed_attributes=[ca])

        # ScopedKey (Key_F) resolves
        assert registry_resolve(registry,"plant.p_net_kw") is not None
        # SysML QN resolves
        assert registry_resolve(registry,"Pkg::plant::p_net_kw") is not None
        # Both resolve to the same canonical channel
        assert registry_resolve(registry,"plant.p_net_kw") == registry_resolve(registry,"Pkg::plant::p_net_kw")
        # Bare key does NOT resolve in typed registries
        assert registry_resolve(registry,"p_net_kw") is None

    def test_expose_pure_excluded_from_registration(self):
        """Only FORMULA attrs are registered; EXPOSE_PURE is excluded.

        Bare keys (just 'attr') are NOT in the typed registry for either
        classification.
        """
        formula = _make_computed_attr("area", "part", "Pkg::part",
                                      ComputedAttributeClassification.FORMULA)
        expose = _make_computed_attr("eta", "part", "Pkg::part",
                                     ComputedAttributeClassification.EXPOSE_PURE)

        registry = _build_test_registry(computed_attributes=[formula, expose])

        # FORMULA resolves via scoped key
        assert registry_resolve(registry,"part.area") is not None
        # EXPOSE_PURE should NOT resolve via scoped key
        assert registry_resolve(registry,"part.eta") is None
        # Bare keys don't exist for either classification
        assert registry_resolve(registry,"area") is None
        assert registry_resolve(registry,"eta") is None

    def test_expose_computed_excluded_from_registration(self):
        """EXPOSE_COMPUTED attrs excluded from registration."""
        ca = _make_computed_attr("scaled", "part", "Pkg::part",
                                 ComputedAttributeClassification.EXPOSE_COMPUTED)
        registry = _build_test_registry(computed_attributes=[ca])

        assert registry_resolve(registry,"part.scaled") is None

    def test_manual_required_formula_excluded_from_registration(self):
        """FORMULA with MANUAL_REQUIRED compilability excluded from registration.

        Only FULLY_COMPILABLE FORMULAs get synthetic modules, so
        MANUAL_REQUIRED FORMULAs must fall through to normal resolution.
        """
        ca = _make_computed_attr(
            "broken", "part", "Pkg::part",
            ComputedAttributeClassification.FORMULA,
            Compilability.MANUAL_REQUIRED,
        )
        registry = _build_test_registry(computed_attributes=[ca])

        assert registry_resolve(registry,"part.broken") is None
        assert registry_resolve(registry,"broken") is None

    def test_empty_computed_attrs(self):
        """Empty computed_attributes produces empty registry (for these keys)."""
        registry = _build_test_registry(computed_attributes=[])
        assert registry_resolve(registry,"anything") is None

    def test_none_computed_attrs_default(self):
        """Default (no computed_attributes) produces empty registry."""
        registry = _build_test_registry()
        assert registry_resolve(registry,"anything") is None

    def test_multiple_parts_register_distinct_channels(self):
        """Multiple parts each register their own entries with distinct channels."""
        ca1 = _make_computed_attr("area", "part_a", "Pkg::part_a")
        ca2 = _make_computed_attr("cost", "part_b", "Pkg::part_b")

        registry = _build_test_registry(computed_attributes=[ca1, ca2])

        assert registry_resolve(registry,"part_a.area") is not None
        assert registry_resolve(registry,"part_b.cost") is not None
        # Distinct channels
        assert registry_resolve(registry,"part_a.area") != registry_resolve(registry,"part_b.cost")


# ---------------------------------------------------------------------------
# Category (a): Channel Format Tests
# ---------------------------------------------------------------------------


class TestComputedAttrChannelFormat:
    """Test that registry resolves to correct PQN-format channel names."""

    def test_simple_channel_name(self):
        """Channel follows PQN format: {part_qn}__{attr}__{attr}."""
        ca = _make_computed_attr("area", "probe_design",
                                 "AttrExprProbeDesign::probe_design")
        registry = _build_test_registry(computed_attributes=[ca])

        channel = registry_resolve(registry,"probe_design.area")
        assert channel == "AttrExprProbeDesign__probe_design__area__area"

    def test_nested_namespace_channel(self):
        """Channel works with deeply nested SysML namespaces."""
        ca = _make_computed_attr("p_net_kw", "plant",
                                 "CATFDesign::FusionPlant::plant")
        registry = _build_test_registry(computed_attributes=[ca])

        channel = registry_resolve(registry,"plant.p_net_kw")
        assert channel == "CATFDesign__FusionPlant__plant__p_net_kw__p_net_kw"


# ---------------------------------------------------------------------------
# Category (b): Resolution Tests
# ---------------------------------------------------------------------------


class TestComputedAttrResolution:
    """Test _trace_dependencies with FORMULA bindings via OutputRegistry."""

    def test_binding_to_formula_resolves_module_output(self):
        """CalcUsage binding source_path='plant.p_net_kw' where p_net_kw is FORMULA
        -> MODULE_OUTPUT resolution with correct channel name."""
        ca = _make_computed_attr("p_net_kw", "plant", "Pkg::plant")

        usage = _make_calc_usage(
            "cost_calc", "CostCalc",
            bindings=[
                BindingInfo(
                    param_name="power",
                    source_path="plant.p_net_kw",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
            qualified_name="Pkg__Part__cost_calc",
        )

        calc_def = SimpleCalcDef(
            name="CostCalc",
            qualified_name="Lib::CostCalc",
            output_attributes=[SimpleAttrInfo("cost")],
        )

        registry = _build_test_registry(
            computed_attributes=[ca], calc_usages=[usage], calc_defs=[calc_def],
        )
        bt = DependencyBacktracker(
            [usage], [calc_def],
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__cost_calc|power"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
        assert resolution.qualified_name == "Pkg__plant__p_net_kw__p_net_kw"
        assert resolution.source_path == "plant.p_net_kw"
        assert resolution.is_transitive is False

    def test_dotted_path_exact_match_resolution(self):
        """source_path='part_x.area' resolves via dotted-key exact match in registry."""
        ca = _make_computed_attr("area", "part_x", "Pkg::part_x")

        usage = _make_calc_usage(
            "my_calc", "MyCalc",
            bindings=[
                BindingInfo(
                    param_name="a",
                    source_path="part_x.area",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
            qualified_name="Pkg__Part__my_calc",
        )

        calc_def = SimpleCalcDef(
            name="MyCalc",
            qualified_name="Lib::MyCalc",
            output_attributes=[SimpleAttrInfo("result")],
        )

        registry = _build_test_registry(
            computed_attributes=[ca], calc_usages=[usage], calc_defs=[calc_def],
        )
        bt = DependencyBacktracker(
            [usage], [calc_def],
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__my_calc|a"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
        assert "area__area" in resolution.qualified_name

    def test_non_formula_binding_unchanged(self):
        """Binding to non-FORMULA source goes through existing resolution."""
        ca = _make_computed_attr("eta", "plant", "Pkg::plant",
                                 ComputedAttributeClassification.EXPOSE_PURE)

        usage = _make_calc_usage(
            "my_calc", "MyCalc",
            bindings=[
                BindingInfo(
                    param_name="efficiency",
                    source_path="plant.eta",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
            qualified_name="Pkg__Part__my_calc",
        )

        calc_def = SimpleCalcDef(
            name="MyCalc",
            qualified_name="Lib::MyCalc",
            output_attributes=[SimpleAttrInfo("result")],
        )

        registry = _build_test_registry(
            computed_attributes=[ca], calc_usages=[usage], calc_defs=[calc_def],
        )
        bt = DependencyBacktracker(
            [usage], [calc_def],
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__my_calc|efficiency"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.ENTRY_POINT

    def test_bare_name_binding_falls_through_to_entry_point(self):
        """Bare name source_path='p_net_kw' is not in typed registries.

        Typed registries require scoped keys (part.attr) or SysML QN
        (Pkg::part::attr). A bare name without scope information cannot
        be resolved, so the backtracker falls through to ENTRY_POINT.
        """
        ca = _make_computed_attr("p_net_kw", "plant", "Pkg::plant")

        usage = _make_calc_usage(
            "cost_calc", "CostCalc",
            bindings=[
                BindingInfo(
                    param_name="power",
                    source_path="p_net_kw",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
            qualified_name="Pkg__Part__cost_calc",
        )

        calc_def = SimpleCalcDef(
            name="CostCalc",
            qualified_name="Lib::CostCalc",
            output_attributes=[SimpleAttrInfo("cost")],
        )

        registry = _build_test_registry(
            computed_attributes=[ca], calc_usages=[usage], calc_defs=[calc_def],
        )
        bt = DependencyBacktracker(
            [usage], [calc_def],
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__cost_calc|power"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.ENTRY_POINT


    # -- Category (c): Integration Tests --

    def test_trace_log_contains_computed_attr_resolution(self):
        """Trace log records resolution for debugging (checks outcome, not label)."""
        ca = _make_computed_attr("area", "part", "Pkg::part")

        usage = _make_calc_usage(
            "my_calc", "MyCalc",
            bindings=[
                BindingInfo(
                    param_name="a",
                    source_path="part.area",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
            qualified_name="Pkg__Part__my_calc",
        )

        calc_def = SimpleCalcDef(
            name="MyCalc",
            qualified_name="Lib::MyCalc",
            output_attributes=[SimpleAttrInfo("result")],
        )

        registry = _build_test_registry(
            computed_attributes=[ca], calc_usages=[usage], calc_defs=[calc_def],
        )
        bt = DependencyBacktracker(
            [usage], [calc_def],
            output_registry=registry,
        )
        result = bt.find_required_modules([], include_all=True)

        # Verify the binding resolved to MODULE_OUTPUT
        key = "Pkg__Part__my_calc|a"
        assert bt._binding_resolutions[key].resolution_type == BindingResolutionType.MODULE_OUTPUT

        # Verify trace log mentions the attribute (resilient to label changes)
        area_entries = [line for line in result.trace_log if "area" in line.lower()]
        assert len(area_entries) >= 1

    def test_literal_binding_not_affected_by_computed_attrs(self):
        """LITERAL bindings are still handled before computed attr check."""
        ca = _make_computed_attr("area", "part", "Pkg::part")

        usage = _make_calc_usage(
            "my_calc", "MyCalc",
            bindings=[
                BindingInfo(
                    param_name="x",
                    source_path="42.0",
                    binding_type=BindingType.LITERAL,
                    literal_value=42.0,
                ),
            ],
            qualified_name="Pkg__Part__my_calc",
        )

        calc_def = SimpleCalcDef(
            name="MyCalc",
            qualified_name="Lib::MyCalc",
            output_attributes=[SimpleAttrInfo("result")],
        )

        registry = _build_test_registry(
            computed_attributes=[ca], calc_usages=[usage], calc_defs=[calc_def],
        )
        bt = DependencyBacktracker(
            [usage], [calc_def],
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__my_calc|x"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.ENTRY_POINT


# ---------------------------------------------------------------------------
# Category (a): SysML :: Qualified Name Registration
# ---------------------------------------------------------------------------


class TestSysmlQualifiedNameRegistration:
    """SysML :: qualified name keys registered in OutputRegistry."""

    def test_sysml_qn_key_resolves(self):
        """Registry resolves SysMLQN and ScopedKey for FORMULA, not bare key."""
        ca = _make_computed_attr("power_mw", "e2e_plant", "E2EDesign::e2e_plant")
        registry = _build_test_registry(computed_attributes=[ca])

        # SysML QN resolves
        assert registry_resolve(registry,"E2EDesign::e2e_plant::power_mw") is not None
        # ScopedKey (Key_F) resolves
        assert registry_resolve(registry,"e2e_plant.power_mw") is not None
        # Both point to the same canonical channel
        assert registry_resolve(registry,"E2EDesign::e2e_plant::power_mw") == registry_resolve(registry,"e2e_plant.power_mw")
        # Bare key does NOT resolve in typed registries
        assert registry_resolve(registry,"power_mw") is None

    def test_sysml_qn_key_skipped_when_no_owning_part_qn(self):
        """No SysML QN key registered when owning_part_qualified_name is empty.

        ScopedKey (Key_F) is still registered. Bare key does not exist.
        """
        ca = _make_computed_attr("area", "part", "")
        registry = _build_test_registry(computed_attributes=[ca])

        # ScopedKey (Key_F) still resolves
        assert registry_resolve(registry,"part.area") is not None
        # Bare key does NOT resolve in typed registries
        assert registry_resolve(registry,"area") is None
        # No :: key because owning_part_qualified_name is empty
        assert registry_resolve(registry,"::area") is None


# ---------------------------------------------------------------------------
# Category (b): :: Binding Resolution
# ---------------------------------------------------------------------------


class TestColonColonBindingResolution:
    """:: source_path resolves to FORMULA MODULE_OUTPUT via OutputRegistry."""

    def test_colon_colon_binding_resolves_to_module_output(self):
        """CalcUsage binding with source_path 'E2EDesign::e2e_plant::power_mw'
        resolves as MODULE_OUTPUT via the :: registry key."""
        ca = _make_computed_attr("power_mw", "e2e_plant", "E2EDesign::e2e_plant")

        usage = _make_calc_usage(
            "energy_calc", "EnergyCalc",
            bindings=[
                BindingInfo(
                    param_name="power",
                    source_path="E2EDesign::e2e_plant::power_mw",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
            qualified_name="Pkg__Part__energy_calc",
        )

        calc_def = SimpleCalcDef(
            name="EnergyCalc",
            qualified_name="Lib::EnergyCalc",
            output_attributes=[SimpleAttrInfo("energy")],
        )

        registry = _build_test_registry(
            computed_attributes=[ca], calc_usages=[usage], calc_defs=[calc_def],
        )
        bt = DependencyBacktracker(
            [usage], [calc_def],
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__energy_calc|power"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
        assert "power_mw" in resolution.qualified_name

    def test_colon_colon_binding_to_expose_pure_resolves_transitively(self):
        """Binding with :: source_path to EXPOSE_PURE attr resolves transitively
        to upstream calc output via design attribute alias.

        The consumer usage must be scoped inside the same part (e2e_plant) where
        the transitive alias is registered, so the backtracker's REFERENCE
        secondary resolution finds 'e2e_plant.total_capex' via alias_lookup.
        """
        usage_producer = _make_calc_usage(
            "component_cost", "CostCalc",
            bindings=[],
            qualified_name="Pkg__e2e_plant__component_cost",
        )

        usage_consumer = _make_calc_usage(
            "financial", "FinancialCalc",
            bindings=[
                BindingInfo(
                    param_name="capex",
                    source_path="E2EDesign::e2e_plant::total_capex",
                    binding_type=BindingType.REFERENCE,
                ),
            ],
            qualified_name="Pkg__e2e_plant__financial",
        )

        calc_def_cost = SimpleCalcDef(
            name="CostCalc",
            qualified_name="Lib::CostCalc",
            output_attributes=[SimpleAttrInfo("total_cost")],
        )
        calc_def_fin = SimpleCalcDef(
            name="FinancialCalc",
            qualified_name="Lib::FinancialCalc",
            output_attributes=[SimpleAttrInfo("lcoe")],
        )

        # Design attr binding: e2e_plant.total_capex -> component_cost.total_cost
        design_attrs = {
            Path("design.sysml"): [
                DesignAttributeData(
                    qualified_name="Pkg__e2e_plant__total_capex",
                    name="total_capex",
                    sysml_type="Real",
                    default_value="component_cost.total_cost",
                    unit=None,
                    source_file=Path("design.sysml"),
                    source_line=10,
                    parent_part="e2e_plant",
                ),
            ],
        }

        registry = _build_test_registry(
            computed_attributes=[],
            calc_usages=[usage_producer, usage_consumer],
            calc_defs=[calc_def_cost, calc_def_fin],
            design_attributes=design_attrs,
        )
        bt = DependencyBacktracker(
            [usage_producer, usage_consumer],
            [calc_def_cost, calc_def_fin],
            design_attributes=design_attrs,
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__e2e_plant__financial|capex"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
