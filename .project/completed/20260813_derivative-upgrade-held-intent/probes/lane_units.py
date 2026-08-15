"""Report each lane's per-port `unit` for the consumers that collide.

Answers the mechanism question the refusal leaves open: does the calc lane read the real
fixture's calc-def unit comments at all? Uses the same accessor Item 8's own conformance
test uses (`node.input_metadata` keyed through `node.input_names`).

Usage:  python lane_units.py <fixture-root> <display-path-suffix> [...]
"""

from __future__ import annotations

import sys
from pathlib import Path

from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths


def main() -> int:
    root = Path(sys.argv[1])
    graph = elaborate_model_paths([root])
    for suffix in sys.argv[2:]:
        matches = [
            node
            for nodes in (graph.calcs, graph.constraints)
            for node in nodes.values()
            if node.display_path.endswith(suffix)
        ]
        print(f"\n=== {suffix} -> {len(matches)} node(s)")
        for node in matches:
            print(f"  {node.display_path}")
            for port, metadata in node.input_metadata.items():
                print(f"    {node.input_names[port]:28} unit={metadata.unit!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
