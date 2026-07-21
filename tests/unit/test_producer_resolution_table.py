"""The key-form table read as data (Item 2, invariants I2/I3/I4/I6).

These pins exist so drift becomes visible. The three ladders this replaces each invented
their own ordering, guard placement, and terminal behavior, and nothing failed when they
diverged. Here the order, the per-form admissibility, the refusal rule, the guard, and
the terminal fork are all observable, so a change to any of them breaks a test rather
than a fixture six months later.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.core.output_registry import OutputRegistry, ScopedKey
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.resolution.producer_resolution import (
    KEY_FORMS,
    Outcome,
    ProducerContext,
    ProducerRequest,
    TerminalPolicy,
    Tier,
    resolve_producer,
)

# The declared order, as data. Changing the table changes this list, deliberately.
_EXPECTED_ORDER = [
    (1, "scoped_prefixed", Tier.CHANNEL, False),
    (2, "scoped_deindexed", Tier.CHANNEL, False),
    (3, "scoped_bare", Tier.CHANNEL, False),
    (4, "alias_prefixed", Tier.CHANNEL, False),
    (5, "alias_deindexed", Tier.CHANNEL, False),
    (6, "scoped_alias_prefixed", Tier.CHANNEL, False),
    (7, "scoped_alias_deindexed", Tier.CHANNEL, False),
    (8, "structured_alias_unscoped", Tier.CHANNEL, False),
    (9, "structured_alias_deindexed", Tier.CHANNEL, False),
    (10, "alias_bare", Tier.CHANNEL, False),
    (11, "sysml_qn", Tier.CHANNEL, False),
    (12, "direct_channel", Tier.CHANNEL, False),
    (13, "chain_redefinition_follow", Tier.CHANNEL, True),
    (14, "leaf_parent_scoped", Tier.CHANNEL, True),
    (15, "leaf_consumer_scoped", Tier.CHANNEL, True),
    (16, "occurrence_materialized_qn", Tier.DESIGN_ATTRIBUTE, False),
    (17, "target_qn", Tier.DESIGN_ATTRIBUTE, False),
    (18, "owner_def_qn", Tier.DESIGN_ATTRIBUTE, False),
    (19, "dotted_pair", Tier.DESIGN_ATTRIBUTE, True),
    (20, "leaf_unique", Tier.DESIGN_ATTRIBUTE, True),
    (21, "bare_name_unique", Tier.DESIGN_ATTRIBUTE, True),
]


def _request(**overrides) -> ProducerRequest:
    base = {
        "consumer_eqn": "pkg__part__consumer",
        "reference": "missing_thing",
        "param_name": "formal",
        "consumer_scope": "part",
        "policy": TerminalPolicy.LENIENT,
        "diagnostic_context": "pkg__part__consumer.formal",
    }
    base.update(overrides)
    return ProducerRequest(**base)


def _context(channels: dict[str, str] | None = None, **kwargs) -> ProducerContext:
    registry = OutputRegistry()
    for key, channel in (channels or {}).items():
        registry.register_scoped(ScopedKey(key), channel)
    return ProducerContext(output_registry=registry, **kwargs)


def test_table_order_and_admissibility_are_declared():
    """I2: one ordered sequence, read as data — both order and per-form policy."""
    actual = [(f.number, f.name, f.tier, f.lenient_only) for f in KEY_FORMS]
    assert actual == _EXPECTED_ORDER


def test_tier_one_exhausts_before_tier_two():
    """Contract invariant 19: a real producer channel outranks a design attribute."""
    tiers = [f.tier for f in KEY_FORMS]
    assert tiers == sorted(tiers, key=lambda t: t.value)


def test_name_based_forms_are_exactly_the_lenient_only_ones():
    """D11: the forms that identify candidates by name are the restricted set."""
    assert {f.name for f in KEY_FORMS if f.lenient_only} == {
        "chain_redefinition_follow",
        "leaf_parent_scoped",
        "leaf_consumer_scoped",
        "dotted_pair",
        "leaf_unique",
        "bare_name_unique",
    }


def test_strict_consumer_never_attempts_a_name_based_form():
    """I4/D11: admissibility is applied by the table, not by the consumer.

    The constraint consumer's eleven lookups are all exact today; this keeps it that way
    when the shared table gains forms that are not.
    """
    with pytest.raises(CodeGenerationError) as excinfo:
        resolve_producer(_request(policy=TerminalPolicy.STRICT), _context())
    attempted = str(excinfo.value)
    for name in (
        "chain_redefinition_follow",
        "leaf_parent_scoped",
        "leaf_consumer_scoped",
        "dotted_pair",
        "leaf_unique",
        "bare_name_unique",
    ):
        assert name not in attempted


def test_lenient_consumer_attempts_every_form():
    resolution = resolve_producer(_request(), _context())
    assert resolution.outcome is Outcome.ENTRY_POINT
    for name in ("dotted_pair", "leaf_unique", "bare_name_unique", "scope_climb"):
        assert name in resolution.attempted


def test_self_reference_is_skipped_and_the_table_continues():
    """I6: the guard skips the candidate and keeps going, rather than abandoning the
    rest of the strategy — which is what the aggregation driver does today."""
    consumer = "pkg__part__consumer"
    context = _context(
        {
            # Row 1 would resolve to a channel the consumer itself produces.
            "part.thing": f"{consumer}__thing",
            # Row 3 reaches a real upstream producer.
            "thing": "pkg__part__upstream__thing",
        }
    )
    resolution = resolve_producer(_request(reference="thing"), context)
    assert resolution.outcome is Outcome.MODULE_OUTPUT
    assert resolution.identity == "pkg__part__upstream__thing"
    assert resolution.key_form == "scoped_bare"


def test_strict_terminal_miss_names_the_attempted_forms():
    """SR-R14: today's error carries three strings and names no attempted classes."""
    with pytest.raises(CodeGenerationError) as excinfo:
        resolve_producer(
            _request(policy=TerminalPolicy.STRICT, reference="nope"), _context()
        )
    message = str(excinfo.value)
    assert "nope" in message
    assert "scoped_prefixed" in message and "target_qn" in message
    assert "no fallback, no entry-point synthesis" in message


