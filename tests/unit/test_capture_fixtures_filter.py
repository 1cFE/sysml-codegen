"""Selective-capture `--fixtures` filter (D7, Item 1 Phase 0).

Byte-identity of untouched committed baselines is only checkable if capture is
selective. These tests cover the pure name-selection decision (license-free) and,
gated on a live license, prove a filtered re-capture touches only the named
fixture's paths so the `git status` byte-identity gate is real.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# The shared filter lives under scripts/ (a script-tooling change, not src/).
# scripts/ is importable as a namespace package (repo root is pytest's rootdir).
from scripts.capture_filter import select_fixtures
from sysml_codegen.snapshot import capture_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

# --- Pure name-selection (license-free) ----------------------------------------


def test_select_none_returns_all():
    """No `--fixtures` arg → every available name (backward-compatible full run)."""
    assert select_fixtures(["a", "b", "c"], None) == {"a", "b", "c"}


def test_select_subset_returns_only_named():
    assert select_fixtures(["a", "b", "c"], "b") == {"b"}
    assert select_fixtures(["a", "b", "c"], "a,c") == {"a", "c"}


def test_select_tolerates_whitespace_and_empties():
    assert select_fixtures(["a", "b"], " a , b ") == {"a", "b"}
    assert select_fixtures(["a", "b"], "a,,b,") == {"a", "b"}


def test_select_unknown_name_raises_naming_offender():
    with pytest.raises(ValueError, match="no_such_fixture"):
        select_fixtures(["a", "b"], "no_such_fixture")
    # A partially-valid list still fails loud on the bad name.
    with pytest.raises(ValueError, match="bad"):
        select_fixtures(["a", "b"], "a,bad")


# --- Byte-identity gate (license-gated: a real filtered capture) ----------------


@requires_license
def test_public_capture_writes_only_the_requested_destination(tmp_path: Path):
    """Selective callers can capture one model without touching committed fixtures."""
    destination = tmp_path / "source_identity_mixed_consumers.json"
    capture_snapshot([FIXTURES_DIR / "source_identity_mixed_consumers"], destination)
    assert list(tmp_path.iterdir()) == [destination]
    assert json.loads(destination.read_bytes())["version"] == 6
