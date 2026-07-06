"""Conformance tests for the imported WI-014 toy fixture (Item 8, UPSTREAM-FINDINGS).

``wi014_toy`` is the fusion-tea WI-014 construct-validation toy, imported verbatim
(see ``tests/fixtures/wi014_toy/PROVENANCE.md``). It carries the **part-def
EXPOSE_PURE (shape A)** case — a derived attribute ``total_cost = cost_calc.cost``
on ``part def 'Toy Plant'`` — the fixture that funds the deferred REQ-CA-09 test.

Two layers, mirroring ``test_type_indexing.py``:

- **Offline snapshot** (license-free): the committed ``extraction_snapshot.json``
  loads and carries the shape-A EXPOSE_PURE computed attribute.
- **Live extractor** (skips without a license): the model loads through
  ``SysMLDataExtractor``.

REQ-CA-09 (shape-A EXPOSE_PURE warning, deferred from Item 1) is discharged below
as a **recorded deferral** — see ``test_wi014_toy_shape_a_fires_malformed_refs``.

## REQ-CA-09 disposition (Item 8 live probe, 2026-07-05)

Item 1 reworded the EXPOSE_PURE *name-drop* warning (``graph_builder.py``,
``_resolve_expose_pure``, the "derived-attribute name is dropped" branch) but could
not test it against a real fixture: a minimal shape-A probe fired the *malformed-refs*
warning ("could not identify instance/output from refs") instead, and the only
in-repo EXPOSE fixtures were shape B (part-*usage*).

The Item 8 live probe on ``wi014_toy`` reproduces exactly that: the shape-A
``total_cost = cost_calc.cost`` fires the **malformed-refs** warning, because on a
part def the calc-usage instance names are not populated into ``calc_usage_names``,
so ``_resolve_expose_pure`` cannot separate the instance ref (``cost_calc``) from the
output ref (``cost``) and returns before reaching the name-drop branch.

Therefore REQ-CA-09 is discharged as a **recorded deferral**: this file pins the
malformed-refs warning as the *current baseline*, and the reworded name-drop-warning
test is handed off to **Items 10/11** — the items that own the shape-A part-def
resolution path (``epic_upstream_findings.md:387``). Once that path lands, the ref
classification succeeds, ``_resolve_expose_pure`` reaches the name-drop branch, and
the deferred assertion can be upgraded there. This is not a silent third punt: the
handoff item is named and the current warning is asserted, not ignored.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.extraction.data_models import ComputedAttributeClassification
from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import requires_license, snapshot_fixture

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"


# ---------------------------------------------------------------------------
# Offline snapshot layer (license-free)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def wi014_snapshot() -> dict:
    """Load the committed wi014_toy extraction snapshot."""
    return load_extraction_snapshot(snapshot_fixture("wi014_toy"))


def test_wi014_toy_snapshot_loads(wi014_snapshot: dict) -> None:
    """The snapshot loads and carries the two chained calc usages and the shape-A
    EXPOSE_PURE derived attribute (``total_cost``)."""
    qns = {cu.qualified_name for cu in wi014_snapshot["calc_usages"]}
    assert "toy_plant__demo_plant__area_calc" in qns
    assert "toy_plant__demo_plant__cost_calc" in qns
    # shape-A EXPOSE_PURE marker: a derived attribute on the part def.
    assert wi014_snapshot["computed_attributes"], "no computed attributes captured"


def test_wi014_toy_shape_a_is_expose_pure_on_part_def(wi014_snapshot: dict) -> None:
    """The ``total_cost`` derived attribute is classified EXPOSE_PURE and sits on the
    part *def* (shape A), distinct from the in-repo shape-B part-usage EXPOSE cases."""
    total_cost = [
        ca for ca in wi014_snapshot["computed_attributes"] if ca.name == "total_cost"
    ]
    assert len(total_cost) == 1, [ca.name for ca in wi014_snapshot["computed_attributes"]]
    ca = total_cost[0]
    assert ca.classification == ComputedAttributeClassification.EXPOSE_PURE
    assert ca.is_on_part_definition  # shape A: derived attr on the part DEF


# ---------------------------------------------------------------------------
# Live extractor layer (license-gated)
# ---------------------------------------------------------------------------


@requires_license
def test_wi014_toy_loads_live() -> None:
    """The toy loads through ``SysMLDataExtractor`` (import fidelity: it parses in
    isolation after the copy, no shape adaptation)."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    ex = SysMLDataExtractor([FIXTURES_DIR / "wi014_toy"])
    assert ex.load_models()


@requires_license
def test_wi014_toy_shape_a_fires_malformed_refs(
    caplog: pytest.LogCaptureFixture, tmp_path: Path
) -> None:
    """REQ-CA-09 (recorded deferral). The shape-A ``total_cost = cost_calc.cost``
    EXPOSE_PURE fires the **malformed-refs** warning, NOT the reworded name-drop
    warning — because on a part def ``_resolve_expose_pure`` cannot classify the
    refs and returns before the name-drop branch. This pins the current baseline;
    the reworded-warning test is deferred to Items 10/11 (shape-A resolution path).
    See the module docstring for the full disposition.
    """
    import logging

    from sysml_codegen.snapshot import capture_snapshot

    with caplog.at_level(logging.WARNING, logger="sysml_codegen.resolution.graph_builder"):
        capture_snapshot(
            [FIXTURES_DIR / "wi014_toy"],
            tmp_path / "extraction_snapshot.json",
        )

    expose_warnings = [
        r.getMessage()
        for r in caplog.records
        if "EXPOSE_PURE total_cost" in r.getMessage()
    ]
    assert expose_warnings, "no EXPOSE_PURE warning fired for total_cost"
    joined = "\n".join(expose_warnings)
    # Current baseline: malformed-refs branch.
    assert "could not identify instance/output from refs" in joined
    # NOT the reworded name-drop branch (deferred to Items 10/11).
    assert "derived-attribute name is dropped" not in joined
