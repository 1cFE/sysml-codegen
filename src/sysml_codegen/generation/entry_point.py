"""Entry point schema and JSON generation for pipeline inputs.

Generates:
- Parameter group Pydantic schemas containing entry point parameters
- JSON files with default values for all parameters
"""

import json
import logging
from pathlib import Path
from typing import Any

import jinja2

# UPDATED: Import from sysml_codegen package
from sysml_codegen.extraction.data_models import AttributeInfo, CalculationDefinitionData

logger = logging.getLogger(__name__)


def collect_entry_point_attributes(
    calc_defs: list[CalculationDefinitionData],
    calc_usages: list | None = None,
) -> list[AttributeInfo]:
    """Collect full AttributeInfo for entry points (not just names/types).

    Entry points are input parameters that are not produced by any calculation
    definition output. Uses 2-pass algorithm to identify them.

    Args:
        calc_defs: All calculation definitions from SysML extraction
        calc_usages: Optional list of calc usages. If provided, only outputs from
                     calc defs with usages are considered "produced".

    Returns:
        List of AttributeInfo objects for parameters not produced by any module,
        deduplicated by name (keeping first occurrence)
    """
    # Pass 1: Collect output attribute names (only from used calc defs if usages provided)
    output_names = set()

    if calc_usages is not None:
        # Only consider outputs from calc defs that have usages
        used_calc_def_names = {u.calc_def_name for u in calc_usages}
        used_calc_defs = [cd for cd in calc_defs if cd.name in used_calc_def_names]
    else:
        used_calc_defs = calc_defs

    for calc_def in used_calc_defs:
        for output_attr in calc_def.output_attributes:
            output_names.add(output_attr.name)

    # Pass 2: Collect input attributes not in outputs
    entry_attrs_dict: dict[str, AttributeInfo] = {}
    for calc_def in calc_defs:
        for input_attr in calc_def.input_attributes:
            # Skip if this input is produced by some output
            if input_attr.name in output_names:
                continue

            # Add to entry points if not already seen (deduplication)
            if input_attr.name not in entry_attrs_dict:
                entry_attrs_dict[input_attr.name] = input_attr
            else:
                # Log warning about duplicate
                existing = entry_attrs_dict[input_attr.name]
                logger.warning(
                    f"Duplicate entry point '{input_attr.name}' found in "
                    f"{calc_def.source_file}:{calc_def.source_line} "
                    f"(already defined in {existing.source_line}). "
                    f"Keeping first occurrence."
                )

    return list(entry_attrs_dict.values())


def _map_input_type(sysml_type: str) -> str:
    """Map SysML type to Python primitive for input fields.

    Args:
        sysml_type: SysML type string (e.g., "Real", "Integer")

    Returns:
        Python type string (e.g., "float", "int")
    """
    type_map = {
        "Real": "float",
        "Integer": "int",
        "String": "str",
        "Boolean": "bool",
    }

    if sysml_type in type_map:
        return type_map[sysml_type]
    else:
        logger.warning(
            f"Unknown SysML type '{sysml_type}', defaulting to 'float'. "
            f"Consider adding explicit mapping."
        )
        return "float"


def generate_entry_point_schema(
    entry_attrs: list[AttributeInfo],
    template_env: jinja2.Environment,
    output_path: Path,
    schema_class_name: str = "FusionParams",
) -> str:
    """Generate Pydantic schema from entry point attributes.

    Args:
        entry_attrs: Entry point attributes with full metadata
        template_env: Jinja2 environment with templates loaded
        output_path: Output file path (for reference/logging)
        schema_class_name: Name for the schema class (parameterized)

    Returns:
        Generated Python code string for the schema
    """
    # Build field list from AttributeInfo objects
    fields: list[dict[str, Any]] = []
    sysml_sources = set()

    for attr in entry_attrs:
        # Map SysML type to Python type
        python_type = _map_input_type(attr.sysml_type)

        # Extract default value if available
        default_value: Any = None
        if attr.default_value is not None:
            raw_default = attr.default_value
            # Check if it's already the right type
            if isinstance(raw_default, (int, float, bool)):
                default_value = raw_default
            elif isinstance(raw_default, str) and raw_default.strip():
                # Legacy string handling - parse to correct type
                try:
                    if python_type == "float":
                        default_value = float(raw_default)
                    elif python_type == "int":
                        default_value = int(raw_default)
                    elif python_type == "bool":
                        default_value = raw_default.lower() in ("true", "1")
                    else:
                        default_value = raw_default
                except (ValueError, AttributeError) as e:
                    logger.warning(
                        f"Failed to parse default value '{raw_default}' "
                        f"for attribute '{attr.name}': {e}. Using None."
                    )
                    default_value = None

        # Build field dict
        field: dict[str, Any] = {
            "name": attr.name,
            "type": python_type,
            "description": attr.description or f"Parameter {attr.name}",
            "default": default_value,
            "constraints": {},
        }
        fields.append(field)

        # Track source file for traceability
        if attr.source_line > 0:
            sysml_sources.add(f"{attr.source_line}")

    # Build template context
    context = {
        "class_name": schema_class_name,
        "doc_comment": f"{schema_class_name} input parameters.\n\nGenerated from SysML calculation definitions.",
        "fields": fields,
        "sysml_sources": sorted(list(sysml_sources)) if sysml_sources else ["Multiple sources"],
    }

    # Render template
    template = template_env.get_template("entry_point_schema.py.jinja2")
    schema_code = template.render(**context)

    # Ensure final newline (PEP 8)
    if not schema_code.endswith("\n"):
        schema_code += "\n"

    logger.info(
        f"Generated entry point schema with {len(fields)} parameters: {output_path}"
    )

    return schema_code


