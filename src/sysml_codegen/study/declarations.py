"""What a target declares about itself for ``integrate``, read from its ``pyproject.toml``.

``integrate`` judges any target, so the facts one target used to hard-code about itself are
data the target writes, in the table ``[tool.sysml-codegen.integrate]`` of the
``pyproject.toml`` at its project root:

- ``gates.pinned-packages`` and ``gates.model-family-spine``: for each repo-scope gate, the
  pytest ``target`` that judges it (project-relative, optionally ``path::node``) and the
  ``checked`` text the return states that gate examined;
- ``environment``: further variables gate 0 sweeps, because a declared producer reads them;
- ``record-distributions``: toolchain key to installed distribution, recorded in the return
  beside the fixed keys;
- ``backup-prefix``: the prefix of the directory the package is copied aside into.

Validation is strict, and anything malformed raises :class:`DeclarationError`, which
``integrate`` reports at gate 0 as ``input-invalid``. A declared gate has no default
``checked`` text, because a default would claim a check nobody declared. A gate left out is
not declared, and ``integrate`` blocks on it as a question the target never answered.
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

PYPROJECT = "pyproject.toml"
REPO_GATES = ("pinned-packages", "model-family-spine")
FIXED_TOOLCHAIN_KEYS = ("agentic_mbse", "sysml_codegen", "teax_revision", "teax_module_path")
DEFAULT_BACKUP_PREFIX = "sysml-codegen-integration-backup-"

_TABLE_PATH = ("tool", "sysml-codegen", "integrate")
_TABLE = "[tool.sysml-codegen.integrate]"
_TABLE_KEYS = ("gates", "environment", "record-distributions", "backup-prefix")
_GATE_KEYS = ("target", "checked")
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class DeclarationError(Exception):
    """The target's declaration is malformed. The message names the table and the problem."""


@dataclass(frozen=True)
class GateDeclaration:
    """One repo-scope gate: the pytest target that judges it, and what it is said to check."""

    target: str
    checked: str


@dataclass(frozen=True)
class IntegrateDeclaration:
    """Everything a target declares for ``integrate``. ``gates`` holds only declared gates."""

    gates: Mapping[str, GateDeclaration]
    environment: tuple[str, ...]
    record_distributions: tuple[tuple[str, str], ...]
    backup_prefix: str


#: A target that declares nothing: no repo gate, no extra variable, no recorded distribution.
UNDECLARED = IntegrateDeclaration(
    gates=MappingProxyType({}),
    environment=(),
    record_distributions=(),
    backup_prefix=DEFAULT_BACKUP_PREFIX,
)


def load_declaration(project_root: Path) -> IntegrateDeclaration:
    """The declaration in ``project_root``'s ``pyproject.toml``.

    A missing file, or a file without the table, declares nothing and gives
    :data:`UNDECLARED`. Anything malformed raises :class:`DeclarationError`.
    """
    path = project_root / PYPROJECT
    if not path.is_file():
        return UNDECLARED
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise DeclarationError(f"{PYPROJECT} is not valid TOML: {exc}") from exc
    table = _integrate_table(document)
    if table is None:
        return UNDECLARED
    return _parse(table, project_root)


def _integrate_table(document: dict[str, Any]) -> dict[str, Any] | None:
    """The ``[tool.sysml-codegen.integrate]`` table, or ``None`` when it is absent."""
    node = document
    for depth, key in enumerate(_TABLE_PATH, start=1):
        if key not in node:
            return None
        node = _table(node[key], "[" + ".".join(_TABLE_PATH[:depth]) + "]")
    return node


def _parse(table: dict[str, Any], project_root: Path) -> IntegrateDeclaration:
    _no_unknown_keys(table, _TABLE_KEYS, _TABLE)
    return IntegrateDeclaration(
        gates=MappingProxyType(_gates(table.get("gates", {}), project_root)),
        environment=_environment(table.get("environment", [])),
        record_distributions=_distributions(table.get("record-distributions", {})),
        backup_prefix=_backup_prefix(table.get("backup-prefix", DEFAULT_BACKUP_PREFIX)),
    )


def _gates(value: object, project_root: Path) -> dict[str, GateDeclaration]:
    declared: dict[str, GateDeclaration] = {}
    for name, entry in _table(value, f"{_TABLE} gates").items():
        if name not in REPO_GATES:
            gates = ", ".join(REPO_GATES)
            raise _error(f"{_TABLE} gates", f"{name} is not a repo-scope gate; they are {gates}")
        where = f"[tool.sysml-codegen.integrate.gates.{name}]"
        fields = _table(entry, where)
        _no_unknown_keys(fields, _GATE_KEYS, where)
        for key in _GATE_KEYS:
            if key not in fields:
                raise _error(
                    where,
                    f"has no {key}; a declared gate states the target that judges it and what it "
                    "checked, and neither has a default",
                )
        target = _text(fields["target"], f"{where} target")
        checked = _text(fields["checked"], f"{where} checked")
        _require_inside(target, project_root, where)
        declared[name] = GateDeclaration(target=target, checked=checked)
    return declared


def _require_inside(target: str, project_root: Path, where: str) -> None:
    """The file part of ``target`` is relative and stays inside the project root, resolved."""
    file_part = target.split("::", 1)[0]
    if not file_part.strip():
        raise _error(where, f"target {target!r} names no file")
    if Path(file_part).is_absolute():
        raise _error(where, f"target {target!r} is absolute; targets are project-relative")
    root = project_root.resolve()
    if not (root / file_part).resolve().is_relative_to(root):
        raise _error(where, f"target {target!r} resolves outside the project root")


def _environment(value: object) -> tuple[str, ...]:
    where = f"{_TABLE} environment"
    if not isinstance(value, list):
        raise _error(where, "must be an array of variable names")
    names: list[str] = []
    for item in value:
        if not isinstance(item, str) or not _NAME.fullmatch(item):
            raise _error(where, f"{item!r} is not a variable name")
        if item in names:
            raise _error(where, f"names {item} twice")
        names.append(item)
    return tuple(names)


def _distributions(value: object) -> tuple[tuple[str, str], ...]:
    where = f"{_TABLE} record-distributions"
    pairs: list[tuple[str, str]] = []
    for key, distribution in _table(value, where).items():
        if not _NAME.fullmatch(key):
            raise _error(where, f"{key!r} is not an identifier")
        if key in FIXED_TOOLCHAIN_KEYS:
            raise _error(where, f"{key} is a fixed toolchain key")
        pairs.append((key, _text(distribution, f"{where}.{key}")))
    return tuple(pairs)


def _backup_prefix(value: object) -> str:
    where = f"{_TABLE} backup-prefix"
    prefix = _text(value, where)
    if "/" in prefix:
        raise _error(where, f"{prefix!r} contains '/'; it names a directory, not a path")
    return prefix


def _table(value: object, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error(where, "must be a table")
    return value


def _text(value: object, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _error(where, "must be a non-empty string")
    return value


def _no_unknown_keys(table: dict[str, Any], allowed: tuple[str, ...], where: str) -> None:
    unknown = sorted(set(table) - set(allowed))
    if unknown:
        raise _error(where, f"unknown key {unknown[0]}; the keys are {', '.join(allowed)}")


def _error(where: str, problem: str) -> DeclarationError:
    return DeclarationError(f"{PYPROJECT} {where} {problem}")
