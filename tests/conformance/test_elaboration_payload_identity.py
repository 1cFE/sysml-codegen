"""Exact calculation-payload attachment for the internal elaborator route."""

from __future__ import annotations

import importlib
from dataclasses import replace
from uuid import UUID

import pytest
from agentic_mbse.sysml.executable_profile import Eligibility
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration import (
    DeclarationId,
    ElaborationCode,
    ElaborationDiagnosticError,
    InstanceGraph,
    ProjectionError,
    project,
)
from sysml_codegen.elaboration.identity import declaration_id_for
from sysml_codegen.extraction import expression_compiler
from sysml_codegen.extraction.data_models import CalculationDefinitionData
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.snapshot.instance_graph import (
    decode_instance_graph,
    encode_instance_graph,
)
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.elaboration_graph import calc
from tests.helpers.expression_evidence import calculation_dependencies
from tests.helpers.raw_elaboration import elaborate

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "elab_payload_identity"
SOURCE_KEY_FIXTURE = FIXTURES_DIR / "constraint_shared_polarity"


@pytest.fixture(scope="module")
def extracted() -> tuple[SysMLDataExtractor, list[CalculationDefinitionData]]:
    extractor = SysMLDataExtractor([FIXTURE])
    assert extractor.load_models()
    return extractor, extractor.extract_calculation_definitions()


def _by_package(
    calc_defs: list[CalculationDefinitionData], package: str
) -> CalculationDefinitionData:
    return next(item for item in calc_defs if item.qualified_name.startswith(f"{package}::"))


def _elaborate(
    extractor: SysMLDataExtractor,
    calc_defs: list[CalculationDefinitionData],
    *,
    strict: bool = False,
) -> InstanceGraph:
    assert extractor.diagnostics is not None
    return elaborate(
        extractor.model,
        calc_defs,
        validation_diagnostics=extractor.diagnostics.validation,
        strict=strict,
    )


def test_live_extraction_carries_total_calc_declaration_identity(
    extracted: tuple[SysMLDataExtractor, list[CalculationDefinitionData]],
) -> None:
    _extractor, calc_defs = extracted
    assert len(calc_defs) == 2
    for calc_def in calc_defs:
        assert isinstance(calc_def.element_id, UUID)
        assert calc_def.element_id.version == 5
        members = calc_def.input_attributes + calc_def.output_attributes
        assert members
        assert all(isinstance(member.element_id, UUID) for member in members)
        assert all(member.element_id.version == 5 for member in members)
        assert {member.element_id for member in members} <= calc_def.all_member_ids
        assert set(calc_def.member_names_by_id) == calc_def.all_member_ids
        assert set(calc_def.output_expression_asts_by_id) == {
            member.element_id for member in calc_def.output_attributes
        }


def test_exact_compiler_keys_definition_outputs_and_dependencies_by_uuid(
    extracted: tuple[SysMLDataExtractor, list[CalculationDefinitionData]],
) -> None:
    extractor, calc_defs = extracted
    dependencies = calculation_dependencies(extractor.model)
    for calc_def in calc_defs:
        result = expression_compiler.compile_calc_def_exact(calc_def, dependencies)
        assert result.definition_id == calc_def.element_id
        assert result.declared_output_ids == tuple(
            member.element_id for member in calc_def.output_attributes
        )
        output = next(
            item for item in result.output_results if not item.is_undeclared_intermediate
        )
        assert output.output_id == calc_def.output_attributes[0].element_id
        if calc_def.qualified_name.startswith("PayloadIdentityA::"):
            intermediate = next(
                item for item in result.output_results if item.is_undeclared_intermediate
            )
            assert intermediate.input_ids == (calc_def.input_attributes[0].element_id,)
            assert output.input_ids == ()
            assert output.dependency_ids == (intermediate.output_id,)
        else:
            assert output.input_ids == (calc_def.input_attributes[0].element_id,)
            assert output.dependency_ids == ()


