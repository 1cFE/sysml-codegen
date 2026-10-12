"""``integrate`` on the station with real teax: the simkit probe, and gate 7's refusal.

The probe pair is fusion-tea ``tests/study/test_integrate_preconditions.py`` at ``b06585709``,
moved here because it needs teax. The gate-7 test needs the licence as well: gates 2 and 4
regenerate the package and recapture the snapshot before gate 7 runs the route.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from sysml_codegen.study import integrate, manifest, roots
from tests.conftest import requires_license
from tests.study.conftest import (
    STATION,
    commit_station_copy,
    git_head,
    integration_request,
    run_integrate,
    seam_environment,
)

pytestmark = pytest.mark.execution


@pytest.fixture
def simkit_root(execution_provenance: Any) -> Path:
    root: Path = execution_provenance.teax_simkit_root
    return root


def independently_can_import_simkit(env: dict[str, str]) -> bool:
    """What a ``verify.py`` subprocess under ``env`` actually does, built without the seam."""
    done = subprocess.run(
        [sys.executable, "-c", "import simkit"],
        capture_output=True, text=True, cwd=str(STATION), env=env,
    )
    return done.returncode == 0


def test_simkit_probe_agrees_with_the_verify_subprocess(
    monkeypatch: pytest.MonkeyPatch, simkit_root: Path
) -> None:
    """Gate 8's residual is only narrow while this holds."""
    monkeypatch.setenv(roots.PROJECT_ROOT_ENV, str(STATION))
    monkeypatch.setenv(roots.TEAX_SIMKIT_PATH, str(simkit_root))
    env = integrate.seam_env()
    assert integrate.simkit_module_path(env) is not None
    assert independently_can_import_simkit(env) is True


def test_simkit_probe_finds_inherited_path_without_teax_simkit_path(
    monkeypatch: pytest.MonkeyPatch, simkit_root: Path
) -> None:
    """The probe reports imports the producer can perform, including inherited ones."""
    monkeypatch.setenv(roots.PROJECT_ROOT_ENV, str(STATION))
    monkeypatch.delenv(roots.TEAX_SIMKIT_PATH, raising=False)
    monkeypatch.setenv("PYTHONPATH", str(simkit_root))
    env = integrate.seam_env()
    assert integrate.simkit_module_path(env) is not None
    assert independently_can_import_simkit(env) is True


# ------------------------------------------------------------- gate 7 refuses (SC3)

#: A route that reads a project file outside its declared sources, then runs the station's.
LEAKY_ROUTE = '''"""The station route, after reading a project file no route may read."""
from pathlib import Path

import study_route


def execute_baseline(out, *, package_dir, manifest_path):
    (Path(manifest_path).resolve().parents[1] / "census.json").read_text()
    return study_route.execute_baseline(out, package_dir=package_dir, manifest_path=manifest_path)
'''


def _lineage(repo: Path) -> dict[str, str]:
    package = repo / "pkg" / "station_study"
    return {
        "expected_semantic_fingerprint": manifest.read_semantic_fingerprint(package),
        "expected_executable_fingerprint": manifest.read_executable_fingerprint(package),
    }


@requires_license
def test_a_route_that_reads_outside_its_declared_sources_is_refused_at_gate_7(
    simkit_root: Path, tmp_path: Path
) -> None:
    """``read_coverage``'s docstring: an undeclared dependency read fails the observed run."""
    repo = commit_station_copy(tmp_path / "station")
    (repo / "studies" / "leaky_route.py").write_text(LEAKY_ROUTE)
    env = seam_environment(
        teax=simkit_root, license_key=os.environ["SYSIDE_LICENSE_KEY"], tmpdir=tmp_path / "tmp"
    )
    argv = integration_request(
        repo, tmp_path / "out", route_module="leaky_route",
        expected_teax_revision=git_head(simkit_root), **_lineage(repo),
    )
    result = run_integrate(repo, argv, env)

    assert result.returncode == 1, result.stderr
    assert [row["status"] for row in result.document["gates"][:7]] == ["pass"] * 7
    blocker = result.document["blocker"]
    assert (blocker["gate"], blocker["mode"], blocker["condition"]) == (
        "preflight", "refused", "read-coverage-refused"
    )
    assert blocker["producer"] == "sysml_codegen/study/read_coverage.py"
    assert blocker["detail"] == str([f"undeclared dependency read: {repo / 'census.json'}"])
    assert blocker["evidence"] == ["../out/read_coverage.json"]
    receipt = json.loads((tmp_path / "out" / "read_coverage.json").read_text())
    assert receipt["outcome"] == "fail"
