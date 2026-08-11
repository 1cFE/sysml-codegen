"""Independent exact literal oracle for the maintained WI-014 toy fixture."""

from __future__ import annotations

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

SOURCE_KEYS = {
    "toy_plant__demo_plant__plant_budget",
    "toy_plant__demo_plant__plant_length",
    "toy_plant__demo_plant__plant_unit_cost",
    "toy_plant__demo_plant__plant_width",
}
EXPECTED_ALIAS = (
    "total_cost",
    "toy_plant__demo_plant__cost_calc__cost",
    "demo_plant",
    "part_def",
    "demo_plant__total_cost.json",
)
EXPECTED_CONSTRAINT_ID = "toy_plant__demo_plant__affordable__c122240f4b148939"


def test_wi014_literal_group_alias_and_constraint_are_exact() -> None:
    graph = build_pipeline_context([FIXTURES_DIR / "wi014_toy"]).computation_graph

    [group] = graph.entry_point_groups
    assert group.name == "toy_plant_params"
    assert {parameter.qualified_name for parameter in group.parameters} == SOURCE_KEYS

    aliases = {
        (
            alias.alias_name,
            alias.canonical_channel,
            alias.instance_path,
            alias.shape,
            alias.output_filename,
        )
        for alias in graph.output_aliases
    }
    assert aliases == {EXPECTED_ALIAS}

    assert graph.constraint_catalog is not None
    assert {
        entry.constraint_id for entry in graph.constraint_catalog.concrete_entries
    } == {EXPECTED_CONSTRAINT_ID}
