"""Throwaway (design stage, Item 5): build scratch copies of catf_mfe_d5 for probes.

Not a committed fixture and not a test. Copies land under /tmp; nothing here is authority.
"""

from __future__ import annotations

import os
import shutil
import sys

SRC = "/home/reid/1cfe/sysml-codegen-item7-rebuild/tests/fixtures/catf_mfe_d5"
ROOT = "/tmp/item5probe"


def fresh(name: str) -> str:
    dst = os.path.join(ROOT, name)
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(SRC, dst)
    for f in ("instance_graph_snapshot.json", "PROVENANCE.md"):
        p = os.path.join(dst, f)
        if os.path.exists(p):
            os.remove(p)
    return dst


if __name__ == "__main__":
    for n in sys.argv[1:] or ["p1"]:
        print(fresh(n))
