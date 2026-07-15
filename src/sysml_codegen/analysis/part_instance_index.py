"""Part-instance index: subtype closure and cardinality expansion over part structure.

A second, structure-only enumerator that answers, per part definition, what all the
concrete occurrences of that definition are — counting subtype instances and
fixed-multiplicity siblings, each as its own identity. It runs beside the calc-driven
instantiation-path finder in ``usage_extractor.py`` and never through it: this module
is additive, imported by nothing else in this item (Item 5 wires it in).
"""

from dataclasses import dataclass, field
from typing import Any, Protocol

from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.core.qualified_names import build_element_qualified_name, sanitize_name
from sysml_codegen.extraction.usage_extractor import (
    _build_part_usage_index,
    _supertype_closure,
    most_specific,
    owned_feature_typing_targets,
    user_partdef_lookup,
    user_partdef_types,
)


@dataclass(frozen=True)
class PathStep:
    """One step of a structured instantiation path.

    ``occurrence_index`` is set only when the step's usage carries a fixed
    multiplicity (``classify_cardinality`` returned ``Fixed``); it is ``None`` for a
    singleton step.
    """

    owning_def_qn: str
    feature_name: str
    occurrence_index: int | None


@dataclass(frozen=True)
class Fixed:
    """A usage's multiplicity is a single, provably finite literal count."""

    count: int


@dataclass(frozen=True)
class NonFinite:
    """A usage's multiplicity cannot be proven to be a single finite count."""

    reason: str


class NonFiniteCardinalityError(Exception):
    """Raised when a queried path passes through a non-finite multiplicity.

    Names the owning part definition and the part usage feature so the diagnostic
    is actionable — the index never silently drops a non-finite shape (Design
    Principle 5: no third disposition beyond expand-finite or block-loud).
    """

    def __init__(self, owning_part_def_qn: str, part_usage_name: str, reason: str) -> None:
        self.owning_part_def_qn = owning_part_def_qn
        self.part_usage_name = part_usage_name
        self.reason = reason
        super().__init__(
            f"Non-finite multiplicity on '{part_usage_name}' owned by "
            f"'{owning_part_def_qn}' ({reason}); cannot expand to concrete instances."
        )


def classify_cardinality(usage: Any, owning_def_qn: str, feature_name: str) -> Fixed | NonFinite:
    """Classify a usage's multiplicity as a single fixed count or non-finite.

    Called only for a usage that carries a multiplicity node (``usage.multiplicity
    is not None``); a singleton usage is the walker's job, not this function's.

    Reads only the usage's live ``multiplicity`` node and its ``is_ordered`` /
    ``is_nonunique`` flags — never ``MultiplicityData`` or any cached bound, both of
    which are confirmed unreliable for this gate (B1/B2 evidence, design.md D3/D8):
    a parameterized ``[n]`` resolves its default into ``cached_upper_bound``, so a
    cached-value gate would silently expand the default instead of blocking it.

    Dispatch is fail-closed: any ``upper_bound`` node type other than
    ``LiteralInteger`` or the two explicitly recognized non-finite shapes
    (``LiteralInfinity``, ``FeatureReferenceExpression``) blocks, so a future SysIDE
    surface change cannot silently start expanding.
    """
    if usage.is_ordered:
        return NonFinite(reason=f"'{feature_name}' is ordered")
    if usage.is_nonunique:
        return NonFinite(reason=f"'{feature_name}' is nonunique")

    multiplicity = usage.multiplicity
    upper_bound = multiplicity.upper_bound
    lower_bound = multiplicity.lower_bound

    if SysideAdapter.is_instance(upper_bound, "LiteralInfinity"):
        return NonFinite(reason=f"'{feature_name}' is unbounded ([*])")
    if SysideAdapter.is_instance(upper_bound, "FeatureReferenceExpression"):
        return NonFinite(reason=f"'{feature_name}' has a parameterized multiplicity")
    if not SysideAdapter.is_instance(upper_bound, "LiteralInteger"):
        return NonFinite(
            reason=f"'{feature_name}' has an unrecognized multiplicity bound "
            f"({type(upper_bound).__name__})"
        )

    upper = upper_bound.value
    if lower_bound is None:
        return Fixed(count=upper)
    if not SysideAdapter.is_instance(lower_bound, "LiteralInteger"):
        return NonFinite(
            reason=f"'{feature_name}' has an unrecognized lower multiplicity bound "
            f"({type(lower_bound).__name__})"
        )

    lower = lower_bound.value
    if lower == upper:
        return Fixed(count=upper)
    return NonFinite(reason=f"'{feature_name}' has a multiplicity range [{lower}..{upper}]")


