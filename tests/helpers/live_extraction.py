"""Live extraction facts for the conformance tests whose evidence was a v5 snapshot.

Two surviving conformance files (`test_extractor.py`, `test_expression_compiler.py`)
assert on *extraction* facts: calc definitions and their declaration identity. Their
evidence used to be each fixture's committed v5 extraction snapshot, read back through the
v5 loader; the evidence moved to the extractor itself, run live.

The facts narrowed with the legacy extraction lane (REPO-CLEANUP Move C, 2026-08-25):
``calc_usages`` and ``hierarchy_data`` were produced by ``usage_extractor`` /
``hierarchy_resolver``, both deleted as unreachable from ``run_codegen``; only the live
``calc_defs`` fact remains. The v6 instance-graph snapshot is still not a substitute for
it: that is an elaborated graph, not extractor output.

This module names no retiring path of its own: it reads the fixture *sources*, which stay.

Live extraction needs a syside license, so every caller is license-gated. See
`tests/conftest.py::requires_license`.
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"


def extract_live_facts(model_name: str) -> dict[str, Any]:
    """Extract one fixture model's calc defs, live.

    Args:
        model_name: a fixture directory name under ``tests/fixtures``.

    Returns:
        ``{"calc_defs": [...]}`` — the extraction fact the surviving conformance files
        read, produced by the same extractor the generator runs.

    Raises:
        RuntimeError: if the model does not load (no license, or a parse error).
    """
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    model_path = FIXTURES_DIR / model_name
    extractor = SysMLDataExtractor([model_path])
    if not extractor.load_models():
        raise RuntimeError(f"live extraction failed to load {model_path}")

    return {"calc_defs": extractor.extract_calculation_definitions()}


@functools.cache
def live_facts(model_name: str) -> dict[str, Any]:
    """``extract_live_facts`` memoised per model, so one session loads each model once."""
    return extract_live_facts(model_name)
