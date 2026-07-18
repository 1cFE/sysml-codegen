"""Phase 3: expansion — four-kind dispatch, blocked-owner error, multi-instance.

Live tests load each fixture through the real ``build_pipeline_context`` (for a
production-shaped registry/design-attrs/calc-usages triple) plus
``build_part_instance_index`` and ``extract_constraint_facts`` — the exact
inputs ``lower_constraints`` takes in production. Offline tests hand-build
``ConstraintUsageFact``s for the owner-kinds no live fixture models
(``requirement_def``, ``package``).
"""

from __future__ import annotations

import logging

import pytest
from agentic_mbse.sysml.constraint_extraction import extract_constraint_facts
from agentic_mbse.sysml.constraint_facts import (
    ActualFact,
    ConstraintDefinitionFact,
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    FormalFact,
    IdentityFact,
    OwnerFact,
    OwningDefinitionFact,
)
from agentic_mbse.sysml.executable_profile import Eligibility, evaluate_profile
from agentic_mbse.sysml.expression_facts import (
    FeatureReferenceFact,
    LiteralFact,
    OperandTypeFact,
    UnitFact,
)
from agentic_mbse.sysml.expression_ir import (
    FeatureReferenceNode,
    LiteralNode,
    OperatorNode,
    UnitAnnotationNode,
    serialize_expression,
)

from sysml_codegen.analysis.constraint_lowering import lower_constraints
from sysml_codegen.analysis.part_instance_index import (
    NonFiniteCardinalityError,
    build_part_instance_index,
)
from sysml_codegen.generation.predicate_compiler import (
    PredicateCompileError,
    compile_predicate,
    load_predicate,
)
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from tests.conftest import FIXTURES_DIR, requires_license


def _load(name: str):
    # lower_constraints_enabled=False: these tests call `lower_constraints`
    # manually below to test it in isolation — the pipeline context itself
    # must stay inert so a model with a halting/blocked assert (e.g.
    # constraint_blocked_owner) doesn't raise before the test reaches its
    # own `lower_constraints` call.
    ctx = build_pipeline_context([FIXTURES_DIR / name], lower_constraints_enabled=False)
    occ_index = build_part_instance_index(ctx.extractor.model)
    facts = extract_constraint_facts(ctx.extractor.model)
    return ctx, occ_index, facts


@requires_license
def test_multi_instance_three_ids_three_channels_shared_binding():
    ctx, occ_index, facts = _load("constraint_multi_instance")
    concrete = lower_constraints(
        facts,
        occ_index=occ_index,
        registry=ctx.output_registry,
        design_attrs=ctx.design_attributes,
        calc_usages=ctx.calc_usages,
    )
    assert len(concrete) == 3
    assert len({c.constraint_id for c in concrete}) == 3
    assert len({c.evaluation_channel for c in concrete}) == 3
    assert all(c.eligible for c in concrete)

    # B1-settled: each entry records the shared de-indexed producer binding —
    # not three distinct producer channels.
    bound = {
        inp.bound_channel for c in concrete for inp in c.inputs if inp.resolution == "module_output"
    }
    assert len(bound) == 1
    assert list(bound)[0].endswith("power_calc__p")


@requires_license
def test_blocked_owner_named_generation_error():
    ctx, occ_index, facts = _load("constraint_blocked_owner")
    with pytest.raises(CodeGenerationError) as exc_info:
        lower_constraints(
            facts,
            occ_index=occ_index,
            registry=ctx.output_registry,
            design_attrs=ctx.design_attributes,
            calc_usages=ctx.calc_usages,
        )
    message = str(exc_info.value)
    assert "BlockedLeaf" in message
    assert "star_member" in message or "non-finite" in message


@requires_license
def test_blocked_owner_occ_index_raises_directly():
    """Corroborates the generation-error path: the raw index call itself raises
    NonFiniteCardinalityError, the exception lower_constraints translates."""
    _ctx, occ_index, _facts = _load("constraint_blocked_owner")
    with pytest.raises(NonFiniteCardinalityError):
        occ_index.occurrences_of("constraint_blocked_owner__BlockedLeaf")


