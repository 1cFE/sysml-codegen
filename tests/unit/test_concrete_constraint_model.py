"""Phase 1: ConcreteConstraint data contract + constraint_id minting (offline, no model)."""

import pytest

from sysml_codegen.analysis.constraint_lowering import (
    assert_unique_constraint_ids,
    mint_constraint_id,
)
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.resolution.models import (
    ConcreteConstraint,
    ConcreteConstraintInput,
    ConstraintInputResolution,
)


def test_constraint_id_deterministic_and_collision_distinct():
    tup = ("Design__c__cell__nonneg", "Design__c__cell", "assert", False)
    a = mint_constraint_id(instance_path="Design__c__cell", source_local="nonneg", tuple_=tup)
    b = mint_constraint_id(instance_path="Design__c__cell", source_local="nonneg", tuple_=tup)
    assert a == b  # byte-identical across calls
    suffix = a.rsplit("__", 1)[1]
    assert len(suffix) == 16
    assert all(ch in "0123456789abcdef" for ch in suffix)

    # two anonymous asserts on one instance -> LocationFact tuple disambiguates
    anon1 = mint_constraint_id(
        instance_path="Design__c",
        source_local="anon",
        tuple_=("file:10:2", "Design__c", "assert", False),
    )
    anon2 = mint_constraint_id(
        instance_path="Design__c",
        source_local="anon",
        tuple_=("file:20:2", "Design__c", "assert", False),
    )
    assert anon1 != anon2


def _make_cc(
    constraint_id: str, owner_instance_path: str, eligible: bool = True
) -> ConcreteConstraint:
    return ConcreteConstraint(
        constraint_id=constraint_id,
        usage_qualified_name="Design__c__cell__nonneg",
        source_local_identity="nonneg",
        source_form="definition_typed",
        owner_kind="part_def",
        owner_qualified_name="Design__Cell",
        owner_instance_path=owner_instance_path,
        membership_kind="assert",
        is_negated=False,
        expected_value=True,
        predicate_ir='{"kind":"literal"}' if eligible else None,
        inputs=[
            ConcreteConstraintInput(
                formal_name="p",
                resolution=ConstraintInputResolution.MODULE_OUTPUT,
                bound_channel="Design__c__cell__power_calc__p",
            )
        ]
        if eligible
        else [],
        evaluation_channel=f"{constraint_id}__evaluation" if eligible else None,
        eligible=eligible,
    )


def test_concrete_constraint_json_roundtrip():
    cc = _make_cc("Design__c__cell__nonneg__deadbeefdeadbeef", "Design__c__cell")
    assert ConcreteConstraint.model_validate_json(cc.model_dump_json()) == cc


def test_unassessed_shape_carries_kind_and_no_node():
    cc = _make_cc("Design__c__cell__nonneg__deadbeefdeadbeef", "Design__c__cell", eligible=False)
    assert cc.eligible is False
    assert cc.evaluation_channel is None
    assert cc.inputs == []


def test_assert_unique_constraint_ids_raises_on_duplicate():
    a = _make_cc("dup_id", "Design__c__cell[0]")
    b = _make_cc("dup_id", "Design__c__cell[1]")
    with pytest.raises(CodeGenerationError, match="dup_id"):
        assert_unique_constraint_ids([a, b])


def test_assert_unique_constraint_ids_passes_on_distinct():
    a = _make_cc("id_0", "Design__c__cell[0]")
    b = _make_cc("id_1", "Design__c__cell[1]")
    assert_unique_constraint_ids([a, b])  # no raise
