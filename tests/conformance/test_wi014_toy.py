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
    instance; resolution flows per occurrence instead.)

    Read off the exact route. Until retirement step 2 this node read the legacy
    ``OutputRegistry._scoped_alias`` table directly; that registry retired with the v5
    family. The discharge is a public fact, so it is asserted on the public artefact the
    projection ships: the shape-A ``OutputAlias``, scoped to the ``demo_plant`` occurrence
    and pointing at the calc-output channel.
    """
    from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline

    graph = build_elaborated_pipeline([FIXTURES_DIR / "wi014_toy"])

    (alias,) = [a for a in graph.output_aliases if a.alias_name == "total_cost"]
    assert alias.shape == "part_def"
    assert alias.instance_path == "demo_plant"
    assert alias.canonical_channel.endswith("cost_calc__cost"), alias.canonical_channel


@requires_license
def test_wi014_toy_scoped_alias_tuple_no_collapse() -> None:
    """C3: scope and leaf stay separate fields, so a mis-split can never collide.

    The failure this guards against is one string ``"demo_plant.total_cost"`` split at the
    wrong dot: ``("demo_plant.total", "cost")`` instead of ``("demo_plant", "total_cost")``.
    It cannot happen while the two halves are never joined in the first place. The legacy
    ``_scoped_alias`` tuple key that carried them retired with the v5 family (retirement
    step 2); the exact route carries the same pair as two ``OutputAlias`` fields, and the
    leaf is still a single segment.
    """
    from sysml_codegen.orchestration.elaborated_pipeline import build_elaborated_pipeline

    graph = build_elaborated_pipeline([FIXTURES_DIR / "wi014_toy"])

    (alias,) = [a for a in graph.output_aliases if a.alias_name == "total_cost"]
    assert alias.instance_path == "demo_plant"
    assert "." not in alias.alias_name
    assert alias.alias_name != "cost"
