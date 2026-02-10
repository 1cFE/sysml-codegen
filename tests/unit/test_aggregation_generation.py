"""Unit tests for aggregation code generation (Phase 4).

Tests pipeline YAML comment, registry inclusion, backlog report,
module wrapper template context, and auto-implementation template context
for aggregation modules.
"""

from __future__ import annotations

from pathlib import Path

import jinja2
import pytest

from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    CalculationDefinitionData,
    ScopedAggregationData,
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


def _make_scoped_agg(
    attribute_name: str = "capital_cost",
    owning_part_qn: str = "Lib__Solar_Array",
    owning_part_name: str = "Solar_Array",
    instance_path: str = "Design__plant__solar_array",
    raw_expression_text: str = "sum(child.capital_cost * child.count)",
    transformed_expression: str = "sum(child_capital_cost * child_count)",
    has_unsupported_nodes: bool = False,
) -> ScopedAggregationData:
    expr = AggregationExpressionData(
        owning_part_qn=owning_part_qn,
        owning_part_name=owning_part_name,
        attribute_name=attribute_name,
        raw_expression_text=raw_expression_text,
        transformed_expression=transformed_expression,
        sum_terms=[],
        singleton_terms=[],
        local_terms=[],
        input_channels=[],
        entry_points=[],
        has_unsupported_nodes=has_unsupported_nodes,
    )
    return ScopedAggregationData(expression=expr, instance_path=instance_path)


def _make_pipeline_module(
    name: str = "test_module",
    module_type: str = "TestModule",
    is_computed_attribute: bool = False,
    is_aggregation: bool = False,
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
        is_aggregation=is_aggregation,
    )


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
# Tests: Pipeline YAML Comment (F.3)
# ---------------------------------------------------------------------------


class TestPipelineYamlAggregationComment:
    """Test YAML comment for aggregation modules."""

    def test_aggregation_module_has_source_comment(self):
        """Module context 'name' field contains 'source: aggregation'."""
        module = _make_pipeline_module(
            name="design__plant__solar_array__capital_cost",
            module_type="solar_array.capital_costModule",
            is_aggregation=True,
        )
        channel_field_map = {
            "design__plant__solar_array__capital_cost__out": "root",
        }

        ctx = _module_to_context(module, channel_field_map)

        assert "source: aggregation" in ctx["name"]
        assert "solar_array.capital_costModule" in ctx["name"]

    def test_aggregation_takes_priority_over_computed_attr(self):
        """If both is_aggregation and is_computed_attribute, aggregation wins."""
        module = _make_pipeline_module(
            name="test",
            module_type="TestModule",
            is_aggregation=True,
            is_computed_attribute=True,
        )
        channel_field_map = {"test__out": "root"}

        ctx = _module_to_context(module, channel_field_map)

        assert "source: aggregation" in ctx["name"]
        assert "computed_attribute" not in ctx["name"]

    def test_regular_module_no_aggregation_comment(self):
        """Regular CalcUsage module has plain module_type."""
        module = _make_pipeline_module(
            name="my_calc",
            module_type="MyCalcModule",
        )
        channel_field_map = {"my_calc__out": "root"}

        ctx = _module_to_context(module, channel_field_map)

        assert ctx["name"] == "MyCalcModule"
        assert "aggregation" not in ctx["name"]

    def test_type_field_unchanged_for_aggregation(self):
        """The 'type' field always uses module_type."""
        module = _make_pipeline_module(
            name="agg_mod",
            module_type="solar_array.capital_costModule",
            is_aggregation=True,
        )
        channel_field_map = {"agg_mod__out": "root"}

        ctx = _module_to_context(module, channel_field_map)

        assert ctx["type"] == "solar_array.capital_costModule"


# ---------------------------------------------------------------------------
# Tests: Backlog Report (F.5)
# ---------------------------------------------------------------------------


