"""Real SysIDE coverage for the closed containment-address domain."""

from __future__ import annotations

from collections.abc import Collection, Iterator
from typing import Any

import pytest
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration import (
    ElaborationCode,
    ElaborationDiagnosticError,
    NodeRef,
)
from sysml_codegen.elaboration.identity import declaration_id_for
from sysml_codegen.elaboration.occurrence import (
    build_containment_address,
    build_feature_slot_index,
    build_occurrence_index,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.raw_elaboration import elaborate

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "occurrence_domain_derivation"


def _loaded() -> SysMLDataExtractor:
    extractor = SysMLDataExtractor([FIXTURE])
    assert extractor.load_models()
    return extractor


def _by_qn(model: Any, kind: str, qualified_name: str) -> Any:
    return next(
        element
        for element in SysideAdapter.elements_of_type(model, kind)
        if str(getattr(element, "qualified_name", None)) == qualified_name
    )


def _lenient_graph():
    return elaborate_model_paths([FIXTURE], strict=False)


def _sole_target_path(graph, calculation_path: str) -> str:
    calculation = graph.calc_by_display_path(calculation_path)
    [edge] = calculation.inputs.values()
    assert isinstance(edge, NodeRef)
    return graph.attrs[edge.target].display_path


def test_real_fixture_instantiates_same_nested_repeated_and_package_domains() -> None:
    graph = _lenient_graph()

    assert _sole_target_path(
        graph,
        "OccurrenceDomainDerivation__direct_container__sensor__scale_reading",
    ) == "OccurrenceDomainDerivation__direct_container__sensor__reading"
    assert _sole_target_path(
        graph,
        "OccurrenceDomainDerivation__direct_container__explicit_sensor_reading",
    ) == "OccurrenceDomainDerivation__direct_container__sensor__reading"
    assert _sole_target_path(
        graph,
        "OccurrenceDomainDerivation__explicit_nested_reader",
    ) == "OccurrenceDomainDerivation__package_nested__nested_sensor__reading"
    assert _sole_target_path(
        graph,
        "OccurrenceDomainDerivation__package_scale",
    ) == "OccurrenceDomainDerivation__package_source"

    repeated_targets = {
        _sole_target_path(
            graph,
            f"OccurrenceDomainDerivation__repeated_container[{index}]"
            "__explicit_sensor_reading",
        )
        for index in (0, 1)
    }
    assert repeated_targets == {
        f"OccurrenceDomainDerivation__repeated_container[{index}]__sensor__reading"
        for index in (0, 1)
    }


def test_explicit_package_sibling_resolves_from_the_exact_package_anchor() -> None:
    graph = elaborate_model_paths([FIXTURES_DIR / "u4_usage_qual_pkg_sibling"])

    assert _sole_target_path(
        graph,
        "U4UsageQualPkgSibling__plant__area_calc",
    ) == "U4UsageQualPkgSibling__shared_component__length"


def test_real_fixture_has_one_redefinition_slot_and_effective_specialized_usage() -> None:
    extractor = _loaded()
    model = extractor.model
    slots = build_feature_slot_index(model)
    occurrences = build_occurrence_index(model, slots)
    base = _by_qn(model, "PartUsage", "OccurrenceDomainDerivation::Container::sensor")
    redefining = _by_qn(
        model,
        "PartUsage",
        "OccurrenceDomainDerivation::VariantContainer::sensor",
    )

    assert slots.slot_of(declaration_id_for(base)) == slots.slot_of(
        declaration_id_for(redefining)
    )
    [variant] = [
        occurrence
        for occurrence in occurrences.occurrences_for_declaration(
            declaration_id_for(redefining)
        )
        if occurrence.display_path.endswith("__variant_container__sensor")
    ]
    assert variant.effective_usage_id == declaration_id_for(redefining)


def test_real_repeated_root_is_plural_and_scalar_resolution_refuses_ambiguity() -> None:
    extractor = _loaded()
    model = extractor.model
    slots = build_feature_slot_index(model)
    occurrences = build_occurrence_index(model, slots)
    repeated = _by_qn(
        model,
        "PartUsage",
        "OccurrenceDomainDerivation::repeated_container",
    )
    package_source = _by_qn(
        model,
        "AttributeUsage",
        "OccurrenceDomainDerivation::package_source",
    )
    address = build_containment_address(repeated, slots)
    package_address = build_containment_address(package_source, slots)
    [package_scope] = occurrences.consumer_domain(
        occurrences.occurrences_for_declaration(declaration_id_for(repeated))[0].occurrence_id
    ).scopes_for("package", address.anchor_id)
    domain = occurrences.consumer_domain(package_scope)

    assert [
        occurrence.steps[-1].occurrence_index
        for occurrence in occurrences.resolve_address(address, domain, plural=True)
    ] == [0, 1]
    with pytest.raises(Exception, match="SI_OCCURRENCE_AMBIGUOUS"):
        occurrences.resolve_address(address, domain, plural=False)
    assert package_address.anchor_kind == "package"
    assert package_address.steps == ()


def test_definition_owned_unrelated_target_refuses_strict_and_stays_unbound_lenient() -> None:
    with pytest.raises(ElaborationDiagnosticError) as excinfo:
        elaborate_model_paths([FIXTURE])
    [diagnostic] = excinfo.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_OCCURRENCE_MISSING
    assert diagnostic.consumer_display == "OccurrenceDomainDerivation__definition_only_reader"
    assert diagnostic.reference == "Sensor::reading"
    assert diagnostic.source_file == "root-0/model.sysml"
    assert diagnostic.source_line == 52
    assert diagnostic.detail.startswith("consumer domain has no part_definition anchor")
    rendered = str(excinfo.value)
    assert "Sensor::reading" in rendered
    assert "root-0/model.sysml:52" in rendered
    assert rendered.count("SI_OCCURRENCE_MISSING") == 1

    graph = _lenient_graph()
    assert graph.calc_by_display_path(
        "OccurrenceDomainDerivation__definition_only_reader"
    ).inputs == {}


def test_reversed_parser_declaration_order_keeps_occurrences_and_edges(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    extractor = _loaded()
    baseline = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=False,
    )
    original = SysideAdapter.elements_of_type

    def reversed_elements(
        cls: type[SysideAdapter],
        model: Any,
        type_name: str,
        *,
        include_subtypes: bool = False,
        exclude: Collection[str] = (),
    ) -> Iterator[Any]:
        del cls
        return iter(
            reversed(
                tuple(
                    original(
                        model,
                        type_name,
                        include_subtypes=include_subtypes,
                        exclude=exclude,
                    )
                )
            )
        )

    monkeypatch.setattr(SysideAdapter, "elements_of_type", classmethod(reversed_elements))
    reordered = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=False,
    )

    assert set(reordered.occurrences) == set(baseline.occurrences)
    assert reordered.semantic_edges() == baseline.semantic_edges()
