"""Test generator for implementation stencils.

Generates runnable unit tests that verify handwritten implementation functions
can be imported, called with sample inputs, and return correct types.

Usage:
    from sysml_codegen.generation.test_gen import generate_test_implementations

    code = generate_test_implementations(calc_defs, package_name, template_env, output_path)
"""

import logging
from pathlib import Path

import jinja2

from sysml_codegen.core.identifier_types import PythonModulePath, SysMLQualifiedName

# UPDATED: Import from sysml_codegen package
from sysml_codegen.extraction.data_models import CalculationDefinitionData

logger = logging.getLogger(__name__)


def generate_test_implementations(
    calc_defs: list[CalculationDefinitionData],
    package_name: str,
    template_env: jinja2.Environment,
    output_path: Path,
) -> str:
    """Generate test file for all implementation stencils.

    ADR-003: Generates test imports using namespaced paths.

    Args:
        calc_defs: All calculation definitions from SysML extraction
        package_name: Package name (parameterized)
        template_env: Jinja2 environment with templates loaded
        output_path: Output file path (for logging, not written here)

    Returns:
        Generated Python test code string
    """
    # Build module metadata from calc_defs
    modules = []
    for calc_def in calc_defs:
        # Get source path for documentation
        source_file = calc_def.source_file
        if isinstance(source_file, Path):
            try:
                source_str = str(source_file)
                if "models/" in source_str:
                    source_path = "models/" + source_str.split("models/", 1)[1]
                else:
                    source_path = source_file.name
            except Exception:
                source_path = source_file.name
        else:
            source_path = str(source_file)

        # Determine if multi-output
        is_multi = len(calc_def.output_attributes) >= 2
        output_count = len(calc_def.output_attributes)

        # ADR-003: Derive namespaced import paths
        sqn = SysMLQualifiedName(calc_def.qualified_name)
        python_path = PythonModulePath.from_sysml(sqn)
        module_import_path = python_path.import_path
        impl_import_path = python_path.impl_import_path

        modules.append(
            {
                "name": calc_def.name.lower(),  # snake_case module name
                "class_name": calc_def.name,  # TitleCase class name
                "function": f"run_{calc_def.name.lower()}",
                "source": f"{source_path}:{calc_def.source_line}",
                "is_multi_output": is_multi,
                "output_count": output_count,
                "module_import_path": module_import_path,  # ADR-003
                "impl_import_path": impl_import_path,  # ADR-003
            }
        )

    # Render template
    template = template_env.get_template("test_implementations.py.jinja2")
    content = template.render(
        package_name=package_name,
        modules=modules,
        calc_count=len(calc_defs),
    )

    # Ensure final newline
    if not content.endswith("\n"):
        content += "\n"

    logger.info(f"Generated test file with {len(modules)} test classes")
    return content


__all__ = [
    "generate_test_implementations",
]
