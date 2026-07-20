"""The one producer-resolution authority (Item 2).

Every consumer that asks *which real thing produces this consumed value?* — a
calculation binding, a constraint actual, an aggregation term — builds a
:class:`ProducerRequest` and reads a :class:`ProducerResolution`. The ordered key-form
table, the self-reference guard, and the terminal fork live here and nowhere else.

**Tier versus key form.** A tier is a claim about what class of thing may produce a
value; contract invariant 19 names two — a real producer channel, then a real design
attribute under exact qualified identity. A key form is one way of asking "is it here?"
The three ladders this replaces drifted not because they tried many key forms (they
tried about two dozen, nearly all exact) but because each invented its own list, its own
guard placement, and its own terminal behavior. So the forms are declared as data, in
one order, and a consumer cannot add, reorder, or skip one.

**Name-based forms are lenient-only.** Rows marked ``lenient_only`` identify candidates
by name rather than by exact key. None of them guesses: each returns a result only when
exactly one candidate survives, and records the tie otherwise. They are unreachable from
the strict constraint consumer, which is exactly where they are unreachable today — all
eleven of that consumer's lookups are exact.

**A residual, recorded rather than hidden.** No single total order reproduces all three
ladders' current precedence: the calculation ladder tries the structured alias forms
(rows 6, 8) before the bare alias form (row 5), and the constraint ladder tries them in
the opposite order. The table takes the constraint order. Measured across the corpus, no
reference reaches more than one of those rows — 44 of 249 calculation bindings hit
exactly one, none hits two — so the conflict is latent, not exercised. Byte identity is
the standing control if that ever changes.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from sysml_codegen.core.output_registry import (
    OutputRegistry,
    ScopedAliasKey,
    ScopedKey,
    SysMLQN,
)
from sysml_codegen.core.qualified_names import (
    get_channel_name,
    sanitize_name,
    sanitize_qualified_name,
)

if TYPE_CHECKING:
    from sysml_codegen.analysis.parameter_groups import DesignAttributeData
    from sysml_codegen.extraction.data_models import RedefinitionData

__all__ = [
    "KEY_FORMS",
    "KeyForm",
    "Outcome",
    "ProducerContext",
    "ProducerRequest",
    "ProducerResolution",
    "TerminalPolicy",
    "Tier",
    "entry_point_qualified_name",
    "resolve_producer",
]


class Tier(Enum):
    """The two positive-resolution tiers of contract invariant 19."""

    CHANNEL = 1
    DESIGN_ATTRIBUTE = 2


class TerminalPolicy(Enum):
    """What a consumer does when the whole table misses. The only fork."""

    STRICT = "strict"
    LENIENT = "lenient"


class Outcome(Enum):
    """What a resolution produced."""

    MODULE_OUTPUT = "module_output"
    DESIGN_ATTRIBUTE = "design_attribute"
    ENTRY_POINT = "entry_point"


@dataclass(frozen=True)
class ProducerRequest:
    """One consumer's question, as declared data.

    ``reference`` is the reference the consumer holds, never pre-split. Note that the
    calculation consumer holds the *resolved referent qualified name* rather than the
    reference as written — binding extraction discards the written name — which is why
    the occurrence-materialized form (row 15) is unreachable from it. See design PC-4
    and ``tests/fixtures/shared_producer/PROVENANCE.md``.

    ``target_qn`` is the resolved referent where the consumer carries it separately from
    the reference; row 16 keys on it.
    """

    consumer_eqn: str
    reference: str
    param_name: str | None
    consumer_scope: str
    policy: TerminalPolicy
    diagnostic_context: str
    instance_path: str | None = None
    owner_def_qn: str | None = None
    target_qn: str | None = None
    parent_scope: str | None = None


@dataclass(frozen=True)
class ProducerResolution:
    """What the table produced, plus enough context for a contextual error."""

    outcome: Outcome
    identity: str
    default_value: float | None = None
    simple_name: str | None = None
    records_v11: bool = False
    key_form: str | None = None
    attempted: tuple[str, ...] = ()
    ambiguous_candidates: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProducerContext:
    """Everything the table may read. Built once per run.

    Named to avoid the ``ResolutionContext`` this replaces.
    """

    output_registry: OutputRegistry
    design_attr_by_qn: dict[str, DesignAttributeData] = field(default_factory=dict)
    design_attrs: tuple[DesignAttributeData, ...] = ()
    redefinitions: tuple[RedefinitionData, ...] = ()
    usage_type_map: dict[tuple[str, str], str] = field(default_factory=dict)
    calc_def_qns: frozenset[str] = frozenset()

    @property
    def canonical_channels(self) -> frozenset[str]:
        return frozenset(str(c) for c in self.output_registry.canonical_channels)


# ---------------------------------------------------------------------------
# Shared string surgery, moved here with the forms that need it
# ---------------------------------------------------------------------------


def deindexed_scope(scope: str) -> str:
    """Strip every ``[i]`` occurrence bracket from a dotted scope."""
    out: list[str] = []
    skip = False
    for ch in scope:
        if ch == "[":
            skip = True
        elif ch == "]":
            skip = False
        elif not skip:
            out.append(ch)
    return "".join(out)


def _is_calc_def_owned(qualified_name: str, context: ProducerContext) -> bool:
    """True when a "design attribute" QN is really a calc-def I/O attribute.

    Design attributes are extracted from every attribute carrying a value expression,
    which includes calc-def ``out attribute y = expr`` outputs. Matching one of those by
    leaf name would cross-wire a module-output binding into a design-attribute entry
    point carrying a library default.
    """
    return qualified_name.rsplit("__", 1)[0] in context.calc_def_qns


# ---------------------------------------------------------------------------
# Key forms. Each returns (identity, tied_candidates).
# ---------------------------------------------------------------------------

FormResult = tuple[str | None, tuple[str, ...]]
FormFn = Callable[[ProducerRequest, ProducerContext], FormResult]

_MISS: FormResult = (None, ())


def _hit(value: str | None) -> FormResult:
    return (value, ()) if value else _MISS


def _scoped_prefixed(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    if not req.consumer_scope:
        return _MISS
    key = ScopedKey(f"{req.consumer_scope}.{req.reference}")
    return _hit(_str_or_none(ctx.output_registry.scoped_lookup(key)))


def _scoped_deindexed(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    scope = deindexed_scope(req.consumer_scope)
    if not scope or scope == req.consumer_scope:
        return _MISS
    key = ScopedKey(f"{scope}.{req.reference}")
    return _hit(_str_or_none(ctx.output_registry.scoped_lookup(key)))


def _scoped_bare(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    return _hit(_str_or_none(ctx.output_registry.scoped_lookup(ScopedKey(req.reference))))


def _alias_prefixed(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    if not req.consumer_scope:
        return _MISS
    key = ScopedKey(f"{req.consumer_scope}.{req.reference}")
    return _hit(_str_or_none(ctx.output_registry.alias_lookup(key)))


def _alias_deindexed(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    scope = deindexed_scope(req.consumer_scope)
    if not scope or scope == req.consumer_scope:
        return _MISS
    key = ScopedKey(f"{scope}.{req.reference}")
    return _hit(_str_or_none(ctx.output_registry.alias_lookup(key)))


def _alias_bare(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    return _hit(_str_or_none(ctx.output_registry.alias_lookup(ScopedKey(req.reference))))


def _scoped_alias_prefixed(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    if "." not in req.reference or not req.consumer_scope:
        return _MISS
    prefix, leaf = req.reference.rsplit(".", 1)
    key = ScopedAliasKey((f"{req.consumer_scope}.{prefix}", leaf))
    return _hit(_str_or_none(ctx.output_registry.scoped_alias_lookup(key)))


def _scoped_alias_deindexed(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    scope = deindexed_scope(req.consumer_scope)
    if "." not in req.reference or not scope or scope == req.consumer_scope:
        return _MISS
    prefix, leaf = req.reference.rsplit(".", 1)
    key = ScopedAliasKey((f"{scope}.{deindexed_scope(prefix)}", leaf))
    return _hit(_str_or_none(ctx.output_registry.scoped_alias_lookup(key)))


def _structured_alias_unscoped(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    if "." not in req.reference:
        return _MISS
    prefix, leaf = req.reference.rsplit(".", 1)
    key = ScopedAliasKey((prefix, leaf))
    return _hit(_str_or_none(ctx.output_registry.scoped_alias_lookup(key)))


def _structured_alias_deindexed(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    if "." not in req.reference:
        return _MISS
    prefix, leaf = req.reference.rsplit(".", 1)
    de = deindexed_scope(prefix)
    if de == prefix:
        return _MISS
    return _hit(_str_or_none(ctx.output_registry.scoped_alias_lookup(ScopedAliasKey((de, leaf)))))


def _sysml_qn(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    key = SysMLQN(sanitize_qualified_name(req.reference))
    return _hit(_str_or_none(ctx.output_registry.sysml_qn_lookup(key)))


def _direct_channel(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    """Construct a CalcUsage-format channel and return it iff it is registered."""
    if "." not in req.reference or not req.instance_path:
        return _MISS
    prefix, output_name = req.reference.rsplit(".", 1)
    channel = get_channel_name(f"{req.instance_path}__{prefix.replace('.', '__')}", output_name)
    return _hit(channel if channel in ctx.canonical_channels else None)


def _reference_leaf(reference: str) -> str:
    """The reference's last segment, however it is spelled."""
    for sep in ("::", "."):
        if sep in reference:
            return reference.rsplit(sep, 1)[-1]
    return reference


