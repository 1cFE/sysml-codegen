"""Exact owner anchoring for one-segment references owned by a ``PartUsage``.

SysIDE resolves a direct reference to an exact feature declaration. When that
declaration is owned by a concrete ``PartUsage``, the owner names the occurrence the
author meant. The shipped one-segment route drops that owner and re-finds the leaf's
slot by walking the *consumer's* occurrence lineage, so a consumer inside ``comp_b``
that names ``comp_a``'s length can bind to ``comp_b.length`` with no diagnostic.

This file is the durable authority for that repair. The fixtures it reads are promoted
copies of two research paths that will be archived; see
``tests/fixtures/usage_owned_reference_consumers/PROVENANCE.md`` for where each came
from and what it is for.

**The oracle is typed identity.** Display paths appear only to locate a node; every
assertion compares ``NodeRef``/``ProducerRef`` values, node IDs, or diagnostic codes. A
rename can therefore break a lookup loudly, but it can never make a wrong edge look
right.

**Red before the Phase-3 resolver repair.** These nodes fail today, and each fails on
the *target identity* — never on a load or fixture error, which
``test_combined_fixture_loads_and_elaborates_cleanly`` and the control nodes below pin
separately:

* ``test_u4_package_sibling_binds_the_package_scoped_occurrence`` (``SI_OCCURRENCE_MISSING`` today)
* ``test_u5_named_sibling_binds_the_named_occurrence`` (``SI_OCCURRENCE_AMBIGUOUS`` today)
* ``test_u6_cross_owner_consumer_binds_the_named_sibling`` (silently ``comp_b.length`` today)
* ``test_u7_paired_spellings_bind_distinct_nodes`` (both ``SI_OCCURRENCE_AMBIGUOUS`` today)
* ``test_u7_qualified_edges_equal_their_dot_path_controls`` (same cause)
* ``test_bare_alias_discriminator_binds_the_aliased_owner`` (silently ``comp_b.length`` today)
* the seven ``test_combined_*`` lane nodes and the fan-out node
* ``test_arrayed_exact_owner_refuses_rather_than_answering`` (silently answers today)

All of it requires a live SysIDE license.
"""

from __future__ import annotations

import functools
from collections import Counter
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.elaboration import (
    CalcNode,
    ConstraintNode,
    ElaborationCode,
    InstanceGraph,
    NodeRef,
)
from sysml_codegen.elaboration.identity import NodeId, NodeKind
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import attr, calc, constraint
from tests.helpers.raw_elaboration import elaborate

pytestmark = requires_license

COMBINED = "usage_owned_reference_consumers"
COMBINED_PREFIX = "UsageOwnedReferenceConsumers__plant"

#: The one modelled source every combined-fixture consumer names.
NAMED_SOURCE = f"{COMBINED_PREFIX}__comp_a__length"
#: The same-slot attribute of the enclosing sibling — where the defect lands instead.
ENCLOSING_SIBLING = f"{COMBINED_PREFIX}__comp_b__length"


@functools.cache
def elaborated(fixture: str) -> InstanceGraph:
    """The lenient graph of one fixture root, elaborated once per session.

    Lenient, because several controls exist to carry a diagnostic rather than raise;
    strict/lenient parity is a separate obligation and lives in its own file.
    """
    extractor = SysMLDataExtractor([FIXTURES_DIR / fixture])
    assert extractor.load_models(), f"fixture {fixture} failed to load"
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=False,
    )


def diagnostic_codes(graph: InstanceGraph) -> Counter[object]:
    return Counter(diagnostic.code for diagnostic in graph.diagnostics)


def bound_formal_names(node: CalcNode | ConstraintNode) -> frozenset[str]:
    """The formals that actually received an edge, by name.

    Names identify the *formal*, never a target. A formal missing here is the visible
    shape of a refused reference.
    """
    return frozenset(name for port, name in node.input_names.items() if port in node.inputs)


def consumers_of(graph: InstanceGraph, source: NodeRef) -> Counter[object]:
    """How many input ports of each consumer node carry an edge to ``source``."""
    return Counter(
        node.node_id
        for population in (graph.calcs, graph.constraints)
        for node in population.values()
        for edge in node.inputs.values()
        if edge == source
    )


