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

from sysml_codegen.study import manifest as manifest_mod
from sysml_codegen.study import roots

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(__file__).parent / "data"
SYNTHETIC_DIR = DATA_DIR / "synthetic_pkg"
SYNTHETIC_PACKAGE = SYNTHETIC_DIR / "pkg"
SYNTHETIC_MANIFEST = SYNTHETIC_DIR / "manifest.json"
SYNTHETIC_AXES = SYNTHETIC_DIR / "axes.json"
STATION_PACKAGE = REPO_ROOT / "tests" / "fixtures" / "study_station" / "pkg" / "station_study"
SCHEMAS = importlib.resources.files("sysml_codegen.study") / "schemas"


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

    def repin(self) -> None:
        computed = manifest_mod.indicator_input_fingerprint(self.path)
        self.edit_manifest(
            lambda data: data["fingerprints"]["indicator_inputs"].update(
                digest=computed["digest"], files=[f["path"] for f in computed["files"]]
            )
        )

    def run(self, *, repin: bool = True) -> tuple[int, str, str]:
        if repin:
            self.repin()
        return run_tool_raw(
            self.path, self.manifest, self.axes, env=environment_with_root(REPO_ROOT)
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
