"""Identifier type transformations for ADR-003.

Provides data classes and functions for transforming SysML qualified names
to Python identifiers (module types, file paths, EQNs).

Typed identifier wrappers (NewType over str) for the typed registry refactor:
- SysMLQN: SysML qualified name with :: separator
- EQN: Execution qualified name with __ separator
- PQN: Parameter qualified name (EQN__param)
- CanonicalChannel: PQN-format output channel name
- ScopedKey: Dotted hierarchy key (design prefix stripped)

See: 27-typed-registry-refactor.md
"""

import hashlib
import json
from dataclasses import dataclass
from typing import NewType

from sysml_codegen.core.qualified_names import sanitize_name

# ---------------------------------------------------------------------------
# Typed identifier wrappers (FR-1, NFR-1: zero runtime cost via NewType)
# ---------------------------------------------------------------------------
SysMLQN = NewType("SysMLQN", str)
"""SysML qualified name with ``::`` separator (e.g., ``Package::Element``)."""

EQN = NewType("EQN", str)
"""Execution qualified name with ``__`` separator (e.g., ``Design__plant__calc``)."""

PQN = NewType("PQN", str)
"""Parameter qualified name: ``EQN__param`` (e.g., ``Design__plant__calc__output``)."""

CanonicalChannel = NewType("CanonicalChannel", str)
"""PQN-format output channel name. Rejects ``::`` and ``.``."""

ScopedKey = NewType("ScopedKey", str)
"""Dotted hierarchy key with design prefix stripped. Rejects ``::``."""

ScopedAliasKey = NewType("ScopedAliasKey", tuple[str, str])
"""Structured ``(scope, leaf)`` key for the part-def / consumer-scoped alias
registry (Item 10, D7). Stored UNJOINED so ``("a.b", "c")`` and ``("a", "b.c")``
can never collapse — the leaf is always a single segment, so ``("a", "b.c")``
cannot even arise. Distinct namespace from the flat string ``ScopedKey`` alias."""


def make_scoped_key(usage_eqn: str, attr_name: str) -> ScopedKey:
    """Derive a ScopedKey from a usage EQN and attribute name.

    Replaces ``OutputRegistry.derive_key_c()``. Splits EQN on ``__``,
    drops ``segments[0]`` (design prefix), joins remaining with ``.``,
    appends ``.{attr_name}``.

    Args:
        usage_eqn: The CalcUsage EQN
            (e.g., ``"SolarBatteryDesign__solar_battery_plant__lcoe"``).
        attr_name: The output attribute name (e.g., ``"lcoe_per_mwh"``).

    Returns:
        ScopedKey in dotted format
        (e.g., ``"solar_battery_plant.lcoe.lcoe_per_mwh"``).
    """
    segments = usage_eqn.split("__")
    return ScopedKey(".".join(segments[1:]) + "." + attr_name)


def make_canonical_channel(usage_eqn: str, attr_name: str) -> CanonicalChannel:
    """Derive a CanonicalChannel from a usage EQN and attribute name.

    Wraps ``get_channel_name()`` output in the ``CanonicalChannel`` type.

    Args:
        usage_eqn: The CalcUsage EQN
            (e.g., ``"SolarBatteryDesign__solar_battery_plant__lcoe"``).
        attr_name: The output attribute name (e.g., ``"lcoe_per_mwh"``).

    Returns:
        CanonicalChannel in PQN format
        (e.g., ``"SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"``).
    """
    return CanonicalChannel(f"{usage_eqn}__{attr_name}")


@dataclass(frozen=True)
class SysMLQualifiedName:
    """Raw qualified name from SysIDE (uses :: separator)."""

    value: str

    @property
    def segments(self) -> list[str]:
        """Split into individual segments (packages + element name)."""
        return self.value.split("::")

    @property
    def package_segments(self) -> list[str]:
        """Get package path segments (everything except last segment)."""
        return self.segments[:-1]

    @property
    def element_name(self) -> str:
        """Get element name (last segment)."""
        return self.segments[-1]


