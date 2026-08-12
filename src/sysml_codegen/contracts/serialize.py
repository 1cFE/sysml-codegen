"""Deterministic JSON serialization for contracts (design.md:196-201), both forms.

Two byte-stable spellings live here, side by side because they are the same decision seen
twice. ``canonical_json`` is the compact fingerprint payload form — what gets hashed.
``write_contract_json`` is the on-disk form: pretty and human-readable but still identical
across two builds (INV-6), so a contract file's own bytes hash reproducibly inside the seal.

``canonical_json`` moved here from ``generation.constraint_catalog`` in Revise step 6d. It
sat there because catalog assembly was its first caller; assembly is now the projector's
(`elaboration/project.py`), and the contract fingerprint is the only reader left.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from pydantic import BaseModel

__all__ = ["canonical_json", "write_contract_json"]


def canonical_json(obj: Any) -> str:
    """Return the compact, key-sorted, ASCII-safe JSON form used as a fingerprint payload."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def write_contract_json(path: Path, model: BaseModel) -> None:
    """Write ``model`` as deterministic, pretty-printed JSON bytes."""
    payload = json.dumps(model.model_dump(), indent=2, sort_keys=True, ensure_ascii=True)
    path.write_text(payload + "\n")
