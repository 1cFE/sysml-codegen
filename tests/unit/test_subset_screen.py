"""``assess_screen`` answers without a license where it never reaches SysIDE (Item 2b D2, D10).

A skewed profile is decided before the adapter is imported, and a snapshot or failed load
is reported without running the screen. The live screen is tested in
``tests/conformance/subset_profile/test_assess_screen.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from agentic_mbse.sysml import subset_profile

from sysml_codegen._upstream_pins import SUBSET_PROFILE_VERSION
from sysml_codegen.cli.prepare import SnapshotFile
from sysml_codegen.core.errors import SysMLParsingError
from sysml_codegen.orchestration.elaborated_pipeline import FailedLoad, LiveLoad, LoadFailureKind
from sysml_codegen.subset_screen import NotAssessedCause, ScreenNotAssessed, assess_screen

ADAPTER = "sysml_codegen.subset_profile_adapter"


def _shifted(version: str, offset: int) -> str:
    """``subset-profile/vN`` with N moved by ``offset``: an older or a newer profile."""
    prefix, number = version.rsplit("v", 1)
    return f"{prefix}v{int(number) + offset}"


def _unloaded_live_load() -> LiveLoad:
    """A live load the skew check returns before reading: it never touches the extractor."""
    return LiveLoad(extractor=None, model_paths=(), source_referents={})  # type: ignore[arg-type]


@pytest.mark.parametrize("offset", [-1, +1], ids=["older", "newer"])
def test_skew_is_not_assessed_and_the_adapter_is_not_imported(monkeypatch, offset):
    monkeypatch.delitem(sys.modules, ADAPTER, raising=False)
    installed = _shifted(SUBSET_PROFILE_VERSION, offset)
    monkeypatch.setattr(subset_profile, "SUBSET_PROFILE_VERSION", installed)
    result = assess_screen(_unloaded_live_load())
    assert isinstance(result, ScreenNotAssessed)
    assert result.cause is NotAssessedCause.PROFILE_SKEW
    assert SUBSET_PROFILE_VERSION in result.reason and installed in result.reason
    assert ADAPTER not in sys.modules


def test_a_snapshot_source_is_not_assessed():
    result = assess_screen(SnapshotFile(Path("instance_graph_snapshot.json")))
    assert result == ScreenNotAssessed(
        NotAssessedCause.SNAPSHOT_SOURCE, "snapshots do not carry the screen"
    )


@pytest.mark.parametrize(
    ("kind", "cause", "reason"),
    [
        (LoadFailureKind.PARSE_ERRORS, NotAssessedCause.PARSE_ERRORS, "the model has parse errors"),
        (LoadFailureKind.NOT_LOADED, NotAssessedCause.NOT_LOADED, "the model did not load"),
    ],
)
def test_a_failed_load_is_not_assessed(kind, cause, reason):
    loaded = FailedLoad(kind, SysMLParsingError("probe"))
    assert assess_screen(loaded) == ScreenNotAssessed(cause, reason)


def test_a_screen_that_cannot_run_is_not_assessed():
    """The stand-in has no model, so extraction raises; the screen reports, never raises."""
    result = assess_screen(_unloaded_live_load())
    assert isinstance(result, ScreenNotAssessed)
    assert result.cause is NotAssessedCause.SCREEN_FAILED
    assert result.reason.startswith("the screen failed: AttributeError:")


def test_a_path_the_load_does_not_hold_keeps_its_raw_string():
    from sysml_codegen.subset_screen import _referent

    referents = {"/models/a.sysml": "root-0/a.sysml"}
    assert _referent("///models/a.sysml", referents) == "root-0/a.sysml"
    assert _referent("/elsewhere/b.sysml", referents) == "/elsewhere/b.sysml"
    assert _referent(None, referents) is None
