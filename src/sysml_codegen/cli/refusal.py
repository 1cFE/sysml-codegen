"""The structured form of a ``run_codegen`` refusal, logged beside its text.

Every log call on the generate route that ends a run with ``False`` passes one
``Refusal`` as ``extra={"refusal": ...}`` (EXEC-SUBSET-CONTRACT Item 2a D2). A caller
reads codes, site reasons and locations from it instead of parsing the message, where a
code can also appear inside detail text.

The kind names the carrier, not the stage that raised it: an unclassified failure during
generation is converted to the same ``SI_INTERNAL_DEFECT`` diagnostic as one during
construction, so it is a ``DIAGNOSTIC`` refusal either way.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sysml_codegen.core.errors import CodeGenerationError, GenerationCode
    from sysml_codegen.elaboration.diagnostics import ElaborationCode, SiteReason
    from sysml_codegen.elaboration.elaborate import (
        ElaborationDiagnosticError,
        ElaborationError,
    )
    from sysml_codegen.extraction.source_evidence import ReadinessCode

__all__ = [
    "Refusal",
    "RefusalItem",
    "RefusalKind",
    "diagnostic_refusal",
    "generation_refusal",
    "readiness_refusal",
]


class RefusalKind(StrEnum):
    #: Carries no code: the input never reached the exact route.
    SNAPSHOT = "snapshot"
    PARSING = "parsing"
    READINESS = "readiness"
    DIAGNOSTIC = "diagnostic"
    GENERATION = "generation"
    #: Carries no code: writing or sealing the output tree failed.
    PACKAGE_WRITE = "package_write"


@dataclass(frozen=True)
class RefusalItem:
    code: ElaborationCode | ReadinessCode | GenerationCode
    reason: SiteReason | None
    source_file: str | None
    source_line: int | None


@dataclass(frozen=True)
class Refusal:
    kind: RefusalKind
    items: tuple[RefusalItem, ...] = ()


def readiness_refusal(error: ElaborationError) -> Refusal:
    return Refusal(
        RefusalKind.READINESS,
        tuple(RefusalItem(f.code, f.reason, f.source_file, f.source_line) for f in error.findings),
    )


def diagnostic_refusal(error: ElaborationDiagnosticError) -> Refusal:
    return Refusal(
        RefusalKind.DIAGNOSTIC,
        tuple(
            RefusalItem(d.code, d.reason, d.source_file, d.source_line) for d in error.diagnostics
        ),
    )


def generation_refusal(error: CodeGenerationError) -> Refusal:
    """The generation code, then the diagnostics of any graph refusal it wraps."""
    return Refusal(
        RefusalKind.GENERATION,
        (
            RefusalItem(error.code, error.reason, None, None),
            *(
                RefusalItem(d.code, d.reason, d.source_file, d.source_line)
                for d in error.diagnostics
            ),
        ),
    )
