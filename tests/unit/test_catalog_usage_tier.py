"""Item 8: the additive catalog surface — five projected entry fields + the admitted-usage tier.

License-free: builds ``ConcreteConstraint`` objects directly and exercises
``assemble_constraint_catalog``. The definition→usage FK *gating* (non-None iff
``source_form == "definition_typed"``) lives in lowering and is covered against a real fixture
in ``tests/conformance/test_catalog_definition_join.py``; here we assert the projection carries
whatever lowering recorded, and that the usage tier deduplicates by full usage identity (F2).
"""

from __future__ import annotations

from agentic_mbse.sysml.constraint_facts import ConstraintFacts
from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import (
    FeatureReferenceNode,
    OperatorNode,
    serialize_expression,
)

from sysml_codegen.generation.constraint_catalog import assemble_constraint_catalog
from sysml_codegen.resolution.models import ConcreteConstraint


def _empty_facts() -> ConstraintFacts:
    return ConstraintFacts(definitions=[], usages=[], contexts=[], diagnostics=[])


def _predicate_ir() -> str:
    ref_a = FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name="a", target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )
    ref_b = FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name="b", target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )
    node = OperatorNode(operator=">", operands=[ref_a, ref_b], operand_type=None)
    return serialize_expression(node)


def _concrete(
    constraint_id: str,
    owner_instance_path: str,
    *,
    usage_qualified_name: str = "Pkg::Cell::nonneg",
    source_local_identity: str = "nonneg",
    source_form: str = "inline",
    owner_qualified_name: str = "Pkg::Cell",
    definition_qualified_name: str | None = None,
    predicate_source_key: str | None = None,
) -> ConcreteConstraint:
    return ConcreteConstraint(
        constraint_id=constraint_id,
        usage_qualified_name=usage_qualified_name,
        source_local_identity=source_local_identity,
        source_form=source_form,
        owner_kind="part_def",
        owner_qualified_name=owner_qualified_name,
        owner_instance_path=owner_instance_path,
        membership_kind="assert",
        predicate_source_key=predicate_source_key or usage_qualified_name,
        is_negated=False,
        expected_value=True,
        predicate_ir=_predicate_ir(),
        inputs=[],
        evaluation_channel=f"{constraint_id}__evaluation",
        eligible=True,
        definition_qualified_name=definition_qualified_name,
    )


def test_entry_projects_five_identity_fields():
    """Each eligible entry carries source_form, usage short name, owner QN, definition QN."""
    concrete = [
        _concrete(
            "C1",
            "Pkg__Cell_1",
            source_form="definition_typed",
            definition_qualified_name="Lib::Reusable",
            predicate_source_key="definition:Lib::Reusable",
        )
    ]
    catalog = assemble_constraint_catalog(concrete, _empty_facts())
    (entry,) = catalog.concrete_entries
    assert entry.source_form == "definition_typed"
    assert entry.source_local_identity == "nonneg"
    assert entry.owner_qualified_name == "Pkg::Cell"
    assert entry.definition_qualified_name == "Lib::Reusable"
    # the existing usage_qualified_name completes the entry-level def→usage join
    assert entry.usage_qualified_name == "Pkg::Cell::nonneg"


def test_entry_carries_none_definition_qn_for_inline():
    concrete = [_concrete("C1", "Pkg__Cell_1", source_form="inline")]
    catalog = assemble_constraint_catalog(concrete, _empty_facts())
    (entry,) = catalog.concrete_entries
    assert entry.definition_qualified_name is None


def test_usage_tier_one_row_per_usage_deduped_across_occurrences():
    """Two occurrences of one usage collapse to a single admitted-usage record (INV-2)."""
    concrete = [
        _concrete("C1", "Pkg__Cell_1"),
        _concrete("C2", "Pkg__Cell_2"),
    ]
    catalog = assemble_constraint_catalog(concrete, _empty_facts())
    assert len(catalog.concrete_entries) == 2
    assert len(catalog.usage_records) == 1
    (usage,) = catalog.usage_records
    assert usage.usage_qualified_name == "Pkg::Cell::nonneg"
    assert usage.source_local_identity == "nonneg"
    assert usage.source_form == "inline"
    assert usage.owner_qualified_name == "Pkg::Cell"
    assert usage.definition_qualified_name is None


def test_usage_tier_distinguishes_two_anonymous_usages_by_local_identity():
    """F2: two distinct anonymous eligible constraints must not collide on '<anonymous>'."""
    concrete = [
        _concrete(
            "A1",
            "Pkg__Cell_1",
            usage_qualified_name="<anonymous>",
            source_local_identity="assert_line_10",
        ),
        _concrete(
            "A2",
            "Pkg__Cell_1",
            usage_qualified_name="<anonymous>",
            source_local_identity="assert_line_20",
        ),
    ]
    catalog = assemble_constraint_catalog(concrete, _empty_facts())
    assert len(catalog.usage_records) == 2
    locals_ = sorted(u.source_local_identity for u in catalog.usage_records)
    assert locals_ == ["assert_line_10", "assert_line_20"]


def test_usage_tier_does_not_carry_predicate_ir():
    """D2a: predicate_ir authority stays on the occurrence tier, not duplicated on the usage."""
    catalog = assemble_constraint_catalog([_concrete("C1", "Pkg__Cell_1")], _empty_facts())
    (usage,) = catalog.usage_records
    assert not hasattr(usage, "predicate_ir")


def test_fingerprint_covers_the_usage_tier():
    """Adding a usage-distinguishing field changes the catalog fingerprint."""
    base = assemble_constraint_catalog([_concrete("C1", "Pkg__Cell_1")], _empty_facts())
    other = assemble_constraint_catalog(
        [_concrete("C1", "Pkg__Cell_1", owner_qualified_name="Pkg::OtherOwner")], _empty_facts()
    )
    assert base.fingerprint != other.fingerprint