def _cardinality_indices(usage: Any, owning_def_qn: str, feature_name: str) -> list[int | None]:
    """Return the occurrence indices a usage's own multiplicity fans into.

    A singleton (``usage.multiplicity is None``) fans into a single step with index
    ``None``. A gated ``Fixed(n)`` fans into ``n`` indexed copies. ``NonFinite``
    raises — every multiplicity on a queried path is gated, not just the leaf
    (design.md#potential-risks "intermediate-container multiplicity").
    """
    if usage.multiplicity is None:
        return [None]
    verdict = classify_cardinality(usage, owning_def_qn, feature_name)
    if isinstance(verdict, NonFinite):
        raise NonFiniteCardinalityError(owning_def_qn, feature_name, verdict.reason)
    return list(range(verdict.count))


def _structured_paths(
    target_part_def_qn: str,
    part_usage_index: dict[str, list[Any]],
    _visited: set[str] | None = None,
) -> list[tuple[tuple[PathStep, ...], Any]]:
    """Structured sibling of ``_find_instantiation_paths`` (usage_extractor.py:313-369).

    Mirrors its owning-type recursion but keeps each step's ``(owning_def_qn,
    feature_name, occurrence_index)`` instead of flattening to a joined string, and
    gates every step's multiplicity — not just the leaf — via
    ``_cardinality_indices``. Keep this walker in sync with
    ``_find_instantiation_paths`` by hand if that function's recursion shape
    changes; it is not modified here (INV-1: the original stays untouched).

    Returns ``(path, usage)`` pairs, where ``usage`` is the PartUsage that produced
    the path at *this* invocation (i.e. typed as ``target_part_def_qn``) — callers
    use it to compute the leaf's entry-independent ``part_def_qn`` (D5/C3).
    """
    if _visited is None:
        _visited = set()
    if target_part_def_qn in _visited:
        return []
    _visited = _visited | {target_part_def_qn}

    usages = part_usage_index.get(target_part_def_qn, [])
    if not usages:
        return []

    seen: set[tuple[PathStep, ...]] = set()
    result: list[tuple[tuple[PathStep, ...], Any]] = []

    for usage in usages:
        usage_name = sanitize_name(getattr(usage, "name", ""))
        owning_type = getattr(usage, "owning_type", None)
        if owning_type is not None and SysideAdapter.is_instance(owning_type, "PartDefinition"):
            # Recursive step: usage is a feature of a PartDefinition. Recurse to
            # find every live instance of that owning def, then fan this usage's
            # own multiplicity onto each — the Cartesian product down the path.
            parent_def_qn = build_element_qualified_name(owning_type)
            parent_paths = _structured_paths(parent_def_qn, part_usage_index, _visited)
            for parent_path, _parent_usage in parent_paths:
                for index in _cardinality_indices(usage, parent_def_qn, usage_name):
                    path = parent_path + (PathStep(parent_def_qn, usage_name, index),)
                    if path not in seen:
                        seen.add(path)
                        result.append((path, usage))
        else:
            # Terminal step: owned by a Package or a PartUsage, not a PartDefinition.
            base = build_element_qualified_name(getattr(usage, "owner", None))
            for index in _cardinality_indices(usage, base, usage_name):
                path = (PathStep(base, usage_name, index),)
                if path not in seen:
                    seen.add(path)
                    result.append((path, usage))

    return result


@dataclass(frozen=True)
class InstanceOccurrence:
    """One concrete part occurrence: a structured path plus its own type.

    ``part_def_qn`` is the usage's own most-specific user type (D5) — computed
    once from the usage itself, never from the closure-entry type the walk
    arrived through, so a double-keyed retyped usage collapses to one record
    with the correct (sub)type (C3).
    """

    part_def_qn: str
    steps: tuple[PathStep, ...]

    @property
    def instance_path(self) -> str:
        """Human-readable path, e.g. ``InstanceIndexProbe__root__bank__member[0]``."""
        rendered = self.steps[0].owning_def_qn
        for step in self.steps:
            rendered += f"__{step.feature_name}"
            if step.occurrence_index is not None:
                rendered += f"[{step.occurrence_index}]"
        return rendered


def _occurrence_sort_key(
    occurrence: InstanceOccurrence,
) -> tuple[tuple[str, ...], tuple[int, ...]]:
    """Deterministic order (D6): integer indices, never rendered-string order.

    Singleton steps normalize to ``-1`` so a future key change cannot reintroduce
    a ``None < int`` comparison hazard; comparing ``indices`` only matters when
    ``segment_names`` already match, so aligned positions are guaranteed.
    """
    segment_names = tuple(step.feature_name for step in occurrence.steps)
    indices = tuple(
        step.occurrence_index if step.occurrence_index is not None else -1
        for step in occurrence.steps
    )
    return segment_names, indices


