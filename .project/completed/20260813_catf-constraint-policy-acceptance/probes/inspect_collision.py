"""THROWAWAY (Item 5 design stage). Dump the entry points around a rendering collision."""

from __future__ import annotations

import sys
from pathlib import Path

from sysml_codegen.elaboration import elaborate

root = Path(sys.argv[1])
needle = sys.argv[2] if len(sys.argv) > 2 else "n_pumps"

graph = elaborate([root])
for node in getattr(graph, "attribute_nodes", getattr(graph, "attributes", [])):
    name = getattr(node, "qualified_name", "") or ""
    if needle in name:
        print(
            f"{name}\n"
            f"    display={getattr(node, 'display_path', None)}"
            f" value={getattr(node, 'value', None)}"
            f" kind={getattr(node, 'kind', None)}"
        )