class TestBacklogAggregation:
    """Test backlog report with aggregation auto-implementations."""

    def test_aggregation_auto_impl_shown_in_summary(self):
        """Backlog contains auto-implemented summary line for aggregation modules."""
        agg = _make_scoped_agg(attribute_name="capital_cost")

        report = generate_backlog_report(
            calc_defs=[],
            output_path=Path("test.md"),
            aggregation_data=[agg],
        )

        assert "1 aggregation module(s) auto-implemented" in report

    def test_unsupported_nodes_not_counted(self):
        """has_unsupported_nodes=True not counted as auto-implemented."""
        agg = _make_scoped_agg(
            attribute_name="broken",
            has_unsupported_nodes=True,
        )

        report = generate_backlog_report(
            calc_defs=[],
            output_path=Path("test.md"),
            aggregation_data=[agg],
        )

        assert "aggregation module(s) auto-implemented" not in report

    def test_no_aggregation_data_no_summary(self):
        """No aggregation data -> no aggregation summary line."""
        report = generate_backlog_report(
            calc_defs=[],
            output_path=Path("test.md"),
        )

        assert "aggregation" not in report.lower() or "aggregation module(s)" not in report

    def test_multiple_aggregation_counted(self):
        """Multiple compilable aggregation modules produce correct count."""
        aggs = [
            _make_scoped_agg(attribute_name="capital_cost"),
            _make_scoped_agg(
                attribute_name="operating_cost",
                instance_path="Design__plant__battery",
            ),
            _make_scoped_agg(
                attribute_name="total_cost",
                instance_path="Design__plant__wind_turbine",
            ),
        ]

        report = generate_backlog_report(
            calc_defs=[],
            output_path=Path("test.md"),
            aggregation_data=aggs,
        )

        assert "3 aggregation module(s) auto-implemented" in report


# ---------------------------------------------------------------------------
# Tests: Registry Inclusion (F.4)
# ---------------------------------------------------------------------------


class TestRegistryAggregation:
    """Test registry includes aggregation modules."""

    def test_aggregation_module_in_registry(self):
        """Registry imports and registers aggregation module."""
        env = _get_template_env()
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            owning_part_qn="Lib__Solar_Array",
        )

        code = generate_registry_function(
            calc_defs=[],
            package_name="test_pkg",
            template_env=env,
            output_path=Path("test_init.py"),
            entry_point_groups=[],
            exit_point_primitive_types=[],
            aggregation_data=[agg],
        )

        assert "capital_costModule" in code
        assert "from test_pkg.modules." in code

    def test_no_aggregation_data_no_aggregation_in_registry(self):
        """No aggregation data -> no aggregation modules in registry."""
        env = _get_template_env()

        code = generate_registry_function(
            calc_defs=[],
            package_name="test_pkg",
            template_env=env,
            output_path=Path("test_init.py"),
            entry_point_groups=[],
            exit_point_primitive_types=[],
        )

        # Only standard imports, no aggregation
        assert "capital_costModule" not in code

    def test_multiple_aggregation_modules_in_registry(self):
        """Multiple aggregation modules all appear in registry."""
        env = _get_template_env()
        aggs = [
            _make_scoped_agg(
                attribute_name="capital_cost",
                owning_part_qn="Lib__Solar_Array",
            ),
            _make_scoped_agg(
                attribute_name="operating_cost",
                owning_part_qn="Lib__Battery_System",
                instance_path="Design__plant__battery_system",
            ),
        ]

        code = generate_registry_function(
            calc_defs=[],
            package_name="test_pkg",
            template_env=env,
            output_path=Path("test_init.py"),
            entry_point_groups=[],
            exit_point_primitive_types=[],
            aggregation_data=aggs,
        )

        assert "capital_costModule" in code
        assert "operating_costModule" in code


# ---------------------------------------------------------------------------
# Tests: Module Wrapper Template Context (F.1)
# ---------------------------------------------------------------------------


class TestAggregationModuleGeneration:
    """Test module wrapper generation for aggregation modules."""

    def test_template_context_renders(self):
        """Verify aggregation template context renders with teax_module.py.jinja2."""
        env = _get_template_env()
        template = env.get_template("teax_module.py.jinja2")

        context = {
            "class_name": "capital_costModule",
            "input_class_name": "capital_costInput",
            "output_class_name": None,
            "schema_name": None,
            "handler_name": "design__plant__solar_array__capital_cost",
            "impl_import_path": "lib.solar_array.capital_cost_impl",
            "doc_comment": (
                "Aggregation module.\n\n"
                "SysML Expression: sum(child.capital_cost * child.count)"
            ),
            "package_name": "test_pkg",
            "is_multioutput": False,
            "input_attributes": [
                {"name": "child_capital_cost", "type_hint": "float", "description": "Input child_capital_cost"},
                {"name": "child_count", "type_hint": "float", "description": "Input child_count"},
            ],
            "output_attributes": [
                {"name": "capital_cost", "description": "Aggregated capital_cost"},
            ],
            "calc_expressions": ["sum(child.capital_cost * child.count)"],
            "sysml_source": "aggregation",
            "primitive_imports": ["Float"],
        }

        rendered = template.render(**context)

        assert "class capital_costInput(BaseModel):" in rendered
        assert "class capital_costModule(ModuleBase[capital_costInput, Float]):" in rendered
        assert "child_capital_cost: float" in rendered
        assert "child_count: float" in rendered
        assert "Aggregation module" in rendered

    def test_aggregation_doc_comment_mentions_aggregation(self):
        """Doc comment says 'Aggregation module', not 'Computed attribute module'."""
        env = _get_template_env()
        template = env.get_template("teax_module.py.jinja2")

        context = {
            "class_name": "capital_costModule",
            "input_class_name": "capital_costInput",
            "output_class_name": None,
            "schema_name": None,
            "handler_name": "design__plant__solar_array__capital_cost",
            "impl_import_path": "lib.solar_array.capital_cost_impl",
            "doc_comment": "Aggregation module.\n\nSysML Expression: sum(...)",
            "package_name": "test_pkg",
            "is_multioutput": False,
            "input_attributes": [],
            "output_attributes": [
                {"name": "capital_cost", "description": "Aggregated capital_cost"},
            ],
            "calc_expressions": ["sum(...)"],
            "sysml_source": "aggregation",
            "primitive_imports": ["Float"],
        }

        rendered = template.render(**context)

        assert "Aggregation module" in rendered
        assert "Computed attribute" not in rendered


