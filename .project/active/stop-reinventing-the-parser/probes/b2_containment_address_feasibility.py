#!/usr/bin/env python3
"""Probe the seven D2 containment-address topologies on real SysIDE models."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import syside
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from probe_support import load_model, sha256_file, validate_lock, write_canonical_json

from sysml_codegen.elaboration.identity import (
    DeclarationId,
    FeatureSlotId,
    OccurrenceId,
    declaration_id_for,
)
from sysml_codegen.elaboration.occurrence import (
    ExactOccurrence,
    FeatureSlotIndex,
    OccurrenceIndex,
    build_feature_slot_index,
    build_occurrence_index,
)

TOPOLOGY_ROWS = (
    "direct_package_owned_target",
    "definition_owned_target",
    "nested_package_explicit_and_no_prefix_refusal",
    "repeated_outer_consumer_index",
    "redefined_usage_canonical_slot",
    "calculation_usage_owner_and_output_scope",
    "multiplicity_writer_owner_domain",
)


@dataclass(frozen=True)
class PrototypeAddress:
    anchor_kind: Literal["package", "part_definition"]
    anchor_id: DeclarationId
    steps: tuple[FeatureSlotId, ...]

    def to_data(self) -> dict[str, object]:
        return {
            "anchor_kind": self.anchor_kind,
            "anchor_id": self.anchor_id.to_wire(),
            "steps": [step.root_declaration.to_wire() for step in self.steps],
        }


class AddressMissingError(RuntimeError):
    """The prototype cannot instantiate an address in the supplied domain."""


def semantic_owner(element: Any) -> Any:
    """Apply the design's acquisition-only owner selector."""
    owning_type = getattr(element, "owning_type", None)
    return owning_type if owning_type is not None else getattr(element, "owner", None)


def _stable_id(element: Any) -> DeclarationId:
    qualified_name = getattr(element, "qualified_name", None)
    if qualified_name is None:
        raise RuntimeError(f"{type(element).__name__} has no stable qualified identity")
    return declaration_id_for(element)


def build_address(element: Any, slots: FeatureSlotIndex) -> PrototypeAddress:
    """Build the minimal read-only D2 prototype, refusing unsupported owner shapes."""
    current = (
        element if SysideAdapter.is_instance(element, "PartUsage") else semantic_owner(element)
    )
    steps: list[FeatureSlotId] = []
    active: set[DeclarationId] = set()
    while current is not None:
        identity = _stable_id(current)
        if identity in active:
            raise RuntimeError("containment owner walk contains a cycle")
        active.add(identity)
        if SysideAdapter.is_instance(current, "PartUsage"):
            steps.append(slots.slot_of(identity))
            current = semantic_owner(current)
            continue
        if SysideAdapter.is_instance(current, "PartDefinition"):
            return PrototypeAddress("part_definition", identity, tuple(reversed(steps)))
        if SysideAdapter.is_instance(current, "Package"):
            return PrototypeAddress("package", identity, tuple(reversed(steps)))
        raise RuntimeError(f"unsupported containment owner kind {type(current).__name__}")
    raise RuntimeError("containment owner walk ended without an anchor")


def _features_by_qn(model: Any) -> dict[str, Any]:
    return {
        str(element.qualified_name): element
        for element in SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True)
        if getattr(element, "qualified_name", None) is not None
    }


def _package_id_for_root(element: Any) -> DeclarationId:
    current = element
    while current is not None:
        owner = semantic_owner(current)
        if SysideAdapter.is_instance(owner, "Package"):
            return _stable_id(owner)
        current = owner
    raise RuntimeError(f"{getattr(element, 'qualified_name', element)!r} has no package owner")


