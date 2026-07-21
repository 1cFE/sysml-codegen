"""The codegen sink for extraction diagnostics (DD-R08, DD-R09).

One function, two call sites, both **before lowering**: the live route
(`orchestration/pipeline_builder`, before `prepare_constraint_usages`) and the
snapshot route (`orchestration/snapshot_context`, before
`build_full_graph_from_snapshot`, which lowers). A blocking
diagnostic stops generation with its code, severity, message, and location in the
failure text; an advisory one is rendered at a level a build log shows and does not
stop generation.

This is deliberately not a routing or registry layer (explicit Non-Goal). It reads a
field the writer already decided (`DiagnosticSeverity`, fixed at construction
upstream) and branches on it. No `kind -> severity` lookup exists here, which is the
whole point of severity being a field: two readers at different versions cannot
disagree about whether the same bytes block.

Codegen's own diagnostics — the tier-2 malformed literal, the unresolved modeled
default — are not `ExtractionDiagnosticFact`s and do not travel on the wire. They
share the severity discipline and are emitted locally. Stating that is what keeps
this from growing into a router.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from agentic_mbse.sysml.constraint_facts import DiagnosticSeverity

if TYPE_CHECKING:
    from agentic_mbse.sysml.constraint_facts import (
        ConstraintFacts,
        ExtractionDiagnosticFact,
    )

logger = logging.getLogger(__name__)


def _render(diagnostic: ExtractionDiagnosticFact) -> str:
    location = diagnostic.location
    where = (
        f"{location.file}:{location.line}:{location.column}"
        if location is not None
        else "<no location>"
    )
    return (
        f"[{diagnostic.severity.value}/{diagnostic.kind}] {where}: {diagnostic.message}"
    )


def screen_extraction_diagnostics(facts: ConstraintFacts) -> None:
    """Halt on blocking extraction diagnostics; log advisory ones.

    Raises ``CodeGenerationError`` naming every blocking diagnostic, before lowering.
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

    from sysml_codegen.orchestration.pipeline_context import CodeGenerationError

    rendered = "\n".join(f"  - {_render(diagnostic)}" for diagnostic in blocking)
    raise CodeGenerationError(
        "Constraint generation halted — extraction raised blocking diagnostics:\n" + rendered
    )
