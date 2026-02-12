"""CLI entry point for sysml-codegen.

CRITICAL CHANGES:
- Parameterized all hardcoded values
- Removed CATF-specific references
- Package name is now a CLI argument
- Added install-commands subcommand for TEAx completion helper
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import jinja2

if TYPE_CHECKING:
    from sysml_codegen.generation import PipelineContext

# Note: Heavy imports moved inside run_codegen to avoid loading generation
# module at CLI import time. This keeps CLI startup fast.

logger = logging.getLogger(__name__)


def _ensure_package_init_files(
    base_dir: Path, relative_path: str, docstring: str = '"""Namespace package."""\n'
) -> None:
    """Ensure __init__.py exists in all directories along relative_path."""
    parts = Path(relative_path).parts
    current = base_dir
    for part in parts:
        current = current / part
        init_file = current / "__init__.py"
        if not init_file.exists():
            init_file.write_text(docstring)

# Commands available for installation
CODEGEN_COMMANDS = [
    "teax-completion.md",
]


def get_commands_dir() -> Path:
    """Get path to bundled commands directory.

    Path calculation:
    - __file__ = sysml-codegen/src/sysml_codegen/cli/__init__.py
    - parent.parent.parent.parent = sysml-codegen/
    - result = sysml-codegen/claude/commands/
    """
    package_root = Path(__file__).parent.parent.parent.parent
    return package_root / "claude" / "commands"


@dataclass
class GenerationConfig:
    """Configuration for code generation."""

    models_path: Path
    output_path: Path
    package_name: str = "generated_code"  # Parameterized, was: fusion_simkit
    schema_class_name: str = "Params"  # Parameterized, was: FusionParams
    pipeline_name: str = "pipeline"  # Parameterized, was: catf_fusion
    overwrite: bool = False
    preserve_handwritten: bool = False
    smart_regen: bool = False
    design_path_filter: str = ""


def _clear_output_directory(config: GenerationConfig) -> None:
    """Clear existing output directory before regeneration.

    Respects preserve_handwritten flag to keep handwritten/ directory intact.
    """
    if not config.output_path.exists():
        return

    for item in config.output_path.iterdir():
        # Skip handwritten directory if preserve flag is set
        if config.preserve_handwritten and item.name == "handwritten":
            logger.debug("Preserving handwritten/ directory")
            continue

        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    logger.debug(f"Cleared output directory: {config.output_path}")


def _setup_output_directories(config: GenerationConfig) -> None:
    """Create output directory structure."""
    dirs = [
        config.output_path,
        config.output_path / "schemas",
        config.output_path / "modules",
        config.output_path / "handwritten",
        config.output_path / "pipelines",
        config.output_path / "inputs",
        config.output_path / "tests",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def _generate_primitives(config: GenerationConfig) -> None:
    """Generate primitives.py with RootModel wrappers."""
    content = '''"""Pydantic RootModel wrappers for primitive types."""
from pydantic import RootModel

Float = RootModel[float]
Int = RootModel[int]
String = RootModel[str]
Bool = RootModel[bool]

__all__ = ["Float", "Int", "String", "Bool"]
'''
    output_path = config.output_path / "primitives.py"
    output_path.write_text(content)
    logger.debug(f"Generated primitives: {output_path}")


def _get_template_env() -> jinja2.Environment:
    """Set up Jinja2 environment with package templates."""
    # Use __file__ to find templates relative to package
    template_dir = Path(__file__).parent.parent / "templates"
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _generate_schemas(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate Pydantic schemas using multioutput helper."""
    from sysml_codegen.generation import generate_multioutput_model, should_use_multioutput

    schemas_dir = config.output_path / "schemas"

    # Generate multi-output schemas
    multioutput_count = 0
    for calc_def in ctx.calc_defs:
        if should_use_multioutput(calc_def):
            output_path = schemas_dir / f"{calc_def.name.lower()}_output.py"
            code = generate_multioutput_model(
                calc_def,
                template_env,
                output_path,
                package_name=config.package_name,
            )
            if code:
                output_path.write_text(code)
                multioutput_count += 1
                logger.debug(f"Generated schema: {output_path.name}")

    logger.info(f"Generated {multioutput_count} multi-output schemas")


