"""Enumerate the candidate refusal sites in ``src/sysml_codegen/`` (Item 2a D7, § E).

A port of the codegen half of agentic-mbse's site scanner (``scan_sites/1``, its
``scan_sites.py`` at agentic-mbse ``e268357f``). The recognized forms are that scanner's,
unchanged, so the 441 site IDs the account moved with keep their meaning. Two things are added:

- every other ``raise`` under ``src/sysml_codegen/`` is reported as an ``unrecognized`` site
  named by what it raises, so the inventory is total over ``raise`` statements;
- agentic-mbse's site IDs are resolved from the installed package's source, so a case's
  witnesses at the agentic-mbse sites the generator runs can be checked here without reading
  agentic-mbse's tree.

A site is where a refusal originates. Its ID is (path, enclosing qualname, channel, code,
ordinal within that function), which survives line moves. Channels:

  coded            ElaborationCode/ReadinessCode/SemanticEvidenceCode literal at a construction
                   or factory call
  coded-fixed      construction of a subclass that fixes its code in ``__init__``
  coded-relay      the code is ``<expr>.code``: forwarding an already-coded refusal
  coded-returned   the code is a local bound from a helper whose every return is a code literal
  coded-mapped     the code is ``TABLE.get(k, default)`` over a module-level literal table
  plumbing         the code is a parameter of the enclosing function (a factory)
  coded-DYNAMIC    the code is computed some other way
  free-text        raise of a codegen public exception class that carries no code
  builtin          raise of a builtin exception in codegen
  unrecognized     any other raise in codegen, named by the raised class, helper or variable
  shared-evidence  SemanticEvidenceError(...) (or a factory of it) in agentic-mbse
  shared-profile   executable_profile ``_diagnostic(...)`` with a literal reason in agentic-mbse

Pure: reads source text only.
"""

from __future__ import annotations

import ast
import csv
import functools
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

import agentic_mbse

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
#: The installed agentic-mbse package's source root (``src/`` for an editable install).
AGENTIC_SRC = Path(agentic_mbse.__file__).resolve().parents[1]
ACCOUNT = REPO_ROOT / "tests" / "expectations" / "refusal_cases" / "site_account.csv"

# ---- recognized forms (scan_sites/1's, unchanged) ---------------------------------------------

CODE_ENUMS = frozenset({"ElaborationCode", "ReadinessCode", "SemanticEvidenceCode"})
#: Classes whose constructor takes a code (first positional or ``code=``).
CODE_TAKING = frozenset(
    {
        "ElaborationInvariantError",
        "MultiplicityExpansionError",
        "OccurrenceResolutionError",
        "_ReferenceResolutionError",
        "Diagnostic",
        "ReadinessFinding",
        "SemanticEvidenceError",
    }
)
#: Codegen public exception classes that carry free text only.
FREE_TEXT = frozenset(
    {
        "CodeGenerationError",
        "SysMLParsingError",
        "SourceAdmissionError",
        "PredicateCompileError",
        "CompilationError",
        "GraphValidationError",
        "ExpressionInventoryError",
        "ScopePolicyMismatchError",
        "PackageSealError",
        "ProvenanceError",
        "InstanceGraphSnapshotError",
        "SnapshotShapeError",
        "SnapshotIntegrityError",
        "SnapshotCompatibilityError",
        "SnapshotStaleSourceError",
        "SnapshotCertifiabilityError",
    }
)
BUILTIN = frozenset(
    {
        "ValueError",
        "RuntimeError",
        "TypeError",
        "KeyError",
        "AssertionError",
        "LookupError",
        "NotImplementedError",
        "IndexError",
    }
)
#: Not on the generation path: study/ and cli/install.py are separate tools; contracts/verify.py
#: uses an unrelated seal-verification Diagnostic class.
EXCLUDE = ("study/", "cli/install.py", "contracts/verify.py")
SHARED_EVIDENCE_CLASS = "SemanticEvidenceError"
UNRECOGNIZED = "unrecognized"


