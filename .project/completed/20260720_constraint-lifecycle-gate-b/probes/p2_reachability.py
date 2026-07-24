"""Gate B probe 2 — is probe 1's shape B reachable? Corpus namespace sweep.

Probe 1 showed extension DOES raise a genuinely-new V11 violation when an appended
constraint module carries an ``entry_point`` input whose qualified_name is already in
``fallback_entry_points``. That input can only come from ``resolve_actual`` returning
DESIGN_ATTRIBUTE with ``identity`` equal to that key (producer_resolution.py:561 —
identity is always a key of ``design_attr_by_qn``), or from the MODELED_DEFAULT mint
``{constraint_id}__{formal}``.

So the whole vacuity question is one set question, per model:

    design_attr_by_qn.keys()  INTERSECT  fallback_entry_points   == empty ?

This runs the live public path (``build_pipeline_context``) over every fixture model in
the repo and reports that intersection, plus the MODELED_DEFAULT synthetic-key check.

License env required:
    set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
Run:
    uv run python .project/active/constraint-lifecycle-gate-b/probes/p2_reachability.py
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

FIXTURES = Path("tests/fixtures")


def model_dirs() -> list[Path]:
    return sorted(d for d in FIXTURES.iterdir() if d.is_dir() and any(d.rglob("*.sysml")))


def main() -> None:
    total_fallback = 0
    total_attrs = 0
    collisions: list[tuple[str, str]] = []
    ok, failed = 0, 0

    for d in model_dirs():
        try:
            ctx = build_pipeline_context([d], include_all=True)
        except Exception as exc:  # noqa: BLE001 - probe; some fixtures fail by design
            failed += 1
            print(f"{d.name:32s} SKIP ({type(exc).__name__}: {str(exc)[:70]})")
            continue
        ok += 1
        fallback = set(ctx.computation_graph.fallback_entry_points)
        attr_qns = {
            a.qualified_name
            for attrs in ctx.design_attributes.values()
            for a in attrs
            if a.qualified_name
        }
        inter = fallback & attr_qns
        total_fallback += len(fallback)
        total_attrs += len(attr_qns)
        for qn in sorted(inter):
            collisions.append((d.name, qn))
        flag = "  <-- COLLISION" if inter else ""
        print(
            f"{d.name:32s} fallback={len(fallback):3d}  design_attrs={len(attr_qns):3d}  "
            f"intersection={len(inter)}{flag}"
        )
        if fallback and not inter:
            sample_f = sorted(fallback)[0]
            sample_a = sorted(attr_qns)[0] if attr_qns else "<none>"
            print(f"{'':32s}   e.g. fallback {sample_f!r} vs design_attr {sample_a!r}")

    print()
    print(f"models built: {ok}   skipped: {failed}")
    print(f"total fallback EP QNs: {total_fallback}   total design-attribute QNs: {total_attrs}")
    print(f"COLLISIONS (design attr QN that is also a fallback key): {len(collisions)}")
    for name, qn in collisions:
        print(f"  {name}: {qn}")


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - probe
        traceback.print_exc()
        sys.exit(1)
