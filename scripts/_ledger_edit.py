#!/usr/bin/env python3
"""Apply per-row Gate 4C disposition edits to ledger-4a.json from a JSON patch file.

One row per key. Values replace the row's field wholesale; a field the patch does not name is
left alone. Writing the ledger through this rather than by hand keeps the file's key order and
JSON formatting stable, so a review diff shows the dispositions and nothing else.

    python scripts/_ledger_edit.py patch.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

LEDGER = Path(__file__).resolve().parent.parent / ".project/ledger/ledger-4a.json"


def main(argv: list[str]) -> int:
    patch = json.loads(Path(argv[1]).read_text())
    ledger = json.loads(LEDGER.read_text())
    by_id = {row["id"]: row for row in ledger["rows"]}

    missing = sorted(set(patch) - set(by_id))
    if missing:
        raise SystemExit(f"no such rows: {missing}")

    for row_id, fields in patch.items():
        by_id[row_id].update(fields)
        print(f"{row_id} -> {fields.get('disposition_4c', '(fields only)')}")

    LEDGER.write_text(json.dumps(ledger, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
