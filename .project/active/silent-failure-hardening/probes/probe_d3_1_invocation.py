#!/usr/bin/env python3
"""D3-1: InvocationExpression binding RHS silently becomes UNBOUND (entry point).

An input bound to a function call (`in x = max(a, b)`) is an InvocationExpression.
_extract_single_binding dispatches FCE / FRE / literal / OperatorExpression only;
anything else falls through to BindingType.UNBOUND (usage_extractor.py:748) with NO
warning. _extract_bindings then routes UNBOUND -> unbound_params, so the model's real
binding is discarded and the param silently becomes a JSON entry point.

Doc 01 (01-extraction.md:147) defines UNBOUND as "no binding expression at all" —
but here an expression DOES exist. That is the code-vs-doc divergence.

Usage:
    uv run python .project/active/silent-failure-hardening/probes/probe_d3_1_invocation.py
"""
from __future__ import annotations

from pathlib import Path

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.usage_extractor import extract_calculation_usages

FIX = Path(__file__).resolve().parent / "fixtures" / "invocation_binding_probe"


def main() -> None:
    ex = SysMLDataExtractor([FIX])
    assert ex.load_models(), f"failed to load {FIX}"
    calc_defs = ex.extract_calculation_definitions()
    usages, report = extract_calculation_usages(ex.model, calc_defs=calc_defs)

    print(f"fixture: {FIX}")
    print(f"extraction warnings ({len(report.warnings)}): {report.warnings}")
    for u in usages:
        if u.instance_name != "c":
            continue
        print(f"\ncalc usage: {u.instance_name}")
        print(f"  bindings ({len(u.bindings)}):")
        for b in u.bindings:
            print(f"    {b.param_name}: type={b.binding_type} source={b.source_path!r} "
                  f"raw={b.raw_expression!r}")
        print(f"  unbound_params: {u.unbound_params}")
        print("\n  EXPECTED: 'x' is a real binding (an invocation).")
        print("  OBSERVED: 'x' in unbound_params (silent entry point), binding discarded,"
              " no warning.")


if __name__ == "__main__":
    main()
