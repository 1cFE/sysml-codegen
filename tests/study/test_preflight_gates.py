"""The six checks pass on the station package, and the document says so completely.

Moved from fusion-tea ``tests/study/test_preflight_gates.py`` at ``b06585709`` and re-pointed at
the neutral station fixture. Preflight reads two documents the route writes at the baseline
point. The fixture commits them under ``studies/baseline/``, so this lane needs no teax. The
fixture is read in place, as its own project.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from sysml_codegen.study import roots
from tests.study.conftest import (
    REPO_ROOT,
    STATION,
    STATION_AXES,
    STATION_BASELINE,
    STATION_IDENTITY,
    STATION_MANIFEST,
    STATION_PACKAGE,
    environment_with_root,
)

PREFLIGHT = roots.TOOL_HOME / "sysml_codegen" / "study" / "preflight.py"

ALL_SIX = {
    "declared_keys",
    "sibling_scan",
    "identity",
    "manifest_currency",
    "baseline_headline",
    "package_clean",
}
#: A record's preflight section has five rows: the two fingerprint checks share one.
RECORD_ROWS = {
    "declared_keys": "Declared-group key validation",
    "sibling_scan": "Suffix-sibling scan (warnings only)",
    "identity": "Manifest / package fingerprint match",
    "manifest_currency": "Manifest / package fingerprint match",
    "baseline_headline": "Baseline gate against the pinned headline",
    "package_clean": "Package cleanliness",
}


def run_preflight(
    *argv: str, expect: int | None = None, cwd: Path = REPO_ROOT,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """``preflight`` as a subprocess, by default on the station read in place."""
    done = subprocess.run(
        [sys.executable, "-m", "sysml_codegen.study.preflight", *argv],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=environment_with_root(STATION) if env is None else env,
    )
    if expect is not None:
        assert done.returncode == expect, f"exit {done.returncode}\n{done.stderr}"
    return done


def gates_argv(
    results: Path,
    *,
    package: Path = STATION_PACKAGE,
    manifest: Path = STATION_MANIFEST,
    groups: Path = STATION_AXES,
    identity: Path = STATION_IDENTITY,
    baseline: Path = STATION_BASELINE,
) -> list[str]:
    return [
        "gates",
        "--package", str(package),
        "--manifest", str(manifest),
        "--groups", str(groups),
        "--identity", str(identity),
        "--baseline-result", str(baseline),
        "--out", str(results),
    ]


@pytest.fixture
def gates_document(tmp_path: Path) -> dict[str, Any]:
    results = tmp_path / "preflight_results.json"
    run_preflight(*gates_argv(results), expect=0)
    document: dict[str, Any] = json.loads(results.read_text())
    return document


def test_all_six_checks_pass_on_the_station_package(gates_document: dict[str, Any]) -> None:
    assert gates_document["outcome"] == "pass"
    assert {g["gate"] for g in gates_document["gates"]} == ALL_SIX
    assert all(g["status"] == "pass" for g in gates_document["gates"]), gates_document["gates"]


def test_the_results_document_validates_against_its_schema(
    gates_document: dict[str, Any], load_schema: Callable[[str], dict[str, Any]]
) -> None:
    jsonschema.validate(gates_document, load_schema("preflight_results.v1"))


def test_the_document_carries_a_digest_for_every_input_it_read(
    gates_document: dict[str, Any],
) -> None:
    assert set(gates_document["input_digests"]) == {
        "manifest",
        "axis_declaration",
        "identity_document",
        "baseline_result",
    }
    assert all(len(d) == 64 for d in gates_document["input_digests"].values())
    assert gates_document["inputs"] == {
        "package": "pkg/station_study",
        "manifest": "studies/manifest.json",
        "axis_declaration": "studies/axes.json",
        "identity_document": "studies/baseline/package_identity.json",
        "baseline_result": "studies/baseline/baseline_result.json",
    }


def test_the_six_results_map_onto_the_records_five_rows(gates_document: dict[str, Any]) -> None:
    """The two fingerprint checks share a row, and its detail carries both."""
    assert {RECORD_ROWS[g["gate"]] for g in gates_document["gates"]} == set(RECORD_ROWS.values())
    assert len(set(RECORD_ROWS.values())) == 5
    shared = [g for g in gates_document["gates"] if g["gate"] in ("identity", "manifest_currency")]
    assert len(shared) == 2 and all(g["detail"] for g in shared)


def test_the_tool_reports_its_own_revision_as_a_named_recipe_over_a_named_file_list(
    gates_document: dict[str, Any],
) -> None:
    digest = gates_document["tool"]["source_digest"]
    assert digest["recipe"] == "tool-source-digest/v1"
    assert [f["path"] for f in digest["files"]] == sorted(f["path"] for f in digest["files"])
    assert "sysml_codegen/study/preflight.py" in [f["path"] for f in digest["files"]]


def test_the_sibling_scan_is_advisory_and_can_never_fail(gates_document: dict[str, Any]) -> None:
    scan = next(g for g in gates_document["gates"] if g["gate"] == "sibling_scan")
    assert scan["status"] == "pass"


def test_the_identity_gate_reports_the_recomputed_digest(gates_document: dict[str, Any]) -> None:
    declared = json.loads(STATION_IDENTITY.read_text())["identity"]["digest"]
    gate = next(g for g in gates_document["gates"] if g["gate"] == "identity")
    assert declared in gate["detail"]


def test_the_clean_subcommand_gates_the_package_alone(tmp_path: Path) -> None:
    results = tmp_path / "clean.json"
    run_preflight("clean", "--package", str(STATION_PACKAGE), "--out", str(results), expect=0)
    document = json.loads(results.read_text())
    assert document["subcommand"] == "clean"
    assert [g["gate"] for g in document["gates"]] == ["package_clean"]
    assert document["outcome"] == "pass"


def test_preflight_imports_no_teax_and_no_adapter() -> None:
    """The strongest available form of "no teax import": the source names none of it."""
    text = PREFLIGHT.read_text()
    for needle in ("simkit", "era_adapter", "oracle_entry", "StudyRunner", "StudyQuery"):
        assert needle not in text
