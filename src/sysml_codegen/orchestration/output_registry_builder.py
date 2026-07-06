"""OutputRegistry construction from pipeline data.

Extracted from generation/initialization.py (Step 7.1).
Implements the 4-phase registration protocol for building
a fully-populated OutputRegistry.
"""

import logging
from pathlib import Path

from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.core.identifier_types import (
    CanonicalChannel,
    ScopedKey,
    SysMLQN,
    make_canonical_channel,
    make_scoped_key,
)
from sysml_codegen.core.models import ChannelAlias
from sysml_codegen.core.output_registry import OutputRegistry, is_transitive_default
from sysml_codegen.core.qualified_names import (
    get_channel_name,
    owning_part_leaf,
    sanitize_qualified_name,
)
from sysml_codegen.extraction.data_models import (
    CalculationDefinitionData,
    ComputedAttributeClassification,
    ComputedAttributeData,
    ScopedAggregationData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.usage_extractor import CalcUsageData

logger = logging.getLogger(__name__)


def _resolve_reference_chain(
    instance_prefix: str,
    chain: list[str],
    ca_by_part_attr: dict[tuple[str, str], ComputedAttributeData],
    registry: OutputRegistry,
    visited: set[str],
) -> CanonicalChannel | None:
    """Walk a multi-hop reference_chain to a canonical channel (Item 10, #2).

    The transitive N-segment walk the confirm pass runs (the recursive analog of
    ``_resolve_aggregation_input_channel``, with its ``visited`` cycle guard, M5).

    Two terminal shapes, both handled here:
    - Direct calc-output terminal (ife_plant): ``radial_build.magnet_volume_total
      = tf_coil.volume_calc.volume`` — the full chain under the instance scope is a
      scoped channel key, so ``scoped_lookup`` hits directly.
    - Alias terminal one hop further (catf_mfe): ``catf_radial_build.magnet_volume_total
      = tf_coil.volume``, where ``tf_coil.volume`` is itself an EXPOSE alias for
      ``volume_calc.volume``. The direct key misses, so substitute the terminal
      attribute's OWN reference_chain and recurse. This resolves through the SCOPED
      calc-output channel, never the flat ``_alias`` (which is corrupted first-wins
      across same-named siblings — probe D-B).

    ``instance_prefix`` is the owning part's short name (the design-prefix-stripped
    scope, matching make_scoped_key's format). Returns the channel or None.
    """
    if not chain:
        return None

    key = f"{instance_prefix}.{'.'.join(chain)}"
    if key in visited:
        return None  # cycle guard (M5)
    visited.add(key)

    channel = registry.scoped_lookup(ScopedKey(key))
    if channel is not None:
        return channel

    # Alias terminal: the last segment names an attribute on the part reached by
    # the penultimate segment. Follow it by substituting its own reference_chain.
    if len(chain) < 2:
        return None
    part_seg, leaf = chain[-2], chain[-1]
    alias_ca = ca_by_part_attr.get((part_seg, leaf))
    if alias_ca is None or not alias_ca.reference_chain:
        return None
    substituted = chain[:-1] + alias_ca.reference_chain
    return _resolve_reference_chain(
        instance_prefix, substituted, ca_by_part_attr, registry, visited
    )


def build_output_registry(
    calc_usages: list[CalcUsageData],
    calc_defs: list[CalculationDefinitionData],
    aggregation_data: list[ScopedAggregationData],
    computed_attributes: list[ComputedAttributeData],
    channel_aliases: list[ChannelAlias],
    design_attributes: dict[Path, list[DesignAttributeData]],
) -> OutputRegistry:
    """Construct a fully-populated OutputRegistry from pipeline data.

    Implements the 4-phase registration protocol:
      Phase 1: Canonical channels (CalcUsage outputs, aggregation outputs, FORMULA outputs)
      Phase 2: CHAIN aliases (source="redefinition")
      Phase 3: EXPOSE_PURE aliases (source="expose_pure")
      Phase 4: Transitive design attribute aliases

    Args:
        calc_usages: All CalcUsageData from usage extraction.
        calc_defs: All CalculationDefinitionData from model.
        aggregation_data: ScopedAggregationData list from Step 3.5.
        computed_attributes: ComputedAttributeData list from Step 4.5.
        channel_aliases: ChannelAlias list from Steps 3.5 + 4.5.
        design_attributes: Design attributes by source file.

    Returns:
        Fully-populated OutputRegistry.
    """
    registry = OutputRegistry()
    calc_def_by_name = {cd.name: cd for cd in calc_defs}

    # ------------------------------------------------------------------
    # Offline-parity re-tag (Item 10, reconciles M6 with D9).
    #
    # M6 serializes the POST-confirm EXPOSE_PURE state, but the Phase-3b confirm
    # walk — the ONLY code that resolves a multi-hop chain to its correct transitive
    # channel — runs only on EXPOSE_CHAIN_TENTATIVE CAs. So when a recaptured snapshot
    # is reloaded, a multi-hop expose arrives as EXPOSE_PURE, Phase 3 registers its
    # alias via the NAIVE 2-segment path (which resolves the ambiguous terminal through
    # the first-wins-corrupted flat _alias — plasma_region, not tf_coil), and Phase 3b
    # skips it. The live path never hits this because the CA is still tentative when
    # Phase 3 runs (Phase 3 skips it) and 3b registers the correct channel first.
    #
    # D9 captured reference_chain precisely so the walk can re-run offline. Reconstruct
    # the PRE-confirm tentative state here for exactly the multi-hop candidates: an
    # already-EXPOSE_PURE CA whose reference_chain is a part-rooted chain of >= 2
    # segments (the durable INV-E signal; the AST is None on replay, but EXPOSE_PURE
    # already encodes the pure-FeatureChain root that the live leaf-tag checked). A
    # single-hop calc-rooted expose (reference_chain[0] is a calc-usage instance) is
    # left EXPOSE_PURE — Phase 3's naive path is correct for it. Live CAs are still
    # tentative here, so this is a no-op on the live path.
    # ------------------------------------------------------------------
    # Short calc-usage names (the last EQN segment). instance_name is short in some
    # fixtures but the full QN in others, so derive the short form from the QN.
    calc_usage_names = {cu.qualified_name.rsplit("__", 1)[-1] for cu in calc_usages}
    for ca in computed_attributes:
        if (
            ca.classification == ComputedAttributeClassification.EXPOSE_PURE
            and ca.reference_chain
            and len(ca.reference_chain) >= 2
            and ca.reference_chain[0] not in calc_usage_names
        ):
            ca.classification = ComputedAttributeClassification.EXPOSE_CHAIN_TENTATIVE

    # ------------------------------------------------------------------
    # Phase 1: Canonical channels
    #
    # Typed registration puts Key_C, Key_E_stripped, SysML QN into typed
    # registries. Key_A aliases registered for cross-scope CHAIN resolution.
    # ------------------------------------------------------------------
    phase1_count = 0
    # Local helper for Phase 3/4: maps Key_A format to CanonicalChannel.
    # NOT persisted in registry — exists only during construction.
    instance_attr_to_channel: dict[str, CanonicalChannel] = {}

    # Phase 1a: CalcUsage outputs
    for usage in calc_usages:
        calc_def = calc_def_by_name.get(usage.calc_def_name)
        if not calc_def:
            # D3-5: an unknown calc def means this usage registers ZERO output
            # channels — a real gap (every CalcUsage should register its outputs,
            # doc 10-output-registry.md Phase 1a). The bare `continue` hid it;
            # warn so the missing channels are visible, not silently absent.
            logger.warning(
                "OutputRegistry Phase 1a: calc def '%s' for usage '%s' not "
                "found — skipping; its output channels are NOT registered.",
                usage.calc_def_name,
                usage.instance_name,
            )
            continue
        for attr in calc_def.output_attributes:
            canonical = make_canonical_channel(usage.qualified_name, attr.name)
            key_c = make_scoped_key(usage.qualified_name, attr.name)
            # Typed: Key_C (REQ-OR-05, REQ-OR-08)
            registry.register_scoped(key_c, canonical)
            # Alias: Key_A for cross-scope CHAIN resolution (first-wins)
            key_a = f"{usage.instance_name}.{attr.name}"
            registry.register_alias(ScopedKey(key_a), canonical)
            # Helper for Phase 3/4 (Key_A -> CanonicalChannel)
            if key_a not in instance_attr_to_channel:
                instance_attr_to_channel[key_a] = canonical
            phase1_count += 1

    # Phase 1b: Aggregation outputs
    for agg in aggregation_data:
        canonical = CanonicalChannel(
            get_channel_name(agg.module_eqn, agg.expression.attribute_name)
        )
        instance_parts = agg.instance_path.split("__")

        # Typed: Key_E_stripped only (REQ-OR-05)
        if len(instance_parts) > 1:
            key_e_stripped = ScopedKey(
                ".".join(instance_parts[1:] + [agg.expression.attribute_name])
            )
            registry.register_scoped(key_e_stripped, canonical)

            # BF-7 alias variants — Key_E_stripped format
            for alias_name in agg.expression.aliases:
                alias_stripped = ScopedKey(
                    ".".join(instance_parts[1:] + [alias_name])
                )
                registry.register_scoped(alias_stripped, canonical)
        else:
            registry._canonical.add(canonical)

        phase1_count += 1

    # Phase 1c: FORMULA computed attribute outputs
    for ca in computed_attributes:
        if ca.classification != ComputedAttributeClassification.FORMULA:
            continue
        if ca.compilability != Compilability.FULLY_COMPILABLE:
            continue
        part_qn_python = sanitize_qualified_name(ca.owning_part_qualified_name)
        module_eqn = f"{part_qn_python}__{ca.python_name}"
        canonical = CanonicalChannel(get_channel_name(module_eqn, ca.python_name))

        # Typed: SysML QN (REQ-OR-05)
        if ca.owning_part_qualified_name:
            # Site 1 of the FORMULA sysml-QN lockstep flip (Item 7 / INV-1):
            # register the key per-segment sanitized so a quoted-owner REFERENCE
            # consumer (which now sanitizes its lookup key) matches.
            sysml_qn_key = SysMLQN(
                sanitize_qualified_name(f"{ca.owning_part_qualified_name}::{ca.name}")
            )
            registry.register_sysml_qn(sysml_qn_key, canonical)
        else:
            registry._canonical.add(canonical)

        # Key_F as ScopedKey for REFERENCE secondary resolution (spike Q5)
        key_f = f"{ca.owning_part_name}.{ca.python_name}"
        registry.register_scoped(ScopedKey(key_f), canonical)

        phase1_count += 1

    # ------------------------------------------------------------------
    # Phase 2: CHAIN aliases (source="redefinition")
    # canonical_name is ScopedKey format — use scoped_lookup directly
    # ------------------------------------------------------------------
    phase2_count = 0
    for alias in channel_aliases:
        if alias.source != "redefinition":
            continue
        resolved = registry.scoped_lookup(ScopedKey(alias.canonical_name))
        if resolved:
            registry.register_alias(ScopedKey(alias.alias_name), resolved)
            phase2_count += 1
        else:
            logger.warning(
                "Phase 2: CHAIN alias '%s' canonical '%s' not in registry",
                alias.alias_name,
                alias.canonical_name,
            )

    # ------------------------------------------------------------------
    # Phase 3: EXPOSE_PURE aliases (source="expose_pure")
    # canonical_name is Key_A format — use instance_attr_to_channel helper
    # ------------------------------------------------------------------
    phase3_count = 0
    for alias in channel_aliases:
        if alias.source != "expose_pure":
            continue
        # owning_part_qn may use "::" (SysML format) or "__" (Python format)
        owning_part_short = owning_part_leaf(alias.owning_part_qn)
        scoped_key = ScopedKey(f"{owning_part_short}.{alias.alias_name}")
        resolved = instance_attr_to_channel.get(alias.canonical_name)
        if resolved is None:
            resolved = registry.scoped_lookup(ScopedKey(alias.canonical_name))
        if resolved:
            registry.register_alias(scoped_key, resolved)
            phase3_count += 1
        else:
            logger.warning(
                "Phase 3: EXPOSE_PURE alias '%s' is dropped from generated "
                "output — canonical channel '%s' is not in the registry, so no "
                "named alias is emitted.",
                scoped_key,
                alias.canonical_name,
            )

    # ------------------------------------------------------------------
    # Phase 3b: Confirm multi-hop EXPOSE tentatives (Item 10, D6 / REQ-CA-10)
    #
    # The leaf tagged EXPOSE_CHAIN_TENTATIVE structurally (INV-E); it could not
    # decide EXPOSE-ness (B5). Now, with Phase-1 channels and Phase-2/3 aliases
    # registered, walk each tentative's reference_chain to a canonical channel.
    # Resolve -> register the cross-part alias and finalize EXPOSE_PURE IN PLACE
    # (M6: the shared CA objects, so nothing serializes a live tentative). Fail ->
    # revert to FORMULA in place (INV-D: byte-identical to today's behavior). Runs
    # after Phase 3, before Phase 4 (INV-G).
    # ------------------------------------------------------------------
    confirm_resolved = 0
    confirm_reverted = 0
    ca_by_part_attr: dict[tuple[str, str], ComputedAttributeData] = {
        (ca.owning_part_name, ca.name): ca for ca in computed_attributes
    }
    for ca in computed_attributes:
        if ca.classification != ComputedAttributeClassification.EXPOSE_CHAIN_TENTATIVE:
            continue
        channel = _resolve_reference_chain(
            ca.owning_part_name,
            ca.reference_chain or [],
            ca_by_part_attr,
            registry,
            set(),
        )
        if channel is not None:
            owning_part_short = owning_part_leaf(ca.owning_part_qualified_name)
            registry.register_alias(
                ScopedKey(f"{owning_part_short}.{ca.python_name}"), channel
            )
            ca.classification = ComputedAttributeClassification.EXPOSE_PURE
            confirm_resolved += 1
        else:
            ca.classification = ComputedAttributeClassification.FORMULA
            confirm_reverted += 1

    if confirm_resolved or confirm_reverted:
        logger.info(
            "Phase 3b: confirmed %d multi-hop EXPOSE alias(es), reverted %d "
            "unresolvable tentative(s) to FORMULA",
            confirm_resolved,
            confirm_reverted,
        )

    # INV-F (registry-side guarantee): every tentative is now EXPOSE_PURE or
    # FORMULA. A survivor means the confirm loop skipped a classification it must
    # own — a bug, not a degraded input — so raise rather than let it leak to the
    # graph builder's readers (which each also raise defensively, INV-F).
    for ca in computed_attributes:
        if ca.classification == ComputedAttributeClassification.EXPOSE_CHAIN_TENTATIVE:
            raise ValueError(
                f"INV-F violation: EXPOSE_CHAIN_TENTATIVE survived the confirm pass "
                f"for '{ca.owning_part_name}.{ca.name}' — the tentative was neither "
                f"resolved nor reverted."
            )

    # ------------------------------------------------------------------
    # Phase 4: Transitive design attribute aliases
    # default_value is Key_A format — use instance_attr_to_channel,
    # then scoped_lookup, then alias_lookup
    # ------------------------------------------------------------------
    phase4_count = 0
    for _path, attrs in design_attributes.items():
        for attr in attrs:
            if not is_transitive_default(attr.default_value):
                continue
            key = ScopedKey(f"{attr.parent_part}.{attr.name}")
            val = str(attr.default_value)
            resolved = instance_attr_to_channel.get(val)
            if resolved is None:
                resolved = registry.scoped_lookup(ScopedKey(val))
            if resolved is None:
                resolved = registry.alias_lookup(ScopedKey(val))
            if resolved:
                registry.register_alias(key, resolved)
                phase4_count += 1

    logger.info(
        "Step 5.5: OutputRegistry built — %d Phase 1 channels, "
        "%d Phase 2 CHAIN aliases, %d Phase 3 EXPOSE_PURE aliases, "
        "%d Phase 4 transitive aliases (%d total keys)",
        phase1_count,
        phase2_count,
        phase3_count,
        phase4_count,
        len(registry),
    )

    # Item 7 / D5: one WARNING count-summary for the first-wins alias collisions
    # (the per-collision lines are DEBUG). Non-empty only — a clean model stays
    # silent. Keeps the SC-5 cross-part signal loud without the per-key noise.
    if registry.alias_collision_count:
        logger.warning(
            "OutputRegistry: %d alias collision(s) resolved first-wins "
            "(%d distinct key(s)).",
            registry.alias_collision_count,
            registry.alias_collision_distinct_keys,
        )

    return registry


__all__ = [
    "build_output_registry",
]
