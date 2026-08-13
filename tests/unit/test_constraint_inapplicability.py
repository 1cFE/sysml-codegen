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

from sysml_codegen.elaboration.elaborate import ElaborationDiagnosticError
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


def test_a_malformed_annotation_halts_rather_than_doing_nothing():
    with pytest.raises(ElaborationDiagnosticError, match="malformed inapplicability annotation"):
        elaborate_model_paths(
            [Path(FIXTURES_DIR / "constraint_domain_inapplicable_malformed")]
        )


def test_a_marker_on_a_later_documentation_line_halts():
    with pytest.raises(ElaborationDiagnosticError, match="later documentation line"):
        elaborate_model_paths(
            [Path(FIXTURES_DIR / "constraint_domain_inapplicable_late_marker")]
        )


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
