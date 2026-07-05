"""Signature extraction and comparison for implementation preservation.

This module provides utilities to extract function signatures from existing
implementation files and generate expected signatures from SysML data,
enabling smart preservation of handwritten implementations during code regeneration.
"""

import ast
from dataclasses import dataclass
from pathlib import Path

# UPDATED: Import from sysml_codegen package
from sysml_codegen.extraction.data_models import CalculationDefinitionData


@dataclass
class FunctionSignature:
    """Represents a function signature for comparison.

    Used to compare existing implementation signatures with expected signatures
    generated from SysML models. Enables detection of interface changes.

    Attributes:
        function_name: Name of function (e.g., 'run_alphaneutronsplit')
        input_type: Type annotation of inputs parameter (e.g., 'AlphaNeutronSplitInput')
        return_type: Return type annotation (e.g., 'tuple[float, float]' or 'float')
        input_fields: List of field names on Input class (for detailed comparison)
    """

    function_name: str
    input_type: str
    return_type: str
    input_fields: list[str] | None = None

    def matches(self, other: "FunctionSignature") -> bool:
        """Check if signatures are compatible.

        Compares function name, input type, return type, and input fields
        to determine if two signatures represent the same interface.

        When input_fields is None on either side (legacy files or unmodified
        stubs), field comparison is skipped and only type-level checks apply.

        Args:
            other: Signature to compare against

        Returns:
            True if signatures match (same interface), False otherwise
        """
        if not (
            self.function_name == other.function_name
            and self.input_type == other.input_type
            and self.return_type == other.return_type
        ):
            return False

        # Field-level comparison when both sides have field info
        if self.input_fields is not None and other.input_fields is not None:
            return sorted(self.input_fields) == sorted(other.input_fields)

        # Graceful fallback: no field info on one/both sides
        return True


class FunctionSignatureVisitor(ast.NodeVisitor):
    """AST visitor to extract function signature.

    Visits function definitions and extracts signature information from
    run_* functions in implementation files.
    """

    def __init__(self):
        """Initialize visitor with empty signature."""
        self.signature: FunctionSignature | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition and extract signature if it's a run_* function.

        Args:
            node: AST FunctionDef node to visit
        """
        if node.name.startswith("run_"):
            # Extract function name
            func_name = node.name

            # Extract input parameter type (first parameter should be 'inputs')
            if len(node.args.args) > 0:
                first_param = node.args.args[0]
                input_type = self._extract_annotation(first_param.annotation)
            else:
                input_type = "Unknown"

            # Extract return type
            return_type = self._extract_annotation(node.returns)

            # Extract input field references from function body
            input_fields = self._extract_input_field_refs(node)

            self.signature = FunctionSignature(
                function_name=func_name,
                input_type=input_type,
                return_type=return_type,
                input_fields=input_fields if input_fields else None,
            )

        self.generic_visit(node)

    def _extract_annotation(self, annotation) -> str:
        """Extract type annotation as string.

        Converts AST annotation node to string representation.

        Args:
            annotation: AST annotation node (can be None)

        Returns:
            String representation of type (e.g., 'tuple[float, float]')
            or 'Unknown' if annotation is missing
        """
        if annotation is None:
            return "Unknown"

        return ast.unparse(annotation)

    def _extract_input_field_refs(self, func_node: ast.FunctionDef) -> list[str]:
        """Extract input field names referenced in function body.

        Walks the function body AST to find ``inputs.X`` attribute accesses,
        revealing which input fields the implementation actually uses.

        Args:
            func_node: AST node for the run_* function

        Returns:
            Sorted list of field names, or empty list if none found
        """
        fields: set[str] = set()
        for node in ast.walk(func_node):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id == "inputs"
            ):
                fields.add(node.attr)
        return sorted(fields)


def extract_signature_from_impl(impl_path: Path) -> FunctionSignature | None:
    """Extract function signature from implementation file.

    Parses Python source using AST to find run_* function and extract signature.
    Used to compare existing implementations with expected signatures.

    Args:
        impl_path: Path to *_impl.py file

    Returns:
        FunctionSignature if found and parseable, None otherwise

    Example:
        >>> sig = extract_signature_from_impl(Path("package/handwritten/alphaneutronsplit_impl.py"))
        >>> sig.function_name
        'run_alphaneutronsplit'
        >>> sig.input_type
        'AlphaNeutronSplitInput'
        >>> sig.return_type
        'tuple[float, float]'
    """
    if not impl_path.exists():
        return None

    try:
        source = impl_path.read_text()
        tree = ast.parse(source)

        # Find run_* function using visitor
        visitor = FunctionSignatureVisitor()
        visitor.visit(tree)

        if visitor.signature:
            return visitor.signature
        else:
            return None

    except SyntaxError as e:
        # File has syntax errors - can't parse
        print(f"        Warning: Could not parse {impl_path.name}: {e}")
        return None
    except Exception as e:
        # Other errors - log and return None
        print(f"        Warning: Error reading {impl_path.name}: {e}")
        return None


def generate_expected_signature(calc_def: CalculationDefinitionData) -> FunctionSignature:
    """Generate expected function signature from calculation definition.

    Creates signature based on SysML data - what the generated stencil will have.
    Used to compare against existing implementations to detect interface changes.

    Args:
        calc_def: Calculation definition from SysML

    Returns:
        Expected function signature

    Example:
        >>> sig = generate_expected_signature(calc_def)
        >>> sig.function_name
        'run_alphaneutronsplit'
        >>> sig.return_type
        'tuple[float, float]'
    """
    # Function name: run_{module_name_lower}
    func_name = f"run_{calc_def.name.lower()}"

    # Input type: {Module}Input
    input_type = f"{calc_def.name}Input"

    # Return type based on output count
    output_count = len(calc_def.output_attributes)
    if output_count == 0:
        return_type = "None"
    elif output_count == 1:
        return_type = "float"
    else:
        # Multiple outputs - tuple[float, float, ...]
        return_types = ", ".join(["float"] * output_count)
        return_type = f"tuple[{return_types}]"

    # Extract input field names for detailed comparison (optional)
    input_fields = [attr.name for attr in calc_def.input_attributes]

    return FunctionSignature(
        function_name=func_name,
        input_type=input_type,
        return_type=return_type,
        input_fields=input_fields,
    )


__all__ = [
    "FunctionSignature",
    "FunctionSignatureVisitor",
    "extract_signature_from_impl",
    "generate_expected_signature",
]
