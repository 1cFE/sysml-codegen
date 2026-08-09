"""Runtime contracts for exact elaboration identity types."""

from __future__ import annotations

from uuid import UUID

import pytest

from sysml_codegen.elaboration.identity import (
    ConsumerPortId,
    DeclarationId,
    FeatureSlotId,
    NodeId,
    NodeKind,
    OccurrenceId,
    OccurrenceStep,
    OutputPortId,
    PackageScopeId,
    ResolvedSemanticReference,
)


def _declaration(suffix: int) -> DeclarationId:
    return DeclarationId(UUID(f"00000000-0000-5000-8000-{suffix:012d}"))


def test_identity_namespaces_are_runtime_distinct_and_hashable() -> None:
    declaration = _declaration(1)
    slot = FeatureSlotId(declaration)
    occurrence = OccurrenceId((OccurrenceStep(slot, None),))
    package = PackageScopeId(_declaration(2))
    attr = NodeId(NodeKind.ATTRIBUTE, occurrence, slot)
    calc = NodeId(NodeKind.CALCULATION, occurrence, _declaration(3))
    output = OutputPortId(calc, _declaration(4))
    consumer = ConsumerPortId(calc, _declaration(5))

    assert declaration != slot
    assert occurrence != package
    assert len({attr, calc}) == 2
    assert output.calculation == calc
    assert consumer.consumer == calc


def test_identity_wire_values_are_canonical_and_round_trip() -> None:
    declaration = _declaration(10)
    slot = FeatureSlotId(declaration)
    occurrence = OccurrenceId(
        (OccurrenceStep(slot, None), OccurrenceStep(FeatureSlotId(_declaration(11)), 2))
    )
    node = NodeId(NodeKind.ATTRIBUTE, occurrence, FeatureSlotId(_declaration(12)))

    assert DeclarationId.from_wire(declaration.to_wire()) == declaration
    assert OccurrenceId.from_wire(occurrence.to_wire()) == occurrence
    assert NodeId.from_wire(node.to_wire()) == node
    assert declaration.to_wire() == str(declaration.value)


def test_identity_constructors_reject_wrong_runtime_types() -> None:
    with pytest.raises(TypeError):
        DeclarationId("00000000-0000-5000-8000-000000000001")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        OccurrenceStep(FeatureSlotId(_declaration(1)), -1)
    with pytest.raises(ValueError):
        OutputPortId(
            NodeId(
                NodeKind.ATTRIBUTE,
                OccurrenceId((OccurrenceStep(FeatureSlotId(_declaration(1)), None),)),
                FeatureSlotId(_declaration(2)),
            ),
            _declaration(3),
        )


def test_resolved_reference_keeps_exact_root_segments_and_leaf() -> None:
    reference = ResolvedSemanticReference(
        root_id=_declaration(20),
        segment_ids=(_declaration(21), _declaration(22)),
        leaf_id=_declaration(22),
    )
    assert reference.root_id != reference.leaf_id
    assert reference.segment_ids[-1] == reference.leaf_id
