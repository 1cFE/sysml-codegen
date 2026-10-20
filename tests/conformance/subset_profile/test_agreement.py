"""Every case's two stored answers agree, or the record lists exactly how they disagree.

Item 2a spec C1 and C3, design § C and D3. For each case, wherever it lives, the stored
screen answer is judged against the stored generator answer by the agreement rule
(``cases.disagreement``). A case that agrees passes; a case that disagrees passes only if
the hand-edited record lists that exact disagreement (subject, kind, codes and reasons).
Then the record's case entries must be exactly the computed ones, so an entry whose case
has started to agree, or whose case is gone, fails too. Fixture entries are held the same
way, live, by ``test_fixture_agreement.py``.

Both answers are stored and reviewed, so this test is pure. ``test_generator_half.py`` and
``test_screen_half.py`` hold each stored answer to its live half.
"""

from __future__ import annotations

import pytest

from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.cases import Disagreement, StoredAnswer

ANSWERS = cases.all_answers()
RECORD = cases.read_disagreements()


def _computed(answer: StoredAnswer) -> Disagreement | None:
    return cases.disagreement(answer.subject, answer.generator.run, cases.screen_of(answer))


@pytest.mark.parametrize("answer", ANSWERS, ids=lambda a: a.case_id)
def test_a_case_agrees_or_its_disagreement_is_recorded(answer: StoredAnswer):
    found = _computed(answer)
    assert found is None or cases.recorded(found, RECORD), found


def test_the_records_case_entries_are_exactly_the_computed_disagreements():
    computed = {d for a in ANSWERS if (d := _computed(a)) is not None}
    recorded = {e.disagreement for e in RECORD if e.disagreement.subject.startswith("case:")}
    assert recorded - computed == set(), "recorded, but the case now agrees or is gone"
    assert computed - recorded == set(), "disagrees, but the record does not list it"
