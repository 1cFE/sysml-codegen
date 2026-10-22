#!/usr/bin/env python3
"""Record or compare every package ``generate`` writes (EXEC-SUBSET-CONTRACT Item 2b, D15).

The byte-identity check every 2b refactor phase runs. For every 2a case the generator builds,
every committed v6 snapshot replayed, and each snapshot's sources live where they are
present, it calls ``run_codegen(GenerationConfig(...))`` with default options into a fresh
folder and records the outcome and relative path → sha256 for every file written.

Nothing is normalized: at the base, two runs into different folders give identical bytes
(Phase 0's double-run check).

Usage (licensed; source the license first)::

    uv run --all-extras python scripts/package_manifest.py record OUT.json
    uv run --all-extras python scripts/package_manifest.py compare BASE.json

``compare`` re-records into a temporary folder and exits 1 naming every subject whose
outcome differs and every file that differs, was added, or was removed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _generate_corpus as corpus  # noqa: E402


def _tree(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def record(work: Path) -> dict[str, Any]:
    from sysml_codegen.cli import run_codegen

    corpus.quiet()
    subjects = [*corpus.case_subjects("generated"), *corpus.snapshot_subjects()]
    packages: dict[str, Any] = {}
    for number, subject in enumerate(subjects):
        output = work / f"{number:03d}" / "pkg"
        generated = run_codegen(corpus.config_for(subject, output))
        packages[subject.key] = {"generated": generated, "files": _tree(output)}
    return {
        "schema": "package-manifest/1",
        "missing_sources": corpus.missing_sources(),
        "packages": packages,
    }


def differences(base: dict[str, Any], now: dict[str, Any]) -> list[str]:
    found: list[str] = []
    if base["missing_sources"] != now["missing_sources"]:
        found.append(f"missing sources: {base['missing_sources']} -> {now['missing_sources']}")
    for key in sorted(base["packages"].keys() | now["packages"].keys()):
        if key not in now["packages"]:
            found.append(f"{key}: subject removed")
            continue
        if key not in base["packages"]:
            found.append(f"{key}: subject added")
            continue
        was, is_ = base["packages"][key], now["packages"][key]
        if was["generated"] != is_["generated"]:
            found.append(f"{key}: generated {was['generated']} -> {is_['generated']}")
        for path in sorted(was["files"].keys() | is_["files"].keys()):
            if path not in is_["files"]:
                found.append(f"{key}: removed {path}")
            elif path not in was["files"]:
                found.append(f"{key}: added {path}")
            elif was["files"][path] != is_["files"][path]:
                found.append(f"{key}: differs {path}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("out", type=Path)
    cmp = sub.add_parser("compare")
    cmp.add_argument("base", type=Path)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="package-manifest-") as work:
        manifest = record(Path(work))
    if args.command == "record":
        args.out.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
        built = sum(p["generated"] for p in manifest["packages"].values())
        print(f"recorded {len(manifest['packages'])} subjects ({built} generated) to {args.out}")
        return 0
    found = differences(json.loads(args.base.read_text()), manifest)
    for line in found:
        print(line)
    print(f"{len(found)} differences against {args.base}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
