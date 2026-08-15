"""SPIKE THROWAWAY — the agentic-mbse validation path over the same scratch fixtures.

Produces row 1b (self-named refused) and finding F-2 (the D-6 owner-qualified false
positive, plus the source_path that explains it).

Run from the repo root, with the license loaded:
    set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
    uv run python .project/active/self-binding-replacement/spike/probe_validation.py
"""

from pathlib import Path

from agentic_mbse.sysml.binding import extract_bindings
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.validation.level2_structure import validate_structure

FIXTURES = Path(".project/active/self-binding-replacement/spike/fixtures")
CASES = [
    "s1_self_named",
    "s2_names_differ",
    "s3_path_named",
    "s4a_qual_one_occ",
    "s4c_qual_multi_leaf",
    "s5_sibling_formal",
    "s7_sibling_in_formal",
]

print("### validate_structure()")
for name in CASES:
    result = validate_structure(str(FIXTURES / name))
    print(f"--- {name}: success={result.success} issues={len(result.issues)}")
    for issue in result.issues:
        print("   ", issue)

print()
print("### extract_bindings() source_path (explains F-2 and F-5)")
for name in ["s1_self_named", "s4a_qual_one_occ", "s3_path_named"]:
    adapter = SysideAdapter()
    loaded = adapter.load_model([FIXTURES / name])
    model = loaded[0] if isinstance(loaded, tuple) else loaded
    print(f"--- {name}")
    for calc_usage in SysideAdapter.elements_of_type(model, "CalculationUsage"):
        for binding in extract_bindings(calc_usage):
            print(
                f"    param={binding.param_name} type={binding.binding_type} "
                f"source_path={binding.source_path!r:.120}"
            )
