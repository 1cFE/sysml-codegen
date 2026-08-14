"""Enumerate EVERY entry-point metadata collision, instead of stopping at the first.

`project()` refuses on the first SI_RENDERING_COLLISION, so a single run says nothing about
how large the refusing set is. This swallows each collision (keeping the first-minted entry)
and reports them all, so the design can state exactly which ruled forms refuse.

Usage:  python collect_collisions.py <fixture-root>
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths

project_module = importlib.import_module("sysml_codegen.elaboration.project")


def main() -> int:
    root = Path(sys.argv[1])
    owner_class = project_module._Projection
    original = owner_class._entry_source
    collisions: list[tuple[str, str, str]] = []

    def traced(self, **kwargs):
        qualified_name = kwargs["qualified_name"]
        existing = self.entry_points.get(qualified_name)
        try:
            return original(self, **kwargs)
        except project_module.ProjectionError:
            metadata = kwargs["metadata"]
            if existing is None:
                raise
            fields = []
            for label, was, now in (
                ("entry_type", existing.entry_type, kwargs["entry_type"]),
                ("unit_text", existing.unit_text, metadata.unit),
                ("python_type", existing.python_type, metadata.python_type),
                ("default_value", existing.default_value, kwargs["default_value"]),
                ("source_calc_usage", existing.source_calc_usage, kwargs["source_calc_usage"]),
            ):
                if was != now:
                    fields.append(f"{label}: {was!r} -> {now!r}")
            collisions.append((qualified_name, "; ".join(fields), kwargs["owner"].source_line))
            return project_module.InputSource(
                source_type="entry_point",
                param_group=existing.param_group,
                qualified_name=existing.qualified_name,
            )

    owner_class._entry_source = traced

    graph = elaborate_model_paths([root])
    print(f"elaboration ADMITTED ({len(graph.nodes) if hasattr(graph, 'nodes') else '?'} nodes)")
    try:
        complete = project_module.project(graph)
    except Exception as error:  # noqa: BLE001 - the point is to report, not to handle
        print(f"projection still refused: {type(error).__name__}: {error}")
        complete = None

    print(f"\ncollisions collected: {len(collisions)}")
    for qualified_name, diff, line in collisions:
        print(f"  {qualified_name}  (radial_build.sysml:{line})\n      {diff}")

    if complete is not None:
        print(f"\nmodules: {len(complete.modules)}")
        print(f"entry points: {len(complete.entry_points)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
