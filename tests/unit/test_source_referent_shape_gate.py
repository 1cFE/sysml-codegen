"""Item 5 v5 shape gate: a source_file that is not a portable referent is rejected.

Closes Item 4 note N1: a version bump alone is not enough — the loader must reject a
field-less or absolute source_file loudly, in both skew directions, rather than load it
silently and reintroduce the checkout-absolute leak.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sysml_codegen.snapshot import SNAPSHOT_FORMAT_VERSION, SnapshotFormatError
from sysml_codegen.snapshot.loader import load_extraction_snapshot
from tests.conftest import FIXTURES_DIR

_SNAPSHOT = FIXTURES_DIR / "sample_model/extraction_snapshot.json"


def _write_mutated(tmp_path: Path, mutate) -> Path:
    raw = json.loads(_SNAPSHOT.read_text())
    mutate(raw)
    out = tmp_path / "extraction_snapshot.json"
    out.write_text(json.dumps(raw, indent=2))
    return out


def test_committed_v5_snapshot_loads_clean(tmp_path: Path) -> None:
    """The committed v5 snapshot passes the gate (referent source_file everywhere)."""
    raw = json.loads(_SNAPSHOT.read_text())
    assert raw["snapshot_format_version"] == SNAPSHOT_FORMAT_VERSION == 5
    assert load_extraction_snapshot(_SNAPSHOT)["calc_defs"]


def test_absolute_source_file_rejected(tmp_path: Path) -> None:
    """Skew A — an absolute source_file (the pre-v5 leak form) is rejected loudly."""

    def mutate(raw: dict) -> None:
        raw["calc_defs"][0]["source_file"] = "/home/someone/checkout/library/geometry.sysml"

    snapshot = _write_mutated(tmp_path, mutate)
    with pytest.raises(SnapshotFormatError, match="portable"):
        load_extraction_snapshot(snapshot)


def test_snapshot_dir_relative_source_file_rejected(tmp_path: Path) -> None:
    """Skew B — a bare snapshot-dir-relative path (Branch B's form) is rejected.

    This is the exact value a silent v4-style edit would have let through: it looks
    portable but is not the certified root-N/ referent, so the gate rejects it.
    """

    def mutate(raw: dict) -> None:
        raw["calc_defs"][0]["source_file"] = "library/geometry.sysml"

    snapshot = _write_mutated(tmp_path, mutate)
    with pytest.raises(SnapshotFormatError, match="portable"):
        load_extraction_snapshot(snapshot)


def test_stale_version_rejected(tmp_path: Path) -> None:
    """The version gate rejects a stale (pre-v5) snapshot before any field is read."""

    def mutate(raw: dict) -> None:
        raw["snapshot_format_version"] = 4

    snapshot = _write_mutated(tmp_path, mutate)
    with pytest.raises(SnapshotFormatError, match="version"):
        load_extraction_snapshot(snapshot)
