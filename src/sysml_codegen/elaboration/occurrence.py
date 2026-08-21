"""Exact containment-slot expansion for the elaborate-first front end."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Literal

from agentic_mbse.sysml.expression import evaluate_true_static_expression
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration.diagnostics import (
    ElaborationCode,
    ElaborationInvariantError,
)
from sysml_codegen.elaboration.display import display_name, display_qualified_name
from sysml_codegen.elaboration.identity import (
    DeclarationId,
    FeatureSlotId,
    IdentityBoundaryError,
    OccurrenceId,
    OccurrenceStep,
    PackageScopeId,
    ScopeId,
    declaration_id_for,
)
from sysml_codegen.extraction.binding_evidence import (
    WRITTEN_UNKNOWN,
    written_reference_text,
)

__all__ = [
    "ExactOccurrence",
    "FeatureSlotIndex",
    "MultiplicityExpansionError",
    "OccurrenceIndex",
    "RecursiveContainmentError",
    "build_feature_slot_index",
    "build_occurrence_index",
    "semantic_owner",
]


class InvalidRedefinitionFamilyError(ElaborationInvariantError):
    """Redefinition endpoints do not form one acyclic rooted slot family."""

    def __init__(
        self,
        detail: str,
        *,
        reference: str | None = None,
        location: tuple[str, int] | None = None,
    ) -> None:
        super().__init__(
            ElaborationCode.SI_REDEFINITION_INVALID,
            detail,
            reference=reference,
            location=location,
        )


class MultiplicityExpansionError(ElaborationInvariantError):
    """A containment declaration cannot expand into supported occurrences."""

    def __init__(
        self,
        code: ElaborationCode,
        detail: str,
        *,
        reference: str | None = None,
        location: tuple[str, int] | None = None,
    ) -> None:
        super().__init__(code, detail, reference=reference, location=location)


class RecursiveContainmentError(ElaborationInvariantError):
    """Containment re-enters an active effective definition."""

    def __init__(
        self,
        detail: str,
        *,
        reference: str | None = None,
        location: tuple[str, int] | None = None,
    ) -> None:
        super().__init__(
            ElaborationCode.SI_CONTAINMENT_RECURSIVE,
            detail,
            reference=reference,
            location=location,
        )


class OccurrenceResolutionError(ElaborationInvariantError):
    """A modeled containment address has no one permitted concrete answer."""


def authored_site(element: Any) -> tuple[str | None, tuple[str, int] | None]:
    """The authored name and exact source site of one parser element.

    Both halves are measured off the element or omitted. An element the parser
    gave no qualified name or no location contributes nothing rather than a
    stand-in, so a refusal never cites a place nobody read.
    """
    if element is None:
        return None, None
    qualified = getattr(element, "qualified_name", None)
    # The authored spelling, as the rest of the boundary reports references —
    # ``str`` and not ``repr``, which is what leaked a parser object into a
    # user-facing message.
    reference = str(qualified) if qualified is not None else None
    return reference, SysideAdapter.get_source_location(element)


def semantic_owner(element: Any) -> Any:
    """Return SysIDE's semantic owner without imposing a containment policy."""
    owning_type = getattr(element, "owning_type", None)
    return owning_type if owning_type is not None else getattr(element, "owner", None)


@dataclass(frozen=True)
class ContainmentAddress:
    """A declaration-only path from one closed modeled containment anchor."""

    anchor_kind: Literal["package", "part_definition"]
    anchor_id: DeclarationId
    steps: tuple[FeatureSlotId, ...]


@dataclass(frozen=True)
class ConsumerDomain:
    """The exact scopes that realize anchors on one consumer's lineage."""

    scope: ScopeId
    anchor_scopes: tuple[
        tuple[
            tuple[Literal["package", "part_definition"], DeclarationId],
            tuple[ScopeId, ...],
        ],
        ...,
    ]

    def scopes_for(
        self, kind: Literal["package", "part_definition"], anchor: DeclarationId
    ) -> tuple[ScopeId, ...]:
        key = (kind, anchor)
        matches = [scopes for item, scopes in self.anchor_scopes if item == key]
        if len(matches) > 1:
            raise RuntimeError("consumer domain repeats one anchor key")
        return matches[0] if matches else ()

    def with_explicit_package(self, package: DeclarationId) -> ConsumerDomain:
        """Add the exact package named by an explicit resolved prefix."""
        if self.scopes_for("package", package):
            return self
        entries = (*self.anchor_scopes, (("package", package), (PackageScopeId(package),)))
        return ConsumerDomain(
            self.scope,
            tuple(sorted(entries, key=lambda item: (item[0][0], item[0][1].to_wire()))),
        )


