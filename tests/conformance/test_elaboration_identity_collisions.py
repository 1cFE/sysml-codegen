"""Identity collision and typed-edge validation for the exact graph."""

from __future__ import annotations

from uuid import UUID

import pytest
from agentic_mbse.sysml.expression_facts import FeatureReferenceFact
from agentic_mbse.sysml.expression_ir import FeatureReferenceNode, OperatorNode

from sysml_codegen.elaboration import (
    AttrNode,
    CalcNode,
    ConsumerPortId,
    DeclarationId,
    ElaborationCode,
    ExpressionPortId,
    FeatureSlotId,
    GraphValidationError,
    InstanceGraph,
    LiteralInput,
    NodeId,
    NodeKind,
    NodeRef,
    OutputPortId,
    PackageScopeId,
    PortMetadata,
    ProducerRef,
)
from sysml_codegen.extraction.expression_compiler import Compilability


def _declaration(value: int) -> DeclarationId:
    return DeclarationId(UUID(int=value))


def test_semantic_graph_keeps_same_rendered_names_distinct() -> None:
    package = PackageScopeId(_declaration(1))
    first_slot = FeatureSlotId(_declaration(2))
    second_slot = FeatureSlotId(_declaration(3))
    first_id = NodeId(NodeKind.ATTRIBUTE, package, first_slot)
    second_id = NodeId(NodeKind.ATTRIBUTE, package, second_slot)
    graph = InstanceGraph(
        attrs={
            first_id: AttrNode(
                first_id,
                package,
                _declaration(2),
                first_slot,
                "pkg__same_name",
                "same_name",
                "pkg::first",
            ),
            second_id: AttrNode(
                second_id,
                package,
                _declaration(3),
                second_slot,
                "pkg__same_name",
                "same_name",
                "pkg::second",
            ),
        }
    )

    graph.validate()
    assert set(graph.attrs) == {first_id, second_id}


def test_dangling_node_edge_raises_named_graph_error() -> None:
    package = PackageScopeId(_declaration(10))
    consumer_id = NodeId(NodeKind.CALCULATION, package, _declaration(11))
    formal = _declaration(12)
    missing_id = NodeId(
        NodeKind.ATTRIBUTE,
        package,
        FeatureSlotId(_declaration(13)),
    )
    port = ConsumerPortId(consumer_id, formal)
    consumer = CalcNode(
        node_id=consumer_id,
        scope=package,
        declaration_id=_declaration(11),
        display_path="pkg__consumer",
        display_name="consumer",
        calc_def_name="Consumer",
        calc_def_qualified_name="pkg::Consumer",
        inputs={port: NodeRef(missing_id)},
        input_names={port: "value"},
    )
    graph = InstanceGraph(calcs={consumer_id: consumer})

    with pytest.raises(GraphValidationError) as excinfo:
        graph.validate()

    assert excinfo.value.diagnostics[0].code is ElaborationCode.SI_EDGE_DANGLING


def test_output_and_expression_keys_do_not_collapse_on_rendered_name() -> None:
    package = PackageScopeId(_declaration(20))
    calculation_id = NodeId(NodeKind.CALCULATION, package, _declaration(21))
    first_output = _declaration(22)
    second_output = _declaration(23)
    first_operand = _declaration(24)
    second_operand = _declaration(25)
    first_port = ExpressionPortId(calculation_id, 0, 0, first_operand)
    second_port = ExpressionPortId(calculation_id, 1, 0, second_operand)
    calculation = CalcNode(
        node_id=calculation_id,
        scope=package,
        declaration_id=_declaration(21),
        display_path="pkg__collision",
        display_name="collision",
        calc_def_name="Collision",
        calc_def_qualified_name="pkg::Collision",
        inputs={first_port: LiteralInput(1.0), second_port: LiteralInput(2.0)},
        input_names={first_port: "same_name", second_port: "same_name"},
        input_metadata={first_port: PortMetadata(), second_port: PortMetadata()},
        outputs={
            first_output: OutputPortId(calculation_id, first_output),
            second_output: OutputPortId(calculation_id, second_output),
        },
        output_names={first_output: "same_name", second_output: "same_name"},
        output_metadata={
            first_output: PortMetadata(),
            second_output: PortMetadata(),
        },
        is_computed=True,
        expression_ir=OperatorNode(
            operator="+",
            operands=[
                FeatureReferenceNode(
                    FeatureReferenceFact("same_name", None, [], []),
                    None,
                ),
                FeatureReferenceNode(
                    FeatureReferenceFact("same_name", None, [], []),
                    None,
                ),
            ],
            operand_type=None,
        ),
        compilability=Compilability.FULLY_COMPILABLE,
    )
    graph = InstanceGraph(calcs={calculation_id: calculation})

    graph.validate()
    assert len(calculation.inputs) == 2
    assert len(calculation.outputs) == 2