def test_public_generation_renders_qualified_predicate_by_exact_local_name(
    tmp_path: Path,
) -> None:
    """The real model's ``comp_a::length`` predicate becomes executable Python."""
    output = tmp_path / "out"
    assert run_codegen(
        GenerationConfig(
            models_path=FIXTURES_DIR / COMBINED,
            output_path=output,
            package_name="qualified_predicate",
            pipeline_name="pipeline",
        )
    )

    python_sources = [path.read_text() for path in output.rglob("*.py")]
    assert python_sources
    assert any("_cmp('>', length, 0.0)" in source for source in python_sources)
    assert all("comp_a::length" not in source for source in python_sources)


# ---------------------------------------------------------------------------
# Affected qualified lanes — the promoted u4-u7 topologies
# ---------------------------------------------------------------------------


def test_u4_package_sibling_binds_the_package_scoped_occurrence() -> None:
    """A package-scoped ``PartUsage`` named from inside a part def is a real occurrence.

    Its occurrence is a top-level sibling of the consumer's, so the consumer-lineage walk
    never reaches it and reports the leaf slot missing.
    """
    graph = elaborated("u4_usage_qual_pkg_sibling")
    consumer = calc(graph, "U4UsageQualPkgSibling__plant__area_calc")

    assert consumer.input_by_name("length") == NodeRef(
        attr(graph, "U4UsageQualPkgSibling__shared_component__length").node_id
    )
    assert graph.diagnostics == []


def test_u5_named_sibling_binds_the_named_occurrence() -> None:
    """Naming one of two sibling usages is unambiguous; only the discarded owner is."""
    graph = elaborated("u5_usage_qual_named_sibling")
    consumer = calc(graph, "U5UsageQualNamedSibling__plant__area_calc")

    assert consumer.input_by_name("length_in") == NodeRef(
        attr(graph, "U5UsageQualNamedSibling__plant__comp_a__length").node_id
    )
    assert graph.diagnostics == []


def test_u6_cross_owner_consumer_binds_the_named_sibling() -> None:
    """The sharpest case: authored inside ``comp_b``, naming ``comp_a``.

    Today this edge exists, carries no diagnostic, and points at the wrong occurrence —
    the confident wrong answer the whole item exists to end. The second assertion is what
    makes a silent fallback visible if one is ever added.
    """
    graph = elaborated("u6_usage_qual_crossnamed")
    consumer = calc(graph, "U6UsageQualCrossnamed__plant__comp_b__area_calc")
    named = NodeRef(attr(graph, "U6UsageQualCrossnamed__plant__comp_a__length").node_id)
    enclosing = NodeRef(attr(graph, "U6UsageQualCrossnamed__plant__comp_b__length").node_id)

    assert consumer.input_by_name("length_in") == named
    assert consumers_of(graph, enclosing) == Counter()
    assert graph.diagnostics == []


def test_u7_paired_spellings_bind_distinct_nodes() -> None:
    """Two qualified inputs on one consumer must stay two distinct occurrences."""
    graph = elaborated("u7_both_spellings")
    consumer = calc(graph, "U7BothSpellings__plant__pair_calc")

    assert consumer.input_by_name("a_len") == NodeRef(
        attr(graph, "U7BothSpellings__plant__comp_a__length").node_id
    )
    assert consumer.input_by_name("b_len") == NodeRef(
        attr(graph, "U7BothSpellings__plant__comp_b__length").node_id
    )
    assert graph.diagnostics == []


def test_u7_qualified_edges_equal_their_dot_path_controls() -> None:
    """The two spellings of one value are the same edge, compared edge to edge.

    The dot-path consumer already resolves correctly, so it is the in-fixture control:
    the qualified spelling has to agree with it rather than with a separately asserted
    expectation.
    """
    graph = elaborated("u7_both_spellings")
    qualified = calc(graph, "U7BothSpellings__plant__pair_calc")
    dot_path = calc(graph, "U7BothSpellings__plant__dot_calc")

    assert qualified.input_by_name("a_len") == dot_path.input_by_name("a_len")
    assert qualified.input_by_name("b_len") == dot_path.input_by_name("b_len")


# ---------------------------------------------------------------------------
# Affected bare lane — the Phase-1 authored discriminator
# ---------------------------------------------------------------------------


