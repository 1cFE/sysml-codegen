"""The snapshot envelope gate: fail closed both directions, before any semantic use.

DD-A06, DD-A20. An envelope version exists so that one version cannot describe two payloads
(DD-R12). The rule that follows from it is the same whichever envelope is in force: a reader
handed a payload it does not own must refuse, *typed*, before it reads anything semantic, and
without producing a partial context. No migration and no grandfathering path.

**Two envelopes, and the file is organised by which retirement step each one dies at.**

- The **v6 instance-graph envelope** is what the exact route reads. Those nodes are at the top
  and they are the ones that survive: `snapshot.envelope` is not in any deletion group, so this
  file keeps a live subject after G2' removes the v5 read path. The retirement runbook's
  post-step-4 battery — "the v5 typed refusal still typed" — checks *these*.
- The **v5 extraction envelope** nodes are below, and each one imports
  `orchestration.snapshot_context` inside its own body rather than at module scope. That is
  deliberate: it keeps the rest of this file collecting after G2' deletes that owner, and it
  makes the retirement of the v5 gate a per-node fact instead of a whole-file one. Those nodes
  retire with the v5 family, when the fixtures they read retire.

Gate 4C part 7 chunk 12 authored the split. See row L-180.
"""

from __future__ import annotations

import json

import pytest

from sysml_codegen.snapshot import SNAPSHOT_FORMAT_VERSION, SnapshotFormatError
from sysml_codegen.snapshot.envelope import SnapshotShapeError, load_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR, snapshot_fixture

#: A committed v6 instance-graph snapshot, read for its bytes only — the fixture it came from
#: is immaterial to an envelope check.
V6_SNAPSHOT = FIXTURES_DIR / "gate_a_d5" / "instance_graph_snapshot.json"


def _write(tmp_path, payload: dict, name: str = "extraction_snapshot.json"):
    path = tmp_path / name
    path.write_text(json.dumps(payload))
    return path


# ---------------------------------------------------------------------------
# The v6 instance-graph envelope — the gate that survives the retirement
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "foreign", [5, 7], ids=["reader-newer-than-writer", "reader-older-than-writer"]
)
def test_both_v6_envelope_skew_directions_fail_closed(tmp_path, foreign):
    """Skew in either direction refuses, and the refusal says which version it found.

    Both directions matter and for different reasons. A payload from an older writer is the
    ordinary stale case. A payload from a *newer* writer is the dangerous one: the reader has
    no way to know what changed, so guessing is exactly the one-version-two-payloads failure
    the envelope exists to prevent.
    """
    payload = json.loads(V6_SNAPSHOT.read_text())
    payload["version"] = foreign
    with pytest.raises(SnapshotShapeError, match=f"snapshot version {foreign}"):
        load_instance_graph_snapshot(_write(tmp_path, payload, "instance_graph_snapshot.json"))


def test_a_v5_extraction_snapshot_is_refused_by_name_not_by_a_null_version(tmp_path):
    """DD-A06 carried forward: the refusal names the format it was actually handed.

    A v5 extraction snapshot carries no `version` key at all, so a generic message would
    report `None` and leave the reader guessing what they handed over. It says
    `v5 extraction snapshot` and gives the recapture instruction, which is what makes the
    refusal actionable rather than merely correct.
    """
    payload = json.loads(snapshot_fixture("wi014_toy").read_text())
    with pytest.raises(SnapshotShapeError) as refusal:
        load_instance_graph_snapshot(_write(tmp_path, payload))
    assert "v5 extraction snapshot" in str(refusal.value)
    assert "requires snapshot v6" in str(refusal.value)
    assert "Recapture with `sysml-codegen snapshot`" in str(refusal.value)


def test_the_v6_envelope_gate_runs_before_anything_semantic_is_read(tmp_path):
    """DD-A20: the version gate precedes every semantic read, so it cannot be outvoted.

    If a semantic decoder ran first, a payload from a foreign envelope could take a branch
    chosen on a field that no longer means what the reader thinks. Corrupting the instance
    graph past any decoder's tolerance *and* the version proves the ordering: the version
    error has to win.
    """
    payload = json.loads(V6_SNAPSHOT.read_text())
    payload["version"] = 5
    payload["instance_graph"] = "not an object at all"
    with pytest.raises(SnapshotShapeError, match="snapshot version 5"):
        load_instance_graph_snapshot(_write(tmp_path, payload, "instance_graph_snapshot.json"))


