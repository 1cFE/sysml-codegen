"""D3-8 probe: `^` in an aggregation silently compiles to Python XOR.

Intended behavior (docs 13-aggregation-scoping, 14-expression-compiler, 25):
  The aggregation walker turns a PartDef-level `:>>` EXPRESSION redefinition
  into a Python string (`transformed_expression`). SysML/KerML `^` is the power
  operator; the expression compiler's PYTHON_OPERATOR_MAP maps `^` -> ` ** `.
  The walker SHOULD produce the same Python power, and SHOULD flag anything it
  cannot faithfully translate via has_unsupported_nodes.

Observed defect claim (D3-8): the walker uses expression_utils.OPERATOR_MAP,
  where `^` -> ` ^ ` (Python bitwise XOR) and unknown ops pass through, and it
  never sets has_unsupported. So `^` becomes XOR, silently.

This probe drives the full pipeline against an authored fixture and prints the
transformed_expression + has_unsupported_nodes for the aggregation.
"""
from __future__ import annotations

import logging
from pathlib import Path

logging.basicConfig(level=logging.ERROR)

FIX = Path(__file__).parent / "fixtures" / "d38_caret"


def main() -> None:
    from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

    ctx = build_pipeline_context([FIX])

    aggs = ctx.hierarchy_data.aggregation_expressions if ctx.hierarchy_data else []
    print(f"aggregation_expressions extracted: {len(aggs)}")
    for a in aggs:
        print(f"\n  owning_part_qn: {a.owning_part_qn}")
        print(f"  attribute_name: {a.attribute_name}")
        print(f"  transformed_expression: {a.transformed_expression!r}")
        print(f"  has_unsupported_nodes: {a.has_unsupported_nodes}")
        expr = a.transformed_expression or ""
        has_xor = " ^ " in expr
        has_pow = " ** " in expr
        print(f"  --> contains ' ^ ' (Python XOR): {has_xor}")
        print(f"  --> contains ' ** ' (Python power): {has_pow}")
        if has_xor and not a.has_unsupported_nodes:
            print("  VERDICT: CONFIRMED — '^' compiled to Python XOR, silently "
                  "(has_unsupported_nodes stayed False)")
        elif has_pow:
            print("  VERDICT: NOT-REPRODUCED — '^' rendered as Python power")


if __name__ == "__main__":
    main()
