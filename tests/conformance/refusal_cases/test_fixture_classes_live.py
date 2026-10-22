"""Every fixture's stored class holds live (Item 2a spec B5, second half).

For each model root under ``tests/fixtures/`` (``fixture_classes.model_roots``) the generator
half runs and must give the stored class: generating, or refusing with the stored codes. This
is what confirms the one reviewed run each class was written from.

A root SysIDE cannot load is refused at parsing, with no code; its stored class says why.

Licensed.
"""

from __future__ import annotations

from functools import cache

import pytest

from sysml_codegen.cli.refusal import RefusalKind
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.refusal_cases import observe
from tests.helpers.refusal_cases.cases import GeneratorOutcome
from tests.helpers.refusal_cases.fixture_classes import FixtureClass, model_roots

pytestmark = requires_license

ROOTS = model_roots()


@cache
def _generator(key: str) -> observe.GeneratorObservation:
    return observe.generator_half(FIXTURES_DIR / key)


@pytest.mark.parametrize("key", sorted(ROOTS), ids=str)
def test_the_stored_class_holds_live(key: str):
    stored, observation = ROOTS[key], _generator(key)
    if stored.fixture_class is FixtureClass.REFUSING and not stored.codes:
        assert observation.refusal is not None
        assert observation.refusal.kind is RefusalKind.PARSING
        return
    run = observation.run()
    if stored.fixture_class is FixtureClass.GENERATING:
        assert run.outcome is GeneratorOutcome.GENERATED, run
    else:
        assert (run.outcome, run.codes) == (GeneratorOutcome.REFUSED, stored.codes)
