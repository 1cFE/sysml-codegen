"""The block-reason renderer, over hand-built diagnostics.

The de-duplication and the ordering share one key — the full normalized identity
`(basename(file), line, column, reason, construct, message)`. Because the order key *is*
the de-dup identity, no two survivors can tie, so the rendered text never falls back to
the companion's walk order.

Two failure modes are cheap to write and expensive to land: a `None` `line` compared
against an `int` raises `TypeError` at sort time, and two entries differing only in
`construct` survive de-dup and then tie. Both are pinned here rather than left to a
licensed fixture that happens not to produce them.
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.constraint_facts import LocationFact
from agentic_mbse.sysml.executable_profile import EligibilityDiagnostic
from agentic_mbse.sysml.expression_facts import IdentityFact

from sysml_codegen.elaboration.elaborate import _render_block_reasons

_IDENTITY = IdentityFact(kind="AssertConstraintUsage", name="guard", qualified_name="P::guard")


def _diagnostic(
    reason: str = "block_feature_chain",
    construct: str = "feature_chain",
    message: str = "chain 'a.b' is not executable",
    location: LocationFact | None = LocationFact(file="/abs/path/model.sysml", line=7, column=9),
) -> EligibilityDiagnostic:
    return EligibilityDiagnostic(
        reason=reason,
        construct=construct,
        location=location,
        constraint_identity=_IDENTITY,
        message=message,
    )


def test_a_present_location_renders_as_basename_and_line() -> None:
    """Never the absolute path: it differs per checkout and poisons any baseline."""
    assert _render_block_reasons([_diagnostic()]) == (
        "block_feature_chain: chain 'a.b' is not executable [model.sysml:7]"
    )


@pytest.mark.parametrize(
    "location",
    [
        None,
        LocationFact(file="", line=7, column=9),
        LocationFact(file="model.sysml", line=None, column=9),  # type: ignore[arg-type]
    ],
    ids=["no-location-fact", "empty-file", "no-line"],
)
def test_an_absent_location_renders_no_suffix_at_all(location: LocationFact | None) -> None:
    """A placeholder would advertise a location that does not exist (D6/M4)."""
    rendered = _render_block_reasons([_diagnostic(location=location)])
    assert rendered == "block_feature_chain: chain 'a.b' is not executable"


def test_a_none_line_or_column_never_raises_at_sort_time() -> None:
    """M1: every key field is normalized independently, so no `None` meets an `int`."""
    diagnostics = [
        _diagnostic(location=LocationFact(file="m.sysml", line=None, column=None)),  # type: ignore[arg-type]
        _diagnostic(message="other", location=LocationFact(file="m.sysml", line=2, column=0)),
        _diagnostic(message="third", location=None),
    ]
    assert _render_block_reasons(diagnostics).count("; ") == 2


def test_identical_diagnostics_collapse_to_one_entry() -> None:
    """The 13-copy `LayerContinuity` case, in miniature."""
    assert _render_block_reasons([_diagnostic()] * 13) == _render_block_reasons([_diagnostic()])


def test_two_entries_differing_only_in_construct_order_stably() -> None:
    """`construct` is in the key, so these survive de-dup *and* cannot tie."""
    first = _diagnostic(construct="feature_chain")
    second = _diagnostic(reason="block_invocation", construct="invocation")
    assert _render_block_reasons([first, second]) == _render_block_reasons([second, first])


def test_the_rendered_detail_is_one_line() -> None:
    """Invariant 8, at the one place that builds the string."""
    rendered = _render_block_reasons(
        [_diagnostic(), _diagnostic(message="second"), _diagnostic(location=None)]
    )
    assert "\n" not in rendered
    assert rendered.count("; ") == 2
