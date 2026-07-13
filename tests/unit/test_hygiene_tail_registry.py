"""D3 Hygiene Tail Site 3 — `type_map` "Any" exit-point skip
(TRUTH-DEBT Item 6).

`_collect_exit_point_primitive_types` silently skips a single-output
("root") exit point whose `python_type` is outside `{float,int,str,bool}`
(notably "Any") — no wrapper registered, no diagnostic. Phase 0's
reachability scan found 0 non-primitive exit points on the covered corpus
(latent-only today); `"Any"` is minted independently on the live extractor
path (`extractor.py:492`), so the diagnostic is pinned with a constructed
fixture rather than a real one. Expectations are anchored to the
constructed `python_type`, never computed by the code under test (R1).
"""

from __future__ import annotations

import logging

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


def test_any_exit_point_warns(caplog):
    mods = [_module_with_root_output(python_type="Any")]
    with caplog.at_level(logging.WARNING):
        result = _collect_exit_point_primitive_types(mods)
    assert result == []
    assert any("Any" in w for w in _warns(caplog))


def test_float_exit_point_no_warn(caplog):
    mods = [_module_with_root_output(python_type="float")]
    with caplog.at_level(logging.WARNING):
        result = _collect_exit_point_primitive_types(mods)
    assert result == ["Float"]
    assert _warns(caplog) == []
