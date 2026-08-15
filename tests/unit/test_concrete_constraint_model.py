"""Phase 1: ConcreteConstraint data contract + constraint_id minting (offline, no model)."""

import pytest

import sysml_codegen.resolution.models as resolution_models
from sysml_codegen.core.errors import CodeGenerationError
from sysml_codegen.core.identifier_types import mint_constraint_id
from sysml_codegen.resolution.models import (
    ConcreteConstraint,
    ConcreteConstraintInput,
    ConstraintCatalogEntry,
    ConstraintInputResolution,
)


def test_catalog_exclusion_models_are_public_and_fingerprint_contract_is_complete():
    assert "ConstraintExclusion" in resolution_models.__all__
    assert "ConstraintCatalogExcludedRecord" in resolution_models.__all__

    docstring = resolution_models.ConstraintCatalog.__doc__
    assert docstring is not None
    for collection in ("source_records", "concrete_entries", "excluded_records"):
        assert collection in docstring


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
        predicate_source_key="definition:Design::ReusableConstraint",
        is_negated=False,
        expected_value=True if eligible else None,
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
        exclusion=(
            None
            if eligible
            else {
                "kind": "unassessed_form",
                "reasons": [],
                "location": "<no location>",
            }
        ),
    )


def test_concrete_constraint_json_roundtrip():
    cc = _make_cc("Design__c__cell__nonneg__deadbeefdeadbeef", "Design__c__cell")
    assert ConcreteConstraint.model_validate_json(cc.model_dump_json()) == cc


def test_unassessed_shape_carries_kind_and_no_node():
    cc = _make_cc("Design__c__cell__nonneg__deadbeefdeadbeef", "Design__c__cell", eligible=False)
    assert cc.eligible is False
    assert cc.evaluation_channel is None
    assert cc.inputs == []


# The three ``assert_unique_constraint_ids`` guard nodes that stood here retired with the
# v5 family (retirement step 2): that helper lived in ``analysis/constraint_lowering.py``
# (ledger L-001) and was called only from inside it, and ledger L-212 records the per-node
# disposition. The property they guarded survives in a stronger form. The exact route mints
# the same ids (``core/identifier_types.mint_constraint_id``) and claims
# ``f"{constraint_id}__evaluation"`` as a public channel, so two constraints minting one id
# now collide *at the seam*, with a typed ``SI_RENDERING_COLLISION`` refusal
# (``elaboration/project.py:287``) instead of a post-hoc assertion. That refusal is pinned by
# ``tests/conformance/test_elaboration_projection.py:156`` on constructed inputs and by
# ``tests/conformance/test_d5_variants.py:273`` end to end.


# --- invariant enforcement (code-quality remediation, 2026-07-14) ---------------
# The docstrings always claimed these states were impossible; the models now
# reject them at construction instead of relying on downstream asserts.


def test_input_module_output_requires_bound_channel():
    # The review's original probe: wrong arm populated, right arm empty.
    with pytest.raises(ValueError, match="must not populate 'design_attribute_qn'"):
        ConcreteConstraintInput(
            formal_name="p",
            resolution=ConstraintInputResolution.MODULE_OUTPUT,
            bound_channel=None,
            design_attribute_qn="Design__c__wrong",
        )
    # And the pure-missing case:
    with pytest.raises(ValueError, match="requires 'bound_channel'"):
        ConcreteConstraintInput(
            formal_name="p",
            resolution=ConstraintInputResolution.MODULE_OUTPUT,
        )


def test_input_rejects_field_from_other_resolution_arm():
    with pytest.raises(ValueError, match="must not populate 'design_attribute_qn'"):
        ConcreteConstraintInput(
            formal_name="p",
            resolution=ConstraintInputResolution.MODULE_OUTPUT,
            bound_channel="Design__c__cell__power_calc__p",
            design_attribute_qn="Design__c__also_set",
        )


def test_input_design_attribute_requires_qn():
    with pytest.raises(ValueError, match="requires 'design_attribute_qn'"):
        ConcreteConstraintInput(
            formal_name="p",
            resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
        )


def test_input_modeled_default_allows_absent_default_ir():
    # Pinned edge: a formal with no recorded default mints a defaultless
    # LIBRARY_DEFAULT entry point downstream (test_phase4_bugfix_regressions).
    inp = ConcreteConstraintInput(
        formal_name="zero",
        resolution=ConstraintInputResolution.MODELED_DEFAULT,
        default_ir=None,
    )
    assert inp.default_ir is None


def test_input_modeled_default_rejects_channel():
    with pytest.raises(ValueError, match="must not populate 'bound_channel'"):
        ConcreteConstraintInput(
            formal_name="zero",
            resolution=ConstraintInputResolution.MODELED_DEFAULT,
            bound_channel="Design__c__cell__power_calc__p",
        )


def test_eligible_requires_predicate_ir_and_channel():
    kwargs = _make_cc("id_0", "Design__c__cell").model_dump()
    kwargs["predicate_ir"] = None
    with pytest.raises(ValueError, match="has no predicate_ir"):
        ConcreteConstraint(**kwargs)
    kwargs = _make_cc("id_0", "Design__c__cell").model_dump()
    kwargs["evaluation_channel"] = None
    with pytest.raises(ValueError, match="has no evaluation_channel"):
        ConcreteConstraint(**kwargs)


