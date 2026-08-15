"""D3's bucket table, row by row, over records built here — no fixture, no generation.

The table is the rule the report, the preflight, and the validators all read, so it is
proved directly rather than through a model. A hand-built record can put a reason token on a
form the corpus does not currently pair it with, which is what makes the totality claim
("every record lands in exactly one bucket, for every token in the closed vocabulary") a
claim about the rule instead of a claim about today's fixtures.

`tests/unit/test_coverage_ledger_agreement.py` is the other half: the same rule against real
models, checked against accounts hand-written from their `.sysml` sources.
"""

from __future__ import annotations

import itertools

import pytest

from sysml_codegen.core.errors import CodeGenerationError
from sysml_codegen.elaboration.graph import (
    ASSERTED_SOURCE_FORMS,
    DISPOSITION_REASONS,
    SOURCE_FORMS,
)
from sysml_codegen.generation.coverage import (
    KNOWN_REASONS,
    assert_reason_vocabulary_is_known,
    coverage_account,
)
from sysml_codegen.resolution.models import ConstraintCatalog, ConstraintCatalogUsageRecord

_IDS = itertools.count()


def record(
    *,
    form: str,
    kind: str,
    reason: str,
    inapplicability_reason: str | None = None,
    occurrence_count: int = 0,
) -> ConstraintCatalogUsageRecord:
    """One usage record, with only the fields the bucket table reads made interesting."""
    index = next(_IDS)
    return ConstraintCatalogUsageRecord(
        declaration_id=f"decl-{index}",
        usage_qualified_name=f"Pkg::Host::gate_{index}",
        source_local_identity=f"gate_{index}",
        source_form=form,
        owner_kind="part_def",
        owner_qualified_name="Pkg::Host",
        definition_qualified_name=None,
        membership_kind=None,
        is_negated=False,
        expected_value=True,
        disposition_kind=kind,
        disposition_reason=reason,
        disposition_severity="info",
        disposition_detail="",
        inapplicability_reason=inapplicability_reason,
        occurrence_count=occurrence_count,
    )


def catalog_of(*records: ConstraintCatalogUsageRecord) -> ConstraintCatalog:
    return ConstraintCatalog(usage_records=list(records), fingerprint="0" * 64)


# ---------------------------------------------------------------------------
# The table itself
# ---------------------------------------------------------------------------


def test_every_bucket_row_over_hand_built_records():
    """One record per row, so each row's contribution is separable in the totals."""
    account = coverage_account(
        catalog_of(
            record(form="plain_usage", kind="excluded", reason="unassessed_form"),  # row 1
            record(
                form="definition_typed",
                kind="excluded",
                reason="non_numerical",
                inapplicability_reason="vacuous",
            ),  # row 2
            record(
                form="inline", kind="eligible", reason="admitted", occurrence_count=1
            ),  # row 3
            record(
                form="named_usage_reference", kind="non_reaching", reason="owner_absent"
            ),  # row 4
        )
    )
    assert account.authored_usage_total == 4
    assert account.applicable_gate_total == 2
    assert account.assessed_gate_count == 1
    assert account.unassessed_gate_count == 1
    assert account.inapplicable_gate_count == 1
    assert account.unassessed_reasons == {"owner_absent": 1}
    assert account.coverage_state == "partial"


@pytest.mark.parametrize("form", sorted(SOURCE_FORMS - ASSERTED_SOURCE_FORMS))
def test_a_non_asserted_form_is_inventory_whatever_its_disposition(form: str):
    """Row 1 is decided by the form alone — the disposition beside it never promotes it."""
    account = coverage_account(
        catalog_of(
            record(form=form, kind="eligible", reason="admitted", occurrence_count=3),
        )
    )
    assert account.authored_usage_total == 1
    assert account.applicable_gate_total == 0
    assert account.inapplicable_gate_count == 0
    assert account.coverage_state == "none"


