"""Unit tests for registry generation — Gap 2 fixes."""
from pathlib import Path

import jinja2


class TestRequiredExitPointTypes:
    """Tests for graph-derived exit-point wrapper authority."""

    def test_single_output_modules_produce_float(self):
        """Single-output modules with python_type='float' should produce 'Float'."""
        from sysml_codegen.generation.registry import required_exit_point_wrapper_types
        from sysml_codegen.resolution.models import (
            ComputationGraph,
            ModuleKind,
            ModuleOutput,
            PipelineModule,
        )

        modules = [
            PipelineModule(
                name="test_module",
                module_type="TestModule",
                inputs=[],
                outputs=[
                    ModuleOutput(
                        field_name="root",
                        python_type="float",
                        channel_name="test__result",
                    )
                ],
                execution_order=0,
                module_kind=ModuleKind.CALCULATION,
            )
        ]

        graph = ComputationGraph(
            modules=modules,
            entry_point_groups=[],
            execution_order=["test_module"],
        )
        types = required_exit_point_wrapper_types(graph)
        assert "Float" in types

    def test_multi_output_modules_excluded(self):
        """Multi-output modules (field_name != 'root') should not add primitive types."""
        from sysml_codegen.generation.registry import required_exit_point_wrapper_types
        from sysml_codegen.resolution.models import (
            ComputationGraph,
            ModuleKind,
            ModuleOutput,
            PipelineModule,
        )

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
                module_kind=ModuleKind.CALCULATION,
            )
        ]

        graph = ComputationGraph(
            modules=modules,
            entry_point_groups=[],
            execution_order=["test_module"],
        )
        types = required_exit_point_wrapper_types(graph)
        assert len(types) == 0

    def test_deduplication(self):
        """Multiple single-output float modules should produce only one 'Float'."""
        from sysml_codegen.generation.registry import required_exit_point_wrapper_types
        from sysml_codegen.resolution.models import (
            ComputationGraph,
            ModuleKind,
            ModuleOutput,
            PipelineModule,
        )

        modules = [
            PipelineModule(
                name=f"mod_{i}",
                module_type=f"Mod{i}Module",
                inputs=[],
                outputs=[
                    ModuleOutput(
                        field_name="root",
                        python_type="float",
                        channel_name=f"mod{i}__out",
                    )
                ],
                execution_order=i,
                module_kind=ModuleKind.CALCULATION,
            )
            for i in range(3)
        ]

        graph = ComputationGraph(
            modules=modules,
            entry_point_groups=[],
            execution_order=[module.name for module in modules],
        )
        types = required_exit_point_wrapper_types(graph)
        assert types == ("Float",)  # sorted, deduplicated


class TestRegistryTemplateRendering:
    """Tests for graph-derived registry rendering with exit point types."""

    @staticmethod
    def _render(tmp_path: Path, *root_types: str) -> str:
        from sysml_codegen.generation.registry import generate_registry
        from sysml_codegen.resolution.models import (
            ComputationGraph,
            ModuleKind,
            ModuleOutput,
            PipelineModule,
        )

        modules = [
            PipelineModule(
                name=f"module_{index}",
                module_type=f"Module{index}",
                inputs=[],
                outputs=[
                    ModuleOutput(
                        field_name="root",
                        python_type=python_type,
                        channel_name=f"module_{index}__result",
                    )
                ],
                execution_order=index,
                module_kind=ModuleKind.CALCULATION,
                calc_def_name=f"Calculation{index}",
                calc_def_qualified_name=f"RegistryProbe::Calculation{index}",
            )
            for index, python_type in enumerate(root_types)
        ]
        graph = ComputationGraph(
            modules=modules,
            entry_point_groups=[],
            execution_order=[module.name for module in modules],
        )
        template_dir = Path(__file__).parents[2] / "src" / "sysml_codegen" / "templates"
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        return generate_registry(graph, "test_pkg", env, tmp_path / "__init__.py")

    def test_custom_schema_types_are_derived_from_graph_root_outputs(self, tmp_path: Path):
        """Changing graph output types must change the rendered wrapper account."""
        rendered = self._render(tmp_path, "float", "str")

        assert "CUSTOM_SCHEMA_TYPES" in rendered
        assert "Float" in rendered
        assert "String" in rendered
        assert "from test_pkg.primitives import Float, String" in rendered

    def test_graph_without_root_outputs_renders_no_primitive_registry(self, tmp_path: Path):
        rendered = self._render(tmp_path)

        assert "CUSTOM_SCHEMA_TYPES" not in rendered
        assert "primitives" not in rendered
