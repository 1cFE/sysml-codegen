"""Every case's live generator half equals its stored answer, and refuses only on its construct.

Item 2a design D1 and § C. Each case's model runs through ``run_codegen`` with the screen
tripwired (``observe.generator_half``). Its outcome, codes and site reasons must equal the
stored answer, and every refusal the run locates must sit on the case's construct, so a case
that refuses for an unrelated reason shows up as a broken case rather than as evidence.

A case may also assert seams (design D9): a fact about one declaration at a named point of
the output, such as "no attribute node" for a dropped String value. Each must hold live. And
every calc def member the run compiles to a ``MANUAL_REQUIRED`` stub must be stored with the
cause its ``ManualStubNotice`` names, so a stub can neither appear nor change cause unseen.

Two kinds of refusal carry no location in the payload, so isolation cannot check them:
generation-stage codes, which name no source, and ``SI_CONSTRAINT_BLOCKED``, whose location
the executable profile writes only into the message text (``_render_block_reason`` in
``elaboration/elaborate.py``), which the harness does not parse (design D2).

Item 2a P3 added two more, both found on the cases where the generator refuses with a code no
screen finding maps to. ``SI_ID_UNSTABLE`` is raised from ``elaboration/identity.py:45`` with a
message and no source, and the ``SI_EDGE_DANGLING`` raises those cases reach (a
dangling definition UUID or feature, a producer cycle) name a subject but pass no source.
A located refusal with either code is still held to the construct.

Item 2a P5 added two more. ``SI_ID_MISSING``: an anonymous calc def is refused at calc payload
indexing (``_index_calculation_payloads`` in ``elaboration/elaborate.py``), which passes no
source. ``SI_SNAPSHOT_INVALID``: projection's computed-expression renderer refuses a ``sum`` with
no argument (``elaboration/project.py``) naming the attribute's display path, not a source.

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
from tests.helpers.subset_profile.cases import SeamAnswer, StoredAnswer

pytestmark = requires_license

ANSWERS = cases.all_answers()
SEAMS = [(a, seam) for a in ANSWERS for seam in a.generator.seams]
UNLOCATED_CODES = frozenset(
    {
        ElaborationCode.SI_CONSTRAINT_BLOCKED.value,
        ElaborationCode.SI_EDGE_DANGLING.value,
        ElaborationCode.SI_ID_UNSTABLE.value,
        ElaborationCode.SI_ID_MISSING.value,
        ElaborationCode.SI_SNAPSHOT_INVALID.value,
    }
    | {code.value for code in GenerationCode}
)
_ROOT_SLOT = re.compile(r"root-\d+/")


@cache
def _observe(case_id: str) -> observe.GeneratorObservation:
    return observe.generator_half(cases.model_root(cases.load_answer(case_id)))


@pytest.mark.parametrize("answer", ANSWERS, ids=lambda a: a.case_id)
def test_live_run_equals_the_stored_answer(answer: StoredAnswer):
    assert _observe(answer.case_id).run() == answer.generator.run


@pytest.mark.parametrize("answer", ANSWERS, ids=lambda a: a.case_id)
def test_live_stubs_equal_the_stored_stubs(answer: StoredAnswer):
    """Every calc def member the run stubs, with its cause, is stored; none other is (D9)."""
    assert _observe(answer.case_id).stubs() == answer.generator.stubs


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


@pytest.mark.parametrize(
    ("answer", "seam"), SEAMS, ids=lambda v: v.case_id if isinstance(v, StoredAnswer) else v.kind
)
def test_every_seam_holds(answer: StoredAnswer, seam: SeamAnswer):
    declaration = observe.declaration_in(cases.model_root(answer), seam.declaration)
    assert observe.seam_value(_observe(answer.case_id), seam.kind, declaration) == seam.expect