def test_bare_alias_discriminator_binds_the_aliased_owner() -> None:
    """A literally bare written reference, resolved by SysIDE to the sibling's leaf.

    The written text is ``a_len`` — one segment, no qualifier — declared as
    ``alias a_len for comp_a::length`` at parent scope. This is spec criterion SC8's
    discriminating topology: consumer-lineage selection lands on ``comp_b`` (7.0) and
    exact-owner selection lands on ``comp_a`` (3.0), so the computed value is ``14.0``
    where the model says ``6.0``.
    """
    graph = elaborated("usage_owner_bare_alias")
    consumer = calc(graph, "BareAliasParentScope__plant__comp_b__doubled")
    named = NodeRef(attr(graph, "BareAliasParentScope__plant__comp_a__length").node_id)

    assert list(consumer.inputs.values()) == [named]
    assert graph.diagnostics == []


# ---------------------------------------------------------------------------
# The combined fixture — one named source, every shared-resolver consumer lane
# ---------------------------------------------------------------------------


def test_combined_fixture_loads_and_elaborates_cleanly() -> None:
    """Guard on every red node below: the fixture is not the failure.

    If this node ever fails, the red set above is evidence of a broken fixture rather
    than of the defect, which is the Phase-2 risk the plan calls out by name.
    """
    graph = elaborated(COMBINED)

    assert graph.diagnostics == []
    assert graph.is_projectable
    assert len(graph.occurrences) == 3  # plant, comp_a, comp_b
    assert {node.display_path for node in graph.attrs.values()} == {
        NAMED_SOURCE,
        ENCLOSING_SIBLING,
        f"{COMBINED_PREFIX}__comp_b__aliased_length",
    }


def test_combined_alias_raw_target_is_the_named_source() -> None:
    """The typed-alias lane, asserted on the raw ``alias_target``.

    ``semantic_edges()`` omits alias targets, so this is the only place the alias lane's
    own edge is visible; consumers of the alias are a separate obligation below.
    """
    graph = elaborated(COMBINED)
    alias_node = attr(graph, f"{COMBINED_PREFIX}__comp_b__aliased_length")

    assert alias_node.is_alias
    assert alias_node.alias_target == NodeRef(attr(graph, NAMED_SOURCE).node_id)


def test_combined_alias_following_consumer_reaches_the_named_source() -> None:
    """Alias following stays caller-owned, so a consumer of the alias lands on the source."""
    graph = elaborated(COMBINED)
    consumer = calc(graph, f"{COMBINED_PREFIX}__comp_b__alias_calc")

    assert consumer.input_by_name("length_in") == NodeRef(attr(graph, NAMED_SOURCE).node_id)


def test_combined_computed_attribute_reaches_the_named_source() -> None:
    """The computed-expression lane — 76 of the corpus's bare sites run through it."""
    graph = elaborated(COMBINED)
    computed = calc(graph, f"{COMBINED_PREFIX}__comp_b__doubled_length")

    assert computed.is_computed
    assert list(computed.inputs.values()) == [NodeRef(attr(graph, NAMED_SOURCE).node_id)]


def test_combined_calculation_input_reaches_the_named_source() -> None:
    """The calculation-binding lane, the shape u6 isolates."""
    graph = elaborated(COMBINED)
    consumer = calc(graph, f"{COMBINED_PREFIX}__comp_b__area_calc")

    assert consumer.input_by_name("length_in") == NodeRef(attr(graph, NAMED_SOURCE).node_id)


def test_combined_constraint_actual_reaches_the_named_source() -> None:
    """The typed constraint-actual lane, through the same ``_resolve_bindings`` caller."""
    graph = elaborated(COMBINED)
    gate = constraint(graph, f"{COMBINED_PREFIX}__comp_b__bound_check")

    assert gate.input_by_name("length_in") == NodeRef(attr(graph, NAMED_SOURCE).node_id)


def test_combined_inline_predicate_reaches_the_named_source() -> None:
    """The asserted inline-predicate lane.

    The tracked corpus contains zero usage-owned direct references in an inline
    predicate, so this authored regression is the lane's sole evidence.
    """
    graph = elaborated(COMBINED)
    gate = constraint(graph, f"{COMBINED_PREFIX}__comp_b__inline_check")

    assert list(gate.inputs.values()) == [NodeRef(attr(graph, NAMED_SOURCE).node_id)]


