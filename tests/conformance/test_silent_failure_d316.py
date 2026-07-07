"""D3-16 — cross-part single-hop EXPOSE_PURE no longer silently skips its alias.

Classification (EXPOSE_PURE) and alias production must agree (REQ-CA-01). A
cross-part single-hop EXPOSE (`exposed = gen.gval`, where `gen` is a calc usage
OUTSIDE this part) classifies EXPOSE_PURE but no local instance ref matches, so
the alias is skipped — the Item-10 gate misses this shape. It must WARN, not go
silent. Expectation anchored to the fixture source, not computed (R1).
"""

from __future__ import annotations

import logging

from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.extraction.computed_attribute_extractor import (
    extract_computed_attributes,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import requires_license, snapshot_fixture


def _calc_usage_names(part) -> set[str]:
    return {
        m.name
        for m in getattr(part, "owned_members", [])
        if SysideAdapter.is_instance(m, "CalculationUsage")
    }


@requires_license
def test_d316_crosspart_expose_warns_not_silent(caplog):
    fixture_dir = snapshot_fixture("d316_crosspart_expose").parent
    ex = SysMLDataExtractor([fixture_dir])
    assert ex.load_models()

    warned = False
    with caplog.at_level(logging.WARNING):
        for part in SysideAdapter.elements_of_type(ex.model, "PartUsage"):
            if getattr(part, "name", None) != "consumer":
                continue
            extract_computed_attributes(SysideAdapter(), part, _calc_usage_names(part))
    warned = any(
        "D3-16" in r.message and "exposed" in r.message for r in caplog.records
    )
    assert warned, [r.message for r in caplog.records]
