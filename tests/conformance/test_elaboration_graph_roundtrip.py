"""Canonical internal resolved-graph codec for future snapshot replacement."""

from __future__ import annotations

import hashlib
import json

import pytest

from sysml_codegen.elaboration import ProjectionError, elaborate, project
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.snapshot.instance_graph import (
    InstanceGraphCodecError,
    decode_instance_graph,
    encode_instance_graph,
)
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


def _graph():
    extractor = SysMLDataExtractor([FIXTURES_DIR / "source_identity_mixed_consumers"])
    assert extractor.load_models()
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )


def test_resolved_graph_round_trip_is_canonical_and_projectable() -> None:
    live = _graph()
    first = encode_instance_graph(live)
    rebuilt = decode_instance_graph(first)

    assert encode_instance_graph(rebuilt) == first
    assert rebuilt == live
    assert project(rebuilt) == project(live)


def test_graph_codec_rejects_foreign_schema_and_tampered_fingerprint() -> None:
    payload = encode_instance_graph(_graph())

    with pytest.raises(InstanceGraphCodecError):
        decode_instance_graph(payload.replace(b'"instance-graph/v1"', b'"other-graph/v1"'))
    with pytest.raises(InstanceGraphCodecError):
        decode_instance_graph(payload.replace(b'"fingerprint":"', b'"fingerprint":"0'))


def test_graph_codec_preserves_blocking_diagnostics() -> None:
    extractor = SysMLDataExtractor([FIXTURES_DIR / "elab_fail_closed_probe"])
    assert extractor.load_models()
    live = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=False,
    )

    rebuilt = decode_instance_graph(encode_instance_graph(live))

    assert rebuilt == live
    assert rebuilt.diagnostics
    with pytest.raises(ProjectionError):
        project(rebuilt)


def test_graph_codec_rejects_re_fingerprinted_foreign_identity() -> None:
    document = json.loads(encode_instance_graph(_graph()))
    document["graph"]["attrs"][0]["node_id"] = "[]"
    signed = {
        "schema_version": document["schema_version"],
        "graph": document["graph"],
    }
    canonical = json.dumps(
        signed,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode()
    document["fingerprint"] = hashlib.sha256(canonical).hexdigest()

    with pytest.raises(InstanceGraphCodecError):
        decode_instance_graph(json.dumps(document).encode())
