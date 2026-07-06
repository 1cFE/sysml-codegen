#!/usr/bin/env python3
"""D3-2: 3+-segment CHAIN binding truncates to 2 segments (no warning).

deep_cross_scope_probe Pattern A binds `data_point = station.array.derived_calc.derived_value`
(4 segments). Doc/design comment expects source_path == the full 4-segment chain.
_parse_chain_expression only takes operands[0] name + target_feature name = 2 segments.

Usage:
    uv run python .project/active/silent-failure-hardening/probes/probe_d3_2_chain_truncation.py
"""
from __future__ import annotations

from pathlib import Path

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.usage_extractor import extract_calculation_usages

FIX = Path(__file__).resolve().parents[4] / "tests" / "fixtures" / "deep_cross_scope_probe"


def main() -> None:
    ex = SysMLDataExtractor([FIX])
    assert ex.load_models(), f"failed to load {FIX}"
    calc_defs = ex.extract_calculation_definitions()
    usages, report = extract_calculation_usages(ex.model, calc_defs=calc_defs)

    print(f"fixture: {FIX}")
    print(f"warnings from extraction ({len(report.warnings)}):")
    for w in report.warnings:
        print(f"  - {w}")

    for u in usages:
        if u.instance_name != "chain_analysis":
            continue
        print(f"\ncalc usage: {u.instance_name}  ({u.qualified_name})")
        for b in u.bindings:
            print(f"  param={b.param_name!r} type={b.binding_type} "
                  f"source_path={b.source_path!r}")
            if b.param_name == "data_point":
                expected = "station.array.derived_calc.derived_value"
                got = b.source_path or ""
                segs = got.count(".") + 1 if got else 0
                print(f"\n  EXPECTED (design comment): {expected!r} (4 segments)")
                print(f"  OBSERVED source_path:      {got!r} ({segs} segments)")
                print(f"  TRUNCATED: {segs < 4}")
        print(f"  unbound_params: {u.unbound_params}")


if __name__ == "__main__":
    main()
