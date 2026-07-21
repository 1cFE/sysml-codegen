"""Portable path setup for the real TEAx SimKit execution lane."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from tests.helpers.teax_discovery import discover_teax_simkit

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_REPO_SRC = _REPOSITORY_ROOT / "src"
_TEAX_SIMKIT = discover_teax_simkit(os.environ, repository_root=_REPOSITORY_ROOT)

for _p in (_REPO_SRC, _TEAX_SIMKIT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
