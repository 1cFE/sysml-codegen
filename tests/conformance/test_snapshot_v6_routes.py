"""One vertical route: live, in-place v6, and relocated v6 must agree exactly.

This is the slice's public behavior claim. A model elaborated live, the same
model captured and loaded back where it was written, and that same snapshot file
loaded from a different directory must produce one instance graph and one
projected computation graph — not three that happen to look similar.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from sysml_codegen.elaboration import project
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_admitted_sources
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot
from sysml_codegen.snapshot.instance_graph import encode_instance_graph
from sysml_codegen.extraction.source_manifest import admit_sources
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "source_identity_mixed_consumers"


def _instance_fingerprint(graph) -> str:
    return json.loads(encode_instance_graph(graph))["fingerprint"]


def _computation_digest(graph) -> str:
    """Digest the whole projected public surface, not a sampled corner of it."""
    payload = graph.model_dump(mode="json")
    payload["fallback_entry_points"] = sorted(graph.fallback_entry_points)
    payload["constraint_catalog"] = (
        graph.constraint_catalog.model_dump(mode="json")
        if graph.constraint_catalog is not None
        else None
    )
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def test_live_in_place_and_relocated_routes_have_one_graph(tmp_path: Path) -> None:
    with admit_sources([FIXTURE]) as admission:
        live = elaborate_admitted_sources(admission)

    captured = capture_instance_graph_snapshot([FIXTURE], tmp_path / "case.json")
    in_place = load_instance_graph_snapshot(captured)

    relocated_path = tmp_path / "moved" / "case.json"
    relocated_path.parent.mkdir()
    shutil.copyfile(captured, relocated_path)
    relocated = load_instance_graph_snapshot(relocated_path)

    assert len({_instance_fingerprint(route) for route in (live, in_place, relocated)}) == 1, (
        "live and v6 routes disagree on the instance graph"
    )
    assert (
        len({_computation_digest(project(route)) for route in (live, in_place, relocated)}) == 1
    ), "live and v6 routes disagree on the projected computation graph"


def test_the_route_carries_real_modelled_content(tmp_path: Path) -> None:
    """Guard against three empty graphs agreeing with each other."""
    captured = capture_instance_graph_snapshot([FIXTURE], tmp_path / "case.json")
    graph = load_instance_graph_snapshot(captured)
    assert graph.calcs, "the fixture models calculations; an empty graph proves nothing"
    assert graph.occurrences
    assert not graph.diagnostics

    modules = project(graph).modules
    assert modules
    assert all(module.inputs for module in modules)


def test_relocated_snapshot_needs_no_source_tree(tmp_path: Path) -> None:
    """A v6 snapshot is self-contained: loading never reads the original model."""
    staging = tmp_path / "staging"
    shutil.copytree(FIXTURE, staging)
    captured = capture_instance_graph_snapshot([staging], tmp_path / "case.json")
    expected = _instance_fingerprint(load_instance_graph_snapshot(captured))

    shutil.rmtree(staging)
    assert _instance_fingerprint(load_instance_graph_snapshot(captured)) == expected
