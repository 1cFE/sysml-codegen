"""Item 4 — dump every fixture's entry points as (qualified_name -> default_value).

Run once with the carry applied and once at the predecessor, then diff. This is
the instrument for Gate 2's "default carried" and "numeric result" columns and
for DD-R29's requirement that every moved entry point kept its correct modeled
default: a pure key rename shows as a key move with the value preserved, while a
value change shows as the same key carrying a different number.

Run: ``uv run python scripts/probes/probe_item4_entrypoints.py <out.json>``
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures"


def main() -> None:
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )

    out: dict[str, dict[str, object]] = {}
    for snapshot in sorted(FIXTURES.glob("*/extraction_snapshot.json")):
        try:
            context = build_pipeline_context_from_snapshot(snapshot)
        except Exception as exc:  # noqa: BLE001 - probe reports, never masks
            out[snapshot.parent.name] = {"__error__": f"{type(exc).__name__}: {exc}"}
            continue
        out[snapshot.parent.name] = {
            parameter.qualified_name: parameter.default_value
            for group in context.computation_graph.entry_point_groups
            for parameter in group.parameters
        }

    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, sort_keys=True, default=str))
    print(f"wrote {sys.argv[1]}")


if __name__ == "__main__":
    main()
