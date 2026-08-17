"""The complete v6 instance-graph envelope acceptance and refusal matrix.

Every cell here is a public behavior of ``load_instance_graph_snapshot``: what a
v6 snapshot must contain, and what it must refuse. The refusals are written
against a *re-sealed* document wherever re-sealing is possible, because the
integrity digest is unkeyed — anyone who edits the file can recompute it. A
refusal that only survives while the digest is stale is not a refusal.

The identity cells are the ones the earlier candidate got wrong. It carried a
free-form ``capture.model_name`` and a ``capture.captured_at`` timestamp, so a
document could be re-labelled as a different model, re-sealed, and loaded clean.
Reintroducing either field is now refused by the exact-shape gate.

But the manifest under ``sources`` is itself self-declared, and offline the loader
can only check its form. So three re-labelling shapes still load: renaming a
sealed referent consistently, appending a fabricated file row, and restating a
real row's digest. Those cells assert the **accepting** behavior on purpose — the
limit is pinned so the matrix states the truth — paired with cells proving that
supplying ``source_roots`` refuses all three.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from sysml_codegen.snapshot import envelope as v6
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "source_identity_mixed_consumers"
A9 = FIXTURES_DIR / "unit_lane_a9"
A9_COUNT_KEY = "CATFMFEVacuum__catf_vacuum_pumping__n_pumps"

OUTER_FIELDS = ("format", "version", "authority", "sources", "instance_graph", "integrity")


@pytest.fixture(scope="module")
def captured_payload(tmp_path_factory) -> bytes:
    """One captured v6 snapshot, reused by every read-only cell in this module."""
    destination = tmp_path_factory.mktemp("v6-envelope") / "case.json"
    return capture_instance_graph_snapshot([FIXTURE], destination).read_bytes()


@pytest.fixture(scope="module")
def a9_captured_payload(tmp_path_factory) -> bytes:
    destination = tmp_path_factory.mktemp("v6-envelope-a9") / "case.json"
    return capture_instance_graph_snapshot([A9], destination).read_bytes()


def _document(payload: bytes) -> dict:
    return json.loads(payload)


def _reseal_outer(document: dict) -> dict:
    """Recompute ``integrity.digest`` the way a forger would."""
    if not isinstance(document.get("integrity"), dict):
        return document  # nothing to re-seal; the shape gate owns this document
    signed = json.loads(json.dumps(document))
    signed["integrity"].pop("digest", None)
    document["integrity"]["digest"] = hashlib.sha256(v6.canonical_json(signed)).hexdigest()
    return document


def _source_fingerprint(document: dict) -> str:
    """Recompute the sources fingerprint over the edited manifest."""
    sources = document["sources"]
    return hashlib.sha256(
        v6.canonical_json({"roots": sources["roots"], "files": sources["files"]})
    ).hexdigest()


def _reseal_graph(document: dict) -> dict:
    """Recompute the inner graph fingerprint and then the outer digest."""
    instance = document["instance_graph"]
    instance["fingerprint"] = hashlib.sha256(
        v6.canonical_json(
            {"schema_version": instance["schema_version"], "graph": instance["graph"]}
        )
    ).hexdigest()
    return _reseal_outer(document)


def _written(tmp_path: Path, name: str, document: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(document))
    return path


def _other_capture(tmp_path: Path) -> dict:
    """Capture the same model under a different source referent.

    Identity is the only thing that differs, which is exactly the axis these
    refusals have to be sensitive to.
    """
    root = tmp_path / "other-root"
    root.mkdir()
    shutil.copyfile(FIXTURE / "model.sysml", root / "other_model.sysml")
    return _document(capture_instance_graph_snapshot([root], tmp_path / "other.json").read_bytes())


# --------------------------------------------------------------------------
# Accepted shape
# --------------------------------------------------------------------------


def test_envelope_carries_only_anchored_fields(captured_payload: bytes) -> None:
    document = _document(captured_payload)
    assert set(document) == set(OUTER_FIELDS)
    assert document["format"] == "sysml-codegen-instance-graph"
    assert document["version"] == v6.INSTANCE_GRAPH_SNAPSHOT_VERSION == 6
    assert set(document["authority"]) == {
        "certifiability_profile",
        "instance_graph_schema",
        "expression_ir_schema",
        "executable_profile",
        "projector_semantics",
        "syside_version",
        "sysml_codegen_version",
        "agentic_mbse_version",
        "standard_library",
    }
    assert set(document["sources"]) == {"roots", "files", "fingerprint"}
    assert set(document["instance_graph"]) == {"schema_version", "fingerprint", "graph"}
    assert set(document["integrity"]) == {"algorithm", "canonicalization", "digest"}


def test_field_order_and_whitespace_are_not_semantic(
    tmp_path: Path, captured_payload: bytes
) -> None:
    document = _document(captured_payload)
    reordered = _written(tmp_path, "reordered.json", document)
    reordered.write_text(json.dumps(document, indent=2, sort_keys=False))
    original = _written(tmp_path, "original.json", document)
    assert v6.load_instance_graph_snapshot(reordered) == v6.load_instance_graph_snapshot(original)


def test_capture_is_deterministic_and_content_addressed(tmp_path: Path) -> None:
    """The positive form of the identity guarantee: bytes are a function of content.

    No timestamp, no directory label, nothing an editor could re-point at another
    model. Two captures of one model agree byte for byte; a different model gets a
    different digest.
    """
    first = capture_instance_graph_snapshot([FIXTURE], tmp_path / "first.json").read_bytes()
    second = capture_instance_graph_snapshot([FIXTURE], tmp_path / "second.json").read_bytes()
    assert first == second

    other = _other_capture(tmp_path)
    assert other["integrity"]["digest"] != _document(first)["integrity"]["digest"]


# --------------------------------------------------------------------------
# Version gate
# --------------------------------------------------------------------------


@pytest.mark.parametrize("version", [None, 5, 7, "6", 6.0, True])
def test_missing_current_and_future_versions_refuse_before_payload_interpretation(
    tmp_path: Path, captured_payload: bytes, version: object
) -> None:
    document = _document(captured_payload)
    if version is None:
        document.pop("version")
    else:
        document["version"] = version
    document["instance_graph"] = "must not be interpreted"
    _reseal_outer(document)
    with pytest.raises(v6.SnapshotShapeError, match="requires snapshot v6"):
        v6.load_instance_graph_snapshot(_written(tmp_path, "version.json", document))


def test_duplicate_object_keys_are_refused(tmp_path: Path, captured_payload: bytes) -> None:
    duplicate = captured_payload.replace(b"{", b'{"format":"duplicate",', 1)
    path = tmp_path / "duplicate.json"
    path.write_bytes(duplicate)
    with pytest.raises(v6.SnapshotShapeError, match="duplicate"):
        v6.load_instance_graph_snapshot(path)


def test_unreadable_and_non_object_payloads_are_refused(tmp_path: Path) -> None:
    with pytest.raises(v6.SnapshotShapeError, match="cannot read"):
        v6.load_instance_graph_snapshot(tmp_path / "absent.json")
    path = tmp_path / "array.json"
    path.write_text("[]")
    with pytest.raises(v6.SnapshotShapeError, match="top level"):
        v6.load_instance_graph_snapshot(path)


# --------------------------------------------------------------------------
# Outer shape: missing, added, wrong-typed
# --------------------------------------------------------------------------


@pytest.mark.parametrize("field", [name for name in OUTER_FIELDS if name != "version"])
def test_missing_outer_field_is_refused(
    tmp_path: Path, captured_payload: bytes, field: str
) -> None:
    document = _document(captured_payload)
    document.pop(field)
    _reseal_outer(document)
    with pytest.raises(v6.SnapshotShapeError, match=field):
        v6.load_instance_graph_snapshot(_written(tmp_path, "missing.json", document))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model_name", "some-other-model"),
        ("captured_at", "2026-08-10T00:00:00Z"),
        ("comment", "harmless"),
    ],
)
def test_added_outer_field_is_refused_even_when_resealed(
    tmp_path: Path, captured_payload: bytes, field: str, value: str
) -> None:
    """The identity cell: no unanchored declaration may be introduced.

    ``model_name`` and ``captured_at`` are the two the earlier candidate carried
    and let a forger re-point. Here they are unknown keys like any other.
    """
    document = _document(captured_payload)
    document[field] = value
    _reseal_outer(document)
    with pytest.raises(v6.SnapshotShapeError, match=field):
        v6.load_instance_graph_snapshot(_written(tmp_path, "added.json", document))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model_name", "some-other-model"),
        ("captured_at", "2026-08-10T00:00:00Z"),
    ],
)
def test_identity_declaration_cannot_be_smuggled_into_a_nested_block(
    tmp_path: Path, captured_payload: bytes, field: str, value: str
) -> None:
    document = _document(captured_payload)
    document["authority"][field] = value
    _reseal_outer(document)
    with pytest.raises(v6.SnapshotShapeError, match=field):
        v6.load_instance_graph_snapshot(_written(tmp_path, "smuggled.json", document))


@pytest.mark.parametrize(
    ("mutate", "match"),
    [
        (lambda d: d.__setitem__("format", 6), "format"),
        (lambda d: d.__setitem__("authority", []), "authority"),
        (lambda d: d.__setitem__("sources", "root-0"), "sources"),
        (lambda d: d.__setitem__("instance_graph", None), "instance_graph"),
        (lambda d: d.__setitem__("integrity", 0), "integrity"),
        (lambda d: d["sources"].__setitem__("files", {}), "sources.files"),
        (lambda d: d["sources"].__setitem__("roots", []), "sources.roots"),
        (lambda d: d["authority"].__setitem__("standard_library", "syside"), "standard_library"),
        (
            lambda d: d["authority"]["standard_library"].__setitem__("document_count", "94"),
            "document_count",
        ),
        (lambda d: d["instance_graph"].__setitem__("fingerprint", "nothex"), "fingerprint"),
        (lambda d: d["instance_graph"].__setitem__("graph", []), "graph"),
    ],
)
def test_wrong_typed_field_is_refused(
    tmp_path: Path, captured_payload: bytes, mutate, match: str
) -> None:
    document = _document(captured_payload)
    mutate(document)
    _reseal_outer(document)
    with pytest.raises(v6.SnapshotShapeError, match=match):
        v6.load_instance_graph_snapshot(_written(tmp_path, "typed.json", document))


@pytest.mark.parametrize("digest", [0, None, "0" * 63, "0" * 64 + "0", "F" * 64])
def test_a_digest_that_is_not_a_sha256_string_is_refused(
    tmp_path: Path, captured_payload: bytes, digest: object
) -> None:
    """The digest field itself is shape-checked; it cannot be re-sealed into shape."""
    document = _document(captured_payload)
    document["integrity"]["digest"] = digest
    with pytest.raises(v6.SnapshotShapeError, match="integrity.digest"):
        v6.load_instance_graph_snapshot(_written(tmp_path, "digest.json", document))


def test_source_referent_shape_is_enforced(tmp_path: Path, captured_payload: bytes) -> None:
    document = _document(captured_payload)
    document["sources"]["files"][0]["referent"] = "/absolute/model.sysml"
    _reseal_outer(document)
    with pytest.raises(v6.SnapshotShapeError, match="referent"):
        v6.load_instance_graph_snapshot(_written(tmp_path, "referent.json", document))


# --------------------------------------------------------------------------
# Integrity layers
# --------------------------------------------------------------------------


def test_valid_inner_graph_inside_a_tampered_outer_envelope_never_reaches_decode(
    tmp_path: Path, captured_payload: bytes, monkeypatch
) -> None:
    """The hard case: the graph is untouched and would decode cleanly.

    The outer envelope is edited without re-sealing, so the document must be
    refused on the outer digest before any payload interpretation happens.
    """
    document = _document(captured_payload)
    document["authority"]["syside_version"] = "9.9.9"
    path = _written(tmp_path, "outer-tamper.json", document)

    def forbidden_decode(_payload):
        raise AssertionError("graph decode ran before the outer integrity refusal")

    monkeypatch.setattr(v6, "decode_instance_graph", forbidden_decode)
    with pytest.raises(v6.SnapshotIntegrityError, match="outer digest"):
        v6.load_instance_graph_snapshot(path)


def test_inner_fingerprint_tamper_is_an_integrity_failure(
    tmp_path: Path, captured_payload: bytes
) -> None:
    document = _document(captured_payload)
    document["instance_graph"]["fingerprint"] = "0" * 64
    _reseal_outer(document)
    with pytest.raises(v6.SnapshotIntegrityError, match="inner fingerprint"):
        v6.load_instance_graph_snapshot(_written(tmp_path, "inner.json", document))


def test_source_fingerprint_tamper_refuses_before_graph_decode(
    tmp_path: Path, captured_payload: bytes, monkeypatch
) -> None:
    document = _document(captured_payload)
    document["sources"]["fingerprint"] = "0" * 64
    _reseal_outer(document)
    path = _written(tmp_path, "source-fingerprint.json", document)

    def forbidden_decode(_payload):
        raise AssertionError("graph decode crossed an earlier validation layer")

    monkeypatch.setattr(v6, "decode_instance_graph", forbidden_decode)
    with pytest.raises(v6.SnapshotIntegrityError, match="source fingerprint"):
        v6.load_instance_graph_snapshot(path)


@pytest.mark.parametrize("group", ["attrs", "calcs", "constraints", "occurrences"])
def test_added_and_removed_graph_row_fields_are_refused(
    tmp_path: Path, captured_payload: bytes, group: str
) -> None:
    """The codec owns the node contract, and it is exact in both directions."""
    added = _document(captured_payload)
    added["instance_graph"]["graph"][group][0]["smuggled"] = "value"
    _reseal_graph(added)
    with pytest.raises(v6.SnapshotShapeError, match="smuggled"):
        v6.load_instance_graph_snapshot(_written(tmp_path, f"added-{group}.json", added))

    removed = _document(captured_payload)
    row = removed["instance_graph"]["graph"][group][0]
    dropped = sorted(row)[0]
    del row[dropped]
    _reseal_graph(removed)
    with pytest.raises(v6.SnapshotShapeError, match=dropped):
        v6.load_instance_graph_snapshot(_written(tmp_path, f"removed-{group}.json", removed))


def test_typed_graph_tamper_is_a_shape_failure(tmp_path: Path, captured_payload: bytes) -> None:
    document = _document(captured_payload)
    document["instance_graph"]["graph"]["attrs"][0]["scope"]["wire"] = "[]"
    _reseal_graph(document)
    with pytest.raises(v6.SnapshotShapeError):
        v6.load_instance_graph_snapshot(_written(tmp_path, "typed-graph.json", document))


# --------------------------------------------------------------------------
# Graph replacement
# --------------------------------------------------------------------------


def test_graph_replacement_is_refused_at_every_reseal_depth(
    tmp_path: Path, captured_payload: bytes
) -> None:
    """Swapping another model's graph in fails whether or not the forger re-seals."""
    other_graph = _other_capture(tmp_path)["instance_graph"]

    raw = _document(captured_payload)
    raw["instance_graph"] = json.loads(json.dumps(other_graph))
    with pytest.raises(v6.SnapshotIntegrityError, match="outer digest"):
        v6.load_instance_graph_snapshot(_written(tmp_path, "swap-raw.json", raw))

    resealed = _document(captured_payload)
    resealed["instance_graph"] = json.loads(json.dumps(other_graph))
    _reseal_outer(resealed)
    with pytest.raises(v6.SnapshotIntegrityError, match="absent from sources.files"):
        v6.load_instance_graph_snapshot(_written(tmp_path, "swap-outer.json", resealed))

    stale_fingerprint = _document(captured_payload)
    stale_fingerprint["instance_graph"]["graph"] = json.loads(json.dumps(other_graph["graph"]))
    _reseal_outer(stale_fingerprint)
    with pytest.raises(v6.SnapshotIntegrityError, match="absent from sources.files"):
        v6.load_instance_graph_snapshot(_written(tmp_path, "swap-graph.json", stale_fingerprint))


