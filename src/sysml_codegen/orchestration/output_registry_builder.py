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
from sysml_codegen.core.qualified_names import get_channel_name, sysml_to_python_qualified_name
from sysml_codegen.extraction.data_models import (
    CalculationDefinitionData,
    ComputedAttributeClassification,
    ComputedAttributeData,
    ScopedAggregationData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.usage_extractor import CalcUsageData

logger = logging.getLogger(__name__)


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
        part_qn_python = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
        module_eqn = f"{part_qn_python}__{ca.python_name}"
        canonical = CanonicalChannel(get_channel_name(module_eqn, ca.python_name))

        # Typed: SysML QN (REQ-OR-05)
        if ca.owning_part_qualified_name:
            sysml_qn_key = SysMLQN(f"{ca.owning_part_qualified_name}::{ca.name}")
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
        qn = alias.owning_part_qn
        if "::" in qn:
            owning_part_short = qn.rsplit("::", 1)[-1]
        else:
            owning_part_short = qn.split("__")[-1]
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

    return registry


__all__ = [
    "build_output_registry",
]
