"""Instance graph: the elaborated model (ELABORATE-FIRST Item 4 design, D1).

Node identity is the occurrence path: ``InstanceOccurrence.instance_path``
extended with member leaves, ``__``-joined — the same rendering
``PartInstanceIndex`` already produces. A modeled value is ONE attribute node
however many calculation, constraint, or aggregation consumers read it; every
consumer holds a typed reference to a node, never a string to re-resolve later
(spec R1/R2).

Indexed occurrences are positional (``cell[2]``): a model edit that reorders
siblings renames those nodes — accepted and recorded (D1), matrix-visible at
the Item-6 semantic review.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from sysml_codegen.extraction.source_evidence import ReadinessCode

__all__ = [
    "AttrNode",
    "CalcNode",
    "ConstraintNode",
    "Diagnostic",
    "ElaborationCode",
    "InputRef",
    "InstanceGraph",
    "LiteralInput",
    "NodeRef",
    "ProducerRef",
    "ValueSite",
]


class ValueSite(str, Enum):
    """Which value tier supplied an attribute node's effective value (design D4).

    Tiers are innermost-wins: occurrence ``:>>`` (deepest anchor) beats a
    specialized-def ``:>>`` beats the definition default. The value site drives
    entry-point classification directly at projection (D8) — no downstream
    backfill re-derives it.
    """

    NONE = "none"
    DEFINITION_DEFAULT = "definition_default"
    SPECIALIZED_DEF = "specialized_def"
    OCCURRENCE_OVERRIDE = "occurrence_override"


class ElaborationCode(str, Enum):
    """Elaboration-time diagnostic codes (design D9).

    The three extraction-detectable form codes (``SI_SELF_BINDING``,
    ``SI_INDEXED_SOURCE_UNSUPPORTED``, ``SI_EXPRESSION_SOURCE_UNSUPPORTED``)
    live in :class:`~sysml_codegen.extraction.source_evidence.ReadinessCode`
    and hard-fail elaboration; these are the occurrence-level outcomes.
    """

    SI_OCCURRENCE_MISSING = "SI_OCCURRENCE_MISSING"
    SI_OCCURRENCE_AMBIGUOUS = "SI_OCCURRENCE_AMBIGUOUS"
    OVERRIDE_TARGET_MISSING = "OVERRIDE_TARGET_MISSING"


@dataclass(frozen=True)
class Diagnostic:
    """One named elaboration finding. Never a fallback input (design D5).

    ``code`` is an occurrence-level :class:`ElaborationCode`, or — in lenient
    (report-not-halt) elaboration only — one of the contract's form codes
    (:class:`ReadinessCode`) that strict mode raises as
    :class:`~sysml_codegen.elaboration.elaborate.ElaborationError`. Strict vs
    lenient changes halt-vs-report, never identity (design D9).
    """

    code: ElaborationCode | ReadinessCode
    consumer: str
    param_name: str | None
    detail: str


@dataclass(frozen=True)
class NodeRef:
    """Edge to an attribute node: the consumer reads that node's value."""

    node_id: str


@dataclass(frozen=True)
class ProducerRef:
    """Edge to a calc node's output: the consumer reads a computed value."""

    calc_node_id: str
    output_name: str


@dataclass(frozen=True)
class LiteralInput:
    """An authored usage literal — its own source (contract value-site kind 3)."""

    value: float | int | str | bool


InputRef = NodeRef | ProducerRef | LiteralInput


@dataclass
class AttrNode:
    """One attribute occurrence: ``{occurrence_path}__{attr_name}``.

    ``decl_qn`` is the declaring ``AttributeUsage``'s raw ``::`` qualified name
    (definition-declared and possibly inherited, or declared on the part usage
    itself). ``value`` is the effective literal after tiering; ``None`` with
    ``value_site == NONE`` and no alias means no modeled value supplies this
    node (an entry-point candidate at projection).

    ``alias_target`` is the EXPOSE edge: an attribute whose declared value is a
    pure feature chain (``attribute pump_power = pump_load.pump_power``) does
    not hold a value — it aliases the chain's target, resolved per occurrence.
    Consumers reading such a node follow the alias to the real source, so the
    exposed attribute never mints an input of its own (spec R2).
    """

    node_id: str
    occurrence_path: str
    attr_name: str
    decl_qn: str
    value: float | int | str | bool | None = None
    value_site: ValueSite = ValueSite.NONE
    alias_target: InputRef | None = None


@dataclass
class CalcNode:
    """One concrete calculation occurrence — a calc usage or a computed attribute.

    ``calc_def_qualified_name`` keeps the raw ``::`` form — projection derives
    module types and the registry template requires it (spike probe 3).
    ``unbound_params`` are declared inputs with no binding: entry-point
    candidates, carried so projection never re-walks the model.

    A FORMULA attribute (``attribute area = length * width``) is a computed
    node (design D6): ``is_computed`` is set, its single output is
    ``calc_name`` (the attribute's own name), its ``inputs`` are the
    expression's term edges keyed by term path, both def-name fields are empty
    (no calc def exists), and ``expression_ast`` carries the live value
    expression for projection to render. Consumers referencing the attribute
    resolve to a producer edge on this node — never to an attribute node.
    """

    node_id: str
    calc_name: str
    calc_def_name: str
    calc_def_qualified_name: str
    inputs: dict[str, InputRef] = field(default_factory=dict)
    unbound_params: tuple[str, ...] = ()
    is_computed: bool = False
    expression_ast: object | None = None


@dataclass
class ConstraintNode:
    """One concrete constraint occurrence riding the same graph (design D7)."""

    node_id: str
    constraint_def_name: str
    inputs: dict[str, InputRef] = field(default_factory=dict)


@dataclass
class InstanceGraph:
    """The elaborated model: nodes keyed by occurrence-path node ID."""

    attrs: dict[str, AttrNode] = field(default_factory=dict)
    calcs: dict[str, CalcNode] = field(default_factory=dict)
    constraints: dict[str, ConstraintNode] = field(default_factory=dict)
    diagnostics: list[Diagnostic] = field(default_factory=list)

    def attr_at(self, occurrence_path: str, attr_name: str) -> AttrNode | None:
        """The attribute node for ``attr_name`` at an occurrence, if it exists."""
        return self.attrs.get(f"{occurrence_path}__{attr_name}")
