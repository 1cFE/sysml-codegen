"""Capture fusion-tea's compatibility surface from the staged b06585709 modules (SC6).

Run once, from the worktree root, with this worktree's interpreter:

    .venv/bin/python .project/active/study-layer-to-codegen/evidence/compat/capture_compat_surface.py

It imports the staged ``scripts/study/*.py`` and ``scripts/integrate.py`` from
``.orchestrate-logs/src/fusion-tea@b06585709/`` as the namespace packages they were, describes
each name ``tests/study/test_compat_surface.py`` lists with that test's own ``describe``, and
writes ``tests/study/data/compat_surface.json``. Using the test's recipe means the table and
the check cannot disagree about what a shape is.

It refuses if the staged tree is not at ``b06585709`` or if any listed name is missing there.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[5]
STAGED = WORKTREE / ".orchestrate-logs" / "src" / "fusion-tea@b06585709"
OUT = WORKTREE / "tests" / "study" / "data" / "compat_surface.json"
COMMIT = "b06585709"

#: Where each module the test names lived before the move.
STAGED_MODULES = {
    "common": "scripts.study.common",
    "identity": "scripts.study.identity",
    "indicators": "scripts.study.indicators",
    "integrate": "scripts.integrate",
    "manifest": "scripts.study.manifest",
    "verify": "scripts.study.verify",
}


def main() -> int:
    # SOURCE_COMMIT reads "fusion-tea origin/main = <sha>".
    source_commit = (STAGED / "SOURCE_COMMIT").read_text().strip()
    if not source_commit.endswith(f"= {COMMIT}"):
        print(f"refusing: the staged tree is at {source_commit}, not {COMMIT}", file=sys.stderr)
        return 1
    sys.path.insert(0, str(WORKTREE))
    from tests.study.test_compat_surface import SURFACE, describe

    sys.path.insert(0, str(STAGED))
    names = {}
    for module_name, attributes in sorted(SURFACE.items()):
        module = importlib.import_module(STAGED_MODULES[module_name])
        if not str(Path(module.__file__ or "").resolve()).startswith(str(STAGED)):
            print(f"refusing: {module.__name__} imported from {module.__file__}", file=sys.stderr)
            return 1
        for attribute in attributes:
            if not hasattr(module, attribute):
                print(f"refusing: {module.__name__} has no {attribute}", file=sys.stderr)
                return 1
            names[f"{module_name}.{attribute}"] = describe(getattr(module, attribute))
    table = {
        "source": f"fusion-tea {COMMIT}: scripts/study/*.py and scripts/integrate.py",
        "captured_by": (
            ".project/active/study-layer-to-codegen/evidence/compat/capture_compat_surface.py"
        ),
        "names": dict(sorted(names.items())),
    }
    OUT.write_text(json.dumps(table, indent=2) + "\n")
    print(f"wrote {len(names)} names to {OUT.relative_to(WORKTREE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
