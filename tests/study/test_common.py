"""The shared internals the study tools stand on.

Moved from fusion-tea ``tests/study/test_common.py`` at ``b06585709``. The committed package
is this repository's study fixture, and tool sources are read under the tool home.
"""

from pathlib import Path

import pytest

from sysml_codegen.study import common
from sysml_codegen.study import manifest as manifest_mod
from tests.study.conftest import STATION_PACKAGE


def test_the_git_clean_gate_passes_on_the_committed_package() -> None:
    common.assert_tree_clean(STATION_PACKAGE)


def test_the_git_clean_gate_names_the_offending_file(repo_root: Path) -> None:
    """The gate runs after every run, because a mutation a run introduces is exactly
    what a pre-run check cannot see. So it must actually see one."""
    tree = repo_root / "tests" / "study" / "_clean_gate_probe"
    tree.mkdir()
    intruder = tree / "left_behind.txt"
    try:
        common.assert_tree_clean(tree)  # an empty tree is clean
        intruder.write_text("a file a run left behind\n")
        with pytest.raises(common.ToolError) as exc:
            common.assert_tree_clean(tree)
        assert "left_behind.txt" in str(exc.value)
        assert "not git-clean" in str(exc.value)
    finally:
        intruder.unlink(missing_ok=True)
        tree.rmdir()


def test_the_git_clean_gate_refuses_a_path_git_cannot_see(tmp_path: Path) -> None:
    """tmp_path is outside the repository; a gate that quietly passed there would
    report 'clean' about a tree it never looked at."""
    with pytest.raises(common.ToolError) as exc:
        common.assert_tree_clean(tmp_path)
    assert "git status failed" in str(exc.value)


def test_an_atomic_write_leaves_no_temporary_behind(tmp_path: Path) -> None:
    path = common.write_document({"a": 1}, tmp_path / "out" / "doc.json")
    assert path.read_text() == '{\n  "a": 1\n}\n'
    assert sorted(p.name for p in path.parent.iterdir()) == ["doc.json"]


def test_a_failed_write_leaves_nothing(tmp_path: Path) -> None:
    class Unserializable:
        pass

    with pytest.raises(TypeError):
        common.write_document({"a": Unserializable()}, tmp_path / "doc.json")
    assert not (tmp_path / "doc.json").exists()
    assert list(tmp_path.iterdir()) == []


def test_the_tool_source_digest_carries_its_file_list() -> None:
    """One recipe id must not silently mean two things across the tools."""
    files = ("sysml_codegen/study/common.py", "sysml_codegen/study/identity.py")
    computed = common.tool_source_digest(files)
    assert computed["recipe"] == "tool-source-digest/v1"
    assert [f["path"] for f in computed["files"]] == list(files)
    assert all(len(f["sha256"]) == 64 for f in computed["files"])


def test_the_tool_source_digest_shape_matches_the_manifest_modules() -> None:
    theirs = manifest_mod.tool_source_digest()
    mine = common.tool_source_digest(("sysml_codegen/study/common.py",))
    assert set(theirs) == set(mine)
    assert set(theirs["files"][0]) == set(mine["files"][0])


def test_a_missing_tool_source_file_fails_naming_it() -> None:
    with pytest.raises(common.ToolError) as exc:
        common.tool_source_digest(("sysml_codegen/study/no_such_tool.py",))
    assert "sysml_codegen/study/no_such_tool.py" in str(exc.value)


def test_a_project_digest_reads_under_the_root_it_is_given(tmp_path: Path) -> None:
    """A record digests its oracle's sources under the project root, not the tool home."""
    (tmp_path / "studies").mkdir()
    oracle = tmp_path / "studies" / "oracle.py"
    oracle.write_text("VALUE = 1\n")
    computed = common.tool_source_digest(("studies/oracle.py",), root=tmp_path)
    assert computed["files"] == [
        {"path": "studies/oracle.py", "sha256": manifest_mod.sha256_file(oracle)}
    ]
    with pytest.raises(common.ToolError, match="studies/oracle.py"):
        common.tool_source_digest(("studies/oracle.py",))  # not under the tool home


def test_read_json_names_the_file_and_what_it_wanted(tmp_path: Path) -> None:
    with pytest.raises(common.ToolError) as exc:
        common.read_json(tmp_path / "gone.json", "package identity document")
    assert "package identity document" in str(exc.value) and "gone.json" in str(exc.value)

    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    with pytest.raises(common.ToolError) as exc:
        common.read_json(bad, "package identity document")
    assert "not valid JSON" in str(exc.value)


def test_relative_deviation_does_not_divide_by_zero() -> None:
    assert common.relative_deviation(0.0, 0.0) == 0.0
    assert common.relative_deviation(2.0, 1.0) == 1.0