@dataclass(frozen=True)
class AllOccurrencesResult:
    """Result of a bulk occurrence dump: occurrences plus every blocked definition.

    Cured post-audit (Certify-with-notes, part-instance-index/audit.md): the prior
    ``all_occurrences()`` silently ``continue``d past a
    :class:`NonFiniteCardinalityError` per definition — a third disposition INV-2
    forbids, reachable through a completeness-named public method. ``blocked`` maps
    each affected PartDef QN to the diagnostic message that fired while enumerating
    it, so a bulk caller can never mistake a partial dump for a complete one.
    """

    occurrences: list[InstanceOccurrence]
    blocked: dict[str, str]


@dataclass(frozen=True)
class SourceOwnersResult:
    """Result of a bulk source-owner dump: owners plus every blocked definition.

    Same cure as :class:`AllOccurrencesResult` — ``all_source_owners()`` is a thin
    wrapper over :meth:`PartInstanceIndex.all_occurrences` and inherited the same
    silent omission, so it carries the same ``blocked`` mapping forward.
    """

    owners: list[str]
    blocked: dict[str, str]


class PartInstanceIndex:
    """Query object over the live model's concrete part occurrences.

    Constructed once per model via :func:`build_part_instance_index`; closes over
    the part-usage index and user-PartDef lookup so ``occurrences_of`` never
    rescans the model.
    """

    def __init__(self, part_usage_index: dict[str, list[Any]], qn_to_partdef: dict[str, Any]):
        self._part_usage_index = part_usage_index
        self._qn_to_partdef = qn_to_partdef
        self._user_qn_set = set(qn_to_partdef)

    def _leaf_part_def_qn(self, usage: Any) -> str:
        """The usage's own most-specific user type, entry-independent (D5/C3)."""
        key_qns = set(user_partdef_types(usage, self._user_qn_set))
        for target in owned_feature_typing_targets(usage):
            target_qn = build_element_qualified_name(target)
            if target_qn in self._user_qn_set:
                key_qns.add(target_qn)
        winner, _incomparable = most_specific(sorted(key_qns), self._qn_to_partdef)
        if winner is None:  # the usage was found keyed under a user PartDef QN
            raise RuntimeError(
                f"no most-specific user PartDef for usage typed by {sorted(key_qns)!r}"
            )
        return winner

    def occurrences_of(self, part_def_qn: str) -> list[InstanceOccurrence]:
        """All concrete occurrences of ``part_def_qn``, over its subtype closure.

        Multiplicity-expanded, deduped, and deterministically ordered (D6/D7).
        Raises :class:`NonFiniteCardinalityError` if a non-finite multiplicity lies
        on the path to any occurrence (INV-2: no silent drop).
        """
        applicable = sorted(
            {part_def_qn}
            | {
                candidate_qn
                for candidate_qn in self._qn_to_partdef
                if part_def_qn in _supertype_closure(candidate_qn, self._qn_to_partdef)
            }
        )
        occurrences: set[InstanceOccurrence] = set()
        for applicable_type in applicable:
            for path, usage in _structured_paths(applicable_type, self._part_usage_index):
                occurrences.add(InstanceOccurrence(self._leaf_part_def_qn(usage), path))
        return sorted(occurrences, key=_occurrence_sort_key)

    def all_occurrences(self) -> AllOccurrencesResult:
        """Every concrete occurrence in the model, plus every blocked definition.

        A thin union of :meth:`occurrences_of` over every user PartDef — for
        full-dump diagnostics and the determinism test, not a distinct algorithm.
        This is a bulk best-effort dump, not a per-owner query, but it is not
        silent about it either (cured post-audit): a PartDef whose own occurrences
        hit a non-finite multiplicity is omitted from ``occurrences`` and instead
        recorded in ``blocked`` (QN -> the diagnostic message), so a caller can
        never mistake a partial dump for a complete one. :meth:`occurrences_of`
        itself is unaffected — a direct call on the affected owner still raises
        loud (INV-2).
        """
        combined: set[InstanceOccurrence] = set()
        blocked: dict[str, str] = {}
        for part_def_qn in sorted(self._qn_to_partdef):
            try:
                combined.update(self.occurrences_of(part_def_qn))
            except NonFiniteCardinalityError as error:
                blocked[part_def_qn] = str(error)
        return AllOccurrencesResult(
            occurrences=sorted(combined, key=_occurrence_sort_key),
            blocked=blocked,
        )

    def all_source_owners(self) -> SourceOwnersResult:
        """Every owning part-definition QN appearing in any enumerable occurrence's
        path, plus every blocked definition (cured post-audit; see
        :meth:`all_occurrences`, whose ``blocked`` mapping this carries forward)."""
        result = self.all_occurrences()
        owners = sorted(
            {step.owning_def_qn for occurrence in result.occurrences for step in occurrence.steps}
        )
        return SourceOwnersResult(owners=owners, blocked=result.blocked)


