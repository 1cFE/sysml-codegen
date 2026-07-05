"""Integration tests for computed attribute pipeline (Phase 5).

Tests end-to-end scenarios from extraction through graph building,
validating that computed attributes flow correctly through the pipeline
stages: Step 4.5 (extraction + filtering) -> backtracker -> graph builder.

Six scenarios from design.md Component 7:
1. Simple FORMULA module generation
2. FORMULA chain (two modules, wiring, toposort)
3. FORMULA with EXPOSE_PURE input (alias resolution)
4. FORMULA removal from design_attributes
5. Backtracker resolution (MODULE_OUTPUT, not ENTRY_POINT)
6. Empty computed attributes (no-op)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agentic_mbse.sysml.types import BindingType, ExpressionRef

from sysml_codegen.analysis.dependency_backtracker import (
    BacktrackingResult,
    DependencyBacktracker,
    _ensure_backtracking_result_rebuilt,
)
from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.analysis.phantom_detector import PhantomDetectionReport
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from sysml_codegen.core.qualified_names import get_channel_name, sysml_to_python_qualified_name
from sysml_codegen.extraction.data_models import (
    AttributeInfo,
    CalculationDefinitionData,
    ComputedAttributeClassification,
    ComputedAttributeData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.usage_extractor import BindingInfo, CalcUsageData
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from sysml_codegen.orchestration.pipeline_builder import _remove_formula_from_design_attrs
from sysml_codegen.resolution.graph_builder import build_computation_graph
from sysml_codegen.resolution.models import (
    EntryPointType,
    InputSource,
    ModuleInput,
    ModuleOutput,
    PipelineModule,
)


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _make_computed_attr(
    name: str,
    owning_part_name: str,
    owning_part_qn: str,
    classification: ComputedAttributeClassification = ComputedAttributeClassification.FORMULA,
    compilability: Compilability = Compilability.FULLY_COMPILABLE,
    compiled_expression: str | None = None,
    references: list[ExpressionRef] | None = None,
) -> ComputedAttributeData:
    """Create a ComputedAttributeData for testing."""
    if compiled_expression is None and classification == ComputedAttributeClassification.FORMULA:
        compiled_expression = f"(inputs.{name}_input)"
    return ComputedAttributeData(
        name=name,
        python_name=name,
        owning_part_name=owning_part_name,
        owning_part_qualified_name=owning_part_qn,
        expression_ast=None,
        expression_text=f"{name} expression",
        references=references or [],
        classification=classification,
        compilability=compilability,
        compiled_expression=compiled_expression,
    )


def _make_calc_usage(
    instance_name: str,
    calc_def_name: str,
    bindings: list[BindingInfo] | None = None,
    unbound_params: list[str] | None = None,
    qualified_name: str = "",
) -> CalcUsageData:
    """Create a CalcUsageData for testing."""
    return CalcUsageData(
        instance_name=instance_name,
        calc_def_name=calc_def_name,
        calc_def_qualified_name=f"Lib::{calc_def_name}",
        module_type=f"{calc_def_name}Module",
        bindings=bindings or [],
        unbound_params=unbound_params or [],
        qualified_name=qualified_name or f"Pkg__Part__{instance_name}",
    )


def _make_calc_def(
    name: str,
    qualified_name: str = "",
    inputs: list[str] | None = None,
    outputs: list[str] | None = None,
) -> CalculationDefinitionData:
    """Create a CalculationDefinitionData for testing."""
    return CalculationDefinitionData(
        name=name,
        qualified_name=qualified_name or f"Lib::{name}",
        doc_comment="",
        calc_expressions=[],
        input_attributes=[
            AttributeInfo(name=n, sysml_type="Real", python_type="float")
            for n in (inputs or [])
        ],
        output_attributes=[
            AttributeInfo(name=n, sysml_type="Real", python_type="float")
            for n in (outputs or [])
        ],
        references=[],
        source_file=Path("test.sysml"),
    )


def _make_mock_group_deriver():
    """Create a mock ParameterGroupDeriver."""
    deriver = MagicMock()
    deriver.classify.return_value = "test_params"
    deriver.derive_groups_filtered.return_value = []
    return deriver


def _make_minimal_backtracking_result(
    usages: list[CalcUsageData] | None = None,
    entry_points: set[str] | None = None,
    entry_point_sources: dict[str, str] | None = None,
    binding_resolutions: dict[str, BindingResolution] | None = None,
) -> BacktrackingResult:
    """Create a minimal BacktrackingResult for testing."""
    _ensure_backtracking_result_rebuilt()
    return BacktrackingResult(
        required_usages=usages or [],
        dependency_graph={},
        entry_points=entry_points or set(),
        entry_point_sources=entry_point_sources or {},
        phantom_report=PhantomDetectionReport(),
        binding_resolutions=binding_resolutions or {},
    )


# ---------------------------------------------------------------------------
# Test 1: Simple FORMULA Module Generation
# ---------------------------------------------------------------------------


class TestSimpleFormula:
    """Test 1: area = length * width -> PipelineModule with entry point inputs."""

    def test_formula_produces_pipeline_module(self):
        """FORMULA computed attr produces a PipelineModule in the ComputationGraph."""
        ca = _make_computed_attr(
            "area", "probe_design", "Pkg::probe_design",
            compiled_expression="(inputs.length * inputs.width)",
        )

        result = _make_minimal_backtracking_result()
        graph = build_computation_graph(
            result=result,
            calc_defs=[],
            design_attrs={},
            group_deriver=_make_mock_group_deriver(),
            output_registry=OutputRegistry(),
            computed_attributes=[ca],
        )

        assert len(graph.modules) == 1
        module = graph.modules[0]
        assert module.is_computed_attribute is True
        assert module.compilability == Compilability.FULLY_COMPILABLE

    def test_formula_module_has_correct_inputs(self):
        """FORMULA module inputs match expression references (length, width)."""
        ca = _make_computed_attr(
            "area", "probe_design", "Pkg::probe_design",
            compiled_expression="(inputs.length * inputs.width)",
        )

        result = _make_minimal_backtracking_result()
        graph = build_computation_graph(
            result=result,
            calc_defs=[],
            design_attrs={},
            group_deriver=_make_mock_group_deriver(),
            output_registry=OutputRegistry(),
            computed_attributes=[ca],
        )

        module = graph.modules[0]
        input_names = {inp.param_name for inp in module.inputs}
        assert input_names == {"length", "width"}

    def test_formula_module_has_correct_output_channel(self):
        """FORMULA module output channel follows PQN format."""
        ca = _make_computed_attr(
            "area", "probe_design", "Pkg::probe_design",
            compiled_expression="(inputs.length * inputs.width)",
        )
        sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
        module_eqn = sysml_to_python_qualified_name(sysml_qn)
        expected_channel = get_channel_name(module_eqn, ca.python_name)

        result = _make_minimal_backtracking_result()
        graph = build_computation_graph(
            result=result,
            calc_defs=[],
            design_attrs={},
            group_deriver=_make_mock_group_deriver(),
            output_registry=OutputRegistry(),
            computed_attributes=[ca],
        )

        module = graph.modules[0]
        assert len(module.outputs) == 1
        assert module.outputs[0].channel_name == expected_channel
        assert module.outputs[0].field_name == "root"

    def test_formula_inputs_wired_to_entry_points(self):
        """FORMULA module inputs resolve to entry points (no upstream module)."""
        ca = _make_computed_attr(
            "area", "probe_design", "Pkg::probe_design",
            compiled_expression="(inputs.length * inputs.width)",
        )

        result = _make_minimal_backtracking_result()
        graph = build_computation_graph(
            result=result,
            calc_defs=[],
            design_attrs={},
            group_deriver=_make_mock_group_deriver(),
            output_registry=OutputRegistry(),
            computed_attributes=[ca],
        )

        module = graph.modules[0]
        for inp in module.inputs:
            assert inp.source.source_type == "entry_point", (
                f"Input {inp.param_name} should be entry_point, "
                f"got {inp.source.source_type}"
            )


# ---------------------------------------------------------------------------
# Test 2: FORMULA Chain
# ---------------------------------------------------------------------------


class TestFormulaChain:
    """Test 2: area = l*w, cost = area*rate -> two modules, correct wiring and order."""

    def _build_chain_graph(self):
        """Build graph with area -> cost chain."""
        ca_area = _make_computed_attr(
            "area", "part", "Pkg::part",
            compiled_expression="(inputs.length * inputs.width)",
        )
        ca_cost = _make_computed_attr(
            "cost", "part", "Pkg::part",
            compiled_expression="(inputs.area * inputs.rate)",
        )

        result = _make_minimal_backtracking_result()
        graph = build_computation_graph(
            result=result,
            calc_defs=[],
            design_attrs={},
            group_deriver=_make_mock_group_deriver(),
            output_registry=OutputRegistry(),
            computed_attributes=[ca_area, ca_cost],
        )
        return graph

    def test_chain_produces_two_modules(self):
        """Two FORMULA attrs produce two PipelineModules."""
        graph = self._build_chain_graph()
        assert len(graph.modules) == 2
        assert all(m.is_computed_attribute for m in graph.modules)

    def test_cost_area_input_wired_to_area_output(self):
        """cost module's 'area' input wired to area module's output channel."""
        graph = self._build_chain_graph()

        # Find modules by name
        modules_by_name = {m.name: m for m in graph.modules}
        area_mod = next(m for m in graph.modules if "area" in m.name)
        cost_mod = next(m for m in graph.modules if "cost" in m.name)

        # cost's area input should be module_output pointing to area's channel
        area_input = next(
            inp for inp in cost_mod.inputs if inp.param_name == "area"
        )
        assert area_input.source.source_type == "module_output"
        assert area_input.source.producer_channel == area_mod.outputs[0].channel_name

    def test_area_executes_before_cost(self):
        """area.execution_order < cost.execution_order."""
        graph = self._build_chain_graph()

        area_mod = next(m for m in graph.modules if "area" in m.name)
        cost_mod = next(m for m in graph.modules if "cost" in m.name)

        assert area_mod.execution_order < cost_mod.execution_order

    def test_cost_rate_input_is_entry_point(self):
        """cost module's 'rate' input (not a FORMULA) is an entry point."""
        graph = self._build_chain_graph()

        cost_mod = next(m for m in graph.modules if "cost" in m.name)
        rate_input = next(
            inp for inp in cost_mod.inputs if inp.param_name == "rate"
        )
        assert rate_input.source.source_type == "entry_point"


