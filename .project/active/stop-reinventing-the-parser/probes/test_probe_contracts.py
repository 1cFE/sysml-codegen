"""Contract tests for the retained pre-production probe inputs and outputs."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROBES = Path(__file__).resolve().parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, PROBES / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_closed_fixture_inventory() -> None:
    manifest = json.loads((ROOT / "verification/fixture-manifest.json").read_text())
    assert manifest["counts"] == {
        "added_roots": 6,
        "added_source_files": 7,
        "canonical_graph_records": 15,
        "canonical_refusal_records": 22,
        "canonical_roots": 37,
        "total_roots": 43,
    }
    roots = manifest["roots"]
    assert len(roots) == 43
    assert len({row["root"] for row in roots}) == 43
    for row in roots:
        assert row["sources"]
        for source in row["sources"]:
            path = Path(source["path"])
            assert not path.is_absolute() and ".." not in path.parts


def test_b8_probe_has_no_post_gate_evidence_dependency() -> None:
    source = (PROBES / "b8_resolved_fact_totality.py").read_text()
    assert "SemanticEvidence" not in source
    assert "missing_leaf_count" in source
    assert '"REAL_CORPUS_TOTAL"' in source


def test_probe_verdict_vocabulary_is_closed() -> None:
    b2 = _load("b2_containment_address_feasibility")
    b8 = _load("b8_resolved_fact_totality")
    b10 = _load("b10_document_origin")
    assert len(b2.TOPOLOGY_ROWS) == 7
    assert "REAL_CORPUS_TOTAL" in Path(b8.__file__).read_text()
    assert "DELETE_UNREACHABLE" in Path(b10.__file__).read_text()


def test_b10_normalizes_real_source_admission_string_referents() -> None:
    from sysml_codegen.extraction.source_manifest import admit_sources

    b10 = _load("b10_document_origin")
    root = ROOT / "tests/fixtures/feature_metadata_multifile"
    with admit_sources([root]) as admission:
        referents = sorted(item.referent for item in admission.files)

    assert referents == ["root-0/design.sysml", "root-0/library.sysml"]
    assert all(type(referent) is str for referent in referents)
    assert [b10._root_relative_referent(referent) for referent in referents] == referents
