"""Phase 3: expansion — four-kind dispatch, blocked-owner error, multi-instance.

Live tests load each fixture through the real ``build_pipeline_context`` (for a
production-shaped registry/design-attrs/calc-usages triple) plus
``build_part_instance_index`` and ``extract_constraint_facts`` — the exact
inputs ``lower_constraints`` takes in production. Offline tests hand-build
``ConstraintUsageFact``s for the owner-kinds no live fixture models
(``requirement_def``, ``package``).
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.constraint_extraction import extract_constraint_facts
from agentic_mbse.sysml.constraint_facts import (
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    IdentityFact,
    OwnerFact,
    OwningDefinitionFact,
)
from agentic_mbse.sysml.expression_ir import serialize_expression

from sysml_codegen.analysis.constraint_lowering import lower_constraints
from sysml_codegen.analysis.part_instance_index import (
    NonFiniteCardinalityError,
    build_part_instance_index,
)
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from tests.conftest import FIXTURES_DIR, requires_license


def _load(name: str):
    ctx = build_pipeline_context([FIXTURES_DIR / name])
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
        inp.bound_channel
        for c in concrete
        for inp in c.inputs
        if inp.resolution == "module_output"
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
    assert cc.inputs == []  # inline predicate has no named formals/actuals
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
        schema_version="constraint-facts/v1",
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
        predicate=None,
        inherited_into=[],
    )
    facts = ConstraintFacts(
        schema_version="constraint-facts/v1",
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
