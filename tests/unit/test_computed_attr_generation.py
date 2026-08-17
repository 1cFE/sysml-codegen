"""Unit tests for computed attribute code generation (Phase 4).

Tests module wrapper generation, auto-implementation generation,
pipeline YAML comment, registry inclusion, and backlog report
for FORMULA computed attributes.
"""

from __future__ import annotations

from pathlib import Path

import jinja2
import pytest

from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ComputedAttributeData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.generation.pipeline import _module_to_context
from sysml_codegen.generation.registry import (
    _collect_exit_point_primitive_types,
    generate_registry,
)
from sysml_codegen.generation.stencils import generate_backlog_report
from sysml_codegen.resolution.models import (
    ComputationGraph,
    InputSource,
    ModuleInput,
    ModuleKind,
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
) -> ComputedAttributeData:
    if compiled_expression is None and classification == ComputedAttributeClassification.FORMULA:
        compiled_expression = f"(inputs.{name}_input)"
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
        compiled_expression=compiled_expression,
    )


def _make_pipeline_module(
    name: str = "test_module",
    module_type: str = "TestModule",
    module_kind: ModuleKind = ModuleKind.CALCULATION,
) -> PipelineModule:
    return PipelineModule(
        name=name,
        module_type=module_type,
        inputs=[],
        outputs=[ModuleOutput(
            field_name="root", python_type="float",
            channel_name=f"{name}__out",
        )],
        execution_order=0,
        module_kind=module_kind,
    )


def _make_formula_module(
    attr_name: str = "area",
    owning_part_qn: str = "Pkg::part",
    auto_impl: bool = True,
) -> PipelineModule:
    """Build a PipelineModule for a FORMULA computed attribute."""
    owning_part_name = owning_part_qn.split("::")[-1]
    name = f"{owning_part_qn.replace('::', '__').lower()}__{attr_name}"
    module_type = f"{owning_part_name.lower()}.{attr_name}Module"
    return PipelineModule(
        name=name,
        module_type=module_type,
        inputs=[],
        outputs=[ModuleOutput(
            field_name="root", python_type="float",
            channel_name=f"{name}__out",
        )],
        execution_order=0,
        module_kind=ModuleKind.FORMULA,
        calc_def_name=attr_name,
        calc_def_qualified_name=owning_part_qn.replace("::", "__"),
        auto_impl_context={"execution_steps": [], "output_expressions": [{"name": attr_name, "expression": f"(inputs.{attr_name}_input)"}], "output_count": 1, "single_output_expression": f"(inputs.{attr_name}_input)"} if auto_impl else None,
    )


def _make_graph(modules: list[PipelineModule]) -> ComputationGraph:
    return ComputationGraph(
        modules=modules,
        entry_point_groups=[],
        execution_order=[m.name for m in modules],
    )


# ---------------------------------------------------------------------------
# Tests: Pipeline YAML Comment
# ---------------------------------------------------------------------------


class TestPipelineYamlComment:
    """Test YAML comment for computed attr modules."""

    def test_computed_attr_module_has_source_comment(self):
        """Module context 'name' field contains 'source: computed_attribute'."""
        module = _make_pipeline_module(
            name="part__area",
            module_type="part.AreaModule",
            module_kind=ModuleKind.FORMULA,
        )
        channel_field_map = {"part__area__out": "root"}

        ctx = _module_to_context(module, channel_field_map)

        assert "source: computed_attribute" in ctx["name"]
        assert "part.AreaModule" in ctx["name"]

    def test_calcusage_module_no_source_comment(self):
        """Regular CalcUsage module has plain module_type as name."""
        module = _make_pipeline_module(
            name="my_calc",
            module_type="MyCalcModule",
            module_kind=ModuleKind.CALCULATION,
        )
        channel_field_map = {"my_calc__out": "root"}

        ctx = _module_to_context(module, channel_field_map)

        assert ctx["name"] == "MyCalcModule"
        assert "computed_attribute" not in ctx["name"]

    def test_type_field_unchanged(self):
        """The 'type' field always uses module_type regardless of module_kind."""
        module = _make_pipeline_module(
            name="part__area",
            module_type="part.AreaModule",
            module_kind=ModuleKind.FORMULA,
        )
        channel_field_map = {"part__area__out": "root"}

        ctx = _module_to_context(module, channel_field_map)

        assert ctx["type"] == "part.AreaModule"


