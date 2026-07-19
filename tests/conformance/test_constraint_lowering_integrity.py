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

from sysml_codegen.analysis.constraint_lowering import (
    excluded_usage_indices,
    lower_constraints,
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
    profile = evaluate_profile(facts)
    assert excluded_usage_indices(facts, profile.decisions) == (0, 1)
    with caplog.at_level(logging.WARNING, logger="sysml_codegen.analysis.constraint_lowering"):
        records = lower_constraints(
            facts,
            occ_index=None,
            registry=None,
            design_attrs={},
            calc_usages=[],
            source_location_mode="live",
            source_roots=[tmp_path],
        )
    repeated = lower_constraints(
        facts,
        occ_index=None,
        registry=None,
        design_attrs={},
        calc_usages=[],
        source_location_mode="live",
        source_roots=[tmp_path],
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
    common = dict(occ_index=None, registry=None, design_attrs={}, calc_usages=[])
    with pytest.raises(CodeGenerationError, match="explicit source-location route"):
        lower_constraints(facts, **common)
    with pytest.raises(CodeGenerationError, match="does not match"):
        lower_constraints(
            facts,
            **common,
            source_location_mode="live",
            source_roots=[tmp_path / "other"],
        )
    with pytest.raises(CodeGenerationError, match="canonical source referent"):
        lower_constraints(
            facts,
            **common,
            source_location_mode="snapshot",
            source_roots=[],
        )
    usage.location = None
    with pytest.raises(CodeGenerationError, match="anonymous assertion has no LocationFact"):
        lower_constraints(
            facts,
            **common,
            source_location_mode="live",
            source_roots=[tmp_path],
        )


def test_selector_rejects_profile_cardinality_mismatch():
    facts = _facts([])
    usage = _usage(
        location=None,
        source_form="satisfy",
        owner_kind="package",
        predicate=None,
    )
    decision = evaluate_profile(_facts([usage])).decisions[0]
    with pytest.raises(CodeGenerationError, match="cardinality"):
        excluded_usage_indices(facts, [decision])


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
    common = dict(occ_index=None, registry=None, design_attrs={}, calc_usages=[])
    for usage, expected_id in named_cases:
        [record] = lower_constraints(_facts([usage]), **common)
        assert record.constraint_id == expected_id

    eligible = _usage(
        location=LocationFact("/evidence/root/model.sysml", 10, 2),
        source_form="inline",
        owner_kind="package",
        predicate=_comparison("<=", "real"),
    )
    [record] = lower_constraints(_facts([eligible]), **common)
    assert record.constraint_id == "Pkg__Owner__anon__016538f43a48a34e"
    assert record.source_local_identity == "anon"
    assert len(record.constraint_id.rsplit("__", 1)[1]) == 16
    assert record.usage_qualified_name == "<anonymous>"
