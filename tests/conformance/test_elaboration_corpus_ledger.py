"""Mechanical completeness check for the 37-fixture dual-run ledger.

The two nodes that re-ran the corpus and compared the result to the ledger drove
``scripts/run_elaboration_corpus.py``, whose whole subject is the legacy-versus-exact dual
run. That script retired with the v5 family (retirement step 2, ledger L-044). The exact
route's half of the measurement did not move: ``scripts/capture_v6_batch.py --verify``
produces it and ``tests/conformance/test_v6_recapture_batch.py`` pins it, both already in
every battery. What is left here is the ledger's own completeness — that it classifies all
37 fixtures and no others.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.helpers.corpus import corpus_fixture_names

ROOT = Path(__file__).parents[2]
LEDGER = ROOT / ".project/completed/20260809_elaborator-breadth/diff-ledger.md"


def test_dual_run_ledger_classifies_all_snapshot_fixtures() -> None:
    expected = set(corpus_fixture_names())
    text = LEDGER.read_text()
    rows = re.findall(
        r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|.*\|\s*"
        r"(expected-collapse|expected-fix|needs-review|new-bug)\s*\|",
        text,
        re.MULTILINE,
    )

    assert len(expected) == 37
    assert len(rows) == 37
    assert {fixture for fixture, _classification in rows} == expected
