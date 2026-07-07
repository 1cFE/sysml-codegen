"""D3-7 probe: attribute-resolution buckets keyed by bare owning_part_name merge.

Intended behavior (doc 16-computed-attributes "AttributeResolution Map",
07-graph-assembly, 15-naming-conventions):
  `_build_attribute_resolution_map` builds `owning_part_name -> {attr -> res}`.
  Each PartDef's FORMULA/EXPOSE attributes should resolve against THAT part's
  own attributes. Two distinct PartDefs must not share a resolution namespace.

Observed defect claim (D3-7): the map is keyed by the BARE `owning_part_name`
  (graph_builder.py ~984), consumed by the same bare name (~1102). Two PartDefs
  named `Widget` in different packages MERGE into one bucket, and same-named
  attributes overwrite first-wins-loses. A FORMULA input then resolves to the
  wrong part's channel — a silent cross-wire that still passes Step-8 validation.

Reproduction: drive the pipeline on the authored two-package fixture, confirm
both computed attrs carry owning_part_name == "Widget" with DIFFERENT QNs, then
call the real `_build_attribute_resolution_map` and show the merged single
bucket (one "result" entry, not two).
"""
from __future__ import annotations

import logging
from pathlib import Path

logging.basicConfig(level=logging.ERROR)

FIX = Path(__file__).parent / "fixtures" / "d37_partname_merge"


def main() -> None:
    from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
    from sysml_codegen.resolution.graph_builder import _build_attribute_resolution_map

    ctx = build_pipeline_context([FIX])

    cas = ctx.computed_attributes
    print(f"computed_attributes extracted: {len(cas)}")
    for ca in cas:
        print(f"  name={ca.name!r} python_name={ca.python_name!r} "
              f"owning_part_name={ca.owning_part_name!r} "
              f"owning_qn={ca.owning_part_qualified_name!r} "
              f"class={ca.classification} compilability={ca.compilability}")

    names = [ca.owning_part_name for ca in cas]
    collision = len(names) != len(set(names))
    print(f"\nowning_part_name collision present: {collision} (names={names})")

    calc_usage_names = {u.instance_name for u in ctx.calc_usages}
    res = _build_attribute_resolution_map(
        cas, ctx.design_attributes, ctx.output_registry, calc_usage_names
    )
    print("\n_build_attribute_resolution_map output:")
    for part_name, attr_map in res.items():
        print(f"  bucket[{part_name!r}] = {{")
        for attr, r in attr_map.items():
            print(f"      {attr!r}: kind={r.kind} channel={r.channel_name!r}")
        print("  }")

    widget_bucket = res.get("Widget", {})
    n_result = 1 if "result" in widget_bucket else 0
    print(f"\nNumber of PartDefs feeding bucket 'Widget': "
          f"{sum(1 for ca in cas if ca.owning_part_name == 'Widget')}")
    print(f"Distinct 'result' entries surviving in bucket 'Widget': {n_result} "
          f"(two authored, so >1 lost to overwrite if this is 1)")
    if collision and len(res.get("Widget", {})) < sum(
        1 for ca in cas if ca.owning_part_name == "Widget"
    ):
        print("VERDICT: CONFIRMED — two PartDefs merged into one bare-name bucket; "
              "same-named attr overwritten (silent cross-wire surface).")


if __name__ == "__main__":
    main()
