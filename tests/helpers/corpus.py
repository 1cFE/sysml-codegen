"""The corpus fixture names, from a route-neutral home.

Two conformance tests used to import ``MODELS`` and ``EXTRACTION_ONLY_MODELS`` from
``scripts/capture_extraction_snapshots.py`` to enumerate the corpus. That coupled them to
the v5 capture script, which is a deletion row, and it was invisible to the Gate 4C part 3
surface check because a script import is not a package import.

The enumeration now comes from the v6 recapture batch manifest, which names the same 37
fixtures — checked equal to the capture script's own corpus before the move — and which
survives the v5 retirement by construction. The capture script keeps its dictionaries,
because they carry capture-specific rationale that does not belong in a neutral module.
"""

from __future__ import annotations

import json
from pathlib import Path

BATCH_MANIFEST = (
    Path(__file__).resolve().parents[1] / "fixtures/v6_recapture_batch/batch.json"
)


def corpus_fixture_names() -> list[str]:
    """The 37 corpus fixture names, sorted, from the committed batch manifest."""
    return sorted(json.loads(BATCH_MANIFEST.read_text())["fixtures"])
