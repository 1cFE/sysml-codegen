"""Item 8 Phase 4: the plant_values/fusion_tea grandfather carve-out (D3, INV-5).

Both fixtures assert real constraints the `gain` hierarchy-extraction gap
(Item 14's prerequisite) blocks from lowering. Captured with
`lower_constraints_enabled=False`, they stamp `constraint_lowering_mode:
"grandfathered_off"` — the offline path reads that marker and skips lowering,
loudly, rather than silently inferring "don't lower" from an empty facts/
occurrence section. The live CLI is NOT exempted: under the new default it
still halts on the unresolved `gain` actual, exactly as before this item.

Captures fresh into `tmp_path` rather than reading the committed corpus —
Phase 5 re-captures the committed snapshots; until then they are still v2 and
would fail the version gate before this test could exercise anything.
"""

from __future__ import annotations

import json

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.snapshot import build_full_graph_from_snapshot, capture_snapshot
from tests.conftest import FIXTURES_DIR, requires_license


@requires_license
@pytest.mark.parametrize("fixture", ["plant_values", "fusion_tea"])
def test_grandfathered_snapshot_captures_honest_facts_and_skips_offline(fixture, tmp_path, caplog):
    snap_path = capture_snapshot(
        [FIXTURES_DIR / fixture],
        tmp_path / "extraction_snapshot.json",
        lower_constraints_enabled=False,
    )
    raw = json.loads(snap_path.read_text())
    assert raw["constraint_lowering_mode"] == "grandfathered_off"
    assert raw["constraint_facts"]["usages"], (
        f"{fixture}: grandfathered facts must stay honest/non-empty, never a "
        "dishonest empty section (D3, rejected alternative)"
    )
    assert raw["part_occurrences"] == {}

    import logging

    with caplog.at_level(logging.WARNING):
        graph, _inputs = build_full_graph_from_snapshot(snap_path)
    assert graph.constraint_catalog is None  # lowering skipped, no catalog assembled
    assert "grandfather" in caplog.text.lower()


@requires_license
@pytest.mark.parametrize("fixture", ["plant_values", "fusion_tea"])
def test_live_generate_grandfathered_still_halts_on_gain(fixture):
    """The grandfather is scoped to the capture scripts, never the CLI (D3
    sub-bullet) — live generation under the new default still halts loudly on
    the unresolved `gain` actual, the honest signal Item 14 clears."""
    with pytest.raises(CodeGenerationError, match="gain"):
        build_pipeline_context([FIXTURES_DIR / fixture])