def _generate_modules(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate TEAx module wrappers (ADR-003 namespacing)."""
    from sysml_codegen.generation import generate_teax_module
    from sysml_codegen.resolution.identifier_types import PythonModulePath, SysMLQualifiedName

    modules_dir = config.output_path / "modules"
    module_count = 0

    for calc_def in ctx.calc_defs:
        # Skip calc_defs without outputs (can't generate meaningful module)
        if not calc_def.output_attributes:
            logger.debug(f"Skipping {calc_def.name}: no output attributes")
            continue

        # ADR-003: Derive nested path from qualified name
        sqn = SysMLQualifiedName(calc_def.qualified_name)
        python_path = PythonModulePath.from_sysml(sqn)

        # Create namespace subdirectory with __init__.py in all intermediates
        if python_path.directory:
            namespace_dir = modules_dir / python_path.directory
            namespace_dir.mkdir(parents=True, exist_ok=True)
            _ensure_package_init_files(
                modules_dir, python_path.directory,
                '"""Namespace package for generated modules."""\n',
            )

        output_path = modules_dir / python_path.full_path
        code = generate_teax_module(
            calc_def,
            template_env,
            output_path,
            config.package_name,
        )
        if code:
            output_path.write_text(code)
            module_count += 1
            logger.debug(f"Generated module: {output_path}")

    logger.info(f"Generated {module_count} TEAx module wrappers")


def _generate_computed_attr_modules(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate TEAx module wrappers for FORMULA computed attributes."""
    import re

    from sysml_codegen.core.identifier_types import (
        PythonModulePath,
        SysMLQualifiedName,
        derive_module_type,
    )
    from sysml_codegen.core.qualified_names import get_module_name, sysml_to_python_qualified_name
    from sysml_codegen.extraction.data_models import ComputedAttributeClassification
    from sysml_codegen.extraction.expression_compiler import Compilability

    modules_dir = config.output_path / "modules"
    module_count = 0

    for ca in ctx.computed_attributes:
        if (
            ca.classification != ComputedAttributeClassification.FORMULA
            or ca.compilability != Compilability.FULLY_COMPILABLE
        ):
            continue

        sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
        sqn = SysMLQualifiedName(sysml_qn)
        python_path = PythonModulePath.from_sysml(sqn)
        module_eqn = sysml_to_python_qualified_name(sysml_qn)

        # Create namespace subdirectory with __init__.py in all intermediates
        if python_path.directory:
            namespace_dir = modules_dir / python_path.directory
            namespace_dir.mkdir(parents=True, exist_ok=True)
            _ensure_package_init_files(
                modules_dir, python_path.directory,
                '"""Namespace package for generated modules."""\n',
            )

        # Extract input names from compiled expression
        if ca.compiled_expression is None:
            raise ValueError(
                f"FORMULA attr {ca.name} has no compiled_expression "
                f"(compilability={ca.compilability})"
            )
        raw_inputs = re.findall(r"inputs\.(\w+)", ca.compiled_expression)
        seen: set[str] = set()
        input_names: list[str] = []
        for name in raw_inputs:
            if name not in seen:
                seen.add(name)
                input_names.append(name)

        module_type_full = derive_module_type(sysml_qn)
        class_name = module_type_full.split(".")[-1]
        input_class_name = class_name.replace("Module", "Input")

        input_attributes = [
            {"name": n, "type_hint": "float", "description": f"Input {n}"}
            for n in input_names
        ]

        # Derive primitive imports from input types (matching modules.py pattern)
        primitive_types = set()
        for attr in input_attributes:
            if attr["type_hint"] in ("Float", "Int", "String", "Bool"):
                primitive_types.add(attr["type_hint"])
        primitive_types.add("Float")  # Output is always Float for computed attrs
        primitive_imports = sorted(primitive_types)

        context = {
            "class_name": class_name,
            "input_class_name": input_class_name,
            "output_class_name": None,
            "schema_name": None,
            "handler_name": get_module_name(module_eqn),
            "impl_import_path": python_path.impl_import_path,
            "doc_comment": (
                f"Computed attribute module.\n\n"
                f"SysML Expression: {ca.expression_text}"
            ),
            "package_name": config.package_name,
            "is_multioutput": False,
            "input_attributes": input_attributes,
            "output_attributes": [
                {"name": ca.python_name, "description": f"Computed {ca.name}"},
            ],
            "calc_expressions": [ca.expression_text],
            "sysml_source": f"{ca.source_file}:{ca.source_line}",
            "primitive_imports": primitive_imports,
        }

        template = template_env.get_template("teax_module.py.jinja2")
        code = template.render(**context)
        if not code.endswith('\n'):
            code += '\n'

        output_path = modules_dir / python_path.full_path
        output_path.write_text(code)
        module_count += 1
        logger.debug(f"Generated computed attr module: {output_path}")

    if module_count:
        logger.info(f"Generated {module_count} computed attribute module wrappers")


def _generate_computed_attr_stencils(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate auto-implementation files for FORMULA computed attributes."""
    from sysml_codegen.core.identifier_types import (
        PythonModulePath,
        SysMLQualifiedName,
        derive_module_type,
    )
    from sysml_codegen.core.qualified_names import get_module_name, sysml_to_python_qualified_name
    from sysml_codegen.extraction.data_models import ComputedAttributeClassification
    from sysml_codegen.extraction.expression_compiler import Compilability

    handwritten_dir = config.output_path / "handwritten"
    impl_count = 0

    for ca in ctx.computed_attributes:
        if (
            ca.classification != ComputedAttributeClassification.FORMULA
            or ca.compilability != Compilability.FULLY_COMPILABLE
        ):
            continue

        sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
        sqn = SysMLQualifiedName(sysml_qn)
        python_path = PythonModulePath.from_sysml(sqn)
        module_eqn = sysml_to_python_qualified_name(sysml_qn)
        module_type_full = derive_module_type(sysml_qn)
        class_name = module_type_full.split(".")[-1]
        input_class_name = class_name.replace("Module", "Input")

        # Create namespace subdirectory with __init__.py in all intermediates
        if python_path.directory:
            namespace_dir = handwritten_dir / python_path.directory
            namespace_dir.mkdir(parents=True, exist_ok=True)
            _ensure_package_init_files(
                handwritten_dir, python_path.directory,
                '"""Handwritten implementations."""\n',
            )
            output_path = namespace_dir / f"{python_path.filename}_impl.py"
        else:
            output_path = handwritten_dir / f"{python_path.filename}_impl.py"

        if ca.compiled_expression is None:
            raise ValueError(
                f"FORMULA attr {ca.name} has no compiled_expression "
                f"(compilability={ca.compilability})"
            )
        context = {
            "function_name": f"run_{get_module_name(module_eqn)}",
            "calc_name": module_eqn,
            "input_class_name": input_class_name,
            "return_type": "float",
            "execution_steps": [],
            "output_expressions": [
                {"name": ca.python_name, "expression": ca.compiled_expression},
            ],
            "output_count": 1,
            "single_output_expression": ca.compiled_expression,
            "module_import_path": python_path.import_path,
            "package_name": config.package_name,
            "sysml_source": f"{ca.source_file}:{ca.source_line}",
            "sysml_expressions": [ca.expression_text],
            "docstring": (
                f"Execute {ca.name} computed attribute.\n\n"
                f"SysML Expression: {ca.expression_text}"
            ),
        }

        template = template_env.get_template("auto_implementation.py.jinja2")
        code = template.render(**context)
        if not code.endswith('\n'):
            code += '\n'

        output_path.write_text(code)
        impl_count += 1
        logger.debug(f"Generated computed attr auto-impl: {output_path}")

    if impl_count:
        logger.info(
            f"Generated {impl_count} computed attribute auto-implementations"
        )


def _generate_aggregation_modules(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate TEAx module wrappers for aggregation modules."""
    from sysml_codegen.core.identifier_types import (
        PythonModulePath,
        SysMLQualifiedName,
        derive_module_type,
    )
    from sysml_codegen.core.qualified_names import get_module_name, sysml_to_python_qualified_name

    modules_dir = config.output_path / "modules"
    module_count = 0

    # Build lookup from module_eqn to PipelineModule for input derivation
    agg_modules_by_name = {
        m.name: m
        for m in ctx.computation_graph.modules
        if m.is_aggregation
    }

    for agg in (ctx.aggregation_expressions or []):
        sysml_qn = agg.module_eqn.replace("__", "::")  # BF-4: instance-scoped
        sqn = SysMLQualifiedName(sysml_qn)
        python_path = PythonModulePath.from_sysml(sqn)
        module_eqn = sysml_to_python_qualified_name(sysml_qn)

        # Create namespace subdirectory with __init__.py
        if python_path.directory:
            namespace_dir = modules_dir / python_path.directory
            namespace_dir.mkdir(parents=True, exist_ok=True)
            _ensure_package_init_files(
                modules_dir, python_path.directory,
                '"""Namespace package for generated modules."""\n',
            )

        module_type_full = derive_module_type(sysml_qn)
        class_name = module_type_full.split(".")[-1]
        input_class_name = class_name.replace("Module", "Input")

        # Derive input names from PipelineModule if available (BF-3: normalize case)
        pipeline_module = agg_modules_by_name.get(get_module_name(agg.module_eqn))
        if pipeline_module:
            input_names = [inp.param_name for inp in pipeline_module.inputs]
        else:
            logger.warning(
                "Aggregation module %s not found in computation graph; "
                "generating wrapper with empty inputs",
                agg.module_eqn,
            )
            input_names = []

        input_attributes = [
            {"name": n, "type_hint": "float", "description": f"Input {n}"}
            for n in input_names
        ]

        primitive_imports = ["Float"]

        context = {
            "class_name": class_name,
            "input_class_name": input_class_name,
            "output_class_name": None,
            "schema_name": None,
            "handler_name": get_module_name(module_eqn),
            "impl_import_path": python_path.impl_import_path,
            "doc_comment": (
                f"Aggregation module.\n\n"
                f"SysML Expression: {agg.expression.raw_expression_text}"
            ),
            "package_name": config.package_name,
            "is_multioutput": False,
            "input_attributes": input_attributes,
            "output_attributes": [
                {
                    "name": agg.expression.attribute_name,
                    "description": f"Aggregated {agg.expression.attribute_name}",
                },
            ],
            "calc_expressions": [agg.expression.raw_expression_text],
            "sysml_source": "aggregation",
            "primitive_imports": primitive_imports,
        }

        template = template_env.get_template("teax_module.py.jinja2")
        code = template.render(**context)
        if not code.endswith('\n'):
            code += '\n'

        output_path = modules_dir / python_path.full_path
        output_path.write_text(code)
        module_count += 1
        logger.debug(f"Generated aggregation module: {output_path}")

    if module_count:
        logger.info(f"Generated {module_count} aggregation module wrappers")


def _generate_aggregation_stencils(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate auto-implementation files for aggregation modules."""
    from sysml_codegen.core.identifier_types import (
        PythonModulePath,
        SysMLQualifiedName,
        derive_module_type,
    )
    from sysml_codegen.core.qualified_names import get_module_name

    handwritten_dir = config.output_path / "handwritten"
    impl_count = 0

    # Build lookup from module name to PipelineModule for compiled_expression
    agg_modules_by_name = {
        m.name: m
        for m in ctx.computation_graph.modules
        if m.is_aggregation
    }

    for agg in (ctx.aggregation_expressions or []):
        if agg.expression.has_unsupported_nodes:
            continue

        if not agg.expression.transformed_expression:
            continue

        sysml_qn = agg.module_eqn.replace("__", "::")  # BF-5: instance-scoped
        sqn = SysMLQualifiedName(sysml_qn)
        python_path = PythonModulePath.from_sysml(sqn)
        module_eqn = agg.module_eqn  # BF-5: use directly, no recompute
        module_type_full = derive_module_type(sysml_qn)
        class_name = module_type_full.split(".")[-1]
        input_class_name = class_name.replace("Module", "Input")

        # Create namespace subdirectory with __init__.py
        if python_path.directory:
            namespace_dir = handwritten_dir / python_path.directory
            namespace_dir.mkdir(parents=True, exist_ok=True)
            _ensure_package_init_files(
                handwritten_dir, python_path.directory,
                '"""Handwritten implementations."""\n',
            )
            output_path = namespace_dir / f"{python_path.filename}_impl.py"
        else:
            output_path = handwritten_dir / f"{python_path.filename}_impl.py"

        # BF-2: Use compiled_expression (inputs.X form) from PipelineModule
        pipeline_module = agg_modules_by_name.get(get_module_name(agg.module_eqn))
        expression = agg.expression.transformed_expression  # fallback
        if pipeline_module and pipeline_module.compiled_expression:
            expression = pipeline_module.compiled_expression

        context = {
            "function_name": f"run_{get_module_name(module_eqn)}",
            "calc_name": module_eqn,
            "input_class_name": input_class_name,
            "return_type": "float",
            "execution_steps": [],
            "output_expressions": [
                {
                    "name": agg.expression.attribute_name,
                    "expression": expression,
                },
            ],
            "output_count": 1,
            "single_output_expression": expression,
            "module_import_path": python_path.import_path,
            "package_name": config.package_name,
            "sysml_source": "aggregation",
            "sysml_expressions": [agg.expression.raw_expression_text],
            "docstring": (
                f"Execute {agg.expression.attribute_name} aggregation.\n\n"
                f"SysML Expression: {agg.expression.raw_expression_text}"
            ),
        }

        template = template_env.get_template("auto_implementation.py.jinja2")
        code = template.render(**context)
        if not code.endswith('\n'):
            code += '\n'

        output_path.write_text(code)
        impl_count += 1
        logger.debug(f"Generated aggregation auto-impl: {output_path}")

    if impl_count:
        logger.info(
            f"Generated {impl_count} aggregation auto-implementations"
        )


def _generate_stencils(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate implementation stencils (ADR-003 namespacing)."""
    from sysml_codegen.extraction.expression_compiler import Compilability
    from sysml_codegen.generation import (
        backup_implementation,
        generate_implementation,
        should_regenerate_stencil,
    )
    from sysml_codegen.resolution.identifier_types import (
        PythonModulePath,
        SysMLQualifiedName,
    )

    handwritten_dir = config.output_path / "handwritten"
    backup_dir = handwritten_dir / "backup"

    stats = {"new": 0, "preserved": 0, "regenerated": 0}

    for calc_def in ctx.calc_defs:
        # Skip calc_defs without outputs (nothing to implement)
        if not calc_def.output_attributes:
            continue

        sqn = SysMLQualifiedName(calc_def.qualified_name)
        python_path = PythonModulePath.from_sysml(sqn)

        # Create namespace subdirectory with __init__.py in all intermediates
        if python_path.directory:
            namespace_dir = handwritten_dir / python_path.directory
            namespace_dir.mkdir(parents=True, exist_ok=True)
            _ensure_package_init_files(
                handwritten_dir, python_path.directory,
                '"""Handwritten implementations."""\n',
            )

            output_path = namespace_dir / f"{python_path.filename}_impl.py"
        else:
            output_path = handwritten_dir / f"{python_path.filename}_impl.py"

        # Look up compilation result (may be None if no ASTs)
        compilation_result = ctx.compilation_results.get(calc_def.name)

        # Smart regeneration logic
        if config.smart_regen and output_path.exists():
            should_regen, reason = should_regenerate_stencil(calc_def, output_path)
            if should_regen:
                backup_implementation(output_path, backup_dir)
                code = generate_implementation(
                    calc_def, template_env, output_path, config.package_name,
                    compilation_result=compilation_result,
                )
                if code:
                    output_path.write_text(code)
                stats["regenerated"] += 1
                logger.debug(f"Regenerated stencil ({reason}): {output_path.name}")
            else:
                # Smart-regen: signature unchanged. Check if stub can be upgraded.
                existing_content = output_path.read_text()
                is_stub = "raise NotImplementedError" in existing_content
                has_auto_impl = (
                    compilation_result is not None
                    and compilation_result.overall_compilability == Compilability.FULLY_COMPILABLE
                )
                if is_stub and has_auto_impl:
                    backup_implementation(output_path, backup_dir)
                    code = generate_implementation(
                        calc_def, template_env, output_path, config.package_name,
                        compilation_result=compilation_result,
                    )
                    if code:
                        output_path.write_text(code)
                    stats["regenerated"] += 1
                    logger.debug(f"Upgraded stub to auto-impl: {output_path.name}")
                else:
                    stats["preserved"] += 1
                    logger.debug(f"Preserved stencil ({reason}): {output_path.name}")
        elif config.preserve_handwritten and output_path.exists():
            stats["preserved"] += 1
            logger.debug(f"Preserved existing stencil: {output_path.name}")
        else:
            code = generate_implementation(
                calc_def, template_env, output_path, config.package_name,
                compilation_result=compilation_result,
            )
            if code:
                output_path.write_text(code)
            stats["new"] += 1

    if config.smart_regen:
        logger.info(
            f"Stencils - New: {stats['new']}, "
            f"Preserved: {stats['preserved']}, "
            f"Regenerated: {stats['regenerated']}"
        )
    else:
        logger.info(f"Generated {stats['new']} implementation stencils")


def _generate_pipeline(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate pipeline YAML from computation graph."""
    from sysml_codegen.generation import generate_pipeline_yaml

    pipelines_dir = config.output_path / "pipelines"
    output_path = pipelines_dir / f"{config.pipeline_name}.yaml"

    yaml_content = generate_pipeline_yaml(
        graph=ctx.computation_graph,
        package_name=config.package_name,
        template_env=template_env,
    )
    if yaml_content:
        output_path.write_text(yaml_content)
        logger.debug(f"Generated pipeline: {output_path}")

    logger.info(f"Generated pipeline configuration: {config.pipeline_name}.yaml")


def _generate_registry(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate registry function in __init__.py."""
    from sysml_codegen.generation import generate_registry_function
    from sysml_codegen.generation.registry import _collect_exit_point_primitive_types

    output_path = config.output_path / "__init__.py"

    # Filter calc_defs to only those with outputs (matching module generation)
    calc_defs_with_outputs = [
        cd for cd in ctx.calc_defs if cd.output_attributes
    ]

    exit_point_types = _collect_exit_point_primitive_types(ctx.computation_graph.modules)

    code = generate_registry_function(
        calc_defs=calc_defs_with_outputs,
        package_name=config.package_name,
        template_env=template_env,
        output_path=output_path,
        entry_point_groups=ctx.computation_graph.entry_point_groups,
        exit_point_primitive_types=exit_point_types,
        computed_attributes=ctx.computed_attributes,
        aggregation_data=ctx.aggregation_expressions or None,
    )
    if code:
        output_path.write_text(code)
        logger.debug(f"Generated registry: {output_path}")

    logger.info(f"Generated module registry with {len(calc_defs_with_outputs)} modules")


def _generate_entry_points(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate entry point parameter group schemas and JSON templates."""
    from sysml_codegen.generation import (
        generate_all_derived_jsons_from_graph,
        generate_all_derived_schemas_from_graph,
    )

    entry_point_groups = ctx.computation_graph.entry_point_groups

    if entry_point_groups:
        schema_files = generate_all_derived_schemas_from_graph(
            entry_point_groups,
            template_env,
            config.output_path,
        )
        logger.info(f"Generated {len(schema_files)} parameter group schemas")

        json_files = generate_all_derived_jsons_from_graph(
            entry_point_groups,
            config.output_path,
        )
        logger.info(f"Generated {len(json_files)} JSON input templates")
    else:
        logger.info("No entry point groups to generate")


def _generate_backlog(
    ctx: PipelineContext,
    config: GenerationConfig,
) -> None:
    """Generate implementation backlog report."""
    from sysml_codegen.generation import generate_backlog_report

    output_path = config.output_path / "IMPLEMENTATION_BACKLOG.md"

    # Filter to calc_defs with outputs (matching module generation)
    calc_defs_with_outputs = [
        cd for cd in ctx.calc_defs if cd.output_attributes
    ]

    markdown = generate_backlog_report(
        calc_defs_with_outputs,
        output_path,
        config.package_name,
        compilation_results=ctx.compilation_results,
        computed_attributes=ctx.computed_attributes,
        aggregation_data=ctx.aggregation_expressions or None,
    )
    if markdown:
        output_path.write_text(markdown)
        logger.info(f"Generated implementation backlog: {output_path.name}")


def _generate_tests(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate runnable test file for implementations."""
    from sysml_codegen.generation import generate_test_implementations

    tests_dir = config.output_path / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    output_path = tests_dir / "test_implementations_runnable.py"

    # Filter to calc_defs with outputs (matching module generation)
    calc_defs_with_outputs = [
        cd for cd in ctx.calc_defs if cd.output_attributes
    ]

    content = generate_test_implementations(
        calc_defs=calc_defs_with_outputs,
        package_name=config.package_name,
        template_env=template_env,
        output_path=output_path,
    )
    output_path.write_text(content)
    logger.info(f"Generated runnable tests: {output_path.name}")


def cmd_generate(args: argparse.Namespace) -> int:
    """Run the code generation command."""
    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    # Validate agentic-mbse is installed
    try:
        import agentic_mbse
        logger.debug(f"agentic-mbse version: {agentic_mbse.__version__}")
    except ImportError:
        logger.error("agentic-mbse is not installed. Please install it first.")
        return 1

    config = GenerationConfig(
        models_path=args.models,
        output_path=args.output,
        package_name=args.package_name,
        schema_class_name=args.schema_class,
        pipeline_name=args.pipeline_name,
        overwrite=args.overwrite,
        preserve_handwritten=args.preserve_handwritten,
        smart_regen=args.smart_regen,
        design_path_filter=args.design_path_filter,
    )

    success = run_codegen(config)
    return 0 if success else 1


def cmd_install_commands(args: argparse.Namespace) -> int:
    """Install teax-completion helper command to a project."""
    if args.list:
        print("Available codegen helper commands:")
        for cmd in CODEGEN_COMMANDS:
            print(f"  - {cmd}")
        return 0

    target_dir = Path(args.directory).resolve()
    if not target_dir.is_dir():
        print(f"Error: {target_dir} is not a directory", file=sys.stderr)
        return 1

    commands_dir = target_dir / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    source_dir = get_commands_dir()
    copied = 0
    for cmd in CODEGEN_COMMANDS:
        src = source_dir / cmd
        dst = commands_dir / cmd
        if dst.exists() and not args.force:
            print(f"Skipping {cmd} (exists, use --force to overwrite)")
            continue
        if src.exists():
            shutil.copy(src, dst)
            print(f"Installed {cmd}")
            copied += 1
        else:
            print(f"Warning: {cmd} not found in package", file=sys.stderr)

    print(f"Installed {copied} command(s) to {commands_dir}")
    return 0


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SysML v2 code generation tools"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate subcommand
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate Python code from SysML v2 models"
    )
    gen_parser.add_argument(
        "--models", "-m",
        type=Path,
        required=True,
        help="Path to SysML model directory or file"
    )
    gen_parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output directory for generated code"
    )
    gen_parser.add_argument(
        "--package-name",
        type=str,
        default="generated_code",
        help="Python package name for generated code (default: generated_code)"
    )
    gen_parser.add_argument(
        "--schema-class",
        type=str,
        default="Params",
        help="Name for the main schema class (default: Params)"
    )
    gen_parser.add_argument(
        "--pipeline-name",
        type=str,
        default="pipeline",
        help="Name for the pipeline configuration (default: pipeline)"
    )
    gen_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files"
    )
    gen_parser.add_argument(
        "--preserve-handwritten",
        action="store_true",
        help="Preserve handwritten implementations during regeneration"
    )
    gen_parser.add_argument(
        "--smart-regen",
        action="store_true",
        help="Smart regeneration with signature comparison"
    )
    gen_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    gen_parser.add_argument(
        "--design-path-filter",
        type=str,
        default="",
        help="Substring filter for design file paths (default: accept all files)"
    )
    gen_parser.set_defaults(func=cmd_generate)

    # Install-commands subcommand
    install_parser = subparsers.add_parser(
        "install-commands",
        help="Install teax-completion helper command"
    )
    install_parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Target directory (default: current directory)"
    )
    install_parser.add_argument(
        "--list",
        action="store_true",
        help="List available commands without installing"
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files"
    )
    install_parser.set_defaults(func=cmd_install_commands)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    sys.exit(args.func(args))


def run_codegen(config: GenerationConfig) -> bool:
    """Run the code generation pipeline.

    Args:
        config: Generation configuration with paths and options.

    Returns:
        True if generation succeeded, False otherwise.
    """
    from sysml_codegen.generation import (
        CodeGenerationError,
        SysMLParsingError,
        build_pipeline_context,
    )

    logger.info(f"Generating code from {config.models_path}")
    logger.info(f"Output to {config.output_path}")
    logger.info(f"Package name: {config.package_name}")

    try:
        # Step 1: Build pipeline context (7-step initialization)
        logger.info("Building pipeline context...")
        ctx = build_pipeline_context(
            [config.models_path],
            design_path_filter=config.design_path_filter,
        )
        logger.info(f"Extracted {len(ctx.calc_defs)} calculation definitions")
        logger.info(f"Built computation graph with {len(ctx.computation_graph.modules)} modules")

        # Step 2: Clear and setup output directories
        if config.overwrite:
            logger.info("Clearing existing output directory...")
            _clear_output_directory(config)

        logger.info("Creating output directory structure...")
        _setup_output_directories(config)

        # Step 3: Generate primitives.py (required for module imports)
        _generate_primitives(config)

        # Step 4: Setup Jinja2 template environment
        template_env = _get_template_env()

        # Step 5: Generate schemas
        logger.info("Generating schemas...")
        _generate_schemas(ctx, config, template_env)

        # Step 6: Generate modules and stencils
        logger.info("Generating TEAx module wrappers...")
        _generate_modules(ctx, config, template_env)

        if ctx.computed_attributes:
            logger.info("Generating computed attribute module wrappers...")
            _generate_computed_attr_modules(ctx, config, template_env)

        logger.info("Generating implementation stencils...")
        _generate_stencils(ctx, config, template_env)

        if ctx.computed_attributes:
            logger.info("Generating computed attribute auto-implementations...")
            _generate_computed_attr_stencils(ctx, config, template_env)

        if ctx.aggregation_expressions:
            logger.info("Generating aggregation module wrappers...")
            _generate_aggregation_modules(ctx, config, template_env)

            logger.info("Generating aggregation auto-implementations...")
            _generate_aggregation_stencils(ctx, config, template_env)

        # Step 7: Generate pipeline and registry
        logger.info("Generating pipeline configuration...")
        _generate_pipeline(ctx, config, template_env)

        logger.info("Generating module registry...")
        _generate_registry(ctx, config, template_env)

        # Step 8: Generate entry points and extras
        logger.info("Generating entry point schemas and JSON templates...")
        _generate_entry_points(ctx, config, template_env)

        logger.info("Generating implementation backlog...")
        _generate_backlog(ctx, config)

        logger.info("Generating runnable tests...")
        _generate_tests(ctx, config, template_env)

        logger.info("Code generation complete")
        return True

    except SysMLParsingError as e:
        logger.error(f"SysML parsing failed: {e}")
        return False
    except CodeGenerationError as e:
        logger.error(f"Code generation failed: {e}")
        return False
    except Exception as e:
        import traceback
        logger.error(f"Unexpected error: {e}")
        logger.debug(traceback.format_exc())
        return False


__all__ = [
    "main",
    "run_codegen",
    "GenerationConfig",
    "cmd_generate",
    "cmd_install_commands",
    "CODEGEN_COMMANDS",
]