@requires_license
def test_inline_source_form_selects_usage_predicate():
    ctx, occ_index, facts = _load("constraint_inline")
    concrete = lower_constraints(
        facts,
        occ_index=occ_index,
        registry=ctx.output_registry,
        design_attrs=ctx.design_attributes,
        calc_usages=ctx.calc_usages,
    )
    assert len(concrete) == 1
    cc = concrete[0]
    assert cc.source_form == "inline"
    assert cc.eligible is True
    assert [(item.formal_name, item.design_attribute_qn) for item in cc.inputs] == [
        ("value", "constraint_inline__InlineHost__value")
    ]
    usage = facts.usages[0]
    assert cc.predicate_ir == serialize_expression(usage.predicate)


def _identity(qn: str, name: str | None, kind: str = "AssertConstraintUsage") -> IdentityFact:
    return IdentityFact(kind=kind, name=name, qualified_name=qn)


def test_requirement_def_owner_cataloged_unassessed():
    usage = ConstraintUsageFact(
        identity=_identity("Design__req__check", "check"),
        location=None,
        source=ConstraintSource(
            form="requirement_constraint",
            effective_predicate_source=None,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=None,
        ),
        owner=OwnerFact(
            owner=_identity("Design__req", "req", kind="RequirementUsage"),
            owning_definition=OwningDefinitionFact(
                kind="requirement_def", qualified_name="Design::ReqDef"
            ),
        ),
        scope=_identity("Design__req__check", "check"),
        membership_kind="assume",
        is_negated=None,
        actuals=[],
        omitted_default_formals=[],
        predicate=None,
        inherited_into=[],
    )
    facts = ConstraintFacts(
        definitions=[],
        usages=[usage],
        contexts=[],
        diagnostics=[],
    )
    concrete = lower_constraints(
        facts, occ_index=None, registry=None, design_attrs={}, calc_usages=[]
    )
    assert len(concrete) == 1
    cc = concrete[0]
    assert cc.eligible is False
    assert cc.evaluation_channel is None
    assert cc.owner_kind == "requirement_def"
    assert cc.inputs == []
    assert cc.exclusion is not None
    assert cc.exclusion.kind == "unsupported_owner"
    assert cc.exclusion.location == "<no location>"


def test_package_owned_expands_once():
    usage = ConstraintUsageFact(
        identity=_identity("Design__top_level_assert", "top_level_assert"),
        location=None,
        source=ConstraintSource(
            form="inline",
            effective_predicate_source=_identity("Design__top_level_assert", "top_level_assert"),
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=_identity("Design__top_level_assert", "top_level_assert"),
        ),
        owner=OwnerFact(
            owner=None,
            owning_definition=OwningDefinitionFact(kind="package", qualified_name="Design"),
        ),
        scope=_identity("Design__top_level_assert", "top_level_assert"),
        membership_kind=None,
        is_negated=False,
        actuals=[],
        omitted_default_formals=[],
        # Item 3 preflight: a predicate-less assert now correctly blocks
        # (block_missing_predicate), so this expansion test carries a real
        # admitted predicate to stay on the admit path.
        predicate=_admitted_predicate(),
        inherited_into=[],
    )
    facts = ConstraintFacts(
        definitions=[],
        usages=[usage],
        contexts=[],
        diagnostics=[],
    )
    concrete = lower_constraints(
        facts, occ_index=None, registry=None, design_attrs={}, calc_usages=[]
    )
    assert len(concrete) == 1
    cc = concrete[0]
    assert cc.eligible is True
    assert cc.owner_kind == "package"
    assert cc.evaluation_channel is not None


# ---------------------------------------------------------------------------
# Item 3 preflight wiring (applied by orchestrator from the ready-to-apply
# brief in agentic-mbse .project/active/executable-profile/sysml-codegen-wiring.md).
# ---------------------------------------------------------------------------


