"""A blocking extraction diagnostic halts the exact route, on both routes (REQ-DIAG-02/03).

The sink these pin is `elaboration/extraction_screen.py`, reached from the elaborator's
single read of the identified constraint facts. The requirement predates it: it used to be
discharged by `analysis/diagnostic_screen.py`, which was called only from the two v5
builders and lost both call sites when they were retired. See
`docs/architecture/reference/30-diagnostic-severity.md`.

The `non_finite_literal` fixture is the one modelled shape that produces a BLOCKING
diagnostic; the writer-side severity table has exactly one entry. The advisory pin below is
therefore synthetic, and says so.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    DiagnosticSeverity,
    ExtractionDiagnosticFact,
    LocationFact,
)

from sysml_codegen.elaboration import ElaborationCode, ElaborationDiagnosticError
from sysml_codegen.elaboration.diagnostics import ElaborationInvariantError
from sysml_codegen.elaboration.extraction_screen import screen_extraction_diagnostics
from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

BLOCKING_FIXTURE = FIXTURES_DIR / "non_finite_literal"


def _assert_names_the_blocking_diagnostic(error: ElaborationDiagnosticError) -> None:
    diagnostics = error.diagnostics
    assert [diagnostic.code for diagnostic in diagnostics] == [
        ElaborationCode.EXTRACTION_DIAGNOSTIC_BLOCKING
    ]
    detail = diagnostics[0].detail
    assert "blocking/non_finite_literal" in detail
    assert "model.sysml:36:24" in detail
    assert "inf" in detail


@requires_license
def test_the_live_route_refuses_a_blocking_diagnostic_by_its_typed_error() -> None:
    with pytest.raises(ElaborationDiagnosticError) as caught:
        build_elaborated_pipeline([BLOCKING_FIXTURE])

    _assert_names_the_blocking_diagnostic(caught.value)
    # Before the screen existed the route still halted, but by accident: projection
    # hit `json.dumps(inf)` and raised a bare ValueError naming nothing in the model.
    assert not isinstance(caught.value, ValueError)


@requires_license
def test_capture_refuses_a_blocking_diagnostic_before_it_seals_anything(tmp_path: Path) -> None:
    destination = tmp_path / "case.json"

    with pytest.raises(ElaborationDiagnosticError) as caught:
        capture_instance_graph_snapshot([BLOCKING_FIXTURE], destination)

    _assert_names_the_blocking_diagnostic(caught.value)
    assert not destination.exists()
    assert list(tmp_path.iterdir()) == []


def _advisory_fact() -> ExtractionDiagnosticFact:
    """A synthetic ADVISORY diagnostic.

    `EXTRACTION_DIAGNOSTIC_SEVERITY` has one entry today and it is BLOCKING, so no
    model can produce an advisory fact. Rather than add a kind upstream to make the
    branch reachable, this rewrites the writer-derived severity on a real fact — the
    screen reads the field and looks nothing up, so the field is the whole input.
    """
    fact = ExtractionDiagnosticFact(
        kind="non_finite_literal",
        message="synthetic advisory",
        operand_source="1.0e400",
        location=LocationFact(file="synthetic.sysml", line=7, column=3),
    )
    fact.severity = DiagnosticSeverity.ADVISORY
    return fact


def _facts(*diagnostics: ExtractionDiagnosticFact) -> ConstraintFacts:
    return ConstraintFacts(
        definitions=[], usages=[], contexts=[], diagnostics=list(diagnostics)
    )


def test_an_advisory_diagnostic_is_rendered_and_the_screen_continues(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING):
        screen_extraction_diagnostics(_facts(_advisory_fact()))

    assert "advisory/non_finite_literal" in caplog.text
    assert "synthetic.sysml:7:3" in caplog.text


def test_advisory_rendering_cannot_swallow_the_blocking_halt(
    caplog: pytest.LogCaptureFixture,
) -> None:
    blocking = ExtractionDiagnosticFact(
        kind="non_finite_literal",
        message="blocking operand",
        operand_source="1.0e400",
        location=None,
    )

    with caplog.at_level(logging.WARNING):
        with pytest.raises(ElaborationInvariantError) as caught:
            screen_extraction_diagnostics(_facts(_advisory_fact(), blocking))

    # The advisory was rendered first and the halt still landed. A missing location
    # degrades to `<no location>` rather than raising, so it cannot pre-empt the halt.
    assert "synthetic.sysml:7:3" in caplog.text
    assert caught.value.code is ElaborationCode.EXTRACTION_DIAGNOSTIC_BLOCKING
    assert "<no location>" in caught.value.detail
    assert "blocking operand" in caught.value.detail


# --- The first real ADVISORY kind (CONSTRAINT-SEMANTICS Item 2, invariant 61) ----------
#
# Until now every pin in this module used a synthetic fact with `severity` forced to
# ADVISORY, because the writer table had no advisory kind. `vacuous_asserted_gate` is the
# first real one, so these assert the *existing* sink handles it — no sink change was
# needed, which is the point of routing the advisory through the companion rather than
# inventing a second channel.

VACUOUS_FIXTURE = FIXTURES_DIR / "constraint_domain_detached_owner"


@requires_license
def test_the_sink_renders_the_new_advisory_kind_without_halting(
    caplog: pytest.LogCaptureFixture,
) -> None:
    from agentic_mbse.sysml.constraint_extraction import extract_identified_constraint_facts
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    extractor = SysMLDataExtractor([VACUOUS_FIXTURE])
    assert extractor.load_models()
    facts = extract_identified_constraint_facts(extractor.model).facts

    with caplog.at_level(logging.WARNING):
        screen_extraction_diagnostics(facts)

    assert "advisory/vacuous_asserted_gate" in caplog.text
    assert "vacuous_gate" in caplog.text
    assert "model.sysml:" in caplog.text


@requires_license
def test_generation_completes_with_the_advisory_present() -> None:
    """Warning grade means warning grade: the package still builds."""
    assert build_elaborated_pipeline([VACUOUS_FIXTURE]) is not None


@requires_license
def test_the_domain_is_identical_with_the_advisory_suppressed(monkeypatch) -> None:
    """Invariant 59 independence: codegen's grading never consults authoring validation."""
    from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths

    with_advisory = elaborate_model_paths([VACUOUS_FIXTURE]).constraint_usages

    import sys

    monkeypatch.setattr(
        sys.modules["sysml_codegen.elaboration.elaborate"],
        "screen_extraction_diagnostics",
        lambda facts, source_referents=None: None,
    )
    without_advisory = elaborate_model_paths([VACUOUS_FIXTURE]).constraint_usages

    assert with_advisory == without_advisory
    assert [
        record.disposition
        for record in with_advisory.values()
        if record.disposition.severity == "warning"
    ]
