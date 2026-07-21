"""S2 probe 3: non-finite points against the documented Kleene truth table.

The oracle here is the concept's documented three-valued semantics, NOT raw
SysIDE (the IEEE divergence is by design): any non-finite operand (NaN, +inf,
-inf) makes its own leaf comparison unknown; unknown propagates only where a
connective needs it (true or unknown = true; false and unknown = false); the
assertion is indeterminate only when its overall value is unknown. Margins are
None whenever an operand is non-finite, and the sign respects polarity.

Also runs one informative live probe: what SysIDE itself returns when a
predicate operand is 1.0/0.0 (undocumented in syside docs; recorded as
evidence, not gated).

Run from repo root:
    uv run python .project/active/spike-expression-tree-parity/probe3_nonfinite_kleene.py
"""

from __future__ import annotations

import math
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from s2_ir import IRNode, compile_predicate, load_predicate

NAN, PINF, NINF = float("nan"), float("inf"), float("-inf")


def ir_cmp(op, a, b):
    return IRNode(kind="op", operator=op, operands=[a, b])


def ref(name):
    return IRNode(kind="feature_ref", source_name=name)


def lit(v):
    return IRNode(kind="literal", value=v, value_type="real")


def check(label, actual, expected, failures):
    ok = (
        actual == expected
        if not isinstance(expected, float)
        else (actual == expected or (actual is not None and math.isclose(actual, expected)))
    )
    print(f"  [{'OK ' if ok else 'FAIL'}] {label}: got {actual!r}, expected {expected!r}")
    if not ok:
        failures.append(f"{label}: got {actual!r}, expected {expected!r}")