def _real_literal(value: float):
    from agentic_mbse.sysml.expression_facts import LiteralFact, OperandTypeFact
    from agentic_mbse.sysml.expression_ir import LiteralNode

    return LiteralNode(
        literal=LiteralFact(kind="LiteralRational", value=value, result_type="Real"),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _admitted_predicate():
    """A profile-admitted static scalar comparison: 1.0 <= 2.0."""
    from agentic_mbse.sysml.expression_ir import OperatorNode

    return OperatorNode(
        operator="<=",
        operands=[_real_literal(1.0), _real_literal(2.0)],
        operand_type=None,
    )


def _blocked_predicate():
    """A profile-blocked construct: real-valued equality (block_real_equality)."""
    from agentic_mbse.sysml.expression_ir import OperatorNode

    return OperatorNode(
        operator="==",
        operands=[_real_literal(1.0), _real_literal(2.0)],
        operand_type=None,
    )


def _package_assert(qn: str, predicate) -> ConstraintUsageFact:
    return ConstraintUsageFact(
        identity=_identity(qn, qn.rsplit("__", 1)[-1]),
        location=None,
        source=ConstraintSource(
            form="inline",
            effective_predicate_source=_identity(qn, None),
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=_identity(qn, None),
        ),
        owner=OwnerFact(
            owner=None,
            owning_definition=OwningDefinitionFact(kind="package", qualified_name="Design"),
        ),
        scope=_identity(qn, None),
        membership_kind=None,
        is_negated=False,
        actuals=[],
        omitted_default_formals=[],
        predicate=predicate,
        inherited_into=[],
    )


def _facts(usages) -> ConstraintFacts:
    return ConstraintFacts(
        definitions=[],
        usages=list(usages),
        contexts=[],
        diagnostics=[],
    )


def _typed_literal(value, category: str, enumeration: str | None = None) -> LiteralNode:
    kind = {
        "boolean": "LiteralBoolean",
        "integer": "LiteralInteger",
        "real": "LiteralRational",
        "string": "LiteralString",
        "enum": "LiteralString",
    }[category]
    return LiteralNode(
        literal=LiteralFact(kind=kind, value=value, result_type=category),
        operand_type=OperandTypeFact(category=category, enumeration=enumeration, unit=None),
    )


_METRE = UnitFact(unit="SI::metre", dimension="ISQBase::LengthUnit")


def _typed_ref(name: str, category: str, *, unit: UnitFact | None = None) -> FeatureReferenceNode:
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category=category, enumeration=None, unit=unit),
    )


def _quantity_literal(value: int) -> UnitAnnotationNode:
    return UnitAnnotationNode(
        value=_typed_literal(value, "integer"),
        unit_text="m",
        operand_type=OperandTypeFact(category="quantity", enumeration=None, unit=_METRE),
    )