@pytest.mark.parametrize(
    "kind,reason",
    sorted(
        (kind, reason)
        for kind, reasons in DISPOSITION_REASONS.items()
        for reason in reasons
        if reason != "admitted"
    ),
)
@pytest.mark.parametrize("form", sorted(ASSERTED_SOURCE_FORMS))
def test_each_reason_token_buckets_as_unassessed_and_the_identities_hold(
    kind: str, reason: str, form: str
):
    """Row 4 over all nine non-`admitted` tokens: `excluded` and `non_reaching` share a bucket.

    An asserted gate the profile excluded and one that reached nothing are both gates the
    author wrote and nobody checked. Keeping them in the denominator is what stops a model
    from shrinking its way to full satisfaction.
    """
    account = coverage_account(catalog_of(record(form=form, kind=kind, reason=reason)))
    assert account.applicable_gate_total == 1
    assert account.assessed_gate_count == 0
    assert account.unassessed_gate_count == 1
    assert account.unassessed_reasons == {reason: 1}
    assert account.coverage_state == "partial"


@pytest.mark.parametrize("form", sorted(ASSERTED_SOURCE_FORMS))
def test_an_inapplicable_marker_removes_an_asserted_gate_from_the_denominator(form: str):
    """Row 2, for every asserted form and whatever the disposition beside the marker."""
    account = coverage_account(
        catalog_of(
            record(
                form=form,
                kind="non_reaching",
                reason="owner_has_no_occurrences",
                inapplicability_reason="no build of this variant is planned",
            )
        )
    )
    assert account.applicable_gate_total == 0
    assert account.inapplicable_gate_count == 1
    assert account.unassessed_reasons == {}
    assert account.coverage_state == "none"


def test_an_empty_catalog_accounts_for_nothing():
    account = coverage_account(catalog_of())
    assert account.as_mapping() == {
        "authored_usage_total": 0,
        "applicable_gate_total": 0,
        "assessed_gate_count": 0,
        "unassessed_gate_count": 0,
        "inapplicable_gate_count": 0,
        "unassessed_reasons": {},
        "coverage_state": "none",
    }


def test_the_histogram_counts_repeats_and_lists_no_zero_keys():
    """D2's derived-keys rule: a key appears iff a record landed on it (DR-3)."""
    account = coverage_account(
        catalog_of(
            record(form="inline", kind="non_reaching", reason="owner_absent"),
            record(form="inline", kind="non_reaching", reason="owner_absent"),
            record(form="inline", kind="excluded", reason="non_numerical"),
        )
    )
    assert account.unassessed_reasons == {"non_numerical": 1, "owner_absent": 2}


def test_coverage_state_is_complete_only_when_a_gate_was_actually_assessed():
    """`none` and `complete` are not the same answer, and neither is `partial`."""
    assessed = coverage_account(
        catalog_of(record(form="inline", kind="eligible", reason="admitted", occurrence_count=1))
    )
    nothing_applicable = coverage_account(
        catalog_of(record(form="plain_usage", kind="excluded", reason="unassessed_form"))
    )
    assert assessed.coverage_state == "complete"
    assert nothing_applicable.coverage_state == "none"


# ---------------------------------------------------------------------------
# The two refusals
# ---------------------------------------------------------------------------


def test_eligible_plus_inapplicable_is_refused_by_name():
    """D9. The message names the usage, its declaration id, and the entry count."""
    with pytest.raises(CodeGenerationError, match="marked inapplicable but produced") as raised:
        coverage_account(
            catalog_of(
                record(
                    form="inline",
                    kind="eligible",
                    reason="admitted",
                    inapplicability_reason="vacuous",
                    occurrence_count=4,
                )
            )
        )
    message = str(raised.value)
    assert "decl-" in message and "produced 4 executable entries" in message


def test_an_unknown_reason_refuses_with_the_ruling_instruction():
    """The `KNOWN_REASONS` pin: a reason Item 2 adds must force a coverage ruling."""
    with pytest.raises(CodeGenerationError, match="has not been taught reason") as raised:
        assert_reason_vocabulary_is_known(
            {"eligible": frozenset({"admitted"}), "excluded": frozenset({"brand_new"})}
        )
    assert "'brand_new'" in str(raised.value)
    assert "inside or outside the feasibility denominator" in str(raised.value)


def test_the_shipped_vocabulary_is_taught_in_full():
    """Both directions, so `KNOWN_REASONS` cannot drift from Item 2's closed vocabulary."""
    assert_reason_vocabulary_is_known()
    authored = {reason for reasons in DISPOSITION_REASONS.values() for reason in reasons}
    assert set(KNOWN_REASONS) == authored
