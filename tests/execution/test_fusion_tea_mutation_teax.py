"""C25 and C2 mutations against the sealed package, in real TEAx, on all three routes.

**The matrix.** Every mutation runs on every route a customer can generate
through — live from the model tree, from the committed v6 snapshot read in
place beside that model, and from a v6 snapshot read at a foreign checkout root
with the model tree deleted. The assertions are identical across the three, so
a route that wired an entry point differently, or that lost a consumer, fails
here rather than in the field. One harness builds all three (``_harness``); the
routes differ only in how the package is generated and where its graph comes
from.

The protocol is the one Phase 2 decided under delegated authority: mutate at
runtime through TEAx's typed entry injection —
``CandidateBridge.build(selected_fields)`` fills every entry channel from the
package's own modelled defaults, and ``PreparedEvaluator.evaluate`` runs the
real executor against that mapping. Nothing is written to disk, and the seal
stays an active check during the mutation because the same
``ProvisionalPackageLoader`` verifies the package the evaluator then runs.

The route this test does *not* take is the one the plan calls invalid: edit a
sealed ``inputs/*.json`` and ask ``seal`` to bless it.
``test_editing_a_sealed_input_and_resealing_is_refused`` proves that refusal is
in code, not in policy.

**Every-and-only, in two legs.** A mutation must move exactly its consumers and
nothing else, and "nothing else" has to be enumerated rather than asserted:

- *Runtime* — the evaluation seam projects scalar module outputs and the
  constraint verdicts (``simkit/evaluation/projection.py``); the full set is
  compared before and after, so an unexpected mover fails.
- *Structural* — every ``(module, formal)`` input port in the whole graph is
  partitioned into the ports fed by the mutated entry point and the rest. That
  covers the two multi-output driver-cost modules, whose fields the evaluation
  seam does not project.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from sysml_codegen.contracts import (
    DEFAULT_COVERAGE_POLICY,
    ProvenanceError,
    check_reseal_provenance,
    ensure_package_tree_is_link_free,
)
from sysml_codegen.orchestration.exact_pipeline_context import (
    build_exact_pipeline_context,
    build_exact_pipeline_context_from_snapshot,
)
from tests.execution import fusion_tea_arithmetic as hand
from tests.execution.real_teax import (
    FUSION_TEA,
    LCOE_CHANNEL,
    all_ports,
    consumer_ports,
    generate_package_from_models,
    generate_package_from_snapshot,
    package_loader,
    relocated_snapshot,
)

pytestmark = pytest.mark.execution

REL = 1e-12

AVAILABILITY_ENTRY = "hif_plant_pkg__hif_plant__availability"
THERMAL_ENTRY = "hif_plant_pkg__hif_plant__thermal_efficiency"

COE_CHANNEL = "hif_plant_pkg__hif_plant__meier_coe_calc__coe_cents_kwh"
RECIRC_CHANNEL = "hif_plant_pkg__hif_plant__recirc_calc__f_recirc"

#: The forensic diagnostics this slice re-proves rather than accepts.
LCOE_AT_AVAILABILITY_091 = 269.5300723203276
LCOE_AT_THERMAL_044 = 263.85170462810606


#: The committed v6 snapshot, read where it sits beside its own model tree.
IN_PLACE_SNAPSHOT = FUSION_TEA / "instance_graph_snapshot.json"

ROUTES = ("live", "in_place_snapshot", "relocated_snapshot")


def _harness(root: Path, name: str, package: Path, graph) -> dict[str, object]:
    """Seal-load one generated package and prepare its evaluator and bridge."""
    from simkit.evaluation.evaluator import PreparedEvaluator
    from simkit.study.bridge import CandidateBridge

    loader = package_loader(package, name, root / "link")
    evaluator = PreparedEvaluator(loader, package / "pipelines" / "pipeline.yaml")
    return {
        "root": root,
        "name": name,
        "package": package,
        "graph": graph,
        "evaluator": evaluator,
        "bridge": CandidateBridge(evaluator.entry_models),
    }


@pytest.fixture(scope="module")
def live_harness(tmp_path_factory) -> dict[str, object]:
    """Generated from the model tree, the way a licensed user generates."""
    root = tmp_path_factory.mktemp("ft-mutation-live")
    name = "fusion_tea_mutation_live"
    package = generate_package_from_models(FUSION_TEA, root / name, name)
    graph = build_exact_pipeline_context([FUSION_TEA]).computation_graph
    return _harness(root, name, package, graph)


@pytest.fixture(scope="module")
def in_place_snapshot_harness(tmp_path_factory) -> dict[str, object]:
    """Generated license-free from the committed snapshot, read in place."""
    root = tmp_path_factory.mktemp("ft-mutation-in-place")
    name = "fusion_tea_mutation_in_place"
    package = generate_package_from_snapshot(IN_PLACE_SNAPSHOT, root / name, name)
    graph = build_exact_pipeline_context_from_snapshot(
        IN_PLACE_SNAPSHOT
    ).computation_graph
    return _harness(root, name, package, graph)


@pytest.fixture(scope="module")
def relocated_snapshot_harness(tmp_path_factory) -> dict[str, object]:
    """Generated from a snapshot at a foreign root, with the model tree deleted."""
    root = tmp_path_factory.mktemp("ft-mutation-relocated")
    name = "fusion_tea_mutation_relocated"
    with relocated_snapshot(FUSION_TEA, "item7-ft-mutation-") as snapshot:
        package = generate_package_from_snapshot(snapshot, root / name, name)
        graph = build_exact_pipeline_context_from_snapshot(snapshot).computation_graph
    return _harness(root, name, package, graph)


@pytest.fixture(scope="module", params=ROUTES)
def sealed(request) -> dict[str, object]:
    """Each test below runs once per generation route."""
    return request.getfixturevalue(f"{request.param}_harness")


def _evaluate(sealed, selected_fields: dict[str, float]):
    return sealed["evaluator"].evaluate(sealed["bridge"].build(selected_fields))


def _movers(baseline, mutated) -> set[str]:
    """Every observable that changed, over outputs and constraint responses."""
    assert set(baseline.outputs) == set(mutated.outputs)
    assert set(baseline.responses) == set(mutated.responses)
    moved = {
        name for name in baseline.outputs if baseline.outputs[name] != mutated.outputs[name]
    }
    moved |= {
        name
        for name in baseline.responses
        if baseline.responses[name] != mutated.responses[name]
    }
    return moved


# ---------------------------------------------------------------------------
# The unmutated baseline
# ---------------------------------------------------------------------------


def test_the_typed_entry_route_reproduces_the_hand_computed_baseline(sealed) -> None:
    """Injecting no overrides runs the package's own modelled defaults.

    That is the check that makes every mutation below comparable: the bridge
    fills each channel from the entry model's defaults, which are generated from
    the same model the emitted ``inputs/*.json`` come from, so the injected
    baseline must land on the same LCOE the file-backed route does.
    """
    evidence = _evaluate(sealed, {})

    assert evidence.outputs[LCOE_CHANNEL] == pytest.approx(hand.RUN_C_LCOE, rel=1e-6)
    assert evidence.outputs[LCOE_CHANNEL] == pytest.approx(hand.lcoe(), rel=REL)
    assert evidence.outputs[COE_CHANNEL] == pytest.approx(
        hand.meier_coe_cents_kwh(), rel=REL
    )
    assert evidence.outputs[RECIRC_CHANNEL] == pytest.approx(
        hand.recirculating_fraction(), rel=REL
    )
    assert evidence.responses["headline"] == "satisfied"
    assert evidence.provenance.executable_fingerprint


# ---------------------------------------------------------------------------
# C25 — availability
# ---------------------------------------------------------------------------


def test_c25_availability_feeds_exactly_two_consumer_ports(sealed) -> None:
    """Structural leg: one entry point, two ports, and every other port named."""
    graph = sealed["graph"]
    fed = consumer_ports(graph, AVAILABILITY_ENTRY)

    assert fed == {
        ("hif_plant_pkg__hif_plant__lcoe_calc", "availability_in"),
        ("hif_plant_pkg__hif_plant__meier_coe_calc", "availability_in"),
    }
    # The negative set: every remaining input port in the graph, enumerated.
    assert len(all_ports(graph) - fed) == len(all_ports(graph)) - 2
    assert not any(
        port[1].startswith("availability") for port in all_ports(graph) - fed
    )


def test_c25_mutating_availability_moves_exactly_lcoe_and_meier_coe(sealed) -> None:
    """Runtime leg, with both moved values computed by hand at 0.91."""
    baseline = _evaluate(sealed, {})
    mutated = _evaluate(sealed, {AVAILABILITY_ENTRY: 0.91})

    assert _movers(baseline, mutated) == {LCOE_CHANNEL, COE_CHANNEL}

    assert mutated.outputs[LCOE_CHANNEL] == pytest.approx(
        hand.lcoe(availability=0.91), rel=REL
    )
    assert hand.lcoe(availability=0.91) == LCOE_AT_AVAILABILITY_091
    assert mutated.outputs[COE_CHANNEL] == pytest.approx(
        hand.meier_coe_cents_kwh(availability=0.91), rel=REL
    )


# ---------------------------------------------------------------------------
# C2 — thermal efficiency
# ---------------------------------------------------------------------------


def test_c2_thermal_efficiency_feeds_exactly_two_consumer_ports(sealed) -> None:
    graph = sealed["graph"]
    fed = consumer_ports(graph, THERMAL_ENTRY)

    assert fed == {
        ("hif_plant_pkg__hif_plant__lcoe_calc", "thermal_efficiency_in"),
        ("hif_plant_pkg__hif_plant__recirc_calc", "thermal_efficiency_in"),
    }
    assert len(all_ports(graph) - fed) == len(all_ports(graph)) - 2
    assert not any(
        port[1].startswith("thermal_efficiency") for port in all_ports(graph) - fed
    )


def test_c2_mutating_thermal_efficiency_moves_exactly_lcoe_and_recirc(sealed) -> None:
    baseline = _evaluate(sealed, {})
    mutated = _evaluate(sealed, {THERMAL_ENTRY: 0.44})

    assert _movers(baseline, mutated) == {LCOE_CHANNEL, RECIRC_CHANNEL}

    assert mutated.outputs[LCOE_CHANNEL] == pytest.approx(
        hand.lcoe(thermal_efficiency=0.44), rel=REL
    )
    assert hand.lcoe(thermal_efficiency=0.44) == LCOE_AT_THERMAL_044
    assert mutated.outputs[RECIRC_CHANNEL] == pytest.approx(
        hand.recirculating_fraction(thermal_efficiency=0.44), rel=REL
    )


# ---------------------------------------------------------------------------
# The mutation protocol's own guarantees
# ---------------------------------------------------------------------------


def test_the_mutations_left_the_sealed_package_untouched(sealed) -> None:
    """Reload the package after every mutation above: the seal still verifies.

    Typed-entry injection never writes to disk, so a fresh load of the same
    directory must reproduce the same ``executable_fingerprint``.
    """
    root: Path = sealed["root"]
    reloaded = package_loader(sealed["package"], sealed["name"], root / "link")
    _module, fingerprint = reloaded.load()
    assert fingerprint == sealed["evaluator"].fingerprint


def test_an_unknown_entry_field_fails_closed(live_harness) -> None:
    """The bridge refuses a field no channel declares, so a typo cannot no-op.

    A property of the injection protocol rather than of a generation route, so
    it is proved once rather than once per route.
    """
    from simkit.evaluation.failure import EvaluationFailed

    with pytest.raises(EvaluationFailed):
        _evaluate(live_harness, {"hif_plant_pkg__hif_plant__not_a_field": 1.0})


def test_editing_a_sealed_input_and_resealing_is_refused(live_harness, tmp_path) -> None:
    """The invalid route, demonstrated against the real provenance gate.

    ``inputs/*.json`` is inside the sealed set, and ``check_reseal_provenance``
    lets only ``handwritten/**`` change across a re-seal. Editing an input and
    re-sealing therefore cannot launder the edit, which is why the mutation
    tests above go through the evaluator instead.
    """
    copy = tmp_path / "edited"
    shutil.copytree(live_harness["package"], copy)

    target = copy / "inputs" / "hif_plant_params.json"
    payload = json.loads(target.read_text())
    assert payload[AVAILABILITY_ENTRY] == hand.AVAILABILITY
    payload[AVAILABILITY_ENTRY] = 0.91
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    entries = ensure_package_tree_is_link_free(copy)
    prior_seal = json.loads((copy / "contracts" / "package_contract.json").read_text())

    with pytest.raises(ProvenanceError) as excinfo:
        check_reseal_provenance(copy, entries, prior_seal, DEFAULT_COVERAGE_POLICY)
    assert "inputs/hif_plant_params.json" in str(excinfo.value)