def generate_input_json(
    entry_attrs: list[AttributeInfo],
    output_path: Path,
) -> str:
    """Generate baseline JSON input file from entry point attributes.

    Args:
        entry_attrs: Entry point attributes with default values
        output_path: Output file path

    Returns:
        JSON string with all parameters and defaults
    """
    # Build dictionary from entry attributes
    data = {}
    for attr in entry_attrs:
        json_value = _extract_json_value(attr)
        data[attr.name] = json_value

    # Render JSON with sorted keys for deterministic output
    json_content = json.dumps(data, indent=2, sort_keys=True)

    # Ensure final newline
    if not json_content.endswith("\n"):
        json_content += "\n"

    logger.info(
        f"Generated baseline JSON with {len(data)} parameters: {output_path}"
    )

    return json_content


def _extract_json_value(attr: AttributeInfo) -> Any:
    """Extract JSON-serializable value from AttributeInfo.

    Args:
        attr: Attribute with default_value field

    Returns:
        JSON-serializable value or None if no default
    """
    # Handle None
    if attr.default_value is None:
        return None

    raw_default = attr.default_value

    # Check if it's already the right type
    if isinstance(raw_default, (int, float, bool)):
        return raw_default

    # Handle empty string
    if isinstance(raw_default, str) and not raw_default.strip():
        return None

    # Map Python type for conversion
    python_type = _map_input_type(attr.sysml_type)

    try:
        # Convert based on Python type
        if python_type == "float":
            return float(raw_default)
        elif python_type == "int":
            return int(raw_default)
        elif python_type == "bool":
            # Handle boolean strings
            lower_val = raw_default.lower()
            if lower_val in ("true", "1"):
                return True
            elif lower_val in ("false", "0"):
                return False
            else:
                logger.warning(
                    f"Invalid boolean value '{raw_default}' for "
                    f"attribute '{attr.name}'. Using None."
                )
                return None
        else:
            # String type - return as-is
            return raw_default
    except (ValueError, AttributeError) as e:
        logger.warning(
            f"Failed to convert default value '{raw_default}' "
            f"for attribute '{attr.name}' to {python_type}: {e}. Using None."
        )
        return None


