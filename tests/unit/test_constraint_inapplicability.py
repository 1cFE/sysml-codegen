"""``@inapplicable:`` is explicit, fingerprinted, and cannot rewrite a disposition.

Marking a gate inapplicable is a *coverage* statement — it tells a later feasibility count
that this gate was never meant to be in the set. Invariant 9 is about a structural
authoring error. Keeping the two apart is why the annotation is a field beside the
disposition rather than a value folded into it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sysml_codegen.elaboration import elaborate
from sysml_codegen.elaboration.diagnostics import ElaborationCode
from sysml_codegen.elaboration.elaborate import ElaborationDiagnosticError
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from sysml_codegen.snapshot.instance_graph import encode_instance_graph
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


def _record(fixture: str, suffix: str):
    graph = elaborate_model_paths([Path(FIXTURES_DIR / fixture)])
    return next(
        record
        for record in graph.constraint_usages.values()
        if record.usage_qualified_name.endswith(suffix)
    )


def test_the_annotation_is_read_and_carried_on_the_record():
    record = _record("constraint_domain_inapplicable", "marked_vacuous")
    assert record.inapplicability is not None
    assert record.inapplicability.reason == "no build of this variant is planned"
    # The annotation is located by the record it sits on, not by a second copy of the path.
    assert record.source_file.endswith("model.sysml")
    assert record.source_line > 0


def test_the_annotation_does_not_rewrite_kind_reason_or_severity():
    record = _record("constraint_domain_inapplicable", "marked_vacuous")
    assert (
        record.disposition.kind,
        record.disposition.reason,
        record.disposition.severity,
    ) == ("non_reaching", "owner_has_no_occurrences", "warning")


def test_an_unannotated_usage_carries_no_inapplicability():
    assert _record("constraint_domain_inapplicable", "reached_gate").inapplicability is None


# --- A near-miss halts, but per usage, never model-wide (invariant 5) ------------------


def _lenient(fixture: str):
    """The graph a non-strict elaboration produces, diagnostics and all.

    Strict elaboration converts the diagnostics into the halt, so this is how a test sees
    what the halting model still carried. Invariant 5's whole claim is about that: the
    difference between a halt that names one usage and a raise that leaves the model with
    no domain at all.
    """
    extractor = SysMLDataExtractor([Path(FIXTURES_DIR / fixture)])
    assert extractor.load_models()
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=False,
    )


@pytest.mark.parametrize(
    ("fixture", "usage", "phrase"),
    [
        (
            "constraint_domain_inapplicable_malformed",
            "typo_marker",
            "malformed inapplicability annotation",
        ),
        (
            "constraint_domain_inapplicable_late_marker",
            "late_marker",
            "later documentation line",
        ),
    ],
    ids=["malformed-shape", "marker-on-a-later-line"],
)
def test_a_near_miss_halts(fixture: str, usage: str, phrase: str):
    with pytest.raises(ElaborationDiagnosticError, match=phrase) as raised:
        elaborate_model_paths([Path(FIXTURES_DIR / fixture)])
    assert usage in str(raised.value)


@pytest.mark.parametrize(
    ("fixture", "usage"),
    [
        ("constraint_domain_inapplicable_malformed", "typo_marker"),
        ("constraint_domain_inapplicable_late_marker", "late_marker"),
    ],
    ids=["malformed-shape", "marker-on-a-later-line"],
)
def test_a_near_miss_leaves_every_other_carrier_intact(fixture: str, usage: str):
    """Invariant 5: minting never raises, so one authoring typo cannot erase the domain.

    Before this cure the parse raised out of the mint, and *no* usage in the model carried
    a disposition — the absence-not-disposition failure this whole item exists to end,
    reached by a typo in one doc comment.
    """
    graph = _lenient(fixture)

    # Both authored usages are present, not just the well-formed one.
    assert len(graph.constraint_usages) == 2
    by_name = {
        record.usage_qualified_name.rsplit("::", 1)[-1]: record
        for record in graph.constraint_usages.values()
    }
    assert set(by_name) == {usage, "reached_gate"}

    defective = by_name[usage]
    assert defective.disposition.kind == "non_reaching"
    assert defective.disposition.reason == "classification_incomplete"
    assert defective.disposition.severity == "error"
    assert defective.inapplicability is None

    # The other carrier is untouched and still correctly graded.
    assert by_name["reached_gate"].disposition.severity == "info"
    assert by_name["reached_gate"].disposition.kind == "eligible"


@pytest.mark.parametrize(
    "fixture",
    [
        "constraint_domain_inapplicable_malformed",
        "constraint_domain_inapplicable_late_marker",
    ],
    ids=["malformed-shape", "marker-on-a-later-line"],
)
def test_a_near_miss_reports_exactly_one_diagnostic(fixture: str):
    """One usage is defective, so one diagnostic — not a model-wide failure."""
    codes = [item.code for item in _lenient(fixture).diagnostics]
    assert codes == [ElaborationCode.SI_CONSTRAINT_INCOMPLETE]


def test_the_annotation_moves_the_graph_fingerprint():
    """If it did not, the decision would not be sealed and a route could disagree on it."""
    graph = elaborate_model_paths([Path(FIXTURES_DIR / "constraint_domain_inapplicable")])
    annotated = json.loads(encode_instance_graph(graph))["fingerprint"]

    for record in graph.constraint_usages.values():
        record.inapplicability = None
    stripped = json.loads(encode_instance_graph(graph))["fingerprint"]

    assert annotated != stripped


def test_marking_an_unattachable_gate_does_not_suppress_the_halt():
    """Invariant 6 against invariant 9: coverage and authoring errors are different things."""
    with pytest.raises(ElaborationDiagnosticError) as raised:
        elaborate_model_paths(
            [Path(FIXTURES_DIR / "constraint_domain_inapplicable_unattachable")]
        )
    assert "marked_but_unattachable" in str(raised.value)
    assert "owner_kind_unattachable" in str(raised.value)
