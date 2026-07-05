"""Shared exception types for codegen scripts.

PipelineContext has been moved to sysml_codegen.orchestration.pipeline_context
(Step 7.6). Exception classes remain here for backward compatibility and are
also re-exported from orchestration/.
"""

from sysml_codegen.orchestration.pipeline_context import (
    CodeGenerationError,
    PipelineContext,
    SysMLParsingError,
)

__all__ = [
    "CodeGenerationError",
    "PipelineContext",
    "SysMLParsingError",
]
