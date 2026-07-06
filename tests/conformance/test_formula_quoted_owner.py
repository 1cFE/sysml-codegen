"""SC #2 R1 lock: FORMULA wire under a quoted owner (Item 5, INV-5).

A quoted-named owner part (``'Margin Part'``) owns a FORMULA computed attribute
(``'net margin'`` -> python_name ``net_margin``) that a second same-part FORMULA
attribute (``total_payout = 'net margin' * 2.0``) consumes. The consumer wires
through the in-memory ``resolution_map`` (``graph_builder.py:745``, consumed at
``:823``) -- the Item-5 FORMULA-derivation path, per the design appendix -- NOT
through the raw SysML-QN REFERENCE match sites (``dependency_backtracker.py``
``:473/:595``), which are Item 7's.

The lock is a *path-resolved* assertion, not string equality of two derivations:
the channel the consumer actually resolved to must equal the channel the output
registry registered for the FORMULA output. On raw code they diverge -- the
consumer resolves the graph-side module output (raw ``net margin``) while the
registry registers the python_name form (``net_margin``) -- so this test is RED
before M1 and GREEN after (producer == consumer by construction).

Requirement: REQ-NC-08.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.core.identifier_types import ScopedKey
from sysml_codegen.orchestration.snapshot_context import (
    build_pipeline_context_from_snapshot,
)

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "quoted_owner_formula"
    / "extraction_snapshot.json"
)

# The sanitized channel both sides must agree on after M1: the quoted owner
# 'Margin Part' -> Margin_Part; the FORMULA leaf comes from python_name.
_EXPECTED_CHANNEL = (
    "QuotedOwnerFormulaDesign__Margin_Part__net_margin__net_margin"
)
# key_f for the FORMULA output: owning_part_name (already sanitized at capture)
# + python_name. Stable across the fix -- only the channel *value* changes.
_FORMULA_KEY_F = "Margin_Part.net_margin"
# python_name of the FORMULA input the consumer (total_payout) reads.
_CONSUMER_INPUT = "net_margin"


def _consumer_resolved_channel(ctx) -> str | None:
    """The channel the consumer module actually resolved its FORMULA input to."""
    for module in ctx.computation_graph.modules:
        if module.name.endswith("__total_payout"):
            for inp in module.inputs:
                if inp.param_name == _CONSUMER_INPUT:
                    assert inp.source.source_type == "module_output", (
                        f"consumer input did not wire to a module output: "
                        f"{inp.source.source_type}"
                    )
                    return inp.source.producer_channel
    raise AssertionError("total_payout consumer module or net_margin input not found")


@pytest.mark.req("REQ-NC-08")
def test_formula_quoted_owner_channel_resolves() -> None:
    """The consumer's resolved channel equals the registry's registered channel.

    Path-resolved lock (INV-5): proves the FORMULA wire actually resolved under a
    quoted owner, not merely that two derivations are string-equal. RED before
    M1 (registry uses python_name, graph uses raw ``ca.name``); GREEN after.
    """
    ctx = build_pipeline_context_from_snapshot(FIXTURE)

    registered = ctx.output_registry.scoped_lookup(ScopedKey(_FORMULA_KEY_F))
    resolved = _consumer_resolved_channel(ctx)

    assert registered is not None, "FORMULA output not registered under its key_f"
    assert resolved == registered, (
        "FORMULA wire did not resolve under a quoted owner: consumer resolved "
        f"{resolved!r} but registry registered {registered!r}"
    )
    # The agreed channel is fully sanitized -- no quotes or spaces leaked.
    assert registered == _EXPECTED_CHANNEL, (
        f"registered channel is not sanitized: {registered!r}"
    )
