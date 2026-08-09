"""Typed resolved instance graph for the exact-ID elaborator."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import TypeVar

from sysml_codegen.elaboration.diagnostics import ElaborationCode
from sysml_codegen.elaboration.identity import (
    ConsumerPortId,
    DeclarationId,
    ExpressionPortId,
    FeatureSlotId,
    NodeId,
    OutputPortId,
    ScopeId,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.source_evidence import ReadinessCode

__all__ = [
    "AttrNode",
    "CalcNode",
    "ConstraintNode",
    "Diagnostic",
    "ElaborationCode",
    "GraphValidationError",
    "InputPortId",
    "InputRef",
    "InstanceGraph",
    "LiteralInput",
    "PortMetadata",
    "NodeRef",
    "ProducerRef",
    "ValueSite",
]

_DisplayNode = TypeVar("_DisplayNode")


class ValueSite(str, Enum):
    NONE = "none"
    DEFINITION_DEFAULT = "definition_default"
    SPECIALIZED_DEF = "specialized_def"
    OCCURRENCE_OVERRIDE = "occurrence_override"


@dataclass(frozen=True)
class Diagnostic:
    code: ElaborationCode | ReadinessCode
    consumer: NodeId | None
    consumer_display: str
    param_name: str | None
    detail: str


class GraphValidationError(ValueError):
    """The typed graph violates referential integrity."""

    def __init__(self, diagnostics: list[Diagnostic]) -> None:
        self.diagnostics = tuple(diagnostics)
        super().__init__("; ".join(f"{item.code.value}: {item.detail}" for item in diagnostics))


@dataclass(frozen=True)
class NodeRef:
    target: NodeId


@dataclass(frozen=True)
class ProducerRef:
    target: OutputPortId


@dataclass(frozen=True)
class LiteralInput:
    value: float | int | str | bool


type InputRef = NodeRef | ProducerRef | LiteralInput
type InputPortId = ConsumerPortId | ExpressionPortId


@dataclass(frozen=True)
class PortMetadata:
    python_type: str = "float"
    description: str | None = None
    default_value: float | int | str | bool | None = None
    unit: str | None = None
    qualified_name: str | None = None
    unresolved_default_kind: str | None = None


@dataclass
class AttrNode:
    node_id: NodeId
    scope: ScopeId
    declaration_id: DeclarationId
    slot_id: FeatureSlotId
    display_path: str
    display_name: str
    declaration_qn: str
    value: float | int | str | bool | None = None
    value_site: ValueSite = ValueSite.NONE
    alias_target: InputRef | None = None
    is_alias: bool = False
    alias_shape: str | None = None
    source_file: str = "unknown"
    source_line: int = 0


@dataclass
class CalcNode:
    node_id: NodeId
    scope: ScopeId
    declaration_id: DeclarationId
    display_path: str
    display_name: str
    calc_def_name: str
    calc_def_qualified_name: str
    inputs: dict[InputPortId, InputRef] = field(default_factory=dict)
    input_names: dict[InputPortId, str] = field(default_factory=dict)
    input_metadata: dict[InputPortId, PortMetadata] = field(default_factory=dict)
    outputs: dict[DeclarationId, OutputPortId] = field(default_factory=dict)
    output_names: dict[DeclarationId, str] = field(default_factory=dict)
    output_metadata: dict[DeclarationId, PortMetadata] = field(default_factory=dict)
    unbound_formals: tuple[DeclarationId, ...] = ()
    is_computed: bool = False
    expression_ir: str | None = None
    aggregation_reference_ordinals: tuple[int, ...] = ()
    compilability: Compilability = Compilability.UNKNOWN
    auto_impl_context: dict | None = None
    doc_comment: str | None = None
    calc_expressions: tuple[str, ...] = ()
    source_file: str = "unknown"
    source_line: int = 0

    def input_by_name(self, name: str) -> InputRef:
        matches = [
            self.inputs[port]
            for port, display_name in self.input_names.items()
            if display_name == name and port in self.inputs
        ]
        if len(matches) != 1:
            raise KeyError(
                f"calculation {self.display_path!r} has {len(matches)} inputs named {name!r}"
            )
        return matches[0]


@dataclass
class ConstraintNode:
    node_id: NodeId
    scope: ScopeId
    declaration_id: DeclarationId
    display_path: str
    display_name: str
    constraint_def_name: str
    inputs: dict[InputPortId, InputRef] = field(default_factory=dict)
    input_names: dict[InputPortId, str] = field(default_factory=dict)
    input_metadata: dict[InputPortId, PortMetadata] = field(default_factory=dict)
    unbound_formals: tuple[DeclarationId, ...] = ()
    predicate_ir: str | None = None
    source_form: str = "plain_usage"
    owner_kind: str = "package"
    owner_qualified_name: str = ""
    usage_qualified_name: str = ""
    membership_kind: str | None = None
    predicate_source_key: str = ""
    is_negated: bool = False
    definition_qualified_name: str | None = None
    eligibility: str = "admit"
    exclusion_reasons: tuple[str, ...] = ()
    exclusion_location: str | None = None
    source_file: str = "unknown"
    source_line: int = 0

    def input_by_name(self, name: str) -> InputRef:
        matches = [
            self.inputs[port]
            for port, display_name in self.input_names.items()
            if display_name == name and port in self.inputs
        ]
        if len(matches) != 1:
            raise KeyError(
                f"constraint {self.display_path!r} has {len(matches)} inputs named {name!r}"
            )
        return matches[0]


@dataclass
class InstanceGraph:
    attrs: dict[NodeId, AttrNode] = field(default_factory=dict)
    calcs: dict[NodeId, CalcNode] = field(default_factory=dict)
    constraints: dict[NodeId, ConstraintNode] = field(default_factory=dict)
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def is_projectable(self) -> bool:
        return not self.diagnostics

    def validate(self) -> None:
        """Validate typed keys, ports, outputs, and direct edge targets."""
        failures: list[Diagnostic] = []
        for node_id, attr_node in self.attrs.items():
            if node_id != attr_node.node_id:
                failures.append(
                    self._dangling(node_id, attr_node.display_path, "attribute key mismatch")
                )
            if attr_node.alias_target is not None:
                self._validate_edge(
                    attr_node.node_id,
                    attr_node.display_path,
                    None,
                    attr_node.alias_target,
                    failures,
                )
        for node_id, calc_node in self.calcs.items():
            self._validate_consumer(node_id, calc_node, failures)
        for node_id, constraint_node in self.constraints.items():
            self._validate_consumer(node_id, constraint_node, failures)
        for calc_node in self.calcs.values():
            for declaration, port in calc_node.outputs.items():
                if port.calculation != calc_node.node_id or port.output != declaration:
                    failures.append(
                        self._dangling(
                            calc_node.node_id,
                            calc_node.display_path,
                            "output port does not match its calculation/declaration key",
                        )
                    )
        if failures:
            raise GraphValidationError(failures)

    def _validate_consumer(
        self,
        node_id: NodeId,
        node: CalcNode | ConstraintNode,
        failures: list[Diagnostic],
    ) -> None:
        if node_id != node.node_id:
            failures.append(self._dangling(node_id, node.display_path, "consumer key mismatch"))
        for port, edge in node.inputs.items():
            if port.consumer != node.node_id:
                failures.append(
                    self._dangling(
                        node.node_id,
                        node.display_path,
                        "consumer port belongs to another node",
                    )
                )
            self._validate_edge(
                node.node_id,
                node.display_path,
                node.input_names.get(port),
                edge,
                failures,
            )

    def require_projectable(self) -> None:
        """Reject partial lenient graphs before projection or generation."""
        self.validate()
        if self.diagnostics:
            raise GraphValidationError(list(self.diagnostics))

    def _validate_edge(
        self,
        consumer: NodeId,
        consumer_display: str,
        param_name: str | None,
        edge: InputRef,
        failures: list[Diagnostic],
    ) -> None:
        if isinstance(edge, NodeRef) and edge.target not in self.attrs:
            failures.append(
                self._dangling(
                    consumer,
                    consumer_display,
                    "attribute target is absent",
                    param_name,
                )
            )
        if isinstance(edge, ProducerRef):
            producer = self.calcs.get(edge.target.calculation)
            if producer is None or edge.target.output not in producer.outputs:
                failures.append(
                    self._dangling(
                        consumer,
                        consumer_display,
                        "producer output is absent",
                        param_name,
                    )
                )

    @staticmethod
    def _dangling(
        consumer: NodeId,
        consumer_display: str,
        detail: str,
        param_name: str | None = None,
    ) -> Diagnostic:
        return Diagnostic(
            code=ElaborationCode.SI_EDGE_DANGLING,
            consumer=consumer,
            consumer_display=consumer_display,
            param_name=param_name,
            detail=detail,
        )

    def attr_by_display_path(self, path: str) -> AttrNode:
        return self._unique_display(self.attrs, path)

    def calc_by_display_path(self, path: str) -> CalcNode:
        return self._unique_display(self.calcs, path)

    def constraint_by_display_path(self, path: str) -> ConstraintNode:
        return self._unique_display(self.constraints, path)

    @staticmethod
    def _unique_display(nodes: Mapping[NodeId, _DisplayNode], path: str) -> _DisplayNode:
        matches = [node for node in nodes.values() if getattr(node, "display_path") == path]
        if len(matches) != 1:
            raise KeyError(f"graph has {len(matches)} nodes displayed as {path!r}")
        return matches[0]

    def input_edge(self, consumer: NodeId, formal: DeclarationId) -> InputRef:
        if consumer in self.calcs:
            return self.calcs[consumer].inputs[ConsumerPortId(consumer, formal)]
        if consumer in self.constraints:
            return self.constraints[consumer].inputs[ConsumerPortId(consumer, formal)]
        raise KeyError(consumer)

    def semantic_edges(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                repr((node.node_id, port, edge))
                for population in (self.calcs, self.constraints)
                for node in population.values()
                for port, edge in node.inputs.items()
            )
        )

    def rendered_names_are_metadata_only(self) -> bool:
        return (
            all(isinstance(key, NodeId) for key in self.attrs)
            and all(isinstance(key, NodeId) for key in self.calcs)
            and all(isinstance(key, NodeId) for key in self.constraints)
            and all(
                isinstance(port, ConsumerPortId | ExpressionPortId)
                for population in (self.calcs, self.constraints)
                for node in population.values()
                for port in node.inputs
            )
        )
