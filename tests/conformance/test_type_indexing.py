"""Conformance tests for part-usage type indexing (SC-3, Item 4).

Two extraction sites used to pick a usage's type by list position
(``next(iter(usage.types))``), so a retyped ``part :>> driver : 'HIF Driver'`` was
indexed only under its supertype and the subtype's template calcs were silently
dropped. The fix indexes each usage under *all* its user-model types (owned
FeatureTyping targets ∪ user PartDefs in ``.types``) and resolves ``usage_type_map``
to the most-specific owned typing.

The ``retype_model`` fixture carries the pinned shape matrix:

- Shape 1: the retyped ``the_variant.driver`` instantiates the HIF-owned template
  (``hif_calc``).
- Shape 2: it still instantiates the IFE-owned (supertype) template (``ife_calc``).
- Shape 3: IFE and HIF both own a same-named ``shared_calc`` → one virtual QN →
  most-specific (HIF) wins + the V9 collision warning.
- Shape 4: ``ife_calc`` and ``hif_calc`` are differently named → both instantiate.
- Shape 5: the plain ``plain_hif : 'HIF Driver'`` sibling is NOT reached by the
  IFE-owned template (the deferred supertype-chain walk is a Non-Goal).

Two layers:

- **Offline snapshot** (license-free) asserts the committed ``retype_model`` snapshot:
  virtual instances, the collision winner, the plain-sibling negative, the
  most-specific ``usage_type_map``, and the V10 incomparable warning (which lands in
  ``hierarchy_data.warnings``).
- **Live extractor** (skips without a license) asserts the index key set directly
  (REQ-EXT-13) and the V9 collision warning, which is an extraction-report warning
  not serialized into the snapshot.

REQ-EXT-13: index each PartUsage under all its owned FeatureTyping targets and every
            user-model PartDefinition in ``usage.types``.
REQ-EXT-14: same-named collision keeps the most-specific owner + warns; differently
            named templates both instantiate.
REQ-LVP-08: ``usage_type_map`` resolves to the most-specific owned typing;
            incomparable multi-typings resolve deterministically with a warning.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.extraction.usage_extractor import (
    _build_part_usage_index,
    extract_calculation_usages,
)
from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import snapshot_fixture

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

IFE = "RetypeLibrary__IFE_Driver"
HIF = "RetypeLibrary__HIF_Driver"
VARIANT_DRIVER = ("RetypeLibrary__Variant", "driver")
FACILITY_DRIVER = ("RetypeLibrary__Facility", "driver")
MULTI = ("RetypeLibrary__MultiHolder", "multi")


# ---------------------------------------------------------------------------
# Offline snapshot layer (license-free)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def retype_snapshot() -> dict:
    """Load the committed retype_model extraction snapshot."""
    return load_extraction_snapshot(snapshot_fixture("retype_model"))


def _virtual_qns(snapshot: dict) -> set[str]:
    return {cu.qualified_name for cu in snapshot["calc_usages"]}


def _owner_of(snapshot: dict, qn_suffix: str) -> str | None:
    """Owner of the single virtual whose QN ends with ``qn_suffix`` (None if absent)."""
    matches = [
        cu for cu in snapshot["calc_usages"] if cu.qualified_name.endswith(qn_suffix)
    ]
    assert len(matches) <= 1, [m.qualified_name for m in matches]
    return matches[0].owning_part_def_qn if matches else None


@pytest.mark.req(id="REQ-EXT-13")
def test_subtype_and_supertype_templates_both_instantiate(retype_snapshot: dict) -> None:
    """Shapes 1, 2, 4: the retyped driver instantiates both the HIF-owned and the
    IFE-owned (preserved supertype) template, under differently-named virtual QNs."""
    qns = _virtual_qns(retype_snapshot)
    assert any(q.endswith("the_variant__driver__hif_calc") for q in qns)  # shape 1
    assert any(q.endswith("the_variant__driver__ife_calc") for q in qns)  # shape 2
    # Differently named -> both survive (shape 4).
    assert _owner_of(retype_snapshot, "the_variant__driver__hif_calc") == HIF
    assert _owner_of(retype_snapshot, "the_variant__driver__ife_calc") == IFE


@pytest.mark.req(id="REQ-EXT-14")
def test_same_named_collision_tiebreak(retype_snapshot: dict) -> None:
    """Shape 3: the same-named shared_calc resolves to ONE virtual QN owned by the
    most-specific type (HIF), not two, and not the supertype."""
    shared = [
        cu
        for cu in retype_snapshot["calc_usages"]
        if cu.qualified_name.endswith("the_variant__driver__shared_calc")
    ]
    assert len(shared) == 1, [c.qualified_name for c in shared]
    assert shared[0].owning_part_def_qn == HIF


@pytest.mark.req(id="REQ-EXT-13")
def test_plain_sibling_not_reached_by_supertype_template(retype_snapshot: dict) -> None:
    """Shape 5 (Non-Goal guard): the IFE-owned (supertype) template MUST NOT reach the
    plain subtype-typed sibling; only its HIF-owned templates do."""
    qns = _virtual_qns(retype_snapshot)
    assert not any(q.endswith("plain_hif__ife_calc") for q in qns)
    # The HIF-owned templates DO reach it (the plain usage is keyed under HIF).
    assert any(q.endswith("plain_hif__hif_calc") for q in qns)


@pytest.mark.req(id="REQ-LVP-08")
def test_usage_type_map_resolves_retyped_to_declared(retype_snapshot: dict) -> None:
    """FIX 2: the retyped usage's usage_type_map entry is its DECLARED (subtype) type,
    while the plain Facility.driver stays on the supertype."""
    utm = retype_snapshot["hierarchy_data"].usage_type_map
    assert utm[VARIANT_DRIVER] == HIF
    assert utm[FACILITY_DRIVER] == IFE


@pytest.mark.req(id="REQ-LVP-08")
def test_usage_type_map_incomparable_resolves_and_warns(retype_snapshot: dict) -> None:
    """V10: two unrelated owned typings resolve to sorted-first + a warning."""
    hd = retype_snapshot["hierarchy_data"]
    assert hd.usage_type_map[MULTI] == IFE  # sorted-first of {IFE, Other}
    assert any(
        "incomparable owned types" in w and "MultiHolder.multi" in w
        for w in hd.warnings
    ), hd.warnings


# ---------------------------------------------------------------------------
# Live extractor layer (license-gated)
# ---------------------------------------------------------------------------


def _load_live_model():
    """Load the retype_model live; skip (not fail) when syside is unavailable."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    extractor = SysMLDataExtractor([FIXTURES_DIR / "retype_model"])
    try:
        loaded = extractor.load_models()
    except ImportError as exc:  # syside license not configured
        pytest.skip(f"syside unavailable: {exc}")
    if not loaded:
        pytest.skip("Could not load retype_model")
    return extractor


