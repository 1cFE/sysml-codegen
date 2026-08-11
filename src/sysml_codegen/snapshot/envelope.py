"""Canonical, strict v6 instance-graph snapshot envelope."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Sequence
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import agentic_mbse
import syside

import sysml_codegen
from sysml_codegen.elaboration.graph import GraphValidationError, InstanceGraph
from sysml_codegen.snapshot.instance_graph import (
    INSTANCE_GRAPH_SCHEMA_VERSION,
    InstanceGraphCodecError,
    decode_instance_graph,
    encode_instance_graph,
)
from sysml_codegen.snapshot.source_manifest import (
    PINNED_STANDARD_LIBRARY_COUNT,
    PINNED_STANDARD_LIBRARY_SHA256,
    SourceAdmission,
    SourceAdmissionError,
    admit_sources,
)

__all__ = [
    "SNAPSHOT_FORMAT_VERSION",
    "SnapshotCertifiabilityError",
    "SnapshotCompatibilityError",
    "SnapshotFormatError",
    "SnapshotIntegrityError",
    "SnapshotStaleSourceError",
    "build_snapshot_envelope",
    "canonical_json",
    "encode_snapshot_envelope",
    "load_snapshot",
    "validate_snapshot_bytes",
]

SNAPSHOT_FORMAT_VERSION = 6
SNAPSHOT_FORMAT = "sysml-codegen-instance-graph"
CERTIFIABILITY_PROFILE = "projectable-instance-graph/v1"
EXPRESSION_IR_SCHEMA = "expression-ir/v1"
EXECUTABLE_PROFILE = "executable-profile/v4"
PROJECTOR_SEMANTICS = "instance-projector/v1"
INTEGRITY_CANONICALIZATION = "sysml-codegen-json-v1"

_HASH = re.compile(r"[0-9a-f]{64}\Z")
_REFERENT = re.compile(
    r"root-(?:0|[1-9][0-9]*)/"
    r"(?:[A-Za-z0-9._~-]|%[0-9A-F]{2})+"
    r"(?:/(?:[A-Za-z0-9._~-]|%[0-9A-F]{2})+)*"
    r"\.(?:sysml|kerml)\Z"
)
_UTC_TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?Z\Z"
)


class SnapshotFormatError(Exception):
    """A snapshot is not syntactically and structurally valid v6 JSON."""


class SnapshotIntegrityError(SnapshotFormatError):
    """A structurally valid snapshot disagrees with its bound digest or sources."""


class SnapshotCompatibilityError(SnapshotFormatError):
    """A valid snapshot names an authority this implementation cannot execute."""


class SnapshotStaleSourceError(SnapshotFormatError):
    """Optional replacement roots do not reproduce the captured admission."""


class SnapshotCertifiabilityError(SnapshotFormatError):
    """A decoded graph is not an empty-diagnostic projectable authority."""


class _DuplicateKeyError(ValueError):
    pass


def canonical_json(value: object) -> bytes:
    """Encode the v6 canonical JSON form."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()


def build_snapshot_envelope(
    graph: InstanceGraph,
    admission: SourceAdmission,
    *,
    model_name: str,
    design_path_filter: str = "",
    captured_at: str | None = None,
) -> dict[str, object]:
    """Construct a complete integrity-bound v6 document in memory."""
    graph.validate()
    graph.require_projectable()
    if graph.diagnostics:
        raise SnapshotCertifiabilityError("public snapshot graphs must have no diagnostics")
    capture_options: dict[str, object] = {"design_path_filter": design_path_filter}
    document: dict[str, object] = {
        "format": SNAPSHOT_FORMAT,
        "version": SNAPSHOT_FORMAT_VERSION,
        "authority": {
            "certifiability_profile": CERTIFIABILITY_PROFILE,
            "instance_graph_schema": INSTANCE_GRAPH_SCHEMA_VERSION,
            "expression_ir_schema": EXPRESSION_IR_SCHEMA,
            "executable_profile": EXECUTABLE_PROFILE,
            "projector_semantics": PROJECTOR_SEMANTICS,
            "syside_version": syside.__version__,
            "standard_library": admission.standard_library.envelope_data(),
        },
        "capture": {
            "model_name": model_name,
            "captured_at": captured_at or datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "producer": {
                "sysml_codegen_version": sysml_codegen.__version__,
                "agentic_mbse_version": agentic_mbse.__version__,
            },
            "options": capture_options,
        },
        "sources": admission.envelope_sources(capture_options),
        "instance_graph": json.loads(encode_instance_graph(graph)),
        "integrity": {
            "algorithm": "sha256",
            "canonicalization": INTEGRITY_CANONICALIZATION,
            "digest": "0" * 64,
        },
    }
    integrity = _object(document["integrity"], "integrity")
    integrity["digest"] = _outer_digest(document)
    return document


