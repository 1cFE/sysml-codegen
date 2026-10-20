"""Every fixture's class holds live, and the live screen agrees with it or is recorded.

Item 2a spec B5 (second half), C2 and C3, design § C. For each model root under
``tests/fixtures/`` (``fixture_classes.model_roots``):

1. The generator half runs and must give the stored class: generating, or refusing with the
   stored codes. This is what confirms the one reviewed run each class was written from.
2. The screen runs live and is judged against that run by the agreement rule. A disagreement
   passes only if the hand-edited record lists it. So a generating fixture the screen refuses,
   and a refusing fixture whose refusal no screen finding maps to, each fail unless recorded.

A root SysIDE cannot load is refused at parsing, with no code. Neither half has an answer to
compare, so such a root is checked to be one (a parsing refusal, and a load that reports
errors to the screen too) and is not a subject of agreement. Its stored class says why.

A codegen-home conformance case is a model root here too, so its class is held live, but it is
a ``case:`` subject of ``test_agreement.py``, not a ``fixture:`` subject, so one model is never
recorded twice.

Then the record's fixture entries must be exactly the computed ones.

Licensed.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

import pytest
from agentic_mbse.sysml.conformance_case import ScreenAnswer, screen_answer
from agentic_mbse.sysml.subset_extraction import extract_subset_facts
from agentic_mbse.sysml.subset_profile import evaluate_subset_profile
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.cli.refusal import RefusalKind
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.subset_profile import cases, observe
from tests.helpers.subset_profile.cases import Disagreement, GeneratorOutcome
from tests.helpers.subset_profile.fixture_classes import FixtureClass, StoredClass, model_roots

pytestmark = requires_license

ROOTS = model_roots()
RECORD = cases.read_disagreements()


def _parse_refused(stored: StoredClass) -> bool:
    return stored.fixture_class is FixtureClass.REFUSING and not stored.codes


@cache
def _generator(key: str) -> observe.GeneratorObservation:
    return observe.generator_half(FIXTURES_DIR / key)


@cache
def _screen(key: str) -> ScreenAnswer | None:
    """The live screen answer, or ``None`` when SysIDE reports errors loading the root."""
    model, diagnostics = SysideAdapter.load_model([FIXTURES_DIR / key])
    if diagnostics.contains_errors():
        return None
    return screen_answer(evaluate_subset_profile(extract_subset_facts(model)))


def _disagreement(key: str) -> Disagreement | None:
    screen = _screen(key)
    assert screen is not None, f"{key}: SysIDE reports errors, but the generator parsed it"
    return cases.disagreement(f"fixture:{key}", _generator(key).run(), screen)


@pytest.mark.parametrize("key", sorted(ROOTS), ids=str)
def test_the_stored_class_holds_live(key: str):
    stored, observation = ROOTS[key], _generator(key)
    if _parse_refused(stored):
        assert observation.refusal is not None
        assert observation.refusal.kind is RefusalKind.PARSING
        assert _screen(key) is None
        return
    run = observation.run()
    if stored.fixture_class is FixtureClass.GENERATING:
        assert run.outcome is GeneratorOutcome.GENERATED, run
    else:
        assert (run.outcome, run.codes) == (GeneratorOutcome.REFUSED, stored.codes)


CASE_ROOT = cases.CODEGEN_CASES_DIR.relative_to(FIXTURES_DIR)
SUBJECTS = sorted(
    k for k, v in ROOTS.items() if not _parse_refused(v) and Path(k).parent != CASE_ROOT
)


@pytest.mark.parametrize("key", SUBJECTS, ids=str)
def test_the_live_screen_agrees_or_the_disagreement_is_recorded(key: str):
    found = _disagreement(key)
    assert found is None or cases.recorded(found, RECORD), found


def test_the_records_fixture_entries_are_exactly_the_computed_disagreements():
    computed = {d for k in SUBJECTS if (d := _disagreement(k)) is not None}
    recorded = {e.disagreement for e in RECORD if e.disagreement.subject.startswith("fixture:")}
    assert recorded - computed == set(), "recorded, but the fixture now agrees or is gone"
    assert computed - recorded == set(), "disagrees, but the record does not list it"
