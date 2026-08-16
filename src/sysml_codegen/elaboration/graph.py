"""Typed resolved instance graph for the exact-ID elaborator."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import TypeVar

from agentic_mbse.sysml.executable_profile import Eligibility
from agentic_mbse.sysml.expression_ir import (
    EXPRESSION_IR_SCHEMA_VERSION,
    ExpressionIR,
    FeatureReferenceNode,
    InvocationNode,
    LiteralNode,
    OperatorNode,
    UnitAnnotationNode,
    UnsupportedNode,
)

from sysml_codegen.core.models import AutoImplContext
from sysml_codegen.elaboration.diagnostics import ElaborationCode
from sysml_codegen.elaboration.identity import (
    ConsumerPortId,
    DeclarationId,
    ExpressionPortId,
    FeatureSlotId,
    NodeId,
    OccurrenceId,
    OutputPortId,
    ScopeId,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.source_evidence import ReadinessCode

__all__ = [
    "ASSERTED_SOURCE_FORMS",
    "AttrNode",
    "CalcNode",
    "ConstraintNode",
    "ConstraintUsageRecord",
    "DISPOSITION_REASONS",
    "Inapplicability",
    "SOURCE_FORMS",
    "UsageDisposition",
    "expected_severity",
    "Diagnostic",
    "ElaborationCode",
    "GraphValidationError",
    "InputPortId",
    "InputRef",
    "InstanceGraph",
    "LiteralInput",
    "PortMetadata",
    "FormalProvenance",
    "NodeRef",
    "OccurrenceRecord",
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
class FormalProvenance:
    declaration_id: DeclarationId
    raw_name: str
    qualified_name: str


@dataclass(frozen=True)
class PortMetadata:
    python_type: str = "float"
    description: str | None = None
    default_value: float | int | str | bool | None = None
    unit: str | None = None
    qualified_name: str | None = None
    unresolved_default_kind: str | None = None
    formal_provenance: FormalProvenance | None = None


@dataclass(frozen=True)
class OccurrenceRecord:
    occurrence_id: OccurrenceId
    parent_id: OccurrenceId | None
    containment_slot: FeatureSlotId
    occurrence_index: int | None
    effective_usage_id: DeclarationId
    effective_type_ids: tuple[DeclarationId, ...]
    display_segment: str
    package_display: str | None = None


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
    owner_qualified_name: str = ""


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
    expression_ir: ExpressionIR | None = None
    aggregation_reference_ordinals: tuple[int, ...] = ()
    compilability: Compilability = Compilability.UNKNOWN
    auto_impl_context: AutoImplContext | None = None
    doc_comment: str | None = None
    calc_expressions: tuple[str, ...] = ()
    calculation_definition_id: DeclarationId | None = None
    compilation_definition_id: DeclarationId | None = None
    compiled_output_ids: tuple[DeclarationId, ...] = ()
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
    eligibility: Eligibility
    effective_definition_id: DeclarationId | None
    inputs: dict[InputPortId, InputRef] = field(default_factory=dict)
    input_names: dict[InputPortId, str] = field(default_factory=dict)
    input_metadata: dict[InputPortId, PortMetadata] = field(default_factory=dict)
    unbound_formals: tuple[DeclarationId, ...] = ()
    predicate_ir: ExpressionIR | None = None
    source_form: str = "plain_usage"
    owner_kind: str = "package"
    owner_qualified_name: str = ""
    usage_qualified_name: str = ""
    membership_kind: str | None = None
    predicate_source_key: str = ""
    is_negated: bool = False
    definition_qualified_name: str | None = None
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


#: The three source forms that assert their predicate. Everything else — ``plain_usage``,
#: ``requirement_constraint``, ``satisfy_reference`` — states a condition without asking
#: for it to be enforced, and no non-asserted form ever grades ``error``.
ASSERTED_SOURCE_FORMS = frozenset({"definition_typed", "inline", "named_usage_reference"})

#: Every source form the classifier can emit, closed.
SOURCE_FORMS = frozenset(
    {
        "definition_typed",
        "inline",
        "named_usage_reference",
        "plain_usage",
        "requirement_constraint",
        "satisfy_reference",
    }
)

#: The closed reason vocabulary, per disposition kind.
DISPOSITION_REASONS: Mapping[str, frozenset[str]] = {
    "eligible": frozenset({"admitted"}),
    "excluded": frozenset(
        {
            "out_of_scope_satisfy",
            "out_of_profile_owner",
            "non_numerical",
            "unassessed_form",
            "profile_blocked",
        }
    ),
    "non_reaching": frozenset(
        {
            "owner_absent",
            "owner_kind_unattachable",
            "owner_has_no_occurrences",
            "classification_incomplete",
        }
    ),
}

#: Reason -> the severity an *asserted* form gets. A reason absent from this map is
#: ``info`` for every form; a reason present is that grade for an asserted form and
#: ``info`` otherwise. ``classification_incomplete`` only ever arises for an asserted
#: form, so it is unconditional.
_ASSERTED_SEVERITY: Mapping[str, str] = {
    "owner_absent": "error",
    "owner_kind_unattachable": "error",
    "owner_has_no_occurrences": "warning",
    "classification_incomplete": "error",
}


def expected_severity(reason: str, source_form: str) -> str:
    """The one severity a (reason, form) pair may carry.

    Severity is derived, never authored, and it keys on form *and* cause together: a
    non-reaching gate that nobody asserted is a fact about the model, while the same
    cause under an asserted form is either an authoring error (nothing could ever attach
    it) or a vacuous gate (nothing was ever instantiated to run it against).
    """
    if reason == "classification_incomplete":
        return "error"
    if source_form not in ASSERTED_SOURCE_FORMS:
        return "info"
    return _ASSERTED_SEVERITY.get(reason, "info")


@dataclass(frozen=True)
class UsageDisposition:
    """Why one authored constraint usage stands where it does. Exactly one per member."""

    kind: str
    reason: str
    severity: str
    detail: str


@dataclass(frozen=True)
class Inapplicability:
    """An author's explicit decision that a usage is not part of the feasible set.

    Carried beside the disposition and never folded into it: marking a gate
    inapplicable is a coverage statement, and it must not be able to suppress an
    authoring error.

    It holds the reason and nothing else. The annotation is written on the usage, so the
    usage record's own ``source_file`` and ``source_line`` already locate it, and a second
    copy of a source path here would be a second thing reaching the fingerprint that every
    route has to remember to rewrite — the defect ``exclusion_location`` already taught.
    """

    reason: str


@dataclass
class ConstraintUsageRecord:
    """One authored ``ConstraintUsage``, minted before occurrence expansion.

    This is the domain. It exists whether or not the usage's owner expanded to any
    scope, which is what makes totality a property of where records are born rather
    than a check bolted on after the population has already been truncated. It carries
    no ``predicate_ir`` — that authority stays on the per-occurrence tier, and leaving
    it off is what lets the mint stop before the predicate walk.
    """

    declaration_id: DeclarationId
    usage_qualified_name: str
    display_name: str
    source_form: str
    owner_kind: str
    owner_qualified_name: str
    membership_kind: str | None
    is_negated: bool
    source_file: str
    source_line: int
    disposition: UsageDisposition
    occurrence_count: int = 0
    inapplicability: Inapplicability | None = None
    definition_qualified_name: str | None = None


@dataclass
class InstanceGraph:
    occurrences: dict[OccurrenceId, OccurrenceRecord] = field(default_factory=dict)
    attrs: dict[NodeId, AttrNode] = field(default_factory=dict)
    calcs: dict[NodeId, CalcNode] = field(default_factory=dict)
    constraints: dict[NodeId, ConstraintNode] = field(default_factory=dict)
    constraint_usages: dict[DeclarationId, ConstraintUsageRecord] = field(default_factory=dict)
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def is_projectable(self) -> bool:
        return not self.diagnostics

    def validate(self) -> None:
        """Validate typed keys, ports, outputs, and direct edge targets."""
        failures: list[Diagnostic] = []
        self._validate_occurrences(failures)
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
            self._validate_calculation_payload(calc_node, failures)
        for node_id, constraint_node in self.constraints.items():
            self._validate_consumer(node_id, constraint_node, failures)
            self._validate_constraint_formal_provenance(constraint_node, failures)
            if not isinstance(constraint_node.eligibility, Eligibility):
                failures.append(
                    self._dangling(
                        node_id,
                        constraint_node.display_path,
                        "constraint eligibility is not a closed Eligibility value",
                    )
                )
            if (
                constraint_node.eligibility in (Eligibility.ADMIT, Eligibility.BLOCK)
                and constraint_node.predicate_ir is None
                and not self.diagnostics
            ):
                failures.append(
                    self._dangling(
                        node_id,
                        constraint_node.display_path,
                        "executable constraint predicate IR is absent",
                    )
                )
            if constraint_node.predicate_ir is not None:
                try:
                    self._validate_expression_tags(constraint_node.predicate_ir)
                except TypeError as error:
                    failures.append(
                        self._dangling(node_id, constraint_node.display_path, str(error))
                    )
            if (
                constraint_node.source_form == "definition_typed"
                and constraint_node.effective_definition_id is None
            ):
                failures.append(
                    self._dangling(
                        node_id,
                        constraint_node.display_path,
                        "definition-typed constraint has no effective definition identity",
                    )
                )
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
        self._validate_producer_cycles(failures)
        self._validate_constraint_usage_domain(failures)
        if failures:
            raise GraphValidationError(failures)

    def _validate_constraint_usage_domain(self, failures: list[Diagnostic]) -> None:
        """Per-record structure and the two-tier join, both by ``declaration_id``.

        This runs on the live route, on both decode paths, and on the sealed context, so
        a domain that arrives malformed from any of them is refused in the same place and
        with the same words. It checks join integrity, not totality: totality is
        established upstream by where the records are minted, and proven independently by
        the reviewed expected-population files.
        """
        for declaration_id, record in self.constraint_usages.items():
            display = record.usage_qualified_name
            if record.declaration_id != declaration_id:
                failures.append(
                    self._incomplete(
                        f"usage record key disagrees with its declaration id for {display}"
                    )
                )
            if record.source_form not in SOURCE_FORMS:
                failures.append(
                    self._incomplete(f"unknown source form {record.source_form!r} for {display}")
                )
            reasons = DISPOSITION_REASONS.get(record.disposition.kind)
            if reasons is None:
                failures.append(
                    self._incomplete(
                        f"unknown disposition kind {record.disposition.kind!r} for {display}"
                    )
                )
            elif record.disposition.reason not in reasons:
                failures.append(
                    self._incomplete(
                        f"reason {record.disposition.reason!r} is outside kind "
                        f"{record.disposition.kind!r} for {display}"
                    )
                )
            else:
                severity = expected_severity(record.disposition.reason, record.source_form)
                if record.disposition.severity != severity:
                    failures.append(
                        self._incomplete(
                            f"severity {record.disposition.severity!r} disagrees with the "
                            f"derived {severity!r} for {display}"
                        )
                    )
            if record.disposition.kind == "eligible" and record.occurrence_count == 0:
                failures.append(
                    self._incomplete(f"eligible usage reaches no occurrence: {display}")
                )

        counted: dict[DeclarationId, int] = {}
        for node in self.constraints.values():
            if node.declaration_id not in self.constraint_usages:
                failures.append(
                    self._incomplete(
                        "occurrence node joins no usage record: "
                        f"{node.usage_qualified_name} ({node.declaration_id.to_wire()})"
                    )
                )
                continue
            counted[node.declaration_id] = counted.get(node.declaration_id, 0) + 1
        for declaration_id, record in self.constraint_usages.items():
            nodes = counted.get(declaration_id, 0)
            if record.occurrence_count != nodes:
                failures.append(
                    self._incomplete(
                        f"occurrence_count {record.occurrence_count} disagrees with {nodes} "
                        f"nodes for {record.usage_qualified_name} "
                        f"({declaration_id.to_wire()})"
                    )
                )

    @staticmethod
    def _incomplete(detail: str) -> Diagnostic:
        return Diagnostic(
            code=ElaborationCode.SI_CONSTRAINT_INCOMPLETE,
            consumer=None,
            consumer_display="<constraint-usage-domain>",
            param_name=None,
            detail=f"constraint usage domain incomplete: {detail}",
        )

    def _validate_constraint_formal_provenance(
        self,
        node: ConstraintNode,
        failures: list[Diagnostic],
    ) -> None:
        for port, metadata in node.input_metadata.items():
            if not isinstance(port, ConsumerPortId):
                failures.append(
                    self._dangling(
                        node.node_id,
                        node.display_path,
                        "constraint input uses a non-formal port",
                    )
                )
                continue
            provenance = metadata.formal_provenance
            if provenance is None:
                failures.append(
                    self._dangling(
                        node.node_id,
                        node.display_path,
                        "constraint input has no exact formal provenance",
                    )
                )
                continue
            if provenance.declaration_id != port.formal:
                failures.append(
                    self._dangling(
                        node.node_id,
                        node.display_path,
                        "constraint formal provenance disagrees with its typed port",
                    )
                )
            if not provenance.raw_name or not provenance.qualified_name:
                failures.append(
                    self._dangling(
                        node.node_id,
                        node.display_path,
                        "constraint formal provenance lacks display metadata",
                    )
                )

    def _validate_occurrences(self, failures: list[Diagnostic]) -> None:
        for occurrence_id, record in self.occurrences.items():
            if occurrence_id != record.occurrence_id:
                failures.append(
                    self._graph_failure("occurrence key does not match its record")
                )
                continue
            final_step = occurrence_id.steps[-1]
            if (
                record.containment_slot != final_step.containment_slot
                or record.occurrence_index != final_step.occurrence_index
            ):
                failures.append(
                    self._graph_failure("occurrence containment fields disagree with its ID")
                )
            if not record.display_segment:
                failures.append(self._graph_failure("occurrence display segment is empty"))
            if record.parent_id is None:
                if len(occurrence_id.steps) != 1:
                    failures.append(
                        self._graph_failure("non-root occurrence has no parent record")
                    )
                if not record.package_display:
                    failures.append(
                        self._graph_failure("root occurrence has no package display metadata")
                    )
            else:
                if record.parent_id not in self.occurrences:
                    failures.append(
                        self._graph_failure("occurrence parent record is absent")
                    )
                elif record.parent_id.steps != occurrence_id.steps[:-1]:
                    failures.append(
                        self._graph_failure("occurrence parent does not match its structured ID")
                    )
                if record.package_display is not None:
                    failures.append(
                        self._graph_failure("non-root occurrence carries package display metadata")
                    )

        for population in (self.attrs, self.calcs, self.constraints):
            for node in population.values():
                if isinstance(node.scope, OccurrenceId) and node.scope not in self.occurrences:
                    failures.append(
                        self._dangling(
                            node.node_id,
                            node.display_path,
                            "occurrence-scoped node has no occurrence record",
                        )
                    )

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
        required_ports = set(node.inputs) | {
            ConsumerPortId(node.node_id, formal) for formal in node.unbound_formals
        }
        if not self.diagnostics:
            if set(node.input_names) != required_ports:
                failures.append(
                    self._dangling(
                        node.node_id,
                        node.display_path,
                        "input name inventory is not total",
                    )
                )
            if set(node.input_metadata) != required_ports:
                failures.append(
                    self._dangling(
                        node.node_id,
                        node.display_path,
                        "input metadata inventory is not total",
                    )
                )
        elif not set(node.inputs) <= set(node.input_names) & set(node.input_metadata):
            failures.append(
                self._dangling(
                    node.node_id,
                    node.display_path,
                    "resolved input lacks name or metadata",
                )
            )

    def _validate_calculation_payload(
        self,
        node: CalcNode,
        failures: list[Diagnostic],
    ) -> None:
        output_ids = set(node.outputs)
        if set(node.output_names) != output_ids:
            failures.append(
                self._dangling(
                    node.node_id,
                    node.display_path,
                    "output name inventory is not total",
                )
            )
        if set(node.output_metadata) != output_ids:
            failures.append(
                self._dangling(
                    node.node_id,
                    node.display_path,
                    "output metadata inventory is not total",
                )
            )
        if node.compilability is Compilability.UNKNOWN:
            failures.append(
                self._dangling(
                    node.node_id,
                    node.display_path,
                    "calculation compilation state is unknown",
                )
            )
        if node.is_computed:
            if node.expression_ir is None:
                failures.append(
                    self._dangling(
                        node.node_id,
                        node.display_path,
                        "computed calculation expression IR is absent",
                    )
                )
                return
            if node.compilability is not Compilability.FULLY_COMPILABLE:
                failures.append(
                    self._dangling(
                        node.node_id,
                        node.display_path,
                        "computed calculation is not explicitly fully compilable",
                    )
                )
            try:
                reference_count = self._expression_reference_count(node.expression_ir)
            except TypeError as error:
                failures.append(
                    self._dangling(node.node_id, node.display_path, str(error))
                )
                return
            ports = set(node.inputs) | set(node.input_names) | set(node.input_metadata)
            if not all(isinstance(port, ExpressionPortId) for port in ports):
                failures.append(
                    self._dangling(
                        node.node_id,
                        node.display_path,
                        "computed calculation has a non-expression input port",
                    )
                )
                return
            expression_ports = [port for port in ports if isinstance(port, ExpressionPortId)]
            ordinals = {port.reference_ordinal for port in expression_ports}
            expected_ordinals = set(range(reference_count))
            ordinals_are_valid = (
                ordinals <= expected_ordinals
                if self.diagnostics
                else ordinals == expected_ordinals
            )
            if not ordinals_are_valid:
                failures.append(
                    self._dangling(
                        node.node_id,
                        node.display_path,
                        "expression port ordinals do not match typed IR references",
                    )
                )
            aggregation_ordinals = set(node.aggregation_reference_ordinals)
            if not aggregation_ordinals <= expected_ordinals:
                failures.append(
                    self._dangling(
                        node.node_id,
                        node.display_path,
                        "aggregation ordinal does not identify a typed IR reference",
                    )
                )
            for ordinal in range(reference_count):
                count = sum(port.reference_ordinal == ordinal for port in expression_ports)
                if (
                    (not self.diagnostics and count == 0)
                    or (count > 0 and ordinal not in aggregation_ordinals and count != 1)
                ):
                    failures.append(
                        self._dangling(
                            node.node_id,
                            node.display_path,
                            f"typed IR reference {ordinal} has {count} permitted edges",
                        )
                    )
            return
        if node.expression_ir is not None:
            failures.append(
                self._dangling(
                    node.node_id,
                    node.display_path,
                    "non-computed calculation carries expression IR",
                )
            )
        if node.calculation_definition_id is None:
            failures.append(
                self._dangling(
                    node.node_id,
                    node.display_path,
                    "calculation definition identity is absent",
                )
            )
        if node.compilation_definition_id != node.calculation_definition_id:
            failures.append(
                self._dangling(
                    node.node_id,
                    node.display_path,
                    "compilation identity does not match the calculation definition",
                )
            )
        if set(node.compiled_output_ids) != output_ids:
            failures.append(
                self._dangling(
                    node.node_id,
                    node.display_path,
                    "compiled output identity does not match the graph outputs",
                )
            )

    @classmethod
    def _expression_reference_count(cls, expression: ExpressionIR) -> int:
        cls._validate_expression_tags(expression)
        if isinstance(expression, FeatureReferenceNode):
            return 1
        if isinstance(expression, LiteralNode):
            return 0
        if isinstance(expression, UnitAnnotationNode):
            return cls._expression_reference_count(expression.value)
        if isinstance(expression, OperatorNode):
            return sum(cls._expression_reference_count(item) for item in expression.operands)
        if isinstance(expression, InvocationNode):
            return sum(cls._expression_reference_count(item) for item in expression.arguments)
        if isinstance(expression, UnsupportedNode):
            raise TypeError("computed calculation contains unsupported typed IR")
        raise TypeError(
            "computed calculation contains invalid typed IR "
            f"{type(expression).__name__}"
        )

    @classmethod
    def _validate_expression_tags(cls, expression: ExpressionIR) -> None:
        expected_kind = {
            LiteralNode: "literal",
            FeatureReferenceNode: "feature_ref",
            OperatorNode: "operator",
            UnitAnnotationNode: "unit",
            InvocationNode: "invocation",
            UnsupportedNode: "unsupported",
        }.get(type(expression))
        if expected_kind is None:
            raise TypeError(f"invalid typed IR node {type(expression).__name__}")
        if (
            expression.kind != expected_kind
            or expression.schema_version != EXPRESSION_IR_SCHEMA_VERSION
        ):
            raise TypeError(
                f"invalid typed IR tags on {type(expression).__name__}"
            )
        if isinstance(expression, UnitAnnotationNode):
            cls._validate_expression_tags(expression.value)
        elif isinstance(expression, OperatorNode):
            for item in expression.operands:
                cls._validate_expression_tags(item)
        elif isinstance(expression, InvocationNode):
            for item in expression.arguments:
                cls._validate_expression_tags(item)

    def _validate_producer_cycles(self, failures: list[Diagnostic]) -> None:
        dependencies: dict[NodeId, set[NodeId]] = {
            node_id: set() for node_id in self.calcs
        }
        consumers = [
            (node.node_id, node.inputs) for node in self.calcs.values()
        ] + [
            (node.node_id, node.inputs) for node in self.constraints.values()
        ]
        for consumer_id, inputs in consumers:
            for edge in inputs.values():
                if isinstance(edge, ProducerRef):
                    dependencies.setdefault(consumer_id, set()).add(
                        edge.target.calculation
                    )

        def display(node_id: NodeId) -> str:
            node = self.calcs.get(node_id) or self.constraints.get(node_id)
            return node.display_path if node is not None else node_id.to_wire()

        # The DFS retains its active stack so a detected cycle can name every
        # participant; display-ordered visits keep the report deterministic
        # regardless of graph insertion order.
        stack: list[NodeId] = []
        active: set[NodeId] = set()
        complete: set[NodeId] = set()
        cycles: list[tuple[NodeId, ...]] = []

        def visit(node_id: NodeId) -> None:
            if node_id in active:
                cycles.append(tuple(stack[stack.index(node_id) :]))
                return
            if node_id in complete:
                return
            active.add(node_id)
            stack.append(node_id)
            for dependency in sorted(dependencies.get(node_id, ()), key=display):
                visit(dependency)
            stack.pop()
            active.remove(node_id)
            complete.add(node_id)

        for node_id in sorted(dependencies, key=display):
            visit(node_id)

        for cycle in cycles:
            participants = " -> ".join(display(node_id) for node_id in cycle)
            failures.append(
                Diagnostic(
                    code=ElaborationCode.SI_EDGE_DANGLING,
                    consumer=cycle[0],
                    consumer_display=display(cycle[0]),
                    param_name=None,
                    detail=f"typed producer dependency cycle: {participants}",
                )
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

    @staticmethod
    def _graph_failure(detail: str) -> Diagnostic:
        return Diagnostic(
            code=ElaborationCode.SI_EDGE_DANGLING,
            consumer=None,
            consumer_display="<instance-graph>",
            param_name=None,
            detail=detail,
        )

    def occurrence_display_path(self, occurrence_id: OccurrenceId) -> str:
        records = self._occurrence_lineage(occurrence_id)
        package_display = records[0].package_display
        if not package_display:
            raise KeyError(f"root occurrence {records[0].occurrence_id!r} has no package display")
        return "__".join(
            [package_display, *(record.display_segment for record in records)]
        )

    def occurrence_instance_path(self, occurrence_id: OccurrenceId) -> str:
        return "__".join(
            record.display_segment for record in self._occurrence_lineage(occurrence_id)
        )

    def _occurrence_lineage(
        self, occurrence_id: OccurrenceId
    ) -> tuple[OccurrenceRecord, ...]:
        records: list[OccurrenceRecord] = []
        current = self.occurrences[occurrence_id]
        records.append(current)
        while current.parent_id is not None:
            current = self.occurrences[current.parent_id]
            records.append(current)
        return tuple(reversed(records))

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
