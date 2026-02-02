"""Unit tests for registry generation — Gap 2 fixes."""
import pytest


class TestCollectExitPointTypes:
    """Tests for _collect_exit_point_primitive_types()."""

    def test_single_output_modules_produce_float(self):
        """Single-output modules with python_type='float' should produce 'Float'."""
        from sysml_codegen.generation.registry import _collect_exit_point_primitive_types
        from sysml_codegen.resolution.models import PipelineModule, ModuleOutput

        modules = [
            PipelineModule(
                name="test_module",
                module_type="TestModule",
                inputs=[],
                outputs=[
                    ModuleOutput(field_name="root", python_type="float", channel_name="test__result")
                ],
                execution_order=0,
            )
        ]

        types = _collect_exit_point_primitive_types(modules)
        assert "Float" in types

    def test_multi_output_modules_excluded(self):
        """Multi-output modules (field_name != 'root') should not add primitive types."""
        from sysml_codegen.generation.registry import _collect_exit_point_primitive_types
        from sysml_codegen.resolution.models import PipelineModule, ModuleOutput

        modules = [
            PipelineModule(
                name="test_module",
                module_type="TestModule",
                inputs=[],
                outputs=[
                    ModuleOutput(field_name="area", python_type="float", channel_name="test__area"),
                    ModuleOutput(field_name="cost", python_type="float", channel_name="test__cost"),
                ],
                execution_order=0,
            )
        ]

        types = _collect_exit_point_primitive_types(modules)
        assert len(types) == 0

    def test_deduplication(self):
        """Multiple single-output float modules should produce only one 'Float'."""
        from sysml_codegen.generation.registry import _collect_exit_point_primitive_types
        from sysml_codegen.resolution.models import PipelineModule, ModuleOutput

        modules = [
            PipelineModule(
                name=f"mod_{i}",
                module_type=f"Mod{i}Module",
                inputs=[],
                outputs=[
                    ModuleOutput(field_name="root", python_type="float", channel_name=f"mod{i}__out")
                ],
                execution_order=i,
            )
            for i in range(3)
        ]

        types = _collect_exit_point_primitive_types(modules)
        assert types == ["Float"]  # sorted, deduplicated


class TestRegistryTemplateRendering:
    """Tests for registry template rendering with exit point types."""

    def test_custom_schema_types_includes_exit_point_types(self):
        """CUSTOM_SCHEMA_TYPES should include both entry point and exit point types.

        FR-6: Template must render exit point types alongside entry point schemas.
        AC-3: Generated __init__.py includes Float in CUSTOM_SCHEMA_TYPES.
        """
        import jinja2
        from pathlib import Path

        template_dir = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        template = env.get_template("registry_function.py.jinja2")
        rendered = template.render(
            function_name="create_test_registry",
            all_modules=[],
            imports=["from simkit.core.registry_builder import create_registry",
                     "from simkit.core.pipeline_registry import PipelineModuleRegistry"],
            schema_imports=["from test_pkg.schemas.design_params import DesignParams as DesignParams"],
            parameter_groups=["DesignParams"],
            exit_point_types=["Float"],
            package_name="test_pkg",
        )

        assert "CUSTOM_SCHEMA_TYPES" in rendered
        assert "DesignParams" in rendered
        assert "Float" in rendered
        assert "from test_pkg.primitives import Float" in rendered

    def test_no_exit_point_types_still_renders(self):
        """Template should render correctly without exit point types."""
        import jinja2
        from pathlib import Path

        template_dir = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        template = env.get_template("registry_function.py.jinja2")
        rendered = template.render(
            function_name="create_test_registry",
            all_modules=[],
            imports=["from simkit.core.registry_builder import create_registry",
                     "from simkit.core.pipeline_registry import PipelineModuleRegistry"],
            schema_imports=[],
            parameter_groups=[],
            exit_point_types=[],
            package_name="test_pkg",
        )

        assert "CUSTOM_SCHEMA_TYPES" not in rendered
        assert "primitives" not in rendered
