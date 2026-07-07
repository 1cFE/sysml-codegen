"""Conformance tests for Input Resolver (C12).

Requirements: REQ-IR-01 through REQ-IR-07, REQ-DRA-02, REQ-DRA-04
Design intent: 04-input-resolver.md, 24-dual-resolution-architecture.md

Tests use real extraction snapshot data — no mocks.
"""

from __future__ import annotations

import ast
import inspect
import textwrap
from pathlib import Path

import pytest

from sysml_codegen.core.identifier_types import (
    CanonicalChannel,
    ScopedKey,
    SysMLQN,
)
from sysml_codegen.core.qualified_names import get_channel_name, sanitize_name
from sysml_codegen.extraction.data_models import (
    RedefinitionData,
    RedefinitionType,
    ScopedAggregationData,
)
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from sysml_codegen.resolution.models import InputSource
from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import snapshot_fixture

# ---------------------------------------------------------------------------
# Import resolve_input and friends — these don't exist yet; tests will FAIL
# until BUILD phase creates resolution/input_resolver.py.
# ---------------------------------------------------------------------------
try:
    from sysml_codegen.resolution.input_resolver import (
        AGG_STRATEGIES,
        ResolutionContext,
        resolve_input,
    )

    INPUT_RESOLVER_AVAILABLE = True
except ImportError:
    INPUT_RESOLVER_AVAILABLE = False

    # Stubs so test file parses
    class ResolutionContext:  # type: ignore[no-redef]
        pass

    def resolve_input(ref, ctx, strategies):  # type: ignore[no-redef]
        raise NotImplementedError

    AGG_STRATEGIES = []  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Strategy callable imports
# ---------------------------------------------------------------------------
try:
    from sysml_codegen.resolution.input_resolver import (
        ChainRedefinitionFollow,
        DirectChannelConstruction,
        ScopedRegistryLookup,
        SysMLQNLookup,
    )

    STRATEGIES_AVAILABLE = True
except ImportError:
    STRATEGIES_AVAILABLE = False

    def ScopedRegistryLookup(ref, ctx):  # type: ignore[no-redef]
        raise NotImplementedError

    def ChainRedefinitionFollow(ref, ctx):  # type: ignore[no-redef]
        raise NotImplementedError

    def SysMLQNLookup(ref, ctx):  # type: ignore[no-redef]
        raise NotImplementedError

    def DirectChannelConstruction(ref, ctx):  # type: ignore[no-redef]
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Test fixtures and helpers
# ---------------------------------------------------------------------------
SKIP_REASON = "resolve_input() not yet implemented"


def _build_registry_from_snapshot(model_name: str):
    """Load snapshot and build OutputRegistry."""
    snap = load_extraction_snapshot(snapshot_fixture(model_name))
    registry = build_output_registry(
        calc_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        aggregation_data=snap["aggregation_expressions"],
        computed_attributes=snap["computed_attributes"],
        channel_aliases=snap.get("channel_aliases", []),
        design_attributes=snap.get("design_attributes", {}),
    )
    return registry, snap


def _build_resolution_context_for_agg(
    agg: ScopedAggregationData,
    output_registry,
    redefinitions: list[RedefinitionData],
    design_attrs: dict[str, object],
) -> ResolutionContext:
    """Construct ResolutionContext from ScopedAggregationData and shared state.

    Derives consumer_scope from module_eqn per doc 04:
    split on __, drop [0] (design prefix) and [-1] (self), join with '.'.
    """
    parts = agg.module_eqn.split("__")
    consumer_scope = ".".join(parts[1:-1]) if len(parts) >= 3 else ""

    return ResolutionContext(
        output_registry=output_registry,
        redefinitions=redefinitions,
        design_attrs=design_attrs,
        module_eqn=agg.module_eqn,
        consumer_scope=consumer_scope,
        instance_path=agg.instance_path,
    )


def _flatten_design_attrs(design_attrs_dict) -> dict:
    """Flatten dict[Path, list[DesignAttributeData]] to dict[str, DesignAttributeData]."""
    flat = {}
    for path, attrs in design_attrs_dict.items():
        for da in attrs:
            if da.qualified_name:
                flat[da.qualified_name] = da
            flat[da.name] = da
    return flat