def test_the_public_route_refuses_a_foreign_snapshot_and_writes_no_package(tmp_path, caplog):
    """The gate as a user meets it: `run_codegen` declines and leaves nothing behind.

    A refusal that still emitted a partial package would be worse than no gate at all — the
    tree would look generated and be built from a payload the reader could not read.
    """
    import logging

    from sysml_codegen.cli import GenerationConfig, run_codegen

    payload = json.loads(snapshot_fixture("wi014_toy").read_text())
    output = tmp_path / "refused_package"
    with caplog.at_level(logging.ERROR, logger="sysml_codegen.cli"):
        accepted = run_codegen(
            GenerationConfig(
                from_snapshot=_write(tmp_path, payload),
                output_path=output,
                package_name="refused_package",
                overwrite=True,
            )
        )

    assert accepted is False
    assert "v5 extraction snapshot" in caplog.text
    assert not output.exists() or not any(output.rglob("*.py"))


# ---------------------------------------------------------------------------
# The v5 extraction envelope — retires with the v5 family
# ---------------------------------------------------------------------------
#
# Every node below imports `orchestration.snapshot_context` in its own body. Module-scope would
# make G2' break this whole file, including the four surviving nodes above.


def _v5_payload() -> dict:
    return json.loads(snapshot_fixture("wi014_toy").read_text())


def test_envelope_is_v5():
    assert SNAPSHOT_FORMAT_VERSION == 5


@pytest.mark.parametrize(
    "foreign", [4, 6], ids=["reader-newer-than-writer", "reader-older-than-writer"]
)
def test_both_envelope_skew_directions_fail_closed(tmp_path, foreign):
    from sysml_codegen.orchestration.snapshot_context import build_pipeline_context_from_snapshot

    payload = _v5_payload()
    payload["snapshot_format_version"] = foreign
    with pytest.raises(SnapshotFormatError, match=f"format version {foreign}, tool expects 5"):
        build_pipeline_context_from_snapshot(_write(tmp_path, payload))


def test_retained_pre_v5_snapshot_fails_with_the_existing_recapture_message(tmp_path):
    """DD-A06: the pre-existing message, not a new mechanism, and no partial context."""
    from sysml_codegen.orchestration.snapshot_context import build_pipeline_context_from_snapshot

    payload = _v5_payload()
    payload["snapshot_format_version"] = 4
    with pytest.raises(SnapshotFormatError, match="Recapture with"):
        build_pipeline_context_from_snapshot(_write(tmp_path, payload))


def test_envelope_gate_runs_before_the_lowering_mode_is_read(tmp_path):
    """DD-A20 / DD-R15: the version gate precedes any mode read.

    If the mode were read first, a stale snapshot could take the `grandfathered_off`
    fail-open branch that Item 12 owns — which would be exactly the second
    grandfathering route this item must not introduce. Corrupting the mode to a value
    no reader accepts proves the ordering: the version error must win.
    """
    from sysml_codegen.orchestration.snapshot_context import build_pipeline_context_from_snapshot

    payload = _v5_payload()
    payload["snapshot_format_version"] = 4
    payload["constraint_lowering_mode"] = "not_a_real_mode"
    with pytest.raises(SnapshotFormatError, match="format version 4, tool expects 5"):
        build_pipeline_context_from_snapshot(_write(tmp_path, payload))


def test_every_committed_snapshot_loads_at_v5():
    """DD-A06: every committed fixture loads at the new version."""
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

    stale = [
        path.parent.name
        for path in sorted(FIXTURES_DIR.glob("*/extraction_snapshot.json"))
        if json.loads(path.read_text())["constraint_facts"]["schema_version"]
        != _upstream_pins.CONSTRAINT_FACTS_SCHEMA_VERSION
    ]
    assert stale == [], f"snapshots carrying stale facts schema: {stale}"
