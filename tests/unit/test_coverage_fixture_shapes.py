"""Each coverage fixture really produces the dispositions its ledger entry assumes.

This is a **shape** check against Item 2's landed catalog, not a coverage assertion. It runs
before `coverage_account()` exists so that a mis-shaped fixture is caught here, cheaply,
rather than in Phase 5 when it is load-bearing — the lesson from Item 13's cell 18, where an
over-built fixture read as a product defect for days.

The expected dispositions come from each fixture's `.sysml` source read against D3's bucket
table; the accounts they imply are in
`.project/active/constraint-coverage-policy/expected-coverage.md`.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from sysml_codegen.elaboration import project
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

#: fixture -> (disposition-kind histogram, how many records carry an inapplicability marker).
COVERAGE_FIXTURE_SHAPES = [
    # Authored for this item.
    ("constraint_coverage_zero_eligible", {"non_reaching": 1}, 0),
    ("constraint_coverage_all_inapplicable", {"non_reaching": 1}, 1),
    ("constraint_coverage_violation_partial", {"eligible": 1, "non_reaching": 1}, 0),
    ("constraint_coverage_eligible_inapplicable", {"eligible": 1}, 1),
    # Reused, per the PD4 survey.
    ("constraint_domain_detached_owner", {"eligible": 1, "non_reaching": 1}, 0),
    ("constraint_domain_inapplicable", {"eligible": 1, "non_reaching": 1}, 1),
    ("constraint_non_numerical", {"eligible": 1, "excluded": 1}, 0),
    ("constraint_domain_plain_forms", {"excluded": 1, "non_reaching": 1}, 0),
    ("constraint_domain_satisfy", {"excluded": 2}, 0),
]


@pytest.mark.parametrize(
    "fixture,expected_kinds,expected_markers",
    COVERAGE_FIXTURE_SHAPES,
    ids=[row[0] for row in COVERAGE_FIXTURE_SHAPES],
)
def test_fixture_produces_the_intended_dispositions(
    fixture: str, expected_kinds: dict[str, int], expected_markers: int
):
    catalog = project(
        elaborate_model_paths([Path(FIXTURES_DIR / fixture)])
    ).constraint_catalog
    assert catalog is not None
    records = catalog.usage_records
    assert Counter(record.disposition_kind for record in records) == Counter(expected_kinds)
    assert (
        sum(1 for record in records if record.inapplicability_reason is not None)
        == expected_markers
    )


def test_the_d9_fixture_carries_the_contradiction_it_exists_to_provoke():
    """`eligible` beside an inapplicability marker — the one shape D9 refuses.

    Stated separately from the histogram above because it is the *combination* on a single
    record that matters, and a histogram cannot see a combination.
    """
    catalog = project(
        elaborate_model_paths(
            [Path(FIXTURES_DIR / "constraint_coverage_eligible_inapplicable")]
        )
    ).constraint_catalog
    (record,) = catalog.usage_records
    assert record.disposition_kind == "eligible"
    assert record.inapplicability_reason == "this gate is not part of the feasible set"
    assert record.occurrence_count == 1