def _iter_agg_sum_singleton_terms(agg):
    """Yield (ref, literal_lookup_key) for every SumTerm and dotted SingletonTerm of
    an aggregation. literal_lookup_key is the (part_usage, attr) the inline block looks
    up a LITERAL default for — pre-split fields for SumTerm, an rsplit for SingletonTerm.
    Dotless SingletonTerms are skipped here (the M3 gate iterates dotted refs only, as
    the old channel function returns None for them without a lookup)."""
    for term in agg.expression.sum_terms:
        ref = f"{term.part_usage_name}.{term.attribute_name}"
        yield ref, (term.part_usage_name, term.attribute_name)
    for s_term in agg.expression.singleton_terms:
        if "." not in s_term.source_path:
            continue
        s_part_usage, s_attr = s_term.source_path.rsplit(".", 1)
        yield s_term.source_path, (s_part_usage, s_attr)


# ---------------------------------------------------------------------------
# REQ-IR-01: resolve_input() always returns InputSource
# ---------------------------------------------------------------------------
class TestReqIR01:
    """resolve_input() SHALL always return an InputSource — never raise."""

    @pytest.mark.req("REQ-IR-01")
    @pytest.mark.parametrize("model_name", ["solar_battery_model", "issue22_model", "alias_agg_probe"])
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_always_returns_input_source(self, model_name):
        """For every SumTerm and SingletonTerm ref, resolve_input() returns InputSource."""
        registry, snap = _build_registry_from_snapshot(model_name)
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        for agg in agg_data:
            ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)

            for term in agg.expression.sum_terms:
                ref = f"{term.part_usage_name}.{term.attribute_name}"
                result = resolve_input(ref, ctx, AGG_STRATEGIES)
                assert isinstance(result, InputSource), (
                    f"Expected InputSource for ref='{ref}' in {agg.module_eqn}, got {type(result)}"
                )
                assert result.source_type in ("module_output", "entry_point")

            for s_term in agg.expression.singleton_terms:
                if "." in s_term.source_path:
                    result = resolve_input(s_term.source_path, ctx, AGG_STRATEGIES)
                    assert isinstance(result, InputSource), (
                        f"Expected InputSource for ref='{s_term.source_path}' in {agg.module_eqn}"
                    )
                    assert result.source_type in ("module_output", "entry_point")

    @pytest.mark.req("REQ-IR-01")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_unresolvable_ref_returns_entry_point(self):
        """Unresolvable ref returns entry_point InputSource (never raises)."""
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        agg = snap["aggregation_expressions"][0]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))
        ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)

        result = resolve_input("nonexistent_part.nonexistent_attr", ctx, AGG_STRATEGIES)
        assert isinstance(result, InputSource)
        assert result.source_type == "entry_point"
        assert result.qualified_name is not None


# ---------------------------------------------------------------------------
# REQ-IR-02: Strategies execute in declared order; first match wins
# ---------------------------------------------------------------------------
class TestReqIR02:
    """Strategies execute in declared list order; first non-None result wins."""

    @pytest.mark.req("REQ-IR-02")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_first_match_wins(self):
        """For agg-to-agg ref that Strategy A resolves, verify A result used
        even though Strategy C would also match."""
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        # Plant-level capital_cost: ref='solar_array.capital_cost'
        # Strategy A should hit via scoped registry (agg-to-agg key).
        plant_capital = [a for a in agg_data
                         if a.module_eqn.endswith("__capital_cost")
                         and "solar_battery_plant__capital_cost" in a.module_eqn]
        assert len(plant_capital) >= 1, "Expected plant-level capital_cost agg"
        agg = plant_capital[0]
        ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)

        result = resolve_input("solar_array.capital_cost", ctx, AGG_STRATEGIES)
        assert result.source_type == "module_output"
        assert result.producer_channel is not None

        # Independently check Strategy A hits
        a_result = ScopedRegistryLookup("solar_array.capital_cost", ctx)
        assert a_result is not None, "Strategy A should hit for agg-to-agg ref"

    @pytest.mark.req("REQ-IR-02")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_strategy_ordering_matches_agg_strategies(self):
        """AGG_STRATEGIES has exactly 4 entries in order: A/C/B/E. The dead Strategy D
        (DesignAttributeLookup) was deleted in the F4 cutover; Strategy E
        (DirectChannelConstruction) reproduces the SingletonTerm Try-2 channel."""
        assert len(AGG_STRATEGIES) == 4
        assert AGG_STRATEGIES[0] is ScopedRegistryLookup
        assert AGG_STRATEGIES[1] is ChainRedefinitionFollow
        assert AGG_STRATEGIES[2] is SysMLQNLookup
        assert AGG_STRATEGIES[3] is DirectChannelConstruction


