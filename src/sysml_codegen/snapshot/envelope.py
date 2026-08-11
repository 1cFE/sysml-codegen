"""The v6 instance-graph snapshot envelope: what a sealed snapshot may claim.

A v6 snapshot is a self-contained, license-free capture of one elaborated
instance graph. Loading it must not need the model tree, a parser, or a licence,
so everything the loader can check has to be inside the file or inside the
running environment.

**What the digest is worth.** ``integrity.digest`` is an unkeyed SHA-256. Anyone
who edits the file recomputes it, so the digest proves the document is *coherent*
— that nobody changed one part and left the rest stale — and never that it is
*authentic*. Every refusal below is written with that in mind: it has to survive a
forger who re-seals properly, or it is not a refusal.

**What is anchored, and what is not.** Three kinds of field are anchored, meaning
a forger cannot make them say something false and get past the loader:

- constants this build defines (``format``, the profile markers), compared against
  the constants;
- environment facts (SysIDE and producer versions, the pinned standard-library
  digest), compared against the process that is loading;
- the graph, whose internal consistency the codec re-derives, and which must be
  projectable and diagnostic-free.

``sources`` is **not** anchored. It is a self-declared manifest: a referent, size,
and SHA-256 per file, checked for canonical form but never against the files
themselves. Offline, the loader only cross-checks that every graph row's
``source_file`` appears in it. So a re-sealed snapshot can be re-labelled — the
sealed referents renamed consistently across the manifest and every graph row, a
fabricated row appended, or a real row's digest restated — and it will load. Those
three shapes are pinned as accepted behavior in the conformance matrix so the
limit is stated rather than implied away.

Passing ``source_roots`` is what closes them. The admission is then recomputed
from the model tree on disk and must reproduce the sealed manifest exactly, which
catches all three. **A caller that needs provenance, rather than only structure,
must supply ``source_roots``.**

This is a narrower guarantee than the earlier Item 7 candidate claimed, and a
narrower one than this module first claimed. What did change is that the envelope
no longer carries an identity field with *no* verification path at all: the
candidate's ``capture.model_name`` and ``capture.captured_at`` could not be
checked even with the sources in hand, whereas ``sources`` can.

A consequence worth relying on: capture is deterministic. The same model in the
same environment produces byte-identical snapshot files.

**What no amount of checking can prove offline.** That the sealed graph really is
the elaboration of the sealed sources means elaborating them again, which needs
the parser and a licence. Even ``source_roots`` only proves the sources are the
ones named. That proof belongs to ``capture``, which elaborates and seals in one
step.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any

import agentic_mbse

import sysml_codegen
from sysml_codegen.elaboration.graph import GraphValidationError, InstanceGraph
from sysml_codegen.extraction.source_manifest import (
    PINNED_STANDARD_LIBRARY_COUNT,
    PINNED_STANDARD_LIBRARY_SHA256,
    PINNED_SYSIDE_VERSION,
    SourceAdmission,
    SourceAdmissionError,
    admit_sources,
    validate_source_referent,
)
from sysml_codegen.snapshot.instance_graph import (
    INSTANCE_GRAPH_SCHEMA_VERSION,
    InstanceGraphCodecError,
    decode_instance_graph,
    encode_instance_graph,
)

__all__ = [
    "INSTANCE_GRAPH_SNAPSHOT_VERSION",
    "InstanceGraphSnapshotError",
    "SnapshotCertifiabilityError",
    "SnapshotCompatibilityError",
    "SnapshotIntegrityError",
    "SnapshotShapeError",
    "SnapshotStaleSourceError",
    "build_envelope",
    "canonical_json",
    "encode_envelope",
    "load_instance_graph_snapshot",
    "validate_envelope_bytes",
]

INSTANCE_GRAPH_SNAPSHOT_VERSION = 6
SNAPSHOT_FORMAT = "sysml-codegen-instance-graph"
CERTIFIABILITY_PROFILE = "projectable-instance-graph/v1"
EXPRESSION_IR_SCHEMA = "expression-ir/v1"
EXECUTABLE_PROFILE = "executable-profile/v4"
PROJECTOR_SEMANTICS = "instance-projector/v1"
INTEGRITY_ALGORITHM = "sha256"
INTEGRITY_CANONICALIZATION = "sysml-codegen-json-v1"

OUTER_FIELDS = frozenset(
    {"format", "version", "authority", "sources", "instance_graph", "integrity"}
)
AUTHORITY_FIELDS = frozenset(
    {
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
)


class InstanceGraphSnapshotError(Exception):
    """A v6 snapshot cannot be accepted as an instance-graph authority."""


class SnapshotShapeError(InstanceGraphSnapshotError):
    """The document is not syntactically and structurally valid v6 JSON."""


class SnapshotIntegrityError(InstanceGraphSnapshotError):
    """A structurally valid document disagrees with its own bound digests."""


class SnapshotCompatibilityError(InstanceGraphSnapshotError):
    """A valid document names an authority this build cannot execute."""


class SnapshotStaleSourceError(InstanceGraphSnapshotError):
    """Replacement source roots do not reproduce the sealed admission."""


class SnapshotCertifiabilityError(InstanceGraphSnapshotError):
    """The decoded graph is not an empty-diagnostic projectable authority."""


class _DuplicateKeyError(ValueError):
    pass


def canonical_json(value: object) -> bytes:
    """Encode the one canonical JSON form every v6 digest is taken over."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()


