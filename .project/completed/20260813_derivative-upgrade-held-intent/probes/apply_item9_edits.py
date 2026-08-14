"""Author the Item 9 ruled forms on a scratch copy of `catf_mfe_gated`.

This is the design-stage de-risk probe's edit half (the epic's binding lesson: a probe that
gates a landing must run generation, not only elaboration). It applies, mechanically:

- A5/A6 — all 27 radial-build derivations, each carrying the owner-required two-line
  relation + chosen-basis block, and deletes `LayerContinuity` / `RadiusThicknessConsistency`.
- A9 — `ProductWithinBand` in `gate_forms.sysml` plus the ruled `assert constraint
  pumping_speed_agrees : ProductWithinBand` in relative form at `rel_tol = 0.01`.

Usage:  python apply_item9_edits.py <fixture-root> [--sibling-spelling qualified]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

#: The radial build's 14 layers, outermost-derived-from-innermost, in authored order.
#: `None` marks the free root: `axis_region.inner_radius` is a free parameter.
LAYERS: list[tuple[str, str | None]] = [
    ("axis_region", None),
    ("plasma_region", "axis_region"),
    ("vacuum_gap", "plasma_region"),
    ("first_wall", "vacuum_gap"),
    ("blanket", "first_wall"),
    ("reflector", "blanket"),
    ("ht_shield", "reflector"),
    ("structure", "ht_shield"),
    ("gap1", "structure"),
    ("vessel", "gap1"),
    ("tf_coil", "vessel"),
    ("gap2", "tf_coil"),
    ("lt_shield", "gap2"),
    ("bioshield", "lt_shield"),
]

AUTHORITY_A5 = "owner-disposition.md Group A, A5 (derive-instead)"
AUTHORITY_A6 = "owner-disposition.md Group A, A6 (derive-instead)"

INDENT = " " * 12


def _block_bounds(lines: list[str], owner: str) -> tuple[int, int]:
    """[start, end) line indices of the `part <owner> { ... }` block."""
    header = re.compile(rf"^\s*part\s+{re.escape(owner)}\s*\{{\s*$")
    start = next(i for i, line in enumerate(lines) if header.match(line))
    depth = 0
    for cursor in range(start, len(lines)):
        depth += lines[cursor].count("{") - lines[cursor].count("}")
        if depth == 0:
            return start, cursor + 1
    raise AssertionError(f"unterminated block for {owner}")


def _replace_in_block(
    lines: list[str], owner: str, attribute: str, replacement: list[str]
) -> None:
    start, end = _block_bounds(lines, owner)
    pattern = re.compile(rf"^\s*attribute\s+{re.escape(attribute)}\s*:")
    hits = [i for i in range(start, end) if pattern.match(lines[i])]
    assert len(hits) == 1, f"{owner}.{attribute}: {len(hits)} declarations found"
    lines[hits[0] : hits[0] + 1] = replacement


def derive_radial_build(text: str, sibling_spelling: str) -> str:
    lines = text.splitlines()

    for layer, below in LAYERS:
        if below is not None:
            reference = (
                f"catf_radial_build::{below}.outer_radius"
                if sibling_spelling == "qualified"
                else f"{below}.outer_radius"
            )
            _replace_in_block(
                lines,
                layer,
                "inner_radius",
                [
                    f"{INDENT}// Relation (undirected): {layer}.inner_radius = "
                    f"{below}.outer_radius (adjacent layers abut).",
                    f"{INDENT}// CHOSEN BASIS, not physics: the axis root radius and the 14 layer "
                    f"thicknesses are free; radii derive outward. Authority: {AUTHORITY_A5}.",
                    f"{INDENT}attribute inner_radius : Real = {reference};  // m",
                ],
            )
        _replace_in_block(
            lines,
            layer,
            "outer_radius",
            [
                f"{INDENT}// Relation (undirected): {layer}.outer_radius = {layer}.inner_radius "
                f"+ {layer}.thickness.",
                f"{INDENT}// CHOSEN BASIS, not physics: inner_radius and thickness are free; "
                f"outer_radius derives. Authority: {AUTHORITY_A6}.",
                f"{INDENT}attribute outer_radius : Real = inner_radius + thickness;  // m",
            ],
        )

    body = "\n".join(lines) + "\n"

    # `tf_coil.thickness` is the one free thickness a calc also consumes
    # (`magnet_surface_calc.thickness`, whose calc-def formal reads `m`). Its authored trailing
    # comment `// From line 83 (= tf_dr)` yields no unit, so the new derived-`outer_radius` port
    # would read `None` and the two lanes would refuse. Give the comment a readable unit.
    thickness_before = "attribute thickness : Real = 0.25 [m];  // From line 83 (= tf_dr)"
    thickness_after = "attribute thickness : Real = 0.25 [m];  // m - from line 83 (= tf_dr)"
    assert thickness_before in body, "tf_coil.thickness comment not found verbatim"
    body = body.replace(thickness_before, thickness_after, 1)

    for constraint in ("LayerContinuity", "RadiusThicknessConsistency"):
        removed = re.sub(
            rf"\n *constraint {constraint} \{{.*?\n *\}}\n",
            "\n",
            body,
            count=1,
            flags=re.DOTALL,
        )
        assert removed != body, f"{constraint} not deleted"
        body = removed
    return body


#: The formals carry unit comments because the *constraint* lane reads a port's unit from the
#: formal's own declaration. Unannotated formals project `unit_text=None`, which collides with
#: the calc lane's authored unit on the same design attribute and refuses the whole projection.
#: This is the shape Item 8's own customer fixture uses (`tests/fixtures/unit_lane_a9`).
PRODUCT_WITHIN_BAND = """
    constraint def ProductWithinBand {
        in observed : Real;        // m³/s
        in count : Real;           // Dimensionless
        in each_capacity : Real;   // m³/s
        in rel_tol : Real;         // Dimensionless
        observed > count * each_capacity * (1.0 - rel_tol) and
        observed < count * each_capacity * (1.0 + rel_tol)
    }
