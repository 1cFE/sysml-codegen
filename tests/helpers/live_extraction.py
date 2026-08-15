"""Live extraction facts for the conformance tests whose evidence was a v5 snapshot.

Four surviving conformance files (`test_extractor.py`, `test_hierarchy_resolver.py`,
`test_ast_dispatch_invariant.py`, `test_expression_compiler.py`) assert on *extraction*
facts: calc definitions, calc usages and their bindings, and the hierarchy result. Their
evidence used to be each fixture's committed v5 extraction snapshot, read back through the
v5 loader. Both the snapshot files and the loader retire with the v5 family, so the
evidence moves to the extractor itself, run live.

The v6 instance-graph snapshot is not a substitute: it is an elaborated graph, it carries
no ``CalcUsageData`` bindings or ``HierarchyExtractionResult`` at all, and the exact route
refuses 22 of the 37 corpus fixtures — including every model these files lean on except
``sample_model`` and ``attr_expr_probe``.

This module names no retiring path of its own: it reads the fixture *sources*, which stay.

Live extraction needs a syside license, so every caller is license-gated. See
`tests/conftest.py::requires_license`.

Only the extraction stage is run here. Nothing in this module reaches the legacy
`orchestration.pipeline_builder`, so no v5 binding rewrite, aggregation scoping or CHAIN
alias production is applied — those are pipeline steps, not extraction facts, and they
retire with the stack that owns them.
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"


def extract_live_facts(model_name: str) -> dict[str, Any]:
    """Extract one fixture model's calc defs, calc usages and hierarchy result, live.

    Args:
        model_name: a fixture directory name under ``tests/fixtures``.

    Returns:
        ``{"calc_defs": [...], "calc_usages": [...], "hierarchy_data": ...}`` — the three
        extraction facts the surviving conformance files read, produced by the same three
        extractors the generator runs.

    Raises:
        RuntimeError: if the model does not load (no license, or a parse error).
    """
    from sysml_codegen.extraction.extractor import SysMLDataExtractor
    from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data
    from sysml_codegen.extraction.usage_extractor import extract_calculation_usages

    model_path = FIXTURES_DIR / model_name
    extractor = SysMLDataExtractor([model_path])
    if not extractor.load_models():
        raise RuntimeError(f"live extraction failed to load {model_path}")

    calc_defs = extractor.extract_calculation_definitions()
    calc_usages, _report = extract_calculation_usages(extractor.model, calc_defs=calc_defs)
    return {
        "calc_defs": calc_defs,
        "calc_usages": calc_usages,
        "hierarchy_data": extract_hierarchy_data(extractor.model),
    }


@functools.cache
def live_facts(model_name: str) -> dict[str, Any]:
    """``extract_live_facts`` memoised per model, so one session loads each model once."""
    return extract_live_facts(model_name)
