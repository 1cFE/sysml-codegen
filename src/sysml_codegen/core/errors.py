"""The package's two public error classes, on a route-neutral home.

Both classes were defined in ``orchestration/pipeline_context.py`` beside the
legacy ``PipelineContext``. That single import edge is what held the whole legacy
analysis stack inside the exact route's import closure, so the classes moved here
(Gate 4B-G0) and the class they lived beside retires with its builder in G3.

They live in ``core`` because every layer raises or catches them — extraction,
analysis, resolution, generation, orchestration and the CLI alike — and ``core``
is the one package all of those may import without inverting the layering.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sysml_codegen.generation.constraint_name_safety import ConstraintNameViolation


class SysMLParsingError(Exception):
    """Error during SysML model parsing.

    Raised when:
    - Model paths do not exist
    - SysML syntax errors in model files
    - Model loading fails for any reason
    """

    pass


class CodeGenerationError(Exception):
    """Error during code generation.

    Raised when:
    - No calculation definitions found in models
    - Required model elements are missing
    - Generation process fails
    """

    def __init__(
        self,
        message: str,
        *,
        name_safety_violation: ConstraintNameViolation | None = None,
    ) -> None:
        super().__init__(message)
        self.name_safety_violation = name_safety_violation
