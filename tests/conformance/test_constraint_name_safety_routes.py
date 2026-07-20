"""License-free route and carrier checks for generated constraint name safety."""

from __future__ import annotations

import json
from pathlib import Path

from sysml_codegen.snapshot import SNAPSHOT_FORMAT_VERSION
from sysml_codegen.orchestration.snapshot_context import build_pipeline_context_from_snapshot
from sysml_codegen.resolution.models import ModuleKind

FIXTURE = Path(__file__).parents[1] / "fixtures/constraint_multi_instance/extraction_snapshot.json"


def test_snapshot_rebuild_retains_identity_carriers_without_snapshot_change():
    snapshot_payload = json.loads(FIXTURE.read_text())
    ctx = build_pipeline_context_from_snapshot(FIXTURE)
    graph = ctx.computation_graph
    constraint_modules = [
        module for module in graph.modules if module.module_kind == ModuleKind.CONSTRAINT
    ]
    assert constraint_modules
    carriers = [item.formal_identity for module in constraint_modules for item in module.inputs]
    assert carriers and all(carrier is not None for carrier in carriers)
    copied = graph.model_copy(deep=True)
    copied_carriers = [
        item.formal_identity
        for module in copied.modules
        if module.module_kind == ModuleKind.CONSTRAINT
        for item in module.inputs
    ]
    assert copied_carriers == carriers
    assert "formal_identity" not in json.dumps(graph.model_dump(mode="json"))
    assert snapshot_payload["snapshot_format_version"] == SNAPSHOT_FORMAT_VERSION
    assert "formal_identity" not in FIXTURE.read_text()
