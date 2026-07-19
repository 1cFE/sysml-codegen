"""Portable discovery for the real TEAx SimKit execution dependency."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

TEAX_SIMKIT_PATH = "TEAX_SIMKIT_PATH"


def discover_teax_simkit(environment: Mapping[str, str], *, repository_root: Path) -> Path:
    """Return a validated package root containing the real ``simkit`` package."""
    candidates: list[tuple[str, Path]] = []
    explicit = environment.get(TEAX_SIMKIT_PATH)
    if explicit:
        candidates.append((TEAX_SIMKIT_PATH, Path(explicit)))
    candidates.append(
        (
            "checkout-relative sibling",
            repository_root.parent / "teax" / "packages" / "teax-simkit",
        )
    )

    checked: list[str] = []
    seen: set[Path] = set()
    for route, candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
            valid = resolved.is_dir() and (resolved / "simkit" / "__init__.py").is_file()
        except (OSError, RuntimeError) as error:
            checked.append(f"{route}={candidate} (invalid: {error})")
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        checked.append(f"{route}={resolved}")
        if valid:
            return resolved

    raise RuntimeError(
        "TEAx SimKit was not found. Set TEAX_SIMKIT_PATH to the teax-simkit package root "
        "or provide the checkout-relative sibling ../teax/packages/teax-simkit. Checked: "
        + ", ".join(checked)
    )
