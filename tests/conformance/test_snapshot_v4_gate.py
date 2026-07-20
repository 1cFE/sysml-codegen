"""The v4 envelope gate: fail closed both directions, before any semantic use.

DD-A06, DD-A20. `SNAPSHOT_FORMAT_VERSION` advanced 3 -> 4 alongside
`constraint-facts/v2`, because leaving the envelope at 3 while its embedded facts
changed meaning would let one version describe two payloads (DD-R12).

No migration and no grandfathering path is added: a retained v3 snapshot fails with
the existing recapture message and produces no partial context (DD-R15 — Item 12 owns
closing the `grandfathered_off` fail-open path, and this item must not pre-empt it).
"""

from __future__ import annotations

import json

import pytest

from sysml_codegen.orchestration.snapshot_context import build_pipeline_context_from_snapshot
from sysml_codegen.snapshot import SNAPSHOT_FORMAT_VERSION, SnapshotFormatError
from tests.conftest import snapshot_fixture


def _payload() -> dict:
    return json.loads(snapshot_fixture("wi014_toy").read_text())


def _write(tmp_path, payload: dict):
    path = tmp_path / "extraction_snapshot.json"
    path.write_text(json.dumps(payload))
    return path


def test_envelope_is_v4():
    assert SNAPSHOT_FORMAT_VERSION == 4


@pytest.mark.parametrize(
    "foreign", [3, 5], ids=["reader-newer-than-writer", "reader-older-than-writer"]
)
def test_both_envelope_skew_directions_fail_closed(tmp_path, foreign):
    payload = _payload()
    payload["snapshot_format_version"] = foreign
    with pytest.raises(SnapshotFormatError, match=f"format version {foreign}, tool expects 4"):
        build_pipeline_context_from_snapshot(_write(tmp_path, payload))


def test_retained_v3_snapshot_fails_with_the_existing_recapture_message(tmp_path):
    """DD-A06: the pre-existing message, not a new mechanism, and no partial context."""
    payload = _payload()
    payload["snapshot_format_version"] = 3
    with pytest.raises(SnapshotFormatError, match="Recapture with"):
        build_pipeline_context_from_snapshot(_write(tmp_path, payload))


def test_envelope_gate_runs_before_the_lowering_mode_is_read(tmp_path):
    """DD-A20 / DD-R15: the version gate precedes any mode read.

    If the mode were read first, a stale snapshot could take the `grandfathered_off`
    fail-open branch that Item 12 owns — which would be exactly the second
    grandfathering route this item must not introduce. Corrupting the mode to a value
    no reader accepts proves the ordering: the version error must win.
    """
    payload = _payload()
    payload["snapshot_format_version"] = 3
    payload["constraint_lowering_mode"] = "not_a_real_mode"
    with pytest.raises(SnapshotFormatError, match="format version 3, tool expects 4"):
        build_pipeline_context_from_snapshot(_write(tmp_path, payload))


def test_every_committed_snapshot_loads_at_v4():
    """DD-A06: all 34 (now 35) committed fixtures load at the new version."""
    from tests.conftest import FIXTURES_DIR

    snapshots = sorted(FIXTURES_DIR.glob("*/extraction_snapshot.json"))
    assert len(snapshots) >= 34
    stale = [
        path.parent.name
        for path in snapshots
        if json.loads(path.read_text())["snapshot_format_version"] != SNAPSHOT_FORMAT_VERSION
    ]
    assert stale == [], f"snapshots not re-captured at v{SNAPSHOT_FORMAT_VERSION}: {stale}"


def test_every_committed_snapshot_carries_facts_v2():
    from sysml_codegen import _upstream_pins
    from tests.conftest import FIXTURES_DIR

    stale = [
        path.parent.name
        for path in sorted(FIXTURES_DIR.glob("*/extraction_snapshot.json"))
        if json.loads(path.read_text())["constraint_facts"]["schema_version"]
        != _upstream_pins.CONSTRAINT_FACTS_SCHEMA_VERSION
    ]
    assert stale == [], f"snapshots carrying stale facts schema: {stale}"