def build_containment_address(
    element: Any, slots: FeatureSlotIndex
) -> ContainmentAddress:
    """Build the sole supported declaration path from live semantic ownership."""
    current = (
        element
        if SysideAdapter.is_instance(element, "PartUsage")
        else semantic_owner(element)
    )
    steps: list[FeatureSlotId] = []
    visited: set[DeclarationId] = set()
    while current is not None:
        if not any(
            SysideAdapter.is_instance(current, kind)
            for kind in ("PartUsage", "PartDefinition", "Package")
        ):
            raise OccurrenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_MISSING,
                f"semantic owner kind {type(current).__name__!r} cannot anchor containment",
            )
        try:
            current_id = declaration_id_for(current)
        except IdentityBoundaryError as error:
            raise OccurrenceResolutionError(
                error.code,
                error.detail,
            ) from error
        if current_id in visited:
            reference, location = authored_site(current)
            raise OccurrenceResolutionError(
                ElaborationCode.SI_CONTAINMENT_RECURSIVE,
                f"containment ownership repeats {reference or current_id.to_wire()}",
                reference=reference,
                location=location,
            )
        visited.add(current_id)
        if SysideAdapter.is_instance(current, "PartUsage"):
            try:
                steps.insert(0, slots.slot_of(current_id))
            except KeyError as error:
                raise OccurrenceResolutionError(
                    ElaborationCode.SI_OCCURRENCE_MISSING,
                    f"part usage {current_id.to_wire()} has no canonical containment slot",
                ) from error
            current = semantic_owner(current)
            continue
        anchor_kind: Literal["package", "part_definition"] = (
            "part_definition"
            if SysideAdapter.is_instance(current, "PartDefinition")
            else "package"
        )
        return ContainmentAddress(anchor_kind, current_id, tuple(steps))
    raise OccurrenceResolutionError(
        ElaborationCode.SI_OCCURRENCE_MISSING,
        "modeled containment path reaches no package or part-definition anchor",
    )


class FeatureSlotIndex:
    """Maps exact feature declarations to roots of parser redefinition edges."""

    def __init__(
        self,
        declarations: set[DeclarationId],
        parents: dict[DeclarationId, frozenset[DeclarationId]],
        sites: dict[DeclarationId, tuple[str | None, tuple[str, int] | None]] | None = None,
    ) -> None:
        self._declarations = declarations
        self._parents = parents
        self._roots: dict[DeclarationId, DeclarationId] = {}
        #: Read from the parser once at build time, so a family failure names the
        #: declaration the modeller wrote rather than an internal identifier.
        self._sites = dict(sites or {})

    def site_of(
        self, declaration: DeclarationId
    ) -> tuple[str | None, tuple[str, int] | None]:
        """The authored name and location recorded for one declaration, if any."""
        return self._sites.get(declaration, (None, None))

    def slot_of(self, declaration: DeclarationId) -> FeatureSlotId:
        if declaration not in self._declarations:
            raise KeyError(f"unknown feature declaration {declaration.to_wire()}")
        return FeatureSlotId(self._root_of(declaration, ()))

    def effective_declaration(
        self, candidates: set[DeclarationId]
    ) -> DeclarationId:
        """Return the sole declaration that redefines every other candidate."""
        if not candidates:
            # Nothing was passed in, so there is no declaration to name: the two
            # provenance fields stay absent rather than being filled with a guess.
            raise InvalidRedefinitionFamilyError(
                "effective declaration selection has no candidates",
                reference=None,
                location=None,
            )
        anchor_reference, anchor_location = self.site_of(min(candidates))
        if len({self.slot_of(candidate) for candidate in candidates}) != 1:
            raise InvalidRedefinitionFamilyError(
                "effective declaration candidates belong to different slots: "
                + self._named(candidates),
                reference=anchor_reference,
                location=anchor_location,
            )
        winners = {
            candidate
            for candidate in candidates
            if all(
                other == candidate or self._redefines(candidate, other, ())
                for other in candidates
            )
        }
        if len(winners) != 1:
            raise InvalidRedefinitionFamilyError(
                "native usage view has no unique effective declaration for one slot: "
                + self._named(candidates),
                reference=anchor_reference,
                location=anchor_location,
            )
        (winner,) = winners
        return winner

    def _named(self, declarations: set[DeclarationId]) -> str:
        """Name a set of declarations the way the modeller wrote them."""
        return ", ".join(
            sorted(
                self.site_of(declaration)[0] or declaration.to_wire()
                for declaration in declarations
            )
        )

    def _redefines(
        self,
        declaration: DeclarationId,
        ancestor: DeclarationId,
        active: tuple[DeclarationId, ...],
    ) -> bool:
        if declaration in active:
            reference, location = self.site_of(declaration)
            raise InvalidRedefinitionFamilyError(
                f"redefinition family contains a cycle at {reference or declaration.to_wire()}",
                reference=reference,
                location=location,
            )
        parents = self._parents.get(declaration, frozenset())
        return ancestor in parents or any(
            self._redefines(parent, ancestor, active + (declaration,))
            for parent in parents
        )

    def _root_of(
        self, declaration: DeclarationId, active: tuple[DeclarationId, ...]
    ) -> DeclarationId:
        cached = self._roots.get(declaration)
        if cached is not None:
            return cached
        if declaration in active:
            reference, location = self.site_of(declaration)
            raise InvalidRedefinitionFamilyError(
                f"redefinition family contains a cycle at {reference or declaration.to_wire()}",
                reference=reference,
                location=location,
            )
        parents = self._parents.get(declaration, frozenset())
        if not parents:
            root = declaration
        else:
            roots = {self._root_of(parent, active + (declaration,)) for parent in parents}
            if len(roots) != 1:
                reference, location = self.site_of(declaration)
                raise InvalidRedefinitionFamilyError(
                    "redefinition declaration "
                    f"{reference or declaration.to_wire()} has unrelated roots: "
                    + self._named(roots),
                    reference=reference,
                    location=location,
                )
            root = min(roots)
        self._roots[declaration] = root
        return root


