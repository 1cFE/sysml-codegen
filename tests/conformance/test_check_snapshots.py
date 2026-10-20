"""Snapshots: ``check`` replays them without the screen, and capture is untouched (Item 2b).

Spec Success Criteria 5 and 6, design Validation 5 and 6.

- Every committed snapshot replays through ``check``. The screen is not assessed, for the
  snapshot reason, and the model is never ready. The generator outcome equals ``check`` on
  the live sources wherever the sources are committed. ``catf_mfe_d5``'s are not (they are
  regenerated into an untracked folder), so its live comparison is not run here.
- Every 2a case that builds is captured on the fly and replayed: same outcome as live.
- ``generate --from-snapshot`` reports the screen as not assessed for the same reason. Its
  bytes are held by the Phase 0 package manifest (``scripts/package_manifest.py``).
- A snapshot the loader refuses is refused by ``check`` with the record ``generate`` logs.
- ``sysml-codegen snapshot`` writes the same bytes with the screen patched to raise, and
  under profile skew in both directions.

Licensed.
"""

from __future__ import annotations

import json
import logging
import sys
from functools import cache
from pathlib import Path

import pytest
from agentic_mbse.sysml import subset_extraction, subset_profile

from sysml_codegen import cli, subset_profile_adapter
from sysml_codegen.cli import CheckRequest, prepare, readiness, run_check
from sysml_codegen.subset_screen import NotAssessedCause, ScreenNotAssessed
from tests.conformance.test_snapshot_v5_gate import _v5_extraction_payload
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers import refusal_records
from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.cases import GeneratorOutcome

pytestmark = requires_license

SNAPSHOTS = sorted(
    [
        *FIXTURES_DIR.glob("*/instance_graph_snapshot.json"),
        FIXTURES_DIR / "study_station" / "station.snapshot.json",
    ]
)
#: Snapshots whose source models are not committed.
NO_COMMITTED_SOURCES = {FIXTURES_DIR / "catf_mfe_d5" / "instance_graph_snapshot.json"}
BUILDS = [a for a in cases.all_answers() if a.generator.run.outcome is GeneratorOutcome.GENERATED]
#: A case the generator builds.
BUILDS_CASE = "anonymous-declaration__attribute_usage"
SNAPSHOT_SCREEN = ScreenNotAssessed(
    NotAssessedCause.SNAPSHOT_SOURCE, "snapshots do not carry the screen"
)


def _sources(snapshot: Path) -> Path:
    return (
        snapshot.parent / "models" if snapshot.parent.name == "study_station" else snapshot.parent
    )


def _id(snapshot: Path) -> str:
    return snapshot.relative_to(FIXTURES_DIR).as_posix()


def _check(source: prepare.ModelSource) -> readiness.ReadinessReport:
    return run_check(CheckRequest(source, "generated_code", None))


@cache
def _live_outcome(models: Path) -> tuple[str, ...] | None:
    return _outcome(_check(prepare.LiveModels((models,))))


def _outcome(report: readiness.ReadinessReport) -> tuple[str, ...] | None:
    """``None`` when the model builds, else the sorted refusal codes."""
    if isinstance(report.generator, prepare.Prepared):
        return None
    return readiness.generator_codes(report.generator)


def _main(monkeypatch: pytest.MonkeyPatch, *argv: str | Path) -> int:
    monkeypatch.setattr(sys, "argv", ["sysml-codegen", *map(str, argv)])
    with pytest.raises(SystemExit) as exit_info:
        cli.main()
    code = exit_info.value.code
    assert isinstance(code, int)
    return code


def test_there_are_23_committed_snapshots():
    assert len(SNAPSHOTS) == 23


@pytest.mark.parametrize("snapshot", SNAPSHOTS, ids=_id)
def test_a_committed_snapshot_replays_without_the_screen_and_is_never_ready(snapshot):
    report = _check(prepare.SnapshotFile(snapshot))
    assert report.screen == SNAPSHOT_SCREEN
    assert report.disagreement is None
    assert readiness.readiness(report).value is not readiness.Readiness.READY
    if snapshot not in NO_COMMITTED_SOURCES:
        assert _outcome(report) == _live_outcome(_sources(snapshot))


@pytest.mark.parametrize("answer", BUILDS, ids=lambda a: a.case_id)
def test_a_building_case_captured_on_the_fly_replays_as_live(answer, tmp_path):
    from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot

    snapshot = capture_instance_graph_snapshot(
        [cases.model_root(answer)], tmp_path / "instance_graph_snapshot.json"
    )
    report = _check(prepare.SnapshotFile(snapshot))
    assert isinstance(report.generator, prepare.Prepared)
    assert report.screen == SNAPSHOT_SCREEN
    assert readiness.readiness(report).value is readiness.Readiness.NOT_READY
    assert _live_outcome(cases.model_root(answer)) is None


def test_generate_from_a_snapshot_reports_the_screen_not_assessed(monkeypatch, tmp_path, caplog):
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    snapshot = FIXTURES_DIR / "sample_model" / "instance_graph_snapshot.json"
    output = tmp_path / "pkg"
    assert _main(monkeypatch, "generate", "--from-snapshot", snapshot, "-o", output) == 0
    infos = [r.getMessage() for r in caplog.records if r.levelno == logging.INFO]
    assert "Screen not assessed: snapshots do not carry the screen" in infos
    assert "  - the source is a snapshot, and a snapshot is never ready" in infos


def test_check_refuses_a_snapshot_the_loader_refuses_with_generate_s_record(monkeypatch, tmp_path):
    snapshot = tmp_path / "extraction_snapshot.json"
    snapshot.write_text(json.dumps(_v5_extraction_payload()))
    output = tmp_path / "pkg"
    with refusal_records.capture_refusals(output) as generated:
        assert _main(monkeypatch, "generate", "--from-snapshot", snapshot, "-o", output) == 1
    with refusal_records.capture_refusals(output) as checked:
        assert _main(monkeypatch, "check", "--from-snapshot", snapshot, "-o", output) == 1
    assert len(generated) == 1
    assert "v5 extraction snapshot" in generated[0]["message"]
    assert checked == generated


def _raising(*_args: object, **_kwargs: object) -> None:
    raise RuntimeError("probe: the screen broke")


SCREEN_FAULTS = {
    "extract_subset_facts raises": (subset_extraction, "extract_subset_facts", _raising),
    "evaluate_subset_profile raises": (subset_profile, "evaluate_subset_profile", _raising),
    "render_finding raises": (subset_profile_adapter, "render_finding", _raising),
    "installed profile older": (subset_profile, "SUBSET_PROFILE_VERSION", "subset-profile/v1"),
    "installed profile newer": (subset_profile, "SUBSET_PROFILE_VERSION", "subset-profile/v3"),
}


@pytest.mark.parametrize("fault", sorted(SCREEN_FAULTS))
def test_snapshot_capture_writes_the_same_bytes_whatever_the_screen_does(
    fault, monkeypatch, tmp_path
):
    models = cases.model_root(cases.load_answer(BUILDS_CASE))
    plain = tmp_path / "plain.json"
    assert _main(monkeypatch, "snapshot", "--models", models, "-o", plain) == 0
    module, name, value = SCREEN_FAULTS[fault]
    monkeypatch.setattr(module, name, value)
    faulted = tmp_path / "faulted.json"
    assert _main(monkeypatch, "snapshot", "--models", models, "-o", faulted) == 0
    assert faulted.read_bytes() == plain.read_bytes()