def build_envelope(graph: InstanceGraph, admission: SourceAdmission) -> dict[str, object]:
    """Build one complete, integrity-bound v6 document from a graph and its sources.

    Refuses any graph that is not projectable: a snapshot exists to be generated
    from, and a graph carrying diagnostics cannot be.
    """
    try:
        graph.require_projectable()
    except GraphValidationError as error:
        raise SnapshotCertifiabilityError(
            f"only a projectable, diagnostic-free graph may be sealed: {error}"
        ) from error

    document: dict[str, object] = {
        "format": SNAPSHOT_FORMAT,
        "version": INSTANCE_GRAPH_SNAPSHOT_VERSION,
        "authority": {
            "certifiability_profile": CERTIFIABILITY_PROFILE,
            "instance_graph_schema": INSTANCE_GRAPH_SCHEMA_VERSION,
            "expression_ir_schema": EXPRESSION_IR_SCHEMA,
            "executable_profile": EXECUTABLE_PROFILE,
            "projector_semantics": PROJECTOR_SEMANTICS,
            "syside_version": PINNED_SYSIDE_VERSION,
            "sysml_codegen_version": sysml_codegen.__version__,
            "agentic_mbse_version": agentic_mbse.__version__,
            "standard_library": admission.standard_library.envelope_data(),
        },
        "sources": admission.envelope_sources(),
        "instance_graph": json.loads(encode_instance_graph(graph)),
        "integrity": {
            "algorithm": INTEGRITY_ALGORITHM,
            "canonicalization": INTEGRITY_CANONICALIZATION,
        },
    }
    integrity = _object(document["integrity"], "integrity")
    integrity["digest"] = _outer_digest(document)
    return document


def encode_envelope(document: dict[str, object]) -> bytes:
    """Return canonical bytes, after the public loader has accepted them."""
    payload = canonical_json(document)
    validate_envelope_bytes(payload)
    return payload


def load_instance_graph_snapshot(
    snapshot_path: Path,
    *,
    source_roots: Sequence[Path] | None = None,
) -> InstanceGraph:
    """Load one validated, self-contained, projectable v6 instance graph.

    ``source_roots`` is the optional freshness check: when the caller still has
    the model tree, the admission is recomputed from disk and must reproduce the
    sealed manifest exactly.
    """
    try:
        payload = snapshot_path.read_bytes()
    except OSError as error:
        raise SnapshotShapeError(f"cannot read snapshot {snapshot_path}: {error}") from error
    return validate_envelope_bytes(payload, source_roots=source_roots)