def _most_specific_definition(
    candidates: set[DeclarationId],
    closures: dict[DeclarationId, frozenset[DeclarationId]],
    sites: dict[DeclarationId, tuple[str | None, tuple[str, int] | None]] | None = None,
) -> DeclarationId:
    winners = {
        candidate
        for candidate in candidates
        if all(other == candidate or other in closures[candidate] for other in candidates)
    }
    if len(winners) != 1:
        recorded = sites or {}
        named = ", ".join(
            sorted(
                recorded.get(candidate, (None, None))[0] or candidate.to_wire()
                for candidate in candidates
            )
        )
        reference, location = recorded.get(min(candidates), (None, None))
        raise InvalidRedefinitionFamilyError(
            f"applicable definition writers have no unique most-specific owner: {named}",
            reference=reference,
            location=location,
        )
    return min(winners)


def build_feature_slot_index(model: Any) -> FeatureSlotIndex:
    declarations: set[DeclarationId] = set()
    parent_sets: dict[DeclarationId, set[DeclarationId]] = defaultdict(set)
    sites: dict[DeclarationId, tuple[str | None, tuple[str, int] | None]] = {}
    features = list(SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True))
    for feature in features:
        if getattr(feature, "qualified_name", None) is not None:
            declarations.add(declaration_id_for(feature))
            sites[declaration_id_for(feature)] = authored_site(feature)
    for feature in features:
        # Operator-expression formals are parser-local UUIDv4 objects, not authored
        # or implied model declarations. They never enter the stable slot domain.
        if getattr(feature, "qualified_name", None) is None:
            continue
        for relationship in getattr(feature, "owned_redefinitions", ()) or ():
            redefined = getattr(relationship, "redefined_feature", None)
            redefining = getattr(relationship, "redefining_feature", None)
            if redefined is None or redefining is None:
                reference, location = authored_site(feature)
                raise InvalidRedefinitionFamilyError(
                    "redefinition relationship on "
                    f"{reference or "<anonymous feature>"} has a missing semantic endpoint",
                    reference=reference,
                    location=location,
                )
            redefined_chain = list(getattr(redefined, "chaining_features", ()) or ())
            redefined_endpoint = redefined_chain[-1] if redefined_chain else redefined
            if getattr(redefined_endpoint, "qualified_name", None) is None:
                reference, location = authored_site(feature)
                raise InvalidRedefinitionFamilyError(
                    f"redefined endpoint of {reference or "<anonymous feature>"} has no "
                    "stable declaration identity",
                    reference=reference,
                    location=location,
                )
            redefined_id = declaration_id_for(redefined_endpoint)
            declarations.add(redefined_id)
            sites.setdefault(redefined_id, authored_site(redefined_endpoint))
            if getattr(redefining, "qualified_name", None) is None:
                reference, location = authored_site(feature)
                raise InvalidRedefinitionFamilyError(
                    f"redefining endpoint of {reference or "<anonymous feature>"} has no "
                    "stable declaration identity",
                    reference=reference,
                    location=location,
                )
            redefining_id = declaration_id_for(redefining)
            declarations.add(redefining_id)
            sites.setdefault(redefining_id, authored_site(redefining))
            parent_sets[redefining_id].add(redefined_id)
    index = FeatureSlotIndex(
        declarations,
        {key: frozenset(value) for key, value in parent_sets.items()},
        sites,
    )
    for declaration in declarations:
        index.slot_of(declaration)
    return index


