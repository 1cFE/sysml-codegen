"""Acceptance: the ambiguous/defaulted producer coordinate (Item 10, RED-first).

Contract acceptance row "Ambiguous/defaulted producer resolution": a model with two
same-leaf candidate design attributes and a defaulted-fallback shape must fail with a
named ambiguity/producer error, or resolve only under exact QN — and produce **no verdict
from a guessed or defaulted binding while V11 is clean.**

This exercises the property at the real resolver+check boundary (license-free): a genuine
two-same-leaf tie driven through ``resolve_producer`` under capture, then the completeness
check reads the recorded outcome. The named error is the **check's**, not the resolver's —
today the resolver refuses to pick (``_unique_or_tie``) and falls through to a synthesized
entry point carrying the tied QNs; the completeness check is what turns that into a named
ambiguity violation.

The captured-snapshot fixture route (``two_same_leaf_producers/`` — both public extraction
routes) is authored alongside; see that fixture's ``README`` for capture state.
"""

from __future__ import annotations

from pathlib import Path

from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.resolution.producer_completeness import (
    CompletenessViolationKind,
    check_producer_completeness,
)
from sysml_codegen.resolution.producer_resolution import (
    Outcome,
    ProducerContext,
    ProducerRequest,
    TerminalPolicy,
    capturing_resolutions,
    resolve_producer,
)


def _same_leaf_context() -> ProducerContext:
    """Two design attributes sharing the leaf name ``cost`` in different scopes — the
    ambiguity is real: two candidates, no exact-QN discriminator on a bare reference."""
    cost_a = DesignAttributeData(
        name="cost",
        sysml_type="Real",
        default_value="10.0",
        unit=None,
        source_file=Path("model.sysml"),
        source_line=1,
        parent_part="pkg.a",
        qualified_name="pkg__a__cost",
    )
    cost_b = DesignAttributeData(
        name="cost",
        sysml_type="Real",
        default_value="20.0",
        unit=None,
        source_file=Path("model.sysml"),
        source_line=2,
        parent_part="pkg.b",
        qualified_name="pkg__b__cost",
    )
    return ProducerContext(
        output_registry=OutputRegistry(),
        design_attrs=(cost_a, cost_b),
        # Exact-QN rows (16-18) key this dict by the sanitized QN (`__` collapses to `_`);
        # the name-based rows (19-21) scan design_attrs by bare name.
        design_attr_by_qn={"pkg_a_cost": cost_a, "pkg_b_cost": cost_b},
    )


def _bare_leaf_request() -> ProducerRequest:
    """A bare-leaf consumer reference — reaches the lenient name-based rows (19-21) and
    ties. A scope-qualified reference would resolve cleanly and never tie, so the bare
    form is what exercises the property."""
    return ProducerRequest(
        consumer_eqn="pkg__plant__consumer",
        reference="cost",
        param_name=None,
        consumer_scope="pkg.plant",
        policy=TerminalPolicy.LENIENT,
        diagnostic_context="ambiguous-producer acceptance",
    )


def test_bare_leaf_tie_is_refused_by_resolver_not_guessed() -> None:
    """The resolver never first-picks: a same-leaf tie yields ENTRY_POINT carrying both
    tied QNs, not a bound value."""
    ctx = _same_leaf_context()
    res = resolve_producer(_bare_leaf_request(), ctx)
    assert res.outcome is Outcome.ENTRY_POINT
    assert set(res.ambiguous_candidates) == {"pkg__a__cost", "pkg__b__cost"}


def test_completeness_check_names_the_ambiguity() -> None:
    """The named ambiguity/producer error is the completeness check firing on the recorded
    tie — no verdict is produced from a guessed binding."""
    ctx = _same_leaf_context()
    with capturing_resolutions() as sink:
        resolve_producer(_bare_leaf_request(), ctx)
    violations = check_producer_completeness(sink)
    assert len(violations) == 1
    assert violations[0].kind is CompletenessViolationKind.AMBIGUOUS_PRODUCER
    assert violations[0].reference == "cost"
    assert "pkg__a__cost" in violations[0].message()


def test_exact_qn_reference_resolves_cleanly_no_violation() -> None:
    """The exact-QN escape: a reference carrying its resolved referent (row 17 target_qn)
    resolves under exact identity and raises no completeness violation."""
    ctx = _same_leaf_context()
    exact = ProducerRequest(
        consumer_eqn="pkg__plant__consumer",
        reference="cost",
        param_name=None,
        consumer_scope="pkg.plant",
        policy=TerminalPolicy.LENIENT,
        diagnostic_context="exact-qn escape",
        target_qn="pkg__b__cost",
    )
    with capturing_resolutions() as sink:
        res = resolve_producer(exact, ctx)
    assert res.outcome is Outcome.DESIGN_ATTRIBUTE
    assert res.identity == "pkg_b_cost"  # sanitized exact QN
    assert res.key_form == "target_qn"
    assert check_producer_completeness(sink) == []