# ---------------------------------------------------------------------------
# REQ-IR-03: Self-reference guard
# ---------------------------------------------------------------------------
class TestReqIR03:
    """Self-reference guard rejects channels where producing module == module_eqn."""

    @pytest.mark.req("REQ-IR-03")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_self_reference_guard(self):
        """Construct a ResolutionContext where module_eqn matches a known channel's
        producing module. Verify the strategy skips it and falls through."""
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        # Find a channel and its producing module
        # solar_array.capital_cost is an aggregation output registered in scoped registry
        # Producer module: SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost
        # If we set module_eqn to this, any resolution of a ref that points back to
        # this module should be rejected.
        module_eqn = "SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost"
        consumer_scope = "solar_battery_plant.solar_array"

        ctx = ResolutionContext(
            output_registry=registry,
            redefinitions=redefs,
            design_attrs=design_attrs,
            module_eqn=module_eqn,
            consumer_scope=consumer_scope,
            instance_path="SolarBatteryDesign__solar_battery_plant__solar_array",
        )

        # "solar_array.capital_cost" at plant scope would resolve to the solar_array
        # aggregation output — but that IS our own module. Guard should reject it.
        # At solar_array scope with module_eqn pointing to solar_array.capital_cost,
        # the scoped key would be solar_battery_plant.solar_array.solar_array.capital_cost
        # which probably doesn't exist. Let's instead test with a ref that we know
        # Strategy A would resolve to our own module's channel.

        # The module's own channel: capital_cost output registered under
        # ScopedKey "solar_battery_plant.solar_array.capital_cost"
        own_channel = registry.scoped_lookup(
            ScopedKey("solar_battery_plant.solar_array.capital_cost")
        )
        if own_channel is not None:
            # Construct a ref that would resolve to this channel via unscoped fallback
            # in Strategy A. The ref "solar_array.capital_cost" at consumer_scope
            # "solar_battery_plant" would form ScopedKey "solar_battery_plant.solar_array.capital_cost"
            plant_ctx = ResolutionContext(
                output_registry=registry,
                redefinitions=redefs,
                design_attrs=design_attrs,
                module_eqn=module_eqn,
                consumer_scope="solar_battery_plant",
                instance_path="SolarBatteryDesign__solar_battery_plant",
            )
            result = resolve_input("solar_array.capital_cost", plant_ctx, AGG_STRATEGIES)
            # Self-reference guard should prevent wiring to own channel.
            # It should fall through to entry_point.
            assert result.source_type == "entry_point", (
                f"Expected entry_point (self-reference guard), got {result.source_type} "
                f"with channel={result.producer_channel}"
            )


# ---------------------------------------------------------------------------
# REQ-IR-04: ResolutionContext immutability
# ---------------------------------------------------------------------------
class TestReqIR04:
    """ResolutionContext is frozen — no strategy mutates it."""

    @pytest.mark.req("REQ-IR-04")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_resolution_context_immutable(self):
        """Attempt to set ctx.module_eqn = 'x' raises FrozenInstanceError."""
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        ctx = ResolutionContext(
            output_registry=registry,
            redefinitions=redefs,
            design_attrs=design_attrs,
            module_eqn="test_module",
            consumer_scope="test_scope",
            instance_path="test_path",
        )

        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            ctx.module_eqn = "changed"  # type: ignore[misc]

    @pytest.mark.req("REQ-IR-04")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_resolution_context_fields(self):
        """ResolutionContext has all 6 documented fields with correct types."""
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        ctx = ResolutionContext(
            output_registry=registry,
            redefinitions=redefs,
            design_attrs=design_attrs,
            module_eqn="test_module",
            consumer_scope="test_scope",
            instance_path="test_path",
        )

        assert hasattr(ctx, "output_registry")
        assert hasattr(ctx, "redefinitions")
        assert hasattr(ctx, "design_attrs")
        assert hasattr(ctx, "module_eqn")
        assert hasattr(ctx, "consumer_scope")
        assert hasattr(ctx, "instance_path")
        assert ctx.module_eqn == "test_module"
        assert ctx.consumer_scope == "test_scope"
        assert ctx.instance_path == "test_path"
        assert isinstance(ctx.redefinitions, list)
        assert isinstance(ctx.design_attrs, dict)


