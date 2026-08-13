"""THROWAWAY (Item 5 design stage). Show WHICH EntryPoint fields collide.

Wraps `_ProjectionState._entry_source` so the two candidates are printed field by field
before the projection fails.
"""

from __future__ import annotations

import sys
from pathlib import Path

import importlib

from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline

project_module = importlib.import_module("sysml_codegen.elaboration.project")


def _patch() -> None:
    owner_cls = project_module._Projection
    original = owner_cls._entry_source

    def traced(self, **kwargs):  # noqa: ANN001, ANN003
        qn = kwargs["qualified_name"]
        existing = self.entry_points.get(qn)
        try:
            return original(self, **kwargs)
        except Exception:
            candidate = self.entry_points.get(qn)
            print(f"\nCOLLISION on {qn}")
            print(f"  incoming kwargs: {kwargs}")
            if existing is not None:
                for field in type(existing).model_fields:
                    print(f"    existing.{field} = {getattr(existing, field)!r}")
            print(f"  (post-state candidate: {candidate!r})")
            raise

    owner_cls._entry_source = traced


_patch()
try:
    build_elaborated_pipeline([Path(sys.argv[1])])
    print("no collision")
except Exception as error:  # noqa: BLE001
    print(f"{type(error).__name__}: {error}")
