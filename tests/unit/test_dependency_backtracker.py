"""Unit tests for DependencyBacktracker CHAIN resolution (Item 2, multi-hop).

Two families, both on synthetic registries (no fixture, no snapshot):

- Ancestor-scope climb + ambiguity guard (`_resolve_chain_dispatch`): a 3+-segment
  CHAIN resolves by dropping trailing segments of the consumer scope; a Step-1 direct
  hit needs no climb; two prefixes reaching different channels refuse; a 2-segment
  chain never enters the climb (byte-identity gate).
- Loud Step-4 fallback (`_resolve_binding_via_registry`, D5/M-2): a genuinely
  unresolvable 3+-segment CHAIN warns at WARNING level, names the full chain, and
  surfaces as a full untruncated entry point — the silent-on-clean sibling proves a
  resolvable chain fires no WARN.
"""

from __future__ import annotations

import logging

from agentic_mbse.sysml.types import BindingType

from sysml_codegen.resolution.producer_resolution import (
    Outcome,
    ProducerRequest,
    TerminalPolicy,
    resolve_producer,
)

def _channel(bt, source_path, usage):
    """The observable outcome the deleted `_resolve_chain_dispatch` produced, read
    through the shared table (SR-R43). The climb is now the tier-1 terminal search,
    running after every tier-1 row rather than mid-sequence; it keeps its
    collect-then-require-unique ambiguity guard.
    """
    resolution = resolve_producer(
        ProducerRequest(
            consumer_eqn=usage.qualified_name,
            reference=source_path,
            param_name="probe",
            consumer_scope=bt._consumer_scope_dotted(usage),
            parent_scope=bt._get_parent_part_for_usage(usage),
            policy=TerminalPolicy.LENIENT,
            diagnostic_context="climb probe",
        ),
        bt._producer_context(),
    )
    return resolution.identity if resolution.outcome is Outcome.MODULE_OUTPUT else None


from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.core.identifier_types import CanonicalChannel, ScopedKey
from sysml_codegen.core.models import BindingResolutionType
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.extraction.usage_extractor import BindingInfo, CalcUsageData

_LOGGER = "sysml_codegen.analysis.dependency_backtracker"


def _usage(qualified_name: str) -> CalcUsageData:
    """Minimal synthetic consumer usage keyed only by its qualified name."""
    return CalcUsageData(
        instance_name=qualified_name.rsplit("__", 1)[-1],
        calc_def_name="Synthetic",
        calc_def_qualified_name="Lib::Synthetic",
        module_type="SyntheticModule",
        bindings=[],
        unbound_params=[],
        qualified_name=qualified_name,
    )


def _registry(scoped: dict[str, str]) -> OutputRegistry:
    reg = OutputRegistry()
    for key, channel in scoped.items():
        reg.register_scoped(ScopedKey(key), CanonicalChannel(channel))
    return reg


def _backtracker(usage: CalcUsageData, reg: OutputRegistry) -> DependencyBacktracker:
    return DependencyBacktracker([usage], [], output_registry=reg)


# ---------------------------------------------------------------------------
# Ancestor-scope climb + ambiguity guard (_resolve_chain_dispatch)
# ---------------------------------------------------------------------------

_CHANNEL_D = "Design__measurement_system__station__array__derived_calc__derived_value"
_CHANNEL_M = "Design__measurement_system__station__array__sensor__core__metric_value"


def test_climb_resolves_one_level_up_data_point_shape():
    """data_point shape: consumer scope is a sibling of the chain root, so Step 1
    misses; the climb drops the trailing scope segment and hits the ancestor key."""
    reg = _registry(
        {"measurement_system.station.array.derived_calc.derived_value": _CHANNEL_D}
    )
    usage = _usage("Design__measurement_system__analyzer__chain_analysis")
    bt = _backtracker(usage, reg)
    ch = _channel(bt, "station.array.derived_calc.derived_value", usage
    )
    assert ch == _CHANNEL_D


