"""The snapshot envelope gate: fail closed both directions, before any semantic use.

DD-A06, DD-A20. An envelope version exists so that one version cannot describe two payloads
(DD-R12). The rule that follows from it is the same whichever envelope is in force: a reader
handed a payload it does not own must refuse, *typed*, before it reads anything semantic, and
without producing a partial context. No migration and no grandfathering path.

**One envelope is left.** The **v6 instance-graph envelope** is what the exact route reads,
and `snapshot.envelope` is in no deletion group, so this file keeps a live subject. The
retirement runbook's post-step battery — "the v5 typed refusal is still typed" — checks these
four nodes plus the two `test_public_authority_switch.py` refusal nodes.

The **v5 extraction envelope** half retired at retirement step 1 with the reader it gated
(`orchestration.snapshot_context`). Note that the by-name refusal of a v5 payload is *not*
part of what retired: `test_a_v5_extraction_snapshot_is_refused_by_name_not_by_a_null_version`
below is the surviving statement of it, and it runs against `snapshot/envelope.py`.

Gate 4C part 7 chunk 12 authored the split. See row L-180.
"""

from __future__ import annotations

import json

import pytest

from sysml_codegen.snapshot.envelope import SnapshotShapeError, load_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR

#: A committed v6 instance-graph snapshot, read for its bytes only — the fixture it came from
#: is immaterial to an envelope check.
V6_SNAPSHOT = FIXTURES_DIR / "gate_a_d5" / "instance_graph_snapshot.json"


def _v5_extraction_payload() -> dict:
    """A v5 extraction snapshot, as far as the v6 loader is concerned.

    The refusal keys on exactly two things (``snapshot/envelope.py:255-268``): no ``version``
    key, and a ``snapshot_format_version`` naming the format actually handed over. Nothing
    below that line is read. Building the payload here rather than reading a committed
    fixture is what keeps the by-name refusal checkable after the v5 fixtures retired with
    the family (retirement step 2).
    """
    return {"snapshot_format_version": 5, "calc_defs": [], "calc_usages": []}


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
    payload = _v5_extraction_payload()
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

    payload = _v5_extraction_payload()
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
