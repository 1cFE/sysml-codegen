"""Item 8 Phase 3: end-to-end live/snapshot constraint parity (INV-3, INV-4).

Proves the from-snapshot rebuild (``graph_rebuild.build_full_graph_from_snapshot``)
re-lowers constraint facts offline to a byte-identical graph and catalog on the
three clean-lowering fixtures — genuine re-derivation from carried inputs, not
carriage of a frozen catalog (S3's CF(2) trap, the thing D1 rejected).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.snapshot import build_full_graph_from_snapshot, capture_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

REPO_ROOT = Path(__file__).resolve().parents[2]


@requires_license
@pytest.mark.parametrize(
    "fixture",
    ["wi014_toy", "constraint_multi_instance", "constraint_inline", "catf_mfe_model"],
)
def test_live_snapshot_constraint_parity(fixture, tmp_path):
    live = build_pipeline_context([FIXTURES_DIR / fixture], lower_constraints_enabled=True)
    snap_path = capture_snapshot(
        [FIXTURES_DIR / fixture],
        tmp_path / "extraction_snapshot.json",
    )
    offline_graph, _inputs = build_full_graph_from_snapshot(snap_path)

    live_graph = live.computation_graph
    # `constraint_catalog` is `exclude=True` on the model (never serialized into
    # committed baselines), so this dump already covers everything else: module
    # list, entry points, execution order — including the CONSTRAINT/
    # REPORT_AGGREGATOR nodes P3 EXTEND appended and the entry points it minted.
    assert json.loads(offline_graph.model_dump_json()) == json.loads(live_graph.model_dump_json())

    live_catalog = live_graph.constraint_catalog
    offline_catalog = offline_graph.constraint_catalog
    assert live_catalog is not None, f"{fixture}: live catalog must be assembled"
    assert offline_catalog is not None, f"{fixture}: offline catalog must be assembled"
    assert [e.constraint_id for e in offline_catalog.concrete_entries] == [
        e.constraint_id for e in live_catalog.concrete_entries
    ]  # INV-3: identical constraint_ids, identical catalog order
    assert offline_catalog.fingerprint == live_catalog.fingerprint
    assert offline_catalog.model_dump(mode="json") == live_catalog.model_dump(mode="json")


@requires_license
def test_constraint_free_fixture_loads_empty_catalog_graph_unchanged(tmp_path):
    """A constraint-free fixture: no catalog on either path, graph untouched."""
    fixture = "sample_model"
    live = build_pipeline_context([FIXTURES_DIR / fixture], lower_constraints_enabled=True)
    assert live.constraint_facts is not None and live.constraint_facts.usages == []

    snap_path = capture_snapshot(
        [FIXTURES_DIR / fixture],
        tmp_path / "extraction_snapshot.json",
    )
    offline_graph, _inputs = build_full_graph_from_snapshot(snap_path)

    assert live.computation_graph.constraint_catalog is None
    assert offline_graph.constraint_catalog is None
    assert json.loads(offline_graph.model_dump_json()) == json.loads(
        live.computation_graph.model_dump_json()
    )


def test_offline_path_never_builds_part_instance_index():
    """INV-4: the offline rebuild never invokes the live-model-only index builder."""
    out = subprocess.run(
        ["grep", "-n", "build_part_instance_index", "src/sysml_codegen/snapshot/graph_rebuild.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert out.stdout.strip() == "", (
        f"graph_rebuild.py must never call build_part_instance_index (INV-4) — found:\n{out.stdout}"
    )