def _callee(node: ast.Call) -> str | None:
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _literal_codes(expr: ast.expr | None) -> list[str] | None:
    """Codes named by a literal enum attribute, or both arms of a literal conditional."""
    if (
        isinstance(expr, ast.Attribute)
        and isinstance(expr.value, ast.Name)
        and expr.value.id in CODE_ENUMS
    ):
        return [expr.attr]
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str) and expr.value.isidentifier():
        return [expr.value]  # executable_profile's string reason vocabulary
    if isinstance(expr, ast.IfExp):
        a, b = _literal_codes(expr.body), _literal_codes(expr.orelse)
        if a is not None and b is not None:
            return a + b
    return None


def _code_returners(tree: ast.AST) -> dict[str, list[str]]:
    """Functions whose every return is a code literal or None."""
    out: dict[str, list[str]] = {}
    for fn in ast.walk(tree):
        if isinstance(fn, ast.FunctionDef):
            rets = [n for n in ast.walk(fn) if isinstance(n, ast.Return)]
            codes: list[str] = []
            ok = bool(rets)
            for r in rets:
                if r.value is None or (isinstance(r.value, ast.Constant) and r.value.value is None):
                    continue
                c = _literal_codes(r.value)
                if c is None:
                    ok = False
                    break
                codes += c
            if ok and codes:
                out[fn.name] = codes
    return out


def _code_tables(tree: ast.Module) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for st in tree.body:
        if isinstance(st, ast.AnnAssign):
            target: ast.expr | None = st.target
            value = st.value
        elif isinstance(st, ast.Assign):
            target, value = st.targets[0], st.value
        else:
            target, value = None, None
        if isinstance(target, ast.Name) and isinstance(value, ast.Dict):
            vals = [_literal_codes(v) for v in value.values]
            codes = [c for v in vals if v is not None for c in v]
            if vals and all(v is not None for v in vals):
                out[target.id] = codes
    return out


def _fixed_code_classes(trees: Iterable[ast.Module]) -> dict[str, str]:
    """Subclasses whose __init__ calls super().__init__(ElaborationCode.X, ...)."""
    fixed: dict[str, str] = {}
    for tree in trees:
        for cls in ast.walk(tree):
            if not isinstance(cls, ast.ClassDef):
                continue
            for item in cls.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    for call in ast.walk(item):
                        if (
                            isinstance(call, ast.Call)
                            and isinstance(call.func, ast.Attribute)
                            and call.func.attr == "__init__"
                            and call.args
                        ):
                            codes = _literal_codes(call.args[0])
                            if codes is not None:
                                fixed[cls.name] = "|".join(codes)
    return fixed


def _code_expr(node: ast.Call, factory_pos: dict[str, int]) -> ast.expr | None:
    for kw in node.keywords:
        if kw.arg == "code":
            return kw.value
    pos = factory_pos.get(_callee(node) or "", 0)
    return node.args[pos] if len(node.args) > pos else None


def _factories(trees: Iterable[ast.Module]) -> dict[str, int]:
    """Functions that take a code parameter and pass it to a code-taking constructor (fixpoint)."""
    trees = list(trees)
    found: dict[str, int] = {}
    while True:
        before = dict(found)
        for tree in trees:
            for fn in ast.walk(tree):
                if not isinstance(fn, ast.FunctionDef):
                    continue
                names = [a.arg for a in fn.args.args if a.arg not in ("self", "cls")]
                for call in ast.walk(fn):
                    if isinstance(call, ast.Call) and _callee(call) in CODE_TAKING | set(found):
                        e = _code_expr(call, before)
                        if isinstance(e, ast.Name) and e.id in names:
                            found[fn.name] = names.index(e.id)
        if found == before:
            return found


def _raised_name(exc: ast.expr | None) -> str:
    """What a raise names: its class or helper, a raised variable, or a bare re-raise."""
    if exc is None:
        return "<reraise>"
    target = exc.func if isinstance(exc, ast.Call) else exc
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return ast.unparse(target)


