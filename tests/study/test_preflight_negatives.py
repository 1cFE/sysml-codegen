"""Each negative fails closed, names the fault, and still writes a complete document.

Moved from fusion-tea ``tests/study/test_preflight_negatives.py`` at ``b06585709`` and re-pointed
at the neutral station fixture. Each case is a refusal ``preflight``'s module docstring
documents (``sysml_codegen/study/preflight.py:9-37``), and each test names its line.

The rule under test is as much the document as the checks: a failed check is recorded as
``fail`` with its detail, every other check still carries its real outcome, and the process
exits non-zero (``preflight.py:29-34``). Writing nothing on failure would make a record's
preflight section fillable only by hand from stderr, and would lose the outcome of every check
after the failing one.

The committed fixture is never written. Most negatives mutate copies of the documents
preflight reads, in ``tmp_path``. The dirty-tree case needs a tree git can see, so it runs on
the fixture copied into a fresh git repository.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from tests.study.conftest import STATION_AXES, STATION_BASELINE, STATION_IDENTITY, STATION_MANIFEST
from tests.study.test_preflight_gates import ALL_SIX, gates_argv, run_preflight

P = "PumpStation__station__"
ANNUAL_COST = P + "pumping__annual_cost"

Overrides = dict[str, Path]


def _copy_json(source: Path, dest: Path, mutate: Callable[[Any], object]) -> Path:
    data = json.loads(source.read_text())
    mutate(data)
    dest.write_text(json.dumps(data, indent=2) + "\n")
    return dest


def remove_declared_key(tmp_path: Path) -> tuple[Overrides, str, str]:
    """A declared key no package input defines (``preflight.py:11``)."""
    absent = f"{P}no_such_axis_key"
    path = _copy_json(
        STATION_AXES, tmp_path / "axes.json",
        lambda d: d["groups"][0]["keys"].append({"key": absent, "provenance": "fan_out"}),
    )
    return {"groups": path}, "declared_keys", absent


def point_key_at_a_channel(tmp_path: Path) -> tuple[Overrides, str, str]:
    """A declared key that names a produced channel, a computed quantity rather than an
    input (``preflight.py:11-13``)."""
    path = _copy_json(
        STATION_AXES, tmp_path / "axes.json",
        lambda d: d["groups"][0]["keys"].append({"key": ANNUAL_COST, "provenance": "fan_out"}),
    )
    return {"groups": path}, "declared_keys", "computed quantity"


def corrupt_the_identity(tmp_path: Path) -> tuple[Overrides, str, str]:
    """An identity document that does not recompute (``preflight.py:17``)."""
    path = _copy_json(
        STATION_IDENTITY, tmp_path / "package_identity.json",
        lambda d: d["identity"].update(digest="0" * 64),
    )
    return {"identity": path}, "identity", "recomputed"


def stale_the_manifest(tmp_path: Path) -> tuple[Overrides, str, str]:
    """A manifest pinned against another package generation (``preflight.py:19-22``)."""
    path = _copy_json(
        STATION_MANIFEST, tmp_path / "manifest.json",
        lambda d: d["fingerprints"]["recorded_provenance"].update(semantic_fingerprint="0" * 64),
    )
    return {"manifest": path}, "manifest_currency", "semantic_fingerprint"


NEGATIVES: dict[str, Callable[[Path], tuple[Overrides, str, str]]] = {
    "missing_declared_key": remove_declared_key,
    "key_names_a_channel": point_key_at_a_channel,
    "wrong_fingerprint": corrupt_the_identity,
    "stale_manifest": stale_the_manifest,
}


def _gate(results: Path, name: str) -> dict[str, Any]:
    gate: dict[str, Any] = next(
        g for g in json.loads(results.read_text())["gates"] if g["gate"] == name
    )
    return gate


@pytest.mark.parametrize("case", sorted(NEGATIVES))
def test_each_negative_fails_closed_and_still_writes_a_complete_document(
    case: str, tmp_path: Path
) -> None:
    overrides, gate, needle = NEGATIVES[case](tmp_path)
    results = tmp_path / "preflight_results.json"
    done = run_preflight(*gates_argv(results, **overrides))

    assert done.returncode != 0, "a refused gate must exit non-zero"
    document = json.loads(results.read_text())
    assert {g["gate"] for g in document["gates"]} == ALL_SIX, "complete, not torn"
    assert document["outcome"] == "fail"

    failing = next(g for g in document["gates"] if g["gate"] == gate)
    assert failing["status"] == "fail"
    assert needle in failing["detail"], failing["detail"]

    # Every other check carried its real outcome rather than being abandoned.
    others = [g for g in document["gates"] if g["gate"] != gate]
    assert all(g["status"] in ("pass", "fail") for g in others)
    assert any(g["status"] == "pass" for g in others)


def test_the_wrong_fingerprint_message_names_both_values(tmp_path: Path) -> None:
    """``preflight.py:17``: recomputed rather than trusted, and the refusal says both."""
    overrides, _, _ = corrupt_the_identity(tmp_path)
    declared = json.loads(STATION_IDENTITY.read_text())["identity"]["digest"]
    results = tmp_path / "preflight_results.json"
    run_preflight(*gates_argv(results, **overrides))
    detail = _gate(results, "identity")["detail"]
    assert "0" * 64 in detail and declared in detail


def test_an_unreadable_input_is_did_not_run_with_its_condition(tmp_path: Path) -> None:
    """A gate that never got the chance must not look like a gate that refused
    (``preflight.py:30-31``)."""
    broken = tmp_path / "package_identity.json"
    broken.write_text("{not json")
    results = tmp_path / "preflight_results.json"
    done = run_preflight(*gates_argv(results, identity=broken))
    assert done.returncode != 0
    document = json.loads(results.read_text())
    gate = next(g for g in document["gates"] if g["gate"] == "identity")
    assert gate["status"] == "did not run"
    assert "not valid JSON" in gate["detail"]
    assert "identity_document" not in document["input_digests"]
    # The checks that did not depend on it still ran.
    assert _gate(results, "manifest_currency")["status"] == "pass"


def test_a_baseline_executed_under_another_identity_is_refused(tmp_path: Path) -> None:
    """The identity gated and the identity executed are one value (``preflight.py:17-18``)."""
    baseline = _copy_json(
        STATION_BASELINE, tmp_path / "baseline_result.json",
        lambda d: d["executed_under"].update(identity_digest="0" * 64),
    )
    results = tmp_path / "preflight_results.json"
    done = run_preflight(*gates_argv(results, baseline=baseline))
    assert done.returncode != 0
    gate = _gate(results, "identity")
    assert gate["status"] == "fail"
    assert "different identity" in gate["detail"]


def test_a_wrong_headline_is_refused_naming_the_channel(tmp_path: Path) -> None:
    """The executed point must reproduce the pinned headline (``preflight.py:23-24``)."""
    baseline = _copy_json(
        STATION_BASELINE, tmp_path / "baseline_result.json",
        lambda d: d["channels"].update({ANNUAL_COST: 999.0}),
    )
    results = tmp_path / "preflight_results.json"
    run_preflight(*gates_argv(results, baseline=baseline))
    gate = _gate(results, "baseline_headline")
    assert gate["status"] == "fail"
    assert ANNUAL_COST in gate["detail"] and "999.0" in gate["detail"]


def test_a_differing_baseline_verdict_is_refused_naming_the_constraint(tmp_path: Path) -> None:
    """The executed verdicts must equal the pinned ones (``preflight.py:23-24``)."""

    def flip(data: dict[str, Any]) -> None:
        data["verdicts"][0]["status"] = "violated"

    baseline = _copy_json(STATION_BASELINE, tmp_path / "baseline_result.json", flip)
    name = json.loads(baseline.read_text())["verdicts"][0]["source_local_identity"]
    results = tmp_path / "preflight_results.json"
    run_preflight(*gates_argv(results, baseline=baseline))
    gate = _gate(results, "baseline_headline")
    assert gate["status"] == "fail"
    assert name in gate["detail"] and "violated" in gate["detail"]


def test_a_dirty_tree_is_refused_naming_the_file(station_repo: Path, tmp_path: Path) -> None:
    """The cleanliness gate must see a tree git can see, and name what it found there
    (``preflight.py:25-27``). Run from inside the copy, whose work tree is the project root;
    every study test runs with the root variable unset."""
    package = station_repo / "pkg" / "station_study"
    results = tmp_path / "clean.json"
    clean = ("clean", "--package", str(package), "--out", str(results))
    run_preflight(*clean, cwd=station_repo, env=dict(os.environ), expect=0)

    (package / "left_behind.txt").write_text("a file a run left behind\n")
    done = run_preflight(*clean, cwd=station_repo, env=dict(os.environ))
    assert done.returncode != 0
    document = json.loads(results.read_text())
    assert document["outcome"] == "fail"
    gate = document["gates"][0]
    assert gate["gate"] == "package_clean" and gate["status"] == "fail"
    assert "pkg/station_study/left_behind.txt" in gate["detail"]
