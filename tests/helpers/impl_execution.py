"""Shared utilities for executing generated impl code and comparing results.

Adapted from scripts/spike_compile_expressions.py execution logic.
Used by integration tests to validate auto-generated implementations
produce numerically correct results.
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from types import SimpleNamespace


def find_impl_files(output_path: Path) -> list[Path]:
    """Find all _impl.py files in the handwritten directory.

    Returns sorted list for deterministic ordering.
    """
    handwritten_dir = output_path / "handwritten"
    return sorted(
        p
        for p in handwritten_dir.rglob("*_impl.py")
        if p.name != "__init__.py"
    )


def is_auto_implemented(impl_path: Path) -> bool:
    """Check whether an impl file was auto-implemented."""
    content = impl_path.read_text()
    return "AUTO_IMPLEMENTED = True" in content


def extract_function_body(impl_path: Path) -> str | None:
    """Extract the executable function body from an _impl.py file.

    Returns the dedented body (everything after the def line and docstring),
    or None if the file is a stub (contains NotImplementedError) or has no
    function definition.
    """
    text = impl_path.read_text()

    if "raise NotImplementedError" in text:
        return None

    lines = text.split("\n")

    # Find the function definition
    func_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("def run_"):
            func_start = i
            break

    if func_start is None:
        return None

    # Extract body: everything after the def line
    body_lines = lines[func_start + 1 :]

    # Skip docstring
    in_docstring = False
    body_start = 0
    for i, line in enumerate(body_lines):
        stripped = line.strip()
        if not in_docstring and stripped.startswith('"""'):
            if stripped.endswith('"""') and len(stripped) > 3:
                # Single-line docstring
                body_start = i + 1
                continue
            in_docstring = True
            continue
        if in_docstring:
            if '"""' in stripped:
                in_docstring = False
                body_start = i + 1
                continue
            continue
        body_start = i
        break

    body_lines = body_lines[body_start:]

    body = textwrap.dedent("\n".join(body_lines)).strip()
    if not body:
        return None

    return body


def execute_impl_body(
    body: str,
    input_dict: dict[str, float],
    output_names: list[str],
) -> dict[str, float]:
    """Execute an impl function body with given inputs.

    Wraps the body in a function definition, executes it with a
    SimpleNamespace as the 'inputs' argument, and returns the output
    values as a dict.

    Handles both single-value returns (mapped to first output name)
    and tuple returns (mapped to output names in order).
    """
    inputs_ns = SimpleNamespace(**input_dict)

    func_code = f"def _fn(inputs):\n{textwrap.indent(body, '    ')}"
    func_globals: dict = {}
    exec(func_code, func_globals)  # noqa: S102

    result = func_globals["_fn"](inputs_ns)

    outputs: dict[str, float] = {}
    if isinstance(result, tuple):
        for i, name in enumerate(output_names):
            if i < len(result):
                outputs[name] = result[i]
    elif result is not None:
        if len(output_names) >= 1:
            outputs[output_names[0]] = result

    return outputs


def assert_outputs_match(
    actual: dict[str, float],
    expected: dict[str, float],
    tolerance: float = 1e-10,
) -> None:
    """Assert all outputs match within relative tolerance.

    Raises AssertionError with a detailed message on mismatch.
    """
    for name, expected_val in expected.items():
        assert name in actual, (
            f"Missing output '{name}': got keys {list(actual.keys())}"
        )
        actual_val = actual[name]

        if expected_val == 0.0 and actual_val == 0.0:
            rel_error = 0.0
        elif expected_val == 0.0:
            rel_error = abs(actual_val)
        else:
            rel_error = abs(actual_val - expected_val) / abs(expected_val)

        assert rel_error < tolerance, (
            f"Output '{name}' mismatch: "
            f"actual={actual_val}, expected={expected_val}, "
            f"rel_error={rel_error:.2e} (tolerance={tolerance:.0e})"
        )
