"""D3 Hygiene Tail Site 3 — `type_map` "Any" exit-point skip
(TRUTH-DEBT Item 6).

The public generation boundary and direct registry seam derive from the same graph
and refuse an unsupported root output before mutation.
"""

from __future__ import annotations

import logging

import pytest

from sysml_codegen.generation import CodeGenerationError
from sysml_codegen.generation.registry import required_exit_point_wrapper_types
from sysml_codegen.resolution.models import (
    Compilability,
    ComputationGraph,
    ModuleKind,
    ModuleOutput,
    PipelineModule,
)


def _warns(caplog):
    return [r.message for r in caplog.records if r.levelno >= logging.WARNING]


def _module_with_root_output(python_type: str) -> PipelineModule:
    return PipelineModule(
        name="probe_mod",
        module_type="ProbeModule",
        inputs=[],
        outputs=[
            ModuleOutput(
                field_name="root",
                python_type=python_type,
                channel_name="probe_mod__root",
            )
        ],
        execution_order=0,
        compilability=Compilability.FULLY_COMPILABLE,
        module_kind=ModuleKind.CALCULATION,
    )


def _graph_with_root_output(python_type: str) -> ComputationGraph:
    module = _module_with_root_output(python_type)
    return ComputationGraph(
        modules=[module],
        entry_point_groups=[],
        execution_order=[module.name],
    )


def test_any_exit_point_cannot_be_omitted_by_a_direct_registry_caller(caplog):
    with caplog.at_level(logging.WARNING):
        with pytest.raises(CodeGenerationError, match="EXIT_POINT_TYPE_UNSUPPORTED"):
            required_exit_point_wrapper_types(_graph_with_root_output("Any"))
    assert _warns(caplog) == []


def test_float_exit_point_no_warn(caplog):
    with caplog.at_level(logging.WARNING):
        result = required_exit_point_wrapper_types(_graph_with_root_output("float"))
    assert result == ("Float",)
    assert _warns(caplog) == []
