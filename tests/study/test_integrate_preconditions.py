"""Gate 0: the seam decides every precondition before it invokes any producer.

Moved from fusion-tea ``tests/study/test_integrate_preconditions.py`` at ``b06585709`` and
re-pointed at the station, copied into a fresh git repository, with a stub ``simkit`` for teax
and a dummy licence value: gate 0 runs no producer, so nothing here needs either for real.
Every artifact the seam writes lands under ``tmp_path``.

The one that matters most is the variable sweep. A repo gate may read a declared variable
inside its *test body*, so an absence lands as a junit ``<failure>`` and would be reported as
a toolchain refusal by any seam that let the gate run first. That misreport is the failure
these tests exist to make impossible.

The two simkit-probe tests that need teax are in ``tests/execution/test_study_integrate.py``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from sysml_codegen.study import integrate, roots
from sysml_codegen.study.declarations import load_declaration
from tests.study.conftest import (
    STATION,
    commit_stub_simkit,
    integration_request,
    run_integrate,
    seam_environment,
)

DUMMY_LICENSE = "dummy-licence-gate-zero-only-checks-presence"


@pytest.fixture
def stub_teax(tmp_path: Path) -> Path:
    return commit_stub_simkit(tmp_path / "stub-teax")


def full_env(stub_teax: Path, tmp_path: Path) -> dict[str, str]:
    """Everything gate 0 sweeps, exported, so a test can remove one variable from it."""
    return seam_environment(teax=stub_teax, license_key=DUMMY_LICENSE, tmpdir=tmp_path / "tmp")


def drop_flag(argv: list[str], flag: str) -> list[str]:
    index = argv.index(flag)
    return argv[:index] + argv[index + 2:]


@pytest.mark.parametrize(
    "missing", [*integrate.REQUIRED_ENV, *load_declaration(STATION).environment]
)
def test_each_env_var_unset_refuses_at_gate_zero(
    station_repo: Path, stub_teax: Path, tmp_path: Path, missing: str
) -> None:
    env = {name: value for name, value in full_env(stub_teax, tmp_path).items() if name != missing}
    result = run_integrate(station_repo, integration_request(station_repo, tmp_path / "out"), env)
    assert result.returncode == 1
    document = result.document
    assert document["class"] == "BLOCKER"
    blocker = document["blocker"]
    assert blocker["gate"] == "preconditions"
    assert blocker["mode"] == "could_not_run"
    assert blocker["condition"] == "env-missing"
    assert missing in blocker["detail"]
    assert [gate["status"] for gate in document["gates"]] == ["not reached"] * 10


def test_missing_required_input_is_a_blocker_not_a_usage_error(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    argv = drop_flag(integration_request(station_repo, tmp_path / "out"), "--manifest")
    result = run_integrate(station_repo, argv, full_env(stub_teax, tmp_path))
    assert result.returncode == 1, "a missing input must never be argparse's exit 2"
    assert result.document["blocker"]["condition"] == "input-missing"
    assert "--manifest" in result.document["blocker"]["detail"]


def test_out_dir_inside_package_root_is_input_invalid(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    out_dir = station_repo / "pkg" / "station_study" / "out"
    result = run_integrate(
        station_repo, integration_request(station_repo, out_dir), full_env(stub_teax, tmp_path)
    )
    assert result.returncode == 1
    assert result.document["blocker"]["condition"] == "input-invalid"
    assert not out_dir.exists(), "the seam wrote into the package it was refusing to touch"


def test_two_packages_are_ambiguous_lineage_not_a_last_one_wins(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    argv = [*integration_request(station_repo, tmp_path / "out"),
            "--package", str(station_repo / "models")]
    result = run_integrate(station_repo, argv, full_env(stub_teax, tmp_path))
    assert result.document["blocker"]["condition"] == "input-invalid"
    assert "exactly one package" in result.document["blocker"]["detail"]


def test_audited_work_must_carry_its_commit(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    argv = integration_request(station_repo, tmp_path / "out", audited_work="models")
    result = run_integrate(station_repo, argv, full_env(stub_teax, tmp_path))
    assert result.document["blocker"]["condition"] == "input-invalid"
    assert "PATH@COMMIT" in result.document["blocker"]["detail"]


def test_the_return_document_is_complete_on_every_exit_path(
    station_repo: Path, stub_teax: Path, tmp_path: Path
) -> None:
    argv = drop_flag(integration_request(station_repo, tmp_path / "out"), "--groups")
    document = run_integrate(station_repo, argv, full_env(stub_teax, tmp_path)).document
    assert document["schema_version"] == "integration-seam-return/v1"
    assert document["tool"]["path"] == "sysml_codegen/study/integrate.py"
    assert document["tool"]["source_digest"]["recipe"] == "tool-source-digest/v1"
    assert document["command"][0] == "sysml_codegen/study/integrate.py"
    assert document["candidate"] is None
    assert document["exit_code"] == 1
    assert set(document["toolchain"]) == {
        "agentic_mbse",
        "sysml_codegen",
        "teax_revision",
        "teax_module_path",
    }
    assert [gate["gate"] for gate in document["gates"]] == [g.name for g in integrate.GATES]
    assert all(gate["scope"] in ("repo", "request") for gate in document["gates"])


def test_the_condition_slug_set_is_closed() -> None:
    """A slug the guide does not enumerate cannot reach a caller: the constructor refuses."""
    with pytest.raises(ValueError, match="closed set"):
        integrate.SeamBlocker(
            gate="preconditions",
            producer="sysml_codegen/study/integrate.py",
            scope="request",
            mode="could_not_run",
            condition="not-a-real-slug",
            detail="",
        )


# ------------------------------------------------- the de-risk (design.md, Next-Stage)


def independently_can_import_simkit(env: dict[str, str]) -> bool:
    """What a ``verify.py`` subprocess under ``env`` actually does, built without the seam.

    ``verify.build_summary`` opens with a bare ``import simkit``; this is that import, in
    a fresh interpreter, reached the same way the producer reaches it.
    """
    done = subprocess.run(
        [sys.executable, "-c", "import simkit"],
        capture_output=True,
        text=True,
        cwd=str(STATION),
        env=env,
    )
    return done.returncode == 0


def test_simkit_probe_refuses_without_the_teax_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """Absence requires removing both the explicit simkit root and inherited import paths."""
    monkeypatch.setenv(roots.PROJECT_ROOT_ENV, str(STATION))
    monkeypatch.delenv(roots.TEAX_SIMKIT_PATH, raising=False)
    monkeypatch.delenv("PYTHONPATH", raising=False)
    env = integrate.seam_env()
    assert integrate.simkit_module_path(env) is None
    assert independently_can_import_simkit(env) is False
