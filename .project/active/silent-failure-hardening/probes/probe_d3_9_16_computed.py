#!/usr/bin/env python3
"""D3-9 / D3-16: computed-attribute silent drops.

D3-9: `_classify_attribute_expression` returns LITERAL when refs==[] (line 93).
      An empty refs list from extract_feature_refs (blind ref-extractor) is
      indistinguishable from a genuine constant, so a computed attr that SHOULD
      have references is silently dropped as LITERAL (extract_computed_attributes
      line 221 `continue`). This probe prints every attr's refs count + class so a
      false-empty can be spotted.

D3-16: EXPOSE_PURE alias production (lines 307-322). If classification is EXPOSE_PURE
       but no ref is in calc_usage_names (e.g. cross-part instance), instance_name
       stays None and `if instance_name and output_name` fails -> alias silently
       skipped, no warning. This probe reports EXPOSE_PURE attrs whose alias count
       does not match (a produced ChannelAlias vs a silently-skipped one).

Usage:
    uv run python .project/active/silent-failure-hardening/probes/probe_d3_9_16_computed.py
"""
from __future__ import annotations

from pathlib import Path

from sysml_codegen.extraction.computed_attribute_extractor import (
    extract_computed_attributes,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor

ROOT = Path(__file__).resolve().parents[4]
# catf_mfe carries cross-part EXPOSE chains; swap fixture as needed.
FIXTURES = [
    ROOT / "tests" / "fixtures" / "catf_mfe_model",
    ROOT / "tests" / "fixtures" / "ife_plant",
    ROOT / "tests" / "fixtures" / "wi014_toy",
]


def calc_usage_names_on(adapter, part_elem) -> set[str]:
    names: set[str] = set()
    for m in part_elem.owned_members:
        if adapter.is_instance(m, "CalculationUsage"):
            names.add(m.name)
    return names


def main() -> None:
    for fix in FIXTURES:
        if not fix.exists():
            continue
        print("=" * 70)
        print(f"fixture: {fix.name}")
        ex = SysMLDataExtractor([fix])
        if not ex.load_models():
            print("  (failed to load)")
            continue
        adapter = ex.adapter
        for part in adapter.elements_of_type(ex.model, "PartDefinition"):
            _report_part(adapter, part)
        for part in adapter.elements_of_type(ex.model, "PartUsage"):
            _report_part(adapter, part)


def _report_part(adapter, part) -> None:
    cun = calc_usage_names_on(adapter, part)
    try:
        cas, aliases = extract_computed_attributes(adapter, part, cun)
    except Exception as e:  # noqa: BLE001
        print(f"  part {getattr(part, 'name', '?')}: ERROR {e}")
        return
    if not cas:
        return
    alias_names = {a.alias_name for a in aliases}
    for ca in cas:
        n_refs = len(ca.references)
        marker = ""
        if ca.classification.value == "EXPOSE_PURE" and ca.python_name not in alias_names:
            marker = "  <-- D3-16 EXPOSE_PURE but NO alias produced (silent skip?)"
        print(f"  {ca.owning_part_name}.{ca.name}: class={ca.classification.value} "
              f"refs={n_refs} chain={ca.reference_chain}{marker}")


if __name__ == "__main__":
    main()
