"""Public live/snapshot occurrence mutations executed by real TEAx."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from sysml_codegen.orchestration.exact_pipeline_context import (
    build_exact_pipeline_context,
    build_exact_pipeline_context_from_snapshot,
)
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from tests.execution.real_teax import (
    all_ports,
    consumer_ports,
    generate_package_from_models,
    generate_package_from_snapshot,
    package_loader,
)

pytestmark = pytest.mark.execution

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "occurrence_execution_matrix"
PACKAGE_NAME = "occurrence_derivation_matrix"
PREFIX = "occurrenceexecutionmatrix"
CHANNEL_PREFIX = "OccurrenceExecutionMatrix"


@dataclass(frozen=True)
class MutationCase:
    token: str
    value: float
    direct_ports: frozenset[tuple[str, str]]
    movers: frozenset[str]


def _channel(module: str, output: str = "y") -> str:
    return f"{module.replace(PREFIX, CHANNEL_PREFIX, 1)}__{output}"


CASES = (
    *(
        MutationCase(
            token=f"OccurrenceExecutionMatrix__unit[{index}]__local_value",
            value=9.0 + index,
            direct_ports=frozenset(
                {
                    (f"{PREFIX}__unit[{index}]__same", "x"),
                    (f"{PREFIX}__unit[{index}]__definition_local", "x"),
                    (f"{PREFIX}__unit[{index}]__producer", "x"),
                }
            ),
            movers=frozenset(
                {
                    _channel(f"{PREFIX}__unit[{index}]__same"),
                    _channel(f"{PREFIX}__unit[{index}]__definition_local"),
                    _channel(f"{PREFIX}__unit[{index}]__producer"),
                    _channel(f"{PREFIX}__unit[{index}]__output_consumer"),
                }
            ),
        )
        for index in (0, 1)
    ),
    MutationCase(
        token="OccurrenceExecutionMatrix__unit[0]__child__value",
        value=13.0,
        direct_ports=frozenset(
            {
                (f"{PREFIX}__unit[0]__child__local", "x"),
                (f"{PREFIX}__unit[0]__nested_sibling", "x"),
            }
        ),
        movers=frozenset(
            {
                _channel(f"{PREFIX}__unit[0]__child__local"),
                _channel(f"{PREFIX}__unit[0]__nested_sibling"),
            }
        ),
    ),
    MutationCase(
        token="OccurrenceExecutionMatrix__package_source",
        value=17.0,
        direct_ports=frozenset({(f"{PREFIX}__package_calc", "x")}),
        movers=frozenset({_channel(f"{PREFIX}__package_calc")}),
    ),
    MutationCase(
        token="OccurrenceExecutionMatrix__bank__cell[0]__cost",
        value=19.0,
        direct_ports=frozenset({(f"{PREFIX}__bank__total", "cost_0")}),
        movers=frozenset({_channel(f"{PREFIX}__bank__total", "total")}),
    ),
)


def _tree(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _harness(package: Path, graph, root: Path):
    from simkit.evaluation.evaluator import PreparedEvaluator
    from simkit.study.bridge import CandidateBridge

    evaluator = PreparedEvaluator(
        package_loader(package, PACKAGE_NAME, root / "link"),
        package / "pipelines" / "pipeline.yaml",
        expects_constraint_report=False,
    )
    return graph, evaluator, CandidateBridge(evaluator.entry_models)


@pytest.fixture(scope="module")
def public_routes(tmp_path_factory):
    root = tmp_path_factory.mktemp("occurrence-derivation-matrix")
    live_package = generate_package_from_models(FIXTURE, root / "live", PACKAGE_NAME)
    snapshot = capture_instance_graph_snapshot([FIXTURE], root / "snapshot.json")
    snapshot_package = generate_package_from_snapshot(
        snapshot,
        root / "snapshot",
        PACKAGE_NAME,
    )
    live_graph = build_exact_pipeline_context([FIXTURE]).computation_graph
    snapshot_graph = build_exact_pipeline_context_from_snapshot(snapshot).computation_graph

    assert _tree(live_package) == _tree(snapshot_package)
    assert live_graph == snapshot_graph
    return {
        "live": _harness(live_package, live_graph, root / "live-harness"),
        "snapshot": _harness(
            snapshot_package,
            snapshot_graph,
            root / "snapshot-harness",
        ),
    }


def _evaluate(route, selected_fields: dict[str, float]):
    _graph, evaluator, bridge = route
    return evaluator.evaluate(bridge.build(selected_fields))


def _entry_field(public_token: str) -> str:
    """Use the generated schema field while retaining the public channel token."""
    return public_token.replace("[", "_").replace("]", "")


def _movers(before, after) -> set[str]:
    assert set(before.outputs) == set(after.outputs)
    assert before.responses == after.responses == {}
    return {
        name for name in before.outputs if before.outputs[name] != after.outputs[name]
    }


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.token)
def test_modeled_source_mutates_every_and_only_its_consumers(
    public_routes,
    case: MutationCase,
) -> None:
    route_results = {}
    for route_name, route in public_routes.items():
        graph, _evaluator, _bridge = route
        published = [
            parameter.qualified_name
            for group in graph.entry_point_groups
            for parameter in group.parameters
        ]
        assert published.count(case.token) == 1
        assert consumer_ports(graph, case.token) == case.direct_ports
        assert len(all_ports(graph) - case.direct_ports) == len(all_ports(graph)) - len(
            case.direct_ports
        )

        baseline = _evaluate(route, {})
        mutated = _evaluate(route, {_entry_field(case.token): case.value})
        assert _movers(baseline, mutated) == case.movers
        route_results[route_name] = (
            dict(baseline.outputs),
            dict(mutated.outputs),
        )

    assert route_results["live"] == route_results["snapshot"]


def test_repeated_outer_and_plural_siblings_are_isolated(public_routes) -> None:
    graph, _evaluator, _bridge = public_routes["live"]
    tokens = {
        parameter.qualified_name
        for group in graph.entry_point_groups
        for parameter in group.parameters
    }
    assert {
        "OccurrenceExecutionMatrix__unit[0]__local_value",
        "OccurrenceExecutionMatrix__unit[1]__local_value",
        "OccurrenceExecutionMatrix__bank__cell[0]__cost",
        "OccurrenceExecutionMatrix__bank__cell[1]__cost",
    } <= tokens

    baseline = _evaluate(public_routes["live"], {})
    mutated = _evaluate(
        public_routes["live"],
        {_entry_field("OccurrenceExecutionMatrix__bank__cell[1]__cost"): 23.0},
    )
    assert _movers(baseline, mutated) == {
        _channel(f"{PREFIX}__bank__total", "total")
    }