def main():
    failures = []

    # --- 1. every comparison op x every non-finite value x both operand sides ---
    print("=== leaf comparisons: non-finite operand -> unknown (indeterminate) ===")
    simple = ir_cmp("<=", ref("a"), ref("b"))
    for op in ("<", "<=", ">", ">="):
        pred_ir = ir_cmp(op, ref("a"), ref("b"))
        src, _ = compile_predicate(pred_ir, "pred", negated=False)
        fn = load_predicate(src, "pred")
        for nf in (NAN, PINF, NINF):
            for kwargs in ({"a": nf, "b": 1.0}, {"a": 1.0, "b": nf}):
                r = fn(**kwargs)
                label = f"{op} with {kwargs}"
                check(f"{label} value", r["value"], None, failures)
                check(f"{label} status", r["status"], "indeterminate", failures)
                check(f"{label} margin", r["margin"], None, failures)

    # NOTE the deliberate IEEE divergence: inf <= 1.0 is False in IEEE, but
    # the documented semantics say unknown. The checks above assert unknown.

    # --- 2. Kleene connective propagation ---
    print("\n=== Kleene propagation: unknown only where the connective needs it ===")
    # A and B where A comes from a non-finite leaf, B from a finite one
    and_ir = IRNode(kind="op", operator="and", operands=[
        ir_cmp("<=", ref("a"), lit(10.0)),   # A: unknown when a is NaN
        ir_cmp("<=", ref("c"), lit(10.0)),   # B: finite
    ])
    src, _ = compile_predicate(and_ir, "pred_and", negated=False)
    fn_and = load_predicate(src, "pred_and")
    check("false and unknown", fn_and(a=NAN, c=99.0)["value"], False, failures)
    check("false and unknown -> violated", fn_and(a=NAN, c=99.0)["status"], "violated", failures)
    check("true and unknown", fn_and(a=NAN, c=1.0)["value"], None, failures)
    check("true and unknown -> indeterminate", fn_and(a=NAN, c=1.0)["status"], "indeterminate", failures)

    or_ir = IRNode(kind="op", operator="or", operands=[
        ir_cmp("<=", ref("a"), lit(10.0)),
        ir_cmp("<=", ref("c"), lit(10.0)),
    ])
    src, _ = compile_predicate(or_ir, "pred_or", negated=False)
    fn_or = load_predicate(src, "pred_or")
    check("true or unknown", fn_or(a=NAN, c=1.0)["value"], True, failures)
    check("true or unknown -> satisfied", fn_or(a=NAN, c=1.0)["status"], "satisfied", failures)
    check("false or unknown", fn_or(a=NAN, c=99.0)["value"], None, failures)

    not_ir = IRNode(kind="op", operator="not", operands=[ir_cmp("<", ref("a"), lit(1.0))])
    src, _ = compile_predicate(not_ir, "pred_not", negated=False)
    fn_not = load_predicate(src, "pred_not")
    check("not unknown", fn_not(a=NAN)["value"], None, failures)

    # --- 3. the probe-2 compound, non-finite in EVERY Boolean position ---
    # combo = A and (B or not C);  A: p_cost<=p_budget, B: p_eta*p_gain>=10, C: p_eta<1
    print("\n=== compound: non-finite in every Boolean position ===")
    combo_ir = IRNode(kind="op", operator="and", operands=[
        ir_cmp("<=", ref("p_cost"), ref("p_budget")),
        IRNode(kind="op", operator="or", operands=[
            ir_cmp(">=",
                   IRNode(kind="op", operator="*", operands=[ref("p_eta"), ref("p_gain")]),
                   lit(10.0)),
            IRNode(kind="op", operator="not",
                   operands=[ir_cmp("<", ref("p_eta"), lit(1.0))]),
        ]),
    ])
    src, _ = compile_predicate(combo_ir, "pred_combo", negated=False)
    fn = load_predicate(src, "pred_combo")
    cases = [
        # (label, kwargs, expected value, expected status)
        ("A=NaN, rest true",
         dict(p_cost=NAN, p_budget=5e3, p_eta=0.35, p_gain=40.0), None, "indeterminate"),
        ("A=+inf cost (IEEE would say False; documented: unknown)",
         dict(p_cost=PINF, p_budget=5e3, p_eta=0.35, p_gain=40.0), None, "indeterminate"),
        ("A false, B=NaN (false and unknown -> False)",
         dict(p_cost=6e3, p_budget=5e3, p_eta=NAN, p_gain=40.0), False, "violated"),
        ("A true, B=NaN via gain, C false rescues (unknown or True -> True)",
         dict(p_cost=3e3, p_budget=5e3, p_eta=2.0, p_gain=NAN), True, "satisfied"),
        ("A true, B=NaN via gain, C true (unknown or False -> unknown)",
         dict(p_cost=3e3, p_budget=5e3, p_eta=0.5, p_gain=NAN), None, "indeterminate"),
        ("A true, B=-inf product true? (-inf>=10 unknown by design), C true",
         dict(p_cost=3e3, p_budget=5e3, p_eta=NINF, p_gain=40.0), None, "indeterminate"),
        ("all three non-finite",
         dict(p_cost=NAN, p_budget=PINF, p_eta=NAN, p_gain=NINF), None, "indeterminate"),
    ]
    for label, kwargs, ev, es in cases:
        r = fn(**kwargs)
        check(f"{label} value", r["value"], ev, failures)
        check(f"{label} status", r["status"], es, failures)
        check(f"{label} margin (compound -> always None)", r["margin"], None, failures)

    # --- 4. margin sign under negation, finite and non-finite ---
    print("\n=== margin sign under negation ===")
    gt_ir = ir_cmp(">", ref("cost"), ref("budget"))
    src, _ = compile_predicate(gt_ir, "pred_neg", negated=True)  # assert not (cost > budget)
    fn_neg = load_predicate(src, "pred_neg")
    r = fn_neg(cost=3000.0, budget=5000.0)
    check("negated satisfied margin positive", r["margin"], 2000.0, failures)
    check("negated satisfied status", r["status"], "satisfied", failures)
    r = fn_neg(cost=6000.0, budget=5000.0)
    check("negated violated margin negative", r["margin"], -1000.0, failures)
    check("negated violated status", r["status"], "violated", failures)
    r = fn_neg(cost=NAN, budget=5000.0)
    check("negated non-finite margin None", r["margin"], None, failures)
    check("negated non-finite status", r["status"], "indeterminate", failures)

    # un-negated counterpart: sign convention must be positive-when-satisfied too
    src, _ = compile_predicate(gt_ir, "pred_pos", negated=False)
    fn_pos = load_predicate(src, "pred_pos")
    r = fn_pos(cost=6000.0, budget=5000.0)
    check("un-negated satisfied margin positive", r["margin"], 1000.0, failures)

    # --- 5. informative: what does live SysIDE return at a non-finite point? ---
    print("\n=== informative live probe: SysIDE at 1.0/0.0 (not gated) ===")
    try:
        from agentic_mbse.sysml.syside_adapter import SysideAdapter, get_syside

        syside = get_syside()
        model_text = """package s2_nf {
    private import ScalarValues::*;
    part def 'NF Plant' {
        attribute p_num : Real = 1.0;
        attribute p_zero : Real = 0.0;
        attribute p_budget : Real = 5000.0;
        assert constraint nf_check { (p_num / p_zero) <= p_budget }
    }
    part nf_plant : 'NF Plant';
}
"""
        tmp = Path(tempfile.mkdtemp(prefix="s2_nf_")) / "nf.sysml"
        tmp.write_text(model_text)
        model, diags = SysideAdapter.load_model([tmp])
        usage = next(
            u for u in SysideAdapter.elements_of_type(model, "AssertConstraintUsage")
            if getattr(u, "name", None) == "nf_check"
        )
        compiler = syside.Compiler()
        value, report = compiler.evaluate(usage.result_expression, scope=usage)
        n_diags = len(list(getattr(report, "diagnostics", []) or []))
        print(f"  live value: {value!r} (type {type(value).__name__}), "
              f"report fatal={getattr(report, 'fatal', None)}, diagnostics={n_diags}")
        for d in list(getattr(report, "diagnostics", []) or [])[:5]:
            print(f"    diag: {d}")
    except Exception as e:  # noqa: BLE001
        print(f"  live probe errored: {e}")

    print(f"\n{'FAILURES:' if failures else 'ALL KLEENE-TABLE CHECKS PASSED'}")
    for f in failures:
        print(f"  - {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
