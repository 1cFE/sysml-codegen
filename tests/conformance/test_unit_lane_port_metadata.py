"""Declaration-owned unit metadata across calc, constraint, and expression lanes."""

from __future__ import annotations

import importlib
import shutil
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.elaboration import ElaborationCode, InstanceGraph, ProjectionError, project
from sysml_codegen.elaboration.identity import (
    DeclarationId,
    ExpressionPortId,
    declaration_id_for,
)
from sysml_codegen.elaboration.occurrence import FeatureSlotIndex, build_feature_slot_index
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from sysml_codegen.snapshot.envelope import (
    SnapshotCertifiabilityError,
    load_instance_graph_snapshot,
)
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

A9 = FIXTURES_DIR / "unit_lane_a9"
RADIUS = FIXTURES_DIR / "unit_lane_radius"
CONSTRAINT_DISAGREEMENT = FIXTURES_DIR / "unit_lane_constraint_disagreement"
COMPUTED_DISAGREEMENT = FIXTURES_DIR / "unit_lane_computed_disagreement"
SOURCE_IDENTITY = FIXTURES_DIR / "unit_lane_source_identity"
CONSTRAINT_BINDING_UNIT_ANNOTATION = (
    FIXTURES_DIR / "constraint_binding_unit_annotation"
)

A9_COLLIDING_KEY = "CATFMFEVacuum__catf_vacuum_pumping__n_pumps"
RADIUS_COLLIDING_KEY = (
    "CATFMFERadialBuild__catf_radial_build__plasma_region__inner_radius"
)
CONSTRAINT_DISAGREEMENT_KEY = (
    "UnitLaneConstraintDisagreement__disagreement__shared_length"
)
COMPUTED_DISAGREEMENT_KEY = "UnitLaneComputedDisagreement__disagreement__shared_length"


def _node(graph: InstanceGraph, suffix: str):
    matches = [
        node
        for nodes in (graph.calcs, graph.constraints)
        for node in nodes.values()
        if node.display_path.endswith(suffix)
    ]
    assert len(matches) == 1, (suffix, [node.display_path for node in matches])
    return matches[0]


def _input_units(graph: InstanceGraph, suffix: str) -> dict[str, str | None]:
    node = _node(graph, suffix)
    return {
        node.input_names[port]: metadata.unit
        for port, metadata in node.input_metadata.items()
    }


def _input_records(
    graph: InstanceGraph, suffix: str
) -> dict[str, tuple[str, object, object]]:
    node = _node(graph, suffix)
    return {
        node.input_names[port]: (str(port), metadata, node.inputs.get(port))
        for port, metadata in node.input_metadata.items()
    }


def _entry_units(computation_graph) -> dict[str, str | None]:
    return {
        parameter.qualified_name: parameter.unit_text
        for group in computation_graph.entry_point_groups
        for parameter in group.parameters
    }


def _assert_collision(error: ProjectionError, key: str) -> None:
    assert error.diagnostics
    diagnostic = error.diagnostics[0]
    assert diagnostic.code is ElaborationCode.SI_RENDERING_COLLISION
    assert key in diagnostic.detail
    assert "conflicting projected metadata" in diagnostic.detail


def _loaded_model(fixture: Path) -> tuple[SysMLDataExtractor, object, FeatureSlotIndex]:
    extractor = SysMLDataExtractor([fixture])
    assert extractor.load_models()
    return extractor, extractor.model, build_feature_slot_index(extractor.model)


def _named_element(extractor: SysMLDataExtractor, model: object, kind: str, name: str):
    matches = [
        item
        for item in extractor.adapter.elements_of_type(model, kind, include_subtypes=True)
        if item.name == name
    ]
    assert len(matches) == 1, (kind, name, matches)
    return matches[0]


def test_a9_constraint_formals_preserve_authored_units() -> None:
    graph = elaborate_model_paths([A9])
    projected = project(graph)

    assert _input_units(graph, "__pumping_speed_agrees") == {
        "observed": "m³/s",
        "count": "Dimensionless",
        "each_capacity": "m³/s",
        "rel_tol": "Dimensionless",
    }
    assert _input_units(graph, "__pump_load") == {
        "pumping_speed_total_in": "m³/s",
        "pump_count": "Dimensionless",
        "pump_capacity": "m³/s",
    }
    entry_units = _entry_units(projected)
    assert entry_units["CATFMFEVacuum__catf_vacuum_pumping__pumping_speed_total"] == "m³/s"
    assert entry_units[A9_COLLIDING_KEY] == "Dimensionless"
    assert entry_units["CATFMFEVacuum__catf_vacuum_pumping__pump_capacity_each"] == "m³/s"
    [relative_tolerance] = [
        unit
        for key, unit in entry_units.items()
        if key.endswith("__pumping_speed_agrees__rel_tol")
    ]
    assert relative_tolerance == "Dimensionless"


