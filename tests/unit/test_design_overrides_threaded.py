"""Phase 1 (F-A): `design_overrides` reaches `build_computation_graph`.

The materializer's precedence tier 1 reads `design_overrides`; if either call site
(snapshot rebuild or live pipeline build) drops it on the floor, shapes (b)/(c) have
no value source and the headline flip is dead. This spies the snapshot call site (the
one every graph baseline is captured through) and asserts the kwarg arrives non-empty.
The live call site (`pipeline_builder`) threads it symmetrically with the identical
`hierarchy_data.design_overrides` expression.
"""

from __future__ import annotations

from unittest.mock import patch

import sysml_codegen.snapshot.graph_rebuild as graph_rebuild
from tests.conftest import snapshot_fixture


def test_design_overrides_reaches_build_from_snapshot():
    real_build = graph_rebuild.build_computation_graph
    captured: dict = {}

    def spy(*args, **kwargs):
        captured["design_overrides"] = kwargs.get("design_overrides")
        return real_build(*args, **kwargs)

    with patch.object(graph_rebuild, "build_computation_graph", spy):
        graph_rebuild.build_full_graph_from_snapshot(snapshot_fixture("plant_values"))

    overrides = captured["design_overrides"]
    assert overrides is not None
    # plant_values carries the (b) target_factory block and (c) chamber dotted override.
    attrs = {o.attribute_name for o in overrides}
    assert {"cost_per_target", "cost_per_unit"} <= attrs