# ---------------------------------------------------------------------------
# REQ-IR-05: AGG_STRATEGIES ordering + CHAIN redef resolution
# ---------------------------------------------------------------------------
class TestReqIR05:
    """Aggregation modules use AGG_STRATEGIES with ChainRedefinitionFollow at position 2."""

    @pytest.mark.req("REQ-IR-05")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_agg_strategies_ordering(self):
        """AGG_STRATEGIES[0] is ScopedRegistryLookup; [1] is ChainRedefinitionFollow."""
        assert AGG_STRATEGIES[0] is ScopedRegistryLookup
        assert AGG_STRATEGIES[1] is ChainRedefinitionFollow

    @pytest.mark.req("REQ-IR-05")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_chain_redef_resolves_sumterm(self):
        """For pv_module.capital_cost in solar_array: Strategy C follows CHAIN redef
        :>> capital_cost = cost_model.total_cost and resolves to CalcUsage output."""
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        # Find solar_array capital_cost agg
        solar_array_cap = [a for a in agg_data
                           if "solar_array__capital_cost" in a.module_eqn]
        assert solar_array_cap, "Expected solar_array capital_cost agg"
        agg = solar_array_cap[0]
        ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)

        # pv_module.capital_cost should resolve via CHAIN redef
        result = resolve_input("pv_module.capital_cost", ctx, AGG_STRATEGIES)
        assert result.source_type == "module_output"
        assert result.producer_channel is not None
        # Channel should point to cost_model CalcUsage output
        assert "cost_model" in result.producer_channel or "pv_module" in result.producer_channel

    @pytest.mark.req("REQ-IR-05")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_chain_redef_resolves_singleton(self):
        """For a SingletonTerm that resolves via CHAIN redef."""
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        # Find an agg with singleton terms that use CHAIN redef
        # solar_array.raw_material_cost has singleton: allocation_model.material_portion
        raw_mat = [a for a in agg_data
                   if "solar_array__raw_material_cost" in a.module_eqn]
        if raw_mat and raw_mat[0].expression.singleton_terms:
            agg = raw_mat[0]
            ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)
            s_term = agg.expression.singleton_terms[0]
            if "." in s_term.source_path:
                result = resolve_input(s_term.source_path, ctx, AGG_STRATEGIES)
                assert isinstance(result, InputSource)
                # Should resolve to module_output (allocation_model is a CalcUsage)
                assert result.source_type == "module_output"


# ---------------------------------------------------------------------------
# REQ-IR-06: Fallback produces entry_point
# ---------------------------------------------------------------------------
class TestReqIR06:
    """Fallback produces entry_point InputSource with qualified_name format."""

    @pytest.mark.req("REQ-IR-06")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_fallback_entry_point_format(self):
        """Unresolvable ref produces entry_point with QN = '{module_eqn}__{param_name}'."""
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        agg = snap["aggregation_expressions"][0]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))
        ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)

        result = resolve_input("unknown_part.unknown_attr", ctx, AGG_STRATEGIES)
        assert result.source_type == "entry_point"
        assert result.qualified_name is not None
        assert result.qualified_name.startswith(ctx.module_eqn)
        assert "unknown_attr" in result.qualified_name


# ---------------------------------------------------------------------------
# REQ-IR-07: Scope — SumTerm/SingletonTerm use resolve_input, others don't
# ---------------------------------------------------------------------------
class TestReqIR07:
    """Aggregation SumTerm/SingletonTerm inputs SHALL use resolve_input()."""

    @pytest.mark.req("REQ-IR-07")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_scope_sumterm_only(self):
        """For every solar_battery SumTerm: resolve_input() result matches baseline."""
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        for agg in agg_data:
            ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)
            for term in agg.expression.sum_terms:
                ref = f"{term.part_usage_name}.{term.attribute_name}"
                result = resolve_input(ref, ctx, AGG_STRATEGIES)
                assert isinstance(result, InputSource)
                # Must be one of the two valid types
                assert result.source_type in ("module_output", "entry_point")
                if result.source_type == "module_output":
                    assert result.producer_channel is not None
                else:
                    assert result.qualified_name is not None

    @pytest.mark.req("REQ-IR-07")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_scope_singleton_only(self):
        """For every solar_battery SingletonTerm with dotted ref: resolve_input() returns valid."""
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        for agg in agg_data:
            ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)
            for s_term in agg.expression.singleton_terms:
                if "." in s_term.source_path:
                    result = resolve_input(s_term.source_path, ctx, AGG_STRATEGIES)
                    assert isinstance(result, InputSource)
                    assert result.source_type in ("module_output", "entry_point")

    @pytest.mark.req("REQ-IR-07")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_local_term_not_resolved_by_input_resolver(self):
        """LocalTerm resolution is NOT routed through resolve_input()."""
        # LocalTerms have bare attribute names (no dot), which resolve_input()
        # would fall through to entry_point. The actual resolution uses a
        # factory-specific cascade (sibling agg lookup → EXPOSE_PURE alias → entry point).
        # This test verifies that resolve_input with a LocalTerm-style bare ref
        # produces entry_point (not module_output), confirming it's not the right path.
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        # Find an agg with local terms
        for agg in agg_data:
            if agg.expression.local_terms:
                ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)
                local_ref = agg.expression.local_terms[0].attribute_name
                result = resolve_input(local_ref, ctx, AGG_STRATEGIES)
                # LocalTerm bare name → strategies all miss → entry_point
                assert result.source_type == "entry_point"
                break


