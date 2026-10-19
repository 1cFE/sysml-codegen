"""Turn off one detector, in-process, and see which cases notice (Item 2a design D5, § B).

A ``Target`` is one statement: the one holding a line in a named function. A scanned site
becomes one through ``site_target(site_id)``. Three tools act on targets or rules:

- ``recording_fired(targets)`` records which targets a run reaches. A target fires when a
  line of its statement runs, seen through ``sys.monitoring`` line events on the code of the
  function that owns it and nothing else. A witness is a case that fires its site.
- ``rewritten(target, rewrites)`` runs a block with statements replaced. ``neutral(target)``
  is the rewrite that stops a statement refusing: ``raise …`` and a recorder call become
  ``pass``, ``return [x]`` becomes ``return []``. Four sites need a named rewrite instead
  (``HAND_PATCHES``); ``neutralize(site_id)`` picks one or the other. The owning top-level
  function or method is recompiled from the live source and its new code is assigned to the
  existing function's ``__code__``, so every by-name import sees the change; the original
  code comes back on exit. A function behind a caching wrapper is refused, because a cached
  result would hide the change.
- ``disable_recognizer(rule, shape)`` makes one rule of the screen stop recognizing one
  shape, by filtering that shape's recognitions out of the rule's function in
  ``subset_profile._RULES``.

Only a run that executes a site's statement can change under its mutation: the recompiled
function is the original but for that one statement. So the cases a mutation can flip are
among the cases that fire the site, and the mutation tests run only those.

``SHARED`` tags the agentic-mbse sites both halves run (design § Independence limits): their
mutations move the generator and the screen together, so they show drift at the site, not
that the two sides agree on their own.

Every private name the helpers patch or rely on, in either repo, is in ``PATCHED_NAMES``, so a
rename fails by name in ``test_mutator.py``.
"""

from __future__ import annotations
import __future__

import ast
import dataclasses
import functools
import importlib
import inspect
import sys
from collections.abc import Callable, Iterable, Iterator, Mapping
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import CodeType, FunctionType, ModuleType
from typing import Any

from tests.helpers.subset_profile import site_scan
from tests.helpers.subset_profile.site_scan import Site

#: ``(module, dotted attribute path)`` of every private name this module or ``observe.py``
#: patches or names in a rewrite.
PATCHED_NAMES: tuple[tuple[str, str], ...] = (
    ("agentic_mbse.sysml.executable_profile", "_evaluate_usage_against_definition"),
    ("agentic_mbse.sysml.executable_profile", "_unassessed"),
    ("agentic_mbse.sysml.subset_profile", "_RULES"),
    ("agentic_mbse.sysml.subset_profile", "_Recognized"),
    ("sysml_codegen.elaboration.expression_evidence", "_indexed_refusal"),
    ("sysml_codegen.elaboration.expression_evidence", "_acquire"),
    ("sysml_codegen.elaboration.project", "_Projection._entry_source"),
)

_PROFILE = "agentic_mbse/sysml/executable_profile.py::_evaluate_usage_against_definition"
_REFERENCE_USE = "agentic_mbse/sysml/reference_use.py"
_INDEXED = (
    "sysml_codegen/elaboration/expression_evidence.py::_indexed_refusal::coded"
    "::INDEXED_REFERENCE_UNSUPPORTED::1"
)

#: The agentic-mbse sites the generator mutation test neutralizes (plan PD6). The 19 walker
#: sites in ``executable_profile.py`` and the table ``invocation_allowlist.py`` are not here.
SHARED: frozenset[str] = frozenset(
    {
        f"{_PROFILE}::shared-profile::block_assert_by_reference::1",
        f"{_PROFILE}::shared-profile::block_unresolved_definition::1",
        f"{_PROFILE}::shared-profile::block_missing_predicate::1",
        f"{_REFERENCE_USE}::_require_supported_invocation::shared-evidence"
        "::EXPRESSION_KIND_UNSUPPORTED::1",
        f"{_REFERENCE_USE}::_reference_use::shared-evidence::RESOLVED_TARGET_MISSING::1",
        f"{_REFERENCE_USE}::require_exact_reference_use::shared-evidence"
        "::INDEXED_REFERENCE_UNSUPPORTED::1",
    }
)


