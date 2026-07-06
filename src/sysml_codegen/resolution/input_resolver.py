"""Consolidated input resolver for aggregation SumTerm/SingletonTerm inputs.

Replaces inline resolution logic scattered through _resolve_aggregation_input_channel()
and _build_aggregation_module() in graph_builder.py with one function and an explicit,
ordered strategy chain.

Design intent: 04-input-resolver.md, 24-dual-resolution-architecture.md
Requirements: REQ-IR-01 through REQ-IR-07
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.core.identifier_types import (
    CanonicalChannel,
    ScopedKey,
    SysMLQN,
)
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.core.qualified_names import (
    get_channel_name,
    sanitize_name,
    sanitize_qualified_name,
)
from sysml_codegen.extraction.data_models import RedefinitionData, RedefinitionType
from sysml_codegen.resolution.models import InputSource

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ResolutionContext — immutable context bag (REQ-IR-04)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ResolutionContext:
    """Immutable context for resolve_input().

    No strategy mutates it. Mutation raises FrozenInstanceError.

    Attributes:
        output_registry: Typed registries (scoped, SysML QN, alias).
        redefinitions: PartDef-level :>> redefinitions from extraction.
        design_attrs: Flattened dict[str, DesignAttributeData] keyed by name/QN.
        module_eqn: Current module EQN (for self-reference guard).
        consumer_scope: Consumer's parent scope (dotted, design prefix stripped).
            Derived from module_eqn: split on __, drop [0] and [-1], join with '.'.
        instance_path: Full __-separated instance path for aggregation scoping.
    """

    output_registry: OutputRegistry
    redefinitions: list[RedefinitionData]
    design_attrs: dict[str, DesignAttributeData]
    module_eqn: str
    consumer_scope: str
    instance_path: str


# Type alias for strategy callables
ResolutionStrategy = Callable[[str, ResolutionContext], CanonicalChannel | None]


# ---------------------------------------------------------------------------
# Strategy A: ScopedRegistryLookup
# ---------------------------------------------------------------------------
def ScopedRegistryLookup(ref: str, ctx: ResolutionContext) -> CanonicalChannel | None:  # noqa: N802
    """Resolve ref via scoped registry lookup (Strategy A).

    Primary form: prepend consumer_scope to ref, query scoped + alias registries.
    Unscoped fallback: try ref directly as ScopedKey.

    Handles both CalcUsage-target refs (via Phase 1 scoped keys) and agg-to-agg
    refs (via Phase 1b aggregation keys and Phase 2 CHAIN aliases).
    """
    if "." not in ref:
        return None

    part_usage, attr = ref.rsplit(".", 1)

    # Primary: scoped lookup
    if ctx.consumer_scope:
        scoped_key = ScopedKey(f"{ctx.consumer_scope}.{part_usage}.{attr}")
        channel = ctx.output_registry.scoped_lookup(scoped_key)
        if channel is None:
            channel = ctx.output_registry.alias_lookup(scoped_key)
        if channel is not None:
            logger.debug(
                "Strategy A: '%s' resolved via scoped key '%s'",
                ref, scoped_key,
            )
            return channel

    # Unscoped fallback (e.g., "solar_array.capital_cost" at plant level)
    catalog_key = ScopedKey(f"{part_usage}.{attr}")
    channel = ctx.output_registry.scoped_lookup(catalog_key)
    if channel is None:
        channel = ctx.output_registry.alias_lookup(catalog_key)
    if channel is not None:
        logger.debug(
            "Strategy A: '%s' resolved via unscoped key '%s'",
            ref, catalog_key,
        )
        return channel

    return None


# ---------------------------------------------------------------------------
# Strategy B: SysMLQNLookup
# ---------------------------------------------------------------------------
def SysMLQNLookup(ref: str, ctx: ResolutionContext) -> CanonicalChannel | None:  # noqa: N802
    """Resolve ref via SysML QN registry lookup (Strategy B).

    Only applies when ref contains '::' (REFERENCE binding format).
    Zero-exercise for aggregation scope (spike confirmed), but required for
    completeness.
    """
    if "::" not in ref:
        return None

    # Site 5 of the FORMULA sysml-QN lockstep flip (Item 7 / INV-1): the second
    # sysml_qn_lookup consumer of the same registry; sanitize its key to match the
    # per-segment-sanitized registration key.
    channel = ctx.output_registry.sysml_qn_lookup(SysMLQN(sanitize_qualified_name(ref)))
    if channel is not None:
        logger.debug("Strategy B: '%s' resolved via SysML QN lookup", ref)
        return channel

    return None


# ---------------------------------------------------------------------------
# Strategy C: ChainRedefinitionFollow
# ---------------------------------------------------------------------------
def ChainRedefinitionFollow(ref: str, ctx: ResolutionContext) -> CanonicalChannel | None:  # noqa: N802
    """Resolve ref by following CHAIN :>> redefinitions (Strategy C).

    Searches ctx.redefinitions for a CHAIN redef matching the attribute in ref.
    If found, constructs a channel from the chain target and verifies it exists
    in the registry. Includes cycle detection via visited set.

    Connects aggregation inputs to CalcUsage outputs through part hierarchy
    redefinitions (e.g., :>> capital_cost = cost_model.total_cost).
    """
    if "." not in ref:
        return None

    canonical_channels = ctx.output_registry.canonical_channels
    visited: set[str] = set()

    def _follow(symbolic_ref: str) -> CanonicalChannel | None:
        if "." not in symbolic_ref:
            return None

        part_usage, attr = symbolic_ref.rsplit(".", 1)

        # Cycle guard
        visit_key = f"{part_usage}.{attr}"
        if visit_key in visited:
            logger.warning(
                "Strategy C: circular CHAIN detected: %s already visited in %s",
                visit_key, visited,
            )
            return None
        visited.add(visit_key)

        # Find CHAIN redefinition for this attribute on the child PartDef
        chain_redef = None
        for redef in ctx.redefinitions:
            if (redef.redefinition_type == RedefinitionType.CHAIN
                    and redef.attribute_name == attr):
                redef_part_name = redef.owning_part_qn.split("__")[-1]
                if sanitize_name(redef_part_name).lower() == part_usage.lower():
                    chain_redef = redef
                    break

        if chain_redef and chain_redef.source_path:
            # Parse chain source "calc_usage.output"
            if "." in chain_redef.source_path:
                calc_usage, output = chain_redef.source_path.rsplit(".", 1)
                channel = get_channel_name(
                    f"{ctx.instance_path}__{part_usage}__{calc_usage}", output,
                )
                if channel in canonical_channels:
                    return CanonicalChannel(channel)
            # Recurse with cycle guard
            return _follow(chain_redef.source_path)

        return None

    return _follow(ref)


# ---------------------------------------------------------------------------
# Strategy D: DesignAttributeLookup
# ---------------------------------------------------------------------------
def DesignAttributeLookup(ref: str, ctx: ResolutionContext) -> CanonicalChannel | None:  # noqa: N802
    """Match ref against design attributes by leaf name (Strategy D).

    Enables entry point deduplication: if a design attribute matches the ref
    leaf name, returns None (causing fallthrough to the entry point fallback,
    which will use the design attribute's QN as the entry point name).

    Currently returns None for all cases — Strategy D does not produce a
    CanonicalChannel. It is included in AGG_STRATEGIES for future extensibility
    and to document the design intent.
    """
    # Strategy D matches design attributes but does not produce a CanonicalChannel
    # (design attrs are entry points, not module outputs). The entry point fallback
    # in resolve_input() handles QN construction.
    return None


# ---------------------------------------------------------------------------
# Strategy chain constants
# ---------------------------------------------------------------------------
AGG_STRATEGIES: list[ResolutionStrategy] = [
    ScopedRegistryLookup,       # A: ScopedKey → scoped registry + alias registry
    ChainRedefinitionFollow,    # C: :>> chain → ScopedKey → scoped registry
    SysMLQNLookup,              # B: SysMLQN → SysML QN registry (for :: refs)
    DesignAttributeLookup,      # D: design attr match → entry point
]


# ---------------------------------------------------------------------------
# resolve_input() — consolidated resolution function (REQ-IR-01)
# ---------------------------------------------------------------------------
def resolve_input(
    ref: str,
    ctx: ResolutionContext,
    strategies: list[ResolutionStrategy],
) -> InputSource:
    """Resolve a symbolic reference to an InputSource.

    Always returns an InputSource (REQ-IR-01) — never raises on unresolved refs.
    Strategies execute in declared list order; first non-None result wins (REQ-IR-02).
    Self-reference guard rejects channels where the producing module matches
    ctx.module_eqn (REQ-IR-03).
    Fallback produces an entry_point InputSource (REQ-IR-06).

    Args:
        ref: Symbolic reference (e.g., "pv_module.capital_cost").
        ctx: Immutable ResolutionContext.
        strategies: Ordered strategy list (e.g., AGG_STRATEGIES).

    Returns:
        InputSource with source_type "module_output" or "entry_point".
    """
    for strategy in strategies:
        channel = strategy(ref, ctx)
        if channel is not None:
            # Self-reference guard (REQ-IR-03)
            producing_module = channel.rsplit("__", 1)[0]
            if producing_module == ctx.module_eqn:
                logger.debug(
                    "Self-reference guard: '%s' resolved to channel '%s' "
                    "belonging to own module '%s' — skipping",
                    ref, channel, ctx.module_eqn,
                )
                continue
            return InputSource(
                source_type="module_output",
                producer_channel=channel,
            )

    # Fallback: entry_point (REQ-IR-06)
    param_name = ref.rsplit(".", 1)[-1] if "." in ref else ref
    ep_qn = f"{ctx.module_eqn}__{param_name}"
    logger.debug(
        "resolve_input fallback: '%s' → entry_point '%s'",
        ref, ep_qn,
    )
    return InputSource(
        source_type="entry_point",
        qualified_name=ep_qn,
    )