def encode_snapshot_envelope(document: dict[str, object]) -> bytes:
    """Return canonical bytes after the public validator accepts the document."""
    payload = canonical_json(document)
    validate_snapshot_bytes(payload)
    return payload


def load_snapshot(
    snapshot_path: Path,
    *,
    source_roots: Sequence[Path] | None = None,
) -> InstanceGraph:
    """Load one validated, self-contained and projectable v6 instance graph."""
    try:
        payload = snapshot_path.read_bytes()
    except OSError as error:
        raise SnapshotFormatError(f"cannot read snapshot {snapshot_path}: {error}") from error
    return validate_snapshot_bytes(payload, source_roots=source_roots)


def validate_snapshot_bytes(
    payload: bytes | str,
    *,
    source_roots: Sequence[Path] | None = None,
) -> InstanceGraph:
    """Apply the normative v6 validation and failure order."""
    document = _parse_document(payload)

    version = document.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version != 6:
        raise SnapshotFormatError(
            f"unsupported or missing snapshot version {version!r}; recapture with snapshot v6"
        )

    try:
        _validate_exact_shape(document)
    except (TypeError, ValueError) as error:
        raise SnapshotFormatError(f"invalid snapshot v6 shape: {error}") from error
    actual_outer = _hash_string(
        _object(document["integrity"], "integrity")["digest"], "integrity.digest"
    )
    if actual_outer != _outer_digest(document):
        raise SnapshotIntegrityError("snapshot outer digest mismatch")

    _validate_compatibility(document)
    _validate_sources(document, source_roots)

    instance_document = _object(document["instance_graph"], "instance_graph")
    graph_data = _object(instance_document["graph"], "instance_graph.graph")
    expected_inner = hashlib.sha256(
        canonical_json(
            {
                "schema_version": instance_document["schema_version"],
                "graph": graph_data,
            }
        )
    ).hexdigest()
    if instance_document["fingerprint"] != expected_inner:
        raise SnapshotIntegrityError("resolved graph inner fingerprint mismatch")
    try:
        graph = decode_instance_graph(canonical_json(instance_document))
    except InstanceGraphCodecError as error:
        if "fingerprint mismatch" in str(error):
            raise SnapshotIntegrityError(str(error)) from error
        raise SnapshotFormatError(str(error)) from error
    try:
        graph.validate()
        if graph.diagnostics:
            raise GraphValidationError(graph.diagnostics)
        graph.require_projectable()
    except GraphValidationError as error:
        raise SnapshotCertifiabilityError(str(error)) from error
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
        raise SnapshotFormatError(f"invalid snapshot JSON: {error}") from error
    if not isinstance(raw, dict):
        raise SnapshotFormatError("snapshot top level must be an object")
    return raw


