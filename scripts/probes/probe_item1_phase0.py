"""Phase 0 de-risk probe for UPSTREAM-FINDINGS Item 1 (throwaway).

Settles the two live-only uncertainties before any production code changes:
  Probe 1 (SC-7): which _resolve_expose_pure warning a shape-A fixture fires.
  Probe 2 (constraints): the ConstraintUsage enumeration mechanism + owner reach.
  Probe 3 (zero-output): confirm the fixture reaches the zero-output condition.

Run once with a live license:
    uv run --env-file ~/1cfe/agentic-mbse/.env python scripts/probes/probe_item1_phase0.py
"""

from __future__ import annotations

import logging
from pathlib import Path

from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

FIXTURES = Path(__file__).parent.parent.parent / "tests" / "fixtures"


class _Capture(logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=logging.INFO)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def probe1_expose() -> None:
    print("\n=== Probe 1: SC-7 EXPOSE_PURE warning (shape A) ===")
    cap = _Capture()
    root = logging.getLogger("sysml_codegen")
    root.addHandler(cap)
    root.setLevel(logging.INFO)
    build_pipeline_context([FIXTURES / "expose_pure_shape_a"])
    root.removeHandler(cap)
    hits = [
        r for r in cap.records
        if r.levelno == logging.WARNING and "EXPOSE_PURE" in r.getMessage()
    ]
    for r in hits:
        print(f"  [{r.name}:{r.lineno}] {r.getMessage()}")
    if not hits:
        print("  (no EXPOSE_PURE warning fired)")


def probe2_constraints() -> None:
    print("\n=== Probe 2: ConstraintUsage enumeration (catf_mfe) ===")
    ex = SysMLDataExtractor([FIXTURES / "catf_mfe_model"])
    assert ex.load_models(), "catf_mfe failed to load"
    cus = list(ex.adapter.elements_of_type(ex.model, "ConstraintUsage"))
    print(f"  elements_of_type('ConstraintUsage') -> {len(cus)} nodes")
    calc_owned = part_owned = usage_owned = other = 0
    saw_radius = saw_calc_example = False
    for c in cus:
        owner = getattr(c, "owner", None)
        owner_name = getattr(owner, "name", None)
        if owner is None:
            other += 1
            continue
        if ex.adapter.is_instance(owner, "CalculationDefinition"):
            calc_owned += 1
            saw_calc_example = True
        elif ex.adapter.is_instance(owner, "PartDefinition"):
            part_owned += 1
        elif ex.adapter.is_instance(owner, "PartUsage"):
            usage_owned += 1
        else:
            other += 1
        if getattr(c, "name", None) == "RadiusConsistency":
            saw_radius = True
    print(f"  owner kinds: calc_def={calc_owned} part_def={part_owned} "
          f"part_usage={usage_owned} other/unowned={other}")
    print(f"  reaches RadiusConsistency (part-def-owned): {saw_radius}")
    print(f"  reaches at least one calc-def-owned constraint: {saw_calc_example}")
    # Sample a few (name, owner.name, owner metaclass)
    for c in cus[:8]:
        owner = getattr(c, "owner", None)
        print(f"    - {getattr(c, 'name', '<anon>')!r} on "
              f"{type(owner).__name__} {getattr(owner, 'name', None)!r}")


def probe3_zero_output() -> None:
    print("\n=== Probe 3: zero-output calc def extracts with 0 outputs ===")
    ex = SysMLDataExtractor([FIXTURES / "zero_output_calc"])
    assert ex.load_models(), "zero_output_calc failed to load"
    cds = ex.extract_calculation_definitions()
    for cd in cds:
        print(f"  calc def {cd.name!r}: inputs={len(cd.input_attributes)} "
              f"outputs={len(cd.output_attributes)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    probe1_expose()
    probe2_constraints()
    probe3_zero_output()
