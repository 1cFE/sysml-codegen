"""Fixtures for the study tool tests.

The tools cite every path relative to a project root (``sysml_codegen.study.roots``). These
tests run from this repository, so a tool given a package inside it resolves this repository
as its root. A package copied under ``tmp_path`` sits outside every work tree, so those runs
name this repository with ``SYSML_CODEGEN_PROJECT_ROOT``: that reproduces the paths the tools
cited when they located the project from their own file, ``..`` segments included.

The committed packages here are read-only. A test that mutates one works on a
``package_copy``.
"""

from __future__ import annotations

import importlib.resources
import itertools
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from sysml_codegen.study import common, roots
from sysml_codegen.study import manifest as manifest_mod

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(__file__).parent / "data"
SYNTHETIC_DIR = DATA_DIR / "synthetic_pkg"
SYNTHETIC_PACKAGE = SYNTHETIC_DIR / "pkg"
SYNTHETIC_MANIFEST = SYNTHETIC_DIR / "manifest.json"
SYNTHETIC_AXES = SYNTHETIC_DIR / "axes.json"
#: The neutral station fixture: a project of its own, every path in it relative to it.
STATION = REPO_ROOT / "tests" / "fixtures" / "study_station"
STATION_PACKAGE = STATION / "pkg" / "station_study"
STATION_MANIFEST = STATION / "studies" / "manifest.json"
STATION_AXES = STATION / "studies" / "axes.json"
STATION_IDENTITY = STATION / "studies" / "baseline" / "package_identity.json"
STATION_BASELINE = STATION / "studies" / "baseline" / "baseline_result.json"
SCHEMAS = importlib.resources.files("sysml_codegen.study") / "schemas"
#: Every post-move tool path starts here (spec D7, design I4).
TOOL_PREFIX = "sysml_codegen/study/"


