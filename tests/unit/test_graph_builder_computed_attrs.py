"""Unit tests for graph builder computed attribute support (Phase 3).

Tests the attribute resolution map, EXPOSE_PURE resolution, computed attribute
module building, output catalog extension, and unified topological sort.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agentic_mbse.sysml.types import ExpressionRef

from sysml_codegen.analysis.dependency_backtracker import (
    BacktrackingResult,
    CircularDependencyError,
    _ensure_backtracking_result_rebuilt,
)
from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.analysis.phantom_detector import PhantomDetectionReport
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from sysml_codegen.core.qualified_names import get_channel_name
from sysml_codegen.extraction.data_models import (
    AttributeInfo,
    CalculationDefinitionData,
    ComputedAttributeClassification,
    ComputedAttributeData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.usage_extractor import CalcUsageData
from sysml_codegen.resolution.graph_builder import (
    AttributeResolutionKind,
    _build_attribute_resolution_map,
    _build_computed_attr_module,
    _extend_output_catalog_with_computed_attrs,
    _resolve_expose_pure,
    _unified_topological_sort,
    build_computation_graph,
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
# Tests: Attribute Resolution Map
# ---------------------------------------------------------------------------


class TestAttributeResolutionMap:
    """Test per-part attribute resolution map construction."""

    def test_formula_attr_resolves_to_formula_kind(self):
        """FORMULA attr -> kind='formula' with correct channel_name."""
        ca = _make_computed_attr("area", "probe_design", "Pkg::probe_design")

        attr_map = _build_attribute_resolution_map(
            computed_attrs=[ca],
            design_attrs={},
            output_catalog={},
            calc_usage_names=set(),
        )

        assert "probe_design" in attr_map
        assert "area" in attr_map["probe_design"]
        resolution = attr_map["probe_design"]["area"]
        assert resolution.kind == AttributeResolutionKind.FORMULA
        assert resolution.channel_name == "Pkg__probe_design__area__area"

    def test_expose_pure_resolves_to_alias(self):
        """EXPOSE_PURE attr -> kind='expose_alias' with upstream calc channel."""
        # EXPOSE_PURE: p_alpha_out = alpha_split.p_alpha
        ca = _make_computed_attr(
            "p_alpha_out", "plant", "Pkg::plant",
            classification=ComputedAttributeClassification.EXPOSE_PURE,
            compilability=Compilability.FULLY_COMPILABLE,
            compiled_expression=None,
            references=[
                ExpressionRef(name="alpha_split", qualified_name="Pkg::plant::alpha_split"),
                ExpressionRef(name="p_alpha", qualified_name="Lib::AlphaSplitCalc::p_alpha"),
            ],
        )

        # Output catalog has the upstream calc output
        output_catalog = {
            "alpha_split.p_alpha": ("AlphaSplitModule", "Pkg__plant__alpha_split__p_alpha", "root"),
        }

        attr_map = _build_attribute_resolution_map(
            computed_attrs=[ca],
            design_attrs={},
            output_catalog=output_catalog,
            calc_usage_names={"alpha_split"},
        )

        assert "plant" in attr_map
        assert "p_alpha_out" in attr_map["plant"]
        resolution = attr_map["plant"]["p_alpha_out"]
        assert resolution.kind == AttributeResolutionKind.EXPOSE_ALIAS
        assert resolution.channel_name == "Pkg__plant__alpha_split__p_alpha"

    def test_literal_attr_resolves_to_literal(self):
        """Design attr not in computed_attrs -> not in resolution map."""
        # No computed attrs, but a design attr for "length"
        design_attrs = {
            Path("test.sysml"): [
                DesignAttributeData(
                    qualified_name="Pkg__probe_design__length",
                    name="length",
                    sysml_type="Real",
                    default_value="10.0",
                    unit=None,
                    source_file=Path("test.sysml"),
                    source_line=1,
                    parent_part="probe_design",
                ),
            ],
        }

        attr_map = _build_attribute_resolution_map(
            computed_attrs=[],
            design_attrs=design_attrs,
            output_catalog={},
            calc_usage_names=set(),
        )

        # No entries because no computed attrs to build map for
        assert len(attr_map) == 0

    def test_expose_computed_excluded(self):
        """EXPOSE_COMPUTED attrs are excluded from resolution map (deferred)."""
        ca = _make_computed_attr(
            "scaled", "part", "Pkg::part",
            classification=ComputedAttributeClassification.EXPOSE_COMPUTED,
        )

        attr_map = _build_attribute_resolution_map(
            computed_attrs=[ca],
            design_attrs={},
            output_catalog={},
            calc_usage_names=set(),
        )

        # EXPOSE_COMPUTED should not produce formula or alias entries
        if "part" in attr_map:
            assert "scaled" not in attr_map["part"] or attr_map["part"]["scaled"].kind != AttributeResolutionKind.FORMULA

    def test_multiple_parts_separate_maps(self):
        """Each part gets its own resolution map."""
        ca1 = _make_computed_attr("area", "part_a", "Pkg::part_a",
                                  compiled_expression="(inputs.length * inputs.width)")
        ca2 = _make_computed_attr("cost", "part_b", "Pkg::part_b",
                                  compiled_expression="(inputs.area * inputs.rate)")

        attr_map = _build_attribute_resolution_map(
            computed_attrs=[ca1, ca2],
            design_attrs={},
            output_catalog={},
            calc_usage_names=set(),
        )

        assert "part_a" in attr_map
        assert "area" in attr_map["part_a"]
        assert "part_b" in attr_map
        assert "cost" in attr_map["part_b"]


# ---------------------------------------------------------------------------
# Tests: EXPOSE_PURE Resolution
# ---------------------------------------------------------------------------


class TestExposeResolution:
    """Test _resolve_expose_pure() algorithm."""

    def test_separates_instance_and_output_refs(self):
        """Correctly identifies calc instance vs output attr from references."""
        ca = _make_computed_attr(
            "p_alpha_out", "plant", "Pkg::plant",
            classification=ComputedAttributeClassification.EXPOSE_PURE,
            compiled_expression=None,
            references=[
                ExpressionRef(name="alpha_split", qualified_name="Pkg::plant::alpha_split"),
                ExpressionRef(name="p_alpha", qualified_name="Lib::AlphaSplitCalc::p_alpha"),
            ],
        )

        output_catalog = {
            "alpha_split.p_alpha": ("AlphaSplitModule", "Pkg__plant__alpha_split__p_alpha", "root"),
        }

        channel = _resolve_expose_pure(ca, {"alpha_split"}, output_catalog)
        assert channel == "Pkg__plant__alpha_split__p_alpha"

    def test_builds_correct_catalog_key(self):
        """Catalog key is '{instance_name}.{output_attr_name}'."""
        ca = _make_computed_attr(
            "eta_out", "part", "Pkg::part",
            classification=ComputedAttributeClassification.EXPOSE_PURE,
            compiled_expression=None,
            references=[
                ExpressionRef(name="my_calc", qualified_name="Pkg::part::my_calc"),
                ExpressionRef(name="efficiency", qualified_name="Lib::EffCalc::efficiency"),
            ],
        )

        # The catalog key should be "my_calc.efficiency"
        output_catalog = {
            "my_calc.efficiency": ("EffCalcModule", "Pkg__part__my_calc__efficiency", "root"),
        }

        channel = _resolve_expose_pure(ca, {"my_calc"}, output_catalog)
        assert channel == "Pkg__part__my_calc__efficiency"

    def test_missing_catalog_key_returns_none(self):
        """Returns None when catalog key not found."""
        ca = _make_computed_attr(
            "missing_out", "part", "Pkg::part",
            classification=ComputedAttributeClassification.EXPOSE_PURE,
            compiled_expression=None,
            references=[
                ExpressionRef(name="my_calc", qualified_name="Pkg::part::my_calc"),
                ExpressionRef(name="x", qualified_name="Lib::SomeCalc::x"),
            ],
        )

        # Empty catalog -- key won't be found
        channel = _resolve_expose_pure(ca, {"my_calc"}, {})
        assert channel is None

    def test_no_instance_ref_returns_none(self):
        """Returns None when no calc usage instance can be identified."""
        ca = _make_computed_attr(
            "bad_ref", "part", "Pkg::part",
            classification=ComputedAttributeClassification.EXPOSE_PURE,
            compiled_expression=None,
            references=[
                # Neither ref name is in calc_usage_names
                ExpressionRef(name="unknown1", qualified_name="Pkg::part::unknown1"),
                ExpressionRef(name="unknown2", qualified_name="Lib::SomeCalc::unknown2"),
            ],
        )

        channel = _resolve_expose_pure(ca, {"real_calc"}, {})
        assert channel is None


# ---------------------------------------------------------------------------
# Tests: Output Catalog Extension
# ---------------------------------------------------------------------------


class TestOutputCatalogExtension:
    """Test _extend_output_catalog_with_computed_attrs()."""

    def test_formula_output_added_to_catalog(self):
        """FORMULA+FULLY_COMPILABLE computed attr added to output catalog."""
        ca = _make_computed_attr("area", "probe_design", "Pkg::probe_design")

        catalog: dict[str, tuple[str, str, str]] = {}
        _extend_output_catalog_with_computed_attrs(catalog, [ca])

        key = "probe_design.area"
        assert key in catalog
        module_type, channel_name, field_name = catalog[key]
        assert "areaModule" in module_type  # lowercase because element name is "area"
        assert "area__area" in channel_name
        assert field_name == "root"

    def test_manual_required_excluded(self):
        """FORMULA with MANUAL_REQUIRED not added to catalog."""
        ca = _make_computed_attr(
            "broken", "part", "Pkg::part",
            compilability=Compilability.MANUAL_REQUIRED,
        )

        catalog: dict[str, tuple[str, str, str]] = {}
        _extend_output_catalog_with_computed_attrs(catalog, [ca])

        assert "part.broken" not in catalog

    def test_expose_pure_excluded(self):
        """EXPOSE_PURE not added to catalog (not a synthetic module)."""
        ca = _make_computed_attr(
            "alias", "part", "Pkg::part",
            classification=ComputedAttributeClassification.EXPOSE_PURE,
            compiled_expression=None,
        )

        catalog: dict[str, tuple[str, str, str]] = {}
        _extend_output_catalog_with_computed_attrs(catalog, [ca])

        assert "part.alias" not in catalog

    def test_existing_catalog_entries_preserved(self):
        """Extending catalog doesn't overwrite existing CalcUsage entries."""
        ca = _make_computed_attr("area", "part", "Pkg::part")

        catalog = {
            "my_calc.result": ("MyCalcModule", "Pkg__Part__my_calc__result", "root"),
        }
        _extend_output_catalog_with_computed_attrs(catalog, [ca])

        assert "my_calc.result" in catalog
        assert "part.area" in catalog


