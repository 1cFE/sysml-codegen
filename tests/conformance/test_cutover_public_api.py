"""Final public builder and context surface for the elaborator cutover."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

import sysml_codegen
import sysml_codegen.generation as generation
import sysml_codegen.generation.initialization as initialization
import sysml_codegen.orchestration as orchestration
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.pipeline_context import (
    CodeGenerationError,
    PipelineContext,
    SysMLParsingError,
)
from sysml_codegen.orchestration.snapshot_context import (
    build_pipeline_context_from_snapshot,
)
from sysml_codegen.snapshot import capture_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "source_identity_mixed_consumers"
CONSTRUCTION_ERROR = (
    "PipelineContext is builder-created; use build_pipeline_context or "
    "build_pipeline_context_from_snapshot"
)


def test_public_builder_signatures_and_aliases_are_exact() -> None:
    live = inspect.signature(build_pipeline_context)
    assert list(live.parameters) == [
        "model_paths",
        "targets",
        "include_all",
        "design_path_filter",
    ]
    assert live.parameters["targets"].default is None
    assert live.parameters["include_all"].default is True
    assert live.parameters["design_path_filter"].default == ""

    snapshot = inspect.signature(build_pipeline_context_from_snapshot)
    assert list(snapshot.parameters) == [
        "snapshot_path",
        "targets",
        "include_all",
        "source_roots",
    ]
    assert snapshot.parameters["source_roots"].kind is inspect.Parameter.KEYWORD_ONLY

    assert orchestration.PipelineContext is PipelineContext
    assert orchestration.CodeGenerationError is CodeGenerationError
    assert orchestration.SysMLParsingError is SysMLParsingError
    assert orchestration.build_pipeline_context is build_pipeline_context
    assert (
        orchestration.build_pipeline_context_from_snapshot
        is build_pipeline_context_from_snapshot
    )
    assert generation.PipelineContext is PipelineContext
    assert generation.CodeGenerationError is CodeGenerationError
    assert generation.SysMLParsingError is SysMLParsingError
    assert initialization.PipelineContext is PipelineContext
    assert initialization.CodeGenerationError is CodeGenerationError
    assert initialization.SysMLParsingError is SysMLParsingError
    assert not hasattr(generation, "build_pipeline_context")
    assert not hasattr(generation, "build_pipeline_context_from_snapshot")
    assert not hasattr(sysml_codegen, "PipelineContext")
    assert not hasattr(sysml_codegen, "build_pipeline_context")


@pytest.mark.parametrize(
    "args, kwargs",
    [
        ((), {}),
        ((object(),), {}),
        ((), {"computation_graph": object()}),
        ((), {"extractor": None, "calc_defs": []}),
        ((), {"constraint_" "lowering_mode": "applied"}),
    ],
)
def test_direct_context_construction_and_legacy_kwargs_refuse(args, kwargs) -> None:
    with pytest.raises(TypeError, match=CONSTRUCTION_ERROR):
        PipelineContext(*args, **kwargs)


def test_both_public_builders_create_the_narrow_context(tmp_path: Path) -> None:
    live = build_pipeline_context([FIXTURE])
    captured = capture_snapshot([FIXTURE], tmp_path / "case.json")
    offline = build_pipeline_context_from_snapshot(captured)

    assert PipelineContext.__slots__ == ("_instance_bytes", "_selection", "_receipt")
    for context in (live, offline):
        assert context.computation_graph.modules
        assert not hasattr(context, "instance_graph")
        assert not hasattr(context, "selection")
        assert not hasattr(context, "receipt")
        assert not hasattr(context, "calc_defs")
        assert not hasattr(context, "constraint_" "lowering_mode")

    with pytest.raises(TypeError):
        build_pipeline_context([FIXTURE], lower_constraints_enabled=True)  # type: ignore[call-arg]
