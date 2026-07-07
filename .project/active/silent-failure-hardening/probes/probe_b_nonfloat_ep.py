"""Item B: non-float entry-point literals dropped by float(value_str).

Drives extraction on plant_value_shapes (Item-1 fixture carrying bool/string/enum
value shapes) and shows the enum-valued `wall` entry point vanishing from the
derived parameter groups, plus whether any diagnostic fires.
"""

import logging
from pathlib import Path

# Capture ALL logs so we can see whether the drop emits a warning/debug or nothing.
logging.basicConfig(level=logging.DEBUG, format="LOG %(levelname)s %(name)s: %(message)s")

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.usage_extractor import extract_calculation_usages
from sysml_codegen.analysis.parameter_groups import (
    ParameterGroupDeriver,
    extract_design_attributes,
)

FIX = Path(__file__).resolve().parents[4] / "tests" / "fixtures" / "plant_value_shapes"

print("=" * 70)
print("Loading fixture:", FIX)
extractor = SysMLDataExtractor([FIX])
assert extractor.load_models(), "load_models failed"

calc_defs = extractor.extract_calculation_definitions()
calc_usages, _ = extract_calculation_usages(extractor.model, calc_defs=calc_defs)
design_attrs = extract_design_attributes(extractor.model)

print("\n--- DESIGN ATTRIBUTES (name -> default_value string, sysml_type) ---")
for fp, attrs in design_attrs.items():
    for a in attrs:
        print(f"  {a.qualified_name:45} default={a.default_value!r:30} type={a.sysml_type!r}")

print("\n--- CALC USAGE BINDINGS (looking for `wall`) ---")
for u in calc_usages:
    for b in u.bindings:
        if "wall" in (b.param_name or "") or "wall" in (b.source_path or ""):
            print(f"  {u.qualified_name}.{b.param_name}: type={b.binding_type} "
                  f"source_path={b.source_path!r} literal={getattr(b,'literal_value',None)!r}")

print("\n" + "=" * 70)
print("DERIVE PARAMETER GROUPS")
print("=" * 70)
deriver = ParameterGroupDeriver(design_attrs, calc_usages, calc_defs)
groups = deriver.derive_groups()

all_params = []
for g in groups:
    print(f"\n  Group {g.name} ({g.source_type}):")
    for p in g.parameters:
        all_params.append(p.name)
        print(f"    {p.name:50} default={p.default_value!r} type={p.sysml_type!r}")

print("\n--- PRESENCE CHECK ---")
wall_params = [n for n in all_params if "wall" in n.lower()]
foot_params = [n for n in all_params if "footprint" in n.lower()]
print(f"  params mentioning 'wall'     : {wall_params}   (enum-valued, expected DROPPED)")
print(f"  params mentioning 'footprint': {foot_params}   (float 12.0, expected PRESENT)")

print("\n--- DIRECT _parse_default_value BEHAVIOR ---")
for v in ["12.0", "'Wall Kind'::liquid_wall", "liquid_wall", "true", "hello"]:
    print(f"  _parse_default_value({v!r:28}) -> {deriver._parse_default_value(v)!r}")