def validate_envelope_bytes(
    payload: bytes | str,
    *,
    source_roots: Sequence[Path] | None = None,
) -> InstanceGraph:
    """Apply the normative v6 validation order and return the accepted graph.

    The order is layered on purpose, and each layer is a distinct exception type:
    shape, then the outer digest, then compatibility, then sources, then the
    graph. Nothing interprets the payload until the envelope around it has been
    accepted, so a tampered outer envelope can never be excused by a valid graph
    inside it.
    """
    document = _parse_document(payload)
    _validate_version(document)

    try:
        _validate_shape(document)
    except ValueError as error:
        raise SnapshotShapeError(f"invalid snapshot v6 shape: {error}") from error

    integrity = _object(document["integrity"], "integrity")
    if integrity["digest"] != _outer_digest(document):
        raise SnapshotIntegrityError("snapshot outer digest mismatch")

    _validate_compatibility(document)
    _validate_sources(document, source_roots)
    return _decode_graph(document)


def _validate_version(document: dict[str, Any]) -> None:
    version = document.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version != 6:
        # A v5 extraction snapshot carries no "version" key at all, so the plain
        # message would report ``None`` and leave the reader guessing what they
        # handed over. Name the format actually found.
        legacy_version = document.get("snapshot_format_version")
        found = (
            f"v{legacy_version} extraction snapshot"
            if isinstance(legacy_version, int) and not isinstance(legacy_version, bool)
            else f"snapshot version {version!r}"
        )
        raise SnapshotShapeError(
            f"unsupported or missing snapshot version: this is a {found}, but the instance-graph "
            f"route requires snapshot v6. Recapture with `sysml-codegen snapshot`."
        )


def _decode_graph(document: dict[str, Any]) -> InstanceGraph:
    instance = _object(document["instance_graph"], "instance_graph")
    expected = hashlib.sha256(
        canonical_json({"schema_version": instance["schema_version"], "graph": instance["graph"]})
    ).hexdigest()
    if instance["fingerprint"] != expected:
        raise SnapshotIntegrityError("resolved graph inner fingerprint mismatch")

    try:
        graph = decode_instance_graph(canonical_json(instance))
    except InstanceGraphCodecError as error:
        raise SnapshotShapeError(str(error)) from error
    try:
        graph.require_projectable()
    except GraphValidationError as error:
        raise SnapshotCertifiabilityError(
            f"sealed graph is not a projectable authority: {error}"
        ) from error
    return graph


def _parse_document(payload: bytes | str) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise _DuplicateKeyError(f"duplicate JSON object key {key!r}")
            result[key] = value
        return result

    try:
        raw = json.loads(payload, object_pairs_hook=reject_duplicates)
    except (_DuplicateKeyError, json.JSONDecodeError, UnicodeDecodeError, TypeError) as error:
        raise SnapshotShapeError(f"invalid snapshot JSON: {error}") from error
    if not isinstance(raw, dict):
        raise SnapshotShapeError("snapshot top level must be an object")
    return raw


# --------------------------------------------------------------------------
# Shape
# --------------------------------------------------------------------------


def _validate_shape(document: dict[str, Any]) -> None:
    _exact(document, OUTER_FIELDS, "envelope")
    _string(document["format"], "format")

    authority = _exact(document["authority"], AUTHORITY_FIELDS, "authority")
    for key in sorted(AUTHORITY_FIELDS - {"standard_library"}):
        if not _string(authority[key], f"authority.{key}"):
            raise ValueError(f"authority.{key} must be nonempty")
    standard = _exact(
        authority["standard_library"],
        {"kind", "document_count", "sha256"},
        "authority.standard_library",
    )
    _string(standard["kind"], "authority.standard_library.kind")
    if _integer(standard["document_count"], "authority.standard_library.document_count") < 1:
        raise ValueError("authority.standard_library.document_count must be positive")
    _hash_string(standard["sha256"], "authority.standard_library.sha256")

    _validate_source_manifest_shape(document["sources"])

    instance = _exact(
        document["instance_graph"],
        {"schema_version", "fingerprint", "graph"},
        "instance_graph",
    )
    _string(instance["schema_version"], "instance_graph.schema_version")
    _hash_string(instance["fingerprint"], "instance_graph.fingerprint")
    _validate_graph_shape(instance["graph"])

    integrity = _exact(
        document["integrity"], {"algorithm", "canonicalization", "digest"}, "integrity"
    )
    _string(integrity["algorithm"], "integrity.algorithm")
    _string(integrity["canonicalization"], "integrity.canonicalization")
    _hash_string(integrity["digest"], "integrity.digest")