def test_source_manifest_replacement_is_refused(tmp_path: Path, captured_payload: bytes) -> None:
    """Keeping the graph and swapping in another model's sources is refused too."""
    document = _document(captured_payload)
    document["sources"] = json.loads(json.dumps(_other_capture(tmp_path)["sources"]))
    _reseal_outer(document)
    with pytest.raises(v6.SnapshotIntegrityError, match="absent from sources.files"):
        v6.load_instance_graph_snapshot(_written(tmp_path, "swap-sources.json", document))


# --------------------------------------------------------------------------
# Source re-labelling: what a re-sealing forger can still do offline
# --------------------------------------------------------------------------


def _renamed_referent(document: dict, replacement: str) -> dict:
    """Rename the sealed referent consistently, the way a careful forger would."""
    original = document["sources"]["files"][0]["referent"]
    document["sources"]["files"][0]["referent"] = replacement
    for group in ("attrs", "calcs", "constraints"):
        for row in document["instance_graph"]["graph"][group]:
            if row["source_file"] == original:
                row["source_file"] = replacement
    document["sources"]["fingerprint"] = _source_fingerprint(document)
    return _reseal_graph(document)


def _appended_phantom_source(document: dict) -> dict:
    """Append a fabricated file row that no graph row references."""
    document["sources"]["files"].append(
        {"referent": "root-0/zz_fabricated.sysml", "size_bytes": 1234, "sha256": "ab" * 32}
    )
    document["sources"]["files"].sort(key=lambda row: row["referent"])
    document["sources"]["fingerprint"] = _source_fingerprint(document)
    return _reseal_outer(document)


