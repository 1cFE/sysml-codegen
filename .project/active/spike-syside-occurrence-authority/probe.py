"""Compare SysIDE usage declarations with codegen's concrete occurrence index."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter, get_syside

from sysml_codegen.elaboration.identity import DeclarationId
from sysml_codegen.elaboration.occurrence import (
    build_feature_slot_index,
    build_occurrence_index,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES = REPO_ROOT / "tests" / "fixtures"
FIXTURE_NAMES = (
    "nested_occurrence_override_probe",
    "spec_chain_twolevel",
    "retype_model",
    "d38_caret",
    "deep_cross_scope_probe",
)
SYSIDE = get_syside()


def _load(name: str) -> Any:
    model, diagnostics = SysideAdapter.load_model([FIXTURES / name])
    errors = [
        diagnostic
        for diagnostic in diagnostics.all
        if str(diagnostic.severity).endswith("Error")
    ]
    if errors:
        raise RuntimeError(f"{name}: parser errors: {errors!r}")
    return model


def _element_id(element: Any) -> str:
    return str(SysideAdapter.element_id(element))


def _identity(element: Any) -> dict[str, str | None]:
    owner = getattr(element, "owning_type", None) or getattr(element, "owner", None)
    return {
        "kind": type(element).__name__,
        "id": _element_id(element),
        "name": str(getattr(element, "name", None)),
        "qualified_name": (
            str(getattr(element, "qualified_name", None))
            if getattr(element, "qualified_name", None) is not None
            else None
        ),
        "owner": (
            str(getattr(owner, "qualified_name", None))
            if owner is not None and getattr(owner, "qualified_name", None) is not None
            else None
        ),
    }


def _native_summary(model: Any) -> dict[str, Any]:
    usages = list(model.elements(SYSIDE.Usage, include_subtypes=True))
    part_usages = [
        usage for usage in usages if SysideAdapter.is_instance(usage, "PartUsage")
    ]
    by_id = {_element_id(usage): usage for usage in usages}
    surface_counts: Counter[str] = Counter()
    target_counts: dict[str, Counter[str]] = {
        surface: Counter()
        for surface in ("nested_occurrences", "nested_parts", "nested_usages", "usages")
    }
    contextual_clones: set[str] = set()
    nested_occurrence_targets: dict[str, dict[str, str | None]] = {}

    for owner in usages:
        for surface in ("nested_occurrences", "nested_parts", "nested_usages", "usages"):
            values = list(getattr(owner, surface, ()) or ())
            for value in values:
                surface_counts[surface] += 1
                value_id = _element_id(value)
                target_counts[surface][value_id] += 1
                if value_id in by_id and value is not by_id[value_id]:
                    contextual_clones.add(value_id)
                if surface == "nested_occurrences" and not bool(
                    getattr(value, "is_library_element", False)
                ):
                    nested_occurrence_targets[value_id] = _identity(value)

    return {
        "usage_declarations": len(usages),
        "part_usage_declarations": len(part_usages),
        "surface_edge_counts": dict(sorted(surface_counts.items())),
        "surface_distinct_target_counts": {
            surface: len(counts) for surface, counts in target_counts.items()
        },
        "surface_targets_cloned_for_context": sorted(contextual_clones),
        "nested_occurrence_targets": list(nested_occurrence_targets.values()),
        "part_usage_identities": [_identity(usage) for usage in part_usages],
    }


def _codegen_summary(model: Any) -> dict[str, Any]:
    slots = build_feature_slot_index(model)
    index = build_occurrence_index(model, slots)
    occurrences = index.occurrences()
    declaration_counts = Counter(
        occurrence.effective_usage_id.to_wire() for occurrence in occurrences
    )
    return {
        "concrete_occurrences": len(occurrences),
        "declarations_with_multiple_concrete_occurrences": {
            declaration: count
            for declaration, count in sorted(declaration_counts.items())
            if count > 1
        },
        "occurrences": [
            {
                "occurrence_id": occurrence.occurrence_id.to_wire(),
                "effective_usage_id": occurrence.effective_usage_id.to_wire(),
                "effective_type_id": (
                    occurrence.effective_type_id.to_wire()
                    if isinstance(occurrence.effective_type_id, DeclarationId)
                    else None
                ),
                "parent_id": (
                    occurrence.parent_id.to_wire() if occurrence.parent_id is not None else None
                ),
                "display_path": occurrence.display_path,
            }
            for occurrence in occurrences
        ],
    }


def main() -> None:
    report: dict[str, Any] = {}
    for name in FIXTURE_NAMES:
        model = _load(name)
        report[name] = {
            "native": _native_summary(model),
            "codegen": _codegen_summary(model),
        }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
