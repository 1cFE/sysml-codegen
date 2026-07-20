"""The codegen extraction-diagnostic sink, on both routes (DD-A03, DD-R08, DD-R09).

Written in response to audit F1 and F3. The sink was correct by direct execution but
had **zero** test coverage on either route, so the ordering defect F1 found — the
snapshot sink running after lowering — had nothing to catch it. These tests pin the
behaviour and the ordering together.

Two honest constraints on what can be pinned, both structural rather than oversights:

* **The snapshot route cannot use a captured fixture.** A `non_finite_literal`
  diagnostic requires a non-finite literal, and the facts serializer refuses those
  outright (`allow_nan=False`, the D2a serialize-time backstop). So such a diagnostic
  can never reach a snapshot by capture. The payload is synthesized instead — the same
  technique `test_snapshot_v4_gate.py` uses for a stale envelope.
* **The advisory branch has no reachable input today.** The writer-side table has one
  entry, `non_finite_literal: BLOCKING`, and `parse` refuses a document whose stored
  severity disagrees with it. The advisory leg is therefore exercised by constructing
  the fact directly, which pins the renderer and the branch without pretending an
  end-to-end route exists. Recorded in evidence rather than papered over.
"""

from __future__ import annotations

import json
import logging

import pytest
from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    DiagnosticSeverity,
    ExtractionDiagnosticFact,
)

from sysml_codegen.analysis.diagnostic_screen import screen_extraction_diagnostics
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.orchestration.snapshot_context import build_pipeline_context_from_snapshot
from tests.conftest import FIXTURES_DIR, requires_license, snapshot_fixture

ROOT = FIXTURES_DIR / "non_finite_literal"
SCREEN_LOGGER = "sysml_codegen.analysis.diagnostic_screen"


def _blocking_fact() -> ExtractionDiagnosticFact:
    return ExtractionDiagnosticFact(
        kind="non_finite_literal",
        message="Non-finite literal operand encountered during extraction: inf",
        operand_source="1.0e400",
        location=None,
    )


def _facts(diagnostics: list[ExtractionDiagnosticFact]) -> ConstraintFacts:
    return ConstraintFacts(definitions=[], usages=[], contexts=[], diagnostics=diagnostics)


# --- the function itself ----------------------------------------------------


def test_blocking_diagnostic_raises_with_code_severity_and_message():
    """DD-R09: the failure text names the code, the severity, and the message."""
    with pytest.raises(CodeGenerationError) as excinfo:
        screen_extraction_diagnostics(_facts([_blocking_fact()]))

    text = str(excinfo.value)
    assert "non_finite_literal" in text
    assert "blocking" in text
    assert "Non-finite literal operand" in text


def test_location_is_rendered_when_present():
    from agentic_mbse.sysml.constraint_facts import LocationFact

    fact = ExtractionDiagnosticFact(
        kind="non_finite_literal",
        message="m",
        operand_source=None,
        location=LocationFact(file="root-0/model.sysml", line=36, column=24),
    )
    with pytest.raises(CodeGenerationError, match=r"root-0/model\.sysml:36:24"):
        screen_extraction_diagnostics(_facts([fact]))


def test_absent_location_renders_a_marker_rather_than_crashing():
    with pytest.raises(CodeGenerationError, match="<no location>"):
        screen_extraction_diagnostics(_facts([_blocking_fact()]))


def test_no_diagnostics_is_silent(caplog):
    with caplog.at_level(logging.WARNING, logger=SCREEN_LOGGER):
        screen_extraction_diagnostics(_facts([]))
    assert [r for r in caplog.records if r.name == SCREEN_LOGGER] == []


def test_advisory_diagnostic_logs_and_does_not_halt(caplog, monkeypatch):
    """DD-R09's advisory leg.

    No `ConstraintFacts` can carry an ADVISORY diagnostic today — the writer table
    has one entry and it is BLOCKING — so the severity is overridden on a
    constructed fact. This pins the branch and the renderer honestly; it does not
    claim an end-to-end advisory route exists. See the module docstring.
    """
    fact = _blocking_fact()
    object.__setattr__(fact, "severity", DiagnosticSeverity.ADVISORY)

    with caplog.at_level(logging.WARNING, logger=SCREEN_LOGGER):
        screen_extraction_diagnostics(_facts([fact]))  # must NOT raise

    messages = [r.getMessage() for r in caplog.records if r.name == SCREEN_LOGGER]
    assert len(messages) == 1
    assert "advisory" in messages[0]
    assert "non_finite_literal" in messages[0]


# --- the live route ---------------------------------------------------------


@requires_license
def test_live_route_halts_before_lowering():
    """DD-A03 live leg: generation stops, with the actionable diagnostic."""
    with pytest.raises(CodeGenerationError) as excinfo:
        build_pipeline_context([ROOT])

    text = str(excinfo.value)
    assert "extraction raised blocking diagnostics" in text
    assert "non_finite_literal" in text
    assert "model.sysml:36:24" in text


# --- the snapshot route, and the ordering F1 found --------------------------


def _synthesized_blocking_snapshot(tmp_path):
    """A committed v4 snapshot with one blocking diagnostic spliced in.

    Synthesized rather than captured: see the module docstring.
    """
    payload = json.loads(snapshot_fixture("wi014_toy").read_text())
    payload["constraint_facts"]["diagnostics"] = [
        {
            "kind": "non_finite_literal",
            "message": "Non-finite literal operand encountered during extraction: inf",
            "severity": "blocking",
            "operand_source": "1.0e400",
            "location": {"file": "root-0/model.sysml", "line": 36, "column": 24},
        }
    ]
    path = tmp_path / "extraction_snapshot.json"
    path.write_text(json.dumps(payload))
    return path


def test_snapshot_route_halts_on_a_blocking_diagnostic(tmp_path):
    with pytest.raises(CodeGenerationError, match="non_finite_literal"):
        build_pipeline_context_from_snapshot(_synthesized_blocking_snapshot(tmp_path))


def test_snapshot_route_screens_before_lowering(tmp_path, monkeypatch):
    """Audit F1: the sink must run BEFORE lowering, symmetric with the live route.

    As shipped at `16dbaa7` the order was ['lower_constraints',
    'screen_extraction_diagnostics'] — lowering consumed the bad literal first, so a
    user got an obscure lowering failure instead of the actionable diagnostic, which
    is the failure DD-R09 exists to prevent. This records the call order directly
    rather than inferring it from where the code appears.
    """
    import sysml_codegen.orchestration.snapshot_context as snapshot_context
    import sysml_codegen.snapshot.graph_rebuild as graph_rebuild

    order: list[str] = []
    real_lower = graph_rebuild.lower_constraints
    real_screen = snapshot_context.screen_extraction_diagnostics

    def spy_lower(*args, **kwargs):
        order.append("lower_constraints")
        return real_lower(*args, **kwargs)

    def spy_screen(*args, **kwargs):
        order.append("screen_extraction_diagnostics")
        return real_screen(*args, **kwargs)

    monkeypatch.setattr(graph_rebuild, "lower_constraints", spy_lower)
    monkeypatch.setattr(snapshot_context, "screen_extraction_diagnostics", spy_screen)

    snapshot_context.build_pipeline_context_from_snapshot(snapshot_fixture("wi014_toy"))

    assert order[0] == "screen_extraction_diagnostics", order
    assert "lower_constraints" in order, order
