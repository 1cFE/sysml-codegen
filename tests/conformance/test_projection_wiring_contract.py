"""Two projection-boundary contracts, pinned with the arms audit-7 F2 found missing.

Narrow-correction step 4 (rev-2 brief), closing the two surviving PARTIAL rows:

- REQ-EPC-01 — every emitted entry point carries exactly one member of the
  three-value ``EntryPointType``. The prior heirs proved route parity and
  per-occurrence minting; a misclassified-but-route-consistent type would not
  have failed them. Here the classification itself is the subject: membership
  is asserted over every committed snapshot, and correctness is asserted
  against an authored oracle for ``fusion_tea``, whose 27 entry points cover
  all three classes.
- REQ-GA-03 — a ``module_output`` producer channel resolves to a declared
  output channel. On the public route this holds by construction (the sealed
  context re-projects, and projection mints channels only from resolved
  producer edges), and the specific violation is refused at the semantic layer:
  deleting a consumed producer makes both ``InstanceGraph.validate()`` and
  ``project()`` fail with ``SI_EDGE_DANGLING``. The prior cited arms exercised
  a missing occurrence and a producer cycle, never the absent producer itself.

License-free: everything loads from committed v6 snapshots.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.elaboration import GraphValidationError, ProducerRef, project
from sysml_codegen.resolution.models import EntryPointType
from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR

FUSION_SNAPSHOT = FIXTURES_DIR / "fusion_tea" / "instance_graph_snapshot.json"

# Authored oracle, not derived: fusion_tea's complete entry-point classification.
# beam energy / efficiency / plant attributes are modelled design values; the
# two calc-usage literal bindings and the three unbound formals falling back to
# calc-def defaults are the other two classes.
FUSION_TEA_CLASSIFICATION = {
    "hif_driver__hif_driver_instance__beam_energy_mj": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_driver__hif_driver_instance__efficiency": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_driver__hif_driver_instance__num_chambers": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_driver__hif_driver_instance__pulse_rate_ref": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__driver__efficiency": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__driver__energy": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__driver__lifetime_shots": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__meier_capital_calc__target_factory_cost": (
        EntryPointType.USAGE_LITERAL
    ),
    "hif_plant_pkg__hif_plant__meier_reactor_cost_calc__num_units": EntryPointType.USAGE_LITERAL,
    "hif_plant_pkg__hif_plant__availability": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__chamber__blanket_energy_multiple": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__chamber__yield_cost_constant": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__discount_rate": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__driver__beam_energy_mj": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__driver__num_chambers": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__driver__pulse_rate_ref": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__frequency": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__gain": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__net_electric_power_gw": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__om_cost_constant": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__plant_cost_constant": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__target_factory__cost_per_target": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__thermal_efficiency": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__thermal_power_gw": EntryPointType.DESIGN_ATTRIBUTE,
    "hif_plant_pkg__hif_plant__lcoe_calc__construction_years": EntryPointType.LIBRARY_DEFAULT,
    "hif_plant_pkg__hif_plant__lcoe_calc__operational_years": EntryPointType.LIBRARY_DEFAULT,
    "hif_plant_pkg__hif_plant__viability__threshold": EntryPointType.LIBRARY_DEFAULT,
}


def _entry_points(snapshot: Path):
    graph = project(load_instance_graph_snapshot(snapshot))
    return [ep for group in graph.entry_point_groups for ep in group.parameters]


def test_the_classification_is_a_closed_three_value_set() -> None:
    assert {member.value for member in EntryPointType} == {
        "library_default",
        "design_attribute",
        "usage_literal",
    }, "EntryPointType grew or shrank; ADR-001 classification is a reviewed rev"


def test_every_emitted_entry_point_carries_exactly_one_classification() -> None:
    """Membership totality over every committed snapshot."""
    seen = 0
    for snapshot in sorted(FIXTURES_DIR.glob("*/instance_graph_snapshot.json")):
        for ep in _entry_points(snapshot):
            assert isinstance(ep.entry_type, EntryPointType), (
                f"{snapshot.parent.name}:{ep.qualified_name} carries "
                f"{ep.entry_type!r}, not an EntryPointType member"
            )
            seen += 1
    assert seen > 0, "no entry points found across committed snapshots; re-anchor"


def test_fusion_tea_classification_matches_the_authored_oracle_exactly() -> None:
    """Correctness, not just membership: all three classes, exact per key."""
    actual = {ep.qualified_name: ep.entry_type for ep in _entry_points(FUSION_SNAPSHOT)}
    assert actual == FUSION_TEA_CLASSIFICATION
    assert set(FUSION_TEA_CLASSIFICATION.values()) == set(EntryPointType), (
        "the oracle no longer covers all three classes; re-anchor the fixture"
    )


def _first_consumed_producer(graph):
    for node in graph.calcs.values():
        for edge in node.inputs.values():
            if isinstance(edge, ProducerRef):
                return edge.target.calculation
    raise AssertionError("fusion_tea has no producer-consumer edge; re-anchor")


def test_an_absent_producer_is_refused_specifically_at_both_layers() -> None:
    """REQ-GA-03's missing failing arm: delete a consumed producer node."""
    graph = load_instance_graph_snapshot(FUSION_SNAPSHOT)
    del graph.calcs[_first_consumed_producer(graph)]
    with pytest.raises(GraphValidationError, match="SI_EDGE_DANGLING"):
        graph.validate()

    graph = load_instance_graph_snapshot(FUSION_SNAPSHOT)
    del graph.calcs[_first_consumed_producer(graph)]
    with pytest.raises(Exception, match="SI_EDGE_DANGLING") as excinfo:
        project(graph)
    assert type(excinfo.value).__name__ == "ProjectionError"
