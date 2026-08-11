"""Static absence and final public-surface proof for the Item-7 cutover."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import pytest

import sysml_codegen
import sysml_codegen.generation as generation
import sysml_codegen.generation.initialization as initialization
import sysml_codegen.orchestration as orchestration
import sysml_codegen.snapshot as snapshot
from sysml_codegen.orchestration.pipeline_context import (
    CodeGenerationError,
    PipelineContext,
    SysMLParsingError,
)

ROOT = Path(__file__).parents[2]
AGENTIC = ROOT.parent / "agentic-mbse"
INVENTORY = ROOT / ".project/active/elaborator-cutover/cutover-inventory.json"
RESIDUE = ROOT / "scripts/check_cutover_residue.py"

ORCHESTRATION_EXPORTS = {
    "CodeGenerationError",
    "PipelineContext",
    "SysMLParsingError",
    "build_pipeline_context",
    "build_pipeline_context_from_snapshot",
}
GENERATION_AUTHORITY_EXPORTS = {
    "CodeGenerationError",
    "PipelineContext",
    "SysMLParsingError",
}
SNAPSHOT_EXPORTS = {
    "SNAPSHOT_FORMAT_VERSION",
    "SnapshotCertifiabilityError",
    "SnapshotCompatibilityError",
    "SnapshotFormatError",
    "SnapshotIntegrityError",
    "SnapshotStaleSourceError",
    "capture_snapshot",
    "load_snapshot",
}
ROOT_AUTHORITY_NAMES = ORCHESTRATION_EXPORTS | SNAPSHOT_EXPORTS
OLD_CONTEXT_FIELDS = (
    "extractor",
    "calc_defs",
    "constraint_" "lowering_mode",
    "output_registry",
    "backtracker_result",
    "part_instance_index",
)


def _residue_result(rule: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(RESIDUE),
            "--repo",
            f"codegen={ROOT}",
            "--repo",
            f"agentic={AGENTIC}",
            "--inventory",
            str(INVENTORY),
            "--rule",
            rule,
            "--expect",
            "absent",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _assert_inventory_paths_match_final_worktree() -> None:
    document = json.loads(INVENTORY.read_text())
    assert document["schema"] == "cutover-inventory/v1"
    by_path: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in document["rows"]:
        if row["status"] == "existing":
            by_path[(row["repo"], row["path"])].append(row)

    roots = {"codegen": ROOT, "agentic": AGENTIC}
    for (repo, relative), rows in by_path.items():
        path = roots[repo] / relative
        expected_state = "present" if path.is_file() else "deleted"
        if expected_state == "deleted":
            assert {row["disposition"] for row in rows} <= {"delete", "migrate"}
        assert {row["worktree_state"] for row in rows} == {expected_state}


def test_closed_census_has_no_runtime_residue() -> None:
    _assert_inventory_paths_match_final_worktree()

    for rule in ("all", "item6-dual-2"):
        result = _residue_result(rule)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["hits"] == 0

    capture_name = "extraction_" + "snapshot.json"
    assert list((ROOT / "tests/fixtures").rglob(capture_name)) == []


def test_final_public_exports_match_the_allowlists() -> None:
    assert set(orchestration.__all__) == ORCHESTRATION_EXPORTS
    assert set(initialization.__all__) == GENERATION_AUTHORITY_EXPORTS
    assert set(snapshot.__all__) == SNAPSHOT_EXPORTS
    assert {
        name for name in ROOT_AUTHORITY_NAMES if hasattr(generation, name)
    } == GENERATION_AUTHORITY_EXPORTS
    assert not any(hasattr(sysml_codegen, name) for name in ROOT_AUTHORITY_NAMES)

    assert orchestration.PipelineContext is PipelineContext
    assert generation.PipelineContext is PipelineContext
    assert initialization.PipelineContext is PipelineContext
    assert orchestration.CodeGenerationError is CodeGenerationError
    assert generation.CodeGenerationError is CodeGenerationError
    assert initialization.CodeGenerationError is CodeGenerationError
    assert orchestration.SysMLParsingError is SysMLParsingError
    assert generation.SysMLParsingError is SysMLParsingError
    assert initialization.SysMLParsingError is SysMLParsingError


@pytest.mark.parametrize("field", OLD_CONTEXT_FIELDS)
def test_deleted_context_fields_cannot_be_constructed(field: str) -> None:
    with pytest.raises(TypeError):
        PipelineContext(**{field: object()})
