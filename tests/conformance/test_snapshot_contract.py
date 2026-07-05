"""Conformance tests for the promoted snapshot machinery (Item 2, SC-9 + SC-10).

Covers the format contract added when the snapshot loader/serializer/graph-rebuild
helpers were promoted from ``tests/helpers`` into ``sysml_codegen.snapshot``:

- INV-3: no second copy of the promoted helpers survives in the test tree.
- INV-2: a missing or mismatched ``snapshot_format_version`` is a hard error.
- INV-5: a re-captured expression-bearing snapshot carries ``compilation_results``.

Requirements: REQ-SNAP-08 through REQ-SNAP-14.
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

import pytest

from sysml_codegen.extraction.expression_compiler import CalcDefCompilationResult
from sysml_codegen.snapshot import SnapshotFormatError, load_extraction_snapshot
from tests.conftest import snapshot_fixture

REPO_ROOT = Path(__file__).resolve().parents[2]


# ===========================================================================
# REQ-SNAP-08 (INV-3): the promoted helpers live only in src, no second copy.
# ===========================================================================
@pytest.mark.req("REQ-SNAP-08")
def test_no_tests_helpers_snapshot_copies():
    """No file references ``tests.helpers.snapshot`` and the copies are deleted."""
    # Match the stale *import* form, not the bare token (so this test file's own
    # references in strings/docs do not self-trigger).
    out = subprocess.run(
        ["grep", "-rn", r"from tests\.helpers\.snapshot", "tests", "scripts", "src"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert out.stdout.strip() == "", f"stale tests.helpers.snapshot imports:\n{out.stdout}"
    assert not (REPO_ROOT / "tests/helpers/snapshot_loader.py").exists()
    assert not (REPO_ROOT / "tests/helpers/snapshot_serializer.py").exists()


# ===========================================================================
# REQ-SNAP-09 (INV-2): version guard runs first — missing/mismatched is a hard error.
# ===========================================================================
@pytest.mark.req("REQ-SNAP-09")
def test_missing_version_is_hard_error(tmp_path):
    """A snapshot with no snapshot_format_version raises before deserialization."""
    snap = tmp_path / "extraction_snapshot.json"
    snap.write_text(json.dumps({"model_name": "x", "calc_defs": []}))
    with pytest.raises(SnapshotFormatError, match="no snapshot_format_version"):
        load_extraction_snapshot(snap)


@pytest.mark.req("REQ-SNAP-09")
def test_wrong_version_is_hard_error(tmp_path):
    """A snapshot with a mismatched version raises with a recapture instruction."""
    snap = tmp_path / "extraction_snapshot.json"
    snap.write_text(json.dumps({"snapshot_format_version": 999, "model_name": "x"}))
    with pytest.raises(SnapshotFormatError, match="format version 999"):
        load_extraction_snapshot(snap)


# ===========================================================================
# REQ-SNAP-10 (INV-5): a re-captured expression-bearing snapshot carries
# compilation_results (SC-10 proving fixture: chain_spike_model).
# ===========================================================================
@pytest.mark.req("REQ-SNAP-10")
def test_chain_spike_compilation_results_nonempty():
    """chain_spike's compilation_results is a non-empty dict of typed results."""
    snap = load_extraction_snapshot(snapshot_fixture("chain_spike_model"))
    assert snap["compilation_results"], "chain_spike compilation_results is empty"
    assert all(
        isinstance(v, CalcDefCompilationResult)
        for v in snap["compilation_results"].values()
    )


# ===========================================================================
# REQ-SNAP-11 (V4): a version-current snapshot missing compilation_results
# degrades with a warning (does not crash).
# ===========================================================================
@pytest.mark.req("REQ-SNAP-11")
def test_missing_compilation_results_degrades(tmp_path, caplog):
    """Dropping the compilation_results section warns and degrades to {}."""
    raw = json.loads(snapshot_fixture("chain_spike_model").read_text())
    raw.pop("compilation_results")
    snap_path = tmp_path / "extraction_snapshot.json"
    snap_path.write_text(json.dumps(raw))

    with caplog.at_level(logging.WARNING):
        loaded = load_extraction_snapshot(snap_path)

    assert loaded["compilation_results"] == {}
    assert "no compilation_results section" in caplog.text


# ===========================================================================
# REQ-SNAP-12 (V3): a stale source hash warns and the run continues.
# ===========================================================================
@pytest.mark.req("REQ-SNAP-12")
def test_stale_source_hash_warns(tmp_path, caplog):
    """A calc_def whose on-disk source hash no longer matches warns (not raises)."""
    src = snapshot_fixture("chain_spike_model")
    raw = json.loads(src.read_text())
    # Copy the sources beside the tmp snapshot so re-absolutization resolves to a
    # real file, then poison one calc_def's stored hash to force a mismatch.
    model_dir = src.parent
    for name in ("library.sysml", "design.sysml"):
        (tmp_path / name).write_text((model_dir / name).read_text())
    raw["calc_defs"][0]["source_hash"] = "0" * 64
    snap_path = tmp_path / "extraction_snapshot.json"
    snap_path.write_text(json.dumps(raw))

    with caplog.at_level(logging.WARNING):
        loaded = load_extraction_snapshot(snap_path)

    assert loaded["stale_sources"], "expected a stale source to be recorded"
    assert "no longer matches on-disk source" in caplog.text
