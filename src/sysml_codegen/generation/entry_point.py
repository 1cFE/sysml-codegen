"""Entry point schema and JSON generation for pipeline inputs.

Generates from ComputationGraph entry_point_groups:
- Parameter group Pydantic schemas
- JSON files with default values for all parameters
"""

import json
import logging
from pathlib import Path
from typing import Any

import jinja2

from sysml_codegen.core.qualified_names import params_field_name
from sysml_codegen.resolution.models import ParameterGroup

logger = logging.getLogger(__name__)


def _refuse_colliding_field_names(group_label: str, fields: list[dict[str, Any]]) -> None:
    """Refuse a group whose keys sanitize onto one Python field name.

    Two distinct params keys must never share a field: the second declaration
    would silently replace the first and one modelled value would vanish from
    the schema. Only an indexed key is rewritten at all, so this can only fire
    when a model also declares the unindexed spelling — rare, and a genuine
    ambiguity the operator has to resolve in the model.
    """
    from sysml_codegen.core.errors import CodeGenerationError

    seen: dict[str, str] = {}
    for field in fields:
        name, alias = field["name"], field["alias"]
        prior = seen.get(name)
        if prior is not None and prior != alias:
            raise CodeGenerationError(
                f"PARAM_FIELD_COLLISION: parameter group {group_label!r}: keys "
                f"{prior!r} and {alias!r} both "
                f"render as the schema field {name!r} — rename one in the model"
            )
        seen[name] = alias


def generate_all_derived_schemas(
    entry_point_groups: list[ParameterGroup],
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
                "name": params_field_name(ep.qualified_name),
                "alias": ep.qualified_name,
                "type": getattr(ep, "python_type", "float"),
                "description": f"Entry point: {ep.simple_name}",
                "default": ep.default_value,
            }
            fields.append(field)
        _refuse_colliding_field_names(group.name, fields)

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


def generate_all_derived_jsons(
    entry_point_groups: list[ParameterGroup],
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
        # Every entry point in the group gets a key. An entry point with no
        # resolvable modeled default emits `null`, not nothing: omitting the key
        # made an unfilled parameter indistinguishable from one the user had
        # already supplied, and hid the omission behind a "field required" error
        # far from its cause (DD-R21, I7).
        data = {ep.qualified_name: ep.default_value for ep in group.parameters}

        # Render JSON with sorted keys for deterministic output
        json_content = json.dumps(data, indent=2, sort_keys=True, allow_nan=False)

        # Ensure final newline
        if not json_content.endswith("\n"):
            json_content += "\n"

        output_path = inputs_dir / f"{group.name}.json"
        output_path.write_text(json_content)
        generated_files.append(output_path)

    logger.info(f"Generated {len(generated_files)} JSON templates from graph")
    return generated_files


# Keep old names as aliases for backward compatibility during transition
generate_all_derived_schemas_from_graph = generate_all_derived_schemas
generate_all_derived_jsons_from_graph = generate_all_derived_jsons


__all__ = [
    "generate_all_derived_jsons",
    "generate_all_derived_jsons_from_graph",
    "generate_all_derived_schemas",
    "generate_all_derived_schemas_from_graph",
]
