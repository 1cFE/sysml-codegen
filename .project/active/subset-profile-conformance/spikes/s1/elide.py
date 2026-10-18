"""Spike S1 (throwaway): elide one refusal site, chosen by scanner site ID, in-process.

Method: find the site with Item 1's scanner (run on the live source of the imported
packages), find the innermost statement that contains it, require that statement to be a
`raise`, and replace it with `pass`. Recompile the outermost function that owns the site
(module function, or method directly in a class body; a nested function is recompiled
through its outer function) and swap the new code object into the *existing* function
object (`fn.__code__ = new`). Because the function object keeps its identity, every module
that imported it by name, every bound method and every table holding it sees the change, so
no re-binding is needed. `restore()` swaps the original code back.
"""

from __future__ import annotations

import __future__
import ast
import contextlib
import importlib
import inspect
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from types import CodeType, FunctionType

SCANNER_DIR = Path("/home/reid/src/subset-conformance/agentic-mbse/scripts/subset_profile")
sys.path.insert(0, str(SCANNER_DIR))

import scan_sites  # noqa: E402


def _package_src(name: str) -> Path:
    return Path(importlib.import_module(name).__file__).resolve().parents[1]


_ROWS: dict[str, dict[str, str]] | None = None


def site_rows() -> dict[str, dict[str, str]]:
    global _ROWS
    if _ROWS is None:
        rows = scan_sites.scan_sources(_package_src("sysml_codegen"), _package_src("agentic_mbse"))
        _ROWS = {r["site_id"]: r for r in rows}
    return _ROWS


class ElisionError(RuntimeError):
    pass


@dataclass
class Elision:
    site_id: str
    target: FunctionType
    original: CodeType
    replacement: CodeType
    statement: str

    def restore(self) -> None:
        self.target.__code__ = self.original


def _module_name(rel: str) -> str:
    return rel.removesuffix(".py").replace("/", ".")


def _innermost_statement(tree: ast.AST, line: int) -> tuple[list[ast.AST], ast.stmt]:
    """Path of enclosing nodes and the innermost statement whose span contains `line`."""
    best: tuple[list[ast.AST], ast.stmt] | None = None

    def walk(node: ast.AST, path: list[ast.AST]) -> None:
        nonlocal best
        for child in ast.iter_child_nodes(node):
            if not hasattr(child, "lineno"):
                continue
            if not (child.lineno <= line <= child.end_lineno):
                continue
            if isinstance(child, ast.stmt):
                best = (path + [child], child)
            walk(child, path + [child])

    walk(tree, [])
    if best is None:
        raise ElisionError(f"no statement at line {line}")
    return best


def _resolve_owner(module, qual: list[str]) -> tuple[FunctionType, ast.AST | None]:
    """The runtime function object for the outermost def in `qual` (function or class.method)."""
    obj = module
    for i, part in enumerate(qual):
        holder = obj
        obj = holder.__dict__[part] if hasattr(holder, "__dict__") else getattr(holder, part)
        raw = obj
        if isinstance(raw, (staticmethod, classmethod)):
            raw = raw.__func__
        if isinstance(raw, property):
            raw = raw.fget
        raw = inspect.unwrap(raw) if callable(raw) else raw
        if isinstance(raw, FunctionType):
            return raw, i
        obj = raw
    raise ElisionError(f"no function found along {qual}")


def elide(site_id: str, generalized: bool = False) -> Elision:
    row = site_rows().get(site_id)
    if row is None:
        raise ElisionError(f"unknown site id {site_id}")
    rel, line = row["file"], int(row["line"])
    module = importlib.import_module(_module_name(rel))
    path = Path(module.__file__)
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    enclosing, stmt = _innermost_statement(tree, line)
    replacement = _neutral(stmt, generalized)
    if replacement is None:
        raise ElisionError(
            f"{site_id}: site statement is {type(stmt).__name__}, not Raise: "
            f"{ast.unparse(stmt)[:120]!r}"
        )
    qual = row["function"].split(".")
    fn, depth = _resolve_owner(module, qual)
    # The AST def matching the runtime outer function.
    defs = [n for n in enclosing if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    outer_def = next(d for d in defs if d.name == fn.__name__)
    # Replace the raise inside outer_def with pass (same node object, so mutate in place).
    replaced = False
    for parent in ast.walk(outer_def):
        for field, value in ast.iter_fields(parent):
            if isinstance(value, list) and stmt in value:
                value[value.index(stmt)] = ast.copy_location(replacement, stmt)
                replaced = True
    if not replaced:
        raise ElisionError(f"{site_id}: raise not found under {fn.__qualname__}")
    stripped = ast.FunctionDef(**{f: getattr(outer_def, f) for f in outer_def._fields})
    stripped.decorator_list = []  # decorators already applied to the live object
    body: ast.stmt = stripped
    if "__class__" in fn.__code__.co_freevars:  # zero-arg super(): compile inside a class
        body = ast.ClassDef(name="_Spike", bases=[], keywords=[], body=[stripped], decorator_list=[])
    mod_ast = ast.fix_missing_locations(ast.Module(body=[body], type_ignores=[]))
    flags = 0
    if "annotations" in module.__dict__ and module.__dict__["annotations"] is __future__.annotations:
        flags |= __future__.annotations.compiler_flag
    code = compile(mod_ast, str(path), "exec", flags=flags, dont_inherit=True)
    new_code = _find_code(code, fn.__code__.co_name, outer_def.lineno)
    if new_code.co_freevars != fn.__code__.co_freevars:
        raise ElisionError(f"{site_id}: free variables differ {new_code.co_freevars}")
    original = fn.__code__
    fn.__code__ = new_code
    return Elision(site_id, fn, original, new_code, ast.unparse(stmt).splitlines()[0])


def _neutral(stmt: ast.stmt, generalized: bool) -> ast.stmt | None:
    """The no-refusal stand-in for the statement that emits a site, or None if there is none.

    Strict (D5 as written): only `raise X` -> `pass`. Generalized: also a bare call statement
    that records a finding (`self._diagnose(...)`, `findings.append(...)`) -> `pass`, and
    `return [finding]` -> `return []`.
    """
    if isinstance(stmt, ast.Raise):
        return ast.Pass()
    if not generalized:
        return None
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        return ast.Pass()
    if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.List):
        return ast.Return(value=ast.List(elts=[], ctx=ast.Load()))
    return None


def _find_code(code: CodeType, name: str, lineno: int) -> CodeType:
    for const in code.co_consts:
        if isinstance(const, CodeType):
            if const.co_name == name:
                return const
            with contextlib.suppress(LookupError):
                return _find_code(const, name, lineno)
    raise LookupError(name)


@contextlib.contextmanager
def elided(site_id: str, generalized: bool = False) -> Iterator[Elision]:
    e = elide(site_id, generalized)
    try:
        yield e
    finally:
        e.restore()