@dataclass(frozen=True)
class ExactOccurrence:
    occurrence_id: OccurrenceId
    effective_usage_id: DeclarationId
    effective_type_id: DeclarationId | None
    type_closure: frozenset[DeclarationId]
    parent_id: OccurrenceId | None
    child_declaration_ids: tuple[DeclarationId, ...]
    display_segment: str
    package_display: str | None
    root_package_id: DeclarationId | None
    display_path: str


class OccurrenceIndex:
    def __init__(
        self,
        occurrences: dict[OccurrenceId, ExactOccurrence],
        slots: FeatureSlotIndex,
        definition_closures: dict[DeclarationId, frozenset[DeclarationId]],
        definition_sites: dict[
            DeclarationId, tuple[str | None, tuple[str, int] | None]
        ] | None = None,
    ) -> None:
        self._occurrences = occurrences
        self._slots = slots
        self._definition_closures = definition_closures
        self._definition_sites = dict(definition_sites or {})
        self._children_by_parent_and_slot: dict[
            tuple[OccurrenceId, FeatureSlotId], tuple[ExactOccurrence, ...]
        ] = {}
        child_buckets: dict[
            tuple[OccurrenceId, FeatureSlotId], list[ExactOccurrence]
        ] = defaultdict(list)
        root_buckets: dict[
            tuple[DeclarationId, FeatureSlotId], list[ExactOccurrence]
        ] = defaultdict(list)
        for occurrence in occurrences.values():
            slot = occurrence.occurrence_id.steps[-1].containment_slot
            if occurrence.parent_id is not None:
                child_buckets[(occurrence.parent_id, slot)].append(occurrence)
            elif occurrence.root_package_id is not None:
                root_buckets[(occurrence.root_package_id, slot)].append(occurrence)
        self._children_by_parent_and_slot = {
            key: tuple(sorted(value, key=lambda item: item.occurrence_id.to_wire()))
            for key, value in child_buckets.items()
        }
        self._roots_by_package_and_slot = {
            key: tuple(sorted(value, key=lambda item: item.occurrence_id.to_wire()))
            for key, value in root_buckets.items()
        }

    def occurrence_ids(self) -> tuple[OccurrenceId, ...]:
        return tuple(sorted(self._occurrences, key=lambda item: item.to_wire()))

    def occurrences(self) -> tuple[ExactOccurrence, ...]:
        return tuple(self._occurrences[item] for item in self.occurrence_ids())

    def occurrence(self, occurrence_id: OccurrenceId) -> ExactOccurrence:
        return self._occurrences[occurrence_id]

    def occurrences_for_declaration(
        self, declaration: DeclarationId
    ) -> tuple[ExactOccurrence, ...]:
        slot = self._slots.slot_of(declaration)
        return tuple(
            occurrence
            for occurrence in self.occurrences()
            if occurrence.occurrence_id.steps[-1].containment_slot == slot
        )

    def occurrences_for_type(self, definition: DeclarationId) -> tuple[ExactOccurrence, ...]:
        return tuple(
            occurrence for occurrence in self.occurrences() if definition in occurrence.type_closure
        )

    def ancestors(self, occurrence_id: OccurrenceId) -> tuple[ExactOccurrence, ...]:
        result: list[ExactOccurrence] = []
        current = self._occurrences[occurrence_id]
        while current.parent_id is not None:
            current = self._occurrences[current.parent_id]
            result.append(current)
        return tuple(result)

    def children(self, occurrence_id: OccurrenceId) -> tuple[ExactOccurrence, ...]:
        return tuple(
            occurrence
            for (parent, _slot), children in self._children_by_parent_and_slot.items()
            if parent == occurrence_id
            for occurrence in children
        )

    def children_for_slot(
        self, occurrence_id: OccurrenceId, slot: FeatureSlotId
    ) -> tuple[ExactOccurrence, ...]:
        return self._children_by_parent_and_slot.get((occurrence_id, slot), ())

    def consumer_domain(self, scope: ScopeId) -> ConsumerDomain:
        anchors: dict[
            tuple[Literal["package", "part_definition"], DeclarationId], set[ScopeId]
        ] = defaultdict(set)
        if isinstance(scope, PackageScopeId):
            anchors[("package", scope.package_declaration)].add(scope)
        else:
            lineage = (self.occurrence(scope),) + self.ancestors(scope)
            root = lineage[-1]
            if root.root_package_id is not None:
                package_scope = PackageScopeId(root.root_package_id)
                anchors[("package", root.root_package_id)].add(package_scope)
            for occurrence in lineage:
                for definition in occurrence.type_closure:
                    anchors[("part_definition", definition)].add(
                        occurrence.occurrence_id
                    )
        frozen = tuple(
            (
                key,
                tuple(sorted(scopes, key=repr)),
            )
            for key, scopes in sorted(
                anchors.items(), key=lambda item: (item[0][0], item[0][1].to_wire())
            )
        )
        return ConsumerDomain(scope, frozen)

    def resolve_address(
        self,
        address: ContainmentAddress,
        consumer_domain: ConsumerDomain,
        *,
        plural: bool,
    ) -> tuple[ScopeId, ...]:
        """Instantiate one address without a positional or population fallback."""
        anchor_scopes = consumer_domain.scopes_for(address.anchor_kind, address.anchor_id)
        if not anchor_scopes:
            raise OccurrenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_MISSING,
                f"consumer domain has no {address.anchor_kind} anchor "
                f"{address.anchor_id.to_wire()}",
            )
        if address.anchor_kind == "part_definition" and len(anchor_scopes) != 1:
            raise OccurrenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                f"consumer domain has {len(anchor_scopes)} concrete scopes for definition "
                f"{address.anchor_id.to_wire()}",
            )
        states = anchor_scopes
        shared_prefix = True
        for slot in address.steps:
            candidates: list[ExactOccurrence] = []
            for state in states:
                if isinstance(state, PackageScopeId):
                    candidates.extend(
                        self._roots_by_package_and_slot.get(
                            (state.package_declaration, slot), ()
                        )
                    )
                else:
                    candidates.extend(self.children_for_slot(state, slot))
            if not candidates:
                raise OccurrenceResolutionError(
                    ElaborationCode.SI_OCCURRENCE_MISSING,
                    f"exact containment step {slot!r} has no concrete occurrence",
                )
            selected = candidates
            consumer_scope = consumer_domain.scope
            if shared_prefix and isinstance(consumer_scope, OccurrenceId):
                matching = [
                    candidate
                    for candidate in candidates
                    if len(candidate.occurrence_id.steps) <= len(consumer_scope.steps)
                    and candidate.occurrence_id.steps
                    == consumer_scope.steps[: len(candidate.occurrence_id.steps)]
                ]
                if matching:
                    selected = matching
                else:
                    shared_prefix = False
            if not plural and len(selected) != 1:
                raise OccurrenceResolutionError(
                    ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                    f"exact containment step {slot!r} has {len(selected)} concrete occurrences",
                )
            states = tuple(item.occurrence_id for item in selected)
        if not plural and len(states) != 1:
            raise OccurrenceResolutionError(
                ElaborationCode.SI_OCCURRENCE_AMBIGUOUS,
                f"containment address has {len(states)} concrete scopes",
            )
        return tuple(sorted(states, key=repr))

    def definition_depth(self, definition: DeclarationId) -> int:
        return len(self._definition_closures[definition])

    def most_specific_definition(self, candidates: set[DeclarationId]) -> DeclarationId:
        """Return the sole candidate that specializes every other candidate."""
        return _most_specific_definition(
            candidates, self._definition_closures, self._definition_sites
        )


