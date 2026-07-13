"""Deterministic on-disk JSON serialization for contract files (design.md:196-201).

The fingerprint payload form lives in ``generation.constraint_catalog._canonical_json``
(compact, reused per P2). This is the sibling on-disk form: pretty and human-readable but
still byte-stable across two builds (INV-6), so a contract file's own bytes hash
reproducibly inside the seal.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from pydantic import BaseModel

__all__ = ["write_contract_json"]


def write_contract_json(path: Path, model: BaseModel) -> None:
    """Write ``model`` as deterministic, pretty-printed JSON bytes."""
    payload = json.dumps(model.model_dump(), indent=2, sort_keys=True, ensure_ascii=True)
    path.write_text(payload + "\n")