class MutationError(RuntimeError):
    """A site cannot be traced or neutralized as asked."""


@dataclass(frozen=True)
class Rewrite:
    """Replace one statement of ``function`` in the site's module with ``replacement``.

    ``statement`` is the target's ``ast.unparse`` text; ``None`` means the site's own statement.
    """

    function: str
    statement: str | None
    replacement: str


#: The sites a plain rewrite cannot neutralize (design D5). The three profile returns build a
#: blocking decision; the hand patch returns the decision the function gives a usage it does
#: not assess. ``_indexed_refusal`` returns its refusal; both callers raise it.
HAND_PATCHES: dict[str, tuple[Rewrite, ...]] = {
    **{
        f"{_PROFILE}::shared-profile::{reason}::1": (
            Rewrite("_evaluate_usage_against_definition", None, "return _unassessed(usage, form)"),
        )
        for reason in (
            "block_assert_by_reference",
            "block_unresolved_definition",
            "block_missing_predicate",
        )
    },
    _INDEXED: (
        Rewrite("require_exact_use", "raise _indexed_refusal(value)", "pass"),
        Rewrite("_acquire", "raise _indexed_refusal(use)", "pass"),
    ),
}


# ---- locating a statement ---------------------------------------------------------------------


@dataclass(frozen=True)
class Target:
    """One statement: the one holding ``line`` inside ``function`` (a dotted qualname)."""

    module: ModuleType
    function: str
    line: int


@functools.cache
def _sites() -> dict[str, Site]:
    return site_scan.scan().by_id()


def site_target(site_id: str) -> Target:
    """Where the scanned site with this ID is, in either repo."""
    found = _sites().get(site_id)
    if found is None:
        raise MutationError(f"no site {site_id!r} in either source tree")
    return Target(importlib.import_module(module_name(found.file)), found.function, found.line)


def module_name(file: str) -> str:
    """The import name of a scanned source file; a package's ``__init__.py`` is the package.

    Importing ``pkg.__init__`` would load a second copy of the package's module, whose
    functions the code under test never calls, so a recorder or rewrite there sees nothing.
    """
    return file.removesuffix(".py").removesuffix("/__init__").replace("/", ".")


def _parse(module: ModuleType) -> tuple[Path, ast.Module]:
    path = Path(inspect.getfile(module))
    return path, ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _def_path(tree: ast.Module, qualname: str) -> list[ast.FunctionDef | ast.ClassDef]:
    """The class and function definitions named by ``qualname``, outermost first."""
    body: list[ast.stmt] = tree.body
    path: list[ast.FunctionDef | ast.ClassDef] = []
    for name in qualname.split("."):
        node = next(
            (n for n in body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name),
            None,
        )
        if node is None:
            raise MutationError(f"no definition {qualname!r} in the module source")
        path.append(node)
        body = node.body
    return path


def _owner(path: list[ast.FunctionDef | ast.ClassDef]) -> tuple[str, ast.FunctionDef]:
    """The qualname and definition of the outermost function along ``path``."""
    for depth, node in enumerate(path):
        if isinstance(node, ast.FunctionDef):
            return ".".join(n.name for n in path[: depth + 1]), node
    raise MutationError(f"{'.'.join(n.name for n in path)} is not inside a function")


def _statements(root: ast.AST) -> Iterator[tuple[list[ast.stmt], ast.stmt]]:
    """Every statement under ``root``, with the body list that holds it."""
    for parent in ast.walk(root):
        for _field, value in ast.iter_fields(parent):
            if isinstance(value, list):
                for child in value:
                    if isinstance(child, ast.stmt):
                        yield value, child


def _innermost(owner: ast.FunctionDef, line: int) -> tuple[list[ast.stmt], ast.stmt]:
    holding = [
        (body, stmt)
        for body, stmt in _statements(owner)
        if stmt.lineno <= line <= (stmt.end_lineno or stmt.lineno)
    ]
    if not holding:
        raise MutationError(f"no statement holds line {line} in {owner.name}")
    return max(holding, key=lambda pair: (pair[1].lineno, -(pair[1].end_lineno or 0)))


def _statement(target: Target) -> tuple[ast.FunctionDef, ast.stmt]:
    _, tree = _parse(target.module)
    _, owner = _owner(_def_path(tree, target.function))
    return owner, _innermost(owner, target.line)[1]