# ---------------------------------------------------------------------------
# Tests: Backlog Report
# ---------------------------------------------------------------------------


class TestBacklogComputedAttrs:
    """Test backlog report with computed attributes."""

    def test_computed_attrs_shown_as_auto_implemented(self):
        """Backlog contains auto-implemented summary line for computed attrs."""
        module = _make_formula_module("area", "Pkg::part")
        graph = _make_graph([module])

        report = generate_backlog_report(graph, Path("test.md"))

        assert "1 computed attribute module(s) auto-implemented" in report

    def test_manual_required_not_counted(self):
        """MANUAL_REQUIRED FORMULA (no auto_impl_context) not counted as auto-implemented."""
        module = _make_formula_module("broken", "Pkg::part", auto_impl=False)
        graph = _make_graph([module])

        report = generate_backlog_report(graph, Path("test.md"))

        assert "auto-implemented" not in report

    def test_no_computed_attrs_no_summary(self):
        """No computed attrs -> no auto-implemented summary line."""
        graph = _make_graph([])

        report = generate_backlog_report(graph, Path("test.md"))

        assert "auto-implemented" not in report

    def test_multiple_formula_attrs_counted(self):
        """Multiple FORMULA attrs produce correct count."""
        modules = [
            _make_formula_module("area", "Pkg::part"),
            _make_formula_module("cost", "Pkg::part"),
            _make_formula_module("volume", "Pkg::part"),
        ]
        graph = _make_graph(modules)

        report = generate_backlog_report(graph, Path("test.md"))

        assert "3 computed attribute module(s) auto-implemented" in report


# ---------------------------------------------------------------------------
# Template environment helper
# ---------------------------------------------------------------------------


def _get_template_env() -> jinja2.Environment:
    """Create Jinja2 environment pointing at package templates."""
    template_dir = (
        Path(__file__).parent.parent.parent
        / "src"
        / "sysml_codegen"
        / "templates"
    )
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


# ---------------------------------------------------------------------------
# Tests: Module Wrapper Generation
# ---------------------------------------------------------------------------


