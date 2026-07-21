"""Unit tests for the producer-completeness check and its capture sink (Item 10).

The check reads recorded resolver outcomes (the capture sink); it does not re-resolve.
These tests exercise the check's logic directly on hand-built ``CapturedResolution``s and
the sink's capture behavior on a real ``resolve_producer`` call.
"""

from __future__ import annotations

from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.resolution.producer_completeness import (
    CompletenessViolationKind,
    check_producer_completeness,
)
from sysml_codegen.resolution.producer_resolution import (
    CapturedResolution,
    Outcome,
    ProducerContext,
    ProducerRequest,
    ProducerResolution,
    TerminalPolicy,
    capturing_resolutions,
    resolve_producer,
)


def _req(reference: str, consumer: str = "pkg__plant__consumer") -> ProducerRequest:
    return ProducerRequest(
        consumer_eqn=consumer,
        reference=reference,
        param_name=None,
        consumer_scope="pkg.plant",
        policy=TerminalPolicy.LENIENT,
        diagnostic_context="test",
    )


def _cap(reference: str, resolution: ProducerResolution) -> CapturedResolution:
    return CapturedResolution(request=_req(reference), resolution=resolution)


# --- The check's logic --------------------------------------------------------------


def test_ambiguous_producer_is_flagged() -> None:
    """A tie (ambiguous_candidates non-empty) is an ambiguous-producer violation — the
    RED-coordinate signal."""
    cap = _cap(
        "cost",
        ProducerResolution(
            outcome=Outcome.ENTRY_POINT,
            identity="pkg__plant__consumer__cost",
            ambiguous_candidates=("pkg__a__cost", "pkg__b__cost"),
        ),
    )
    violations = check_producer_completeness([cap])
    assert len(violations) == 1
    assert violations[0].kind is CompletenessViolationKind.AMBIGUOUS_PRODUCER
    assert "pkg__a__cost" in violations[0].detail


def test_qualified_leaf_name_guess_is_flagged() -> None:
    """A QUALIFIED reference (``part.attr``) resolved via a name-based lenient row by
    dropping its qualifier is a leaf-name-guess violation (the scope-collapse defect)."""
    cap = _cap(
        "magnet.cost",
        ProducerResolution(
            outcome=Outcome.DESIGN_ATTRIBUTE,
            identity="pkg__a__cost",
            key_form="leaf_unique",
        ),
    )
    violations = check_producer_completeness([cap])
    assert len(violations) == 1
    assert violations[0].kind is CompletenessViolationKind.LEAF_NAME_GUESS


def test_qualified_channel_tier_leaf_guess_is_flagged() -> None:
    """Audit Major 1: a QUALIFIED reference resolved to a MODULE_OUTPUT via a name-based
    CHANNEL row (leaf_parent_scoped / leaf_consumer_scoped) drops its scope qualifier just
    like the design-attribute rows — the MODULE_OUTPUT exemption must NOT hide it."""
    for row in ("leaf_parent_scoped", "leaf_consumer_scoped"):
        cap = _cap(
            "sibling.power",
            ProducerResolution(
                outcome=Outcome.MODULE_OUTPUT,
                identity="pkg__plant__consumer__power",  # the consumer's own, not sibling's
                key_form=row,
            ),
        )
        v = check_producer_completeness([cap])
        assert len(v) == 1, row
        assert v[0].kind is CompletenessViolationKind.LEAF_NAME_GUESS, row


def test_structural_channel_row_is_exempt() -> None:
    """chain_redefinition_follow (row 13) consults the reference's own owner and follows
    :>> redefinitions structurally — a MODULE_OUTPUT via it is NOT a guess."""
    cap = _cap(
        "magnet.capital_cost",
        ProducerResolution(
            outcome=Outcome.MODULE_OUTPUT,
            identity="inst__magnet_cost__capital_cost",
            key_form="chain_redefinition_follow",
        ),
    )
    assert check_producer_completeness([cap]) == []