class PrototypeResolver:
    """Instantiate prototype addresses from exact occurrence/index records only."""

    def __init__(
        self,
        model: Any,
        slots: FeatureSlotIndex,
        occurrences: OccurrenceIndex,
    ) -> None:
        self._model = model
        self._slots = slots
        self._occurrences = occurrences
        self._features = _features_by_qn(model)
        self._children: dict[tuple[OccurrenceId, FeatureSlotId], list[ExactOccurrence]] = {}
        self._roots: dict[tuple[DeclarationId, FeatureSlotId], list[ExactOccurrence]] = {}
        by_declaration = {
            declaration_id_for(element): element for element in self._features.values()
        }
        for occurrence in occurrences.occurrences():
            slot = occurrence.occurrence_id.steps[-1].containment_slot
            if occurrence.parent_id is None:
                usage = by_declaration[occurrence.effective_usage_id]
                package_id = _package_id_for_root(usage)
                self._roots.setdefault((package_id, slot), []).append(occurrence)
            else:
                self._children.setdefault((occurrence.parent_id, slot), []).append(occurrence)

    def resolve(
        self,
        address: PrototypeAddress,
        consumer: OccurrenceId | DeclarationId,
    ) -> tuple[ExactOccurrence, ...] | tuple[str, DeclarationId]:
        if address.anchor_kind == "package":
            if not isinstance(consumer, DeclarationId) or consumer != address.anchor_id:
                raise AddressMissingError("consumer is outside the exact package anchor")
            if not address.steps:
                return ("package", address.anchor_id)
            first, *rest = address.steps
            current = list(self._roots.get((address.anchor_id, first), []))
            for step in rest:
                current = [
                    child
                    for parent in current
                    for child in self._children.get((parent.occurrence_id, step), [])
                ]
        else:
            if not isinstance(consumer, OccurrenceId):
                raise AddressMissingError("definition anchor requires an occurrence consumer")
            lineage = (self._occurrences.occurrence(consumer),) + self._occurrences.ancestors(
                consumer
            )
            current = [
                occurrence for occurrence in lineage if address.anchor_id in occurrence.type_closure
            ]
            if len(current) != 1:
                raise AddressMissingError(
                    f"definition anchor has {len(current)} concrete scopes in consumer lineage"
                )
            for step in address.steps:
                current = [
                    child
                    for parent in current
                    for child in self._children.get((parent.occurrence_id, step), [])
                ]
        if not current:
            raise AddressMissingError("address has no concrete occurrence")
        return tuple(sorted(current, key=lambda item: item.occurrence_id.to_wire()))


def _occurrence(index: OccurrenceIndex, display_path: str) -> ExactOccurrence:
    matches = [item for item in index.occurrences() if item.display_path == display_path]
    if len(matches) != 1:
        raise RuntimeError(f"expected one occurrence {display_path!r}, found {len(matches)}")
    return matches[0]


def _fixture_state(root: Path) -> tuple[Any, FeatureSlotIndex, OccurrenceIndex, PrototypeResolver]:
    model = load_model(root)
    slots = build_feature_slot_index(model)
    occurrences = build_occurrence_index(model, slots)
    return model, slots, occurrences, PrototypeResolver(model, slots, occurrences)