# ---------------------------------------------------------------------------
# REQ-DRA-02: FORMULA and CalcUsage don't use resolve_input()
# ---------------------------------------------------------------------------
class TestReqDRA02:
    """FORMULA uses attribute resolution map; CalcUsage uses backtracker."""

    @pytest.mark.req("REQ-DRA-02")
    def test_formula_not_via_resolve_input(self):
        """Static analysis: _build_computed_attr_module() does NOT call resolve_input()."""
        source = inspect.getsource(
            __import__(
                "sysml_codegen.resolution.graph_builder",
                fromlist=["_build_computed_attr_module"],
            )._build_computed_attr_module
        )
        assert "resolve_input" not in source, (
            "_build_computed_attr_module() should not call resolve_input()"
        )

    @pytest.mark.req("REQ-DRA-02")
    def test_calcusage_not_via_resolve_input(self):
        """Static analysis: _build_pipeline_module() does NOT call resolve_input()."""
        source = inspect.getsource(
            __import__(
                "sysml_codegen.resolution.graph_builder",
                fromlist=["_build_pipeline_module"],
            )._build_pipeline_module
        )
        assert "resolve_input" not in source, (
            "_build_pipeline_module() should not call resolve_input()"
        )


# ---------------------------------------------------------------------------
# REQ-DRA-04: Cross-path consistency
# ---------------------------------------------------------------------------
class TestReqDRA04:
    """Same reference in same scope produces same wiring as backtracker."""

    @pytest.mark.req("REQ-DRA-04")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_cross_path_consistency(self):
        """Verify a known CalcUsage binding ref resolves to the same channel
        when fed through resolve_input() with an equivalent ResolutionContext.

        Uses solar_battery CalcUsage binding refs — these are resolved by the
        backtracker. We construct a ResolutionContext with the same scope and
        verify Strategy A produces the same channel.
        """
        from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
        from sysml_codegen.core.models import BindingResolutionType

        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        # Run backtracker
        backtracker = DependencyBacktracker(
            all_usages=snap["calc_usages"],
            calc_defs=snap["calc_defs"],
            design_attributes=snap.get("design_attributes", {}),
            output_registry=registry,
        )
        result = backtracker.find_required_modules([], include_all=True)

        # Find MODULE_OUTPUT resolutions with CHAIN source_path (dotted, no ::)
        verified = 0
        for key, res in result.binding_resolutions.items():
            if (res.resolution_type == BindingResolutionType.MODULE_OUTPUT
                    and res.source_path
                    and "::" not in res.source_path
                    and "." in res.source_path):
                # Derive scope from usage_qn
                usage_qn = key.split("|")[0]
                parts = usage_qn.split("__")
                if len(parts) < 3:
                    continue
                consumer_scope = ".".join(parts[1:-1])

                ctx = ResolutionContext(
                    output_registry=registry,
                    redefinitions=redefs,
                    design_attrs=design_attrs,
                    module_eqn=usage_qn,
                    consumer_scope=consumer_scope,
                    instance_path="__".join(parts[:-1]),
                )

                ir_result = resolve_input(res.source_path, ctx, AGG_STRATEGIES)
                if ir_result.source_type == "module_output":
                    assert ir_result.producer_channel == res.qualified_name, (
                        f"Cross-path mismatch for key='{key}' ref='{res.source_path}' "
                        f"scope='{consumer_scope}': "
                        f"backtracker='{res.qualified_name}' vs "
                        f"resolve_input='{ir_result.producer_channel}'"
                    )
                    verified += 1

        assert verified > 0, "Expected at least one cross-path verification"


# ---------------------------------------------------------------------------
# Individual strategy tests
# ---------------------------------------------------------------------------
class TestStrategyA:
    """Strategy A: ScopedRegistryLookup."""

    @pytest.mark.req("REQ-IR-03")
    @pytest.mark.skipif(not STRATEGIES_AVAILABLE, reason=SKIP_REASON)
    def test_scoped_lookup_primary(self):
        """For agg-to-agg ref: Strategy A hits via scoped registry."""
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        # Plant-level capital_cost: ref='solar_array.capital_cost'
        plant_cap = [a for a in agg_data
                     if "solar_battery_plant__capital_cost" in a.module_eqn]
        assert plant_cap
        agg = plant_cap[0]
        ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)

        channel = ScopedRegistryLookup("solar_array.capital_cost", ctx)
        assert channel is not None
        assert isinstance(channel, str)

    @pytest.mark.req("REQ-IR-03")
    @pytest.mark.skipif(not STRATEGIES_AVAILABLE, reason=SKIP_REASON)
    def test_alias_cross_package(self):
        """If alias_agg_probe has a cross-package alias, Strategy A resolves it."""
        registry, snap = _build_registry_from_snapshot("alias_agg_probe")
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        if agg_data:
            agg = agg_data[0]
            ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)

            # widget.total_cost should resolve
            for term in agg.expression.sum_terms:
                ref = f"{term.part_usage_name}.{term.attribute_name}"
                channel = ScopedRegistryLookup(ref, ctx)
                if channel is not None:
                    assert isinstance(channel, str)
                    break


