"""The mint: one visible record per authored usage, one disposition, never a raise.

Each test names the fixture shape it pins, because the point of these is severity *by
cause*: the same empty attachment is an authoring error under one owner kind, a vacuous
gate under another, and an ordinary fact under a non-asserted form.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.elaboration.diagnostics import ElaborationCode
from sysml_codegen.elaboration.elaborate import ElaborationDiagnosticError
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


def _domain(fixture: str) -> dict[str, object]:
    graph = elaborate_model_paths([Path(FIXTURES_DIR / fixture)])
    return {
        record.usage_qualified_name: record for record in graph.constraint_usages.values()
    }


def _disposition(record) -> tuple[str, str, str]:
    return (record.disposition.kind, record.disposition.reason, record.disposition.severity)


def test_asserted_gate_owned_by_a_calc_def_halts_naming_the_missing_attachment():
    with pytest.raises(ElaborationDiagnosticError) as raised:
        elaborate_model_paths([Path(FIXTURES_DIR / "constraint_domain_calc_def_owner")])
    (diagnostic,) = [
        item
        for item in raised.value.diagnostics
        if item.code is ElaborationCode.SI_CONSTRAINT_UNATTACHED
    ]
    assert "constraint_domain_calc_def_owner::Sizer::demand_positive" in diagnostic.detail
    assert "constraint_domain_calc_def_owner::Sizer" in diagnostic.detail
    assert "calc_def" in diagnostic.detail
    assert "owner_kind_unattachable" in diagnostic.detail


def test_asserted_gate_on_a_detached_part_def_warns_and_keeps_generating():
    domain = _domain("constraint_domain_detached_owner")
    vacuous = domain["constraint_domain_detached_owner::Detached::vacuous_gate"]
    assert _disposition(vacuous) == ("non_reaching", "owner_has_no_occurrences", "warning")
    assert vacuous.occurrence_count == 0
    reached = domain["constraint_domain_detached_owner::Live::reached_gate"]
    assert _disposition(reached) == ("eligible", "admitted", "info")
    assert reached.occurrence_count == 1


def test_a_typed_but_uninstantiated_owner_is_still_graded_vacuous():
    """Invariant 9's containment direction, codegen side.

    ``Typed`` *is* typed by a part usage, so the companion's structural trigger cannot
    see it. Codegen reads the occurrence index and grades it anyway, which is what makes
    the companion's trigger set a strict subset rather than a disagreement.
    """
    domain = _domain("constraint_domain_containment")
    nested = domain["constraint_domain_containment::Typed::nested_vacuous_gate"]
    assert _disposition(nested) == ("non_reaching", "owner_has_no_occurrences", "warning")


def test_non_asserted_forms_never_grade_error_whatever_their_predicate_would_do():
    """Invariant 5 and 7 together: the form gate runs before any predicate walk."""
    domain = _domain("constraint_domain_plain_forms")
    blocked = domain["constraint_domain_plain_forms::Host::blocked_if_asserted"]
    assert _disposition(blocked) == ("excluded", "unassessed_form", "info")
    unreached = domain["constraint_domain_plain_forms::Detached::unreached_plain"]
    assert _disposition(unreached) == ("non_reaching", "owner_has_no_occurrences", "info")


def test_a_blocked_decision_that_reaches_nothing_is_non_reaching_and_emits_no_block():
    """Precedence step 2 beats step 3, and there is no predicate to block."""
    graph = elaborate_model_paths(
        [Path(FIXTURES_DIR / "constraint_domain_block_non_reaching")]
    )
    record = graph.constraint_usages[
        next(
            key
            for key, value in graph.constraint_usages.items()
            if value.usage_qualified_name.endswith("blocked_and_unreached")
        )
    ]
    assert _disposition(record) == ("non_reaching", "owner_has_no_occurrences", "warning")
    assert not [
        item
        for item in graph.diagnostics
        if item.code is ElaborationCode.SI_CONSTRAINT_BLOCKED
    ]


def test_satisfy_is_its_own_form_with_its_own_named_exclusion():
    domain = _domain("constraint_domain_satisfy")
    satisfy = domain["constraint_domain_satisfy::the_rig::budget_met"]
    assert satisfy.source_form == "satisfy_reference"
    assert _disposition(satisfy) == ("excluded", "out_of_scope_satisfy", "info")
    required = domain["constraint_domain_satisfy::MassBudget::within"]
    assert _disposition(required) == ("excluded", "out_of_profile_owner", "info")


def test_the_form_gate_is_precedence_step_one_and_beats_the_unattachable_halt():
    """A ``satisfy`` owned by a ``calc def`` matches two rows; step 1 wins, so no halt."""
    domain = _domain("constraint_domain_satisfy_calc_def")
    satisfy = domain["constraint_domain_satisfy_calc_def::Sizer::budget_met"]
    assert satisfy.owner_kind == "calc_def"
    assert _disposition(satisfy) == ("excluded", "out_of_scope_satisfy", "info")


def test_every_domain_member_carries_its_identity_join_and_source_location():
    domain = _domain("constraint_domain_detached_owner")
    for record in domain.values():
        assert record.declaration_id is not None
        assert record.source_file.endswith(".sysml")
        assert record.source_line > 0
        assert record.owner_qualified_name
