"""Conformance tests for the authored ife_plant fixture (Item 8, UPSTREAM-FINDINGS).

``ife_plant`` is the authored plant-idiom fixture carrying six of the plant idiom's
structural shapes in one parseable model. It is the substrate Items 9-11 build,
snapshot, and diff against. The shape 6 self-named-binding trap lives in its own
fixture (``self_named_binding_trap``) so its failure mode cannot poison this snapshot.

## Per-shape labels (INFERRED per-shape labeling — spec.md Fixture 2)

A deliberate mix of **working** shapes (correct snapshot) and **known-incomplete**
baselines (to be improved by a later item). The labels are what make the later
baseline diffs legible:

- Shape 1 (mech —), **correct**: plant def with 16 def-declared attribute literals
  (richness floor met, ≥14).
- Shape 2 (mech A), **known-incomplete**: ``:>>``-valued specialized subsystem def
  (``Shielded Core``) — the redefinition is captured but unwired (no consumer).
- Shape 3 (mech —), **correct**: retyped nested part (``driver`` → ``Hif Driver``) —
  instantiates the subtype-owned ``hif_cost_calc`` (the Item 4/5 win).
- Shape 4 (mech B), **known-incomplete**: cross-part calc-chain
  (``cryo_load.magnet_volume``) — falls to a valueless wired fallback EP that the
  collector pins.
- Shape 5 (mech C), **known-incomplete**: plain-usage ``:>>`` override
  (``baseline_plant.capacity_factor``) — dropped at extraction.
- Shape 7 (mech —), **correct**: two same-type sibling chambers
  (``chamber_a``/``chamber_b``) — each produces its own virtual ``yield_calc``.

The **working** shapes (3, 7) prove the Item 4/5 path; the **known-incomplete**
shapes (2, 4, 5) are the baselines Items 9-10 improve.

## Item 7 sequencing (the conditional collector pin)

The cross-part-input assertion is written conditionally on Item 7's
``collect_uncovered_params``. As of Item 8 implementation, **Item 7 has landed**, so
this file pins the exact expected uncovered set (shape 4's ``cryo_load.magnet_volume``
— mirroring the way Item 7 pins catf_mfe's ``[cryo_load.magnet_volume]``). Items 9-10
flip this pin as they wire the cross-part chain. The ``else`` branch (Item 7 absent)
is retained so the test is satisfiable at either landing order.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import sysml_codegen.resolution.graph_builder as gb
from sysml_codegen.snapshot import (
    build_full_graph_from_snapshot,
    load_extraction_snapshot,
)
from tests.conftest import requires_license, snapshot_fixture

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

HIF_DRIVER = "IfePlantLib__Hif_Driver"


# ---------------------------------------------------------------------------
# Offline snapshot layer (license-free)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def ife_snapshot() -> dict:
    """Load the committed ife_plant extraction snapshot."""
    return load_extraction_snapshot(snapshot_fixture("ife_plant"))


def _def_declared_literals(snapshot: dict) -> list[tuple[str, str]]:
    """Def-declared attribute literals on the plant def: design_attributes whose
    ``default_value`` parses as a numeric literal (shape 1 richness floor)."""
    lits: list[tuple[str, str]] = []
    for attrs in snapshot["design_attributes"].values():
        for a in attrs:
            qn = a.qualified_name
            val = a.default_value
            if "Ife_Power_Plant" not in qn or val is None:
                continue
            try:
                float(val)
            except (TypeError, ValueError):
                continue
            lits.append((a.name, val))
    return lits


def _virtual_qns(snapshot: dict) -> set[str]:
    return {cu.qualified_name for cu in snapshot["calc_usages"]}


# --- Shape 1 (correct): richness floor -------------------------------------


def test_ife_plant_def_literals_present(ife_snapshot: dict) -> None:
    """Shape 1 (correct): the plant def carries ≥14 def-declared attribute literals
    (the richness floor mirroring the ~14 Hawker parameters Item 9 measures against)."""
    lits = _def_declared_literals(ife_snapshot)
    assert len(lits) >= 14, [n for n, _ in lits]


# --- Shape 3 (correct): retyping works -------------------------------------


def test_retyped_part_instantiates_subtype_calcs(ife_snapshot: dict) -> None:
    """Shape 3 (correct): the retyped ``driver`` (→ ``Hif Driver``) instantiates the
    subtype-owned template calc ``hif_cost_calc`` — the Item 4/5 win, distinct from
    the deliberately-unwired cross-part shapes."""
    qns = _virtual_qns(ife_snapshot)
    assert any(q.endswith("hif_plant__driver__hif_cost_calc") for q in qns), qns
    # The supertype-owned template is preserved too (superset indexing).
    assert any(q.endswith("hif_plant__driver__base_power_calc") for q in qns), qns


def test_retyped_driver_subtype_calc_owned_by_subtype(ife_snapshot: dict) -> None:
    """Shape 3 (correct): the subtype template calc is owned by the HIF subtype."""
    hif = [
        cu
        for cu in ife_snapshot["calc_usages"]
        if cu.qualified_name.endswith("hif_plant__driver__hif_cost_calc")
    ]
    assert len(hif) == 1, [c.qualified_name for c in hif]
    assert hif[0].owning_part_def_qn == HIF_DRIVER


# --- Shape 7 (correct): two same-type siblings -----------------------------


def test_two_sibling_parts_each_produce_own_virtual_calc(ife_snapshot: dict) -> None:
    """Shape 7 (correct): the two same-type sibling chambers each produce their own
    instance-scoped virtual CalcUsage — the instance-ambiguity substrate Item 10's
    per-instance binding rewrite is tested against."""
    qns = _virtual_qns(ife_snapshot)
    yield_qns = {q for q in qns if q.endswith("yield_calc")}
    assert len(yield_qns) >= 2, yield_qns
    assert any(q.endswith("chamber_a__yield_calc") for q in yield_qns)
    assert any(q.endswith("chamber_b__yield_calc") for q in yield_qns)


# --- Shape 2 (known-incomplete): :>>-valued specialized def -----------------


def test_shape2_specialized_def_redefinition_captured(ife_snapshot: dict) -> None:
    """Shape 2 (known-incomplete baseline, mechanism A): the ``:>>``-set literal on
    the specialized ``Shielded Core`` def is captured as a redefinition. It is
    captured but unwired (no calc consumes ``Shielded Core``) — the baseline Item 9's
    literal pre-fill improves."""
    redefs = [
        r
        for r in ife_snapshot["hierarchy_data"].redefinitions
        if r.owning_part_qn == "IfePlantLib__Shielded_Core"
        and r.attribute_name == "scope_multiplier"
    ]
    assert len(redefs) == 1, ife_snapshot["hierarchy_data"].redefinitions
    assert redefs[0].literal_value == 3.0


# --- Shape 5 (known-incomplete): plain-usage :>> override dropped -----------


def test_shape5_plain_usage_override_dropped(ife_snapshot: dict) -> None:
    """Shape 5 (known-incomplete baseline, mechanism C): the plain-usage ``:>>``
    override on ``baseline_plant`` (``capacity_factor = 0.95``) is DROPPED at
    extraction — only the def default (0.90) survives. Pinning the drop is what makes
    Item 9's override-capture win show up as a baseline diff."""
    overrides = [
        a
        for attrs in ife_snapshot["design_attributes"].values()
        for a in attrs
        if a.name == "capacity_factor" and "baseline_plant" in a.qualified_name
    ]
    assert overrides == [], [o.qualified_name for o in overrides]
    # Only the def-level default (0.90) is present.
    def_level = [
        a
        for attrs in ife_snapshot["design_attributes"].values()
        for a in attrs
        if a.qualified_name == "IfePlantLib__Ife_Power_Plant__capacity_factor"
    ]
    assert len(def_level) == 1 and float(def_level[0].default_value) == 0.90