def test_base_metric_shape_hits_step1_no_climb():
    """base_metric shape: consumer scope already prefixes the target, so Step 1 is a
    direct hit and the climb is never needed."""
    reg = _registry(
        {"measurement_system.station.array.sensor.core.metric_value": _CHANNEL_M}
    )
    usage = _usage("Design__measurement_system__station__array__derived_calc")
    bt = _backtracker(usage, reg)
    ch = _channel(bt, "sensor.core.metric_value", usage)
    assert ch == _CHANNEL_M


def test_climb_refuses_on_two_distinct_channels():
    """M-1 / INV-2b: two *intermediate* ancestor prefixes reach different channels —
    refuse (return None → Step 4 loud fallback), never silently pick one. The keys are
    climb-only: the full-scope key (Step 1) and the bare source_path (Step 1b) are both
    absent, so the collision is decided inside the climb."""
    reg = _registry(
        {
            "a.b.x.y.z": "Design__a__b__x__y__z",  # climb prefix "a.b"
            "a.x.y.z": "Design__a__x__y__z",  # climb prefix "a"
        }
    )
    usage = _usage("Design__a__b__c__consumer")  # consumer scope = a.b.c
    bt = _backtracker(usage, reg)
    assert _channel(bt, "x.y.z", usage) is None


def test_two_segment_chain_never_enters_climb():
    """D4 gate: a 2-segment source_path (count('.') == 1) is below the climb gate, so
    an ancestor key that would only be reachable by climbing must NOT resolve."""
    # Only the climbed-ancestor key exists; the ungated Step-1/1b keys do not.
    reg = _registry({"measurement_system.calc.out": "Design__measurement_system__calc__out"})
    usage = _usage("Design__measurement_system__analyzer__consumer")
    bt = _backtracker(usage, reg)
    # Step 1 tries `measurement_system.analyzer.calc.out` (miss); Step 1b tries
    # `calc.out` (miss). The climb — which would find it — must not run for 2 segments.
    assert _channel(bt, "calc.out", usage) is None


# ---------------------------------------------------------------------------
# Loud Step-4 fallback (D5 / M-2)
# ---------------------------------------------------------------------------


def test_multihop_fallback_warns_loud_and_untruncated(caplog):
    """A 3+-segment CHAIN whose tail names a non-existent output falls through every
    step and hits Step 4: WARNING-level, full chain named, full untruncated EP QN."""
    reg = _registry({})  # nothing resolves
    usage = _usage("Design__scope__consumer")
    bt = _backtracker(usage, reg)
    binding = BindingInfo(
        param_name="p",
        source_path="a.b.c.missing",
        binding_type=BindingType.CHAIN,
    )
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        res = bt._resolve_binding_via_registry(binding, usage)
    assert res.resolution_type == BindingResolutionType.ENTRY_POINT
    assert res.qualified_name == "Design__scope__consumer__p"  # full, untruncated (M-2)
    assert any(
        r.levelno == logging.WARNING and r.name == _LOGGER for r in caplog.records
    ), caplog.records
    assert "a.b.c.missing" in caplog.text  # names the full chain


def test_resolvable_multihop_chain_is_silent(caplog):
    """Silent-on-clean sibling: a resolvable 3+-segment CHAIN wires to its channel with
    NO WARNING (guards against a future over-firing multi-hop WARN)."""
    reg = _registry({"plant.sub.calc.out": "Design__plant__sub__calc__out"})
    usage = _usage("Design__plant__consumer")
    bt = _backtracker(usage, reg)
    binding = BindingInfo(
        param_name="p",
        source_path="sub.calc.out",
        binding_type=BindingType.CHAIN,
    )
    with caplog.at_level(logging.WARNING, logger=_LOGGER):
        res = bt._resolve_binding_via_registry(binding, usage)
    assert res.resolution_type == BindingResolutionType.MODULE_OUTPUT
    assert res.qualified_name == "Design__plant__sub__calc__out"
    assert not any(
        r.levelno == logging.WARNING and r.name == _LOGGER for r in caplog.records
    ), caplog.records
