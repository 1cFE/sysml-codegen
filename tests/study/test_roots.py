"""The project root, the tool home and the teax root (design DD2, I3).

Paths a document cites are relative to the project root, and the same project gives the same
bytes from any working directory. Where no root can be named, or the working directory sits
in a different work tree from the package, the tool refuses with exit 2 and writes nothing.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from sysml_codegen.study import roots
from tests.study.conftest import SYNTHETIC_AXES, SYNTHETIC_MANIFEST, SYNTHETIC_PACKAGE


def _git_repo(path: Path) -> Path:
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    return path.resolve()


@pytest.fixture
def package_repo(tmp_path: Path) -> Path:
    """A git work tree holding a package directory, ``pkg``."""
    repo = _git_repo(tmp_path / "project")
    (repo / "pkg").mkdir()
    return repo


@pytest.fixture
def other_repo(tmp_path: Path) -> Path:
    return _git_repo(tmp_path / "elsewhere")


@pytest.fixture
def outside(tmp_path: Path) -> Path:
    """A directory inside no git work tree."""
    path = tmp_path / "scratch"
    path.mkdir()
    assert subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"], capture_output=True
    ).returncode != 0, f"{path} is inside a work tree; these tests need one that is not"
    return path


@pytest.fixture
def synthetic_project(package_repo: Path) -> Path:
    """A project of its own: the synthetic package, manifest and axes at its top."""
    shutil.copytree(SYNTHETIC_PACKAGE, package_repo / "pkg", dirs_exist_ok=True)
    manifest = json.loads(SYNTHETIC_MANIFEST.read_text())
    manifest["package"]["path"] = "pkg"
    (package_repo / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    shutil.copyfile(SYNTHETIC_AXES, package_repo / "axes.json")
    return package_repo


def _indicators(project: Path, cwd: Path, *package: str) -> subprocess.CompletedProcess[str]:
    argv = [
        sys.executable, "-m", "sysml_codegen.study.indicators",
        "--package", str(project / (package[0] if package else "pkg")),
        "--manifest", str(project / "manifest.json"),
        "--groups", str(project / "axes.json"),
    ]
    return subprocess.run(argv, capture_output=True, text=True, cwd=str(cwd))


# ------------------------------------------------------------------- the order


def test_the_override_wins_over_the_variable_and_every_work_tree(
    package_repo: Path, other_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(roots.PROJECT_ROOT_ENV, str(other_repo))
    monkeypatch.chdir(other_repo)
    roots.use_project_root(package_repo)
    assert roots.project_root() == package_repo
    # An override is never checked against a work tree: the caller states where it is.
    assert roots.require_project_root("indicators", other_repo / "pkg") == package_repo


def test_the_variable_wins_over_the_anchor_without_a_work_tree_check(
    package_repo: Path, other_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(roots.PROJECT_ROOT_ENV, str(other_repo))
    monkeypatch.chdir(package_repo)
    assert roots.require_project_root("indicators", package_repo / "pkg") == other_repo
    assert roots.project_root() == other_repo


def test_the_command_line_root_is_the_anchors_work_tree_and_is_pinned(
    package_repo: Path, outside: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(outside)
    assert roots.require_project_root("indicators", package_repo / "pkg") == package_repo
    # Every later lookup in this run answers with the pinned root, even from outside.
    assert roots.project_root() == package_repo


def test_each_command_line_resolution_is_fresh(
    package_repo: Path, other_repo: Path, outside: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A pin from one in-process run never answers for a package in another project."""
    monkeypatch.chdir(outside)
    roots.require_project_root("indicators", package_repo / "pkg")
    (other_repo / "pkg").mkdir()
    assert roots.require_project_root("indicators", other_repo / "pkg") == other_repo
    assert roots.project_root() == other_repo


