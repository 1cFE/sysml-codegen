"""Real SysIDE coverage for contextual calculation-output producers."""

from __future__ import annotations

import pytest

from sysml_codegen.elaboration import (
    ElaborationCode,
    ElaborationDiagnosticError,
    ProducerRef,
)
from sysml_codegen.elaboration.elaborate import (
    _ExactElaborator,
    _ReferenceResolutionError,
)
from sysml_codegen.elaboration.identity import ResolvedSemanticReference
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "occurrence_calc_domain_derivation"


def _elaborator() -> tuple[_ExactElaborator, object]:
    extractor = SysMLDataExtractor([FIXTURE])
    assert extractor.load_models()
    elaborator = _ExactElaborator(
        extractor.model,
        extractor.extract_calculation_definitions(),
        strict=True,
    )
    return elaborator, elaborator.run()


def _sole_input_target(graph, path: str):
    calculation = graph.calc_by_display_path(path)
    [edge] = calculation.inputs.values()
    assert isinstance(edge, ProducerRef)
    return edge.target


def test_exact_producer_bucket_keeps_usage_scope_node_and_result_identity() -> None:
    elaborator, graph = _elaborator()
    first = graph.calc_by_display_path(
        "OccurrenceCalcDomainDerivation__cell[0]__first_producer"
    )
    [(output_declaration, _port)] = first.outputs.items()
    records = elaborator._calculation_output_producers[output_declaration]

    assert len(records) == 5
    assert len(
        {
            (
                record.calculation_usage_id,
                record.scope,
                record.node_id,
                record.port_id,
                record.effective_usage_id,
            )
            for record in records
        }
    ) == 5
    assert {record.node_id for record in records} == {
        graph.calc_by_display_path(path).node_id
        for path in (
            "OccurrenceCalcDomainDerivation__cell[0]__first_producer",
            "OccurrenceCalcDomainDerivation__cell[0]__second_producer",
            "OccurrenceCalcDomainDerivation__cell[1]__first_producer",
            "OccurrenceCalcDomainDerivation__cell[1]__second_producer",
            "OccurrenceCalcDomainDerivation__package_producer",
        )
    }
    assert all(record.port_id.output == output_declaration for record in records)


@pytest.mark.parametrize("index", [0, 1])
def test_explicit_sibling_consumer_uses_first_producer_in_its_own_repeat(index: int) -> None:
    graph = elaborate_model_paths([FIXTURE])
    prefix = f"OccurrenceCalcDomainDerivation__cell[{index}]"
    target = _sole_input_target(graph, f"{prefix}__explicit_consumer")
    first = graph.calc_by_display_path(f"{prefix}__first_producer")
    second = graph.calc_by_display_path(f"{prefix}__second_producer")

    assert target in first.outputs.values()
    assert target not in second.outputs.values()
    other = graph.calc_by_display_path(
        f"OccurrenceCalcDomainDerivation__cell[{1 - index}]__first_producer"
    )
    assert target not in other.outputs.values()


def test_package_consumer_uses_the_exact_package_producer() -> None:
    graph = elaborate_model_paths([FIXTURE])
    target = _sole_input_target(graph, "OccurrenceCalcDomainDerivation__package_consumer")
    package_producer = graph.calc_by_display_path(
        "OccurrenceCalcDomainDerivation__package_producer"
    )

    assert target in package_producer.outputs.values()
    assert all(
        target not in calculation.outputs.values()
        for calculation in graph.calcs.values()
        if calculation is not package_producer
    )


def test_consumer_result_ports_are_not_mistaken_for_producer_results() -> None:
    elaborator, graph = _elaborator()
    consumer = graph.calc_by_display_path(
        "OccurrenceCalcDomainDerivation__cell[0]__explicit_consumer"
    )
    [consumer_output] = consumer.outputs
    records = elaborator._calculation_output_producers[consumer_output]

    assert len(records) == 3
    assert {record.node_id for record in records} == {
        graph.calc_by_display_path(path).node_id
        for path in (
            "OccurrenceCalcDomainDerivation__cell[0]__explicit_consumer",
            "OccurrenceCalcDomainDerivation__cell[1]__explicit_consumer",
            "OccurrenceCalcDomainDerivation__package_consumer",
        )
    }


def test_bare_sibling_output_keeps_both_producers_and_refuses_scalar_election() -> None:
    extractor = SysMLDataExtractor([FIXTURES_DIR / "source_identity_mixed_consumers"])
    assert extractor.load_models()
    elaborator = _ExactElaborator(
        extractor.model,
        extractor.extract_calculation_definitions(),
        strict=False,
    )
    graph = elaborator.run()
    calc_a = graph.calc_by_display_path(
        "source_identity_mixed_consumers__twin_bay__calc_a"
    )
    calc_b = graph.calc_by_display_path(
        "source_identity_mixed_consumers__twin_bay__calc_b"
    )
    [output_declaration] = calc_a.outputs
    reference = ResolvedSemanticReference(
        root_id=output_declaration,
        segment_ids=(output_declaration,),
        leaf_id=output_declaration,
    )

    with pytest.raises(_ReferenceResolutionError) as caught:
        elaborator._resolve_calculation_output(
            reference,
            calc_a.scope,
            usage_filter=None,
            plural=False,
            no_prefix=True,
        )

    assert calc_a.scope == calc_b.scope
    assert caught.value.code is ElaborationCode.SI_OCCURRENCE_AMBIGUOUS
    assert "2 producers" in caught.value.detail


def test_unrelated_globally_sole_output_refuses_instead_of_crossing_domains() -> None:
    fixture = FIXTURES_DIR / "deep_cross_scope_probe"
    extractor = SysMLDataExtractor([fixture])
    assert extractor.load_models()
    elaborator = _ExactElaborator(
        extractor.model,
        extractor.extract_calculation_definitions(),
        strict=False,
    )
    graph = elaborator.run()
    producer = graph.calc_by_display_path(
        "DeepCrossScopeDesign__measurement_system__station__array__sensor__core"
    )
    [output_declaration] = producer.outputs
    assert len(elaborator._calculation_output_producers[output_declaration]) == 1
    [diagnostic] = graph.diagnostics
    assert diagnostic.code is ElaborationCode.SI_OCCURRENCE_MISSING
    assert diagnostic.consumer_display.endswith("__analyzer__ref_analysis")
    assert diagnostic.detail == (
        f"exact output {output_declaration.to_wire()} has no producer in the consumer domain"
    )

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborate_model_paths([fixture])
    [public] = caught.value.diagnostics
    assert public.code is diagnostic.code
    assert public.detail == diagnostic.detail
    assert public.reference == (
        "measurement_system::station::array::sensor::core::metric_value"
    )
    assert public.source_file == "root-0/design.sysml"
    assert public.source_line == 77
    rendered = str(caught.value)
    assert public.reference in rendered
    assert "root-0/design.sysml:77" in rendered
    assert rendered.count("SI_OCCURRENCE_MISSING") == 1
