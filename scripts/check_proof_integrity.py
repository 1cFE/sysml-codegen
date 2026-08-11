#!/usr/bin/env python3
"""No row may be proven by evidence that is itself scheduled to break.

A Gate 4C row clears its deletion group by naming a replacement node that exists, collects and
passes. That is necessary but not sufficient: if the file holding the replacement is itself a
blocker of one of the deletion groups, the proof dies with the deletion it is authorising, and
the row was never really green.

Gate 4C part 7 found this twice by hand — five files in chunk 10's predecessor backing fifteen
rows including two already-executed deletions, and a sixth (L-130, named by L-157) in chunk 10.
This makes the check mechanical so it runs every chunk instead of when somebody remembers.

The check is transitive by construction: `group_readiness` reports a group's blockers over
*all* the deletion groups' surfaces, so a proof node in a file that only breaks on G4' is
caught even though it survives the v5-family step.

    python scripts/check_proof_integrity.py
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

#: Every deletion group whose execution the retirement runbook orders. A proof node living in
#: a file any one of these still blocks is a proof that outlives nothing.
GROUPS = ("4B-G0", "4B-G1", "4B-G2", "4B-G3", "4B-G4", "4B-v5-family")


def _checker() -> dict:
    """The Gate 4A checker's own module, loaded rather than re-implemented."""
    argv, sys.argv = sys.argv, ["check_ledger_4a"]
    try:
        return runpy.run_path(str(REPO_ROOT / "scripts/check_ledger_4a.py"), run_name="_checker")
    finally:
        sys.argv = argv


def main() -> int:
    checker = _checker()
    ledger = checker["load_ledger"]()

    blocked_paths: dict[str, str] = {}
    for group in GROUPS:
        for blocker in checker["group_readiness"](ledger, group).blockers:
            row_id, _, path = blocker.partition(" ")
            blocked_paths.setdefault(path, row_id)

    problems = []
    for row in ledger["rows"]:
        nodes = row["replacement_proof_node"]
        if nodes is None:
            continue
        for node in [nodes] if isinstance(nodes, str) else nodes:
            path = node.split("::", 1)[0]
            if path in blocked_paths:
                problems.append(
                    f"{row['id']} ({row['path']}) is proven by {node}, whose file is still "
                    f"blocking a deletion group as {blocked_paths[path]}"
                )

    for problem in problems:
        print(f"FAIL {problem}")
    print(f"proof integrity: {len(problems)} problems over {len(blocked_paths)} blocked files")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
