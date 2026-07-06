#!/usr/bin/env python3
"""D3-3: unresolvable REFERENCE/CHAIN -> param vanishes from BOTH ledgers.

_parse_reference_expression returns (None, None) when the referent is None or its
qualified_name is empty (usage_extractor.py:789-796). _extract_single_binding then
builds BindingInfo(binding_type=REFERENCE, source_path=None). Because it is NOT
UNBOUND, _extract_bindings puts it in `bindings`, so it is NOT in unbound_params.
And CalcUsageData.parameter_bindings (line 126) filters `if b.source_path`, dropping
it from the wired dict. Net: the param is neither wired nor an entry point.

This probe scans fixtures for the vanish signature: a binding with a non-UNBOUND
type but source_path is None (also true for EXPRESSION, which doc 01 documents as a
handled entry-point path — those are labeled). A REFERENCE/CHAIN with source_path=None
is the D3-3 silent double-vanish.

Usage:
    uv run python .project/active/silent-failure-hardening/probes/probe_d3_3_vanish.py
"""
from __future__ import annotations

from pathlib import Path

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.usage_extractor import (
    BindingType,
    extract_calculation_usages,
)

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = sorted((ROOT / "tests" / "fixtures").glob("*"))


def main() -> None:
    hits = 0
    for fix in FIXTURES:
        if not fix.is_dir():
            continue
        ex = SysMLDataExtractor([fix])
        if not ex.load_models():
            continue
        calc_defs = ex.extract_calculation_definitions()
        try:
            usages, _ = extract_calculation_usages(ex.model, calc_defs=calc_defs)
        except Exception:  # noqa: BLE001
            continue
        for u in usages:
            for b in u.bindings:
                if b.source_path is None and b.binding_type in (
                    BindingType.REFERENCE,
                    BindingType.CHAIN,
                ):
                    hits += 1
                    print(f"[VANISH] {fix.name} :: {u.instance_name}.{b.param_name} "
                          f"type={b.binding_type} source_path=None")
                    print(f"         in unbound_params? {b.param_name in u.unbound_params}")
                    print(f"         in parameter_bindings? "
                          f"{b.param_name in u.parameter_bindings}")
    print(f"\nTotal D3-3 vanish-signature bindings across fixtures: {hits}")
    if hits == 0:
        print("None found in current fixtures -> D3-3 is a LATENT gap (parser resolves "
              "well-formed refs). The vanish is code-traceable but not fixture-triggered.")


if __name__ == "__main__":
    main()