def test_calc_payload_attachment_is_exact_and_total(
    extracted: tuple[SysMLDataExtractor, list[CalculationDefinitionData]],
) -> None:
    extractor, calc_defs = extracted
    first = _by_package(calc_defs, "PayloadIdentityA")
    second = _by_package(calc_defs, "PayloadIdentityB")

    # Reverse every presentation-shaped collection and lie in the extracted display metadata.
    # Exact IDs stay fixed, so neither payload association may move.
    reordered = [
        replace(
            second,
            name="display_only_second",
            qualified_name="DisplayOnly::Second",
            input_attributes=list(reversed(second.input_attributes)),
            output_attributes=list(reversed(second.output_attributes)),
        ),
        replace(
            first,
            name="display_only_first",
            qualified_name="DisplayOnly::First",
            input_attributes=list(reversed(first.input_attributes)),
            output_attributes=list(reversed(first.output_attributes)),
        ),
    ]
    graph = _elaborate(extractor, reordered)

    power = calc(graph, "PayloadIdentityDesign__system__power_calc")
    length = calc(graph, "PayloadIdentityDesign__system__length_calc")
    assert power.calculation_definition_id == DeclarationId(first.element_id)
    assert length.calculation_definition_id == DeclarationId(second.element_id)
    assert power.compilation_definition_id == DeclarationId(first.element_id)
    assert length.compilation_definition_id == DeclarationId(second.element_id)
    assert set(power.compiled_output_ids) == set(power.outputs)
    assert set(length.compiled_output_ids) == set(length.outputs)
    assert next(iter(power.output_metadata.values())).unit == "W"
    assert next(iter(length.output_metadata.values())).unit == "m"
    assert power.auto_impl_context != length.auto_impl_context


@pytest.mark.parametrize("missing", ["definition", "formal", "output"])
def test_missing_required_calc_payload_identity_fails_closed(
    extracted: tuple[SysMLDataExtractor, list[CalculationDefinitionData]],
    missing: str,
) -> None:
    extractor, calc_defs = extracted
    target = calc_defs[0]
    if missing == "definition":
        broken = replace(target, element_id=None)
    elif missing == "formal":
        broken = replace(
            target,
            input_attributes=[replace(target.input_attributes[0], element_id=None)],
        )
    else:
        broken = replace(
            target,
            output_attributes=[replace(target.output_attributes[0], element_id=None)],
        )

    with pytest.raises(ElaborationDiagnosticError) as excinfo:
        _elaborate(extractor, [broken, *calc_defs[1:]])

    assert excinfo.value.diagnostics[0].code is ElaborationCode.SI_ID_MISSING


def test_conflicting_calc_payload_identity_fails_closed(
    extracted: tuple[SysMLDataExtractor, list[CalculationDefinitionData]],
) -> None:
    extractor, calc_defs = extracted
    conflicting = replace(calc_defs[1], element_id=calc_defs[0].element_id)

    with pytest.raises(ElaborationDiagnosticError) as excinfo:
        _elaborate(extractor, [calc_defs[0], conflicting])

    assert excinfo.value.diagnostics[0].code is ElaborationCode.SI_EDGE_DANGLING


def test_constraint_profile_attachment_is_exact_closed_and_total(
    extracted: tuple[SysMLDataExtractor, list[CalculationDefinitionData]],
) -> None:
    extractor, calc_defs = extracted
    graph = _elaborate(extractor, list(reversed(calc_defs)))
    nodes = {node.display_name: node for node in graph.constraints.values()}

    assert set(nodes) == {
        "blocked_guard",
        "admitted_guard",
        "annotation_guard",
        "unassessed_guard",
    }
    assert nodes["blocked_guard"].eligibility is Eligibility.BLOCK
    assert nodes["admitted_guard"].eligibility is Eligibility.ADMIT
    assert nodes["annotation_guard"].eligibility is Eligibility.NON_NUMERICAL
    assert nodes["unassessed_guard"].eligibility is Eligibility.UNASSESSED
    assert not isinstance(nodes["blocked_guard"].predicate_ir, str)
    assert not isinstance(nodes["admitted_guard"].predicate_ir, str)

    usages = {
        str(getattr(item, "name", "")): item
        for item in SysideAdapter.elements_of_type(
            extractor.model, "ConstraintUsage", include_subtypes=True
        )
    }
    definitions = {
        str(getattr(item, "name", "")): item
        for item in SysideAdapter.elements_of_type(
            extractor.model, "ConstraintDefinition", include_subtypes=True
        )
    }
    assert nodes["blocked_guard"].declaration_id == declaration_id_for(
        usages["blocked_guard"]
    )
    assert nodes["admitted_guard"].declaration_id == declaration_id_for(
        usages["admitted_guard"]
    )
    assert nodes["blocked_guard"].effective_definition_id == declaration_id_for(
        definitions["Payload Guard"]
    )
    assert nodes["admitted_guard"].effective_definition_id == declaration_id_for(
        definitions["Payload_Guard"]
    )


