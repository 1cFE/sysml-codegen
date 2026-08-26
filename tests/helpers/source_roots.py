"""Ordinary-checkout source roots for tests that scan companion sources.

Replaces the manifest-gated ``verification.artifact_sources`` seam (REPO-CLEANUP Move C):
the agentic root is derived from the installed editable ``agentic_mbse`` package, and the
history root is this repository itself.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def agentic_source_root() -> Path:
    """Root of the agentic-mbse checkout the installed package came from."""
    import agentic_mbse

    root = Path(agentic_mbse.__file__).resolve().parents[2]
    if not (root / "src" / "agentic_mbse").is_dir():
        raise RuntimeError(f"agentic_mbse does not resolve to an editable checkout: {root}")
    return root


def codegen_history_root() -> Path:
    """The git history the fingerprint-stability checks read: this repository."""
    return REPO_ROOT
