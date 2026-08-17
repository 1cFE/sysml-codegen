"""Fail-closed behavior for the exact-ID elaborator."""

from __future__ import annotations

from collections import Counter

import pytest
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration import (
    ElaborationCode,
    ElaborationDiagnosticError,
    ElaborationError,
    InstanceGraph,
)
from sysml_codegen.elaboration.identity import declaration_id_for
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.source_evidence import ReadinessCode
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import calc, every_alias_target, every_typed_edge
from tests.helpers.raw_elaboration import elaborate

pytestmark = requires_license


def _load(name: str) -> SysMLDataExtractor:
    extractor = SysMLDataExtractor([FIXTURES_DIR / name])
    assert extractor.load_models(), f"fixture {name} failed to load"
    return extractor


def _elaborate_lenient(name: str) -> InstanceGraph:
    extractor = _load(name)
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=False,
    )


def _elaborate_strict(name: str) -> InstanceGraph:
    extractor = _load(name)
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )


def test_invocation_rhs_is_diagnostic_not_an_unbound_candidate() -> None:
    graph = _elaborate_lenient("invocation_binding_probe")
    consumer = calc(graph, "InvocationBindingDesign__probe__c")

    assert Counter(diagnostic.code for diagnostic in graph.diagnostics) == Counter(
        {ReadinessCode.SI_EXPRESSION_SOURCE_UNSUPPORTED: 1}
    )
    assert "x" in consumer.input_names.values()
    assert all(
        not (consumer.input_names[port] == "x" and port in consumer.inputs)
        for port in consumer.input_names
    )
    assert consumer.unbound_formals == ()


def test_indexed_source_has_its_distinct_readiness_diagnostic() -> None:
    extractor = _load("source_identity_indexed_source")

    with pytest.raises(ElaborationError) as excinfo:
        elaborate(
            extractor.model,
            extractor.extract_calculation_definitions(),
            validation_diagnostics=extractor.diagnostics.validation,
        )

    assert Counter(finding.code for finding in excinfo.value.findings) == Counter(
        {ReadinessCode.SI_INDEXED_SOURCE_UNSUPPORTED: 2}
    )


def test_definition_reference_refusals_keep_their_distinct_codes() -> None:
    graph = _elaborate_lenient("source_identity_occurrence_ambiguity")

    assert Counter(diagnostic.code for diagnostic in graph.diagnostics) == Counter(
        {
            ElaborationCode.SI_OCCURRENCE_MISSING: 1,
            ElaborationCode.SI_OCCURRENCE_AMBIGUOUS: 1,
        }
    )
    assert {diagnostic.param_name for diagnostic in graph.diagnostics} == {"value_in"}
    assert all("amb_" in diagnostic.consumer_display for diagnostic in graph.diagnostics)


def test_strict_mode_rejects_blocking_occurrence_diagnostics() -> None:
    extractor = _load("source_identity_occurrence_ambiguity")

    with pytest.raises(ElaborationDiagnosticError) as excinfo:
        elaborate(
            extractor.model,
            extractor.extract_calculation_definitions(),
            validation_diagnostics=extractor.diagnostics.validation,
        )

    assert Counter(diagnostic.code for diagnostic in excinfo.value.diagnostics) == Counter(
        {
            ElaborationCode.SI_OCCURRENCE_MISSING: 1,
            ElaborationCode.SI_OCCURRENCE_AMBIGUOUS: 1,
        }
    )


