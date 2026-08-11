"""Exact Fusion Tea formal renames and one-source C25/C2 fan-out."""

from __future__ import annotations

import re
import shutil
from collections import Counter
from pathlib import Path

import pytest
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration import elaborate
from sysml_codegen.elaboration.identity import OccurrenceId, declaration_id_for
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.snapshot_context import build_pipeline_context_from_snapshot
from sysml_codegen.snapshot import capture_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FUSION_TEA = FIXTURES_DIR / "fusion_tea"

FT_RENAMES = (
    ("designs/generic_ife/ife_plant.sysml", "availability_in", "availability"),
    ("designs/generic_ife/ife_plant.sysml", "discount_rate_in", "discount_rate"),
    ("designs/generic_ife/ife_plant.sysml", "frequency_in", "frequency"),
    ("designs/generic_ife/ife_plant.sysml", "gain_in", "gain"),
    ("designs/generic_ife/ife_plant.sysml", "om_cost_constant_in", "om_cost_constant"),
    ("designs/generic_ife/ife_plant.sysml", "plant_cost_constant_in", "plant_cost_constant"),
    ("designs/generic_ife/ife_plant.sysml", "thermal_efficiency_in", "thermal_efficiency"),
    ("designs/generic_ife/ife_plant.sysml", "gain_in", "gain"),
    ("designs/generic_ife/ife_plant.sysml", "thermal_efficiency_in", "thermal_efficiency"),
    ("designs/generic_ife/ife_plant.sysml", "gain_in", "gain"),
    ("designs/hif_ife/hif_plant.sysml", "thermal_power_gw_in", "thermal_power_gw"),
    ("designs/hif_ife/hif_plant.sysml", "availability_in", "availability"),
    (
        "designs/hif_ife/hif_plant.sysml",
        "net_electric_power_gw_in",
        "net_electric_power_gw",
    ),
    ("designs/hif_ife/hif_driver.sysml", "beam_energy_mj_in", "beam_energy_mj"),
    ("designs/hif_ife/hif_driver.sysml", "num_chambers_in", "num_chambers"),
)

SOURCE_CONSUMERS = {
    "hif_plant_pkg__hif_plant__availability": {
        ("hif_plant_pkg__hif_plant__lcoe_calc", "availability_in"),
        ("hif_plant_pkg__hif_plant__meier_coe_calc", "availability_in"),
    },
    "hif_plant_pkg__hif_plant__thermal_efficiency": {
        ("hif_plant_pkg__hif_plant__lcoe_calc", "thermal_efficiency_in"),
        ("hif_plant_pkg__hif_plant__recirc_calc", "thermal_efficiency_in"),
    },
}

INHERITED_ENUM_OCCURRENCES = (
    (
        "hif_driver__hif_driver_instance__scope",
        "ife_subsystems::'CAS22.1.3 Driver'::scope",
        "cas_hierarchy::'CAS Account'::scope",
        "economic_parameter::'CAS Scope'::ife_divergent",
    ),
    (
        "hif_plant_pkg__hif_plant__chamber__shield__scope",
        "ife_subsystems::'CAS22.1.2 Shield'::scope",
        "cas_hierarchy::'CAS Account'::scope",
        "economic_parameter::'CAS Scope'::shared",
    ),
    (
        "hif_plant_pkg__hif_plant__chamber__structure__scope",
        "ife_subsystems::'CAS22.1.5 Primary Structure'::scope",
        "cas_hierarchy::'CAS Account'::scope",
        "economic_parameter::'CAS Scope'::shared",
    ),
    (
        "hif_plant_pkg__hif_plant__chamber__blanket__scope",
        "ife_subsystems::'CAS22.1.1 First Wall Blanket'::scope",
        "cas_hierarchy::'CAS Account'::scope",
        "economic_parameter::'CAS Scope'::shared",
    ),
    (
        "hif_plant_pkg__hif_plant__target_factory__scope",
        "ife_subsystems::'CAS22.1.8 Target Factory'::scope",
        "cas_hierarchy::'CAS Account'::scope",
        "economic_parameter::'CAS Scope'::ife_divergent",
    ),
    (
        "hif_plant_pkg__hif_plant__driver__scope",
        "ife_subsystems::'CAS22.1.3 Driver'::scope",
        "cas_hierarchy::'CAS Account'::scope",
        "economic_parameter::'CAS Scope'::ife_divergent",
    ),
    (
        "hif_plant_pkg__hif_plant__chamber__wall_type",
        "hif_plant_pkg::hif_plant::chamber::wall_type",
        "ife_subsystems::'Reaction Chamber'::wall_type",
        "ife_subsystems::'Wall Type'::liquid_wall",
    ),
)


@pytest.fixture(scope="module")
def fusion_tea_lenient_exact_graph():
    extractor = SysMLDataExtractor([FUSION_TEA])
    assert extractor.load_models()
    graph = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=False,
    )
    return extractor.model, graph


def _feature(model, qualified_name: str):
    matches = [
        feature
        for feature in SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True)
        if str(getattr(feature, "qualified_name", "")) == qualified_name
    ]
    assert len(matches) == 1, qualified_name
    return matches[0]


