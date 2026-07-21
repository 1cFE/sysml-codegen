"""S2 probe 4: can the one tree serve today's calc compilation byte-identically?

Relationship-decision evidence. For every CalcDef output expression in the
committed wi014_toy and plant_values fixtures, plus a scratch model exercising
n-ary left-fold, unary minus, `^` power, and nested arithmetic:

  path A (today):  build_expression_ast() + compile_expression()
                   (sysml-codegen extraction/expression_compiler.py)
  path B (probe):  extract_ir() -> compat renderer -> Python string

and byte-compare the two Python strings. If B reproduces A everywhere, the
shared tree can absorb the calc path without disturbing generated artifacts
(extract-and-migrate is derisked); any mismatch names the seam that keeps the
paths separate for now.

Run from repo root:
    uv run python .project/active/spike-expression-tree-parity/probe4_calc_compat.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.extraction.expression_compiler import (
    CompilationError,
    _sanitize_name,
    build_expression_ast,
    compile_expression,
)

from s2_ir import ARITHMETIC_OPS, IRNode, extract_ir

REPO = Path(__file__).resolve().parents[3]

SCRATCH = """package s2_calc {
    private import ScalarValues::*;

    calc def 'Quad Product' {
        in attribute a : Real;
        in attribute b : Real;
        in attribute c : Real;
        in attribute d : Real;
        out attribute q : Real = a * b * c * d;
    }

    calc def 'Shapes' {
        in attribute x : Real;
        in attribute y : Real;
        out attribute neg : Real = -x + y;
        out attribute pw : Real = x ^ 2.0;
        out attribute nested : Real = (x + y) / (x - 2.0);
        out attribute chained : Real = x + y + 2.0 + x;
    }
}
"""


def compat_render(n: IRNode, input_names: set[str], member_names: set[str]) -> str:
    """Render IR to a Python string in today's compiler dialect.

    Mirrors compile_expression(): inputs.<name> for input refs, bare name for
    intermediates, n-ary left-fold with parens at every fold step, unary minus
    as (-x), '^' as ' ** ', unit annotation stripped to its value operand.
    """
    if n.kind == "literal":
        return str(n.value)
    if n.kind == "feature_ref":
        name = _sanitize_name(n.source_name or "")
        if name in input_names:
            return f"inputs.{name}"
        if name in member_names:
            return name
        raise CompilationError(f"unresolved reference: {name}")
    if n.kind == "unit":
        return compat_render(n.operands[0], input_names, member_names)
    if n.kind == "op" and n.operator in ARITHMETIC_OPS:
        if len(n.operands) == 1:
            return f"(-{compat_render(n.operands[0], input_names, member_names)})"
        py_op = " ** " if n.operator in ("**", "^") else f" {n.operator} "
        expr = compat_render(n.operands[0], input_names, member_names)
        for operand in n.operands[1:]:
            expr = f"({expr}{py_op}{compat_render(operand, input_names, member_names)})"
        return expr
    raise CompilationError(f"unsupported in calc-compat: {n.kind}/{n.operator}")


def calc_def_members(cdef):
    """(input_names, output_names, all_member_names, {out_name: expr_node})."""
    inputs, outputs, members, exprs = set(), set(), set(), {}
    for m in list(getattr(cdef, "owned_elements", []) or []):
        name = getattr(m, "name", None)
        if not name:
            continue
        sname = _sanitize_name(name)
        members.add(sname)
        direction = str(getattr(m, "direction", "") or "").lower()
        if "in" in direction and "out" not in direction:
            inputs.add(sname)
        elif "out" in direction:
            outputs.add(sname)
            expr = getattr(m, "feature_value_expression", None)
            if expr is not None:
                exprs[sname] = expr
        else:
            expr = getattr(m, "feature_value_expression", None)
            if expr is not None:
                exprs[sname] = expr
    return inputs, outputs, members, exprs


def run_model(label, paths, failures):
    model, _ = SysideAdapter.load_model(paths)
    print(f"\n=== {label} ===")
    n = 0
    for cdef in SysideAdapter.elements_of_type(model, "CalculationDefinition"):
        inputs, outputs, members, exprs = calc_def_members(cdef)
        for out_name, expr in exprs.items():
            n += 1
            # path A — today's compiler
            try:
                a_str = compile_expression(
                    build_expression_ast(expr, inputs, outputs, members)
                )
            except CompilationError as e:
                a_str = f"<A-error: {e}>"
            # path B — shared IR + compat renderer
            try:
                b_str = compat_render(extract_ir(expr), inputs, members)
            except CompilationError as e:
                b_str = f"<B-error: {e}>"
            match = a_str == b_str
            print(f"  [{'OK ' if match else 'DIFF'}] {getattr(cdef, 'name', '?')}.{out_name}")
            print(f"        A: {a_str}")
            if not match:
                print(f"        B: {b_str}")
                failures.append(f"{label}/{getattr(cdef, 'name', '?')}.{out_name}")
    if n == 0:
        failures.append(f"{label}: no calc output expressions found")


def main():
    failures = []
    run_model("wi014_toy", [REPO / "tests" / "fixtures" / "wi014_toy"], failures)
    run_model("plant_values", [REPO / "tests" / "fixtures" / "plant_values"], failures)

    tmp = Path(tempfile.mkdtemp(prefix="s2_calc_")) / "scratch.sysml"
    tmp.write_text(SCRATCH)
    run_model("scratch (n-ary, unary, power, nested, chained)", [tmp], failures)

    print(f"\n{'DIVERGENCES:' if failures else 'ALL CALC RENDERINGS BYTE-IDENTICAL'}")
    for f in failures:
        print(f"  - {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
