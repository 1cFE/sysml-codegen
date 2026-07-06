"""Selective-capture `--fixtures` filter (D7, Item 1 Phase 0).

Byte-identity of untouched committed baselines is only checkable if capture is
selective. These tests cover the pure name-selection decision (license-free) and,
gated on a live license, prove a filtered re-capture touches only the named
fixture's paths so the `git status` byte-identity gate is real.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

# The shared filter lives under scripts/ (a script-tooling change, not src/).
# scripts/ is importable as a namespace package (repo root is pytest's rootdir).
from scripts.capture_filter import select_fixtures
from tests.conftest import REPO_ROOT, requires_license

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


# --- Script-level fail-loud on unknown name (license-free: validation precedes
#     any model load, so no syside license is needed to exercise it) -------------


@pytest.mark.parametrize(
    "script",
    ["capture_extraction_snapshots.py", "capture_pipeline_baselines.py"],
)
def test_unknown_fixture_name_errors(script: str):
    result = subprocess.run(
        [sys.executable, f"scripts/{script}", "--fixtures", "no_such_fixture"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert result.returncode != 0
    assert "no_such_fixture" in result.stderr


# --- Byte-identity gate (license-gated: a real filtered capture) ----------------


def _git_changed_paths() -> list[str]:
    out = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=True,
    ).stdout
    # porcelain lines are "XY path"; the path starts at column 3.
    return [line[3:] for line in out.splitlines() if line.strip()]


@requires_license
def test_extraction_filter_touches_only_named():
    """A `--fixtures sample_model` re-capture leaves every OTHER committed snapshot
    byte-identical — `git status` names only sample_model paths (or none).

    This is the checkable property Phase 2's byte-identity gate relies on.
    """
    before = set(_git_changed_paths())
    subprocess.run(
        [sys.executable, "scripts/capture_extraction_snapshots.py",
         "--fixtures", "sample_model"],
        check=True,
        cwd=REPO_ROOT,
    )
    try:
        newly_changed = set(_git_changed_paths()) - before
        assert all("sample_model" in p for p in newly_changed), newly_changed
    finally:
        # Restore any re-captured bytes so the test is side-effect-free.
        subprocess.run(
            ["git", "checkout", "--",
             "tests/fixtures/sample_model/extraction_snapshot.json"],
            cwd=REPO_ROOT,
            check=False,
        )