def test_a_library_call_uses_the_working_directorys_work_tree(
    package_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(package_repo / "pkg")
    assert roots.project_root() == package_repo


def test_a_library_call_with_no_root_raises_root_error(
    outside: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(outside)
    with pytest.raises(roots.RootError, match=roots.PROJECT_ROOT_ENV):
        roots.project_root()


def test_a_named_root_that_is_not_a_directory_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv(roots.PROJECT_ROOT_ENV, str(tmp_path / "absent"))
    with pytest.raises(SystemExit) as exit_:
        roots.require_project_root("verify", tmp_path)
    assert exit_.value.code == 2
    assert str(tmp_path / "absent") in capsys.readouterr().err
    with pytest.raises(roots.RootError):
        roots.use_project_root(tmp_path / "absent")


# ------------------------------------------------------------------ refusals


def test_a_package_in_no_work_tree_refuses(
    outside: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(outside)
    with pytest.raises(SystemExit) as exit_:
        roots.require_project_root("preflight", outside / "pkg")
    err = capsys.readouterr().err
    assert exit_.value.code == 2
    assert err.startswith("preflight: ")
    assert str(outside / "pkg") in err and roots.PROJECT_ROOT_ENV in err


def test_a_cwd_inside_another_work_tree_refuses(
    package_repo: Path,
    other_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(other_repo)
    with pytest.raises(SystemExit) as exit_:
        roots.require_project_root("indicators", anchor=package_repo / "pkg")
    err = capsys.readouterr().err
    assert exit_.value.code == 2
    assert str(other_repo) in err and str(package_repo) in err


def test_a_repository_git_refuses_is_refused_with_gits_message(
    package_repo: Path,
    outside: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Dubious ownership is not "no work tree": the refusal carries git's own remedy.

    ``GIT_TEST_ASSUME_DIFFERENT_OWNER`` is git's own switch for producing this failure
    without a second user account.
    """
    monkeypatch.chdir(outside)
    monkeypatch.setenv("GIT_TEST_ASSUME_DIFFERENT_OWNER", "1")
    with pytest.raises(SystemExit) as exit_:
        roots.require_project_root("verify", package_repo / "pkg")
    err = capsys.readouterr().err
    assert exit_.value.code == 2
    assert "detected dubious ownership" in err and "safe.directory" in err
    assert "in no git work tree" not in err
    assert roots.PROJECT_ROOT_ENV in err


def test_a_git_failure_in_the_working_directory_is_not_read_as_outside(
    package_repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Inside ``.git`` there is no work tree to compare, and git says so; that refuses too."""
    monkeypatch.chdir(package_repo / ".git")
    with pytest.raises(SystemExit) as exit_:
        roots.require_project_root("indicators", package_repo / "pkg")
    err = capsys.readouterr().err
    assert exit_.value.code == 2
    assert "must be run in a work tree" in err


def test_a_refused_tool_writes_no_document(
    synthetic_project: Path, other_repo: Path, tmp_path: Path
) -> None:
    out = tmp_path / "report.json"
    done = subprocess.run(
        [
            sys.executable, "-m", "sysml_codegen.study.indicators",
            "--package", str(synthetic_project / "pkg"),
            "--manifest", str(synthetic_project / "manifest.json"),
            "--groups", str(synthetic_project / "axes.json"),
            "--out", str(out),
        ],
        capture_output=True, text=True, cwd=str(other_repo),
    )
    assert done.returncode == 2
    assert done.stdout == ""
    assert not out.exists()
    assert str(other_repo) in done.stderr


# ----------------------------------------------------------- the same bytes (I3)


def test_a_working_directory_outside_every_work_tree_gives_the_same_bytes(
    synthetic_project: Path, outside: Path
) -> None:
    inside = _indicators(synthetic_project, synthetic_project)
    from_outside = _indicators(synthetic_project, outside)
    assert inside.returncode == 0, inside.stderr
    assert from_outside.returncode == 0, from_outside.stderr
    assert inside.stdout == from_outside.stdout
    report = json.loads(inside.stdout)
    # Cited relative to the package's own project, not to this repository or the cwd.
    assert report["manifest"]["path"] == "manifest.json"
    assert report["axis_declaration"]["path"] == "axes.json"


def test_a_missing_package_keeps_its_old_failure_and_exit_code(
    synthetic_project: Path, outside: Path
) -> None:
    """The anchor is the nearest existing ancestor, so the root still resolves and the
    tool fails where it always did: at its own package checks, exit 1."""
    done = _indicators(synthetic_project, outside, "pkg/missing")
    assert done.returncode == 1
    assert done.stdout == ""
    assert done.stderr.startswith("cannot read pkg/missing/contracts/package_contract.json")
    assert roots.PROJECT_ROOT_ENV not in done.stderr


# ------------------------------------------------------------- side effects


def test_no_lookup_mutates_the_process_environment(
    package_repo: Path, outside: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    before = dict(os.environ)
    monkeypatch.chdir(outside)
    roots.require_project_root("indicators", package_repo / "pkg")
    roots.project_root()
    roots.use_project_root(package_repo)
    roots.environment()["INJECTED"] = "x"
    roots.teax_simkit_path()
    assert dict(os.environ) == before


def test_the_tool_home_holds_the_installed_package() -> None:
    assert roots.TOOL_HOME == Path(roots.__file__).resolve().parents[2]
    assert (roots.TOOL_HOME / "sysml_codegen" / "study" / "roots.py").is_file()


def test_the_teax_root_is_the_variable_and_nothing_else(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(roots.TEAX_SIMKIT_PATH, raising=False)
    assert roots.teax_simkit_path() is None
    monkeypatch.setenv(roots.TEAX_SIMKIT_PATH, "")
    assert roots.teax_simkit_path() is None
    monkeypatch.setenv(roots.TEAX_SIMKIT_PATH, str(tmp_path))
    assert roots.teax_simkit_path() == tmp_path
