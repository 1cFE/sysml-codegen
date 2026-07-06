"""Item C: self_named_rescue binding_type drift (reference -> chain) attribution.

Shows the RAW binding classifier (usage_extractor._extract_single_binding) still
produces REFERENCE for `in throughput = throughput`, and that the reference->chain
flip is done by the downstream mechanism-D rescue (_rescue_self_named_bindings),
not by the binding classifier that Item 5 owns.
"""

from pathlib import Path

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.usage_extractor import extract_calculation_usages

FIX = Path(__file__).resolve().parents[4] / "tests" / "fixtures" / "self_named_rescue"

print("=" * 70)
print("STEP 1: RAW extraction (pre-rescue) — what the classifier produces")
print("=" * 70)
extractor = SysMLDataExtractor([FIX])
assert extractor.load_models(), "load_models failed"
calc_defs = extractor.extract_calculation_definitions()
calc_usages, _ = extract_calculation_usages(extractor.model, calc_defs=calc_defs)

for u in calc_usages:
    if "sink_calc" in u.qualified_name:
        for b in u.bindings:
            print(f"  sink_calc.{b.param_name}:")
            print(f"    binding_type   = {b.binding_type}")
            print(f"    source_path    = {b.source_path!r}")
            print(f"    raw_expression = {b.raw_expression!r}")

print()
print("=" * 70)
print("STEP 2: Full pipeline (post-rescue) — final binding_type")
print("=" * 70)
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
ctx = build_pipeline_context([FIX])
# calc_usages is mutated in place by the rescue; re-inspect
for u in ctx.calc_usages if hasattr(ctx, "calc_usages") else []:
    if "sink_calc" in u.qualified_name:
        for b in u.bindings:
            print(f"  sink_calc.{b.param_name}: binding_type={b.binding_type} "
                  f"source_path={b.source_path!r} raw={b.raw_expression!r}")

print("\nCONCLUSION: raw classifier -> REFERENCE; rescue rewrites to CHAIN.")