def _site_reason(node: ast.Call | ast.Raise) -> str | None:
    """The ``SiteReason`` member a site passes literally as ``reason=``, if it passes one."""
    call = node.exc if isinstance(node, ast.Raise) else node
    if not isinstance(call, ast.Call):
        return None
    for kw in call.keywords:
        if (
            kw.arg == "reason"
            and isinstance(kw.value, ast.Attribute)
            and isinstance(kw.value.value, ast.Name)
            and kw.value.value.id == "SiteReason"
        ):
            return kw.value.attr
    return None


@dataclass(frozen=True)
class Site:
    site_id: str
    file: str
    line: int
    function: str
    channel: str
    code: str
    #: The callee or raised name the site was recognized by.
    via: str
    #: Keyword names passed at the site's call (empty for a raise of a non-call).
    keywords: frozenset[str]
    #: The ``SiteReason`` member name passed literally as ``reason=``, if any.
    reason: str | None


@dataclass(frozen=True)
class Scan:
    sites: tuple[Site, ...]

    def codegen(self) -> tuple[Site, ...]:
        return tuple(s for s in self.sites if s.file.startswith("sysml_codegen/"))

    def ids(self) -> set[str]:
        """The codegen site IDs: the set the account is total over."""
        return {s.site_id for s in self.codegen()}

    def by_id(self) -> dict[str, Site]:
        return {s.site_id: s for s in self.sites}


@dataclass
class _FunctionScope:
    params: set[str] = field(default_factory=set)
    locals: dict[str, str | None] = field(default_factory=dict)


