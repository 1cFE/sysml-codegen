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
    """65 authored usages -> 65 domain members, 9 of them eligible."""
    records = catf_mfe_d5_graph.constraint_usages
    assert len(records) == 65
    assert sum(1 for record in records.values() if record.disposition.kind == "eligible") == 9


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