def _validate_exact_shape(document: dict[str, Any]) -> None:
    _exact(
        document,
        {"format", "version", "authority", "capture", "sources", "instance_graph", "integrity"},
        "envelope",
    )
    _string(document["format"], "format")
    _integer(document["version"], "version")

    authority = _exact(
        document["authority"],
        {
            "certifiability_profile",
            "instance_graph_schema",
            "expression_ir_schema",
            "executable_profile",
            "projector_semantics",
            "syside_version",
            "standard_library",
        },
        "authority",
    )
    for key in (
        "certifiability_profile",
        "instance_graph_schema",
        "expression_ir_schema",
        "executable_profile",
        "projector_semantics",
        "syside_version",
    ):
        _string(authority[key], f"authority.{key}")
    standard = _exact(
        authority["standard_library"], {"kind", "document_count", "sha256"}, "standard_library"
    )
    _string(standard["kind"], "standard_library.kind")
    if _integer(standard["document_count"], "standard_library.document_count") < 1:
        raise ValueError("standard_library.document_count must be positive")
    _hash_string(standard["sha256"], "standard_library.sha256")

    capture = _exact(
        document["capture"], {"model_name", "captured_at", "producer", "options"}, "capture"
    )
    if not _string(capture["model_name"], "capture.model_name"):
        raise ValueError("capture.model_name must be nonempty")
    timestamp = _string(capture["captured_at"], "capture.captured_at")
    if _UTC_TIMESTAMP.fullmatch(timestamp) is None:
        raise ValueError("capture.captured_at must be an RFC-3339 UTC timestamp")
    producer = _exact(
        capture["producer"], {"sysml_codegen_version", "agentic_mbse_version"}, "capture.producer"
    )
    for key in ("sysml_codegen_version", "agentic_mbse_version"):
        if not _string(producer[key], f"capture.producer.{key}"):
            raise ValueError(f"capture.producer.{key} must be nonempty")
    options = _exact(capture["options"], {"design_path_filter"}, "capture.options")
    _string(options["design_path_filter"], "capture.options.design_path_filter")

    sources = _exact(document["sources"], {"roots", "files", "fingerprint"}, "sources")
    roots = _array(sources["roots"], "sources.roots")
    if not roots:
        raise ValueError("sources.roots must be nonempty")
    for index, raw_root in enumerate(roots):
        root = _exact(raw_root, {"ordinal", "kind"}, f"sources.roots[{index}]")
        ordinal = _integer(root["ordinal"], f"sources.roots[{index}].ordinal")
        if ordinal != index:
            raise ValueError("source root ordinal must equal its array position")
        if root["kind"] not in ("file", "directory"):
            raise ValueError("source root kind must be file or directory")
    files = _array(sources["files"], "sources.files")
    if not files:
        raise ValueError("sources.files must be nonempty")
    referents: list[str] = []
    for index, raw_file in enumerate(files):
        file_row = _exact(raw_file, {"referent", "size_bytes", "sha256"}, f"sources.files[{index}]")
        referent = _string(file_row["referent"], f"sources.files[{index}].referent")
        if _REFERENT.fullmatch(referent) is None:
            raise ValueError(f"invalid canonical source referent {referent!r}")
        if int(referent.split("/", 1)[0][5:]) >= len(roots):
            raise ValueError(f"source referent names absent root: {referent}")
        if _integer(file_row["size_bytes"], f"sources.files[{index}].size_bytes") < 0:
            raise ValueError("source size must be nonnegative")
        _hash_string(file_row["sha256"], f"sources.files[{index}].sha256")
        referents.append(referent)
    if referents != sorted(set(referents)):
        raise ValueError("source referents must be strictly sorted and unique")
    _hash_string(sources["fingerprint"], "sources.fingerprint")

    instance = _exact(
        document["instance_graph"], {"schema_version", "fingerprint", "graph"}, "instance_graph"
    )
    _string(instance["schema_version"], "instance_graph.schema_version")
    _hash_string(instance["fingerprint"], "instance_graph.fingerprint")
    _validate_graph(instance["graph"])

    integrity = _exact(
        document["integrity"], {"algorithm", "canonicalization", "digest"}, "integrity"
    )
    _string(integrity["algorithm"], "integrity.algorithm")
    _string(integrity["canonicalization"], "integrity.canonicalization")
    _hash_string(integrity["digest"], "integrity.digest")


