"""Unsupported root outputs refuse at the public boundary before any write."""

from __future__ import annotations

import argparse
import inspect
import logging
from pathlib import Path
from types import SimpleNamespace

import jinja2
import pytest

from sysml_codegen.cli import cmd_generate
from sysml_codegen.generation import (
    CodeGenerationError,
    generate_registry,
    generate_registry_from_graph,
    generate_registry_function,
)
from sysml_codegen.generation.registry import (
    exit_point_wrapper_type,
    required_exit_point_wrapper_types,
)
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ModuleKind,
    ModuleOutput,
    PipelineModule,
)


def _tree(root: Path) -> dict[str, tuple[str, bytes | None]]:
    if not root.exists():
        return {}
    result: dict[str, tuple[str, bytes | None]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            result[relative] = ("directory", None)
        else:
            result[relative] = ("file", path.read_bytes())
    return result


@pytest.mark.parametrize(
    ("python_type", "wrapper"),
    [("float", "Float"), ("int", "Int"), ("str", "String"), ("bool", "Bool")],
)
def test_exit_wrapper_validator_is_total_for_supported_primitives(
    python_type: str, wrapper: str
) -> None:
    assert exit_point_wrapper_type(python_type) == wrapper


def test_exit_wrapper_validator_names_unsupported_types() -> None:
    assert exit_point_wrapper_type("Decimal") is None


def _unsupported_graph() -> ComputationGraph:
    module = PipelineModule(
        name="thermal_balance",
        module_type="ThermalBalanceModule",
        inputs=[],
        outputs=[
            ModuleOutput(
                field_name="root",
                python_type="Decimal",
                channel_name="thermal_balance__result",
            )
        ],
        execution_order=0,
        module_kind=ModuleKind.CALCULATION,
        calc_def_name="ThermalBalance",
        calc_def_qualified_name="InvalidExit::ThermalBalance",
        source_file="root-0/model.sysml",
        source_line=17,
    )
    return ComputationGraph(
        modules=[module],
        entry_point_groups=[],
        execution_order=[module.name],
    )


def _graph_with_root_types(*python_types: str) -> ComputationGraph:
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
            source_file="root-0/model.sysml",
            source_line=10 + index,
        )
        for index, python_type in enumerate(python_types)
    ]
    return ComputationGraph(
        modules=modules,
        entry_point_groups=[],
        execution_order=[module.name for module in modules],
    )


@pytest.mark.parametrize(
    ("python_types", "expected"),
    [
        ((), ()),
        (("float",), ("Float",)),
        (("float", "float"), ("Float",)),
        (("str", "bool", "int", "float"), ("Bool", "Float", "Int", "String")),
    ],
)
def test_required_exit_wrappers_are_derived_from_the_complete_graph(
    python_types: tuple[str, ...],
    expected: tuple[str, ...],
) -> None:
    assert required_exit_point_wrapper_types(_graph_with_root_types(*python_types)) == expected


def _template_environment() -> jinja2.Environment:
    templates = Path(__file__).parents[2] / "src" / "sysml_codegen" / "templates"
    return jinja2.Environment(loader=jinja2.FileSystemLoader(templates))


@pytest.mark.parametrize(
    "renderer",
    (generate_registry, generate_registry_from_graph, generate_registry_function),
)
def test_every_exported_registry_seam_has_no_caller_type_account_and_derives_wrappers(
    renderer: object,
    tmp_path: Path,
) -> None:
    assert list(inspect.signature(renderer).parameters) == [
        "graph",
        "package_name",
        "template_env",
        "output_path",
    ]
    rendered = renderer(
        _graph_with_root_types("str", "float", "str"),
        "registry_probe",
        _template_environment(),
        tmp_path / "__init__.py",
    )
    assert "from registry_probe.primitives import Float, String" in rendered


@pytest.mark.parametrize(
    "renderer",
    (generate_registry, generate_registry_from_graph, generate_registry_function),
)
def test_every_exported_registry_seam_refuses_an_unsupported_graph_without_writing(
    renderer: object,
    tmp_path: Path,
) -> None:
    output = tmp_path / "__init__.py"
    output.write_bytes(b"sentinel\x00")

    with pytest.raises(CodeGenerationError, match="EXIT_POINT_TYPE_UNSUPPORTED") as caught:
        renderer(
            _unsupported_graph(),
            "registry_probe",
            _template_environment(),
            output,
        )

    assert "module='thermal_balance'" in str(caught.value)
    assert "output='root/thermal_balance__result'" in str(caught.value)
    assert "python_type='Decimal'" in str(caught.value)
    assert "source='root-0/model.sysml:17'" in str(caught.value)
    assert output.read_bytes() == b"sentinel\x00"
def test_public_exit_type_refusal_is_status_one_and_byte_preserving(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    from sysml_codegen.orchestration import exact_pipeline_context

    output = tmp_path / "sentinel-package"
    (output / "nested").mkdir(parents=True)
    (output / "sentinel.bin").write_bytes(b"unchanged\x00")
    (output / "nested" / "record.txt").write_bytes(b"before\n")
    before = _tree(output)
    graph = _unsupported_graph()
    monkeypatch.setattr(
        exact_pipeline_context,
        "build_exact_pipeline_context",
        lambda _paths: SimpleNamespace(computation_graph=graph),
    )
    args = argparse.Namespace(
        verbose=False,
        models=tmp_path / "model.sysml",
        from_snapshot=None,
        output=output,
        package_name="invalid_exit",
        schema_class="Params",
        pipeline_name="pipeline",
        overwrite=True,
        preserve_handwritten=False,
        smart_regen=False,
    )

    with caplog.at_level(logging.ERROR):
        status = cmd_generate(args)

    assert status == 1
    assert _tree(output) == before
    message = "\n".join(record.message for record in caplog.records)
    assert message.count("EXIT_POINT_TYPE_UNSUPPORTED") == 1
    assert "module='thermal_balance'" in message
    assert "output='root/thermal_balance__result'" in message
    assert "python_type='Decimal'" in message
    assert "source='root-0/model.sysml:17'" in message
