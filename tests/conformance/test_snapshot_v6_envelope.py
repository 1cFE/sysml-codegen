"""Strict v6 envelope shape, ordering, and integrity boundaries."""

from __future__ import annotations

import hashlib
import json

import pytest

import sysml_codegen.snapshot as snapshot
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "source_identity_mixed_consumers"


def _captured(tmp_path):
    path = tmp_path / "case.json"
    snapshot.capture_snapshot([FIXTURE], path)
    return path


def _reseal_outer(document) -> None:
    signed = json.loads(json.dumps(document))
    signed["integrity"].pop("digest")
    document["integrity"]["digest"] = hashlib.sha256(
        json.dumps(
            signed,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode()
    ).hexdigest()


def _reseal_graph(document) -> None:
    instance = document["instance_graph"]
    instance["fingerprint"] = hashlib.sha256(
        json.dumps(
            {"schema_version": instance["schema_version"], "graph": instance["graph"]},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode()
    ).hexdigest()
    _reseal_outer(document)


def _write_document(tmp_path, name, document):
    path = tmp_path / name
    path.write_text(json.dumps(document))
    return path


def test_v6_envelope_is_exact_and_field_order_is_not_semantic(tmp_path) -> None:
    assert snapshot.SNAPSHOT_FORMAT_VERSION == 6
    assert callable(getattr(snapshot, "load_snapshot", None))

    path = _captured(tmp_path)
    document = json.loads(path.read_bytes())
    assert set(document) == {
        "format",
        "version",
        "authority",
        "capture",
        "sources",
        "instance_graph",
        "integrity",
    }
    assert document["format"] == "sysml-codegen-instance-graph"
    assert document["version"] == 6

    reordered = tmp_path / "reordered.json"
    reordered.write_text(json.dumps(document, indent=2, sort_keys=False))
    assert snapshot.load_snapshot(reordered) == snapshot.load_snapshot(path)


def test_duplicate_keys_and_v5_refuse_before_payload_interpretation(tmp_path) -> None:
    path = _captured(tmp_path)
    payload = path.read_bytes()
    duplicate = payload.replace(b"{", b'{"format":"duplicate",', 1)
    duplicate_path = tmp_path / "duplicate.json"
    duplicate_path.write_bytes(duplicate)

    with pytest.raises(snapshot.SnapshotFormatError, match="duplicate"):
        snapshot.load_snapshot(duplicate_path)

    document = json.loads(payload)
    document["version"] = 5
    document["instance_graph"] = "must not be inspected"
    v5_path = tmp_path / "v5.json"
    v5_path.write_text(json.dumps(document))
    with pytest.raises(snapshot.SnapshotFormatError, match="recapture with snapshot v6"):
        snapshot.load_snapshot(v5_path)


def test_outer_authority_tamper_fails_before_graph_decode(tmp_path, monkeypatch) -> None:
    path = _captured(tmp_path)
    document = json.loads(path.read_bytes())
    document["capture"]["model_name"] = "tampered"
    tampered = tmp_path / "tampered.json"
    tampered.write_text(json.dumps(document))

    decoded = False

    def forbidden_decode(_payload):
        nonlocal decoded
        decoded = True
        raise AssertionError("graph decode ran before outer integrity refusal")

    monkeypatch.setattr("sysml_codegen.snapshot.envelope.decode_instance_graph", forbidden_decode)
    with pytest.raises(snapshot.SnapshotIntegrityError, match="outer digest"):
        snapshot.load_snapshot(tampered)
    assert decoded is False


@pytest.mark.parametrize(
    ("mutate", "error_type", "message"),
    [
        (
            lambda document: document["authority"].__setitem__(
                "projector_semantics", "foreign-projector/v1"
            ),
            snapshot.SnapshotCompatibilityError,
            "projector_semantics",
        ),
        (
            lambda document: document["sources"].__setitem__("fingerprint", "0" * 64),
            snapshot.SnapshotIntegrityError,
            "source fingerprint",
        ),
    ],
)
def test_compatibility_and_source_tamper_refuse_before_graph_decode(
    tmp_path, monkeypatch, mutate, error_type, message
) -> None:
    document = json.loads(_captured(tmp_path).read_bytes())
    mutate(document)
    _reseal_outer(document)
    path = _write_document(tmp_path, "layered-tamper.json", document)
    decoded = False

    def forbidden_decode(_payload):
        nonlocal decoded
        decoded = True
        raise AssertionError("graph decode crossed an earlier validation layer")

    monkeypatch.setattr("sysml_codegen.snapshot.envelope.decode_instance_graph", forbidden_decode)
    with pytest.raises(error_type, match=message):
        snapshot.load_snapshot(path)
    assert decoded is False


def test_inner_digest_and_typed_graph_failures_have_distinct_types(tmp_path) -> None:
    original = json.loads(_captured(tmp_path).read_bytes())

    inner_tamper = json.loads(json.dumps(original))
    inner_tamper["instance_graph"]["fingerprint"] = "0" * 64
    _reseal_outer(inner_tamper)
    with pytest.raises(snapshot.SnapshotIntegrityError, match="inner fingerprint"):
        snapshot.load_snapshot(_write_document(tmp_path, "inner-tamper.json", inner_tamper))

    typed_tamper = json.loads(json.dumps(original))
    typed_tamper["instance_graph"]["graph"]["attrs"][0]["scope"]["wire"] = "[]"
    _reseal_graph(typed_tamper)
    with pytest.raises(snapshot.SnapshotFormatError, match="invalid resolved graph"):
        snapshot.load_snapshot(_write_document(tmp_path, "typed-tamper.json", typed_tamper))


def test_diagnostic_graph_is_not_certifiable(tmp_path) -> None:
    document = json.loads(_captured(tmp_path).read_bytes())
    document["instance_graph"]["graph"]["diagnostics"] = [
        {
            "code": "SI_SNAPSHOT_INVALID",
            "consumer": None,
            "consumer_display": "<test>",
            "param_name": None,
            "detail": "not certifiable",
        }
    ]
    _reseal_graph(document)
    with pytest.raises(snapshot.SnapshotCertifiabilityError, match="not certifiable"):
        snapshot.load_snapshot(_write_document(tmp_path, "diagnostic.json", document))
