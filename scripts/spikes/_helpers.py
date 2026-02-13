"""Shared utilities for SysIDE assumption spikes.

Common model loading, output formatting, and defensive attribute access
used by all spike scripts in this directory.

Usage:
    from _helpers import DEFAULT_SUITES, load_model, safe_attr, type_name
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import dotenv

# Load SysIDE license key from agentic-mbse .env (or local .env if present)
dotenv.load_dotenv(Path.home() / "1cfe/agentic-mbse/.env")
dotenv.load_dotenv()  # also check local .env (won't override existing vars)

from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.usage_extractor import (
    CalcUsageData,
    extract_calculation_usages,
)


# ---------------------------------------------------------------------------
# Model Suites
# ---------------------------------------------------------------------------

DEFAULT_SUITES: list[tuple[str, list[Path]]] = [
    ("solar_battery", [Path("tests/fixtures/solar_battery_model")]),
    ("chain_spike", [Path("tests/fixtures/chain_spike_model")]),
    ("e2e_attr_expr", [Path.home() / "1cfe/fusion-tea/models/tests/e2e_attr_expr"]),
]

EXTENDED_SUITES: list[tuple[str, list[Path]]] = DEFAULT_SUITES + [
    ("catf_mfe", [Path("tests/fixtures/catf_mfe_model")]),
]


# ---------------------------------------------------------------------------
# Model Loading
# ---------------------------------------------------------------------------


def load_model(
    model_paths: list[Path],
) -> tuple[Any | None, Any | None, SysMLDataExtractor | None]:
    """Load a SysML model, fail loudly if it doesn't work.

    Returns:
        (model, adapter, extractor) or (None, None, None) on failure.
    """
    extractor = SysMLDataExtractor(model_paths)
    if not extractor.load_models():
        label = ", ".join(str(p) for p in model_paths)
        print(f"  ERROR: Failed to load models from {label}", file=sys.stderr)
        return None, None, None
    return extractor.model, extractor.adapter, extractor


# ---------------------------------------------------------------------------
# Defensive Attribute Access
# ---------------------------------------------------------------------------


def safe_attr(obj: Any, attr: str, default: Any = "<missing>") -> Any:
    """Safely access attribute, returning default if missing or error."""
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default


def type_name(obj: Any) -> str:
    """Return type(obj).__name__ for AST node identification."""
    if obj is None or obj == "<missing>":
        return "<None>"
    return type(obj).__name__


# ---------------------------------------------------------------------------
# Output Formatting
# ---------------------------------------------------------------------------


def print_section(title: str) -> None:
    """Print a section header with separator lines."""
    width = max(len(title) + 4, 60)
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_subsection(title: str) -> None:
    """Print a subsection header."""
    print(f"\n--- {title} ---\n")


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    """Print an aligned table to stdout.

    Computes column widths from headers and row data, then prints
    with consistent padding.
    """
    if not rows:
        print("  (no data)")
        return

    # Compute column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Print header
    header_line = "  ".join(
        str(h).ljust(col_widths[i]) for i, h in enumerate(headers)
    )
    print(f"  {header_line}")
    separator = "  ".join("-" * w for w in col_widths)
    print(f"  {separator}")

    # Print rows
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            width = col_widths[i] if i < len(col_widths) else 0
            cells.append(str(cell).ljust(width))
        print(f"  {'  '.join(cells)}")
