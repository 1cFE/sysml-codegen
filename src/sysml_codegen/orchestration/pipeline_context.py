"""The ``SysMLParsingError`` / ``CodeGenerationError`` re-export point.

The ``PipelineContext`` dataclass this module was named for was the legacy string-
resolution route's carrier, and it retired with the v5 family (retirement step 2).

The two error classes are defined in ``core/errors.py`` (Gate 4B-G0 moved them there).
They are re-exported here, and from ``orchestration/__init__.py``, because that is where
every existing ``raise`` and ``except`` in the tree names them — the same class objects,
so no handler changes.
"""

from __future__ import annotations

from sysml_codegen.core.errors import CodeGenerationError, SysMLParsingError

__all__ = ["CodeGenerationError", "SysMLParsingError"]
