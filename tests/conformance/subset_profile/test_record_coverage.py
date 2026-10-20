"""Every record outcome rests on a case that shows it on the generator's side.

Item 2a design § B (record coverage) and spec criteria B2, B3, B7 and B8:

- a `refused` pair cites a case the generator refuses;
- a refused shape has a case in a context it is not refused in, or an SA-1 statement;
- an `omitted` or `excluded` pair cites a case whose stored answer asserts at a seam (design
  D9), so the omission is observed in the generator's output rather than by text search;
- every pair r3-proposal § 3 routes to Item 2 is decided or recorded `unobservable`, and an
  `unobservable` pair cites a case with a stored generator answer.

Pure: reads the packaged records and the stored generator answers. The seams themselves are
checked live in ``test_generator_half.py``.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from agentic_mbse.sysml.subset_profile import (
    PACKAGED_RULES,
    CaseRef,
    ContextId,
    Outcome,
    ShapeRecord,
)

from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.cases import GeneratorOutcome

ANSWERS = {a.case_id: a for a in cases.all_answers()}

#: The `unconfirmed` pairs r3-proposal § 3 routes to Item 2 (spec Known Requirements, R3 rows).
R3_UNCONFIRMED = sorted(
    [
        ("binding-source", "expression_source", ContextId.OWNER_OTHER),
        ("binding-source", "self_reference_source", ContextId.OWNER_OTHER),
        ("binding-source", "self_reference_source", ContextId.WRITER_OVERRIDDEN),
        *(
            ("conditional-expression", "conditional_resolved_branches", context)
            for context in (
                ContextId.ATTRIBUTE_VALUE,
                ContextId.BINDING_VALUE,
                ContextId.CALC_DEFINITION_FEATURE_VALUE,
                ContextId.CALC_RESULT_EXPRESSION,
                ContextId.CONSTRAINT_PREDICATE,
                ContextId.OTHER_EXPRESSION_SITE,
            )
        ),
        (
            "conditional-expression",
            "conditional_unresolved_branch",
            ContextId.CALC_RESULT_EXPRESSION,
        ),
        ("indexed-reference", "indexed_reference", ContextId.CALC_RESULT_EXPRESSION),
        ("invocation-callable", "unsupported_callable", ContextId.CALC_RESULT_EXPRESSION),
        ("constraint-predicate", "blocked_predicate", ContextId.OWNER_OTHER),
        ("constraint-predicate", "non_numerical_predicate", ContextId.OWNER_OTHER),
        ("constraint-predicate", "non_numerical_predicate", ContextId.OWNER_PACKAGE),
        ("constraint-predicate", "non_numerical_predicate", ContextId.OWNER_UNINSTANTIATED),
    ],
    key=lambda p: (p[0], p[1], p[2].value),
)


def _shapes() -> Iterator[tuple[str, ShapeRecord]]:
    for rule in PACKAGED_RULES.rules:
        for shape in rule.shapes:
            yield rule.rule_id, shape


def _pairs(*outcomes: Outcome) -> list[tuple[str, str, ContextId, tuple[str, ...]]]:
    return [
        (
            rule_id,
            shape.shape_id,
            context,
            tuple(e.case_id for e in admission.evidence if isinstance(e, CaseRef)),
        )
        for rule_id, shape in _shapes()
        for context, admission in shape.admissions.items()
        if admission.outcome in outcomes
    ]


def _pair_id(pair: tuple[object, ...]) -> str:
    rule_id, shape_id, context = pair[:3]
    assert isinstance(context, ContextId)
    return f"{rule_id}/{shape_id}/{context.value}"


@pytest.mark.parametrize("pair", _pairs(Outcome.REFUSED), ids=_pair_id)
def test_a_refused_pair_cites_a_case_the_generator_refuses(pair):
    *_, case_ids = pair
    refusing = [c for c in case_ids if ANSWERS[c].generator.run.outcome is GeneratorOutcome.REFUSED]
    assert refusing, f"{_pair_id(pair)} cites no case the generator refuses"


REFUSED_SHAPES = [(r, s) for r, s in _shapes() if s.contexts_with(Outcome.REFUSED)]


@pytest.mark.parametrize(
    ("rule_id", "shape"), REFUSED_SHAPES, ids=lambda v: v if isinstance(v, str) else v.shape_id
)
def test_a_refused_shape_has_a_case_where_it_is_not_refused_or_an_sa1_statement(rule_id, shape):
    not_refused = [
        e.case_id
        for a in shape.admissions.values()
        if a.outcome is not Outcome.REFUSED
        for e in a.evidence
        if isinstance(e, CaseRef)
    ]
    assert not_refused or shape.no_admitted_context is not None, (rule_id, shape.shape_id)
    for case_id in not_refused:
        assert ANSWERS[case_id].generator.run.outcome is GeneratorOutcome.GENERATED, case_id


@pytest.mark.parametrize("pair", _pairs(Outcome.OMITTED, Outcome.EXCLUDED), ids=_pair_id)
def test_an_omitted_or_excluded_pair_cites_a_case_that_asserts_at_a_seam(pair):
    *_, case_ids = pair
    asserting = [c for c in case_ids if ANSWERS[c].generator.seams]
    assert asserting, f"{_pair_id(pair)} cites no case with a seam"


@pytest.mark.parametrize("pair", R3_UNCONFIRMED, ids=_pair_id)
def test_each_r3_unconfirmed_pair_is_decided_or_recorded_unobservable(pair):
    rule_id, shape_id, context = pair
    shape = PACKAGED_RULES.rule(rule_id).shape(shape_id)
    decided = context in shape.admissions
    unobservable = shape.unobservable.get(context)
    assert decided != (unobservable is not None), _pair_id(pair)
    if unobservable is not None:
        for ref in unobservable.evidence:
            assert ref.case_id in ANSWERS, f"{ref.case_id} has no stored generator answer"
