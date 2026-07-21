"""Phase 1 (F-A): `design_overrides` reaches the supplied-value enrichment seam.

The value ladder's precedence tier 1 reads `design_overrides`. If the snapshot rebuild
path drops it on the floor, shapes (b)/(c) have no value source and the headline flip
is dead. This spies the enrichment call in the snapshot rebuild (the path every graph
baseline is captured through) and asserts the overrides arrive non-empty. The live path
(`pipeline_builder` Step 5.65) threads it symmetrically from the same
`hierarchy_data.design_overrides`.

Item 1 additions: replay calls the shared seam exactly once, and the seam is
copy-on-write — the loaded snapshot's attribute mapping and its lists come back
unchanged.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import sysml_codegen.snapshot.graph_rebuild as graph_rebuild
from tests.conftest import snapshot_fixture


def test_design_overrides_reaches_enrichment_from_snapshot():
    real = graph_rebuild.enrich_graph_design_attributes
    captured: dict = {}
    calls: list[str] = []

    def spy(real_design_attrs, **kwargs):
        calls.append("enrich")
        captured["design_overrides"] = kwargs["design_overrides"]
        captured["incoming_keys"] = list(real_design_attrs)
        captured["incoming_counts"] = {
            str(key): len(value) for key, value in real_design_attrs.items()
        }
        captured["incoming_mapping"] = real_design_attrs
        return real(real_design_attrs, **kwargs)

    with patch.object(graph_rebuild, "enrich_graph_design_attributes", spy):
        graph, inputs = graph_rebuild.build_full_graph_from_snapshot(
            snapshot_fixture("plant_values")
        )

    assert calls == ["enrich"]

    overrides = captured["design_overrides"]
    assert overrides is not None
    # plant_values carries the (b) target_factory block and (c) chamber dotted override.
    attrs = {o.attribute_name for o in overrides}
    assert {"cost_per_target", "cost_per_unit"} <= attrs

    # Copy-on-write: the loaded mapping and its lists are exactly as they arrived.
    incoming = captured["incoming_mapping"]
    assert list(incoming) == captured["incoming_keys"]
    assert {str(k): len(v) for k, v in incoming.items()} == captured["incoming_counts"]

    # The returned map is the Path-keyed enriched one the rest of the rebuild uses.
    assert all(isinstance(key, Path) for key in inputs["design_attrs"])
    assert graph is not None
