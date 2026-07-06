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

REQ-CA-09 (shape-A EXPOSE_PURE resolution, deferred from Item 1 → 8 → 10) is now
**DISCHARGED** by Item 10 #4/#1 — see ``test_wi014_toy_shape_a_resolves_via_scoped_alias``.
The part-def EXPOSE expands per instance into the structured ``_scoped_alias`` namespace
and resolves. The historical deferral disposition below is kept for provenance.

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
    # Item 10 recapture: the snapshot now carries reference_chain so the offline
    # path can expand the part-def EXPOSE per instance (the test below).
    assert ca.reference_chain == ["cost_calc", "cost"]


def test_wi014_toy_shape_a_resolves_offline_via_scoped_alias() -> None:
    """REQ-CA-09 (offline, license-free): the shape-A part-def EXPOSE resolves from the
    committed snapshot alone.

    The Item 10 recapture put ``reference_chain`` on ``total_cost``, so the offline
    registry build (``build_output_registry`` + the Step-5.55 part-def expansion, the
    same helpers ``build_full_graph_from_snapshot`` runs) expands ``total_cost`` per
    design instance into ``_scoped_alias``: ``("demo_plant", "total_cost")`` maps to the
    ``demo_plant.cost_calc.cost`` channel. This is the license-free companion to
    ``test_wi014_toy_shape_a_resolves_via_scoped_alias`` (live).
    """
    from sysml_codegen.core.identifier_types import ScopedAliasKey
    from sysml_codegen.orchestration.output_registry_builder import build_output_registry
    from sysml_codegen.orchestration.pipeline_builder import (
        _register_partdef_expose_scoped_aliases,
    )

    snap = load_extraction_snapshot(snapshot_fixture("wi014_toy"))
    registry = build_output_registry(
        calc_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        aggregation_data=snap["aggregation_expressions"],
        computed_attributes=snap["computed_attributes"],
        channel_aliases=snap.get("channel_aliases", []),
        design_attributes=snap.get("design_attributes", {}),
    )
    _register_partdef_expose_scoped_aliases(
        registry,
        snap["computed_attributes"],
        snap["calc_usages"],
        snap.get("hierarchy_data"),
    )

    key = ScopedAliasKey(("demo_plant", "total_cost"))
    # Inertness gate (C5), offline: #4 wrote a structured scoped alias from the snapshot.
    assert key in registry._scoped_alias, dict(registry._scoped_alias)
    channel = registry.scoped_alias_lookup(key)
    assert channel is not None
    assert channel.endswith("cost_calc__cost"), channel


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
def test_wi014_toy_shape_a_resolves_via_scoped_alias() -> None:
    """REQ-CA-09 DISCHARGED (Item 10 #4/#1) — the shape-A part-def EXPOSE resolves.

    The deferral chain (Item 1 → 8 → "10 or 11") ends here. The part-def EXPOSE
    ``total_cost = cost_calc.cost`` on ``part def 'Toy Plant'`` is now expanded per
    design instance into the structured ``_scoped_alias`` namespace: for the
    ``demo_plant`` instance, ``("demo_plant", "total_cost")`` maps to the
    ``demo_plant.cost_calc.cost`` channel. A consumer of ``demo_plant.total_cost``
    reaches it via the ``_resolve_chain_dispatch`` #1 step (split at the last dot).

    (The old recorded-deferral baseline pinned a benign ``_resolve_expose_pure``
    malformed-refs warning from the per-def resolution map, which cannot pick an
    instance; resolution now flows through #1/_scoped_alias instead.)
    """
    from sysml_codegen.core.identifier_types import ScopedAliasKey
    from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

    ctx = build_pipeline_context([FIXTURES_DIR / "wi014_toy"])
    registry = ctx.output_registry

    key = ScopedAliasKey(("demo_plant", "total_cost"))
    # Inertness gate (C5): #4 actually wrote a structured scoped alias.
    assert key in registry._scoped_alias, dict(registry._scoped_alias)
    # Shape-A resolution: the consumer-scoped key reaches the calc-output channel.
    channel = registry.scoped_alias_lookup(key)
    assert channel is not None
    assert channel.endswith("cost_calc__cost"), channel


@requires_license
def test_wi014_toy_scoped_alias_tuple_no_collapse() -> None:
    """C3: the structured key is a real ``(scope, leaf)`` tuple, stored unjoined, so
    a mis-split ``("demo_plant.total", "cost")`` can never collide with the correct
    ``("demo_plant", "total_cost")``. The leaf is always a single segment."""
    from sysml_codegen.core.identifier_types import ScopedAliasKey
    from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

    ctx = build_pipeline_context([FIXTURES_DIR / "wi014_toy"])
    registry = ctx.output_registry
    assert ScopedAliasKey(("demo_plant", "total_cost")) in registry._scoped_alias
    assert ScopedAliasKey(("demo_plant.total", "cost")) not in registry._scoped_alias