class _Visitor(ast.NodeVisitor):
    """Collect the sites in one module. ``shared`` selects the agentic-mbse forms."""

    def __init__(
        self,
        rel: str,
        tree: ast.Module,
        fixed: dict[str, str],
        factory_pos: dict[str, int],
        shared: bool,
    ) -> None:
        self.rel, self.fixed, self.factory_pos, self.shared = rel, fixed, factory_pos, shared
        self.returners, self.tables = _code_returners(tree), _code_tables(tree)
        self.scope = _FunctionScope()
        self.stack: list[str] = []
        self.sites: list[Site] = []
        self.recorded: set[int] = set()
        self.ordinals: Counter[tuple[str, str, str]] = Counter()

    def classify_code(self, expr: ast.expr | None) -> tuple[str, str]:
        codes = _literal_codes(expr)
        if codes is not None:
            return "coded", "|".join(codes)
        if isinstance(expr, ast.Attribute) and expr.attr == "code":
            return "coded-relay", ast.unparse(expr)
        if isinstance(expr, ast.Name):
            if expr.id in self.scope.params:
                return "plumbing", expr.id
            fn = self.scope.locals.get(expr.id)
            if fn is not None and fn in self.returners:
                return "coded-returned", "|".join(self.returners[fn])
        if (
            isinstance(expr, ast.Call)
            and isinstance(expr.func, ast.Attribute)
            and expr.func.attr == "get"
            and isinstance(expr.func.value, ast.Name)
            and expr.func.value.id in self.tables
        ):
            default = _literal_codes(expr.args[1]) if len(expr.args) > 1 else []
            if default is not None:
                table = self.tables[expr.func.value.id]
                return "coded-mapped", "|".join(sorted(set(table + default)))
        return "coded-DYNAMIC", ast.unparse(expr) if expr is not None else "<none>"

    def _scope(self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> None:
        self.stack.append(node.name)
        saved = self.scope
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self.scope = _FunctionScope(
                params={a.arg for a in node.args.args + node.args.kwonlyargs}
            )
            for st in ast.walk(node):
                if (
                    isinstance(st, ast.Assign)
                    and len(st.targets) == 1
                    and isinstance(st.targets[0], ast.Name)
                    and isinstance(st.value, ast.Call)
                ):
                    self.scope.locals[st.targets[0].id] = _callee(st.value)
        self.generic_visit(node)
        self.scope = saved
        self.stack.pop()

    visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = _scope  # noqa: N815

    def add(self, node: ast.Call | ast.Raise, channel: str, code: str, via: str) -> None:
        func = ".".join(self.stack) or "<module>"
        key = (func, channel, code)
        self.ordinals[key] += 1
        call = node.exc if isinstance(node, ast.Raise) else node
        self.recorded.add(id(node))
        self.sites.append(
            Site(
                site_id=f"{self.rel}::{func}::{channel}::{code}::{self.ordinals[key]}",
                file=self.rel,
                line=node.lineno,
                function=func,
                channel=channel,
                code=code,
                via=via,
                keywords=frozenset(kw.arg for kw in call.keywords if kw.arg is not None)
                if isinstance(call, ast.Call)
                else frozenset(),
                reason=_site_reason(node),
            )
        )

    def visit_Call(self, node: ast.Call) -> None:
        name = _callee(node)
        in_super_init = bool(self.stack) and self.stack[-1] == "__init__"
        if self.shared:
            if name in {SHARED_EVIDENCE_CLASS} | set(self.factory_pos):
                channel, code = self.classify_code(_code_expr(node, self.factory_pos))
                if channel == "coded":
                    channel = "shared-evidence" if code.isupper() else "shared-profile"
                self.add(node, channel, code, name or "?")
        elif name in self.factory_pos or (name in CODE_TAKING and not in_super_init):
            not_elaboration = (
                name == "Diagnostic"
                and not node.args
                and not any(kw.arg == "code" for kw in node.keywords)
            )
            if not not_elaboration:
                channel, code = self.classify_code(_code_expr(node, self.factory_pos))
                self.add(node, channel, code, name or "?")
        elif name in self.fixed:
            self.add(node, "coded-fixed", self.fixed[name], name)
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        if self.shared:
            self.generic_visit(node)
            return
        name = _raised_name(node.exc)
        if name in FREE_TEXT:
            self.add(node, "free-text", name, name)
        elif name in BUILTIN:
            self.add(node, "builtin", name, name)
        self.generic_visit(node)
        if id(node) in self.recorded:
            return
        # A raise whose exception expression holds a recognized site is that site's raise.
        if node.exc is not None and any(id(n) in self.recorded for n in ast.walk(node.exc)):
            return
        self.add(node, UNRECOGNIZED, name, name)


@functools.cache
def _sources(root: Path, package: str, exclude: tuple[str, ...]) -> list[tuple[str, ast.Module]]:
    """Parsed modules under ``root/package``, cached: the trees are read, never mutated."""
    out = []
    for path in sorted((root / package).rglob("*.py")):
        rel = str(path.relative_to(root))
        if any(rel.replace(f"{package}/", "", 1).startswith(e) for e in exclude):
            continue
        out.append((rel, ast.parse(path.read_text(encoding="utf-8"))))
    return out


def scan(codegen_src: Path = SRC, agentic_src: Path = AGENTIC_SRC) -> Scan:
    """Every site in the two source roots, in file then source order."""
    cg = _sources(codegen_src, "sysml_codegen", EXCLUDE)
    am = _sources(agentic_src, "agentic_mbse", ())
    fixed = _fixed_code_classes(tree for _, tree in cg)
    factory_pos = _factories(tree for _, tree in cg + am)
    sites: list[Site] = []
    for sources, shared in ((cg, False), (am, True)):
        for rel, tree in sources:
            visitor = _Visitor(rel, tree, fixed, factory_pos, shared)
            visitor.visit(tree)
            sites += visitor.sites
    return Scan(tuple(sites))


def code_generation_errors_without_code(codegen_src: Path = SRC) -> list[str]:
    """Every ``CodeGenerationError(...)`` construction that passes no ``code=`` (design D15).

    Constructions, not raises: a factory returns the error for its caller to raise.
    """
    missing = []
    for rel, tree in _sources(codegen_src, "sysml_codegen", EXCLUDE):
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and _callee(node) == "CodeGenerationError"
                and not any(kw.arg == "code" for kw in node.keywords)
            ):
                missing.append(f"{rel}:{node.lineno}")
    return missing


