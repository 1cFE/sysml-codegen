"""Private typed refusals raised while extracting codegen-owned evidence."""

from __future__ import annotations

from sysml_codegen.elaboration.diagnostics import (
    ElaborationCode,
    ElaborationInvariantError,
    SiteReason,
)


class ExactTypeError(ElaborationInvariantError):
    """A feature does not have one supported exact qualified primitive typing."""

    def __init__(
        self,
        detail: str,
        *,
        reference: str,
        location: tuple[str, int] | None,
        reason: SiteReason | None = None,
    ) -> None:
        super().__init__(ElaborationCode.SI_TYPE_INVALID, detail, reason=reason)
        self.operation = "extract_type"
        self.reference = reference
        self.location = location


class ExactExtractionError(ElaborationInvariantError):
    """An authored declaration cannot form complete extraction evidence."""

    def __init__(
        self,
        detail: str,
        *,
        reference: str,
        location: tuple[str, int] | None,
        reason: SiteReason | None = None,
    ) -> None:
        super().__init__(
            ElaborationCode.SI_EVIDENCE_INCOMPLETE,
            detail,
            reference=reference,
            location=location,
            reason=reason,
        )
        self.operation = "extract_calculation_definition"


__all__ = ["ExactExtractionError", "ExactTypeError"]
