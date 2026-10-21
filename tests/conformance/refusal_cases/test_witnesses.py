"""Every witness fires its site in the generator half (Item 2a D7, plan PD5).

The firing is seen by ``mutate.recording_fired``: line events on the site's own statement, in
the function that owns it.

Licensed.
"""

from __future__ import annotations

import pytest

from tests.conftest import requires_license
from tests.helpers.refusal_cases import cases, witnesses

pytestmark = requires_license

WITNESSED = sorted(a.case_id for a in cases.all_answers() if a.generator.witnesses)


@pytest.mark.parametrize("case_id", WITNESSED, ids=str)
def test_a_witness_fires_its_sites_in_the_generator_half(case_id):
    named = set(cases.load_answer(case_id).generator.witnesses)
    assert named - witnesses.generator_firing()[case_id] == set()