# ---------------------------------------------------------------------------
# Test 3: FORMULA With EXPOSE_PURE Input
# ---------------------------------------------------------------------------


class TestFormulaWithExposePure:
    """Test 3: FORMULA referencing EXPOSE_PURE alias -> wired to calc output channel."""

    def test_formula_input_wired_through_expose_alias(self):
        """FORMULA module's input wired to upstream calc output via EXPOSE_PURE alias.

        Scenario: calc usage alpha_split has output p_alpha.
        EXPOSE_PURE p_alpha_out = alpha_split.p_alpha (alias).
        FORMULA useful_power = p_alpha_out * efficiency.
        -> useful_power's p_alpha_out input should wire to alpha_split's output channel.
        """
        # CalcUsage: alpha_split with output p_alpha
        calc_def = _make_calc_def(
            "AlphaSplitCalc",
            qualified_name="Lib::AlphaSplitCalc",
            inputs=["p_fusion"],
            outputs=["p_alpha"],
        )
        usage = _make_calc_usage(
            "alpha_split", "AlphaSplitCalc",
            unbound_params=["p_fusion"],
            qualified_name="Pkg__plant__alpha_split",
        )

        # EXPOSE_PURE: p_alpha_out = alpha_split.p_alpha
        expose_ca = _make_computed_attr(
            "p_alpha_out", "plant", "Pkg::plant",
            classification=ComputedAttributeClassification.EXPOSE_PURE,
            compilability=Compilability.UNKNOWN,
            compiled_expression=None,
            references=[
                ExpressionRef(name="alpha_split", qualified_name="Pkg::plant::alpha_split"),
                ExpressionRef(name="p_alpha", qualified_name="Lib::AlphaSplitCalc::p_alpha"),
            ],
        )

        # FORMULA: useful_power = p_alpha_out * efficiency
        formula_ca = _make_computed_attr(
            "useful_power", "plant", "Pkg::plant",
            compiled_expression="(inputs.p_alpha_out * inputs.efficiency)",
        )

        # Build backtracking result with the alpha_split usage
        # The key format is "{instance_name}.{output_attr}" for output catalog
        binding_resolutions = {
            "Pkg__plant__alpha_split|p_fusion": BindingResolution(
                resolution_type=BindingResolutionType.ENTRY_POINT,
                qualified_name="Pkg__plant__p_fusion",
            ),
        }
        result = _make_minimal_backtracking_result(
            usages=[usage],
            entry_points={"Pkg__plant__p_fusion"},
            entry_point_sources={"Pkg__plant__p_fusion": "test.sysml"},
            binding_resolutions=binding_resolutions,
        )

        registry = build_output_registry(
            calc_usages=[usage], calc_defs=[calc_def],
            computed_attributes=[expose_ca, formula_ca],
            aggregation_data=[], channel_aliases=[], design_attributes={},
        )
        graph = build_computation_graph(
            result=result,
            calc_defs=[calc_def],
            design_attrs={},
            group_deriver=_make_mock_group_deriver(),
            output_registry=registry,
            computed_attributes=[expose_ca, formula_ca],
        )

        # Find the FORMULA module (only computed_attribute module is useful_power)
        formula_modules = [m for m in graph.modules if m.is_computed_attribute]
        assert len(formula_modules) == 1, (
            f"Expected 1 FORMULA module, got {len(formula_modules)}: "
            f"{[m.name for m in formula_modules]}"
        )
        useful_power_mod = formula_modules[0]

        # p_alpha_out input should be wired to upstream calc output (module_output)
        p_alpha_input = next(
            (inp for inp in useful_power_mod.inputs if inp.param_name == "p_alpha_out"),
            None,
        )
        assert p_alpha_input is not None, (
            f"Expected p_alpha_out input, got: {[i.param_name for i in useful_power_mod.inputs]}"
        )
        assert p_alpha_input.source.source_type == "module_output", (
            f"p_alpha_out should wire through EXPOSE_PURE alias to calc output, "
            f"got {p_alpha_input.source.source_type}"
        )

    def test_expose_pure_does_not_generate_module(self):
        """EXPOSE_PURE computed attrs do NOT produce their own PipelineModule."""
        expose_ca = _make_computed_attr(
            "p_alpha_out", "plant", "Pkg::plant",
            classification=ComputedAttributeClassification.EXPOSE_PURE,
            compilability=Compilability.UNKNOWN,
            compiled_expression=None,
        )

        result = _make_minimal_backtracking_result()
        graph = build_computation_graph(
            result=result,
            calc_defs=[],
            design_attrs={},
            group_deriver=_make_mock_group_deriver(),
            output_registry=OutputRegistry(),
            computed_attributes=[expose_ca],
        )

        assert len(graph.modules) == 0


