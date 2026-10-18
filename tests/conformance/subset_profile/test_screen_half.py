"""Every case's live screen answer equals its stored screen answer.

Item 2a design D13 says the pre-merge run of this suite is what checks an agentic-mbse
extractor or evaluator change against the generator. Agreement (``test_agreement.py``) judges
the stored screen answer against the stored generator answer, and both are files, so a screen
change reaches neither. This test is the link: the screen run live on every case, in either
home, must give the answer agreement was judged on. agentic-mbse's rule tests replay its
packaged cases the same way, but only inside agentic-mbse's suite; this one runs in codegen's.

Licensed.
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.conformance_case import screen_answer

from tests.conftest import requires_license
from tests.helpers.subset_profile import cases, observe
from tests.helpers.subset_profile.cases import StoredAnswer

pytestmark = requires_license


@pytest.mark.parametrize("answer", cases.all_answers(), ids=lambda a: a.case_id)
def test_live_screen_equals_the_stored_screen_answer(answer: StoredAnswer):
    live = screen_answer(observe.screen_half(cases.model_root(answer)))
    assert live == cases.screen_of(answer)
