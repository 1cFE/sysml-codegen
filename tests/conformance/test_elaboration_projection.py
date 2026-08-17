"""Projection of the resolved exact-ID graph onto ``ComputationGraph``."""

from __future__ import annotations

from collections import Counter
from uuid import UUID

import pytest

from sysml_codegen.elaboration import (
    AttrNode,
    CalcNode,
    ConsumerPortId,
    DeclarationId,
    ElaborationCode,
    FeatureSlotId,
    InstanceGraph,
    NodeId,
    NodeKind,
    NodeRef,
    PackageScopeId,
    PortMetadata,
    ProjectionError,
    ValueSite,
    project,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.resolution.models import EntryPointType, ModuleKind
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.raw_elaboration import elaborate

pytestmark = requires_license


@pytest.fixture(scope="module")
def projected():
    extractor = SysMLDataExtractor([FIXTURES_DIR / "source_identity_mixed_consumers"])
    assert extractor.load_models()
    graph = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )
    return project(graph)


def test_projection_covers_every_live_module_kind(projected) -> None:
    kinds = Counter(module.module_kind for module in projected.modules)
    assert kinds[ModuleKind.CALCULATION] > 0
    assert kinds[ModuleKind.FORMULA] > 0
    assert kinds[ModuleKind.AGGREGATION] > 0
    assert kinds[ModuleKind.CONSTRAINT] > 0
    assert kinds[ModuleKind.REPORT_AGGREGATOR] == 1
    assert projected.constraint_catalog is not None
    assert projected.fallback_entry_points == set()


def test_projected_sources_preserve_value_site_classification(projected) -> None:
    parameters = {
        parameter.qualified_name: parameter
        for group in projected.entry_point_groups
        for parameter in group.parameters
    }
    availability = parameters[
        "source_identity_mixed_consumers__avail_ctx__avail_plant__availability"
    ]
    literal = parameters["source_identity_mixed_consumers__stamp_plant__lit_calc__value_in"]
    assert availability.entry_type is EntryPointType.DESIGN_ATTRIBUTE
    assert availability.default_value == 0.8
    assert literal.entry_type is EntryPointType.USAGE_LITERAL
    assert literal.default_value == 9.5


def test_projection_is_topological_and_every_input_is_covered(projected) -> None:
    assert projected.execution_order == [module.name for module in projected.modules]
    order = {module.name: module.execution_order for module in projected.modules}
    channels = {
        output.channel_name: module.name
        for module in projected.modules
        for output in module.outputs
    }
    for module in projected.modules:
        for input_ in module.inputs:
            if input_.source.source_type == "module_output":
                producer = channels[input_.source.producer_channel]
                assert order[producer] < order[module.name]
            else:
                assert input_.source.qualified_name is not None
                assert input_.source.param_group is not None


def _declaration(value: int) -> DeclarationId:
    return DeclarationId(UUID(int=value))


def test_public_rendering_collision_blocks_without_merging_nodes() -> None:
    scope = PackageScopeId(_declaration(1))
    first_slot = FeatureSlotId(_declaration(2))
    second_slot = FeatureSlotId(_declaration(3))
    first_id = NodeId(NodeKind.ATTRIBUTE, scope, first_slot)
    second_id = NodeId(NodeKind.ATTRIBUTE, scope, second_slot)
    consumer_id = NodeId(NodeKind.CALCULATION, scope, _declaration(4))
    first_port = ConsumerPortId(consumer_id, _declaration(5))
    second_port = ConsumerPortId(consumer_id, _declaration(6))
    graph = InstanceGraph(
        attrs={
            first_id: AttrNode(
                first_id,
                scope,
                _declaration(2),
                first_slot,
                "pkg__same",
                "same",
                "pkg::first",
                1.0,
                ValueSite.DEFINITION_DEFAULT,
            ),
            second_id: AttrNode(
                second_id,
                scope,
                _declaration(3),
                second_slot,
                "pkg__same",
                "same",
                "pkg::second",
                2.0,
                ValueSite.DEFINITION_DEFAULT,
            ),
        },
        calcs={
            consumer_id: CalcNode(
                node_id=consumer_id,
                scope=scope,
                declaration_id=_declaration(4),
                display_path="pkg__consumer",
                display_name="consumer",
                calc_def_name="Consumer",
                calc_def_qualified_name="pkg::Consumer",
                inputs={first_port: NodeRef(first_id), second_port: NodeRef(second_id)},
                input_names={first_port: "a", second_port: "b"},
                input_metadata={
                    first_port: PortMetadata(),
                    second_port: PortMetadata(),
                },
                calculation_definition_id=_declaration(5),
                compilation_definition_id=_declaration(5),
                compilability=Compilability.MANUAL_REQUIRED,
            )
        },
    )

    with pytest.raises(ProjectionError) as excinfo:
        project(graph)

    assert excinfo.value.diagnostics[0].code is ElaborationCode.SI_RENDERING_COLLISION


def test_unit_text_and_missing_unit_remain_a_rendering_collision() -> None:
    scope = PackageScopeId(_declaration(20))
    slot = FeatureSlotId(_declaration(21))
    source_id = NodeId(NodeKind.ATTRIBUTE, scope, slot)
    consumer_id = NodeId(NodeKind.CALCULATION, scope, _declaration(22))
    metre_port = ConsumerPortId(consumer_id, _declaration(23))
    missing_port = ConsumerPortId(consumer_id, _declaration(24))
    graph = InstanceGraph(
        attrs={
            source_id: AttrNode(
                source_id,
                scope,
                _declaration(21),
                slot,
                "pkg__shared_length",
                "shared_length",
                "pkg::shared_length",
                1.0,
                ValueSite.DEFINITION_DEFAULT,
            )
        },
        calcs={
            consumer_id: CalcNode(
                node_id=consumer_id,
                scope=scope,
                declaration_id=_declaration(22),
                display_path="pkg__consumer",
                display_name="consumer",
                calc_def_name="Consumer",
                calc_def_qualified_name="pkg::Consumer",
                inputs={
                    metre_port: NodeRef(source_id),
                    missing_port: NodeRef(source_id),
                },
                input_names={metre_port: "metres", missing_port: "unspecified"},
                input_metadata={
                    metre_port: PortMetadata(unit="m"),
                    missing_port: PortMetadata(unit=None),
                },
                calculation_definition_id=_declaration(25),
                compilation_definition_id=_declaration(25),
                compilability=Compilability.MANUAL_REQUIRED,
            )
        },
    )

    with pytest.raises(ProjectionError) as excinfo:
        project(graph)

    [diagnostic] = excinfo.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_RENDERING_COLLISION
    assert "pkg__shared_length" in diagnostic.detail
    assert "conflicting projected metadata" in diagnostic.detail
