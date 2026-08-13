"""Complete tracked-snapshot inventory gates for CONSTRAINT-SEMANTICS Item 8."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import assess_v6_snapshot_churn as inventory  # noqa: E402

ITEM_ROOT = ROOT / ".project" / "active" / "unit-lane-port-metadata"
PRE_INVENTORY = ITEM_ROOT / "snapshot-inventory-pre.json"
FINAL_INVENTORY = ITEM_ROOT / "snapshot-inventory-final.json"
RECAPTURE_RECEIPT = ITEM_ROOT / "v3-recapture.json"


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text())
    assert isinstance(value, dict)
    return value


def test_inventory_rejects_missing_extra_and_duplicate_rows() -> None:
    tracked = ["a/instance_graph_snapshot.json", "b/instance_graph_snapshot.json"]

    with pytest.raises(inventory.InventorySetError, match="duplicate"):
        inventory.require_exact_row_set(tracked, [tracked[0], tracked[0], tracked[1]])
    with pytest.raises(inventory.InventorySetError, match="missing"):
        inventory.require_exact_row_set(tracked, [tracked[0]])
    with pytest.raises(inventory.InventorySetError, match="extra"):
        inventory.require_exact_row_set(tracked, [*tracked, "c/instance_graph_snapshot.json"])


def test_inventory_records_required_digests_and_unit_maps() -> None:
    document = _load(PRE_INVENTORY)
    rows = document["rows"]
    assert isinstance(rows, list) and rows
    for raw_row in rows:
        assert isinstance(raw_row, dict)
        committed = raw_row["committed"]
        live = raw_row["live"]
        assert isinstance(committed, dict)
        assert isinstance(live, dict)
        assert committed["envelope_sha256"]
        assert committed["outer_digest"]
        assert committed["instance_graph_fingerprint"]
        assert committed["source_manifest_fingerprint"]
        assert committed["instance_graph_payload_digest"]
        assert isinstance(committed["unit_map"], list)
        assert live["instance_graph_fingerprint"]
        assert live["source_manifest_fingerprint"]
        assert live["instance_graph_payload_digest"]
        assert isinstance(live["unit_map"], list)
        for arm in (committed, live):
            projection = arm["projection"]
            assert isinstance(projection, dict)
            if projection["status"] == "projectable":
                assert projection["computation_digest"]
                assert projection["generated_entry_point_digest"]
                assert isinstance(projection["generated_entry_point_paths"], list)
            else:
                assert projection["generated_entry_point_digest"] is None
                assert projection["generated_entry_point_inapplicable"]


def test_pre_inventory_rows_equal_exact_tracked_snapshot_set() -> None:
    document = _load(PRE_INVENTORY)
    tracked = inventory.tracked_snapshot_paths(ROOT)
    rows = document["rows"]
    assert isinstance(rows, list)
    row_paths = [row["path"] for row in rows]
    inventory.require_exact_row_set(tracked, row_paths)
    assert document["tracked_paths"] == tracked
    assert document["tracked_count"] == len(tracked) == 23
    assert document["row_count"] == len(rows) == 23
    assert document["missing_paths"] == []
    assert document["extra_paths"] == []
    assert document["duplicate_paths"] == []


def test_final_inventory_rows_equal_exact_tracked_snapshot_set() -> None:
    document = _load(FINAL_INVENTORY)
    tracked = inventory.tracked_snapshot_paths(ROOT)
    rows = document["rows"]
    assert isinstance(rows, list)
    row_paths = [row["path"] for row in rows]
    inventory.require_exact_row_set(tracked, row_paths)
    assert document["tracked_paths"] == tracked
    assert document["tracked_count"] == len(tracked)
    assert document["row_count"] == len(rows)
    assert document["missing_paths"] == []
    assert document["extra_paths"] == []
    assert document["duplicate_paths"] == []


def test_final_inventory_records_every_path_addition_and_removal() -> None:
    pre = _load(PRE_INVENTORY)
    final = _load(FINAL_INVENTORY)
    pre_paths = set(pre["tracked_paths"])
    final_paths = set(final["tracked_paths"])
    assert final["path_additions"] == sorted(final_paths - pre_paths)
    assert final["path_removals"] == sorted(pre_paths - final_paths)


def test_final_inventory_classifies_every_digest_and_unit_movement() -> None:
    final = _load(FINAL_INVENTORY)
    rows = final["rows"]
    assert isinstance(rows, list)
    stale_paths = []
    for row in rows:
        movement = row["movement"]
        assert set(movement) == {
            "instance_graph_payload_changed",
            "unit_map_changed",
            "envelope_sha_changed",
            "source_manifest_changed",
            "computation_digest_changed",
            "generated_entry_point_digest_changed",
            "projected_counts_changed",
        }
        assert all(isinstance(value, bool) for value in movement.values())
        stale = (
            movement["instance_graph_payload_changed"]
            or movement["unit_map_changed"]
        )
        assert row["stale"] is stale
        assert row["stale_reason"] == [
            reason
            for changed, reason in (
                (
                    movement["instance_graph_payload_changed"],
                    "instance_graph_payload_changed",
                ),
                (movement["unit_map_changed"], "unit_map_changed"),
            )
            if changed
        ]
        if stale:
            stale_paths.append(row["path"])
    assert final["stale_paths"] == stale_paths


def test_final_inventory_and_recap_receipt_obey_zero_or_one_law() -> None:
    final = _load(FINAL_INVENTORY)
    tracked = inventory.tracked_snapshot_paths(ROOT)
    rows = final["rows"]
    assert isinstance(rows, list)
    inventory.require_exact_row_set(tracked, [row["path"] for row in rows])
    stale_paths = final["stale_paths"]
    if not stale_paths:
        assert not RECAPTURE_RECEIPT.exists()
    else:
        receipt = _load(RECAPTURE_RECEIPT)
        assert receipt["invocation_count"] == 1
        assert receipt["paths"] == stale_paths


def test_non_stale_snapshot_bytes_are_unchanged() -> None:
    pre = _load(PRE_INVENTORY)
    final = _load(FINAL_INVENTORY)
    pre_by_path = {row["path"]: row for row in pre["rows"]}
    stale = set(final["stale_paths"])
    common = set(pre["tracked_paths"]) & set(final["tracked_paths"])
    for row in final["rows"]:
        path = row["path"]
        if path in common - stale:
            assert row["committed"]["envelope_sha256"] == pre_by_path[path]["committed"][
                "envelope_sha256"
            ]