@dataclass(frozen=True)
class ModuleType:
    """TEAx registry key and YAML module_type."""

    value: str

    @classmethod
    def from_sysml(cls, sqn: SysMLQualifiedName) -> "ModuleType":
        """Create ModuleType from SysML qualified name.

        Sanitizes each segment before lowercasing (order is load-bearing: the
        reserved-word guard must see the pre-lowercased form, matching
        build_element_qualified_name). Class name preserves case.
        """
        namespace = ".".join(sanitize_name(s).lower() for s in sqn.package_segments)
        class_name = f"{sanitize_name(sqn.element_name)}Module"
        return cls(f"{namespace}.{class_name}" if namespace else class_name)


@dataclass(frozen=True)
class PythonModulePath:
    """Generated Python module location."""

    directory: str
    filename: str

    @property
    def full_path(self) -> str:
        """Get full relative path including .py extension."""
        if self.directory:
            return f"{self.directory}/{self.filename}.py"
        return f"{self.filename}.py"

    @property
    def import_path(self) -> str:
        """Get Python import path (dotted, no .py extension)."""
        if self.directory:
            return f"{self.directory.replace('/', '.')}.{self.filename}"
        return self.filename

    @property
    def impl_import_path(self) -> str:
        """Get Python import path for handwritten implementation."""
        if self.directory:
            return f"{self.directory.replace('/', '.')}.{self.filename}_impl"
        return f"{self.filename}_impl"

    @classmethod
    def from_sysml(cls, sqn: SysMLQualifiedName) -> "PythonModulePath":
        """Create PythonModulePath from SysML qualified name.

        Sanitizes each segment before lowercasing (sanitize-then-lower, matching
        ModuleType.from_sysml and build_element_qualified_name).
        """
        directory = "/".join(sanitize_name(s).lower() for s in sqn.package_segments)
        return cls(directory, sanitize_name(sqn.element_name).lower())


@dataclass(frozen=True)
class ElementQualifiedName:
    """Internal codegen identifier (uses __ separator per ADR-001)."""

    value: str

    @classmethod
    def from_sysml(cls, sqn: SysMLQualifiedName) -> "ElementQualifiedName":
        """Create ElementQualifiedName from SysML qualified name."""
        return cls("__".join(sqn.segments))


def derive_module_type(qualified_name: str) -> str:
    """Transform SysML qualified name to namespaced module_type.

    Args:
        qualified_name: SysML qualified name (e.g., "Package::Element")

    Returns:
        Namespaced module type (e.g., "package.ElementModule")
    """
    sqn = SysMLQualifiedName(qualified_name)
    return ModuleType.from_sysml(sqn).value


def derive_python_path(qualified_name: str) -> str:
    """Transform SysML qualified name to Python file path.

    Args:
        qualified_name: SysML qualified name (e.g., "Package::Element")

    Returns:
        Relative path to Python file (e.g., "package/element.py")
    """
    sqn = SysMLQualifiedName(qualified_name)
    return PythonModulePath.from_sysml(sqn).full_path


def mint_constraint_id(
    *,
    instance_path: str,
    source_local: str,
    tuple_: tuple,
    digest_hex_length: int = 16,
) -> str:
    """Mint a deterministic, collision-checkable ``constraint_id`` (D3/N1).

    ``{instance_path}__{source_local}__{sha256[:16] of the canonical tuple}``.
    The prefix is human-scannable; the suffix folds source-local identity,
    owner-instance identity, membership kind, and polarity into a 64-bit
    collision-visible fingerprint (a hard duplicate is a generation error,
    checked post-expansion by
    :func:`sysml_codegen.analysis.constraint_lowering.assert_unique_constraint_ids`).

    Lives here rather than in the legacy lowering module so the exact
    projection route and the legacy route mint one identity by one rule.
    """
    canonical = json.dumps(list(tuple_), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    if digest_hex_length < 1 or digest_hex_length > 64:
        raise ValueError("digest_hex_length must be between 1 and 64")
    suffix = hashlib.sha256(canonical.encode()).hexdigest()[:digest_hex_length]
    return f"{instance_path}__{source_local}__{suffix}"


__all__ = [
    "SysMLQualifiedName",
    "ModuleType",
    "PythonModulePath",
    "ElementQualifiedName",
    "derive_module_type",
    "derive_python_path",
    "SysMLQN",
    "EQN",
    "PQN",
    "CanonicalChannel",
    "ScopedKey",
    "make_scoped_key",
    "make_canonical_channel",
    "mint_constraint_id",
]
