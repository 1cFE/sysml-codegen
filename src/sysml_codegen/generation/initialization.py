"""Shared exception types for codegen scripts.

The ``PipelineContext`` alias retired with the v5 family (retirement step 2); the
dataclass it aliased is gone. The exception classes are defined in ``core/errors.py``
and re-exported here and from ``orchestration/``.
"""

from sysml_codegen.core.errors import CodeGenerationError, SysMLParsingError

__all__ = [
    "CodeGenerationError",
    "SysMLParsingError",
]