# ---- the site account --------------------------------------------------------------------------

ACCOUNT_FIELDS = (
    "site_id",
    "file",
    "line",
    "channel",
    "code",
    "disposition",
    "role",
    "owner",
    "reason",
    "evidence",
    "coverage_limitation",
    "note",
)


class SiteAccountError(ValueError):
    """The site account breaks its schema."""


class Disposition(StrEnum):
    IN_SCOPE = "in_scope"
    HANDLED_ELSEWHERE = "handled_elsewhere"
    EXPLICIT_FOLLOW_UP = "explicit_follow_up"


class Role(StrEnum):
    PUBLIC_CAPABILITY = "public_capability"
    MALFORMED_INPUT = "malformed_input"
    ENVIRONMENT = "environment"
    SNAPSHOT_INTEGRITY = "snapshot_integrity"
    RELAY_PLUMBING = "relay_plumbing"
    INTERNAL_INVARIANT = "internal_invariant"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class AccountRow:
    site_id: str
    file: str
    #: The site's line when the row was last written; the scan is the authority for location.
    line: int
    channel: str
    code: str
    disposition: Disposition
    role: Role
    owner: str
    #: The ``SiteReason`` value the site passes, once it has one.
    reason: str | None
    #: ``file.py:line`` of the site, then any further pointers, ``;``-separated.
    evidence: tuple[str, ...]
    #: Required for an explicit follow-up.
    coverage_limitation: str
    note: str


@dataclass(frozen=True)
class SiteAccount:
    header: tuple[str, ...]
    rows: tuple[AccountRow, ...]

    def ids(self) -> set[str]:
        return {r.site_id for r in self.rows}


def _split(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(";") if part.strip())


def _account_row(raw: dict[str, str]) -> AccountRow:
    where = f"site {raw.get('site_id', '?')!r}"
    try:
        disposition = Disposition(raw["disposition"])
        role = Role(raw["role"])
    except ValueError as error:
        raise SiteAccountError(f"{where}: {error}") from None
    row = AccountRow(
        site_id=raw["site_id"],
        file=raw["file"],
        line=int(raw["line"]),
        channel=raw["channel"],
        code=raw["code"],
        disposition=disposition,
        role=role,
        owner=raw["owner"].strip(),
        reason=raw["reason"].strip() or None,
        evidence=_split(raw["evidence"]),
        coverage_limitation=raw["coverage_limitation"].strip(),
        note=raw["note"].strip(),
    )
    if not row.owner or not row.evidence or not row.note:
        raise SiteAccountError(f"{where}: owner, evidence and note are required")
    if not row.evidence[0].startswith(f"{row.file}:{row.line}"):
        raise SiteAccountError(f"{where}: evidence must start with the site, {row.file}:{row.line}")
    if (disposition is Disposition.EXPLICIT_FOLLOW_UP) != bool(row.coverage_limitation):
        raise SiteAccountError(f"{where}: coverage_limitation is required iff explicit follow-up")
    return row


def load_account(path: Path = ACCOUNT) -> SiteAccount:
    lines = path.read_text(encoding="utf-8").splitlines()
    header = tuple(line[2:] for line in lines if line.startswith("# "))
    reader = csv.DictReader(line for line in lines if not line.startswith("#"))
    if tuple(reader.fieldnames or ()) != ACCOUNT_FIELDS:
        raise SiteAccountError(f"{path}: columns must be {ACCOUNT_FIELDS}, got {reader.fieldnames}")
    rows = tuple(_account_row(raw) for raw in reader)
    ids = [r.site_id for r in rows]
    if len(set(ids)) != len(ids):
        raise SiteAccountError(f"{path}: repeated site ids")
    return SiteAccount(header=header, rows=rows)


