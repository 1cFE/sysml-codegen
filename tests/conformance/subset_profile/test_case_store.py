"""Every case has one generator answer and one home, and the records' citations resolve here.

Item 2a design D4 and D14. agentic-mbse checks that each cited case is packaged and that its
screen answer shows the cited pair. This module checks the generator side of the same
citations, from stored answers only: the cited case has a stored generator answer, a refused
pair's case refused with a code its reason maps to, and a case the records cite for a run the
generator completes generated. It also checks that each case is well formed on the screen
side: every ``refused`` finding sits on the case's construct (the generator side of that
check is live, in ``test_generator_half.py``).

Pure: reads stored answers, packaged ``case.json`` files and the packaged records.
"""

from __future__ import annotations

import json
from collections.abc import Iterator

import pytest
from agentic_mbse.sysml.subset_profile import (
    PACKAGED_RULES,
    SNAPSHOT_FIXTURES,
    CaseRef,
    ContextId,
    Outcome,
)

from sysml_codegen.subset_profile_adapter import REASON_MAPPING, ReasonMapping
from tests.conftest import FIXTURES_DIR
from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.cases import CaseHome, GeneratorOutcome, StoredAnswer

ANSWERS = {a.case_id: a for a in cases.all_answers()}


def test_every_case_has_exactly_one_generator_answer_and_one_home():
    packaged, local = cases.packaged_ids(), cases.codegen_ids()
    assert packaged.isdisjoint(local)
    assert cases.answer_ids() == packaged | local
    for answer in ANSWERS.values():
        expected = CaseHome.AGENTIC if answer.case_id in packaged else CaseHome.CODEGEN
        assert answer.home is expected, answer.case_id


def _citations() -> Iterator[tuple[str, str, ContextId, Outcome, str]]:
    for rule in PACKAGED_RULES.rules:
        for shape in rule.shapes:
            for context, admission in shape.admissions.items():
                for ref in admission.evidence:
                    if isinstance(ref, CaseRef):
                        yield rule.rule_id, shape.shape_id, context, admission.outcome, ref.case_id


CITATIONS = sorted(set(_citations()), key=lambda c: (c[-1], c[0], c[1]))


@pytest.mark.parametrize("citation", CITATIONS, ids=lambda c: c[-1])
def test_a_cited_case_shows_the_generator_doing_what_the_record_says(citation):
    rule_id, shape_id, context, outcome, case_id = citation
    answer = ANSWERS.get(case_id)
    assert answer is not None, f"records cite {case_id}, which has no stored generator answer"
    run = answer.generator.run
    if outcome is Outcome.REFUSED:
        shape = PACKAGED_RULES.rule(rule_id).shape(shape_id)
        mapping = REASON_MAPPING[shape.reason]
        assert isinstance(mapping, ReasonMapping), shape.reason
        assert run.outcome is GeneratorOutcome.REFUSED
        assert mapping.code_for(context).value in run.codes
    else:
        assert run.outcome is GeneratorOutcome.GENERATED


def test_each_rule_example_is_a_case_the_generator_generates():
    for rule in PACKAGED_RULES.rules:
        if rule.example_case is not None:
            run = ANSWERS[rule.example_case].generator.run
            assert run.outcome is GeneratorOutcome.GENERATED, rule.rule_id


def test_corpus_citations_can_name_only_fixtures_the_batch_captured():
    """A `corpus:` citation is admissible only for a fixture whose graph the batch sealed."""
    batch = json.loads((FIXTURES_DIR / "v6_recapture_batch" / "batch.json").read_text())
    assert set(SNAPSHOT_FIXTURES) == set(batch["captured"])


@pytest.mark.parametrize("answer", list(ANSWERS.values()), ids=lambda a: a.case_id)
def test_screen_refusals_sit_on_the_construct(answer: StoredAnswer):
    construct = cases.construct_of(answer)
    outside = [
        f
        for f in cases.screen_of(answer).findings
        if f.outcome is Outcome.REFUSED and (f.line is None or not construct.contains(f.line))
    ]
    assert outside == []
