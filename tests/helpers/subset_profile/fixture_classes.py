"""The class of every directory under ``tests/fixtures/``, each from one source (Item 2a § B).

A directory is a model root (``generating`` or ``refusing``), lies inside one, or is a
``container`` whose children are classed in turn. A directory that holds no model is
``not_a_model``, and so is everything under it. Classes come from exactly one place each:

- the 37 corpus fixtures: ``tests/fixtures/v6_recapture_batch/batch.json`` (``refused`` lists
  the refusing ones; their codes are the public package oracle's);
- codegen-home conformance cases: their stored generator answer;
- every other directory: ``tests/expectations/subset_profile/fixture_classes.json``, written
  from one reviewed generator-half run per root and confirmed live by P3's fixture test.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from tests.conftest import FIXTURES_DIR
from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.cases import CaseHome, GeneratorOutcome

FIXTURE_CLASSES_PATH = cases.EXPECTATIONS_DIR / "fixture_classes.json"
BATCH_PATH = FIXTURES_DIR / "v6_recapture_batch" / "batch.json"
SCHEMA = "subset-fixture-classes/1"


class FixtureClassError(ValueError):
    """The stored fixture classes are malformed."""


class FixtureClass(StrEnum):
    GENERATING = "generating"
    REFUSING = "refusing"
    CONTAINER = "container"
    NOT_A_MODEL = "not_a_model"


MODEL_CLASSES = frozenset({FixtureClass.GENERATING, FixtureClass.REFUSING})


@dataclass(frozen=True)
class StoredClass:
    fixture_class: FixtureClass
    #: The sorted multiset of a refusing root's codes; empty for every other class.
    codes: tuple[str, ...]
    note: str | None


def _stored_class(value: Any, where: str) -> StoredClass:
    if not isinstance(value, dict) or not {"class"} <= value.keys() <= {"class", "codes", "note"}:
        raise FixtureClassError(f"{where}: expected class, and optionally codes and note")
    try:
        fixture_class = FixtureClass(value["class"])
    except ValueError as error:
        raise FixtureClassError(f"{where}: {value['class']!r} is not a FixtureClass") from error
    codes = value.get("codes", [])
    note = value.get("note")
    if not isinstance(codes, list) or codes != sorted(codes):
        raise FixtureClassError(f"{where}.codes: expected a sorted list")
    if note is not None and (not isinstance(note, str) or not note.strip()):
        raise FixtureClassError(f"{where}.note: expected non-empty text")
    if fixture_class is FixtureClass.REFUSING and not codes and note is None:
        raise FixtureClassError(f"{where}: a refusal with no code says why in a note")
    if fixture_class is not FixtureClass.REFUSING and codes:
        raise FixtureClassError(f"{where}: only a refusing root has codes")
    if fixture_class not in MODEL_CLASSES and note is None:
        raise FixtureClassError(f"{where}: a {fixture_class.value} directory says what it holds")
    return StoredClass(fixture_class, tuple(codes), note)


def read_fixture_classes(path: Path = FIXTURE_CLASSES_PATH) -> dict[str, StoredClass]:
    """The hand-reviewed classes, keyed by path relative to ``tests/fixtures/``."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA or set(data) != {"schema", "fixtures"}:
        raise FixtureClassError(f"{path}: expected {{schema: {SCHEMA}, fixtures}}")
    return {key: _stored_class(value, key) for key, value in data["fixtures"].items()}


def batch_classes(path: Path = BATCH_PATH) -> dict[str, FixtureClass]:
    """The 37 corpus fixtures, classed by the recapture batch."""
    batch = json.loads(path.read_text(encoding="utf-8"))
    refused = set(batch["refused"])
    return {
        name: FixtureClass.REFUSING if name in refused else FixtureClass.GENERATING
        for name in batch["fixtures"]
    }


def case_classes() -> dict[str, FixtureClass]:
    """Codegen-home conformance cases, classed by their stored generator answers."""
    root = cases.CODEGEN_CASES_DIR.relative_to(FIXTURES_DIR)
    classes = {
        str(root / answer.case_id): FixtureClass.REFUSING
        if answer.generator.run.outcome is GeneratorOutcome.REFUSED
        else FixtureClass.GENERATING
        for answer in cases.all_answers()
        if answer.home is CaseHome.CODEGEN
    }
    return classes | ({str(root): FixtureClass.CONTAINER} if classes else {})
