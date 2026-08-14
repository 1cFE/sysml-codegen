"""Does the derived radius chain reproduce the authored literals bit-exactly in IEEE-754?

The spec makes this [HARD]: "the derivations must reproduce the authored literals exactly...
If a run shows any downstream number moving, that is a surfacing event." Decimal equality on
paper is not the same claim as float equality after a 14-step accumulation, so check it.
"""

from __future__ import annotations

#: (layer, authored inner_radius, authored thickness, authored outer_radius) from
#: tests/fixtures/catf_mfe_gated/designs/catf_mfe/radial_build.sysml.
AUTHORED = [
    ("axis_region", 0.0, 3.0, 3.0),
    ("plasma_region", 3.0, 1.1, 4.1),
    ("vacuum_gap", 4.1, 0.1, 4.2),
    ("first_wall", 4.2, 0.2, 4.4),
    ("blanket", 4.4, 0.8, 5.2),
    ("reflector", 5.2, 0.2, 5.4),
    ("ht_shield", 5.4, 0.2, 5.6),
    ("structure", 5.6, 0.2, 5.8),
    ("gap1", 5.8, 0.5, 6.3),
    ("vessel", 6.3, 0.2, 6.5),
    ("tf_coil", 6.5, 0.25, 6.75),
    ("gap2", 6.75, 0.5, 7.25),
    ("lt_shield", 7.25, 0.3, 7.55),
    ("bioshield", 7.55, 1.0, 8.55),
]


def main() -> int:
    drifts = []
    inner = AUTHORED[0][1]
    for layer, authored_inner, thickness, authored_outer in AUTHORED:
        if inner != authored_inner:
            drifts.append(
                f"{layer}.inner_radius: derived {inner!r} != authored {authored_inner!r} "
                f"(delta {inner - authored_inner:+.3e})"
            )
        outer = inner + thickness
        if outer != authored_outer:
            drifts.append(
                f"{layer}.outer_radius: derived {outer!r} != authored {authored_outer!r} "
                f"(delta {outer - authored_outer:+.3e})"
            )
        inner = outer

    print(f"final bioshield.outer_radius derived = {inner!r} (authored 8.55)")
    if drifts:
        print(f"\nFLOAT DRIFT on {len(drifts)} value(s):")
        for drift in drifts:
            print(f"  {drift}")
    else:
        print("\nno drift: every derived value is bit-identical to its authored literal")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
