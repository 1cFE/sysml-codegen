"""Every authored constraint usage is a visible domain member with one disposition.

The lifecycle contract promises that an authored constraint usage never simply
disappears (invariants 1 and 28). Before this item the exact route minted records only
*after* owner-to-scope expansion, so a usage whose owner yielded zero scopes emitted
nothing: ``catf_mfe_d5`` authors 65 constraint usages and produced 9 carriers.

This module pins the headline. It is deliberately identity-shaped where it can be and
count-shaped where the fixture's own authored population is the claim.
"""

from __future__ import annotations

import pytest

from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


@pytest.fixture(scope="module")
def catf_mfe_d5_graph():
    return elaborate_model_paths([FIXTURES_DIR / "catf_mfe_d5"])


def test_catf_mfe_d5_authored_population_is_total(catf_mfe_d5_graph):
    """65 authored usages -> 65 domain members, 9 of which reach an instance.

    The design and plan both call the 9 "eligible". Measured, they are not: every one of
    ``catf_mfe_d5``'s 65 usages is a bare ``constraint``, so the 9 that expand grade
    ``excluded`` / ``unassessed_form`` and the fixture has **zero** eligible constraints.
    The 9 was always the count of *visible dispositions* — the pre-item catalog carried
    9 ``excluded_records`` and an empty ``usage_records`` list. The totality claim this
    item exists for is unaffected, and the correction is recorded in the plan.
    """
    records = catf_mfe_d5_graph.constraint_usages
    assert len(records) == 65
    assert sum(1 for record in records.values() if record.occurrence_count > 0) == 9
    assert sum(1 for record in records.values() if record.disposition.kind == "eligible") == 0


def test_catf_mfe_d5_dispositions_split_by_the_precedence_rule(catf_mfe_d5_graph):
    """The 56 absences resolve into the two expansion causes the research named."""
    by_reason: dict[str, int] = {}
    for record in catf_mfe_d5_graph.constraint_usages.values():
        by_reason[record.disposition.reason] = by_reason.get(record.disposition.reason, 0) + 1
    assert by_reason == {
        "owner_kind_unattachable": 51,
        "owner_has_no_occurrences": 5,
        "unassessed_form": 9,
    }


def test_catf_mfe_d5_never_halts_on_its_non_asserted_population(catf_mfe_d5_graph):
    """No non-asserted form grades error, so the frozen twin still generates."""
    assert not [
        record
        for record in catf_mfe_d5_graph.constraint_usages.values()
        if record.disposition.severity == "error"
    ]


def test_every_member_carries_exactly_one_disposition(catf_mfe_d5_graph):
    for record in catf_mfe_d5_graph.constraint_usages.values():
        assert record.disposition is not None
        assert record.disposition.kind in {"eligible", "excluded", "non_reaching"}


def test_occurrence_nodes_join_the_domain_by_declaration_id(catf_mfe_d5_graph):
    """The two tiers join by identity, and the arity agrees in both directions."""
    records = catf_mfe_d5_graph.constraint_usages
    counted: dict[object, int] = {}
    for node in catf_mfe_d5_graph.constraints.values():
        assert node.declaration_id in records
        counted[node.declaration_id] = counted.get(node.declaration_id, 0) + 1
    for declaration_id, record in records.items():
        assert record.occurrence_count == counted.get(declaration_id, 0)
