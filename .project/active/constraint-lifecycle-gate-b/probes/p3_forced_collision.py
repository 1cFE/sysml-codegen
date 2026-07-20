"""Gate B probe 3 — try to REACH probe 1's shape B from a real SysML model.

Probe 1 showed extension raises a genuinely-new V11 violation only when an appended
constraint module carries an ``entry_point`` input whose qualified_name is (a) already in
``fallback_entry_points`` and (b) bound to a valueless entry point.

That input can only come from:
  * ``resolve_actual`` -> DESIGN_ATTRIBUTE, identity always a key of ``design_attr_by_qn``
    (producer_resolution.py:561, :367-380), or
  * the MODELED_DEFAULT mint ``{constraint_id}__{formal}`` (constraint_lowering.py:1414).

This probe attempts every way to reach it from a real model. Each variant is written to a
temp dir and run through the live public path ``build_pipeline_context``.

License env required:
    set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
Run:
    uv run python .project/active/constraint-lifecycle-gate-b/probes/p3_forced_collision.py
"""

from __future__ import annotations

import tempfile
import traceback
from pathlib import Path

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.resolution.graph_builder import collect_uncovered_params

HERE = Path(".project/active/constraint-lifecycle-gate-b/probes")

VARIANTS = {
    # A: two same-named members in one namespace, so a design-attribute QN could equal
    #    a `{calc_eqn}__{formal}` fallback key.
    "A same-name siblings": HERE / "collision_model" / "collision.sysml",
    # A-control: identical but the calc usage is renamed, so no duplicate name.
    "A' control (renamed)": HERE / "collision_control" / "control.sysml",
    # B: no duplicate names; the design attribute's NAME carries the `__` separator, so
    #    its QN would join to the same string as the fallback key. Attribute VALUELESS.
    "B separator, valueless": HERE / "collision_sep" / "collision_sep.sysml",
}


def variant_b_valued(src: str) -> str:
    """B with the attribute given a value — isolates which leg blocks the collision."""
    return src.replace("attribute scaler__gain : Real;", "attribute scaler__gain : Real = 3.0;")


def run(label: str, source: str) -> None:
    print(f"\n=== {label} ===")
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "m.sysml").write_text(source)
        try:
            ctx = build_pipeline_context([Path(tmp)], include_all=True)
        except Exception as exc:  # noqa: BLE001 - probe
            print(f"  REJECTED before extension: {type(exc).__name__}")
            print(f"    {str(exc).splitlines()[0][:200]}")
            return

    fallback = set(ctx.computation_graph.fallback_entry_points)
    attrs = {
        a.qualified_name: a.default_value
        for lst in ctx.design_attributes.values()
        for a in lst
        if a.qualified_name
    }
    print(f"  fallback_entry_points : {sorted(fallback)}")
    print(f"  design attribute index: {attrs}")
    print(f"  INTERSECTION          : {sorted(fallback & set(attrs))}")
    for g in ctx.computation_graph.entry_point_groups:
        for p in g.parameters:
            print(f"    EP {p.qualified_name}  {p.entry_type.name}  default={p.default_value!r}")
    for m in ctx.computation_graph.modules:
        if m.module_kind.name == "CONSTRAINT":
            for i in m.inputs:
                print(
                    f"    constraint input {i.param_name} <- {i.source.source_type} "
                    f"{i.source.qualified_name or i.source.producer_channel}"
                )
    print(f"  V11 offenders on the built (already extended) graph: {collect_uncovered_params(ctx.computation_graph)}")


def main() -> None:
    for label, path in VARIANTS.items():
        run(label, path.read_text())
    # B-valued: same model, attribute given a literal.
    run(
        "B' separator, valued",
        variant_b_valued((HERE / "collision_sep" / "collision_sep.sysml").read_text()),
    )
    # B-noassert: B with the constraint removed, to show the valueless attribute is
    # absent from the design-attribute index entirely (not merely unresolvable).
    src = (HERE / "collision_sep" / "collision_sep.sysml").read_text()
    start = src.index("        assert constraint nonneg")
    end = src.index("}\n", src.index("in v = scaler__gain;")) + 2
    run("B'' separator, valueless, no assert", src[:start] + src[end:])


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - probe
        traceback.print_exc()