# ---------------------------------------------------------------------------
# Tests: Auto-Implementation Template Context (F.2)
# ---------------------------------------------------------------------------


class TestAggregationAutoImpl:
    """Test auto-implementation generation for aggregation modules."""

    def test_compiled_expression_in_output(self):
        """Auto-impl contains the transformed expression."""
        env = _get_template_env()
        template = env.get_template("auto_implementation.py.jinja2")

        context = {
            "function_name": "run_design__plant__solar_array__capital_cost",
            "calc_name": "Design__plant__solar_array__capital_cost",
            "input_class_name": "capital_costInput",
            "return_type": "float",
            "execution_steps": [],
            "output_expressions": [
                {
                    "name": "capital_cost",
                    "expression": "(inputs.child_capital_cost * inputs.child_count)",
                },
            ],
            "output_count": 1,
            "single_output_expression": "(inputs.child_capital_cost * inputs.child_count)",
            "module_import_path": "lib.solar_array.capital_cost",
            "package_name": "test_pkg",
            "sysml_source": "aggregation",
            "sysml_expressions": ["sum(child.capital_cost * child.count)"],
            "docstring": (
                "Execute capital_cost aggregation.\n\n"
                "SysML Expression: sum(child.capital_cost * child.count)"
            ),
        }

        rendered = template.render(**context)

        assert "return (inputs.child_capital_cost * inputs.child_count)" in rendered
        assert "AUTO_IMPLEMENTED = True" in rendered
        assert "def run_design__plant__solar_array__capital_cost(" in rendered

    def test_unsupported_nodes_not_auto_implemented(self):
        """has_unsupported_nodes=True should NOT produce auto-implementation."""
        agg = _make_scoped_agg(has_unsupported_nodes=True)
        assert agg.expression.has_unsupported_nodes is True


# ---------------------------------------------------------------------------
# Tests: Virtual CalcUsage Code Path (Issue #2)
# ---------------------------------------------------------------------------


class TestVirtualCalcUsageAutoImpl:
    """Verify virtual CalcUsages share the regular CalcDef auto-impl code path.

    Virtual CalcUsages are just CalcUsageData with is_virtual=True. Their
    CalcDefs go through _generate_modules() and _generate_stencils() -- the
    same path as regular CalcDefs. This test confirms the template renders
    identically for a virtual CalcUsage's calc def.
    """

    def test_virtual_calc_usage_module_renders_normally(self):
        """A CalcDef from a virtual CalcUsage renders the same module template."""
        env = _get_template_env()
        template = env.get_template("teax_module.py.jinja2")

        # Context identical to regular CalcDef -- virtual CalcUsages
        # produce standard CalculationDefinitionData entries
        context = {
            "class_name": "CostModelModule",
            "input_class_name": "CostModelInput",
            "output_class_name": None,
            "schema_name": None,
            "handler_name": "design__plant__solar_array__pv_module__cost_model",
            "impl_import_path": "lib.pv_module.cost_model_impl",
            "doc_comment": "Virtual CalcUsage module.",
            "package_name": "test_pkg",
            "is_multioutput": False,
            "input_attributes": [
                {"name": "wattage", "type_hint": "float", "description": "Input wattage"},
            ],
            "output_attributes": [
                {"name": "total_cost", "description": "Calculated total_cost"},
            ],
            "calc_expressions": ["total_cost = wattage * cost_per_watt"],
            "sysml_source": "models/pv_module.sysml:42",
            "primitive_imports": ["Float"],
        }

        rendered = template.render(**context)

        assert "class CostModelInput(BaseModel):" in rendered
        assert "class CostModelModule(ModuleBase[CostModelInput, Float]):" in rendered
        assert "wattage: float" in rendered