def test_radius_derivation_inputs_preserve_authored_units() -> None:
    graph = elaborate_model_paths([RADIUS])
    projected = project(graph)

    assert _input_units(graph, "__outer_radius") == {
        "inner_radius": "m",
        "thickness": "m",
    }
    assert _input_units(graph, "__minor_calc") == {
        "r_inner": "m",
        "r_outer": "m",
        "r_major": "m",
    }
    entry_units = _entry_units(projected)
    assert entry_units[RADIUS_COLLIDING_KEY] == "m"
    assert entry_units[
        "CATFMFERadialBuild__catf_radial_build__plasma_region__thickness"
    ] == "m"
    assert entry_units["CATFMFERadialBuild__catf_radial_build__major_radius"] == "m"


def test_constraint_and_calculation_unit_agreement_projects_one_entry() -> None:
    graph = elaborate_model_paths([A9])
    assert _input_units(graph, "__pumping_speed_agrees")["count"] == "Dimensionless"
    assert _input_units(graph, "__pump_load")["pump_count"] == "Dimensionless"
    projected = project(graph)
    matching = [
        parameter
        for group in projected.entry_point_groups
        for parameter in group.parameters
        if parameter.qualified_name == A9_COLLIDING_KEY
    ]
    assert len(matching) == 1
    assert matching[0].unit_text == "Dimensionless"


def test_constraint_and_calculation_unit_disagreement_refuses() -> None:
    graph = elaborate_model_paths([CONSTRAINT_DISAGREEMENT])
    assert _input_units(graph, "__length_calc")["value"] == "m"
    assert _input_units(graph, "__length_guard")["observed"] == "cm"
    with pytest.raises(ProjectionError) as excinfo:
        project(graph)
    _assert_collision(excinfo.value, CONSTRAINT_DISAGREEMENT_KEY)


def test_computed_and_calculation_unit_agreement_projects_one_entry() -> None:
    graph = elaborate_model_paths([RADIUS])
    assert _input_units(graph, "__outer_radius")["inner_radius"] == "m"
    assert _input_units(graph, "__minor_calc")["r_inner"] == "m"
    projected = project(graph)
    matching = [
        parameter
        for group in projected.entry_point_groups
        for parameter in group.parameters
        if parameter.qualified_name == RADIUS_COLLIDING_KEY
    ]
    assert len(matching) == 1
    assert matching[0].unit_text == "m"


def test_computed_and_calculation_unit_disagreement_refuses() -> None:
    graph = elaborate_model_paths([COMPUTED_DISAGREEMENT])
    assert _input_units(graph, "__length_calc")["value"] == "m"
    assert _input_units(graph, "__doubled")["shared_length"] == "cm"
    with pytest.raises(ProjectionError) as excinfo:
        project(graph)
    _assert_collision(excinfo.value, COMPUTED_DISAGREEMENT_KEY)


def test_band_guard_base_formals_are_selected_from_definition_usages() -> None:
    elaborate_module = importlib.import_module("sysml_codegen.elaboration.elaborate")
    selector_type = getattr(elaborate_module, "_EffectiveInputFormalSelector", None)
    assert selector_type is not None, "effective-formal selector is not implemented"

    extractor, model, slots = _loaded_model(CONSTRAINT_BINDING_UNIT_ANNOTATION)
    selector = selector_type(model, slots)
    [band_guard] = [
        definition
        for definition in extractor.adapter.elements_of_type(model, "ConstraintDefinition")
        if definition.name == "BandGuard"
    ]
    selected = selector.effective_input_formals(band_guard)
    expected = {
        "a25d4eca-7e4c-55fd-88af-e2b703d539e4": (
            "a25d4eca-7e4c-55fd-88af-e2b703d539e4"
        ),
        "8540a49e-c62d-5b4b-b96c-a31d5f85e7ee": (
            "8540a49e-c62d-5b4b-b96c-a31d5f85e7ee"
        ),
    }
    assert {
        slot.root_declaration.to_wire(): declaration.to_wire()
        for slot, declaration in selected.items()
    } == expected

    selected_ids = set(selected.values())
    selected_objects = [
        item
        for item in band_guard.usages
        if getattr(item, "qualified_name", None) is not None
        and DeclarationId(extractor.adapter.element_id(item)) in selected_ids
    ]
    assert len(selected_objects) == 2
    assert all(extractor.adapter.is_instance(item, "AttributeUsage") for item in selected_objects)
    assert all(
        elaborate_module._ExactElaborator._direction(item) == "in"
        for item in selected_objects
    )

    [band] = [
        usage
        for usage in extractor.adapter.elements_of_type(model, "ConstraintUsage")
        if usage.name == "band"
    ]
    bound_slots = {
        slots.slot_of(DeclarationId(extractor.adapter.element_id(member)))
        for member in band.owned_members
        if elaborate_module._ExactElaborator._direction(member) == "in"
    }
    assert set(selected) == bound_slots


