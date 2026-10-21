"""A site's recorded role and reason agree with what the corpus reaches (Item 2a E3, E4).

The account states reachability from inspection (its header's blind spots). These tests hold
that statement to the cases, so a reached site cannot be recorded as reached by no model, the
mistake the final audit found at two sites (``audit.md``, final, Blocker 1):

- no case fires a site whose role says no case reaches it (``witnesses.UNREACHED_ROLES``).
  Licensed: the tracer sees which sites each case's generator half runs;
- every case the generator refuses carries a site reason. A refusal's reason is set where it
  starts, so a refused case with none is a reached refusing site with no reason (E3), and a
  ``reproduced_gap`` needs a stable codegen reason (spec § R3 rows). Pure: over the stored
  answers, which ``test_generator_half.py`` holds to live runs.

Limit: only cases are traced. A fixture under ``tests/fixtures/`` that reaches a site is not
seen here unless a case reaches the same site.
"""

from __future__ import annotations

import pytest

from tests.conftest import requires_license
from tests.helpers.refusal_cases import cases, witnesses
from tests.helpers.refusal_cases.cases import GeneratorOutcome

REFUSED = sorted(
    (a for a in cases.all_answers() if a.generator.run.outcome is GeneratorOutcome.REFUSED),
    key=lambda a: a.case_id,
)


@requires_license
@pytest.mark.parametrize("site_id", witnesses.recorded_unreached_sites(), ids=str)
def test_no_case_reaches_a_site_recorded_unreached(site_id):
    assert witnesses.fired_in_generator(site_id) == ()


@pytest.mark.parametrize("answer", REFUSED, ids=lambda a: a.case_id)
def test_every_refused_case_carries_a_site_reason(answer):
    assert answer.generator.run.reasons != ()
