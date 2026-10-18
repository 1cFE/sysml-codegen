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

from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sysml_codegen.elaboration.diagnostics import SiteReason
    from sysml_codegen.elaboration.graph import Diagnostic
    from sysml_codegen.generation.constraint_name_safety import ConstraintNameViolation


class SysMLParsingError(Exception):
    """Error during SysML model parsing.

    Raised when:
    - Model paths do not exist
    - SysML syntax errors in model files
    - Model loading fails for any reason
    """

    pass


class GenerationCode(StrEnum):
    """The closed code of every ``CodeGenerationError`` (EXEC-SUBSET-CONTRACT Item 2a D15).

    A generation-stage refusal was named only by a prefix in its message. The code is the
    same name as a field, so a caller reads it without parsing text. The message is
    unchanged: where a family already wrote a prefix, the member is that prefix; the
    families whose messages carry none are named for their condition and stay unwritten
    in the text.
    """

    # Written as the message prefix.
    PARAM_FIELD_COLLISION = "PARAM_FIELD_COLLISION"
    REGISTRY_CLASS_NAME_COLLISION = "REGISTRY_CLASS_NAME_COLLISION"
    EXIT_POINT_TYPE_UNSUPPORTED = "EXIT_POINT_TYPE_UNSUPPORTED"
    GENERATION_METADATA_MISSING = "GENERATION_METADATA_MISSING"
    DUPLICATE_OUTPUT_PATH = "DUPLICATE_OUTPUT_PATH"
    CONSTRAINT_DOMAIN_INCOMPLETE = "CONSTRAINT_DOMAIN_INCOMPLETE"
    COVERAGE_ACCOUNT_INVALID = "COVERAGE_ACCOUNT_INVALID"
    PREDICATE_COMPILE_FAILED = "PREDICATE_COMPILE_FAILED"
    # Not written in the message.
    CONSTRAINT_NAME_UNSAFE = "CONSTRAINT_NAME_UNSAFE"
    MODULE_KIND_UNRENDERABLE = "MODULE_KIND_UNRENDERABLE"
    PREDICATE_FUNCTION_NAME_COLLISION = "PREDICATE_FUNCTION_NAME_COLLISION"
    PREDICATE_SCOPE_MISMATCH = "PREDICATE_SCOPE_MISMATCH"
    PREDICATE_INPUT_UNRECONCILED = "PREDICATE_INPUT_UNRECONCILED"
    PREDICATE_IR_INCONSISTENT = "PREDICATE_IR_INCONSISTENT"
    COVERAGE_REASON_UNTAUGHT = "COVERAGE_REASON_UNTAUGHT"
    NOTHING_TO_GENERATE = "NOTHING_TO_GENERATE"
    RECEIPT_INVALID = "RECEIPT_INVALID"
    PROJECTION_NONCANONICAL = "PROJECTION_NONCANONICAL"
    PROJECTION_FAILED = "PROJECTION_FAILED"
    GRAPH_NOT_PROJECTABLE = "GRAPH_NOT_PROJECTABLE"


class CodeGenerationError(Exception):
    """Error during code generation.

    Raised when:
    - No calculation definitions found in models
    - Required model elements are missing
    - Generation process fails

    ``code`` names the refusal family. ``reason`` names the raise site within it, where
    one has been assigned (``SiteReason``). ``diagnostics`` holds the elaboration
    diagnostics of a refusal that wraps a graph's own (a projection failure), so a caller
    reads their codes and locations without parsing the message that renders them.
    """

    def __init__(
        self,
        message: str,
        *,
        code: GenerationCode,
        reason: SiteReason | None = None,
        name_safety_violation: ConstraintNameViolation | None = None,
        diagnostics: tuple[Diagnostic, ...] = (),
    ) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.name_safety_violation = name_safety_violation
        self.diagnostics = diagnostics