def test_calc_redefinition_uses_selected_effective_formal_unit() -> None:
    graph = elaborate_model_paths([SOURCE_IDENTITY])
    assert _input_units(graph, "__base_calc") == {"value": "cm"}
    assert _input_units(graph, "__redefined_calc") == {"value": "m"}

    extractor, model, slots = _loaded_model(SOURCE_IDENTITY)
    elaborate_module = importlib.import_module("sysml_codegen.elaboration.elaborate")
    definition = _named_element(
        extractor, model, "CalculationDefinition", "MetreLengthCalc"
    )
    usage = _named_element(extractor, model, "CalculationUsage", "redefined_calc")
    [binding_member] = [
        member
        for member in usage.owned_members
        if elaborate_module._ExactElaborator._direction(member) == "in"
    ]
    binding_id = declaration_id_for(binding_member)
    binding_slot = slots.slot_of(binding_id)
    selector = elaborate_module._EffectiveInputFormalSelector(model, slots)
    effective_formal = selector.effective_input_formals(definition)[binding_slot]

    redefined = _node(graph, "__redefined_calc")
    [(port, metadata)] = list(redefined.input_metadata.items())
    assert redefined.calculation_definition_id == declaration_id_for(definition)
    assert port.formal == binding_id
    assert effective_formal != binding_slot.root_declaration
    calc_payload = next(
        item
        for item in extractor.extract_calculation_definitions()
        if item.element_id == declaration_id_for(definition).value
    )
    assert [item.element_id for item in calc_payload.input_attributes] == [
        effective_formal.value
    ]
    assert metadata.unit == "m"
    assert metadata.formal_provenance is None
    assert _entry_units(project(graph))[
        "UnitLaneSourceIdentity__source_identity__metre_source"
    ] == "m"


def test_constraint_redefinition_uses_selected_effective_formal_unit() -> None:
    graph = elaborate_model_paths([SOURCE_IDENTITY])
    assert _input_units(graph, "__base_guard") == {"observed": "cm", "limit": "cm"}
    assert _input_units(graph, "__redefined_guard") == {"observed": "m", "limit": "m"}

    extractor, model, slots = _loaded_model(SOURCE_IDENTITY)
    elaborate_module = importlib.import_module("sysml_codegen.elaboration.elaborate")
    definition = _named_element(
        extractor, model, "ConstraintDefinition", "MetreLengthGuard"
    )
    usage = _named_element(extractor, model, "ConstraintUsage", "redefined_guard")
    selected = elaborate_module._EffectiveInputFormalSelector(
        model, slots
    ).effective_input_formals(definition)
    binding_slots = {
        member.name: slots.slot_of(declaration_id_for(member))
        for member in usage.owned_members
        if elaborate_module._ExactElaborator._direction(member) == "in"
    }
    redefined = _node(graph, "__redefined_guard")
    for port, metadata in redefined.input_metadata.items():
        name = redefined.input_names[port]
        assert redefined.effective_definition_id == declaration_id_for(definition)
        assert port.formal == selected[binding_slots[name]]
        assert port.formal != binding_slots[name].root_declaration
        assert metadata.formal_provenance is not None
        assert metadata.formal_provenance.declaration_id == port.formal
        assert metadata.unit == "m"
    assert _entry_units(project(graph))[
        "UnitLaneSourceIdentity__source_identity__metre_source"
    ] == "m"


