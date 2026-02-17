"""OutputRegistry: typed registries for resolving binding source_paths to canonical channel names.

Three typed registries replace the former flat ``dict[str, str]``:
- Scoped: ``dict[ScopedKey, CanonicalChannel]`` — Key_C (CalcUsage) and Key_E_stripped (Aggregation)
- SysML QN: ``dict[SysMLQN, CanonicalChannel]`` — Phase 1c FORMULA outputs
- Alias: ``dict[ScopedKey, CanonicalChannel]`` — Phases 2-4 aliases (CHAIN, EXPOSE_PURE, transitive)

See: 10-output-registry.md, 27-typed-registry-refactor.md
"""

import logging
from typing import Any

from sysml_codegen.core.identifier_types import (
    CanonicalChannel,
    ScopedKey,
    SysMLQN,
    make_scoped_key,
)

logger = logging.getLogger(__name__)


class OutputRegistry:
    """Typed registries for resolving binding source_paths to canonical channel names.

    Three typed registries provide scoped, exact-match lookups:
    - ``_scoped``: ``dict[ScopedKey, CanonicalChannel]`` — Key_C and Key_E_stripped
    - ``_sysml_qn``: ``dict[SysMLQN, CanonicalChannel]`` — SysML QN keys
    - ``_alias``: ``dict[ScopedKey, CanonicalChannel]`` — Phase 2-4 aliases

    Usage protocol (4-phase registration):
        Phase 1a: register_scoped() — CalcUsage outputs (Key_C)
        Phase 1b: register_scoped() — Aggregation outputs (Key_E_stripped)
        Phase 1c: register_sysml_qn() — FORMULA outputs
        Phase 2:  register_alias() — CHAIN redefinition aliases
        Phase 3:  register_alias() — EXPOSE_PURE aliases
        Phase 4:  register_alias() — Transitive design attribute aliases
    """

    def __init__(self) -> None:
        self._scoped: dict[ScopedKey, CanonicalChannel] = {}
        self._sysml_qn: dict[SysMLQN, CanonicalChannel] = {}
        self._alias: dict[ScopedKey, CanonicalChannel] = {}
        self._canonical: set[CanonicalChannel] = set()
        # Legacy keys (Key_A, Key_D, Key_F, bare) for deprecated resolve()
        # only. NOT checked by typed lookup methods. Removed in C11.
        self._compat: dict[str, CanonicalChannel] = {}

    # ------------------------------------------------------------------
    # Typed registration methods (REQ-OR-03)
    # ------------------------------------------------------------------

    def register_scoped(self, key: ScopedKey, channel: CanonicalChannel) -> None:
        """Register a scoped key mapping to a canonical channel (Phase 1a, 1b).

        Also adds the channel to the canonical set for phase-ordering enforcement.

        Collision policy: raise on duplicate key with different channel (unique
        by construction — a duplicate indicates a bug in key derivation).
        Same key with same channel is silently ignored.
        """
        self._canonical.add(channel)
        if key in self._scoped:
            if self._scoped[key] != channel:
                raise ValueError(
                    f"OutputRegistry scoped key collision: '{key}' already maps "
                    f"to '{self._scoped[key]}', cannot overwrite with '{channel}'"
                )
            return
        self._scoped[key] = channel

    def register_sysml_qn(self, key: SysMLQN, channel: CanonicalChannel) -> None:
        """Register a SysML QN key mapping to a canonical channel (Phase 1c).

        Also adds the channel to the canonical set.

        Collision policy: raise on duplicate key with different channel.
        """
        self._canonical.add(channel)
        if key in self._sysml_qn:
            if self._sysml_qn[key] != channel:
                raise ValueError(
                    f"OutputRegistry SysML QN collision: '{key}' already maps "
                    f"to '{self._sysml_qn[key]}', cannot overwrite with '{channel}'"
                )
            return
        self._sysml_qn[key] = channel

    def register_alias(
        self, alias: ScopedKey | str, canonical_channel: CanonicalChannel | str
    ) -> None:
        """Register an alias pointing to an existing canonical channel (Phases 2-4).

        Enforces phase ordering: the canonical_channel MUST already be in
        ``_canonical``. If not, logs a warning and skips.

        Collision policy: first-wins with warning (alias registry is not
        guaranteed unique — different sources may produce the same alias key).
        """
        # Accept str for backward compatibility during transition
        canonical_channel = CanonicalChannel(canonical_channel)
        alias = ScopedKey(alias)

        if canonical_channel not in self._canonical:
            logger.warning(
                "OutputRegistry alias '%s' targets unregistered channel '%s' "
                "(possible phase ordering violation)",
                alias,
                canonical_channel,
            )
            return
        if alias in self._alias:
            if self._alias[alias] != canonical_channel:
                logger.warning(
                    "OutputRegistry alias collision: '%s' already maps to '%s', "
                    "refusing to overwrite with '%s'",
                    alias,
                    self._alias[alias],
                    canonical_channel,
                )
            return
        self._alias[alias] = canonical_channel

    # ------------------------------------------------------------------
    # Typed lookup methods (REQ-OR-02)
    # ------------------------------------------------------------------

    def scoped_lookup(self, key: ScopedKey) -> CanonicalChannel | None:
        """Exact-match lookup in the scoped registry."""
        return self._scoped.get(key)

    def sysml_qn_lookup(self, key: SysMLQN) -> CanonicalChannel | None:
        """Exact-match lookup in the SysML QN registry."""
        return self._sysml_qn.get(key)

    def alias_lookup(self, key: ScopedKey) -> CanonicalChannel | None:
        """Exact-match lookup in the alias registry."""
        return self._alias.get(key)

    # ------------------------------------------------------------------
    # Deprecated API (backward compat for C11/C12 transition)
    # ------------------------------------------------------------------

    def register(self, canonical_channel: str, lookup_keys: list[str]) -> None:
        """Register a canonical channel with lookup keys (DEPRECATED).

        This method is kept for backward compatibility during the transition
        to typed registration. It registers keys in the ``_compat`` dict
        (checked only by ``resolve()``, not by typed lookup methods) and
        adds the canonical channel to the canonical set.

        Use ``register_scoped()``, ``register_sysml_qn()``, or
        ``register_alias()`` instead.
        """
        cc = CanonicalChannel(canonical_channel)
        self._canonical.add(cc)
        for key in lookup_keys:
            if key in self._compat:
                if self._compat[key] != cc:
                    logger.warning(
                        "OutputRegistry key collision: '%s' already maps to '%s', "
                        "refusing to overwrite with '%s'",
                        key,
                        self._compat[key],
                        cc,
                    )
                continue
            self._compat[key] = cc

    def resolve(self, source_path: str) -> str | None:
        """Resolve a source_path to a canonical channel name (DEPRECATED).

        Checks registries in order:
        scoped → sysml_qn → alias → compat → canonical_set.

        The ``_compat`` dict holds legacy keys (Key_A, Key_D, Key_F, bare)
        that the backtracker's ``resolve()`` calls still need. These are NOT
        visible to typed lookup methods. Removed when C11 updates the
        backtracker to use typed dispatch.

        Use ``scoped_lookup()``, ``sysml_qn_lookup()``, or ``alias_lookup()``
        instead.
        """
        result = self._scoped.get(ScopedKey(source_path))
        if result is not None:
            return result
        result = self._sysml_qn.get(SysMLQN(source_path))
        if result is not None:
            return result
        result = self._alias.get(ScopedKey(source_path))
        if result is not None:
            return result
        # Legacy compat keys (Key_A, Key_D, Key_F, bare)
        result = self._compat.get(source_path)
        if result is not None:
            return result
        # Canonical self-lookup (Key_B equivalent)
        cc = CanonicalChannel(source_path)
        if cc in self._canonical:
            return cc
        return None

    @staticmethod
    def derive_key_c(usage_qualified_name: str, output_attr_name: str) -> str:
        """Derive Key_C: dotted hierarchy path (DEPRECATED).

        Use ``make_scoped_key()`` from ``core.identifier_types`` instead.
        """
        return make_scoped_key(usage_qualified_name, output_attr_name)

    # ------------------------------------------------------------------
    # Properties and diagnostics
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Total number of lookup keys across all registries."""
        return (
            len(self._scoped) + len(self._sysml_qn) + len(self._alias)
            + len(self._compat) + len(self._canonical)
        )

    def __repr__(self) -> str:
        """Diagnostic repr showing registry sizes."""
        return (
            f"OutputRegistry(scoped={len(self._scoped)}, "
            f"sysml_qn={len(self._sysml_qn)}, "
            f"alias={len(self._alias)}, "
            f"compat={len(self._compat)}, "
            f"channels={len(self._canonical)})"
        )

    @property
    def canonical_channels(self) -> frozenset[CanonicalChannel]:
        """Read-only view of all canonical channel names."""
        return frozenset(self._canonical)


def is_transitive_default(default_value: Any) -> bool:
    """Check if a design attribute default_value is a dotted-path reference.

    A transitive default is a design attribute whose default_value is a
    dotted path pointing to a module output (e.g., "cost_model.total_cost"),
    as opposed to a numeric literal ("3.14"), None, or a bare name ("width").

    Used by Phase 4 registration to filter candidates for transitive alias
    registration.

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