def iter_unrecognized(found: Scan) -> Iterator[Site]:
    return (s for s in found.codegen() if s.channel == UNRECOGNIZED)


# ---- reachability (Item 2b D14) -----------------------------------------------------------------

#: A function in ``src/sysml_codegen/``, named as a ``Site`` names its enclosing function:
#: (``Site.file``, ``Site.function``).
FunctionKey = tuple[str, str]

_AnyFunction = ast.FunctionDef | ast.AsyncFunctionDef
#: The methods instantiating a class runs.
_CONSTRUCTION = frozenset({"__new__", "__init__", "__post_init__"})
_PROPERTY_DECORATORS = frozenset({"property", "cached_property"})


@dataclass(frozen=True)
class _Body:
    """What one function's body can run, by name (see ``_body_names``)."""

    #: Names called or loaded bare, import-alias resolved.
    bare: frozenset[str]
    #: Attribute names called, dunders excepted.
    attribute_calls: frozenset[str]
    #: Attribute names loaded without a call.
    attribute_loads: frozenset[str]


@dataclass
class _CallIndex:
    """What the closure follows, read once from every module."""

    #: Module-level function name → every such function.
    module_functions: dict[str, set[FunctionKey]] = field(default_factory=dict)
    #: Method name → every method of that name, in any class.
    methods: dict[str, set[FunctionKey]] = field(default_factory=dict)
    #: Enclosing function → its nested functions by name.
    nested: dict[FunctionKey, dict[str, FunctionKey]] = field(default_factory=dict)
    #: Class name → its construction methods.
    constructors: dict[str, set[FunctionKey]] = field(default_factory=dict)
    #: Class name → the bare names of its bases.
    bases: dict[str, set[str]] = field(default_factory=dict)
    #: Names of properties, which run on attribute access rather than on a call.
    properties: set[str] = field(default_factory=set)
    #: A module-level ``alias = name``, which other modules import under ``alias``.
    assigned_aliases: dict[str, str] = field(default_factory=dict)
    bodies: dict[FunctionKey, _Body] = field(default_factory=dict)


def _bare_name(node: ast.expr) -> str | None:
    target = node.func if isinstance(node, ast.Call) else node
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return None


def _import_aliases(tree: ast.Module) -> dict[str, str]:
    """``from x import name as alias`` anywhere in the module: alias → name."""
    return {
        alias.asname: alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
        if alias.asname is not None
    }


def _without_annotations(fn: _AnyFunction) -> Iterator[ast.AST]:
    """The nodes of a function's decorators, defaults and body, never its annotations."""
    annotations: set[int] = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.arg) and node.annotation is not None:
            annotations.add(id(node.annotation))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns:
            annotations.add(id(node.returns))
        elif isinstance(node, ast.AnnAssign):
            annotations.add(id(node.annotation))
    pending: list[ast.AST] = [fn]
    while pending:
        node = pending.pop()
        if id(node) in annotations:
            continue
        yield node
        pending.extend(ast.iter_child_nodes(node))


