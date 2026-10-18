"""The generator's route never runs the screen (Item 2a design § B, spec criterion B1).

Every case's generator half runs with ``extract_subset_facts``, ``evaluate_subset_profile``
and ``extract_occurrence_structure`` rebound to raise wherever a module binds them
(``observe.screen_tripwire``), and must still end as its stored answer says. Item 2b, which
adopts the screen inside ``generate``, inherits this test: from then on the generator half
of a case is the route with the screen bypassed, and this is what keeps it so.

The first two tests show the tripwire itself works: a call through the defining module or a
by-name import raises at the call and fails the observation afterwards, even when the caller
swallows the raise, and the original functions come back after the run.

Licensed.
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml import occurrence_extraction, subset_extraction, subset_profile
from agentic_mbse.sysml.subset_extraction import extract_subset_facts

from tests.conftest import requires_license
from tests.helpers.subset_profile import cases, observe
from tests.helpers.subset_profile.cases import StoredAnswer
from tests.helpers.subset_profile.observe import ScreenCalledError

pytestmark = requires_license

ENTRY_POINTS = (
    (subset_extraction, "extract_subset_facts"),
    (subset_profile, "evaluate_subset_profile"),
    (occurrence_extraction, "extract_occurrence_structure"),
)


@pytest.mark.parametrize(("module", "name"), ENTRY_POINTS, ids=lambda v: getattr(v, "__name__", v))
def test_a_swallowed_screen_call_still_fails_the_observation(module, name):
    original = getattr(module, name)
    with pytest.raises(ScreenCalledError, match="called the screen"):
        with observe.screen_tripwire():
            try:
                getattr(module, name)(None)
            except ScreenCalledError:
                pass  # the route's own error handling would turn this into a refusal
    assert getattr(module, name) is original


def test_a_by_name_import_is_rebound_too():
    original = extract_subset_facts
    with pytest.raises(ScreenCalledError, match="called the screen"):
        with observe.screen_tripwire():
            with pytest.raises(ScreenCalledError):
                globals()["extract_subset_facts"](None)
    assert globals()["extract_subset_facts"] is original


@pytest.mark.parametrize("answer", cases.all_answers(), ids=lambda a: a.case_id)
def test_every_case_ends_as_stored_with_the_screen_tripwired(answer: StoredAnswer):
    observation = observe.generator_half(cases.model_root(answer))
    assert observation.run().outcome is answer.generator.run.outcome
