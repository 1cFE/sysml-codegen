"""C19: the named nested-occurrence fixture, executed on all three public routes.

C19 is the case the string pipeline could not fix. ``:>> source.reading = 80.0``
sits on a ``panel`` usage nested inside an *instantiated* part def, so the
override is written definition-relative while demand resolves
occurrence-relative. The predecessor never matched the two and applied ``0`` on
both consumer paths. The exact route resolves it by node identity, and this is
that claim executed rather than asserted about a graph: the modelled ``80.0``
has to arrive at the one calculation input and the one constraint input, in real
TEAx, off the shipped public route.

**Three routes, one expectation.** Live from the model tree, from the committed
v6 snapshot read in place, and from a snapshot read at a foreign checkout root
with the model tree deleted. The snapshot routes are the ones the fixture had no
kept coverage for.

**The expectation is derived, not read back.** ``_modelled`` parses the three
literals out of ``model.sysml`` and everything asserted below is computed from
them. Nothing here reads a generated artifact to decide what the answer should
be, so a generator that emitted a self-consistent wrong number still fails.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from sysml_codegen.snapshot.envelope import (
    INSTANCE_GRAPH_SNAPSHOT_VERSION,
    load_instance_graph_snapshot,
)
from tests.execution.real_teax import (
    execute_sealed_package,
    generate_package_from_models,
    generate_package_from_snapshot,
    relocated_snapshot,
)

pytestmark = pytest.mark.execution

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "nested_occurrence_override_probe"
IN_PLACE_SNAPSHOT = FIXTURE / "instance_graph_snapshot.json"

ENTRY = "nested_occurrence_override_probe__the_design__panel__source__reading"
NOOP_CHANNEL = "nested_occurrence_override_probe__the_design__panel__noop__y"
WITHIN_ID = "nested_occurrence_override_probe__the_design__panel__within__c6f10edd2c380c4f"
WITHIN_CHANNEL = f"{WITHIN_ID}__evaluation"

ROUTES = ("live", "in_place_snapshot", "relocated_snapshot")


def _modelled() -> tuple[float, float]:
    """The overridden reading and the constraint limit, read off the SysML text.

    Parsed rather than restated so that editing the fixture's literals without
    editing this test fails loudly instead of silently comparing to a stale
    constant.
    """
    source = (FIXTURE / "model.sysml").read_text()
    (reading,) = re.findall(r":>> source\.reading = ([0-9.]+);", source)
    (limit,) = re.findall(r"v <= ([0-9.]+)", source)
    return float(reading), float(limit)


@pytest.fixture(scope="module")
def live_run(tmp_path_factory) -> dict[str, object]:
    root = tmp_path_factory.mktemp("c19-live")
    name = "c19_live"
    package = generate_package_from_models(FIXTURE, root / name, name)
    return execute_sealed_package(package, name, root)


@pytest.fixture(scope="module")
def in_place_snapshot_run(tmp_path_factory) -> dict[str, object]:
    root = tmp_path_factory.mktemp("c19-in-place")
    name = "c19_in_place"
    package = generate_package_from_snapshot(IN_PLACE_SNAPSHOT, root / name, name)
    return execute_sealed_package(package, name, root)


@pytest.fixture(scope="module")
def relocated_snapshot_run(tmp_path_factory) -> dict[str, object]:
    root = tmp_path_factory.mktemp("c19-relocated")
    name = "c19_relocated"
    with relocated_snapshot(FIXTURE, "item7-c19-") as snapshot:
        package = generate_package_from_snapshot(snapshot, root / name, name)
    return execute_sealed_package(package, name, root)


@pytest.fixture(scope="module", params=ROUTES)
def executed(request) -> dict[str, object]:
    """Each test below runs once per generation route."""
    return request.getfixturevalue(f"{request.param}_run")


def test_the_in_place_route_reads_the_committed_v6_envelope() -> None:
    """The in-place input is a committed v6 envelope, not a capture made at test time."""
    envelope = json.loads(IN_PLACE_SNAPSHOT.read_text())
    assert envelope["format"] == "sysml-codegen-instance-graph"
    assert envelope["version"] == INSTANCE_GRAPH_SNAPSHOT_VERSION == 6
    assert load_instance_graph_snapshot(IN_PLACE_SNAPSHOT) is not None


def test_the_modelled_reading_reaches_the_calculation(executed) -> None:
    """``calc Noop`` is ``y = x`` fed by ``source.reading``, so ``y`` is the override."""
    reading, _limit = _modelled()
    outputs = executed["result"].outputs

    assert outputs[NOOP_CHANNEL].root == reading


def test_the_modelled_reading_reaches_the_constraint(executed) -> None:
    """``v <= limit`` sees the same override, with the slack it implies."""
    reading, limit = _modelled()
    evaluation = executed["result"].outputs[WITHIN_CHANNEL]

    assert evaluation.constraint_id == WITHIN_ID
    assert evaluation.observed == {"v": reading}
    assert evaluation.actual_value is (reading <= limit)
    assert evaluation.status == "satisfied"
    assert evaluation.margin == limit - reading


def test_both_consumers_carry_one_and_the_same_value(executed) -> None:
    """The C19 claim itself: one modelled value, two consumers, no second answer.

    The predecessor's failure mode was not a wrong number on one path — it was
    ``0`` on both while the model said ``80.0``. Comparing the two consumers to
    each other would pass under exactly that failure, so both are compared to
    the parsed literal and to each other.
    """
    reading, _limit = _modelled()
    outputs = executed["result"].outputs

    assert outputs[NOOP_CHANNEL].root == outputs[WITHIN_CHANNEL].observed["v"] == reading
    assert reading == 80.0


def test_the_package_publishes_exactly_these_three_channels(executed) -> None:
    """Enumerated, so a channel appearing or vanishing has to be accounted for here."""
    assert set(executed["result"].outputs) == {
        NOOP_CHANNEL,
        WITHIN_CHANNEL,
        "constraint_report",
    }


def test_the_generated_entry_point_carries_the_override(executed) -> None:
    """The emitted JSON is where a customer reads and edits the value."""
    reading, _limit = _modelled()
    package: Path = executed["package"]
    payload = json.loads(
        (package / "inputs" / "nested_occurrence_override_probe_params.json").read_text()
    )
    assert payload == {ENTRY: reading}


def test_the_three_routes_agree_channel_for_channel(
    live_run, in_place_snapshot_run, relocated_snapshot_run
) -> None:
    """Route parity, dumped whole rather than spot-checked.

    ``catalog_fingerprint`` is included on purpose: it is a digest of the
    constraint catalog, so a route that built a different catalog and still
    happened to produce ``80.0`` fails here.
    """

    def dump(run) -> dict[str, object]:
        outputs = run["result"].outputs
        return {
            NOOP_CHANNEL: outputs[NOOP_CHANNEL].root,
            WITHIN_CHANNEL: outputs[WITHIN_CHANNEL].model_dump(mode="json"),
            "constraint_report": outputs["constraint_report"].model_dump(mode="json"),
        }

    assert dump(live_run) == dump(in_place_snapshot_run) == dump(relocated_snapshot_run)


def test_the_relocated_route_ran_without_the_model_tree(relocated_snapshot_run) -> None:
    """The relocated route's precondition, asserted rather than assumed.

    ``relocated_snapshot`` deletes the copied model tree before generation and
    removes its whole scratch root afterwards, so the package that executed
    above has no model tree to reach back to.
    """
    package: Path = relocated_snapshot_run["package"]
    assert package.is_dir()
    assert not (package.parent / "model-tree").exists()
    assert (package / "contracts" / "package_contract.json").is_file()