def _validate_graph(raw_graph: object) -> None:
    graph = _exact(
        raw_graph, {"occurrences", "attrs", "calcs", "constraints", "diagnostics"}, "graph"
    )
    occurrences = _array(graph["occurrences"], "graph.occurrences")
    attrs = _array(graph["attrs"], "graph.attrs")
    calcs = _array(graph["calcs"], "graph.calcs")
    constraints = _array(graph["constraints"], "graph.constraints")
    diagnostics = _array(graph["diagnostics"], "graph.diagnostics")
    occurrence_ids: list[str] = []
    for index, raw in enumerate(occurrences):
        row = _exact(
            raw,
            {
                "occurrence_id",
                "parent_id",
                "containment_slot",
                "occurrence_index",
                "effective_usage_id",
                "effective_type_ids",
                "display_segment",
                "package_display",
            },
            f"occurrence[{index}]",
        )
        occurrence_ids.append(_wire(row["occurrence_id"], "occurrence_id"))
        _nullable_wire(row["parent_id"], "parent_id")
        _wire(row["containment_slot"], "containment_slot")
        if (
            row["occurrence_index"] is not None
            and _integer(row["occurrence_index"], "occurrence_index") < 0
        ):
            raise ValueError("occurrence_index must be nonnegative or null")
        _wire(row["effective_usage_id"], "effective_usage_id")
        effective_types = [
            _wire(value, "effective_type_id")
            for value in _array(row["effective_type_ids"], "effective_type_ids")
        ]
        if len(effective_types) != len(set(effective_types)):
            raise ValueError("effective_type_ids must be unique")
        if not _string(row["display_segment"], "display_segment"):
            raise ValueError("display_segment must be nonempty")
        _nullable_string(row["package_display"], "package_display")
    _strictly_sorted(occurrence_ids, "occurrence identities")

    attr_ids: list[str] = []
    for index, raw in enumerate(attrs):
        row = _exact(
            raw,
            {
                "node_id",
                "scope",
                "declaration_id",
                "slot_id",
                "display_path",
                "display_name",
                "declaration_qn",
                "value",
                "value_site",
                "alias_target",
                "is_alias",
                "alias_shape",
                "source_file",
                "source_line",
                "owner_qualified_name",
            },
            f"attribute[{index}]",
        )
        attr_ids.append(_wire(row["node_id"], "attribute.node_id"))
        _validate_scope(row["scope"])
        _wire(row["declaration_id"], "attribute.declaration_id")
        _wire(row["slot_id"], "attribute.slot_id")
        for key in ("display_path", "display_name", "declaration_qn", "owner_qualified_name"):
            _string(row[key], f"attribute.{key}")
        _nullable_scalar(row["value"], "attribute.value")
        if row["value_site"] not in (
            "none",
            "definition_default",
            "specialized_def",
            "occurrence_override",
        ):
            raise ValueError("invalid attribute value_site")
        if row["alias_target"] is not None:
            _validate_edge(row["alias_target"])
        _boolean(row["is_alias"], "attribute.is_alias")
        _nullable_string(row["alias_shape"], "attribute.alias_shape")
        _string(row["source_file"], "attribute.source_file")
        _nonnegative_integer(row["source_line"], "attribute.source_line")
    _strictly_sorted(attr_ids, "attribute identities")

    calc_ids: list[str] = []
    for index, raw in enumerate(calcs):
        row = _exact(
            raw,
            {
                "node_id",
                "scope",
                "declaration_id",
                "display_path",
                "display_name",
                "calc_def_name",
                "calc_def_qualified_name",
                "inputs",
                "outputs",
                "unbound_formals",
                "is_computed",
                "expression_ir",
                "aggregation_reference_ordinals",
                "compilability",
                "auto_impl_context",
                "doc_comment",
                "calc_expressions",
                "calculation_definition_id",
                "compilation_definition_id",
                "compiled_output_ids",
                "source_file",
                "source_line",
            },
            f"calculation[{index}]",
        )
        calc_ids.append(_wire(row["node_id"], "calculation.node_id"))
        _validate_scope(row["scope"])
        _wire(row["declaration_id"], "calculation.declaration_id")
        for key in (
            "display_path",
            "display_name",
            "calc_def_name",
            "calc_def_qualified_name",
            "source_file",
        ):
            _string(row[key], f"calculation.{key}")
        _validate_inputs(row["inputs"])
        _validate_outputs(row["outputs"])
        _unique_wires(row["unbound_formals"], "calculation.unbound_formals")
        _boolean(row["is_computed"], "calculation.is_computed")
        if row["expression_ir"] is not None:
            _validate_expression(row["expression_ir"])
        ordinals = [
            _nonnegative_integer(value, "aggregation ordinal")
            for value in _array(
                row["aggregation_reference_ordinals"], "aggregation_reference_ordinals"
            )
        ]
        _strictly_sorted(ordinals, "aggregation ordinals")
        if row["compilability"] not in (
            "fully_compilable",
            "partially_compilable",
            "manual_required",
        ):
            raise ValueError("invalid calculation compilability")
        if row["auto_impl_context"] is not None:
            _validate_auto(row["auto_impl_context"])
        _nullable_string(row["doc_comment"], "calculation.doc_comment")
        for value in _array(row["calc_expressions"], "calculation.calc_expressions"):
            _string(value, "calculation expression")
        _nullable_wire(row["calculation_definition_id"], "calculation_definition_id")
        _nullable_wire(row["compilation_definition_id"], "compilation_definition_id")
        _unique_wires(row["compiled_output_ids"], "compiled_output_ids")
        _nonnegative_integer(row["source_line"], "calculation.source_line")
    _strictly_sorted(calc_ids, "calculation identities")

    constraint_ids: list[str] = []
    for index, raw in enumerate(constraints):
        row = _exact(
            raw,
            {
                "node_id",
                "scope",
                "declaration_id",
                "display_path",
                "display_name",
                "constraint_def_name",
                "inputs",
                "unbound_formals",
                "predicate_ir",
                "source_form",
                "owner_kind",
                "owner_qualified_name",
                "usage_qualified_name",
                "membership_kind",
                "predicate_source_key",
                "is_negated",
                "definition_qualified_name",
                "eligibility",
                "effective_definition_id",
                "exclusion_reasons",
                "exclusion_location",
                "source_file",
                "source_line",
            },
            f"constraint[{index}]",
        )
        constraint_ids.append(_wire(row["node_id"], "constraint.node_id"))
        _validate_scope(row["scope"])
        _wire(row["declaration_id"], "constraint.declaration_id")
        for key in (
            "display_path",
            "display_name",
            "constraint_def_name",
            "owner_qualified_name",
            "usage_qualified_name",
            "predicate_source_key",
            "source_file",
        ):
            _string(row[key], f"constraint.{key}")
        for key in ("source_form", "owner_kind"):
            if not _string(row[key], f"constraint.{key}"):
                raise ValueError(f"constraint.{key} must be nonempty")
        _validate_inputs(row["inputs"])
        _unique_wires(row["unbound_formals"], "constraint.unbound_formals")
        if row["predicate_ir"] is not None:
            _validate_expression(row["predicate_ir"])
        _nullable_string(row["membership_kind"], "constraint.membership_kind")
        _boolean(row["is_negated"], "constraint.is_negated")
        _nullable_string(row["definition_qualified_name"], "definition_qualified_name")
        if row["eligibility"] not in ("admit", "block", "non_numerical", "unassessed"):
            raise ValueError("invalid constraint eligibility")
        _nullable_wire(row["effective_definition_id"], "effective_definition_id")
        for value in _array(row["exclusion_reasons"], "constraint.exclusion_reasons"):
            _string(value, "constraint exclusion reason")
        _nullable_string(row["exclusion_location"], "constraint.exclusion_location")
        _nonnegative_integer(row["source_line"], "constraint.source_line")
    _strictly_sorted(constraint_ids, "constraint identities")

    for index, raw in enumerate(diagnostics):
        row = _exact(
            raw,
            {"code", "consumer", "consumer_display", "param_name", "detail"},
            f"diagnostic[{index}]",
        )
        _string(row["code"], "diagnostic.code")
        _nullable_wire(row["consumer"], "diagnostic.consumer")
        _string(row["consumer_display"], "diagnostic.consumer_display")
        _nullable_string(row["param_name"], "diagnostic.param_name")
        _string(row["detail"], "diagnostic.detail")


