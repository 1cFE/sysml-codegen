"""Conformance tests for the module_kind fail-loud contract (Item 6 / INV-3).

A CONSTRAINT (or REPORT_AGGREGATOR) module has no rendering at any of the four
calc-shaped generation seams until Item 7 wires it. Each seam's entry point
must raise CodeGenerationError rather than silently skipping the module or
mis-rendering it as a calculation.
"""

from __future__ import annotations

from pathlib import Path

import jinja2
import pytest

from sysml_codegen.generation import CodeGenerationError
from sysml_codegen.generation.modules import generate_teax_module
from sysml_codegen.generation.pipeline import generate_pipeline_yaml
from sysml_codegen.generation.registry import generate_registry
from sysml_codegen.generation.stencils import generate_implementation
from sysml_codegen.generation.test_gen import generate_test_implementations
from sysml_codegen.resolution.models import ComputationGraph, ModuleKind, PipelineModule

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"


@pytest.fixture(scope="session")
def template_env():
    """Jinja2 template environment, matching test_gen_registry.py / test_gen_module_wrappers.py."""
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _constraint_module() -> PipelineModule:
    return PipelineModule(
        name="c1",
        module_type="C1Module",
        inputs=[],
        outputs=[],
        execution_order=0,
        module_kind=ModuleKind.CONSTRAINT,
    )


def _graph_with_constraint() -> ComputationGraph:
    return ComputationGraph(
        modules=[_constraint_module()], entry_point_groups=[], execution_order=["c1"]
    )


def test_registry_seam_refuses_constraint(template_env):
    """The critical fails-open seam: partition-by-equality silently drops an
    unmatched kind unless the guard-pass raises first (design-review M2)."""
    graph = _graph_with_constraint()
    with pytest.raises(CodeGenerationError, match="constraint"):
        generate_registry(
            graph=graph,
            package_name="pkg",
            template_env=template_env,
            output_path=Path("/tmp/test_registry.py"),
        )


def test_check_duplicate_output_paths_refuses_constraint():
    from sysml_codegen.cli import _check_duplicate_output_paths

    with pytest.raises(CodeGenerationError, match="constraint"):
        _check_duplicate_output_paths([_constraint_module()])


def test_generate_teax_module_refuses_constraint(template_env):
    with pytest.raises(CodeGenerationError, match="constraint"):
        generate_teax_module(
            _constraint_module(),
            template_env=template_env,
            output_path=Path("/tmp/test_wrapper.py"),
        )


def test_generate_implementation_refuses_constraint(template_env):
    with pytest.raises(CodeGenerationError, match="constraint"):
        generate_implementation(
            _constraint_module(),
            template_env=template_env,
            output_path=Path("/tmp/test_impl.py"),
        )


def test_generate_backlog_report_refuses_constraint():
    from sysml_codegen.generation.stencils import generate_backlog_report

    with pytest.raises(CodeGenerationError, match="constraint"):
        generate_backlog_report(
            _graph_with_constraint(), output_path=Path("/tmp/BACKLOG.md"), package_name="pkg"
        )


def test_generate_pipeline_yaml_refuses_constraint(template_env):
    with pytest.raises(CodeGenerationError, match="constraint"):
        generate_pipeline_yaml(
            _graph_with_constraint(), package_name="pkg", template_env=template_env
        )


def test_generate_test_implementations_refuses_constraint(template_env):
    with pytest.raises(CodeGenerationError, match="constraint"):
        generate_test_implementations(
            _graph_with_constraint(),
            package_name="pkg",
            template_env=template_env,
            output_path=Path("/tmp/test_gen.py"),
        )
