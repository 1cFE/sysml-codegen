"""Portable discovery for the real TEAx SimKit execution dependency."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

TEAX_SIMKIT_PATH = "TEAX_SIMKIT_PATH"


_REMEDY = (
    "Set TEAX_SIMKIT_PATH to the teax-simkit package root, or unset it to use the "
    "checkout-relative sibling ../teax/packages/teax-simkit."
)


def discover_teax_simkit(environment: Mapping[str, str], *, repository_root: Path) -> Path:
    """Return a validated package root containing the real ``simkit`` package.

    An explicitly-set ``TEAX_SIMKIT_PATH`` is authoritative: if it does not point at a
    real simkit package the call fails, rather than silently falling back to the
    checkout-relative sibling and hiding the operator's misconfiguration. The sibling is
    tried only when no explicit path is set.
    """
    explicit = environment.get(TEAX_SIMKIT_PATH)
    if explicit:
        return _require_simkit_root(TEAX_SIMKIT_PATH, Path(explicit))

    sibling = repository_root.parent / "teax" / "packages" / "teax-simkit"
    return _require_simkit_root("checkout-relative sibling", sibling)


def _require_simkit_root(route: str, candidate: Path) -> Path:
    """Resolve ``candidate`` and return it, or raise if it is not a simkit package root."""
    try:
        resolved = candidate.expanduser().resolve()
    except (OSError, RuntimeError) as error:
        raise RuntimeError(
            f"TEAx SimKit {route} {candidate} could not be resolved ({error}). {_REMEDY}"
        ) from error
    if not (resolved.is_dir() and (resolved / "simkit" / "__init__.py").is_file()):
        raise RuntimeError(
            f"TEAx SimKit {route} {resolved} does not contain simkit/__init__.py. {_REMEDY}"
        )
    return resolved