def _body_names(fn: _AnyFunction, aliases: dict[str, str]) -> _Body:
    """The names a function's body, nested functions included, can run.

    A dunder call such as ``super().__init__`` is left to construction, which reaches the
    construction methods of a class and its bases; a bare name loaded anywhere is followed,
    so a function handed over as an argument is reached.
    """
    bare: set[str] = set()
    attribute_calls: set[str] = set()
    attribute_loads: set[str] = set()
    for node in _without_annotations(fn):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            name = node.func.attr
            if not (name.startswith("__") and name.endswith("__")):
                attribute_calls.add(name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            bare.add(aliases.get(node.id, node.id))
        elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
            attribute_loads.add(node.attr)
    return _Body(frozenset(bare), frozenset(attribute_calls), frozenset(attribute_loads))


def _index_module(rel: str, tree: ast.Module, index: _CallIndex) -> None:
    aliases = _import_aliases(tree)
    for st in tree.body:
        if (
            isinstance(st, ast.Assign)
            and len(st.targets) == 1
            and isinstance(st.targets[0], ast.Name)
            and isinstance(st.value, ast.Name)
        ):
            index.assigned_aliases[st.targets[0].id] = st.value.id

    def walk(node: ast.AST, stack: tuple[str, ...], owner: FunctionKey | str | None) -> None:
        """``owner`` is the enclosing function's key, a class name, or ``None`` at module level."""
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qualname = (*stack, child.name)
                key = (rel, ".".join(qualname))
                index.bodies[key] = _body_names(child, aliases)
                if owner is None:
                    index.module_functions.setdefault(child.name, set()).add(key)
                elif isinstance(owner, str):
                    index.methods.setdefault(child.name, set()).add(key)
                    if child.name in _CONSTRUCTION:
                        index.constructors.setdefault(owner, set()).add(key)
                    if any(_bare_name(d) in _PROPERTY_DECORATORS for d in child.decorator_list):
                        index.properties.add(child.name)
                else:
                    index.nested.setdefault(owner, {})[child.name] = key
                walk(child, qualname, key)
            elif isinstance(child, ast.ClassDef):
                index.bases.setdefault(child.name, set()).update(
                    name for base in child.bases if (name := _bare_name(base)) is not None
                )
                walk(child, (*stack, child.name), child.name)
            else:
                walk(child, stack, owner)

    walk(tree, (), None)


def _construction(class_name: str, index: _CallIndex) -> set[FunctionKey]:
    """The construction methods of a class and of every base it names, by bare name."""
    found: set[FunctionKey] = set()
    pending, seen = [class_name], set()
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        found |= index.constructors.get(name, set())
        pending.extend(index.bases.get(name, ()))
    return found


def _enclosing(key: FunctionKey) -> Iterator[FunctionKey]:
    """The key itself, then each enclosing qualname, innermost first."""
    file, function = key
    parts = function.split(".")
    for end in range(len(parts), 0, -1):
        yield file, ".".join(parts[:end])


def _callees(key: FunctionKey, index: _CallIndex) -> set[FunctionKey]:
    body = index.bodies[key]
    found: set[FunctionKey] = set()
    for name in body.bare:
        target = index.assigned_aliases.get(name, name)
        found |= index.module_functions.get(target, set()) | _construction(target, index)
        found |= {
            nested[name]
            for scope in _enclosing(key)
            if name in (nested := index.nested.get(scope, {}))
        }
    for name in body.attribute_calls:
        target = index.assigned_aliases.get(name, name)
        found |= index.methods.get(name, set())
        found |= index.module_functions.get(target, set()) | _construction(target, index)
    for name in body.attribute_loads & index.properties:
        found |= index.methods[name]
    return found


def call_closure(roots: Iterable[FunctionKey], codegen_src: Path = SRC) -> frozenset[FunctionKey]:
    """Every function in ``src/sysml_codegen/`` reachable from ``roots`` by name.

    Name-based and over-approximate. A bare name reaches every module-level function of that
    name, a nested function it can see, and, for a class name, the construction methods of the
    class and its named bases; ``x.name(...)`` also reaches every method of that name; loading
    ``x.name`` reaches a property of that name. A module-level ``alias = name`` is followed
    across modules. Annotations are not followed, and neither is a call made through
    ``getattr`` or a callable stored and called under another name. Pure: reads source only.
    """
    index = _CallIndex()
    for rel, tree in _sources(codegen_src, "sysml_codegen", EXCLUDE):
        _index_module(rel, tree, index)

    pending = list(roots)
    unknown = [root for root in pending if root not in index.bodies]
    if unknown:
        raise KeyError(f"no such function under {codegen_src}: {unknown}")
    reached: set[FunctionKey] = set()
    while pending:
        key = pending.pop()
        if key in reached:
            continue
        reached.add(key)
        pending.extend(_callees(key, index))
    return frozenset(reached)