def _cycle_calc(
    package: PackageScopeId,
    node_id: NodeId,
    declaration: DeclarationId,
    display_path: str,
    output: DeclarationId,
    port: ConsumerPortId,
    upstream: OutputPortId,
) -> CalcNode:
    """One structurally valid calc whose single input feeds on another's output."""
    return CalcNode(
        node_id=node_id,
        scope=package,
        declaration_id=declaration,
        display_path=display_path,
        display_name=display_path.rsplit("__", 1)[-1],
        calc_def_name="Cycle",
        calc_def_qualified_name="pkg::Cycle",
        inputs={port: ProducerRef(upstream)},
        input_names={port: "value_in"},
        input_metadata={port: PortMetadata()},
        outputs={output: OutputPortId(node_id, output)},
        output_names={output: "result"},
        output_metadata={output: PortMetadata()},
        compilability=Compilability.FULLY_COMPILABLE,
    )


def test_producer_cycle_diagnostic_names_each_participant_once_in_stable_order() -> None:
    """F-3: a producer cycle is refused with a diagnostic that carries every
    cycle participant exactly once, in a stable order independent of graph
    insertion order — never the anonymous ``<instance-graph>`` display."""
    package = PackageScopeId(_declaration(30))
    alpha_id = NodeId(NodeKind.CALCULATION, package, _declaration(31))
    beta_id = NodeId(NodeKind.CALCULATION, package, _declaration(32))
    alpha_out = _declaration(33)
    beta_out = _declaration(34)
    alpha = _cycle_calc(
        package,
        alpha_id,
        _declaration(31),
        "pkg__alpha_calc",
        alpha_out,
        ConsumerPortId(alpha_id, _declaration(35)),
        OutputPortId(beta_id, beta_out),
    )
    beta = _cycle_calc(
        package,
        beta_id,
        _declaration(32),
        "pkg__beta_calc",
        beta_out,
        ConsumerPortId(beta_id, _declaration(36)),
        OutputPortId(alpha_id, alpha_out),
    )

    with pytest.raises(GraphValidationError) as excinfo:
        InstanceGraph(calcs={alpha_id: alpha, beta_id: beta}).validate()

    cycles = [
        diagnostic
        for diagnostic in excinfo.value.diagnostics
        if "typed producer dependency cycle" in diagnostic.detail
    ]
    assert len(cycles) == 1, excinfo.value.diagnostics
    diagnostic = cycles[0]
    assert diagnostic.detail == "typed producer dependency cycle: pkg__alpha_calc -> pkg__beta_calc"
    assert diagnostic.detail.count("pkg__alpha_calc") == 1
    assert diagnostic.detail.count("pkg__beta_calc") == 1
    assert diagnostic.consumer == alpha_id
    assert diagnostic.consumer_display == "pkg__alpha_calc"

    with pytest.raises(GraphValidationError) as reordered:
        InstanceGraph(calcs={beta_id: beta, alpha_id: alpha}).validate()

    assert [item.detail for item in reordered.value.diagnostics] == [
        item.detail for item in excinfo.value.diagnostics
    ]
