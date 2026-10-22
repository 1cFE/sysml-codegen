"""Snapshots: ``check`` replays them as it checks live models (Item 2b).

Spec Success Criteria 5 and 6, design Validation 5 and 6.

- Every committed snapshot replays through ``check``. The generator outcome equals ``check``
  on the live sources wherever the sources are committed. ``catf_mfe_d5``'s are not (they are
  regenerated into an untracked folder), so its live comparison is not run here.
- Every 2a case that builds is captured on the fly and replayed: same outcome as live.
- ``generate --from-snapshot``'s bytes are held by the Phase 0 package manifest
  (``scripts/package_manifest.py``).
- A snapshot the loader refuses is refused by ``check`` with the record ``generate`` logs.

Licensed.
"""

from __future__ import annotations

import json
import sys
from functools import cache
from pathlib import Path

import pytest

from sysml_codegen import cli
from sysml_codegen.cli import CheckRequest, prepare, run_check
from tests.conformance.test_snapshot_v5_gate import _v5_extraction_payload
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers import refusal_records
from tests.helpers.refusal_cases import cases
from tests.helpers.refusal_cases.cases import GeneratorOutcome

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


def _sources(snapshot: Path) -> Path:
    return (
        snapshot.parent / "models" if snapshot.parent.name == "study_station" else snapshot.parent
    )


def _id(snapshot: Path) -> str:
    return snapshot.relative_to(FIXTURES_DIR).as_posix()


def _check(source: prepare.ModelSource) -> prepare.Prepared | prepare.Refused:
    return run_check(CheckRequest(source, "generated_code", None))


@cache
def _live_outcome(models: Path) -> tuple[str, ...] | None:
    return _outcome(_check(prepare.LiveModels((models,))))


def _outcome(checked: prepare.Prepared | prepare.Refused) -> tuple[str, ...] | None:
    """``None`` when the model builds, else the sorted refusal codes."""
    if isinstance(checked, prepare.Prepared):
        return None
    return tuple(sorted(item.code.value for item in checked.refusal.items))


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
def test_a_committed_snapshot_replays_as_its_live_sources(snapshot):
    checked = _check(prepare.SnapshotFile(snapshot))
    if snapshot not in NO_COMMITTED_SOURCES:
        assert _outcome(checked) == _live_outcome(_sources(snapshot))


@pytest.mark.parametrize("answer", BUILDS, ids=lambda a: a.case_id)
def test_a_building_case_captured_on_the_fly_replays_as_live(answer, tmp_path):
    from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot

    snapshot = capture_instance_graph_snapshot(
        [cases.model_root(answer)], tmp_path / "instance_graph_snapshot.json"
    )
    assert isinstance(_check(prepare.SnapshotFile(snapshot)), prepare.Prepared)
    assert _live_outcome(cases.model_root(answer)) is None


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
