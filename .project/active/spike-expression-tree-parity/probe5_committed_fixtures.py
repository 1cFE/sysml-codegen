"""S2 probe 5: the two committed real predicates, end to end.

- wi014_toy `affordable : 'Cost Within Budget'` (cost <= budget); operands at
  the fixture's literals: cost = 4*3*250 = 3000, budget = 5000 (hand-transcribed
  from toy_plant.sysml).
- plant_values `viability : 'Viability Threshold'` (eta * gain >= threshold);
  eta = 0.35 (subtype-retype mechanism a), gain = 40.0, threshold = default
  10.0 (hand-transcribed from library.sysml / design.sysml).

For each: live two-step oracle, IR extraction + JSON round-trip, compiled
verdict at the hand-transcribed operand values, and a check that the committed
predicate's IR tree equals the probe-2 scratch replica's tree modulo the
qualified-name package prefix. Also records syside operand arity as seen live.

Run from repo root:
    uv run python .project/active/spike-expression-tree-parity/probe5_committed_fixtures.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentic_mbse.sysml.syside_adapter import SysideAdapter, get_syside

from s2_ir import IRNode, compile_predicate, extract_ir, load_predicate

REPO = Path(__file__).resolve().parents[3]

CASES = [
    {
        "fixture": "wi014_toy",
        "usage": "affordable",
        "operands": {"cost": 3000.0, "budget": 5000.0},
        "expected_live": True,
    },
    {
        # ORACLE BOUNDARY (probe 7): this usage carries the self-named binding
        # `in gain = gain`, which infinite-recurses in SysIDE's evaluator until
        # the step limit (the known WI-014 trap). The live two-step therefore
        # returns (None, step-limit diagnostic) BY EXPECTATION; the verdict at
        # the hand-transcribed operands comes from the compiled side only.
        "fixture": "plant_values",
        "usage": "viability",
        "operands": {"eta": 0.35, "gain": 40.0, "threshold": 10.0},
        "expected_live": None,
        "expected_compiled": True,
    },
]


def strip_qn(obj):
    """Drop target_qn fields so trees compare structurally across packages."""
    if isinstance(obj, dict):
        return {k: strip_qn(v) for k, v in obj.items() if k != "target_qn"}
    if isinstance(obj, list):
        return [strip_qn(v) for v in obj]
    return obj


def main():
    syside = get_syside()
    compiler = syside.Compiler()
    failures = []

    for case in CASES:
        print(f"\n=== {case['fixture']} / {case['usage']} ===")
        model, _ = SysideAdapter.load_model([REPO / "tests" / "fixtures" / case["fixture"]])
        usage = next(
            u for u in SysideAdapter.elements_of_type(model, "AssertConstraintUsage")
            if getattr(u, "name", None) == case["usage"]
        )
        cdef = usage.predicate
        predicate = cdef.result_expression

        # live two-step
        live, report = compiler.evaluate(predicate, scope=usage)
        n_diags = len(list(getattr(report, "diagnostics", []) or []))
        print(f"  live two-step: {live!r} (diagnostics: {n_diags})")
        if live != case["expected_live"]:
            failures.append(
                f"{case['fixture']}: live={live!r}, expected {case['expected_live']!r}"
            )

        # IR + round-trip + compile at hand-transcribed operands
        ir = extract_ir(predicate)
        j1 = ir.to_json()
        if IRNode.from_json(j1).to_json() != j1:
            failures.append(f"{case['fixture']}: JSON round-trip not byte-stable")
        print(f"  IR: {j1}")

        src, args = compile_predicate(ir, "pred", negated=bool(usage.is_negated))
        fn = load_predicate(src, "pred")
        r = fn(**{a: case["operands"][a] for a in args})
        print(f"  compiled at {case['operands']}: value={r['value']} "
              f"status={r['status']} margin={r['margin']}")
        expected_compiled = case.get("expected_compiled", case["expected_live"])
        if r["value"] != expected_compiled:
            failures.append(
                f"{case['fixture']}: compiled={r['value']!r}, "
                f"expected {expected_compiled!r}"
            )
        if case["expected_live"] is not None and r["value"] != live:
            failures.append(
                f"{case['fixture']}: compiled={r['value']!r} live={live!r}"
            )

    # structural equality with the probe-2 scratch replicas (modulo package QNs)
    print("\n=== committed vs scratch tree (structural, QNs stripped) ===")
    import tempfile

    from probe2_parity import MODEL_TEMPLATE, POINTS

    tmp = Path(tempfile.mkdtemp(prefix="s2_p5_")) / "scratch.sysml"
    tmp.write_text(MODEL_TEMPLATE.format(**POINTS["P1_sat"]))
    scratch_model, _ = SysideAdapter.load_model([tmp])

    for case, scratch_name in ((CASES[0], "affordable"), (CASES[1], "viability")):
        model, _ = SysideAdapter.load_model([REPO / "tests" / "fixtures" / case["fixture"]])
        committed = next(
            u for u in SysideAdapter.elements_of_type(model, "AssertConstraintUsage")
            if getattr(u, "name", None) == case["usage"]
        )
        scratch = next(
            u for u in SysideAdapter.elements_of_type(scratch_model, "AssertConstraintUsage")
            if getattr(u, "name", None) == scratch_name
        )
        a = strip_qn(json.loads(extract_ir(committed.predicate.result_expression).to_json()))
        b = strip_qn(json.loads(extract_ir(scratch.predicate.result_expression).to_json()))
        same = a == b
        print(f"  {case['fixture']}/{case['usage']} vs scratch/{scratch_name}: "
              f"{'identical' if same else 'DIFFERENT'}")
        if not same:
            failures.append(f"{case['fixture']}: committed tree != scratch replica")

    print(f"\n{'FAILURES:' if failures else 'ALL COMMITTED-FIXTURE CHECKS PASSED'}")
    for f in failures:
        print(f"  - {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
