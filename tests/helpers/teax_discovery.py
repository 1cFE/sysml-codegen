"""Strict discovery for the provenance-pinned real TEAx SimKit dependency."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

TEAX_SIMKIT_PATH = "TEAX_SIMKIT_PATH"


def discover_teax_simkit(
    environment: Mapping[str, str], *, expected_root: Path
) -> Path:
    """Require the explicit SimKit root to equal the provenance root."""
    explicit = environment.get(TEAX_SIMKIT_PATH)
    if not explicit:
        raise RuntimeError(
            f"{TEAX_SIMKIT_PATH} is required and must equal the provenance root"
        )
    resolved = _require_simkit_root(TEAX_SIMKIT_PATH, Path(explicit))
    expected = _require_simkit_root("execution provenance", expected_root)
    if resolved != expected:
        raise RuntimeError(
            f"{TEAX_SIMKIT_PATH} {resolved} does not equal the provenance root {expected}"
        )
    return resolved


def _require_simkit_root(route: str, candidate: Path) -> Path:
    """Resolve ``candidate`` and require a real ``simkit`` package."""
    try:
        resolved = candidate.expanduser().resolve()
    except (OSError, RuntimeError) as error:
        raise RuntimeError(
            f"TEAx SimKit {route} {candidate} could not be resolved ({error})"
        ) from error
    if not (resolved.is_dir() and (resolved / "simkit" / "__init__.py").is_file()):
        raise RuntimeError(
            f"TEAx SimKit {route} {resolved} does not contain simkit/__init__.py"
        )
    return resolved