def _validate_inputs(raw_inputs: object) -> None:
    keys: list[bytes] = []
    for index, raw in enumerate(_array(raw_inputs, "inputs")):
        row = _exact(raw, {"port", "edge", "name", "metadata"}, f"input[{index}]")
        _validate_port(row["port"])
        keys.append(canonical_json(row["port"]))
        if row["edge"] is not None:
            _validate_edge(row["edge"])
        _string(row["name"], "input.name")
        _validate_metadata(row["metadata"])
    _strictly_sorted(keys, "input ports")


def _validate_outputs(raw_outputs: object) -> None:
    declarations: list[str] = []
    for index, raw in enumerate(_array(raw_outputs, "outputs")):
        row = _exact(raw, {"declaration", "port", "name", "metadata"}, f"output[{index}]")
        declarations.append(_wire(row["declaration"], "output.declaration"))
        port = _exact(row["port"], {"calculation", "output"}, "output.port")
        _wire(port["calculation"], "output.port.calculation")
        _wire(port["output"], "output.port.output")
        _string(row["name"], "output.name")
        _validate_metadata(row["metadata"])
    _strictly_sorted(declarations, "output declarations")


def _validate_scope(raw: object) -> None:
    scope = _exact(raw, {"kind", "wire"}, "scope")
    if scope["kind"] not in ("occurrence", "package"):
        raise ValueError("invalid scope kind")
    _wire(scope["wire"], "scope.wire")