# ---------------------------------------------------------------------------
# Test 4: FORMULA Removal From design_attributes
# ---------------------------------------------------------------------------


class TestFormulaRemoval:
    """Test 4: FORMULA attrs absent from design_attrs, non-FORMULA preserved."""

    def _make_design_attr(
        self,
        qualified_name: str,
        name: str,
        parent_part: str,
        default_value=None,
    ) -> DesignAttributeData:
        """Create a DesignAttributeData with required fields."""
        return DesignAttributeData(
            name=name,
            sysml_type="Real",
            default_value=default_value,
            unit=None,
            source_file=Path("design.sysml"),
            source_line=1,
            parent_part=parent_part,
            qualified_name=qualified_name,
        )

    def test_formula_removed_non_formula_preserved(self):
        """FORMULA attrs removed from design_attrs; non-FORMULA kept."""
        design_attrs: dict[Path, list[DesignAttributeData]] = {
            Path("design.sysml"): [
                self._make_design_attr("Pkg__part__area", "area", "part"),
                self._make_design_attr("Pkg__part__length", "length", "part", 10.0),
            ]
        }

        formula_ca = _make_computed_attr("area", "part", "Pkg::part")

        removed = _remove_formula_from_design_attrs([formula_ca], design_attrs)

        assert removed == 1
        remaining = design_attrs[Path("design.sysml")]
        assert len(remaining) == 1
        assert remaining[0].name == "length"

    def test_expose_pure_not_removed(self):
        """EXPOSE_PURE attrs remain in design_attrs."""
        design_attrs: dict[Path, list[DesignAttributeData]] = {
            Path("design.sysml"): [
                self._make_design_attr("Pkg__part__eta_out", "eta_out", "part"),
            ]
        }

        expose_ca = _make_computed_attr(
            "eta_out", "part", "Pkg::part",
            classification=ComputedAttributeClassification.EXPOSE_PURE,
            compiled_expression=None,
        )

        removed = _remove_formula_from_design_attrs([expose_ca], design_attrs)

        assert removed == 0
        assert len(design_attrs[Path("design.sysml")]) == 1

    def test_formula_removal_prevents_false_entry_points(self):
        """FORMULA removal + graph building -> no entry point for FORMULA attr."""
        ca = _make_computed_attr(
            "area", "probe_design", "Pkg::probe_design",
            compiled_expression="(inputs.length * inputs.width)",
        )
        design_attrs: dict[Path, list[DesignAttributeData]] = {
            Path("design.sysml"): [
                self._make_design_attr("Pkg__probe_design__area", "area", "probe_design"),
                self._make_design_attr("Pkg__probe_design__length", "length", "probe_design", 5.0),
            ]
        }

        # Step 4.5: Remove FORMULA from design_attrs
        _remove_formula_from_design_attrs([ca], design_attrs)

        # Build graph with filtered design_attrs
        result = _make_minimal_backtracking_result()
        graph = build_computation_graph(
            result=result,
            calc_defs=[],
            design_attrs=design_attrs,
            group_deriver=_make_mock_group_deriver(),
            output_registry=OutputRegistry(),
            computed_attributes=[ca],
        )

        # The module should exist
        assert len(graph.modules) == 1
        # "area" should NOT appear as an entry point (it was removed from design_attrs)
        entry_point_names = set()
        for group in graph.entry_point_groups:
            for ep in group.parameters:
                entry_point_names.add(ep.simple_name)
        # "area" must not be an entry point (it's a module output)
        assert "area" not in entry_point_names or all(
            "area" in m.name for m in graph.modules
        )


