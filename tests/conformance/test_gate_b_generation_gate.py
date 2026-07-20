"""Gate B (LC-E04): final generation still owns V11 coverage, whole-graph and strict.

The companion half of the Gate B change. `extend_graph_with_constraints` no longer
runs a V11 coverage check (LC-E02 — proven vacuous; see
`.project/active/constraint-lifecycle-gate-b/decision.md`, and the extension-side
regressions in `tests/unit/test_constraint_graph_extension.py`). That deletion is only
safe because the generation boundary still rejects the same offender.

This file pins the second half: the exact graph extension now lets through must still
abort generation at `_reconcile_params_coverage`, and must pass once the key is covered.
Without this, the deletion would look like a coverage hole rather than a move of
ownership to the gate that already had it.

Offline — constructed `ComputationGraph` objects, no syside license needed.
"""

from pathlib import Path

import pytest

from sysml_codegen.analysis.constraint_lowering import extend_graph_with_constraints
from sysml_codegen.analysis.parameter_groups import DesignAttributeData, ParameterGroupDeriver
from sysml_codegen.cli import _reconcile_params_coverage
from sysml_codegen.generation import CodeGenerationError
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ConcreteConstraint,
    ConcreteConstraintInput,
    ConstraintInputResolution,
    EntryPoint,
    EntryPointType,
    InputSource,
    ModuleInput,
    ModuleKind,
    ModuleOutput,
    ParameterGroup,
    PipelineModule,
)

# The fusion-tea capital-rollup shape, reduced: a fell-through, valueless entry point
# that a pre-existing calc module reads.
DEFERRED_QN = "plant__lcoe_calc__total_capital"
PRODUCER_CHANNEL = "plant__cost_calc__direct"


def _graph(*, covered: bool) -> ComputationGraph:
    """The base graph. `covered=True` gives the deferred key a value (the late fill)."""
    producer = PipelineModule(
        name="cost_calc",
        module_type="plant.CostCalcModule",
        inputs=[],
        outputs=[
            ModuleOutput(field_name="direct", python_type="float", channel_name=PRODUCER_CHANNEL)
        ],
        execution_order=0,
        module_kind=ModuleKind.CALCULATION,
    )
    consumer = PipelineModule(
        name="lcoe_calc",
        module_type="plant.LcoeCalcModule",
        inputs=[
            ModuleInput(
                param_name="total_capital",
                python_type="float",
                source=InputSource(
                    source_type="entry_point",
                    param_group="plant_params",
                    qualified_name=DEFERRED_QN,
                ),
            )
        ],
        outputs=[
            ModuleOutput(
                field_name="lcoe", python_type="float", channel_name="plant__lcoe_calc__lcoe"
            )
        ],
        execution_order=1,
        module_kind=ModuleKind.CALCULATION,
    )
    group = ParameterGroup(
        name="plant_params",
        class_name="PlantParams",
        source_file=Path("design.sysml"),
        parameters=[
            EntryPoint(
                qualified_name=DEFERRED_QN,
                simple_name="total_capital",
                entry_type=EntryPointType.LIBRARY_DEFAULT,
                default_value=1.0 if covered else None,
                param_group="plant_params",
            )
        ],
    )
    return ComputationGraph(
        modules=[producer, consumer],
        entry_point_groups=[group],
        execution_order=["cost_calc", "lcoe_calc"],
        fallback_entry_points={DEFERRED_QN},
    )


def _safe_constraint() -> ConcreteConstraint:
    """A constraint that reads a produced channel — unrelated to the deferred key."""
    return ConcreteConstraint(
        constraint_id="plant__p__safe",
        usage_qualified_name="Plant__p__safe",
        source_local_identity="safe",
        source_form="definition_typed",
        owner_kind="part_def",
        owner_qualified_name="Plant__Plant",
        owner_instance_path="plant__p",
        membership_kind=None,
        predicate_source_key="definition:Plant::Safe",
        is_negated=False,
        expected_value=True,
        predicate_ir='{"kind":"literal"}',
        inputs=[
            ConcreteConstraintInput(
                formal_name="direct",
                resolution=ConstraintInputResolution.MODULE_OUTPUT,
                bound_channel=PRODUCER_CHANNEL,
            )
        ],
        evaluation_channel="plant__p__safe__evaluation",
        eligible=True,
    )


def _deriver() -> ParameterGroupDeriver:
    attrs: list[DesignAttributeData] = []
    return ParameterGroupDeriver({Path("design.sysml"): attrs}, calc_usages=[], calc_defs=[])


@pytest.mark.req("LC-E04")
def test_generation_gate_still_rejects_what_extension_now_allows():
    """The offender extension lets through must still abort at the generation boundary."""
    extended = extend_graph_with_constraints(
        _graph(covered=False), [_safe_constraint()], _deriver()
    )

    with pytest.raises(CodeGenerationError, match="V11") as excinfo:
        _reconcile_params_coverage(extended)

    message = str(excinfo.value)
    assert "lcoe_calc" in message, "the gate must name the offending module"
    assert DEFERRED_QN in message, "the gate must name the missing params key"


@pytest.mark.req("LC-E04")
def test_generation_gate_passes_once_the_key_is_covered():
    """Same graph, key given a value: the gate passes. The check is satisfiable, not absolute."""
    extended = extend_graph_with_constraints(_graph(covered=True), [_safe_constraint()], _deriver())
    _reconcile_params_coverage(extended)  # must not raise


@pytest.mark.req("LC-E04")
def test_gate_is_whole_graph_not_constraint_scoped():
    """The gate reports the PRE-EXISTING calc module, not any appended constraint module.

    This is the ownership statement: coverage is a whole-graph property of the final
    graph, independent of which modules the constraint pathway appended.
    """
    extended = extend_graph_with_constraints(
        _graph(covered=False), [_safe_constraint()], _deriver()
    )
    appended = {
        m.name
        for m in extended.modules
        if m.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR)
    }
    assert appended, "precondition: the extension appended constraint modules"

    with pytest.raises(CodeGenerationError) as excinfo:
        _reconcile_params_coverage(extended)

    message = str(excinfo.value)
    assert "module 'lcoe_calc'" in message
    for name in appended:
        assert f"module '{name}'" not in message