def test_computed_alias_uses_referenced_declaration_unit() -> None:
    graph = elaborate_model_paths([SOURCE_IDENTITY])
    extractor, model, _slots = _loaded_model(SOURCE_IDENTITY)
    alias = _named_element(extractor, model, "AttributeUsage", "a")
    source = _named_element(extractor, model, "AttributeUsage", "alias_source")
    computed = _node(graph, "__computed_from_alias")
    [(port, metadata)] = list(computed.input_metadata.items())
    assert isinstance(port, ExpressionPortId)
    assert port.referenced_declaration == declaration_id_for(alias)
    assert computed.input_names[port] == "a"
    assert metadata.unit == "m"
    edge = computed.inputs[port]
    assert graph.attrs[edge.target].declaration_id == declaration_id_for(source)
    assert _entry_units(project(graph))[
        "UnitLaneSourceIdentity__source_identity__alias_source"
    ] == "m"


def test_capture_unit_collision_does_not_replace_destination(tmp_path: Path) -> None:
    destination = tmp_path / "existing.json"
    sentinel = b"item-8-sentinel\n"
    destination.write_bytes(sentinel)

    with pytest.raises(SnapshotCertifiabilityError) as excinfo:
        capture_instance_graph_snapshot([CONSTRAINT_DISAGREEMENT], destination)

    assert destination.read_bytes() == sentinel
    assert not list(tmp_path.glob(".existing.json.*.tmp"))
    _assert_collision_from_snapshot(excinfo.value, CONSTRAINT_DISAGREEMENT_KEY)


def test_capture_unit_collision_does_not_create_destination(tmp_path: Path) -> None:
    destination = tmp_path / "missing.json"

    with pytest.raises(SnapshotCertifiabilityError) as excinfo:
        capture_instance_graph_snapshot([CONSTRAINT_DISAGREEMENT], destination)

    assert not destination.exists()
    assert not list(tmp_path.glob(".missing.json.*.tmp"))
    _assert_collision_from_snapshot(excinfo.value, CONSTRAINT_DISAGREEMENT_KEY)


def test_live_generation_unit_collision_reports_its_authored_site(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    destination = tmp_path / "generated"

    with caplog.at_level("ERROR"):
        result = run_codegen(
            GenerationConfig(
                models_path=CONSTRAINT_DISAGREEMENT,
                output_path=destination,
                package_name="unit_collision_probe",
            )
        )

    assert result is False
    assert not destination.exists()
    assert f"reference='{CONSTRAINT_DISAGREEMENT_KEY}'" in caplog.text
    assert "[root-0/model.sysml:15]" in caplog.text


def _assert_collision_from_snapshot(
    error: SnapshotCertifiabilityError, key: str
) -> None:
    assert error.diagnostics
    diagnostic = error.diagnostics[0]
    assert diagnostic.code is ElaborationCode.SI_RENDERING_COLLISION
    assert key in diagnostic.detail
    assert "conflicting projected metadata" in diagnostic.detail


@pytest.mark.parametrize(
    ("fixture", "node_suffixes"),
    [
        (A9, ("__pump_load", "__pumping_speed_agrees")),
        (RADIUS, ("__outer_radius", "__minor_calc")),
        (
            SOURCE_IDENTITY,
            (
                "__base_calc",
                "__redefined_calc",
                "__alias_calc",
                "__base_guard",
                "__redefined_guard",
                "__computed_from_alias",
            ),
        ),
    ],
    ids=["constraint-formal", "computed-attribute", "source-identity"],
)
def test_live_in_place_and_relocated_routes_preserve_unit_metadata(
    tmp_path: Path, fixture: Path, node_suffixes: tuple[str, ...]
) -> None:
    live = elaborate_model_paths([fixture])
    captured = capture_instance_graph_snapshot([fixture], tmp_path / fixture.name / "case.json")
    in_place = load_instance_graph_snapshot(captured)
    relocated_path = tmp_path / "relocated" / fixture.name / "case.json"
    relocated_path.parent.mkdir(parents=True)
    shutil.copyfile(captured, relocated_path)
    relocated = load_instance_graph_snapshot(relocated_path)

    for suffix in node_suffixes:
        assert _input_records(live, suffix) == _input_records(in_place, suffix)
        assert _input_records(in_place, suffix) == _input_records(relocated, suffix)

    live_entries = _entry_units(project(live))
    assert live_entries == _entry_units(project(in_place)) == _entry_units(project(relocated))