# ---- recording which statements run -----------------------------------------------------------


def _code_tree(code: CodeType) -> Iterator[CodeType]:
    yield code
    for const in code.co_consts:
        if isinstance(const, CodeType):
            yield from _code_tree(const)


def _live_function(module: ModuleType, qualname: str) -> FunctionType:
    """The function object the outermost function along ``qualname`` names at runtime.

    A caching wrapper is refused, because a cached result would hide a change to the code.
    """
    holder: Any = module
    for name in qualname.split("."):
        obj = vars(holder)[name]
        if isinstance(obj, functools.cached_property):
            raise MutationError(f"{qualname} is behind a caching wrapper")
        if isinstance(obj, (staticmethod, classmethod)):
            obj = obj.__func__
        if isinstance(obj, property):
            obj = obj.fget
        while hasattr(obj, "__wrapped__"):
            if hasattr(obj, "cache_clear"):
                raise MutationError(f"{qualname} is behind a caching wrapper")
            obj = obj.__wrapped__
        if isinstance(obj, FunctionType):
            return obj
        holder = obj
    raise MutationError(f"{qualname} names no function")


def _free_tool_id() -> int:
    for tool in range(6):
        if sys.monitoring.get_tool(tool) is None:
            return tool
    raise MutationError("every sys.monitoring tool id is in use")


@functools.cache
def _recordable_lines(target: Target) -> range:
    """The source lines of the target's statement, refused if a line event cannot isolate it.

    Cached, because a recording over every site in every case would otherwise parse each
    module once per site per case; the source does not change during a run.
    """
    owner, stmt = _statement(target)
    if any(s is not stmt and s.lineno == stmt.lineno for _, s in _statements(owner)):
        raise MutationError(
            f"{target.function}, line {target.line}: its statement shares its first line "
            "with another"
        )
    return range(stmt.lineno, (stmt.end_lineno or stmt.lineno) + 1)


@contextmanager
def recording_fired(targets: Mapping[str, Target]) -> Iterator[set[str]]:
    """Record, into the yielded set, the key of each target whose statement runs in the block.

    A statement that shares its first line with an enclosing one (``if x: raise E``) is
    refused: a line event cannot tell the test from the raise.
    """
    watched: dict[CodeType, dict[int, set[str]]] = {}
    for key, target in targets.items():
        statement_lines = _recordable_lines(target)
        function = _live_function(target.module, target.function)
        for code in _code_tree(function.__code__):
            lines = watched.setdefault(code, {})
            for line in statement_lines:
                lines.setdefault(line, set()).add(key)

    fired: set[str] = set()
    tool = _free_tool_id()
    events = sys.monitoring.events

    def on_line(code: CodeType, line: int) -> object:
        fired.update(watched.get(code, {}).get(line, ()))
        return sys.monitoring.DISABLE

    sys.monitoring.use_tool_id(tool, "subset-profile-witness")
    try:
        sys.monitoring.register_callback(tool, events.LINE, on_line)
        for code in watched:
            sys.monitoring.set_local_events(tool, code, events.LINE)
        yield fired
    finally:
        for code in watched:
            sys.monitoring.set_local_events(tool, code, events.NO_EVENTS)
        sys.monitoring.register_callback(tool, events.LINE, None)
        sys.monitoring.free_tool_id(tool)
        sys.monitoring.restart_events()


def recording_sites(site_ids: Iterable[str]) -> AbstractContextManager[set[str]]:
    """``recording_fired`` over scanned sites, keyed by site ID."""
    return recording_fired({site_id: site_target(site_id) for site_id in site_ids})


# ---- rewriting statements ---------------------------------------------------------------------


def neutral(target: Target) -> tuple[Rewrite, ...]:
    """The rewrite that stops the target statement from refusing (design D5)."""
    _, stmt = _statement(target)
    if isinstance(stmt, ast.Raise) or (
        isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
    ):
        return (Rewrite(target.function, None, "pass"),)
    if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.List):
        return (Rewrite(target.function, None, "return []"),)
    raise MutationError(
        f"no neutral form for a {type(stmt).__name__}: {ast.unparse(stmt).splitlines()[0]!r}"
    )