def _leaf_under(scope: str, req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    if not scope:
        return _MISS
    key = ScopedKey(f"{scope}.{_reference_leaf(req.reference)}")
    channel = ctx.output_registry.scoped_lookup(key) or ctx.output_registry.alias_lookup(key)
    return _hit(_str_or_none(channel))


def _leaf_parent_scoped(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    """Leaf recombined with the consumer's immediate parent part.

    Name-based: the reference's own owner is never consulted, so `Pkg::PartA::x` and
    `Pkg::PartB::x` construct the same key. Lenient-only for that reason.
    """
    return _leaf_under(req.parent_scope or "", req, ctx)


def _leaf_consumer_scoped(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    """Leaf recombined with the consumer's full scope. Name-based, as above."""
    if req.consumer_scope == (req.parent_scope or ""):
        return _MISS
    return _leaf_under(req.consumer_scope, req, ctx)


def _chain_redefinition_follow(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    """Follow ``:>>`` CHAIN redefinitions to a constructed channel.

    The recursion and its cycle guard are real mechanism. The case-insensitive match and
    the first-``break`` that this form replaces were not: a leaf-name collision resolved
    to whichever redefinition happened to come first. Here the match is case-sensitive
    and ties refuse.
    """
    from sysml_codegen.extraction.data_models import RedefinitionType

    if "." not in req.reference or not req.instance_path:
        return _MISS
    visited: set[str] = set()

    def follow(ref: str) -> FormResult:
        if "." not in ref or ref in visited:
            return _MISS
        visited.add(ref)
        part_usage, attr = ref.rsplit(".", 1)
        matches = [
            r
            for r in ctx.redefinitions
            if r.redefinition_type == RedefinitionType.CHAIN
            and r.attribute_name == attr
            and sanitize_name(r.owning_part_qn.split("__")[-1]) == part_usage
        ]
        targets = sorted({r.source_path for r in matches if r.source_path})
        if len(targets) > 1:
            return None, tuple(targets)
        if not targets:
            return _MISS
        target = targets[0]
        if "." in target:
            calc_usage, output = target.rsplit(".", 1)
            channel = get_channel_name(
                f"{req.instance_path}__{part_usage}__{calc_usage}", output
            )
            if channel in ctx.canonical_channels:
                return channel, ()
        return follow(target)

    return follow(req.reference)


def _occurrence_materialized_qn(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    if not req.instance_path:
        return _MISS
    qn = f"{req.instance_path}__{'__'.join(req.reference.split('.'))}"
    return _hit(qn if qn in ctx.design_attr_by_qn else None)


def _target_qn(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    raw = req.target_qn if req.target_qn is not None else req.reference
    qn = sanitize_qualified_name(raw)
    return _hit(qn if qn in ctx.design_attr_by_qn else None)


def _owner_def_qn(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    if not req.owner_def_qn:
        return _MISS
    qn = f"{req.owner_def_qn}__{'__'.join(req.reference.split('.'))}"
    return _hit(qn if qn in ctx.design_attr_by_qn else None)


def _unique_or_tie(candidates: Iterable[DesignAttributeData]) -> FormResult:
    """Refuse rather than guess: a result only when exactly one candidate survives."""
    qns = sorted({c.qualified_name for c in candidates})
    if len(qns) == 1:
        return qns[0], ()
    return None, tuple(qns)


def _dotted_pair(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    """Dotted reference matched as ``(first segment, leaf)`` against parent/name."""
    if "." not in req.reference:
        return _MISS
    parts = req.reference.split(".")
    parent, leaf = parts[0], parts[-1]
    return _unique_or_tie(
        a for a in ctx.design_attrs if a.name == leaf and a.parent_part == parent
    )


def _leaf_unique(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    """Leaf name unique across files, with calc-def-owned attributes filtered out."""
    if "." not in req.reference:
        return _MISS
    leaf = req.reference.split(".")[-1]
    return _unique_or_tie(
        a
        for a in ctx.design_attrs
        if a.name == leaf and not _is_calc_def_owned(a.qualified_name, ctx)
    )


def _bare_name_unique(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    """Bare reference matched by attribute name, unique or refused."""
    if "." in req.reference or "::" in req.reference:
        return _MISS
    return _unique_or_tie(a for a in ctx.design_attrs if a.name == req.reference)


def _str_or_none(value: object) -> str | None:
    return str(value) if value is not None else None


@dataclass(frozen=True)
class KeyForm:
    """One declared way of asking whether a producer is here."""

    number: int
    name: str
    tier: Tier
    lookup: FormFn
    lenient_only: bool = False


KEY_FORMS: tuple[KeyForm, ...] = (
    KeyForm(1, "scoped_prefixed", Tier.CHANNEL, _scoped_prefixed),
    KeyForm(2, "scoped_deindexed", Tier.CHANNEL, _scoped_deindexed),
    KeyForm(3, "scoped_bare", Tier.CHANNEL, _scoped_bare),
    KeyForm(4, "alias_prefixed", Tier.CHANNEL, _alias_prefixed),
    KeyForm(5, "alias_deindexed", Tier.CHANNEL, _alias_deindexed),
    KeyForm(6, "scoped_alias_prefixed", Tier.CHANNEL, _scoped_alias_prefixed),
    KeyForm(7, "scoped_alias_deindexed", Tier.CHANNEL, _scoped_alias_deindexed),
    KeyForm(8, "structured_alias_unscoped", Tier.CHANNEL, _structured_alias_unscoped),
    KeyForm(9, "structured_alias_deindexed", Tier.CHANNEL, _structured_alias_deindexed),
    KeyForm(10, "alias_bare", Tier.CHANNEL, _alias_bare),
    KeyForm(11, "sysml_qn", Tier.CHANNEL, _sysml_qn),
    KeyForm(12, "direct_channel", Tier.CHANNEL, _direct_channel),
    KeyForm(13, "chain_redefinition_follow", Tier.CHANNEL, _chain_redefinition_follow,
            lenient_only=True),
    KeyForm(14, "leaf_parent_scoped", Tier.CHANNEL, _leaf_parent_scoped, lenient_only=True),
    KeyForm(15, "leaf_consumer_scoped", Tier.CHANNEL, _leaf_consumer_scoped, lenient_only=True),
    KeyForm(16, "occurrence_materialized_qn", Tier.DESIGN_ATTRIBUTE, _occurrence_materialized_qn),
    KeyForm(17, "target_qn", Tier.DESIGN_ATTRIBUTE, _target_qn),
    KeyForm(18, "owner_def_qn", Tier.DESIGN_ATTRIBUTE, _owner_def_qn),
    KeyForm(19, "dotted_pair", Tier.DESIGN_ATTRIBUTE, _dotted_pair, lenient_only=True),
    KeyForm(20, "leaf_unique", Tier.DESIGN_ATTRIBUTE, _leaf_unique, lenient_only=True),
    KeyForm(21, "bare_name_unique", Tier.DESIGN_ATTRIBUTE, _bare_name_unique, lenient_only=True),
)


def entry_point_qualified_name(
    *, consumer_eqn: str, reference: str, param_name: str | None
) -> str:
    """The QN of an entry point minted by a lenient terminal miss (D9).

    One rule for all three lenient consumers, chosen to reproduce every formula already
    in the tree byte-for-byte: the calculation binding path keys on the consumer's
    declared formal, which a calc binding always has; the aggregation term and LocalTerm
    paths have no formal, so they key on the reference with its dots flattened to
    underscores (a bare attribute name flattens to itself).
    """
    key = param_name if param_name is not None else reference.replace(".", "_")
    return f"{consumer_eqn}__{key}"


def _is_self_reference(channel: str, consumer_eqn: str) -> bool:
    """One predicate, applied at every tier-1 hit for every consumer.

    A consumer's input may not resolve to a channel its own module produces — that is a
    cycle in every consumer's graph. Today this guard sits at three different
    granularities and is missing from two paths entirely; here it is applied once, and a
    rejection skips the candidate and continues the table rather than abandoning the
    remaining keys.
    """
    return channel.rsplit("__", 1)[0] == consumer_eqn


def _scope_climb(req: ProducerRequest, ctx: ProducerContext) -> FormResult:
    """The tier-1 terminal search: retry the scoped key under ancestor scopes.

    Not a table row. It collects every distinct non-self-referential channel the
    ancestor prefixes reach and returns one only when they agree — that collect-then-
    require-unique behavior is its whole justification, and modelling it as an ordered
    row would lose it. Gated to 3+-segment chains. The ``i = len(segments)`` and
    ``i = 0`` iterations are omitted: they rebuild rows 1 and 3 byte-identically and are
    guaranteed misses by the time the climb runs.
    """
    if req.reference.count(".") < 2:
        return _MISS
    segments = req.consumer_scope.split(".") if req.consumer_scope else []
    climbed: set[str] = set()
    for i in range(len(segments) - 1, 0, -1):
        prefix = ".".join(segments[:i])
        channel = _str_or_none(
            ctx.output_registry.scoped_lookup(ScopedKey(f"{prefix}.{req.reference}"))
        )
        if channel is not None and not _is_self_reference(channel, req.consumer_eqn):
            climbed.add(channel)
    if len(climbed) == 1:
        return next(iter(climbed)), ()
    return None, tuple(sorted(climbed))


def _admissible(form: KeyForm, policy: TerminalPolicy) -> bool:
    return not (form.lenient_only and policy is TerminalPolicy.STRICT)


def _modeled_default(qualified_name: str, ctx: ProducerContext) -> float | None:
    attr = ctx.design_attr_by_qn.get(qualified_name)
    if attr is None or attr.default_value is None:
        return None
    try:
        return float(attr.default_value)
    except (TypeError, ValueError):
        return None


def resolve_producer(
    request: ProducerRequest, context: ProducerContext
) -> ProducerResolution:
    """The only positive-resolution path in the tree.

    Runs the declared table in order, tier 1 before tier 2, applying the self-reference
    guard at every tier-1 hit and the lenient-only admissibility rule at every row. Then
    the tier-1 terminal search. Then, and only then, reads the terminal policy.
    """
    attempted: list[str] = []
    ties: tuple[str, ...] = ()

    for tier in (Tier.CHANNEL, Tier.DESIGN_ATTRIBUTE):
        for form in KEY_FORMS:
            if form.tier is not tier or not _admissible(form, request.policy):
                continue
            attempted.append(form.name)
            identity, tied = form.lookup(request, context)
            if tied:
                ties = ties or tied
            if identity is None:
                continue
            if tier is Tier.CHANNEL:
                if _is_self_reference(identity, request.consumer_eqn):
                    continue
                return ProducerResolution(
                    outcome=Outcome.MODULE_OUTPUT,
                    identity=identity,
                    key_form=form.name,
                    attempted=tuple(attempted),
                )
            return ProducerResolution(
                outcome=Outcome.DESIGN_ATTRIBUTE,
                identity=identity,
                default_value=_modeled_default(identity, context),
                simple_name=identity.rsplit("__", 1)[-1],
                key_form=form.name,
                attempted=tuple(attempted),
            )
        if tier is Tier.CHANNEL:
            attempted.append("scope_climb")
            identity, tied = _scope_climb(request, context)
            if tied:
                ties = ties or tied
            if identity is not None:
                return ProducerResolution(
                    outcome=Outcome.MODULE_OUTPUT,
                    identity=identity,
                    key_form="scope_climb",
                    attempted=tuple(attempted),
                )

    return _terminal_miss(request, tuple(attempted), ties)


def _terminal_miss(
    request: ProducerRequest, attempted: tuple[str, ...], ties: tuple[str, ...]
) -> ProducerResolution:
    """The one place strict and lenient differ."""
    if request.policy is TerminalPolicy.STRICT:
        from sysml_codegen.orchestration.pipeline_context import CodeGenerationError

        detail = f"; tied candidates: {', '.join(ties)}" if ties else ""
        raise CodeGenerationError(
            f"{request.diagnostic_context}: unresolved actual '{request.reference}' "
            f"(strict mode: no fallback, no entry-point synthesis — INV-2). "
            f"Attempted: {', '.join(attempted)}{detail}"
        )

    qualified_name = entry_point_qualified_name(
        consumer_eqn=request.consumer_eqn,
        reference=request.reference,
        param_name=request.param_name,
    )
    return ProducerResolution(
        outcome=Outcome.ENTRY_POINT,
        identity=qualified_name,
        simple_name=request.param_name or request.reference.replace(".", "_"),
        attempted=attempted,
        ambiguous_candidates=ties,
    )
