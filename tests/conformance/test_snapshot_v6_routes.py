"""One vertical route: live, in-place v6, and relocated v6 must agree exactly.

This is the slice's public behavior claim. A model elaborated live, the same
model captured and loaded back where it was written, and that same snapshot file
loaded from a different directory must produce one projected computation graph —
not three that happen to look similar.

The live arm deliberately does **not** go through admission. It calls
``build_elaborated_pipeline``, which reaches the elaborator by its own path, so a
defect anywhere in the capture route — admission, ``elaborate_admitted_sources``,
sealing, decoding — moves one side of the comparison and not the other. An
earlier version of this module took its live arm from the same two functions
capture calls, which made the comparison a round-trip check dressed up as a route
comparison: an injected defect in ``elaborate_admitted_sources`` changed the graph
and the assertion stayed green.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import shutil
from pathlib import Path

from sysml_codegen.elaboration import elaborate, project
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.source_manifest import admit_sources
from sysml_codegen.orchestration.elaborated_pipeline import (
    build_elaborated_pipeline,
    elaborate_admitted_sources,
)
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot
from sysml_codegen.snapshot.instance_graph import encode_instance_graph
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "source_identity_mixed_consumers"

#: Every field the two routes are expected to disagree on, all of them derived
#: from ``source_file``. The live builder records the caller's own path; the v6
#: route records the portable referent the sealed manifest names the file by.
#: ``_group_identity`` (``src/sysml_codegen/elaboration/project.py:164``) then
#: names each entry-point group after that path, so the referent rewrite renames
#: the group as well. These are masked for the structural comparison and then
#: asserted by value, so the divergence stays visible instead of being hashed
#: over. See ``test_the_two_routes_diverge_only_on_source_derived_naming``.
MASK = "<source-derived>"


def _instance_fingerprint(graph) -> str:
    return json.loads(encode_instance_graph(graph))["fingerprint"]


def _live_instance_graph(fixture: Path):
    """Elaborate without going through admission — an independent live arm.

    ``build_elaborated_pipeline`` projects, and projection drops detail the
    elaborator carries (``display_name``, for one), so a projected comparison
    alone cannot see every divergence. This reaches the same elaborator by the
    same path that builder takes, and stops one step earlier.
    """
    extractor = SysMLDataExtractor([fixture])
    assert extractor.load_models()
    assert extractor.diagnostics is not None
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )


def _graph_digest_ignoring_sources(graph) -> str:
    """Digest the whole encoded graph with only ``source_file`` neutralised."""
    document = json.loads(encode_instance_graph(graph))
    for group in ("attrs", "calcs", "constraints"):
        for row in document["graph"][group]:
            row["source_file"] = MASK
    encoded = json.dumps(
        document["graph"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _payload(graph) -> dict:
    """The whole projected public surface, not a sampled corner of it."""
    payload = graph.model_dump(mode="json")
    payload["fallback_entry_points"] = sorted(graph.fallback_entry_points)
    payload["constraint_catalog"] = (
        graph.constraint_catalog.model_dump(mode="json")
        if graph.constraint_catalog is not None
        else None
    )
    return payload


def _computation_digest(graph) -> str:
    encoded = json.dumps(
        _payload(graph), sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _masked(payload: dict) -> dict:
    """Mask exactly the source-derived naming, structurally rather than by key name.

    Blanket-masking every ``name`` would blind the comparison to real module and
    port differences, so each site is named explicitly.
    """
    masked = json.loads(json.dumps(payload))
    for module in masked["modules"]:
        module["source_file"] = MASK
        for module_input in module["inputs"]:
            source = module_input.get("source")
            if isinstance(source, dict) and "param_group" in source:
                source["param_group"] = MASK
    for group in masked["entry_point_groups"]:
        group["name"] = MASK
        group["class_name"] = MASK
        group["source_file"] = MASK
        for parameter in group["parameters"]:
            parameter["param_group"] = MASK
    return masked


def _source_derived_naming(payload: dict) -> dict[str, set[str]]:
    return {
        "module_source_files": {module["source_file"] for module in payload["modules"]},
        "group_names": {group["name"] for group in payload["entry_point_groups"]},
        "group_class_names": {group["class_name"] for group in payload["entry_point_groups"]},
    }


def test_live_in_place_and_relocated_routes_have_one_graph(tmp_path: Path) -> None:
    live = build_elaborated_pipeline([FIXTURE])

    captured = capture_instance_graph_snapshot([FIXTURE], tmp_path / "case.json")
    in_place = load_instance_graph_snapshot(captured)

    relocated_path = tmp_path / "moved" / "case.json"
    relocated_path.parent.mkdir()
    shutil.copyfile(captured, relocated_path)
    relocated = load_instance_graph_snapshot(relocated_path)

    assert _instance_fingerprint(in_place) == _instance_fingerprint(relocated), (
        "the in-place and relocated v6 routes disagree on the instance graph"
    )
    assert _computation_digest(project(in_place)) == _computation_digest(project(relocated)), (
        "the in-place and relocated v6 routes disagree on the projected computation graph"
    )
    assert _masked(_payload(live)) == _masked(_payload(project(in_place))), (
        "the live route and the v6 route disagree beyond the source-derived naming"
    )
    assert _graph_digest_ignoring_sources(_live_instance_graph(FIXTURE)) == (
        _graph_digest_ignoring_sources(in_place)
    ), "the live elaborator and the sealed graph disagree"


def test_the_two_routes_diverge_only_on_source_derived_naming(tmp_path: Path) -> None:
    """Pin the known divergence by value — it carries a real defect, deferred to 3B.

    Two things show up here, and both are worth seeing rather than hashing over.

    The v6 side is the improvement: one portable referent everywhere. The live
    side is what the referent design exists to replace — absolute checkout paths,
    one of them still carrying a leftover ``//`` URI prefix, and modules with no
    recorded source at all.

    The defect is the knock-on. ``_group_identity`` names each entry-point group
    after the source path, so on the v6 route the group is named after the staging
    referent: a package generated from a v6 snapshot would ship
    ``inputs/root_0_params.json`` and a ``Root0Params`` schema class instead of
    names taken from the model. Slice 3B owns ``elaboration/project.py`` and must
    resolve it before the public authority switch. Recorded here, not normalised
    away, so the day it changes this test says so.
    """
    live = _source_derived_naming(_payload(build_elaborated_pipeline([FIXTURE])))
    captured = capture_instance_graph_snapshot([FIXTURE], tmp_path / "case.json")
    v6 = _source_derived_naming(_payload(project(load_instance_graph_snapshot(captured))))

    # The v6 side is exact: one portable referent, and no path of any other shape.
    assert v6["module_source_files"] == {None, "root-0/model.sysml"}
    assert v6["group_names"] == {"root_0_params"}
    assert v6["group_class_names"] == {"Root0Params"}

    # The live side is what the referent design exists to replace: absolute
    # checkout paths, one of them carrying a leftover URI prefix, plus modules
    # with no recorded source at all.
    absolute = str(FIXTURE / "model.sysml")
    assert live["module_source_files"] == {None, absolute, "//" + absolute}
    assert live["group_names"] == {"source_identity_mixed_consumers_params"}
    assert live["group_class_names"] == {"SourceIdentityMixedConsumersParams"}


def test_the_live_arm_does_not_share_the_capture_route(tmp_path: Path) -> None:
    """The comparison above is only worth anything if its arms are independent.

    ``build_elaborated_pipeline`` must not reach the elaborator through admission,
    or a defect inside ``elaborate_admitted_sources`` moves both sides at once and
    the equality assertion cannot see it.
    """
    source = Path(inspect.getsourcefile(build_elaborated_pipeline) or "").read_text()
    live_body = inspect.getsource(build_elaborated_pipeline)
    assert "elaborate_admitted_sources" not in live_body
    assert "admit_sources" not in live_body
    assert "capture_instance_graph_snapshot" not in source

    with admit_sources([FIXTURE]) as admission:
        admitted = elaborate_admitted_sources(admission)
    captured = capture_instance_graph_snapshot([FIXTURE], tmp_path / "case.json")
    assert _instance_fingerprint(admitted) == _instance_fingerprint(
        load_instance_graph_snapshot(captured)
    ), "capture must seal exactly what the admitted route elaborates"


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