# ---------------------------------------------------------------------------
# Tests: Computed Attribute Module Building
# ---------------------------------------------------------------------------


class TestComputedAttrModule:
    """Test _build_computed_attr_module() output."""

    def test_simple_formula_module_structure(self):
        """area = length * width -> correct inputs, single output, naming."""
        ca = _make_computed_attr(
            "area", "probe_design", "AttrExprProbeDesign::probe_design",
            compiled_expression="(inputs.length * inputs.width)",
        )

        # Resolution map: length and width are literals (entry points)
        attr_resolution_map = {}

        entry_points: dict[str, EntryPoint] = {}

        design_attrs: dict[Path, list[DesignAttributeData]] = {}
        group_deriver = _make_mock_group_deriver()

        module = _build_computed_attr_module(
            ca, attr_resolution_map, entry_points,
            design_attrs, group_deriver,
        )

        # Naming
        assert module.name == "attrexprprobedesign__probe_design__area"
        assert "areaModule" in module.module_type  # lowercase element name
        assert module.is_computed_attribute is True
        assert module.compilability == Compilability.FULLY_COMPILABLE

        # Inputs: length and width
        assert len(module.inputs) == 2
        input_names = [inp.param_name for inp in module.inputs]
        assert "length" in input_names
        assert "width" in input_names

        # Output: single output
        assert len(module.outputs) == 1
        assert module.outputs[0].field_name == "root"
        assert "area__area" in module.outputs[0].channel_name

    def test_formula_chain_wiring(self):
        """cost = area * rate where area is FORMULA -> area input wired to formula channel."""
        ca_area = _make_computed_attr(
            "area", "part", "Pkg::part",
            compiled_expression="(inputs.length * inputs.width)",
        )
        ca_cost = _make_computed_attr(
            "cost", "part", "Pkg::part",
            compiled_expression="(inputs.area * inputs.rate)",
        )

        # Build resolution map with both formulas
        attr_resolution_map = _build_attribute_resolution_map(
            computed_attrs=[ca_area, ca_cost],
            design_attrs={},
            output_catalog={},
            calc_usage_names=set(),
        )

        entry_points: dict[str, EntryPoint] = {}

        design_attrs: dict[Path, list[DesignAttributeData]] = {}
        group_deriver = _make_mock_group_deriver()

        module = _build_computed_attr_module(
            ca_cost, attr_resolution_map, entry_points,
            design_attrs, group_deriver,
        )

        # Find the "area" input
        area_input = next(inp for inp in module.inputs if inp.param_name == "area")
        assert area_input.source.source_type == "module_output"
        assert "area__area" in area_input.source.producer_channel

        # "rate" should be an entry point (not in resolution map as formula)
        rate_input = next(inp for inp in module.inputs if inp.param_name == "rate")
        assert rate_input.source.source_type == "entry_point"

    def test_expose_alias_input_wiring(self):
        """FORMULA referencing EXPOSE_PURE attr -> wired to upstream calc channel."""
        # EXPOSE_PURE: p_alpha_out = alpha_split.p_alpha
        ca_expose = _make_computed_attr(
            "p_alpha_out", "plant", "Pkg::plant",
            classification=ComputedAttributeClassification.EXPOSE_PURE,
            compiled_expression=None,
            references=[
                ExpressionRef(name="alpha_split", qualified_name="Pkg::plant::alpha_split"),
                ExpressionRef(name="p_alpha", qualified_name="Lib::AlphaSplitCalc::p_alpha"),
            ],
        )

        # FORMULA: useful = p_alpha_out * efficiency
        ca_formula = _make_computed_attr(
            "useful", "plant", "Pkg::plant",
            compiled_expression="(inputs.p_alpha_out * inputs.efficiency)",
        )

        output_catalog = {
            "alpha_split.p_alpha": ("AlphaSplitModule", "Pkg__plant__alpha_split__p_alpha", "root"),
        }

        attr_resolution_map = _build_attribute_resolution_map(
            computed_attrs=[ca_expose, ca_formula],
            design_attrs={},
            output_catalog=output_catalog,
            calc_usage_names={"alpha_split"},
        )

        entry_points: dict[str, EntryPoint] = {}

        design_attrs: dict[Path, list[DesignAttributeData]] = {}
        group_deriver = _make_mock_group_deriver()

        module = _build_computed_attr_module(
            ca_formula, attr_resolution_map, entry_points,
            design_attrs, group_deriver,
        )

        # p_alpha_out input should be wired via EXPOSE_PURE alias
        p_alpha_input = next(inp for inp in module.inputs if inp.param_name == "p_alpha_out")
        assert p_alpha_input.source.source_type == "module_output"
        assert p_alpha_input.source.producer_channel == "Pkg__plant__alpha_split__p_alpha"

    def test_entry_point_created_for_literal_input(self):
        """Literal input creates entry point with correct qualified name."""
        ca = _make_computed_attr(
            "area", "probe_design", "AttrExprProbeDesign::probe_design",
            compiled_expression="(inputs.length * inputs.width)",
        )

        entry_points: dict[str, EntryPoint] = {}

        design_attrs: dict[Path, list[DesignAttributeData]] = {}
        group_deriver = _make_mock_group_deriver()

        _build_computed_attr_module(
            ca, {}, entry_points,
            design_attrs, group_deriver,
        )

        # Entry points should have been created for length and width
        assert any("length" in qn for qn in entry_points)
        assert any("width" in qn for qn in entry_points)

    def test_deduplicates_input_names(self):
        """Duplicate input names in expression -> single input."""
        ca = _make_computed_attr(
            "result", "part", "Pkg::part",
            compiled_expression="(inputs.x + inputs.x * inputs.y)",
        )

        entry_points: dict[str, EntryPoint] = {}
        module = _build_computed_attr_module(
            ca, {}, entry_points,
            {}, _make_mock_group_deriver(),
        )

        # x appears twice in expression but should only create one input
        input_names = [inp.param_name for inp in module.inputs]
        assert input_names.count("x") == 1
        assert "y" in input_names


