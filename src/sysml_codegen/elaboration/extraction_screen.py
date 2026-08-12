"""The exact route's sink for extraction diagnostics (REQ-DIAG-02, REQ-DIAG-03).

One function, one call site: the elaborator reads the identified constraint facts
once, and this screens them there — before any graph is built, so before either
route can serialize or lower anything. Live generation and v6 capture both reach
the elaborator through `orchestration/elaborated_pipeline.py`, so screening here
covers both without a second sink.

It is deliberately not a routing or registry layer. It reads a field the writer
already decided (`DiagnosticSeverity`, fixed at construction upstream) and
branches on it. No `kind -> severity` lookup exists here, which is the whole point
of severity being a field: two readers at different versions cannot disagree about
whether the same bytes block.

Codegen's own diagnostics — the tier-2 malformed literal, the unresolved modeled
default — are not `ExtractionDiagnosticFact`s and do not travel on the wire. They
share the severity discipline and are emitted locally.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from agentic_mbse.sysml.constraint_facts import DiagnosticSeverity

from sysml_codegen.elaboration.diagnostics import ElaborationCode, ElaborationInvariantError

if TYPE_CHECKING:
    from agentic_mbse.sysml.constraint_facts import (
        ConstraintFacts,
        ExtractionDiagnosticFact,
    )

__all__ = ["screen_extraction_diagnostics"]

logger = logging.getLogger(__name__)


def _render(diagnostic: ExtractionDiagnosticFact) -> str:
    location = diagnostic.location
    where = (
        f"{location.file}:{location.line}:{location.column}"
        if location is not None
        else "<no location>"
    )
    return f"[{diagnostic.severity.value}/{diagnostic.kind}] {where}: {diagnostic.message}"


def screen_extraction_diagnostics(facts: ConstraintFacts) -> None:
    """Halt on blocking extraction diagnostics; log advisory ones.

    Raises ``ElaborationInvariantError`` naming every blocking diagnostic — kind,
    severity, location, and message. Advisories are logged first, and `_render`
    degrades a missing location to `<no location>` rather than raising, so nothing
    in the advisory pass can occupy the slot the blocking halt needs.
    """
    blocking = [
        diagnostic
        for diagnostic in facts.diagnostics
        if diagnostic.severity is DiagnosticSeverity.BLOCKING
    ]
    advisory = [
        diagnostic
        for diagnostic in facts.diagnostics
        if diagnostic.severity is DiagnosticSeverity.ADVISORY
    ]

    for diagnostic in advisory:
        logger.warning("Extraction diagnostic: %s", _render(diagnostic))

    if not blocking:
        return

    rendered = "; ".join(_render(diagnostic) for diagnostic in blocking)
    raise ElaborationInvariantError(
        ElaborationCode.EXTRACTION_DIAGNOSTIC_BLOCKING,
        f"extraction raised blocking diagnostics: {rendered}",
    )
