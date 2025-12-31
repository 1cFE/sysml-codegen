"""SysML Constraint Translator for Pydantic Validators.

This module translates SysML constraints into Pydantic validation code:
- Simple constraints (x > 0, 1 <= x <= 10) → Field() parameters (gt, ge, lt, le)
- Complex constraints (cross-field, output) → @model_validator methods or assertions
- Untranslatable constraints → Documented with SysML source for manual implementation
"""

import re
from dataclasses import dataclass
from typing import Any

import jinja2

# UPDATED: Import from sysml_codegen instead of scripts
from sysml_codegen.extraction.data_models import CalculationDefinitionData


@dataclass
class ConstraintInfo:
    """Represents a parsed SysML constraint with metadata."""

    name: str
    expression: str
    referenced_attributes: list[str]
    constraint_type: str  # 'input', 'output', 'cross-field'
    sysml_source: str  # file:line reference


@dataclass
class FieldConstraint:
    """Pydantic Field constraint parameters."""

    field_name: str
    gt: float | None = None  # Greater than
    ge: float | None = None  # Greater than or equal
    lt: float | None = None  # Less than
    le: float | None = None  # Less than or equal


def parse_constraints(calc_def: CalculationDefinitionData) -> list[ConstraintInfo]:
    """Extract and parse constraints from calc def.

    Args:
        calc_def: Calculation definition with constraints

    Returns:
        List of parsed constraints with metadata
    """
    constraints = []

    if not hasattr(calc_def, "constraints"):
        return []

    for constraint in calc_def.constraints:  # type: ignore[attr-defined]
        referenced_attrs = _extract_attribute_refs(constraint.expression)
        constraint_type = _classify_constraint(constraint, calc_def)

        info = ConstraintInfo(
            name=constraint.name,
            expression=constraint.expression,
            referenced_attributes=referenced_attrs,
            constraint_type=constraint_type,
            sysml_source=f"{constraint.source_file}:{constraint.line_number}",
        )
        constraints.append(info)

    return constraints


def translate_simple_constraint(constraint: ConstraintInfo) -> FieldConstraint | None:
    """Translate simple comparison to Field constraint."""
    if constraint.constraint_type != "input":
        return None

    if not _is_simple_comparison(constraint.expression):
        return None

    return _parse_simple_comparison(constraint)


def generate_field_constraints(
    calc_def: CalculationDefinitionData,
) -> dict[str, FieldConstraint]:
    """Generate Field constraints for input attributes.

    Args:
        calc_def: Calculation definition

    Returns:
        Dict mapping attribute name to FieldConstraint
    """
    constraints = parse_constraints(calc_def)
    field_constraints = {}

    for constraint in constraints:
        if constraint.constraint_type != "input":
            continue

        field_constraint = translate_simple_constraint(constraint)
        if field_constraint:
            field_constraints[field_constraint.field_name] = field_constraint

    return field_constraints


def generate_validator_code(
    constraint: ConstraintInfo, template_env: jinja2.Environment
) -> str:
    """Generate Pydantic @model_validator method for complex constraint."""
    readable_name = _to_title_case(constraint.name)

    context = {
        "method_name": f"check_{_to_snake_case(constraint.name)}",
        "constraint_name": readable_name,
        "sysml_source": constraint.sysml_source,
        "expression": constraint.expression,
        "python_expression": _translate_expression_to_python(constraint.expression),
    }

    template = template_env.get_template("constraint_validator.py.jinja2")
    return template.render(**context)


def generate_assertion_code(constraint: ConstraintInfo) -> str:
    """Generate assertion statement for module run() method."""
    return f"""# Constraint: {constraint.name} ({constraint.sysml_source})
# {constraint.expression}""".strip()


# ========== HELPER FUNCTIONS ==========


def _classify_constraint(constraint: Any, calc_def: CalculationDefinitionData) -> str:
    """Classify constraint as 'input', 'output', or 'cross-field'."""
    refs = _extract_attribute_refs(constraint.expression)

    has_input_refs = any(
        attr.name in refs for attr in calc_def.input_attributes
    )

    has_output_refs = any(
        attr.name in refs for attr in calc_def.output_attributes
    )

    if has_output_refs:
        return "cross-field" if has_input_refs else "output"
    return "input"


def _extract_attribute_refs(expression: str) -> list[str]:
    """Extract attribute names referenced in expression."""
    return re.findall(r"\b([a-z_][a-z0-9_]*)\b", expression)


def _is_simple_comparison(expression: str) -> bool:
    """Check if expression is simple comparison."""
    expr = expression.replace(" ", "")

    simple_patterns = [
        r"^[a-z_]\w*[<>]=?[\d.]+$",
        r"^[\d.]+[<>]=?[a-z_]\w*$",
        r"^[\d.]+[<>]=?[a-z_]\w*[<>]=?[\d.]+$",
    ]

    return any(re.match(pattern, expr) for pattern in simple_patterns)


def _parse_simple_comparison(constraint: ConstraintInfo) -> FieldConstraint | None:
    """Parse simple comparison expression to FieldConstraint."""
    expr = constraint.expression.replace(" ", "")

    if len(constraint.referenced_attributes) != 1:
        return None

    field_name = constraint.referenced_attributes[0]

    gt = None
    ge = None
    lt = None
    le = None

    range_match = re.match(
        r"^([\d.]+)([<>]=?)([a-z_]\w*)([<>]=?)([\d.]+)$", expr
    )
    if range_match:
        lower_val, lower_op, var, upper_op, upper_val = range_match.groups()

        if lower_op == "<=":
            ge = float(lower_val)
        elif lower_op == "<":
            gt = float(lower_val)

        if upper_op == "<=":
            le = float(upper_val)
        elif upper_op == "<":
            lt = float(upper_val)

        return FieldConstraint(
            field_name=field_name, gt=gt, ge=ge, lt=lt, le=le
        )

    single_match = re.match(r"^([a-z_]\w*|[\d.]+)([<>]=?)([a-z_]\w*|[\d.]+)$", expr)
    if single_match:
        left, op, right = single_match.groups()

        if left == field_name:
            value = float(right)
            if op == ">":
                gt = value
            elif op == ">=":
                ge = value
            elif op == "<":
                lt = value
            elif op == "<=":
                le = value
        else:
            value = float(left)
            if op == ">":
                lt = value
            elif op == ">=":
                le = value
            elif op == "<":
                gt = value
            elif op == "<=":
                ge = value

        return FieldConstraint(
            field_name=field_name, gt=gt, ge=ge, lt=lt, le=le
        )

    return None


def _translate_expression_to_python(expression: str) -> str:
    """Translate SysML expression to Python."""
    return expression


def _to_snake_case(name: str) -> str:
    """Convert CamelCase to snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def _to_title_case(name: str) -> str:
    """Convert CamelCase to Title Case with spaces."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1 \2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1 \2", s1)
    return s2.strip()


__all__ = [
    "ConstraintInfo",
    "FieldConstraint",
    "parse_constraints",
    "translate_simple_constraint",
    "generate_field_constraints",
    "generate_validator_code",
    "generate_assertion_code",
]
