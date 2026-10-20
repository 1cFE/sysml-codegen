"""The generator route's steps, in the order they run (Item 2b design, Architecture).

``Refused`` names one of these, and the report reads it, so the order is part of the contract.
``prepare`` produces CONSTRUCTION through CONSTRAINT_TOTALITY, and CONSTRAINT_PLAN only if
creating the template environment fails; ``emit_package`` produces CONSTRAINT_PLAN,
COVERAGE_ACCOUNT, DESTINATION and EMIT. Nothing produces PARAMETER_FIELD_NAMES yet.
"""

from __future__ import annotations

from sysml_codegen.cli.prepare import PreparationStep


def test_step_order_is_pinned():
    assert [step.name for step in PreparationStep] == [
        "CONSTRUCTION",
        "GENERATION_METADATA",
        "EXIT_POINT_TYPES",
        "CONSTRAINT_NAMES",
        "OUTPUT_PATHS",
        "REGISTRY_CLASS_NAMES",
        "CONSTRAINT_TOTALITY",
        "CONSTRAINT_PLAN",
        "COVERAGE_ACCOUNT",
        "PARAMETER_FIELD_NAMES",
        "DESTINATION",
        "EMIT",
    ]