def test_combined_direct_sum_term_is_scalar_and_reaches_the_named_source() -> None:
    """A direct term beneath ``sum()`` stays one edge.

    The caller passes ``plural=True`` here — ``aggregation_reference_ordinals`` is what
    records that it did. One-segment owner anchoring must not inherit that flag and fan
    the direct term out across occurrences.
    """
    graph = elaborated(COMBINED)
    summed = calc(graph, f"{COMBINED_PREFIX}__comp_b__summed_length")

    assert summed.aggregation_reference_ordinals == (0,)
    assert list(summed.inputs.values()) == [NodeRef(attr(graph, NAMED_SOURCE).node_id)]


def test_combined_named_source_reaches_every_and_only_its_consumers() -> None:
    """One modelled source occurrence, exactly one runtime source, all six consumers.

    This is the product obligation in one assertion: the six consumer ports that name
    ``comp_a::length`` reach it, and the enclosing sibling's node — the current wrong
    answer — is left with no consumer at all.
    """
    graph = elaborated(COMBINED)
    named = NodeRef(attr(graph, NAMED_SOURCE).node_id)
    enclosing = NodeRef(attr(graph, ENCLOSING_SIBLING).node_id)

    assert consumers_of(graph, named) == Counter(
        {
            calc(graph, f"{COMBINED_PREFIX}__comp_b__alias_calc").node_id: 1,
            calc(graph, f"{COMBINED_PREFIX}__comp_b__area_calc").node_id: 1,
            calc(graph, f"{COMBINED_PREFIX}__comp_b__doubled_length").node_id: 1,
            calc(graph, f"{COMBINED_PREFIX}__comp_b__summed_length").node_id: 1,
            constraint(graph, f"{COMBINED_PREFIX}__comp_b__bound_check").node_id: 1,
            constraint(graph, f"{COMBINED_PREFIX}__comp_b__inline_check").node_id: 1,
        }
    )
    assert consumers_of(graph, enclosing) == Counter()


# ---------------------------------------------------------------------------
# Controls — usage-owned self-reference, then definition-owned lineage misses
# ---------------------------------------------------------------------------


def test_u1_self_qualified_control_is_unchanged() -> None:
    """The qualifier names the consumer's own enclosing usage. Both routes agree."""
    graph = elaborated("u1_usage_qual_self")
    consumer = calc(graph, "U1UsageQualSelf__component__area_calc")

    assert consumer.input_by_name("length") == NodeRef(
        attr(graph, "U1UsageQualSelf__component__length").node_id
    )
    assert consumer.input_by_name("width") == NodeRef(
        attr(graph, "U1UsageQualSelf__component__width").node_id
    )
    assert graph.diagnostics == []


# These qualifiers name usages, but the leaf SysIDE resolves is still owned by
# the part definition because the usages add no redefinition.
def test_u2_definition_owned_descendants_refuse_for_each_consumer() -> None:
    """The usage qualifier does not make its definition-owned leaf usage-owned.

    Each area calculation sits above its nested ``component`` occurrence. Neither
    occurrence is on the consumer's lineage, so both references refuse rather than
    selecting the sole descendant below each plant.
    """
    graph = elaborated("u2_usage_qual_two_owner_occ")
    assert diagnostic_codes(graph) == Counter({ElaborationCode.SI_OCCURRENCE_MISSING: 2})
    for occurrence in ("plant_a", "plant_b"):
        consumer = calc(graph, f"U2UsageQualTwoOwnerOcc__{occurrence}__area_calc")
        assert bound_formal_names(consumer) == frozenset()


def test_u3_definition_owned_array_descendants_refuse_as_missing() -> None:
    """Array cardinality is irrelevant when neither occurrence is on the lineage."""
    graph = elaborated("u3_usage_qual_multi_occ")
    consumer = calc(graph, "U3UsageQualMultiOcc__plant__area_calc")

    assert diagnostic_codes(graph) == Counter({ElaborationCode.SI_OCCURRENCE_MISSING: 1})
    assert bound_formal_names(consumer) == frozenset()


def test_u3b_single_definition_owned_descendant_also_refuses() -> None:
    """One descendant is not an occurrence on the consumer's lineage."""
    graph = elaborated("u3b_usage_qual_single_occ")
    consumer = calc(graph, "U3BUsageQualSingleOcc__plant__area_calc")

    assert diagnostic_codes(graph) == Counter({ElaborationCode.SI_OCCURRENCE_MISSING: 1})
    assert bound_formal_names(consumer) == frozenset()


