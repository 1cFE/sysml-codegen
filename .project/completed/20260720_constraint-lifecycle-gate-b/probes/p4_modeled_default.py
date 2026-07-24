"""Gate B probe 4 — the MODELED_DEFAULT mint, the third and last extension EP path.

`extend_graph_with_constraints` can wire an appended module to an entry point three ways:
  1. MODULE_OUTPUT     -> `source_type == "module_output"`, never an entry_point input, so
                          it can never satisfy V11's predicate at all.
  2. DESIGN_ATTRIBUTE  -> QN from `design_attr_by_qn` (probes 2 and 3).
  3. MODELED_DEFAULT   -> QN `{constraint_id}__{formal}` (constraint_lowering.py:1414),
                          default = `_literal_float(default_ir)`, which is **None** when the
                          modeled default is not a plain literal.

Path 3 is therefore the one place extension mints a VALUELESS entry point. This probe shows
that (a) it really does mint valueless, and (b) it is still not a V11 violation, because the
synthetic QN is not in `fallback_entry_points` — and that it WOULD be one if it were.

License-free. Run:
    uv run python .project/active/constraint-lifecycle-gate-b/probes/p4_modeled_default.py
"""

from pathlib import Path

from sysml_codegen.analysis.constraint_lowering import extend_graph_with_constraints
from sysml_codegen.analysis.parameter_groups import DesignAttributeData, ParameterGroupDeriver
from sysml_codegen.resolution.graph_builder import collect_uncovered_params
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ConcreteConstraint,
    ConcreteConstraintInput,
    ConstraintInputResolution,
)

CID = "plant__p__safe__0123456789abcdef"
FORMAL = "threshold"
SYNTHETIC_QN = f"{CID}__{FORMAL}"

# A non-literal modeled default: `_literal_float` returns None for anything that is not a
# LiteralNode, so the minted entry point is valueless.
NON_LITERAL_IR = (
    '{"kind":"feature_ref","schema_version":"expression-ir/v1","operand_type":null,'
    '"reference":{"chain_segments":[],"source_name":"other","target":null,"target_types":[]}}'
)


def _cc() -> ConcreteConstraint:
    return ConcreteConstraint(
        constraint_id=CID,
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
                formal_name=FORMAL,
                resolution=ConstraintInputResolution.MODELED_DEFAULT,
                default_ir=NON_LITERAL_IR,
            )
        ],
        evaluation_channel=f"{CID}__evaluation",
        eligible=True,
    )


def _deriver() -> ParameterGroupDeriver:
    attrs: list[DesignAttributeData] = []
    return ParameterGroupDeriver({Path("design.sysml"): attrs}, calc_usages=[], calc_defs=[])


def run(label: str, fallback: set[str]) -> None:
    graph = ComputationGraph(
        modules=[], entry_point_groups=[], execution_order=[], fallback_entry_points=fallback
    )
    print(f"\n=== {label} ===")
    print(f"  base fallback_entry_points: {sorted(fallback)}")
    try:
        extended = extend_graph_with_constraints(graph, [_cc()], _deriver())
    except Exception as exc:  # noqa: BLE001 - probe
        print(f"  extend RAISED {type(exc).__name__}: {exc}")
        return
    for g in extended.entry_point_groups:
        for p in g.parameters:
            print(f"  minted EP {p.qualified_name}  {p.entry_type.name}  default={p.default_value!r}")
    print(f"  V11 offenders: {collect_uncovered_params(extended)}")


def main() -> None:
    print("Gate B probe 4 — MODELED_DEFAULT mint at candidate 3700fee")
    print(f"synthetic QN: {SYNTHETIC_QN}")
    # Real case: the synthetic QN is fresh, so it is not in the fallback set.
    run("real: synthetic QN not in fallback set", set())
    # Counterfactual: force the synthetic QN into the fallback set. This is the only way
    # path 3 becomes a V11 violation, and nothing in the model can put it there — the
    # fallback set only ever holds `{calc_eqn}__{formal}` keys minted by the lenient
    # calculation consumer (dependency_backtracker.py:603).
    run("counterfactual: synthetic QN forced into fallback set", {SYNTHETIC_QN})


if __name__ == "__main__":
    main()
