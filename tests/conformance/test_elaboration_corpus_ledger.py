"""Mechanical completeness checks for the 37-fixture dual-run ledger."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

from tests.conftest import requires_license
from tests.helpers.corpus import corpus_fixture_names

ROOT = Path(__file__).parents[2]
LEDGER = ROOT / ".project/completed/20260809_elaborator-breadth/diff-ledger.md"
RUNNER = ROOT / "scripts/run_elaboration_corpus.py"

pytestmark = requires_license


def _runner():
    spec = importlib.util.spec_from_file_location("run_elaboration_corpus", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def test_corpus_runner_discovers_the_same_closed_fixture_set() -> None:
    expected = corpus_fixture_names()
    assert _runner().discover_fixture_names() == expected


def test_dual_run_ledger_outcomes_match_a_live_corpus_run() -> None:
    runner = _runner()
    result = runner.run(runner.discover_fixture_names())
    assert runner.result_outcomes(result) == runner.read_ledger_outcomes(LEDGER)