def test_customer_fixture_lenient_diagnostics_are_accounted_for() -> None:
    """The customer model now elaborates with an empty diagnostic set.

    It used to carry 15 ``SI_SELF_BINDING`` plus 7 ``SI_OCCURRENCE_MISSING``
    (``scope`` 6, ``wall_type`` 1). Slice 3D closed both: the fifteen bindings
    were migrated in place to the D-5 ``<formal>_in`` form, and the seven were
    enumeration-value redefinitions (``:>> scope = 'CAS Scope'::shared;``) that
    the elaborator was sending down the alias walk instead of reading as
    literals.

    Empty on its own would go green on an empty graph, so the counts below pin
    what the clean elaboration actually produced.
    """
    graph = _elaborate_lenient("fusion_tea")

    assert Counter(diagnostic.code for diagnostic in graph.diagnostics) == Counter()
    assert len(graph.calcs) == 7
    assert len(graph.constraints) == 1
    assert graph.attrs

    # The seven attributes that used to be the seven diagnostics, one for one,
    # now carry a resolved enumeration literal keyed by qualified name.
    assert {
        node.display_path: node.value
        for node in graph.attrs.values()
        if isinstance(node.value, str)
    } == {
        "hif_driver__hif_driver_instance__scope": (
            "economic_parameter::'CAS Scope'::ife_divergent"
        ),
        "hif_plant_pkg__hif_plant__driver__scope": (
            "economic_parameter::'CAS Scope'::ife_divergent"
        ),
        "hif_plant_pkg__hif_plant__target_factory__scope": (
            "economic_parameter::'CAS Scope'::ife_divergent"
        ),
        "hif_plant_pkg__hif_plant__chamber__blanket__scope": (
            "economic_parameter::'CAS Scope'::shared"
        ),
        "hif_plant_pkg__hif_plant__chamber__shield__scope": (
            "economic_parameter::'CAS Scope'::shared"
        ),
        "hif_plant_pkg__hif_plant__chamber__structure__scope": (
            "economic_parameter::'CAS Scope'::shared"
        ),
        "hif_plant_pkg__hif_plant__chamber__wall_type": (
            "ife_subsystems::'Wall Type'::liquid_wall"
        ),
    }


def test_alias_cycle_and_unsupported_formula_are_blocking_diagnostics() -> None:
    graph = _elaborate_lenient("elab_fail_closed_probe")

    codes = Counter(diagnostic.code for diagnostic in graph.diagnostics)
    assert codes == Counter(
        {
            ElaborationCode.SI_ALIAS_CYCLE: 2,
            ReadinessCode.SI_EXPRESSION_SOURCE_UNSUPPORTED: 1,
        }
    )
    assert not graph.is_projectable
    assert all(node.alias_target is None for node in graph.attrs.values() if node.is_alias)


def test_standard_sum_is_classified_by_exact_declaration_id() -> None:
    graph = _elaborate_lenient("source_identity_mixed_consumers")
    bank_total = calc(graph, "source_identity_mixed_consumers__bank__bank_total")
    assert len(bank_total.inputs) == 3
    assert graph.diagnostics == []


#: Owner-anchoring fixtures that elaborate cleanly, so a strict/lenient difference
#: here could only come from reference resolution — no readiness finding intervenes.
OWNER_ANCHORING_PARITY = (
    "usage_owned_reference_consumers",
    "u4_usage_qual_pkg_sibling",
    "u5_usage_qual_named_sibling",
    "u6_usage_qual_crossnamed",
    "u7_both_spellings",
    "usage_owner_bare_alias",
)


@pytest.mark.parametrize("fixture", OWNER_ANCHORING_PARITY)
def test_owner_anchoring_resolves_identically_in_strict_and_lenient(fixture: str) -> None:
    """Both modes run the same reference resolution, so the graphs are equal by value.

    Equality of the whole graph covers the typed edges *and* the raw alias targets that
    ``semantic_edges()`` leaves out. The empty diagnostic set is asserted too, because
    two graphs that both failed the same way would also compare equal.
    """
    lenient = _elaborate_lenient(fixture)
    strict = _elaborate_strict(fixture)

    assert lenient.diagnostics == []
    assert every_typed_edge(strict) == every_typed_edge(lenient)
    assert every_alias_target(strict) == every_alias_target(lenient)
    assert strict == lenient


