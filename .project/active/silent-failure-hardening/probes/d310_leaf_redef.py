"""D3-10 probe: LITERAL redefinition matched by leaf name, first-wins.

Intended behavior (docs 25-hierarchy-resolver, 07-graph-assembly, 18-LVP):
  `_find_literal_redefinition(part_usage, attr, redefs, usage_type_map, owning_qn)`
  finds the LITERAL `:>>` default for a specific part usage's attribute. Strategy 1
  keys on the resolved type PartDef QN (exact). Strategy 2 (the fallback, used when
  usage_type_map has no entry) matches by the LAST `__` segment of owning_part_qn
  plus attribute_name. A given usage must resolve to ITS OWN PartDef's literal.

Observed defect claim (D3-10): Strategy 2 matches by bare leaf name across ALL
  PartDefs, first-wins. Two PartDefs with the same leaf name and the same attr name
  collide — the loop returns whichever redef comes first in the list, silently,
  regardless of which PartDef was intended.

Reproduction: extract real redefinitions from the authored two-`Motor` fixture,
then call the real `_find_literal_redefinition` with usage_type_map=None (the
fallback path) and show it returns one fixed value for BOTH intended parts.
"""
from __future__ import annotations

import logging
from pathlib import Path

logging.basicConfig(level=logging.ERROR)

FIX = Path(__file__).parent / "fixtures" / "d310_leaf_redef"


def main() -> None:
    from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
    from sysml_codegen.resolution.graph_builder import _find_literal_redefinition

    ctx = build_pipeline_context([FIX])
    redefs = ctx.hierarchy_data.redefinitions if ctx.hierarchy_data else []

    motor_power = [
        r for r in redefs
        if r.attribute_name == "power" and r.owning_part_qn.split("__")[-1] == "Motor"
    ]
    print(f"Motor.power LITERAL redefinitions extracted: {len(motor_power)}")
    for r in motor_power:
        print(f"  owning_qn={r.owning_part_qn!r} type={r.redefinition_type} "
              f"value={r.literal_value!r}")

    # Strategy-2 fallback path: no usage_type_map entry available.
    got = _find_literal_redefinition(
        part_usage="motor", attr="power", redefinitions=redefs,
        usage_type_map=None, owning_part_qn=None,
    )
    print(f"\n_find_literal_redefinition('motor','power', usage_type_map=None) -> {got}")
    values = sorted({r.literal_value for r in motor_power})
    print(f"Distinct authored values for the two Motors: {values}")
    if len(motor_power) >= 2 and got is not None:
        print("VERDICT: CONFIRMED — first-wins leaf-name match returns a single "
              f"fixed value ({got}) for BOTH same-named Motors; the other "
              "PartDef's literal is unreachable via the fallback, silently.")


if __name__ == "__main__":
    main()
