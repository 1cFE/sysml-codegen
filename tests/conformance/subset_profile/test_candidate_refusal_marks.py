"""A candidate refusal is marked the same way in the records and in the cases (Item 2a D10).

A loss that should block, pending the owner's RG-1 decision, is marked twice: the record
admission carries the ``candidate_refusal`` qualification, and each case it cites carries a
``loss`` block with that disposition. Each mark implies the other, so neither side can drift
alone. That each case's ``RG1-<n>`` is well formed is the stored-answer loader's check.

Pure: reads the packaged records and the stored answers.
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.subset_profile import PACKAGED_RULES, CaseRef, Qualification

from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.cases import LossDisposition

CITED = sorted(
    {
        (ref.case_id, admission.qualification is Qualification.CANDIDATE_REFUSAL)
        for rule in PACKAGED_RULES.rules
        for shape in rule.shapes
        for admission in shape.admissions.values()
        for ref in admission.evidence
        if isinstance(ref, CaseRef)
    }
)


def _is_candidate(case_id: str) -> bool:
    loss = cases.load_answer(case_id).loss
    return loss is not None and loss.disposition is LossDisposition.CANDIDATE_REFUSAL


def test_no_case_is_cited_both_as_a_candidate_and_not():
    case_ids = [case_id for case_id, _ in CITED]
    assert len(case_ids) == len(set(case_ids))


def test_some_admission_is_a_candidate_refusal():
    assert any(candidate for _, candidate in CITED)


@pytest.mark.parametrize(("case_id", "candidate"), CITED, ids=lambda v: str(v))
def test_a_record_candidate_refusal_holds_iff_its_case_marks_it(case_id: str, candidate: bool):
    assert _is_candidate(case_id) == candidate