def test_ambiguous_exact_owner_is_lenient_diagnostic_and_strict_refusal() -> None:
    """The arrayed-owner negative: same finding, one mode reports it, one refuses.

    Scalar owner selection cannot choose between an arrayed owner's two occurrences,
    and there is no positional route left to fall back to — so the consumer stays
    unbound rather than silently binding the enclosing occurrence.

    The whole diagnostic is pinned, not its code: the consumer it is attributed to, the
    parameter it names, and the detail that says why. A code-only assertion would stay
    green if the finding moved to another consumer or lost its explanation.
    """
    lenient = _elaborate_lenient("usage_owner_bare_alias_arrayed")
    consumer = calc(lenient, "BareAliasArrayedOwner__plant__comp_b__doubled")

    [diagnostic] = lenient.diagnostics
    assert diagnostic.code == ElaborationCode.SI_OCCURRENCE_AMBIGUOUS
    assert diagnostic.consumer == consumer.node_id
    assert diagnostic.param_name is None
    assert diagnostic.detail == "consumer context contains 2 candidate occurrences"
    assert consumer.inputs == {}

    with pytest.raises(ElaborationDiagnosticError) as excinfo:
        _elaborate_strict("usage_owner_bare_alias_arrayed")

    assert list(excinfo.value.diagnostics) == lenient.diagnostics


def _declaration_wire(model: object, type_name: str, qualified_name: str) -> str:
    """The exact declaration wire of one named element, located by name and asserted by ID."""
    for element in SysideAdapter.elements_of_type(model, type_name, include_subtypes=True):
        if str(getattr(element, "qualified_name", None)) == qualified_name:
            return declaration_id_for(element).to_wire()
    raise AssertionError(f"no {type_name} named {qualified_name!r}")


def test_selected_owner_without_a_leaf_target_refuses_by_name() -> None:
    """An authored reference to a `PartUsage`-owned calculation usage, not to its output.

    `comp_a::twice` resolves to the exact `twice` declaration, and `comp_a` is a live
    `PartUsage`, so exact-owner anchoring selects `comp_a`'s occurrence. That occurrence
    carries an attribute and a calculation node, but no attribute or computed target for
    a calculation-usage leaf — the last step of the owner route has nothing to return.

    This is the reachable authored shape for that refusal. It refuses rather than picking
    one of `twice`'s outputs on the author's behalf, and the detail names the exact owner
    and leaf declarations so the reader can see which two the resolver held.
    """
    extractor = _load("usage_owner_calc_usage_leaf")
    graph = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=False,
    )
    consumer = calc(graph, "CalcUsageLeafOwner__plant__comp_b__doubled")
    owner = _declaration_wire(extractor.model, "PartUsage", "CalcUsageLeafOwner::Plant::comp_a")
    leaf = _declaration_wire(
        extractor.model, "CalculationUsage", "CalcUsageLeafOwner::Plant::comp_a::twice"
    )

    [diagnostic] = graph.diagnostics
    assert diagnostic.code == ElaborationCode.SI_OCCURRENCE_MISSING
    assert diagnostic.consumer == consumer.node_id
    assert diagnostic.param_name is None
    assert diagnostic.detail == (
        f"exact owner {owner} has no target for leaf {leaf} at its selected occurrence"
    )
    assert consumer.inputs == {}


def test_strict_readiness_halt_precedes_graph_diagnostic_rejection() -> None:
    """The two strict exits are distinct, and readiness is the earlier one.

    ``_finish_readiness`` raises ``ElaborationError`` before ``graph.validate()`` ever
    runs, so a readiness fixture never reaches the ``ElaborationDiagnosticError`` path
    the owner-resolution controls above use. The two error types are unrelated classes,
    which is what makes this distinguishable rather than a matter of message text.
    """
    assert not issubclass(ElaborationDiagnosticError, ElaborationError)

    with pytest.raises(ElaborationError) as excinfo:
        _elaborate_strict("source_identity_indexed_source")

    assert Counter(finding.code for finding in excinfo.value.findings) == Counter(
        {ReadinessCode.SI_INDEXED_SOURCE_UNSUPPORTED: 2}
    )
    lenient = _elaborate_lenient("source_identity_indexed_source")
    assert Counter(diagnostic.code for diagnostic in lenient.diagnostics) == Counter(
        {ReadinessCode.SI_INDEXED_SOURCE_UNSUPPORTED: 2}
    )