def test_definition_owned_alias_leaf_keeps_the_consumer_local_edge() -> None:
    """Owner guard: the alias names a ``PartDefinition``-owned leaf.

    The bare reference looks identical to the affected shape from the consumer's side.
    Only the owner's metatype separates them, which is why the branch guards on the
    metatype and not on the reference's form.
    """
    graph = elaborated("usage_owner_bare_alias_def_owned")
    consumer = calc(graph, "BareAliasDefinitionOwned__plant__comp_b__doubled")

    assert list(consumer.inputs.values()) == [
        NodeRef(attr(graph, "BareAliasDefinitionOwned__plant__comp_b__length").node_id)
    ]
    assert graph.diagnostics == []


def test_definition_owned_subset_leaf_keeps_the_consumer_local_edge() -> None:
    """The same guard reached through subsetting instead of aliasing."""
    graph = elaborated("usage_owner_bare_subset_def_owned")
    consumer = calc(graph, "BareSubsetSiblingUsage__plant__comp_b__doubled")

    assert list(consumer.inputs.values()) == [
        NodeRef(attr(graph, "BareSubsetSiblingUsage__plant__comp_b__length").node_id)
    ]
    assert graph.diagnostics == []


# ---------------------------------------------------------------------------
# Negative — a refused owner is final, never recovered positionally
# ---------------------------------------------------------------------------


def test_arrayed_exact_owner_refuses_rather_than_answering() -> None:
    """The exact owner has two occurrences, so scalar selection has no answer.

    Today the resolver silently returns the consumer's own ``comp_b.length``. After the
    repair it must raise the existing ambiguity diagnostic and leave the consumer
    unbound: an owner that cannot be selected is final, and consumer position is not a
    fallback authority.
    """
    graph = elaborated("usage_owner_bare_alias_arrayed")
    consumer = calc(graph, "BareAliasArrayedOwner__plant__comp_b__doubled")

    assert diagnostic_codes(graph) == Counter({ElaborationCode.SI_OCCURRENCE_AMBIGUOUS: 1})
    assert consumer.inputs == {}


# ---------------------------------------------------------------------------
# Identity stability — the repair may move an edge, never an identity
# ---------------------------------------------------------------------------

FAMILY = (
    COMBINED,
    "u1_usage_qual_self",
    "u2_usage_qual_two_owner_occ",
    "u3_usage_qual_multi_occ",
    "u3b_usage_qual_single_occ",
    "u4_usage_qual_pkg_sibling",
    "u5_usage_qual_named_sibling",
    "u6_usage_qual_crossnamed",
    "u7_both_spellings",
    "usage_owner_bare_alias",
    "usage_owner_bare_alias_arrayed",
    "usage_owner_bare_alias_def_owned",
    "usage_owner_bare_subset_def_owned",
)


@pytest.mark.parametrize("fixture", FAMILY)
def test_attribute_node_ids_stay_derived_from_occurrence_and_slot(fixture: str) -> None:
    """Node identity comes from (occurrence, feature slot) and from nothing else.

    The exact byte-level before/after comparison of these identities lives in the item's
    ledger (``verification/before.json``). What this node pins is the derivation itself,
    so a repair that reached identity construction fails here rather than in a diff.
    """
    graph = elaborated(fixture)

    assert all(
        node.node_id == NodeId(NodeKind.ATTRIBUTE, node.scope, node.slot_id)
        for node in graph.attrs.values()
    )


@pytest.mark.parametrize("fixture", FAMILY)
def test_occurrence_records_stay_anchored_to_their_containment_slot(fixture: str) -> None:
    """Every occurrence is reached through its containment-slot family.

    Exact-owner selection enters that family; it does not replace it. A record whose last
    step disagrees with its own containment slot would mean the occurrence bridge itself
    moved, which this item's design forbids.
    """
    graph = elaborated(fixture)

    assert all(
        record.occurrence_id.steps[-1].containment_slot == record.containment_slot
        for record in graph.occurrences.values()
    )
    assert all(
        record.parent_id is None or record.parent_id in graph.occurrences
        for record in graph.occurrences.values()
    )