"""

A9_AUTHORED = """        // A9, ruled assert-band at 1% relative (owner-disposition.md Group A, A9):
        // band = n_pumps * pump_capacity_each +/- 1%. rel_tol is dimensionless.
        assert constraint pumping_speed_agrees : ProductWithinBand {
            in observed = pumping_speed_total;
            in count = n_pumps;
            in each_capacity = pump_capacity_each;
            in rel_tol = 0.01;
        }
"""

A9_AUTHORED_OLD = """        // Constraint: total pumping speed equals sum of all pumps
        constraint PumpingSpeedConsistency {
            doc /* Total pumping speed should match sum of pump capacities */
            pumping_speed_total == n_pumps * pump_capacity_each
        }
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--sibling-spelling", default="bare", choices=["bare", "qualified"])
    parser.add_argument("--only", default="all", choices=["all", "a56", "a9"])
    options = parser.parse_args()
    root: Path = options.root

    if options.only in ("all", "a56"):
        radial = root / "designs/catf_mfe/radial_build.sysml"
        radial.write_text(derive_radial_build(radial.read_text(), options.sibling_spelling))
    if options.only == "a56":
        print("A5/A6 only: applied")
        return 0

    gate_forms = root / "library/constraints/gate_forms.sysml"
    text = gate_forms.read_text()
    assert text.rstrip().endswith("}")
    gate_forms.write_text(text.rstrip()[: -len("}")].rstrip("\n") + "\n" + PRODUCT_WITHIN_BAND + "}\n")

    vacuum = root / "designs/catf_mfe/vacuum.sysml"
    text = vacuum.read_text()
    assert A9_AUTHORED_OLD in text, "A9's authored constraint block not found verbatim"
    text = text.replace(A9_AUTHORED_OLD, A9_AUTHORED, 1)
    text = text.replace(
        "    private import FusionAnalysesThermalLoads::VacuumPumpPower;",
        "    private import CATFGateForms::ProductWithinBand;\n"
        "    private import FusionAnalysesThermalLoads::VacuumPumpPower;",
        1,
    )
    vacuum.write_text(text)

    for line_number, line in enumerate(vacuum.read_text().splitlines(), start=1):
        if "assert constraint pumping_speed_agrees" in line:
            print(f"A9 authored at designs/catf_mfe/vacuum.sysml:{line_number}")
    print("edits applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
