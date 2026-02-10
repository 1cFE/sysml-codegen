"""Unit tests for backtracker computed attribute awareness (Phase 2).

Tests the FORMULA lookup index, channel name building, and _trace_dependencies()
integration that resolves CalcUsage bindings to FORMULA computed attributes as
MODULE_OUTPUT instead of falling through to ENTRY_POINT.
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


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


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
# Tests: FORMULA Lookup Index
# ---------------------------------------------------------------------------


class TestComputedAttrIndex:
    """Test FORMULA lookup index construction."""

    def test_index_keys_dotted_and_bare(self):
        """Index has both 'part.attr' and 'attr' keys for each FORMULA."""
        ca = _make_computed_attr("p_net_kw", "plant", "Pkg::plant")
        bt = DependencyBacktracker([], [], computed_attributes=[ca])

        assert "plant.p_net_kw" in bt._computed_attr_index
        assert "p_net_kw" in bt._computed_attr_index
        assert bt._computed_attr_index["plant.p_net_kw"] is ca
        assert bt._computed_attr_index["p_net_kw"] is ca

    def test_expose_pure_excluded_from_index(self):
        """Only FORMULA attrs go into the index."""
        formula = _make_computed_attr("area", "part", "Pkg::part",
                                      ComputedAttributeClassification.FORMULA)
        expose = _make_computed_attr("eta", "part", "Pkg::part",
                                     ComputedAttributeClassification.EXPOSE_PURE)

        bt = DependencyBacktracker([], [], computed_attributes=[formula, expose])

        assert "part.area" in bt._computed_attr_index
        assert "area" in bt._computed_attr_index
        # EXPOSE_PURE should NOT be in index
        assert "part.eta" not in bt._computed_attr_index
        assert "eta" not in bt._computed_attr_index

    def test_expose_computed_excluded_from_index(self):
        """EXPOSE_COMPUTED attrs also excluded from index."""
        ca = _make_computed_attr("scaled", "part", "Pkg::part",
                                 ComputedAttributeClassification.EXPOSE_COMPUTED)
        bt = DependencyBacktracker([], [], computed_attributes=[ca])

        assert "part.scaled" not in bt._computed_attr_index

    def test_manual_required_formula_excluded_from_index(self):
        """FORMULA with MANUAL_REQUIRED compilability excluded from index.

        Only FULLY_COMPILABLE FORMULAs get synthetic modules, so
        MANUAL_REQUIRED FORMULAs must fall through to normal resolution.
        """
        ca = _make_computed_attr(
            "broken", "part", "Pkg::part",
            ComputedAttributeClassification.FORMULA,
            Compilability.MANUAL_REQUIRED,
        )
        bt = DependencyBacktracker([], [], computed_attributes=[ca])

        assert "part.broken" not in bt._computed_attr_index
        assert "broken" not in bt._computed_attr_index

    def test_empty_computed_attrs(self):
        """Empty computed_attributes produces empty index."""
        bt = DependencyBacktracker([], [])
        assert bt._computed_attr_index == {}

    def test_none_computed_attrs(self):
        """None computed_attributes produces empty index."""
        bt = DependencyBacktracker([], [], computed_attributes=None)
        assert bt._computed_attr_index == {}

    def test_multiple_parts_in_index(self):
        """Multiple parts each contribute their own entries."""
        ca1 = _make_computed_attr("area", "part_a", "Pkg::part_a")
        ca2 = _make_computed_attr("cost", "part_b", "Pkg::part_b")

        bt = DependencyBacktracker([], [], computed_attributes=[ca1, ca2])

        assert "part_a.area" in bt._computed_attr_index
        assert "part_b.cost" in bt._computed_attr_index
        assert len(bt._computed_attr_index) == 6  # 2 dotted + 2 bare + 2 :: keys


# ---------------------------------------------------------------------------
# Tests: Channel Name Building
# ---------------------------------------------------------------------------


class TestBuildComputedAttrChannel:
    """Test _build_computed_attr_channel() output format."""

    def test_simple_channel_name(self):
        """Channel follows PQN format: {part_qn}__{attr}__{attr}."""
        ca = _make_computed_attr("area", "probe_design",
                                 "AttrExprProbeDesign::probe_design")
        bt = DependencyBacktracker([], [], computed_attributes=[ca])

        channel = bt._build_computed_attr_channel(ca)

        # module_eqn = "AttrExprProbeDesign__probe_design__area"
        # channel = get_channel_name(module_eqn, "area")
        #         = "AttrExprProbeDesign__probe_design__area__area"
        assert channel == "AttrExprProbeDesign__probe_design__area__area"

    def test_nested_namespace_channel(self):
        """Channel works with deeply nested SysML namespaces."""
        ca = _make_computed_attr("p_net_kw", "plant",
                                 "CATFDesign::FusionPlant::plant")
        bt = DependencyBacktracker([], [], computed_attributes=[ca])

        channel = bt._build_computed_attr_channel(ca)

        assert channel == "CATFDesign__FusionPlant__plant__p_net_kw__p_net_kw"


# ---------------------------------------------------------------------------
# Tests: _trace_dependencies() Integration
# ---------------------------------------------------------------------------


class TestComputedAttrResolution:
    """Test _trace_dependencies with FORMULA bindings."""

    def test_binding_to_formula_resolves_module_output(self):
        """CalcUsage binding source_path='plant.p_net_kw' where p_net_kw is FORMULA
        -> MODULE_OUTPUT resolution with correct channel name."""
        ca = _make_computed_attr("p_net_kw", "plant", "Pkg::plant")

        # CalcUsage with a binding to the FORMULA attribute
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

        # A calc def for cost_calc so the output catalog builds correctly
        calc_def = SimpleCalcDef(
            name="CostCalc",
            qualified_name="Lib::CostCalc",
            output_attributes=[SimpleAttrInfo("cost")],
        )

        bt = DependencyBacktracker(
            [usage], [calc_def],
            computed_attributes=[ca],
        )
        bt.find_required_modules([], include_all=True)

        # Check binding resolution
        key = "Pkg__Part__cost_calc|power"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
        assert resolution.qualified_name == "Pkg__plant__p_net_kw__p_net_kw"
        assert resolution.source_path == "plant.p_net_kw"
        assert resolution.is_transitive is False

    def test_dotted_path_bare_name_fallback(self):
        """source_path='plant.area' tries dotted key first, falls back to bare 'area'."""
        # Index only has bare key "area" (owning_part_name = "part_x", not "plant")
        ca = _make_computed_attr("area", "part_x", "Pkg::part_x")

        usage = _make_calc_usage(
            "my_calc", "MyCalc",
            bindings=[
                BindingInfo(
                    param_name="a",
                    source_path="plant.area",
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

        bt = DependencyBacktracker(
            [usage], [calc_def],
            computed_attributes=[ca],
        )
        bt.find_required_modules([], include_all=True)

        # Should fall back to bare name "area" and resolve
        key = "Pkg__Part__my_calc|a"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
        assert "area__area" in resolution.qualified_name

    def test_non_formula_binding_unchanged(self):
        """Binding to non-FORMULA source goes through existing resolution."""
        # Only EXPOSE_PURE in computed attrs - not in index
        ca = _make_computed_attr("eta", "plant", "Pkg::plant",
                                 ComputedAttributeClassification.EXPOSE_PURE)

        # Binding to a non-computed source that doesn't resolve to anything
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

        bt = DependencyBacktracker(
            [usage], [calc_def],
            computed_attributes=[ca],
        )
        bt.find_required_modules([], include_all=True)

        # Should fall through to existing resolution (ENTRY_POINT since unresolvable)
        key = "Pkg__Part__my_calc|efficiency"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.ENTRY_POINT

    def test_bare_name_binding_resolves(self):
        """Bare name source_path='p_net_kw' resolves via bare key in index."""
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

        bt = DependencyBacktracker(
            [usage], [calc_def],
            computed_attributes=[ca],
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__cost_calc|power"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT

    def test_trace_log_contains_computed_attr_entry(self):
        """Trace log records COMPUTED_ATTR resolution for debugging."""
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

        bt = DependencyBacktracker(
            [usage], [calc_def],
            computed_attributes=[ca],
        )
        result = bt.find_required_modules([], include_all=True)

        # Check trace log has COMPUTED_ATTR entry
        computed_entries = [
            line for line in result.trace_log if "COMPUTED_ATTR" in line
        ]
        assert len(computed_entries) == 1
        assert "area" in computed_entries[0]

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

        bt = DependencyBacktracker(
            [usage], [calc_def],
            computed_attributes=[ca],
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__my_calc|x"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.ENTRY_POINT


# ---------------------------------------------------------------------------
# Tests: Bug 2 — SysML :: qualified name index key + resolution
# ---------------------------------------------------------------------------


class TestSysmlQualifiedNameIndex:
    """Bug 2 Change A: _computed_attr_index includes :: qualified name key."""

    def test_sysml_qn_key_in_index(self):
        """Index has 'Part::attr' key alongside dotted and bare keys."""
        ca = _make_computed_attr("power_mw", "e2e_plant", "E2EDesign::e2e_plant")
        bt = DependencyBacktracker([], [], computed_attributes=[ca])

        assert "E2EDesign::e2e_plant::power_mw" in bt._computed_attr_index
        assert "e2e_plant.power_mw" in bt._computed_attr_index
        assert "power_mw" in bt._computed_attr_index
        assert len(bt._computed_attr_index) == 3

    def test_sysml_qn_key_skipped_when_no_owning_part_qn(self):
        """No :: key added when owning_part_qualified_name is empty."""
        ca = _make_computed_attr("area", "part", "")
        bt = DependencyBacktracker([], [], computed_attributes=[ca])

        assert "part.area" in bt._computed_attr_index
        assert "area" in bt._computed_attr_index
        # No :: key because owning_part_qualified_name is empty
        assert len(bt._computed_attr_index) == 2


class TestColonColonBindingResolution:
    """Bug 2 Changes B+C: :: source_path resolves to FORMULA MODULE_OUTPUT."""

    def test_colon_colon_binding_resolves_to_module_output(self):
        """CalcUsage binding with source_path 'E2EDesign::e2e_plant::power_mw'
        resolves as MODULE_OUTPUT via the :: index key."""
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

        bt = DependencyBacktracker(
            [usage], [calc_def],
            computed_attributes=[ca],
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__energy_calc|power"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
        assert "power_mw" in resolution.qualified_name

    def test_colon_colon_binding_to_expose_pure_resolves_transitively(self):
        """Binding with :: source_path to EXPOSE_PURE attr resolves transitively
        to upstream calc output via _resolve_binding_to_usage."""
        # Set up: EXPOSE_PURE attr "total_capex" is aliased via design attr binding
        # to a calc usage output "component_cost.total_cost"
        usage_producer = _make_calc_usage(
            "component_cost", "CostCalc",
            bindings=[],
            qualified_name="Pkg__Part__component_cost",
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
            qualified_name="Pkg__Part__financial",
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
                    qualified_name="Pkg__Part__total_capex",
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

        bt = DependencyBacktracker(
            [usage_producer, usage_consumer],
            [calc_def_cost, calc_def_fin],
            design_attributes=design_attrs,
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__financial|capex"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
