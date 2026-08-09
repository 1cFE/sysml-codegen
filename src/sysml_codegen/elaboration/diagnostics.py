"""One diagnostic vocabulary for exact-ID elaboration failures."""

from __future__ import annotations

from enum import Enum

__all__ = ["ElaborationCode", "ElaborationInvariantError"]


class ElaborationCode(str, Enum):
    SYSML_NAMESPACE_NOT_DISTINGUISHABLE = "SYSML_NAMESPACE_NOT_DISTINGUISHABLE"
    SI_OCCURRENCE_MISSING = "SI_OCCURRENCE_MISSING"
    SI_OCCURRENCE_AMBIGUOUS = "SI_OCCURRENCE_AMBIGUOUS"
    OVERRIDE_TARGET_MISSING = "OVERRIDE_TARGET_MISSING"
    SI_ID_MISSING = "SI_ID_MISSING"
    SI_ID_UNSTABLE = "SI_ID_UNSTABLE"
    SI_REDEFINITION_INVALID = "SI_REDEFINITION_INVALID"
    SI_MULTIPLICITY_UNRESOLVED = "SI_MULTIPLICITY_UNRESOLVED"
    SI_MULTIPLICITY_UNSUPPORTED = "SI_MULTIPLICITY_UNSUPPORTED"
    SI_MULTIPLICITY_INVALID = "SI_MULTIPLICITY_INVALID"
    SI_CONTAINMENT_RECURSIVE = "SI_CONTAINMENT_RECURSIVE"
    SI_ALIAS_CYCLE = "SI_ALIAS_CYCLE"
    SI_EDGE_DANGLING = "SI_EDGE_DANGLING"
    SI_RENDERING_COLLISION = "SI_RENDERING_COLLISION"
    SI_SNAPSHOT_INVALID = "SI_SNAPSHOT_INVALID"


class ElaborationInvariantError(ValueError):
    """An exact-ID invariant failed before a usable graph could be built."""

    def __init__(self, code: ElaborationCode, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code.value}: {detail}")