@pytest.mark.req(id="REQ-EXT-13")
def test_retyped_usage_indexed_under_both_types_live() -> None:
    """INV-1: the retyped Variant.driver is keyed under BOTH its supertype (IFE) and
    its declared subtype (HIF) — the superset index, verified on the raw model."""
    from agentic_mbse.sysml.syside_adapter import SysideAdapter

    from sysml_codegen.core.qualified_names import build_element_qualified_name

    extractor = _load_live_model()
    index = _build_part_usage_index(extractor.model)

    assert IFE in index and HIF in index

    def _retyped_driver(usages: list) -> object | None:
        for usage in usages:
            owner = getattr(usage, "owning_type", None)
            if (
                getattr(usage, "name", None) == "driver"
                and owner is not None
                and build_element_qualified_name(owner) == "RetypeLibrary__Variant"
            ):
                return usage
        return None

    driver_under_hif = _retyped_driver(index[HIF])
    assert driver_under_hif is not None, "retyped driver missing from HIF key"
    # The SAME usage element is keyed under IFE too (superset, not either-or).
    assert driver_under_hif in index[IFE]
    # sanity: SysideAdapter import used so the live path is genuinely exercised
    assert SysideAdapter is not None


@pytest.mark.req(id="REQ-EXT-14")
def test_collision_emits_v9_warning_live() -> None:
    """V9 is an extraction-report warning (not serialized into the snapshot): the
    same-named collision names both owners and the most-specific winner."""
    extractor = _load_live_model()
    calc_defs = extractor.extract_calculation_definitions()
    _usages, report = extract_calculation_usages(extractor.model, calc_defs=calc_defs)

    collision = [w for w in report.warnings if "Template collision" in w]
    assert collision, report.warnings
    msg = collision[0]
    assert "shared_calc" in msg
    assert HIF in msg and IFE in msg
    assert f"kept most-specific owner '{HIF}'" in msg