# ---------------------------------------------------------------------------
# Tests: Unified Topological Sort
# ---------------------------------------------------------------------------


class TestUnifiedToposort:
    """Test _unified_topological_sort()."""

    def test_formula_before_dependent_calcusage(self):
        """FORMULA module ordered before CalcUsage that consumes its output."""
        # FORMULA module produces channel "part__area__area"
        formula_module = PipelineModule(
            name="part__area",
            module_type="part.AreaModule",
            inputs=[],
            outputs=[ModuleOutput(
                field_name="root", python_type="float",
                channel_name="part__area__area",
            )],
            execution_order=0,
            is_computed_attribute=True,
        )

        # CalcUsage module consumes "part__area__area"
        calc_module = PipelineModule(
            name="part__cost_calc",
            module_type="CostCalcModule",
            inputs=[ModuleInput(
                param_name="area",
                python_type="float",
                source=InputSource(
                    source_type="module_output",
                    producer_channel="part__area__area",
                ),
            )],
            outputs=[ModuleOutput(
                field_name="root", python_type="float",
                channel_name="part__cost_calc__cost",
            )],
            execution_order=0,
        )

        sorted_modules = _unified_topological_sort([calc_module, formula_module])

        assert sorted_modules[0].name == "part__area"
        assert sorted_modules[1].name == "part__cost_calc"
        assert sorted_modules[0].execution_order < sorted_modules[1].execution_order

    def test_formula_chain_ordering(self):
        """area -> cost chain: area.execution_order < cost.execution_order."""
        area_module = PipelineModule(
            name="part__area",
            module_type="part.AreaModule",
            inputs=[],
            outputs=[ModuleOutput(
                field_name="root", python_type="float",
                channel_name="part__area__area",
            )],
            execution_order=0,
            is_computed_attribute=True,
        )

        cost_module = PipelineModule(
            name="part__cost",
            module_type="part.CostModule",
            inputs=[ModuleInput(
                param_name="area",
                python_type="float",
                source=InputSource(
                    source_type="module_output",
                    producer_channel="part__area__area",
                ),
            )],
            outputs=[ModuleOutput(
                field_name="root", python_type="float",
                channel_name="part__cost__cost",
            )],
            execution_order=0,
            is_computed_attribute=True,
        )

        sorted_modules = _unified_topological_sort([cost_module, area_module])

        assert sorted_modules[0].name == "part__area"
        assert sorted_modules[1].name == "part__cost"

    def test_calcusage_only_preserves_dependency_order(self):
        """With no computed attrs, toposort respects dependency edges."""
        # Module A produces output consumed by Module B
        module_a = PipelineModule(
            name="module_a",
            module_type="ModuleAModule",
            inputs=[],
            outputs=[ModuleOutput(
                field_name="root", python_type="float",
                channel_name="module_a__result",
            )],
            execution_order=99,  # Wrong order initially
        )

        module_b = PipelineModule(
            name="module_b",
            module_type="ModuleBModule",
            inputs=[ModuleInput(
                param_name="x",
                python_type="float",
                source=InputSource(
                    source_type="module_output",
                    producer_channel="module_a__result",
                ),
            )],
            outputs=[ModuleOutput(
                field_name="root", python_type="float",
                channel_name="module_b__result",
            )],
            execution_order=0,  # Wrong order initially
        )

        sorted_modules = _unified_topological_sort([module_b, module_a])

        assert sorted_modules[0].name == "module_a"
        assert sorted_modules[1].name == "module_b"
        assert sorted_modules[0].execution_order == 0
        assert sorted_modules[1].execution_order == 1

    def test_independent_modules_stable(self):
        """Independent modules (no inter-dependencies) get sequential order."""
        module_x = PipelineModule(
            name="module_x",
            module_type="XModule",
            inputs=[],
            outputs=[ModuleOutput(
                field_name="root", python_type="float",
                channel_name="module_x__out",
            )],
            execution_order=0,
        )

        module_y = PipelineModule(
            name="module_y",
            module_type="YModule",
            inputs=[],
            outputs=[ModuleOutput(
                field_name="root", python_type="float",
                channel_name="module_y__out",
            )],
            execution_order=0,
        )

        sorted_modules = _unified_topological_sort([module_x, module_y])

        assert len(sorted_modules) == 2
        assert sorted_modules[0].execution_order == 0
        assert sorted_modules[1].execution_order == 1

    def test_three_level_chain(self):
        """A -> B -> C: correct ordering across 3 levels."""
        mod_a = PipelineModule(
            name="a", module_type="AModule",
            inputs=[],
            outputs=[ModuleOutput(field_name="root", python_type="float", channel_name="a__out")],
            execution_order=0,
        )
        mod_b = PipelineModule(
            name="b", module_type="BModule",
            inputs=[ModuleInput(
                param_name="x", python_type="float",
                source=InputSource(source_type="module_output", producer_channel="a__out"),
            )],
            outputs=[ModuleOutput(field_name="root", python_type="float", channel_name="b__out")],
            execution_order=0,
        )
        mod_c = PipelineModule(
            name="c", module_type="CModule",
            inputs=[ModuleInput(
                param_name="y", python_type="float",
                source=InputSource(source_type="module_output", producer_channel="b__out"),
            )],
            outputs=[ModuleOutput(field_name="root", python_type="float", channel_name="c__out")],
            execution_order=0,
        )

        sorted_modules = _unified_topological_sort([mod_c, mod_b, mod_a])

        names = [m.name for m in sorted_modules]
        assert names.index("a") < names.index("b") < names.index("c")

    def test_cycle_raises_circular_dependency_error(self):
        """Circular dependency between modules raises CircularDependencyError."""
        # Two modules where each depends on the other's output
        mod_a = PipelineModule(
            name="a", module_type="AModule",
            inputs=[ModuleInput(
                param_name="x", python_type="float",
                source=InputSource(source_type="module_output", producer_channel="b__out"),
            )],
            outputs=[ModuleOutput(field_name="root", python_type="float", channel_name="a__out")],
            execution_order=0,
        )
        mod_b = PipelineModule(
            name="b", module_type="BModule",
            inputs=[ModuleInput(
                param_name="y", python_type="float",
                source=InputSource(source_type="module_output", producer_channel="a__out"),
            )],
            outputs=[ModuleOutput(field_name="root", python_type="float", channel_name="b__out")],
            execution_order=0,
        )

        with pytest.raises(CircularDependencyError, match="Circular dependency"):
            _unified_topological_sort([mod_a, mod_b])


