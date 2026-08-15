"""Gate B probe 1 — the three shapes from the two Gate B reports, run for real.

Candidate: 3700fee (src/ byte-identical at 14f042c, where this was run).
License-free: pure ComputationGraph / ConcreteConstraint objects, no syside.

Shapes (both reports name these):
  A  pre-existing/unrelated  — base graph has a valueless fell-through EP wired by a
                               pre-existing calc module; a SAFE constraint is added.
  B  newly consumed          — base graph has a valueless fell-through EP that is
                               UNWIRED; a constraint is added that consumes it.
  C  mixed                   — A's pre-existing offender plus B's newly consumed one.

Run:  uv run python .project/active/constraint-lifecycle-gate-b/probes/p1_shapes.py
"""

from pathlib import Path

from sysml_codegen.analysis.constraint_lowering import extend_graph_with_constraints
from sysml_codegen.analysis.parameter_groups import DesignAttributeData, ParameterGroupDeriver
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
from sysml_codegen.resolution.graph_builder import collect_uncovered_params

# The demo's real deferred key shape: {calc_eqn}__{formal}, minted by the lenient
# calculation consumer's terminal miss (dependency_backtracker.py:603).
DEFERRED_QN = "plant__lcoe_calc__total_capital"
PRODUCER_CHANNEL = "plant__cost_calc__direct"


def _valueless_group(qn: str) -> ParameterGroup:
    """The group the graph builder emits for a fell-through, valueless EP."""
    return ParameterGroup(
        name="plant_params",
        class_name="PlantParams",
        source_file=Path("design.sysml"),
        parameters=[
            EntryPoint(
                qualified_name=qn,
                simple_name=qn.split("__")[-1],
                entry_type=EntryPointType.LIBRARY_DEFAULT,
                default_value=None,  # valueless -> the V11 predicate's second leg
                param_group="plant_params",
            )
        ],
    )


def _producer_module() -> PipelineModule:
    return PipelineModule(
        name="cost_calc",
        module_type="plant.CostCalcModule",
        inputs=[],
        outputs=[
            ModuleOutput(field_name="direct", python_type="float", channel_name=PRODUCER_CHANNEL)
        ],
        execution_order=0,
        module_kind=ModuleKind.CALCULATION,
    )


def _consumer_wired_to(qn: str) -> PipelineModule:
    """A pre-existing calc module reading the deferred key (the fusion rollup shape)."""
    return PipelineModule(
        name="lcoe_calc",
        module_type="plant.LcoeCalcModule",
        inputs=[
            ModuleInput(
                param_name="total_capital",
                python_type="float",
                source=InputSource(
                    source_type="entry_point", param_group="plant_params", qualified_name=qn
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


def _graph(*, wired: bool) -> ComputationGraph:
    modules = [_producer_module()]
    if wired:
        modules.append(_consumer_wired_to(DEFERRED_QN))
    return ComputationGraph(
        modules=modules,
        entry_point_groups=[_valueless_group(DEFERRED_QN)],
        execution_order=[m.name for m in modules],
        fallback_entry_points={DEFERRED_QN},
    )


def _cc(constraint_id: str, inputs: list[ConcreteConstraintInput]) -> ConcreteConstraint:
    return ConcreteConstraint(
        constraint_id=constraint_id,
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
        inputs=inputs,
        evaluation_channel=f"{constraint_id}__evaluation",
        eligible=True,
    )


SAFE_INPUT = ConcreteConstraintInput(
    formal_name="direct",
    resolution=ConstraintInputResolution.MODULE_OUTPUT,
    bound_channel=PRODUCER_CHANNEL,
)

# Shape B's consuming input. The ONLY way an appended constraint module can carry an
# entry_point input whose qualified_name equals a base fallback key is for the strict
# resolver to have returned DESIGN_ATTRIBUTE with identity == that key. Probe 2 tests
# whether that is reachable; here we FORCE it to characterise what extension does.
CONSUMING_INPUT = ConcreteConstraintInput(
    formal_name="total_capital",
    resolution=ConstraintInputResolution.DESIGN_ATTRIBUTE,
    design_attribute_qn=DEFERRED_QN,
)


def _deriver() -> ParameterGroupDeriver:
    attrs: list[DesignAttributeData] = []
    return ParameterGroupDeriver({Path("design.sysml"): attrs}, calc_usages=[], calc_defs=[])


def run(label: str, graph: ComputationGraph, constraints: list[ConcreteConstraint]) -> None:
    baseline = collect_uncovered_params(graph)
    print(f"\n=== {label} ===")
    print(f"  base graph V11 offenders (baseline): {[v.missing_key for v in baseline]}")
    try:
        extended = extend_graph_with_constraints(graph, constraints, _deriver())
    except Exception as exc:  # noqa: BLE001 - probe
        print(f"  extend_graph_with_constraints RAISED {type(exc).__name__}")
        print(f"    {exc}")
        return
    after = collect_uncovered_params(extended)
    print(f"  extend SUCCEEDED; extended V11 offenders: {[v.missing_key for v in after]}")


def main() -> None:
    print("Gate B probe 1 — three shapes at candidate 3700fee")
    print(f"deferred (fell-through, valueless) key: {DEFERRED_QN}")

    # A: pre-existing offender, wired by a pre-existing calc; constraint is unrelated/safe.
    run("A  pre-existing / unrelated", _graph(wired=True), [_cc("cA", [SAFE_INPUT])])

    # B: pre-existing key exists but NOTHING wires it (baseline clean); the constraint
    #    consumes it. This is the only shape that could be a NEW violation.
    run("B  newly consumed (forced)", _graph(wired=False), [_cc("cB", [CONSUMING_INPUT])])

    # B-control: same base graph, safe constraint. Proves the base is V11-clean.
    run("B' control (safe constraint)", _graph(wired=False), [_cc("cB2", [SAFE_INPUT])])

    # C: mixed — pre-existing wired offender AND the newly consuming constraint.
    run("C  mixed (forced)", _graph(wired=True), [_cc("cC", [CONSUMING_INPUT])])


if __name__ == "__main__":
    main()