def _restated_source_bytes(document: dict) -> dict:
    """Restate a real row's sealed size and digest."""
    document["sources"]["files"][0]["sha256"] = "cd" * 32
    document["sources"]["files"][0]["size_bytes"] = 99999
    document["sources"]["fingerprint"] = _source_fingerprint(document)
    return _reseal_outer(document)


RELABELLINGS = [
    pytest.param(
        lambda document: _renamed_referent(document, "root-0/customer_proprietary.sysml"),
        id="renamed-referent",
    ),
    pytest.param(_appended_phantom_source, id="appended-phantom-source"),
    pytest.param(_restated_source_bytes, id="restated-source-bytes"),
]


@pytest.mark.parametrize("relabel", RELABELLINGS)
def test_a_resealed_relabelling_is_accepted_offline(
    tmp_path: Path, captured_payload: bytes, relabel
) -> None:
    """An accepted, documented limit — not a guarantee, and not an oversight.

    ``sources`` is a self-declared manifest. Offline the loader checks its form
    and that every graph row names a sealed source; it cannot check the manifest
    against files it is not allowed to read. A forger who re-seals correctly can
    therefore re-label a snapshot, and does.

    These cells exist so the matrix states that rather than implying closure. The
    refusal lives in the freshness path below, and ``envelope.py``'s module
    docstring says a caller that needs provenance must supply ``source_roots``.
    """
    document = relabel(_document(captured_payload))
    graph = v6.load_instance_graph_snapshot(_written(tmp_path, "relabelled.json", document))
    assert graph.calcs, "the forged snapshot loads as a full, usable graph"


