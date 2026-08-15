"""Orchestration layer: the exact route's pipeline context.

The string-resolution pipeline builder, the output-registry builder and the
``PipelineContext`` dataclass retired with the v5 family (retirement step 2).
The exact route's elaborator entry is deliberately **not** re-exported here (Slice 3E F4
pin, checked by ``tests/unit/test_elaboration_import_boundaries.py``): the exact route is
reached through ``orchestration.exact_pipeline_context``.
"""

from sysml_codegen.orchestration.pipeline_context import (
    CodeGenerationError,
    SysMLParsingError,
)

__all__ = [
    "CodeGenerationError",
    "SysMLParsingError",
]