# ---------------------------------------------------------------------------
# Graph-build layer (license-free) — shape 4 conditional collector pin
# ---------------------------------------------------------------------------


# Shape 4 (known-incomplete, mechanism B): the exact expected uncovered cross-part
# input. Items 9-10 flip this as they wire the chain. Pinned as (module, input,
# missing_key) tuples so the assertion is a definitive equality, not a bare count.
EXPECTED_UNCOVERED = {
    (
        "ifeplantdesign__magnet_system__cryo_load",
        "magnet_volume",
        "design_params.IfePlantDesign__magnet_system__cryo_load__magnet_volume",
    ),
}


def test_ife_plant_graph_builds(ife_snapshot: dict) -> None:
    """Every fixture builds its graph without raising (the success bar — unresolved
    cross-part inputs fall to Step-4 fallback EPs, they do not stop assembly)."""
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("ife_plant"))
    assert graph.modules


def test_cross_part_inputs_pinned_or_baseline() -> None:
    """Shape 4 (known-incomplete): the deliberately-unwired cross-part chain.

    Conditional on Item 7's ``collect_uncovered_params`` (satisfiable at either
    landing order):
    - *Item 7 landed* (current): pin the EXACT expected uncovered set — shape 4's
      ``cryo_load.magnet_volume`` fell through to a valueless wired fallback EP.
      Items 9-10 flip this.
    - *Item 7 absent*: assert only that the graph builds; the warning set is the
      recorded baseline (see the module docstring / plan notes).
    """
    graph, _ = build_full_graph_from_snapshot(snapshot_fixture("ife_plant"))
    collector = getattr(gb, "collect_uncovered_params", None)
    if callable(collector):
        actual = {(u.module, u.input, u.missing_key) for u in collector(graph)}
        assert actual == EXPECTED_UNCOVERED, actual
    else:  # pragma: no cover - Item 7 has landed in this repo
        assert graph.modules


# ---------------------------------------------------------------------------
# Live extractor layer (license-gated)
# ---------------------------------------------------------------------------


@requires_license
def test_ife_plant_loads_live() -> None:
    """ife_plant loads through ``SysMLDataExtractor`` (all six shapes co-exist in one
    parseable model)."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    ex = SysMLDataExtractor([FIXTURES_DIR / "ife_plant"])
    assert ex.load_models()
