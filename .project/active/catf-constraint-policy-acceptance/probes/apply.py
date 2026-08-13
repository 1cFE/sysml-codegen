"""THROWAWAY (Item 5 design stage). Apply named probe edits to a scratch copy.

Usage:  probes/licensed.sh probes/apply.py /tmp/item5probe/p1 lib a2
"""

from __future__ import annotations

import sys
from pathlib import Path

import edits
import edits2

ACTIONS = {
    "lib": edits.write_library,
    "a2": edits.apply_a2,
    "a3": edits.apply_a3,
    "a9": edits.apply_a9,
    "d_intra": edits.apply_derive_intra,
    "d_cross": edits.apply_derive_cross,
    "d_cross_qn": edits.apply_derive_cross_qualified,
    "d_both_unitless": edits.apply_derive_both_unitless,
    "a7": edits2.apply_a7,
    "a8": edits2.apply_a8,
    "axis": edits2.apply_axis,
}

if __name__ == "__main__":
    root = Path(sys.argv[1])
    for name in sys.argv[2:]:
        ACTIONS[name](root)
        print(f"applied {name} to {root}")
