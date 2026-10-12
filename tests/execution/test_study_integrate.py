"""``integrate`` on the station with real teax: the simkit probe, gates 7 and 8, and ``CANDIDATE``.

The probe pair is fusion-tea ``tests/study/test_integrate_preconditions.py`` at ``b06585709``,
moved here because it needs teax. Every full ``integrate`` run needs the licence as well: gates
2 and 4 regenerate the package and recapture the snapshot before gate 7 runs the route.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from sysml_codegen.study import integrate, manifest, read_coverage, roots
from tests.conftest import requires_license
from tests.study.conftest import (
    STATION,
    assert_post_move_tool_identity,
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


# ------------------------------------------------------- gate 7's route on the station


def test_the_station_route_passes_read_coverage(
    monkeypatch: pytest.MonkeyPatch, simkit_root: Path, tmp_path: Path
) -> None:
    """The route reads only declared sources and the interpreter's own runtime data.

    Gate 7's driver, run in the environment and scratch directory ``integrate.execute_baseline``
    gives it. Under uv's standalone CPython the route first read ``/dev/urandom`` and then
    ``/usr/share/zoneinfo/Etc/UTC`` outside ``sys.prefix``, and each was refused as an
    undeclared dependency until the observer counted the interpreter's platform data as
    runtime (spec B13).
    """
    repo = commit_station_copy(tmp_path / "station")
    out = tmp_path / "out"
    scratch = out / "read-coverage-tmp-lane-token"
    scratch.mkdir(parents=True)
    monkeypatch.setenv(roots.PROJECT_ROOT_ENV, str(repo))
    monkeypatch.setenv(roots.TEAX_SIMKIT_PATH, str(simkit_root))
    monkeypatch.delenv("PYTHONPATH", raising=False)
    env = {**integrate.seam_env(), "TMPDIR": str(scratch)}
    done = subprocess.run(
        [sys.executable, "-c", integrate.ROUTE_DRIVER_SOURCE, str(repo / "studies"),
         "study_route", "execute_baseline", str(out), str(repo / "pkg" / "station_study"),
         str(repo / "studies" / "manifest.json"), "lane-token"],
        capture_output=True, text=True, cwd=str(repo), env=env,
    )
    receipt = json.loads((out / "read_coverage.json").read_text())

    assert receipt["violations"] == [], done.stderr
    assert done.returncode == 0, done.stderr
    assert read_coverage.valid_receipt(receipt, "lane-token")


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


# ------------------------------------------------------------- gate 8 refuses (SC3)


@requires_license
def test_an_oracle_that_disagrees_with_the_store_is_refused_at_gate_8(
    simkit_root: Path, tmp_path: Path
) -> None:
    """``verify.py:10-11``: named channels agree at rel < 1e-9, or verify refuses.

    The station's oracle is skewed by one part in a million on the annual cost. No gate before
    8 judges the oracle's arithmetic, so they pass, and gate 8 files verify's exit as a refusal
    (``integrate.gate_verification``). verify writes no summary when it refuses.
    """
    repo = commit_station_copy(tmp_path / "station")
    oracle = repo / "studies" / "oracle_entry.py"
    exact = "* values[STATION + \"energy_price\"] * 1000.0"
    assert oracle.read_text().count(exact) == 1
    oracle.write_text(oracle.read_text().replace(exact, exact + " * 1.000001"))
    env = seam_environment(
        teax=simkit_root, license_key=os.environ["SYSIDE_LICENSE_KEY"], tmpdir=tmp_path / "tmp"
    )
    argv = integration_request(
        repo, tmp_path / "out", expected_teax_revision=git_head(simkit_root), **_lineage(repo)
    )
    result = run_integrate(repo, argv, env)

    assert result.returncode == 1, result.stderr
    assert [row["status"] for row in result.document["gates"][:8]] == ["pass"] * 8
    assert result.row("lineage")["status"] == "not reached"
    blocker = result.document["blocker"]
    assert (blocker["gate"], blocker["mode"], blocker["condition"]) == (
        "verification", "refused", "verification-refused"
    )
    assert blocker["producer"] == "sysml_codegen/study/verify.py"
    assert blocker["detail"].startswith("verify.py exited 1: ")
    assert "PumpStation__station__pumping__annual_cost" in blocker["detail"]
    assert "relative deviation" in blocker["detail"]
    assert blocker["evidence"] == ["../out/verify_stderr.txt"]
    assert not (tmp_path / "out" / "verification_summary.json").exists()


# ------------------------------------------------------------------- CANDIDATE (SC3)


@requires_license
def test_the_station_returns_candidate_with_all_ten_gates_passing(
    simkit_root: Path, tmp_path: Path
) -> None:
    """``integrate``'s module docstring: ``CANDIDATE`` (exit 0) names one package, manifest, pin
    and lineage, and only when all ten gates passed (design I7)."""
    repo = commit_station_copy(tmp_path / "station")
    env = seam_environment(
        teax=simkit_root, license_key=os.environ["SYSIDE_LICENSE_KEY"], tmpdir=tmp_path / "tmp"
    )
    lineage = _lineage(repo)
    argv = integration_request(
        repo, tmp_path / "out", expected_teax_revision=git_head(simkit_root), **lineage
    )
    result = run_integrate(repo, argv, env)

    assert result.returncode == 0, result.stderr
    document = result.document
    assert (document["class"], document["exit_code"], document["blocker"]) == ("CANDIDATE", 0, None)
    assert [row["status"] for row in document["gates"]] == ["pass"] * 10
    assert document["candidate"] == {
        "package": "pkg/station_study",
        "manifest": "studies/manifest.json",
        "pin": manifest.load(repo / "studies" / "manifest.json").pinned_digest,
        "semantic_fingerprint": lineage["expected_semantic_fingerprint"],
        "executable_fingerprint": lineage["expected_executable_fingerprint"],
        "identity_document": "../out/package_identity.json",
        "baseline_result": "../out/baseline_result.json",
        "verification_summary": "../out/verification_summary.json",
    }
    assert_post_move_tool_identity(document)
    summary = json.loads((tmp_path / "out" / "verification_summary.json").read_text())
    assert summary["verdicts_rederived"] is True
