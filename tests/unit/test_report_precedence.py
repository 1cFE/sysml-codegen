"""D6's precedence, and the validators, over the code the template actually emits.

The aggregator's `run` is generated, so the precedence rule is tested by rendering a real
aggregator and executing its module. Rewriting the five arms in the test would prove the test
agrees with itself.

`simkit` is imported by the generated module, so these run in the same environment the
execution lane uses.
"""

from __future__ import annotations

import pytest

from sysml_codegen.generation.coverage import CoverageAccountData

COMPLETE = CoverageAccountData(
    authored_usage_total=1,
    applicable_gate_total=1,
    assessed_gate_count=1,
    unassessed_gate_count=0,
    inapplicable_gate_count=0,
)
PARTIAL = CoverageAccountData(
    authored_usage_total=2,
    applicable_gate_total=2,
    assessed_gate_count=1,
    unassessed_gate_count=1,
    inapplicable_gate_count=0,
    unassessed_reasons={"owner_has_no_occurrences": 1},
)
NONE = CoverageAccountData(
    authored_usage_total=1,
    applicable_gate_total=0,
    assessed_gate_count=0,
    unassessed_gate_count=0,
    inapplicable_gate_count=0,
)
ALL_INAPPLICABLE = CoverageAccountData(
    authored_usage_total=1,
    applicable_gate_total=0,
    assessed_gate_count=0,
    unassessed_gate_count=0,
    inapplicable_gate_count=1,
)


@pytest.mark.parametrize(
    "statuses,account,expected",
    [
        # The top arm survives partial coverage: a violated gate is a violated gate, and the
        # account beside it still says the denominator was not whole.
        (["violated", "satisfied"], PARTIAL, "violation"),
        (["violated"], COMPLETE, "violation"),
        (["indeterminate", "satisfied"], COMPLETE, "indeterminate"),
        # Indeterminate outranks partial coverage — the interaction this item created, and the
        # one contract-ordered pair that had no test at any tier. "We could not assess this
        # gate" is a stronger statement about the candidate than "we did not assess that one",
        # so the status arm must win over the account arm.
        (["indeterminate"], PARTIAL, "indeterminate"),
        (["indeterminate", "satisfied"], PARTIAL, "indeterminate"),
        # Everything assessed passed, and everything applicable was assessed.
        (["satisfied"], COMPLETE, "full_satisfaction"),
        # Spec success criterion 3: full satisfaction is unclaimable under partial assessment,
        # even though every gate that ran passed.
        (["satisfied"], PARTIAL, "partial_coverage"),
        # Both zero-input branches, distinguished by the account alone.
        ([], PARTIAL, "partial_coverage"),
        ([], NONE, "not_assessed"),
        # D4's ruling: every asserted gate waived leaves nothing to have passed.
        ([], ALL_INAPPLICABLE, "not_assessed"),
    ],
    ids=[
        "violation-over-partial",
        "violation-over-complete",
        "indeterminate",
        "indeterminate-over-partial",
        "indeterminate-over-partial-with-a-pass",
        "full-satisfaction",
        "satisfied-but-partial",
        "zero-input-partial",
        "zero-input-descriptive",
        "zero-input-all-inapplicable",
    ],
)
def test_precedence(rendered_aggregator, statuses, account, expected):
    report = rendered_aggregator(statuses, account)
    assert report.headline == expected
    assert report.assessed_entry_count == len(statuses)
    assert report.coverage.coverage_state == account.coverage_state


def test_the_two_tiers_are_deliberately_asymmetric(rendered_aggregator):
    """DR-12: one gate over forty occurrences. This is the rule working, not a bug to fix.

    `assessed_gate_count` counts usages and `assessed_entry_count` counts occurrences. A
    later reader who "reconciles" them removes the only way to tell forty checks of one gate
    from one check each of forty gates.
    """
    report = rendered_aggregator(["satisfied"] * 40, COMPLETE)
    assert report.coverage.assessed_gate_count == 1
    assert report.assessed_entry_count == 40
    assert report.headline == "full_satisfaction"


def test_a_violation_still_states_its_coverage(rendered_aggregator):
    """The two axes are orthogonal, which is the point of carrying the account always."""
    report = rendered_aggregator(["violated"], PARTIAL)
    assert report.headline == "violation"
    assert report.coverage.coverage_state == "partial"
    assert report.coverage.unassessed_gate_count == 1
    assert report.coverage.unassessed_reasons == {"owner_has_no_occurrences": 1}


# ---------------------------------------------------------------------------
# The validators
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "overrides,message",
    [
        ({"assessed_gate_count": 3}, "!= applicable"),
        ({"unassessed_reasons": {"owner_absent": 5}}, "unassessed_reasons sums to"),
        ({"coverage_state": "complete"}, "disagrees with the counts"),
    ],
    ids=["identity-broken", "histogram-does-not-sum", "state-disagrees"],
)
def test_coverage_account_rejects_inconsistent_arithmetic(
    coverage_account_model, overrides, message
):
    """An internally inconsistent bake cannot construct — the second end of D3's check."""
    from pydantic import ValidationError

    payload = PARTIAL.as_mapping() | overrides
    with pytest.raises(ValidationError, match=message):
        coverage_account_model(**payload)


def test_a_consistent_account_constructs(coverage_account_model):
    """The negative cases above are worthless if the positive one does not pass."""
    account = coverage_account_model(**PARTIAL.as_mapping())
    assert account.coverage_state == "partial"


def test_the_headline_literal_refuses_the_retired_token(constraint_report_model):
    """B5: a stale producer writing `all_satisfied` is refused at construction, not read."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        constraint_report_model(
            catalog_fingerprint="0" * 64,
            assessed_entry_count=1,
            headline="all_satisfied",
            coverage=COMPLETE.as_mapping(),
            results=[],
        )
