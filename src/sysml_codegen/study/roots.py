"""The three roots the study tools locate things by, and their one read of the environment.

The tools once found everything relative to their own file. Installed, that file sits inside
site-packages, so each former ``__file__`` question is answered here by the root it meant:

- **The project root** anchors every path a document cites, and the target's declaration.
  It is the git work tree that contains the package a tool was given. The first rule that
  applies wins:

  1. an in-process override, :func:`use_project_root`, which only library callers set;
  2. the ``SYSML_CODEGEN_PROJECT_ROOT`` environment variable;
  3. on the command line, the work tree containing the tool's anchor (the package it was
     given); in a library call, the work tree containing the working directory.

  When rule 3 applies on the command line, two cases are refused with exit 2 and no
  document: the anchor is in no work tree, or the working directory is inside a different
  work tree from the anchor. A working directory outside every work tree is not a conflict,
  so a tool run from a scratch directory cites the same paths as one run from the project.
  When an override applies, no work-tree check runs, and a package outside the root renders
  with leading ``..`` segments.
- **The tool home** anchors tool identity: ``tool.path`` and every tool-source digest. It is
  the directory that holds the installed ``sysml_codegen`` package.
- **The teax root** is ``TEAX_SIMKIT_PATH``, a simkit root, and nothing else.

This is the one study module that reads ``os.environ``. Every other module asks here.
"""

from __future__ import annotations

import functools
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT_ENV = "SYSML_CODEGEN_PROJECT_ROOT"
TEAX_SIMKIT_PATH = "TEAX_SIMKIT_PATH"

#: The directory holding ``sysml_codegen/``. The one place where ``__file__`` is the answer.
TOOL_HOME: Path = Path(__file__).resolve().parents[2]

#: Set only by :func:`use_project_root`: a library caller's explicit project root.
_override: Path | None = None
#: Set only by :func:`require_project_root`: the root a command-line run resolved at entry.
_pinned: Path | None = None


class RootError(Exception):
    """No project root can be named, or the one the anchor names conflicts with the caller's."""


def use_project_root(root: Path | None) -> None:
    """Pin the project root in-process for a library caller; ``None`` forgets every root.

    The override wins over the environment variable and over any work tree, and it is never
    checked against one: the caller is stating where its project is. ``None`` clears the
    override, the command-line pin and the cached library default, so the next lookup
    resolves afresh.
    """
    global _override, _pinned
    if root is None:
        _override = None
        _pinned = None
        _library_root.cache_clear()
        return
    _override = _named_root(str(root), "use_project_root")


def project_root() -> Path:
    """The project root every cited path is relative to.

    Raises :class:`RootError` when nothing names one: no override, no pinned command-line
    root, no ``SYSML_CODEGEN_PROJECT_ROOT``, and a working directory outside every work tree.
    """
    if _override is not None:
        return _override
    if _pinned is not None:
        return _pinned
    return _library_root(os.environ.get(PROJECT_ROOT_ENV) or None, Path.cwd())


def require_project_root(prog: str, anchor: Path) -> Path:
    """Resolve, check and pin the project root for a command-line run anchored on ``anchor``.

    On a :class:`RootError` it prints the reason, naming the paths involved, and exits 2.
    """
    global _pinned
    try:
        root = _command_line_root(anchor)
    except RootError as exc:
        print(f"{prog}: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    _pinned = root
    return root


def environment() -> dict[str, str]:
    """A copy of the process environment, for the subprocesses a tool launches."""
    return dict(os.environ)


def teax_simkit_path() -> Path | None:
    """The simkit root ``TEAX_SIMKIT_PATH`` names, or ``None`` when it is unset or empty."""
    value = os.environ.get(TEAX_SIMKIT_PATH)
    return Path(value) if value else None


def _work_tree(start: Path) -> Path | None:
    """The top of the git work tree containing the directory ``start``, or ``None``."""
    done = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if done.returncode != 0:
        return None
    return Path(done.stdout.strip()).resolve()


def _named_root(value: str, source: str) -> Path:
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise RootError(f"{source} names {root} as the project root, which is not a directory")
    return root


@functools.cache
def _library_root(variable: str | None, cwd: Path) -> Path:
    if variable is not None:
        return _named_root(variable, PROJECT_ROOT_ENV)
    tree = _work_tree(cwd)
    if tree is None:
        raise RootError(
            f"no project root: the working directory {cwd} is in no git work tree and "
            f"{PROJECT_ROOT_ENV} is not set"
        )
    return tree


def _command_line_root(anchor: Path) -> Path:
    if _override is not None:
        return _override
    variable = os.environ.get(PROJECT_ROOT_ENV)
    if variable:
        return _named_root(variable, PROJECT_ROOT_ENV)
    cwd = Path.cwd()
    tree = _work_tree(_nearest_existing_directory(anchor))
    if tree is None:
        raise RootError(
            f"no project root: the package {anchor} is in no git work tree (working "
            f"directory {cwd}); set {PROJECT_ROOT_ENV} to the project root"
        )
    cwd_tree = _work_tree(cwd)
    if cwd_tree is not None and cwd_tree != tree:
        raise RootError(
            f"conflicting project roots: the package {anchor} is in the work tree {tree}, "
            f"but the working directory {cwd} is in the work tree {cwd_tree}; run from "
            f"inside {tree} or outside every work tree, or set {PROJECT_ROOT_ENV}"
        )
    return tree


def _nearest_existing_directory(path: Path) -> Path:
    """``path`` itself if it is a directory, else its nearest existing ancestor directory."""
    candidate = path.resolve()
    while not candidate.is_dir():
        candidate = candidate.parent
    return candidate