def _definition_supertypes(
    definitions: dict[DeclarationId, Any],
) -> dict[DeclarationId, frozenset[DeclarationId]]:
    direct: dict[DeclarationId, set[DeclarationId]] = defaultdict(set)
    for definition_id, definition in definitions.items():
        for specialization in getattr(definition, "owned_specializations", ()) or ():
            supertype = getattr(specialization, "superclassifier", None)
            if supertype is None or getattr(supertype, "qualified_name", None) is None:
                continue
            supertype_id = declaration_id_for(supertype)
            if supertype_id in definitions:
                direct[definition_id].add(supertype_id)

    def closure(
        definition_id: DeclarationId, active: tuple[DeclarationId, ...]
    ) -> frozenset[DeclarationId]:
        if definition_id in active:
            reference, location = authored_site(definitions.get(definition_id))
            raise RecursiveContainmentError(
                "part-definition specialization cycle at "
                f"{reference or definition_id.to_wire()}",
                reference=reference,
                location=location,
            )
        result = {definition_id}
        for parent in direct.get(definition_id, set()):
            result.update(closure(parent, active + (definition_id,)))
        return frozenset(result)

    return {definition_id: closure(definition_id, ()) for definition_id in definitions}


def _effective_type(
    usage: Any,
    definitions: dict[DeclarationId, Any],
    closures: dict[DeclarationId, frozenset[DeclarationId]],
) -> DeclarationId | None:
    candidates = {
        declaration_id_for(type_element)
        for type_element in (getattr(usage, "types", None) or ())
        if getattr(type_element, "qualified_name", None) is not None
        and declaration_id_for(type_element) in definitions
    }
    most_specific = {
        candidate
        for candidate in candidates
        if not any(candidate != other and candidate in closures[other] for other in candidates)
    }
    if len(most_specific) > 1:
        reference, location = authored_site(usage)
        raise InvalidRedefinitionFamilyError(
            f"part usage {reference or "<anonymous>"} has incomparable exact "
            "user-definition typings",
            reference=reference,
            location=location,
        )
    return min(most_specific, default=None)