@pytest.mark.parametrize(
    ("predicate", "values", "expected"),
    [
        (
            OperatorNode(
                operator="<=",
                operands=[
                    OperatorNode(
                        operator="+",
                        operands=[_typed_literal(2, "integer")],
                        operand_type=None,
                    ),
                    _typed_literal(3, "integer"),
                ],
                operand_type=None,
            ),
            {},
            True,
        ),
        (
            OperatorNode(
                operator="<=",
                operands=[_typed_ref("a", "integer"), _typed_ref("b", "integer")],
                operand_type=None,
            ),
            {"a": 1, "b": 2},
            True,
        ),
        (
            OperatorNode(
                operator=">",
                operands=[_typed_ref("a", "real"), _typed_literal(0.0, "real")],
                operand_type=None,
            ),
            {"a": -1.0},
            False,
        ),
        (
            OperatorNode(
                operator="<=",
                operands=[
                    _typed_ref("length", "quantity", unit=_METRE),
                    _quantity_literal(2),
                ],
                operand_type=None,
            ),
            {"length": 2.0},
            True,
        ),
        (
            OperatorNode(
                operator="<=",
                operands=[
                    OperatorNode(
                        operator="*",
                        operands=[
                            _typed_literal(2, "integer"),
                            _typed_ref("length", "quantity", unit=_METRE),
                        ],
                        operand_type=None,
                    ),
                    _quantity_literal(3),
                ],
                operand_type=None,
            ),
            {"length": 2.0},
            False,
        ),
        (
            OperatorNode(
                operator="<=",
                operands=[
                    OperatorNode(
                        operator="/",
                        operands=[
                            _typed_ref("a", "quantity", unit=_METRE),
                            _typed_ref("b", "quantity", unit=_METRE),
                        ],
                        operand_type=None,
                    ),
                    _typed_literal(2, "integer"),
                ],
                operand_type=None,
            ),
            {"a": 6.0, "b": 3.0},
            True,
        ),
        (
            OperatorNode(
                operator="<=",
                operands=[
                    OperatorNode(
                        operator="**",
                        operands=[_typed_literal(2, "integer"), _typed_literal(3, "integer")],
                        operand_type=None,
                    ),
                    _typed_literal(9.0, "real"),
                ],
                operand_type=None,
            ),
            {},
            True,
        ),
        (
            OperatorNode(
                operator="and",
                operands=[
                    OperatorNode(
                        operator="<=",
                        operands=[_typed_literal(1, "integer"), _typed_literal(2, "integer")],
                        operand_type=None,
                    ),
                    OperatorNode(
                        operator="not",
                        operands=[
                            OperatorNode(
                                operator=">",
                                operands=[
                                    _typed_literal(1, "integer"),
                                    _typed_literal(2, "integer"),
                                ],
                                operand_type=None,
                            )
                        ],
                        operand_type=None,
                    ),
                ],
                operand_type=None,
            ),
            {},
            True,
        ),
    ],
    ids=[
        "unary-plus",
        "integer-ordering-refs",
        "real-ordering-ref",
        "quantity-ordering-ref",
        "scalar-times-quantity",
        "quantity-ratio",
        "dimensionless-power",
        "connectives",
    ],
)
def test_profile_v3_admit_implies_predicate_compiles_and_executes(predicate, values, expected):
    facts = _facts([_package_assert("Design__profile_v3", predicate)])
    [decision] = evaluate_profile(facts).decisions
    assert decision.eligibility is Eligibility.ADMIT

    source, args = compile_predicate(predicate, "profile_v3_predicate")
    assert args == list(values)
    result = load_predicate(source, "profile_v3_predicate")(**values)
    assert result.actual_value is expected


@pytest.mark.parametrize("operator", ["+", "-", "*", "/", "**", "^"])
def test_profile_v3_admitted_arithmetic_operator_matrix(operator):
    left = _typed_ref("x", "integer")
    right = _typed_literal(2, "integer")
    arithmetic = OperatorNode(
        operator=operator,
        operands=[left, right],
        operand_type=None,
    )
    predicate = OperatorNode(
        operator="<=",
        operands=[arithmetic, _typed_literal(16.0, "real")],
        operand_type=None,
    )
    [decision] = evaluate_profile(
        _facts([_package_assert("Design__arithmetic", predicate)])
    ).decisions
    assert decision.eligibility is Eligibility.ADMIT
    source, args = compile_predicate(predicate, "profile_v3_arithmetic")
    assert args == ["x"]
    assert load_predicate(source, "profile_v3_arithmetic")(x=4).actual_value is True


@pytest.mark.parametrize("operator", ["<", "<=", ">", ">="])
def test_profile_v3_admitted_ordering_operator_matrix(operator):
    predicate = OperatorNode(
        operator=operator,
        operands=[_typed_ref("x", "real"), _typed_literal(2.0, "real")],
        operand_type=None,
    )
    [decision] = evaluate_profile(
        _facts([_package_assert("Design__ordering", predicate)])
    ).decisions
    assert decision.eligibility is Eligibility.ADMIT
    source, args = compile_predicate(predicate, "profile_v3_ordering")
    assert args == ["x"]
    expected = {"<": True, "<=": True, ">": False, ">=": False}[operator]
    assert load_predicate(source, "profile_v3_ordering")(x=1.0).actual_value is expected


