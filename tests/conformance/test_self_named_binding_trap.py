"""Conformance tests for the isolated self-named-binding trap (Item 8, UPSTREAM-FINDINGS).

``self_named_binding_trap`` is a minimal fixture containing exactly the mechanism-D
trap — a self-named binding ``in availability = availability`` — and nothing else, so
its failure mode cannot be confounded. It lives in its OWN fixture directory (not
inside ife_plant) because the epic flags self-named-binding recursion as a syside-level
concern (register A-1): if the trap recursed during extraction, a co-located trap would
hang the whole ife_plant snapshot that Items 9-11 depend on.

## Observed failure mode (Item 8 live probe, 2026-07-05): (a) finite degenerate

The trap **extracts cleanly** — no recursion, no hang, no diagnostic. The self-named
binding resolves to the calc usage's OWN parameter
(``TrapLib::'Trap Plant'::avail_calc::availability``, a REFERENCE self-reference), NOT
the outer part attribute ``Trap Plant::availability``. This is the degenerate baseline
the spec names as branch (a): captured as-is, the baseline Items 9/12 later correct.

The recursion the toy's comments documented is an *evaluation-time* syside behavior
(expression evaluation spinning to the step limit), on a different path than
*extraction*. Extraction of the trap is finite. So no register A-1 recursion vendor
note is triggered by this probe — recorded for Item 12.

The fixture is captured **extraction-only** (``EXTRACTION_ONLY_MODELS``) — it needs no
pipeline baseline; the degenerate binding is fully visible in the extraction snapshot.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import requires_license, snapshot_fixture

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture(scope="module")
def trap_snapshot() -> dict:
    """Load the committed self_named_binding_trap extraction snapshot.

    The trap survived capture (benign branch), so a snapshot ships. If a future
    re-capture recursed, the fixture would ship without a snapshot and this fixture
    would need a skip guard — but the Item 8 probe observed finite degenerate
    resolution.
    """
    return load_extraction_snapshot(snapshot_fixture("self_named_binding_trap"))


def test_trap_baseline_recorded(trap_snapshot: dict) -> None:
    """The trap captured a finite baseline (branch a): exactly one calc usage."""
    qns = {cu.qualified_name for cu in trap_snapshot["calc_usages"]}
    assert qns == {"TrapDesign__trap_plant__avail_calc"}, qns


@pytest.mark.req("REQ-VBR-10")
def test_self_named_binding_resolves_to_own_param(trap_snapshot: dict) -> None:
    """Degenerate baseline (mechanism D): the self-named ``in availability =
    availability`` resolves to the calc usage's OWN parameter, not the outer part
    attribute. Pinning this is what makes Item 9's self-named-binding rescue show up
    as a baseline diff."""
    (avail_calc,) = trap_snapshot["calc_usages"]
    bindings = [b for b in avail_calc.bindings if b.param_name == "availability"]
    assert len(bindings) == 1, avail_calc.bindings
    b = bindings[0]
    # Degenerate: the source path points at the calc's own parameter (self-ref),
    # NOT the outer 'Trap Plant'::availability attribute.
    assert b.source_path == "TrapLib::'Trap Plant'::avail_calc::availability"


@requires_license
def test_trap_extracts_without_recursion() -> None:
    """The trap loads and extracts finitely (no recursion/hang) — the isolation
    guarantee that keeps ife_plant safe. Runs under the suite's own process timeout;
    a recursion here would surface as a timeout, not a pass."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    ex = SysMLDataExtractor([FIXTURES_DIR / "self_named_binding_trap"])
    assert ex.load_models()
    calc_defs = ex.extract_calculation_definitions()
    assert [c.qualified_name for c in calc_defs] == ["TrapLib::AvailabilityCalc"]
