"""Pinned version constants for the contracts package (CONSTRAINT-EXEC Item 9 / P4).

Both are generator constants, never read from an installed runtime — a package's seal
records the generator that produced it, not whatever happens to be on the loading
machine (D5: coupling generation to an installed teax would break license-free
snapshot determinism).
"""

from __future__ import annotations

RUNTIME_CONTRACT_VERSION = "1.0.0"
"""The runtime API surface the emitted code targets.

Bump the major version on any breaking change to that surface; minor/patch for
compatible additions. Owner-overridable; this is the initial token (P4).
"""


def generator_version() -> str:
    """The sysml-codegen version that produced a seal."""
    from sysml_codegen import __version__

    return __version__


__all__ = ["RUNTIME_CONTRACT_VERSION", "generator_version"]
