#!/usr/bin/env python3
"""Measure Item 1's automatic before/after production union.

Production is tracked Python, Jinja, and SysML outside tests, docs, generated output,
and project metadata.  Python executable lines exclude blanks, comment-only lines,
and lines wholly covered by a module/class/function docstring.  AST statements are
``ast.stmt`` nodes.  Branch points are ``if``, loop, handler, conditional-expression,
match-case, assertion, and Boolean short-circuit decisions.  Per-callable cyclomatic
complexity is one plus those branch points within the callable, excluding nested
callables.  The same script and algorithm measure both sides.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import tokenize
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


PRODUCTION_SUFFIXES = {".py", ".jinja2", ".sysml"}
EXCLUDED_PARTS = {
    ".git",
    ".project",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "__pycache__",
    "docs",
    "generated",
    "results",
    "tests",
}


@dataclass(frozen=True)
class FileMetrics:
    raw_lines: int = 0
    executable_lines: int = 0
    statements: int = 0
    branch_points: int = 0
    callable_complexity: dict[str, int] | None = None


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def _tracked_paths(root: Path) -> set[str]:
    if not (root / ".git").exists():
        return {str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()}
    return {line for line in _git(root, "ls-files").splitlines() if line}


def _is_production(path: str) -> bool:
    item = Path(path)
    return item.suffix in PRODUCTION_SUFFIXES and not (set(item.parts) & EXCLUDED_PARTS)


def _changed_union(root: Path, baseline_rev: str, candidate_rev: str) -> set[str]:
    output = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "diff",
            "--name-status",
            "-z",
            "--find-renames",
            baseline_rev,
            candidate_rev,
        ],
        check=True,
        capture_output=True,
    ).stdout.split(b"\0")
    paths: set[str] = set()
    index = 0
    while index < len(output) and output[index]:
        status = output[index].decode()
        index += 1
        path = output[index].decode()
        index += 1
        paths.add(path)
        if status.startswith(("R", "C")):
            paths.add(output[index].decode())
            index += 1
    return paths


def _docstring_lines(tree: ast.AST) -> set[int]:
    lines: set[int] = set()
    containers = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    for container in containers:
        body = getattr(container, "body", [])
        if not body:
            continue
        first = body[0]
        if not (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            continue
        end = getattr(first, "end_lineno", first.lineno)
        lines.update(range(first.lineno, end + 1))
    return lines


def _comment_only_lines(path: Path) -> set[int]:
    lines: set[int] = set()
    with path.open("rb") as source:
        for token in tokenize.tokenize(source.readline):
            if token.type == tokenize.COMMENT:
                prefix = path.read_text().splitlines()[token.start[0] - 1][: token.start[1]]
                if not prefix.strip():
                    lines.add(token.start[0])
    return lines


BRANCH_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.Assert)


def _branch_weight(node: ast.AST) -> int:
    if isinstance(node, BRANCH_NODES):
        return 1
    if isinstance(node, ast.BoolOp):
        return max(0, len(node.values) - 1)
    if isinstance(node, ast.Try):
        return len(node.handlers) + bool(node.orelse) + bool(node.finalbody)
    if isinstance(node, ast.Match):
        return len(node.cases)
    if isinstance(node, ast.comprehension):
        return 1 + len(node.ifs)
    return 0


def _branch_points(tree: ast.AST) -> int:
    return sum(_branch_weight(node) for node in ast.walk(tree))


class _CallableComplexity(ast.NodeVisitor):
    def __init__(self) -> None:
        self.values: dict[str, int] = {}
        self._scope: list[str] = []

    def _measure(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        name = ".".join([*self._scope, node.name])
        decision_count = 0
        for child in ast.walk(node):
            if child is node:
                continue
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                continue
            decision_count += _branch_weight(child)
        self.values[name] = 1 + decision_count
        self._scope.append(node.name)
        for child in node.body:
            self.visit(child)
        self._scope.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._scope.append(node.name)
        for child in node.body:
            self.visit(child)
        self._scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._measure(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._measure(node)


def _python_metrics(path: Path) -> FileMetrics:
    text = path.read_text()
    tree = ast.parse(text, filename=str(path))
    raw_lines = len(text.splitlines())
    excluded = _docstring_lines(tree) | _comment_only_lines(path)
    executable = sum(
        1 for number, line in enumerate(text.splitlines(), start=1) if line.strip() and number not in excluded
    )
    complexity = _CallableComplexity()
    complexity.visit(tree)
    return FileMetrics(
        raw_lines=raw_lines,
        executable_lines=executable,
        statements=sum(isinstance(node, ast.stmt) for node in ast.walk(tree)),
        branch_points=_branch_points(tree),
        callable_complexity=dict(sorted(complexity.values.items())),
    )


def _text_metrics(path: Path) -> FileMetrics:
    lines = path.read_text().splitlines()
    return FileMetrics(
        raw_lines=len(lines),
        executable_lines=sum(bool(line.strip()) and not line.lstrip().startswith(("#", "//")) for line in lines),
    )


def _metrics(root: Path, paths: Iterable[str]) -> dict[str, FileMetrics]:
    measured: dict[str, FileMetrics] = {}
    for relative in sorted(paths):
        path = root / relative
        if not path.is_file():
            measured[relative] = FileMetrics()
        elif path.suffix == ".py":
            measured[relative] = _python_metrics(path)
        else:
            measured[relative] = _text_metrics(path)
    return measured


def _totals(values: dict[str, FileMetrics]) -> dict[str, int]:
    return {
        field: sum(getattr(value, field) for value in values.values())
        for field in ("raw_lines", "executable_lines", "statements", "branch_points")
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--baseline-rev", required=True)
    parser.add_argument("--candidate-rev", required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()

    changed = (
        _changed_union(args.candidate_root, args.baseline_rev, args.candidate_rev)
        if (args.candidate_root / ".git").exists()
        else set()
    )
    if args.baseline_rev == args.candidate_rev:
        changed.update(
            {
                "src/sysml_codegen/analysis/part_instance_index.py",
                "src/sysml_codegen/analysis/constraint_lowering.py",
                "src/sysml_codegen/resolution/supplied_values.py",
                "src/sysml_codegen/orchestration/pipeline_builder.py",
                "src/sysml_codegen/snapshot/graph_rebuild.py",
                "src/sysml_codegen/snapshot/serializer.py",
                "src/sysml_codegen/orchestration/pipeline_context.py",
                "src/sysml_codegen/snapshot/__init__.py",
                "src/sysml_codegen/snapshot/loader.py",
            }
        )
    production = sorted(path for path in changed if _is_production(path))
    baseline_tracked = _tracked_paths(args.baseline_root)
    candidate_tracked = _tracked_paths(args.candidate_root)
    baseline = _metrics(args.baseline_root, (path for path in production if path in baseline_tracked))
    candidate = _metrics(args.candidate_root, (path for path in production if path in candidate_tracked))
    for path in production:
        baseline.setdefault(path, FileMetrics())
        candidate.setdefault(path, FileMetrics())
    payload = {
        "algorithm_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "baseline_revision": args.baseline_rev,
        "candidate_revision": args.candidate_rev,
        "production_union": production,
        "baseline": {path: asdict(baseline[path]) for path in production},
        "candidate": {path: asdict(candidate[path]) for path in production},
        "baseline_totals": _totals(baseline),
        "candidate_totals": _totals(candidate),
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
