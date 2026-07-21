from __future__ import annotations

import os
from pathlib import Path

import pytest

from sysml_codegen.analysis.source_referent import (
    map_live_source_referent,
    validate_snapshot_source_referent,
)


def test_directory_and_exact_file_roots(tmp_path: Path):
    directory = tmp_path / "models"
    directory.mkdir()
    source = directory / "nested" / "model.sysml"
    source.parent.mkdir()
    source.write_text("")

    assert map_live_source_referent(str(source), [directory]) == "root-0/nested/model.sysml"
    assert map_live_source_referent(str(source), [source]) == "root-0/model.sysml"
    with pytest.raises(ValueError, match="does not match"):
        map_live_source_referent(str(directory / "other.sysml"), [source])


def test_exact_file_then_most_specific_directory_then_earliest_duplicate(tmp_path: Path):
    broad = tmp_path / "models"
    narrow = broad / "nested"
    narrow.mkdir(parents=True)
    source = narrow / "model.sysml"
    source.write_text("")

    assert map_live_source_referent(str(source), [broad, narrow]) == "root-1/model.sysml"
    assert map_live_source_referent(str(source), [broad, source, narrow]) == "root-1/model.sysml"
    assert map_live_source_referent(str(source), [narrow, narrow]) == "root-0/model.sysml"


def test_root_slot_distinguishes_same_relative_file_and_survives_relocation(tmp_path: Path):
    tree_a = tmp_path / "checkout-a"
    tree_b = tmp_path / "checkout-b"
    for tree in (tree_a, tree_b):
        for root_name in ("library", "design"):
            root = tree / root_name
            root.mkdir(parents=True)
            (root / "model.sysml").write_text("")

    a = [
        map_live_source_referent(
            str(tree_a / name / "model.sysml"), [tree_a / "library", tree_a / "design"]
        )
        for name in ("library", "design")
    ]
    b = [
        map_live_source_referent(
            str(tree_b / name / "model.sysml"), [tree_b / "library", tree_b / "design"]
        )
        for name in ("library", "design")
    ]
    assert a == b == ["root-0/model.sysml", "root-1/model.sysml"]


def test_lexical_symlink_spelling_and_redundant_leading_separators(tmp_path: Path):
    real = tmp_path / "real"
    real.mkdir()
    source = real / "model.sysml"
    source.write_text("")
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)

    assert map_live_source_referent(str(link / "model.sysml"), [link]) == "root-0/model.sysml"
    redundant = f"///{str(source).lstrip('/')}"
    assert map_live_source_referent(redundant, [real]) == "root-0/model.sysml"


def test_utf8_segments_are_canonically_percent_encoded(tmp_path: Path):
    root = tmp_path / "models"
    source = root / "space here" / "café#.sysml"
    source.parent.mkdir(parents=True)
    source.write_text("")
    referent = map_live_source_referent(str(source), [root])
    assert referent == "root-0/space%20here/caf%C3%A9%23.sysml"
    assert validate_snapshot_source_referent(referent) == referent


@pytest.mark.parametrize(
    "referent",
    [
        "root-0",
        "root-0/",
        "root-00/file.sysml",
        "root--1/file.sysml",
        "root-0//file.sysml",
        "root-0/.",
        "root-0/..",
        "root-0/%2e%2e",
        "root-0/%2Fetc",
        "root-0/%5Cetc",
        "root-0/space%20here/%63af%C3%A9.sysml",
        "/root-0/file.sysml",
        "root-0/C:%5Cfile.sysml",
    ],
)
def test_malformed_snapshot_referents_fail_loud(referent: str):
    with pytest.raises(ValueError, match="canonical source referent"):
        validate_snapshot_source_referent(referent)


def test_live_mapping_never_depends_on_cwd(tmp_path: Path, monkeypatch):
    root = tmp_path / "models"
    root.mkdir()
    source = root / "model.sysml"
    source.write_text("")
    before = map_live_source_referent(str(source), [root])
    monkeypatch.chdir(tmp_path.parent)
    assert os.getcwd() == str(tmp_path.parent)
    assert map_live_source_referent(str(source), [root]) == before