def test_eligible_requires_known_polarity():
    kwargs = _make_cc("id_0", "Design__c__cell").model_dump()
    kwargs["is_negated"] = None
    kwargs["expected_value"] = None
    with pytest.raises(ValueError, match="known polarity"):
        ConcreteConstraint(**kwargs)


def test_unassessed_rejects_executable_payload():
    kwargs = _make_cc("id_0", "Design__c__cell").model_dump()
    kwargs["eligible"] = False
    with pytest.raises(ValueError, match="unassessed.*executable payload"):
        ConcreteConstraint(**kwargs)


def test_eligible_allows_missing_membership_kind():
    kwargs = _make_cc("id_0", "Design__c__cell").model_dump()
    kwargs["membership_kind"] = None
    assert ConcreteConstraint(**kwargs).membership_kind is None


def test_unassessed_record_stays_constructible():
    cc = _make_cc("id_0", "Design__c__cell", eligible=False)
    assert cc.eligible is False and cc.predicate_ir is None


def test_eligible_record_with_exclusion_rejected():
    kwargs = _make_cc("id_0", "Design__c__cell").model_dump()
    kwargs["exclusion"] = {
        "kind": "non_numerical",
        "reasons": ["warn_non_numerical_equality"],
        "location": "model.sysml:10:3",
    }
    with pytest.raises(ValueError, match="must not carry exclusion"):
        ConcreteConstraint(**kwargs)


def test_ineligible_record_without_exclusion_rejected():
    kwargs = _make_cc("id_0", "Design__c__cell", eligible=False).model_dump()
    kwargs["exclusion"] = None
    with pytest.raises(ValueError, match="requires exclusion"):
        ConcreteConstraint(**kwargs)


def test_expected_value_must_derive_from_polarity():
    kwargs = _make_cc("id_0", "Design__c__cell").model_dump()
    kwargs["is_negated"] = True  # expected_value stays True -> inconsistent
    with pytest.raises(ValueError, match="does not derive from is_negated"):
        ConcreteConstraint(**kwargs)


def _catalog_entry(**changes) -> ConstraintCatalogEntry:
    values = {
        "declaration_id": "decl_id_0",
        "constraint_id": "id_0",
        "usage_qualified_name": "Design__c__cell__nonneg",
        "source_local_identity": "nonneg",
        "source_form": "definition_typed",
        "owner_qualified_name": "Design__c__cell",
        "definition_qualified_name": "Design::ReusableConstraint",
        "owner_instance_path": "Design__c__cell",
        "membership_kind": None,
        "predicate_source_key": "definition:Design::ReusableConstraint",
        "is_negated": False,
        "expected_value": True,
        "predicate_ir": '{"kind":"literal"}',
        "evaluation_channel": "id_0__evaluation",
    }
    values.update(changes)
    return ConstraintCatalogEntry(**values)


def _default_eligible_constraint() -> ConcreteConstraint:
    values = _make_cc("default_eligible", "Design__c__cell").model_dump(
        exclude={"eligible", "exclusion"}
    )
    return ConcreteConstraint(**values)


def _assert_rejected_assignment_is_transactional(
    model: ConcreteConstraint | ConstraintCatalogEntry,
    field: str,
    value: object,
    match: str,
) -> None:
    before = model.model_copy(deep=True)
    before_json = model.model_dump_json()
    with pytest.raises(ValueError, match=match):
        setattr(model, field, value)
    assert model == before
    assert model.model_dump_json() == before_json
    assert type(model).model_validate_json(model.model_dump_json()) == before


@pytest.mark.parametrize("field", ["is_negated", "expected_value", "predicate_ir"])
def test_catalog_entry_requires_executable_fields(field):
    with pytest.raises(ValueError):
        _catalog_entry(**{field: None})


def test_catalog_entry_expected_value_derives_from_polarity():
    with pytest.raises(ValueError, match="does not derive"):
        _catalog_entry(is_negated=True, expected_value=True)


def test_concrete_constraint_rejects_eligibility_mutation_in_both_directions():
    eligible = _make_cc("eligible", "Design__c__cell")
    _assert_rejected_assignment_is_transactional(
        eligible, "eligible", False, "unassessed.*executable payload"
    )

    unassessed = _make_cc("unassessed", "Design__c__cell", eligible=False)
    _assert_rejected_assignment_is_transactional(
        unassessed, "eligible", True, "must not carry exclusion"
    )


def test_default_eligible_rejects_eligibility_mutation_transactionally():
    constraint = _default_eligible_constraint()
    assert "eligible" not in constraint.model_fields_set
    assert "exclusion" not in constraint.model_fields_set
    _assert_rejected_assignment_is_transactional(
        constraint, "eligible", False, "unassessed.*executable payload"
    )


def test_default_eligible_rejects_exclusion_mutation_transactionally():
    constraint = _default_eligible_constraint()
    _assert_rejected_assignment_is_transactional(
        constraint,
        "exclusion",
        {
            "kind": "non_numerical",
            "reasons": ["warn_non_numerical_equality"],
            "location": "model.sysml:10:3",
        },
        "must not carry exclusion",
    )


def test_catalog_entry_rejects_polarity_mutation_and_stays_serializable():
    entry = _catalog_entry()
    _assert_rejected_assignment_is_transactional(entry, "is_negated", True, "does not derive")
