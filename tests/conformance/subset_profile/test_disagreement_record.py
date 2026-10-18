"""The disagreement record is edited by hand only, and capture cannot make a disagreement pass.

Item 2a design D3 and invariant 2. Three guards:

- no Python file under ``src/``, ``tests/`` or ``scripts/`` names the record's file except its
  reader (``tests/helpers/subset_profile/cases.py``) and this test;
- the reader makes no call that writes;
- the capture helper refuses a run that disagrees with the case's screen answer unless the
  record already lists that disagreement, and writes nothing when it refuses.

Limit: a path assembled from pieces evades the text search; the phase audit is the backstop.
Equality between the computed disagreements and the record over every subject is P3's test.

Pure: the capture guard runs on a replaced observation, not on the generator.
"""

from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.conftest import REPO_ROOT
from tests.helpers.subset_profile import capture, cases
from tests.helpers.subset_profile.cases import GeneratorOutcome, GeneratorRun

RECORD_NAME = "disagreements.json"
READER = REPO_ROOT / "tests" / "helpers" / "subset_profile" / "cases.py"
ALLOWED = {READER, Path(__file__).resolve()}
_WRITING_CALLS = {
    "write_text",
    "write_bytes",
    "dump",
    "open",
    "touch",
    "unlink",
    "rename",
    "replace",
}


def test_the_record_loads():
    assert cases.DISAGREEMENTS_PATH.name == RECORD_NAME
    assert cases.read_disagreements()


def test_only_the_reader_and_this_test_name_the_record():
    naming = [
        str(path.relative_to(REPO_ROOT))
        for root in ("src", "tests", "scripts")
        for path in sorted((REPO_ROOT / root).rglob("*.py"))
        if path.resolve() not in ALLOWED and RECORD_NAME in path.read_text(encoding="utf-8")
    ]
    assert naming == []


def test_the_reader_makes_no_writing_call():
    calls = [
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(ast.parse(READER.read_text(encoding="utf-8")))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute | ast.Name)
    ]
    assert sorted(set(calls) & _WRITING_CALLS) == []


CASE_ID = "candidate-es-002__constraint_binds_calc_input__binding_value"


def _observed(run: GeneratorRun) -> SimpleNamespace:
    return SimpleNamespace(run=lambda: run)


def _answers_in(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    answers = tmp_path / "cases"
    answers.mkdir()
    stored = cases.ANSWERS_DIR / f"{CASE_ID}.json"
    (answers / stored.name).write_bytes(stored.read_bytes())
    monkeypatch.setattr(cases, "ANSWERS_DIR", answers)
    return answers / stored.name


def test_capture_refuses_an_unrecorded_disagreement_and_writes_nothing(tmp_path, monkeypatch):
    path = _answers_in(tmp_path, monkeypatch)
    before = path.read_bytes()
    unrecorded = GeneratorRun(GeneratorOutcome.REFUSED, ("SI_REDEFINITION_INVALID",), ())
    monkeypatch.setattr(capture.observe, "generator_half", lambda _root: _observed(unrecorded))
    with pytest.raises(capture.CaptureRefusedError, match="does not list it"):
        capture.capture(CASE_ID)
    assert path.read_bytes() == before


def test_capture_writes_a_recorded_disagreement(tmp_path, monkeypatch):
    path = _answers_in(tmp_path, monkeypatch)
    recorded = cases.load_stored_answer(path).generator.run
    monkeypatch.setattr(capture.observe, "generator_half", lambda _root: _observed(recorded))
    assert capture.capture(CASE_ID) == f"{CASE_ID}: unchanged"
