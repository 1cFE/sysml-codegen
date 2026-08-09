"""Public-graph comparison for the internal legacy/exact dual run."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sysml_codegen.resolution.models import ComputationGraph

__all__ = [
    "GraphDifference",
    "compare_computation_graphs",
    "public_graph_signature",
]


@dataclass(frozen=True)
class GraphDifference:
    """One independently comparable public graph section."""

    section: str
    legacy: object
    elaborated: object


def public_graph_signature(graph: ComputationGraph) -> dict[str, object]:
    """Return the generation-relevant, route-neutral public graph shape."""
    modules: list[dict[str, object]] = []
    for module in graph.modules:
        modules.append(
            {
                "name": module.name,
                "module_type": module.module_type,
                "module_kind": module.module_kind.value,
                "inputs": [
                    {
                        "param_name": input_.param_name,
                        "python_type": input_.python_type,
                        "source_type": input_.source.source_type,
                        "param_group": input_.source.param_group,
                        "qualified_name": input_.source.qualified_name,
                        "producer_channel": input_.source.producer_channel,
                    }
                    for input_ in module.inputs
                ],
                "outputs": [
                    {
                        "field_name": output.field_name,
                        "python_type": output.python_type,
                        "channel_name": output.channel_name,
                    }
                    for output in module.outputs
                ],
                "execution_order": module.execution_order,
            }
        )
    entry_points = [
        {
            "group": group.name,
            "class_name": group.class_name,
            "parameters": [
                {
                    "qualified_name": parameter.qualified_name,
                    "simple_name": parameter.simple_name,
                    "entry_type": parameter.entry_type.value,
                    "default_value": parameter.default_value,
                    "python_type": parameter.python_type,
                }
                for parameter in group.parameters
            ],
        }
        for group in graph.entry_point_groups
    ]
    aliases = [alias.model_dump(mode="json") for alias in graph.output_aliases]
    catalog: Any = (
        graph.constraint_catalog.model_dump(mode="json")
        if graph.constraint_catalog is not None
        else None
    )
    return {
        "modules": modules,
        "entry_points": entry_points,
        "execution_order": list(graph.execution_order),
        "aliases": aliases,
        "constraint_catalog": catalog,
    }


def compare_computation_graphs(
    legacy: ComputationGraph, elaborated: ComputationGraph
) -> tuple[GraphDifference, ...]:
    """Compare both independently constructed routes section by section."""
    legacy_signature = public_graph_signature(legacy)
    elaborated_signature = public_graph_signature(elaborated)
    return tuple(
        GraphDifference(
            section=section,
            legacy=legacy_signature[section],
            elaborated=elaborated_signature[section],
        )
        for section in legacy_signature
        if legacy_signature[section] != elaborated_signature[section]
    )