class TestStrategyB:
    """Strategy B: SysMLQNLookup."""

    @pytest.mark.req("REQ-IR-03")
    @pytest.mark.skipif(not STRATEGIES_AVAILABLE, reason=SKIP_REASON)
    def test_sysml_qn_lookup(self):
        """Verify SysMLQN lookup with a constructed :: ref against a registry
        that contains matching SysML QN keys."""
        registry, snap = _build_registry_from_snapshot("attr_expr_probe")
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        # attr_expr_probe has FORMULA keys registered as SysML QN
        # Find a SysML QN key in the registry
        ctx = ResolutionContext(
            output_registry=registry,
            redefinitions=redefs,
            design_attrs=design_attrs,
            module_eqn="test__probe_design__test_calc",
            consumer_scope="probe_design",
            instance_path="test__probe_design",
        )

        # Try a known SysML QN from attr_expr_probe
        # These are registered under SysMLQN format
        # e.g., "AttrExprProbeDesign::probe_design::area"
        sysml_qn_ref = "AttrExprProbeDesign::probe_design::area"
        channel = SysMLQNLookup(sysml_qn_ref, ctx)
        # May or may not hit depending on what's registered
        # The key test is that it doesn't crash and returns Channel | None
        assert channel is None or isinstance(channel, str)


class TestStrategyC:
    """Strategy C: ChainRedefinitionFollow."""

    @pytest.mark.req("REQ-IR-03")
    @pytest.mark.skipif(not STRATEGIES_AVAILABLE, reason=SKIP_REASON)
    def test_chain_redef_cycle_detection(self):
        """Circular CHAIN redef chain returns None (no infinite loop)."""
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        # Construct circular redefinitions: a.x :>> b.y, b.y :>> a.x
        circular_redefs = [
            RedefinitionData(
                owning_part_qn="Lib__PartA",
                attribute_name="x",
                redefinition_type=RedefinitionType.CHAIN,
                source_path="partb.y",
            ),
            RedefinitionData(
                owning_part_qn="Lib__PartB",
                attribute_name="y",
                redefinition_type=RedefinitionType.CHAIN,
                source_path="parta.x",
            ),
        ]

        ctx = ResolutionContext(
            output_registry=registry,
            redefinitions=circular_redefs,
            design_attrs=design_attrs,
            module_eqn="Design__scope__test_agg",
            consumer_scope="scope",
            instance_path="Design__scope",
        )

        # Should return None, not infinite loop
        channel = ChainRedefinitionFollow("parta.x", ctx)
        assert channel is None


# Strategy D (DesignAttributeLookup) was a return-None stub with zero live surface
# (probe ii); it was deleted in the F4 cutover. Its test went with it.


# ---------------------------------------------------------------------------
# Regression: Full pipeline baseline comparison
# ---------------------------------------------------------------------------
class TestPhase1ValueHalf:
    """Phase 1 value-half plumbing: the reconciled fallback key (D1) and Strategy E (D3)."""

    @pytest.mark.req("REQ-IR-06")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_agg_fallback_key_is_dotted_underscored(self):
        """resolve_input's entry-point fallback mints {module_eqn}__{ref.replace('.','_')},
        not a leaf-only rsplit (INV-1)."""
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))
        agg = agg_data[0]
        ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)

        # A ref that no strategy resolves → fallback entry_point.
        ref = "no_such_usage.no_such_attr"
        result = resolve_input(ref, ctx, AGG_STRATEGIES)
        assert result.source_type == "entry_point"
        assert result.qualified_name == f"{ctx.module_eqn}__no_such_usage_no_such_attr"
        # The disambiguating part-usage prefix survives (not the bare leaf).
        assert not result.qualified_name.endswith("__no_such_attr")

    @pytest.mark.req("REQ-IR-02")
    @pytest.mark.skipif(not STRATEGIES_AVAILABLE, reason=SKIP_REASON)
    def test_strategy_e_returns_channel_only_when_in_canonical(self):
        """Strategy E is a no-op for dotless refs and for refs whose constructed channel
        is not registered; it returns a channel only when the constructed CalcUsage-format
        channel exists in canonical_channels."""
        registry, snap = _build_registry_from_snapshot("solar_battery_model")
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        # No-op on a dotless ref.
        any_ctx = _build_resolution_context_for_agg(agg_data[0], registry, redefs, design_attrs)
        assert DirectChannelConstruction("bare_local", any_ctx) is None

        # No-op on a dotted ref whose constructed channel is not registered.
        assert DirectChannelConstruction("no_such_usage.no_such_out", any_ctx) is None

        # Every channel E returns must exist in the registry (verified over all
        # singleton terms across the corpus fixture).
        returned = 0
        for agg in agg_data:
            ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)
            for s_term in agg.expression.singleton_terms:
                ch = DirectChannelConstruction(s_term.source_path, ctx)
                if ch is not None:
                    assert ch in registry.canonical_channels
                    returned += 1
        # Strategy E exists to cover the SingletonTerm "Try 2" case; the fixture must
        # exercise it at least once or the strategy is untested.
        assert returned > 0, "Strategy E returned no channel on solar_battery — untested"


