"""Live admission, capture, relocation, and staleness through public routes."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_admitted_sources
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from sysml_codegen.snapshot.envelope import (
    SnapshotStaleSourceError,
    load_instance_graph_snapshot,
)
from sysml_codegen.extraction.source_manifest import (
    PINNED_STANDARD_LIBRARY_COUNT,
    admit_sources,
)
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "source_identity_mixed_consumers"


def test_parsed_documents_are_the_admitted_set_and_graph_sources_are_referents() -> None:
    with admit_sources([FIXTURE]) as admission:
        graph = elaborate_admitted_sources(admission)
        assert [row.referent for row in admission.files] == ["root-0/model.sysml"]
        assert admission.standard_library.document_count == PINNED_STANDARD_LIBRARY_COUNT
        sources = {
            node.source_file
            for nodes in (graph.attrs, graph.calcs, graph.constraints)
            for node in nodes.values()
        }
        assert sources == {"root-0/model.sysml"}


def test_admitted_sources_are_staged_so_the_original_tree_is_never_parsed() -> None:
    with admit_sources([FIXTURE]) as admission:
        staged = admission.staged_files
        assert len(staged) == 1
        assert not staged[0].is_relative_to(FIXTURE)
        assert staged[0].read_bytes() == (FIXTURE / "model.sysml").read_bytes()
    assert not staged[0].exists(), "the stage must be removed when admission closes"


def test_relocated_roots_reproduce_the_manifest_and_edits_are_stale(tmp_path: Path) -> None:
    captured = capture_instance_graph_snapshot([FIXTURE], tmp_path / "captured.json")
    relocated_root = tmp_path / "relocated-source"
    shutil.copytree(FIXTURE, relocated_root)
    relocated_snapshot = tmp_path / "moved" / "captured.json"
    relocated_snapshot.parent.mkdir()
    shutil.copyfile(captured, relocated_snapshot)

    assert load_instance_graph_snapshot(relocated_snapshot, source_roots=[relocated_root])
    document = json.loads(relocated_snapshot.read_bytes())
    with admit_sources([relocated_root]) as replay:
        assert [row.envelope_data() for row in replay.roots] == document["sources"]["roots"]
        assert [row.envelope_data() for row in replay.files] == document["sources"]["files"]

    (relocated_root / "added.sysml").write_text("package added;")
    with pytest.raises(SnapshotStaleSourceError, match="reproduce"):
        load_instance_graph_snapshot(relocated_snapshot, source_roots=[relocated_root])


def test_changed_source_bytes_are_stale_even_when_the_file_set_is_unchanged(
    tmp_path: Path,
) -> None:
    root = tmp_path / "source"
    shutil.copytree(FIXTURE, root)
    captured = capture_instance_graph_snapshot([root], tmp_path / "captured.json")
    model = root / "model.sysml"
    model.write_text(model.read_text() + "\n// a later edit\n")
    with pytest.raises(SnapshotStaleSourceError, match="reproduce"):
        load_instance_graph_snapshot(captured, source_roots=[root])


def test_an_external_document_is_parsed_only_when_explicitly_rooted(tmp_path: Path) -> None:
    main = tmp_path / "main"
    external = tmp_path / "external"
    main.mkdir()
    external.mkdir()
    (main / "model.sysml").write_text(
        "package main {\n"
        "    private import ScalarValues::*;\n"
        "    private import external::*;\n"
        "    calc def UseExternal { in x : Real; out y : Real = x; }\n"
        "}\n"
    )
    (external / "external.sysml").write_text(
        "package external { private import ScalarValues::*; "
        "attribute external_value : Real = 1.0; }"
    )

    with admit_sources([main, external]) as admission:
        extractor = SysMLDataExtractor(list(admission.staged_files))
        assert extractor.load_models()
        admission.verify_after_parse(extractor.model)
        assert [row.referent for row in admission.files] == [
            "root-0/model.sysml",
            "root-1/external.sysml",
        ]

    with admit_sources([main]) as admission:
        extractor = SysMLDataExtractor(list(admission.staged_files))
        with pytest.raises((ValueError, AssertionError)):
            assert extractor.load_models()


def test_a_root_symlink_stays_caller_visible_without_leaking_absolute_paths(
    tmp_path: Path,
) -> None:
    visible = tmp_path / "visible-design-root"
    visible.symlink_to(FIXTURE.resolve(), target_is_directory=True)
    destination = capture_instance_graph_snapshot([visible], tmp_path / "captured.json")
    document = json.loads(destination.read_bytes())

    assert {row["referent"] for row in document["sources"]["files"]} == {"root-0/model.sysml"}
    graph_sources = {
        row["source_file"]
        for group in ("attrs", "calcs", "constraints")
        for row in document["instance_graph"]["graph"][group]
    }
    assert graph_sources == {"root-0/model.sysml"}
    assert str(tmp_path) not in destination.read_text()
