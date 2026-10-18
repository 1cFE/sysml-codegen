"""The stored mutation record covers exactly the planned mutations (Item 2a § B, plan P2.4).

Pure: reads ``mutations.json``, the account, the records and the stored answers. Whether each
stored set is what a live mutation does is ``test_generator_mutations.py`` and
``test_screen_mutations.py``.
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.subset_profile import PACKAGED_RULES, Outcome

from tests.helpers.subset_profile import cases, witnesses
from tests.helpers.subset_profile.cases import GeneratorOutcome

RECORD = witnesses.read_mutations()


def test_every_mutated_site_is_recorded_once():
    assert not RECORD.generator.keys() & RECORD.unwitnessed.keys()
    assert sorted(RECORD.generator.keys() | RECORD.unwitnessed.keys()) == sorted(
        witnesses.mutated_sites()
    )


@pytest.mark.parametrize("site_id", sorted(RECORD.generator), ids=str)
def test_a_generator_mutation_changes_a_witness(site_id):
    assert RECORD.generator[site_id] & witnesses.witnesses_of(site_id), site_id


@pytest.mark.parametrize(
    "site_id", sorted(s for s in RECORD.unwitnessed if s.startswith("sysml_codegen/")), ids=str
)
def test_an_unwitnessed_codegen_site_has_no_witness(site_id):
    assert witnesses.witnesses_of(site_id) == frozenset()


def _refused_shapes() -> set[tuple[str, str]]:
    return {
        (rule.rule_id, shape.shape_id)
        for rule in PACKAGED_RULES.rules
        for shape in rule.shapes
        if shape.contexts_with(Outcome.REFUSED)
    }


def test_every_shape_with_a_refused_context_has_a_screen_mutation():
    assert set(RECORD.screen) == _refused_shapes()


@pytest.mark.parametrize("rule_shape", sorted(RECORD.screen), ids="/".join)
def test_a_screen_mutation_breaks_only_refusing_cases_the_screen_refuses_for_it(rule_shape):
    rule, shape = rule_shape
    for case_id in RECORD.screen[rule_shape]:
        answer = cases.load_answer(case_id)
        assert answer.generator.run.outcome is GeneratorOutcome.REFUSED, case_id
        assert any(
            (f.rule, f.shape, f.outcome) == (rule, shape, Outcome.REFUSED)
            for f in cases.screen_of(answer).findings
        ), case_id