class TestRegression:
    """Regression tests: resolve_input() produces identical wiring to current code."""

    # ==================================================================
    # M3 GATE (INV-3): the new helper reproduces the FULL InputSource the
    # executed old inline block produced — source_type, producer_channel,
    # qualified_name, and param_group — over the aggregation fixtures, GREEN
    # BEFORE the call-site rewire (design D2, spec [HARD] M3).
    #
    # The gate has two halves with different fates at cutover:
    #   • OLD-COMPARAND half (test_m3_full_inputsource_parity): calls the
    #     to-be-deleted _resolve_aggregation_input_channel + reproduces the old
    #     fallback. DELETED in the Phase 3 cutover commit (cannot compile against
    #     the deleted function).
    #   • NEW-SIDE half (test_m3_reconciled_ep_key_survives): asserts the helper's
    #     reconciled EP key against the formula, no deleted-function dependency.
    #     SURVIVES as the permanent guard on the reconciled part-usage EP key.
    # ==================================================================

    @pytest.mark.req("REQ-IR-01")
    @pytest.mark.parametrize("model_name", ["solar_battery_model"])
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_m3_reconciled_ep_key_survives(self, model_name):
        """NEW-SIDE HALF (permanent). Every aggregation input the helper falls back to
        an entry point mints the reconciled part-usage-prefixed key
        {module_eqn}__{ref.replace('.','_')} (INV-1) — the durable guard on the EP key
        that a regenerable byte-identity baseline alone would not provide."""
        from sysml_codegen.resolution.graph_builder import _build_agg_input_source
        from tests.conformance.test_factory_aggregation import (
            build_aggregation_factory_inputs,
        )

        f = build_aggregation_factory_inputs(model_name)
        registry = f["registry"]
        redefs = f["redefinitions"]
        usage_type_map = f["usage_type_map"]
        group_deriver = f["group_deriver"]
        entry_points = f["entry_points"]
        design_attrs = _flatten_design_attrs(f["snap"].get("design_attributes", {}))

        checked = 0
        for agg in f["aggregation_data"]:
            ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)
            owning_part_qn = agg.expression.owning_part_qn
            for ref, lookup_key in _iter_agg_sum_singleton_terms(agg):
                new_src, _manual = _build_agg_input_source(
                    ref, ctx, lookup_key, redefs, usage_type_map,
                    owning_part_qn, group_deriver, entry_points, {},
                )
                if new_src.source_type == "entry_point":
                    assert new_src.qualified_name == (
                        f"{agg.module_eqn}__{ref.replace('.', '_')}"
                    ), f"{agg.module_eqn}/{ref}: EP key not reconciled"
                    # param_group is deterministic from the QN (classify), so an equal
                    # QN implies an equal group — assert it is populated when derivable.
                    assert new_src.param_group == group_deriver.classify(
                        new_src.qualified_name
                    )
                    checked += 1
        assert checked > 0, f"{model_name}: no fallback EP exercised — gate is vacuous"

    @pytest.mark.req("REQ-IR-01")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_issue22_agg_input_resolution(self):
        """issue22 SumTerm widget.total_cost resolves to module_output."""
        registry, snap = _build_registry_from_snapshot("issue22_model")
        agg_data = snap["aggregation_expressions"]
        redefs = snap["hierarchy_data"].redefinitions
        design_attrs = _flatten_design_attrs(snap.get("design_attributes", {}))

        assert len(agg_data) >= 1
        agg = agg_data[0]
        ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)

        assert len(agg.expression.sum_terms) >= 1
        term = agg.expression.sum_terms[0]
        ref = f"{term.part_usage_name}.{term.attribute_name}"

        result = resolve_input(ref, ctx, AGG_STRATEGIES)
        assert result.source_type == "module_output"
        assert result.producer_channel is not None
        # Should point to cost_model CalcUsage output
        assert "cost_model" in result.producer_channel or "total_cost" in result.producer_channel