def build_part_instance_index(model: Any) -> PartInstanceIndex:
    """Build a :class:`PartInstanceIndex` over a live SysIDE model.

    Builds the part-usage index and user-PartDef lookup once; the returned query
    object closes over them. Read-only over ``usage_extractor``'s helpers — does
    not import ``MultiplicityData``, ``pipeline_builder``, or any generation code
    (design.md Boundaries), and nothing existing imports this module in this item
    (INV-1).
    """
    return PartInstanceIndex(
        part_usage_index=_build_part_usage_index(model),
        qn_to_partdef=user_partdef_lookup(model),
    )


class OccurrenceIndex(Protocol):
    """Structural surface :func:`~sysml_codegen.analysis.constraint_lowering.lower_constraints`
    needs from an occurrence source — the only method it calls (design.md#key-bets B1).
    :class:`PartInstanceIndex`, :class:`RecordingOccurrenceIndex`, and
    :class:`FrozenOccurrenceIndex` all satisfy this by duck typing; the Protocol exists
    for mypy clarity, not runtime dispatch."""

    def occurrences_of(self, part_def_qn: str) -> list[InstanceOccurrence]: ...


@dataclass
class RecordingOccurrenceIndex:
    """Capture-time wrapper: delegates ``occurrences_of`` to a live index and
    records every ``(owner_eqn -> result)`` it answered.

    Snapshot v3 (Item 8) serializes ``.recorded`` as the ``part_occurrences``
    section — the exact transcript of the queries the real ``lower_constraints``
    call made (MF3), so the offline replay never needs a second owner-selection
    path.
    """

    _inner: PartInstanceIndex
    recorded: dict[str, list[InstanceOccurrence]] = field(default_factory=dict)

    def occurrences_of(self, part_def_qn: str) -> list[InstanceOccurrence]:
        result = self._inner.occurrences_of(part_def_qn)
        self.recorded[part_def_qn] = result
        return result


class FrozenOccurrenceIndexCorruptionError(Exception):
    """Raised when offline lowering queries an owner absent from the frozen
    occurrence table — the table is the recorded transcript of every query the
    real capture-time lowering made (D2), so a missing key means the snapshot is
    corrupt or was captured against a different model, never that the owner has
    zero occurrences."""


class FrozenOccurrenceIndex:
    """Offline replay dual of :class:`RecordingOccurrenceIndex`: answers
    ``occurrences_of`` by dict lookup into a table deserialized from a v3
    snapshot. A missing key raises (D2) — never ``[]`` — because the table is a
    closed transcript, not a live query surface."""

    def __init__(self, table: dict[str, list[InstanceOccurrence]]):
        self._table = table

    def occurrences_of(self, part_def_qn: str) -> list[InstanceOccurrence]:
        if part_def_qn not in self._table:
            raise FrozenOccurrenceIndexCorruptionError(
                f"owner {part_def_qn!r} was queried but is absent from the frozen "
                "occurrence table — the table must contain every owner the real "
                "capture-time lowering queried. Recapture the snapshot."
            )
        return self._table[part_def_qn]


def deserialize_part_occurrences(
    data: dict[str, list[dict[str, Any]]],
) -> dict[str, list[InstanceOccurrence]]:
    """Rebuild the ``part_occurrences`` snapshot section into
    ``InstanceOccurrence`` objects, the inverse of ``_serialize_value`` over a
    ``RecordingOccurrenceIndex.recorded`` table."""
    return {
        owner_eqn: [
            InstanceOccurrence(
                part_def_qn=occ["part_def_qn"],
                steps=tuple(
                    PathStep(
                        owning_def_qn=step["owning_def_qn"],
                        feature_name=step["feature_name"],
                        occurrence_index=step["occurrence_index"],
                    )
                    for step in occ["steps"]
                ),
            )
            for occ in occurrences
        ]
        for owner_eqn, occurrences in data.items()
    }