def generate_inputs_readme(
    parameter_groups: list,  # List[DerivedParameterGroup]
    package_name: str = "generated_code",
) -> str:
    """Generate README.md for the inputs directory.

    Dynamically generates documentation based on actual parameter groups
    derived from SysML models. No hardcoded values.

    Args:
        parameter_groups: List of DerivedParameterGroup from ParameterGroupDeriver
        package_name: Package name (parameterized)

    Returns:
        README.md content as string
    """
    # Count total parameters
    total_params = sum(len(g.parameters) for g in parameter_groups)

    # Build README content
    readme = [
        "# Input Parameters",
        "",
        "This directory contains input parameter files for the simulation pipeline.",
        "Parameters are extracted from SysML design files via Phase B code generation.",
        "",
        "## Files",
        "",
        f"Parameters are organized into **{len(parameter_groups)} JSON files**:",
        "",
        "| File | Schema Class | Parameters |",
        "|------|--------------|------------|",
    ]

    # Add file table dynamically
    for group in parameter_groups:
        readme.append(
            f"| `{group.name}.json` | `{group.class_name}` | {len(group.parameters)} |"
        )

    readme.extend(
        [
            "",
            "## Overview",
            "",
            f"The input files contain **{total_params} parameters** extracted from",
            "the SysML models. These parameters represent the entry points to the simulation",
            "pipeline - values that must be provided externally and are not computed by any",
            "internal calculation module.",
            "",
            "## Usage",
            "",
            "### Loading Parameters",
            "",
        ]
    )

    # Add dynamic usage example using first group (if available)
    if parameter_groups:
        first = parameter_groups[0]
        readme.extend(
            [
                "To load parameters from a group:",
                "",
                "```python",
                "import json",
                f"from {package_name}.schemas.{first.name} import {first.class_name}",
                "",
                "# Load JSON file",
                f'with open("{package_name}/inputs/{first.name}.json") as f:',
                "    data = json.load(f)",
                "",
                "# Validate against schema",
                f"params = {first.class_name}(**data)",
                "```",
                "",
            ]
        )

    readme.extend(
        [
            "### Creating Custom Scenarios",
            "",
            "To create a custom scenario:",
            "",
            "1. Copy the JSON files to new files (e.g., `high_power_plasma_params.json`)",
            "2. Edit the parameter values in the new files",
            "3. Update the pipeline YAML to reference your new files",
            "",
            "## Schema Reference",
            "",
            "For complete parameter definitions, constraints, and types, see:",
            "",
            f"- `{package_name}/schemas/*_params.py` - Pydantic schemas with full type information",
            "",
            "## Notes",
            "",
            "- Parameters are grouped by their source (design file or library package)",
            "- Parameters with `null` values require explicit values before pipeline execution",
            "- The schemas enforce type validation and constraints at runtime",
            "- Files are generated by code generation scripts",
            "",
        ]
    )

    return "\n".join(readme)


def generate_derived_group_schema(
    group,  # DerivedParameterGroup
    template_env: jinja2.Environment,
    output_path: Path,
) -> str:
    """Generate Pydantic schema for a derived parameter group.

    Args:
        group: DerivedParameterGroup with parameters and defaults
        template_env: Jinja2 environment with templates loaded
        output_path: Output file path (for reference/logging)

    Returns:
        Generated Python code string for the schema
    """
    # Build field list from ParameterSource objects
    fields: list[dict[str, Any]] = []

    for param in group.parameters:
        # Map SysML type to Python type
        python_type = _map_input_type(param.sysml_type)

        # Build field dict with default from derivation
        field: dict[str, Any] = {
            "name": param.name,
            "type": python_type,
            "description": param.description or f"Parameter {param.name}",
            "default": param.default_value,
        }
        fields.append(field)

    # Build description based on source type
    if group.source_type == "design":
        description = f"Parameters from {group.source_identifier}.\n\nSource Type: Design file"
    else:
        description = f"Parameters from library {group.source_identifier}.\n\nSource Type: Library (no defaults)"

    # Build template context
    context = {
        "class_name": group.class_name,
        "description": description,
        "fields": fields,
    }

    # Render template
    template = template_env.get_template("parameter_group_schema.py.jinja2")
    schema_code = template.render(**context)

    # Ensure final newline (PEP 8)
    if not schema_code.endswith("\n"):
        schema_code += "\n"

    logger.info(
        f"Generated derived schema '{group.class_name}' with {len(fields)} parameters: {output_path}"
    )

    return schema_code


def generate_derived_group_json(
    group,  # DerivedParameterGroup
    output_path: Path,
) -> str:
    """Generate JSON input file for a derived parameter group.

    Args:
        group: DerivedParameterGroup with parameters and defaults
        output_path: Output file path (for reference/logging)

    Returns:
        JSON string with all parameters and their defaults
    """
    # Build dictionary from parameters
    data = {}
    for param in group.parameters:
        data[param.name] = param.default_value

    # Render JSON with sorted keys for deterministic output
    json_content = json.dumps(data, indent=2, sort_keys=True)

    # Ensure final newline
    if not json_content.endswith("\n"):
        json_content += "\n"

    logger.info(
        f"Generated derived JSON '{group.name}' with {len(data)} parameters: {output_path}"
    )

    return json_content


