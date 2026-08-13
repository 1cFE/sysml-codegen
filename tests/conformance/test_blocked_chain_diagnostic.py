"""Defect B: a blocked feature chain must name the reference, the rewrite, and the place.

The companion decides and phrases the block; codegen renders what it is handed. Both
chain-block sites passed no `message`, so `_diagnostic`'s default
(`f"{construct}: {reason}"`) produced `feature_chain: block_feature_chain`, and codegen
rendered `f"{reason}: {message}"` on top of it — the reason twice, the reference never.
A three-chain predicate produced three identical copies of that in one string.

After this item the companion names the chain and the supported rewrite, and codegen
de-duplicates, orders, and renders `basename:line`.

Assertions here match the *chain text*, the `in ... =` rewrite fragment, and the
location — never the companion's full sentence. Two repos that agree on a sentence are
two repos coupled by a sentence.
"""

from __future__ import annotations

import re

import pytest

from sysml_codegen.elaboration import elaborate
from sysml_codegen.elaboration.elaborate import ElaborationDiagnosticError
from sysml_codegen.elaboration.graph import InstanceGraph
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "constraint_blocked_chain_multi"

_ITEM4_B = "CONSTRAINT-SEMANTICS Item 4 — Defect B (D3/D4/D5/D6)"


def _elaborate(*, strict: bool) -> InstanceGraph:
    extractor = SysMLDataExtractor([FIXTURE])
    assert extractor.load_models()
    assert extractor.diagnostics is not None
    return elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
        strict=strict,
    )


def _blocked_detail() -> str:
    graph = _elaborate(strict=False)
    [blocked] = [
        diagnostic
        for diagnostic in graph.diagnostics
        if diagnostic.code.value == "SI_CONSTRAINT_BLOCKED"
    ]
    return blocked.detail


def test_the_detail_names_each_blocked_chain_as_authored() -> None:
    detail = _blocked_detail()
    assert "bioshield.outer_radius" in detail
    assert "bioshield.inner_radius" in detail


def test_the_detail_states_the_bindings_rewrite() -> None:
    """The rewrite must be a *supported* form, and must be spelled out per chain."""
    detail = _blocked_detail()
    assert "in outer_radius = bioshield.outer_radius;" in detail
    assert "in inner_radius = bioshield.inner_radius;" in detail


@pytest.mark.xfail(strict=True, reason=_ITEM4_B)
def test_the_detail_names_the_source_location_by_basename() -> None:
    """`basename:line`, never the absolute path — an absolute path is checkout-dependent."""
    detail = _blocked_detail()
    assert re.search(r"\[model\.sysml:\d+\]", detail)
    assert str(FIXTURE) not in detail


@pytest.mark.xfail(strict=True, reason=_ITEM4_B)
def test_three_chain_occurrences_collapse_to_two_distinct_entries() -> None:
    """Identification, not repetition: the same reference twice is one entry."""
    assert _blocked_detail().count("block_feature_chain") == 2


def test_two_elaborations_of_one_model_produce_byte_identical_detail() -> None:
    """Determinism by construction — ordered by the de-dup key, never by walk order.

    Green before the fix as well as after: three identical tautologies are trivially
    stable. It is kept because the fix is what could break it, and the unit test over
    `_render_block_reasons` is where the key's totality is actually pinned.
    """
    assert _blocked_detail() == _blocked_detail()


def test_the_detail_is_a_single_line() -> None:
    """Invariant 8. Two consumers fold this string into a regex match on one line.

    Green before the fix: today's detail is one line, and it must stay one after.
    """
    assert "\n" not in _blocked_detail()


def test_one_blocked_constraint_node_still_yields_one_diagnostic() -> None:
    """Invariant 4: the message gets richer, the row count does not move."""
    graph = _elaborate(strict=False)
    blocked = [
        diagnostic
        for diagnostic in graph.diagnostics
        if diagnostic.code.value == "SI_CONSTRAINT_BLOCKED"
    ]
    assert len(blocked) == 1


def test_an_asserted_blocked_chain_still_halts() -> None:
    """The Item 2 contract is untouched: this item changes what the message says."""
    with pytest.raises(ElaborationDiagnosticError, match="SI_CONSTRAINT_BLOCKED"):
        _elaborate(strict=True)
