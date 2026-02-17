"""Shared static analysis helpers for conformance tests.

Provides AST-based introspection of production source code to verify
dispatch ordering, is_instance() call patterns, and comment annotations.

Extracted from C04, C06, and C07 conformance tests (D3 dedup).
"""

from __future__ import annotations

import ast as python_ast
from pathlib import Path
from typing import Callable


def is_syside_is_instance_call(call_node: python_ast.Call) -> bool:
    """Check if an ast.Call node is SysideAdapter.is_instance(...)."""
    func = call_node.func
    if isinstance(func, python_ast.Attribute) and func.attr == "is_instance":
        if isinstance(func.value, python_ast.Name) and func.value.id == "SysideAdapter":
            return True
    return False


def is_any_is_instance_call(call_node: python_ast.Call) -> bool:
    """Check if an ast.Call node is *.is_instance(...).

    Matches both SysideAdapter.is_instance() and self.adapter.is_instance().
    """
    func = call_node.func
    if isinstance(func, python_ast.Attribute) and func.attr == "is_instance":
        return True
    return False


def find_is_instance_calls_in_function(
    source_path: Path,
    function_name: str,
    predicate: Callable[[python_ast.Call], bool] = is_syside_is_instance_call,
) -> dict[str, int]:
    """Parse source file and find is_instance() calls in a specific function.

    Returns dict mapping type_name argument to line number (first occurrence only).

    Args:
        source_path: Path to the Python source file.
        function_name: Name of the function to inspect.
        predicate: Callable that returns True for matching ast.Call nodes.
            Defaults to is_syside_is_instance_call (SysideAdapter only).
    """
    source = source_path.read_text()
    tree = python_ast.parse(source, filename=str(source_path))

    results: dict[str, int] = {}

    for node in python_ast.walk(tree):
        if isinstance(node, python_ast.FunctionDef) and node.name == function_name:
            for child in python_ast.walk(node):
                if isinstance(child, python_ast.Call) and predicate(child):
                    if len(child.args) >= 2:
                        type_arg = child.args[1]
                        if isinstance(type_arg, python_ast.Constant) and isinstance(
                            type_arg.value, str
                        ):
                            if type_arg.value not in results:
                                results[type_arg.value] = child.lineno
            break

    return results


def find_comment_near_line(
    source_lines: list[str], target_line: int, pattern: str, window: int = 5
) -> bool:
    """Check if a comment matching pattern appears within window lines above target_line.

    Args:
        source_lines: File contents split by newlines (0-indexed).
        target_line: 1-based line number of the target.
        pattern: Substring to look for in comments.
        window: Number of lines above target_line to search.

    Returns:
        True if a comment containing the pattern is found within the window.
    """
    start = max(0, target_line - 1 - window)
    end = target_line  # include the target line itself
    for line in source_lines[start:end]:
        stripped = line.strip()
        if stripped.startswith("#") and pattern in stripped:
            return True
    return False


def find_all_dispatch_functions(
    src_dir: Path,
    type_names: set[str],
    predicate: Callable[[python_ast.Call], bool] = is_any_is_instance_call,
) -> dict[tuple[str, str], dict[str, int]]:
    """Walk all .py files in src_dir and find functions with is_instance() on expression types.

    Returns dict mapping (relative_path, function_name) to {type_name: line_number}.
    Only includes functions that check at least one of the given type_names.

    Args:
        src_dir: Root directory to search.
        type_names: Set of type name strings to filter for.
        predicate: Callable that returns True for matching ast.Call nodes.
    """
    results: dict[tuple[str, str], dict[str, int]] = {}

    for py_file in sorted(src_dir.rglob("*.py")):
        try:
            source = py_file.read_text()
            tree = python_ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue

        rel_path = str(py_file.relative_to(src_dir))

        for node in python_ast.walk(tree):
            if isinstance(node, python_ast.FunctionDef):
                func_types: dict[str, int] = {}
                for child in python_ast.walk(node):
                    if isinstance(child, python_ast.Call) and predicate(child):
                        if len(child.args) >= 2:
                            type_arg = child.args[1]
                            if (
                                isinstance(type_arg, python_ast.Constant)
                                and isinstance(type_arg.value, str)
                                and type_arg.value in type_names
                            ):
                                if type_arg.value not in func_types:
                                    func_types[type_arg.value] = child.lineno

                if func_types:
                    results[(rel_path, node.name)] = func_types

    return results
