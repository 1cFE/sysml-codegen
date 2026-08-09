"""Display-metadata queries for elaboration conformance tests.

Production graph identity stays typed. Tests that describe fixtures by their
rendered paths convert those descriptions to typed IDs at the assertion edge.
"""

from __future__ import annotations

from sysml_codegen.elaboration import (
    AttrNode,
    CalcNode,
    ConstraintNode,
    InstanceGraph,
    NodeRef,
    ProducerRef,
)


def attr(graph: InstanceGraph, path: str) -> AttrNode:
    return graph.attr_by_display_path(path)


def calc(graph: InstanceGraph, path: str) -> CalcNode:
    return graph.calc_by_display_path(path)


def constraint(graph: InstanceGraph, path: str) -> ConstraintNode:
    return graph.constraint_by_display_path(path)


def node_ref(graph: InstanceGraph, path: str) -> NodeRef:
    return NodeRef(attr(graph, path).node_id)


def producer_ref(graph: InstanceGraph, path: str, output_name: str) -> ProducerRef:
    producer = calc(graph, path)
    matches = [
        producer.outputs[declaration]
        for declaration, name in producer.output_names.items()
        if name == output_name
    ]
    if len(matches) != 1:
        raise KeyError(
            f"calculation {path!r} has {len(matches)} outputs named {output_name!r}"
        )
    return ProducerRef(matches[0])


def inputs_by_name(node: CalcNode | ConstraintNode) -> dict[str, object]:
    return {
        node.input_names[port]: edge
        for port, edge in node.inputs.items()
    }
