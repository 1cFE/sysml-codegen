from __future__ import annotations

import logging
from pathlib import Path

import pytest
from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    LocationFact,
    OwnerFact,
    OwningDefinitionFact,
)
from agentic_mbse.sysml.executable_profile import evaluate_profile
from agentic_mbse.sysml.expression_facts import IdentityFact, LiteralFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import LiteralNode, OperatorNode

import sysml_codegen.analysis.constraint_lowering as constraint_lowering
from sysml_codegen.analysis.constraint_lowering import (
    associate_usage_decisions,
    is_excluded_usage,
    lower_constraints,
    prepare_constraint_usages,
)
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError


def _identity(name: str | None = None, qualified_name: str | None = None) -> IdentityFact:
    return IdentityFact(kind="AssertConstraintUsage", name=name, qualified_name=qualified_name)


def _literal(value: object, category: str) -> LiteralNode:
    kind = "LiteralBoolean" if category == "boolean" else "LiteralRational"
    return LiteralNode(
        literal=LiteralFact(kind=kind, value=value, result_type=category),
        operand_type=OperandTypeFact(category=category, enumeration=None, unit=None),
    )


def _comparison(operator: str, category: str) -> OperatorNode:
    values = (True, False) if category == "boolean" else (1.0, 2.0)
    return OperatorNode(
        operator=operator,
        operands=[_literal(values[0], category), _literal(values[1], category)],
        operand_type=None,
    )


def _usage(
    *,
    location: LocationFact | None,
    source_form: str,
    owner_kind: str,
    predicate: OperatorNode | None,
    name: str | None = None,
    qualified_name: str | None = None,
) -> ConstraintUsageFact:
    identity = _identity(name, qualified_name)
    effective = identity if source_form == "inline" else None
    return ConstraintUsageFact(
        identity=identity,
        location=location,
        source=ConstraintSource(
            form=source_form,
            effective_predicate_source=effective,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=effective,
        ),
        owner=OwnerFact(
            owner=None,
            owning_definition=OwningDefinitionFact(kind=owner_kind, qualified_name="Pkg::Owner"),
        ),
        scope=identity,
        membership_kind=None,
        is_negated=False if predicate is not None else None,
        actuals=[],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )


def _facts(usages: list[ConstraintUsageFact]) -> ConstraintFacts:
    return ConstraintFacts(definitions=[], usages=usages, contexts=[], diagnostics=[])


def _locations(tmp_path: Path, dimension: str) -> list[LocationFact]:
    first = tmp_path / "first.sysml"
    second = tmp_path / "second.sysml"
    first.write_text("")
    second.write_text("")
    if dimension == "line":
        return [LocationFact(str(first), 10, 2), LocationFact(str(first), 20, 2)]
    if dimension == "column":
        return [LocationFact(str(first), 10, 2), LocationFact(str(first), 10, 8)]
    return [LocationFact(str(first), 10, 2), LocationFact(str(second), 10, 2)]


@pytest.mark.parametrize("dimension", ["line", "column", "file"])
@pytest.mark.parametrize(
    ("kind", "source_form", "owner_kind", "predicate"),
    [
        ("non_numerical", "inline", "package", _comparison("==", "boolean")),
        ("unassessed_form", "satisfy", "package", None),
        ("unsupported_owner", "inline", "requirement_def", _comparison("<=", "real")),
    ],
)
def test_anonymous_excluded_identity_matrix(
    tmp_path: Path,
    caplog,
    dimension: str,
    kind: str,
    source_form: str,
    owner_kind: str,
    predicate: OperatorNode | None,
):
    usages = [
        _usage(
            location=location,
            source_form=source_form,
            owner_kind=owner_kind,
            predicate=predicate,
        )
        for location in _locations(tmp_path, dimension)
    ]
    assert all(usage.identity.name is None for usage in usages)
    assert all(usage.identity.qualified_name is None for usage in usages)
    assert all(usage.location is not None for usage in usages)

    facts = _facts(usages)
    assert [
        is_excluded_usage(usage, decision)
        for usage, decision in associate_usage_decisions(facts)
    ] == [True, True]
    with caplog.at_level(logging.WARNING, logger="sysml_codegen.analysis.constraint_lowering"):
        records = lower_constraints(
            facts,
            prepared=prepare_constraint_usages(
                facts,
                occ_index=None,
                calc_usages=[],
                source_location_mode="live",
                source_roots=[tmp_path],
            ),
            registry=None,
            design_attrs={},
        )
    repeated = lower_constraints(
        facts,
        prepared=prepare_constraint_usages(
            facts,
            occ_index=None,
            calc_usages=[],
            source_location_mode="live",
            source_roots=[tmp_path],
        ),
        registry=None,
        design_attrs={},
    )

    assert [record.model_dump(mode="json") for record in records] == [
        record.model_dump(mode="json") for record in repeated
    ]
    assert len({record.constraint_id for record in records}) == 2
    assert all(len(record.constraint_id.rsplit("__", 1)[1]) == 32 for record in records)
    assert [record.exclusion.kind for record in records if record.exclusion] == [kind, kind]
    assert all(
        record.exclusion and record.exclusion.location.startswith("root-0/") for record in records
    )
    warnings = [
        record.getMessage()
        for record in caplog.records
        if record.name == "sysml_codegen.analysis.constraint_lowering"
    ]
    expected_warning_count = 4 if kind == "non_numerical" else 0
    assert len(warnings) == expected_warning_count


