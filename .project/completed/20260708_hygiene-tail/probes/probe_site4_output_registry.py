"""Site 4: orchestration/output_registry_builder.py Phase 4 no-`else`.

Reproduce: a design attribute with a transitive default (dotted path,
is_transitive_default True) that fails all three Phase-4 lookups
(instance_attr_to_channel / scoped_lookup / alias_lookup) — no warning fires
today, unlike sibling Phases 2/3.

Gate: scan SNAPSHOT_MODELS for a design attribute with an unresolved
transitive default (none expected — matches byte-identical baselines).
"""

import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG, format="LOG %(levelname)s %(name)s: %(message)s")

from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.core.output_registry import is_transitive_default
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from sysml_codegen.snapshot.loader import load_extraction_snapshot
from tests.conftest import snapshot_fixture

SNAPSHOT_MODELS = [
    "sample_model", "solar_battery_model", "catf_mfe_model", "attr_expr_probe",
    "chain_spike_model", "issue22_model", "expression_binding_probe",
    "chain_override_probe", "unresolvable_attr_probe", "alias_agg_probe",
    "wi014_toy", "ife_plant", "self_named_binding_trap",
    "plant_values", "plant_value_shapes",
]

print("=" * 70)
print("REPRODUCE — unresolved transitive design-attribute default")
print("=" * 70)

attr = DesignAttributeData(
    name="misc_cost",
    sysml_type="ScalarValues::Real",
    default_value="nonexistent_module.nonexistent_channel",
    unit=None,
    source_file=Path("design.sysml"),
    source_line=1,
    parent_part="Design__plant",
    qualified_name="Design__plant__misc_cost",
)
assert is_transitive_default(attr.default_value)

registry = build_output_registry(
    calc_usages=[],
    calc_defs=[],
    aggregation_data=[],
    computed_attributes=[],
    channel_aliases=[],
    design_attributes={Path("design.sysml"): [attr]},
)
from sysml_codegen.core.identifier_types import ScopedKey

resolved_check = (
    registry.scoped_lookup(ScopedKey("nonexistent_module.nonexistent_channel"))
    or registry.alias_lookup(ScopedKey("nonexistent_module.nonexistent_channel"))
)
print(f"  resolved (should be None): {resolved_check!r}")
print("  (expected: no warning was logged above for the dropped alias — that's the gap)")

print()
print("=" * 70)
print("CORPUS SCAN — every SNAPSHOT_MODELS design attribute with an")
print("unresolved transitive default")
print("=" * 70)

hits = 0
for name in SNAPSHOT_MODELS:
    snap = load_extraction_snapshot(snapshot_fixture(name))
    design_attrs = snap.get("design_attributes", {})
    calc_usages = snap.get("calc_usages", [])
    calc_defs = snap.get("calc_defs", [])
    aggregation_data = snap.get("aggregation_expressions", [])
    computed_attributes = snap.get("computed_attributes", [])
    channel_aliases = snap.get("channel_aliases", [])
    reg = build_output_registry(
        calc_usages=calc_usages,
        calc_defs=calc_defs,
        aggregation_data=aggregation_data,
        computed_attributes=computed_attributes,
        channel_aliases=channel_aliases,
        design_attributes=design_attrs,
    )
    from sysml_codegen.core.identifier_types import ScopedKey
    for _path, attrs in design_attrs.items():
        for a in attrs:
            if not is_transitive_default(a.default_value):
                continue
            val = str(a.default_value)
            resolved = (
                reg.scoped_lookup(ScopedKey(val))
                or reg.alias_lookup(ScopedKey(val))
            )
            if not resolved:
                hits += 1
                print(f"  {name}: design attr {a.qualified_name} unresolved "
                      f"transitive default {a.default_value!r}")

print(f"\nTotal unresolved transitive defaults across corpus: {hits}")