def generate_all_derived_schemas(
    groups: list,  # List[DerivedParameterGroup]
    template_env: jinja2.Environment,
    output_dir: Path,
) -> list[str]:
    """Generate Pydantic schemas for all derived parameter groups.

    Args:
        groups: List of DerivedParameterGroup from derivation
        template_env: Jinja2 environment with templates loaded
        output_dir: Output directory (package root)

    Returns:
        List of generated file paths
    """
    generated_files = []
    schemas_dir = output_dir / "schemas"
    schemas_dir.mkdir(parents=True, exist_ok=True)

    for group in groups:
        schema_path = schemas_dir / f"{group.name}.py"
        content = generate_derived_group_schema(group, template_env, schema_path)

        # Write to file
        schema_path.write_text(content)
        generated_files.append(str(schema_path))

    logger.info(f"Generated {len(generated_files)} derived parameter group schemas")
    return generated_files


def generate_all_derived_jsons(
    groups: list,  # List[DerivedParameterGroup]
    output_dir: Path,
) -> list[str]:
    """Generate JSON input files for all derived parameter groups.

    Args:
        groups: List of DerivedParameterGroup from derivation
        output_dir: Output directory (package root)

    Returns:
        List of generated file paths
    """
    generated_files = []
    inputs_dir = output_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)

    for group in groups:
        json_path = inputs_dir / f"{group.name}.json"
        content = generate_derived_group_json(group, json_path)

        # Write to file
        json_path.write_text(content)
        generated_files.append(str(json_path))

    logger.info(f"Generated {len(generated_files)} derived parameter group JSON files")
    return generated_files


def generate_all_derived_schemas_from_graph(
    entry_point_groups: list,  # list[models.ParameterGroup]
    template_env: jinja2.Environment,
    output_dir: Path,
) -> list[Path]:
    """Generate Pydantic schema files from ComputationGraph entry_point_groups.

    Args:
        entry_point_groups: ParameterGroup list from ComputationGraph
        template_env: Jinja2 environment with templates loaded
        output_dir: Output directory (schemas/ subdirectory will be used)

    Returns:
        List of generated schema file paths
    """
    schemas_dir = output_dir / "schemas"
    schemas_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []
    for group in entry_point_groups:
        # Build field list from EntryPoint objects
        fields: list[dict[str, Any]] = []
        for ep in group.parameters:
            field: dict[str, Any] = {
                "name": ep.qualified_name,
                "type": "float",  # All entry points are numeric
                "description": f"Entry point: {ep.simple_name}",
                "default": ep.default_value,
            }
            fields.append(field)

        # Build description from source file
        description = f"Parameters from {group.source_file}."

        # Build template context
        context = {
            "class_name": group.class_name,
            "description": description,
            "fields": fields,
        }

        # Render template
        template = template_env.get_template("parameter_group_schema.py.jinja2")
        content = template.render(**context)

        # Ensure final newline (PEP 8)
        if not content.endswith("\n"):
            content += "\n"

        output_path = schemas_dir / f"{group.name}.py"
        output_path.write_text(content)
        generated_files.append(output_path)

    logger.info(f"Generated {len(generated_files)} parameter group schemas from graph")
    return generated_files


def generate_all_derived_jsons_from_graph(
    entry_point_groups: list,  # list[models.ParameterGroup]
    output_dir: Path,
) -> list[Path]:
    """Generate JSON input files from ComputationGraph entry_point_groups.

    Args:
        entry_point_groups: ParameterGroup list from ComputationGraph
        output_dir: Output directory (inputs/ subdirectory will be used)

    Returns:
        List of generated JSON file paths
    """
    inputs_dir = output_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []
    for group in entry_point_groups:
        # Build dictionary from EntryPoint objects
        data = {}
        for ep in group.parameters:
            if ep.default_value is not None:
                data[ep.qualified_name] = ep.default_value

        # Render JSON with sorted keys for deterministic output
        json_content = json.dumps(data, indent=2, sort_keys=True)

        # Ensure final newline
        if not json_content.endswith("\n"):
            json_content += "\n"

        output_path = inputs_dir / f"{group.name}.json"
        output_path.write_text(json_content)
        generated_files.append(output_path)

    logger.info(f"Generated {len(generated_files)} JSON templates from graph")
    return generated_files


__all__ = [
    "collect_entry_point_attributes",
    "generate_all_derived_jsons",
    "generate_all_derived_jsons_from_graph",
    "generate_all_derived_schemas",
    "generate_all_derived_schemas_from_graph",
    "generate_derived_group_json",
    "generate_derived_group_schema",
    "generate_entry_point_schema",
    "generate_input_json",
    "generate_inputs_readme",
]
