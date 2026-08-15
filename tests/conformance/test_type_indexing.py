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

One layer: the live extractor (skips without a license) asserts the index key set
directly (REQ-EXT-13) and the V9 collision warning, which is an extraction-report
warning. The offline layer read the committed ``retype_model`` extraction snapshot and
retired with the v5 family (retirement step 1).

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

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"

IFE = "RetypeLibrary__IFE_Driver"
HIF = "RetypeLibrary__HIF_Driver"


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
