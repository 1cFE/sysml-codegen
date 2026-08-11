"""Capture writes one complete v6 snapshot or nothing at all."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from sysml_codegen.elaboration.elaborate import ElaborationDiagnosticError
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

GOOD = FIXTURES_DIR / "source_identity_mixed_consumers"
BLOCKED = FIXTURES_DIR / "elab_fail_closed_probe"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_capture_returns_a_loadable_destination_and_leaves_no_temporary_file(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "nested" / "case.json"
    assert capture_instance_graph_snapshot([GOOD], destination) == destination
    assert load_instance_graph_snapshot(destination)
    assert list(destination.parent.iterdir()) == [destination]


def test_a_refused_capture_leaves_an_existing_snapshot_untouched(tmp_path: Path) -> None:
    destination = tmp_path / "case.json"
    destination.write_bytes(b"sentinel-owner-work")
    before = _digest(destination)

    with pytest.raises(Exception):
        capture_instance_graph_snapshot([BLOCKED], destination)

    assert _digest(destination) == before
    assert list(tmp_path.iterdir()) == [destination]


def test_a_refused_capture_creates_no_destination(tmp_path: Path) -> None:
    destination = tmp_path / "missing.json"
    with pytest.raises(Exception):
        capture_instance_graph_snapshot([BLOCKED], destination)
    assert not destination.exists()
    assert not list(tmp_path.iterdir())


def test_capture_refuses_a_model_that_does_not_elaborate_cleanly(tmp_path: Path) -> None:
    """A snapshot may only seal a projectable, diagnostic-free graph.

    The probe models an alias cycle and an unsupported formula, so elaboration
    itself refuses; capture never reaches the sealing step.
    """
    with pytest.raises(ElaborationDiagnosticError):
        capture_instance_graph_snapshot([BLOCKED], tmp_path / "blocked.json")
