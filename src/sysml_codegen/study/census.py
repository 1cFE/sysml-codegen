"""The entry-point census of a generated package: its parameters grouped by entry type.

``integrate`` re-derives a package's census through this one function, and a target's own
census test can import it, so the seam and the target cannot disagree about what a census
is. The grouping reads ``contracts/model_contract.json`` ``parameters[]`` and nothing else.
"""

from __future__ import annotations

import json
from pathlib import Path


def by_entry_type(package_root: Path) -> dict[str, set[str]]:
    """Every parameter's qualified name, grouped under its ``entry_type``."""
    contract = json.loads((package_root / "contracts" / "model_contract.json").read_text())
    by_type: dict[str, set[str]] = {}
    for parameter in contract["parameters"]:
        by_type.setdefault(parameter["entry_type"], set()).add(parameter["qualified_name"])
    return by_type