def test_malformed_operand_fact_blocks_before_predicate_compilation():
    malformed = LiteralNode(
        literal=LiteralFact(kind="LiteralInteger", value=1, result_type="integer"),
        operand_type=None,
    )
    predicate = OperatorNode(
        operator="<=",
        operands=[malformed, _typed_literal(2, "integer")],
        operand_type=None,
    )
    facts = _facts([_package_assert("Design__malformed", predicate)])
    [decision] = evaluate_profile(facts).decisions
    assert decision.eligibility is Eligibility.BLOCK
    assert {diagnostic.reason for diagnostic in decision.diagnostics} == {
        "block_malformed_operand_fact"
    }
    with pytest.raises(CodeGenerationError, match="block_malformed_operand_fact"):
        lower_constraints(facts, occ_index=None, registry=None, design_attrs={}, calc_usages=[])


class _AlwaysResolvedRegistry:
    def scoped_lookup(self, _key):
        return "Design__producer__value"

    def alias_lookup(self, _key):
        return None

    def scoped_alias_lookup(self, _key):
        return None


def _actual_value(name: str = "value") -> FeatureReferenceNode:
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _definition_typed_facts(
    *,
    formals: list[FormalFact],
    actuals: list[ActualFact],
    omitted_default_formals: list[str] | None = None,
) -> ConstraintFacts:
    definition_qn = "Design::RequiredConstraint"
    predicate = _admitted_predicate()
    definition_identity = _identity(
        definition_qn, "RequiredConstraint", kind="ConstraintDefinition"
    )
    definition = ConstraintDefinitionFact(
        identity=definition_identity, formals=formals, predicate=predicate
    )
    usage_qn = "Design__required_assert"
    usage = ConstraintUsageFact(
        identity=_identity(usage_qn, "required_assert"),
        location=None,
        source=ConstraintSource(
            form="definition_typed",
            effective_predicate_source=definition_identity,
            constraint_definition=definition_identity,
            referenced_feature_target=None,
            asserted_constraint=_identity(usage_qn, "required_assert"),
        ),
        owner=OwnerFact(
            owner=None,
            owning_definition=OwningDefinitionFact(kind="package", qualified_name="Design"),
        ),
        scope=_identity(usage_qn, "required_assert"),
        membership_kind=None,
        is_negated=False,
        actuals=actuals,
        omitted_default_formals=omitted_default_formals or [],
        predicate=predicate,
        inherited_into=[],
    )
    return ConstraintFacts(definitions=[definition], usages=[usage], contexts=[], diagnostics=[])


def _formal(name: str, *, has_default: bool = False, default=None) -> FormalFact:
    return FormalFact(
        name=name,
        qualified_name=f"Design::RequiredConstraint::{name}",
        types=["ScalarValues::Real"],
        has_default=has_default,
        default=default,
    )


def _lower_offline(facts: ConstraintFacts):
    return lower_constraints(
        facts,
        occ_index=None,
        registry=_AlwaysResolvedRegistry(),
        design_attrs={},
        calc_usages=[],
    )


def test_actual_local_name_does_not_override_formal_target_identity():
    formal = _formal("required")
    facts = _definition_typed_facts(
        formals=[formal],
        actuals=[
            ActualFact(
                name="alias",
                direction="in",
                formal_targets=[formal.qualified_name],
                value=_actual_value(),
            )
        ],
    )
    [lowered] = _lower_offline(facts)
    assert [input_.formal_name for input_ in lowered.inputs] == ["required"]


