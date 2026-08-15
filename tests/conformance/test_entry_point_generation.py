"""Current entry-point schema/JSON bytes do not consume exact unit text."""

from __future__ import annotations

from pathlib import Path

from sysml_codegen.cli import _get_template_env
from sysml_codegen.generation.entry_point import (
    generate_all_derived_jsons,
    generate_all_derived_schemas,
)
from sysml_codegen.resolution.models import EntryPoint, EntryPointType, ParameterGroup


def _outputs(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_entry_point_unit_text_does_not_change_generated_schema_or_json(
    tmp_path: Path,
) -> None:
    group = ParameterGroup(
        name="design_params",
        class_name="DesignParams",
        source_file=Path("design.sysml"),
        parameters=[
            EntryPoint(
                qualified_name="Package__plant__length",
                simple_name="length",
                entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                default_value=1.0,
                python_type="float",
                unit_text="m",
            )
        ],
    )
    changed = group.model_copy(deep=True)
    changed.parameters[0].unit_text = "cm"
    first = tmp_path / "metres"
    second = tmp_path / "centimetres"

    generate_all_derived_schemas([group], _get_template_env(), first)
    generate_all_derived_jsons([group], first)
    generate_all_derived_schemas([changed], _get_template_env(), second)
    generate_all_derived_jsons([changed], second)

    assert _outputs(first) == _outputs(second)
    assert sorted(_outputs(first)) == [
        "inputs/design_params.json",
        "schemas/design_params.py",
    ]
