"""Source-isolated GAP-CLOSE Item 3 regression overlay."""

from __future__ import annotations

import pytest

from sysml_codegen.contracts.seal import DEFAULT_COVERAGE_POLICY, seal_package
from sysml_codegen.contracts.serialize import write_contract_json
from sysml_codegen.contracts.verify import INVALID_PATH, verify_package
from sysml_codegen.resolution.models import (
    ConcreteConstraint,
    ConcreteConstraintInput,
    ConstraintInputResolution,
)


def _default_eligible_constraint() -> ConcreteConstraint:
    return ConcreteConstraint(
        constraint_id="default_eligible",
        usage_qualified_name="Design__c__cell__nonneg",
        source_local_identity="nonneg",
        source_form="definition_typed",
        owner_kind="part_def",
        owner_qualified_name="Design__Cell",
        owner_instance_path="Design__c__cell",
        membership_kind="assert",
        is_negated=False,
        expected_value=True,
        predicate_ir='{"kind":"literal"}',
        inputs=[
            ConcreteConstraintInput(
                formal_name="p",
                resolution=ConstraintInputResolution.MODULE_OUTPUT,
                bound_channel="Design__c__cell__power_calc__p",
            )
        ],
        evaluation_channel="default_eligible__evaluation",
    )


def _assert_unchanged_and_serializable_after_rejection(
    constraint: ConcreteConstraint, field: str, value: object
) -> None:
    before = constraint.model_copy(deep=True)
    before_json = constraint.model_dump_json()
    with pytest.raises(ValueError):
        setattr(constraint, field, value)
    assert constraint == before
    assert constraint.model_dump_json() == before_json
    assert ConcreteConstraint.model_validate_json(constraint.model_dump_json()) == before


def test_default_eligible_assignment_is_transactional():
    constraint = _default_eligible_constraint()
    assert "eligible" not in constraint.model_fields_set
    _assert_unchanged_and_serializable_after_rejection(constraint, "eligible", False)


def test_default_exclusion_assignment_is_transactional():
    constraint = _default_eligible_constraint()
    assert "exclusion" not in constraint.model_fields_set
    _assert_unchanged_and_serializable_after_rejection(
        constraint,
        "exclusion",
        {
            "kind": "non_numerical",
            "reasons": ["warn_non_numerical_equality"],
            "location": "model.sysml:10:3",
        },
    )


def _sealed(package_dir):
    (package_dir / "modules").mkdir(parents=True)
    (package_dir / "modules" / "calc.py").write_text("def run():\n    return 1\n")
    (package_dir / "pipelines").mkdir()
    (package_dir / "pipelines" / "p.yaml").write_text("modules: []\n")
    (package_dir / "contracts").mkdir()
    seal = seal_package(package_dir, "pkg", DEFAULT_COVERAGE_POLICY)
    write_contract_json(package_dir / "contracts" / "package_contract.json", seal)
    return package_dir


def test_internal_directory_symlink_is_fatal(tmp_path):
    package_dir = _sealed(tmp_path / "pkg")
    link = package_dir / "alias_modules"
    link.symlink_to(package_dir / "modules", target_is_directory=True)
    result = verify_package(package_dir, "pkg")
    assert result.ok is False
    assert any(
        diagnostic.kind == INVALID_PATH and diagnostic.path == link.name
        for diagnostic in result.diagnostics
    )


def test_escaping_directory_symlink_is_fatal(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "injected.py").write_text("value = 1\n")
    package_dir = _sealed(tmp_path / "pkg")
    link = package_dir / "escape_modules"
    link.symlink_to(outside, target_is_directory=True)
    result = verify_package(package_dir, "pkg")
    assert result.ok is False
    assert any(
        diagnostic.kind == INVALID_PATH and diagnostic.path == link.name
        for diagnostic in result.diagnostics
    )
