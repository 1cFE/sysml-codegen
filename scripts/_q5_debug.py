#!/usr/bin/env python3
"""Quick Q5 debug: trace Key_F and FORMULA canonical channels."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sysml_codegen.core.identifier_types import CanonicalChannel, ScopedKey
from sysml_codegen.core.qualified_names import get_channel_name, sysml_to_python_qualified_name
from sysml_codegen.extraction.data_models import ComputedAttributeClassification
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from tests.helpers.snapshot_loader import load_extraction_snapshot

snap = load_extraction_snapshot("solar_battery_model")

# Show all FORMULA computed attributes and their Key_F
print("=== FORMULA computed attributes ===")
for ca in snap["computed_attributes"]:
    if ca.classification != ComputedAttributeClassification.FORMULA:
        continue
    if ca.compilability != Compilability.FULLY_COMPILABLE:
        continue
    part_qn_python = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
    module_eqn = f"{part_qn_python}__{ca.python_name}"
    canonical = CanonicalChannel(get_channel_name(module_eqn, ca.python_name))
    key_f = f"{ca.owning_part_name}.{ca.python_name}"
    print(f"  name={ca.name} Key_F={key_f} canonical={canonical}")

# Build registry and check what solar_battery_plant.p_net_kw resolves to
registry = build_output_registry(
    calc_usages=snap["calc_usages"],
    calc_defs=snap["calc_defs"],
    aggregation_data=snap["aggregation_expressions"],
    computed_attributes=snap["computed_attributes"],
    channel_aliases=snap.get("channel_aliases", []),
    design_attributes=snap.get("design_attributes", {}),
)

print("\n=== solar_battery_plant.p_net_kw resolution trace ===")
key = "solar_battery_plant.p_net_kw"
print(f"  _compat['{key}'] = {registry._compat.get(key)}")
print(f"  scoped_lookup = {registry.scoped_lookup(ScopedKey(key))}")
print(f"  alias_lookup = {registry.alias_lookup(ScopedKey(key))}")

# Check p_net_kw CalcUsage canonical
calc_def_by_name = {cd.name: cd for cd in snap["calc_defs"]}
for usage in snap["calc_usages"]:
    if "p_net_kw" in usage.instance_name:
        cd = calc_def_by_name.get(usage.calc_def_name)
        if cd and cd.output_attributes:
            from sysml_codegen.core.identifier_types import make_canonical_channel
            canonical = make_canonical_channel(usage.qualified_name, cd.output_attributes[0].name)
            print(f"\n  CalcUsage p_net_kw: canonical={canonical}")

# Count of all compat keys not reachable via scoped or alias
print("\n=== Compat keys unreachable via typed lookups ===")
unreachable = 0
for k, v in registry._compat.items():
    scoped = registry.scoped_lookup(ScopedKey(k))
    alias = registry.alias_lookup(ScopedKey(k))
    if scoped is None and alias is None:
        unreachable += 1
print(f"  Total compat keys: {len(registry._compat)}")
print(f"  Unreachable via typed: {unreachable}")

# Show what Key_F compat entries need to become scoped registrations
print("\n=== Key_F entries that need scoped registration ===")
for ca in snap["computed_attributes"]:
    if ca.classification != ComputedAttributeClassification.FORMULA:
        continue
    if ca.compilability != Compilability.FULLY_COMPILABLE:
        continue
    key_f = f"{ca.owning_part_name}.{ca.python_name}"
    part_qn_python = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
    module_eqn = f"{part_qn_python}__{ca.python_name}"
    canonical = CanonicalChannel(get_channel_name(module_eqn, ca.python_name))
    compat_val = registry._compat.get(key_f)
    scoped_val = registry.scoped_lookup(ScopedKey(key_f))
    if compat_val is not None and scoped_val is None:
        print(f"  NEEDS SCOPED: Key_F={key_f} -> compat={compat_val}")
        # Check if compat_val equals the FORMULA canonical or the CalcUsage canonical
        print(f"    FORMULA canonical={canonical}")
        print(f"    Same as compat? {compat_val == canonical}")