@dataclass(frozen=True)
class _Swap:
    function: FunctionType
    original: CodeType
    replacement: CodeType


def _compile_owner(
    module: ModuleType, path: Path, owner: ast.FunctionDef, live: FunctionType
) -> CodeType:
    stripped = ast.FunctionDef(**{name: getattr(owner, name) for name in owner._fields})
    stripped.decorator_list = []  # the live object already carries its decorators
    node: ast.stmt = stripped
    if "__class__" in live.__code__.co_freevars:  # zero-argument super(): compile in a class
        node = ast.ClassDef(
            name="_Mutated", bases=[], keywords=[], body=[stripped], decorator_list=[]
        )
    tree = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    flags = 0
    if vars(module).get("annotations") is __future__.annotations:
        flags |= __future__.annotations.compiler_flag
    compiled = compile(tree, str(path), "exec", flags=flags, dont_inherit=True)
    for code in _code_tree(compiled):
        if code.co_name == owner.name and code is not compiled:
            if code.co_freevars != live.__code__.co_freevars:
                raise MutationError(f"{owner.name}: free variables changed on recompiling")
            return code
    raise MutationError(f"{owner.name}: not found in its recompiled module")


def _swaps(target: Target, rewrites: tuple[Rewrite, ...]) -> list[_Swap]:
    path, tree = _parse(target.module)
    owners: dict[str, ast.FunctionDef] = {}
    for rewrite in rewrites:
        qualname, owner = _owner(_def_path(tree, rewrite.function))
        scope = _def_path(tree, rewrite.function)[-1]
        if rewrite.statement is None:
            body, stmt = _innermost(owner, target.line)
        else:
            matches = [(b, s) for b, s in _statements(scope) if ast.unparse(s) == rewrite.statement]
            if len(matches) != 1:
                raise MutationError(
                    f"{len(matches)} statements in {rewrite.function} read {rewrite.statement!r}"
                )
            body, stmt = matches[0]
        body[body.index(stmt)] = ast.copy_location(ast.parse(rewrite.replacement).body[0], stmt)
        owners[qualname] = owner
    swaps = []
    for qualname, owner in owners.items():
        live = _live_function(target.module, qualname)
        swaps.append(_Swap(live, live.__code__, _compile_owner(target.module, path, owner, live)))
    return swaps


@contextmanager
def rewritten(target: Target, rewrites: tuple[Rewrite, ...]) -> Iterator[None]:
    """Run the block with ``rewrites`` applied in the target's module; restore the code after."""
    swaps = _swaps(target, rewrites)
    for swap in swaps:
        swap.function.__code__ = swap.replacement
    try:
        yield
    finally:
        for swap in swaps:
            swap.function.__code__ = swap.original


def neutralize(site_id: str) -> AbstractContextManager[None]:
    """Run the block with the scanned site unable to refuse, by its hand patch if it has one."""
    target = site_target(site_id)
    return rewritten(target, HAND_PATCHES.get(site_id) or neutral(target))


# ---- disabling one screen recognizer ----------------------------------------------------------


def _without_shape(
    function: Callable[..., list[Any]], recognized: type, shape: str
) -> Callable[..., list[Any]]:
    def filtered(*args: Any) -> list[Any]:
        return [
            out
            for out in function(*args)
            if not (isinstance(out, recognized) and out.shape_id == shape)
        ]

    return filtered


@contextmanager
def disable_recognizer(rule: str, shape: str) -> Iterator[None]:
    """Run the block with ``rule`` no longer recognizing ``shape``; restore the rule after."""
    from agentic_mbse.sysml import subset_profile

    table: dict[str, Any] = subset_profile._RULES  # type: ignore[assignment]
    spec = table[rule]
    if shape not in spec.shapes:
        raise MutationError(f"{rule} has no shape {shape!r}")
    recognized = subset_profile._Recognized
    if spec.model_wide is not None:
        mutated = dataclasses.replace(
            spec, model_wide=_without_shape(spec.model_wide, recognized, shape)
        )
    else:
        mutated = dataclasses.replace(
            spec, instantiated=_without_shape(spec.instantiated, recognized, shape)
        )
    table[rule] = mutated
    try:
        yield
    finally:
        table[rule] = spec