def _validate_port(raw: object) -> None:
    port = _object(raw, "port")
    kind = port.get("kind")
    if kind == "consumer":
        _exact(port, {"kind", "consumer", "formal"}, "consumer port")
        _wire(port["consumer"], "port.consumer")
        _wire(port["formal"], "port.formal")
    elif kind == "expression":
        _exact(
            port,
            {
                "kind",
                "consumer",
                "reference_ordinal",
                "edge_ordinal",
                "referenced_declaration",
                "target_occurrence",
            },
            "expression port",
        )
        _wire(port["consumer"], "port.consumer")
        _nonnegative_integer(port["reference_ordinal"], "port.reference_ordinal")
        _nonnegative_integer(port["edge_ordinal"], "port.edge_ordinal")
        _wire(port["referenced_declaration"], "port.referenced_declaration")
        _nullable_wire(port["target_occurrence"], "port.target_occurrence")
    else:
        raise ValueError(f"unknown port kind {kind!r}")


def _validate_edge(raw: object) -> None:
    edge = _object(raw, "edge")
    kind = edge.get("kind")
    if kind == "node":
        _exact(edge, {"kind", "target"}, "node edge")
        _wire(edge["target"], "edge.target")
    elif kind == "producer":
        _exact(edge, {"kind", "target"}, "producer edge")
        target = _exact(edge["target"], {"calculation", "output"}, "producer target")
        _wire(target["calculation"], "producer.calculation")
        _wire(target["output"], "producer.output")
    elif kind == "literal":
        _exact(edge, {"kind", "value"}, "literal edge")
        _scalar(edge["value"], "literal edge value")
    else:
        raise ValueError(f"unknown edge kind {kind!r}")


def _validate_metadata(raw: object) -> None:
    metadata = _exact(
        raw,
        {
            "python_type",
            "description",
            "default_value",
            "unit",
            "qualified_name",
            "unresolved_default_kind",
            "formal_provenance",
        },
        "metadata",
    )
    _string(metadata["python_type"], "metadata.python_type")
    for key in ("description", "unit", "qualified_name", "unresolved_default_kind"):
        _nullable_string(metadata[key], f"metadata.{key}")
    _nullable_scalar(metadata["default_value"], "metadata.default_value")
    if metadata["formal_provenance"] is not None:
        provenance = _exact(
            metadata["formal_provenance"],
            {"declaration_id", "raw_name", "qualified_name"},
            "formal_provenance",
        )
        _wire(provenance["declaration_id"], "formal_provenance.declaration_id")
        for key in ("raw_name", "qualified_name"):
            if not _string(provenance[key], f"formal_provenance.{key}"):
                raise ValueError(f"formal_provenance.{key} must be nonempty")


def _validate_auto(raw: object) -> None:
    auto = _exact(
        raw,
        {"execution_steps", "output_expressions", "output_count", "single_output_expression"},
        "auto",
    )
    for key in ("execution_steps", "output_expressions"):
        for raw_step in _array(auto[key], f"auto.{key}"):
            step = _exact(raw_step, {"name", "expression"}, f"auto.{key} row")
            _string(step["name"], "auto row name")
            _string(step["expression"], "auto row expression")
    output_count = _nonnegative_integer(auto["output_count"], "auto.output_count")
    if output_count != len(auto["output_expressions"]):
        raise ValueError("auto.output_count must equal output_expressions length")
    _nullable_string(auto["single_output_expression"], "auto.single_output_expression")


