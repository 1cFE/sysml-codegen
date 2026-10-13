"""The committed station fixture is what this generator produces from its model (license lane).

The study tests run on the committed snapshot and package, so a generator change that would
alter them must show up here first, not as a mysterious study failure. A fresh capture must
equal ``station.snapshot.json`` byte for byte, and live generation from ``models/`` must equal
every tracked file of ``pkg/station_study/``. A failure names the regeneration commands in the
fixture's ``PROVENANCE.md``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tests.conftest import requires_license
from tests.study.conftest import REPO_ROOT, STATION, STATION_PACKAGE

pytestmark = requires_license

STALE = (
    "the committed station fixture no longer matches this generator: regenerate it with the "
    "commands under 'Regenerating' in tests/fixtures/study_station/PROVENANCE.md"
)


def _codegen(*argv: str) -> None:
    done = subprocess.run(
        [sys.executable, "-m", "sysml_codegen", *argv],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert done.returncode == 0, done.stderr


def _tracked(directory: Path) -> list[str]:
    """The files git tracks under ``directory``, relative to it. Bytecode caches are not."""
    listed = subprocess.run(
        ["git", "ls-files", "--", "."], capture_output=True, text=True, check=True,
        cwd=str(directory),
    ).stdout.split()
    return sorted(listed)


def test_a_recapture_equals_the_committed_snapshot(tmp_path: Path) -> None:
    fresh = tmp_path / "station.snapshot.json"
    _codegen("snapshot", "--models", str(STATION / "models"), "--output", str(fresh))
    assert fresh.read_bytes() == (STATION / "station.snapshot.json").read_bytes(), STALE


def test_live_generation_equals_the_committed_package(tmp_path: Path) -> None:
    fresh = tmp_path / "pkg" / "station_study"
    _codegen(
        "generate", "--models", str(STATION / "models"), "--output", str(fresh),
        "--package-name", "station_study",
    )
    committed = _tracked(STATION_PACKAGE)
    generated = sorted(
        path.relative_to(fresh).as_posix()
        for path in fresh.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    assert generated == committed, STALE
    differing = [
        relative for relative in committed
        if (fresh / relative).read_bytes() != (STATION_PACKAGE / relative).read_bytes()
    ]
    assert differing == [], STALE
