"""OutputRegistry: single lookup for resolving binding source_paths to canonical channel names.

Replaces the backtracker's 5 ad-hoc indexes with one exact-match dict.
See: .project/reports/08_algorithm_revised.md (Sections 4, 6, 12)
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class OutputRegistry:
    """Single lookup for resolving binding source_paths to canonical channel names.

    Replaces the backtracker's 5 ad-hoc indexes with one exact-match dict.
    No normalization, no cascade, no fallback. If a key isn't registered,
    resolve() returns None.

    Usage protocol (4-phase registration):
        Phase 1: register() -- CalcUsage outputs (Key_A, Key_B, Key_C),
                 aggregation outputs (Key_D, Key_E), FORMULA outputs (Key_F)
        Phase 2: register_alias() -- CHAIN redefinition aliases
        Phase 3: register_alias() -- EXPOSE_PURE aliases (PartUsage only)
        Phase 4: register_alias() -- Transitive design attribute aliases
    """

    def __init__(self) -> None:
        self._index: dict[str, str] = {}
        self._canonical: set[str] = set()

    def register(self, canonical_channel: str, lookup_keys: list[str]) -> None:
        """Register a canonical channel with its lookup keys (Phase 1).

        The canonical_channel itself is also registered as a self-referencing
        key, so resolve(canonical_channel) always works.

        Collision policy: refuse overwrite. If a key already maps to a
        different canonical channel, log a warning and keep the first
        registration. This prevents silent mis-wiring from duplicate keys.

        Args:
            canonical_channel: The PQN-format channel name
                (e.g., "Design__plant__lcoe__lcoe_per_mwh").
            lookup_keys: List of alternative key formats (Key_A, Key_B,
                Key_C, etc.) that should resolve to this channel.
        """
        self._canonical.add(canonical_channel)
        # Self-register the canonical channel name
        if canonical_channel not in self._index:
            self._index[canonical_channel] = canonical_channel
        for key in lookup_keys:
            if key in self._index:
                if self._index[key] != canonical_channel:
                    logger.warning(
                        "OutputRegistry key collision: '%s' already maps to '%s', "
                        "refusing to overwrite with '%s'",
                        key,
                        self._index[key],
                        canonical_channel,
                    )
                continue  # skip duplicate or collision
            self._index[key] = canonical_channel

    def register_alias(self, alias: str, canonical_channel: str) -> None:
        """Register an alias pointing to an existing canonical channel (Phases 2-4).

        Enforces phase ordering: the canonical_channel MUST already be
        registered (via register() or a prior register_alias()). If not,
        logs a warning and skips -- this catches phase ordering violations
        and unresolvable alias targets.

        Note: The source design document (08_algorithm_revised.md, Section 12)
        uses ``assert`` for phase ordering enforcement. This implementation
        intentionally uses ``logger.warning()`` + skip instead, because an
        assert crash on data issues in a production pipeline is too harsh --
        a warning with diagnostic context is more actionable. The spec (FR-2)
        allows either "assert/warn", so this satisfies the contract.

        Collision policy: same as register() -- refuse overwrite on collision.

        Args:
            alias: The alias lookup key (scoped dotted format).
            canonical_channel: The canonical channel this alias points to.
                Must already exist in the registry.
        """
        if canonical_channel not in self._canonical:
            logger.warning(
                "OutputRegistry alias '%s' targets unregistered channel '%s' "
                "(possible phase ordering violation)",
                alias,
                canonical_channel,
            )
            return
        if alias in self._index:
            if self._index[alias] != canonical_channel:
                logger.warning(
                    "OutputRegistry key collision: '%s' already maps to '%s', "
                    "refusing to overwrite with '%s'",
                    alias,
                    self._index[alias],
                    canonical_channel,
                )
            return
        self._index[alias] = canonical_channel

    def resolve(self, source_path: str) -> str | None:
        """Resolve a binding source_path to a canonical channel name.

        EXACT MATCH ONLY. No normalization, no :: -> . conversion,
        no bare-name fallback. This is a pure dict lookup.

        Empirically validated contracts (do NOT add normalization):
        - Spike 4: Zero bare-name references across 94 bindings
        - Spike 5: SYSML_QN normalization is broken (consuming path
          differs from producing path)

        Args:
            source_path: The binding's source_path in dotted format.

        Returns:
            Canonical channel name, or None if not found.
        """
        return self._index.get(source_path)

    @staticmethod
    def derive_key_c(usage_qualified_name: str, output_attr_name: str) -> str:
        """Derive Key_C: dotted hierarchy path (strips design prefix).

        Key_C is CRITICAL for Phase 2 CHAIN alias resolution. Spike 8
        confirmed: ALL 41 Phase 2 CHAIN aliases in solar_battery resolve
        EXCLUSIVELY via Key_C.

        Algorithm: split QN on '__', drop segments[0] (design PartDef
        prefix), join remaining with '.', append '.' + output_attr_name.

        Args:
            usage_qualified_name: The CalcUsage EQN
                (e.g., "SolarBatteryDesign__solar_battery_plant__lcoe").
            output_attr_name: The output attribute name
                (e.g., "lcoe_per_mwh").

        Returns:
            Dotted hierarchy path
            (e.g., "solar_battery_plant.lcoe.lcoe_per_mwh").
        """
        segments = usage_qualified_name.split("__")
        return ".".join(segments[1:]) + "." + output_attr_name

    def __len__(self) -> int:
        """Number of lookup keys in the registry (for diagnostics)."""
        return len(self._index)

    def __repr__(self) -> str:
        """Diagnostic repr showing key and channel counts."""
        return (
            f"OutputRegistry(keys={len(self._index)}, "
            f"channels={len(self._canonical)})"
        )

    @property
    def canonical_channels(self) -> frozenset[str]:
        """Read-only view of all canonical channel names."""
        return frozenset(self._canonical)


def is_transitive_default(default_value: Any) -> bool:
    """Check if a design attribute default_value is a dotted-path reference.

    A transitive default is a design attribute whose default_value is a
    dotted path pointing to a module output (e.g., "cost_model.total_cost"),
    as opposed to a numeric literal ("3.14"), None, or a bare name ("width").

    Used by Phase 4 registration to filter candidates for transitive alias
    registration. Empirically validated by Spike 7: 128 attrs tested,
    correct for all. Only 2 transitive defaults exist across all models.

    Args:
        default_value: The design attribute's default_value (any type).

    Returns:
        True if the value looks like a dotted-path reference.
    """
    if default_value is None:
        return False
    val = str(default_value)
    if "." not in val:
        return False
    try:
        float(val)
        return False  # numeric like "3.14"
    except (ValueError, TypeError):
        return True  # dotted path like "cost_model.total_cost"


__all__ = [
    "OutputRegistry",
    "is_transitive_default",
]
