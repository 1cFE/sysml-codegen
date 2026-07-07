"""Phase 1 (F-A): `design_overrides` reaches the supplied-value materializer.

The materializer's precedence tier 1 reads `design_overrides`. If the snapshot rebuild
path drops it on the floor, shapes (b)/(c) have no value source and the headline flip
is dead. This spies the materializer call in the snapshot rebuild (the path every graph
baseline is captured through) and asserts the overrides arrive non-empty. The live path
(`pipeline_builder` Step 5.65) threads it symmetrically from the same
`hierarchy_data.design_overrides`.
"""

from __future__ import annotations

from unittest.mock import patch

import sysml_codegen.snapshot.graph_rebuild as graph_rebuild
from tests.conftest import snapshot_fixture


def test_design_overrides_reaches_materializer_from_snapshot():
    real = graph_rebuild.materialize_supplied_values
    captured: dict = {}

    def spy(calc_usages, redefinitions, design_overrides, usage_type_map, real_design_attrs):
        captured["design_overrides"] = design_overrides
        return real(calc_usages, redefinitions, design_overrides, usage_type_map, real_design_attrs)

    with patch.object(graph_rebuild, "materialize_supplied_values", spy):
        graph_rebuild.build_full_graph_from_snapshot(snapshot_fixture("plant_values"))

    overrides = captured["design_overrides"]
    assert overrides is not None
    # plant_values carries the (b) target_factory block and (c) chamber dotted override.
    attrs = {o.attribute_name for o in overrides}
    assert {"cost_per_target", "cost_per_unit"} <= attrs