@pytest.mark.parametrize("relabel", RELABELLINGS)
def test_source_roots_refuse_every_resealed_relabelling(tmp_path: Path, relabel) -> None:
    """The freshness path is what actually closes the three shapes above."""
    root = tmp_path / "model-tree"
    shutil.copytree(FIXTURE, root)
    captured = capture_instance_graph_snapshot([root], tmp_path / "captured.json")
    assert v6.load_instance_graph_snapshot(captured, source_roots=[root])

    document = relabel(_document(captured.read_bytes()))
    forged = _written(tmp_path, "relabelled.json", document)
    with pytest.raises(v6.SnapshotStaleSourceError, match="reproduce"):
        v6.load_instance_graph_snapshot(forged, source_roots=[root])


def test_a_sealed_source_need_not_be_referenced_by_any_graph_row(tmp_path: Path) -> None:
    """Why the membership check is one-way, pinned against a real fixture.

    The elaborator records a node's declaration site, so a file holding only
    usages contributes no graph row at all. Requiring the converse — every sealed
    source referenced by some row — would encode a false invariant and reject
    legitimate snapshots. ``agg_literal_probe`` is one: its ``design.sysml`` is
    sealed and referenced by nothing.
    """
    captured = capture_instance_graph_snapshot(
        [FIXTURES_DIR / "agg_literal_probe"], tmp_path / "probe.json"
    )
    document = _document(captured.read_bytes())
    sealed = {row["referent"] for row in document["sources"]["files"]}
    referenced = {
        row["source_file"]
        for group in ("attrs", "calcs", "constraints")
        for row in document["instance_graph"]["graph"][group]
    }
    assert sealed == {"root-0/design.sysml", "root-0/library.sysml"}
    assert referenced == {"root-0/library.sysml"}
    assert v6.load_instance_graph_snapshot(captured)