def _modeled_integer_bound(
    bound: Any,
    *,
    multiplicity_owner: Any,
    parent: ExactOccurrence | None,
    slots: FeatureSlotIndex,
    attributes_by_slot: dict[FeatureSlotId, list[Any]],
    closures: dict[DeclarationId, frozenset[DeclarationId]],
) -> int | None:
    direct = _constant_integer_value(bound)
    if direct is not None:
        return direct
    if not SysideAdapter.is_instance(bound, "FeatureReferenceExpression"):
        return None
    referent = getattr(bound, "referent", None)
    if referent is None or getattr(referent, "qualified_name", None) is None:
        return None
    try:
        slot = slots.slot_of(declaration_id_for(referent))
    except KeyError:
        return None

    candidates = attributes_by_slot.get(slot, [])
    owner = semantic_owner(multiplicity_owner)
    if SysideAdapter.is_instance(owner, "PartUsage"):
        usage_writers = [
            candidate
            for candidate in candidates
            if SysideAdapter.is_instance(semantic_owner(candidate), "PartUsage")
            and declaration_id_for(semantic_owner(candidate)) == declaration_id_for(owner)
        ]
        candidates = usage_writers
    elif SysideAdapter.is_instance(owner, "PartDefinition") and parent is not None:
        definition_writers = [
            candidate
            for candidate in candidates
            if SysideAdapter.is_instance(semantic_owner(candidate), "PartDefinition")
            and declaration_id_for(semantic_owner(candidate)) in parent.type_closure
        ]
        if definition_writers:
            try:
                selected_owner = _most_specific_definition(
                    {
                        declaration_id_for(semantic_owner(candidate))
                        for candidate in definition_writers
                    },
                    closures,
                    {
                        declaration_id_for(semantic_owner(candidate)): authored_site(
                            semantic_owner(candidate)
                        )
                        for candidate in definition_writers
                    },
                )
            except InvalidRedefinitionFamilyError as error:
                reference, location = _multiplicity_diagnostic_context(
                    multiplicity_owner, bound
                )
                raise InvalidRedefinitionFamilyError(
                    error.detail,
                    reference=reference,
                    location=location,
                ) from error
            candidates = [
                candidate
                for candidate in definition_writers
                if declaration_id_for(semantic_owner(candidate)) == selected_owner
            ]
        else:
            candidates = []
    elif SysideAdapter.is_instance(owner, "Package"):
        owner_id = declaration_id_for(owner)
        candidates = [
            candidate
            for candidate in candidates
            if SysideAdapter.is_instance(semantic_owner(candidate), "Package")
            and declaration_id_for(semantic_owner(candidate)) == owner_id
        ]
    else:
        candidates = []
    if len(candidates) != 1:
        return None
    return _constant_integer_value(getattr(candidates[0], "feature_value_expression", None))


def _constant_integer_value(expression: Any) -> int | None:
    if expression is None:
        return None
    try:
        value = evaluate_true_static_expression(expression)
    except (ArithmeticError, TypeError, ValueError):
        return None
    if not math.isfinite(value) or not value.is_integer():
        return None
    return int(value)


def _multiplicity_diagnostic_context(
    usage: Any, bound: Any
) -> tuple[str, tuple[str, int] | None]:
    """Return the authored bound reference and its exact source location."""
    reference: str | None = None
    if SysideAdapter.is_instance(bound, "FeatureReferenceExpression"):
        written = written_reference_text(bound)
        if written != WRITTEN_UNKNOWN:
            reference = written
    if reference is None:
        reference = str(
            getattr(usage, "qualified_name", None)
            or getattr(usage, "name", None)
            or "<anonymous-part-usage>"
        )
    location = SysideAdapter.get_source_location(bound)
    if location is None:
        location = SysideAdapter.get_source_location(usage)
    return reference, location