@pytest.fixture(autouse=True)
def _forget_project_roots(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """A tool pins its project root process-wide, so no test may inherit another's.

    The variable is cleared too: a developer's exported root must not decide a test.
    """
    monkeypatch.delenv(roots.PROJECT_ROOT_ENV, raising=False)
    roots.use_project_root(None)
    yield
    roots.use_project_root(None)


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def load_schema() -> Callable[[str], dict[str, Any]]:
    """Load one of the shipped JSON Schema files by stem, as a package resource."""

    def _load(stem: str) -> dict[str, Any]:
        resource = SCHEMAS / f"{stem}.schema.json"
        assert resource.is_file(), f"missing schema {stem}"
        schema: dict[str, Any] = json.loads(resource.read_text())
        return schema

    return _load


@pytest.fixture
def minimal_manifest_dict() -> dict[str, Any]:
    """The smallest manifest that validates — the shape, with placeholder facts."""
    return {
        "schema_version": "study-package-manifest/v1",
        "package": {"name": "some_pkg", "path": "some/where/some_pkg"},
        "fingerprints": {
            "indicator_inputs": {
                "recipe": "indicator-input-fingerprint/v1",
                "digest": "0" * 64,
                "files": ["contracts/model_contract.json", "inputs/a.json", "pipelines/p.yaml"],
            },
            "recorded_provenance": {
                "executable_fingerprint": "1" * 64,
                "semantic_fingerprint": "2" * 64,
            },
        },
        "objective_catalog": [{"name": "cost", "channel": "some_pkg__cost_calc__cost"}],
        "ties": [{"key": "some_pkg__b__x0", "rides_with": ["some_pkg__a__x"]}],
        "baseline": {
            "point": {"some_pkg__a__x": 1.0},
            "headline": {"channel": "some_pkg__cost_calc__cost", "value": 2.0},
            "verdicts": [{"source_local_identity": "ok", "expected": "satisfied"}],
        },
        "oracle": {
            "kind": "python_callable",
            "module": "some_oracle",
            "callable": "compute",
            "sys_path": "some/where",
        },
    }


def assert_post_move_tool_identity(document: dict[str, Any]) -> None:
    """SC7 on one tool document: the installed prefix, ``command[0]``, and a live digest.

    ``tool.path`` and every digested file sit under ``sysml_codegen/study/``; where the schema
    has a ``command``, its first token is ``tool.path``; and the digest recomputes from the
    bytes under the tool home.
    """
    tool = document["tool"]
    assert tool["path"].startswith(TOOL_PREFIX), tool["path"]
    files = [entry["path"] for entry in tool["source_digest"]["files"]]
    assert files and all(path.startswith(TOOL_PREFIX) for path in files), files
    if "command" in document:
        assert document["command"][0] == tool["path"]
    assert common.tool_source_digest(tuple(files)) == tool["source_digest"]


def environment_with_root(root: Path) -> dict[str, str]:
    """This process's environment plus ``SYSML_CODEGEN_PROJECT_ROOT`` naming ``root``."""
    return {**os.environ, roots.PROJECT_ROOT_ENV: str(root)}


def run_tool_raw(
    package: Path,
    manifest_path: Path,
    groups: Path,
    *,
    out: Path | None = None,
    group: tuple[str, ...] = (),
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    """Invoke ``indicators`` as a subprocess. Returns (returncode, stdout, stderr).

    A subprocess is the honest check for no partial output: a partial report would show up
    as bytes on stdout or a file on disk, and neither survives an in-process call.
    """
    argv = [
        sys.executable,
        "-m",
        "sysml_codegen.study.indicators",
        "--package",
        str(package),
        "--manifest",
        str(manifest_path),
        "--groups",
        str(groups),
    ]
    for name in group:
        argv += ["--group", name]
    if out is not None:
        argv += ["--out", str(out)]
    done = subprocess.run(
        argv, capture_output=True, text=True, cwd=str(cwd or REPO_ROOT), env=env
    )
    return done.returncode, done.stdout, done.stderr


def run_tool(
    package: Path, manifest_path: Path, groups: Path, *, cwd: Path | None = None
) -> dict[str, Any]:
    """Invoke ``indicators`` and return the parsed report. Raises if the run failed."""
    rc, out, err = run_tool_raw(package, manifest_path, groups, cwd=cwd)
    assert rc == 0, f"tool exited {rc}\n{err}"
    report: dict[str, Any] = json.loads(out)
    return report


@dataclass
class PackageCopy:
    """A writable copy of a package plus its manifest and axis declaration.

    Two rules make the negative tests trustworthy:

    * **Assert before mutating.** ``edit`` asserts its target substring exists in the copy
      before replacing. A negative test that corrupts nothing looks exactly like a passing
      one.
    * **Re-pin unless the test is about the pin.** The fingerprint gate runs before the
      parse, so a mutation test must rewrite the copy's pinned digest to reach the failure
      it means to test. ``run`` re-pins by default; ``run(repin=False)`` is the
      fingerprint-mismatch test.
    """

    path: Path
    manifest: Path
    axes: Path

    def edit(self, relative: str, old: str, new: str) -> None:
        """Replace a substring inside one file of the copy, asserting the target first."""
        target = self.path / relative
        text = target.read_text()
        assert old in text, f"mutation target not found in {relative}: {old!r}"
        target.write_text(text.replace(old, new, 1))

    def edit_manifest(self, mutate: Callable[[dict[str, Any]], object]) -> None:
        data = json.loads(self.manifest.read_text())
        mutate(data)
        self.manifest.write_text(json.dumps(data, indent=2) + "\n")

    def edit_axes(self, mutate: Callable[[dict[str, Any]], object]) -> None:
        data = json.loads(self.axes.read_text())
        mutate(data)
        self.axes.write_text(json.dumps(data, indent=2) + "\n")

    def repin(self) -> None:
        computed = manifest_mod.indicator_input_fingerprint(self.path)
        self.edit_manifest(
            lambda data: data["fingerprints"]["indicator_inputs"].update(
                digest=computed["digest"], files=[f["path"] for f in computed["files"]]
            )
        )

    def run(
        self, *, repin: bool = True, out: Path | None = None, group: tuple[str, ...] = ()
    ) -> tuple[int, str, str]:
        if repin:
            self.repin()
        return run_tool_raw(
            self.path, self.manifest, self.axes, out=out, group=group,
            env=environment_with_root(REPO_ROOT),
        )


@pytest.fixture
def package_copy(tmp_path: Path) -> Callable[[Path, Path, Path], PackageCopy]:
    """Factory: copy a package tree plus its manifest and axes into tmp_path."""

    counter = itertools.count()

    def _copy(package: Path, manifest_path: Path, axes_path: Path) -> PackageCopy:
        root = tmp_path / f"copy{next(counter)}"
        root.mkdir()
        package_dest = root / "pkg"
        shutil.copytree(package, package_dest)
        manifest_dest = root / "manifest.json"
        manifest_dest.write_bytes(manifest_path.read_bytes())
        axes_dest = root / "axes.json"
        axes_dest.write_bytes(axes_path.read_bytes())
        copy = PackageCopy(path=package_dest, manifest=manifest_dest, axes=axes_dest)
        # package.path is project-relative by schema; the copy lives outside the project.
        copy.edit_manifest(
            lambda data: data["package"].update(path=os.path.relpath(package_dest, REPO_ROOT))
        )
        return copy

    return _copy


@pytest.fixture
def synthetic_copy(package_copy: Callable[[Path, Path, Path], PackageCopy]) -> PackageCopy:
    return package_copy(SYNTHETIC_PACKAGE, SYNTHETIC_MANIFEST, SYNTHETIC_AXES)


@pytest.fixture
def station_copy(package_copy: Callable[[Path, Path, Path], PackageCopy]) -> PackageCopy:
    return package_copy(STATION_PACKAGE, STATION_MANIFEST, STATION_AXES)


# ------------------------------------------------------------- the station as a project


@pytest.fixture
def station_project(monkeypatch: pytest.MonkeyPatch) -> Path:
    """The station fixture read in place as its own project: the variable names it."""
    monkeypatch.setenv(roots.PROJECT_ROOT_ENV, str(STATION))
    return STATION


#: Commits in a scratch repository need an author, and must not depend on the caller's
#: git configuration.
_SCRATCH_COMMIT = (
    "-c", "user.name=study tests", "-c", "user.email=study-tests@example.invalid",
    "-c", "commit.gpgsign=false",
)


def _commit_everything(repo: Path, message: str) -> None:
    for argv in (["init", "-q"], ["add", "."], [*_SCRATCH_COMMIT, "commit", "-q", "-m", message]):
        subprocess.run(["git", "-C", str(repo), *argv], check=True, capture_output=True)


def commit_station_copy(repo: Path) -> Path:
    """Copy the station fixture to ``repo``, make it a fresh git repository, and commit it.

    The repository ignores ``__pycache__/``, as this one does, because loading the package
    writes bytecode beside it.
    """
    shutil.copytree(STATION, repo, ignore=shutil.ignore_patterns("__pycache__"))
    (repo / ".gitignore").write_text("__pycache__/\n")
    _commit_everything(repo, "station")
    return repo.resolve()


@pytest.fixture
def station_repo(tmp_path: Path) -> Path:
    """The station fixture copied into a fresh git repository and committed, for tests that
    mutate it, and for every ``integrate`` run."""
    return commit_station_copy(tmp_path / "station")


# --------------------------------------------------------- invoking integrate from a test


def commit_stub_simkit(repo: Path) -> Path:
    """A fresh git repository at ``repo`` holding an empty ``simkit`` package, committed.

    It is a simkit root gate 0 accepts and gate 1b can read a revision from, so integrate's own
    logic is testable without teax. Only a producer that executes the route needs real teax.
    """
    (repo / "simkit").mkdir(parents=True)
    (repo / "simkit" / "__init__.py").write_text('"""A stand-in for teax\'s simkit."""\n')
    _commit_everything(repo, "stub simkit")
    return repo.resolve()


def git_head(repo: Path) -> str:
    done = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    )
    return done.stdout.strip()


def integration_request(repo: Path, out: Path, **overrides: str | None) -> list[str]:
    """A complete ``integrate`` request against a committed station repository.

    An override replaces the value of one flag, named without its dashes and with
    underscores (``expected_teax_revision=...``); ``None`` drops the flag.
    """
    request: dict[str, str | None] = {
        "audited_work": "models@HEAD",
        "models_root": str(repo / "models"),
        "package": str(repo / "pkg" / "station_study"),
        "manifest": str(repo / "studies" / "manifest.json"),
        "groups": str(repo / "studies" / "axes.json"),
        "census_file": str(repo / "census.json"),
        "route_sys_path": str(repo / "studies"),
        "route_module": "study_route",
        "route_callable": "execute_baseline",
        "out_dir": str(out),
    }
    request.update(overrides)
    return [
        token
        for name, value in request.items()
        if value is not None
        for token in ("--" + name.replace("_", "-"), value)
    ]


def seam_environment(
    *, teax: Path | None, license_key: str | None, tmpdir: Path, **exported: str
) -> dict[str, str]:
    """This process's environment, with every setting ``integrate`` reads stated explicitly.

    The project-root variable, ``PYTHONPATH``, ``TEAX_SIMKIT_PATH`` and the licence key are
    removed first, so neither a developer's shell nor another lane decides a test. Then
    ``teax`` and ``license_key`` are set when given, and ``exported`` on top. ``TMPDIR`` is
    ``tmpdir``, because every run that passes gate 0 backs the package up into a new
    temporary directory and leaves it there for recovery.
    """
    removed = {roots.PROJECT_ROOT_ENV, roots.TEAX_SIMKIT_PATH, "PYTHONPATH", "SYSIDE_LICENSE_KEY"}
    env = {name: value for name, value in os.environ.items() if name not in removed}
    if teax is not None:
        env[roots.TEAX_SIMKIT_PATH] = str(teax)
    if license_key is not None:
        env["SYSIDE_LICENSE_KEY"] = license_key
    tmpdir.mkdir(parents=True, exist_ok=True)
    return {**env, "TMPDIR": str(tmpdir), **exported}


@dataclass
class IntegrateRun:
    """One ``integrate`` invocation, read back by exit code and return document."""

    returncode: int
    document: dict[str, Any]
    stderr: str

    def row(self, gate: str) -> dict[str, Any]:
        """The return's row for one of the ten gates."""
        (row,) = (row for row in self.document["gates"] if row["gate"] == gate)
        found: dict[str, Any] = row
        return found


def run_integrate(repo: Path, argv: list[str], env: dict[str, str]) -> IntegrateRun:
    """Invoke ``integrate`` from ``repo`` as a caller does: a subprocess.

    The return document is under ``--out-dir`` once gate 0 built the request, and on stdout
    when it rejected the request first. A run that wrote neither fails the test here.
    """
    done = subprocess.run(
        [sys.executable, "-m", "sysml_codegen.study.integrate", *argv],
        capture_output=True, text=True, cwd=str(repo), env=env,
    )
    out = Path(argv[argv.index("--out-dir") + 1]) if "--out-dir" in argv else None
    written = out / "integration_return.json" if out is not None else None
    if written is not None and written.is_file():
        document: dict[str, Any] = json.loads(written.read_text())
    else:
        assert done.stdout, f"no return document (exit {done.returncode})\n{done.stderr}"
        document = json.loads(done.stdout)
    return IntegrateRun(done.returncode, document, done.stderr)