# ---------------------------------------------------------------------------
# Tests: Full Integration -- build_computation_graph with computed attrs
# ---------------------------------------------------------------------------


class TestBuildComputationGraphWithComputedAttrs:
    """Test build_computation_graph() with computed_attributes parameter."""

    def test_empty_computed_attrs_no_impact(self):
        """Empty computed_attributes list produces same result as None."""
        _ensure_backtracking_result_rebuilt()

        calc_def = CalculationDefinitionData(
            name="TestCalc",
            qualified_name="TestCalc",
            doc_comment="",
            calc_expressions=[],
            input_attributes=[],
            output_attributes=[
                AttributeInfo(name="result", sysml_type="Real", python_type="float"),
            ],
            references=[],
            source_file=Path("test.sysml"),
        )

        usage = CalcUsageData(
            instance_name="test_calc",
            calc_def_name="TestCalc",
            calc_def_qualified_name="TestCalc",
            module_type="TestCalcModule",
            qualified_name="test_calc",
        )

        result = _make_minimal_backtracking_result(usages=[usage])
        group_deriver = _make_mock_group_deriver()

        graph = build_computation_graph(
            result=result,
            calc_defs=[calc_def],
            design_attrs={},
            group_deriver=group_deriver,
            computed_attributes=[],
        )

        assert len(graph.modules) == 1
        assert graph.modules[0].is_computed_attribute is False

    def test_formula_module_appears_in_graph(self):
        """FORMULA computed attr produces a PipelineModule in the graph."""
        _ensure_backtracking_result_rebuilt()

        ca = _make_computed_attr(
            "area", "probe_design", "Pkg::probe_design",
            compiled_expression="(inputs.length * inputs.width)",
        )

        result = _make_minimal_backtracking_result()
        group_deriver = _make_mock_group_deriver()

        graph = build_computation_graph(
            result=result,
            calc_defs=[],
            design_attrs={},
            group_deriver=group_deriver,
            computed_attributes=[ca],
        )

        assert len(graph.modules) == 1
        module = graph.modules[0]
        assert module.is_computed_attribute is True
        assert module.compilability == Compilability.FULLY_COMPILABLE
        assert "area" in module.name

    def test_manual_required_formula_excluded_from_graph(self):
        """FORMULA with MANUAL_REQUIRED compilability doesn't produce a module."""
        _ensure_backtracking_result_rebuilt()

        ca = _make_computed_attr(
            "broken", "part", "Pkg::part",
            compilability=Compilability.MANUAL_REQUIRED,
        )

        result = _make_minimal_backtracking_result()
        group_deriver = _make_mock_group_deriver()

        graph = build_computation_graph(
            result=result,
            calc_defs=[],
            design_attrs={},
            group_deriver=group_deriver,
            computed_attributes=[ca],
        )

        assert len(graph.modules) == 0