def test_missing_required_formal_is_generation_error():
    facts = _definition_typed_facts(formals=[_formal("required")], actuals=[])
    with pytest.raises(CodeGenerationError, match="required.*no actual.*modeled default"):
        _lower_offline(facts)


@pytest.mark.parametrize(
    "targets",
    [[], ["Design::RequiredConstraint::required", "Design::Other::required"]],
    ids=["zero-targets", "multiple-targets"],
)
def test_actual_requires_exactly_one_formal_target(targets):
    formal = _formal("required")
    facts = _definition_typed_facts(
        formals=[formal],
        actuals=[
            ActualFact(
                name="alias",
                direction="in",
                formal_targets=targets,
                value=_actual_value(),
            )
        ],
    )
    with pytest.raises(CodeGenerationError, match="exactly one formal target"):
        _lower_offline(facts)


def test_duplicate_actuals_for_one_formal_are_generation_error():
    formal = _formal("required")
    actual = ActualFact(
        name="alias",
        direction="in",
        formal_targets=[formal.qualified_name],
        value=_actual_value(),
    )
    facts = _definition_typed_facts(formals=[formal], actuals=[actual, actual])
    with pytest.raises(CodeGenerationError, match="multiple actuals.*required"):
        _lower_offline(facts)


def test_actual_target_outside_referenced_definition_is_generation_error():
    facts = _definition_typed_facts(
        formals=[_formal("required")],
        actuals=[
            ActualFact(
                name="alias",
                direction="in",
                formal_targets=["Design::OtherConstraint::required"],
                value=_actual_value(),
            )
        ],
    )
    with pytest.raises(CodeGenerationError, match="not a formal of.*RequiredConstraint"):
        _lower_offline(facts)


def test_explicit_modeled_default_covers_formal_even_without_default_ir():
    formal = _formal("threshold", has_default=True, default=None)
    facts = _definition_typed_facts(
        formals=[formal], actuals=[], omitted_default_formals=[formal.qualified_name]
    )
    [lowered] = _lower_offline(facts)
    [input_] = lowered.inputs
    assert input_.formal_name == "threshold"
    assert input_.resolution == "modeled_default"
    assert input_.default_ir is None


def test_preflight_halts_on_blocked_assert_before_any_lowering():
    facts = _facts(
        [
            _package_assert("Design__ok_assert", _admitted_predicate()),
            _package_assert("Design__blocked_assert", _blocked_predicate()),
        ]
    )
    with pytest.raises(CodeGenerationError) as exc_info:
        lower_constraints(facts, occ_index=None, registry=None, design_attrs={}, calc_usages=[])
    message = str(exc_info.value)
    assert "not executable" in message
    assert "Design__blocked_assert" in message
    assert "block_real_equality_requires_tolerance" in message
    assert "two-inequality" in message


def test_non_numerical_outcome_does_not_halt_compatibility_phase():
    predicate = OperatorNode(
        operator="==",
        operands=[_typed_literal(True, "boolean"), _typed_literal(False, "boolean")],
        operand_type=None,
    )
    facts = _facts([_package_assert("Design__annotation", predicate)])

    [record] = lower_constraints(
        facts, occ_index=None, registry=None, design_attrs={}, calc_usages=[]
    )

    assert record.eligible is False
    assert record.predicate_ir is None
    assert record.exclusion is not None
    assert record.exclusion.kind == "non_numerical"
    assert record.exclusion.reasons == ["warn_non_numerical_equality"]


def test_non_numerical_warning_preserves_walk_order_and_location_fallback(caplog):
    predicate = OperatorNode(
        operator="xor",
        operands=[_typed_ref("left", "boolean"), _typed_ref("right", "boolean")],
        operand_type=None,
    )
    facts = _facts([_package_assert("Design__annotation", predicate)])

    with caplog.at_level(logging.WARNING, logger="sysml_codegen.analysis.constraint_lowering"):
        lower_constraints(facts, occ_index=None, registry=None, design_attrs={}, calc_usages=[])

    warnings = [
        record.getMessage()
        for record in caplog.records
        if record.name == "sysml_codegen.analysis.constraint_lowering"
    ]
    assert warnings == [
        "Constraint Design__annotation at <no location> is not numerical and will not execute: "
        "warn_non_numerical_xor, warn_non_numerical_predicate, "
        "warn_non_numerical_predicate"
    ]


