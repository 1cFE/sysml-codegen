"""Execution-lane path setup (Item 7 / D10).

This lane runs by hand in the agentic-mbse venv, not the codegen venv (memory
[[teax-simkit-execution-env]]: teax's own .venv is unprovisioned). The working incantation:

    SYSIDE_LICENSE_KEY=<key> uv run --directory /home/reid/1cfe/agentic-mbse python -m pytest \
        -m execution -p no:cacheprovider \
        --rootdir /home/reid/1cfe/sysml-codegen /home/reid/1cfe/sysml-codegen/tests/execution \
        --override-ini="addopts="

`sys.path` needs two entries the agentic-mbse venv doesn't carry by default: this repo's `src/`
(so `sysml_codegen` itself is importable) and `teax/packages/teax-simkit` (so `simkit` is
importable — real TEAx, not a stub). Both are inserted here, once, defensively — harmless if
already present (e.g. a normal codegen-venv run that got here via explicit `-m execution`).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_SRC = Path(__file__).resolve().parents[2] / "src"
_TEAX_SIMKIT = Path("/home/reid/1cfe/teax/packages/teax-simkit")

for _p in (_REPO_SRC, _TEAX_SIMKIT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
