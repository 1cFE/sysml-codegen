"""Test generator for implementation stencils.

Generates runnable unit tests that verify handwritten implementation functions
can be imported, called with sample inputs, and return correct types.

Usage:
    from sysml_codegen.generation.test_gen import generate_test_implementations

    code = generate_test_implementations(graph, package_name, template_env, output_path)
"""

import logging
from pathlib import Path

import jinja2

from sysml_codegen.core.identifier_types import PythonModulePath, SysMLQualifiedName

logger = logging.getLogger(__name__)


def generate_test_implementations(
    graph,
    package_name: str,
    template_env: jinja2.Environment,
    output_path: Path,
) -> str:
    """Generate test file from ComputationGraph.

    Only generates tests for CalcUsage modules (not FORMULA or aggregation),
    matching historical behavior.

    Args:
        graph: ComputationGraph with modules
        package_name: Package name (parameterized)
        template_env: Jinja2 environment with templates loaded
        output_path: Output file path (for logging, not written here)

    Returns:
        Generated Python test code string
    """
    from sysml_codegen.resolution.models import ModuleKind

    modules = []
    calc_count = 0

    for module in graph.modules:
        # Skip FORMULA, aggregation, and constraint/report-aggregator modules (D8:
        # fully generated, no handwritten implementation to test).
        if module.module_kind in (
            ModuleKind.FORMULA,
            ModuleKind.AGGREGATION,
            ModuleKind.CONSTRAINT,
            ModuleKind.REPORT_AGGREGATOR,
        ):
            continue

        calc_count += 1

        # source_file is already the portable root-N/ referent (Item 5 D1); render
        # it directly. Branch C's "models/"-strip / basename fallback is deleted.
        source_path = str(module.source_file or "unknown")

        is_multi = len(module.outputs) >= 2
        output_count = len(module.outputs)

        # ADR-003: Derive namespaced import paths
        sqn = SysMLQualifiedName(module.calc_def_qualified_name)
        python_path = PythonModulePath.from_sysml(sqn)
        module_import_path = python_path.import_path
        impl_import_path = python_path.impl_import_path

        modules.append(
            {
                "name": module.calc_def_name.lower(),
                "class_name": module.calc_def_name,
                "function": f"run_{module.calc_def_name.lower()}",
                "source": f"{source_path}:{module.source_line}",
                "is_multi_output": is_multi,
                "output_count": output_count,
                "module_import_path": module_import_path,
                "impl_import_path": impl_import_path,
            }
        )

    template = template_env.get_template("test_implementations.py.jinja2")
    content = template.render(
        package_name=package_name,
        modules=modules,
        calc_count=calc_count,
    )

    if not content.endswith("\n"):
        content += "\n"

    logger.info(f"Generated test file with {len(modules)} test classes")
    return content


# Keep old name as alias for backward compatibility during transition
generate_test_implementations_from_graph = generate_test_implementations


__all__ = [
    "generate_test_implementations",
    "generate_test_implementations_from_graph",
]
