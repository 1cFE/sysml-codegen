"""Licensed live, capture, relocation, and standard-library admission routes."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.orchestration.pipeline_builder import _load_and_elaborate
from sysml_codegen.snapshot import SnapshotStaleSourceError, capture_snapshot, load_snapshot
from sysml_codegen.snapshot.source_manifest import admit_sources
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "source_identity_mixed_consumers"


def test_syside_parses_exact_staged_user_documents_and_not_si() -> None:
    with admit_sources([FIXTURE]) as admission:
        graph = _load_and_elaborate(admission)
        assert len(admission.files) == 1
        assert admission.files[0].referent == "root-0/model.sysml"
        assert admission.standard_library.document_count == 94
        assert all(
            node.source_file == "root-0/model.sysml"
            for nodes in (graph.attrs.values(), graph.calcs.values(), graph.constraints.values())
            for node in nodes
        )


def test_relocated_roots_reproduce_manifest_and_changes_are_stale(tmp_path: Path) -> None:
    captured = capture_snapshot([FIXTURE], tmp_path / "captured.json")
    relocated_root = tmp_path / "relocated-source"
    shutil.copytree(FIXTURE, relocated_root)
    relocated_snapshot = tmp_path / "moved" / "captured.json"
    relocated_snapshot.parent.mkdir()
    shutil.copyfile(captured, relocated_snapshot)

    assert load_snapshot(relocated_snapshot, source_roots=[relocated_root])
    document = json.loads(relocated_snapshot.read_bytes())
    with admit_sources([relocated_root]) as replay:
        assert [row.envelope_data() for row in replay.roots] == document["sources"]["roots"]
        assert [row.envelope_data() for row in replay.files] == document["sources"]["files"]

    (relocated_root / "added.sysml").write_text("package added;")
    with pytest.raises(SnapshotStaleSourceError, match="reproduce"):
        load_snapshot(relocated_snapshot, source_roots=[relocated_root])


def test_external_user_document_is_staged_only_when_explicitly_rooted(tmp_path: Path) -> None:
    main = tmp_path / "main"
    external = tmp_path / "external"
    (main / "model.sysml").parent.mkdir()
    (main / "model.sysml").write_text(
        """package main {
            private import ScalarValues::*;
            private import external::*;
            calc def UseExternal { in x : Real; out y : Real = x; }
        }
        """
    )
    (external / "external.sysml").parent.mkdir()
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


def test_design_filter_keeps_caller_visible_root_but_not_absolute_graph_paths(
    tmp_path: Path,
) -> None:
    visible = tmp_path / "visible-design-root"
    visible.symlink_to(FIXTURE.resolve(), target_is_directory=True)
    destination = tmp_path / "filtered.json"
    capture_snapshot([visible], destination, design_path_filter="visible-design-root")
    document = json.loads(destination.read_bytes())
    assert document["capture"]["options"] == {"design_path_filter": "visible-design-root"}
    assert {row["referent"] for row in document["sources"]["files"]} == {"root-0/model.sysml"}
    source_files = {
        row["source_file"]
        for group in ("attrs", "calcs", "constraints")
        for row in document["instance_graph"]["graph"][group]
    }
    assert source_files == {"root-0/model.sysml"}
