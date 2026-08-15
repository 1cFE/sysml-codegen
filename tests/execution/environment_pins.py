"""Where the acceptance evidence must resolve from, as a checkable predicate.

The execution lane pins its import resolution so acceptance evidence cannot be silently
produced against the wrong tree: ``simkit`` from the pinned TEAx checkout, and both
project packages from the main checkouts — this repo and the ``agentic-mbse`` checkout
beside it. The expected roots are derived from this file's own location, never written
as host paths: hardcoded absolute paths are what broke this pin when the rebuild
worktrees were deleted (2026-08-15).

The predicate is pure and stdlib-only so the default (non-execution) suite can feed it
wrong resolutions and prove it still rejects them. A pin that can no longer fail is the
defect, not a repair.
"""

from __future__ import annotations

from pathlib import Path

#: This repo's ``src`` tree — the only place ``sysml_codegen`` may resolve from. A copy
#: installed into a venv's site-packages is a stale tree, not this one.
CODEGEN_SRC = Path(__file__).resolve().parents[2] / "src"

#: The companion checkout beside this repo. Its ``main`` carries the retirement content;
#: no other resolution is the tree under test.
COMPANION_SRC = Path(__file__).resolve().parents[3] / "agentic-mbse" / "src"


def environment_pin_problems(resolved: dict[str, str]) -> list[str]:
    """One problem per import that resolved outside its pinned tree."""
    problems: list[str] = []
    if "/teax/packages/teax-simkit/" not in resolved["simkit"]:
        problems.append(
            f"simkit resolved outside the pinned TEAx checkout: {resolved['simkit']}"
        )
    for name, root in (("sysml_codegen", CODEGEN_SRC), ("agentic_mbse", COMPANION_SRC)):
        if not Path(resolved[name]).resolve().is_relative_to(root):
            problems.append(f"{name} resolved outside {root}: {resolved[name]}")
    return problems
