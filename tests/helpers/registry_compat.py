"""Test helpers replacing removed OutputRegistry.resolve() and .register() methods.

These convenience functions provide the same cascade behavior that was previously
on the OutputRegistry class. Production code should use typed lookups directly
(scoped_lookup, sysml_qn_lookup, alias_lookup). Test code may use these for brevity.
"""

from __future__ import annotations

from sysml_codegen.core.identifier_types import (
    CanonicalChannel,
    ScopedKey,
    SysMLQN,
)
from sysml_codegen.core.output_registry import OutputRegistry


def registry_resolve(reg: OutputRegistry, source_path: str) -> str | None:
    """Cascade through typed registries: scoped -> sysml_qn -> alias -> canonical.

    Equivalent to the removed OutputRegistry.resolve() method.
    """
    result = reg.scoped_lookup(ScopedKey(source_path))
    if result is not None:
        return result
    result = reg.sysml_qn_lookup(SysMLQN(source_path))
    if result is not None:
        return result
    result = reg.alias_lookup(ScopedKey(source_path))
    if result is not None:
        return result
    cc = CanonicalChannel(source_path)
    if cc in reg.canonical_channels:
        return cc
    return None


def registry_register(
    reg: OutputRegistry, canonical_channel: str, lookup_keys: list[str]
) -> None:
    """Register a canonical channel with lookup keys as aliases.

    Equivalent to the removed OutputRegistry.register() method.
    """
    cc = CanonicalChannel(canonical_channel)
    reg._canonical.add(cc)
    for key in lookup_keys:
        reg.register_alias(ScopedKey(key), cc)
