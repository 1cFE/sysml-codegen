"""Require two generated trees to have identical paths, kinds, links, and bytes."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def manifest(root: Path) -> list[tuple[str, str, bytes | str | None]]:
    records: list[tuple[str, str, bytes | str | None]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            records.append((relative, "symlink", os.readlink(path)))
        elif path.is_dir():
            records.append((relative, "directory", None))
        else:
            records.append((relative, "file", path.read_bytes()))
    return records


if __name__ == "__main__":
    left, right = (Path(argument) for argument in sys.argv[1:3])
    if manifest(left) != manifest(right):
        raise SystemExit("generated tree manifests differ")
    print(f"byte-identical: {left} == {right}")
