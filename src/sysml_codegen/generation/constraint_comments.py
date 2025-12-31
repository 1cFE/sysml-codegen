"""Constraint Comment Generator for Schema Docstrings.

Converts extracted ConstraintData into inline docstring comments for
Pydantic schema field descriptions. Follows the first-field rule for
multi-field constraint placement.

Usage:
    from sysml_codegen.generation.constraint_comments import generate_field_constraint_comments
    from sysml_codegen.extraction.constraint_extractor import ConstraintData

    constraints = [...]  # List of ConstraintData from extractor
    output_fields = ["p_net", "p_alpha", "p_neutron"]
    comments = generate_field_constraint_comments(constraints, output_fields)
    # Returns: {"p_net": "Constraint: p_net > 0", ...}
"""

import re

# UPDATED: Import from sysml_codegen package
from sysml_codegen.extraction.constraint_extractor import ConstraintData

# Maximum expression length before truncation
MAX_EXPRESSION_LENGTH = 100


def generate_field_constraint_comments(
    constraints: list[ConstraintData],
    output_fields: list[str],
) -> dict[str, str]:
    """Generate constraint comments for output schema fields.

    Assigns each constraint to the first output field it references
    (first-field rule). Multiple constraints on the same field are
    combined with semicolons.

    Args:
        constraints: List of constraints for a calc def
        output_fields: Names of output fields in the schema

    Returns:
        Dict mapping field name to constraint comment string
    """
    if not constraints or not output_fields:
        return {}

    # Group constraints by their target field
    field_constraints: dict[str, list[ConstraintData]] = {}

    for constraint in constraints:
        target_field = _find_first_output_field(constraint, output_fields)
        if target_field:
            if target_field not in field_constraints:
                field_constraints[target_field] = []
            field_constraints[target_field].append(constraint)

    # Generate comment strings for each field
    result: dict[str, str] = {}

    for field_name, field_constraint_list in field_constraints.items():
        if len(field_constraint_list) == 1:
            # Single constraint: "Constraint: expr"
            result[field_name] = _format_constraint_comment(field_constraint_list[0])
        else:
            # Multiple constraints: "Constraints: expr1; expr2"
            comments = [
                _format_single_expression(c) for c in field_constraint_list
            ]
            result[field_name] = f"Constraints: {'; '.join(comments)}"

    return result


def _format_constraint_comment(constraint: ConstraintData) -> str:
    """Format single constraint for docstring.

    Returns:
        "Constraint: {expression}" or "Constraint ({name}): {expression}"
    """
    expr = _truncate_expression(constraint.expression)

    if constraint.name:
        return f"Constraint ({constraint.name}): {expr}"
    else:
        return f"Constraint: {expr}"


def _format_single_expression(constraint: ConstraintData) -> str:
    """Format a constraint's expression for multi-constraint fields.

    Returns:
        "{expression}" or "({name}) {expression}"
    """
    expr = _truncate_expression(constraint.expression)

    if constraint.name:
        return f"({constraint.name}) {expr}"
    else:
        return expr


def _truncate_expression(expression: str) -> str:
    """Truncate long expressions with condition count.

    Args:
        expression: Full expression string

    Returns:
        Truncated expression with "... [N conditions]" suffix if too long
    """
    if len(expression) <= MAX_EXPRESSION_LENGTH:
        return expression

    # Count conditions (split by 'and' or 'or')
    conditions = re.split(r"\s+and\s+|\s+or\s+", expression, flags=re.IGNORECASE)
    num_conditions = len(conditions)

    # Truncate to max length, find a good break point
    truncated = expression[:MAX_EXPRESSION_LENGTH]

    # Try to break at a word boundary
    last_space = truncated.rfind(" ")
    if last_space > MAX_EXPRESSION_LENGTH // 2:
        truncated = truncated[:last_space]

    return f"{truncated}... [{num_conditions} conditions]"


def _find_first_output_field(
    constraint: ConstraintData,
    output_fields: list[str],
) -> str | None:
    """Find first output field referenced by constraint.

    Uses the first-field rule: the constraint is assigned to the
    first output field that appears in the expression text.

    Args:
        constraint: Constraint data with expression and referenced variables
        output_fields: Available output field names

    Returns:
        First matching output field name, or None if no match
    """
    # Convert output fields to set for O(1) lookup
    output_set = set(output_fields)

    # First, check referenced_variables in order (preserves expression order)
    for var in constraint.referenced_variables:
        if var in output_set:
            return var

    # Fallback: scan expression text for first match
    for field in output_fields:
        # Use word boundary to avoid partial matches
        pattern = rf"\b{re.escape(field)}\b"
        if re.search(pattern, constraint.expression):
            return field

    return None


__all__ = [
    "generate_field_constraint_comments",
]
