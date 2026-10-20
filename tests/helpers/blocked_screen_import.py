"""Run the ``sysml-codegen`` CLI with agentic-mbse's subset screen unimportable (Item 2b).

``python -m tests.helpers.blocked_screen_import <cli arguments>`` installs a meta-path finder
that fails every import of ``agentic_mbse.sysml.subset_profile``, the screen's vocabulary
module, then runs the CLI as its console script does. It runs in a fresh interpreter, so
nothing has imported the module beforehand. The import fails for real: every module that
imports it, the screen's extractor and codegen's adapter included, fails with it.
"""

from __future__ import annotations

import sys
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType

BLOCKED = "agentic_mbse.sysml.subset_profile"


class _Blocked(MetaPathFinder):
    def find_spec(
        self,
        fullname: str,
        path: object = None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        if fullname == BLOCKED:
            raise ModuleNotFoundError(f"No module named {fullname!r} (blocked)", name=fullname)
        return None


if __name__ == "__main__":
    sys.meta_path.insert(0, _Blocked())
    from sysml_codegen.cli import main

    sys.argv = ["sysml-codegen", *sys.argv[1:]]
    main()
