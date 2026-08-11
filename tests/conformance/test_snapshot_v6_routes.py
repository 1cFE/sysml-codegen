"""One exact live, in-place v6, and relocated v6 vertical route."""

from __future__ import annotations

import hashlib
import json
import shutil

import sysml_codegen.snapshot as snapshot
from sysml_codegen.elaboration import project
from sysml_codegen.orchestration import pipeline_builder
from sysml_codegen.snapshot.instance_graph import encode_instance_graph
from sysml_codegen.snapshot.source_manifest import admit_sources
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "source_identity_mixed_consumers"
PROJECTOR_MARKER = "instance-projector/v1"


def _instance_fingerprint(graph) -> str:
    return json.loads(encode_instance_graph(graph))["fingerprint"]


def _computation_digest(graph) -> str:
    payload = graph.model_dump(mode="json")
    payload["fallback_entry_points"] = sorted(graph.fallback_entry_points)
    payload["constraint_catalog"] = (
        graph.constraint_catalog.model_dump(mode="json")
        if graph.constraint_catalog is not None
        else None
    )
    encoded = json.dumps(
        {"projector_semantics": PROJECTOR_MARKER, "computation_graph": payload},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def test_one_live_v6_relocated_route_has_one_digest(tmp_path) -> None:
    load_and_elaborate = getattr(pipeline_builder, "_load_and_elaborate", None)
    assert callable(load_and_elaborate)
    assert callable(getattr(snapshot, "load_snapshot", None))

    with admit_sources([FIXTURE]) as admission:
        live = load_and_elaborate(admission)
    captured = snapshot.capture_snapshot([FIXTURE], tmp_path / "case.json")
    in_place = snapshot.load_snapshot(captured)
    moved = tmp_path / "moved" / "case.json"
    moved.parent.mkdir()
    shutil.copyfile(captured, moved)
    relocated = snapshot.load_snapshot(moved)

    fingerprints = {
        _instance_fingerprint(live),
        _instance_fingerprint(in_place),
        _instance_fingerprint(relocated),
    }
    computation_digests = {
        _computation_digest(project(live)),
        _computation_digest(project(in_place)),
        _computation_digest(project(relocated)),
    }
    assert len(fingerprints) == 1
    assert len(computation_digests) == 1
