"""Nearest portable source context for otherwise unnamed public failures."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path


def model_source_context(
    model_paths: Sequence[Path],
) -> tuple[str, str | None, int | None]:
    """Return the first portable authored source named by caller model roots."""
    for ordinal, root in enumerate(model_paths):
        candidates = [root] if root.is_file() else sorted(root.rglob("*.sysml"))
        if not candidates:
            continue
        source = candidates[0]
        relative = source.name if root.is_file() else source.relative_to(root).as_posix()
        referent = f"root-{ordinal}/{relative}"
        return referent, referent, 1
    return "<model>", None, None


def snapshot_source_context(snapshot_path: Path) -> tuple[str, str | None, int | None]:
    """Read only the first sealed source referent for an unexpected snapshot failure."""
    try:
        document = json.loads(snapshot_path.read_text())
        files = document["sources"]["files"]
        referents = sorted(
            item["referent"]
            for item in files
            if isinstance(item, dict) and isinstance(item.get("referent"), str)
        )
    except (KeyError, TypeError, json.JSONDecodeError, OSError, UnicodeError):
        referents = []
    if not referents:
        return "<snapshot>", None, None
    return referents[0], referents[0], 1


__all__ = ["model_source_context", "snapshot_source_context"]
