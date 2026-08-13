"""Throwaway Item 6 probe: calc-def constraint attachment over the landed exact graph.

This does not mutate production behavior. It runs the shipped exact elaborator in lenient mode so
the current, expected ``SI_CONSTRAINT_UNATTACHED`` diagnostic does not hide the calculation nodes
whose identities and resolved inputs are under test.

Names are emitted only as display evidence. Every attachment and formal-actual lookup in the probe
uses ``DeclarationId``, ``FeatureSlotId``, or ``NodeId`` equality.
"""

from __future__ import annotations

import dataclasses
import json
from collections import Counter
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration.elaborate import _ExactElaborator
from sysml_codegen.elaboration.graph import LiteralInput, NodeRef, ProducerRef
from sysml_codegen.elaboration.identity import (
    ConsumerPortId,
    NodeId,
    NodeKind,
    declaration_id_for,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.snapshot.instance_graph import decode_instance_graph, encode_instance_graph

PROBE_DIR = Path(__file__).resolve().parent
SCENARIOS = {"zero": 0, "one": 1, "multiple": 2}


def _resolved_value(graph: Any, edge: Any) -> dict[str, Any]:
    if isinstance(edge, NodeRef):
        target = graph.attrs[edge.target]
        return {
            "kind": "node_ref",
            "target_node_id": edge.target.to_wire(),
            "target_declaration_id": target.declaration_id.to_wire(),
            "target_display": target.display_path,
        }
    if isinstance(edge, ProducerRef):
        return {
            "kind": "producer_ref",
            "target_calculation_id": edge.target.calculation.to_wire(),
            "target_output_id": edge.target.output.to_wire(),
        }
    if isinstance(edge, LiteralInput):
        return {"kind": "literal", "value": edge.value}
    raise AssertionError(f"unexpected resolved input {edge!r}")


def _formal_actuals(builder: _ExactElaborator, graph: Any, calc: Any) -> list[dict[str, Any]]:
    """Recover one calc occurrence's actual/default map through exact formal identity.

    An authored binding port is the redefining declaration on the calculation usage. The live
    feature-slot index maps it to the root formal declared by the calculation definition. An
    unbound/defaulted port already uses that root declaration. Neither path compares names.
    """
    rows: list[dict[str, Any]] = []
    seen_roots = set()
    for port in sorted(calc.input_names, key=lambda item: item.formal.to_wire()):
        assert isinstance(port, ConsumerPortId)
        root_formal = builder._slots.slot_of(port.formal).root_declaration
        assert root_formal not in seen_roots, (
            f"{calc.node_id.to_wire()} maps more than one port to formal "
            f"{root_formal.to_wire()}"
        )
        seen_roots.add(root_formal)
        metadata = calc.input_metadata[port]
        root_element = builder._elements[root_formal]
        row = {
            "root_formal_id": root_formal.to_wire(),
            "root_formal_display": str(getattr(root_element, "name", None) or ""),
            "occurrence_port_declaration_id": port.formal.to_wire(),
            "port_is_root_formal": port.formal == root_formal,
            "serialized_formal_provenance": metadata.formal_provenance is not None,
        }
        if port in calc.inputs:
            row["resolution"] = _resolved_value(graph, calc.inputs[port])
        else:
            assert port.formal in calc.unbound_formals
            row["resolution"] = {
                "kind": "modeled_default",
                "value": metadata.default_value,
                "unit": metadata.unit,
                "unresolved_default_kind": metadata.unresolved_default_kind,
            }
        rows.append(row)
    return rows


def _load_scenario(name: str) -> tuple[_ExactElaborator, Any, Any]:
    model_dir = PROBE_DIR / "models" / name
    extractor = SysMLDataExtractor([model_dir])
    assert extractor.load_models(), f"failed to load {model_dir}"
    calc_defs = extractor.extract_calculation_definitions()
    builder = _ExactElaborator(extractor.model, calc_defs, strict=False)
    graph = builder.run()
    return builder, extractor.model, graph


def _run_scenario(name: str, expected_count: int) -> dict[str, Any]:
    builder, model, graph = _load_scenario(name)
    usages = list(
        SysideAdapter.elements_of_type(model, "ConstraintUsage", include_subtypes=True)
    )
    assert len(usages) == 1
    usage = usages[0]
    usage_id = declaration_id_for(usage)
    owner = builder._semantic_owner(usage)
    owner_definition_id = declaration_id_for(owner)
    usage_record = graph.constraint_usages[usage_id]

    # The proposed attachment relation. Both sides are landed exact IDs: the semantic owner's
    # DeclarationId and each CalcNode's exact calculation_definition_id.
    matching_calcs = sorted(
        (
            calc
            for calc in graph.calcs.values()
            if calc.calculation_definition_id == owner_definition_id
        ),
        key=lambda calc: calc.node_id.to_wire(),
    )
    assert len(matching_calcs) == expected_count
    assert all(calc.calculation_definition_id == owner_definition_id for calc in matching_calcs)

    attachments = []
    current_constraint_node_ids = []
    actual_kinds = []
    for calc in matching_calcs:
        actuals = _formal_actuals(builder, graph, calc)
        actual_kinds.append(sorted(row["resolution"]["kind"] for row in actuals))
        composite_identity = {
            "constraint_usage_id": usage_id.to_wire(),
            "calculation_node_id": calc.node_id.to_wire(),
        }
        current_node_id = NodeId(NodeKind.CONSTRAINT, calc.scope, usage_id).to_wire()
        current_constraint_node_ids.append(current_node_id)
        attachments.append(
            {
                "identity": composite_identity,
                "calculation_usage_id": calc.declaration_id.to_wire(),
                "calculation_definition_id": calc.calculation_definition_id.to_wire(),
                "calculation_display": calc.display_path,
                "resolved_formals": actuals,
                "current_constraint_node_id": current_node_id,
            }
        )

    composite_keys = [json.dumps(row["identity"], sort_keys=True) for row in attachments]
    assert len(composite_keys) == len(set(composite_keys))

    # Exercise the landed v3 codec. The round trip retains calc node identities and resolved
    # InputRefs, but it intentionally has no live feature-slot index.
    decoded = decode_instance_graph(encode_instance_graph(graph))
    assert set(decoded.calcs) == set(graph.calcs)
    assert all(decoded.calcs[key].inputs == graph.calcs[key].inputs for key in graph.calcs)

    record_fields = {field.name for field in dataclasses.fields(usage_record)}
    has_exact_owner_field = bool(
        {"owner_declaration_id", "owner_definition_id", "calculation_definition_id"}
        & record_fields
    )
    explicit_ports_without_root_provenance = sum(
        1
        for attachment in attachments
        for formal in attachment["resolved_formals"]
        if not formal["port_is_root_formal"]
        and not formal["serialized_formal_provenance"]
    )

    if name == "zero":
        assert not attachments
    elif name == "one":
        assert actual_kinds == [["modeled_default", "node_ref"]]
    elif name == "multiple":
        assert Counter(tuple(kinds) for kinds in actual_kinds) == Counter(
            {("modeled_default", "node_ref"): 1, ("literal", "modeled_default"): 1}
        )
        # Two calculation usages of Sizer are siblings in one part occurrence. The current
        # constraint NodeId shape loses the calculation usage identity and therefore collides.
        assert len(set(current_constraint_node_ids)) == 1
        assert len(set(composite_keys)) == 2

    return {
        "scenario": name,
        "asserted_constraint_usage_id": usage_id.to_wire(),
        "owner_calculation_definition_id": owner_definition_id.to_wire(),
        "current_disposition": {
            "kind": usage_record.disposition.kind,
            "reason": usage_record.disposition.reason,
            "severity": usage_record.disposition.severity,
        },
        "matching_calculation_occurrences": len(matching_calcs),
        "attachments": attachments,
        "landed_context": {
            "constraint_usage_record_has_exact_owner_id": has_exact_owner_field,
            "explicit_ports_without_serialized_root_formal_provenance": (
                explicit_ports_without_root_provenance
            ),
            "snapshot_round_trip_retains_calc_nodes_and_resolved_inputs": True,
            "current_constraint_node_identity_count": len(set(current_constraint_node_ids)),
            "composite_attachment_identity_count": len(set(composite_keys)),
        },
    }


def main() -> None:
    results = [_run_scenario(name, count) for name, count in SCENARIOS.items()]
    constraint_usage_ids = {row["asserted_constraint_usage_id"] for row in results}
    owner_definition_ids = {row["owner_calculation_definition_id"] for row in results}
    assert len(constraint_usage_ids) == 1, "the three variants must preserve usage identity"
    assert len(owner_definition_ids) == 1, "the three variants must preserve definition identity"

    output = {
        "probe_status": "PASS",
        "identity_rule": (
            "match ConstraintUsage semantic-owner DeclarationId to "
            "CalcNode.calculation_definition_id; identify each attachment by "
            "(constraint usage DeclarationId, CalcNode.node_id)"
        ),
        "lookup_fields_used": [
            "DeclarationId",
            "FeatureSlotId.root_declaration",
            "CalcNode.calculation_definition_id",
            "CalcNode.node_id",
            "ConsumerPortId.formal",
        ],
        "rendered_names_used_for_lookup": False,
        "scenarios": results,
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
