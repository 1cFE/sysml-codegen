"""THROWAWAY (Item 5 design stage). Dump entry points matching a substring."""

from __future__ import annotations

import sys
from pathlib import Path

from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline

graph = build_elaborated_pipeline([Path(sys.argv[1])])
needle = sys.argv[2] if len(sys.argv) > 2 else ""
for group in graph.entry_point_groups:
    for parameter in group.parameters:
        if needle in parameter.qualified_name:
            print(
                f"{parameter.qualified_name}\n"
                f"    type={parameter.entry_type} default={parameter.default_value}"
                f" unit={parameter.unit_text!r} group={group.name}"
            )
