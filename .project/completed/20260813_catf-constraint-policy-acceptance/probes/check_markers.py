"""THROWAWAY (Item 5 Phase 1). Did the five @inapplicable markers reach the domain?

The population oracle's rule 3 says SysIDE drops a `doc` comment inside an inline-predicate
constraint body, so on that shape a marker never elaborates. B1-B5 are exactly that shape.
This measures it rather than inferring it.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, "/home/reid/1cfe/sysml-codegen-item7-rebuild")
from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from tests.helpers.constraint_source_scan import scan_inapplicable_markers

root = Path(sys.argv[1])
written = scan_inapplicable_markers(root)
graph = elaborate_model_paths([root])
carried = [
    (r.usage_qualified_name, r.inapplicability)
    for r in graph.constraint_usages.values()
    if r.inapplicability is not None
]
print(f"markers written in source: {len(written)}")
for ref, line in written:
    print(f"  WRITTEN {ref}:{line}")
print(f"markers carried on the domain: {len(carried)}")
for qn, inap in carried:
    print(f"  CARRIED {qn} -> {inap}")