def test_lenient_terminal_miss_mints_under_the_declared_qn_rule():
    """I4: the lenient half of the one fork, keyed by D9."""
    resolution = resolve_producer(_request(reference="nope"), _context())
    assert resolution.outcome is Outcome.ENTRY_POINT
    assert resolution.identity == "pkg__part__consumer__formal"


def test_terminal_policy_is_the_only_fork():
    """SR-A06: one reference, two consumers, identical request shape.

    Both requests differ in exactly one field. The strict one raises and synthesizes
    nothing; the lenient one yields one deterministic typed entry point.
    """
    context = _context()
    lenient = resolve_producer(_request(policy=TerminalPolicy.LENIENT), context)
    assert lenient.outcome is Outcome.ENTRY_POINT
    with pytest.raises(CodeGenerationError):
        resolve_producer(_request(policy=TerminalPolicy.STRICT), context)


def test_dotted_pair_form_refuses_on_multiple_candidates():
    """Review note 3: row 19's re-typing needs its own pin.

    The dotted `(first segment, leaf)` form used to take the first hit in a scan. It now
    refuses when two design attributes tie, and records both. The `test_matcher_fixes_item7`
    coverage routes through the leaf-unique and bare-name forms, so it never exercises
    this one.
    """
    from sysml_codegen.analysis.parameter_groups import DesignAttributeData

    def _attr(qn: str) -> DesignAttributeData:
        return DesignAttributeData(
            name="power", sysml_type="Real", default_value="1.0", unit=None,
            source_file=Path("m.sysml"), source_line=1, parent_part="motor",
            qualified_name=qn,
        )

    tied = (_attr("Pkg__A__motor__power"), _attr("Pkg__B__motor__power"))
    resolution = resolve_producer(
        _request(reference="motor.power"),
        _context(design_attrs=tied, design_attr_by_qn={a.qualified_name: a for a in tied}),
    )
    assert resolution.outcome is Outcome.ENTRY_POINT, "a tie must not resolve"
    assert resolution.ambiguous_candidates == (
        "Pkg__A__motor__power",
        "Pkg__B__motor__power",
    )


def test_two_minters_disagreeing_on_a_default_refuse_rather_than_race():
    """Review note 4 / I5: the default is a function of identity, not of who ran first.

    PC-2 showed a second writer could shadow an entry point created by the calculation
    path, so the default a parameter ended up with depended on consumer iteration order.
    Agreeing defaults are idempotent; disagreeing ones leave the parameter defaultless
    and say so, rather than letting order pick a winner.
    """
    from sysml_codegen.resolution.graph_builder import _mint_entry_point_once

    new: dict = {}
    for value in (3.0, 7.0):
        _mint_entry_point_once(
            "Pkg__part__agg__x", simple_name="x", default_value=value,
            group_deriver=None, entry_points={}, new_entry_points=new,
        )
    assert new["Pkg__part__agg__x"].default_value is None

    agreed: dict = {}
    for value in (3.0, 3.0):
        _mint_entry_point_once(
            "Pkg__part__agg__y", simple_name="y", default_value=value,
            group_deriver=None, entry_points={}, new_entry_points=agreed,
        )
    assert agreed["Pkg__part__agg__y"].default_value == 3.0
