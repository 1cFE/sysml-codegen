"""The one modeled-containment address and its consumer-domain instantiation."""

from __future__ import annotations

from typing import Any

import pytest
from agentic_mbse.sysml.reference_use import ExactSemanticPath, resolved_target_fact
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration.diagnostics import ElaborationCode
from sysml_codegen.elaboration.elaborate import (
    _ExactElaborator,
    _ReferenceResolutionError,
)
from sysml_codegen.elaboration.expression_evidence import (
    build_expression_evidence_inventory,
)
from sysml_codegen.elaboration.identity import (
    ResolvedSemanticReference,
    declaration_id_for,
)
from sysml_codegen.elaboration.occurrence import (
    build_containment_address,
    build_feature_slot_index,
    build_occurrence_index,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


def _load(name: str) -> Any:
    model, diagnostics = SysideAdapter.load_model([FIXTURES_DIR / name])
    errors = [
        diagnostic for diagnostic in diagnostics.all if str(diagnostic.severity).endswith("Error")
    ]
    assert not errors, errors
    return model


def _by_qn(model: Any, type_name: str, qualified_name: str) -> Any:
    return next(
        element
        for element in SysideAdapter.elements_of_type(model, type_name)
        if str(getattr(element, "qualified_name", None)) == qualified_name
    )


def test_sibling_address_reuses_the_consumers_exact_outer_occurrence() -> None:
    model = _load("u7_both_spellings")
    slots = build_feature_slot_index(model)
    occurrences = build_occurrence_index(model, slots)
    consumer_owner = _by_qn(model, "PartUsage", "U7BothSpellings::plant")
    named_sibling = _by_qn(model, "PartUsage", "U7BothSpellings::Plant::comp_a")
    consumer_scope = occurrences.occurrences_for_declaration(
        declaration_id_for(consumer_owner)
    )[0].occurrence_id

    address = build_containment_address(named_sibling, slots)
    resolved = occurrences.resolve_address(
        address,
        occurrences.consumer_domain(consumer_scope),
        plural=False,
    )

    assert [occurrences.occurrence(item).effective_usage_id for item in resolved] == [
        declaration_id_for(named_sibling)
    ]
    assert occurrences.occurrence(resolved[0]).parent_id == consumer_scope


def test_arrayed_address_retains_plural_cardinality_and_refuses_scalar() -> None:
    model = _load("elab_native_plural_scope")
    slots = build_feature_slot_index(model)
    occurrences = build_occurrence_index(model, slots)
    selected = _by_qn(model, "PartUsage", "ElabNativePluralScope::plant::selected")
    leaf = _by_qn(
        model,
        "PartUsage",
        "ElabNativePluralScope::SpecializedContainer::leaf",
    )
    selected_scope = occurrences.occurrences_for_declaration(
        declaration_id_for(selected)
    )[0].occurrence_id
    address = build_containment_address(leaf, slots)
    domain = occurrences.consumer_domain(selected_scope)

    assert [
        item.steps[-1].occurrence_index
        for item in occurrences.resolve_address(address, domain, plural=True)
    ] == [0, 1]
    with pytest.raises(Exception, match="SI_OCCURRENCE_AMBIGUOUS"):
        occurrences.resolve_address(address, domain, plural=False)


def test_calculation_output_index_filters_exact_usage_and_refuses_bare_tie() -> None:
    extractor = SysMLDataExtractor([FIXTURES_DIR / "source_identity_mixed_consumers"])
    assert extractor.load_models()
    elaborator = _ExactElaborator(
        extractor.model,
        extractor.extract_calculation_definitions(),
        inventory=build_expression_evidence_inventory(extractor.model),
        strict=False,
    )
    graph = elaborator.run()
    calc_a = next(node for node in graph.calcs.values() if node.display_path.endswith("__calc_a"))
    calc_b = next(node for node in graph.calcs.values() if node.display_path.endswith("__calc_b"))
    assert calc_a.scope == calc_b.scope
    [(output_id, expected_port)] = calc_a.outputs.items()
    assert output_id in calc_b.outputs

    explicit = ResolvedSemanticReference(
        root_id=calc_a.declaration_id,
        segment_ids=(calc_a.declaration_id, output_id),
        leaf_id=output_id,
    )
    assert elaborator._resolve_calculation_output(
        explicit,
        calc_a.scope,
        usage_filter=calc_a.declaration_id,
        plural=False,
        no_prefix=False,
    )[0].target == expected_port

    bare = ResolvedSemanticReference(
        root_id=output_id,
        segment_ids=(output_id,),
        leaf_id=output_id,
    )
    with pytest.raises(_ReferenceResolutionError) as excinfo:
        elaborator._resolve_calculation_output(
            bare,
            calc_a.scope,
            usage_filter=None,
            plural=False,
            no_prefix=True,
        )
    assert excinfo.value.code is ElaborationCode.SI_OCCURRENCE_AMBIGUOUS
    assert "2 producers" in excinfo.value.detail


def test_no_prefix_nested_package_target_refuses_but_explicit_prefix_resolves() -> None:
    extractor = SysMLDataExtractor([FIXTURES_DIR / "u4_usage_qual_pkg_sibling"])
    assert extractor.load_models()
    elaborator = _ExactElaborator(
        extractor.model,
        extractor.extract_calculation_definitions(),
        inventory=build_expression_evidence_inventory(extractor.model),
        strict=False,
    )
    graph = elaborator.run()
    consumer = next(
        node for node in graph.calcs.values() if node.display_path.endswith("__area_calc")
    )
    leaf = _by_qn(
        extractor.model,
        "ReferenceUsage",
        "U4UsageQualPkgSibling::shared_component::length",
    )
    target = resolved_target_fact(leaf)
    assert target is not None
    fact = ExactSemanticPath(
        root=target,
        segments=(target,),
        leaf=target,
        resolved_member_names=(),
    )

    with pytest.raises(_ReferenceResolutionError) as excinfo:
        elaborator._resolve_semantic_reference(
            fact,
            consumer.scope,
            plural=False,
            no_prefix=True,
        )
    assert excinfo.value.code is ElaborationCode.SI_OCCURRENCE_MISSING
    assert "modeled containment prefix" in excinfo.value.detail
    assert consumer.inputs
