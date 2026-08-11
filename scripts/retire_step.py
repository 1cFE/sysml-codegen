#!/usr/bin/env python3
"""Execute the mechanical half of one retirement step, and close it in the ledger.

The runbook's per-step edit table is the half a person has to make. This is the other half:

    retire_step.py apply 1       # git rm the step's deletions, git mv its archives
    ...make the edit table's edits, commit...
    retire_step.py close 1 <oid> # mark the step's rows executed at that commit
    ...commit the ledger, then run the battery...

Both halves are needed for the battery to come back green. `check_ledger_4a.py paths`
verifies every state claim against Git, so a step whose files are gone while its rows still
say `proposed` fails the checker — which is the check working, not a surprise.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from retirement_worklist import LEDGER, REPO_ROOT, load_items  # noqa: E402

ARCHIVE = "scripts/archive"


def git(*args: str) -> None:
    subprocess.run(["git", "-C", str(REPO_ROOT), *args], check=True)


def apply_step(step: int) -> int:
    """Delete what the step deletes, archive what it archives, and follow the archived rows."""
    items = [item for item in load_items() if item.step == step]
    (REPO_ROOT / ARCHIVE).mkdir(parents=True, exist_ok=True)

    for item in items:
        if item.action == "delete":
            git("rm", "-q", item.path)

    moved: dict[str, str] = {}
    for item in items:
        if item.action == "archive":
            destination = f"{ARCHIVE}/{Path(item.path).name}"
            git("mv", item.path, destination)
            moved[item.row] = destination
    if moved:
        # The row keeps its original `path` — that path is its identity in the Git-derived
        # candidate set — and records where the file now lives.
        _rewrite_rows(
            lambda row: {"archived_to": moved[row["id"]]} if row["id"] in moved else None
        )

    deletions = sum(1 for item in items if item.action == "delete")
    print(f"step {step}: deleted {deletions}, archived {len(moved)}")
    print("Now make the edit table's edits:")
    for item in items:
        if item.action == "edit":
            print(f"  {item.row}  {item.path}")
    return 0


def close_step(step: int, commit: str) -> int:
    """Mark every row the step spent as executed at `commit`."""
    rows = {item.row for item in load_items() if item.step == step}
    _rewrite_rows(
        lambda row: {"state": "executed", "executed_commit": commit}
        if row["id"] in rows
        else None
    )
    print(f"step {step}: {len(rows)} rows marked executed at {commit}")
    return 0


def _rewrite_rows(update) -> None:
    """Apply `update(row) -> dict | None` to the ledger, preserving its formatting."""
    ledger = json.loads(LEDGER.read_text())
    text = LEDGER.read_text()
    for row in ledger["rows"]:
        changes = update(row)
        if not changes:
            continue
        before = json.dumps(row, indent=1)
        row.update(changes)
        after = json.dumps(row, indent=1)
        before_block = "\n".join("  " + line for line in before.splitlines())
        after_block = "\n".join("  " + line for line in after.splitlines())
        if before_block not in text:
            raise SystemExit(f"{row['id']}: cannot locate the row in the ledger text")
        text = text.replace(before_block, after_block, 1)
    LEDGER.write_text(text)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    apply_parser = sub.add_parser("apply")
    apply_parser.add_argument("step", type=int, choices=(1, 2, 3, 4))
    close_parser = sub.add_parser("close")
    close_parser.add_argument("step", type=int, choices=(1, 2, 3, 4))
    close_parser.add_argument("commit")
    args = parser.parse_args(argv)
    return apply_step(args.step) if args.cmd == "apply" else close_step(args.step, args.commit)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
