"""Site 1: snapshot/loader.py load-bearing `.get(field, default)` calls.

Reproduce: hand-edit a real snapshot dict, delete a candidate load-bearing
field, run the deserializer, show the fallback silently substitutes with no
diagnostic today.

Gate: scan every SNAPSHOT_MODELS raw JSON for missing load-bearing fields —
if none are missing, the new diagnostic fires on zero clean snapshots.
"""

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG, format="LOG %(levelname)s %(name)s: %(message)s")

from sysml_codegen.snapshot.loader import _deserialize_attribute_info, _deserialize_calc_usage

FIXTURES_DIR = Path(__file__).resolve().parents[4] / "tests" / "fixtures"

SNAPSHOT_MODELS = [
    "sample_model", "solar_battery_model", "catf_mfe_model", "attr_expr_probe",
    "chain_spike_model", "issue22_model", "expression_binding_probe",
    "chain_override_probe", "unresolvable_attr_probe", "alias_agg_probe",
    "wi014_toy", "ife_plant", "self_named_binding_trap",
    "plant_values", "plant_value_shapes",
]

VALID_ATTR = {
    "name": "cost",
    "sysml_type": "ScalarValues::Real",
    "default_value": "1.0",
    "binding_type": "unbound",
    "is_input": True,
    "is_output": False,
    "python_type": "float",
    "description": "",
    "unit": None,
    "source_line": 12,
    "is_optional": False,
}

VALID_USAGE = {
    "instance_name": "calc1",
    "calc_def_name": "CalcDef",
    "calc_def_qualified_name": "Pkg::CalcDef",
    "module_type": "CalcDefModule",
    "bindings": [],
    "unbound_params": [],
    "source_file": "model.sysml",
    "source_line": 3,
    "parent_part_path": "Pkg::Part1",
    "qualified_name": "Pkg::Part1::calc1",
    "is_template": False,
    "owning_part_def_qn": "Pkg::PartDef1",
}

print("=" * 70)
print("REPRODUCE — attribute-info load-bearing fields")
print("=" * 70)
for field in ("python_type", "binding_type"):
    d = dict(VALID_ATTR)
    del d[field]
    result = _deserialize_attribute_info(d)
    print(f"  delete {field!r:20} -> "
          f"python_type={result.python_type!r} binding_type={result.binding_type!r}")

print()
for field in ("parent_part_path", "qualified_name", "owning_part_def_qn"):
    d = dict(VALID_USAGE)
    del d[field]
    result = _deserialize_calc_usage(d)
    print(f"  delete {field!r:20} -> "
          f"parent_part_path={result.parent_part_path!r} "
          f"qualified_name={result.qualified_name!r} "
          f"owning_part_def_qn={result.owning_part_def_qn!r}")

print()
print("=" * 70)
print("CORPUS SCAN — every SNAPSHOT_MODELS raw JSON, checking for missing")
print("load-bearing fields on attribute_info / calc_usage dicts")
print("=" * 70)

LOAD_BEARING_ATTR_FIELDS = ["python_type", "binding_type"]
LOAD_BEARING_USAGE_FIELDS = ["parent_part_path", "qualified_name", "owning_part_def_qn"]

hits = 0
for name in SNAPSHOT_MODELS:
    path = FIXTURES_DIR / name / "extraction_snapshot.json"
    if not path.exists():
        print(f"  {name}: MISSING SNAPSHOT FILE")
        continue
    data = json.loads(path.read_text())
    calc_defs = data.get("calc_defs", [])
    for cd in calc_defs:
        for attr_list_name in ("input_attributes", "output_attributes"):
            for attr in cd.get(attr_list_name, []):
                for field in LOAD_BEARING_ATTR_FIELDS:
                    if field not in attr:
                        hits += 1
                        print(f"  {name}: calc_def {cd.get('name')} {attr_list_name} "
                              f"attr {attr.get('name')} missing {field!r}")
    calc_usages = data.get("calc_usages", [])
    for cu in calc_usages:
        for field in LOAD_BEARING_USAGE_FIELDS:
            if field not in cu:
                hits += 1
                print(f"  {name}: calc_usage {cu.get('instance_name')} missing {field!r}")

print(f"\nTotal missing-field hits across corpus: {hits}")
