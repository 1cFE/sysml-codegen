"""Every directory under ``tests/fixtures/`` is classed, by exactly one source (Item 2a § B).

Spec criterion B5's first half: an unclassed directory fails here, by name. Whether each
stored class is still what the generator does is P3's licensed fixture test.

Pure: walks the tree and reads the three class sources (``fixture_classes.py``).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.conftest import FIXTURES_DIR
from tests.helpers.refusal_cases.fixture_classes import (
    MODEL_CLASSES,
    FixtureClass,
    all_classes,
    batch_classes,
    case_classes,
    read_fixture_classes,
)

STORED = read_fixture_classes()
SOURCES = {"fixture_classes.json": STORED.keys(), "batch.json": batch_classes().keys()}
SOURCES["stored answers"] = case_classes().keys()
CLASSES: dict[str, FixtureClass] = {k: v.fixture_class for k, v in all_classes().items()}


def test_each_path_has_exactly_one_class_source():
    names = list(SOURCES)
    overlaps = {
        (a, b): sorted(set(SOURCES[a]) & set(SOURCES[b]))
        for i, a in enumerate(names)
        for b in names[i + 1 :]
        if set(SOURCES[a]) & set(SOURCES[b])
    }
    assert overlaps == {}


def _covering(relative: Path) -> FixtureClass | None:
    """The class of the nearest classed directory at or above ``relative``, if any."""
    for candidate in (relative, *relative.parents):
        if str(candidate) in CLASSES:
            return CLASSES[str(candidate)]
    return None


def test_every_directory_is_a_classed_root_inside_one_or_under_a_container():
    unclassed = []
    for path in sorted(p for p in FIXTURES_DIR.rglob("*") if p.is_dir()):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(FIXTURES_DIR)
        covering = _covering(relative)
        if str(relative) in CLASSES:
            continue
        if covering is None or covering is FixtureClass.CONTAINER:
            unclassed.append(str(relative))
    assert unclassed == []


def _has_models(path: Path) -> bool:
    return any(path.rglob("*.sysml"))


@pytest.mark.parametrize("key", sorted(CLASSES), ids=str)
def test_a_classed_path_exists_and_fits_its_class(key: str):
    path = FIXTURES_DIR / key
    assert path.is_dir(), f"{key} is classed but is not a directory"
    fixture_class = CLASSES[key]
    if fixture_class in MODEL_CLASSES:
        assert _has_models(path)
    elif fixture_class is FixtureClass.NOT_A_MODEL:
        assert not _has_models(path)
    else:
        assert not any(path.glob("*.sysml")), f"container {key} holds its own model files"
        assert any(p.is_dir() for p in path.iterdir()), f"container {key} has no children"
        parent = _covering(Path(key).parent) if Path(key).parent != Path() else None
        assert parent in (None, FixtureClass.CONTAINER), f"container {key} sits in a model"
