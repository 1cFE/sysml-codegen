"""Unit tests for the SC-3 type-indexing shared helpers.

The first proof point for Item 4 (Part-Usage Type Indexing): the most-specific
comparison over PartDef heritage. It returns the chain sink for a comparable pair
(the V9 collision tiebreak / usage_type_map most-specific pick) and a deterministic
sorted-first for an incomparable pair (the V10 incomparable-multi-typing branch).

``qn_to_partdef`` is built from a live-loaded probe model — the two PartDefs
``IFE Driver`` (base) and ``HIF Driver :> IFE Driver`` (subtype), plus the unrelated
``Other Driver`` — mirroring the ``_load_live_extractor`` skip convention: the test
skips (does not fail) when syside cannot load, e.g. no license in CI.

REQ-EXT-14 / REQ-LVP-08: most-specific-owner tiebreak; incomparable resolves
deterministically with a warning signalled by the returned ``incomparable`` flag.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from sysml_codegen.core.qualified_names import build_element_qualified_name
from sysml_codegen.extraction.usage_extractor import most_specific

PROBE_MODEL = (
    Path(__file__).resolve().parents[2]
    / ".project"
    / "active"
    / "type-indexing"
    / "probe"
    / "model.sysml"
)

IFE = "ProbePkg__IFE_Driver"
HIF = "ProbePkg__HIF_Driver"
OTHER = "ProbePkg__Other_Driver"


@pytest.fixture(scope="module")
def qn_to_partdef() -> dict[str, Any]:
    """Return a ``{__-form QN: PartDefElement}`` lookup from the live probe model.

    Skips when syside cannot load (no license) — the comparison logic is exercised
    live so ``most_specific`` reads real ``Subclassification`` heritage, not a stub.
    """
    from agentic_mbse.sysml.syside_adapter import SysideAdapter

    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    extractor = SysMLDataExtractor([PROBE_MODEL])
    try:
        loaded = extractor.load_models()
    except ImportError as exc:  # syside license not configured
        pytest.skip(f"syside unavailable: {exc}")
    if not loaded:
        pytest.skip("Could not load SC-3 probe model")

    lookup: dict[str, Any] = {}
    for part_def in SysideAdapter.elements_of_type(extractor.model, "PartDefinition"):
        qn = build_element_qualified_name(part_def)
        if qn:
            lookup[qn] = part_def
    # Guard: the shapes the test relies on must be present.
    assert {IFE, HIF, OTHER} <= set(lookup), sorted(lookup)
    return lookup


def test_most_specific_returns_chain_sink(qn_to_partdef: dict[str, Any]) -> None:
    """Comparable pair (HIF :> IFE) -> the subtype HIF wins, not incomparable."""
    winner, incomparable = most_specific([IFE, HIF], qn_to_partdef)
    assert winner == HIF
    assert incomparable is False


def test_most_specific_order_independent(qn_to_partdef: dict[str, Any]) -> None:
    """The chain sink wins regardless of input order (no reliance on list order)."""
    assert most_specific([HIF, IFE], qn_to_partdef) == (HIF, False)


def test_most_specific_incomparable_is_sorted_first(
    qn_to_partdef: dict[str, Any],
) -> None:
    """Incomparable pair -> sorted-first QN + incomparable flag (drives V10)."""
    winner, incomparable = most_specific([OTHER, IFE], qn_to_partdef)
    assert incomparable is True
    assert winner == sorted([OTHER, IFE])[0]  # 'ProbePkg__IFE_Driver'


def test_most_specific_single_target_no_warning(
    qn_to_partdef: dict[str, Any],
) -> None:
    """One target -> returned as-is, never flagged incomparable."""
    assert most_specific([IFE], qn_to_partdef) == (IFE, False)


def test_most_specific_zero_targets_returns_none(
    qn_to_partdef: dict[str, Any],
) -> None:
    """Zero targets -> (None, False); the caller skips (no type to resolve)."""
    assert most_specific([], qn_to_partdef) == (None, False)


def test_most_specific_dedups_repeated_target(
    qn_to_partdef: dict[str, Any],
) -> None:
    """A QN listed twice (declared type is both an owned typing and a .types entry)
    collapses to a single comparable candidate, never a spurious incomparable."""
    assert most_specific([HIF, HIF], qn_to_partdef) == (HIF, False)
