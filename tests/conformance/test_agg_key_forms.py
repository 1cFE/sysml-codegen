"""The aggregation consumer's key forms, after the cutover (Item 2, Phase 5b).

Replaces `test_input_resolver.py`, whose 27 tests exercised four private strategy
functions that no longer exist. Per SR-R43 the private mechanics go, but the observable
behavior each strategy carried migrates here, onto the table rows that now provide it:

| was | now |
|---|---|
| Strategy A, ScopedRegistryLookup | rows 1, 3, 4, 10 — scoped/alias, scope-prefixed then bare |
| Strategy B, SysMLQNLookup | row 11 — sanitized SysML QN |
| Strategy C, ChainRedefinitionFollow | row 13 — case-sensitive, refusing on multiple |
| Strategy E, DirectChannelConstruction | row 12 — constructed channel, membership-checked |
| the never-None entry-point fallback | the lenient terminal miss, keyed by the shared QN rule |
"""

from __future__ import annotations

from sysml_codegen.core.output_registry import OutputRegistry, ScopedKey, SysMLQN
from sysml_codegen.extraction.data_models import RedefinitionData, RedefinitionType
from sysml_codegen.resolution.producer_resolution import (
    Outcome,
    ProducerContext,
    ProducerRequest,
    TerminalPolicy,
    resolve_producer,
)

_MODULE = "design__plant__idiot_index"
_SCOPE = "plant"
_INSTANCE = "Design__plant"


def _seed_channel(registry: OutputRegistry, channel: str) -> None:
    """Put a channel in the canonical set without making it reachable by any key form.

    The registry derives `canonical_channels` from its registrations, and the forms
    under test here construct their own channel names and check membership. The seed key
    is a shape no key form builds, so it cannot short-circuit the row being tested.
    """
    registry.register_scoped(ScopedKey("__seed__"), channel)


def _resolve(ref: str, registry: OutputRegistry, **ctx_kwargs):
    return resolve_producer(
        ProducerRequest(
            consumer_eqn=_MODULE,
            reference=ref,
            param_name=None,
            consumer_scope=_SCOPE,
            instance_path=_INSTANCE,
            policy=TerminalPolicy.LENIENT,
            diagnostic_context=f"{_MODULE}|{ref}",
        ),
        ProducerContext(output_registry=registry, **ctx_kwargs),
    )


def test_scope_prefixed_scoped_key_resolves():
    """Strategy A's primary form: the consumer's scope is prepended to the reference."""
    registry = OutputRegistry()
    registry.register_scoped(ScopedKey("plant.pv.capital_cost"), "Design__plant__pv__capital_cost")
    resolved = _resolve("pv.capital_cost", registry)
    assert resolved.outcome is Outcome.MODULE_OUTPUT
    assert resolved.identity == "Design__plant__pv__capital_cost"
    assert resolved.key_form == "scoped_prefixed"


def test_unscoped_scoped_key_resolves_when_the_prefixed_one_misses():
    """Strategy A's unscoped fallback, e.g. a plant-level `solar_array.capital_cost`."""
    registry = OutputRegistry()
    registry.register_scoped(ScopedKey("pv.capital_cost"), "Design__plant__pv__capital_cost")
    resolved = _resolve("pv.capital_cost", registry)
    assert resolved.outcome is Outcome.MODULE_OUTPUT
    assert resolved.key_form == "scoped_bare"


def test_sysml_qualified_name_resolves_sanitized():
    """Strategy B: a `::` reference matches the per-segment-sanitized registration key."""
    registry = OutputRegistry()
    registry.register_sysml_qn(SysMLQN("Lib__Motor__power"), "Design__plant__motor__power")
    resolved = _resolve("Lib::Motor::power", registry)
    assert resolved.outcome is Outcome.MODULE_OUTPUT
    assert resolved.key_form == "sysml_qn"


def test_chain_redefinition_follow_reaches_a_constructed_channel():
    """Strategy C: a `:>>` CHAIN redefinition points at a calc output."""
    registry = OutputRegistry()
    channel = "Design__plant__pv_module__cost_model__total_cost"
    _seed_channel(registry, channel)
    redef = RedefinitionData(
        owning_part_qn="Lib__pv_module",
        attribute_name="capital_cost",
        redefinition_type=RedefinitionType.CHAIN,
        source_path="cost_model.total_cost",
    )
    resolved = _resolve("pv_module.capital_cost", registry, redefinitions=(redef,))
    assert resolved.outcome is Outcome.MODULE_OUTPUT
    assert resolved.identity == channel
    assert resolved.key_form == "chain_redefinition_follow"


def test_chain_redefinition_follow_refuses_on_multiple_matches():
    """The deleted behavior: a case-insensitive leaf match that took the first `break`.

    Two redefinitions of the same attribute on differently-named part defs used to
    resolve to whichever came first. The form now refuses and records the tie.
    """
    registry = OutputRegistry()
    redefs = tuple(
        RedefinitionData(
            owning_part_qn=f"Lib__{owner}",
            attribute_name="capital_cost",
            redefinition_type=RedefinitionType.CHAIN,
            source_path=path,
        )
        for owner, path in (("pv_module", "a.total"), ("pv_module", "b.total"))
    )
    resolved = _resolve("pv_module.capital_cost", registry, redefinitions=redefs)
    assert resolved.outcome is Outcome.ENTRY_POINT
    assert resolved.ambiguous_candidates == ("a.total", "b.total")


def test_chain_redefinition_follow_is_case_sensitive():
    """Also deleted: the `.lower()` on both sides of the leaf comparison."""
    registry = OutputRegistry()
    _seed_channel(registry, "Design__plant__pv__cost_model__total_cost")
    redef = RedefinitionData(
        owning_part_qn="Lib__pv_module",
        attribute_name="capital_cost",
        redefinition_type=RedefinitionType.CHAIN,
        source_path="cost_model.total_cost",
    )
    resolved = _resolve("PV_MODULE.capital_cost", registry, redefinitions=(redef,))
    assert resolved.outcome is Outcome.ENTRY_POINT, "a case-folded match must not resolve"


def test_direct_channel_construction_is_membership_checked():
    """Strategy E: build the CalcUsage-format channel and take it only if registered."""
    registry = OutputRegistry()
    channel = "Design__plant__cost_calc__total"
    _seed_channel(registry, channel)
    resolved = _resolve("cost_calc.total", registry)
    assert resolved.outcome is Outcome.MODULE_OUTPUT
    assert resolved.identity == channel
    assert resolved.key_form == "direct_channel"


def test_unconstructable_channel_does_not_resolve():
    """The membership check is what keeps construction from inventing a producer."""
    resolved = _resolve("nowhere.nothing", OutputRegistry())
    assert resolved.outcome is Outcome.ENTRY_POINT


def test_terminal_miss_keys_the_entry_point_on_the_flattened_reference():
    """The F4 trap, pinned: an aggregation term has no declared formal, so the entry
    point is keyed `{module_eqn}__{ref-with-dots-as-underscores}`.

    A leaf-only split would collide sibling part-usage inputs and clash with the
    module's own output channel — that collapse is exactly what this pin guards.
    """
    resolved = _resolve("pv_module.capital_cost", OutputRegistry())
    assert resolved.outcome is Outcome.ENTRY_POINT
    assert resolved.identity == f"{_MODULE}__pv_module_capital_cost"
