"""Strict atomic v6 capture behavior."""

from __future__ import annotations

import hashlib

import pytest

import sysml_codegen.snapshot as snapshot
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

GOOD = FIXTURES_DIR / "source_identity_mixed_consumers"
BLOCKED = FIXTURES_DIR / "elab_fail_closed_probe"


def _digest(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_capture_returns_validated_destination_and_leaves_no_temporary_file(
    tmp_path,
) -> None:
    destination = tmp_path / "nested" / "case.json"
    assert snapshot.capture_snapshot([GOOD], destination) == destination
    assert snapshot.load_snapshot(destination)
    assert list(destination.parent.iterdir()) == [destination]


def test_capture_refusal_preserves_existing_destination_and_cleans_temporary_file(
    tmp_path,
) -> None:
    destination = tmp_path / "case.json"
    destination.write_bytes(b"sentinel-v5-owner-work")
    before = _digest(destination)

    with pytest.raises(Exception):
        snapshot.capture_snapshot([BLOCKED], destination)

    assert _digest(destination) == before
    assert destination.read_bytes() == b"sentinel-v5-owner-work"
    assert list(tmp_path.iterdir()) == [destination]


def test_capture_refusal_creates_no_destination(tmp_path) -> None:
    destination = tmp_path / "missing.json"
    with pytest.raises(Exception):
        snapshot.capture_snapshot([BLOCKED], destination)
    assert not destination.exists()
    assert not list(tmp_path.iterdir())
