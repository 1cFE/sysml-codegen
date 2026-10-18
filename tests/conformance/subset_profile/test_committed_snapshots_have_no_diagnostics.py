"""No committed v6 snapshot seals a diagnostic (Item 2a D8, snapshot stability).

The v6 encoder refuses a diagnostic that carries a site reason, because the format has no
field for one. That refusal can never fire on a sealed graph only if sealed graphs carry no
diagnostics, which ``InstanceGraph.require_projectable`` enforces before sealing. This pins
the premise on the bytes actually committed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR

COMMITTED_V6_SNAPSHOTS = sorted(FIXTURES_DIR.glob("*/instance_graph_snapshot.json"))


def test_every_committed_snapshot_is_listed():
    assert len(COMMITTED_V6_SNAPSHOTS) == 22


@pytest.mark.parametrize("path", COMMITTED_V6_SNAPSHOTS, ids=lambda p: p.parent.name)
def test_sealed_graph_diagnostics_empty(path: Path):
    assert load_instance_graph_snapshot(path).diagnostics == []
