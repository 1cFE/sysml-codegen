"""Disabling one shape's recognizer breaks agreement on exactly the stored cases (§ B, B5).

A screen mutation passes only when the live screen stops agreeing with the stored generator
answer (design D5), never by matching or missing the stored screen answer. Only a case whose
stored screen answer refuses the shape can change: the mutation removes that shape's
recognitions and nothing else. Of those, the ones whose disagreement changes must be the
stored set in ``mutations.json``. A case the screen also refuses for another shape, with a
code the generator gives, keeps agreeing (design O7).

Licensed.
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.conformance_case import screen_answer
from agentic_mbse.sysml.subset_profile import Outcome

from tests.conftest import requires_license
from tests.helpers.subset_profile import cases, mutate, observe, witnesses

pytestmark = requires_license

RECORD = witnesses.read_mutations()


@pytest.mark.parametrize("rule_shape", sorted(RECORD.screen), ids="/".join)
def test_disabling_a_recognizer_breaks_agreement_on_exactly_the_stored_cases(rule_shape):
    rule, shape = rule_shape
    subjects = [
        a
        for a in cases.all_answers()
        if any(
            (f.rule, f.shape, f.outcome) == (rule, shape, Outcome.REFUSED)
            for f in cases.screen_of(a).findings
        )
    ]
    changed = set()
    with mutate.disable_recognizer(rule, shape):
        for answer in subjects:
            live = screen_answer(observe.screen_half(cases.model_root(answer)))
            before = cases.disagreement(
                answer.subject, answer.generator.run, cases.screen_of(answer)
            )
            after = cases.disagreement(answer.subject, answer.generator.run, live)
            if after != before:
                changed.add(answer.case_id)
    assert changed == RECORD.screen[rule_shape]
