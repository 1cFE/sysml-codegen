"""Preservation logic and backup functionality for smart regeneration.

This module provides decision logic for determining when to regenerate
implementation stencils and functionality to backup existing implementations
before regeneration.
"""

import ast
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FunctionSignature:
    """Represents a function signature for comparison.

    Used to compare existing implementation signatures with expected signatures
    generated from SysML models. Enables detection of interface changes.
    """

    function_name: str
    input_type: str
    return_type: str
    input_fields: list[str] | None = None

    def matches(self, other: "FunctionSignature") -> bool:
        """Check if signatures are compatible."""
        if not (
            self.function_name == other.function_name
            and self.input_type == other.input_type
            and self.return_type == other.return_type
        ):
            return False

        if self.input_fields is not None and other.input_fields is not None:
            return sorted(self.input_fields) == sorted(other.input_fields)

        return True


def _extract_signature_from_impl(impl_path: Path) -> FunctionSignature | None:
    """Extract function signature from implementation file.

    Parses Python source using AST to find run_* function and extract signature.
    Pure file parsing — no dependency on extraction or analysis models.

    Args:
        impl_path: Path to *_impl.py file

    Returns:
        FunctionSignature if found and parseable, None otherwise
    """
    if not impl_path.exists():
        return None

    try:
        source = impl_path.read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("run_"):
                # Extract input parameter type
                if len(node.args.args) > 0:
                    first_param = node.args.args[0]
                    input_type = (
                        ast.unparse(first_param.annotation)
                        if first_param.annotation
                        else "Unknown"
                    )
                else:
                    input_type = "Unknown"

                # Extract return type
                return_type = ast.unparse(node.returns) if node.returns else "Unknown"

                # Extract input field references
                fields: set[str] = set()
                for child in ast.walk(node):
                    if (
                        isinstance(child, ast.Attribute)
                        and isinstance(child.value, ast.Name)
                        and child.value.id == "inputs"
                    ):
                        fields.add(child.attr)

                return FunctionSignature(
                    function_name=node.name,
                    input_type=input_type,
                    return_type=return_type,
                    input_fields=sorted(fields) if fields else None,
                )

        return None

    except SyntaxError:
        # D3-14: a parse failure means we could not read the signature. Return
        # None and let the *caller* decide preserve-vs-regenerate by policy — a
        # non-empty impl that fails to parse is PRESERVED on this transient
        # error, not stubbed over. The broad `except Exception: return None` is
        # removed so a genuinely unexpected error propagates loudly.
        return None


def should_regenerate_stencil(
    module,
    impl_path: Path,
) -> tuple[bool, str]:
    """Determine if stencil should be regenerated.

    Uses PipelineModule fields to derive expected signature.
    Decision logic:
    1. File doesn't exist → regenerate (new module)
    2. Can't parse existing file → regenerate (syntax errors)
    3. Signature unchanged → preserve (no interface change)
    4. Signature changed → regenerate (interface changed)

    Args:
        module: PipelineModule with calc_def_name and inputs populated
        impl_path: Path to existing implementation file

    Returns:
        (should_regenerate, reason) tuple
    """
    if not impl_path.exists():
        return True, "New module (file doesn't exist)"

    existing_sig = _extract_signature_from_impl(impl_path)
    if existing_sig is None:
        # D3-14 (preserve-on-transient, INV-4). We could not extract a signature.
        # Policy at the call site: a transient read/parse error on a NON-EMPTY
        # impl must NOT stub over a valid handwritten implementation — preserve
        # it and warn. Only a genuinely-empty impl is safe to regenerate.
        try:
            content = impl_path.read_text()
        except OSError as exc:
            logger.warning(
                "Transient read error on %s (%s); preserving the existing "
                "implementation rather than regenerating a stub (D3-14).",
                impl_path,
                exc,
            )
            return False, "Preserved on transient read error"
        if content.strip():
            logger.warning(
                "Existing implementation %s is non-empty but its signature "
                "could not be parsed; preserving it (transient parse error — "
                "not overwriting a valid impl with a stub, D3-14).",
                impl_path,
            )
            return False, "Preserved (non-empty, unparseable — transient)"
        return True, "Empty implementation (nothing to preserve)"

    expected_sig = _generate_expected_signature_from_module(module)

    if existing_sig.matches(expected_sig):
        return False, "Signature unchanged"
    else:
        return True, "Signature changed (interface differs)"


def _generate_expected_signature_from_module(module) -> FunctionSignature:
    """Generate expected function signature from PipelineModule."""
    func_name = f"run_{module.calc_def_name.lower()}"
    input_type = f"{module.calc_def_name}Input"

    output_count = len(module.outputs)
    if output_count == 0:
        return_type = "None"
    elif output_count == 1:
        return_type = "float"
    else:
        return_types = ", ".join(["float"] * output_count)
        return_type = f"tuple[{return_types}]"

    input_fields = [inp.param_name for inp in module.inputs]

    return FunctionSignature(
        function_name=func_name,
        input_type=input_type,
        return_type=return_type,
        input_fields=input_fields,
    )


def backup_implementation(
    impl_path: Path,
    backup_dir: Path,
) -> Path:
    """Backup existing implementation before regeneration.

    Creates timestamped backup in backup directory.

    Args:
        impl_path: Path to implementation file to backup
        backup_dir: Directory to store backups

    Returns:
        Path to created backup file
    """
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = impl_path.stem
    backup_name = f"{stem}_{timestamp}.py"
    backup_path = backup_dir / backup_name

    shutil.copy2(impl_path, backup_path)

    return backup_path


__all__ = [
    "backup_implementation",
    "should_regenerate_stencil",
]