def _validate_source_manifest_shape(raw_sources: object) -> None:
    sources = _exact(raw_sources, {"roots", "files", "fingerprint"}, "sources")
    roots = _array(sources["roots"], "sources.roots")
    if not roots:
        raise ValueError("sources.roots must be nonempty")
    for index, raw_root in enumerate(roots):
        root = _exact(raw_root, {"ordinal", "kind"}, f"sources.roots[{index}]")
        if _integer(root["ordinal"], f"sources.roots[{index}].ordinal") != index:
            raise ValueError("sources.roots ordinal must equal its array position")
        if root["kind"] not in ("file", "directory"):
            raise ValueError("sources.roots kind must be file or directory")

    files = _array(sources["files"], "sources.files")
    if not files:
        raise ValueError("sources.files must be nonempty")
    referents: list[str] = []
    for index, raw_file in enumerate(files):
        row = _exact(raw_file, {"referent", "size_bytes", "sha256"}, f"sources.files[{index}]")
        referent = validate_source_referent(_string(row["referent"], "sources.files referent"))
        if int(referent.split("/", 1)[0][len("root-") :]) >= len(roots):
            raise ValueError(f"source referent names an absent root: {referent}")
        _nonnegative_integer(row["size_bytes"], f"sources.files[{index}].size_bytes")
        _hash_string(row["sha256"], f"sources.files[{index}].sha256")
        referents.append(referent)
    if referents != sorted(set(referents)):
        raise ValueError("sources.files referents must be strictly sorted and unique")
    _hash_string(sources["fingerprint"], "sources.fingerprint")


def _validate_graph_shape(raw_graph: object) -> None:
    """Check the graph's outer shape only; the codec owns every typed field.

    Re-listing every node field here would be a second, silently divergent copy
    of the codec's contract. What this layer owns is that the payload is the five
    expected collections, so the ordering guarantee above still holds.
    """
    graph = _exact(
        raw_graph,
        {"occurrences", "attrs", "calcs", "constraints", "diagnostics"},
        "instance_graph.graph",
    )
    for key, rows in graph.items():
        for index, row in enumerate(_array(rows, f"instance_graph.graph.{key}")):
            _object(row, f"instance_graph.graph.{key}[{index}]")


# --------------------------------------------------------------------------
# Compatibility and sources
# --------------------------------------------------------------------------


def _validate_compatibility(document: dict[str, Any]) -> None:
    """Refuse a document produced by an authority this process cannot execute."""
    authority = _object(document["authority"], "authority")
    integrity = _object(document["integrity"], "integrity")
    expected = {
        "format": (document["format"], SNAPSHOT_FORMAT),
        "authority.certifiability_profile": (
            authority["certifiability_profile"],
            CERTIFIABILITY_PROFILE,
        ),
        "authority.instance_graph_schema": (
            authority["instance_graph_schema"],
            INSTANCE_GRAPH_SCHEMA_VERSION,
        ),
        "authority.expression_ir_schema": (
            authority["expression_ir_schema"],
            EXPRESSION_IR_SCHEMA,
        ),
        "authority.executable_profile": (authority["executable_profile"], EXECUTABLE_PROFILE),
        "authority.projector_semantics": (authority["projector_semantics"], PROJECTOR_SEMANTICS),
        "authority.syside_version": (authority["syside_version"], PINNED_SYSIDE_VERSION),
        "authority.sysml_codegen_version": (
            authority["sysml_codegen_version"],
            sysml_codegen.__version__,
        ),
        "authority.agentic_mbse_version": (
            authority["agentic_mbse_version"],
            agentic_mbse.__version__,
        ),
        "integrity.algorithm": (integrity["algorithm"], INTEGRITY_ALGORITHM),
        "integrity.canonicalization": (
            integrity["canonicalization"],
            INTEGRITY_CANONICALIZATION,
        ),
    }
    for label, (actual, wanted) in expected.items():
        if actual != wanted:
            raise SnapshotCompatibilityError(
                f"snapshot {label} {actual!r} is incompatible; this build requires {wanted!r}"
            )

    standard = _object(authority["standard_library"], "authority.standard_library")
    if (
        standard["kind"] != "syside-default"
        or standard["document_count"] != PINNED_STANDARD_LIBRARY_COUNT
        or standard["sha256"] != PINNED_STANDARD_LIBRARY_SHA256
    ):
        raise SnapshotCompatibilityError(
            "snapshot standard-library authority does not match the pinned "
            f"SysIDE {PINNED_SYSIDE_VERSION} environment"
        )


