"""Identity collision and typed-edge validation for the exact graph."""

from __future__ import annotations

from uuid import UUID

import pytest

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
)


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
        outputs={
            first_output: OutputPortId(calculation_id, first_output),
            second_output: OutputPortId(calculation_id, second_output),
        },
        output_names={first_output: "same_name", second_output: "same_name"},
        is_computed=True,
    )
    graph = InstanceGraph(calcs={calculation_id: calculation})

    graph.validate()
    assert len(calculation.inputs) == 2
    assert len(calculation.outputs) == 2
