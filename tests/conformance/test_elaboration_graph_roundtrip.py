"""Canonical internal resolved-graph codec for future snapshot replacement."""

from __future__ import annotations

import hashlib
import json

import pytest

from sysml_codegen.elaboration import NodeRef, ProjectionError, elaborate, project
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.snapshot.instance_graph import (
    InstanceGraphCodecError,
    decode_instance_graph,
    encode_instance_graph,
)
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import every_alias_target, every_typed_edge

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
    document = json.loads(first)
    rebuilt = decode_instance_graph(first)

    assert document["schema_version"] == "instance-graph/v3"
    assert document["graph"]["occurrences"]
    assert all(
        isinstance(node["expression_ir"], dict)
        for node in document["graph"]["calcs"]
        if node["expression_ir"] is not None
    )
    assert encode_instance_graph(rebuilt) == first
    assert rebuilt == live
    assert project(rebuilt) == project(live)


def test_graph_codec_rejects_foreign_schema_and_tampered_fingerprint() -> None:
    payload = encode_instance_graph(_graph())

    with pytest.raises(InstanceGraphCodecError):
        decode_instance_graph(payload.replace(b'"instance-graph/v3"', b'"other-graph/v2"'))
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


@pytest.mark.parametrize("eligibility", [None, "allow_by_typo"])
def test_graph_codec_requires_a_closed_constraint_eligibility(eligibility: str | None) -> None:
    document = json.loads(encode_instance_graph(_graph()))
    constraint = document["graph"]["constraints"][0]
    if eligibility is None:
        del constraint["eligibility"]
    else:
        constraint["eligibility"] = eligibility
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


def _refingerprint(document: dict) -> bytes:
    signed = {
        "schema_version": document["schema_version"],
        "graph": document["graph"],
    }
    document["fingerprint"] = hashlib.sha256(
        json.dumps(
            signed,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode()
    ).hexdigest()
    return json.dumps(document).encode()


def test_graph_codec_rejects_missing_and_dangling_occurrence_records() -> None:
    missing = json.loads(encode_instance_graph(_graph()))
    missing["graph"]["occurrences"].pop()
    with pytest.raises(InstanceGraphCodecError):
        decode_instance_graph(_refingerprint(missing))

    dangling = json.loads(encode_instance_graph(_graph()))
    child = next(
        item for item in dangling["graph"]["occurrences"] if item["parent_id"] is not None
    )
    child["parent_id"] = "[[\"00000000-0000-5000-8000-000000000000\",null]]"
    with pytest.raises(InstanceGraphCodecError):
        decode_instance_graph(_refingerprint(dangling))


def test_graph_codec_rejects_invalid_ir_and_extra_expression_port() -> None:
    invalid_ir = json.loads(encode_instance_graph(_graph()))
    computed = next(
        item for item in invalid_ir["graph"]["calcs"] if item["expression_ir"] is not None
    )
    computed["expression_ir"] = {"kind": "not-an-expression"}
    with pytest.raises(InstanceGraphCodecError):
        decode_instance_graph(_refingerprint(invalid_ir))

    extra_port = json.loads(encode_instance_graph(_graph()))
    computed = next(
        item
        for item in extra_port["graph"]["calcs"]
        if item["expression_ir"] is not None and item["inputs"]
    )
    computed["inputs"][0]["port"]["reference_ordinal"] = 999
    with pytest.raises(InstanceGraphCodecError):
        decode_instance_graph(_refingerprint(extra_port))


def test_graph_codec_rejects_missing_metadata_and_conflicting_output_port() -> None:
    missing_metadata = json.loads(encode_instance_graph(_graph()))
    calc_with_input = next(
        item for item in missing_metadata["graph"]["calcs"] if item["inputs"]
    )
    del calc_with_input["inputs"][0]["metadata"]
    with pytest.raises(InstanceGraphCodecError):
        decode_instance_graph(_refingerprint(missing_metadata))

    conflicting_output = json.loads(encode_instance_graph(_graph()))
    calc_with_output = next(
        item for item in conflicting_output["graph"]["calcs"] if item["outputs"]
    )
    calc_with_output["outputs"][0]["port"]["output"] = (
        "00000000-0000-5000-8000-000000000000"
    )
    with pytest.raises(InstanceGraphCodecError):
        decode_instance_graph(_refingerprint(conflicting_output))


def test_graph_codec_rejects_missing_constraint_formal_provenance() -> None:
    missing_provenance = json.loads(encode_instance_graph(_graph()))
    constraint_with_input = next(
        item for item in missing_provenance["graph"]["constraints"] if item["inputs"]
    )
    constraint_with_input["inputs"][0]["metadata"]["formal_provenance"] = None

    with pytest.raises(InstanceGraphCodecError):
        decode_instance_graph(_refingerprint(missing_provenance))


@pytest.mark.parametrize(
    "fixture",
    ["constraint_inline", "deep_cross_scope_probe", "elab_native_plural_scope"],
)
def test_live_and_v2_round_trip_projection_match_across_graph_shapes(fixture: str) -> None:
    extractor = SysMLDataExtractor([FIXTURES_DIR / fixture])
    assert extractor.load_models()
    live = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )

    rebuilt = decode_instance_graph(encode_instance_graph(live))

    assert rebuilt.semantic_edges() == live.semantic_edges()
    assert project(rebuilt) == project(live)


def test_usage_owned_anchoring_survives_the_codec_including_raw_alias_targets() -> None:
    """The decoded graph, not ``semantic_edges()``, is the round-trip oracle here.

    ``semantic_edges()`` reads consumer input ports only, so an attribute's raw
    ``alias_target`` — the qualified typed-alias lane of the combined fixture — is
    invisible to it. The first assertion below pins that omission, which is why the
    rest compares the whole decoded graph and the alias map by value.
    """
    extractor = SysMLDataExtractor([FIXTURES_DIR / "usage_owned_reference_consumers"])
    assert extractor.load_models()
    live = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )
    source = live.attr_by_display_path("UsageOwnedReferenceConsumers__plant__comp_a__length")
    alias = live.attr_by_display_path(
        "UsageOwnedReferenceConsumers__plant__comp_b__aliased_length"
    )
    assert every_alias_target(live) == {alias.node_id: NodeRef(source.node_id)}
    assert set(every_typed_edge(live).values()) == {NodeRef(source.node_id)}
    assert all(str(alias.node_id) not in edge for edge in live.semantic_edges()), (
        "semantic_edges() unexpectedly carries the alias lane; the comparison below "
        "was written because it does not"
    )

    encoded = encode_instance_graph(live)
    rebuilt = decode_instance_graph(encoded)

    assert rebuilt == live
    assert encode_instance_graph(rebuilt) == encoded
    assert every_alias_target(rebuilt) == every_alias_target(live)
    assert every_typed_edge(rebuilt) == every_typed_edge(live)
    assert rebuilt.semantic_edges() == live.semantic_edges()
    assert len(live.semantic_edges()) == 6
    assert project(rebuilt) == project(live)
