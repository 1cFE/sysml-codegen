"""Neutralizing a refusal site changes exactly the stored cases (Item 2a D5, § B, B5).

For each mutated site, the site is neutralized (``mutate.neutralize``) and every case that
fires it in the generator half is run again. The cases whose outcome or site reasons change
must be the stored set in ``mutations.json``, which holds at least one of the site's
witnesses (``test_mutation_record.py``). A case that never runs the site's statement cannot
change, so only the firing cases are run.

Sites in ``mutate.SHARED`` are agentic-mbse sites the generator runs. An ``unwitnessed`` site
must fire in no case, so a new case that reaches one fails here until the record moves it.

Licensed.
"""

from __future__ import annotations

import pytest

from tests.conftest import requires_license
from tests.helpers.subset_profile import cases, mutate, witnesses

pytestmark = requires_license

RECORD = witnesses.read_mutations()


@pytest.mark.parametrize("site_id", sorted(RECORD.generator), ids=str)
def test_neutralizing_a_site_changes_exactly_the_stored_cases(site_id):
    fired = witnesses.fired_in_generator(site_id)
    with mutate.neutralize(site_id):
        changed = {c for c in fired if witnesses.answer_changed(cases.load_answer(c))}
    assert changed == RECORD.generator[site_id]


@pytest.mark.parametrize("site_id", sorted(RECORD.unwitnessed), ids=str)
def test_an_unwitnessed_site_fires_in_no_case(site_id):
    assert witnesses.fired_in_generator(site_id) == ()