def test_profile_block_halts_exact_route_before_projection(
    extracted: tuple[SysMLDataExtractor, list[CalculationDefinitionData]],
) -> None:
    extractor, calc_defs = extracted

    with pytest.raises(
        ElaborationDiagnosticError,
        match="SI_CONSTRAINT_BLOCKED.*blocked_guard.*block_real_equality_requires_tolerance",
    ):
        _elaborate(extractor, calc_defs, strict=True)

    graph = _elaborate(extractor, calc_defs)
    blocked = [
        diagnostic
        for diagnostic in graph.diagnostics
        if diagnostic.code.value == "SI_CONSTRAINT_BLOCKED"
    ]
    assert len(blocked) == 1
    assert blocked[0].consumer_display.endswith("__blocked_guard")
    assert "block_real_equality_requires_tolerance" in blocked[0].detail

    rebuilt = decode_instance_graph(encode_instance_graph(graph))
    rebuilt_blocked = [
        diagnostic
        for diagnostic in rebuilt.diagnostics
        if diagnostic.code is ElaborationCode.SI_CONSTRAINT_BLOCKED
    ]
    assert rebuilt_blocked == blocked

    with pytest.raises(ProjectionError, match="SI_CONSTRAINT_BLOCKED"):
        project(rebuilt)


def test_definition_constraint_source_key_is_rendered_from_model_metadata() -> None:
    extractor = SysMLDataExtractor([SOURCE_KEY_FIXTURE])
    assert extractor.load_models()
    graph = _elaborate(extractor, extractor.extract_calculation_definitions())
    projected = project(graph)
    assert projected.constraint_catalog is not None
    entries = {
        entry.source_local_identity: entry
        for entry in projected.constraint_catalog.concrete_entries
    }

    assert graph.constraints
    for node in graph.constraints.values():
        assert node.definition_qualified_name is not None
        assert node.predicate_source_key == ""
        public_key = entries[node.display_name].predicate_source_key
        assert public_key == f"definition:{node.definition_qualified_name}"
        assert node.effective_definition_id is not None
        assert node.effective_definition_id.to_wire() not in public_key


@pytest.mark.parametrize("corruption", ["missing", "duplicate", "unrecognized"])
def test_constraint_profile_decision_inventory_disagreement_fails_closed(
    extracted: tuple[SysMLDataExtractor, list[CalculationDefinitionData]],
    monkeypatch: pytest.MonkeyPatch,
    corruption: str,
) -> None:
    extractor, calc_defs = extracted
    elaboration_module = importlib.import_module("sysml_codegen.elaboration.elaborate")
    evaluate_exact = elaboration_module.evaluate_identified_profile

    def corrupted_profile(identified):
        result = evaluate_exact(identified)
        decisions = result.decisions
        if corruption == "missing":
            return replace(result, decisions=decisions[1:])
        if corruption == "duplicate":
            return replace(result, decisions=(decisions[0], *decisions))
        foreign = replace(
            decisions[0],
            usage_id=UUID("d61cd004-34cf-54e0-82a6-91da110104cd"),
        )
        return replace(result, decisions=(foreign, *decisions[1:]))

    monkeypatch.setattr(
        elaboration_module,
        "evaluate_identified_profile",
        corrupted_profile,
    )

    with pytest.raises(ElaborationDiagnosticError) as excinfo:
        _elaborate(extractor, calc_defs)

    assert excinfo.value.diagnostics[0].code is ElaborationCode.SI_EDGE_DANGLING
