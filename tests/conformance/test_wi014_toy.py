"""Conformance tests for the imported WI-014 toy fixture (Item 8, UPSTREAM-FINDINGS).

``wi014_toy`` is the fusion-tea WI-014 construct-validation toy, imported verbatim
(see ``tests/fixtures/wi014_toy/PROVENANCE.md``). It carries the **part-def
EXPOSE_PURE (shape A)** case — a derived attribute ``total_cost = cost_calc.cost``
on ``part def 'Toy Plant'`` — the fixture that funds the deferred REQ-CA-09 test.

One layer: the live extractor (skips without a license) loads the model through
``SysMLDataExtractor`` and asserts the shape-A resolution on it. The offline layer read
the committed ``extraction_snapshot.json`` and retired with the v5 family (retirement
step 1).

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

The deferral is now **fully discharged by Item 11 (SC-7)**: the shape-A branch of
``_build_attribute_resolution_map`` no longer calls ``_resolve_expose_pure`` at all
(so it never reaches the malformed-refs warning at :796); it sets the resolution to
LITERAL and consults ``_scoped_alias`` to decide the warning. For ``total_cost`` a
scoped alias is registered, so the case is **silent and the name surfaces** as an
``output_aliases`` entry. The historical deferral narrative above is kept for
provenance; ``test_wi014_toy_shape_a_resolves_via_scoped_alias`` pins the discharged
behavior (the alias tuple survives, the name is emitted) on the live model.
"""

from __future__ import annotations

from pathlib import Path

from tests.conftest import requires_license

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"


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
