"""Exact containment-slot expansion for the elaborate-first front end."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

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
    OccurrenceId,
    OccurrenceStep,
    declaration_id_for,
)

__all__ = [
    "ExactOccurrence",
    "FeatureSlotIndex",
    "MultiplicityExpansionError",
    "OccurrenceIndex",
    "RecursiveContainmentError",
    "build_feature_slot_index",
    "build_occurrence_index",
]


class InvalidRedefinitionFamilyError(ElaborationInvariantError):
    """Redefinition endpoints do not form one acyclic rooted slot family."""

    def __init__(self, detail: str) -> None:
        super().__init__(ElaborationCode.SI_REDEFINITION_INVALID, detail)


class MultiplicityExpansionError(ElaborationInvariantError):
    """A containment declaration cannot expand into supported occurrences."""

    def __init__(self, code: ElaborationCode, detail: str) -> None:
        super().__init__(code, detail)


class RecursiveContainmentError(ElaborationInvariantError):
    """Containment re-enters an active effective definition."""

    def __init__(self, detail: str) -> None:
        super().__init__(ElaborationCode.SI_CONTAINMENT_RECURSIVE, detail)


class FeatureSlotIndex:
    """Maps exact feature declarations to roots of parser redefinition edges."""

    def __init__(
        self,
        declarations: set[DeclarationId],
        parents: dict[DeclarationId, frozenset[DeclarationId]],
    ) -> None:
        self._declarations = declarations
        self._parents = parents
        self._roots: dict[DeclarationId, DeclarationId] = {}

    def slot_of(self, declaration: DeclarationId) -> FeatureSlotId:
        if declaration not in self._declarations:
            raise KeyError(f"unknown feature declaration {declaration.to_wire()}")
        return FeatureSlotId(self._root_of(declaration, ()))

    def effective_declaration(
        self, candidates: set[DeclarationId]
    ) -> DeclarationId:
        """Return the sole declaration that redefines every other candidate."""
        if not candidates:
            raise InvalidRedefinitionFamilyError(
                "effective declaration selection has no candidates"
            )
        if len({self.slot_of(candidate) for candidate in candidates}) != 1:
            raise InvalidRedefinitionFamilyError(
                "effective declaration candidates belong to different slots"
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
                "native usage view has no unique effective declaration for one slot"
            )
        (winner,) = winners
        return winner

    def _redefines(
        self,
        declaration: DeclarationId,
        ancestor: DeclarationId,
        active: tuple[DeclarationId, ...],
    ) -> bool:
        if declaration in active:
            raise InvalidRedefinitionFamilyError("redefinition family contains a cycle")
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
            raise InvalidRedefinitionFamilyError("redefinition family contains a cycle")
        parents = self._parents.get(declaration, frozenset())
        if not parents:
            root = declaration
        else:
            roots = {self._root_of(parent, active + (declaration,)) for parent in parents}
            if len(roots) != 1:
                raise InvalidRedefinitionFamilyError("redefinition declaration has unrelated roots")
            root = min(roots)
        self._roots[declaration] = root
        return root


def _most_specific_definition(
    candidates: set[DeclarationId],
    closures: dict[DeclarationId, frozenset[DeclarationId]],
) -> DeclarationId:
    winners = {
        candidate
        for candidate in candidates
        if all(other == candidate or other in closures[candidate] for other in candidates)
    }
    if len(winners) != 1:
        raise InvalidRedefinitionFamilyError(
            "applicable definition writers have no unique most-specific owner"
        )
    return min(winners)


def build_feature_slot_index(model: Any) -> FeatureSlotIndex:
    declarations: set[DeclarationId] = set()
    parent_sets: dict[DeclarationId, set[DeclarationId]] = defaultdict(set)
    features = list(SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True))
    for feature in features:
        if getattr(feature, "qualified_name", None) is not None:
            declarations.add(declaration_id_for(feature))
    for feature in features:
        for relationship in getattr(feature, "owned_redefinitions", ()) or ():
            redefined = getattr(relationship, "redefined_feature", None)
            redefining = getattr(relationship, "redefining_feature", None)
            if redefined is None or redefining is None:
                raise InvalidRedefinitionFamilyError(
                    "redefinition relationship has a missing semantic endpoint"
                )
            redefined_chain = list(getattr(redefined, "chaining_features", ()) or ())
            redefined_endpoint = redefined_chain[-1] if redefined_chain else redefined
            if getattr(redefined_endpoint, "qualified_name", None) is None:
                continue
            redefined_id = declaration_id_for(redefined_endpoint)
            declarations.add(redefined_id)
            if getattr(redefining, "qualified_name", None) is None:
                # Expression/deep-path wrappers are relationship-local UUIDv4
                # objects. Their stable target endpoint owns the slot; the
                # wrapper itself never becomes declaration identity.
                continue
            redefining_id = declaration_id_for(redefining)
            declarations.add(redefining_id)
            parent_sets[redefining_id].add(redefined_id)
    index = FeatureSlotIndex(
        declarations,
        {key: frozenset(value) for key, value in parent_sets.items()},
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
    display_path: str


class OccurrenceIndex:
    def __init__(
        self,
        occurrences: dict[OccurrenceId, ExactOccurrence],
        slots: FeatureSlotIndex,
        definition_closures: dict[DeclarationId, frozenset[DeclarationId]],
    ) -> None:
        self._occurrences = occurrences
        self._slots = slots
        self._definition_closures = definition_closures

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
            occurrence for occurrence in self.occurrences() if occurrence.parent_id == occurrence_id
        )

    def is_descendant(self, candidate_id: OccurrenceId, ancestor_id: OccurrenceId) -> bool:
        return any(
            ancestor.occurrence_id == ancestor_id for ancestor in self.ancestors(candidate_id)
        )

    def definition_depth(self, definition: DeclarationId) -> int:
        return len(self._definition_closures[definition])

    def most_specific_definition(self, candidates: set[DeclarationId]) -> DeclarationId:
        """Return the sole candidate that specializes every other candidate."""
        return _most_specific_definition(candidates, self._definition_closures)


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
            raise RecursiveContainmentError("part-definition specialization cycle")
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
        raise InvalidRedefinitionFamilyError(
            "part usage has incomparable exact user-definition typings"
        )
    return min(most_specific, default=None)


def _modeled_integer_bound(
    bound: Any,
    *,
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
    if parent is not None:
        usage_writers = [
            candidate
            for candidate in candidates
            if SysideAdapter.is_instance(getattr(candidate, "owning_type", None), "PartUsage")
            and declaration_id_for(candidate.owning_type) == parent.effective_usage_id
        ]
        if usage_writers:
            candidates = usage_writers
        else:
            definition_writers = [
                candidate
                for candidate in candidates
                if SysideAdapter.is_instance(
                    getattr(candidate, "owning_type", None), "PartDefinition"
                )
                and declaration_id_for(candidate.owning_type) in parent.type_closure
            ]
            if definition_writers:
                owner = _most_specific_definition(
                    {declaration_id_for(candidate.owning_type) for candidate in definition_writers},
                    closures,
                )
                candidates = [
                    candidate
                    for candidate in definition_writers
                    if declaration_id_for(candidate.owning_type) == owner
                ]
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
        raise MultiplicityExpansionError(
            ElaborationCode.SI_MULTIPLICITY_UNSUPPORTED,
            f"ordered multiplicity on {name!r} is outside the supported occurrence model",
        )
    if getattr(usage, "is_nonunique", False):
        raise MultiplicityExpansionError(
            ElaborationCode.SI_MULTIPLICITY_UNSUPPORTED,
            f"nonunique multiplicity on {name!r} is outside the supported occurrence model",
        )
    upper = getattr(multiplicity, "upper_bound", None)
    lower = getattr(multiplicity, "lower_bound", None)
    count = (
        _modeled_integer_bound(
            upper,
            parent=parent,
            slots=slots,
            attributes_by_slot=attributes_by_slot,
            closures=closures,
        )
        if upper is not None
        else None
    )
    if count is None:
        raise MultiplicityExpansionError(
            ElaborationCode.SI_MULTIPLICITY_UNRESOLVED,
            f"upper multiplicity on {name!r} is not a known finite integer",
        )
    if count < 0:
        raise MultiplicityExpansionError(
            ElaborationCode.SI_MULTIPLICITY_INVALID,
            f"negative multiplicity on {name!r}",
        )
    if lower is not None:
        lower_count = _modeled_integer_bound(
            lower,
            parent=parent,
            slots=slots,
            attributes_by_slot=attributes_by_slot,
            closures=closures,
        )
        if lower_count is None:
            raise MultiplicityExpansionError(
                ElaborationCode.SI_MULTIPLICITY_UNRESOLVED,
                f"lower multiplicity on {name!r} is not a known finite integer",
            )
        if lower_count != count:
            raise MultiplicityExpansionError(
                ElaborationCode.SI_MULTIPLICITY_UNSUPPORTED,
                f"range multiplicity on {name!r} is outside the supported occurrence model",
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
        owner = getattr(usage, "owning_type", None)
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
                raise InvalidRedefinitionFamilyError(
                    f"native usage view repeats declaration {candidate_id.to_wire()}"
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
            raise RecursiveContainmentError(f"containment re-enters definition {type_id.to_wire()}")
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
            if parent is None:
                owner = getattr(usage, "owner", None)
                if owner is not None and SysideAdapter.is_instance(owner, "Package"):
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
                display_path=rendered,
            )
            existing = occurrences.get(occurrence_id)
            if existing is not None and existing != occurrence:
                raise InvalidRedefinitionFamilyError("duplicate exact occurrence identity")
            occurrences[occurrence_id] = occurrence
            next_active = active_types + ((type_id,) if type_id is not None else ())
            for child in child_declarations:
                add_usage(child, occurrence, next_active)

    for root in sorted(roots, key=lambda item: declaration_id_for(item).to_wire()):
        add_usage(root, None, ())

    return OccurrenceIndex(occurrences, slots, closures)