def _validate_expression(raw: object) -> None:
    expression = _object(raw, "expression")
    kind = expression.get("kind")
    common = {"schema_version", "kind"}
    if kind == "literal":
        _exact(expression, common | {"literal", "operand_type"}, "literal expression")
        literal = _exact(expression["literal"], {"kind", "value", "result_type"}, "literal")
        _string(literal["kind"], "literal.kind")
        _scalar(literal["value"], "literal.value")
        _nullable_string(literal["result_type"], "literal.result_type")
    elif kind == "feature_ref":
        _exact(expression, common | {"reference", "operand_type"}, "feature expression")
        reference = _exact(
            expression["reference"],
            {"source_name", "target", "target_types", "chain_segments"},
            "feature reference",
        )
        _nullable_string(reference["source_name"], "reference.source_name")
        if reference["target"] is not None:
            target = _exact(
                reference["target"], {"kind", "name", "qualified_name"}, "reference target"
            )
            for key in ("kind", "name", "qualified_name"):
                _nullable_string(target[key], f"reference.target.{key}")
        for key in ("target_types", "chain_segments"):
            for value in _array(reference[key], f"reference.{key}"):
                _string(value, f"reference.{key} item")
    elif kind == "operator":
        _exact(expression, common | {"operator", "operands", "operand_type"}, "operator expression")
        _string(expression["operator"], "operator.operator")
        for child in _array(expression["operands"], "operator.operands"):
            _validate_expression(child)
    elif kind == "unit":
        _exact(expression, common | {"value", "unit_text", "operand_type"}, "unit expression")
        _validate_expression(expression["value"])
        _nullable_string(expression["unit_text"], "unit.unit_text")
    elif kind == "invocation":
        _exact(
            expression,
            common | {"function_qn", "arguments", "operand_type"},
            "invocation expression",
        )
        if expression["function_qn"] is not None:
            for value in _array(expression["function_qn"], "invocation.function_qn"):
                _string(value, "invocation.function_qn item")
        for child in _array(expression["arguments"], "invocation.arguments"):
            _validate_expression(child)
    elif kind == "unsupported":
        _exact(
            expression,
            common | {"node_kind", "diagnostic", "source_text"},
            "unsupported expression",
        )
        _string(expression["node_kind"], "unsupported.node_kind")
        _string(expression["diagnostic"], "unsupported.diagnostic")
        _nullable_string(expression["source_text"], "unsupported.source_text")
    else:
        raise ValueError(f"unknown expression kind {kind!r}")
    if expression["schema_version"] != EXPRESSION_IR_SCHEMA:
        raise ValueError("expression schema marker is not expression-ir/v1")
    if kind != "unsupported":
        _validate_operand_type(expression["operand_type"])


def _validate_operand_type(raw: object) -> None:
    if raw is None:
        return
    operand = _exact(raw, {"category", "enumeration", "unit"}, "operand_type")
    if operand["category"] not in (
        "boolean",
        "string",
        "integer",
        "real",
        "enum",
        "quantity",
        "unresolved",
        "unknown",
    ):
        raise ValueError("invalid operand category")
    _nullable_string(operand["enumeration"], "operand_type.enumeration")
    if operand["unit"] is not None:
        unit = _exact(operand["unit"], {"unit", "dimension"}, "operand unit")
        _nullable_string(unit["unit"], "operand unit.unit")
        _nullable_string(unit["dimension"], "operand unit.dimension")


def _validate_compatibility(document: dict[str, Any]) -> None:
    authority = _object(document["authority"], "authority")
    expected = {
        "format": SNAPSHOT_FORMAT,
        "certifiability_profile": CERTIFIABILITY_PROFILE,
        "instance_graph_schema": INSTANCE_GRAPH_SCHEMA_VERSION,
        "expression_ir_schema": EXPRESSION_IR_SCHEMA,
        "executable_profile": EXECUTABLE_PROFILE,
        "projector_semantics": PROJECTOR_SEMANTICS,
        "syside_version": "0.8.4",
        "integrity_algorithm": "sha256",
        "canonicalization": INTEGRITY_CANONICALIZATION,
    }
    actual = {
        "format": document["format"],
        **{key: authority[key] for key in expected if key in authority},
        "integrity_algorithm": _object(document["integrity"], "integrity")["algorithm"],
        "canonicalization": _object(document["integrity"], "integrity")["canonicalization"],
    }
    for key, value in expected.items():
        if actual.get(key) != value:
            raise SnapshotCompatibilityError(
                f"snapshot {key} {actual.get(key)!r} is incompatible; expected {value!r}"
            )
    standard = _object(authority["standard_library"], "standard_library")
    if (
        standard["kind"] != "syside-default"
        or standard["document_count"] != PINNED_STANDARD_LIBRARY_COUNT
        or standard["sha256"] != PINNED_STANDARD_LIBRARY_SHA256
    ):
        raise SnapshotCompatibilityError(
            "snapshot standard-library authority does not match the pinned SysIDE 0.8.4 environment"
        )


