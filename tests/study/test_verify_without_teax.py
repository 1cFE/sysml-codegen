"""Without teax, ``verify`` refuses: it names teax and writes nothing (spec B9, design I9).

Before the move, a missing teax surfaced as a bare ``import simkit`` traceback. Here ``verify``
runs as a subprocess with ``PYTHONPATH`` unset, so no simkit that another lane put on
``sys.path`` can leak in. Its other inputs are the committed station fixture's manifest and
identity document. The store path is never opened, because the teax check comes first.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from sysml_codegen.study import roots
from tests.study.conftest import (
    REPO_ROOT,
    STATION,
    STATION_IDENTITY,
    STATION_MANIFEST,
    STATION_PACKAGE,
)


def _environment_without_teax() -> dict[str, str]:
    environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    environment[roots.PROJECT_ROOT_ENV] = str(STATION)
    return environment


def test_verify_without_teax_names_teax_and_writes_nothing(tmp_path: Path) -> None:
    environment = _environment_without_teax()
    probe = subprocess.run(
        [sys.executable, "-c", "import simkit"], capture_output=True, env=environment
    )
    assert probe.returncode != 0, "simkit imports without PYTHONPATH, so teax is not missing"

    out = tmp_path / "results" / "verification_summary.json"
    done = subprocess.run(
        [
            sys.executable, "-m", "sysml_codegen.study.verify",
            "--package", str(STATION_PACKAGE),
            "--manifest", str(STATION_MANIFEST),
            "--identity", str(STATION_IDENTITY),
            "--store", str(tmp_path / "station-grid-v1.db"),
            "--out", str(out),
        ],
        capture_output=True, text=True, cwd=str(REPO_ROOT), env=environment,
    )
    assert done.returncode == 1
    assert "verify needs teax" in done.stderr and "simkit" in done.stderr
    assert "Traceback" not in done.stderr
    assert done.stdout == ""
    assert list(tmp_path.iterdir()) == []