def _routes(model_path: Path, output_dir: Path):
    output_dir.mkdir(parents=True)
    captured = capture_snapshot([model_path], output_dir / "in-place.json")
    relocated = output_dir / "relocated" / "case.json"
    relocated.parent.mkdir()
    shutil.copyfile(captured, relocated)
    return {
        "live": build_pipeline_context([model_path]).computation_graph,
        "in_place_v6": build_pipeline_context_from_snapshot(captured).computation_graph,
        "relocated_v6": build_pipeline_context_from_snapshot(relocated).computation_graph,
    }


def _consumers(graph, source_qn: str) -> set[tuple[str, str]]:
    return {
        (module.name, input_.param_name)
        for module in graph.modules
        for input_ in module.inputs
        if input_.source.qualified_name == source_qn
    }


def _entry_defaults(graph) -> dict[str, float | None]:
    return {
        parameter.qualified_name: parameter.default_value
        for group in graph.entry_point_groups
        for parameter in group.parameters
    }


def _module_surface(graph) -> dict[str, tuple[list[dict], list[dict]]]:
    return {
        module.name: (
            [item.model_dump(mode="json") for item in module.inputs],
            [item.model_dump(mode="json") for item in module.outputs],
        )
        for module in graph.modules
    }


def _mutated_fixture(tmp_path: Path, field: str, old: str, new: str) -> Path:
    target = tmp_path / field / "fusion_tea"
    shutil.copytree(FUSION_TEA, target)
    plant = target / "designs/hif_ife/hif_plant.sysml"
    original = plant.read_text()
    changed = original.replace(f":>> {field} = {old}", f":>> {field} = {new}", 1)
    assert changed != original
    plant.write_text(changed)
    return target


def test_exactly_fifteen_in_place_formal_renames_are_present() -> None:
    expected = Counter(FT_RENAMES)
    observed: Counter[tuple[str, str, str]] = Counter()
    for relative in sorted({item[0] for item in FT_RENAMES}):
        text = (FUSION_TEA / relative).read_text()
        observed.update(
            (relative, formal, source)
            for formal, source in re.findall(
                r"\bin\s+([A-Za-z_]\w*_in)\s*=\s*([A-Za-z_]\w*)\s*;", text
            )
        )

    assert observed == expected
    assert sum(observed.values()) == 15
    all_sysml = "\n".join(path.read_text() for path in sorted(FUSION_TEA.rglob("*.sysml")))
    assert not re.findall(r"\bin\s+([A-Za-z_]\w*)\s*=\s*\1\s*;", all_sysml)


@pytest.mark.parametrize(
    ("display_path", "writer_qn", "root_qn", "referent_qn"),
    INHERITED_ENUM_OCCURRENCES,
    ids=[item[0] for item in INHERITED_ENUM_OCCURRENCES],
)
def test_inherited_enum_values_are_effective_exact_occurrences(
    fusion_tea_lenient_exact_graph,
    display_path: str,
    writer_qn: str,
    root_qn: str,
    referent_qn: str,
) -> None:
    model, graph = fusion_tea_lenient_exact_graph
    node = graph.attr_by_display_path(display_path)
    writer = _feature(model, writer_qn)
    root = _feature(model, root_qn)
    referent = writer.feature_value_expression.referent

    assert isinstance(node.scope, OccurrenceId)
    assert graph.occurrence_display_path(node.scope) == display_path.rsplit("__", 1)[0]
    assert node.declaration_id == declaration_id_for(writer)
    assert node.slot_id.root_declaration == declaration_id_for(root)
    assert str(referent.qualified_name) == referent_qn
    assert node.value == referent_qn
    assert not node.is_alias
    assert node.alias_target is None


def test_fusion_tea_inherited_enum_occurrences_are_projectable() -> None:
    extractor = SysMLDataExtractor([FUSION_TEA])
    assert extractor.load_models()
    graph = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )
    assert graph.diagnostics == []


def test_c25_and_c2_have_exact_consumers_and_complete_negative_sets(tmp_path: Path) -> None:
    baseline_routes = _routes(FUSION_TEA, tmp_path / "baseline")
    changes = {
        "hif_plant_pkg__hif_plant__availability": _mutated_fixture(
            tmp_path, "availability", "0.9", "0.91"
        ),
        "hif_plant_pkg__hif_plant__thermal_efficiency": _mutated_fixture(
            tmp_path, "thermal_efficiency", "0.43", "0.44"
        ),
    }

    for source_qn, changed_fixture in changes.items():
        changed_routes = _routes(
            changed_fixture,
            tmp_path / f"changed-{source_qn.rsplit('__', 1)[-1]}",
        )
        for route, baseline in baseline_routes.items():
            changed = changed_routes[route]
            expected_consumers = SOURCE_CONSUMERS[source_qn]
            assert _consumers(baseline, source_qn) == expected_consumers
            assert _consumers(changed, source_qn) == expected_consumers

            baseline_defaults = _entry_defaults(baseline)
            changed_defaults = _entry_defaults(changed)
            assert {
                name
                for name, value in baseline_defaults.items()
                if changed_defaults[name] != value
            } == {source_qn}
            assert list(baseline_defaults).count(source_qn) == 1
            assert list(changed_defaults).count(source_qn) == 1

            # This is the complete negative input/output set: every projected module port,
            # including every nonconsumer, is byte-equal after changing only the source value.
            assert _module_surface(changed) == _module_surface(baseline)