def run_probe(repository: Path) -> dict[str, object]:
    fixtures = repository / "tests/fixtures"
    domain_model, domain_slots, domain_occurrences, domain_resolver = _fixture_state(
        fixtures / "occurrence_domain_derivation"
    )
    domain_features = _features_by_qn(domain_model)
    package = domain_features["OccurrenceDomainDerivation::package_source"].owner
    package_id = _stable_id(package)

    package_address = build_address(
        domain_features["OccurrenceDomainDerivation::package_source"], domain_slots
    )
    package_result = domain_resolver.resolve(package_address, package_id)

    repeated_one = _occurrence(
        domain_occurrences, "OccurrenceDomainDerivation__repeated_container[1]"
    )
    repeated_sensor = _occurrence(
        domain_occurrences, "OccurrenceDomainDerivation__repeated_container[1]__sensor"
    )
    sensor_usage = domain_features["OccurrenceDomainDerivation::Container::sensor"]
    sensor_address = build_address(sensor_usage, domain_slots)
    sensor_result = domain_resolver.resolve(sensor_address, repeated_one.occurrence_id)

    reading = domain_features["OccurrenceDomainDerivation::Sensor::reading"]
    reading_address = build_address(reading, domain_slots)
    reading_result = domain_resolver.resolve(reading_address, repeated_sensor.occurrence_id)

    nested_usage = domain_features["OccurrenceDomainDerivation::package_nested::nested_sensor"]
    nested_address = build_address(nested_usage, domain_slots)
    nested_result = domain_resolver.resolve(nested_address, package_id)
    no_prefix_refused = False
    try:
        domain_resolver.resolve(reading_address, package_id)
    except AddressMissingError:
        no_prefix_refused = True
    if not no_prefix_refused:
        raise RuntimeError("nested package target succeeded without its modeled prefix")

    variant = _occurrence(domain_occurrences, "OccurrenceDomainDerivation__variant_container")
    variant_sensor = _occurrence(
        domain_occurrences, "OccurrenceDomainDerivation__variant_container__sensor"
    )
    redefined_usage = domain_features["OccurrenceDomainDerivation::VariantContainer::sensor"]
    base_slot = domain_slots.slot_of(declaration_id_for(sensor_usage))
    redefined_slot = domain_slots.slot_of(declaration_id_for(redefined_usage))
    if base_slot != redefined_slot:
        raise RuntimeError("redefined usage split into a second feature slot")
    variant_result = domain_resolver.resolve(
        build_address(redefined_usage, domain_slots), variant.occurrence_id
    )

    calc_model, calc_slots, calc_occurrences, calc_resolver = _fixture_state(
        fixtures / "occurrence_calc_domain_derivation"
    )
    calc_features = _features_by_qn(calc_model)
    cell_one = _occurrence(calc_occurrences, "OccurrenceCalcDomainDerivation__cell[1]")
    first_producer = calc_features["OccurrenceCalcDomainDerivation::Cell::first_producer"]
    calc_owner_address = build_address(first_producer, calc_slots)
    calc_scope = calc_resolver.resolve(calc_owner_address, cell_one.occurrence_id)

    mult_model, mult_slots, mult_occurrences, mult_resolver = _fixture_state(
        fixtures / "multiplicity_writer_authority"
    )
    mult_features = _features_by_qn(mult_model)
    valid_row = _occurrence(mult_occurrences, "MultiplicityWriterAuthority__valid_row")
    count = mult_features["MultiplicityWriterAuthority::ValidRow::count"]
    count_scope = mult_resolver.resolve(build_address(count, mult_slots), valid_row.occurrence_id)
    valid_cells = [
        item
        for item in mult_occurrences.children(valid_row.occurrence_id)
        if item.display_segment.startswith("cell[")
    ]
    unrelated = mult_features["MultiplicityWriterAuthority::unrelated_count"]
    if semantic_owner(unrelated) == semantic_owner(count):
        raise RuntimeError("unrelated multiplicity writer unexpectedly shares the exact owner")

    def occurrences_data(items: object) -> list[str]:
        if not isinstance(items, tuple) or not items or not isinstance(items[0], ExactOccurrence):
            return []
        return [item.occurrence_id.to_wire() for item in items]

    rows = [
        {
            "id": TOPOLOGY_ROWS[0],
            "address": package_address.to_data(),
            "result": [package_result[0], package_result[1].to_wire()],
        },
        {
            "id": TOPOLOGY_ROWS[1],
            "address": reading_address.to_data(),
            "result": occurrences_data(reading_result),
        },
        {
            "id": TOPOLOGY_ROWS[2],
            "address": nested_address.to_data(),
            "result": occurrences_data(nested_result),
            "no_prefix_refused": no_prefix_refused,
        },
        {
            "id": TOPOLOGY_ROWS[3],
            "address": sensor_address.to_data(),
            "consumer": repeated_one.occurrence_id.to_wire(),
            "result": occurrences_data(sensor_result),
            "expected": repeated_sensor.occurrence_id.to_wire(),
        },
        {
            "id": TOPOLOGY_ROWS[4],
            "canonical_slot": base_slot.root_declaration.to_wire(),
            "effective_usage": variant_sensor.effective_usage_id.to_wire(),
            "result": occurrences_data(variant_result),
        },
        {
            "id": TOPOLOGY_ROWS[5],
            "owner_address": calc_owner_address.to_data(),
            "consumer": cell_one.occurrence_id.to_wire(),
            "result": occurrences_data(calc_scope),
            "calculation_usage": declaration_id_for(first_producer).to_wire(),
        },
        {
            "id": TOPOLOGY_ROWS[6],
            "writer_address": build_address(count, mult_slots).to_data(),
            "writer_scope": occurrences_data(count_scope),
            "modeled_count": 2,
            "materialized_children": [item.occurrence_id.to_wire() for item in valid_cells],
            "unrelated_writer": declaration_id_for(unrelated).to_wire(),
        },
    ]
    if [row["id"] for row in rows] != list(TOPOLOGY_ROWS):
        raise RuntimeError("topology row set changed")
    if occurrences_data(sensor_result) != [repeated_sensor.occurrence_id.to_wire()]:
        raise RuntimeError("repeated outer address crossed to another occurrence")
    if len(valid_cells) != 2:
        raise RuntimeError(f"modeled multiplicity produced {len(valid_cells)} children, expected 2")
    return {
        "schema_version": "stop-parser-b2/v1",
        "verdict": "CONTAINMENT_ADDRESS_FEASIBLE",
        "syside_version": syside.__version__,
        "topology_row_count": len(rows),
        "all_expected": True,
        "live_element_count": sum(
            len(list(SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True)))
            for model in (domain_model, calc_model, mult_model)
        ),
        "rows": rows,
        "sources": {
            str(path.relative_to(repository)): sha256_file(path)
            for root in (
                fixtures / "occurrence_domain_derivation",
                fixtures / "occurrence_calc_domain_derivation",
                fixtures / "multiplicity_writer_authority",
            )
            for path in sorted(root.glob("*.sysml"))
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--lock", type=Path, required=True)
    parser.add_argument("--probe-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repository = args.repository.resolve()
    validate_lock(
        repository,
        lock_path=args.lock.resolve(),
        expected_probe_commit=args.probe_commit,
    )
    write_canonical_json(args.output, run_probe(repository))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