# --------------------------------------------------------------------------
# Compatibility
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mutate", "match"),
    [
        (lambda d: d.__setitem__("format", "foreign-format"), "format"),
        (
            lambda d: d["authority"].__setitem__("projector_semantics", "foreign-projector/v1"),
            "projector_semantics",
        ),
        (
            lambda d: d["authority"].__setitem__("executable_profile", "executable-profile/v3"),
            "executable_profile",
        ),
        (
            lambda d: d["authority"].__setitem__("instance_graph_schema", "instance-graph/v1"),
            "instance_graph_schema",
        ),
        (lambda d: d["authority"].__setitem__("syside_version", "0.8.3"), "syside_version"),
        (
            lambda d: d["authority"].__setitem__("sysml_codegen_version", "0.0.1"),
            "sysml_codegen_version",
        ),
        (
            lambda d: d["authority"].__setitem__("agentic_mbse_version", "0.0.1"),
            "agentic_mbse_version",
        ),
        (
            lambda d: d["authority"]["standard_library"].__setitem__("document_count", 93),
            "standard-library",
        ),
        (
            lambda d: d["authority"]["standard_library"].__setitem__("sha256", "0" * 64),
            "standard-library",
        ),
        (
            lambda d: d["integrity"].__setitem__("canonicalization", "rfc8785"),
            "canonicalization",
        ),
    ],
)
def test_foreign_authority_is_refused_before_graph_decode(
    tmp_path: Path, captured_payload: bytes, monkeypatch, mutate, match: str
) -> None:
    document = _document(captured_payload)
    mutate(document)
    _reseal_outer(document)
    path = _written(tmp_path, "authority.json", document)

    def forbidden_decode(_payload):
        raise AssertionError("graph decode crossed the compatibility layer")

    monkeypatch.setattr(v6, "decode_instance_graph", forbidden_decode)
    with pytest.raises(v6.SnapshotCompatibilityError, match=match):
        v6.load_instance_graph_snapshot(path)


