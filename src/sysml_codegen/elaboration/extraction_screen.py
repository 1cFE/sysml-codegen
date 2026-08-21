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
from collections.abc import Mapping
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


def _render(
    diagnostic: ExtractionDiagnosticFact,
    source_referents: Mapping[str, str],
) -> str:
    location = diagnostic.location
    label = f"[{diagnostic.severity.value}/{diagnostic.kind}]"
    if location is None:
        return f"{label} <no location>: {diagnostic.message}"
    portable = _portable_file(location.file, source_referents)
    where = f"{portable}:{location.line}:{location.column}"
    return f"{label} {where}: {diagnostic.message}"


def _file_path(raw: str) -> str:
    """The parser's location as a filesystem path, not a URI."""
    return raw.removeprefix("file://")


def _portable_file(raw: str, source_referents: Mapping[str, str]) -> str:
    """Name a parsed file the way the modeller does, when the caller knows how.

    Capture parses private staged copies. Without the manifest's referents a
    blocking diagnostic would name a staging directory that is gone by the time
    anyone reads the message.
    """
    path = _file_path(raw)
    return source_referents.get(path) or source_referents.get(raw) or path


def screen_extraction_diagnostics(
    facts: ConstraintFacts,
    *,
    source_referents: Mapping[str, str] | None = None,
) -> None:
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

    referents = source_referents or {}
    for diagnostic in advisory:
        logger.warning("Extraction diagnostic: %s", _render(diagnostic, referents))

    if not blocking:
        return

    rendered = "; ".join(_render(diagnostic, referents) for diagnostic in blocking)
    located = [diagnostic.location for diagnostic in blocking if diagnostic.location is not None]
    # The raw path, deliberately: mapping a location to its portable referent is
    # the pipeline's one job (``_lookup_referent``), and it fails closed on a
    # source it does not know. Only the rendered text is portable here. The
    # anchor is the lowest site in the set, so one refusal cites one place and
    # the ordering of the diagnostics decides nothing.
    location: tuple[str, int] | None = None
    if located:
        anchor = min(located, key=lambda item: (item.file, item.line, item.column))
        location = (_file_path(anchor.file), anchor.line)
    raise ElaborationInvariantError(
        ElaborationCode.EXTRACTION_DIAGNOSTIC_BLOCKING,
        f"extraction raised blocking diagnostics: {rendered}",
        location=location,
    )
