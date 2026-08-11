#!/usr/bin/env python3
"""Find executable cutover residue without matching this oracle's encoded vocabulary."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections.abc import Iterable
from pathlib import Path


def _word(*values: int) -> str:
    return "".join(chr(value) for value in values)


_ALL = (
    (
        98,
        117,
        105,
        108,
        100,
        95,
        101,
        108,
        97,
        98,
        111,
        114,
        97,
        116,
        101,
        100,
        95,
        112,
        105,
        112,
        101,
        108,
        105,
        110,
        101,
    ),
    (
        68,
        101,
        112,
        101,
        110,
        100,
        101,
        110,
        99,
        121,
        66,
        97,
        99,
        107,
        116,
        114,
        97,
        99,
        107,
        101,
        114,
    ),
    (79, 117, 116, 112, 117, 116, 82, 101, 103, 105, 115, 116, 114, 121),
    (
        98,
        117,
        105,
        108,
        100,
        95,
        111,
        117,
        116,
        112,
        117,
        116,
        95,
        114,
        101,
        103,
        105,
        115,
        116,
        114,
        121,
    ),
    (
        98,
        117,
        105,
        108,
        100,
        95,
        99,
        111,
        109,
        112,
        117,
        116,
        97,
        116,
        105,
        111,
        110,
        95,
        103,
        114,
        97,
        112,
        104,
    ),
    (
        99,
        111,
        108,
        108,
        101,
        99,
        116,
        95,
        117,
        110,
        99,
        111,
        118,
        101,
        114,
        101,
        100,
        95,
        112,
        97,
        114,
        97,
        109,
        115,
    ),
    (80, 97, 114, 116, 73, 110, 115, 116, 97, 110, 99, 101, 73, 110, 100, 101, 120),
    (80, 97, 116, 104, 83, 116, 101, 112),
    (73, 110, 115, 116, 97, 110, 99, 101, 79, 99, 99, 117, 114, 114, 101, 110, 99, 101),
    (
        114,
        101,
        119,
        114,
        105,
        116,
        101,
        95,
        118,
        105,
        114,
        116,
        117,
        97,
        108,
        95,
        98,
        105,
        110,
        100,
        105,
        110,
        103,
        115,
    ),
    (
        95,
        114,
        101,
        115,
        99,
        117,
        101,
        95,
        115,
        101,
        108,
        102,
        95,
        110,
        97,
        109,
        101,
        100,
        95,
        98,
        105,
        110,
        100,
        105,
        110,
        103,
        115,
    ),
    (112, 114, 111, 100, 117, 99, 101, 114, 95, 114, 101, 115, 111, 108, 117, 116, 105, 111, 110),
    (
        112,
        114,
        111,
        100,
        117,
        99,
        101,
        114,
        95,
        99,
        111,
        109,
        112,
        108,
        101,
        116,
        101,
        110,
        101,
        115,
        115,
    ),
    (115, 117, 112, 112, 108, 105, 101, 100, 95, 118, 97, 108, 117, 101, 115),
    (
        99,
        111,
        110,
        115,
        116,
        114,
        97,
        105,
        110,
        116,
        95,
        108,
        111,
        119,
        101,
        114,
        105,
        110,
        103,
        95,
        109,
        111,
        100,
        101,
    ),
    (
        108,
        111,
        97,
        100,
        95,
        101,
        120,
        116,
        114,
        97,
        99,
        116,
        105,
        111,
        110,
        95,
        115,
        110,
        97,
        112,
        115,
        104,
        111,
        116,
    ),
    (
        115,
        101,
        114,
        105,
        97,
        108,
        105,
        122,
        101,
        95,
        101,
        120,
        116,
        114,
        97,
        99,
        116,
        105,
        111,
        110,
        95,
        115,
        110,
        97,
        112,
        115,
        104,
        111,
        116,
    ),
    (
        98,
        117,
        105,
        108,
        100,
        95,
        102,
        117,
        108,
        108,
        95,
        103,
        114,
        97,
        112,
        104,
        95,
        102,
        114,
        111,
        109,
        95,
        115,
        110,
        97,
        112,
        115,
        104,
        111,
        116,
    ),
    (
        101,
        118,
        97,
        108,
        117,
        97,
        116,
        101,
        95,
        105,
        100,
        101,
        110,
        116,
        105,
        102,
        105,
        101,
        100,
        95,
        112,
        114,
        111,
        102,
        105,
        108,
        101,
    ),
    (
        101,
        120,
        116,
        114,
        97,
        99,
        116,
        95,
        105,
        100,
        101,
        110,
        116,
        105,
        102,
        105,
        101,
        100,
        95,
        99,
        111,
        110,
        115,
        116,
        114,
        97,
        105,
        110,
        116,
        95,
        102,
        97,
        99,
        116,
        115,
    ),
    (95, 101, 118, 97, 108, 117, 97, 116, 101, 95, 117, 115, 97, 103, 101),
    (
        99,
        111,
        109,
        112,
        105,
        108,
        101,
        95,
        99,
        97,
        108,
        99,
        95,
        100,
        101,
        102,
        95,
        101,
        120,
        97,
        99,
        116,
    ),
    (
        71,
        114,
        97,
        110,
        100,
        102,
        97,
        116,
        104,
        101,
        114,
        101,
        100,
        83,
        110,
        97,
        112,
        115,
        104,
        111,
        116,
        69,
        114,
        114,
        111,
        114,
    ),
)
_DUAL_2 = (_ALL[18], _ALL[20])
RULES = {"all": _ALL, "item6-dual-2": _DUAL_2}
SKIP_PARTS = {
    ".git",
    ".mypy_cache",
    ".orchestrate-logs",
    ".project",
    ".pytest_cache",
    ".venv",
    "__pycache__",
}
SELF_NAMES = {"check_cutover_residue.py", "test_check_cutover_residue.py"}


class ResidueError(ValueError):
    pass


def _parse_repos(values: list[str]) -> dict[str, Path]:
    repos: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ResidueError(f"invalid --repo {value!r}")
        name, raw_path = value.split("=", 1)
        path = Path(raw_path).resolve()
        if not name or name in repos or not path.is_dir():
            raise ResidueError(f"invalid repository mapping {value!r}")
        repos[name] = path
    return repos


def _python_symbols(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text())
    except (OSError, UnicodeDecodeError, SyntaxError):
        return set()
    values: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            values.add(node.id)
        elif isinstance(node, ast.Attribute):
            values.add(node.attr)
        elif isinstance(node, ast.Import):
            values.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            values.add(node.module)
            values.update(alias.name for alias in node.names)
    return values


def _paths(repo: Path) -> Iterable[Path]:
    for path in repo.rglob("*"):
        relative = path.relative_to(repo)
        if not path.is_file() or any(part in SKIP_PARTS for part in relative.parts):
            continue
        if path.name in SELF_NAMES or path.stat().st_size > 4_000_000:
            continue
        yield path


def _hits(repos: dict[str, Path], encoded: tuple[tuple[int, ...], ...]) -> list[dict[str, str]]:
    banned = [_word(*values) for values in encoded]
    hits: list[dict[str, str]] = []
    for repo_name, repo in sorted(repos.items()):
        for path in _paths(repo):
            relative = path.relative_to(repo).as_posix()
            if path.suffix == ".py":
                symbols = _python_symbols(path)
                matched = sorted(
                    item
                    for item in banned
                    if any(item == value or item in value.split(".") for value in symbols)
                )
            else:
                try:
                    text = path.read_text()
                except (OSError, UnicodeDecodeError):
                    continue
                matched = sorted(item for item in banned if item in text)
            hits.extend({"repo": repo_name, "path": relative, "symbol": item} for item in matched)
    return sorted(hits, key=lambda item: (item["repo"], item["path"], item["symbol"]))


def _inventory_rows(path: Path) -> dict[tuple[str, str], list[dict[str, object]]]:
    document = json.loads(path.read_text())
    if document.get("schema") != "cutover-inventory/v1":
        raise ResidueError("invalid inventory schema")
    result: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in document.get("rows", []):
        result.setdefault((row.get("repo"), row.get("path")), []).append(row)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", action="append", required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--rule", choices=sorted(RULES), required=True)
    parser.add_argument("--expect", choices=("absent", "inventoried"), required=True)
    args = parser.parse_args()
    try:
        hits = _hits(_parse_repos(args.repo), RULES[args.rule])
        if args.expect == "absent" and hits:
            raise ResidueError("residue remains: " + json.dumps(hits, sort_keys=True))
        if args.expect == "inventoried":
            inventory = _inventory_rows(args.inventory)
            missing = [
                hit
                for hit in hits
                if not any(
                    row.get("status") == "existing"
                    and row.get("disposition") in {"delete", "migrate"}
                    for row in inventory.get((hit["repo"], hit["path"]), [])
                )
            ]
            if missing:
                raise ResidueError("uninventoried residue: " + json.dumps(missing, sort_keys=True))
        print(
            json.dumps(
                {"expect": args.expect, "hits": len(hits), "rule": args.rule}, sort_keys=True
            )
        )
    except (ResidueError, OSError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
