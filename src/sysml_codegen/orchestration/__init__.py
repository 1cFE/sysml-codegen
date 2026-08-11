"""Supported orchestration builders, context, and live errors."""

from __future__ import annotations

from typing import Any

from sysml_codegen.orchestration.pipeline_context import (
    CodeGenerationError,
    PipelineContext,
    SysMLParsingError,
)


def __getattr__(name: str) -> Any:
    if name == "build_pipeline_context":
        from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

        return build_pipeline_context
    if name == "build_pipeline_context_from_snapshot":
        from sysml_codegen.orchestration.snapshot_context import (
            build_pipeline_context_from_snapshot,
        )

        return build_pipeline_context_from_snapshot
    raise AttributeError(name)


__all__ = [
    "CodeGenerationError",
    "PipelineContext",
    "SysMLParsingError",
    "build_pipeline_context",
    "build_pipeline_context_from_snapshot",
]
