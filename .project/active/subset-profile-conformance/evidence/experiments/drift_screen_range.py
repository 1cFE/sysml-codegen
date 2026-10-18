"""pytest plugin: part-multiplicity stops recognizing `range` for the whole session.

Simulates a screen regression (audit-p12 Blocker 1). Run from the codegen worktree root:
    PYTHONPATH=.project/active/subset-profile-conformance/evidence/experiments \
    uv run --extra dev pytest -p drift_screen_range tests/conformance/subset_profile/ -q
"""

import pytest


@pytest.fixture(autouse=True, scope="session")
def _drift():
    from tests.helpers.subset_profile import mutate

    with mutate.disable_recognizer("part-multiplicity", "range"):
        yield