# ---------------------------------------------------------------------------
# Tests: Bug 1 — FORMULA entry points appear in param_groups after Step 6.6
# ---------------------------------------------------------------------------


class TestParamGroupsRebuild:
    """Bug 1: FORMULA entry points must appear in entry_point_groups."""

    def test_formula_entry_points_in_param_groups(self):
        """After build_computation_graph, FORMULA module entry points appear
        in entry_point_groups (rebuilt at Step 6.6)."""
        _ensure_backtracking_result_rebuilt()

        # FORMULA: area = length * width (creates entry points for length, width)
        ca = _make_computed_attr(
            "area", "probe_design", "Pkg::probe_design",
            compiled_expression="(inputs.length * inputs.width)",
        )

        result = _make_minimal_backtracking_result()
        group_deriver = _make_mock_group_deriver()
        # derive_groups() returns groups that include the FORMULA input params
        from sysml_codegen.analysis.parameter_groups import DerivedParameterGroup, ParameterSource
        group_deriver.derive_groups.return_value = [
            DerivedParameterGroup(
                name="probe_design_params",
                class_name="ProbeDesignParams",
                source_type="design",
                source_identifier="test.sysml",
                parameters=[
                    ParameterSource(name="Pkg__probe_design__length", default_value=1.0),
                    ParameterSource(name="Pkg__probe_design__width", default_value=2.0),
                ],
            ),
        ]

        graph = build_computation_graph(
            result=result,
            calc_defs=[],
            design_attrs={},
            group_deriver=group_deriver,
            computed_attributes=[ca],
        )

        # Collect all EP names from entry_point_groups
        all_ep_names = {
            ep.qualified_name
            for pg in graph.entry_point_groups
            for ep in pg.parameters
        }

        # FORMULA inputs must appear
        assert "Pkg__probe_design__length" in all_ep_names
        assert "Pkg__probe_design__width" in all_ep_names

    def test_param_groups_empty_when_no_formula(self):
        """Without FORMULA attrs, param_groups has only backtracker EPs."""
        _ensure_backtracking_result_rebuilt()

        result = _make_minimal_backtracking_result()
        group_deriver = _make_mock_group_deriver()
        # derive_groups returns empty (no FORMULA EPs to add)
        group_deriver.derive_groups.return_value = []

        graph = build_computation_graph(
            result=result,
            calc_defs=[],
            design_attrs={},
            group_deriver=group_deriver,
            computed_attributes=[],
        )

        assert len(graph.entry_point_groups) == 0
