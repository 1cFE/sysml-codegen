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

**What a 0/0 reading means.** Since Gate 4C part 7 chunk 19 every group is READY, so there are
zero blocked files and the problem loop has nothing to iterate. "0 problems over 0 blocked
files" therefore reads *nothing left to check*, not *checked and clean*. The check did its job
during preparation — it caught six proof nodes — and stays in the battery as a tripwire: if a
step of the retirement re-blocks a file, this is what says so. Its own failure path is proven
by `tests/unit/test_check_proof_integrity.py`, not by the live tree.

    python scripts/check_proof_integrity.py
"""

from __future__ import annotations

import runpy
import sys
from collections.abc import Callable
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


def blocked_paths(ledger: dict, readiness: Callable[[dict, str], object]) -> dict[str, str]:
    """Map each still-blocking file to the ledger row that blocks with it.

    `readiness` is the Gate 4A checker's `group_readiness`; each blocker it reports is a
    ``"<row id> <path>"`` string.
    """
    blocked: dict[str, str] = {}
    for group in GROUPS:
        for blocker in readiness(ledger, group).blockers:
            row_id, _, path = blocker.partition(" ")
            blocked.setdefault(path, row_id)
    return blocked


def find_problems(rows: list[dict], blocked: dict[str, str]) -> list[str]:
    """Every row whose replacement proof lives in a file that is still blocking a deletion."""
    problems = []
    for row in rows:
        nodes = row["replacement_proof_node"]
        if nodes is None:
            continue
        for node in [nodes] if isinstance(nodes, str) else nodes:
            path = node.split("::", 1)[0]
            if path in blocked:
                problems.append(
                    f"{row['id']} ({row['path']}) is proven by {node}, whose file is still "
                    f"blocking a deletion group as {blocked[path]}"
                )
    return problems


def report(problems: list[str], blocked_count: int) -> int:
    for problem in problems:
        print(f"FAIL {problem}")
    print(f"proof integrity: {len(problems)} problems over {blocked_count} blocked files")
    if not blocked_count:
        print("  (0 blocked files means nothing left to check, not checked-and-clean)")
    return 1 if problems else 0


def main() -> int:
    checker = _checker()
    ledger = checker["load_ledger"]()
    blocked = blocked_paths(ledger, checker["group_readiness"])
    return report(find_problems(ledger["rows"], blocked), len(blocked))


if __name__ == "__main__":
    raise SystemExit(main())