def _multiplicity_indices(
    usage: Any,
    *,
    parent: ExactOccurrence | None,
    slots: FeatureSlotIndex,
    attributes_by_slot: dict[FeatureSlotId, list[Any]],
    closures: dict[DeclarationId, frozenset[DeclarationId]],
) -> tuple[int | None, ...]:
    multiplicity = getattr(usage, "multiplicity", None)
    if multiplicity is None:
        return (None,)
    name = str(getattr(usage, "name", None) or "<anonymous>")
    if getattr(usage, "is_ordered", False):
        reference, location = _multiplicity_diagnostic_context(usage, multiplicity)
        raise MultiplicityExpansionError(
            ElaborationCode.SI_MULTIPLICITY_UNSUPPORTED,
            f"ordered multiplicity on {name!r} is outside the supported occurrence model",
            reference=reference,
            location=location,
        )
    if getattr(usage, "is_nonunique", False):
        reference, location = _multiplicity_diagnostic_context(usage, multiplicity)
        raise MultiplicityExpansionError(
            ElaborationCode.SI_MULTIPLICITY_UNSUPPORTED,
            f"nonunique multiplicity on {name!r} is outside the supported occurrence model",
            reference=reference,
            location=location,
        )
    upper = getattr(multiplicity, "upper_bound", None)
    lower = getattr(multiplicity, "lower_bound", None)
    count = (
        _modeled_integer_bound(
            upper,
            multiplicity_owner=usage,
            parent=parent,
            slots=slots,
            attributes_by_slot=attributes_by_slot,
            closures=closures,
        )
        if upper is not None
        else None
    )
    if count is None:
        reference, location = _multiplicity_diagnostic_context(
            usage, upper if upper is not None else usage
        )
        raise MultiplicityExpansionError(
            ElaborationCode.SI_MULTIPLICITY_UNRESOLVED,
            f"upper multiplicity on {name!r} is not a known finite integer",
            reference=reference,
            location=location,
        )
    if count < 0:
        reference, location = _multiplicity_diagnostic_context(
            usage, upper if upper is not None else usage
        )
        raise MultiplicityExpansionError(
            ElaborationCode.SI_MULTIPLICITY_INVALID,
            f"negative multiplicity on {name!r}",
            reference=reference,
            location=location,
        )
    if lower is not None:
        lower_count = _modeled_integer_bound(
            lower,
            multiplicity_owner=usage,
            parent=parent,
            slots=slots,
            attributes_by_slot=attributes_by_slot,
            closures=closures,
        )
        if lower_count is None:
            reference, location = _multiplicity_diagnostic_context(usage, lower)
            raise MultiplicityExpansionError(
                ElaborationCode.SI_MULTIPLICITY_UNRESOLVED,
                f"lower multiplicity on {name!r} is not a known finite integer",
                reference=reference,
                location=location,
            )
        if lower_count != count:
            reference, location = _multiplicity_diagnostic_context(usage, multiplicity)
            raise MultiplicityExpansionError(
                ElaborationCode.SI_MULTIPLICITY_UNSUPPORTED,
                f"range multiplicity on {name!r} is outside the supported occurrence model",
                reference=reference,
                location=location,
            )
    return tuple(range(count))


