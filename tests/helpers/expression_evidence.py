"""Test helpers for compiling payloads through the production evidence boundary."""

from __future__ import annotations

from uuid import UUID

from agentic_mbse.sysml.reference_use import is_standard_library_use

from sysml_codegen.elaboration.expression_evidence import (
    ExpressionEvidenceInventory,
    ExpressionSiteRole,
    build_expression_evidence_inventory,
)


def calculation_dependencies(model: object) -> dict[UUID, tuple[UUID, ...]]:
    """Return the exact calculation-member dependency map acquired from ``model``."""
    inventory = build_expression_evidence_inventory(model)
    return calculation_dependencies_from_inventory(inventory)


def calculation_dependencies_from_inventory(
    inventory: ExpressionEvidenceInventory,
) -> dict[UUID, tuple[UUID, ...]]:
    """Apply the production standard-library policy to acquired calculation rows."""
    dependencies: dict[UUID, tuple[UUID, ...]] = {}
    for site in inventory.sites():
        if site.role is not ExpressionSiteRole.CALC_DEFINITION_DEPENDENCY:
            continue
        ordered: list[UUID] = []
        for use in inventory.require_exact(site):
            leaf_id = use.path.leaf.element_id
            if not is_standard_library_use(use) and leaf_id not in ordered:
                ordered.append(leaf_id)
        dependencies[site.declaration_id] = tuple(ordered)
    return dependencies
