"""The generator route's steps, in the order they run (Item 2b design, Architecture).

``Refused`` names one of these, and the report reads it, so the order is part of the contract.
``prepare`` produces CONSTRUCTION through PARAMETER_FIELD_NAMES; ``emit_package`` produces
DESTINATION and EMIT. The last three ``prepare`` steps are checked here on an empty graph,
which every earlier step accepts, with the step's own function made to refuse.
"""

from __future__ import annotations

import pytest

from sysml_codegen.cli.prepare import PreparationStep, Prepared, Refused, prepare_graph
from sysml_codegen.core.errors import CodeGenerationError, GenerationCode
from sysml_codegen.resolution.models import ComputationGraph


def _empty_graph() -> ComputationGraph:
    return ComputationGraph(modules=[], entry_point_groups=[], execution_order=[])


def test_step_order_is_pinned():
    assert [step.name for step in PreparationStep] == [
        "CONSTRUCTION",
        "GENERATION_METADATA",
        "EXIT_POINT_TYPES",
        "CONSTRAINT_NAMES",
        "OUTPUT_PATHS",
        "REGISTRY_CLASS_NAMES",
        "CONSTRAINT_TOTALITY",
        "CONSTRAINT_PLAN",
        "COVERAGE_ACCOUNT",
        "PARAMETER_FIELD_NAMES",
        "DESTINATION",
        "EMIT",
    ]


def test_an_empty_graph_passes_every_step():
    assert isinstance(prepare_graph(_empty_graph(), "pkg"), Prepared)


@pytest.mark.parametrize(
    ("target", "step"),
    [
        (
            "sysml_codegen.generation.constraint_plan.build_constraint_generation_plan",
            PreparationStep.CONSTRAINT_PLAN,
        ),
        ("sysml_codegen.cli.prepare._preflight_coverage_account", PreparationStep.COVERAGE_ACCOUNT),
        (
            "sysml_codegen.generation.entry_point.refuse_param_field_collisions",
            PreparationStep.PARAMETER_FIELD_NAMES,
        ),
    ],
)
def test_prepare_refuses_at_its_last_three_steps(monkeypatch, target, step):
    def refuse(*_args, **_kwargs):
        raise CodeGenerationError(
            f"probe: {step.name}", code=GenerationCode.MODULE_KIND_UNRENDERABLE
        )

    monkeypatch.setattr(target, refuse)
    refused = prepare_graph(_empty_graph(), "pkg")
    assert isinstance(refused, Refused)
    assert refused.step is step
    assert refused.message == f"Code generation failed: probe: {step.name}"
