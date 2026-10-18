"""Every witness fires its site, in the half that runs the site (Item 2a D7, plan PD5).

A codegen witness fires in the generator half; an agentic-mbse witness in the screen half,
where every linked agentic-mbse site runs. The firing is seen by ``mutate.recording_fired``:
line events on the site's own statement, in the function that owns it.

Licensed.
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.conformance_case import load_packaged_case

from tests.conftest import requires_license
from tests.helpers.subset_profile import cases, mutate, observe, witnesses

pytestmark = requires_license

WITNESSED = sorted(a.case_id for a in cases.all_answers() if a.generator.witnesses)
PACKAGED_WITNESSED = sorted(
    c for c in cases.packaged_ids() if load_packaged_case(c).agentic_site_witnesses
)


@pytest.mark.parametrize("case_id", WITNESSED, ids=str)
def test_a_codegen_witness_fires_its_sites_in_the_generator_half(case_id):
    named = set(cases.load_answer(case_id).generator.witnesses)
    assert named - witnesses.generator_firing()[case_id] == set()


@pytest.mark.parametrize("case_id", PACKAGED_WITNESSED, ids=str)
def test_an_agentic_witness_fires_its_sites_in_the_screen_half(case_id):
    named = load_packaged_case(case_id).agentic_site_witnesses
    with mutate.recording_sites(named) as fired:
        observe.screen_half(cases.model_root(cases.load_answer(case_id)))
    assert set(named) - fired == set()
