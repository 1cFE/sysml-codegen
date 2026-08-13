"""Canonical internal codec for the resolved exact-ID instance graph.

This is the codec the shipped v6 snapshot boundary is built on: ``snapshot/
envelope.py`` seals and loads through it, and both ``sysml-codegen snapshot``
and ``generate --from-snapshot`` reach it that way.  It began as Item-6
evidence for a future boundary, beside a v5 extraction-snapshot loader that is
now retired.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from agentic_mbse.sysml.executable_profile import Eligibility
from agentic_mbse.sysml.expression_ir import (
    ExpressionIR,
    expression_ir_from_dict,
    serialize_expression,
)
from pydantic import ValidationError as PydanticValidationError

from sysml_codegen.core.models import AutoImplContext
from sysml_codegen.elaboration.diagnostics import (
    ElaborationCode,
    ElaborationInvariantError,
)
from sysml_codegen.elaboration.graph import (
    AttrNode,
    CalcNode,
    ConstraintNode,
    ConstraintUsageRecord,
    Diagnostic,
    FormalProvenance,
    GraphValidationError,
    Inapplicability,
    InputPortId,
    InputRef,
    InstanceGraph,
    LiteralInput,
    NodeRef,
    OccurrenceRecord,
    PortMetadata,
    ProducerRef,
    UsageDisposition,
    ValueSite,
)
from sysml_codegen.elaboration.identity import (
    ConsumerPortId,
    DeclarationId,
    ExpressionPortId,
    FeatureSlotId,
    NodeId,
    NodeKind,
    OccurrenceId,
    OutputPortId,
    PackageScopeId,
    ScopeId,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.source_evidence import ReadinessCode

__all__ = [
    "INSTANCE_GRAPH_SCHEMA_VERSION",
    "InstanceGraphCodecError",
    "decode_instance_graph",
    "encode_instance_graph",
]

INSTANCE_GRAPH_SCHEMA_VERSION = "instance-graph/v3"


class InstanceGraphCodecError(ElaborationInvariantError):
    """An internal resolved-graph payload is malformed or incompatible."""

    def __init__(self, detail: str) -> None:
        super().__init__(ElaborationCode.SI_SNAPSHOT_INVALID, detail)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()


def _fingerprint(schema_version: str, graph: object) -> str:
    return hashlib.sha256(
        _canonical({"schema_version": schema_version, "graph": graph})
    ).hexdigest()


def _scope_to_data(scope: ScopeId) -> dict[str, str]:
    if isinstance(scope, OccurrenceId):
        return {"kind": "occurrence", "wire": scope.to_wire()}
    return {"kind": "package", "wire": scope.package_declaration.to_wire()}


def _scope_from_data(data: object) -> ScopeId:
    value = _mapping(data, "scope", {"kind", "wire"})
    kind = _string(value.get("kind"), "scope.kind")
    wire = _string(value.get("wire"), "scope.wire")
    if kind == "occurrence":
        return OccurrenceId.from_wire(wire)
    if kind == "package":
        return PackageScopeId(DeclarationId.from_wire(wire))
    raise ValueError(f"unknown scope kind {kind!r}")


def _output_port_to_data(port: OutputPortId) -> dict[str, str]:
    return {
        "calculation": port.calculation.to_wire(),
        "output": port.output.to_wire(),
    }


def _output_port_from_data(data: object) -> OutputPortId:
    value = _mapping(data, "output port", {"calculation", "output"})
    return OutputPortId(
        NodeId.from_wire(_string(value.get("calculation"), "output.calculation")),
        DeclarationId.from_wire(_string(value.get("output"), "output.output")),
    )


def _input_port_to_data(port: InputPortId) -> dict[str, object]:
    if isinstance(port, ConsumerPortId):
        return {
            "kind": "consumer",
            "consumer": port.consumer.to_wire(),
            "formal": port.formal.to_wire(),
        }
    return {
        "kind": "expression",
        "consumer": port.consumer.to_wire(),
        "reference_ordinal": port.reference_ordinal,
        "edge_ordinal": port.edge_ordinal,
        "referenced_declaration": port.referenced_declaration.to_wire(),
        "target_occurrence": (
            port.target_occurrence.to_wire() if port.target_occurrence is not None else None
        ),
    }


def _input_port_from_data(data: object) -> InputPortId:
    value = _mapping(data, "input port")
    kind = _string(value.get("kind"), "input.kind")
    _require_exact_keys(
        value,
        "input port",
        {"kind", "consumer", "formal"}
        if kind == "consumer"
        else {
            "kind",
            "consumer",
            "reference_ordinal",
            "edge_ordinal",
            "referenced_declaration",
            "target_occurrence",
        },
    )
    consumer = NodeId.from_wire(_string(value.get("consumer"), "input.consumer"))
    if kind == "consumer":
        return ConsumerPortId(
            consumer,
            DeclarationId.from_wire(_string(value.get("formal"), "input.formal")),
        )
    if kind == "expression":
        raw_occurrence = value.get("target_occurrence")
        return ExpressionPortId(
            consumer=consumer,
            reference_ordinal=_integer(value.get("reference_ordinal"), "input.reference_ordinal"),
            edge_ordinal=_integer(value.get("edge_ordinal"), "input.edge_ordinal"),
            referenced_declaration=DeclarationId.from_wire(
                _string(
                    value.get("referenced_declaration"),
                    "input.referenced_declaration",
                )
            ),
            target_occurrence=(
                OccurrenceId.from_wire(_string(raw_occurrence, "input.target_occurrence"))
                if raw_occurrence is not None
                else None
            ),
        )
    raise ValueError(f"unknown input port kind {kind!r}")


def _edge_to_data(edge: InputRef | None) -> dict[str, object] | None:
    if edge is None:
        return None
    if isinstance(edge, NodeRef):
        return {"kind": "node", "target": edge.target.to_wire()}
    if isinstance(edge, ProducerRef):
        return {"kind": "producer", "target": _output_port_to_data(edge.target)}
    return {"kind": "literal", "value": edge.value}


def _edge_from_data(data: object) -> InputRef | None:
    if data is None:
        return None
    value = _mapping(data, "edge")
    kind = _string(value.get("kind"), "edge.kind")
    if kind == "node":
        _require_exact_keys(value, "node edge", {"kind", "target"})
        return NodeRef(NodeId.from_wire(_string(value.get("target"), "edge.target")))
    if kind == "producer":
        _require_exact_keys(value, "producer edge", {"kind", "target"})
        return ProducerRef(_output_port_from_data(value.get("target")))
    if kind == "literal":
        _require_exact_keys(value, "literal edge", {"kind", "value"})
        literal = value.get("value")
        if not isinstance(literal, (float, int, str, bool)):
            raise ValueError(f"invalid literal edge value {literal!r}")
        return LiteralInput(literal)
    raise ValueError(f"unknown edge kind {kind!r}")


def _metadata_to_data(metadata: PortMetadata) -> dict[str, object]:
    formal_provenance = metadata.formal_provenance
    return {
        "python_type": metadata.python_type,
        "description": metadata.description,
        "default_value": metadata.default_value,
        "unit": metadata.unit,
        "qualified_name": metadata.qualified_name,
        "unresolved_default_kind": metadata.unresolved_default_kind,
        "formal_provenance": (
            {
                "declaration_id": formal_provenance.declaration_id.to_wire(),
                "raw_name": formal_provenance.raw_name,
                "qualified_name": formal_provenance.qualified_name,
            }
            if formal_provenance is not None
            else None
        ),
    }


def _metadata_from_data(data: object) -> PortMetadata:
    value = _mapping(
        data,
        "port metadata",
        {
            "python_type",
            "description",
            "default_value",
            "unit",
            "qualified_name",
            "unresolved_default_kind",
            "formal_provenance",
        },
    )
    default = value.get("default_value")
    if default is not None and not isinstance(default, (float, int, str, bool)):
        raise ValueError(f"invalid port default {default!r}")
    raw_provenance = value.get("formal_provenance")
    formal_provenance = None
    if raw_provenance is not None:
        provenance = _mapping(
            raw_provenance,
            "metadata.formal_provenance",
            {"declaration_id", "raw_name", "qualified_name"},
        )
        formal_provenance = FormalProvenance(
            declaration_id=DeclarationId.from_wire(
                _string(
                    provenance.get("declaration_id"),
                    "metadata.formal_provenance.declaration_id",
                )
            ),
            raw_name=_string(provenance.get("raw_name"), "metadata.formal_provenance.raw_name"),
            qualified_name=_string(
                provenance.get("qualified_name"),
                "metadata.formal_provenance.qualified_name",
            ),
        )
    return PortMetadata(
        python_type=_string(value.get("python_type"), "metadata.python_type"),
        description=_optional_string(value.get("description"), "metadata.description"),
        default_value=default,
        unit=_optional_string(value.get("unit"), "metadata.unit"),
        qualified_name=_optional_string(value.get("qualified_name"), "metadata.qualified_name"),
        unresolved_default_kind=_optional_string(
            value.get("unresolved_default_kind"), "metadata.unresolved_default_kind"
        ),
        formal_provenance=formal_provenance,
    )


def _auto_impl_context_to_data(context: AutoImplContext | None) -> object | None:
    """Seal the auto-implementation protocol in the shape v6 has always written."""
    if context is None:
        return None
    return {
        "execution_steps": [
            {"name": step.name, "expression": step.expression} for step in context.execution_steps
        ],
        "output_expressions": [
            {"name": output.name, "expression": output.expression}
            for output in context.output_expressions
        ],
        "output_count": context.output_count,
        "single_output_expression": context.single_output_expression,
    }


def _auto_impl_context_from_data(data: object) -> AutoImplContext | None:
    """Decode the protocol exactly, so a malformed record refuses at the boundary."""
    if data is None:
        return None
    value = _mapping(
        data,
        "calculation.auto_impl_context",
        {"execution_steps", "output_expressions", "output_count", "single_output_expression"},
    )
    try:
        return AutoImplContext.model_validate(value)
    except PydanticValidationError as error:
        raise ValueError(f"calculation auto_impl_context is not a valid record: {error}") from error


def _expression_to_data(expression: ExpressionIR | None) -> object | None:
    if expression is None:
        return None
    value = json.loads(serialize_expression(expression))
    if not isinstance(value, dict):
        raise ValueError("expression IR must serialize as an object")
    return value


def _expression_from_data(data: object) -> ExpressionIR:
    value = _mapping(data, "expression IR")
    return expression_ir_from_dict(value)


def _input_records(node: CalcNode | ConstraintNode) -> list[dict[str, object]]:
    ports = set(node.inputs) | set(node.input_names) | set(node.input_metadata)
    if set(node.input_names) != ports or set(node.input_metadata) != ports:
        raise ValueError("input names and metadata must be total before encoding")
    return [
        {
            "port": _input_port_to_data(port),
            "edge": _edge_to_data(node.inputs.get(port)),
            "name": node.input_names[port],
            "metadata": _metadata_to_data(node.input_metadata[port]),
        }
        for port in sorted(ports, key=lambda item: _canonical(_input_port_to_data(item)))
    ]


def _decode_input_records(
    raw: object, node_id: NodeId
) -> tuple[
    dict[InputPortId, InputRef],
    dict[InputPortId, str],
    dict[InputPortId, PortMetadata],
]:
    inputs: dict[InputPortId, InputRef] = {}
    names: dict[InputPortId, str] = {}
    metadata: dict[InputPortId, PortMetadata] = {}
    for item in _list(raw, "inputs"):
        record = _mapping(item, "input record", {"port", "edge", "name", "metadata"})
        port = _input_port_from_data(record.get("port"))
        if port.consumer != node_id:
            raise ValueError("input port consumer does not match its node")
        if port in names:
            raise ValueError("duplicate input port record")
        edge = _edge_from_data(record.get("edge"))
        if edge is not None:
            inputs[port] = edge
        names[port] = _string(record.get("name"), "input.name")
        metadata[port] = _metadata_from_data(record.get("metadata"))
    return inputs, names, metadata


def _occurrence_to_data(record: OccurrenceRecord) -> dict[str, object]:
    return {
        "occurrence_id": record.occurrence_id.to_wire(),
        "parent_id": record.parent_id.to_wire() if record.parent_id is not None else None,
        "containment_slot": record.containment_slot.root_declaration.to_wire(),
        "occurrence_index": record.occurrence_index,
        "effective_usage_id": record.effective_usage_id.to_wire(),
        "effective_type_ids": [item.to_wire() for item in record.effective_type_ids],
        "display_segment": record.display_segment,
        "package_display": record.package_display,
    }


def _occurrence_from_data(data: object) -> OccurrenceRecord:
    value = _mapping(
        data,
        "occurrence record",
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
    )
    occurrence_id = OccurrenceId.from_wire(
        _string(value.get("occurrence_id"), "occurrence.occurrence_id")
    )
    raw_parent = value.get("parent_id")
    raw_index = value.get("occurrence_index")
    occurrence_index = (
        _integer(raw_index, "occurrence.occurrence_index") if raw_index is not None else None
    )
    return OccurrenceRecord(
        occurrence_id=occurrence_id,
        parent_id=(
            OccurrenceId.from_wire(_string(raw_parent, "occurrence.parent_id"))
            if raw_parent is not None
            else None
        ),
        containment_slot=FeatureSlotId(
            DeclarationId.from_wire(
                _string(value.get("containment_slot"), "occurrence.containment_slot")
            )
        ),
        occurrence_index=occurrence_index,
        effective_usage_id=DeclarationId.from_wire(
            _string(value.get("effective_usage_id"), "occurrence.effective_usage_id")
        ),
        effective_type_ids=tuple(
            DeclarationId.from_wire(_string(item, "occurrence.effective_type_id"))
            for item in _list(value.get("effective_type_ids"), "occurrence.effective_type_ids")
        ),
        display_segment=_string(value.get("display_segment"), "occurrence.display_segment"),
        package_display=_optional_string(
            value.get("package_display"), "occurrence.package_display"
        ),
    )


def _attr_to_data(node: AttrNode) -> dict[str, object]:
    return {
        "node_id": node.node_id.to_wire(),
        "scope": _scope_to_data(node.scope),
        "declaration_id": node.declaration_id.to_wire(),
        "slot_id": node.slot_id.root_declaration.to_wire(),
        "display_path": node.display_path,
        "display_name": node.display_name,
        "declaration_qn": node.declaration_qn,
        "value": node.value,
        "value_site": node.value_site.value,
        "alias_target": _edge_to_data(node.alias_target),
        "is_alias": node.is_alias,
        "alias_shape": node.alias_shape,
        "source_file": node.source_file,
        "source_line": node.source_line,
        "owner_qualified_name": node.owner_qualified_name,
    }


def _attr_from_data(data: object) -> AttrNode:
    value = _mapping(
        data,
        "attribute node",
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
    )
    node_id = NodeId.from_wire(_string(value.get("node_id"), "attribute.node_id"))
    scope = _scope_from_data(value.get("scope"))
    declaration = DeclarationId.from_wire(
        _string(value.get("declaration_id"), "attribute.declaration_id")
    )
    slot = FeatureSlotId(
        DeclarationId.from_wire(_string(value.get("slot_id"), "attribute.slot_id"))
    )
    if (
        node_id.kind is not NodeKind.ATTRIBUTE
        or node_id.scope != scope
        or node_id.declaration != slot
    ):
        raise ValueError("attribute identity fields disagree")
    raw_value = value.get("value")
    if raw_value is not None and not isinstance(raw_value, (float, int, str, bool)):
        raise ValueError(f"invalid attribute value {raw_value!r}")
    return AttrNode(
        node_id=node_id,
        scope=scope,
        declaration_id=declaration,
        slot_id=slot,
        display_path=_string(value.get("display_path"), "attribute.display_path"),
        display_name=_string(value.get("display_name"), "attribute.display_name"),
        declaration_qn=_string(value.get("declaration_qn"), "attribute.declaration_qn"),
        value=raw_value,
        value_site=ValueSite(_string(value.get("value_site"), "attribute.value_site")),
        alias_target=_edge_from_data(value.get("alias_target")),
        is_alias=_boolean(value.get("is_alias"), "attribute.is_alias"),
        alias_shape=_optional_string(value.get("alias_shape"), "attribute.alias_shape"),
        source_file=_string(value.get("source_file"), "attribute.source_file"),
        source_line=_integer(value.get("source_line"), "attribute.source_line"),
        owner_qualified_name=_string(
            value.get("owner_qualified_name"), "attribute.owner_qualified_name"
        ),
    )


def _calc_to_data(node: CalcNode) -> dict[str, object]:
    return {
        "node_id": node.node_id.to_wire(),
        "scope": _scope_to_data(node.scope),
        "declaration_id": node.declaration_id.to_wire(),
        "display_path": node.display_path,
        "display_name": node.display_name,
        "calc_def_name": node.calc_def_name,
        "calc_def_qualified_name": node.calc_def_qualified_name,
        "inputs": _input_records(node),
        "outputs": [
            {
                "declaration": declaration.to_wire(),
                "port": _output_port_to_data(port),
                "name": node.output_names[declaration],
                "metadata": _metadata_to_data(node.output_metadata[declaration]),
            }
            for declaration, port in sorted(
                node.outputs.items(), key=lambda item: item[0].to_wire()
            )
        ],
        "unbound_formals": [item.to_wire() for item in node.unbound_formals],
        "is_computed": node.is_computed,
        "expression_ir": _expression_to_data(node.expression_ir),
        "aggregation_reference_ordinals": list(node.aggregation_reference_ordinals),
        "compilability": node.compilability.value,
        "auto_impl_context": _auto_impl_context_to_data(node.auto_impl_context),
        "doc_comment": node.doc_comment,
        "calc_expressions": list(node.calc_expressions),
        "calculation_definition_id": (
            node.calculation_definition_id.to_wire()
            if node.calculation_definition_id is not None
            else None
        ),
        "compilation_definition_id": (
            node.compilation_definition_id.to_wire()
            if node.compilation_definition_id is not None
            else None
        ),
        "compiled_output_ids": [item.to_wire() for item in node.compiled_output_ids],
        "source_file": node.source_file,
        "source_line": node.source_line,
    }


def _calc_from_data(data: object) -> CalcNode:
    value = _mapping(
        data,
        "calculation node",
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
    )
    node_id = NodeId.from_wire(_string(value.get("node_id"), "calculation.node_id"))
    scope = _scope_from_data(value.get("scope"))
    declaration = DeclarationId.from_wire(
        _string(value.get("declaration_id"), "calculation.declaration_id")
    )
    is_computed = _boolean(value.get("is_computed"), "calculation.is_computed")
    if (
        node_id.kind is not NodeKind.CALCULATION
        or node_id.scope != scope
        or (is_computed and not isinstance(node_id.declaration, FeatureSlotId))
        or (not is_computed and node_id.declaration != declaration)
    ):
        raise ValueError("calculation identity fields disagree")
    inputs, names, input_metadata = _decode_input_records(value.get("inputs"), node_id)
    outputs: dict[DeclarationId, OutputPortId] = {}
    output_names: dict[DeclarationId, str] = {}
    output_metadata: dict[DeclarationId, PortMetadata] = {}
    for item in _list(value.get("outputs"), "calculation.outputs"):
        record = _mapping(item, "output record", {"declaration", "port", "name", "metadata"})
        output_declaration = DeclarationId.from_wire(
            _string(record.get("declaration"), "output.declaration")
        )
        if output_declaration in outputs:
            raise ValueError("duplicate calculation output declaration")
        port = _output_port_from_data(record.get("port"))
        if port.calculation != node_id or port.output != output_declaration:
            raise ValueError("calculation output port identity fields disagree")
        outputs[output_declaration] = port
        output_names[output_declaration] = _string(record.get("name"), "output.name")
        output_metadata[output_declaration] = _metadata_from_data(record.get("metadata"))
    auto_impl_context = _auto_impl_context_from_data(value.get("auto_impl_context"))
    raw_calculation_definition_id = value.get("calculation_definition_id")
    calculation_definition_id = (
        DeclarationId.from_wire(
            _string(
                raw_calculation_definition_id,
                "calculation.calculation_definition_id",
            )
        )
        if raw_calculation_definition_id is not None
        else None
    )
    raw_compilation_definition_id = value.get("compilation_definition_id")
    compilation_definition_id = (
        DeclarationId.from_wire(
            _string(
                raw_compilation_definition_id,
                "calculation.compilation_definition_id",
            )
        )
        if raw_compilation_definition_id is not None
        else None
    )
    return CalcNode(
        node_id=node_id,
        scope=scope,
        declaration_id=declaration,
        display_path=_string(value.get("display_path"), "calculation.display_path"),
        display_name=_string(value.get("display_name"), "calculation.display_name"),
        calc_def_name=_string(value.get("calc_def_name"), "calculation.calc_def_name"),
        calc_def_qualified_name=_string(
            value.get("calc_def_qualified_name"),
            "calculation.calc_def_qualified_name",
        ),
        inputs=inputs,
        input_names=names,
        input_metadata=input_metadata,
        outputs=outputs,
        output_names=output_names,
        output_metadata=output_metadata,
        unbound_formals=tuple(
            DeclarationId.from_wire(_string(item, "unbound formal"))
            for item in _list(value.get("unbound_formals"), "calculation.unbound_formals")
        ),
        is_computed=is_computed,
        expression_ir=(
            _expression_from_data(value.get("expression_ir"))
            if value.get("expression_ir") is not None
            else None
        ),
        aggregation_reference_ordinals=tuple(
            _integer(item, "aggregation ordinal")
            for item in _list(
                value.get("aggregation_reference_ordinals"),
                "calculation.aggregation_reference_ordinals",
            )
        ),
        compilability=Compilability(
            _string(value.get("compilability"), "calculation.compilability")
        ),
        auto_impl_context=auto_impl_context,
        doc_comment=_optional_string(value.get("doc_comment"), "calculation.doc_comment"),
        calc_expressions=tuple(
            _string(item, "calculation expression")
            for item in _list(value.get("calc_expressions"), "calculation.calc_expressions")
        ),
        calculation_definition_id=calculation_definition_id,
        compilation_definition_id=compilation_definition_id,
        compiled_output_ids=tuple(
            DeclarationId.from_wire(_string(item, "compiled output identity"))
            for item in _list(
                value.get("compiled_output_ids"),
                "calculation.compiled_output_ids",
            )
        ),
        source_file=_string(value.get("source_file"), "calculation.source_file"),
        source_line=_integer(value.get("source_line"), "calculation.source_line"),
    )


def _constraint_usage_to_data(record: ConstraintUsageRecord) -> dict[str, object]:
    return {
        "declaration_id": record.declaration_id.to_wire(),
        "usage_qualified_name": record.usage_qualified_name,
        "display_name": record.display_name,
        "source_form": record.source_form,
        "owner_kind": record.owner_kind,
        "owner_qualified_name": record.owner_qualified_name,
        "membership_kind": record.membership_kind,
        "is_negated": record.is_negated,
        "source_file": record.source_file,
        "source_line": record.source_line,
        "occurrence_count": record.occurrence_count,
        "definition_qualified_name": record.definition_qualified_name,
        "disposition": {
            "kind": record.disposition.kind,
            "reason": record.disposition.reason,
            "severity": record.disposition.severity,
            "detail": record.disposition.detail,
        },
        "inapplicability": (
            None
            if record.inapplicability is None
            else {"reason": record.inapplicability.reason}
        ),
    }


def _constraint_usage_from_data(data: object) -> ConstraintUsageRecord:
    value = _mapping(
        data,
        "constraint usage record",
        {
            "declaration_id",
            "usage_qualified_name",
            "display_name",
            "source_form",
            "owner_kind",
            "owner_qualified_name",
            "membership_kind",
            "is_negated",
            "source_file",
            "source_line",
            "occurrence_count",
            "definition_qualified_name",
            "disposition",
            "inapplicability",
        },
    )
    disposition = _mapping(
        value.get("disposition"),
        "usage record disposition",
        {"kind", "reason", "severity", "detail"},
    )
    raw_inapplicability = value.get("inapplicability")
    inapplicability = None
    if raw_inapplicability is not None:
        marked = _mapping(raw_inapplicability, "usage record inapplicability", {"reason"})
        inapplicability = Inapplicability(
            reason=_string(marked.get("reason"), "inapplicability.reason")
        )
    return ConstraintUsageRecord(
        declaration_id=DeclarationId.from_wire(
            _string(value.get("declaration_id"), "usage record.declaration_id")
        ),
        usage_qualified_name=_string(
            value.get("usage_qualified_name"), "usage record.usage_qualified_name"
        ),
        display_name=_string(value.get("display_name"), "usage record.display_name"),
        source_form=_string(value.get("source_form"), "usage record.source_form"),
        owner_kind=_string(value.get("owner_kind"), "usage record.owner_kind"),
        owner_qualified_name=_string(
            value.get("owner_qualified_name"), "usage record.owner_qualified_name"
        ),
        membership_kind=(
            None
            if value.get("membership_kind") is None
            else _string(value.get("membership_kind"), "usage record.membership_kind")
        ),
        is_negated=_boolean(value.get("is_negated"), "usage record.is_negated"),
        source_file=_string(value.get("source_file"), "usage record.source_file"),
        source_line=_integer(value.get("source_line"), "usage record.source_line"),
        occurrence_count=_integer(
            value.get("occurrence_count"), "usage record.occurrence_count"
        ),
        definition_qualified_name=(
            None
            if value.get("definition_qualified_name") is None
            else _string(
                value.get("definition_qualified_name"),
                "usage record.definition_qualified_name",
            )
        ),
        disposition=UsageDisposition(
            kind=_string(disposition.get("kind"), "disposition.kind"),
            reason=_string(disposition.get("reason"), "disposition.reason"),
            severity=_string(disposition.get("severity"), "disposition.severity"),
            detail=_string(disposition.get("detail"), "disposition.detail"),
        ),
        inapplicability=inapplicability,
    )


def _constraint_to_data(node: ConstraintNode) -> dict[str, object]:
    return {
        "node_id": node.node_id.to_wire(),
        "scope": _scope_to_data(node.scope),
        "declaration_id": node.declaration_id.to_wire(),
        "display_path": node.display_path,
        "display_name": node.display_name,
        "constraint_def_name": node.constraint_def_name,
        "inputs": _input_records(node),
        "unbound_formals": [item.to_wire() for item in node.unbound_formals],
        "predicate_ir": _expression_to_data(node.predicate_ir),
        "source_form": node.source_form,
        "owner_kind": node.owner_kind,
        "owner_qualified_name": node.owner_qualified_name,
        "usage_qualified_name": node.usage_qualified_name,
        "membership_kind": node.membership_kind,
        "predicate_source_key": node.predicate_source_key,
        "is_negated": node.is_negated,
        "definition_qualified_name": node.definition_qualified_name,
        "eligibility": node.eligibility.value,
        "effective_definition_id": (
            node.effective_definition_id.to_wire()
            if node.effective_definition_id is not None
            else None
        ),
        "exclusion_reasons": list(node.exclusion_reasons),
        "exclusion_location": node.exclusion_location,
        "source_file": node.source_file,
        "source_line": node.source_line,
    }


def _constraint_from_data(data: object) -> ConstraintNode:
    value = _mapping(
        data,
        "constraint node",
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
    )
    node_id = NodeId.from_wire(_string(value.get("node_id"), "constraint.node_id"))
    scope = _scope_from_data(value.get("scope"))
    declaration = DeclarationId.from_wire(
        _string(value.get("declaration_id"), "constraint.declaration_id")
    )
    if (
        node_id.kind is not NodeKind.CONSTRAINT
        or node_id.scope != scope
        or node_id.declaration != declaration
    ):
        raise ValueError("constraint identity fields disagree")
    inputs, names, input_metadata = _decode_input_records(value.get("inputs"), node_id)
    return ConstraintNode(
        node_id=node_id,
        scope=scope,
        declaration_id=declaration,
        display_path=_string(value.get("display_path"), "constraint.display_path"),
        display_name=_string(value.get("display_name"), "constraint.display_name"),
        constraint_def_name=_string(
            value.get("constraint_def_name"), "constraint.constraint_def_name"
        ),
        eligibility=Eligibility(_string(value.get("eligibility"), "constraint.eligibility")),
        effective_definition_id=(
            DeclarationId.from_wire(
                _string(
                    value.get("effective_definition_id"),
                    "constraint.effective_definition_id",
                )
            )
            if value.get("effective_definition_id") is not None
            else None
        ),
        inputs=inputs,
        input_names=names,
        input_metadata=input_metadata,
        unbound_formals=tuple(
            DeclarationId.from_wire(_string(item, "unbound formal"))
            for item in _list(value.get("unbound_formals"), "constraint.unbound_formals")
        ),
        predicate_ir=(
            _expression_from_data(value.get("predicate_ir"))
            if value.get("predicate_ir") is not None
            else None
        ),
        source_form=_string(value.get("source_form"), "constraint.source_form"),
        owner_kind=_string(value.get("owner_kind"), "constraint.owner_kind"),
        owner_qualified_name=_string(
            value.get("owner_qualified_name"), "constraint.owner_qualified_name"
        ),
        usage_qualified_name=_string(
            value.get("usage_qualified_name"), "constraint.usage_qualified_name"
        ),
        membership_kind=_optional_string(
            value.get("membership_kind"), "constraint.membership_kind"
        ),
        predicate_source_key=_string(
            value.get("predicate_source_key"), "constraint.predicate_source_key"
        ),
        is_negated=_boolean(value.get("is_negated"), "constraint.is_negated"),
        definition_qualified_name=_optional_string(
            value.get("definition_qualified_name"),
            "constraint.definition_qualified_name",
        ),
        exclusion_reasons=tuple(
            _string(item, "constraint.exclusion_reason")
            for item in _list(value.get("exclusion_reasons", []), "constraint.exclusion_reasons")
        ),
        exclusion_location=_optional_string(
            value.get("exclusion_location"), "constraint.exclusion_location"
        ),
        source_file=_string(value.get("source_file"), "constraint.source_file"),
        source_line=_integer(value.get("source_line"), "constraint.source_line"),
    )


def _diagnostic_to_data(item: Diagnostic) -> dict[str, object]:
    return {
        "code": item.code.value,
        "consumer": item.consumer.to_wire() if item.consumer is not None else None,
        "consumer_display": item.consumer_display,
        "param_name": item.param_name,
        "detail": item.detail,
    }


def _diagnostic_from_data(data: object) -> Diagnostic:
    value = _mapping(
        data,
        "diagnostic",
        {"code", "consumer", "consumer_display", "param_name", "detail"},
    )
    code_value = _string(value.get("code"), "diagnostic.code")
    try:
        code: ElaborationCode | ReadinessCode = ElaborationCode(code_value)
    except ValueError:
        code = ReadinessCode(code_value)
    raw_consumer = value.get("consumer")
    return Diagnostic(
        code=code,
        consumer=(
            NodeId.from_wire(_string(raw_consumer, "diagnostic.consumer"))
            if raw_consumer is not None
            else None
        ),
        consumer_display=_string(value.get("consumer_display"), "diagnostic.consumer_display"),
        param_name=_optional_string(value.get("param_name"), "diagnostic.param_name"),
        detail=_string(value.get("detail"), "diagnostic.detail"),
    )


def _graph_to_data(graph: InstanceGraph) -> dict[str, object]:
    return {
        "occurrences": [
            _occurrence_to_data(record)
            for record in sorted(
                graph.occurrences.values(),
                key=lambda item: item.occurrence_id.to_wire(),
            )
        ],
        "attrs": [
            _attr_to_data(node)
            for node in sorted(graph.attrs.values(), key=lambda item: item.node_id.to_wire())
        ],
        "calcs": [
            _calc_to_data(node)
            for node in sorted(graph.calcs.values(), key=lambda item: item.node_id.to_wire())
        ],
        "constraints": [
            _constraint_to_data(node)
            for node in sorted(graph.constraints.values(), key=lambda item: item.node_id.to_wire())
        ],
        "constraint_usages": [
            _constraint_usage_to_data(record)
            for record in sorted(
                graph.constraint_usages.values(),
                key=lambda item: item.declaration_id.to_wire(),
            )
        ],
        "diagnostics": [_diagnostic_to_data(item) for item in graph.diagnostics],
    }


def encode_instance_graph(graph: InstanceGraph) -> bytes:
    """Encode one validated resolved graph as canonical fingerprinted JSON bytes."""
    try:
        graph.validate()
        graph_data = _graph_to_data(graph)
        payload = {
            "schema_version": INSTANCE_GRAPH_SCHEMA_VERSION,
            "fingerprint": _fingerprint(INSTANCE_GRAPH_SCHEMA_VERSION, graph_data),
            "graph": graph_data,
        }
        return _canonical(payload)
    except InstanceGraphCodecError:
        raise
    except (GraphValidationError, TypeError, ValueError) as error:
        raise InstanceGraphCodecError(f"cannot encode resolved graph: {error}") from error


def decode_instance_graph(payload: bytes | str) -> InstanceGraph:
    """Validate and reconstruct a resolved graph without loading a semantic model."""
    try:
        raw = json.loads(payload, object_pairs_hook=_reject_duplicate_keys)
        document = _mapping(
            raw,
            "instance graph document",
            {"schema_version", "fingerprint", "graph"},
        )
        schema_version = _string(document.get("schema_version"), "document.schema_version")
        if schema_version != INSTANCE_GRAPH_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported instance graph schema {schema_version!r}; "
                f"expected {INSTANCE_GRAPH_SCHEMA_VERSION!r}"
            )
        graph_data = _mapping(
            document.get("graph"),
            "document.graph",
            {
                "occurrences",
                "attrs",
                "calcs",
                "constraints",
                "constraint_usages",
                "diagnostics",
            },
        )
        expected = _fingerprint(schema_version, graph_data)
        actual = _string(document.get("fingerprint"), "document.fingerprint")
        if actual != expected:
            raise ValueError("resolved graph fingerprint mismatch")

        occurrences: dict[OccurrenceId, OccurrenceRecord] = {}
        for raw_record in _list(graph_data.get("occurrences"), "graph.occurrences"):
            occurrence = _occurrence_from_data(raw_record)
            if occurrence.occurrence_id in occurrences:
                raise ValueError("duplicate occurrence identity")
            occurrences[occurrence.occurrence_id] = occurrence
        attrs: dict[NodeId, AttrNode] = {}
        for raw_node in _list(graph_data.get("attrs"), "graph.attrs"):
            attr_node = _attr_from_data(raw_node)
            if attr_node.node_id in attrs:
                raise ValueError("duplicate attribute node identity")
            attrs[attr_node.node_id] = attr_node
        calcs: dict[NodeId, CalcNode] = {}
        for raw_node in _list(graph_data.get("calcs"), "graph.calcs"):
            calc_node = _calc_from_data(raw_node)
            if calc_node.node_id in calcs:
                raise ValueError("duplicate calculation node identity")
            calcs[calc_node.node_id] = calc_node
        constraints: dict[NodeId, ConstraintNode] = {}
        for raw_node in _list(graph_data.get("constraints"), "graph.constraints"):
            constraint_node = _constraint_from_data(raw_node)
            if constraint_node.node_id in constraints:
                raise ValueError("duplicate constraint node identity")
            constraints[constraint_node.node_id] = constraint_node
        constraint_usages: dict[DeclarationId, ConstraintUsageRecord] = {}
        for raw_record in _list(
            graph_data.get("constraint_usages"), "graph.constraint_usages"
        ):
            record = _constraint_usage_from_data(raw_record)
            if record.declaration_id in constraint_usages:
                raise ValueError("duplicate usage record")
            constraint_usages[record.declaration_id] = record
        graph = InstanceGraph(
            occurrences=occurrences,
            attrs=attrs,
            calcs=calcs,
            constraints=constraints,
            constraint_usages=constraint_usages,
            diagnostics=[
                _diagnostic_from_data(item)
                for item in _list(graph_data.get("diagnostics"), "graph.diagnostics")
            ],
        )
        graph.validate()
        return graph
    except InstanceGraphCodecError:
        raise
    except (GraphValidationError, json.JSONDecodeError, TypeError, ValueError, KeyError) as error:
        raise InstanceGraphCodecError(f"invalid resolved graph payload: {error}") from error


def _mapping(
    value: object,
    label: str,
    exact_keys: set[str] | None = None,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    if not all(isinstance(key, str) for key in value):
        raise ValueError(f"{label} keys must be strings")
    if exact_keys is not None:
        _require_exact_keys(value, label, exact_keys)
    return value


def _require_exact_keys(value: dict[str, Any], label: str, keys: set[str]) -> None:
    actual = set(value)
    if actual != keys:
        raise ValueError(
            f"{label} has missing keys {sorted(keys - actual)!r} "
            f"and unknown keys {sorted(actual - keys)!r}"
        )


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def _list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    return value


def _string(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    return value


def _optional_string(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _string(value, label)


def _integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    return value


def _boolean(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a Boolean")
    return value