@pytest.mark.parametrize("operator", ["==", "!="])
@pytest.mark.parametrize(
    ("category", "left", "right"),
    [
        ("boolean", True, False),
        ("string", "on", "off"),
        ("integer", 1, 2),
        ("real", 1.0, 2.0),
    ],
)
def test_profile_v3_equality_never_crosses_the_compiler_boundary(operator, category, left, right):
    predicate = OperatorNode(
        operator=operator,
        operands=[_typed_literal(left, category), _typed_literal(right, category)],
        operand_type=None,
    )
    [decision] = evaluate_profile(
        _facts([_package_assert("Design__equality", predicate)])
    ).decisions
    assert decision.eligibility is not Eligibility.ADMIT
    with pytest.raises(PredicateCompileError, match="profile preflight must exclude|not admitted"):
        compile_predicate(predicate, "equality_must_not_compile")


def test_admitted_assert_predicate_ir_unchanged_by_wiring():
    predicate = _admitted_predicate()
    facts = _facts([_package_assert("Design__ok_assert", predicate)])
    concrete = lower_constraints(
        facts, occ_index=None, registry=None, design_attrs={}, calc_usages=[]
    )
    assert len(concrete) == 1
    assert concrete[0].eligible is True
    assert concrete[0].predicate_ir == serialize_expression(predicate)


def test_unassessed_usage_in_batch_neither_halts_nor_lowers():
    satisfy = ConstraintUsageFact(
        identity=_identity("Design__sat", "sat", kind="SatisfyRequirementUsage"),
        location=None,
        source=ConstraintSource(
            form="satisfy",
            effective_predicate_source=None,
            constraint_definition=None,
            referenced_feature_target=None,
            asserted_constraint=None,
        ),
        owner=OwnerFact(
            owner=None,
            owning_definition=OwningDefinitionFact(kind="package", qualified_name="Design"),
        ),
        scope=_identity("Design__sat", None),
        membership_kind=None,
        is_negated=None,
        actuals=[],
        omitted_default_formals=[],
        predicate=None,
        inherited_into=[],
    )
    facts = _facts([satisfy, _package_assert("Design__ok_assert", _admitted_predicate())])
    concrete = lower_constraints(
        facts, occ_index=None, registry=None, design_attrs={}, calc_usages=[]
    )
    by_qn = {c.usage_qualified_name: c for c in concrete}
    assert by_qn["Design__sat"].eligible is False
    assert by_qn["Design__sat"].predicate_ir is None
    assert by_qn["Design__ok_assert"].eligible is True


@requires_license
def test_wired_pipeline_path_lowers_by_default_and_is_inert_when_disabled():
    """The Item 5 P1/P2/P3 threading, exercised end-to-end via the flag.

    Default True since Item 8 Phase 4 (snapshot v3 restores live/snapshot
    parity); explicitly passing `lower_constraints_enabled=False` still opts
    out (the mechanism the grandfather set uses at capture time, D3).
    """
    ctx_default = build_pipeline_context([FIXTURES_DIR / "constraint_multi_instance"])
    assert len(ctx_default.concrete_constraints) == 3

    ctx_off = build_pipeline_context(
        [FIXTURES_DIR / "constraint_multi_instance"], lower_constraints_enabled=False
    )
    assert ctx_off.concrete_constraints == []

    ctx_on = build_pipeline_context(
        [FIXTURES_DIR / "constraint_multi_instance"], lower_constraints_enabled=True
    )
    assert len(ctx_on.concrete_constraints) == 3
    module_names = {m.name for m in ctx_on.computation_graph.modules}
    assert "constraint_report_aggregator" in module_names
