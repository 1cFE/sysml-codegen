"""Projection consumes typed graph structure without parsing rendered identities."""

from __future__ import annotations

from copy import deepcopy

import pytest

from sysml_codegen.elaboration import (
    GraphValidationError,
    ValueSite,
    elaborate,
    project,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.resolution.models import EntryPointType, ModuleKind
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license


def _graph(fixture: str):
    extractor = SysMLDataExtractor([FIXTURES_DIR / fixture])
    assert extractor.load_models()
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )


def test_occurrence_records_are_total_and_computed_ir_stays_typed() -> None:
    graph = _graph("source_identity_mixed_consumers")

    assert graph.occurrences
    assert all(
        node.scope in graph.occurrences
        for population in (graph.attrs, graph.calcs, graph.constraints)
        for node in population.values()
        if node.scope.__class__.__name__ == "OccurrenceId"
    )
    assert all(
        not isinstance(node.expression_ir, str)
        for node in graph.calcs.values()
        if node.expression_ir is not None
    )


def test_constraint_owner_and_alias_scope_ignore_node_display_paths() -> None:
    constraint_graph = _graph("constraint_inline")
    expected_catalog = project(constraint_graph).constraint_catalog
    changed_constraint_graph = deepcopy(constraint_graph)
    [constraint] = changed_constraint_graph.constraints.values()
    constraint.display_path = "misleading__owner__constraint"

    changed_catalog = project(changed_constraint_graph).constraint_catalog
    assert changed_catalog is not None
    assert expected_catalog is not None
    assert changed_catalog.concrete_entries[0].owner_instance_path == (
        expected_catalog.concrete_entries[0].owner_instance_path
    )

    alias_graph = _graph("deep_cross_scope_probe")
    expected_aliases = project(alias_graph).output_aliases
    changed_alias_graph = deepcopy(alias_graph)
    [alias] = [node for node in changed_alias_graph.attrs.values() if node.is_alias]
    alias.display_path = "misleading__alias__path"
    assert project(changed_alias_graph).output_aliases == expected_aliases


def test_value_site_controls_entry_point_classification() -> None:
    graph = _graph("elab_native_plural_scope")
    projected = project(graph)
    parameters = {
        parameter.qualified_name: parameter
        for group in projected.entry_point_groups
        for parameter in group.parameters
    }

    inherited = next(
        node
        for node in graph.attrs.values()
        if node.display_path.endswith("__shadow__leaf[0]__value")
    )
    specialized = next(
        node
        for node in graph.attrs.values()
        if node.display_path.endswith("__selected__leaf[0]__value")
    )
    assert inherited.value_site is ValueSite.DEFINITION_DEFAULT
    assert specialized.value_site is ValueSite.SPECIALIZED_DEF
    assert parameters[inherited.display_path].entry_type is EntryPointType.DESIGN_ATTRIBUTE
    assert parameters[specialized.display_path].entry_type is EntryPointType.DESIGN_ATTRIBUTE


def test_constraint_port_type_comes_from_exact_feature_typing(tmp_path) -> None:
    model = tmp_path / "model.sysml"
    model.write_text(
        """package constraint_port_type {
    private import ScalarValues::*;

    part def Host {
        attribute count : Integer = 5;
        assert constraint positive { count > 0 }
    }

    part host : Host;
}
"""
    )
    extractor = SysMLDataExtractor([tmp_path])
    assert extractor.load_models()
    graph = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )
    [constraint] = graph.constraints.values()

    assert {metadata.python_type for metadata in constraint.input_metadata.values()} == {
        "int"
    }


def test_constraint_formal_provenance_comes_from_exact_port() -> None:
    graph = _graph("elab_constraint_formal_identity")
    [constraint] = graph.constraints.values()
    assert constraint.predicate_ir is not None
    reference = constraint.predicate_ir.operands[0]
    reference.reference.source_name = "misleading rendered spelling"

    projected = project(graph)
    module = next(
        item for item in projected.modules if item.module_kind is ModuleKind.CONSTRAINT
    )
    [input_] = module.inputs

    assert input_.param_name == "max_power"
    assert input_.formal_identity is not None
    assert input_.formal_identity.raw_name == "max power"
    assert input_.formal_identity.qualified_name == (
        "ConstraintFormalIdentity::'Maximum Power'::'max power'"
    )


def test_graph_validation_rejects_missing_occurrence_and_typed_producer_cycle() -> None:
    graph = _graph("source_identity_mixed_consumers")
    occurrence = next(iter(graph.occurrences))
    graph.occurrences.pop(occurrence)
    with pytest.raises(GraphValidationError):
        graph.validate()

    graph = _graph("source_identity_mixed_consumers")
    consumer = next(node for node in graph.calcs.values() if node.inputs and node.outputs)
    port = next(iter(consumer.inputs))
    output = next(iter(consumer.outputs.values()))
    from sysml_codegen.elaboration import ProducerRef

    consumer.inputs[port] = ProducerRef(output)
    with pytest.raises(GraphValidationError):
        graph.validate()