# ---------------------------------------------------------------------------
# Test 5: Backtracker Resolution
# ---------------------------------------------------------------------------


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


class TestBacktrackerResolution:
    """Test 5: CalcUsage binding to FORMULA -> MODULE_OUTPUT resolution."""

    def test_formula_binding_resolves_as_module_output(self):
        """CalcUsage binding to FORMULA attr resolves as MODULE_OUTPUT, not ENTRY_POINT.

        Scenario: cost_calc has input 'p_net_kw' bound to plant.p_net_kw
        where p_net_kw is a FORMULA computed attribute.
        """
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
            output_attributes=[SimpleAttrInfo(name="cost")],
            input_attributes=[SimpleAttrInfo(name="power")],
        )

        registry = build_output_registry(
            calc_usages=[usage], calc_defs=[calc_def],
            computed_attributes=[ca], aggregation_data=[],
            channel_aliases=[], design_attributes={},
        )
        bt = DependencyBacktracker(
            [usage], [calc_def],
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__cost_calc|power"
        assert key in bt._binding_resolutions, (
            f"Expected binding resolution for {key}, "
            f"available: {list(bt._binding_resolutions.keys())}"
        )
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
        assert "p_net_kw" in resolution.qualified_name

    def test_non_formula_binding_not_affected(self):
        """Unbound param goes through normal resolution -> ENTRY_POINT."""
        usage = _make_calc_usage(
            "cost_calc", "CostCalc",
            unbound_params=["rate"],
            qualified_name="Pkg__Part__cost_calc",
        )

        calc_def = SimpleCalcDef(
            name="CostCalc",
            qualified_name="Lib::CostCalc",
            output_attributes=[SimpleAttrInfo(name="cost")],
            input_attributes=[SimpleAttrInfo(name="rate")],
        )

        registry = build_output_registry(
            calc_usages=[usage], calc_defs=[calc_def],
            computed_attributes=[], aggregation_data=[],
            channel_aliases=[], design_attributes={},
        )
        bt = DependencyBacktracker(
            [usage], [calc_def],
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = "Pkg__Part__cost_calc|rate"
        assert key in bt._binding_resolutions
        resolution = bt._binding_resolutions[key]
        assert resolution.resolution_type == BindingResolutionType.ENTRY_POINT

    def test_formula_channel_points_to_synthetic_module(self):
        """MODULE_OUTPUT channel name matches the FORMULA module's output channel format."""
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
        )

        calc_def = SimpleCalcDef(
            name="CostCalc",
            qualified_name="Lib::CostCalc",
            output_attributes=[SimpleAttrInfo(name="cost")],
            input_attributes=[SimpleAttrInfo(name="power")],
        )

        registry = build_output_registry(
            calc_usages=[usage], calc_defs=[calc_def],
            computed_attributes=[ca], aggregation_data=[],
            channel_aliases=[], design_attributes={},
        )
        bt = DependencyBacktracker(
            [usage], [calc_def],
            output_registry=registry,
        )
        bt.find_required_modules([], include_all=True)

        key = f"{usage.qualified_name}|power"
        resolution = bt._binding_resolutions[key]

        # Channel should follow PQN format: {module_eqn}__{attr_name}
        sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
        module_eqn = sysml_to_python_qualified_name(sysml_qn)
        expected_channel = get_channel_name(module_eqn, ca.python_name)
        assert resolution.qualified_name == expected_channel


# ---------------------------------------------------------------------------
# Test 6: Empty Computed Attributes
# ---------------------------------------------------------------------------


class TestEmptyComputedAttrs:
    """Test 6: No computed attrs -> zero impact on existing pipeline."""

    def _build_graph_with_calcusage(self, computed_attrs=None):
        """Build a graph with one CalcUsage module, optionally with computed attrs."""
        calc_def = _make_calc_def(
            "PowerCalc",
            qualified_name="Lib::PowerCalc",
            inputs=["voltage"],
            outputs=["power"],
        )
        usage = _make_calc_usage(
            "power_calc", "PowerCalc",
            unbound_params=["voltage"],
            qualified_name="Pkg__Part__power_calc",
        )

        binding_resolutions = {
            "Pkg__Part__power_calc|voltage": BindingResolution(
                resolution_type=BindingResolutionType.ENTRY_POINT,
                qualified_name="Pkg__Part__voltage",
            ),
        }
        result = _make_minimal_backtracking_result(
            usages=[usage],
            entry_points={"Pkg__Part__voltage"},
            entry_point_sources={"Pkg__Part__voltage": "test.sysml"},
            binding_resolutions=binding_resolutions,
        )

        return build_computation_graph(
            result=result,
            calc_defs=[calc_def],
            design_attrs={},
            group_deriver=_make_mock_group_deriver(),
            output_registry=OutputRegistry(),
            computed_attributes=computed_attrs,
        )

    def test_empty_list_no_impact(self):
        """Empty computed_attributes list has zero impact on graph."""
        graph_without = self._build_graph_with_calcusage(computed_attrs=None)
        graph_with_empty = self._build_graph_with_calcusage(computed_attrs=[])

        assert len(graph_without.modules) == len(graph_with_empty.modules)
        assert len(graph_without.modules) == 1
        assert graph_without.modules[0].is_computed_attribute is False

    def test_none_computed_attrs_no_impact(self):
        """None computed_attributes has zero impact on graph."""
        graph = self._build_graph_with_calcusage(computed_attrs=None)

        assert len(graph.modules) == 1
        assert graph.modules[0].name is not None
        assert graph.modules[0].is_computed_attribute is False

    def test_calcusage_module_unchanged_with_empty_computed_attrs(self):
        """CalcUsage module structure identical with and without computed_attrs."""
        graph = self._build_graph_with_calcusage(computed_attrs=[])

        module = graph.modules[0]
        assert module.is_computed_attribute is False
        assert len(module.inputs) == 1
        assert module.inputs[0].param_name == "voltage"
        assert len(module.outputs) == 1
        assert module.outputs[0].field_name == "root"

    def test_execution_order_preserved(self):
        """Module execution_order unchanged with empty computed_attrs."""
        graph_without = self._build_graph_with_calcusage(computed_attrs=None)
        graph_with_empty = self._build_graph_with_calcusage(computed_attrs=[])

        assert graph_without.modules[0].execution_order == graph_with_empty.modules[0].execution_order
