"""D3 Hygiene Tail Site 3 — `type_map` "Any" exit-point skip
(TRUTH-DEBT Item 6).

The public generation boundary now refuses an unsupported root output before
mutation. If a direct registry caller bypasses that preflight, collection raises
as a programming invariant instead of warning and omitting the wrapper.
"""

from __future__ import annotations

import logging

import pytest

from sysml_codegen.generation.registry import _collect_exit_point_primitive_types
from sysml_codegen.resolution.models import (
    Compilability,
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


def test_any_exit_point_cannot_be_omitted_by_a_direct_registry_caller(caplog):
    mods = [_module_with_root_output(python_type="Any")]
    with caplog.at_level(logging.WARNING):
        with pytest.raises(RuntimeError, match="exit-point type preflight"):
            _collect_exit_point_primitive_types(mods)
    assert _warns(caplog) == []


def test_float_exit_point_no_warn(caplog):
    mods = [_module_with_root_output(python_type="float")]
    with caplog.at_level(logging.WARNING):
        result = _collect_exit_point_primitive_types(mods)
    assert result == ["Float"]
    assert _warns(caplog) == []
