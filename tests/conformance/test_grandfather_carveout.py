"""Item 14 Phase 1: the plant_values/fusion_tea grandfather carve-out retires (INV-D).

Both fixtures asserted real constraints the `gain` hierarchy-extraction gap blocked from
lowering (Item 8's carve-out). Item 14 closes that gap (D2: the instance-self-redef tier
+ the constraint-actual demand widening it needs; D2-twin: the def-scoped base-default
rung for a bare-name actual with no `:>>` override at all) — both fixtures now lower under
the DEFAULT (`lower_constraints_enabled=True`), live and offline alike. The named
`GRANDFATHERED` exclusion set in the capture script is now empty (INV-D); this file
inverts every assertion the old carve-out made.

The `lower_constraints_enabled=False` capture-time opt-out mechanism itself is not
retired (Item 8's grandfather mechanism may still be needed for a future gap) — only its
application to these two fixtures is. `test_snapshot_v3_gate.py` / `capture.py`'s own
tests still cover the flag generically.

Captures fresh into `tmp_path` rather than reading the committed corpus — Phase 1 also
re-captures the committed snapshots; this file is independent of that re-capture.
"""

from __future__ import annotations

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.snapshot import build_full_graph_from_snapshot, capture_snapshot
from tests.conftest import FIXTURES_DIR, requires_license


@requires_license
@pytest.mark.parametrize("fixture", ["plant_values", "fusion_tea"])
def test_grandfathered_fixture_now_lowers(fixture, tmp_path):
    """INV-D: a fresh default capture (lowering enabled) assembles a real catalog —
    the assertion the old carve-out's `grandfathered_off` marker prevented."""
    snap_path = capture_snapshot(
        [FIXTURES_DIR / fixture], tmp_path / "extraction_snapshot.json"
    )
    graph, _inputs = build_full_graph_from_snapshot(snap_path)
    assert graph.constraint_catalog is not None
    assert any(e.constraint_id for e in graph.constraint_catalog.concrete_entries)


@requires_license
@pytest.mark.parametrize("fixture", ["plant_values", "fusion_tea"])
def test_live_generate_grandfathered_no_longer_halts_on_gain(fixture):
    """Inverts the old carve-out's halt assertion: live generation under the default
    now resolves `gain` and assembles the catalog instead of raising."""
    ctx = build_pipeline_context([FIXTURES_DIR / fixture])
    assert ctx.computation_graph.constraint_catalog is not None
    assert any(e.constraint_id for e in ctx.computation_graph.constraint_catalog.concrete_entries)