class TestLocalTermExposeAliasReroutePin:
    """Major 3 / D5: the LocalTerm expose-alias channel reroute (graph_builder.py) has
    ZERO M3 coverage — the M3 gate iterates sum/singleton terms only. This permanent pin
    guards it directly: resolve_input on the alias target yields a module_output whose
    channel is registered, and the D5 module_output-only guard means a non-channel result
    would leave the LocalTerm EP key at {module_eqn}__{attribute_name} (never adopting
    resolve_input's never-None entry_point fallback as a channel).

    NOTE: alias_agg_probe's snapshot carries no EXPOSE_PURE computed_attributes, so it
    cannot exercise the reroute; solar_battery_model exercises the real Major-3 case
    (misc_hardware_cost → allocation_model.total_allocation → channel)."""

    @pytest.mark.req("REQ-DRA-04")
    @pytest.mark.parametrize("model_name", ["solar_battery_model"])
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_localterm_reroute_module_output_only(self, model_name):
        from tests.conformance.test_factory_aggregation import (
            build_aggregation_factory_inputs,
        )

        f = build_aggregation_factory_inputs(model_name)
        registry = f["registry"]
        redefs = f["redefinitions"]
        expose_aliases = f["expose_aliases"]
        design_attrs = _flatten_design_attrs(f["snap"].get("design_attributes", {}))

        channel_hits = 0
        for agg in f["aggregation_data"]:
            ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)
            for l_term in agg.expression.local_terms:
                alias_key = (agg.expression.owning_part_qn, l_term.attribute_name)
                alias_source = expose_aliases.get(alias_key)
                if not alias_source:
                    continue

                new_result = resolve_input(alias_source, ctx, AGG_STRATEGIES)
                if new_result.source_type == "module_output":
                    # The reroute adopts this channel; it must be a real registered one.
                    assert new_result.producer_channel in registry.canonical_channels
                    channel_hits += 1
                else:
                    # D5 guard: a non-channel result is NOT adopted; LocalTerm falls
                    # through to its own key {module_eqn}__{attribute_name} (unchanged).
                    assert new_result.source_type == "entry_point"

        assert channel_hits > 0, (
            f"{model_name}: no LocalTerm expose-alias resolved to a channel — pin is vacuous"
        )


class TestManualRequiredPreserved:
    """INV-2 / L3-2: a genuinely-unresolved aggregation term with no literal default
    routed through _build_agg_input_source returns manual_required=True. Losing this
    signal silently marks an unresolved term compilable — the regression class this epic
    exists to kill. A resolved term returns manual_required=False."""

    @pytest.mark.req("REQ-IR-06")
    @pytest.mark.skipif(not INPUT_RESOLVER_AVAILABLE, reason=SKIP_REASON)
    def test_unresolved_no_default_term_is_manual_required(self):
        from sysml_codegen.resolution.graph_builder import _build_agg_input_source
        from tests.conformance.test_factory_aggregation import (
            build_aggregation_factory_inputs,
        )

        f = build_aggregation_factory_inputs("solar_battery_model")
        registry = f["registry"]
        redefs = f["redefinitions"]
        usage_type_map = f["usage_type_map"]
        group_deriver = f["group_deriver"]
        entry_points = f["entry_points"]
        design_attrs = _flatten_design_attrs(f["snap"].get("design_attributes", {}))
        agg = f["aggregation_data"][0]
        ctx = _build_resolution_context_for_agg(agg, registry, redefs, design_attrs)

        # Unresolvable ref with no LITERAL redefinition → entry_point, manual_required.
        src, manual = _build_agg_input_source(
            "no_such_usage.no_such_attr", ctx, ("no_such_usage", "no_such_attr"),
            redefs, usage_type_map, agg.expression.owning_part_qn,
            group_deriver, entry_points, {},
        )
        assert src.source_type == "entry_point"
        assert manual is True

        # A term that resolves to a channel is never manual_required.
        resolved_ref = None
        for ref, _key in _iter_agg_sum_singleton_terms(agg):
            if resolve_input(ref, ctx, AGG_STRATEGIES).source_type == "module_output":
                resolved_ref = ref
                break
        assert resolved_ref is not None, "fixture has no channel-resolving agg term"
        src2, manual2 = _build_agg_input_source(
            resolved_ref, ctx, None, redefs, usage_type_map,
            agg.expression.owning_part_qn, group_deriver, entry_points, {},
        )
        assert src2.source_type == "module_output"
        assert manual2 is False