def _validate_sources(document: dict[str, Any], source_roots: Sequence[Path] | None) -> None:
    sources = _object(document["sources"], "sources")
    expected = hashlib.sha256(
        canonical_json({"roots": sources["roots"], "files": sources["files"]})
    ).hexdigest()
    if sources["fingerprint"] != expected:
        raise SnapshotIntegrityError("snapshot source fingerprint mismatch")

    # One-way on purpose: every graph row must name a sealed source, but a sealed
    # source need not be named by a graph row. The converse would be a false
    # invariant — the elaborator records a node's *declaration* site, so a file
    # holding only usages contributes no row at all. Measured on the fixture
    # corpus: 5 of 11 cleanly captured multi-file models have a sealed source no
    # graph row references, and occurrence records carry no source location to
    # widen the check onto. See the Slice 3A notes in the recovery plan.
    referents = {row["referent"] for row in sources["files"]}
    graph = _object(
        _object(document["instance_graph"], "instance_graph")["graph"], "instance_graph.graph"
    )
    for group in ("attrs", "calcs", "constraints"):
        for row in graph[group]:
            if row.get("source_file") not in referents:
                raise SnapshotIntegrityError(
                    f"graph source_file {row.get('source_file')!r} is absent from sources.files"
                )

    if source_roots is not None:
        _verify_replacement_roots(sources, source_roots)


def _verify_replacement_roots(sources: dict[str, Any], source_roots: Sequence[Path]) -> None:
    """Re-admit the caller's model tree and require the sealed manifest back."""
    if isinstance(source_roots, (str, bytes)) or not isinstance(source_roots, Sequence):
        raise TypeError("source_roots must be a sequence of pathlib.Path values or None")
    if any(not isinstance(path, Path) for path in source_roots):
        raise TypeError("every source_roots member must be pathlib.Path")
    try:
        with admit_sources(source_roots) as admission:
            replayed = admission.envelope_sources()
    except SourceAdmissionError as error:
        raise SnapshotStaleSourceError(
            f"replacement source roots do not reproduce the sealed admission: {error}"
        ) from error
    if replayed["fingerprint"] != sources["fingerprint"]:
        raise SnapshotStaleSourceError(
            "replacement source roots do not reproduce the sealed admission"
        )


def _outer_digest(document: dict[str, object]) -> str:
    signed = deepcopy(document)
    _object(signed["integrity"], "integrity").pop("digest", None)
    return hashlib.sha256(canonical_json(signed)).hexdigest()


# --------------------------------------------------------------------------
# Typed JSON accessors
# --------------------------------------------------------------------------


def _exact(value: object, keys: frozenset[str] | set[str], label: str) -> dict[str, Any]:
    result = _object(value, label)
    actual = set(result)
    if actual != set(keys):
        missing = sorted(set(keys) - actual)
        unknown = sorted(actual - set(keys))
        raise ValueError(f"{label} has missing keys {missing!r} and unknown keys {unknown!r}")
    return result


def _object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{label} must be an object with string keys")
    return value


def _array(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    return value


def _string(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    return value


def _integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    return value


def _nonnegative_integer(value: object, label: str) -> int:
    result = _integer(value, label)
    if result < 0:
        raise ValueError(f"{label} must be nonnegative")
    return result


def _hash_string(value: object, label: str) -> str:
    result = _string(value, label)
    if len(result) != 64 or any(character not in "0123456789abcdef" for character in result):
        raise ValueError(f"{label} must be a lower-case SHA-256 hash")
    return result