def build_occurrence_index(model: Any, slots: FeatureSlotIndex) -> OccurrenceIndex:
    definitions = {
        declaration_id_for(definition): definition
        for definition in SysideAdapter.elements_of_type(model, "PartDefinition")
    }
    closures = _definition_supertypes(definitions)
    usages = list(SysideAdapter.elements_of_type(model, "PartUsage"))
    usages_by_id = {declaration_id_for(usage): usage for usage in usages}
    attributes_by_slot: dict[FeatureSlotId, list[Any]] = defaultdict(list)
    for attribute in SysideAdapter.elements_of_type(model, "AttributeUsage"):
        if getattr(attribute, "qualified_name", None) is None:
            continue
        attributes_by_slot[slots.slot_of(declaration_id_for(attribute))].append(attribute)

    roots: list[Any] = []
    for usage in usages:
        owner = semantic_owner(usage)
        if owner is None or not (
            SysideAdapter.is_instance(owner, "PartDefinition")
            or SysideAdapter.is_instance(owner, "PartUsage")
        ):
            roots.append(usage)

    occurrences: dict[OccurrenceId, ExactOccurrence] = {}

    def native_child_declarations(usage: Any) -> tuple[Any, ...]:
        """Return SysIDE's effective local PartUsage declarations for ``usage``."""
        native_children: dict[DeclarationId, Any] = {}
        for candidate in getattr(usage, "usages", ()) or ():
            if not SysideAdapter.is_instance(candidate, "PartUsage"):
                continue
            if not bool(getattr(candidate, "is_composite", False)):
                continue
            if getattr(candidate, "qualified_name", None) is None:
                continue
            candidate_id = declaration_id_for(candidate)
            if candidate_id not in usages_by_id:
                # ``Usage.usages`` also exposes inherited standard-library
                # features. Only declarations in the loaded user model belong
                # to codegen's supported containment population.
                continue
            existing = native_children.get(candidate_id)
            if existing is not None and existing is not candidate:
                reference, location = authored_site(candidate)
                raise InvalidRedefinitionFamilyError(
                    "native usage view repeats declaration "
                    f"{reference or candidate_id.to_wire()}",
                    reference=reference,
                    location=location,
                )
            native_children[candidate_id] = candidate

        by_slot: dict[FeatureSlotId, set[DeclarationId]] = defaultdict(set)
        for candidate_id in native_children:
            by_slot[slots.slot_of(candidate_id)].add(candidate_id)
        selected_ids = {
            slots.effective_declaration(candidates) for candidates in by_slot.values()
        }
        return tuple(
            native_children[item]
            for item in sorted(selected_ids, key=lambda item: item.to_wire())
        )

    def add_usage(
        usage: Any,
        parent: ExactOccurrence | None,
        active_types: tuple[DeclarationId, ...],
    ) -> None:
        usage_id = declaration_id_for(usage)
        type_id = _effective_type(usage, definitions, closures)
        if type_id is not None and type_id in active_types:
            definition_reference, definition_location = authored_site(definitions.get(type_id))
            usage_reference, usage_location = authored_site(usage)
            raise RecursiveContainmentError(
                "containment re-enters definition "
                f"{definition_reference or type_id.to_wire()} at "
                f"{usage_reference or usage_id.to_wire()}",
                reference=usage_reference or definition_reference,
                location=usage_location or definition_location,
            )
        type_closure = closures[type_id] if type_id is not None else frozenset()
        child_declarations = native_child_declarations(usage)
        child_declaration_ids = tuple(
            declaration_id_for(child) for child in child_declarations
        )
        slot = slots.slot_of(usage_id)
        raw_name = str(getattr(usage, "name", None) or "anonymous")
        for index in _multiplicity_indices(
            usage,
            parent=parent,
            slots=slots,
            attributes_by_slot=attributes_by_slot,
            closures=closures,
        ):
            step = OccurrenceStep(slot, index)
            steps = (step,) if parent is None else parent.occurrence_id.steps + (step,)
            occurrence_id = OccurrenceId(steps)
            display_segment = display_name(raw_name)
            if index is not None:
                display_segment += f"[{index}]"
            package_display = None
            root_package_id = parent.root_package_id if parent is not None else None
            if parent is None:
                owner = semantic_owner(usage)
                if owner is not None and SysideAdapter.is_instance(owner, "Package"):
                    root_package_id = declaration_id_for(owner)
                    package_display = display_qualified_name(
                        str(getattr(owner, "qualified_name", None) or "")
                    )
                rendered = (
                    f"{package_display}__{display_segment}"
                    if package_display
                    else display_qualified_name(
                        str(getattr(usage, "qualified_name", None) or raw_name)
                    )
                )
            else:
                rendered = f"{parent.display_path}__{display_segment}"
            occurrence = ExactOccurrence(
                occurrence_id=occurrence_id,
                effective_usage_id=usage_id,
                effective_type_id=type_id,
                type_closure=type_closure,
                parent_id=parent.occurrence_id if parent is not None else None,
                child_declaration_ids=child_declaration_ids,
                display_segment=display_segment,
                package_display=package_display,
                root_package_id=root_package_id,
                display_path=rendered,
            )
            existing = occurrences.get(occurrence_id)
            if existing is not None and existing != occurrence:
                reference, location = authored_site(usage)
                raise InvalidRedefinitionFamilyError(
                    f"duplicate exact occurrence identity for {rendered}",
                    reference=reference,
                    location=location,
                )
            occurrences[occurrence_id] = occurrence
            next_active = active_types + ((type_id,) if type_id is not None else ())
            for child in child_declarations:
                add_usage(child, occurrence, next_active)

    for root in sorted(roots, key=lambda item: declaration_id_for(item).to_wire()):
        add_usage(root, None, ())

    return OccurrenceIndex(
        occurrences,
        slots,
        closures,
        {key: authored_site(value) for key, value in definitions.items()},
    )