class TestComputedAttrModuleGeneration:
    """Test module wrapper generation for FORMULA computed attrs."""

    def test_template_context_fields(self):
        """Verify template context has all required fields for teax_module.py.jinja2."""
        env = _get_template_env()
        template = env.get_template("teax_module.py.jinja2")

        # Build the same context dict that _generate_computed_attr_modules() builds
        context = {
            "class_name": "AreaModule",
            "input_class_name": "AreaInput",
            "output_class_name": None,
            "schema_name": None,
            "handler_name": "pkg__part__area",
            "impl_import_path": "pkg.part.area_impl",
            "doc_comment": "Computed attribute module.\n\nSysML Expression: area = length * width",
            "package_name": "test_pkg",
            "is_multioutput": False,
            "input_attributes": [
                {"name": "length", "type_hint": "Float", "description": "Input length"},
                {"name": "width", "type_hint": "Float", "description": "Input width"},
            ],
            "output_attributes": [
                {"name": "area", "description": "Computed area"},
            ],
            "calc_expressions": ["area = length * width"],
            "sysml_source": "unknown:0",
            "primitive_imports": ["Float"],
        }

        rendered = template.render(**context)

        # Verify key structural elements
        assert "class AreaInput(BaseModel):" in rendered
        assert "class AreaModule(ModuleBase[AreaInput, Float]):" in rendered
        assert "length: Float" in rendered
        assert "width: Float" in rendered
        assert "run_pkg__part__area" in rendered
        assert "test_pkg.handwritten.pkg.part.area_impl" in rendered
        assert "area = length * width" in rendered

    def test_single_output_uses_float_not_multioutput(self):
        """Computed attr modules are single-output and use Float, not MultiOutput."""
        env = _get_template_env()
        template = env.get_template("teax_module.py.jinja2")

        context = {
            "class_name": "CostModule",
            "input_class_name": "CostInput",
            "output_class_name": None,
            "schema_name": None,
            "handler_name": "pkg__part__cost",
            "impl_import_path": "pkg.part.cost_impl",
            "doc_comment": "Computed attribute module.",
            "package_name": "test_pkg",
            "is_multioutput": False,
            "input_attributes": [
                {"name": "area", "type_hint": "Float", "description": "Input area"},
                {"name": "rate", "type_hint": "Float", "description": "Input rate"},
            ],
            "output_attributes": [
                {"name": "cost", "description": "Computed cost"},
            ],
            "calc_expressions": ["cost = area * rate"],
            "sysml_source": "unknown:0",
            "primitive_imports": ["Float"],
        }

        rendered = template.render(**context)

        assert "ModuleBase[CostInput, Float]" in rendered
        assert "ModuleResult(data=Float(cost))" in rendered
        # Class definition uses Float, not a MultiOutput schema type
        assert "ModuleBase[CostInput, CostOutput]" not in rendered


# ---------------------------------------------------------------------------
# Tests: Auto-Implementation Generation
# ---------------------------------------------------------------------------


class TestComputedAttrAutoImpl:
    """Test auto-implementation generation."""

    def test_compiled_expression_in_output(self):
        """Auto-impl contains the compiled expression from ComputedAttributeData."""
        env = _get_template_env()
        template = env.get_template("auto_implementation.py.jinja2")

        context = {
            "function_name": "run_pkg__part__area",
            "calc_name": "Pkg__part__area",
            "input_class_name": "AreaInput",
            "return_type": "float",
            "execution_steps": [],
            "output_expressions": [
                {"name": "area", "expression": "(inputs.length * inputs.width)"},
            ],
            "output_count": 1,
            "single_output_expression": "(inputs.length * inputs.width)",
            "module_import_path": "pkg.part.area",
            "package_name": "test_pkg",
            "sysml_source": "unknown:0",
            "sysml_expressions": ["area = length * width"],
            "docstring": "Execute area computed attribute.\n\nSysML Expression: area = length * width",
        }

        rendered = template.render(**context)

        assert "return (inputs.length * inputs.width)" in rendered
        assert "AUTO_IMPLEMENTED = True" in rendered
        assert "def run_pkg__part__area(inputs: AreaInput) -> float:" in rendered

    def test_single_output_template_path(self):
        """Uses single_output_expression, output_count=1 (no tuple return)."""
        env = _get_template_env()
        template = env.get_template("auto_implementation.py.jinja2")

        context = {
            "function_name": "run_pkg__part__p_net_kw",
            "calc_name": "Pkg__part__p_net_kw",
            "input_class_name": "PNetKwInput",
            "return_type": "float",
            "execution_steps": [],
            "output_expressions": [
                {"name": "p_net_kw", "expression": "(inputs.p_net_mw * 1000.0)"},
            ],
            "output_count": 1,
            "single_output_expression": "(inputs.p_net_mw * 1000.0)",
            "module_import_path": "pkg.part.p_net_kw",
            "package_name": "test_pkg",
            "sysml_source": "unknown:0",
            "sysml_expressions": ["p_net_kw = p_net_mw * 1000.0"],
            "docstring": "Execute p_net_kw computed attribute.",
        }

        rendered = template.render(**context)

        # Single output: direct return, no tuple
        assert "return (inputs.p_net_mw * 1000.0)" in rendered
        assert "return (" not in rendered.replace(
            "return (inputs.p_net_mw * 1000.0)", ""
        )
        assert "from test_pkg.modules.pkg.part.p_net_kw import PNetKwInput" in rendered