def _validate_sources(document: dict[str, Any], source_roots: Sequence[Path] | None) -> None:
    capture = _object(document["capture"], "capture")
    sources = _object(document["sources"], "sources")
    expected_fingerprint = hashlib.sha256(
        canonical_json(
            {
                "roots": sources["roots"],
                "files": sources["files"],
                "capture_options": _object(capture["options"], "capture.options"),
            }
        )
    ).hexdigest()
    if sources["fingerprint"] != expected_fingerprint:
        raise SnapshotIntegrityError("snapshot source fingerprint mismatch")
    referents = {row["referent"] for row in sources["files"]}
    graph = _object(_object(document["instance_graph"], "instance_graph")["graph"], "graph")
    for group in ("attrs", "calcs", "constraints"):
        for row in graph[group]:
            if row["source_file"] not in referents:
                raise SnapshotIntegrityError(
                    f"graph source_file {row['source_file']!r} is absent from sources.files"
                )
    if source_roots is None:
        return
    if isinstance(source_roots, (str, bytes)) or not isinstance(source_roots, Sequence):
        raise TypeError("source_roots must be a sequence of pathlib.Path values or None")
    if not source_roots:
        raise SnapshotStaleSourceError("source_roots cannot be empty")
    if any(not isinstance(path, Path) for path in source_roots):
        raise TypeError("every source_roots member must be pathlib.Path")
    try:
        with admit_sources(source_roots) as admission:
            actual_roots = [item.envelope_data() for item in admission.roots]
            actual_files = [item.envelope_data() for item in admission.files]
    except SourceAdmissionError as error:
        raise SnapshotStaleSourceError(str(error)) from error
    if actual_roots != sources["roots"] or actual_files != sources["files"]:
        raise SnapshotStaleSourceError(
            "replacement source roots do not reproduce the captured admission"
        )


def _outer_digest(document: dict[str, object]) -> str:
    signed = deepcopy(document)
    integrity = _object(signed.get("integrity"), "integrity")
    integrity.pop("digest", None)
    return hashlib.sha256(canonical_json(signed)).hexdigest()


def _exact(value: object, keys: set[str], label: str) -> dict[str, Any]:
    result = _object(value, label)
    actual = set(result)
    if actual != keys:
        missing = sorted(keys - actual)
        unknown = sorted(actual - keys)
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


def _nullable_string(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _string(value, label)


def _integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    return value


def _nonnegative_integer(value: object, label: str) -> int:
    result = _integer(value, label)
    if result < 0:
        raise ValueError(f"{label} must be nonnegative")
    return result


def _boolean(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be Boolean")
    return value


def _scalar(value: object, label: str) -> float | int | str | bool:
    if isinstance(value, bool) or isinstance(value, str):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
        return value
    raise ValueError(f"{label} must be a finite JSON scalar")


def _nullable_scalar(value: object, label: str) -> float | int | str | bool | None:
    if value is None:
        return None
    return _scalar(value, label)


def _hash_string(value: object, label: str) -> str:
    result = _string(value, label)
    if _HASH.fullmatch(result) is None:
        raise ValueError(f"{label} must be a lower-case SHA-256 hash")
    return result


def _wire(value: object, label: str) -> str:
    result = _string(value, label)
    if not result:
        raise ValueError(f"{label} must be a nonempty typed-ID wire string")
    return result


def _nullable_wire(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _wire(value, label)


def _unique_wires(value: object, label: str) -> list[str]:
    result = [_wire(item, label) for item in _array(value, label)]
    if len(result) != len(set(result)):
        raise ValueError(f"{label} must contain unique identities")
    return result


def _strictly_sorted(values: list[Any], label: str) -> None:
    if values != sorted(set(values)):
        raise ValueError(f"{label} must be strictly sorted and unique")
