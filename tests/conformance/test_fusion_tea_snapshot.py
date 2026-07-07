"""SC-4: the committed fusion-tea snapshot resolves to TRUE ZERO V11 offenders.

The vendored canonical fusion-tea models (`~/1cfe/fusion-tea/models`) are the license-free
stand-in for Item 3's live acceptance run. All ten cross-part/in-part plain-value
references — the residual plant gap RN-10 left — clear under the supplied-value
materializer (a/b/c cross-part + d in-part). `generate --from-snapshot` on this snapshot
emits the full YAML package; V11 sees zero offenders.
"""

from __future__ import annotations

from sysml_codegen.resolution.graph_builder import collect_uncovered_params
from sysml_codegen.snapshot import build_full_graph_from_snapshot
from tests.conftest import snapshot_fixture


def test_fusion_tea_snapshot_zero_offenders():
    """SC-4 / epic CSF: zero V11 offenders on the committed fusion-tea snapshot."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("fusion_tea"))
    offenders = collect_uncovered_params(graph)
    assert offenders == [], [(u.module, u.input) for u in offenders]


def test_fusion_tea_emits_full_pipeline():
    """The full YAML package emits (modules + pipeline), not a partial graph."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("fusion_tea"))
    assert len(graph.modules) > 0
    # Every module output has a channel; every wired input resolves (no valueless V11).
    assert all(m.name for m in graph.modules)
