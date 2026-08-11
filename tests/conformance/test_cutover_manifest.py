"""The accepted batch is exactly the approved B37 ledger."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.capture_extraction_snapshots import (
    load_approved_manifest,
    validate_candidate_record,
)
from sysml_codegen.elaboration import InstanceGraph
from sysml_codegen.orchestration import pipeline_builder

ROOT = Path(__file__).parents[2]
CENSUS = ROOT / ".project/active/elaborator-cutover/cutover-census.md"


def _candidate() -> dict[str, object]:
    manifest = load_approved_manifest(CENSUS)
    rows = [row.expected_record() for row in manifest]
    return {
        "rows": rows,
        "counts": {"v6": 14, "refusal": 22, "control": 1},
        "semantic_diffs": {
            "classified": [row["id"] for row in rows],
            "unclassified": [],
        },
        "v5_artifacts": [],
    }


def test_manifest_has_exact_37_paths_and_allowed_outcomes() -> None:
    manifest = load_approved_manifest(CENSUS)

    assert [row.id for row in manifest] == [f"B37-{index:02d}" for index in range(1, 38)]
    assert len({row.fixture for row in manifest}) == 37
    assert [row.outcome for row in manifest].count("v6") == 14
    assert [row.outcome for row in manifest].count("refusal") == 22
    assert [row.outcome for row in manifest].count("control") == 1
    validate_candidate_record(_candidate(), manifest)


@pytest.mark.parametrize("missing_id", ["B37-01", "B37-15", "B37-37"])
def test_manifest_validator_rejects_a_wrong_count(missing_id: str) -> None:
    manifest = load_approved_manifest(CENSUS)
    candidate = _candidate()
    candidate["rows"] = [row for row in candidate["rows"] if row["id"] != missing_id]

    with pytest.raises(ValueError, match="exactly 37"):
        validate_candidate_record(candidate, manifest)


def test_manifest_validator_rejects_unexpected_artifact_on_refusal() -> None:
    manifest = load_approved_manifest(CENSUS)
    candidate = _candidate()
    row = next(row for row in candidate["rows"] if row["id"] == "B37-02")
    row["artifact"] = "snapshots/B37-02.json"

    with pytest.raises(ValueError, match="unexpected artifact"):
        validate_candidate_record(candidate, manifest)


def test_manifest_validator_rejects_an_unclassified_diff() -> None:
    manifest = load_approved_manifest(CENSUS)
    candidate = _candidate()
    candidate["semantic_diffs"]["unclassified"] = ["B37-04"]

    with pytest.raises(ValueError, match="unclassified"):
        validate_candidate_record(candidate, manifest)


def test_definition_only_model_remains_a_valid_empty_v6_control(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Extractor:
        model = object()
        diagnostics = SimpleNamespace(validation=[])

        def __init__(self, _paths: list[Path]) -> None:
            pass

        def load_models(self) -> bool:
            return True

        def extract_calculation_definitions(self) -> list[object]:
            return [object()]

    admission = SimpleNamespace(
        staged_files=(),
        files=(),
        staged_to_referent={},
        verify_after_parse=lambda _model: None,
    )
    monkeypatch.setattr(pipeline_builder, "SysMLDataExtractor", Extractor)
    monkeypatch.setattr(pipeline_builder, "elaborate", lambda *_args, **_kwargs: InstanceGraph())

    assert pipeline_builder._load_and_elaborate(admission) == InstanceGraph()
