"""Public v6 snapshot builder for the narrow pipeline context."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from sysml_codegen.orchestration.pipeline_context import (
    PipelineContext,
    _make_pipeline_context,
)
from sysml_codegen.snapshot.envelope import load_snapshot


def build_pipeline_context_from_snapshot(
    snapshot_path: Path,
    targets: list[str] | None = None,
    include_all: bool = True,
    *,
    source_roots: Sequence[Path] | None = None,
) -> PipelineContext:
    """Validate v6 authority and return the same context as the live builder."""
    graph = load_snapshot(snapshot_path, source_roots=source_roots)
    return _make_pipeline_context(graph, targets=targets, include_all=include_all)


__all__ = ["build_pipeline_context_from_snapshot"]