def test_scoped_channel_row_is_exempt() -> None:
    """An exact scoped channel row (scoped_prefixed) is structural — exempt."""
    cap = _cap(
        "chamber.power",
        ProducerResolution(
            outcome=Outcome.MODULE_OUTPUT,
            identity="pkg__plant__chamber__power",
            key_form="scoped_prefixed",
        ),
    )
    assert check_producer_completeness([cap]) == []


def test_bare_name_unique_is_exempt() -> None:
    """A BARE reference matched by bare_name_unique (a unique surviving candidate, no
    qualifier to drop) is the intended producer resolved by its only handle — not a guess."""
    cap = _cap(
        "markup",
        ProducerResolution(
            outcome=Outcome.DESIGN_ATTRIBUTE,
            identity="pkg__bank__markup",
            key_form="bare_name_unique",
        ),
    )
    assert check_producer_completeness([cap]) == []


def test_clean_entry_point_is_exempt() -> None:
    """A clean ENTRY_POINT with no ties and no name-based form is a legitimate external
    declared input — not flagged."""
    cap = _cap(
        "availability",
        ProducerResolution(
            outcome=Outcome.ENTRY_POINT,
            identity="pkg__plant__consumer__availability",
        ),
    )
    assert check_producer_completeness([cap]) == []


def test_module_output_is_exempt() -> None:
    """An exact producer channel is the conformant path — not flagged."""
    cap = _cap(
        "chamber.power",
        ProducerResolution(
            outcome=Outcome.MODULE_OUTPUT,
            identity="pkg__plant__chamber__power",
            key_form="scoped_prefixed",
        ),
    )
    assert check_producer_completeness([cap]) == []


def test_exact_qn_design_attribute_is_exempt() -> None:
    """A design attribute resolved under exact QN (target_qn) is conformant — not flagged."""
    cap = _cap(
        "a::cost",
        ProducerResolution(
            outcome=Outcome.DESIGN_ATTRIBUTE,
            identity="pkg__a__cost",
            key_form="target_qn",
        ),
    )
    assert check_producer_completeness([cap]) == []


def test_multiple_violations_all_reported() -> None:
    caps = [
        _cap(
            "cost",
            ProducerResolution(
                outcome=Outcome.ENTRY_POINT,
                identity="x",
                ambiguous_candidates=("a", "b"),
            ),
        ),
        _cap(
            "driver.gain",
            ProducerResolution(
                outcome=Outcome.DESIGN_ATTRIBUTE, identity="y", key_form="leaf_unique"
            ),
        ),
        _cap(
            "ok",
            ProducerResolution(outcome=Outcome.MODULE_OUTPUT, identity="z"),
        ),
    ]
    kinds = {v.kind for v in check_producer_completeness(caps)}
    assert kinds == {
        CompletenessViolationKind.AMBIGUOUS_PRODUCER,
        CompletenessViolationKind.LEAF_NAME_GUESS,
    }


# --- The capture sink ---------------------------------------------------------------


def test_sink_captures_a_real_resolution() -> None:
    """resolve_producer records into the active sink; the check reads it — no re-resolution."""
    ctx = ProducerContext(output_registry=OutputRegistry())
    req = _req("nowhere.at.all")
    with capturing_resolutions() as sink:
        resolve_producer(req, ctx)
        resolve_producer(req, ctx)
    assert len(sink) == 2
    assert all(isinstance(c, CapturedResolution) for c in sink)


def test_sink_inactive_outside_context() -> None:
    """No sink active → resolve_producer still works and records nothing."""
    ctx = ProducerContext(output_registry=OutputRegistry())
    res = resolve_producer(_req("nowhere"), ctx)
    assert res.outcome is Outcome.ENTRY_POINT  # lenient terminal, no crash, no capture


def test_sink_nesting_is_reset_safe() -> None:
    ctx = ProducerContext(output_registry=OutputRegistry())
    with capturing_resolutions() as outer:
        resolve_producer(_req("a"), ctx)
        with capturing_resolutions() as inner:
            resolve_producer(_req("b"), ctx)
        assert len(inner) == 1
        resolve_producer(_req("c"), ctx)
    assert len(outer) == 2  # a and c, not b
