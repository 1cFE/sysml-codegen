"""Every known silent-loss family is pinned at a seam beside a control (Item 2a design D9, § D).

A case's ``loss`` block names the family, today's disposition and a control case. The control
is the supported form of the same construct: it carries no loss block and asserts at the same
seam kinds, so the two stored answers can be read side by side. A stub family's loss is the
stub itself, so its cases carry stubs and its control carries none.

Pure: reads the stored answers. Whether each seam and stub holds live is
``test_generator_half.py`` (``test_every_seam_holds``, ``test_live_stubs_equal_the_stored_stubs``).
"""

from __future__ import annotations

import pytest

from tests.helpers.refusal_cases import cases
from tests.helpers.refusal_cases.cases import StoredAnswer

#: The families design § D names, by the ``family`` id their cases use, less the ones since
#: closed. ``g1-redefinition-drops-bounds`` closed with named-subset-members (2026-10-26): a
#: redefinition that states no multiplicity now inherits it, with its ordering.
SPEC_FAMILIES = {
    "es-010-string",
    "calc-usage-bare-result-drop",
    "es-007-non-numerical",
    "g2-usage-override-of-referenced-bound",
    "calc-def-output-stub",
}
STUB_FAMILY = "calc-def-output-stub"

LOSSES = [a for a in cases.all_answers() if a.loss is not None]


def _seam_kinds(answer: StoredAnswer) -> set[cases.SeamKind]:
    return {seam.kind for seam in answer.generator.seams}


def test_every_family_has_a_loss_case_and_no_other_family_appears():
    assert {a.loss.family for a in LOSSES if a.loss is not None} == SPEC_FAMILIES


@pytest.mark.parametrize("answer", LOSSES, ids=lambda a: a.case_id)
def test_a_loss_asserts_at_a_seam_its_control_shares(answer: StoredAnswer):
    assert answer.loss is not None
    control = cases.load_answer(answer.loss.control)
    assert control.loss is None
    assert answer.generator.seams, answer.case_id
    assert _seam_kinds(control) == _seam_kinds(answer)


@pytest.mark.parametrize(
    "answer",
    [a for a in LOSSES if a.loss is not None and a.loss.family == STUB_FAMILY],
    ids=lambda a: a.case_id,
)
def test_a_stub_loss_shows_stubs_and_its_control_none(answer: StoredAnswer):
    assert answer.loss is not None
    assert answer.generator.stubs
    assert cases.load_answer(answer.loss.control).generator.stubs == ()