def test_anonymous_route_and_identity_failures_are_loud(tmp_path: Path):
    model = tmp_path / "model.sysml"
    model.write_text("")
    usage = _usage(
        location=LocationFact(str(model), 10, 2),
        source_form="satisfy",
        owner_kind="package",
        predicate=None,
    )
    facts = _facts([usage])
    # Source-location routing is preparation's job now; every route failure is
    # raised before a batch exists, so lowering is never reached.
    with pytest.raises(CodeGenerationError, match="explicit source-location route"):
        prepare_constraint_usages(facts, occ_index=None, calc_usages=[])
    with pytest.raises(CodeGenerationError, match="does not match"):
        prepare_constraint_usages(
            facts,
            occ_index=None,
            calc_usages=[],
            source_location_mode="live",
            source_roots=[tmp_path / "other"],
        )
    with pytest.raises(CodeGenerationError, match="canonical source referent"):
        prepare_constraint_usages(
            facts,
            occ_index=None,
            calc_usages=[],
            source_location_mode="snapshot",
            source_roots=[],
        )
    usage.location = None
    with pytest.raises(CodeGenerationError, match="anonymous assertion has no LocationFact"):
        prepare_constraint_usages(
            facts,
            occ_index=None,
            calc_usages=[],
            source_location_mode="live",
            source_roots=[tmp_path],
        )


def test_association_rejects_profile_cardinality_mismatch(monkeypatch: pytest.MonkeyPatch):
    """Cardinality is verified where the profile is evaluated, so no downstream
    consumer can be handed a short or long decision list."""
    facts = _facts([])
    usage = _usage(
        location=None,
        source_form="satisfy",
        owner_kind="package",
        predicate=None,
    )
    stray = evaluate_profile(_facts([usage]))
    monkeypatch.setattr(constraint_lowering, "evaluate_profile", lambda _facts: stray)
    with pytest.raises(CodeGenerationError, match="cardinality"):
        associate_usage_decisions(facts)


def test_named_ids_and_eligible_anonymous_id_remain_byte_identical():
    named_cases = [
        (
            _usage(
                location=None,
                source_form="inline",
                owner_kind="package",
                predicate=_comparison("==", "boolean"),
                name="named_nonnum",
                qualified_name="Evidence__named_nonnum",
            ),
            "Evidence_named_nonnum__named_nonnum__ae00ccca8ea0d861",
        ),
        (
            _usage(
                location=None,
                source_form="satisfy",
                owner_kind="package",
                predicate=None,
                name="named_unassessed",
                qualified_name="Evidence__named_unassessed",
            ),
            "Evidence_named_unassessed__named_unassessed__ccbd872f5c3f2298",
        ),
        (
            _usage(
                location=None,
                source_form="inline",
                owner_kind="requirement_def",
                predicate=_comparison("<=", "real"),
                name="named_unsupported",
                qualified_name="Evidence__named_unsupported",
            ),
            "Evidence_named_unsupported__named_unsupported__e7202a6c6ee2d32a",
        ),
    ]
    for usage, expected_id in named_cases:
        case_facts = _facts([usage])
        [record] = lower_constraints(
            case_facts,
            prepared=prepare_constraint_usages(case_facts, occ_index=None, calc_usages=[]),
            registry=None,
            design_attrs={},
        )
        assert record.constraint_id == expected_id

    eligible = _usage(
        location=LocationFact("/evidence/root/model.sysml", 10, 2),
        source_form="inline",
        owner_kind="package",
        predicate=_comparison("<=", "real"),
    )
    eligible_facts = _facts([eligible])
    [record] = lower_constraints(
        eligible_facts,
        prepared=prepare_constraint_usages(eligible_facts, occ_index=None, calc_usages=[]),
        registry=None,
        design_attrs={},
    )
    assert record.constraint_id == "Pkg__Owner__anon__016538f43a48a34e"
    assert record.source_local_identity == "anon"
    assert len(record.constraint_id.rsplit("__", 1)[1]) == 16
    assert record.usage_qualified_name == "<anonymous>"
