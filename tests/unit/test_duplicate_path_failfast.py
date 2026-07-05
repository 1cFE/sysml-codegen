"""REQ-NC-09: fail fast when two SysML names sanitize to one output path.

Covers the two write key spaces the collision spans (D2): the module/stencil
python path, and the schema `calc_def_name.lower()` key. Each fail-fast names
BOTH raw sources and the shared path. A same-source repeat (one calc def used by
several usages) must NOT trip the check.
"""

from __future__ import annotations

import pytest

from sysml_codegen.cli import _check_duplicate_output_paths
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.resolution.models import ModuleOutput, PipelineModule


def _calc_usage_module(calc_def_qn: str, calc_def_name: str, n_outputs: int = 1) -> PipelineModule:
    outputs = [
        ModuleOutput(field_name=f"o{i}", python_type="float", channel_name=f"c{i}")
        for i in range(n_outputs)
    ]
    return PipelineModule(
        name=calc_def_name.lower(),
        module_type=f"{calc_def_name}Module",
        inputs=[],
        outputs=outputs,
        execution_order=0,
        calc_def_name=calc_def_name,
        calc_def_qualified_name=calc_def_qn,
    )


def test_module_path_collision_fails_fast():
    """Two calc defs whose names sanitize to one module path -> error names both."""
    modules = [
        _calc_usage_module("AliasAggProbeLibrary::'Margin Calc'", "Margin_Calc"),
        _calc_usage_module("AliasAggProbeLibrary::'margin calc'", "margin_calc"),
    ]
    with pytest.raises(CodeGenerationError, match="Duplicate output path") as exc:
        _check_duplicate_output_paths(modules)
    msg = str(exc.value)
    assert "AliasAggProbeLibrary::'Margin Calc'" in msg
    assert "AliasAggProbeLibrary::'margin calc'" in msg
    assert "aliasaggprobelibrary/margin_calc.py" in msg


def test_schema_key_collision_fails_fast():
    """Different packages (module paths differ) but one schema key -> caught.

    A module-path-only pass would miss this: `LibA::'Margin Calc'` and
    `LibB::'margin calc'` derive distinct module files (liba/ vs libb/) yet both
    lower to `margin_calc_output.py`.
    """
    modules = [
        _calc_usage_module("LibA::'Margin Calc'", "Margin_Calc", n_outputs=2),
        _calc_usage_module("LibB::'margin calc'", "margin_calc", n_outputs=2),
    ]
    with pytest.raises(CodeGenerationError, match="Duplicate output path") as exc:
        _check_duplicate_output_paths(modules)
    msg = str(exc.value)
    assert "LibA::'Margin Calc'" in msg
    assert "LibB::'margin calc'" in msg
    assert "schemas/margin_calc_output.py" in msg


def test_same_calc_def_multiple_usages_is_not_a_collision():
    """One calc def instantiated by several usages derives one path -- not an error."""
    modules = [
        _calc_usage_module("Lib::CostCalc", "CostCalc"),
        _calc_usage_module("Lib::CostCalc", "CostCalc"),
    ]
    _check_duplicate_output_paths(modules)  # must not raise
