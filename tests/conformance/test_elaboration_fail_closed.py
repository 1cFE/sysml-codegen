"""Fail-closed behavior for the exact-ID elaborator."""

from __future__ import annotations

from collections import Counter

import pytest

from sysml_codegen.elaboration import (
    ElaborationCode,
    ElaborationDiagnosticError,
    ElaborationError,
    InstanceGraph,
    elaborate,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.source_evidence import ReadinessCode
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import calc

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


def test_non_unique_definition_reference_has_named_ambiguity() -> None:
    graph = _elaborate_lenient("source_identity_occurrence_ambiguity")

    assert Counter(diagnostic.code for diagnostic in graph.diagnostics) == Counter(
        {ElaborationCode.SI_OCCURRENCE_AMBIGUOUS: 2}
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
        {ElaborationCode.SI_OCCURRENCE_AMBIGUOUS: 2}
    )


def test_customer_fixture_lenient_diagnostics_are_accounted_for() -> None:
    graph = _elaborate_lenient("fusion_tea")

    codes = Counter(diagnostic.code for diagnostic in graph.diagnostics)
    assert codes == Counter(
        {
            ReadinessCode.SI_SELF_BINDING: 15,
            ElaborationCode.SI_OCCURRENCE_MISSING: 7,
        }
    )
    missing = [
        diagnostic
        for diagnostic in graph.diagnostics
        if diagnostic.code is ElaborationCode.SI_OCCURRENCE_MISSING
    ]
    assert Counter(diagnostic.param_name for diagnostic in missing) == Counter(
        {"scope": 6, "wall_type": 1}
    )


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
