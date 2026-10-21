"""Every case has one generator answer and one home (Item 2a design D14).

Pure: reads stored answers and the case folders.
"""

from __future__ import annotations

from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.cases import CaseHome


def test_every_case_has_exactly_one_generator_answer_and_one_home():
    packaged, local = cases.packaged_ids(), cases.codegen_ids()
    assert packaged.isdisjoint(local)
    assert cases.answer_ids() == packaged | local
    for answer in cases.all_answers():
        expected = CaseHome.AGENTIC if answer.case_id in packaged else CaseHome.CODEGEN
        assert answer.home is expected, answer.case_id
