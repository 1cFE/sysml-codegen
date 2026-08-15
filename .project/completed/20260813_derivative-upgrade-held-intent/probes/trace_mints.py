"""Log every entry-point mint for the colliding keys, with the consumer that minted it.

The refusal names the key but not the two lanes that disagree. This records, per mint:
the consumer node's class, its source location, and the `unit_text` that lane produced —
which is what says whether the disagreement is calc-lane-vs-constraint-lane and which side
carries `None`.

Usage:  python trace_mints.py <fixture-root> <key-substring> [<key-substring> ...]
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths

project_module = importlib.import_module("sysml_codegen.elaboration.project")


def main() -> int:
    root = Path(sys.argv[1])
    wanted = sys.argv[2:]
    owner_class = project_module._Projection
    original = owner_class._entry_source
    log: list[str] = []

    def traced(self, **kwargs):
        qualified_name = kwargs["qualified_name"]
        if any(token in qualified_name for token in wanted):
            owner = kwargs["owner"]
            location = (
                f"{getattr(owner, 'source_file', '?')}:{getattr(owner, 'source_line', '?')}"
            )
            log.append(
                f"{qualified_name}\n"
                f"    minted by {type(owner).__name__} "
                f"{getattr(owner, 'declaration_qn', getattr(owner, 'display_path', '?'))}\n"
                f"    at {location}\n"
                f"    unit_text={kwargs['metadata'].unit!r} "
                f"entry_type={kwargs['entry_type']}"
            )
        try:
            return original(self, **kwargs)
        except project_module.ProjectionError as error:
            log.append(f"    >>> REFUSED: {error}")
            existing = self.entry_points[qualified_name]
            return project_module.InputSource(
                source_type="entry_point",
                param_group=existing.param_group,
                qualified_name=existing.qualified_name,
            )

    owner_class._entry_source = traced
    project_module.project(elaborate_model_paths([root]))
    print("\n".join(log))
    return 0


if __name__ == "__main__":
    sys.exit(main())
