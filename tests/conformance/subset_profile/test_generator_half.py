"""Every case's live generator half equals its stored answer, and refuses only on its construct.

Item 2a design D1 and § C. Each case's model runs through ``run_codegen`` with the screen
tripwired (``observe.generator_half``). Its outcome, codes and site reasons must equal the
stored answer, and every refusal the run locates must sit on the case's construct, so a case
that refuses for an unrelated reason shows up as a broken case rather than as evidence.

Two kinds of refusal carry no location in the payload, so isolation cannot check them:
generation-stage codes, which name no source, and ``SI_CONSTRAINT_BLOCKED``, whose location
the executable profile writes only into the message text (``_render_block_reason`` in
``elaboration/elaborate.py``), which the harness does not parse (design D2).

Licensed.
"""

from __future__ import annotations

import re
from functools import cache

import pytest

from sysml_codegen.core.errors import GenerationCode
from sysml_codegen.elaboration.diagnostics import ElaborationCode
from tests.conftest import requires_license
from tests.helpers.subset_profile import cases, observe
from tests.helpers.subset_profile.cases import StoredAnswer

pytestmark = requires_license

ANSWERS = cases.all_answers()
UNLOCATED_CODES = frozenset(
    {ElaborationCode.SI_CONSTRAINT_BLOCKED.value} | {code.value for code in GenerationCode}
)
_ROOT_SLOT = re.compile(r"root-\d+/")


@cache
def _observe(case_id: str) -> observe.GeneratorObservation:
    return observe.generator_half(cases.model_root(cases.load_answer(case_id)))


@pytest.mark.parametrize("answer", ANSWERS, ids=lambda a: a.case_id)
def test_live_run_equals_the_stored_answer(answer: StoredAnswer):
    assert _observe(answer.case_id).run() == answer.generator.run


@pytest.mark.parametrize("answer", ANSWERS, ids=lambda a: a.case_id)
def test_every_located_refusal_sits_on_the_construct(answer: StoredAnswer):
    construct = cases.construct_of(answer)
    stray = []
    for item in _observe(answer.case_id).refusals:
        if item.source_file is None or item.source_line is None:
            assert item.code.value in UNLOCATED_CODES, f"{item.code} carries no location"
            continue
        file = _ROOT_SLOT.sub("", item.source_file, count=1)
        if file != construct.file or not construct.contains(item.source_line):
            stray.append(item)
    assert stray == []
