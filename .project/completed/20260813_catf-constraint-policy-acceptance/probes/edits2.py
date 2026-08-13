"""THROWAWAY (Item 5 design stage). The remaining derivation legs: A7, A8, axis root.

Scopes the blast radius of the SI_RENDERING_COLLISION finding: which of the seven ruled
derive-instead rows can be authored at all, and which cannot.
"""

from __future__ import annotations

from pathlib import Path

from edits import replace


def apply_a7(root: Path) -> None:
    """A7: gamma_shield.fraction_volume derived from neutron_shield.fraction_volume."""
    replace(
        root / "designs" / "catf_mfe" / "shield.sysml",
        "            attribute fraction_volume : Real = 0.10;  // From PyFECONS line 91",
        "            attribute fraction_volume : Real = 1.0 - neutron_shield.fraction_volume;",
    )


def apply_a8(root: Path) -> None:
    """A8: catf_vacuum_vessel.outer_radius derived from inner_radius + wall_thickness."""
    replace(
        root / "designs" / "catf_mfe" / "vacuum.sysml",
        "        attribute outer_radius : Real = 6.5 [m];   // inner_radius + wall_thickness",
        "        attribute outer_radius : Real = inner_radius + wall_thickness;",
    )


def apply_axis(root: Path) -> None:
    """A6, the one radial-build layer with no geometry calc usage on it."""
    replace(
        root / "designs" / "catf_mfe" / "radial_build.sysml",
        "            attribute outer_radius : Real = 3.0 [m];  // Calculated",
        "            attribute outer_radius : Real = inner_radius + thickness;",
    )