# --------------------------------------------------------------------------
# Certifiability
# --------------------------------------------------------------------------


def test_a_graph_carrying_diagnostics_is_not_certifiable(
    tmp_path: Path, captured_payload: bytes
) -> None:
    document = _document(captured_payload)
    document["instance_graph"]["graph"]["diagnostics"] = [
        {
            "code": "SI_SNAPSHOT_INVALID",
            "consumer": None,
            "consumer_display": "<test>",
            "param_name": None,
            "detail": "not certifiable",
            "reference": None,
            "source_file": None,
            "source_line": None,
        }
    ]
    _reseal_graph(document)
    with pytest.raises(v6.SnapshotCertifiabilityError):
        v6.load_instance_graph_snapshot(_written(tmp_path, "diagnostic.json", document))


def test_resealed_unit_collision_is_not_certifiable(
    tmp_path: Path, a9_captured_payload: bytes
) -> None:
    document = _document(a9_captured_payload)
    [constraint] = document["instance_graph"]["graph"]["constraints"]
    [count] = [item for item in constraint["inputs"] if item["name"] == "count"]
    assert count["metadata"]["unit"] == "Dimensionless"
    count["metadata"]["unit"] = "cm"
    _reseal_graph(document)

    with pytest.raises(v6.SnapshotCertifiabilityError) as excinfo:
        v6.load_instance_graph_snapshot(_written(tmp_path, "unit-collision.json", document))

    [diagnostic] = excinfo.value.diagnostics
    assert diagnostic.code.value == "SI_RENDERING_COLLISION"
    assert A9_COUNT_KEY in diagnostic.detail
    assert "conflicting projected metadata" in diagnostic.detail


def test_every_refusal_shares_one_public_base_type(tmp_path: Path, captured_payload: bytes) -> None:
    document = _document(captured_payload)
    document["version"] = 5
    with pytest.raises(v6.InstanceGraphSnapshotError):
        v6.load_instance_graph_snapshot(_written(tmp_path, "base.json", document))
    for subclass in (
        v6.SnapshotShapeError,
        v6.SnapshotIntegrityError,
        v6.SnapshotCompatibilityError,
        v6.SnapshotStaleSourceError,
        v6.SnapshotCertifiabilityError,
    ):
        assert issubclass(subclass, v6.InstanceGraphSnapshotError)