# ---------------------------------------------------------------------------
# Tests: Registry Inclusion
# ---------------------------------------------------------------------------


class TestRegistryInclusion:
    """Test module registry includes computed attrs."""

    def test_computed_attr_in_registry(self):
        """Registry imports and registers computed attr module."""
        env = _get_template_env()
        module = _make_formula_module("area", "Pkg::part")
        graph = _make_graph([module])

        code = generate_registry(
            graph=graph,
            package_name="test_pkg",
            template_env=env,
            output_path=Path("test_init.py"),
            exit_point_primitive_types=_collect_exit_point_primitive_types(graph.modules),
        )

        assert "areaModule" in code
        assert "from test_pkg.modules." in code

    def test_manual_required_excluded_from_registry(self):
        """MANUAL_REQUIRED FORMULA (no auto_impl_context) still included in registry.

        Note: The registry includes ALL FORMULA modules regardless of compilability.
        Only EXPOSE_PURE modules were excluded. With graph-only generation, all
        FORMULA PipelineModules in the graph are included.
        """
        env = _get_template_env()
        module = _make_formula_module("broken", "Pkg::part", auto_impl=False)
        graph = _make_graph([module])

        code = generate_registry(
            graph=graph,
            package_name="test_pkg",
            template_env=env,
            output_path=Path("test_init.py"),
            exit_point_primitive_types=_collect_exit_point_primitive_types(graph.modules),
        )

        # FORMULA modules are always in the graph and thus always in the registry
        assert "brokenModule" in code

    def test_expose_pure_excluded_from_registry(self):
        """EXPOSE_PURE computed attrs not in graph, not in registry.

        Note: EXPOSE_PURE attributes are never added to the ComputationGraph
        as PipelineModules, so they cannot appear in the registry. An empty
        graph produces no modules in the registry.
        """
        env = _get_template_env()
        graph = _make_graph([])

        code = generate_registry(
            graph=graph,
            package_name="test_pkg",
            template_env=env,
            output_path=Path("test_init.py"),
            exit_point_primitive_types=_collect_exit_point_primitive_types(graph.modules),
        )

        assert "PAlphaOutModule" not in code


# ---------------------------------------------------------------------------
# Tests: FORMULA Module Input Type (Bug 3)
# ---------------------------------------------------------------------------


class TestFormulaModuleInputType:
    """Bug 3: FORMULA input type must be 'float', not 'Float'."""

    def test_formula_module_inputs_use_float_primitive(self):
        """FORMULA module inputs should use 'float' (primitive), not 'Float' (RootModel)."""
        env = _get_template_env()
        template = env.get_template("teax_module.py.jinja2")

        context = {
            "class_name": "PowerMwModule",
            "input_class_name": "PowerMwInput",
            "output_class_name": None,
            "schema_name": None,
            "handler_name": "pkg__plant__power_mw",
            "impl_import_path": "pkg.plant.power_mw_impl",
            "doc_comment": "Computed attribute module.",
            "package_name": "test_pkg",
            "is_multioutput": False,
            "input_attributes": [
                {"name": "capacity", "type_hint": "float", "description": "Input capacity"},
                {"name": "factor", "type_hint": "float", "description": "Input factor"},
            ],
            "output_attributes": [
                {"name": "power_mw", "description": "Computed power_mw"},
            ],
            "calc_expressions": ["power_mw = capacity * factor"],
            "sysml_source": "unknown:0",
            "primitive_imports": ["Float"],
        }

        rendered = template.render(**context)

        # Input fields must use float (primitive), not Float (RootModel)
        assert "capacity: float" in rendered
        assert "factor: float" in rendered
        # Output type is still Float (RootModel[float])
        assert "ModuleBase[PowerMwInput, Float]" in rendered
