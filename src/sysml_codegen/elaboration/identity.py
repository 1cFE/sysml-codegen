"""Exact semantic identity types for the elaborate-first front end.

Parser UUIDs are wrapped once here. Semantic code compares these frozen values;
wire strings and display names never participate in lookup or equality.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any
from uuid import UUID

from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration.diagnostics import (
    ElaborationCode,
    ElaborationInvariantError,
)

__all__ = [
    "ConsumerPortId",
    "DeclarationId",
    "ExpressionPortId",
    "FeatureSlotId",
    "IdentityBoundaryError",
    "NodeId",
    "NodeKind",
    "OccurrenceId",
    "OccurrenceStep",
    "OutputPortId",
    "PackageScopeId",
    "ResolvedSemanticReference",
    "ScopeId",
    "declaration_id_for",
]


class IdentityBoundaryError(ElaborationInvariantError):
    """A parser element cannot enter the stable declaration-ID boundary."""

    def __init__(self, detail: str, *, missing: bool = False) -> None:
        super().__init__(
            ElaborationCode.SI_ID_MISSING if missing else ElaborationCode.SI_ID_UNSTABLE,
            detail,
        )


@dataclass(frozen=True, order=True)
class DeclarationId:
    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise TypeError("DeclarationId requires uuid.UUID")

    def to_wire(self) -> str:
        return str(self.value)

    @classmethod
    def from_wire(cls, value: str) -> DeclarationId:
        return cls(UUID(value))


def declaration_id_for(element: Any) -> DeclarationId:
    """Wrap a reload-stable QN-bearing parser declaration.

    SysIDE 0.8.4 gives null-QN declarations session-local UUIDv4 values. They
    are exact inside one document but cannot enter the projectable graph.
    """
    qualified_name = getattr(element, "qualified_name", None)
    if qualified_name is None:
        raise IdentityBoundaryError(
            f"{type(element).__name__} has no reload-stable qualified declaration identity"
        )
    raw = SysideAdapter.element_id(element)
    if raw.version != 5:
        raise IdentityBoundaryError(
            f"{type(element).__name__} declaration ID {raw} is not reload-stable UUIDv5"
        )
    return DeclarationId(raw)


@dataclass(frozen=True, order=True)
class FeatureSlotId:
    root_declaration: DeclarationId


@dataclass(frozen=True, order=True)
class OccurrenceStep:
    containment_slot: FeatureSlotId
    occurrence_index: int | None

    def __post_init__(self) -> None:
        if self.occurrence_index is not None and self.occurrence_index < 0:
            raise ValueError("occurrence index must be non-negative")


@dataclass(frozen=True, order=True)
class OccurrenceId:
    steps: tuple[OccurrenceStep, ...]

    def __post_init__(self) -> None:
        if not self.steps:
            raise ValueError("OccurrenceId requires at least one containment step")

    def to_wire(self) -> str:
        payload = [
            [step.containment_slot.root_declaration.to_wire(), step.occurrence_index]
            for step in self.steps
        ]
        return json.dumps(payload, separators=(",", ":"))

    @classmethod
    def from_wire(cls, value: str) -> OccurrenceId:
        payload = json.loads(value)
        if not isinstance(payload, list):
            raise ValueError("occurrence wire value must be a list")
        return cls(
            tuple(
                OccurrenceStep(
                    FeatureSlotId(DeclarationId.from_wire(raw_declaration)),
                    index,
                )
                for raw_declaration, index in payload
            )
        )


@dataclass(frozen=True, order=True)
class PackageScopeId:
    package_declaration: DeclarationId


type ScopeId = OccurrenceId | PackageScopeId


class NodeKind(str, Enum):
    ATTRIBUTE = "attribute"
    CALCULATION = "calculation"
    CONSTRAINT = "constraint"


type NodeDeclaration = FeatureSlotId | DeclarationId


@dataclass(frozen=True)
class NodeId:
    kind: NodeKind
    scope: ScopeId
    declaration: NodeDeclaration

    def to_wire(self) -> str:
        if isinstance(self.scope, OccurrenceId):
            scope = ["occurrence", self.scope.to_wire()]
        else:
            scope = ["package", self.scope.package_declaration.to_wire()]
        if isinstance(self.declaration, FeatureSlotId):
            declaration = ["slot", self.declaration.root_declaration.to_wire()]
        else:
            declaration = ["declaration", self.declaration.to_wire()]
        return json.dumps([self.kind.value, scope, declaration], separators=(",", ":"))

    @classmethod
    def from_wire(cls, value: str) -> NodeId:
        kind_value, scope_value, declaration_value = json.loads(value)
        scope_kind, scope_payload = scope_value
        if scope_kind == "occurrence":
            scope: ScopeId = OccurrenceId.from_wire(scope_payload)
        elif scope_kind == "package":
            scope = PackageScopeId(DeclarationId.from_wire(scope_payload))
        else:
            raise ValueError(f"unknown scope kind {scope_kind!r}")
        declaration_kind, declaration_payload = declaration_value
        if declaration_kind == "slot":
            declaration: NodeDeclaration = FeatureSlotId(
                DeclarationId.from_wire(declaration_payload)
            )
        elif declaration_kind == "declaration":
            declaration = DeclarationId.from_wire(declaration_payload)
        else:
            raise ValueError(f"unknown node declaration kind {declaration_kind!r}")
        return cls(NodeKind(kind_value), scope, declaration)


@dataclass(frozen=True)
class OutputPortId:
    calculation: NodeId
    output: DeclarationId

    def __post_init__(self) -> None:
        if self.calculation.kind is not NodeKind.CALCULATION:
            raise ValueError("OutputPortId calculation must be a calculation node")


@dataclass(frozen=True)
class ConsumerPortId:
    consumer: NodeId
    formal: DeclarationId

    def __post_init__(self) -> None:
        if self.consumer.kind not in (NodeKind.CALCULATION, NodeKind.CONSTRAINT):
            raise ValueError("consumer port owner must be a calculation or constraint")


@dataclass(frozen=True)
class ExpressionPortId:
    """Structural input position on a computed or aggregation node."""

    consumer: NodeId
    reference_ordinal: int
    edge_ordinal: int
    referenced_declaration: DeclarationId
    target_occurrence: OccurrenceId | None = None

    def __post_init__(self) -> None:
        if self.consumer.kind is not NodeKind.CALCULATION:
            raise ValueError("expression port owner must be a calculation node")
        if self.reference_ordinal < 0 or self.edge_ordinal < 0:
            raise ValueError("expression port ordinals must be non-negative")


@dataclass(frozen=True)
class ResolvedSemanticReference:
    root_id: DeclarationId
    segment_ids: tuple[DeclarationId, ...]
    leaf_id: DeclarationId

    def __post_init__(self) -> None:
        if not self.segment_ids:
            raise ValueError("resolved semantic reference requires path segments")
        if self.segment_ids[-1] != self.leaf_id:
            raise ValueError("resolved semantic reference leaf must end its segments")
