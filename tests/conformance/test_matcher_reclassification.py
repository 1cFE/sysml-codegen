"""Pin the retype_model reclassification — Item 7's headline behavioral change (SC-8).

Bug A (per-segment sanitizing of ``::``-form REFERENCE paths) lets quoted-owner
references like ``RetypeLibrary::'IFE Driver'::power`` match their def-owned
design attributes. The affected entry points reclassify USAGE_LITERAL (value
``None``) → DESIGN_ATTRIBUTE carrying the attribute's real default, and the two
``hif_calc`` usages collapse onto the single shared design-attribute key.

retype_model has no committed pipeline baseline, so this snapshot-driven test
is the corpus pin: a silent revert of the matcher fix flips these assertions
red. Enumerated in the Item 7 release notes (three-part review, section 1/3).

REQ-BT-09: ``::``-form REFERENCE paths sanitize per segment before matching.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.snapshot.graph_rebuild import build_full_graph_from_snapshot

FIXTURES = Path(__file__).parent.parent / "fixtures"

RECLASSIFIED = {
    "RetypeLibrary__IFE_Driver__power": 10.0,
    "RetypeLibrary__HIF_Driver__torque": 20.0,
}


@pytest.fixture(scope="module")
def retype_graph():
    graph, _inputs = build_full_graph_from_snapshot(
        FIXTURES / "retype_model" / "extraction_snapshot.json"
    )
    return graph


def _params(graph):
    return {
        p.qualified_name: p
        for group in graph.entry_point_groups
        for p in group.parameters
    }


def test_quoted_owner_refs_reclassify_to_design_attribute(retype_graph):
    params = _params(retype_graph)
    for qn, expected_default in RECLASSIFIED.items():
        assert qn in params, f"expected design-attribute entry point {qn!r} missing"
        p = params[qn]
        assert str(p.entry_type).endswith("DESIGN_ATTRIBUTE"), (
            f"{qn} classified {p.entry_type} — Bug A regressed to USAGE_LITERAL"
        )
        assert p.default_value == expected_default, (
            f"{qn} default {p.default_value!r} != design attribute's {expected_default}"
        )


def test_shared_design_attribute_key_collapses(retype_graph):
    # Two hif_calc usages reference the same def-owned torque attribute; the
    # reclassification keys both on the attribute QN, so exactly one entry
    # point (not one per usage) survives.
    params = _params(retype_graph)
    torque_keys = [qn for qn in params if qn.endswith("__torque")]
    assert torque_keys == ["RetypeLibrary__HIF_Driver__torque"]


def test_no_valueless_usage_literal_residue(retype_graph):
    # The pre-fix state carried unparseable usage-literals with default None
    # for these references; none may survive.
    params = _params(retype_graph)
    residue = [
        qn
        for qn, p in params.items()
        if str(p.entry_type).endswith("USAGE_LITERAL") and p.default_value is None
    ]
    assert residue == []
