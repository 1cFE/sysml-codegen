"""Print both colliding `EntryPoint` candidates for an SI_RENDERING_COLLISION.

The refusal message names only the qualified name, so it does not say *which field*
disagrees. This wraps the projection's mint step and dumps the field-level diff.

Usage:  python diagnose_collision.py <fixture-root>
"""

from __future__ import annotations

import sys
from pathlib import Path

import importlib

from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths

# `sysml_codegen.elaboration.__init__` re-exports the `project()` *function* under the same
# name as the submodule, so `import ... as` would hand back the function. Go via importlib.
project_module = importlib.import_module("sysml_codegen.elaboration.project")


def main() -> int:
    root = Path(sys.argv[1])

    # Find the class that owns `_entry_source` without assuming its name.
    owner_class = None
    for name in dir(project_module):
        candidate = getattr(project_module, name)
        if isinstance(candidate, type) and "_entry_source" in vars(candidate):
            owner_class = candidate
            break
    assert owner_class is not None, "no class owning _entry_source found"
    print(f"instrumenting {owner_class.__name__}._entry_source")

    original = owner_class._entry_source

    def traced(self, **kwargs):
        qualified_name = kwargs["qualified_name"]
        existing = self.entry_points.get(qualified_name)
        try:
            return original(self, **kwargs)
        except Exception:
            metadata = kwargs["metadata"]
            print(f"\nCOLLISION on {qualified_name}")
            print(f"  existing: {existing!r}")
            print(f"  owner:    {kwargs['owner']!r}")
            print(f"  entry_type={kwargs['entry_type']} default={kwargs['default_value']!r}")
            print(f"  metadata: python_type={metadata.python_type} unit={metadata.unit!r}")
            if existing is not None:
                print(
                    f"  DIFF entry_type {existing.entry_type} vs {kwargs['entry_type']}; "
                    f"unit {existing.unit_text!r} vs {metadata.unit!r}; "
                    f"python_type {existing.python_type} vs {metadata.python_type}; "
                    f"default {existing.default_value!r} vs {kwargs['default_value']!r}; "
                    f"source_calc_usage {existing.source_calc_usage!r} vs "
                    f"{kwargs['source_calc_usage']!r}"
                )
            raise

    owner_class._entry_source = traced

    graph = elaborate_model_paths([root])
    project_module.project(graph)
    print("projected cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
