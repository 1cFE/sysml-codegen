"""``build_model_contract`` — the pure graph-to-semantic-contract projection (Item 9 / INV-1).

No filesystem, no template access: every field comes from the in-memory
``ComputationGraph``. This is what makes a ``ModelContract`` buildable offline, from either
extraction path, with no I/O of its own.
"""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

from sysml_codegen.contracts.models import (
    EVALUATION_SEMANTICS,
    ContractOutput,
    ContractParameter,
    ModelContract,
)
from sysml_codegen.generation.constraint_catalog import _canonical_json

if TYPE_CHECKING:
    from sysml_codegen.resolution.models import ComputationGraph

__all__ = ["build_model_contract"]


def build_model_contract(graph: ComputationGraph) -> ModelContract:
    """Project a ``ComputationGraph`` into its semantic contract (D6, INV-1).

    Pure over ``graph`` — reads ``entry_point_groups``, ``modules``, and
    ``constraint_catalog`` only, then computes the semantic fingerprint over the
    resulting payload with the fingerprint field itself absent (INV-2).
    """
    from sysml_codegen.generation.errors import validate_constraint_graph_or_raise

    validate_constraint_graph_or_raise(graph)

    parameters = [
        ContractParameter(
            qualified_name=param.qualified_name,
            param_group=group.name,
            python_type=param.python_type,
            default_value=param.default_value,
            entry_type=param.entry_type.value,
        )
        for group in graph.entry_point_groups
        for param in group.parameters
    ]
    outputs = [
        ContractOutput(
            channel_name=output.channel_name,
            python_type=output.python_type,
            field_name=output.field_name,
        )
        for module in graph.modules
        for output in module.outputs
    ]

    unfingerprinted = {
        "parameters": [p.model_dump() for p in parameters],
        "outputs": [o.model_dump() for o in outputs],
        "constraint_catalog": (
            graph.constraint_catalog.model_dump() if graph.constraint_catalog else None
        ),
        "evaluation_semantics": EVALUATION_SEMANTICS,
    }
    semantic_fingerprint = hashlib.sha256(
        _canonical_json(unfingerprinted).encode("utf-8")
    ).hexdigest()

    return ModelContract(
        parameters=parameters,
        outputs=outputs,
        constraint_catalog=graph.constraint_catalog,
        evaluation_semantics=EVALUATION_SEMANTICS,
        semantic_fingerprint=semantic_fingerprint,
    )
