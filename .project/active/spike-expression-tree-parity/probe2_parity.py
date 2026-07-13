"""S2 probe 2: live-oracle parity over the five scoped predicate shapes.

Generates a scratch SysML model per evaluation point (syside has no
value-injection API — values must be literals in the model), loads each
live, and for every assertion:
  - extracts the provisional ExpressionIR (structural only),
  - JSON round-trips it (byte-stability within a load and across loads),
  - compiles it to Python (Kleene three-valued semantics),
  - compares the compiled verdict against the live SysIDE oracle:
      typed usages  -> evaluate(def.result_expression, scope=usage)  [two-step]
      inline usages -> evaluate(usage.result_expression, scope=usage)

Throwaway spike script. Run from repo root:
    uv run python .project/active/spike-expression-tree-parity/probe2_parity.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentic_mbse.sysml.syside_adapter import SysideAdapter, get_syside

from s2_ir import IRNode, compile_predicate, extract_ir, load_predicate

MODEL_TEMPLATE = """package s2_probe {{
    private import ScalarValues::*;

    constraint def 'Cost Within Budget' {{
        in attribute cost : Real;
        in attribute budget : Real;
        cost <= budget
    }}

    constraint def 'Viability Threshold' {{
        in attribute eta : Real;
        in attribute gain : Real;
        in attribute threshold : Real default 10.0;
        eta * gain >= threshold
    }}

    part def 'Probe Plant' {{
        attribute p_cost : Real = {p_cost};
        attribute p_budget : Real = {p_budget};
        attribute p_eta : Real = {p_eta};
        attribute p_gain : Real = {p_gain};

        // typed usage, two-step oracle (WI-014 shape)
        assert constraint affordable : 'Cost Within Budget' {{
            in cost = p_cost;
            in budget = p_budget;
        }}

        // typed usage with a defaulted formal left unbound (IFE viability shape)
        assert constraint viability : 'Viability Threshold' {{
            in eta = p_eta;
            in gain = p_gain;
        }}

        // inline owner-reference predicate
        assert constraint inline_ok {{
            p_cost <= p_budget
        }}

        // negated assertion, inline predicate
        assert not constraint overrun {{
            p_cost > p_budget
        }}

        // compound Boolean
        assert constraint combo {{
            p_cost <= p_budget and (p_eta * p_gain >= 10.0 or not (p_eta < 1.0))
        }}
    }}

    part probe_plant : 'Probe Plant';
}}
"""

# (p_cost, p_budget, p_eta, p_gain) — satisfied / violated / boundary / mixed
POINTS = {
    "P1_sat": dict(p_cost=3000.0, p_budget=5000.0, p_eta=0.35, p_gain=40.0),
    "P2_viol": dict(p_cost=6000.0, p_budget=5000.0, p_eta=0.07, p_gain=100.0),
    "P3_boundary": dict(p_cost=5000.0, p_budget=5000.0, p_eta=0.25, p_gain=40.0),
    "P4_mixed": dict(p_cost=3000.0, p_budget=5000.0, p_eta=2.0, p_gain=1.0),
}

# assertion name -> (source form, formal->point-key mapping for compiled args)
ASSERTIONS = {
    "affordable": ("typed", {"cost": "p_cost", "budget": "p_budget"}),
    "viability": ("typed", {"eta": "p_eta", "gain": "p_gain", "threshold": None}),
    "inline_ok": ("inline", {}),
    "overrun": ("inline", {}),
    "combo": ("inline", {}),
}
DEFAULTS = {"threshold": 10.0}


def find_named(model, type_name, name):
    for e in SysideAdapter.elements_of_type(model, type_name):
        if getattr(e, "name", None) == name:
            return e
    raise LookupError(f"{type_name} {name!r} not found")


def main():
    syside = get_syside()
    compiler = syside.Compiler()
    tmp = Path(tempfile.mkdtemp(prefix="s2_probe_"))

    failures = []
    json_by_assertion: dict[str, set[str]] = {}
    negation_flags = {}
    operator_strs = set()

    for point_name, point in POINTS.items():
        model_file = tmp / f"{point_name}.sysml"
        model_file.write_text(MODEL_TEMPLATE.format(**point))
        model, diags = SysideAdapter.load_model([model_file])
        n_errors = sum(
            1 for d in getattr(diags, "diagnostics", []) or []
            if getattr(d, "severity", None) is not None and int(d.severity) == 1
        )
        print(f"\n=== {point_name} {point} (diag errors: {n_errors}) ===")

        for name, (form, formal_map) in ASSERTIONS.items():
            usage = find_named(model, "AssertConstraintUsage", name)
            negation_flags.setdefault(name, getattr(usage, "is_negated", None))
            negated = bool(getattr(usage, "is_negated", False))

            if form == "typed":
                cdef = getattr(usage, "predicate", None)
                predicate_expr = getattr(cdef, "result_expression", None)
            else:
                predicate_expr = getattr(usage, "result_expression", None)
            if predicate_expr is None:
                failures.append(f"{point_name}/{name}: no predicate expression found")
                continue
            operator_strs.add(str(getattr(predicate_expr, "operator", "")))

            # --- live oracle ---
            live_value, report = compiler.evaluate(predicate_expr, scope=usage)

            # --- IR extraction + JSON round-trip ---
            ir = extract_ir(predicate_expr)
            j1 = ir.to_json()
            j2 = IRNode.from_json(j1).to_json()
            rt_ok = j1 == j2
            json_by_assertion.setdefault(name, set()).add(j1)

            # --- compile + evaluate ---
            src, args = compile_predicate(ir, f"pred_{name}", negated=negated)
            fn = load_predicate(src, f"pred_{name}")
            if form == "typed":
                kwargs = {
                    formal: (DEFAULTS[formal] if pk is None else point[pk])
                    for formal, pk in formal_map.items()
                }
            else:
                kwargs = {a: point[a] for a in args}
            result = fn(**kwargs)

            agree = result["value"] == live_value
            status = "OK " if (agree and rt_ok) else "FAIL"
            print(
                f"  [{status}] {name:<11} form={form:<6} negated={negated!s:<5} "
                f"live={live_value!s:<5} compiled={result['value']!s:<5} "
                f"status={result['status']:<13} margin={result['margin']} "
                f"json_rt={'ok' if rt_ok else 'MISMATCH'}"
            )
            if not agree:
                failures.append(
                    f"{point_name}/{name}: live={live_value!r} compiled={result['value']!r}"
                )
            if not rt_ok:
                failures.append(f"{point_name}/{name}: JSON round-trip not byte-stable")

    print("\n=== cross-load JSON byte-stability ===")
    for name, jsons in json_by_assertion.items():
        stable = len(jsons) == 1
        print(f"  {name}: {'stable' if stable else f'UNSTABLE ({len(jsons)} variants)'}")
        if not stable:
            failures.append(f"{name}: IR JSON differs across model loads")
        else:
            print(f"    {next(iter(jsons))[:200]}")

    print(f"\nis_negated flags: {negation_flags}")
    print(f"str(operator) samples: {sorted(operator_strs)}")

    print(f"\n{'PARITY FAILURES:' if failures else 'ALL PARITY CHECKS PASSED'}")
    for f in failures:
        print(f"  - {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
