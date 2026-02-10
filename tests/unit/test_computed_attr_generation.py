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
from sysml_codegen.generation.registry import generate_registry_function
from sysml_codegen.generation.stencils import generate_backlog_report
from sysml_codegen.resolution.models import (
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
    is_computed_attribute: bool = False,
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
        is_computed_attribute=is_computed_attribute,
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
            is_computed_attribute=True,
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
            is_computed_attribute=False,
        )
        channel_field_map = {"my_calc__out": "root"}

        ctx = _module_to_context(module, channel_field_map)

        assert ctx["name"] == "MyCalcModule"
        assert "computed_attribute" not in ctx["name"]

    def test_type_field_unchanged(self):
        """The 'type' field always uses module_type regardless of is_computed_attribute."""
        module = _make_pipeline_module(
            name="part__area",
            module_type="part.AreaModule",
            is_computed_attribute=True,
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
        ca = _make_computed_attr("area", "part", "Pkg::part")

        report = generate_backlog_report(
            calc_defs=[],
            output_path=Path("test.md"),
            computed_attributes=[ca],
        )

        assert "1 computed attribute module(s) auto-implemented" in report

    def test_manual_required_not_counted(self):
        """MANUAL_REQUIRED FORMULA not counted as auto-implemented."""
        ca = _make_computed_attr(
            "broken", "part", "Pkg::part",
            compilability=Compilability.MANUAL_REQUIRED,
        )

        report = generate_backlog_report(
            calc_defs=[],
            output_path=Path("test.md"),
            computed_attributes=[ca],
        )

        assert "auto-implemented" not in report

    def test_no_computed_attrs_no_summary(self):
        """No computed attrs -> no auto-implemented summary line."""
        report = generate_backlog_report(
            calc_defs=[],
            output_path=Path("test.md"),
        )

        assert "auto-implemented" not in report

    def test_multiple_formula_attrs_counted(self):
        """Multiple FORMULA attrs produce correct count."""
        cas = [
            _make_computed_attr("area", "part", "Pkg::part"),
            _make_computed_attr("cost", "part", "Pkg::part"),
            _make_computed_attr("volume", "part", "Pkg::part"),
        ]

        report = generate_backlog_report(
            calc_defs=[],
            output_path=Path("test.md"),
            computed_attributes=cas,
        )

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
        ca = _make_computed_attr(
            "area", "part", "Pkg::part",
            compiled_expression="(inputs.length * inputs.width)",
        )

        code = generate_registry_function(
            calc_defs=[],
            package_name="test_pkg",
            template_env=env,
            output_path=Path("test_init.py"),
            entry_point_groups=[],
            exit_point_primitive_types=[],
            computed_attributes=[ca],
        )

        # derive_module_type produces lowercase class name from attr name
        assert "areaModule" in code
        assert "from test_pkg.modules." in code

    def test_manual_required_excluded_from_registry(self):
        """MANUAL_REQUIRED FORMULA not included in registry."""
        env = _get_template_env()
        ca = _make_computed_attr(
            "broken", "part", "Pkg::part",
            compilability=Compilability.MANUAL_REQUIRED,
        )

        code = generate_registry_function(
            calc_defs=[],
            package_name="test_pkg",
            template_env=env,
            output_path=Path("test_init.py"),
            entry_point_groups=[],
            exit_point_primitive_types=[],
            computed_attributes=[ca],
        )

        assert "BrokenModule" not in code

    def test_expose_pure_excluded_from_registry(self):
        """EXPOSE_PURE computed attrs not included in registry (no module)."""
        env = _get_template_env()
        ca = _make_computed_attr(
            "p_alpha_out", "part", "Pkg::part",
            classification=ComputedAttributeClassification.EXPOSE_PURE,
            compiled_expression=None,
        )

        code = generate_registry_function(
            calc_defs=[],
            package_name="test_pkg",
            template_env=env,
            output_path=Path("test_init.py"),
            entry_point_groups=[],
            exit_point_primitive_types=[],
            computed_attributes=[ca],
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
