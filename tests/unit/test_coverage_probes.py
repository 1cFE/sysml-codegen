"""B3 and D9's reachability claim, pinned as properties rather than left as one-off probes.

**B3.** A constraint-bearing model whose usages are *all* non-eligible still projects a
non-`None` `constraint_catalog` with non-empty `usage_records`. Everything in D5 rests on it:
the report-required trigger reads that population, so if the catalog were `None` for exactly
the models the zero-input aggregator exists to serve, the trigger would be unreadable.

**D9's reachability claim.** No usage record is both `eligible` and carries an
`inapplicability_reason`. D9 refuses that combination at generation, and the claim it breaks
nothing that exists is what makes the refusal safe to land.

Both run license-free off `catf_mfe_d5`'s committed v6 snapshot. The corpus-wide sweep behind
them (57 fixtures, 105 usage records, zero D9 hits) is recorded in
`.project/active/constraint-coverage-policy/expected-coverage.md`.
"""

from __future__ import annotations

import pytest

from tests.conftest import exact_graph_from_fixture


@pytest.fixture(scope="module")
def descriptive_only_catalog():
    """`catf_mfe_d5`: 65 authored usages, none eligible, zero concrete entries."""
    return exact_graph_from_fixture("catf_mfe_d5").constraint_catalog


def test_a_model_with_nothing_eligible_still_projects_a_catalog(descriptive_only_catalog):
    """B3. D5's trigger is unreadable if this is `None`."""
    assert descriptive_only_catalog is not None
    assert len(descriptive_only_catalog.usage_records) == 65
    assert not descriptive_only_catalog.concrete_entries
    assert not [
        record
        for record in descriptive_only_catalog.usage_records
        if record.disposition_kind == "eligible"
    ]


def test_no_usage_record_is_both_eligible_and_inapplicable(descriptive_only_catalog):
    """D9's reachability claim, on the largest catalog the tree carries license-free."""
    assert not [
        record
        for record in descriptive_only_catalog.usage_records
        if record.disposition_kind == "eligible"
        and record.inapplicability_reason is not None
    ]
