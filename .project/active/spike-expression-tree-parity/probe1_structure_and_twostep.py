"""S2 probe 1: predicate AST structure discovery + the two-step live oracle.

Loads the committed wi014_toy fixture, finds the constraint def's predicate
expression, dumps its raw syside node structure, introspects the Compiler
evaluation API, and reproduces the WI-014 two-step:
    Compiler.evaluate(predicate_expr, scope=assert_usage) -> bool

Throwaway spike script (S2). Run from repo root:
    uv run python .project/active/spike-expression-tree-parity/probe1_structure_and_twostep.py
"""

from __future__ import annotations

import inspect
from pathlib import Path

from agentic_mbse.sysml.syside_adapter import SysideAdapter, get_syside

REPO = Path(__file__).resolve().parents[3]
FIXTURE = REPO / "tests" / "fixtures" / "wi014_toy"


def dump(node, depth=0, max_depth=8):
    """Recursively dump a syside expression node's structure."""
    pad = "  " * depth
    tname = type(node).__name__
    bits = [tname]
    op = getattr(node, "operator", None)
    if op:
        bits.append(f"op={op!r}")
    val = getattr(node, "value", None)
    if val is not None and not hasattr(val, "elements"):
        bits.append(f"value={val!r}")
    name = getattr(node, "name", None)
    if isinstance(name, str):
        bits.append(f"name={name!r}")
    print(pad + " ".join(str(b) for b in bits))
    if depth >= max_depth:
        return
    # FeatureReferenceExpression: show referent
    if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
        ref = getattr(node, "referent", None)
        if ref is not None:
            print(
                pad
                + f"  -> referent: {type(ref).__name__} "
                + f"name={getattr(ref, 'name', None)!r} "
                + f"qn={getattr(ref, 'qualified_name', None)!r}"
            )
        return
    for operand in list(getattr(node, "operands", []) or []):
        dump(operand, depth + 1, max_depth)


def main():
    syside = get_syside()
    print(f"syside version: {getattr(syside, '__version__', 'unknown')}")

    model, diags = SysideAdapter.load_model([FIXTURE])
    print(f"loaded model: {type(model).__name__}")

    # --- find the constraint def and the assert usage ---
    cdefs = list(SysideAdapter.elements_of_type(model, "ConstraintDefinition"))
    cusages = list(SysideAdapter.elements_of_type(model, "AssertConstraintUsage"))
    print(f"\nConstraintDefinitions: {[getattr(d, 'name', None) for d in cdefs]}")
    print(f"AssertConstraintUsages: {[getattr(u, 'name', None) for u in cusages]}")

    cdef = next(d for d in cdefs if getattr(d, "name", "") == "Cost Within Budget")

    # --- where does the predicate expression live on the def? ---
    print("\n--- constraint def owned elements ---")
    for m in list(getattr(cdef, "owned_elements", []) or []):
        print(f"  {type(m).__name__} name={getattr(m, 'name', None)!r}")

    # Result expression candidates
    for attr in ("result", "result_expression", "resultExpression", "body"):
        v = getattr(cdef, attr, None)
        if v is not None:
            print(f"  cdef.{attr} = {type(v).__name__}")

    # find OperatorExpression descendants of the def
    print("\n--- OperatorExpressions under the def ---")
    predicate = None
    for oe in SysideAdapter.elements_of_type(model, "OperatorExpression"):
        owner = oe
        depth = 0
        while owner is not None and depth < 10:
            owner = getattr(owner, "owner", None)
            if owner is cdef:
                break
            depth += 1
        if owner is cdef:
            op = getattr(oe, "operator", None)
            print(f"  found op={op!r} (depth {depth})")
            if str(op) in ("<=", ">=", "<", ">", "==", "and", "or", "not"):
                if predicate is None:
                    predicate = oe

    assert predicate is not None, "no comparison OperatorExpression under def"
    print("\n--- predicate tree ---")
    dump(predicate)

    # --- Compiler API introspection ---
    print("\n--- Compiler API ---")
    comp_cls = getattr(syside, "Compiler", None)
    print(f"syside.Compiler: {comp_cls}")
    if comp_cls is not None:
        for nm, member in inspect.getmembers(comp_cls):
            if nm.startswith("_"):
                continue
            try:
                sig = str(inspect.signature(member))
            except (TypeError, ValueError):
                sig = "<no sig>"
            print(f"  Compiler.{nm}{sig}")

    # --- the two-step evaluation ---
    usage = next(u for u in cusages if getattr(u, "name", "") == "affordable")
    print("\n--- two-step evaluation ---")
    compiler = None
    for ctor in (lambda: comp_cls(), lambda: comp_cls(model)):
        try:
            compiler = ctor()
            break
        except Exception as e:  # noqa: BLE001
            print(f"  ctor failed: {e}")
    print(f"  compiler: {compiler!r}")
    if compiler is not None:
        try:
            result = compiler.evaluate(predicate, usage)
            print(f"  evaluate(predicate, scope=affordable) = {result!r} ({type(result).__name__})")
        except Exception as e:  # noqa: BLE001
            print(f"  positional failed: {e}")
            try:
                result = compiler.evaluate(predicate, scope=usage)
                print(f"  evaluate(..., scope=) = {result!r} ({type(result).__name__})")
            except Exception as e2:  # noqa: BLE001
                print(f"  kwarg failed: {e2}")


if __name__ == "__main__":
    main()
